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
    include_sub_segments: bool = False,
) -> list[dict]:
    """Walk segment x geography x metric combinations and report what's missing.

    Args:
        taxonomy_path: Path to config/taxonomy.yaml.
        processed_dir: Directory of processed segment JSON files.
        include_sub_segments: Also walk every taxonomy sub-segment (a
            sub-segment gap means no DataPoint carries that sub_segment for
            the geography). Sub-segment coverage comes almost entirely from
            paid databases (Passport/Statista sub-categories) via /ingest,
            so this view is the research worklist, not a fetcher to-do.

    Returns:
        List of gap dicts: {geography, segment, sub_segment, metric, status}.
        sub_segment is None for segment-level gaps.
    """
    taxonomy_path = Path(taxonomy_path)
    processed_dir = Path(processed_dir)

    with taxonomy_path.open(encoding="utf-8") as fh:
        tax = yaml.safe_load(fh)

    geographies = [g["code"] for g in tax["geographies"]]
    segments = [s["id"] for s in tax["segments"]]
    sub_segments = {s["id"]: (s.get("sub_segments") or []) for s in tax["segments"]}

    # Index what exists: (geo, segment) -> metrics; (geo, segment, sub) -> metrics
    present: dict[tuple[str, str], set[str]] = {}
    sub_present: dict[tuple[str, str, str], set[str]] = {}
    if processed_dir.exists():
        for jf in sorted(processed_dir.glob("*.json")):
            try:
                payload = json.loads(jf.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                logger.exception("Skipping malformed processed file %s", jf)
                continue
            key = (payload.get("geography"), payload.get("segment"))
            for dp in payload.get("data_points", []):
                present.setdefault(key, set()).add(dp["metric"])
                if dp.get("sub_segment"):
                    sub_present.setdefault(
                        (key[0], key[1], dp["sub_segment"]), set()
                    ).add(dp["metric"])

    gaps: list[dict] = []
    for geo in geographies:
        for seg in segments:
            have = present.get((geo, seg), set())
            for metric in CORE_METRICS:
                if metric not in have:
                    gaps.append({
                        "geography": geo,
                        "segment": seg,
                        "sub_segment": None,
                        "metric": metric,
                        "status": "no data" if not have else f"segment has {sorted(have)} only",
                    })
            if not include_sub_segments:
                continue
            for sub in sub_segments[seg]:
                sub_have = sub_present.get((geo, seg, sub), set())
                for metric in CORE_METRICS:
                    if metric not in sub_have:
                        gaps.append({
                            "geography": geo,
                            "segment": seg,
                            "sub_segment": sub,
                            "metric": metric,
                            "status": (
                                "no data" if not sub_have
                                else f"sub-segment has {sorted(sub_have)} only"
                            ),
                        })
    logger.info(
        "Gap scan: %d gaps across %d geographies x %d segments (%s sub-segments)",
        len(gaps), len(geographies), len(segments),
        "incl." if include_sub_segments else "excl.",
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
        "| Geography | Segment | Sub-segment | Metric | Status | Suggested source |",
        "|---|---|---|---|---|---|",
    ]
    for gap in gaps:
        lines.append(
            f"| {gap['geography']} | {gap['segment']} | {gap.get('sub_segment') or '—'} "
            f"| {gap['metric']} | {gap['status']} | {suggest_source(gap)} |"
        )
    lines.append("")
    return "\n".join(lines)


__all__ = ["scan_gaps", "suggest_source", "format_gaps_register", "CORE_METRICS"]
