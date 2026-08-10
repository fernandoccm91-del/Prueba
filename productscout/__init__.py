"""ProductScout — investigación de productos para Amazon FBA / Mercado Libre.

Flujo: descubre productos en Amazon, estima demanda y competencia, cruza el
mismo producto contra Mercado Libre, cotiza proveedores en Alibaba y calcula
el costo puesto en bodega, el margen y el ROI.
"""

from .config import Settings
from .models import AmazonProduct, MLMarket, Opportunity, SupplierQuote
from .pipeline import Pipeline, ScanRequest, ScanResult

__version__ = "0.1.0"
__all__ = [
    "Settings",
    "Pipeline",
    "ScanRequest",
    "ScanResult",
    "AmazonProduct",
    "MLMarket",
    "SupplierQuote",
    "Opportunity",
]
