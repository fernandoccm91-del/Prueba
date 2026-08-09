"""Landed cost and Amazon fee estimation (US marketplace, simplified).

Fee tables are approximations of Amazon's published FBA rate card and change
every year — override them via environment variables or edit the tables here
before trusting the absolute numbers. The relative ranking between products is
what the scoring engine actually consumes.
"""

from __future__ import annotations

from .config import CostAssumptions
from .models import AmazonProduct, Economics, SupplierQuote

MM_PER_INCH = 25.4
G_PER_OZ = 28.3495
G_PER_LB = 453.592

# Small standard-size: <= 15 x 12 x 0.75 in and <= 16 oz
SMALL_STANDARD_MAX_MM = (15 * MM_PER_INCH, 12 * MM_PER_INCH, 0.75 * MM_PER_INCH)
SMALL_STANDARD_MAX_G = 16 * G_PER_OZ

# Large standard-size: <= 18 x 14 x 8 in and <= 20 lb
LARGE_STANDARD_MAX_MM = (18 * MM_PER_INCH, 14 * MM_PER_INCH, 8 * MM_PER_INCH)
LARGE_STANDARD_MAX_G = 20 * G_PER_LB

# weight ceiling in oz -> fee in USD
SMALL_STANDARD_FEES = [
    (2, 3.06), (4, 3.15), (6, 3.24), (8, 3.33),
    (10, 3.43), (12, 3.53), (14, 3.60), (16, 3.65),
]
LARGE_STANDARD_FEES = [
    (4, 3.68), (8, 3.90), (12, 4.15), (16, 4.55),
    (24, 4.99), (32, 5.37), (40, 5.52), (48, 5.77),
]


def _fits(dims_mm: tuple[float, float, float], limits: tuple[float, float, float]) -> bool:
    return all(d <= limit for d, limit in zip(sorted(dims_mm, reverse=True), limits))


def size_tier(product: AmazonProduct) -> str:
    """Classify into the FBA size tier that drives the fulfilment fee."""
    dims = (product.length_mm, product.width_mm, product.height_mm)
    weight = product.weight_g
    if not all(dims) or weight is None:
        return "unknown"
    dims_mm = (float(dims[0]), float(dims[1]), float(dims[2]))
    if weight <= SMALL_STANDARD_MAX_G and _fits(dims_mm, SMALL_STANDARD_MAX_MM):
        return "small_standard"
    if weight <= LARGE_STANDARD_MAX_G and _fits(dims_mm, LARGE_STANDARD_MAX_MM):
        return "large_standard"
    return "oversize"


def fba_fee(product: AmazonProduct) -> float:
    """Estimated FBA fulfilment fee in USD."""
    tier = size_tier(product)
    weight_g = product.weight_g or 450.0
    ounces = weight_g / G_PER_OZ

    if tier == "small_standard":
        table = SMALL_STANDARD_FEES
    elif tier == "large_standard":
        table = LARGE_STANDARD_FEES
    else:
        # Oversize / unknown: flat base plus a per-pound component.
        return round(9.73 + max(0.0, weight_g / G_PER_LB - 1) * 0.42, 2)

    for ceiling_oz, fee in table:
        if ounces <= ceiling_oz:
            return fee
    # Heavier than the table: extend the last step by half-pound increments.
    last_oz, last_fee = table[-1]
    extra_half_lbs = max(0.0, (ounces - last_oz) / 8.0)
    return round(last_fee + extra_half_lbs * 0.08, 2)


def chargeable_weight_kg(product: AmazonProduct, quote: SupplierQuote, costs: CostAssumptions) -> float:
    """Freight-chargeable weight: max(actual, volumetric) for air, actual for sea."""
    actual_kg = (quote.unit_weight_g or product.weight_g or 300.0) / 1000.0
    if costs.freight_mode != "air":
        return actual_kg
    volume_cm3 = product.volume_cm3
    if not volume_cm3:
        return actual_kg
    # Assume ~25% packaging overhead on the retail volume.
    volumetric_kg = (volume_cm3 * 1.25) / costs.volumetric_divisor
    return max(actual_kg, volumetric_kg)


def compute_economics(
    product: AmazonProduct,
    quote: SupplierQuote,
    costs: CostAssumptions,
    order_qty: int | None = None,
    sale_price: float | None = None,
) -> Economics:
    """Full unit economics for buying `order_qty` units and selling on Amazon."""
    qty = order_qty or max(quote.moq, 100)
    unit_cost = quote.price_at(qty)
    price = sale_price if sale_price is not None else product.price

    kg = chargeable_weight_kg(product, quote, costs)
    rate = costs.air_usd_per_kg if costs.freight_mode == "air" else costs.sea_usd_per_kg
    freight = kg * rate
    duty = unit_cost * costs.duty_rate
    prep = costs.inbound_prep_usd_per_unit
    landed = unit_cost + freight + duty + prep

    referral = price * costs.amazon_referral_rate
    fulfilment = fba_fee(product)
    profit = price - landed - referral - fulfilment

    return Economics(
        order_qty=qty,
        unit_cost_usd=round(unit_cost, 3),
        freight_usd=round(freight, 3),
        duty_usd=round(duty, 3),
        prep_usd=round(prep, 3),
        landed_cost_usd=round(landed, 3),
        platform_fee_usd=round(referral, 3),
        fulfilment_fee_usd=round(fulfilment, 3),
        sale_price_usd=round(price, 2),
        profit_per_unit_usd=round(profit, 3),
        margin=round(profit / price, 4) if price else 0.0,
        roi=round(profit / landed, 4) if landed else 0.0,
        size_tier=size_tier(product),
        upfront_investment_usd=round(landed * qty, 2),
    )


def best_quote(
    product: AmazonProduct,
    quotes: list[SupplierQuote],
    costs: CostAssumptions,
) -> tuple[SupplierQuote | None, Economics | None]:
    """Pick the quote with the highest profit per unit."""
    best: tuple[SupplierQuote, Economics] | None = None
    for quote in quotes:
        econ = compute_economics(product, quote, costs)
        if best is None or econ.profit_per_unit_usd > best[1].profit_per_unit_usd:
            best = (quote, econ)
    return best if best else (None, None)
