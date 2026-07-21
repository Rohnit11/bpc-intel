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
