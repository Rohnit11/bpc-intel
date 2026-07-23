# /verify

Cross-check that every number in the system is backed by the source ledger.

Runs `lib/reports/verify.py`, which enforces CLAUDE.md rule 2 in three passes:

1. **processed -> ledger (hard invariant).** Every DataPoint in
   `data/processed/*.json` must have a matching row in `data/sources.csv`.
   Any orphan is an unsourced number and fails the run (exit code 1).
2. **ledger -> processed (informational).** Ledger rows with no processed point
   are flagged `stale` (fixable with `lib.transforms.merge.rebuild_sources_csv`).
3. **report -> ledger (coverage diagnostic).** Numbers rendered in
   `reports/latest/*.md` are matched against ledger values. Derived analytics
   (computed market shares, reconciliation gaps, per-capita, config references)
   legitimately do not match verbatim, so unmatched numbers are listed for
   review — never a failure.

Run: `python -m lib.reports.verify`

Exit 0 = evidence invariant holds; exit 1 = at least one unsourced number.
