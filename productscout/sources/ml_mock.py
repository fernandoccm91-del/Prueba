"""Deterministic offline Mercado Libre source.

Generates a plausible market for any query (same query -> same numbers) so the
pipeline, the CLI and the dashboard can be exercised without credentials.
"""

from __future__ import annotations

import hashlib
import math
import random

from ..config import CURRENCY_BY_SITE
from ..estimators import median, ml_monthly_units, round_or_none
from ..models import MLListing, MLMarket
from .base import MercadoLibreSource

FX_PER_USD = {"MXN": 18.0, "CLP": 950.0, "ARS": 1200.0, "COP": 4000.0, "BRL": 5.4, "PEN": 3.7, "UYU": 40.0}


def _rng(query: str) -> random.Random:
    seed = int(hashlib.md5(query.lower().encode()).hexdigest()[:12], 16)
    return random.Random(seed)


class MockMLSource(MercadoLibreSource):
    name = "mock"

    def market(self, query: str, limit: int = 50) -> MLMarket:
        rng = _rng(query)
        site = self.settings.ml_site
        currency = CURRENCY_BY_SITE.get(site, "MXN")
        fx = FX_PER_USD.get(currency, 18.0)

        total = int(math.exp(rng.uniform(math.log(25), math.log(2600))))
        base_price = rng.uniform(9.0, 55.0) * fx

        listings: list[MLListing] = []
        for i in range(min(limit, 20)):
            sold = int(rng.paretovariate(1.25) * rng.choice([1, 3, 8, 25]))
            listings.append(
                MLListing(
                    id=f"{site}{rng.randint(100000000, 999999999)}",
                    title=f"{query.title()} - modelo {i + 1}",
                    price=round(base_price * rng.uniform(0.7, 1.5), 2),
                    currency=currency,
                    sold_quantity=sold,
                    listing_type=rng.choice(["gold_special", "gold_pro", "free"]),
                    official_store=rng.random() < 0.18,
                    free_shipping=rng.random() < 0.6,
                    url=f"https://articulo.mercadolibre.com/{site}-mock-{i}",
                    seller_id=str(rng.randint(1000, 1080)),
                )
            )

        sold_total = sum(item.sold_quantity or 0 for item in listings)
        official = sum(1 for item in listings if item.official_store)
        return MLMarket(
            query=query,
            site=site,
            total_listings=total,
            median_price=round_or_none(median([item.price for item in listings])),
            currency=currency,
            sold_total=sold_total,
            monthly_units_est=round(ml_monthly_units(sold_total), 1),
            official_store_share=round(official / len(listings), 3) if listings else 0.0,
            top_seller_share=round(rng.uniform(0.1, 0.5), 3),
            listings=listings,
            source="mock",
        )
