"""Supplier quotes you collected by hand, stored in a JSON file.

Alibaba has no open product API (their Open Platform is restricted to approved
partners, and scraping the site breaks their terms of service). In practice the
reliable workflow is: the app shortlists products and hands you a ready-made
Alibaba search URL, you request quotes, and you paste the numbers back here.
Everything downstream — landed cost, margin, ROI, ranking — then runs on real
supplier data.

File format (`data/supplier_quotes.json`)::

    [
      {
        "match": ["herb stripper", "B0D3F8W7RK"],
        "supplier_name": "Yiwu Kitchen Tools Co., Ltd.",
        "product_title": "Stainless steel herb stripper, OEM logo",
        "unit_price_usd": 1.35,
        "moq": 500,
        "url": "https://www.alibaba.com/product-detail/...",
        "years_active": 9,
        "trade_assurance": true,
        "verified_supplier": true,
        "rating": 4.8,
        "lead_time_days": 25,
        "unit_weight_g": 70,
        "price_tiers": [{"min_qty": 500, "unit_price_usd": 1.35},
                        {"min_qty": 2000, "unit_price_usd": 1.12}]
      }
    ]
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from ..config import Settings
from ..models import PriceTier, SupplierQuote
from .base import SupplierSource

_WORD = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> set[str]:
    return set(_WORD.findall(text.lower()))


class ManualSupplierSource(SupplierSource):
    name = "manual"

    def __init__(self, settings: Settings):
        super().__init__(settings)
        self.path = Path(settings.supplier_manual_file)

    def _load(self) -> list[dict]:
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except ValueError:
            return []
        return data if isinstance(data, list) else data.get("quotes", [])

    def quotes(
        self,
        query: str,
        limit: int = 8,
        reference_price_usd: float | None = None,
    ) -> list[SupplierQuote]:
        wanted = _tokens(query)
        scored: list[tuple[float, SupplierQuote]] = []

        for row in self._load():
            keys = row.get("match") or [row.get("product_title", "")]
            best = 0.0
            for key in keys:
                key_tokens = _tokens(str(key))
                if not key_tokens:
                    continue
                if str(key).upper() in query.upper():   # exact ASIN / phrase match
                    best = 1.0
                    break
                overlap = len(key_tokens & wanted) / len(key_tokens)
                best = max(best, overlap)
            if best >= 0.5:
                scored.append((best, self._to_quote(row)))

        scored.sort(key=lambda pair: (-pair[0], pair[1].unit_price_usd))
        return [quote for _, quote in scored[:limit]]

    @staticmethod
    def _to_quote(row: dict) -> SupplierQuote:
        tiers = [
            PriceTier(min_qty=int(t["min_qty"]), unit_price_usd=float(t["unit_price_usd"]))
            for t in row.get("price_tiers", [])
        ]
        return SupplierQuote(
            supplier_name=row.get("supplier_name", "desconocido"),
            product_title=row.get("product_title", ""),
            unit_price_usd=float(row.get("unit_price_usd", 0)),
            moq=int(row.get("moq", 1)),
            url=row.get("url"),
            country=row.get("country", "CN"),
            years_active=row.get("years_active"),
            trade_assurance=bool(row.get("trade_assurance")),
            verified_supplier=bool(row.get("verified_supplier")),
            rating=row.get("rating"),
            lead_time_days=row.get("lead_time_days"),
            unit_weight_g=row.get("unit_weight_g"),
            price_tiers=tiers,
            source="manual",
        )
