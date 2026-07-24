# bpc-intel

Beauty & Personal Care market intelligence system: South Korea × India.
The repo is the deliverable, not the chat. Write to files.

## Scope lock
This system covers Beauty & Personal Care ONLY, across South Korea and India ONLY.
The taxonomy is defined in config/taxonomy.yaml. Do not add segments or geographies
without updating taxonomy.yaml first.

## Corridor focus (added 2026-07-21)
The Korea → India K-beauty corridor is a first-class research axis, not a footnote.
Registry: config/corridor.yaml (conduits, brands carried, whitespace, monitoring
queries). Conventions:
- Any DataPoint about K-beauty inside India carries "[CORRIDOR]" in notes.
- KR export flows to India stay geography=KR, value_basis=EXPORT_FOB, destination
  in notes.
- Every fetcher that supports queries includes the corridor query set from
  corridor.yaml, not just the per-geography defaults.

## Analyst insights (added 2026-07-24)
`/insights` produces the dashboard's "Analyst read" panels — commentary
synthesizing existing DataPoints (what a figure says, its trend, its
caveats), never a new source of numbers. Written by Claude directly (there is
no deterministic script for interpretation), stored in data/manual/insights/,
and copied verbatim by lib/web_export.py into web/public/data/insights/. Bound
by the same non-fabrication rules below, plus: never derive an implied stat
by combining two DataPoints, always name confidence/value_basis when leaning
on a figure, and never net figures across value_basis for the KR-vs-IN
"combined" read (value_usd_bn only, and only when both sides have it).

## Entry-analysis layer & research backlog (added 2026-07-24)
docs/research-backlog.md is the prioritized worklist for the next research
pass (sub-segment coverage is 5/34; the backlog explains why and what fills
it). /research is the protocol for executing it; /entry-analysis is the
market-entry analysis layer (Porter, entrants/M&A, positioning, entry
scorecard, RTM, price ladder, regulatory, demand, value-chain, corridor
vector, profiles, risk, entry-mode) that runs once Tier-1 data lands.
Analysis artifacts live in data/manual/analysis/ and are copied verbatim
into the web bundle. Judgment calls are allowed there but every rating
carries rationale + evidence refs + evidence_strength, and INSUFFICIENT
renders as "research needed" — never a hedged guess.

## Non-negotiable evidence rules

1. NEVER state a market size, share, growth rate, price, or revenue from your own
   knowledge. Every number comes from: (a) a fetcher script in lib/fetchers/,
   (b) a manual data drop in data/manual/, (c) the baseline report in
   data/baseline/ with its original source citation preserved, or (d) is labelled
   [ESTIMATE] with methodology, assumptions, and sensitivity range shown.

2. Every quantitative claim gets a row in data/sources.csv:
   claim | value | unit | currency | geography | segment | period | period_type |
   value_basis | source_name | url | date_accessed | confidence | notes

3. VALUE BASIS is mandatory on every number:
   - RETAIL = consumer sell-through (MRP-inclusive for India)
   - NET_REALISATION = company revenue (ex-trade margins, for India)
   - WHOLESALE = trade/distributor price
   - EXPORT_FOB = customs/FOB value (Korea exports)
   - PRODUCTION = factory-gate output value
   Never compare numbers on different bases without normalising first.

4. CURRENCY: always record original currency (KRW / INR / USD) AND a USD
   equivalent. Pin the exchange rate used in config/exchange_rates.yaml.
   Never use a bare number without currency.

5. If a script in lib/ can fetch it, RUN THE SCRIPT. Do not reason to the answer.

6. Never cite a URL you have not actually fetched and verified.

7. Market sizes must be reconciled TOP-DOWN and BOTTOM-UP where data permits.
   Gap >20% = do not publish; find the definitional mismatch and document it.

## India-specific rules (non-optional)

8. ORGANISED vs UNORGANISED: state which every India number covers.
9. FISCAL YEARS: always write FY24 (Apr-23 to Mar-24), never "2024" for Indian
   company data. Korean data uses calendar year — write CY2024 or 2024.
10. MRP vs NET REALISATION: MRP includes 25-45% trade margin. The normalisation
    function is lib/transforms/mrp_normalise.py. Use it before any reconciliation.

## Korea-specific rules (non-optional)

11. RETAIL vs EXPORT vs PRODUCTION: Korea's domestic retail (~US$13bn),
    export FOB (~US$11.4bn), and production value (KRW 17.9tn) are THREE
    DIFFERENT measures. Never conflate them. Tag each with value_basis.
12. DUTY-FREE is a distinct channel with its own dynamics (Chinese daigou decline).
    Do not include duty-free in "domestic retail" without flagging it.

## Confidence levels
- HIGH: primary source (company filing, government database, Euromonitor Passport)
- MEDIUM: credible secondary (Korea Herald, Business Standard, Statista, McKinsey)
- LOW: aggregator/estimate (Mordor Intelligence, Grand View, IMARC)
- ESTIMATE: model-derived with methodology shown

## Working style
- Write to files. Chat is for decisions only.
- Every fetcher returns timestamped JSON to data/raw/.
- Transforms write to data/processed/.
- Reports read ONLY from data/processed/ and data/baseline/.
- 3+ entities to profile = parallel subagents.
- Charts via lib/reports/charts.py only (matplotlib, saved to reports/latest/charts/).

## Vocabulary
Use precise industry terms. No "brand love", "engagement", "synergy".
Ehrenberg-Bass terms where relevant: Category Entry Points (CEPs), mental
availability, physical availability, Distinctive Brand Assets.
