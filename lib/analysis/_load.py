"""Shared loaders for the analysis layer: read processed DataPoints."""
from __future__ import annotations

import logging
import re
from pathlib import Path

from lib.transforms.schema import DataPoint, load_segment_file

logger = logging.getLogger("bpc_intel.analysis")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

_COMPANY_RE = re.compile(r"Company:\s*([^—;(,]+?)(?:\s*[—;(,]|$)")

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


# Value-chain role per company — brand owners, ODM/OEM manufacturers, and
# retailers operate at DIFFERENT levels; their revenues are not comparable as
# "market share". Sourced from config/companies.yaml groupings.
_ROLE_BY_GROUP = {
    "conglomerates": "brand", "incumbents": "brand", "indie_brands": "brand",
    "d2c_brands": "brand", "platforms": "retailer", "retailers": "retailer",
    "odm_oem": "odm",
}


def _load_company_roles() -> dict[str, str]:
    """Map canonical company name -> role from config/companies.yaml."""
    import yaml
    path = PROJECT_ROOT / "config" / "companies.yaml"
    with path.open(encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    roles: dict[str, str] = {}
    for geo in cfg.values():
        for group, members in geo.items():
            role = _ROLE_BY_GROUP.get(group, "brand")
            for m in members:
                # Strip parenthetical then canonicalize, matching how names are
                # extracted from DataPoint notes.
                stripped = re.sub(r"\s*\(.*\)", "", m["name"])
                roles[canonical_company(stripped)] = role
    return roles


_COMPANY_ROLES = _load_company_roles()


def company_role(name: str) -> str:
    """Value-chain role for a (canonical) company: brand, odm, retailer, or unknown."""
    return _COMPANY_ROLES.get(canonical_company(name), "unknown")

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
    conf_rank = {"HIGH": 3, "MEDIUM": 2, "LOW": 1, "ESTIMATE": 0}
    best: dict[str, DataPoint] = {}
    for dp in points:
        if dp.metric != "revenue":
            continue
        name = company_name(dp)
        if name is None:
            continue
        cur = best.get(name)
        if cur is None:
            best[name] = dp
            continue
        # Prefer the most recent period; on a tie, prefer higher confidence.
        new_key = (period_end_year(dp.period), conf_rank.get(dp.confidence, 0))
        cur_key = (period_end_year(cur.period), conf_rank.get(cur.confidence, 0))
        if new_key > cur_key:
            best[name] = dp
    return best


__all__ = [
    "load_points", "period_end_year", "company_name", "company_role",
    "canonical_company", "latest_company_revenues", "PROCESSED_DIR",
]
