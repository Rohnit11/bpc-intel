"""Generic CSV ingest — freeform files with an explicit column mapping.

For BMI Research, IBEF downloads, and anything without a dedicated handler.
The caller supplies a mapping config describing which column holds what, so
no guessing happens against unknown layouts.
"""
from __future__ import annotations

import logging
from datetime import date
from pathlib import Path

from lib.ingest._common import map_category, map_geography, parse_number
from lib.transforms.schema import DataPoint, validate_segment

logger = logging.getLogger("bpc_intel.ingest.generic")

# A mapping is a dict like:
# {
#   "column_map": {"category": "Segment", "geography": "Country",
#                  "value": "Value2024", "period": "2024"},
#   "metric": "market_size", "unit": "usd_bn", "currency": "USD",
#   "value_basis": "RETAIL", "confidence": "MEDIUM",
#   "source_name": "BMI Research", "period_type": "CY",
# }


def parse(csv_path: str | Path, mapping: dict) -> list[DataPoint]:
    """Parse an arbitrary CSV using an explicit mapping.

    Args:
        csv_path: Path to the CSV.
        mapping: Column mapping + fixed metadata (see module docstring).

    Returns:
        Validated DataPoints.

    Raises:
        KeyError: If the mapping omits a required key.
        ValueError: If a mapped column is absent or a fixed segment is invalid.
    """
    import pandas as pd

    csv_path = Path(csv_path)
    for key in ("column_map", "metric", "unit", "currency", "source_name"):
        if key not in mapping:
            raise KeyError(f"mapping missing required key '{key}'")

    df = pd.read_csv(csv_path)
    cmap = mapping["column_map"]
    value_col = cmap["value"]
    if value_col not in df.columns:
        raise ValueError(f"Value column '{value_col}' not in {list(df.columns)}")

    fixed_segment = mapping.get("segment")
    if fixed_segment and not validate_segment(fixed_segment):
        raise ValueError(f"Fixed segment '{fixed_segment}' not in taxonomy.yaml")

    points: list[DataPoint] = []
    for _, row in df.iterrows():
        geography = (mapping.get("geography")
                     or (map_geography(str(row[cmap["geography"]]))
                         if "geography" in cmap else None))
        if geography is None:
            logger.warning("Row skipped: no in-scope geography")
            continue
        segment = fixed_segment or (map_category(str(row[cmap["category"]]))
                                    if "category" in cmap else None)
        if segment is None:
            logger.warning("Row skipped: unmapped category")
            continue
        value = parse_number(row[value_col])
        if value is None:
            continue
        period = (mapping.get("period")
                  or (str(row[cmap["period"]]).strip() if "period" in cmap else None))
        if period is None:
            raise ValueError("mapping must supply 'period' or column_map['period']")
        points.append(DataPoint(
            geography=geography, segment=segment, metric=mapping["metric"],
            value=value, unit=mapping["unit"], currency=mapping["currency"],
            period=period, period_type=mapping.get("period_type", "CY"),
            value_basis=mapping.get("value_basis", "RETAIL"),
            source_name=mapping["source_name"], date_accessed=date.today(),
            confidence=mapping.get("confidence", "MEDIUM"),
            methodology=mapping.get("methodology"),
            notes=mapping.get("notes", f"Generic ingest ({csv_path.name})"),
        ))
    logger.info("Parsed %d DataPoints from generic export %s", len(points), csv_path.name)
    return points


__all__ = ["parse"]
