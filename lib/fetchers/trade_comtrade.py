"""UN Comtrade — bilateral cosmetics trade flows (HS 3303-3307).

Corridor core: Korea -> India is a standing query, plus Korea -> World totals.
Free tier ~500 calls/day on the public preview endpoint; an API key in
config/api_keys.yaml (`comtrade:`) raises limits.
"""
from __future__ import annotations

import logging
import time
from datetime import date

from lib.fetchers._base import DEFAULT_TIMEOUT, load_api_key, load_yaml, save_raw, session
from lib.transforms.merge import upsert_data_points
from lib.transforms.schema import DataPoint

logger = logging.getLogger("bpc_intel.fetchers.comtrade")

PREVIEW_ENDPOINT = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"
KEYED_ENDPOINT = "https://comtradeapi.un.org/data/v1/get/C/A/HS"

REPORTER_KOREA = "410"
REPORTER_INDIA = "699"
PARTNER_INDIA = "699"
PARTNER_WORLD = "0"
PARTNER_KOREA = "410"
PARTNER_CHINA = "156"

HS_SEGMENT_MAP = {
    "3303": "fragrances",
    "3304": "skincare",       # also covers makeup; noted per point
    "3305": "hair_care",
    "3306": "oral_care",
    "3307": "total_bpc",      # shave/deo/bath prep — mixed, noted
}

_RATE_LIMIT_SECONDS = 1.5


def _hs_codes() -> list[str]:
    corridor = load_yaml("corridor.yaml").get("corridor", {})
    return corridor.get("monitoring_queries", {}).get("comtrade", {}).get(
        "hs_codes", list(HS_SEGMENT_MAP)
    )


def fetch(year: int | None = None) -> list[dict]:
    """Fetch Korea->India and Korea->World export values per HS code.

    Args:
        year: Data year (default: two years back — Comtrade annual lag).

    Returns:
        Raw records; empty list on total failure. Batched to respect the
        free-tier daily limit (one call per HS x partner).
    """
    import requests

    api_key = load_api_key("comtrade")
    endpoint = KEYED_ENDPOINT if api_key else PREVIEW_ENDPOINT
    year = year or (date.today().year - 2)

    records: list[dict] = []
    sess = session()
    if api_key:
        sess.headers["Ocp-Apim-Subscription-Key"] = api_key

    first = True
    for hs in _hs_codes():
        for partner, partner_name in ((PARTNER_INDIA, "India"), (PARTNER_WORLD, "World")):
            if not first:
                time.sleep(_RATE_LIMIT_SECONDS)
            first = False
            params = {
                "reporterCode": REPORTER_KOREA, "partnerCode": partner,
                "period": str(year), "cmdCode": hs, "flowCode": "X",
            }
            try:
                resp = sess.get(endpoint, params=params, timeout=DEFAULT_TIMEOUT)
                resp.raise_for_status()
                payload = resp.json()
            except (requests.RequestException, ValueError) as exc:
                logger.error("Comtrade fetch failed (HS %s -> %s): %s", hs, partner_name, exc)
                continue
            rows = payload.get("data", []) or []
            records.append({"hs": hs, "partner": partner_name, "year": year, "rows": rows})
            logger.info("Fetched %d Comtrade rows for HS %s Korea->%s %d",
                        len(rows), hs, partner_name, year)
    return records


def to_data_points(raw_records: list[dict]) -> list[DataPoint]:
    """Convert Comtrade export rows to EXPORT_FOB DataPoints.

    Args:
        raw_records: Records from fetch().

    Returns:
        One DataPoint per HS x partner with a positive primary value.
    """
    points: list[DataPoint] = []
    for rec in raw_records:
        total_usd = sum(
            row.get("primaryValue") or 0.0
            for row in rec["rows"]
            if row.get("primaryValue")
        )
        if total_usd <= 0:
            continue
        segment = HS_SEGMENT_MAP.get(rec["hs"], "total_bpc")
        corridor_tag = " [CORRIDOR]" if rec["partner"] == "India" else ""
        notes = (
            f"HS {rec['hs']} Korea exports to {rec['partner']} (UN Comtrade, FOB USD)."
            f"{' HS 3304 includes makeup as well as skincare.' if rec['hs'] == '3304' else ''}"
            f"{' HS 3307 is mixed shave/deo/bath preparations.' if rec['hs'] == '3307' else ''}"
            f"{corridor_tag}"
        )
        points.append(DataPoint(
            geography="KR", segment=segment, metric="export_value",
            value=round(total_usd / 1e9, 6), unit="usd_bn", currency="USD",
            period=str(rec["year"]), period_type="CY", value_basis="EXPORT_FOB",
            source_name="UN Comtrade",
            source_url="https://comtradeplus.un.org",
            date_accessed=date.today(), confidence="HIGH", notes=notes,
        ))
    logger.info("Converted Comtrade rows to %d DataPoints", len(points))
    return points


def fetch_india_imports(year: int | None = None) -> list[dict]:
    """Fetch India's cosmetics IMPORTS by HS from World, Korea, and China.

    India-as-reporter, flow=Imports. World totals size the import channel;
    Korea/China partners show sourcing origin (import dependence by origin).

    Args:
        year: Data year (default: two years back).

    Returns:
        Raw records; empty list on total failure.
    """
    import requests

    api_key = load_api_key("comtrade")
    endpoint = KEYED_ENDPOINT if api_key else PREVIEW_ENDPOINT
    year = year or (date.today().year - 2)

    records: list[dict] = []
    sess = session()
    if api_key:
        sess.headers["Ocp-Apim-Subscription-Key"] = api_key

    partners = ((PARTNER_WORLD, "World"), (PARTNER_KOREA, "Korea"), (PARTNER_CHINA, "China"))
    first = True
    for hs in _hs_codes():
        for partner, partner_name in partners:
            if not first:
                time.sleep(_RATE_LIMIT_SECONDS)
            first = False
            params = {
                "reporterCode": REPORTER_INDIA, "partnerCode": partner,
                "period": str(year), "cmdCode": hs, "flowCode": "M",  # imports
            }
            try:
                resp = sess.get(endpoint, params=params, timeout=DEFAULT_TIMEOUT)
                resp.raise_for_status()
                payload = resp.json()
            except (requests.RequestException, ValueError) as exc:
                logger.error("Comtrade India-import fetch failed (HS %s <- %s): %s",
                             hs, partner_name, exc)
                continue
            rows = payload.get("data", []) or []
            records.append({"hs": hs, "partner": partner_name, "year": year,
                            "flow": "import", "rows": rows})
            logger.info("Fetched %d rows for India imports HS %s <- %s %d",
                        len(rows), hs, partner_name, year)
    return records


def india_imports_to_data_points(raw_records: list[dict]) -> list[DataPoint]:
    """Convert India-import rows to import_value DataPoints (IMPORT_CIF).

    Args:
        raw_records: Records from fetch_india_imports().

    Returns:
        One DataPoint per HS x source partner with a positive value.
    """
    points: list[DataPoint] = []
    for rec in raw_records:
        total_usd = sum(row.get("primaryValue") or 0.0
                        for row in rec["rows"] if row.get("primaryValue"))
        if total_usd <= 0:
            continue
        segment = HS_SEGMENT_MAP.get(rec["hs"], "total_bpc")
        origin = rec["partner"]
        corridor = " [CORRIDOR]" if origin == "Korea" else ""
        notes = (
            f"HS {rec['hs']} India imports from {origin} (UN Comtrade, CIF USD)."
            f"{' Includes makeup as well as skincare.' if rec['hs'] == '3304' else ''}"
            f"{corridor}"
        )
        points.append(DataPoint(
            geography="IN", segment=segment, metric="import_value",
            value=round(total_usd / 1e9, 6), unit="usd_bn", currency="USD",
            period=str(rec["year"]), period_type="CY", value_basis="IMPORT_CIF",
            source_name="UN Comtrade", source_url="https://comtradeplus.un.org",
            date_accessed=date.today(), confidence="HIGH", notes=notes,
        ))
    logger.info("Converted India-import rows to %d DataPoints", len(points))
    return points


def run(output_dir: str = "data/raw/") -> str:
    """Full pipeline: fetch -> save raw -> convert -> merge into processed.

    Returns:
        Path to raw output, or '' if nothing was fetched.
    """
    records = fetch()
    if not records:
        return ""
    raw_path = save_raw("comtrade", records, output_dir)
    points = to_data_points(records)
    if points:
        upsert_data_points(points)
    return str(raw_path)


def run_india_imports(output_dir: str = "data/raw/") -> str:
    """Full pipeline for India imports: fetch -> save raw -> convert -> merge.

    Returns:
        Path to raw output, or '' if nothing was fetched.
    """
    records = fetch_india_imports()
    if not records:
        return ""
    raw_path = save_raw("comtrade_india_imports", records, output_dir)
    points = india_imports_to_data_points(records)
    if points:
        upsert_data_points(points)
    return str(raw_path)


__all__ = [
    "fetch", "to_data_points", "run", "HS_SEGMENT_MAP",
    "fetch_india_imports", "india_imports_to_data_points", "run_india_imports",
]
