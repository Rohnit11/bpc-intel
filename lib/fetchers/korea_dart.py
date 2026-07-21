"""DART (Korean EDGAR) — company filings for listed Korean beauty companies.

Free API key: register at https://opendart.fss.or.kr. Put it in
config/api_keys.yaml under `dart:` (copy api_keys.yaml.template).
"""
from __future__ import annotations

import logging
from datetime import date

from lib.fetchers._base import DEFAULT_TIMEOUT, load_api_key, save_raw, session
from lib.transforms.merge import upsert_data_points
from lib.transforms.schema import DataPoint

logger = logging.getLogger("bpc_intel.fetchers.dart")

DART_ENDPOINT = "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json"

# corp_code is DART's 8-digit internal id (not the ticker).
TARGETS = [
    {"name": "AmorePacific", "stock_code": "090430", "corp_code": "00583424"},
    {"name": "LG H&H", "stock_code": "051900", "corp_code": "00356361"},
    {"name": "Cosmax", "stock_code": "192820", "corp_code": "00970538"},
    {"name": "Kolmar Korea", "stock_code": "161890", "corp_code": "00860332"},
]

_REVENUE_ACCOUNTS = {"ifrs-full_Revenue", "ifrs_Revenue"}


def fetch(year: int | None = None) -> list[dict]:
    """Fetch latest annual-report financials for each target company.

    Args:
        year: Business year to request (default: last calendar year).

    Returns:
        Raw records, one per company. Empty list if no API key or on failure.
    """
    api_key = load_api_key("dart")
    if api_key is None:
        logger.warning(
            "No DART API key configured. Register (free) at "
            "https://opendart.fss.or.kr, then copy config/api_keys.yaml.template "
            "to config/api_keys.yaml and set `dart:`. Skipping DART fetch."
        )
        return []

    import requests

    year = year or (date.today().year - 1)
    records: list[dict] = []
    sess = session()
    for target in TARGETS:
        params = {
            "crtfc_key": api_key,
            "corp_code": target["corp_code"],
            "bsns_year": str(year),
            "reprt_code": "11011",  # annual report
            "fs_div": "CFS",        # consolidated
        }
        try:
            resp = sess.get(DART_ENDPOINT, params=params, timeout=DEFAULT_TIMEOUT)
            resp.raise_for_status()
            payload = resp.json()
        except (requests.RequestException, ValueError) as exc:
            logger.error("DART fetch failed for %s: %s", target["name"], exc)
            continue
        if payload.get("status") != "000":
            logger.warning("DART returned status %s for %s (%s)",
                           payload.get("status"), target["name"], payload.get("message"))
            continue
        records.append({"company": target["name"], "year": year,
                        "rows": payload.get("list", [])})
        logger.info("Fetched %d filing rows from DART for %s CY%d",
                    len(payload.get("list", [])), target["name"], year)
    return records


def to_data_points(raw_records: list[dict]) -> list[DataPoint]:
    """Extract consolidated revenue as DataPoints.

    Args:
        raw_records: Records from fetch().

    Returns:
        One revenue DataPoint per company where a revenue line was found.
    """
    points: list[DataPoint] = []
    for rec in raw_records:
        for row in rec["rows"]:
            if row.get("account_id") in _REVENUE_ACCOUNTS and row.get("sj_div") == "CIS":
                raw_amount = str(row.get("thstrm_amount", "")).replace(",", "")
                if not raw_amount.lstrip("-").isdigit():
                    continue
                krw_tn = int(raw_amount) / 1e12
                points.append(DataPoint(
                    geography="KR", segment="total_bpc", metric="revenue",
                    value=round(krw_tn, 3), unit="krw_tn", currency="KRW",
                    period=str(rec["year"]), period_type="CY",
                    value_basis="NET_REALISATION",
                    source_name="DART (FSS) annual filing",
                    source_url="https://dart.fss.or.kr",
                    date_accessed=date.today(), confidence="HIGH",
                    notes=f"Company: {rec['company']} — consolidated revenue from DART",
                ))
                break
    logger.info("Converted DART filings to %d revenue DataPoints", len(points))
    return points


def run(output_dir: str = "data/raw/") -> str:
    """Full pipeline: fetch -> save raw -> convert -> merge into processed.

    Returns:
        Path to the raw output file, or '' if nothing was fetched.
    """
    records = fetch()
    if not records:
        return ""
    raw_path = save_raw("dart", records, output_dir)
    points = to_data_points(records)
    if points:
        upsert_data_points(points)
    return str(raw_path)


__all__ = ["fetch", "to_data_points", "run", "TARGETS"]
