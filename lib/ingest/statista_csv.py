"""Statista CSV ingest — chart data exports (simple year,value pairs).

Statista chart exports are typically two columns (year, value) with no
category/geography metadata, so the caller must supply segment, geography,
metric, unit, and currency at ingest time.
"""
from __future__ import annotations

import logging
from datetime import date
from pathlib import Path

from lib.ingest._common import is_year_column, parse_number
from lib.transforms.schema import DataPoint, validate_segment

logger = logging.getLogger("bpc_intel.ingest.statista")

_UNIT_CURRENCY = {
    "usd_bn": "USD", "usd_mn": "USD", "usd": "USD",
    "inr_cr": "INR", "inr_bn": "INR", "inr_mn": "INR",
    "krw_tn": "KRW", "krw_bn": "KRW",
    "percent": "USD",
}


def parse(
    csv_path: str | Path,
    *,
    geography: str,
    segment: str,
    metric: str,
    unit: str,
    value_basis: str = "RETAIL",
    confidence: str = "MEDIUM",
) -> list[DataPoint]:
    """Parse a Statista two-column export into DataPoints.

    Args:
        csv_path: Path to the exported CSV.
        geography: "KR" or "IN".
        segment: Taxonomy segment id (validated).
        metric: A DataPoint metric literal, e.g. "market_size".
        unit: e.g. "usd_bn" (currency inferred).
        value_basis: Default "RETAIL" (Statista consumer-market series).
        confidence: Default "MEDIUM" per CLAUDE.md (credible secondary).

    Returns:
        Validated DataPoints.

    Raises:
        ValueError: On unknown segment/unit or missing year/value columns.
    """
    import pandas as pd

    csv_path = Path(csv_path)
    if not validate_segment(segment):
        raise ValueError(f"Segment '{segment}' not in taxonomy.yaml")
    currency = _UNIT_CURRENCY.get(unit)
    if currency is None:
        raise ValueError(f"Unknown unit '{unit}'. Known: {list(_UNIT_CURRENCY)}")

    df = pd.read_csv(csv_path)
    year_col = next((c for c in df.columns if is_year_column(df[c].iloc[0])
                     or is_year_column(c) or "year" in str(c).lower()), None)
    value_col = next((c for c in df.columns if c != year_col), None)
    if year_col is None or value_col is None:
        raise ValueError(
            f"Could not identify year/value columns in {csv_path.name}. "
            f"Columns: {list(df.columns)}"
        )

    points: list[DataPoint] = []
    for _, row in df.iterrows():
        year = str(row[year_col]).strip()
        if not is_year_column(year):
            year = str(row[year_col])[:4]
        value = parse_number(row[value_col])
        if value is None or not is_year_column(year):
            continue
        points.append(DataPoint(
            geography=geography, segment=segment, metric=metric,
            value=value, unit=unit, currency=currency,
            period=year, period_type="CY", value_basis=value_basis,
            source_name="Statista", date_accessed=date.today(),
            confidence=confidence,
            notes=f"Statista export ({csv_path.name})",
        ))
    logger.info("Parsed %d DataPoints from Statista export %s", len(points), csv_path.name)
    return points


__all__ = ["parse"]
