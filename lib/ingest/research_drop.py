"""Ingest handler for web-research drop files (the /research pass).

A drop file is JSON written by a research agent into
data/manual/research_drops/ (gitignored — the ledger is data/sources.csv):

    {
      "accessed": "2026-07-24",
      "claims": [
        {
          "geography": "IN", "segment": "skincare",
          "sub_segment": "sheet_masks",          // optional; must match taxonomy
          "metric": "market_size", "value": 0.12, "unit": "usd_bn",
          "currency": "USD", "period": "2025", "period_type": "CY",
          "value_basis": "RETAIL", "tier": null,
          "source_name": "...", "source_url": "https://... (actually fetched)",
          "confidence": "LOW", "methodology": null,
          "notes": "..."
        }
      ]
    }

Two modes, deliberately split so parallel agents can't race on shared files:
  --check <file>   validate only (schema + taxonomy + drop rules); NO writes.
                   This is the ONLY mode research agents may run.
  <file> | --all   validate then merge via upsert_data_points (which also
                   appends data/sources.csv). Single-writer: run from the
                   main session only, after all agents have finished.

Drop rules beyond the DataPoint schema:
  * source_url is REQUIRED unless confidence == "ESTIMATE" (CLAUDE.md rule 6:
    never cite a URL you have not fetched — so every researched claim must
    carry the URL that was actually fetched and verified).
  * Any invalid claim fails the whole file (strict) with per-claim errors,
    so a researcher fixes the drop rather than silently losing rows.
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import date
from pathlib import Path

from pydantic import ValidationError

from lib.ingest._common import MANUAL_DIR
from lib.transforms.merge import upsert_data_points
from lib.transforms.schema import DataPoint, validate_data_point

logger = logging.getLogger("bpc_intel.ingest.research_drop")

DROPS_DIR = MANUAL_DIR / "research_drops"


def parse_drop(path: str | Path) -> tuple[list[DataPoint], list[str]]:
    """Parse and validate one drop file.

    Args:
        path: Path to the drop JSON.

    Returns:
        (points, errors). points is complete only when errors is empty —
        callers must treat any error as failing the whole file.
    """
    path = Path(path)
    errors: list[str] = []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [], [f"{path.name}: unreadable ({exc})"]

    accessed_raw = payload.get("accessed")
    try:
        accessed = date.fromisoformat(accessed_raw)
    except (TypeError, ValueError):
        return [], [f"{path.name}: missing/invalid top-level 'accessed' date"]

    claims = payload.get("claims")
    if not isinstance(claims, list) or not claims:
        return [], [f"{path.name}: 'claims' must be a non-empty list"]

    points: list[DataPoint] = []
    for i, raw in enumerate(claims):
        label = f"{path.name}[{i}]"
        try:
            dp = DataPoint(date_accessed=accessed, **raw)
        except (ValidationError, TypeError) as exc:
            errors.append(f"{label}: schema — {exc}")
            continue
        ok, reason = validate_data_point(dp)
        if not ok:
            errors.append(f"{label}: taxonomy — {reason}")
            continue
        if dp.confidence != "ESTIMATE" and not dp.source_url:
            errors.append(f"{label}: source_url required for researched "
                          f"(non-ESTIMATE) claims")
            continue
        points.append(dp)
    return points, errors


def check(path: str | Path) -> bool:
    """Validate a drop file; print a verdict; write nothing."""
    points, errors = parse_drop(path)
    if errors:
        for e in errors:
            print(f"FAIL {e}")
        return False
    print(f"OK   {Path(path).name}: {len(points)} valid claims")
    return True


def merge(path: str | Path) -> dict:
    """Validate then merge one drop file into processed data + sources.csv.

    Raises:
        ValueError: If the file has any invalid claim (nothing is merged).
    """
    points, errors = parse_drop(path)
    if errors:
        raise ValueError(f"{Path(path).name}: {len(errors)} invalid claims:\n"
                         + "\n".join(errors))
    summary = upsert_data_points(points)
    logger.info("Merged %s: %d points", Path(path).name, len(points))
    return {"file": Path(path).name, "points": len(points), "merge": summary}


def merge_all(drops_dir: str | Path = DROPS_DIR) -> list[dict]:
    """Merge every drop in the directory; any invalid file aborts before writes."""
    drops_dir = Path(drops_dir)
    files = sorted(drops_dir.glob("*.json"))
    if not files:
        logger.info("No drop files in %s", drops_dir)
        return []
    # Validate ALL before merging ANY, so a bad file can't half-land a batch.
    all_errors: list[str] = []
    for f in files:
        _, errors = parse_drop(f)
        all_errors.extend(errors)
    if all_errors:
        raise ValueError(f"{len(all_errors)} invalid claims across drops:\n"
                         + "\n".join(all_errors))
    return [merge(f) for f in files]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    args = sys.argv[1:]
    if args and args[0] == "--check":
        ok = all(check(p) for p in args[1:]) if len(args) > 1 else False
        sys.exit(0 if ok else 1)
    elif args and args[0] == "--all":
        results = merge_all()
        print(json.dumps(results, indent=2))
    elif args:
        print(json.dumps([merge(p) for p in args], indent=2))
    else:
        print("Usage: python -m lib.ingest.research_drop "
              "[--check <file>...] | [--all] | [<file>...]")
        sys.exit(1)
