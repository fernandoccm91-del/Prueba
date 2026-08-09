"""Deterministic offline supplier source (stands in for Alibaba).

Prices are anchored to the retail price so the unit economics in the demo are
in a realistic range (typical China FOB cost is 15-30% of the US retail price
for small consumer goods).
"""

from __future__ import annotations

import hashlib
import random

from ..models import PriceTier, SupplierQuote
from .base import SupplierSource

CITIES = ["Shenzhen", "Ningbo", "Yiwu", "Dongguan", "Xiamen", "Guangzhou", "Qingdao"]
SUFFIX = ["Industrial Co., Ltd.", "Trading Co., Ltd.", "Technology Co., Ltd.", "Houseware Co., Ltd."]


def _rng(query: str) -> random.Random:
    return random.Random(int(hashlib.md5(query.lower().encode()).hexdigest()[:12], 16))


class MockSupplierSource(SupplierSource):
    name = "mock"

    def quotes(
        self,
        query: str,
        limit: int = 8,
        reference_price_usd: float | None = None,
    ) -> list[SupplierQuote]:
        rng = _rng(query)
        retail = reference_price_usd or 20.0
        results: list[SupplierQuote] = []

        for i in range(min(limit, rng.randint(3, 6))):
            base = round(retail * rng.uniform(0.13, 0.32), 2)
            moq = rng.choice([50, 100, 200, 300, 500, 1000])
            tiers = [
                PriceTier(min_qty=moq, unit_price_usd=base),
                PriceTier(min_qty=moq * 5, unit_price_usd=round(base * 0.88, 2)),
                PriceTier(min_qty=moq * 20, unit_price_usd=round(base * 0.76, 2)),
            ]
            results.append(
                SupplierQuote(
                    supplier_name=f"{rng.choice(CITIES)} {query.split()[0].title()} {rng.choice(SUFFIX)}",
                    product_title=f"Custom OEM {query} - logo personalizado",
                    unit_price_usd=base,
                    moq=moq,
                    url=self.search_url(query),
                    years_active=rng.randint(2, 16),
                    trade_assurance=rng.random() < 0.75,
                    verified_supplier=rng.random() < 0.6,
                    rating=round(rng.uniform(4.0, 5.0), 1),
                    lead_time_days=rng.choice([15, 20, 25, 30, 45]),
                    unit_weight_g=None,
                    price_tiers=tiers,
                    source="mock",
                )
            )
        return sorted(results, key=lambda q: q.unit_price_usd)
