"""End-to-end reconciliation and evidence-integrity tests (BUILD-SPEC Phase 8).

Distinct from test_analysis.py (which unit-tests the reconciliation math on
synthetic inputs), this module runs against the *real* repo data:

  * the processed <-> ledger invariant — no number exists without a source row;
  * reconciliation on real KR/IN data always documents its outcome;
  * the rendered snapshot actually surfaces the reconciliation gap.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from lib.analysis import sizing
from lib.reports import verify

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = PROJECT_ROOT / "reports" / "latest" / "snapshot.md"


class TestEvidenceInvariant:
    """CLAUDE.md rule 2: every processed number has a data/sources.csv row."""

    def test_no_unsourced_processed_numbers(self):
        result = verify.verify_processed_ledger()
        assert result["ok"], (
            "Unsourced processed numbers (no ledger row):\n"
            + "\n".join(result["orphans"])
        )
        assert result["orphans"] == []

    def test_processed_and_ledger_counts_align(self):
        result = verify.verify_processed_ledger()
        # Every processed point is ledgered and vice versa -> no stale rows.
        assert result["stale"] == []
        assert result["n_processed"] == result["n_ledger"]

    def test_full_verification_passes(self):
        assert verify.run_verification()["ok"]


class TestReconciliationOnRealData:
    """For every geography with both figures, reconciliation is documented."""

    @pytest.mark.parametrize("geography", ["KR", "IN"])
    def test_reconcile_is_documented(self, geography):
        td = sizing.top_down_size(geography, "total_bpc")
        bu = sizing.bottom_up_size(geography, "total_bpc")
        if td is None or bu is None:
            pytest.skip(f"{geography} lacks both top-down and bottom-up figures")
        report = sizing.reconcile(td, bu)
        # A reconciliation must resolve to *something* auditable: either a
        # numeric gap, or named mismatches, or an explanatory note.
        documented = (
            report["gap_pct"] is not None
            or report["mismatches"]
            or report.get("note")
        )
        assert documented, "reconcile() produced no gap, mismatch, or note"

    def test_incomparable_bases_are_not_publishable(self):
        """India top-down (RETAIL) vs bottom-up (NET_REALISATION) must not publish."""
        td = sizing.top_down_size("IN", "total_bpc")
        bu = sizing.bottom_up_size("IN", "total_bpc")
        if td is None or bu is None:
            pytest.skip("India lacks both figures")
        report = sizing.reconcile(td, bu)
        if report["mismatches"]:
            assert report["publishable"] is False
            assert report["gap_pct"] is None


class TestReconciliationSurfacedInReport:
    """The generated snapshot must actually show the reconciliation."""

    def test_snapshot_documents_reconciliation(self):
        if not SNAPSHOT.exists():
            pytest.skip("snapshot.md not generated yet (run /report)")
        text = SNAPSHOT.read_text(encoding="utf-8").lower()
        assert "reconciliation" in text
        assert "publishable" in text


class TestReportCoverage:
    """Report numbers either trace to the ledger or are declared derived."""

    def test_every_latest_report_has_a_coverage_entry(self):
        result = verify.run_verification()
        names = {r["report"] for r in result["reports"]}
        assert "snapshot.md" in names
        # The snapshot mixes ledgered facts with derived analytics, so some
        # matches are expected but not 100% coverage.
        snap = next(r for r in result["reports"] if r["report"] == "snapshot.md")
        assert snap["n_matched"] > 0
