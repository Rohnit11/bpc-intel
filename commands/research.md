# /research [tier|segment]

Execute the research backlog (docs/research-backlog.md) — the data-expansion
pass that precedes the entry-analysis build. Run with a tier ("tier1") or a
segment id to scope; no argument = work the backlog top-down.

This command is the protocol layer for whatever research capability is
available (a dedicated market-research skill, Tavily, web fetch, paid-database
manual drops). The capability may change; these rules do not.

## Per gap, in order

1. **Paid-database first.** If a Passport/Statista/Capital IQ export exists
   for the cell, drop it in data/manual/ and run /ingest (handler by filename
   prefix — see commands/ingest.md). Lands as HIGH confidence.
2. **Secondary web second.** Research from credible trade press/industry
   sources; every URL actually fetched and verified; ingest via a curated
   ingest module (pattern: lib/ingest/india_curated.py) or generic_csv with
   a mapping. Tag MEDIUM (credible secondary) or LOW (aggregator) honestly.
3. **Leave it standing third.** If neither yields a defensible number, the
   gap stays open. A standing gap is information; a fabricated or
   over-extrapolated number is contamination.

## Every new DataPoint (no exceptions)

- Row in data/sources.csv; `value_basis` mandatory; original currency + USD
  equivalent at the pinned rate (config/exchange_rates.yaml).
- `sub_segment` must match config/taxonomy.yaml exactly — no ad-hoc names.
- India: FY periods for company data, organised/unorganised coverage stated,
  MRP flagged as MRP. Korea: CY periods; retail / export / production never
  conflated; duty-free flagged.
- K-beauty-in-India figures carry "[CORRIDOR]" in notes.
- Estimates: confidence=ESTIMATE with methodology, assumptions, sensitivity.

## After each batch

1. `python -m pytest tests/ -q` — schema validation still green.
2. `python -m lib.web_export` — refresh the dashboard bundle.
3. `/insights <segment>` for any segment whose data changed materially.
4. Commit + push (branch → PR per repo convention) so the live dashboard
   tracks research in near-real-time.
5. When a Tier-1 row completes, check whether commands/entry-analysis.md can
   now run at sub-segment depth for that segment — if yes, run it.
