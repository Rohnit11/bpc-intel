# /insights [segment]

Write the "Analyst read" for one segment, or all 12 segments + `total_bpc` if no
argument is given. Unlike every other command in this file, there is no
deterministic script for this — the analysis itself is the job, so you (Claude)
do the reasoning directly, under the same no-fabrication discipline as every
other number in this system.

## What this is (and is not)

An analyst read is **commentary on figures that already exist in
`data/processed/`**, not a new source of numbers. It never introduces a value
that isn't already a `DataPoint` in the system. Someone new to a segment should
be able to read three short sections — what the number says, what caveats
apply, which direction it's heading — without re-deriving that from a table of
raw figures themselves.

## Inputs

For the segment(s) in scope, read:
- `data/processed/KR_<segment>.json` and `data/processed/IN_<segment>.json`
  (or the `total_bpc` files for the whole-market read) — the raw `DataPoint`s.
- `web/public/data/segments/<segment>.json` if it already exists — it's the
  same data pre-shaped into `size`/`growth`/`cagr`/`export` rows, faster to
  read than re-deriving picks from raw points. For `total_bpc`, use
  `web/public/data/korea.json` / `india.json`'s `headline` blocks instead.
- `config/corridor.yaml` — only if the segment is corridor-relevant
  (skincare, sun_care, colour_cosmetics, hair_care, dermocosmetics have
  `[CORRIDOR]`-tagged data; check for `[CORRIDOR]` in that segment's notes).
- The confidence and value-basis legends (CLAUDE.md's own tables, or
  `web/public/data/meta.json`'s `confidence_legend` / `value_basis_legend`).

## Non-negotiable rules

1. **Never state a number that isn't already a DataPoint you were given.**
   Don't derive a new implied statistic by combining two DataPoints (e.g.
   don't divide one figure by another to invent a per-unit number that
   doesn't exist in the data).
2. **Name the confidence and value_basis in plain language** whenever a figure
   carries the interpretation ("a LOW-confidence aggregator estimate", "the
   HIGH-confidence retail figure from Euromonitor") — never present all
   figures as equally solid.
3. **Forecasts are forecasts.** A `cagr_forecast` or any figure with a
   forward-looking period (e.g. "2025-2030") gets called a forecast, never
   stated as if it already happened. A `growth_yoy` on a past period is
   observed growth.
4. **Never net two figures across different `value_basis`** (RETAIL vs
   NET_REALISATION vs EXPORT_FOB vs MRP vs PRODUCTION, etc.) as if they were
   comparable. For the KR-vs-IN "combined" section, only compare using
   `value_usd_bn` when BOTH sides have it (same currency, same basis by
   construction) — if one side lacks it, say a fair comparison isn't possible
   and why, rather than comparing anyway.
5. **Missing means missing.** If a metric is null/absent for a
   segment × geography, say so plainly ("no export figure is available for
   this segment") — never fill the gap with a plausible-sounding number.
6. **Reflect reconciliation tension honestly.** If the geography's top-down
   vs bottom-up reconciliation doesn't match (different value_basis, gap
   over 20%, etc. — see `reconciliation` in the geography bundle), say so
   rather than quietly picking one number to feature.
7. **Plain, analytical tone.** No marketing language ("exciting", "huge
   opportunity", "game-changing"). Describe what the data supports, and
   separately, what it does not tell you.
8. Note explicitly when a figure is `[CORRIDOR]`-tagged (a K-beauty-in-India
   subset, not the whole segment) rather than treating it as segment-wide.

## What to write, per segment

For **each geography** (KR, IN):
- `read` (2-4 sentences): what the market size / growth / CAGR / export
  figures, read together, actually say about this segment's current
  position.
- `trend` (1-3 sentences): what direction it's heading, strictly from
  `growth_yoy` / `cagr_forecast` if present. If neither is present: "growth
  direction cannot be assessed from current data."
- `caveats` (1-2 sentences): the single most important reason to be careful
  taking these numbers at face value (confidence level, listed-players-only
  coverage, `[CORRIDOR]` subset, organised-vs-unorganised coverage, etc.)

Then one **`combined`** section (2-4 sentences): South Korea vs India for this
segment, side by side — using `value_usd_bn` only where both sides have it,
naming when a fair comparison isn't possible, and noting Korea→India corridor
relevance if corridor data exists for this segment.

## Output

Write `data/manual/insights/<segment>.json` (create the directory if needed):

```json
{
  "segment": "skincare",
  "generated_at": "2026-07-24T00:00:00Z",
  "KR": {"read": "...", "trend": "...", "caveats": "..."},
  "IN": {"read": "...", "trend": "...", "caveats": "..."},
  "combined": {"read": "..."}
}
```

`total_bpc` uses the same shape (segment: "total_bpc"), built from each
geography's `headline` block instead of a segment row.

## After writing

Run `python -m lib.web_export` — it copies `data/manual/insights/*.json`
verbatim into `web/public/data/insights/*.json` (pure serialization, no new
logic) so the dashboard's `AnalystRead` panels pick it up on next `next build`.

## 3+ segments = parallel subagents

Per this repo's working style, generating insights for several segments at
once should be parallelized: dispatch one subagent per segment (each reads
its own two processed files + the corridor config, writes its own output
file) rather than working through all 12 sequentially in one context.
