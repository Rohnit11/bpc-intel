"""Euromonitor Passport CSV ingest — market sizes, brand shares, forecasts.

Passport exports come in three shapes; the handler auto-detects:

1. **Market size:** Category rows x year columns, one geography per file
   (or a Geography column). Values in local currency or USD mn.
2. **Brand shares:** Brand/Company rows x year columns, values in % share.
3. **Forecast:** same as market size but future years — detected when all
   year columns are ahead of the current year.

All Passport data is confidence HIGH and value_basis RETAIL (Passport
reports RSP — retail selling price). India Passport values are MRP-inclusive.
"""
from __future__ import annotations

import logging
from datetime import date
from pathlib import Path

from lib.ingest._common import is_year_column, map_category, map_geography, parse_number
from lib.transforms.schema import DataPoint

logger = logging.getLogger("bpc_intel.ingest.passport")

_UNIT_HINTS = {
    "usd mn": ("usd_mn", "USD"), "us$ mn": ("usd_mn", "USD"),
    "usd million": ("usd_mn", "USD"),
    "inr mn": ("inr_mn", "INR"), "inr bn": ("inr_bn", "INR"),
    "krw bn": ("krw_bn", "KRW"), "krw mn": ("krw_mn", "KRW"),
    "% retail value": ("percent", "USD"), "% value": ("percent", "USD"),
}


def detect_table_type(df) -> str:
    """Classify a Passport export: market_size, brand_share, or forecast.

    Args:
        df: The loaded DataFrame.

    Returns:
        One of "market_size", "brand_share", "forecast".
    """
    cols_lower = [str(c).strip().lower() for c in df.columns]
    if any(c in {"brand", "company", "gbo", "nbo"} for c in cols_lower):
        return "brand_share"
    year_cols = [int(str(c)[:4]) for c in df.columns if is_year_column(c)]
    if year_cols and min(year_cols) > date.today().year:
        return "forecast"
    return "market_size"


def _resolve_unit(df, unit_hint: str | None) -> tuple[str, str]:
    """Resolve (unit, currency) from a Unit column or explicit hint."""
    if unit_hint:
        key = unit_hint.strip().lower()
        if key in _UNIT_HINTS:
            return _UNIT_HINTS[key]
        raise ValueError(f"Unknown unit hint '{unit_hint}'. Known: {list(_UNIT_HINTS)}")
    for col in df.columns:
        if str(col).strip().lower() == "unit":
            raw = str(df[col].iloc[0]).strip().lower()
            if raw in _UNIT_HINTS:
                return _UNIT_HINTS[raw]
    raise ValueError(
        "Could not determine unit. Add a 'Unit' column (e.g. 'USD mn') to the "
        "CSV or pass unit_hint."
    )


def parse(
    csv_path: str | Path,
    geography: str | None = None,
    unit_hint: str | None = None,
    segment: str | None = None,
) -> list[DataPoint]:
    """Parse a Passport CSV export into DataPoints.

    Args:
        csv_path: Path to the exported CSV.
        geography: "KR" or "IN" if the file has no Geography column.
        unit_hint: e.g. "USD mn" if the file has no Unit column.
        segment: Taxonomy segment id for brand-share files that have no
            category column (e.g. a total-BPC company-shares export).

    Returns:
        Validated DataPoints.

    Raises:
        ValueError: On missing geography/unit information or no year columns.
    """
    import pandas as pd

    csv_path = Path(csv_path)
    df = pd.read_csv(csv_path)
    table_type = detect_table_type(df)
    cols = {str(c).strip().lower(): c for c in df.columns}

    year_cols = [c for c in df.columns if is_year_column(c)]
    if not year_cols:
        raise ValueError("No year columns found in Passport CSV.")

    geo_col = cols.get("geography") or cols.get("country")
    if geo_col is None and geography is None:
        raise ValueError("No Geography column — pass geography='KR' or 'IN'.")

    if table_type == "brand_share":
        unit, currency = "percent", "USD"
        metric = "market_share"
        entity_col = (cols.get("brand") or cols.get("company")
                      or cols.get("gbo") or cols.get("nbo"))
        value_note = "Brand/company retail value share (Passport)"
    else:
        unit, currency = _resolve_unit(df, unit_hint)
        metric = "cagr_forecast" if table_type == "forecast" else "market_size"
        entity_col = None
        value_note = "Passport RSP retail value"
        if metric == "cagr_forecast":
            metric = "market_size"  # forecast years are still sizes; period marks the year
            value_note = "Passport forecast (RSP retail value)"

    # A real category column, if any. For brand-share files the first column
    # is the entity (brand/company), not a category — don't fall back to it.
    cat_col = cols.get("category") or cols.get("segment")
    if cat_col is None and table_type != "brand_share":
        cat_col = df.columns[0]
    default_segment = segment or ("total_bpc" if table_type == "brand_share" else None)

    points: list[DataPoint] = []
    for _, row in df.iterrows():
        geo = geography or map_geography(str(row[geo_col]))
        if geo is None:
            logger.warning("Skipping out-of-scope geography: %s", row.get(geo_col))
            continue
        seg = map_category(str(row[cat_col])) if cat_col is not None else default_segment
        if seg is None:
            logger.warning("Skipping unmapped Passport category: %s",
                           row[cat_col] if cat_col is not None else "(no category column)")
            continue
        entity = f"Brand/Company: {str(row[entity_col]).strip()} — " if entity_col else ""
        for yc in year_cols:
            value = parse_number(row[yc])
            if value is None:
                continue
            year = str(yc).strip()
            points.append(DataPoint(
                geography=geo, segment=seg, metric=metric,
                value=value, unit=unit, currency=currency,
                period=year, period_type="CY",
                value_basis="RETAIL",
                source_name="Euromonitor Passport",
                date_accessed=date.today(), confidence="HIGH",
                notes=f"{entity}{value_note} ({csv_path.name})"
                      + ("; India values MRP-inclusive" if geo == "IN" else ""),
            ))
    logger.info("Parsed %d DataPoints from Passport export %s (%s)",
                len(points), csv_path.name, table_type)
    return points


__all__ = ["parse", "detect_table_type"]
