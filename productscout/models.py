"""Domain models shared by every data source, the scoring engine and the API."""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any


def _json_default(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    raise TypeError(f"not JSON serializable: {type(value)!r}")


def to_dict(obj: Any) -> Any:
    """Recursively convert dataclasses (and dates) into plain JSON-ready data."""
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return {k: to_dict(v) for k, v in dataclasses.asdict(obj).items()}
    if isinstance(obj, dict):
        return {k: to_dict(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_dict(v) for v in obj]
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    return obj


@dataclass
class AmazonProduct:
    """A product as seen on Amazon."""

    asin: str
    title: str
    category: str
    price: float
    currency: str = "USD"
    brand: str | None = None
    bsr: int | None = None                  # Best Sellers Rank in `category`
    offers_count: int | None = None         # sellers competing on the listing
    reviews_count: int | None = None
    rating: float | None = None
    monthly_sold: int | None = None         # when the source reports it (Keepa "bought in past month")
    weight_g: float | None = None
    length_mm: float | None = None
    width_mm: float | None = None
    height_mm: float | None = None
    first_available: date | None = None     # listing creation date -> "producto nuevo"
    image_url: str | None = None
    url: str | None = None
    fba_sellers: int | None = None
    amazon_sells_it: bool = False
    source: str = "mock"

    @property
    def age_days(self) -> int | None:
        if not self.first_available:
            return None
        return (date.today() - self.first_available).days

    @property
    def longest_side_mm(self) -> float | None:
        sides = [s for s in (self.length_mm, self.width_mm, self.height_mm) if s]
        return max(sides) if sides else None

    @property
    def volume_cm3(self) -> float | None:
        if not (self.length_mm and self.width_mm and self.height_mm):
            return None
        return (self.length_mm / 10) * (self.width_mm / 10) * (self.height_mm / 10)


@dataclass
class MLListing:
    """A single Mercado Libre listing."""

    id: str
    title: str
    price: float
    currency: str
    sold_quantity: int | None = None
    listing_type: str | None = None
    official_store: bool = False
    free_shipping: bool = False
    url: str | None = None
    seller_id: str | None = None


@dataclass
class MLMarket:
    """Aggregated Mercado Libre picture for one search query."""

    query: str
    site: str
    total_listings: int
    median_price: float | None = None
    currency: str = "MXN"
    sold_total: int = 0              # sum of sold_quantity across sampled listings
    monthly_units_est: float = 0.0   # demand estimate derived from sold_total
    official_store_share: float = 0.0
    top_seller_share: float = 0.0    # share of sales held by the single biggest seller
    listings: list[MLListing] = field(default_factory=list)
    source: str = "mock"


@dataclass
class PriceTier:
    min_qty: int
    unit_price_usd: float


@dataclass
class SupplierQuote:
    """A supplier offer (Alibaba / 1688 / manually collected quote)."""

    supplier_name: str
    product_title: str
    unit_price_usd: float
    moq: int
    url: str | None = None
    country: str = "CN"
    years_active: int | None = None
    trade_assurance: bool = False
    verified_supplier: bool = False
    rating: float | None = None
    lead_time_days: int | None = None
    unit_weight_g: float | None = None
    price_tiers: list[PriceTier] = field(default_factory=list)
    source: str = "mock"

    def price_at(self, qty: int) -> float:
        """Unit price for a given order quantity, using the tier table."""
        price = self.unit_price_usd
        for tier in sorted(self.price_tiers, key=lambda t: t.min_qty):
            if qty >= tier.min_qty:
                price = tier.unit_price_usd
        return price


@dataclass
class Economics:
    """Landed cost and profitability for one product/quote combination."""

    order_qty: int
    unit_cost_usd: float
    freight_usd: float
    duty_usd: float
    prep_usd: float
    landed_cost_usd: float
    platform_fee_usd: float
    fulfilment_fee_usd: float
    sale_price_usd: float
    profit_per_unit_usd: float
    margin: float
    roi: float
    size_tier: str
    upfront_investment_usd: float


@dataclass
class Opportunity:
    """The end product of the pipeline: one scored candidate."""

    product: AmazonProduct
    ml_market: MLMarket | None = None
    quotes: list[SupplierQuote] = field(default_factory=list)
    economics: Economics | None = None
    amazon_monthly_units: float = 0.0
    amazon_daily_units: float = 0.0
    amazon_monthly_revenue_usd: float = 0.0
    scores: dict[str, float] = field(default_factory=dict)
    total_score: float = 0.0
    verdict: str = "descartar"
    reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    scanned_at: datetime = field(default_factory=datetime.utcnow)
