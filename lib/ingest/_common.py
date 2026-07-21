"""Shared helpers for manual ingest handlers."""
from __future__ import annotations

import logging
import re
from pathlib import Path

logger = logging.getLogger("bpc_intel.ingest")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MANUAL_DIR = PROJECT_ROOT / "data" / "manual"

# Maps external category names (lowercased) -> taxonomy segment ids.
CATEGORY_MAP: dict[str, str] = {
    "beauty and personal care": "total_bpc",
    "beauty & personal care": "total_bpc",
    "bpc": "total_bpc",
    "skin care": "skincare",
    "skincare": "skincare",
    "facial care": "skincare",
    "sun care": "sun_care",
    "sun protection": "sun_care",
    "colour cosmetics": "colour_cosmetics",
    "color cosmetics": "colour_cosmetics",
    "make-up": "colour_cosmetics",
    "makeup": "colour_cosmetics",
    "fragrances": "fragrances",
    "fragrance": "fragrances",
    "hair care": "hair_care",
    "haircare": "hair_care",
    "bath and shower": "bath_shower",
    "bath & shower": "bath_shower",
    "deodorants": "deodorants",
    "oral care": "oral_care",
    "oral hygiene": "oral_care",
    "men's grooming": "mens_grooming",
    "mens grooming": "mens_grooming",
    "male grooming": "mens_grooming",
    "baby and child-specific products": "baby_child",
    "baby and child": "baby_child",
    "dermocosmetics": "dermocosmetics",
    "derma": "dermocosmetics",
}

GEO_MAP: dict[str, str] = {
    "south korea": "KR", "korea": "KR", "republic of korea": "KR", "kr": "KR",
    "india": "IN", "in": "IN",
}

_YEAR_RE = re.compile(r"^(19|20)\d{2}$")
_FY_RE = re.compile(r"^FY\d{2,4}$", re.IGNORECASE)


def map_category(name: str) -> str | None:
    """Map an external category name to a taxonomy segment id (or None)."""
    return CATEGORY_MAP.get(name.strip().lower())


def map_geography(name: str) -> str | None:
    """Map a geography name to KR/IN (or None if out of scope)."""
    return GEO_MAP.get(name.strip().lower())


def is_year_column(col: str) -> bool:
    """True if a column header looks like a year or FY label."""
    c = str(col).strip()
    return bool(_YEAR_RE.match(c) or _FY_RE.match(c))


def parse_number(raw: object) -> float | None:
    """Parse a numeric cell tolerant of thousands separators and blanks."""
    s = str(raw).strip().replace(",", "")
    if not s or s in {"-", "–", "nan", "None", "n/a", "N/A"}:
        return None
    try:
        return float(s)
    except ValueError:
        return None


__all__ = ["CATEGORY_MAP", "GEO_MAP", "map_category", "map_geography",
           "is_year_column", "parse_number", "MANUAL_DIR", "PROJECT_ROOT"]
