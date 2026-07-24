# Research Backlog — the worklist for the next research pass

> Written 2026-07-24, ahead of installing a dedicated market-research skill.
> This is the exact, prioritized list of what that pass must fill so the
> dashboard's entry-analysis layer (commands/entry-analysis.md) can run at
> full sub-segment depth. Regenerate the raw gap list any time with:
> `python -c "from lib.analysis.gaps import scan_gaps; ..."` using
> `include_sub_segments=True`.

## Current state (measured, not estimated)

- 211 DataPoints in data/processed/; only 9 carry a `sub_segment`.
- 5 of 34 taxonomy sub-segments have any data at all — all India skincare,
  mostly shelf prices from the corridor pricing sweep.
- Sub-segment gap scan: **203 open sub-segment × geography × core-metric
  combinations** (34 subs × 2 geographies × market_size/growth_yoy/
  cagr_forecast, minus IN serums_ampoules market_size which exists).
- Segment-level scan: 56 open combinations (unchanged; see /gaps on the
  dashboard).

## Why these gaps exist (so the research pass targets the right sources)

Every free/public source the fetchers reach tops out at segment level:
Comtrade HS codes blur categories (3304 = skincare + makeup), DART/Screener
give company totals, Tavily news gives headline figures, q-commerce gives SKU
prices. **Sub-segment market sizes and growth live in paid databases** —
Euromonitor Passport sub-categories, Statista, and specialist reports — which
is exactly what the ingest pipeline (lib/ingest/passport_csv.py,
statista_csv.py, generic_csv.py) was built to receive as manual drops.
Secondary-web research (Tavily-class) can fill some sub-segment figures from
credible trade press, but expect LOW/MEDIUM confidence; tag accordingly.

## Non-negotiables for every new number (same rules as everywhere)

1. Lands via a fetcher, /ingest manual drop, or is [ESTIMATE] with
   methodology. Appends a row to data/sources.csv.
2. `value_basis`, currency + USD equivalent (pinned rate), period +
   period_type (FY for India company data, CY for Korea), confidence tag.
3. `sub_segment` must match config/taxonomy.yaml exactly.
4. India numbers state organised vs unorganised coverage.
5. After ingest: `python -m lib.web_export` refreshes the dashboard bundle;
   re-run `/insights <segment>` for any segment whose data changed materially.

## Priority tiers

Ordering logic: corridor conviction (config/corridor.yaml whitespace +
conduit activity) first, then India-entry relevance, then completeness.

### Tier 1 — corridor-conviction sub-segments (fill first)

| Segment | Sub-segments | Geographies | Why first |
|---|---|---|---|
| skincare | serums_ampoules, sheet_masks, toners_essences, facial_moisturisers, facial_cleansers | KR + IN | Core K-beauty basket; corridor's main trade flow; IN serums already has one size point to build on |
| sun_care | sun_protection | IN first, then KR | Corridor whitespace #2 ("dedicated sunscreens — India underpenetrated"); zero size/growth data either side |
| mens_grooming | mens_skincare | IN first | Corridor whitespace #4; India segment-level size exists (HIGH, Euromonitor) but no sub split |
| dermocosmetics | (no taxonomy subs — deepen segment level) | KR + IN | Corridor whitespace #5, highest conviction; KR has only a growth rate, IN only a LOW-confidence size |

### Tier 2 — India-entry relevance

| Segment | Sub-segments | Geographies | Why |
|---|---|---|---|
| hair_care | shampoo, conditioners_treatments, scalp_care | IN first | "Skinification" demand shift documented in india_findings.yaml; ~US$4bn segment with no sub split |
| colour_cosmetics | face_makeup, lip_colour | KR + IN | Hince/Etude corridor activity; IN mass-tier share exists but no sub sizes |
| skincare (rest) | eye_care, body_care, hand_care, lip_care_non_colour | KR + IN | Completes the flagship segment |

### Tier 3 — completeness

| Segment | Sub-segments | Notes |
|---|---|---|
| fragrances | premium, mass, niche_artisanal | IN premium is import-reliant (UAE) per findings; sub sizes unknown |
| emerging_adjacencies | all 6 (incl. ayurvedic_herbal, halal_certified — India-relevant) | Zero data; segment-level first, then subs |
| sun_care | self_tanning, after_sun | Likely small; low priority |
| mens_grooming | mens_toiletries, mens_cosmetics | |
| hair_care | hair_colorants, styling, salon_professional | |
| colour_cosmetics | eye_makeup, nail | |

### Also outstanding at segment level (from the standing gaps register)

KR: sun_care, deodorants, mens_grooming, baby_child, emerging_adjacencies
have no processed file at all. IN: deodorants, baby_child,
emerging_adjacencies likewise. Fill segment-level size/growth for these
before their subs.

## Beyond sizes: what the entry-analysis layer additionally needs

These feed commands/entry-analysis.md and are researchable from public
sources (MEDIUM confidence acceptable, tagged):

- **Channel splits** (`channel_share`): e-commerce vs q-commerce vs GT/MT
  per segment, IN; Olive Young vs online vs duty-free, KR.
- **Competitive sets per sub-segment**: which brands lead each sub-segment
  (extends config/companies.yaml; qualitative entries are fine — they land
  in config, not sources.csv).
- **Regulatory cost/time**: CDSCO COS-1→COS-2 typical fees + lead times;
  MFDS functional-cosmetic approval times (feeds the regulatory barrier map).
- **Trade margins** (`trade_margin`): distributor + retailer markup ranges
  per channel, IN (only generic 25-45% MRP spread is on file).
- **Per-capita / penetration** (`penetration_rate`): category penetration IN
  vs KR per segment, for the demand-driver analysis.

## Execution protocol for the research skill

Work one Tier-1 row at a time; for each: (a) attempt paid-database export →
drop file in data/manual/ → `/ingest`; (b) else secondary-web research →
curated ingest with source URLs actually fetched and verified; (c) if neither
yields a defensible number, leave the gap standing — a standing gap is
information; a fabricated number is contamination. After each batch:
`python -m lib.fetchers.refresh` is NOT needed (no new fetchers), but
`python -m lib.web_export` + commit + push IS, so the live dashboard tracks
the research in near-real-time.
