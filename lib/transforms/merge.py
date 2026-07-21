"""Idempotent upsert of DataPoints into data/processed/ segment files."""
from __future__ import annotations

import csv
import logging
from collections import defaultdict
from datetime import date
from pathlib import Path

from lib.transforms.schema import DataPoint, SegmentFile, load_segment_file, save_segment_file

logger = logging.getLogger("bpc_intel.merge")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
SOURCES_CSV = PROJECT_ROOT / "data" / "sources.csv"


def _identity_key(dp: DataPoint) -> tuple:
    """Key that identifies 'the same claim' regardless of access date."""
    return (
        dp.geography, dp.segment, dp.sub_segment, dp.metric, dp.period,
        dp.value_basis, dp.tier, dp.source_name, dp.notes,
    )


def upsert_data_points(
    points: list[DataPoint],
    processed_dir: str | Path = PROCESSED_DIR,
) -> dict[str, dict[str, int]]:
    """Merge new DataPoints into processed segment files without duplicating.

    A point matching an existing one on its identity key (everything except
    value and date_accessed) replaces it; otherwise it is appended. Running
    the same fetcher twice therefore leaves files unchanged.

    Args:
        points: New DataPoints from a fetcher or ingest handler.
        processed_dir: The processed-data directory.

    Returns:
        Per-file summary: {filename: {"added": n, "updated": n, "unchanged": n}}.
    """
    processed_dir = Path(processed_dir)
    grouped: dict[tuple[str, str], list[DataPoint]] = defaultdict(list)
    for dp in points:
        grouped[(dp.geography, dp.segment)].append(dp)

    summary: dict[str, dict[str, int]] = {}
    for (geo, seg), new_dps in sorted(grouped.items()):
        fname = f"{geo}_{seg}.json"
        path = processed_dir / fname
        if path.exists():
            sf = load_segment_file(path)
        else:
            sf = SegmentFile(geography=geo, segment=seg,
                             last_updated=date.today(), data_points=[])

        existing = {_identity_key(dp): i for i, dp in enumerate(sf.data_points)}
        added = updated = unchanged = 0
        for dp in new_dps:
            key = _identity_key(dp)
            if key in existing:
                idx = existing[key]
                if sf.data_points[idx].value == dp.value:
                    unchanged += 1
                else:
                    sf.data_points[idx] = dp
                    updated += 1
            else:
                sf.data_points.append(dp)
                existing[key] = len(sf.data_points) - 1
                added += 1

        if added or updated:
            sf.last_updated = date.today()
            save_segment_file(sf, path)
        summary[fname] = {"added": added, "updated": updated, "unchanged": unchanged}
        logger.info("%s: %d added, %d updated, %d unchanged", fname, added, updated, unchanged)

    append_to_sources_csv(points)
    return summary


def append_to_sources_csv(points: list[DataPoint], csv_path: str | Path = SOURCES_CSV) -> int:
    """Append sources.csv rows for DataPoints not already ledgered (CLAUDE.md rule 2).

    Deduplicates on (value, geography, segment, period, value_basis,
    source_name, notes) so reruns never duplicate rows.

    Args:
        points: DataPoints to ledger.
        csv_path: The master source ledger.

    Returns:
        Number of rows appended.
    """
    csv_path = Path(csv_path)
    existing: set[tuple] = set()
    if csv_path.exists():
        with csv_path.open(encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                existing.add((row["value"], row["geography"], row["segment"],
                              row["period"], row["value_basis"],
                              row["source_name"], row["notes"]))

    new_rows: list[list[str]] = []
    for dp in points:
        key = (str(dp.value), dp.geography, dp.segment, dp.period,
               dp.value_basis, dp.source_name, dp.notes or "")
        if key in existing:
            continue
        existing.add(key)
        claim = f"{dp.geography} {dp.segment} {dp.metric}" + (f" [{dp.tier}]" if dp.tier else "")
        new_rows.append([
            claim, str(dp.value), dp.unit, dp.currency, dp.geography, dp.segment,
            dp.period, dp.period_type, dp.value_basis, dp.source_name,
            dp.source_url or "", dp.date_accessed.isoformat(), dp.confidence,
            dp.notes or "",
        ])
    if new_rows:
        with csv_path.open("a", newline="", encoding="utf-8") as fh:
            csv.writer(fh).writerows(new_rows)
    logger.info("Appended %d new rows to %s", len(new_rows), csv_path)
    return len(new_rows)


__all__ = ["upsert_data_points", "append_to_sources_csv"]
