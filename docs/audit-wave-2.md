# Wave-2 integrity audit

## Verdict

**Safe to publish as-is.** Wave 2's own file (`kr_segments_b.json`, 23 claims, the
one whose agent was killed by a session limit) is structurally complete — no
missing fields, no placeholder text, no thin notes — and its 13 mechanical
findings are all one shallow, low-materiality pattern (see below). Five of six
wave-2 files raised nothing. The corpus does carry real integrity debt, but it
is overwhelmingly pre-existing (wave-1/baseline), and separately, this audit
surfaced several defects the mechanical scanner cannot see at all because of a
tooling gap (detailed in Must-fix #1). None of that should block wave 2's
publish; it should be tracked and fixed on its own timeline.

## Must fix before publish

These are ranked by dashboard/correctness risk, not by which wave introduced
them — most predate wave 2, and each note says so.

1. **Audit-tool coverage gap (process, cross-cutting).** `research_kit audit`
   only scans `data/manual/research_drops/*.json`. A direct sweep of
   `data/processed/*.json` (the store that actually feeds the dashboard) finds
   **57** India `market_size`/`market_share` claims with no organised/unorganised
   keyword at all — nearly double the ~30 the scanner attributes to India
   coverage. The ~27-claim gap is concentrated in terse, uncaveated entries
   (e.g. `IN_total_bpc.json[2]` IMARC 31.19usd_bn, notes empty; `IN_colour_cosmetics.json[0]`
   DMI 3.46usd_bn, notes "Forecast CAGR 7.08%" only) whose style matches
   baseline-report-era content, not wave-1/2 drop-file content — i.e. claims
   that reached `data/processed/` by a path the scanner never looks at. Rule 8
   is non-negotiable and non-optional; recommend extending the scanner to walk
   `data/processed/` directly (or `data/baseline/` + fetcher output) so it
   actually covers every claim, not just drop-file claims. *(Pre-existing;
   does not block wave 2, but wave 2's own scanner-clean result is partly an
   artifact of this gap and shouldn't be over-trusted for future waves.)*

2. **`total_bpc` market_size bucket commingles whole-market totals with
   channel/tier/corridor-specific figures**, with no field distinguishing them —
   only prose in `notes`. Confirmed in three separate period-buckets:
   - `IN_total_bpc.json` 2025 (6 rows sharing the bucket): `[8]` is India's
     *entire q-commerce market, all categories* (BPC scope violation dressed as
     a BPC total), `[53]` is a K-beauty-in-India corridor estimate (~$0.33bn)
     mislabeled as a total-market row, `[104]` is online-channel-only GMV.
     Only `[0]` (Statista), `[2]` (IMARC), `[99]` (RedSeer) are genuine
     whole-market attempts.
   - `KR_total_bpc.json` 2024 (4 rows): only `[0]` (Euromonitor 13.0bn) is a
     genuine total; `[6]` is premium-tier only, `[37]` is live-commerce channel,
     `[47]` is e-commerce transaction value.
   - `KR_total_bpc.json` 2025 (4 rows): `[35]` is the duty-free channel *all
     categories* (not BPC-only), `[50]` is one retailer's (Olive Young) revenue
     used as an H&B-channel proxy.
   - Same pattern drives 9 of the mechanical scanner's `channel_shares.json`
     findings (drop file) — those rows are exactly this class of
     channel-scoped figure, not missing duty-free footnotes.
   Recommend: give channel/tier/corridor-scoped rows a distinguishing metric
   (e.g. `channel_share`, or a `market_size` variant carrying explicit
   `scope:` metadata) so a report can't read them as competing whole-market
   estimates. *(Pre-existing/baseline; cross-cutting, both geographies.)*

3. **`IN_bath_shower.json` IMARC internal contradiction.** `[0]` (IMARC "bath &
   shower products," the wider category) = USD 1.8bn (2025); `[2]` (IMARC "bath
   soap" alone, which `[0]`'s own notes say sits inside the wider category) =
   USD 3,406.3mn — 1.9x **larger** than the total it's supposedly part of, a
   mathematical impossibility. `MarkNtel` (`[4]`, USD 3.54bn, bath-soap-only)
   independently corroborates the soap sub-figure within ~4%, reinforcing that
   IMARC's "wider category" total is the broken number, not the soap figure.
   This is the same class of problem as the `niche_artisanal` 80% share
   withdrawn pre-merge (CLAUDE.md precedent: a figure that renders on the
   dashboard as an authoritative headline number needs to survive scrutiny, not
   just carry a flag). Recommend: withdraw or demote `[0]`/`[1]` (IMARC total +
   its CAGR) as the segment headline; the soap-only pair (`[2]`/`[4]`) is
   currently the better-supported anchor, though note that a true "bath &
   shower total" (soap + wash + additives) still doesn't exist cleanly on file.

4. **`value_basis` field says a real basis (mostly RETAIL) while notes hedge
   "value_basis_uncertain" or "basis not stated"** — 22 rows across both
   geographies (full list: `IN_hair_care.json[12]`, `IN_skincare.json[31]`,
   `IN_total_bpc.json[0,1,8,54]`, `KR_baby_child.json[0,2]`,
   `KR_deodorants.json[2]`, `KR_dermocosmetics.json[1,5,10]`,
   `KR_emerging_adjacencies.json[0]`, `KR_skincare.json[9,13,21]`,
   `KR_total_bpc.json[2,4,6,35,36,37]`). This defeats the point of a mandatory
   value_basis tag: anything that filters/rolls up by `value_basis=RETAIL`
   silently includes claims the claim-writer itself wasn't sure about.
   `value_basis: NA` is a legitimate schema value used correctly elsewhere in
   this exact situation (e.g. `KR_dermocosmetics.json[3,4]`); recommend either
   switching these 22 to `NA`, or keeping an assumed value only where notes say
   so explicitly (the more defensible pattern already used at
   `KR_dermocosmetics.json[5]`: "assumed domestic consumer sell-through (NOT
   export FOB, NOT MFDS production value)").

5. **`IN_skincare.json` market_share 2025 three-way collision, undocumented,
   deceptively close values**: `[0]` IMARC 35% (share of total BPC), `[1]` GVR
   49% (share of a narrower "cosmetics" basket), `[9]` IMA Pro 40% (mass-tier
   *brand* share within skincare, unrelated to the other two). None reference
   each other. Because 35/40/49 look like plausible agreement, the risk of
   silent averaging or miscitation here is higher than in the corpus's more
   obviously-conflicting pairs. Needs explicit "not comparable to" notes on all
   three.

6. **`IN_hair_care.json` scalp_care 2025, 5.3x gap, undocumented as a pair**:
   Deep Market Insights `[13]` (155.16usd_mn, hair serum) vs IMARC `[15]`
   (824.8usd_mn, hair growth products) — each cross-references a *different*
   third source (conditioners_treatments; RedSeer) instead of each other,
   despite sharing the identical bucket and exceeding the 20% reconciliation
   threshold several times over.

7. **`IN_colour_cosmetics.json` 2024, 60% gap, undocumented as a pair**: DMI
   `[0]` (3.46usd_bn, notes: "Forecast CAGR 7.08%" only) vs Market Research
   Future `[4]` (5.55usd_bn) — MRFF's note cross-references a third figure
   ("Markets and Data USD 4.80bn FY24") but never mentions DMI, and DMI
   references nothing. A real, sizeable, silent gap sitting in the same cell.

## Should fix

- **Two exact-duplicate claims found by spot-check** (recommend a full
  corpus-wide dedup sweep on geo/segment/sub/metric/value/period/source, since
  finding two unprompted suggests more exist): `IN_mens_grooming.json[3]` and
  `[9]` (both IMARC, USD 2.45bn 2025, identical CAGR); `IN_hair_care.json[2]`
  and `[6]` (both Mordor, USD 4.1bn 2026, identical). Merge each pair, folding
  the unique color from the row you drop into the row you keep.
- **One-sided cross-references worth backfilling** (values are close/agreeing
  or already individually caveated, so this is completeness, not correctness):
  `IN_mens_grooming.json[0]` (Euromonitor 186.3inr_bn, the group's "primary
  anchor" per `[7]`'s own note, carries zero caveat despite a ±10% disputed
  cluster — this one is the most worth doing first); `KR_dermocosmetics.json[3]`
  (should point forward to `[5]`'s "precision refresh"); `IN_oral_care.json[6]`
  (should point forward to `[8]`'s ~40% Renub rebase); the MFDS-vs-aggregator
  cluster (`KR_skincare.json[9]` MarkNtel serum, `KR_skincare.json[21]` Vyansa
  toner) should each explicitly name the ~30x MFDS production gap that
  currently lives only in `KR_skincare.json[13]`'s "SYSTEMIC CAVEAT" — each
  individually already says "treat with caution," just not why, in comparable
  terms; `IN_emerging_adjacencies.json[0]` (ayurvedic skincare-only) should
  name its own wider sibling `[2]` the way `[2]` already names it.
- **Renub India oral care ~40% rebase** (`IN_oral_care.json[6]`→`[8]`, USD
  2.03bn 2024 → USD 1.23bn 2025, no stated definitional change): recording
  both is sufficient — no mathematical impossibility here, just an unexplained
  publisher revision — but backfill the cross-reference (see above) and
  consider surfacing "same publisher revised ~40% without explanation" as a
  standing reliability caveat rather than leaving it implicit.
- **KR colour_cosmetics / sun_care duty-free scope note**: unlike most
  duty-free scanner findings (see triage below), these two categories are
  plausible duty-free/travel-retail lines; add an explicit scope sentence
  rather than relying on the blanket omission being safe.
- **Un-extracted corridor figures**: `IN_total_bpc.json[127]` (TheBK/Beauty
  Kyungjae, already fetched, source_url on file) reports two more numbers
  inside its `notes` that were never promoted to their own claims — India total
  BPC market USD 24bn (2024)→45bn (2030), and **K-beauty in India USD 400M
  (2024), +25.9%/yr, →USD 1.6bn by 2030**. The second is squarely a corridor
  data point per CLAUDE.md's "first-class research axis" framing and is
  currently invisible to anything reading `market_size`/`[CORRIDOR]` claims.
  Recommend extracting both as their own claims (with `[CORRIDOR]` on the
  K-beauty one) from the source already on file.
- **`value_basis: NA` vs. assumed-and-disclosed style inconsistency**: the
  corpus uses both approaches for the identical situation ("source doesn't
  state basis") — e.g. `KR_dermocosmetics.json[1,2,3]` use bare `NA`,
  `dermocosmetics.json[0]` (drop file) assumes RETAIL with a disclosed
  assumption. Both are individually defensible; recommend picking one
  convention (assumed + disclosed is more useful downstream than bare NA,
  since NA silently drops the row from any value_basis-filtered view).
- **`dermocosmetics.json[12]` (drop file) growth_yoy with a range-shaped
  period**: a YoY metric describing "Jul-Sep 2025" should carry
  `period_type=Q3`, `period=2025`, not the range label that tripped the
  scanner — small schema-hygiene fix.

## Accepted with reason

- **MFDS `value_basis` tagging (Step-2 item 2, full review, clean pass).**
  Every MFDS-sourced row found (`KR_bath_shower`, `KR_colour_cosmetics`,
  `KR_fragrances`, `KR_oral_care`, `KR_skincare`, `KR_sun_care`,
  `KR_total_bpc` — ~35 rows) correctly separates EXPORT_FOB / PRODUCTION /
  RETAIL and explicitly disclaims cross-basis reads ("not retail, not export,"
  "production growth ≠ retail demand growth," etc.). No conflation found. This
  is a genuine strength of the wave, worth stating plainly rather than only
  reporting problems.
- **The lotion/cream+essence/oil double-count trap (Step-2 item 3, confirmed
  intact).** `KR_skincare.json[11]`/`[12]` still carry the required "filed once
  here... must NOT be added to any serums_ampoules figure" note. Checked every
  `serums_ampoules` row in the corpus (KR and IN) — none numerically
  incorporates the MFDS combined figure. No double-count occurring today.
- **kr_segments_b.json's 13 duty-free findings** (deodorants, baby_child,
  dermocosmetics x3, hair_care growth, mens_grooming x2, beauty_devices,
  nutricosmetics x2) and **margins_penetration.json[19]** (KR per_capita_spend):
  Rule 4/12 requires flagging duty-free *if included*; nothing in any of these
  notes suggests inclusion, and none of these segments (nor a per-capita
  metric, whose denominator is domestic population, not tourists) are
  materially duty-free-exposed categories. Scanner rule is a blanket,
  segment-blind check; treated here as a prompt correctly triaged to "no
  action."
- **mens_grooming.json / colour_hair_subs.json(hair_care row) / dermocosmetics.json
  duty-free findings** (`mens_grooming.json[0,1,2,3]`, `colour_hair_subs.json[32]`,
  `dermocosmetics.json[0]`): same reasoning — grooming, hair care, and this
  particular dermocosmetics source are not plausible duty-free lines.
- **`sun_care.json[6]` (drop file) duty-free finding**: this claim is a US
  e-commerce export-demand indicator, not a domestic retail figure at all — the
  "domestic retail includes duty-free" rule doesn't apply to it regardless of
  its value_basis tag.
- **`dermocosmetics.json[1,2,3,6,8]` (drop file) value_basis=NA findings**:
  `NA` is a legitimate schema value (confirmed via `research_kit skeleton`)
  precisely for "source doesn't state a basis." Using it here is the honest
  choice, not a defect — see the Should-fix note above for the separate,
  smaller point about corpus-wide consistency of style.
- **`dermocosmetics.json[10,11]` (drop file) organised-coverage findings**:
  these are single-company revenue claims (Minimalist/Entrackr), not market
  estimates — organised-vs-unorganised is a market-structure concept that
  doesn't apply to one firm's reported revenue.
- **Corridor-tag borderline non-tags**: `IN_skincare.json[25]` (TechSci, all
  facial masks, mentions "K-beauty driven" only as color) and
  `IN_total_bpc.json[122]` (Kirana Club GT margin benchmark, mentions K-beauty
  only as a use-case) — the claims themselves measure something other than
  K-beauty, so withholding `[CORRIDOR]` is correct. (Contrast with
  `IN_total_bpc.json[127]` above, which does need action.)
- **54 of 70 mechanical-scanner findings are pre-existing wave-1/baseline
  debt** (all `colour_hair_subs.json`, `dermocosmetics.json`,
  `mens_grooming.json`, `channel_shares.json`, `sun_care.json`,
  `in_skincare_subs.json`, `margins_penetration.json` findings not already
  elevated above). Real, and triaged individually below — but not a wave-2
  regression, so it does not gate this wave's publish.

## Scanner findings triaged

`kr_segments_b.json` (wave 2, 13 findings, all the same pattern) —
**OK-because-not-material** for all 13: `[0,2]` deodorants, `[4,6]` baby_child,
`[8,9,13]` dermocosmetics, `[15]` hair_care growth_yoy, `[16,22]` mens_grooming,
`[17]` beauty_devices, `[19,20]` nutricosmetics. Rule 4 flags duty-free *if
included*; none of these notes suggest inclusion, and none of these segments
are duty-free-exposed. Full-file structural scan (all 23 claims, not just the
13 flagged) found zero missing fields, placeholder text, or thin notes —
no sign the session-limit kill left unfinished work.

`channel_shares.json` (wave 1, 9 findings) — **REAL**, all 9: `[1,2,3]`
organised-coverage gap on India online-BPC-GMV figures; `[15,16,18,19,20,21]`
are the `total_bpc` channel/scope-commingling problem (Must-fix #2), not
simple missing-footnote cases.

`colour_hair_subs.json` (wave 1, 18 findings) — **REAL** (organised-coverage
gap, confirmed no keyword present): `[2,4,5,6,7,9]` colour_cosmetics,
`[20,22]` hair_care, `[24,25,26]` hair_care shampoo/conditioners,
`[28,29,31]` hair_care/scalp_care. **REAL, low-moderate, recommend scope
note** (duty-free plausibly material for this category): `[11,13,15]`
colour_cosmetics. **OK-because-not-material**: `[32]` hair_care.

`dermocosmetics.json` (wave 1, 12 findings) — **OK-because (legitimate NA)**:
`[1,2,3,6,8]` value_basis findings. **REAL** (organised-coverage gap):
`[4,6,8]`. **OK-because (metric doesn't carry the concept)**: `[10,11]`
organised-coverage on company-revenue claims. **REAL** (schema hygiene):
`[12]` growth_yoy range-period. **OK-because-not-material**: `[0]` duty-free.

`mens_grooming.json` (wave 1, 11 findings) — **OK-because-not-material**:
`[0,1,2,3]` duty-free. **REAL** (organised-coverage gap): `[6,7,9,11,12,13,15]`.

`sun_care.json` (wave 1, 4 findings) — **REAL, low-moderate, recommend scope
note**: `[0,2]` duty-free. **OK-because (not a domestic-retail claim at all)**:
`[6]`. **REAL** (organised-coverage gap): `[11]`.

`in_skincare_subs.json` (wave 1, 2 findings) — **REAL** (organised-coverage
gap, confirmed): `[3,10]`.

`margins_penetration.json` (wave 1, 1 finding) — **OK-because** (per-capita
metric; duty-free spend isn't part of a domestic per-capita denominator):
`[19]`.

**Tally**: 42 of 70 findings triage to REAL (30 organised-coverage +
11 duty-free-recharacterized-as-channel-scope-issue + 1 schema hygiene);
28 to OK-because. 9 of the 42 REAL findings are wave-2 or cross-cutting and
appear in Must-fix above; the remaining 33 are pre-existing wave-1 debt,
individually real, collectively non-blocking for this wave.
