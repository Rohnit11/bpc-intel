"""Screener.in — 10-year P&L for listed Indian BPC companies.

Free, no login needed for the consolidated P&L table. Rate-limited to one
request per 2 seconds per the build spec.
"""
from __future__ import annotations

import logging
import time
from datetime import date
from io import StringIO

from lib.fetchers._base import DEFAULT_TIMEOUT, save_raw, session
from lib.transforms.merge import upsert_data_points
from lib.transforms.schema import DataPoint

logger = logging.getLogger("bpc_intel.fetchers.screener")

RATE_LIMIT_SECONDS = 2.0

TARGETS = [
    {"name": "Hindustan Unilever", "slug": "HINDUNILVR"},
    {"name": "Nykaa (FSN E-Commerce)", "slug": "NYKAA"},
    {"name": "Honasa Consumer", "slug": "HONASA"},
    {"name": "Godrej Consumer Products", "slug": "GODREJCP"},
]


def fetch() -> list[dict]:
    """Scrape the consolidated P&L table for each target company.

    Returns:
        Raw records: {company, slug, url, tables: [csv-strings]}. Companies
        that fail are skipped with an ERROR log; never crashes.
    """
    import pandas as pd
    import requests

    records: list[dict] = []
    sess = session()
    for i, target in enumerate(TARGETS):
        if i:
            time.sleep(RATE_LIMIT_SECONDS)
        url = f"https://www.screener.in/company/{target['slug']}/consolidated/"
        try:
            resp = sess.get(url, timeout=DEFAULT_TIMEOUT)
            resp.raise_for_status()
            tables = pd.read_html(StringIO(resp.text))
        except (requests.RequestException, ValueError, ImportError) as exc:
            logger.error("Screener fetch failed for %s: %s", target["name"], exc)
            continue
        records.append({
            "company": target["name"], "slug": target["slug"], "url": url,
            "tables": [t.to_csv(index=False) for t in tables],
        })
        logger.info("Fetched %d tables from Screener for %s", len(tables), target["name"])
    return records


def _clean_labels(series):
    """Normalise row labels: NBSP -> space, strip trailing '+' markers."""
    return (series.astype(str)
            .str.replace("\xa0", " ", regex=False)
            .str.strip().str.rstrip("+").str.strip())


def _find_pl_table(tables_csv: list[str]):
    """Locate the ANNUAL P&L table: a 'Sales' row and all-Mar year columns.

    Screener also serves a quarterly P&L (Mar/Jun/Sep/Dec columns); requiring
    every data column to be 'Mar ...' (TTM allowed) selects the annual one.
    """
    import pandas as pd

    for csv_text in tables_csv:
        df = pd.read_csv(StringIO(csv_text))
        rows = _clean_labels(df[df.columns[0]])
        data_cols = [str(c) for c in df.columns[1:]]
        if not data_cols:
            continue
        all_annual = all(c.startswith("Mar") or c == "TTM" for c in data_cols)
        if rows.str.fullmatch("Sales", case=False).any() and all_annual:
            return df
    return None


def to_data_points(raw_records: list[dict]) -> list[DataPoint]:
    """Extract annual Sales (revenue) per fiscal year as DataPoints.

    Screener's 'Sales' line is reported net revenue in Rs crore; columns are
    'Mar 2016'...'Mar 2025' (Indian FY ends March).

    Args:
        raw_records: Records from fetch().

    Returns:
        Revenue DataPoints per company x fiscal year.
    """
    import pandas as pd

    points: list[DataPoint] = []
    for rec in raw_records:
        df = _find_pl_table(rec["tables"])
        if df is None:
            logger.warning("No P&L table found for %s", rec["company"])
            continue
        labels = _clean_labels(df[df.columns[0]])
        sales_rows = df[labels.str.fullmatch("Sales", case=False)]
        if sales_rows.empty:
            logger.warning("No Sales row for %s", rec["company"])
            continue
        sales = sales_rows.iloc[0]
        for col in df.columns[1:]:
            col_s = str(col)
            if not col_s.startswith("Mar"):
                continue
            try:
                value = float(str(sales[col]).replace(",", ""))
            except ValueError:
                continue
            fy = f"FY{col_s.split()[-1][-2:]}"
            points.append(DataPoint(
                geography="IN", segment="total_bpc", metric="revenue",
                value=value, unit="inr_cr", currency="INR",
                period=fy, period_type="FY", value_basis="NET_REALISATION",
                source_name="Screener.in (consolidated P&L)",
                source_url=rec["url"], date_accessed=date.today(),
                confidence="HIGH",
                notes=f"Company: {rec['company']} — annual Sales line; organised sector",
            ))
    logger.info("Converted Screener tables to %d revenue DataPoints", len(points))
    return points


def run(output_dir: str = "data/raw/") -> str:
    """Full pipeline: fetch -> save raw -> convert -> merge into processed.

    Returns:
        Path to raw output, or '' if nothing was fetched.
    """
    records = fetch()
    if not records:
        return ""
    raw_path = save_raw("screener", records, output_dir)
    points = to_data_points(records)
    if points:
        upsert_data_points(points)
    return str(raw_path)


__all__ = ["fetch", "to_data_points", "run", "TARGETS"]
