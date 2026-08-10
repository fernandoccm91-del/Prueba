"""Mercado Libre via the official API (https://developers.mercadolibre.com).

Search endpoints now require an access token. Create an app in the developer
portal and set ML_CLIENT_ID / ML_CLIENT_SECRET — this source uses the
`client_credentials` grant, so no user login is involved.

Caveat worth knowing: `sold_quantity` is the *lifetime* total for a listing, and
some sites round it into buckets. `estimators.ml_monthly_units` amortises it
over ML_SOLD_WINDOW_MONTHS to get a monthly figure.
"""

from __future__ import annotations

import time
from collections import Counter

from ..config import Settings
from ..estimators import median, ml_monthly_units, round_or_none
from ..http import HttpError, post_form, request_json
from ..models import MLListing, MLMarket
from .base import MercadoLibreSource

API = "https://api.mercadolibre.com"
TOKEN_URL = f"{API}/oauth/token"


class MercadoLibreApiSource(MercadoLibreSource):
    name = "api"

    def __init__(self, settings: Settings):
        super().__init__(settings)
        self._token: str | None = None
        self._token_expires_at: float = 0.0

    def _access_token(self) -> str | None:
        if self._token and time.time() < self._token_expires_at:
            return self._token
        if not (self.settings.ml_client_id and self.settings.ml_client_secret):
            return None
        payload = post_form(
            TOKEN_URL,
            {
                "grant_type": "client_credentials",
                "client_id": self.settings.ml_client_id,
                "client_secret": self.settings.ml_client_secret,
            },
            timeout=self.settings.request_timeout,
        )
        self._token = (payload or {}).get("access_token")
        self._token_expires_at = time.time() + float((payload or {}).get("expires_in", 3600)) - 60
        return self._token

    def market(self, query: str, limit: int = 50) -> MLMarket:
        headers = {}
        token = self._access_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"

        try:
            payload = request_json(
                f"{API}/sites/{self.settings.ml_site}/search",
                params={"q": query, "limit": min(limit, 50)},
                headers=headers,
                timeout=self.settings.request_timeout,
            ) or {}
        except HttpError as exc:
            # 401/403 = missing or expired credentials; return an empty market
            # rather than killing the whole scan.
            return MLMarket(
                query=query,
                site=self.settings.ml_site,
                total_listings=0,
                source=f"api_error_{exc.status}",
            )

        results = payload.get("results") or []
        listings = [self._to_listing(row) for row in results]
        sold_total = sum(item.sold_quantity or 0 for item in listings)

        seller_sales: Counter[str] = Counter()
        for item in listings:
            if item.seller_id:
                seller_sales[item.seller_id] += item.sold_quantity or 0
        top_share = (seller_sales.most_common(1)[0][1] / sold_total) if sold_total and seller_sales else 0.0

        official = sum(1 for item in listings if item.official_store)
        return MLMarket(
            query=query,
            site=self.settings.ml_site,
            total_listings=int((payload.get("paging") or {}).get("total", len(listings))),
            median_price=round_or_none(median([item.price for item in listings])),
            currency=listings[0].currency if listings else "",
            sold_total=sold_total,
            monthly_units_est=round(ml_monthly_units(sold_total), 1),
            official_store_share=round(official / len(listings), 3) if listings else 0.0,
            top_seller_share=round(top_share, 3),
            listings=listings[:20],
            source="api",
        )

    @staticmethod
    def _to_listing(row: dict) -> MLListing:
        return MLListing(
            id=row.get("id", ""),
            title=row.get("title", ""),
            price=float(row.get("price") or 0),
            currency=row.get("currency_id", ""),
            sold_quantity=row.get("sold_quantity"),
            listing_type=row.get("listing_type_id"),
            official_store=bool(row.get("official_store_id")),
            free_shipping=bool((row.get("shipping") or {}).get("free_shipping")),
            url=row.get("permalink"),
            seller_id=str((row.get("seller") or {}).get("id") or row.get("seller_id") or ""),
        )
