"""Shared loaders for the analysis layer: read processed DataPoints."""
from __future__ import annotations

import logging
import re
from pathlib import Path

from lib.transforms.schema import DataPoint, load_segment_file

logger = logging.getLogger("bpc_intel.analysis")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

_COMPANY_RE = re.compile(r"Company:\s*([^—;()]+?)(?:\s*[—;(]|$)")

# Canonical company names — collapse cross-source variants to one entity.
_COMPANY_ALIASES = {
    "honasa": "Honasa Consumer",
    "honasa consumer": "Honasa Consumer",
    "hindustan unilever": "Hindustan Unilever",
    "hul": "Hindustan Unilever",
    "godrej consumer products": "Godrej Consumer Products",
    "nykaa": "Nykaa (FSN E-Commerce)",
    "nykaa (fsn e-commerce)": "Nykaa (FSN E-Commerce)",
    "amorepacific": "AmorePacific",
    "lg h&h": "LG H&H",
    "cosmax": "Cosmax",
    "kolmar korea": "Kolmar Korea",
    "cj olive young": "CJ Olive Young",
}


def canonical_company(name: str) -> str:
    """Map a raw company name to its canonical form (variant-collapsing)."""
    return _COMPANY_ALIASES.get(name.strip().lower(), name.strip())

# Period ordering: newer periods sort higher. Extracts the end year.
_YEAR_RE = re.compile(r"(\d{4})|FY(\d{2})")


def load_points(
    geography: str,
    segment: str,
    processed_dir: str | Path | None = None,
) -> list[DataPoint]:
    """Load all DataPoints for a geography × segment file.

    Args:
        geography: "KR" or "IN".
        segment: Taxonomy segment id (or "total_bpc").
        processed_dir: Processed-data directory (defaults to PROCESSED_DIR,
            resolved at call time so tests can redirect it).

    Returns:
        The file's DataPoints, or [] if the file does not exist.
    """
    base = Path(processed_dir) if processed_dir is not None else PROCESSED_DIR
    path = base / f"{geography}_{segment}.json"
    if not path.exists():
        logger.info("No processed file for %s/%s", geography, segment)
        return []
    return load_segment_file(path).data_points


def period_end_year(period: str) -> int:
    """Best-effort end year for sorting periods ('FY24'->2024, '2020-2024'->2024)."""
    years = [int(y) for y in re.findall(r"\d{4}", period)]
    if years:
        return max(years)
    m = re.search(r"FY(\d{2})", period)
    return 2000 + int(m.group(1)) if m else 0


def company_name(dp: DataPoint) -> str | None:
    """Extract a canonical company name from notes ('Company: X — ...')."""
    if not dp.notes:
        return None
    m = _COMPANY_RE.search(dp.notes)
    return canonical_company(m.group(1)) if m else None


def latest_company_revenues(points: list[DataPoint]) -> dict[str, DataPoint]:
    """Latest revenue DataPoint per named company.

    Args:
        points: DataPoints (typically a total_bpc file).

    Returns:
        {company_name: latest revenue DataPoint}. Only revenue metrics with a
        parseable company name are included.
    """
    best: dict[str, DataPoint] = {}
    for dp in points:
        if dp.metric != "revenue":
            continue
        name = company_name(dp)
        if name is None:
            continue
        if name not in best or period_end_year(dp.period) > period_end_year(best[name].period):
            best[name] = dp
    return best


__all__ = [
    "load_points", "period_end_year", "company_name",
    "latest_company_revenues", "PROCESSED_DIR",
]
