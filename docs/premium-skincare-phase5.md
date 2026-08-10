# Premium Skincare — Phase 5 output: the dashboard section

> Executes Phase 5 of `docs/premium-skincare-brief.md`: the `/premium-skincare`
> route, its nav entry, and the export path that carries the thread's artifacts
> and findings into the web bundle. Run 2026-08-10. Namespace `[PREMIUM-SKIN]`.
>
> This is a **presentation** phase. It produces no new market claim, no new
> DataPoint, and no new row in `data/sources.csv`. Everything the page shows was
> already on disk after Phases 1-4.

## 0. What shipped

A new section, **Premium Skincare**, at `/premium-skincare`, sixth in the nav
between Corridor and Players. It renders the four research phases as one
argument, in the order the evidence actually binds:

1. **The read** — the band-level Porter overall verdict, and the one sentence
   that decides it (order size swings contribution margin 57.3pp).
2. **Does the band hold under discounting?** — retention by platform, brand
   group, format and hero product, both price frames, and the frame-1 vs frame-2
   comparison that confirmed the Rs1,900 floor.
3. **Fit, and what buyers actually complain about** — complaint themes with the
   negation split kept visible, for Korean sunscreen (negative and positive
   frames) and pigmentation serums, plus the self-declared tone table and the
   Phase 2 sourced findings.
4. **Is "Korean" load-bearing?** — the purchase-driver ranking with the two
   Korea-provenance drivers coloured apart, the by-origin encroachment table,
   and the Phase 3 sourced findings.
5. **Unit economics** — landed COGS against MRP at both order sizes, the
   sensitivity ranking, launch cash at risk, the unresolved-input list, and the
   full assumptions table with each input's source, range and confidence.
6. **Entry lanes** — all four, with the case against the primary lane in a
   disclosure rather than buried.
7. **Porter re-rated at band level** — five forces as evidence-backed judgments.
8. **Risks, and what is still open** — the risk register, the offline
   INSUFFICIENT block rendered as *research needed*, and the ranked
   research backlog.

## 1. The rule this section is built on

**The page derives no figure of its own.** Every number rendered is read from an
artifact that Python wrote. This is the same contract `lib/web_export.py` already
states ("the dashboard cannot display a number this module did not receive from
Python"), applied one layer up.

Two consequences worth recording, because both came up while building:

- **The Rs1,900 floor is shown as prose, not as a chart.** The retention-by-MRP-rung
  numbers (55.1% at Rs1,500-1,750 vs 96.8% at Rs2,000-2,500) exist in the Phase 4
  write-up but are *not* a field in `premium_skin_band_frame2.json` — they were
  computed ad hoc during that phase. Deriving them in the exporter or in TSX
  would have put analysis in the presentation layer, so the page shows them only
  where the artifact itself carries them, inside
  `price_frame_comparison.verdict`. If that cut should be a first-class panel,
  the fix belongs in `lib/transforms/premium_skin_band.py`, not here.
- **Launch cash is read, not summed.** The first draft totalled
  `launch_cash_at_risk.by_sku[].total_inr` in the page and produced Rs6,258,475
  against the artifact's own Rs6,258,474 — a one-rupee rounding divergence that
  is harmless in itself and exactly the wrong habit. It now renders
  `entry.unit_economics.launch_cash_at_risk_inr` verbatim.

Where an artifact carries a judgment rather than a figure, the judgment's own
vocabulary is preserved: a lane's `rating` is a verdict sentence
("STRUCTURALLY FAVOURED, BLOCKED ON ONE CAPABILITY QUESTION"), so it renders as
text and is **not** mapped onto a LOW/MEDIUM/HIGH pill. Inventing a scale the
analysis did not use would be the dashboard asserting something the analysis did
not. `INSUFFICIENT` renders as the existing "research needed" empty state — lane
(d), JV/licence, shows exactly that.

## 2. Export path

`lib/web_export.py` gained one function, `build_findings()`, and one line in
`export_all()`.

The **analysis artifacts needed no code change** — `build_analysis()` already
rglobs `data/manual/analysis/**/*.json`, so all six premium-skin artifacts
(`premium_skin_band`, `premium_skin_band_frame2`, `premium_skin_fit`,
`premium_skin_demand`, `premium_skin_unit_economics`, `premium_skin_entry`)
entered the bundle the first time the export was re-run.

The **findings YAMLs did not have a path** into the bundle at all.
`build_findings()` copies `config/{key}_findings.yaml` verbatim to
`web/public/data/findings/{key}.json`. It is globbed rather than named — the
same convention `lib/chat_index.py` already uses for the same files — so a future
phase's findings file reaches the dashboard with no code change. Five files now
export: `korea`, `india`, `corridor`, `premium_skin_fit`, `premium_skin_demand`.
The three non-premium files are carried because the glob is the convention; only
the two premium ones are rendered by this section so far.

Also fixed in passing: `ANALYSIS_DIR` was assigned twice on consecutive lines.

### 2.1 The bundle was four phases stale

Re-running the export brought in everything Phases 1-4 had written to
`data/sources.csv` and `data/processed/` since the last export on 2026-08-01:
**402 `[PREMIUM-SKIN]` rows** newly reached `sources.json`, along with the
skincare and sun_care segment point-level updates. Those are visible on
`/sources`, `/segment/skincare` and `/gaps` as well as here. Nothing was
overwritten — the export is a pure re-serialisation.

## 3. Charts

Four charts, all Recharts, all reading the house tokens from `globals.css` so
they follow the light/dark switch:

| Chart | Form | Why that form |
|---|---|---|
| Complaint themes | Grouped horizontal bars, asserted vs negated | The negation split IS the Phase 2 finding; a combined bar would invert it |
| Purchase drivers | Ranked horizontal bars, Korea drivers coloured apart | Where `korea_origin` lands in the ranking is the Phase 3 answer |
| Landed COGS vs MRP | Grouped bars, one axis, 100%-of-MRP reference line | A bar past the line is a SKU that loses money at full price |
| Sensitivity | Ranked bars, decided vs unresolved coloured apart | Separates what is unknown from what is merely undecided |

Band retention is deliberately **a table, not a chart**: retention only means
something beside the SKU count it is computed over and the discount depth that
qualifies it, and a reader needs all three at once.

**One colour decision was changed by validation.** The complaint chart began as
red (complained of) vs green (explicitly absent), which is the obvious semantic
read and fails colourblind separation: ΔE 4.1 under deuteranopia against a floor
of 8. It ships as red vs blue, which clears at ΔE 23.8 light and 25.7 dark. The
other three pairs (blue/orange, blue/green with per-bar labels) were validated in
both modes and pass.

## 4. Files touched

| File | Change |
|---|---|
| `web/app/premium-skincare/page.tsx` | New route, the section itself |
| `web/components/premium-skin/*.tsx` | 7 new components (4 charts, band table, lanes, findings list, stat tile) |
| `web/types/premium-skin.ts` | Artifact shapes, kept separate from `analysis.ts` |
| `web/lib/data.ts` | `getFindings(key)` loader |
| `web/components/nav-bar.tsx` | One nav entry |
| `lib/web_export.py` | `build_findings()`, wired into `export_all()`; duplicate constant removed |
| `web/public/data/**` | Re-exported bundle: 6 analysis artifacts + 5 findings files added, 402 `[PREMIUM-SKIN]` source rows caught up |

## 5. Verification

- `npx tsc --noEmit` clean.
- `npm run build` succeeds; `/premium-skincare` prerenders as **static** content,
  which means the server component executed against the real artifacts with no
  missing-field or null errors.
- The prerendered HTML was probed for the load-bearing values and they render as
  the artifacts state them: 83.1% / 84.1% platform retention, 3,287 reviews,
  2.2% Korean-provenance mentions, "68 absent vs 11 complained" on white cast,
  the three launch-cash totals matching `premium_skin_entry.json` exactly, and
  the offline block rendering as *research needed*.
- Every section has a null path: an artifact missing from the bundle renders
  "not in the bundle yet" and names the phase that writes it, never a 404 and
  never a blank.

## 6. What Phase 5 does not do

- **It does not deploy.** The brief's Phase 5 bullet says the section deploys to
  both Vercel projects from `main`; this work is on `feat/premium-skincare-brief`
  and has not been merged or pushed. Deployment is the owner's call.
- **It adds no analyst-read panel.** `/insights` writes those, and there is no
  insight file for this thread. The phase docs carry the interpretation instead.
- **It does not surface the SKU-level tables.** `in_band_by_mrp_skus` (380 rows)
  and `all_priced_skus` (620 rows) are in the bundle and reachable at
  `/data/analysis/premium_skin_band_frame2.json`, but the page renders the
  aggregates only. A sortable SKU browser is a reasonable next addition and is
  not in the brief's Phase 5 scope.
- **It does not close the offline gap**, which remains the thread's largest open
  risk. The page states that rather than smoothing over it.
