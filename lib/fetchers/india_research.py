"""India value-chain deep research via Tavily (REST, uses config/api_keys.yaml).

India-only query set across five segment groups (K-beauty, skincare/sun/derma,
fragrances, men's grooming, hair care) and every value-chain dimension:
pricing, cost-of-making, import-vs-make, supply chain, company growth, new
players, and consumer demand. Saves raw results to data/raw/; curation into
DataPoints + the India value-chain brief is a judgment step done downstream.
"""
from __future__ import annotations

import logging

from lib.fetchers._base import DEFAULT_TIMEOUT, load_api_key, save_raw, session

logger = logging.getLogger("bpc_intel.fetchers.india_research")

TAVILY_ENDPOINT = "https://api.tavily.com/search"

# (dimension, segment_group, query). geography is always India.
QUERIES: list[tuple[str, str, str]] = [
    # --- Supply chain / manufacturing / import-vs-make ---
    ("supply_chain", "cross", "India cosmetics contract manufacturing third-party private label who makes"),
    ("supply_chain", "cross", "India beauty D2C brands outsourced manufacturing contract manufacturer ODM"),
    ("supply_chain", "cross", "India cosmetics ODM manufacturers Galaxy Surfactants Fine Organics ingredients"),
    ("import_make", "cross", "India cosmetics import duty customs BIS CDSCO Korea China cosmetics 2026"),
    ("import_make", "fragrances", "India fragrance perfume import dependence France fragrance oils manufacturing"),
    # --- Pricing / cost / MRP build-up ---
    ("pricing", "skincare", "India skincare price tiers mass premium serum sunscreen MRP 2026"),
    ("pricing", "cross", "India D2C beauty gross margin markup MRP trade margin unit economics"),
    ("pricing", "kbeauty", "K-beauty India price COSRX Beauty of Joseon Anua Laneige cost"),
    ("pricing", "fragrances", "India perfume price segments mass premium Bella Vita Skinn deodorant"),
    ("pricing", "mens", "India men grooming price beard oil face wash Beardo Bombay Shaving"),
    # --- Company growth ---
    ("growth", "skincare", "India skincare brands growth Minimalist Derma Co Aqualogica revenue 2026"),
    ("growth", "kbeauty", "K-beauty India market growth 2026 Nykaa Tira Korean brands sales"),
    ("growth", "fragrances", "India fragrance market growth Bella Vita Skinn Engage perfume revenue"),
    ("growth", "mens", "India men grooming market growth Beardo The Man Company revenue 2026"),
    ("growth", "hair", "India hair care market growth serum oil brands D2C 2026"),
    # --- New / small players & performance ---
    ("new_players", "skincare", "India new skincare D2C brands 2026 funding Foxtale Deconstruct Fae"),
    ("new_players", "cross", "India beauty startups funding 2026 D2C new brands seed traction"),
    ("new_players", "fragrances", "India new perfume brands D2C 2026 Bella Vita Ranipink fragrance startup"),
    ("new_players", "hair", "India hair care new D2C brands 2026 Arata Traya scalp"),
    # --- Consumer demand ---
    ("demand", "cross", "India beauty consumer demand Tier 2 3 Gen Z quick commerce 2026"),
    ("demand", "cross", "India beauty quick commerce Blinkit Zepto sales share BPC 2026"),
    ("demand", "sun_care", "India sunscreen demand growth awareness quick commerce 2026"),
]


def fetch() -> list[dict]:
    """Run every India-research query against the Tavily REST API.

    Returns:
        Raw records: {dimension, segment_group, query, results}. Empty list if
        no Tavily key is configured or all requests fail.
    """
    import requests

    api_key = load_api_key("tavily")
    if api_key is None:
        logger.warning("No Tavily API key in config/api_keys.yaml; skipping India research.")
        return []

    sess = session()
    sess.headers.update({"Authorization": f"Bearer {api_key}"})
    records: list[dict] = []
    for dimension, group, query in QUERIES:
        try:
            resp = sess.post(
                TAVILY_ENDPOINT,
                json={"query": query, "search_depth": "advanced",
                      "max_results": 6, "include_answer": False,
                      "country": "India"},
                timeout=DEFAULT_TIMEOUT,
            )
            resp.raise_for_status()
            payload = resp.json()
        except (requests.RequestException, ValueError) as exc:
            logger.error("India-research query failed (%s): %s", query, exc)
            continue
        records.append({"dimension": dimension, "segment_group": group,
                        "query": query, "results": payload.get("results", [])})
        logger.info("Fetched %d results for [%s/%s] %s",
                    len(payload.get("results", [])), dimension, group, query)
    return records


def run(output_dir: str = "data/raw/") -> str:
    """Fetch and save raw India-research results. Returns raw path or ''."""
    records = fetch()
    if not records:
        return ""
    return str(save_raw("india_research", records, output_dir))


__all__ = ["QUERIES", "fetch", "run"]
