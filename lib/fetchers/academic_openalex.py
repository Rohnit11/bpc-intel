"""OpenAlex — publication counts as ingredient-trend momentum proxies.

Uses the free REST API (no key needed). Publication counts by year for
PDRN, exosome cosmetics, ayurvedic beauty, and Korean cosmetics regulation
are directional signals; they become raw JSON, and yearly counts are stored
as DataPoints only under metric penetration_rate? No — counts have no BPC
value basis, so they stay raw-only, mirroring Google Trends.
"""
from __future__ import annotations

import logging
import time

from lib.fetchers._base import DEFAULT_TIMEOUT, save_raw, session

logger = logging.getLogger("bpc_intel.fetchers.openalex")

ENDPOINT = "https://api.openalex.org/works"
_RATE_LIMIT_SECONDS = 1.0
_YEARS = ">2019"

TOPICS = [
    {"key": "pdrn_skincare", "search": "PDRN skin regeneration cosmetic"},
    {"key": "exosome_cosmetics", "search": "exosome cosmetics skin"},
    {"key": "ayurvedic_beauty_clinical", "search": "ayurvedic skincare clinical trial"},
    {"key": "korea_cosmetics_regulation", "search": "Korea cosmetics regulation functional"},
    {"key": "niacinamide_efficacy", "search": "niacinamide skin efficacy"},
]


def fetch() -> list[dict]:
    """Fetch publication counts by year for each tracked topic.

    Returns:
        Raw records: {key, search, counts_by_year: [{year, count}]}.
        Failures are logged and skipped; never crashes.
    """
    import requests

    records: list[dict] = []
    sess = session()
    for i, topic in enumerate(TOPICS):
        if i:
            time.sleep(_RATE_LIMIT_SECONDS)
        params = {
            "search": topic["search"],
            "filter": f"publication_year:{_YEARS}",
            "group_by": "publication_year",
            "mailto": "rohnit.agrawal@hec.edu",
        }
        try:
            resp = sess.get(ENDPOINT, params=params, timeout=DEFAULT_TIMEOUT)
            resp.raise_for_status()
            payload = resp.json()
        except (requests.RequestException, ValueError) as exc:
            logger.error("OpenAlex fetch failed for %s: %s", topic["key"], exc)
            continue
        counts = [
            {"year": g["key"], "count": g["count"]}
            for g in payload.get("group_by", [])
        ]
        records.append({**topic, "counts_by_year": sorted(counts, key=lambda c: c["year"])})
        logger.info("Fetched OpenAlex counts for %s: %s", topic["key"],
                    {c['year']: c['count'] for c in counts})
    return records


def to_data_points(raw_records: list[dict]) -> list:
    """Publication counts have no BPC value basis — raw-only by design.

    Args:
        raw_records: Records from fetch().

    Returns:
        Always [].
    """
    logger.info("OpenAlex counts are momentum proxies; %d topics kept raw-only",
                len(raw_records))
    return []


def run(output_dir: str = "data/raw/") -> str:
    """Full pipeline: fetch -> save raw. Returns raw path or ''."""
    records = fetch()
    if not records:
        return ""
    return str(save_raw("openalex", records, output_dir))


__all__ = ["fetch", "to_data_points", "run", "TOPICS"]
