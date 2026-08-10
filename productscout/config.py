"""Configuration loaded from environment variables (or a local .env file).

Everything has a sensible default so the app runs out of the box with the
`mock` data sources. Add real credentials to enable live sources.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"


def load_dotenv(path: Path | None = None) -> None:
    """Minimal .env loader (no external dependency)."""
    env_path = path or ROOT / ".env"
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _f(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, default))
    except ValueError:
        return default


def _i(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except ValueError:
        return default


@dataclass
class CostAssumptions:
    """Assumptions used to turn a supplier quote into a landed cost."""

    freight_mode: str = "air"  # air | sea
    air_usd_per_kg: float = 7.5
    sea_usd_per_kg: float = 2.2
    # Volumetric weight divisor for air freight (cm3 -> kg).
    volumetric_divisor: int = 6000
    duty_rate: float = 0.08  # 8% import duty on FOB value
    amazon_referral_rate: float = 0.15
    ml_commission_rate: float = 0.16
    inbound_prep_usd_per_unit: float = 0.35
    target_roi: float = 1.0  # 100% ROI over landed cost
    target_margin: float = 0.25


# Moneda de cada sitio de Mercado Libre.
CURRENCY_BY_SITE = {
    "MLC": "CLP", "MLM": "MXN", "MLA": "ARS",
    "MCO": "COP", "MLB": "BRL", "MPE": "PEN", "MLU": "UYU",
}
# Tipo de cambio por defecto (moneda local por 1 USD). Ajústalo con FX_USD_LOCAL.
FX_BY_SITE = {"MLC": 950.0, "MLM": 18.0, "MLA": 1200.0, "MCO": 4000.0, "MLB": 5.4, "MPE": 3.7}
# IVA por país.
VAT_BY_SITE = {"MLC": 0.19, "MLM": 0.16, "MLA": 0.21, "MCO": 0.19, "MLB": 0.0, "MPE": 0.18}
# Arancel de importación general (ad valorem sobre CIF).
DUTY_BY_SITE = {"MLC": 0.06, "MLM": 0.15, "MLA": 0.20, "MCO": 0.10, "MLB": 0.60, "MPE": 0.06}


@dataclass
class MarketAssumptions:
    """Supuestos para vender en Mercado Libre (por defecto, Chile).

    Son aproximaciones públicas y cambian con el tiempo: revísalas en tu cuenta
    de vendedor antes de tomar decisiones de plata.
    """

    site: str = "MLC"
    fx_usd_to_local: float = 950.0
    vat_rate: float = 0.19
    # True = vendes con empresa (inicio de actividades): recuperas el IVA de la
    # importación, pero el precio de Mercado Libre lleva IVA incluido y se
    # descuenta del ingreso. False = vendes como persona natural: te quedas con
    # el precio completo, pero el IVA de importación es un costo perdido.
    # Importar formalmente exige empresa, así que True es el caso normal.
    vat_recoverable: bool = True
    import_duty_rate: float = 0.06
    commission_rate: float = 0.145        # publicación clásica
    fixed_fee_local: float = 800.0        # cargo por unidad en productos baratos
    fixed_fee_threshold_local: float = 9990.0
    free_shipping_threshold_local: float = 19990.0
    # (peso máximo en gramos, costo de envío en moneda local)
    shipping_brackets: tuple[tuple[float, float], ...] = (
        (500, 2900.0), (1000, 3400.0), (2000, 4200.0), (5000, 5600.0), (float("inf"), 7500.0),
    )

    @classmethod
    def for_site(cls, site: str) -> "MarketAssumptions":
        return cls(
            site=site,
            fx_usd_to_local=_f("FX_USD_LOCAL", FX_BY_SITE.get(site, 950.0)),
            vat_rate=_f("VAT_RATE", VAT_BY_SITE.get(site, 0.19)),
            vat_recoverable=os.environ.get("VAT_RECOVERABLE", "true").lower() != "false",
            import_duty_rate=_f("IMPORT_DUTY_RATE", DUTY_BY_SITE.get(site, 0.06)),
            commission_rate=_f("ML_COMMISSION_RATE", 0.145),
            fixed_fee_local=_f("ML_FIXED_FEE_LOCAL", 800.0),
            fixed_fee_threshold_local=_f("ML_FIXED_FEE_THRESHOLD", 9990.0),
            free_shipping_threshold_local=_f("ML_FREE_SHIPPING_THRESHOLD", 19990.0),
        )


@dataclass
class Settings:
    # --- source selection -------------------------------------------------
    amazon_source: str = "mock"          # mock | keepa | paapi
    ml_source: str = "mock"              # mock | api
    supplier_source: str = "mock"        # mock | manual | http

    # --- Amazon -----------------------------------------------------------
    amazon_marketplace: str = "US"
    keepa_api_key: str = ""
    keepa_domain: int = 1                # 1 = amazon.com, 2 = .co.uk, ... 11 = .com.mx
    paapi_access_key: str = ""
    paapi_secret_key: str = ""
    paapi_partner_tag: str = ""
    paapi_host: str = "webservices.amazon.com"
    paapi_region: str = "us-east-1"

    # --- Mercado Libre ----------------------------------------------------
    ml_site: str = "MLC"                 # MLC=Chile, MLM=México, MLA=Argentina, MCO=Colombia, MLB=Brasil
    ml_client_id: str = ""
    ml_client_secret: str = ""

    # --- Suppliers (Alibaba) ---------------------------------------------
    supplier_http_endpoint: str = ""     # third-party scraping/API gateway, if you have one
    supplier_http_key: str = ""
    supplier_manual_file: str = str(DATA_DIR / "supplier_quotes.json")

    # --- filters ----------------------------------------------------------
    max_weight_g: int = 900              # "productos pequeños"
    max_longest_side_mm: int = 380
    min_price_usd: float = 12.0
    max_price_usd: float = 70.0
    max_product_age_days: int = 540      # "productos nuevos"

    # --- runtime ----------------------------------------------------------
    db_path: str = str(ROOT / "productscout.db")
    request_timeout: int = 25
    default_niche: str = "bano"
    costs: CostAssumptions = field(default_factory=CostAssumptions)
    market: MarketAssumptions = field(default_factory=MarketAssumptions)

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        costs = CostAssumptions(
            freight_mode=os.environ.get("FREIGHT_MODE", "air"),
            air_usd_per_kg=_f("AIR_USD_PER_KG", 7.5),
            sea_usd_per_kg=_f("SEA_USD_PER_KG", 2.2),
            duty_rate=_f("DUTY_RATE", 0.08),
            amazon_referral_rate=_f("AMAZON_REFERRAL_RATE", 0.15),
            ml_commission_rate=_f("ML_COMMISSION_RATE", 0.16),
            inbound_prep_usd_per_unit=_f("INBOUND_PREP_USD", 0.35),
            target_roi=_f("TARGET_ROI", 1.0),
            target_margin=_f("TARGET_MARGIN", 0.25),
        )
        site = os.environ.get("ML_SITE", "MLC")
        return cls(
            amazon_source=os.environ.get("AMAZON_SOURCE", "mock"),
            ml_source=os.environ.get("ML_SOURCE", "mock"),
            supplier_source=os.environ.get("SUPPLIER_SOURCE", "mock"),
            amazon_marketplace=os.environ.get("AMAZON_MARKETPLACE", "US"),
            keepa_api_key=os.environ.get("KEEPA_API_KEY", ""),
            keepa_domain=_i("KEEPA_DOMAIN", 1),
            paapi_access_key=os.environ.get("PAAPI_ACCESS_KEY", ""),
            paapi_secret_key=os.environ.get("PAAPI_SECRET_KEY", ""),
            paapi_partner_tag=os.environ.get("PAAPI_PARTNER_TAG", ""),
            paapi_host=os.environ.get("PAAPI_HOST", "webservices.amazon.com"),
            paapi_region=os.environ.get("PAAPI_REGION", "us-east-1"),
            ml_site=site,
            ml_client_id=os.environ.get("ML_CLIENT_ID", ""),
            ml_client_secret=os.environ.get("ML_CLIENT_SECRET", ""),
            supplier_http_endpoint=os.environ.get("SUPPLIER_HTTP_ENDPOINT", ""),
            supplier_http_key=os.environ.get("SUPPLIER_HTTP_KEY", ""),
            supplier_manual_file=os.environ.get(
                "SUPPLIER_MANUAL_FILE", str(DATA_DIR / "supplier_quotes.json")
            ),
            max_weight_g=_i("MAX_WEIGHT_G", 900),
            max_longest_side_mm=_i("MAX_LONGEST_SIDE_MM", 380),
            min_price_usd=_f("MIN_PRICE_USD", 12.0),
            max_price_usd=_f("MAX_PRICE_USD", 70.0),
            max_product_age_days=_i("MAX_PRODUCT_AGE_DAYS", 540),
            db_path=os.environ.get("DB_PATH", str(ROOT / "productscout.db")),
            request_timeout=_i("REQUEST_TIMEOUT", 25),
            default_niche=os.environ.get("DEFAULT_NICHE", "bano"),
            costs=costs,
            market=MarketAssumptions.for_site(site),
        )


SETTINGS = Settings.from_env()
