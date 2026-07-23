"""Refresh orchestrator — run every free-source fetcher in one pass.

Backs the /refresh command. Each fetcher is isolated: a failure, missing API
key, or disabled flag in one never aborts the others (CLAUDE.md working style —
fail loudly per-source, never fabricate, let the gaps register show the hole).

Fetchers that need a key or opt-in report `skipped`, not `error`:
  * korea_dart       — needs `dart:` in config/api_keys.yaml (free, opendart.fss.or.kr)
  * qcommerce_tracker — needs enabled: true in config/qcommerce_enabled.yaml
All others run headlessly: Tavily (REST key set), Comtrade (keyless preview
endpoint), Screener (scrape), Google Trends (pytrends), OpenAlex, India research.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Callable

from lib.fetchers import (
    academic_openalex,
    india_research,
    india_screener,
    korea_dart,
    news_tavily,
    qcommerce_tracker,
    trade_comtrade,
    trends_google,
)

logger = logging.getLogger("bpc_intel.fetchers.refresh")

# (label, run-callable). Order is highest-value first. Comtrade appears twice
# because the corridor flow and India-imports pulls hit different endpoints.
_STEPS: list[tuple[str, Callable[[], str]]] = [
    ("news_tavily", news_tavily.run),
    ("korea_dart", korea_dart.run),
    ("india_screener", india_screener.run),
    ("trade_comtrade", trade_comtrade.run),
    ("trade_comtrade_india_imports", trade_comtrade.run_india_imports),
    ("trends_google", trends_google.run),
    ("academic_openalex", academic_openalex.run),
    ("india_research", india_research.run),
    ("qcommerce_tracker", qcommerce_tracker.run),
]

_STATUS_ICON = {"ok": "OK ", "skipped": "-- ", "error": "ERR"}


def refresh_all() -> dict[str, dict[str, str]]:
    """Run every fetcher in sequence, isolating each failure.

    A fetcher that returns a raw-file path is `ok`; one that returns an empty
    path (missing key, disabled, or empty response) is `skipped`; one that
    raises is `error` (logged with a traceback, but the run continues).

    Returns:
        Ordered mapping ``{label: {"status", "raw_path", "detail"}}`` where
        status is one of "ok" | "skipped" | "error".
    """
    started = datetime.now(timezone.utc)
    results: dict[str, dict[str, str]] = {}
    for label, fn in _STEPS:
        try:
            raw_path = fn()
        except Exception as exc:  # noqa: BLE001 — orchestrator boundary: one bad fetcher must not kill the batch
            results[label] = {"status": "error", "raw_path": "", "detail": repr(exc)}
            logger.exception("[refresh] %s failed", label)
            continue
        if raw_path:
            results[label] = {"status": "ok", "raw_path": str(raw_path), "detail": ""}
            logger.info("[refresh] %s -> %s", label, raw_path)
        else:
            results[label] = {
                "status": "skipped", "raw_path": "",
                "detail": "no data (missing key, disabled flag, or empty response)",
            }
            logger.warning("[refresh] %s produced no data (skipped)", label)

    elapsed = (datetime.now(timezone.utc) - started).total_seconds()
    tally = {s: sum(1 for r in results.values() if r["status"] == s)
             for s in ("ok", "skipped", "error")}
    logger.info("[refresh] done in %.1fs — %d ok, %d skipped, %d error",
                elapsed, tally["ok"], tally["skipped"], tally["error"])
    return results


def format_summary(results: dict[str, dict[str, str]]) -> str:
    """Render a refresh result mapping as a Markdown table.

    Args:
        results: Output of refresh_all().

    Returns:
        A Markdown table (one row per fetcher) suitable for printing.
    """
    lines = ["| Fetcher | Status | Detail |", "|---|---|---|"]
    for label, r in results.items():
        detail = r["raw_path"] or r["detail"]
        lines.append(f"| {label} | {_STATUS_ICON.get(r['status'], '')} {r['status']} | {detail} |")
    return "\n".join(lines)


if __name__ == "__main__":
    print(format_summary(refresh_all()))
