"""Verify evidence integrity — every number is backed by the source ledger.

Backs the /verify command and tests/test_reconciliation.py. Enforces CLAUDE.md
rule 2 ("every quantitative claim gets a row in data/sources.csv") as an
automatable invariant, in three passes:

1. **processed -> ledger (hard invariant).** Every DataPoint in
   data/processed/*.json must have a matching row in data/sources.csv. Any
   `orphan` is a genuine unsourced number and fails verification.

2. **ledger -> processed (informational).** Ledger rows with no corresponding
   processed point are `stale` (e.g. left behind by a corrected URL). Not a
   failure — `lib.transforms.merge.rebuild_sources_csv` cleans these.

3. **report -> ledger (coverage).** Numbers rendered into reports/latest/*.md
   are matched against ledger values. Reports also contain *derived* analytics
   (computed market shares, reconciliation gaps, per-capita) that legitimately
   do not appear verbatim in the ledger, so unmatched numbers are reported for
   review, not treated as failures.
"""
from __future__ import annotations

import csv
import logging
import re
from pathlib import Path

from lib.transforms.schema import DataPoint, load_segment_file

logger = logging.getLogger("bpc_intel.reports.verify")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
SOURCES_CSV = PROJECT_ROOT / "data" / "sources.csv"
LATEST_DIR = PROJECT_ROOT / "reports" / "latest"


def _ledger_key(value: str, geography: str, segment: str, period: str,
                value_basis: str, source_name: str, notes: str) -> tuple:
    """Claim-identity key shared with lib.transforms.merge (minus access date)."""
    return (value, geography, segment, period, value_basis, source_name, notes)


def _processed_key(dp: DataPoint) -> tuple:
    return _ledger_key(str(dp.value), dp.geography, dp.segment, dp.period,
                       dp.value_basis, dp.source_name, dp.notes or "")


def _load_ledger_keys(csv_path: Path | None = None) -> set[tuple]:
    """Every claim-identity key present in data/sources.csv."""
    csv_path = csv_path or SOURCES_CSV
    keys: set[tuple] = set()
    if not csv_path.exists():
        return keys
    with csv_path.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            keys.add(_ledger_key(
                row["value"], row["geography"], row["segment"], row["period"],
                row["value_basis"], row["source_name"], row["notes"]))
    return keys


def _load_ledger_values(csv_path: Path | None = None) -> set[str]:
    """The set of raw value strings in the ledger (for report coverage matching)."""
    csv_path = csv_path or SOURCES_CSV
    values: set[str] = set()
    if not csv_path.exists():
        return values
    with csv_path.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            values.add(row["value"])
    return values


def _iter_processed(processed_dir: Path | None = None) -> list[DataPoint]:
    processed_dir = processed_dir or PROCESSED_DIR
    points: list[DataPoint] = []
    for path in sorted(processed_dir.glob("*.json")):
        points.extend(load_segment_file(path).data_points)
    return points


def verify_processed_ledger(
    processed_dir: Path | None = None, csv_path: Path | None = None
) -> dict:
    """Check the processed<->ledger invariant.

    Args:
        processed_dir: Processed-data directory (default data/processed/).
        csv_path: Source ledger (default data/sources.csv).

    Returns:
        ``{"ok": bool, "orphans": [...], "stale": [...], "n_processed": int,
        "n_ledger": int}``. ``ok`` is True only when there are no orphans
        (unsourced processed numbers). ``orphans``/``stale`` list human-readable
        claim descriptions.
    """
    processed = _iter_processed(processed_dir)
    ledger_keys = _load_ledger_keys(csv_path)
    processed_keys = {_processed_key(dp) for dp in processed}

    orphans = [
        f"{dp.geography} {dp.segment} {dp.metric}={dp.value}{dp.unit} "
        f"({dp.value_basis}, {dp.period}, {dp.source_name})"
        for dp in processed if _processed_key(dp) not in ledger_keys
    ]
    stale = [
        f"{k[1]} {k[2]} value={k[0]} ({k[4]}, {k[3]}, {k[5]})"
        for k in ledger_keys if k not in processed_keys
    ]
    return {
        "ok": not orphans,
        "orphans": sorted(orphans),
        "stale": sorted(stale),
        "n_processed": len(processed),
        "n_ledger": len(ledger_keys),
    }


# Numeric tokens in a report: 1,234.5 / 33.08 / 170 — captured without the
# surrounding currency/percent markup, which varies by template.
_NUMBER_RE = re.compile(r"(?<![\w.])(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)(?![\w])")
# Numbers that are structural noise (section numbers, table scaffolding), not
# claims. Bare four-digit years are filtered separately in _is_noise().
_IGNORE = {"1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "100", "0", "20"}


def _is_noise(token: str) -> bool:
    """True if a numeric token is structural (a section number or a year)."""
    if token in _IGNORE:
        return True
    if token.isdigit() and len(token) == 4 and 1900 <= int(token) <= 2099:
        return True  # a period year, stored separately from any claim value
    return False


def verify_report_coverage(
    report_path: Path, csv_path: Path | None = None
) -> dict:
    """Match numbers rendered in a report against ledger values (coverage only).

    Derived analytics (shares, gaps, per-capita) legitimately will not match;
    this pass is diagnostic, never a hard gate.

    Args:
        report_path: A rendered Markdown report.
        csv_path: Source ledger (default data/sources.csv).

    Returns:
        ``{"report", "n_numbers", "n_matched", "unmatched": [...]}``.
    """
    ledger_values = _load_ledger_values(csv_path)
    # Match against both the raw string and a comma-stripped float form.
    ledger_floats: set[float] = set()
    for v in ledger_values:
        try:
            ledger_floats.add(float(v.replace(",", "")))
        except ValueError:
            continue

    text = report_path.read_text(encoding="utf-8") if report_path.exists() else ""
    numbers = [m.group(1) for m in _NUMBER_RE.finditer(text)]
    unmatched: list[str] = []
    matched = 0
    for tok in numbers:
        if _is_noise(tok):
            continue
        raw = tok.replace(",", "")
        try:
            f = float(raw)
        except ValueError:
            continue
        if tok in ledger_values or any(abs(f - lf) < 1e-6 for lf in ledger_floats):
            matched += 1
        else:
            unmatched.append(tok)
    return {
        "report": report_path.name,
        "n_numbers": matched + len(unmatched),
        "n_matched": matched,
        "unmatched": unmatched,
    }


def run_verification(latest_dir: Path | None = None) -> dict:
    """Full verification: the hard processed<->ledger invariant + report coverage.

    Args:
        latest_dir: Directory of rendered reports (default reports/latest/).

    Returns:
        ``{"ok", "ledger": {...}, "reports": [...]}``. ``ok`` mirrors the
        processed<->ledger invariant (report coverage never fails the run).
    """
    latest_dir = latest_dir or LATEST_DIR
    ledger = verify_processed_ledger()
    reports = [
        verify_report_coverage(p)
        for p in sorted(latest_dir.glob("*.md"))
    ]
    return {"ok": ledger["ok"], "ledger": ledger, "reports": reports}


def format_report(result: dict) -> str:
    """Render a run_verification() result as human-readable Markdown."""
    led = result["ledger"]
    out = ["# Verification report", ""]
    verdict = "[PASS]" if result["ok"] else "[FAIL]"
    out.append(f"**Evidence invariant (processed -> ledger): {verdict}**")
    out.append("")
    out.append(f"- Processed data points: {led['n_processed']}")
    out.append(f"- Ledger claim rows: {led['n_ledger']}")
    out.append(f"- Unsourced numbers (orphans): {len(led['orphans'])}")
    out.append(f"- Stale ledger rows (informational): {len(led['stale'])}")
    if led["orphans"]:
        out += ["", "## Orphans — processed numbers with NO ledger row (must be zero)"]
        out += [f"- {o}" for o in led["orphans"]]
    if led["stale"]:
        out += ["", "## Stale ledger rows — no matching processed point (run rebuild_sources_csv)"]
        out += [f"- {s}" for s in led["stale"][:50]]
        if len(led["stale"]) > 50:
            out.append(f"- …and {len(led['stale']) - 50} more")
    out += ["", "## Report number coverage (diagnostic - derived analytics may be unmatched)"]
    out.append("| Report | Numbers | Matched to ledger | Unmatched |")
    out.append("|---|---|---|---|")
    for r in result["reports"]:
        um = ", ".join(r["unmatched"][:8]) + ("..." if len(r["unmatched"]) > 8 else "")
        out.append(f"| {r['report']} | {r['n_numbers']} | {r['n_matched']} | {um} |")
    return "\n".join(out)


if __name__ == "__main__":
    import sys

    result = run_verification()
    print(format_report(result))
    sys.exit(0 if result["ok"] else 1)


__all__ = [
    "verify_processed_ledger", "verify_report_coverage",
    "run_verification", "format_report",
]
