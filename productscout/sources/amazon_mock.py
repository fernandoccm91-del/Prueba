"""Offline Amazon source backed by `data/mock_amazon.json`.

Lets you run the whole pipeline (and the tests) with no API keys.
"""

from __future__ import annotations

import json
from datetime import date

from ..config import DATA_DIR, Settings
from ..models import AmazonProduct
from .base import AmazonSource

SEED_FILE = DATA_DIR / "mock_amazon.json"


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


class MockAmazonSource(AmazonSource):
    name = "mock"

    def __init__(self, settings: Settings):
        super().__init__(settings)
        self._raw = json.loads(SEED_FILE.read_text(encoding="utf-8"))

    def _build(self, row: dict) -> AmazonProduct:
        return AmazonProduct(
            asin=row["asin"],
            title=row["title"],
            category=row["category"],
            price=float(row["price"]),
            brand=row.get("brand"),
            bsr=row.get("bsr"),
            offers_count=row.get("offers_count"),
            reviews_count=row.get("reviews_count"),
            rating=row.get("rating"),
            weight_g=row.get("weight_g"),
            length_mm=row.get("length_mm"),
            width_mm=row.get("width_mm"),
            height_mm=row.get("height_mm"),
            first_available=_parse_date(row.get("first_available")),
            url=f"https://www.amazon.com/dp/{row['asin']}",
            source="mock",
        )

    def search(self, keyword: str, category: str | None = None, limit: int = 25) -> list[AmazonProduct]:
        needle = (keyword or "").strip().lower()
        hits = []
        for row in self._raw:
            haystack = " ".join(
                [row["title"], row.get("brand") or "", row["category"], *row.get("keywords", [])]
            ).lower()
            category_ok = not category or row["category"].lower() == category.lower()
            if category_ok and (not needle or needle in haystack):
                hits.append(self._build(row))
        if not hits and not category:
            hits = [self._build(row) for row in self._raw]
        return hits[:limit]
