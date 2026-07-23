"""Canonical data schemas and validators for bpc-intel."""
from __future__ import annotations

import json
import logging
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Literal, Optional

import yaml
from pydantic import BaseModel, ValidationError, model_validator

logger = logging.getLogger("bpc_intel.schema")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TAXONOMY_PATH = PROJECT_ROOT / "config" / "taxonomy.yaml"


class DataPoint(BaseModel):
    geography: Literal["KR", "IN"]
    segment: str                        # Must match taxonomy.yaml segment.id
    sub_segment: Optional[str] = None   # Must match taxonomy.yaml if present
    metric: Literal[
        "market_size", "growth_yoy", "cagr_historical", "cagr_forecast",
        "market_share", "revenue", "export_value", "production_value",
        "channel_share", "per_capita_spend", "penetration_rate",
        # Value-chain metrics (India deep-research extension)
        "import_value",        # goods imported (customs)
        "import_dependence",   # imports as % of market/consumption
        "retail_price",        # a product's shelf price (MRP for India)
        "gross_margin",        # (revenue - COGS) / revenue, %
        "operating_margin",    # operating profit / revenue, %
        "adspend_ratio",       # advertising & promotion / revenue, %
        "trade_margin",        # distributor + retailer markup, %
    ]
    value: float
    unit: str                           # "usd_bn", "krw_tn", "inr_cr", "percent", "usd", "inr"
    currency: Literal["USD", "KRW", "INR"]
    period: str                         # "2024", "FY25", "2020-2024", "H1_2025"
    period_type: Literal["CY", "FY", "H1", "H2", "Q1", "Q2", "Q3", "Q4", "range"]
    value_basis: Literal[
        "RETAIL", "NET_REALISATION", "WHOLESALE", "EXPORT_FOB", "PRODUCTION",
        "IMPORT_CIF",   # customs import value (cost-insurance-freight)
        "MRP",          # maximum retail price (India shelf price, tax+margin incl.)
        "NA",           # basis not applicable (e.g. a ratio/margin/dependence %)
    ]
    tier: Optional[Literal["premium", "masstige", "mass"]] = None
    source_name: str
    source_url: Optional[str] = None
    date_accessed: date
    confidence: Literal["HIGH", "MEDIUM", "LOW", "ESTIMATE"]
    methodology: Optional[str] = None   # Required if confidence == "ESTIMATE"
    notes: Optional[str] = None

    @model_validator(mode="after")
    def _require_methodology_for_estimates(self) -> DataPoint:
        if self.confidence == "ESTIMATE" and not self.methodology:
            raise ValueError("methodology is required when confidence is ESTIMATE")
        return self


class SegmentFile(BaseModel):
    """One file per segment × geography in data/processed/."""

    geography: Literal["KR", "IN"]
    segment: str
    last_updated: date
    data_points: list[DataPoint]


@lru_cache(maxsize=1)
def _load_taxonomy() -> dict:
    """Load and cache config/taxonomy.yaml.

    Returns:
        The parsed taxonomy dictionary.

    Raises:
        FileNotFoundError: If taxonomy.yaml is missing.
    """
    with TAXONOMY_PATH.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def taxonomy_segments() -> dict[str, list[str]]:
    """Map segment id -> list of sub-segment ids from the taxonomy.

    Returns:
        Dict of segment id to its sub-segment ids (empty list if none).
    """
    tax = _load_taxonomy()
    return {
        seg["id"]: seg.get("sub_segments") or []
        for seg in tax["segments"]
    }


# Aggregate levels that are valid in processed data but are not taxonomy
# segments: "total_bpc" = the whole BPC market for a geography.
AGGREGATE_SEGMENTS = {"total_bpc"}


def validate_segment(segment_id: str, sub_segment: str | None = None) -> bool:
    """Check a segment (and optional sub-segment) against taxonomy.yaml.

    Args:
        segment_id: Segment id, e.g. "skincare", or an aggregate ("total_bpc").
        sub_segment: Optional sub-segment id, e.g. "sheet_masks".

    Returns:
        True if the segment (and sub-segment, if given) exists in the taxonomy.
    """
    if segment_id in AGGREGATE_SEGMENTS:
        return sub_segment is None
    segments = taxonomy_segments()
    if segment_id not in segments:
        return False
    if sub_segment is not None and sub_segment not in segments[segment_id]:
        return False
    return True


def validate_data_point(dp: DataPoint) -> tuple[bool, str]:
    """Fully validate a DataPoint, including taxonomy membership.

    Args:
        dp: The DataPoint to validate.

    Returns:
        (is_valid, reason). Reason is "" when valid.
    """
    if not validate_segment(dp.segment, dp.sub_segment):
        return False, (
            f"segment '{dp.segment}' / sub_segment '{dp.sub_segment}' "
            "not found in taxonomy.yaml"
        )
    return True, ""


def load_segment_file(path: str | Path) -> SegmentFile:
    """Load a SegmentFile from a processed JSON file.

    Args:
        path: Path to the JSON file in data/processed/.

    Returns:
        The parsed SegmentFile.

    Raises:
        FileNotFoundError: If the file does not exist.
        pydantic.ValidationError: If the file does not conform to the schema.
    """
    path = Path(path)
    with path.open(encoding="utf-8") as fh:
        payload = json.load(fh)
    return SegmentFile.model_validate(payload)


def save_segment_file(sf: SegmentFile, path: str | Path) -> Path:
    """Save a SegmentFile as JSON.

    Args:
        sf: The SegmentFile to save.
        path: Destination path.

    Returns:
        The path written.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(sf.model_dump_json(indent=2), encoding="utf-8")
    logger.info("Saved %d data points to %s", len(sf.data_points), path)
    return path


__all__ = [
    "DataPoint",
    "SegmentFile",
    "ValidationError",
    "validate_segment",
    "validate_data_point",
    "load_segment_file",
    "save_segment_file",
    "taxonomy_segments",
    "PROJECT_ROOT",
]
