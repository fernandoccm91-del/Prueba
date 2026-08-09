"""The scan pipeline: Amazon -> demand -> Mercado Libre -> Alibaba -> score."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from .config import Settings
from .estimators import amazon_demand
from .fees import best_quote, size_tier
from .keywords import alibaba_query, ml_query
from .models import AmazonProduct, Opportunity
from .scoring import score_opportunity
from .sources.base import get_amazon_source, get_ml_source, get_supplier_source


@dataclass
class ScanRequest:
    keywords: list[str] = field(default_factory=list)
    category: str | None = None
    limit_per_keyword: int = 25
    min_score: float = 0.0
    check_mercadolibre: bool = True
    check_suppliers: bool = True
    small_only: bool = False          # drop anything that is not standard-size
    max_results: int = 50


@dataclass
class ScanResult:
    opportunities: list[Opportunity]
    started_at: datetime
    finished_at: datetime
    request: ScanRequest
    sources: dict[str, str]
    errors: list[str] = field(default_factory=list)


class Pipeline:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.amazon = get_amazon_source(settings)
        self.ml = get_ml_source(settings)
        self.suppliers = get_supplier_source(settings)

    # --- helpers ----------------------------------------------------------
    def _passes_hard_filters(self, product: AmazonProduct, request: ScanRequest) -> bool:
        if product.price <= 0:
            return False
        if request.small_only and size_tier(product) == "oversize":
            return False
        if request.small_only and (product.weight_g or 0) > self.settings.max_weight_g:
            return False
        return True

    def _collect(self, request: ScanRequest) -> tuple[list[AmazonProduct], list[str]]:
        found: dict[str, AmazonProduct] = {}
        errors: list[str] = []
        keywords = request.keywords or [""]
        for keyword in keywords:
            try:
                for product in self.amazon.search(keyword, request.category, request.limit_per_keyword):
                    if product.asin and product.asin not in found:
                        found[product.asin] = product
            except Exception as exc:  # noqa: BLE001 - one bad keyword shouldn't kill the scan
                errors.append(f"Amazon '{keyword}': {exc}")
        return list(found.values()), errors

    # --- main -------------------------------------------------------------
    def scan(self, request: ScanRequest) -> ScanResult:
        started = datetime.utcnow()
        products, errors = self._collect(request)
        products = [p for p in products if self._passes_hard_filters(p, request)]
        peer_reviews = [p.reviews_count for p in products if p.reviews_count is not None]

        opportunities: list[Opportunity] = []
        for product in products:
            opp = Opportunity(product=product)
            monthly, daily, method = amazon_demand(product)
            opp.amazon_monthly_units = round(monthly, 1)
            opp.amazon_daily_units = round(daily, 2)
            opp.amazon_monthly_revenue_usd = round(monthly * product.price, 2)
            if method == "bsr_curve":
                opp.warnings.append("demanda estimada desde el BSR (no es dato oficial de Amazon)")

            if request.check_mercadolibre:
                query = ml_query(product.title, product.brand)
                try:
                    opp.ml_market = self.ml.market(query)
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"MercadoLibre '{query}': {exc}")

            if request.check_suppliers:
                query = alibaba_query(product.title, product.brand)
                try:
                    opp.quotes = self.suppliers.quotes(query, reference_price_usd=product.price)
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"Proveedores '{query}': {exc}")
                quote, econ = best_quote(product, opp.quotes, self.settings.costs)
                if quote and econ:
                    opp.economics = econ
                    opp.quotes = [quote] + [q for q in opp.quotes if q is not quote]

            score_opportunity(opp, self.settings, peer_reviews)
            if opp.total_score >= request.min_score:
                opportunities.append(opp)

        opportunities.sort(key=lambda o: o.total_score, reverse=True)
        return ScanResult(
            opportunities=opportunities[: request.max_results],
            started_at=started,
            finished_at=datetime.utcnow(),
            request=request,
            sources={
                "amazon": self.amazon.name,
                "mercadolibre": self.ml.name,
                "suppliers": self.suppliers.name,
            },
            errors=errors,
        )

    def supplier_search_url(self, product: AmazonProduct) -> str:
        return self.suppliers.search_url(alibaba_query(product.title, product.brand))
