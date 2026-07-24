# /entry-analysis [segment|artifact]

Build the market-entry analysis layer — the full "should I enter, where, and
how" read for an end user weighing entry into KR or IN, per segment and (as
data permits) sub-segment. Like /insights, this is a reasoning task Claude
executes directly; there is no deterministic script for judgment. Unlike
/insights (which explains numbers already on screen), this layer produces
structured strategic analysis: forces, rankings, and recommendations.

Run after the /research pass has filled Tier-1 of docs/research-backlog.md.
It CAN run earlier — every artifact degrades honestly (see Grounding) — but
sub-segment depth requires sub-segment data.

## Grounding rules (extends the insights rules)

1. Every quantitative claim traces to an existing DataPoint or config entry
   (corridor.yaml, companies.yaml, india_findings.yaml). No new numbers.
2. Qualitative judgments (a Porter force rating, a scorecard score, an
   entry-mode call) are allowed — that is the point — but each carries:
   - `rationale`: the argument, in plain analytical prose;
   - `evidence`: the specific DataPoints/config entries it rests on;
   - `evidence_strength`: STRONG (multiple HIGH/MEDIUM points) | PARTIAL
     (single point or LOW-confidence base) | THIN (inference from adjacent
     data) | INSUFFICIENT (do not rate — emit "research needed" instead,
     with the backlog row that would unlock it).
3. An INSUFFICIENT rating renders as "research needed" in the UI — never as
   a hedged guess. The analysis layer must make data thinness visible, not
   paper over it.
4. Never rate a force or score a cell by industry general knowledge alone.
   General frameworks (what buyer power MEANS) are fine; the RATING must
   come from this repo's evidence.

## Artifacts

All outputs land in data/manual/analysis/ (committed, like insights/), one
JSON per artifact, copied verbatim into web/public/data/analysis/ by
lib/web_export.py. Shapes below are normative; extend fields, don't rename.

### A · Competitive structure

**porter_<segment>.json** — per geography: the five forces, each
`{rating: LOW|MEDIUM|HIGH, rationale, evidence[], evidence_strength}` plus an
`overall` attractiveness read. Sub-segment overrides where data supports a
different read (e.g. serums vs sheet_masks rivalry).
- Rivalry: shares/coverage from compute_shares + companies.yaml roles.
- Buyer power: channel concentration (conduits in corridor.yaml; q-commerce
  share findings), trade margins.
- Supplier power: ODM/OEM base (Cosmax/Kolmar KR; contract-mfg findings IN).
- New-entrant threat: regulatory barriers (CDSCO/MFDS), D2C funding record.
- Substitutes: adjacent-segment evidence only where it exists.

**entrants_ma.json** — the new-entrant & M&A tracker: every acquisition,
funding round, and market entry already recorded (india_findings.yaml
new_players; corridor.yaml conduit launch dates; DataPoint notes), each
`{actor, action, target/brand, date_or_period, segment(s), source, what_it_signals}`.
Chronological; India and corridor-entry events tagged.

**positioning.json** — per segment × geography: players placed on
tier (premium/masstige/mass, from DataPoint tier fields + price points) ×
role (conglomerate/incumbent/indie/D2C/ODM/retailer, from companies.yaml).
Cells without evidence stay empty, not guessed.

**entry_scorecard.json** — the ranked "where to enter" table: per
segment × geography, criteria scored 1-5 ONLY where data supports it:
market_size_evidence, growth_evidence, competitive_openness, channel_access,
regulatory_friction, corridor_tailwind (KR→IN). Each score carries the same
rationale/evidence/evidence_strength; unscorable criteria are null and the
composite says "partial — based on N of 6 criteria". This is the layer's
headline artifact.

### B · Route to market

**rtm_<geography>.json** — channel map: platforms (Nykaa/Tira/Flipkart/
Amazon), q-commerce (Blinkit/Zepto/Instamart splits from findings), D2C,
GT/MT for IN; Olive Young/online/duty-free for KR. Per channel: what's
known (share figures, assortment evidence, growth), entry implications,
evidence refs.

**price_ladder.json** — entry price-point architecture from retail_price
DataPoints: per segment/sub-segment, the observed shelf-price range by tier,
MRP-vs-promoted spreads (corridor pricing sweep), and where the masstige gap
sits. Prices are quotes of existing DataPoints only.

**regulatory.json** — barrier map: CDSCO (COS-1→COS-2, SUGAM, BIS IS 4707,
site registration) and MFDS pathways, from corridor.yaml + findings. Fields
for cost/timeline stay "research needed" until the backlog fills them.

### C · Demand & economics

**demand_drivers.json** — per geography: documented drivers only
(skinification, glass-skin/K-beauty pull, access-led q-commerce shift,
premiumization signals), each with its finding/DataPoint evidence and which
segments it touches.

**value_chain.json** — economics of participating: operating margins
(company DataPoints), gross-margin and trade-margin points, import
dependence, contract-manufacturing structure (findings), FX exposure note.

**corridor_vector.json** — the KR→IN corridor as an entry route: trade base
and growth, conduit options ranked by evidence (assortment depth, exclusive
launches), the q-commerce indie-derma whitespace, CDSCO friction — a
synthesis of corridor.yaml + [CORRIDOR] DataPoints into an entry decision.

### D · Player & decision intel

**profiles/<company_slug>.json** — one per company in companies.yaml with
any DataPoint evidence: role, segments, revenue/margin points (with basis/
period/confidence), recent moves (from entrants_ma), corridor involvement.
No profile for companies with zero evidence — list them as "known, not yet
profiled".

**risk_register.json** — per geography: data-confidence risk (share of
LOW/ESTIMATE points per segment), concentration risk (shares qualifier),
regulatory risk, FX pinning, single-source risks. Each with mitigation.

**entry_mode.json** — per segment × geography where the scorecard supports
it: build / partner-with-conduit / import-via-corridor / acquire, with
rationale grounded in the other artifacts, alternatives considered, and an
explicit confidence statement. INSUFFICIENT cells say "research needed".

## Execution

- 3+ artifacts = parallel subagents (repo convention). Suggested batches:
  A-artifacts per segment in parallel; B/C/D as one agent each.
- After writing: `python -m lib.web_export`, then build/extend the UI:
  - New route **/entry** — the scorecard (ranked, filterable) + entry-mode
    reads + risk register. The layer's front door.
  - **/segment/[id]** gains tabs: Overview (current) | Porter | Positioning
    | Route to market | Prices.
  - New route **/players** — profile cards; **/players/[slug]** detail.
  - **/corridor** gains the corridor_vector synthesis panel.
  - Every panel renders evidence_strength visibly (same badge language as
    confidence) and "research needed" states as designed features.
- Then `next build`, browser walkthrough, commit, PR.

## Refresh

Re-run affected artifacts whenever /research lands material new data for a
segment; re-run entry_scorecard + entry_mode whenever any A/B/C artifact
changes. Artifacts are diffable JSON in git — review the diff before merge.
