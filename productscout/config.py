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
    ml_site: str = "MLM"                 # MLM=México, MLC=Chile, MLA=Argentina, MCO=Colombia, MLB=Brasil
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
    costs: CostAssumptions = field(default_factory=CostAssumptions)

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
            ml_site=os.environ.get("ML_SITE", "MLM"),
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
            costs=costs,
        )


SETTINGS = Settings.from_env()
