"""Demand estimation.

Amazon does not publish units sold. The industry-standard workaround is to map
Best Sellers Rank (BSR) to units through a per-category power law:

    units_per_day = a * rank ** (-b)

The coefficients below are calibrated so the curve passes through commonly
quoted reference points for the US marketplace. They are *estimates* — treat
them as an ordering signal, not as accounting. You can override any category by
editing ``data/bsr_curves.json``.

When a source gives a direct signal (Keepa's "bought in past month", Mercado
Libre's ``sold_quantity``) that always wins over the curve.
"""

from __future__ import annotations

import json
from pathlib import Path

from .config import DATA_DIR

# category -> (a, b) for units_per_day = a * rank ** -b
DEFAULT_CURVES: dict[str, tuple[float, float]] = {
    "default": (12000.0, 0.80),
    "Home & Kitchen": (16560.0, 0.809),
    "Kitchen & Dining": (9000.0, 0.80),
    "Office Products": (4200.0, 0.78),
    "Sports & Outdoors": (7000.0, 0.79),
    "Toys & Games": (9500.0, 0.80),
    "Beauty & Personal Care": (11000.0, 0.80),
    "Health & Household": (13000.0, 0.81),
    "Pet Supplies": (8000.0, 0.79),
    "Electronics": (10000.0, 0.80),
    "Cell Phones & Accessories": (6500.0, 0.78),
    "Tools & Home Improvement": (7500.0, 0.79),
    "Baby Products": (5200.0, 0.78),
    "Arts, Crafts & Sewing": (3800.0, 0.77),
    "Patio, Lawn & Garden": (6000.0, 0.78),
    "Automotive": (6800.0, 0.79),
}

_CURVES_FILE = DATA_DIR / "bsr_curves.json"


def load_curves() -> dict[str, tuple[float, float]]:
    curves = dict(DEFAULT_CURVES)
    path = Path(_CURVES_FILE)
    if path.exists():
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            for category, params in raw.items():
                curves[category] = (float(params[0]), float(params[1]))
        except (ValueError, KeyError, IndexError, TypeError):
            pass  # a broken override file must not break a scan
    return curves


def bsr_to_daily_units(bsr: int | None, category: str | None = None) -> float:
    """Estimated units sold per day for a given BSR in a category."""
    if not bsr or bsr <= 0:
        return 0.0
    curves = load_curves()
    a, b = curves.get(category or "", curves["default"])
    return a * (bsr ** -b)


def bsr_to_monthly_units(bsr: int | None, category: str | None = None) -> float:
    return bsr_to_daily_units(bsr, category) * 30.0


def amazon_demand(product) -> tuple[float, float, str]:
    """Return (monthly_units, daily_units, method) for an :class:`AmazonProduct`."""
    if product.monthly_sold:
        monthly = float(product.monthly_sold)
        return monthly, monthly / 30.0, "reported"
    monthly = bsr_to_monthly_units(product.bsr, product.category)
    return monthly, monthly / 30.0, "bsr_curve"


# --- Mercado Libre --------------------------------------------------------
# `sold_quantity` on ML is cumulative for the lifetime of the listing, so we
# amortise it over an assumed window. Tune with ML_SOLD_WINDOW_MONTHS.
ML_SOLD_WINDOW_MONTHS = 12.0


def ml_monthly_units(sold_total: int, window_months: float = ML_SOLD_WINDOW_MONTHS) -> float:
    if sold_total <= 0 or window_months <= 0:
        return 0.0
    return sold_total / window_months


def round_or_none(value: float | None, digits: int = 2) -> float | None:
    return None if value is None else round(value, digits)


def median(values: list[float]) -> float | None:
    clean = sorted(v for v in values if v is not None)
    if not clean:
        return None
    mid = len(clean) // 2
    if len(clean) % 2:
        return clean[mid]
    return (clean[mid - 1] + clean[mid]) / 2
