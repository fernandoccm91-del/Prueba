"""Supplier quotes from any HTTP endpoint that returns JSON.

Point SUPPLIER_HTTP_ENDPOINT at whatever gateway you are entitled to use — the
Alibaba Open Platform (if your account is approved), a paid B2B data provider,
or your own service. The mapper below accepts the field names those APIs
commonly use, so in most cases no code change is needed.

The endpoint is called as ``GET {endpoint}?q={query}&limit={limit}`` with an
optional ``Authorization: Bearer {SUPPLIER_HTTP_KEY}`` header.
"""

from __future__ import annotations

from typing import Any

from ..config import Settings
from ..http import HttpError, request_json
from ..models import PriceTier, SupplierQuote
from .base import SupplierSource

ALIASES: dict[str, tuple[str, ...]] = {
    "supplier_name": ("supplier_name", "company_name", "supplier", "companyName", "seller"),
    "product_title": ("product_title", "title", "subject", "name"),
    "unit_price_usd": ("unit_price_usd", "price", "unit_price", "priceUsd", "min_price"),
    "moq": ("moq", "min_order_quantity", "minOrderQuantity", "min_order"),
    "url": ("url", "product_url", "detail_url", "link"),
    "country": ("country", "country_code", "origin"),
    "years_active": ("years_active", "years", "gold_years", "supplier_years"),
    "rating": ("rating", "score", "review_score"),
    "lead_time_days": ("lead_time_days", "lead_time", "delivery_days"),
    "unit_weight_g": ("unit_weight_g", "weight_g", "unit_weight"),
}


def _pick(row: dict, field: str) -> Any:
    for key in ALIASES[field]:
        if row.get(key) not in (None, ""):
            return row[key]
    return None


def _as_float(value: Any) -> float | None:
    try:
        return float(str(value).replace("$", "").replace(",", "").split("-")[0].strip())
    except (TypeError, ValueError):
        return None


class HttpSupplierSource(SupplierSource):
    name = "http"

    def __init__(self, settings: Settings):
        super().__init__(settings)
        if not settings.supplier_http_endpoint:
            raise RuntimeError("SUPPLIER_HTTP_ENDPOINT no está configurado (SUPPLIER_SOURCE=http)")

    def quotes(
        self,
        query: str,
        limit: int = 8,
        reference_price_usd: float | None = None,
    ) -> list[SupplierQuote]:
        headers = {}
        if self.settings.supplier_http_key:
            headers["Authorization"] = f"Bearer {self.settings.supplier_http_key}"
        try:
            payload = request_json(
                self.settings.supplier_http_endpoint,
                params={"q": query, "limit": limit},
                headers=headers,
                timeout=self.settings.request_timeout,
            )
        except HttpError:
            return []

        rows = payload if isinstance(payload, list) else (payload or {}).get("results") or []
        quotes = [self._to_quote(row) for row in rows[:limit]]
        return sorted([q for q in quotes if q.unit_price_usd > 0], key=lambda q: q.unit_price_usd)

    def _to_quote(self, row: dict) -> SupplierQuote:
        tiers = []
        for tier in row.get("price_tiers") or row.get("ladderPrices") or []:
            qty = tier.get("min_qty") or tier.get("startQuantity")
            price = _as_float(tier.get("unit_price_usd") or tier.get("price"))
            if qty and price:
                tiers.append(PriceTier(min_qty=int(qty), unit_price_usd=price))

        return SupplierQuote(
            supplier_name=str(_pick(row, "supplier_name") or "desconocido"),
            product_title=str(_pick(row, "product_title") or ""),
            unit_price_usd=_as_float(_pick(row, "unit_price_usd")) or 0.0,
            moq=int(_as_float(_pick(row, "moq")) or 1),
            url=_pick(row, "url"),
            country=str(_pick(row, "country") or "CN"),
            years_active=int(_as_float(_pick(row, "years_active")) or 0) or None,
            trade_assurance=bool(row.get("trade_assurance") or row.get("tradeAssurance")),
            verified_supplier=bool(row.get("verified_supplier") or row.get("verified")),
            rating=_as_float(_pick(row, "rating")),
            lead_time_days=int(_as_float(_pick(row, "lead_time_days")) or 0) or None,
            unit_weight_g=_as_float(_pick(row, "unit_weight_g")),
            price_tiers=tiers,
            source="http",
        )
