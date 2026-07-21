"""Tavily-powered structured news search.

Inside Claude Code, Tavily is a globally-connected MCP tool, not a Python
API. This module therefore has two modes:

1. **MCP mode (primary):** `queries()` emits the full query manifest
   (per-segment x geography + the corridor set from config/corridor.yaml).
   Claude Code runs each query through the Tavily MCP and saves the combined
   results with `save_results(results)`. Extracted facts become DataPoints
   only when Claude Code writes them with explicit source attribution.

2. **REST mode (fallback):** if `tavily` is set in config/api_keys.yaml,
   `fetch()` calls the Tavily REST API directly.

Raw results always land in data/raw/tavily_*.json. Deduplication against
data/sources.csv happens on URL.
"""
from __future__ import annotations

import csv
import logging

from lib.fetchers._base import DEFAULT_TIMEOUT, PROJECT_ROOT, load_api_key, load_yaml, save_raw, session

logger = logging.getLogger("bpc_intel.fetchers.tavily")

SOURCES_CSV = PROJECT_ROOT / "data" / "sources.csv"
TAVILY_ENDPOINT = "https://api.tavily.com/search"

# Per-segment x geography standing queries (highest-value segments only;
# corridor queries come from config/corridor.yaml).
SEGMENT_QUERIES: list[dict] = [
    {"geography": "KR", "segment": "skincare", "query": "South Korea skincare market size 2025 2026"},
    {"geography": "KR", "segment": "dermocosmetics", "query": "Korea dermocosmetics clinical skincare market growth"},
    {"geography": "KR", "segment": "total_bpc", "query": "Korea cosmetics exports MFDS 2026"},
    {"geography": "KR", "segment": "total_bpc", "query": "Korea beauty M&A acquisition 2026"},
    {"geography": "KR", "segment": "colour_cosmetics", "query": "Korea color cosmetics export market 2026"},
    {"geography": "IN", "segment": "total_bpc", "query": "India beauty personal care market size 2026"},
    {"geography": "IN", "segment": "skincare", "query": "India skincare market growth premiumization 2026"},
    {"geography": "IN", "segment": "sun_care", "query": "India sunscreen market growth quick commerce"},
    {"geography": "IN", "segment": "mens_grooming", "query": "India men's grooming skincare market 2026"},
    {"geography": "IN", "segment": "total_bpc", "query": "India beauty D2C funding acquisition 2026"},
    {"geography": "IN", "segment": "dermocosmetics", "query": "India derma skincare clinical beauty market"},
]


def queries() -> list[dict]:
    """The full query manifest: segment queries + corridor queries.

    Returns:
        List of {geography, segment, query, corridor} dicts. Corridor queries
        are tagged corridor=True and their DataPoints must carry [CORRIDOR]
        in notes per CLAUDE.md.
    """
    manifest = [dict(q, corridor=False) for q in SEGMENT_QUERIES]
    corridor_cfg = load_yaml("corridor.yaml").get("corridor", {})
    for q in corridor_cfg.get("monitoring_queries", {}).get("tavily", []):
        manifest.append({
            "geography": "IN", "segment": "total_bpc", "query": q, "corridor": True,
        })
    return manifest


def _known_urls() -> set[str]:
    """URLs already present in data/sources.csv (for deduplication)."""
    if not SOURCES_CSV.exists():
        return set()
    with SOURCES_CSV.open(encoding="utf-8", newline="") as fh:
        return {row.get("url", "") for row in csv.DictReader(fh) if row.get("url")}


def fetch() -> list[dict]:
    """REST-mode fetch: run every manifest query against the Tavily API.

    Returns:
        Raw result records (one per query), deduplicated against sources.csv.
        Empty list if no API key is configured (MCP mode should be used) or
        on network failure.
    """
    api_key = load_api_key("tavily")
    if api_key is None:
        logger.warning(
            "No Tavily API key in config/api_keys.yaml — use MCP mode: run "
            "queries() through Claude Code's global Tavily MCP and pass the "
            "results to save_results()."
        )
        return []

    known = _known_urls()
    records: list[dict] = []
    sess = session()
    for item in queries():
        try:
            resp = sess.post(
                TAVILY_ENDPOINT,
                json={"api_key": api_key, "query": item["query"],
                      "search_depth": "advanced", "max_results": 5,
                      "include_answer": False},
                timeout=DEFAULT_TIMEOUT,
            )
            resp.raise_for_status()
            payload = resp.json()
        except requests_errors() as exc:
            logger.error("Tavily query failed (%s): %s", item["query"], exc)
            continue
        results = [r for r in payload.get("results", []) if r.get("url") not in known]
        records.append({**item, "results": results})
        logger.info("Fetched %d new results for: %s", len(results), item["query"])
    return records


def requests_errors() -> tuple:
    """The exception types a fetch call may raise (kept narrow, no bare except)."""
    import requests
    return (requests.RequestException, ValueError)


def save_results(records: list[dict]) -> str:
    """Persist raw Tavily results (from MCP or REST mode) to data/raw/.

    Args:
        records: List of {geography, segment, query, corridor, results} dicts.

    Returns:
        Path to the raw file written.
    """
    return str(save_raw("tavily", records))


def to_data_points(raw_records: list[dict]) -> list:
    """Tavily results are news leads, not structured statistics.

    Numbers must be read from the underlying articles and entered with full
    source attribution — extraction is a judgment task done by Claude Code
    (or a human), never blind regex over headlines. This returns [] by design.

    Args:
        raw_records: Raw records from fetch()/save_results().

    Returns:
        Always [] — see above.
    """
    logger.info(
        "to_data_points: %d raw query results are leads; extract claims via "
        "review, then write DataPoints with lib.transforms.merge.upsert_data_points",
        len(raw_records),
    )
    return []


def run(output_dir: str = "data/raw/") -> str:
    """Full pipeline: fetch (REST mode) -> save raw. Returns raw path or ''."""
    records = fetch()
    if not records:
        return ""
    return str(save_raw("tavily", records, output_dir))


__all__ = ["queries", "fetch", "save_results", "to_data_points", "run"]
