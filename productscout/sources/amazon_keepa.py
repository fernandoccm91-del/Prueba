"""Amazon data via the Keepa API (https://keepa.com/#!api).

Keepa is the pragmatic choice here: it is the only affordable source that gives
sales rank history, offer counts, review counts, package dimensions, the date a
listing went live and — for many ASINs — the "bought in past month" figure that
Amazon itself shows. Everything else has to be inferred from BSR.

Requires KEEPA_API_KEY. Each product request costs tokens, so keep `limit` low.
"""

from __future__ import annotations

import json
from datetime import date, datetime, timezone

from ..config import Settings
from ..http import request_json
from ..models import AmazonProduct
from .base import AmazonSource

API = "https://api.keepa.com"
KEEPA_EPOCH_OFFSET_MIN = 21564000  # keepa minutes -> unix seconds

# Indices into Keepa's stats.current array.
IDX_AMAZON, IDX_NEW, IDX_SALES = 0, 1, 3
IDX_COUNT_NEW, IDX_RATING, IDX_COUNT_REVIEWS = 11, 16, 17


def _keepa_time_to_date(minutes: int | None) -> date | None:
    if not minutes or minutes < 0:
        return None
    ts = (minutes + KEEPA_EPOCH_OFFSET_MIN) * 60
    return datetime.fromtimestamp(ts, tz=timezone.utc).date()


def _at(stats: list | None, index: int) -> int | None:
    if not stats or index >= len(stats):
        return None
    value = stats[index]
    return None if value is None or value < 0 else value


class KeepaSource(AmazonSource):
    name = "keepa"

    def __init__(self, settings: Settings):
        super().__init__(settings)
        if not settings.keepa_api_key:
            raise RuntimeError("KEEPA_API_KEY no está configurada (AMAZON_SOURCE=keepa)")

    # --- public API -------------------------------------------------------
    def search(self, keyword: str, category: str | None = None, limit: int = 25) -> list[AmazonProduct]:
        asins = self._find_asins(keyword, limit)
        return self.products(asins) if asins else []

    def products(self, asins: list[str]) -> list[AmazonProduct]:
        if not asins:
            return []
        payload = request_json(
            f"{API}/product",
            params={
                "key": self.settings.keepa_api_key,
                "domain": self.settings.keepa_domain,
                "asin": ",".join(asins[:100]),
                "stats": 30,
                "buybox": 1,
                "offers": 20,
            },
            timeout=self.settings.request_timeout,
        )
        return [self._to_product(row) for row in (payload or {}).get("products", [])]

    # --- discovery --------------------------------------------------------
    def _find_asins(self, keyword: str, limit: int) -> list[str]:
        """Product Finder first (it can filter by rank/reviews/weight/date),
        falling back to plain keyword search."""
        selection = {
            "current_SALES_gte": 1,
            "current_SALES_lte": 60000,
            "current_NEW_gte": int(self.settings.min_price_usd * 100),
            "current_NEW_lte": int(self.settings.max_price_usd * 100),
            "current_COUNT_REVIEWS_lte": 400,
            "packageWeight_lte": self.settings.max_weight_g,
            "productType": [0, 1],
            "sort": [["current_SALES", "asc"]],
            "perPage": min(limit, 50),
            "page": 0,
        }
        if keyword:
            selection["title"] = keyword
        try:
            payload = request_json(
                f"{API}/query",
                params={
                    "key": self.settings.keepa_api_key,
                    "domain": self.settings.keepa_domain,
                    "selection": json.dumps(selection),
                },
                timeout=self.settings.request_timeout,
            )
            asins = (payload or {}).get("asinList") or []
            if asins:
                return asins[:limit]
        except Exception:  # noqa: BLE001 - finder is optional, fall through to search
            pass

        payload = request_json(
            f"{API}/search",
            params={
                "key": self.settings.keepa_api_key,
                "domain": self.settings.keepa_domain,
                "type": "product",
                "term": keyword,
                "stats": 30,
            },
            timeout=self.settings.request_timeout,
        )
        products = (payload or {}).get("products") or []
        return [p["asin"] for p in products if p.get("asin")][:limit]

    # --- mapping ----------------------------------------------------------
    def _to_product(self, row: dict) -> AmazonProduct:
        stats = (row.get("stats") or {}).get("current")
        price_cents = _at(stats, IDX_NEW) or _at(stats, IDX_AMAZON)
        rating = _at(stats, IDX_RATING)
        category_tree = row.get("categoryTree") or []
        category = category_tree[0]["name"] if category_tree else (row.get("rootCategory") or "")

        return AmazonProduct(
            asin=row.get("asin", ""),
            title=row.get("title") or "",
            category=str(category),
            price=(price_cents or 0) / 100.0,
            brand=row.get("brand"),
            bsr=_at(stats, IDX_SALES),
            offers_count=_at(stats, IDX_COUNT_NEW),
            reviews_count=_at(stats, IDX_COUNT_REVIEWS) or row.get("countReviews"),
            rating=(rating / 10.0) if rating else None,
            monthly_sold=row.get("monthlySold"),
            weight_g=row.get("packageWeight") if (row.get("packageWeight") or 0) > 0 else None,
            length_mm=row.get("packageLength") if (row.get("packageLength") or 0) > 0 else None,
            width_mm=row.get("packageWidth") if (row.get("packageWidth") or 0) > 0 else None,
            height_mm=row.get("packageHeight") if (row.get("packageHeight") or 0) > 0 else None,
            first_available=_keepa_time_to_date(row.get("listedSince")),
            image_url=self._image(row),
            url=f"https://www.amazon.com/dp/{row.get('asin', '')}",
            amazon_sells_it=bool(_at(stats, IDX_AMAZON)),
            source="keepa",
        )

    @staticmethod
    def _image(row: dict) -> str | None:
        images = row.get("imagesCSV")
        if not images:
            return None
        return f"https://images-na.ssl-images-amazon.com/images/I/{images.split(',')[0]}"
