"""Google Trends via pytrends — relative demand signals (directional only).

Corridor focus: interest in "Korean skincare" / "K-beauty" / "Korean
sunscreen" / "glass skin" within India, including state-level breakdown.

pytrends is an unofficial library and breaks when Google changes endpoints —
every call is wrapped and failures degrade to an empty result, never a crash.
Trends values are a relative index (0-100), NOT absolute volume; they are
stored as penetration_rate-style signals only in raw form, never as
DataPoints (no defensible unit/value_basis).
"""
from __future__ import annotations

import logging
import time

from lib.fetchers._base import load_yaml, save_raw

logger = logging.getLogger("bpc_intel.fetchers.trends")

_RATE_LIMIT_SECONDS = 5.0
_TIMEFRAME = "today 5-y"

COMPARATIVE_KEYWORDS = [
    {"keyword": "sunscreen", "geos": ["IN", "KR"]},
    {"keyword": "serum", "geos": ["IN", "KR"]},
]


def _corridor_keywords() -> list[dict]:
    corridor = load_yaml("corridor.yaml").get("corridor", {})
    return corridor.get("monitoring_queries", {}).get("google_trends", [])


def fetch() -> list[dict]:
    """Fetch interest-over-time and India state-level interest for all keywords.

    Returns:
        Raw records; empty list if pytrends is unavailable or blocked.
    """
    try:
        from pytrends.request import TrendReq
    except ImportError:
        logger.error("pytrends not installed — run: pip install pytrends")
        return []

    records: list[dict] = []
    try:
        pytrends = TrendReq(hl="en-US", tz=0)
    except Exception as exc:  # noqa: BLE001 — pytrends raises raw exceptions on setup
        logger.exception("pytrends session init failed: %s", exc)
        return []

    jobs: list[dict] = []
    for item in _corridor_keywords():
        jobs.append({"keyword": item["keyword"], "geo": item.get("geo", "IN"),
                     "corridor": True, "regional": True})
    for item in COMPARATIVE_KEYWORDS:
        for geo in item["geos"]:
            jobs.append({"keyword": item["keyword"], "geo": geo,
                         "corridor": False, "regional": False})

    for i, job in enumerate(jobs):
        if i:
            time.sleep(_RATE_LIMIT_SECONDS)
        try:
            pytrends.build_payload([job["keyword"]], geo=job["geo"], timeframe=_TIMEFRAME)
            iot = pytrends.interest_over_time()
            rec = {
                "keyword": job["keyword"], "geo": job["geo"],
                "corridor": job["corridor"], "timeframe": _TIMEFRAME,
                "interest_over_time": (
                    iot.drop(columns=["isPartial"], errors="ignore")
                    .reset_index().astype(str).to_dict("records")
                    if not iot.empty else []
                ),
            }
            if job["regional"] and job["geo"] == "IN":
                region = pytrends.interest_by_region(resolution="REGION")
                top10 = region.sort_values(job["keyword"], ascending=False).head(10)
                rec["top_states"] = top10.reset_index().astype(str).to_dict("records")
            records.append(rec)
            logger.info("Fetched Trends for '%s' in %s (%d time points)",
                        job["keyword"], job["geo"], len(rec["interest_over_time"]))
        except Exception as exc:  # noqa: BLE001 — pytrends raises many raw types
            logger.exception("Trends fetch failed for '%s' in %s: %s",
                             job["keyword"], job["geo"], exc)
    return records


def to_data_points(raw_records: list[dict]) -> list:
    """Trends indices are relative, not absolute — no DataPoints by design.

    Args:
        raw_records: Records from fetch().

    Returns:
        Always [] — use raw JSON for directional charts only.
    """
    logger.info("Trends data is a relative index; %d records kept raw-only",
                len(raw_records))
    return []


def run(output_dir: str = "data/raw/") -> str:
    """Full pipeline: fetch -> save raw. Returns raw path or ''."""
    records = fetch()
    if not records:
        return ""
    return str(save_raw("gtrends", records, output_dir))


__all__ = ["fetch", "to_data_points", "run"]
