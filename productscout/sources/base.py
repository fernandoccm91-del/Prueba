"""Source interfaces and the registry that picks an implementation per config.

Adding a new data provider means implementing one of these three protocols and
registering it — nothing else in the app changes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..config import Settings
from ..models import AmazonProduct, MLMarket, SupplierQuote


class AmazonSource(ABC):
    name = "abstract"

    def __init__(self, settings: Settings):
        self.settings = settings

    @abstractmethod
    def search(self, keyword: str, category: str | None = None, limit: int = 25) -> list[AmazonProduct]:
        """Products matching a keyword (or the top movers of a category)."""

    def enrich(self, product: AmazonProduct) -> AmazonProduct:
        """Optionally add dimensions/age/offers to a product. Default: no-op."""
        return product


class MercadoLibreSource(ABC):
    name = "abstract"

    def __init__(self, settings: Settings):
        self.settings = settings

    @abstractmethod
    def market(self, query: str, limit: int = 50) -> MLMarket:
        """Aggregated competition + demand snapshot for a search query."""


class SupplierSource(ABC):
    name = "abstract"

    def __init__(self, settings: Settings):
        self.settings = settings

    @abstractmethod
    def quotes(
        self,
        query: str,
        limit: int = 8,
        reference_price_usd: float | None = None,
    ) -> list[SupplierQuote]:
        """Supplier offers for a product description.

        `reference_price_usd` is the retail price we expect to sell at; sources
        that only return relative pricing can use it as an anchor.
        """

    def search_url(self, query: str) -> str:
        from urllib.parse import quote_plus

        return f"https://www.alibaba.com/trade/search?SearchText={quote_plus(query)}"


def get_amazon_source(settings: Settings) -> AmazonSource:
    kind = settings.amazon_source.lower()
    if kind == "keepa":
        from .amazon_keepa import KeepaSource

        return KeepaSource(settings)
    if kind == "paapi":
        from .amazon_paapi import PaapiSource

        return PaapiSource(settings)
    from .amazon_mock import MockAmazonSource

    return MockAmazonSource(settings)


def get_ml_source(settings: Settings) -> MercadoLibreSource:
    if settings.ml_source.lower() == "api":
        from .ml_api import MercadoLibreApiSource

        return MercadoLibreApiSource(settings)
    from .ml_mock import MockMLSource

    return MockMLSource(settings)


def get_supplier_source(settings: Settings) -> SupplierSource:
    kind = settings.supplier_source.lower()
    if kind == "manual":
        from .alibaba_manual import ManualSupplierSource

        return ManualSupplierSource(settings)
    if kind == "http":
        from .alibaba_http import HttpSupplierSource

        return HttpSupplierSource(settings)
    from .alibaba_mock import MockSupplierSource

    return MockSupplierSource(settings)
