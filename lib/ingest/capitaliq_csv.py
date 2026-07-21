"""Capital IQ Pro CSV ingest — company financials export -> DataPoints.

Expected shape (Capital IQ financials exports are metric-rows x year-columns):

    Company,Geography,Metric,Currency,Unit,FY2021,FY2022,FY2023,...
    Hindustan Unilever,India,Total Revenue,INR,cr,52446,58154,61896

Column names are matched case-insensitively. Year columns may be "2024",
"FY24", or "FY2024". Values become NET_REALISATION revenue DataPoints with
confidence HIGH (Capital IQ = primary source per CLAUDE.md) and are linked
to config/companies.yaml names where possible.

Export tip (Capital IQ Pro): company page -> Financials -> Income Statement
-> Export -> CSV. Keep the default annual view.
"""
from __future__ import annotations

import logging
from datetime import date
from pathlib import Path

from lib.ingest._common import is_year_column, map_geography, parse_number
from lib.transforms.schema import DataPoint

logger = logging.getLogger("bpc_intel.ingest.capitaliq")

_METRIC_MAP = {
    "total revenue": "revenue",
    "revenue": "revenue",
    "revenues": "revenue",
    "net sales": "revenue",
}

_UNIT_MAP = {
    ("INR", "cr"): "inr_cr", ("INR", "crore"): "inr_cr",
    ("INR", "bn"): "inr_bn", ("INR", "mn"): "inr_mn",
    ("KRW", "tn"): "krw_tn", ("KRW", "bn"): "krw_bn",
    ("USD", "bn"): "usd_bn", ("USD", "mn"): "usd_mn",
}


def _period(col: str, geography: str) -> tuple[str, str]:
    """Normalise a year column to (period, period_type) per geography."""
    c = str(col).strip().upper()
    if c.startswith("FY"):
        return f"FY{c[-2:]}", "FY"
    if geography == "IN":
        # Capital IQ labels Indian fiscal years by end year
        return f"FY{c[-2:]}", "FY"
    return c, "CY"


def parse(csv_path: str | Path) -> list[DataPoint]:
    """Parse a Capital IQ CSV export into DataPoints.

    Args:
        csv_path: Path to the exported CSV.

    Returns:
        Validated DataPoints (revenue metrics only; other rows are logged and
        skipped).

    Raises:
        ValueError: If required columns are missing.
    """
    import pandas as pd

    csv_path = Path(csv_path)
    df = pd.read_csv(csv_path)
    cols = {str(c).strip().lower(): c for c in df.columns}
    required = ["company", "geography", "metric", "currency", "unit"]
    missing = [c for c in required if c not in cols]
    if missing:
        raise ValueError(
            f"Capital IQ CSV missing required columns {missing}. "
            f"Found: {list(df.columns)}. Expected header: Company, Geography, "
            "Metric, Currency, Unit, then year columns."
        )
    year_cols = [c for c in df.columns if is_year_column(str(c))]
    if not year_cols:
        raise ValueError("No year columns (e.g. 2024, FY24, FY2024) found.")

    points: list[DataPoint] = []
    for _, row in df.iterrows():
        geography = map_geography(str(row[cols["geography"]]))
        if geography is None:
            logger.warning("Skipping out-of-scope geography: %s", row[cols["geography"]])
            continue
        metric = _METRIC_MAP.get(str(row[cols["metric"]]).strip().lower())
        if metric is None:
            logger.warning("Skipping unmapped metric: %s", row[cols["metric"]])
            continue
        currency = str(row[cols["currency"]]).strip().upper()
        unit = _UNIT_MAP.get((currency, str(row[cols["unit"]]).strip().lower()))
        if unit is None or currency not in {"USD", "KRW", "INR"}:
            logger.warning("Skipping unmapped currency/unit: %s/%s",
                           currency, row[cols["unit"]])
            continue
        company = str(row[cols["company"]]).strip()
        for yc in year_cols:
            value = parse_number(row[yc])
            if value is None:
                continue
            period, period_type = _period(str(yc), geography)
            points.append(DataPoint(
                geography=geography, segment="total_bpc", metric=metric,
                value=value, unit=unit, currency=currency,
                period=period, period_type=period_type,
                value_basis="NET_REALISATION",
                source_name="S&P Capital IQ Pro",
                date_accessed=date.today(), confidence="HIGH",
                notes=f"Company: {company} — Capital IQ export ({csv_path.name})",
            ))
    logger.info("Parsed %d DataPoints from %s", len(points), csv_path.name)
    return points


__all__ = ["parse"]
