# /report

Generate the full BPC market-intelligence snapshot (Korea × India + corridor).

Runs `lib/reports/snapshot.py::generate_full_report`:
1. Regenerates charts (matplotlib) into `reports/latest/charts/`.
2. Renders `full_report.md.j2` from processed data + the analysis layer.
3. Archives the previous snapshot, writes `reports/latest/snapshot.md`.

Every figure shows its value basis, period, confidence, and source inline.
Reconciliation refuses to publish a gap >20% and names the mismatch.

Run: `python -m lib.reports.snapshot full`
