# Plan: Hosted Vercel Dashboard for bpc-intel

> Architecture and phased build plan for a hosted web dashboard that surfaces
> the bpc-intel market-intelligence system. Produced by a planning pass over the
> full repo (2026-07-23). This is a plan only — no code has been written yet.
> Execute it with the one-shot prompt at the end (or section by section).

## 0. What shapes everything below

Three facts from the repo drive the whole design:

1. **The hard analytical work is already done in Python and is the single source of truth.** `lib/reports/_context.py` is effectively a finished view-model. Its functions (`headline`, `segment_rows`, `reconciliation`, `shares`, `corridor_context`, `india_value_chain_context`, `full_context`) already reshape raw `DataPoint`s into exactly the dicts a dashboard needs, and they carry evidence metadata (basis, confidence, source, notes) on every figure. The analysis layer beneath it (`lib/analysis/sizing.py`, `share.py`, `_load.py`) computes the reconciliation gap, coverage-qualified market shares, and the "best size" selection rules. **None of this can be re-implemented in TypeScript without risking divergence from the governed Python logic** — and divergence would break the CLAUDE.md rule that every number traces to `data/sources.csv`.

2. **The data is static between refreshes and already git-committed.** The 16 `data/processed/*.json` files and `data/sources.csv` are tracked in git. `data/raw/` is gitignored. Refresh happens by re-running Python locally, which rewrites processed files, then committing.

3. **Market share and corridor sizing are computed, not stored.** Company revenues live in `*_total_bpc.json` with the company name embedded in the `notes` field (`"Company: Hindustan Unilever — ..."`), parsed by regex and joined to roles in `config/companies.yaml`. Shares are derived at read time by `compute_shares()`. Corridor sizing is a `[CORRIDOR]`-tagged filtered slice.

**Architectural consequence: the Python side stays the brain; the Next.js app is a pure presentation layer over a Python-emitted JSON bundle.**

## 1. Framework & Stack

**Recommendation: Next.js (App Router) + TypeScript on Vercel, statically generated.**

- The IA is a set of mostly-static pages keyed on segment/geography. App Router file-based routing plus `generateStaticParams` maps one-to-one onto `/segment/[id]`, `/korea`, `/india`, etc.
- There is no runtime data source. Every page can be built as static HTML at deploy time (SSG), reading the committed JSON bundle at build — fast loads, no serverless cold starts, near-zero hosting cost.
- Vercel is the first-party host for Next.js; zero-config deploys, preview URLs per push.

Current versions (July 2026): Next.js 16.2.x is stable (Turbopack default, React 19.2). Note Next 16 renamed the middleware file to `proxy.ts` — relevant to auth below.

- **Language:** TypeScript throughout. Generate TS types from the Pydantic schema so they cannot drift.
- **Styling:** Tailwind CSS + **shadcn/ui** (Radix primitives, copy-into-repo components) for tables, tabs, badges, tooltips — full control over the bespoke evidence-badge components. A serif display face for headlines over a clean sans for data reads "consulting-grade." Avoid a heavy opinionated kit like Tremor as the shell.
- **Charting: re-render natively, do not display the matplotlib PNGs.** Recharts is the pragmatic default. The decisive argument: because every `DataPoint` carries `source`, `value_basis`, and `confidence`, a native chart can put that provenance in the hover tooltip on every bar and dot. Making evidence integrity visible is the stated product goal, so interactive charts are the feature. Keep the PNGs as downloadable artifacts only.

## 2. The Data Bridge (the crux)

**Recommendation: a build-time transform — a Python "web export" module that reuses the existing `_context.py`/analysis functions and emits a versioned JSON bundle into `web/public/data/`, committed to git. Next.js reads that bundle at build time. Vercel's build stays pure Node.**

Options evaluated:
- **(a) Static-import the raw `data/processed/*.json` + `sources.csv` directly.** Rejected as primary — the app would have to re-implement `top_down_size`'s selection priority, `compute_shares`'s coverage logic, and `reconcile`'s mismatch rules in TypeScript. Duplicates governed logic and will drift. (The one file fine to ship near-raw is `sources.csv`, since the ledger page just lists it.)
- **(b) Build-time transform into a web-optimized bundle.** Recommended. The transform already exists in Python; a thin emitter calls it and serializes the result.
- **(c) API routes reading files at runtime.** Rejected. Data only changes on redeploy, so runtime reads add serverless cold-start latency for nothing.

### 2.1 The exporter

Add one module, `lib/web_export.py` (plus a `/web-export` slash command to match the existing `commands/` pattern). It imports the existing functions and writes route-aligned JSON files. No new market logic — only serialization.

Output layout under `web/public/data/`:
- `overview.json` <- `_context.full_context()` (yields Korea + India headline, segment rows, shares, reconciliation, corridor, gaps).
- `korea.json`, `india.json` <- per-geography slices.
- `corridor.json` <- `_context.corridor_context()`.
- `india_value_chain.json` <- `_context.india_value_chain_context()`.
- `segments/{segment_id}.json` <- for each of the 12 taxonomy segments, both geographies: the computed size/growth/cagr row from `segment_rows` plus the full raw `DataPoint` list from `lib/analysis/_load.load_points(geo, seg)` so drilldowns show every underlying number with badges.
- `sources.json` <- parse `data/sources.csv` (pandas already a dependency) into typed rows.
- `gaps.json` <- structured gaps (from `lib/analysis/gaps.py`), so the page can filter.
- `charts/*.json` <- the chart *series* (not PNGs): reuse the data-prep inside `lib/reports/charts.py`. Emit as plain `{label, value, meta}` arrays for Recharts.
- `meta.json` <- generated timestamp, git commit SHA, `config/exchange_rates.yaml` (rates + dates), taxonomy segment id->name map, and the confidence + value-basis legends from CLAUDE.md.

### 2.2 Two transforms the exporter should add (UI-driven, not new intelligence)

- **USD convenience field for size metrics.** Data mixes `usd_bn`, `krw_tn`, `inr_cr`, `inr_bn`. For cross-geography charts, attach a derived `value_usd_bn` using `lib/transforms/currency.py` and pinned rates, **preserving the original value/unit/basis** and recording the rate used. Hard rule: never normalize *across* `value_basis` (RETAIL vs NET_REALISATION vs EXPORT_FOB stay separate) — mirrors `reconcile()`'s existing refusal.
- **Company-share series pre-flattening.** Emit `compute_shares()` output verbatim including its `qualifier` string, so the UI shows the coverage caveat next to the chart.

### 2.3 Type safety

Generate `web/types/schema.ts` from `lib/transforms/schema.py` at export time (Pydantic `.model_json_schema()` -> `json-schema-to-typescript`). A schema change then surfaces as a compile error, not a silent bug.

### 2.4 Why this is simplest-robust

One `git push` ships new data and triggers redeploy atomically. The bundle is diff-able in git (matches the repo-as-deliverable ethos). Vercel needs no Python runtime. The dashboard literally cannot display a number the Python layer didn't compute.

## 3. Refresh Model

Vercel serverless cannot reliably run pytrends, scrapers, pandas, matplotlib, or the MCP-based fetchers. So the refresh loop is **local-first**:

1. Run fetchers / ingest as today (`/refresh`) -> rewrites `data/raw/` then `data/processed/*.json`, appends `data/sources.csv`.
2. Regenerate reports (`python -m lib.reports.snapshot full`, `corridor`, `india`).
3. **New step:** `python -m lib.web_export` -> rewrites `web/public/data/*.json`.
4. `git commit && git push`.
5. Vercel auto-deploys on push to `main`. Preview deploys appear for any branch/PR.

**Fetcher key status:** DART needs an OpenDART key (`config/api_keys.yaml`, gitignored). Comtrade is keyless (500/day). OpenAlex keyless. Tavily uses the stored REST key. Screener scrapes. q-commerce is opt-in (Playwright).

**Optional CI assist:** a scheduled GitHub Action can run only the deterministic keyless fetchers (Comtrade best candidate), regenerate processed + bundle, and commit back to `main` (redeploys). Do not run pytrends or MCP-based fetchers in CI.

## 4. Information Architecture / Routes

```
/                     Overview: KR x India headline comparison cards, key charts,
                      value-basis + confidence legends, jump-links.
/korea                KR segment table, listed-player shares, exports-by-segment.
/india                IN segment table, listed-player shares, sizing reconciliation.
/india/value-chain    India imports/make split, margins, pricing, supply chain, demand.
/segment/[id]         Per-segment drilldown (12 static params). Both geographies;
                      every underlying DataPoint with basis/confidence/source.
/corridor             K-beauty Korea->India: conduit->brand map, trade-flow chart,
                      corridor sizing, India-side players, q-commerce assortment,
                      whitespace ranking, CDSCO regulation.
/sources              Filterable, searchable, sortable ledger of all rows. Confidence
                      + value-basis coding always visible.
/gaps                 Gaps register: missing segment x geo x metric combos.
/methodology          The evidence constitution: value-basis definitions, confidence
                      levels, FX rates + dates, MRP<->net-realisation note, the three
                      Korean measures warning.
```

`/methodology` matters more than it looks: for a consulting-grade audience the evidence discipline is the differentiator — give it a first-class page.

## 5. Key UI Components

- **`BasisBadge` / `ConfidenceBadge`** — color-coded chips (HIGH green, MEDIUM amber, LOW grey, ESTIMATE hatched; RETAIL/NET_REALISATION/EXPORT_FOB/IMPORT_CIF/MRP/PRODUCTION each distinct). The visual backbone of the evidence story.
- **`Figure` / `ProvenanceTooltip`** — renders a value with unit + a hover card (period, basis, confidence, source, URL, notes). Mirrors the `fig()` Jinja macro.
- **`HeadlineComparisonCard`** — one metric, KR vs IN, USD-normalized big with original unit + basis + source beneath.
- **`SegmentTable`** — rows per segment, cells are `Figure` with badges; missing data as "—".
- **`ReconciliationCallout`** — the top-down vs bottom-up panel; renders the "not computed (bases not comparable)" state as a designed feature, listing the mismatch strings. A signature moment: the system refusing to fake a number.
- **`CorridorMap`** — conduit cards (Nykaa, Tira, Flipkart, Amazon, q-commerce) each listing K-brands carried, from `corridor.yaml`; plus whitespace ranking, q-commerce assortment split, and CDSCO panel.
- **`SourcesTable`** — client-side filter by geography/segment/confidence/value-basis, free-text search, sortable columns, external link per row.
- **`ChartCard`** wrappers around Recharts; each bar's tooltip carries source + basis + confidence.
- **`Legend`** — persistent value-basis and confidence legends.

## 6. Auth / Privacy

**Gate it at the application layer, not Vercel's paid protection.** Two reasons to gate: (a) the highest-confidence figures are Euromonitor Passport / Statista derived, whose licenses generally prohibit public redistribution; (b) it is the owner's in-progress research.

Pricing reality (July 2026): Vercel's built-in Password Protection is Enterprise or a $150/mo Pro add-on. Vercel Authentication is free but only admits Vercel-project members (wrong for sharing with a professor).

**Recommendation:** a lightweight middleware password gate in the app itself — a `proxy.ts` (Next 16's renamed middleware) checks a signed cookie; absent -> `/login` posts a shared password compared to `process.env.SITE_PASSWORD`, sets an HTTP-only signed cookie. Free on Hobby, shareable with one password.

**Licensing flags to surface in-product:** a footer/attribution line and a disclaimer on `/methodology` (Euromonitor/Statista figures under academic fair-use for personal research; do not redistribute). Consider whether HIGH-confidence licensed rows show exact or rounded/banded figures — a decision for the owner.

## 7. Repo Structure

**Recommendation: monorepo.** Add a `web/` directory to this repo; set Vercel's Root Directory to `web/`. The bundle is generated *from* the Python data, so co-locating means one commit refreshes data and redeploys UI with no cross-repo sync. Matches the "repo is the deliverable" ethos. `.gitignore` needs `web/node_modules/` and `web/.next/`; the `web/public/data/*.json` bundle **is** committed (it is the deploy input).

## 8. Deployment Steps

1. Scaffold `web/` with `create-next-app` (TypeScript, Tailwind, App Router, ESLint).
2. Add shadcn/ui, Recharts, a CSV/type-gen dev dependency.
3. Write `lib/web_export.py`; run it to emit `web/public/data/*.json` and `web/types/schema.ts`.
4. Build pages/components per phases below; verify locally with `next dev` reading the committed bundle.
5. Add the `proxy.ts` password gate.
6. Commit everything including the JSON bundle.
7. On Vercel: New Project -> import `github.com/Rohnit11/bpc-intel` -> set Root Directory = `web` -> framework auto-detects Next.js -> deploy.
8. Add env vars `SITE_PASSWORD` + a cookie-signing secret; redeploy.
9. (Optional) attach a custom domain.
10. Thereafter: `git push` -> auto-deploy; PRs get preview URLs.

## 9. Phased Build Order (MVP -> full)

- **Phase 0 — Bridge + scaffold.** `lib/web_export.py`, the JSON bundle, TS types, `create-next-app`, Tailwind, shadcn/ui, the `BasisBadge`/`ConfidenceBadge`/`Figure` primitives, the password gate.
- **Phase 1 — MVP: Overview + Sources + Methodology.** The three pages that tell the core story fastest. Ship and get feedback.
- **Phase 2 — Korea + India pages.** Segment tables with badges, the two shares charts, exports chart. Native Recharts with provenance tooltips.
- **Phase 3 — Segment drilldowns.** `/segment/[id]` for all 12, both geographies, full DataPoint listing. The reconciliation callout on `/india`.
- **Phase 4 — Corridor.** Conduit->brand map, trade-flow chart, corridor sizing, India-side players, q-commerce assortment, whitespace, CDSCO panel.
- **Phase 5 — Gaps + India value chain + polish.** Gaps register page, value-chain narrative, dark mode, print-to-PDF stylesheet, per-table CSV download.
- **Phase 6 — Optional automation.** GitHub Actions cron for the keyless Comtrade refresh, committing back to `main`.

## 10. Open Questions / Decisions Needed from the Owner

1. **Hosting tier and auth:** confirm Hobby (free) + middleware password gate vs paying for Vercel's built-in protection. (Recommend the free gate.)
2. **Licensed-source display:** show Euromonitor/Statista HIGH-confidence figures exactly, or rounded/banded, behind the gate?
3. **Audience:** who gets the password — just the owner, HEC reviewers, or wider?
4. **Refresh ownership/cadence:** manual local only, or the Comtrade GitHub Actions cron? Is the OpenDART key available for CI secrets?
5. **Charts:** confirm fully replacing matplotlib PNGs with native Recharts (recommended), keeping PNGs only as downloads.
6. **USD normalization:** confirm the overview may show a derived USD-common value for cross-geography size comparison (stays within one value-basis, always shows the original).
7. **Visual identity:** any color/type/logo direction, or proceed with a neutral consulting palette (serif headlines, clean sans data)?
8. **Custom domain:** wanted, or is the `*.vercel.app` URL fine?
9. **Data depth:** most processed data is single-period snapshots, so charts will be comparative bars rather than trend lines. Confirm acceptable, or flag which time series to prioritize collecting.

## Critical files for implementation

- `lib/reports/_context.py` — the existing view-model; the web exporter calls these functions verbatim to build the bundle.
- `lib/transforms/schema.py` — the `DataPoint`/`SegmentFile` schema; source of the generated TS types and the bundle shape.
- `lib/analysis/sizing.py` (with `share.py`, `_load.py`) — computed reconciliation and top-down/bottom-up logic the UI must consume, not re-derive.
- `data/sources.csv` — the ledger that becomes `sources.json` and the `/sources` page.
- `config/corridor.yaml` — the conduit->brand registry, India-side players, q-commerce assortment, whitespace, and CDSCO content for the `/corridor` page.

## Reference

- Vercel Password Protection: https://vercel.com/docs/deployment-protection/methods-to-protect-deployments/password-protection
- Vercel Deployment Protection: https://vercel.com/docs/deployment-protection
- Next.js Static Exports guide: https://nextjs.org/docs/app/guides/static-exports
