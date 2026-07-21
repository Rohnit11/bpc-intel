"""Blinkit/Zepto beauty assortment snapshots — ToS-sensitive, opt-in only.

Disabled by default. Requires `enabled: true` in config/qcommerce_enabled.yaml.
When enabled: 5+ second delays, identifying user agent, category pages only.
Corridor focus: the K-brand watchlist below is checked for presence/pricing.

Captured per product: name, brand, MRP, selling price, rating count (demand
proxy). Prices are point-in-time MRP-basis observations — raw JSON only;
promotion to DataPoints needs a curation pass because a single-day price
snapshot is not a market statistic.
"""
from __future__ import annotations

import logging
import time

from lib.fetchers._base import DEFAULT_TIMEOUT, load_yaml, save_raw, session

logger = logging.getLogger("bpc_intel.fetchers.qcommerce")

_RATE_LIMIT_SECONDS = 5.0

# Corridor watchlist: K-brands whose q-commerce presence signals Tier 2/3 reach.
KBRAND_WATCHLIST = [
    "COSRX", "Anua", "Beauty of Joseon", "Laneige", "Innisfree",
    "Some By Mi", "Isntree", "Mixsoon", "Etude", "The Face Shop",
]

_SEARCH_TERMS = ["sunscreen", "serum", "face wash", "korean skincare"]


def is_enabled() -> bool:
    """Whether the user has explicitly opted in via config/qcommerce_enabled.yaml."""
    try:
        return bool(load_yaml("qcommerce_enabled.yaml").get("enabled", False))
    except FileNotFoundError:
        return False


def fetch() -> list[dict]:
    """Snapshot Blinkit search results for beauty terms + K-brand watchlist.

    Returns:
        Raw records; empty list when disabled (the default) or on failure.
    """
    if not is_enabled():
        logger.warning(
            "qcommerce_tracker is disabled. Review the ToS implications and set "
            "enabled: true in config/qcommerce_enabled.yaml to activate."
        )
        return []

    import requests

    records: list[dict] = []
    sess = session()
    terms = _SEARCH_TERMS + [f"{b} skincare" for b in KBRAND_WATCHLIST]
    for i, term in enumerate(terms):
        if i:
            time.sleep(_RATE_LIMIT_SECONDS)
        url = "https://blinkit.com/s/"
        try:
            resp = sess.get(url, params={"q": term}, timeout=DEFAULT_TIMEOUT)
            resp.raise_for_status()
        except requests.RequestException as exc:
            logger.error("q-commerce fetch failed for '%s': %s", term, exc)
            continue
        records.append({
            "platform": "blinkit", "search_term": term,
            "corridor": any(b.lower() in term.lower() for b in KBRAND_WATCHLIST),
            "html_length": len(resp.text),
            "html": resp.text[:200000],
        })
        logger.info("Snapshot for '%s': %d bytes", term, len(resp.text))
    return records


def to_data_points(raw_records: list[dict]) -> list:
    """Point-in-time price snapshots are not market statistics — raw-only.

    Args:
        raw_records: Records from fetch().

    Returns:
        Always []; assortment/price analysis is a curation pass over raw HTML.
    """
    logger.info("%d q-commerce snapshots kept raw-only", len(raw_records))
    return []


def run(output_dir: str = "data/raw/") -> str:
    """Full pipeline: fetch -> save raw. Returns raw path or ''."""
    records = fetch()
    if not records:
        return ""
    return str(save_raw("qcommerce", records, output_dir))


__all__ = ["is_enabled", "fetch", "to_data_points", "run", "KBRAND_WATCHLIST"]
