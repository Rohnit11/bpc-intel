"""Gaps register: what the taxonomy demands vs what processed data contains."""
from __future__ import annotations

import json
import logging
from pathlib import Path

import yaml

logger = logging.getLogger("bpc_intel.gaps")

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# The core metrics every segment x geography should eventually have.
CORE_METRICS = ("market_size", "growth_yoy", "cagr_forecast")

# Which registered source is best placed to fill each kind of gap.
_METRIC_SOURCE_HINTS = {
    "market_size": ["euromonitor_passport", "statista", "tavily"],
    "growth_yoy": ["euromonitor_passport", "korea_mfds", "tavily"],
    "cagr_forecast": ["euromonitor_passport", "bmi_research", "statista"],
    "market_share": ["euromonitor_passport", "korea_dart", "india_screener"],
    "revenue": ["korea_dart", "india_screener", "capitaliq_pro"],
    "export_value": ["korea_mfds", "korea_customs", "un_comtrade"],
    "production_value": ["korea_mfds"],
    "channel_share": ["euromonitor_passport", "tavily"],
    "per_capita_spend": ["statista", "euromonitor_passport"],
    "penetration_rate": ["euromonitor_passport", "statista"],
}


def scan_gaps(
    taxonomy_path: str | Path = PROJECT_ROOT / "config" / "taxonomy.yaml",
    processed_dir: str | Path = PROJECT_ROOT / "data" / "processed",
) -> list[dict]:
    """Walk segment x geography x metric combinations and report what's missing.

    Args:
        taxonomy_path: Path to config/taxonomy.yaml.
        processed_dir: Directory of processed segment JSON files.

    Returns:
        List of gap dicts: {geography, segment, metric, status}.
    """
    taxonomy_path = Path(taxonomy_path)
    processed_dir = Path(processed_dir)

    with taxonomy_path.open(encoding="utf-8") as fh:
        tax = yaml.safe_load(fh)

    geographies = [g["code"] for g in tax["geographies"]]
    segments = [s["id"] for s in tax["segments"]]

    # Index what exists: (geo, segment) -> set of metrics present
    present: dict[tuple[str, str], set[str]] = {}
    if processed_dir.exists():
        for jf in sorted(processed_dir.glob("*.json")):
            try:
                payload = json.loads(jf.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                logger.exception("Skipping malformed processed file %s", jf)
                continue
            key = (payload.get("geography"), payload.get("segment"))
            metrics = {dp["metric"] for dp in payload.get("data_points", [])}
            present.setdefault(key, set()).update(metrics)

    gaps: list[dict] = []
    for geo in geographies:
        for seg in segments:
            have = present.get((geo, seg), set())
            for metric in CORE_METRICS:
                if metric not in have:
                    gaps.append({
                        "geography": geo,
                        "segment": seg,
                        "metric": metric,
                        "status": "no data" if not have else f"segment has {sorted(have)} only",
                    })
    logger.info(
        "Gap scan: %d gaps across %d geographies x %d segments x %d core metrics",
        len(gaps), len(geographies), len(segments), len(CORE_METRICS),
    )
    return gaps


def suggest_source(gap: dict) -> str:
    """Suggest which registered source could fill a gap.

    Args:
        gap: A gap dict from scan_gaps().

    Returns:
        Comma-separated source keys from config/sources.yaml, best first.
    """
    hints = _METRIC_SOURCE_HINTS.get(gap["metric"], ["tavily"])
    if gap["geography"] == "KR":
        ordered = [h for h in hints if not h.startswith("india_")]
    else:
        ordered = [h for h in hints if not h.startswith("korea_")]
    return ", ".join(ordered or hints)


def format_gaps_register(gaps: list[dict]) -> str:
    """Render the gaps register as a Markdown table.

    Args:
        gaps: List of gap dicts from scan_gaps().

    Returns:
        Markdown string.
    """
    lines = [
        "# Gaps Register",
        "",
        f"{len(gaps)} missing segment × geography × metric combinations.",
        "",
        "| Geography | Segment | Metric | Status | Suggested source |",
        "|---|---|---|---|---|",
    ]
    for gap in gaps:
        lines.append(
            f"| {gap['geography']} | {gap['segment']} | {gap['metric']} "
            f"| {gap['status']} | {suggest_source(gap)} |"
        )
    lines.append("")
    return "\n".join(lines)


__all__ = ["scan_gaps", "suggest_source", "format_gaps_register", "CORE_METRICS"]
