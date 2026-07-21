"""Ingest orchestrator: detect handler, parse, merge, refresh gaps.

Backs the /ingest slash command. Handler selection is by filename convention
(passport_*, capitaliq_*, statista_*) with an explicit override, since the
subscription exports look similar enough that sniffing is unreliable.
"""
from __future__ import annotations

import logging
from pathlib import Path

from lib.analysis.gaps import format_gaps_register, scan_gaps
from lib.ingest import capitaliq_csv, generic_csv, passport_csv, statista_csv
from lib.transforms.merge import upsert_data_points
from lib.transforms.schema import DataPoint

logger = logging.getLogger("bpc_intel.ingest.orchestrator")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
GAPS_REGISTER = PROJECT_ROOT / "reports" / "latest" / "gaps_register.md"


def detect_handler(filepath: str | Path) -> str:
    """Choose a handler from the filename prefix.

    Args:
        filepath: Path to the dropped file.

    Returns:
        One of "passport", "capitaliq", "statista", "generic".
    """
    name = Path(filepath).name.lower()
    if name.startswith("passport") or "euromonitor" in name:
        return "passport"
    if name.startswith("capitaliq") or "capital_iq" in name or "capiq" in name:
        return "capitaliq"
    if name.startswith("statista"):
        return "statista"
    return "generic"


def ingest(
    filepath: str | Path,
    handler: str | None = None,
    **handler_kwargs,
) -> dict:
    """Process a manual data file end to end.

    Args:
        filepath: Path to the CSV (typically in data/manual/).
        handler: Force a handler ("passport"/"capitaliq"/"statista"/"generic");
            default detects from the filename.
        **handler_kwargs: Extra args passed to the handler (e.g. geography,
            unit_hint for Passport; segment/metric/unit for Statista;
            mapping for generic).

    Returns:
        Summary dict: handler used, points parsed, per-file merge counts,
        gap count after ingest.

    Raises:
        ValueError: If the handler cannot parse the file.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise ValueError(f"File not found: {filepath}")
    handler = handler or detect_handler(filepath)

    parsers = {
        "passport": passport_csv.parse,
        "capitaliq": capitaliq_csv.parse,
        "statista": statista_csv.parse,
        "generic": generic_csv.parse,
    }
    if handler not in parsers:
        raise ValueError(f"Unknown handler '{handler}'. Options: {list(parsers)}")

    points: list[DataPoint] = parsers[handler](filepath, **handler_kwargs)
    if not points:
        logger.warning("No DataPoints parsed from %s", filepath.name)
        return {"handler": handler, "points": 0, "merge": {}, "gaps": None}

    merge_summary = upsert_data_points(points)

    gaps = scan_gaps()
    GAPS_REGISTER.parent.mkdir(parents=True, exist_ok=True)
    GAPS_REGISTER.write_text(format_gaps_register(gaps), encoding="utf-8")

    added = sum(s["added"] for s in merge_summary.values())
    updated = sum(s["updated"] for s in merge_summary.values())
    logger.info("Ingested %d points from %s (%d new, %d updated); gaps now %d",
                len(points), filepath.name, added, updated, len(gaps))
    return {
        "handler": handler, "points": len(points),
        "added": added, "updated": updated,
        "merge": merge_summary, "gaps": len(gaps),
    }


def ingest_folder(
    folder: str | Path = PROJECT_ROOT / "data" / "manual",
    pattern: str = "*.csv",
) -> dict:
    """Ingest every matching file in a folder (batch drop-and-go).

    Handler is auto-detected per file from its name prefix. Files that fail
    to parse are logged and skipped so one bad file never blocks the rest.

    Args:
        folder: Directory to scan (default data/manual/).
        pattern: Glob pattern (default "*.csv").

    Returns:
        Summary: {files_processed, total_points, total_added, total_updated,
        gaps, per_file: {name: result-or-error}}.
    """
    folder = Path(folder)
    results: dict[str, object] = {}
    total_points = total_added = total_updated = 0
    last_gaps: int | None = None

    for path in sorted(folder.glob(pattern)):
        if path.name == ".gitkeep":
            continue
        try:
            res = ingest(path)
        except (ValueError, KeyError) as exc:
            logger.error("Failed to ingest %s: %s", path.name, exc)
            results[path.name] = {"error": str(exc)}
            continue
        results[path.name] = res
        total_points += res["points"]
        total_added += res.get("added", 0)
        total_updated += res.get("updated", 0)
        last_gaps = res.get("gaps", last_gaps)

    logger.info("Batch ingest: %d files, %d points (%d new, %d updated)",
                len(results), total_points, total_added, total_updated)
    return {
        "files_processed": len(results),
        "total_points": total_points,
        "total_added": total_added,
        "total_updated": total_updated,
        "gaps": last_gaps,
        "per_file": results,
    }


if __name__ == "__main__":
    import json
    import sys

    args = sys.argv[1:]
    if args and args[0] == "--folder":
        target = args[1] if len(args) > 1 else str(PROJECT_ROOT / "data" / "manual")
        print(json.dumps(ingest_folder(target), indent=2))
    elif args:
        forced = args[1] if len(args) > 1 else None
        print(json.dumps(ingest(args[0], handler=forced), indent=2))
    else:
        print("Usage:\n"
              "  python -m lib.ingest.ingest <filepath> [handler]\n"
              "  python -m lib.ingest.ingest --folder [dir]   # batch all CSVs")
        raise SystemExit(1)
