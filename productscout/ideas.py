"""Búsqueda por nicho: el flujo principal para vender en Mercado Libre.

Para cada término del nicho:

1. **Mercado Libre** — cuánta competencia hay, cuánto se vende, a qué precio.
   Es donde vas a vender, así que manda el precio de venta.
2. **Amazon (EE.UU.)** — se busca el mismo producto en inglés para confirmar
   que tiene demanda real y ver qué tan peleado está allá.
3. **Alibaba** — a cuánto sale el producto y con qué proveedores.
4. **Cuentas** — costo puesto en el país, comisión de ML, envío, ganancia.

El resultado es una lista de ideas de producto ordenadas por oportunidad.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from .config import Settings
from .estimators import amazon_demand, median
from .fees import best_ml_quote
from .keywords import to_english
from .models import ProductIdea
from .niches import Niche, get_niche
from .scoring import score_idea
from .sources.base import get_amazon_source, get_ml_source, get_supplier_source

# Cuántos resultados de Amazon se miran por término.
AMAZON_MATCHES = 5


@dataclass
class NicheScanRequest:
    niche: str = "bano"
    terms: list[str] = field(default_factory=list)   # sobreescribe los del nicho
    max_terms: int | None = None
    min_score: float = 0.0
    top: int = 20


@dataclass
class NicheScanResult:
    ideas: list[ProductIdea]
    niche_name: str
    site: str
    started_at: datetime
    finished_at: datetime
    sources: dict[str, str]
    terms_scanned: int
    errors: list[str] = field(default_factory=list)


class NicheScanner:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.amazon = get_amazon_source(settings)
        self.ml = get_ml_source(settings)
        self.suppliers = get_supplier_source(settings)

    def resolve_terms(self, request: NicheScanRequest) -> tuple[list[str], str]:
        if request.terms:
            return request.terms, "búsqueda personalizada"
        niche: Niche | None = get_niche(request.niche)
        if not niche:
            raise ValueError(
                f"No conozco el nicho '{request.niche}'. "
                f"Revisa data/nichos.json o usa --termino para buscar algo puntual."
            )
        terms = niche.terminos[: request.max_terms] if request.max_terms else niche.terminos
        return terms, niche.nombre

    def scan_term(self, term: str, errors: list[str]) -> ProductIdea:
        market = self.ml.market(term)
        idea = ProductIdea(term=term, ml_market=market)

        english = to_english(term)
        idea.alibaba_url = self.suppliers.search_url(english)

        # --- Amazon: ¿existe demanda comprobada para esto? ---
        try:
            matches = self.amazon.search(english, limit=AMAZON_MATCHES)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"Amazon '{english}': {exc}")
            matches = []
        idea.amazon_products = matches
        if matches:
            idea.amazon_monthly_units = round(
                sum(amazon_demand(product)[0] for product in matches[:3]), 1
            )
            reviews = [p.reviews_count for p in matches if p.reviews_count is not None]
            idea.amazon_reviews_median = median([float(r) for r in reviews])

        # --- Alibaba: precio y proveedores ---
        reference_usd = None
        if market.median_price:
            reference_usd = market.median_price / self.settings.market.fx_usd_to_local
        try:
            idea.quotes = self.suppliers.quotes(english, reference_price_usd=reference_usd)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"Proveedores '{english}': {exc}")

        # --- cuentas ---
        weight_g = next((p.weight_g for p in matches if p.weight_g), None)
        if market.median_price and idea.quotes:
            quote, econ = best_ml_quote(
                market.median_price,
                idea.quotes,
                self.settings.market,
                self.settings.costs,
                weight_g,
            )
            if quote and econ:
                idea.economics = econ
                idea.quotes = [quote] + [q for q in idea.quotes if q is not quote]

        return score_idea(idea)

    def scan(self, request: NicheScanRequest) -> NicheScanResult:
        started = datetime.utcnow()
        terms, niche_name = self.resolve_terms(request)
        errors: list[str] = []
        ideas: list[ProductIdea] = []

        for term in terms:
            try:
                idea = self.scan_term(term, errors)
            except Exception as exc:  # noqa: BLE001 - un término malo no bota la búsqueda
                errors.append(f"Mercado Libre '{term}': {exc}")
                continue
            if idea.total_score >= request.min_score:
                ideas.append(idea)

        ideas.sort(key=lambda i: i.total_score, reverse=True)
        return NicheScanResult(
            ideas=ideas[: request.top],
            niche_name=niche_name,
            site=self.settings.ml_site,
            started_at=started,
            finished_at=datetime.utcnow(),
            sources={
                "amazon": self.amazon.name,
                "mercadolibre": self.ml.name,
                "proveedores": self.suppliers.name,
            },
            terms_scanned=len(terms),
            errors=errors,
        )
