"""Opportunity scoring.

Every sub-score is 0-100 and independently interpretable, so you can see *why*
a product ranked where it did. `WEIGHTS` controls how they combine.
"""

from __future__ import annotations

import math

from .config import Settings
from .models import AmazonProduct, Economics, MLMarket, Opportunity

WEIGHTS: dict[str, float] = {
    "demand": 0.25,
    "competition": 0.25,
    "margin": 0.20,
    "novelty": 0.10,
    "size": 0.10,
    "mercadolibre": 0.10,
}


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def scale(value: float, low: float, high: float) -> float:
    """Linear 0-100 mapping of `value` between `low` and `high`."""
    if high == low:
        return 50.0
    return clamp((value - low) / (high - low) * 100.0)


def _log_penalty(count: float, factor: float) -> float:
    return clamp(100.0 - factor * math.log10(1.0 + max(0.0, count)))


def demand_score(monthly_units: float, monthly_revenue: float) -> float:
    units = scale(math.log10(monthly_units + 1), 1.0, 3.5)      # 10 -> 0, ~3000 -> 100
    revenue = scale(math.log10(monthly_revenue + 1), 2.5, 5.0)  # ~300 -> 0, ~100k -> 100
    return round(0.6 * units + 0.4 * revenue, 1)


def competition_score(
    product: AmazonProduct,
    peer_reviews: list[int] | None = None,
) -> tuple[float, list[str]]:
    """High score = little competition. `peer_reviews` are the review counts of
    the other results for the same keyword/category page."""
    notes: list[str] = []
    own = _log_penalty(product.reviews_count or 0, 24.0)

    if peer_reviews:
        ordered = sorted(peer_reviews)
        mid = ordered[len(ordered) // 2]
        peers = _log_penalty(mid, 24.0)
        weak_rivals = sum(1 for r in ordered if r < 100) / len(ordered)
        if weak_rivals >= 0.5:
            notes.append(f"{weak_rivals:.0%} de los competidores tiene <100 reseñas")
    else:
        peers = own

    score = 0.5 * own + 0.5 * peers

    offers = product.offers_count or 0
    if offers > 3:
        score -= min(30.0, (offers - 3) * 2.5)
        notes.append(f"{offers} vendedores en el mismo listing")
    if product.amazon_sells_it:
        score -= 25.0
        notes.append("Amazon vende este producto directamente")
    if product.rating is not None and product.rating < 4.2:
        score += 8.0
        notes.append(f"rating bajo ({product.rating}) — hueco de calidad")
    if (product.reviews_count or 0) < 75:
        notes.append(f"listing líder con solo {product.reviews_count or 0} reseñas")

    return round(clamp(score), 1), notes


def novelty_score(product: AmazonProduct) -> tuple[float, list[str]]:
    age = product.age_days
    if age is None:
        return 50.0, ["sin fecha de publicación: novedad no verificada"]
    if age <= 90:
        return 100.0, [f"listing muy nuevo ({age} días)"]
    if age <= 180:
        return 88.0, [f"listing nuevo ({age} días)"]
    if age <= 365:
        return 72.0, [f"menos de un año en catálogo ({age} días)"]
    if age <= 540:
        return 55.0, []
    if age <= 730:
        return 38.0, []
    return 18.0, [f"producto maduro ({age // 365} años en catálogo)"]


def size_score(product: AmazonProduct, settings: Settings) -> tuple[float, list[str]]:
    from .fees import size_tier

    tier = size_tier(product)
    notes: list[str] = []
    if tier == "small_standard":
        base = 100.0
        notes.append("small standard-size: envío y FBA baratos")
    elif tier == "large_standard":
        base = 60.0
    elif tier == "oversize":
        base = 10.0
        notes.append("oversize: flete y FBA caros")
    else:
        return 50.0, ["sin dimensiones/peso: tamaño no verificado"]

    weight = product.weight_g or 0
    if weight > settings.max_weight_g:
        base -= 25.0
        notes.append(f"pesa {weight:.0f} g (límite configurado {settings.max_weight_g} g)")
    longest = product.longest_side_mm
    if longest and longest > settings.max_longest_side_mm:
        base -= 15.0
        notes.append(f"lado mayor {longest:.0f} mm supera el límite configurado")
    return round(clamp(base), 1), notes


def margin_score(econ: Economics | None) -> tuple[float, list[str]]:
    if econ is None:
        return 0.0, ["sin cotización de proveedor: rentabilidad desconocida"]
    margin = scale(econ.margin, 0.05, 0.40)
    roi = scale(econ.roi, 0.3, 2.0)
    notes = []
    if econ.profit_per_unit_usd <= 0:
        notes.append("no deja utilidad al precio actual de venta")
    elif econ.roi >= 1.0:
        notes.append(f"ROI estimado {econ.roi:.0%} con utilidad de ${econ.profit_per_unit_usd:.2f}/u")
    return round(0.5 * margin + 0.5 * roi, 1), notes


def ml_score(market: MLMarket | None) -> tuple[float, list[str]]:
    """Mercado Libre: demand present, competition still thin."""
    if market is None or market.total_listings == 0:
        return 40.0, ["sin datos de Mercado Libre"]
    notes: list[str] = []
    demand = scale(math.log10(market.monthly_units_est + 1), 0.7, 3.0)
    competition = _log_penalty(market.total_listings, 22.0)
    if market.official_store_share > 0.4:
        competition -= 20.0
        notes.append(f"{market.official_store_share:.0%} de las publicaciones son tiendas oficiales")
    if market.total_listings < 150 and market.monthly_units_est > 100:
        notes.append(
            f"ML: ~{market.monthly_units_est:.0f} u/mes con solo {market.total_listings} publicaciones"
        )
    return round(clamp(0.55 * demand + 0.45 * clamp(competition)), 1), notes


def verdict_for(score: float) -> str:
    if score >= 75:
        return "perseguir"
    if score >= 60:
        return "investigar"
    if score >= 45:
        return "dudoso"
    return "descartar"


def score_opportunity(
    opp: Opportunity,
    settings: Settings,
    peer_reviews: list[int] | None = None,
) -> Opportunity:
    """Fill in `scores`, `total_score`, `verdict`, `reasons` and `warnings`."""
    product = opp.product
    reasons: list[str] = []
    warnings: list[str] = []

    d = demand_score(opp.amazon_monthly_units, opp.amazon_monthly_revenue_usd)
    c, c_notes = competition_score(product, peer_reviews)
    m, m_notes = margin_score(opp.economics)
    n, n_notes = novelty_score(product)
    s, s_notes = size_score(product, settings)
    ml, ml_notes = ml_score(opp.ml_market)

    opp.scores = {
        "demand": d,
        "competition": c,
        "margin": m,
        "novelty": n,
        "size": s,
        "mercadolibre": ml,
    }
    opp.total_score = round(sum(opp.scores[k] * w for k, w in WEIGHTS.items()), 1)
    opp.verdict = verdict_for(opp.total_score)

    if opp.amazon_daily_units >= 1:
        reasons.append(
            f"Amazon: ~{opp.amazon_daily_units:.1f} u/día "
            f"(~{opp.amazon_monthly_units:.0f} u/mes, "
            f"~${opp.amazon_monthly_revenue_usd:,.0f}/mes)"
        )
    else:
        warnings.append("demanda en Amazon por debajo de 1 unidad/día")

    for note in (*c_notes, *m_notes, *n_notes, *s_notes, *ml_notes):
        target = warnings if _is_warning(note) else reasons
        target.append(note)

    if not opp.quotes:
        warnings.append("sin proveedores encontrados en Alibaba")
    if product.price < settings.min_price_usd or product.price > settings.max_price_usd:
        warnings.append(
            f"precio ${product.price:.2f} fuera del rango objetivo "
            f"(${settings.min_price_usd:.0f}-${settings.max_price_usd:.0f})"
        )

    # Warnings raised earlier in the pipeline (e.g. "demand is a BSR estimate")
    # must survive scoring.
    opp.reasons = _dedupe(opp.reasons + reasons)
    opp.warnings = _dedupe(opp.warnings + warnings)
    return opp


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


_WARNING_MARKERS = (
    "sin ", "no deja", "supera", "pesa", "Amazon vende", "vendedores en el mismo",
    "oversize", "maduro", "tiendas oficiales",
)


def _is_warning(note: str) -> bool:
    return note.startswith(_WARNING_MARKERS)
