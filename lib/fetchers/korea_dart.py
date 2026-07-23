"""DART (Korean EDGAR) — company filings for listed Korean beauty companies.

Free API key: register at https://opendart.fss.or.kr. Put it in
config/api_keys.yaml under `dart:` (copy api_keys.yaml.template).
"""
from __future__ import annotations

import logging
from datetime import date

from lib.fetchers._base import DEFAULT_TIMEOUT, load_api_keys, save_raw, session
from lib.transforms.merge import upsert_data_points
from lib.transforms.schema import DataPoint

logger = logging.getLogger("bpc_intel.fetchers.dart")

DART_ENDPOINT = "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json"

# corp_code is DART's 8-digit internal id (not the ticker). Verified against
# DART's corpCode registry by stock ticker (2026-07-23) — the earlier codes for
# LG H&H/Cosmax/Kolmar pointed at the wrong entities (LG Chem, a no-data code,
# and Meritz Financial Holdings respectively).
TARGETS = [
    {"name": "AmorePacific", "stock_code": "090430", "corp_code": "00583424"},
    {"name": "LG H&H", "stock_code": "051900", "corp_code": "00356370"},
    {"name": "Cosmax", "stock_code": "192820", "corp_code": "01009789"},
    {"name": "Kolmar Korea", "stock_code": "161890", "corp_code": "00939331"},
]

_REVENUE_ACCOUNTS = {"ifrs-full_Revenue", "ifrs_Revenue"}
# Revenue is reported on the income statement (IS) or, when a filer presents a
# combined statement of comprehensive income (AmorePacific), on CIS. Match both;
# to_data_points takes the first revenue line found per company.
_REVENUE_STATEMENTS = {"IS", "CIS"}

# DART status codes that mean the KEY is the problem, so retrying the same
# request with a fallback key can succeed: 010 unregistered, 011 deactivated/
# suspended, 020 daily request limit exceeded. Other non-"000" statuses
# (013 no-data, 100 bad param, 800 maintenance) are key-agnostic — no failover.
_KEY_FAILURE_STATUSES = {"010", "011", "020"}


def _request_financials(sess, corp_code: str, year: int, api_keys: list[str]) -> dict | None:
    """Fetch one company's annual financials, failing over across keys.

    Tries each key in priority order, advancing to the next only when the
    current key is rejected for a key-specific reason (invalid/deactivated/
    limit-exceeded) or the HTTP request errors. A key-agnostic payload
    (status "000", or e.g. "013" no-data) is returned immediately.

    Args:
        sess: A requests session.
        corp_code: DART 8-digit corp code.
        year: Business year.
        api_keys: Keys to try, primary first (from load_api_keys("dart")).

    Returns:
        The DART JSON payload from the first key that got a usable response, or
        the last key-failure payload if every key was rejected, or None if
        every attempt raised.
    """
    import requests

    last_failure: dict | None = None
    for idx, api_key in enumerate(api_keys):
        params = {
            "crtfc_key": api_key,
            "corp_code": corp_code,
            "bsns_year": str(year),
            "reprt_code": "11011",  # annual report
            "fs_div": "CFS",        # consolidated
        }
        try:
            resp = sess.get(DART_ENDPOINT, params=params, timeout=DEFAULT_TIMEOUT)
            resp.raise_for_status()
            payload = resp.json()
        except (requests.RequestException, ValueError) as exc:
            logger.error("DART request errored on key #%d for %s: %s", idx + 1, corp_code, exc)
            continue  # transient/HTTP issue — try the next key
        if payload.get("status") in _KEY_FAILURE_STATUSES:
            logger.warning(
                "DART key #%d rejected for %s (status %s: %s) — trying next key",
                idx + 1, corp_code, payload.get("status"), payload.get("message"),
            )
            last_failure = payload
            continue  # key-specific failure — fail over to the fallback key
        return payload  # usable response (success or key-agnostic status)
    return last_failure


def fetch(year: int | None = None) -> list[dict]:
    """Fetch latest annual-report financials for each target company.

    Args:
        year: Business year to request (default: last calendar year).

    Returns:
        Raw records, one per company. Empty list if no API key or on failure.
    """
    api_keys = load_api_keys("dart")
    if not api_keys:
        logger.warning(
            "No DART API key configured. Register (free) at "
            "https://opendart.fss.or.kr, then copy config/api_keys.yaml.template "
            "to config/api_keys.yaml and set `dart:` (and optionally "
            "`dart_fallback:`). Skipping DART fetch."
        )
        return []

    year = year or (date.today().year - 1)
    records: list[dict] = []
    sess = session()
    logger.info("DART fetch using %d key(s) (primary + %d fallback)",
                len(api_keys), len(api_keys) - 1)
    for target in TARGETS:
        payload = _request_financials(sess, target["corp_code"], year, api_keys)
        if payload is None:
            logger.error("DART fetch failed for %s: every key errored", target["name"])
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
            if row.get("account_id") in _REVENUE_ACCOUNTS and row.get("sj_div") in _REVENUE_STATEMENTS:
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
