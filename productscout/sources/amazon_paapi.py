"""Amazon Product Advertising API 5.0 (SearchItems / GetItems), signed with SigV4.

Free, but it only works if you have an active Associates account, and it does
NOT expose review counts or listing age, and exposes sales rank only through
``BrowseNodeInfo.WebsiteSalesRank``. Use it for price/dimensions/offers and pair
it with Keepa (or manual input) for demand and competition signals.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import hmac
import json

from ..config import Settings
from ..http import request_json
from ..models import AmazonProduct
from .base import AmazonSource

SERVICE = "ProductAdvertisingAPI"
RESOURCES = [
    "ItemInfo.Title",
    "ItemInfo.ByLineInfo",
    "ItemInfo.ProductInfo",
    "ItemInfo.Classifications",
    "Offers.Listings.Price",
    "Offers.Summaries.OfferCount",
    "Images.Primary.Medium",
    "BrowseNodeInfo.WebsiteSalesRank",
]

# Product dimensions come back in hundredths of an inch or in inches depending
# on the marketplace unit string; normalise everything to millimetres/grams.
_LENGTH_TO_MM = {"inches": 25.4, "hundredths-inches": 0.254, "centimeters": 10.0, "millimeters": 1.0}
_WEIGHT_TO_G = {"pounds": 453.592, "hundredths-pounds": 4.53592, "ounces": 28.3495, "grams": 1.0, "kilograms": 1000.0}


def _sign(key: bytes, msg: str) -> bytes:
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def _signing_key(secret: str, datestamp: str, region: str, service: str) -> bytes:
    k_date = _sign(f"AWS4{secret}".encode(), datestamp)
    k_region = _sign(k_date, region)
    k_service = _sign(k_region, service)
    return _sign(k_service, "aws4_request")


class PaapiSource(AmazonSource):
    name = "paapi"

    def __init__(self, settings: Settings):
        super().__init__(settings)
        missing = [
            key
            for key, value in {
                "PAAPI_ACCESS_KEY": settings.paapi_access_key,
                "PAAPI_SECRET_KEY": settings.paapi_secret_key,
                "PAAPI_PARTNER_TAG": settings.paapi_partner_tag,
            }.items()
            if not value
        ]
        if missing:
            raise RuntimeError(f"Faltan credenciales PA-API: {', '.join(missing)}")

    # --- signing ----------------------------------------------------------
    def _headers(self, target: str, payload: str) -> dict[str, str]:
        s = self.settings
        now = dt.datetime.now(dt.timezone.utc)
        amz_date = now.strftime("%Y%m%dT%H%M%SZ")
        datestamp = now.strftime("%Y%m%d")
        path = f"/paapi5/{target.lower()}"
        amz_target = f"com.amazon.paapi5.v1.ProductAdvertisingAPIv1.{target}"

        canonical_headers = (
            f"content-encoding:amz-1.0\n"
            f"host:{s.paapi_host}\n"
            f"x-amz-date:{amz_date}\n"
            f"x-amz-target:{amz_target}\n"
        )
        signed_headers = "content-encoding;host;x-amz-date;x-amz-target"
        payload_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        canonical_request = "\n".join(
            ["POST", path, "", canonical_headers, signed_headers, payload_hash]
        )

        scope = f"{datestamp}/{s.paapi_region}/{SERVICE}/aws4_request"
        string_to_sign = "\n".join(
            [
                "AWS4-HMAC-SHA256",
                amz_date,
                scope,
                hashlib.sha256(canonical_request.encode("utf-8")).hexdigest(),
            ]
        )
        signature = hmac.new(
            _signing_key(s.paapi_secret_key, datestamp, s.paapi_region, SERVICE),
            string_to_sign.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        return {
            "content-encoding": "amz-1.0",
            "content-type": "application/json; charset=utf-8",
            "host": s.paapi_host,
            "x-amz-date": amz_date,
            "x-amz-target": amz_target,
            "Authorization": (
                f"AWS4-HMAC-SHA256 Credential={s.paapi_access_key}/{scope}, "
                f"SignedHeaders={signed_headers}, Signature={signature}"
            ),
        }

    def _call(self, target: str, body: dict) -> dict:
        payload = json.dumps(body)
        return request_json(
            f"https://{self.settings.paapi_host}/paapi5/{target.lower()}",
            method="POST",
            data=payload.encode("utf-8"),
            headers=self._headers(target, payload),
            timeout=self.settings.request_timeout,
        ) or {}

    # --- public API -------------------------------------------------------
    def search(self, keyword: str, category: str | None = None, limit: int = 25) -> list[AmazonProduct]:
        products: list[AmazonProduct] = []
        for page in range(1, min(limit // 10 + 1, 10) + 1):
            body = {
                "Keywords": keyword,
                "SearchIndex": category or "All",
                "ItemCount": 10,
                "ItemPage": page,
                "PartnerTag": self.settings.paapi_partner_tag,
                "PartnerType": "Associates",
                "Marketplace": f"www.{self.settings.paapi_host.replace('webservices.', '')}",
                "Resources": RESOURCES,
            }
            payload = self._call("SearchItems", body)
            items = (payload.get("SearchResult") or {}).get("Items") or []
            products.extend(self._to_product(item) for item in items)
            if len(products) >= limit or not items:
                break
        return products[:limit]

    # --- mapping ----------------------------------------------------------
    def _to_product(self, item: dict) -> AmazonProduct:
        info = item.get("ItemInfo") or {}
        title = ((info.get("Title") or {}).get("DisplayValue")) or ""
        brand = (((info.get("ByLineInfo") or {}).get("Brand") or {}).get("DisplayValue"))
        product_info = info.get("ProductInfo") or {}
        dims = product_info.get("ItemDimensions") or {}

        listing = ((item.get("Offers") or {}).get("Listings") or [{}])[0]
        price = ((listing.get("Price") or {}).get("Amount")) or 0.0
        currency = ((listing.get("Price") or {}).get("Currency")) or "USD"
        summaries = (item.get("Offers") or {}).get("Summaries") or [{}]
        offer_count = summaries[0].get("OfferCount")

        ranks = (item.get("BrowseNodeInfo") or {}).get("WebsiteSalesRank") or {}
        category = ranks.get("DisplayName") or (
            ((info.get("Classifications") or {}).get("ProductGroup") or {}).get("DisplayValue")
        ) or ""

        return AmazonProduct(
            asin=item.get("ASIN", ""),
            title=title,
            category=str(category),
            price=float(price),
            currency=currency,
            brand=brand,
            bsr=ranks.get("SalesRank"),
            offers_count=offer_count,
            weight_g=self._convert(dims.get("Weight"), _WEIGHT_TO_G),
            length_mm=self._convert(dims.get("Length"), _LENGTH_TO_MM),
            width_mm=self._convert(dims.get("Width"), _LENGTH_TO_MM),
            height_mm=self._convert(dims.get("Height"), _LENGTH_TO_MM),
            image_url=(((item.get("Images") or {}).get("Primary") or {}).get("Medium") or {}).get("URL"),
            url=item.get("DetailPageURL"),
            source="paapi",
        )

    @staticmethod
    def _convert(measure: dict | None, table: dict[str, float]) -> float | None:
        if not measure or measure.get("Value") is None:
            return None
        unit = str(measure.get("Unit", "")).lower()
        factor = table.get(unit)
        if factor is None:
            return None
        return float(measure["Value"]) * factor
