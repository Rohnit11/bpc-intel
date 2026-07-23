# /refresh

Re-fetch every free live source in one pass, then regenerate reports.

Runs `lib/fetchers/refresh.py`, which calls each fetcher's `run()` in isolation
— one failure, missing key, or disabled flag never aborts the others. Raw pulls
land in `data/raw/` (timestamped); new DataPoints are upserted into
`data/processed/` and appended to `data/sources.csv` (idempotent — reruns do not
duplicate).

Fetchers and what they need:
- `news_tavily` — Tavily REST (key in config/api_keys.yaml) — **runs**
- `trade_comtrade` (+ India imports) — keyless UN Comtrade preview — **runs**
- `india_screener` — Screener.in scrape — **runs**
- `trends_google` — pytrends (unofficial; may skip if blocked) — **runs**
- `academic_openalex` — OpenAlex — **runs**
- `india_research` — curated India value-chain research — **runs**
- `korea_dart` — **skipped** until `dart:` is set in config/api_keys.yaml (free key, opendart.fss.or.kr)
- `qcommerce_tracker` — **skipped** until `enabled: true` in config/qcommerce_enabled.yaml (ToS opt-in)

## Steps
1. `python -m lib.fetchers.refresh` — runs all fetchers, prints an OK/skipped/error table.
2. `python -m lib.reports.snapshot full` — regenerate the snapshot + charts.
3. `python -m lib.reports.snapshot corridor` and `... india` — regenerate the briefs.
4. `python -m lib.reports.verify` — confirm every number still traces to the ledger.

Run all: `python -m lib.fetchers.refresh && python -m lib.reports.snapshot full && python -m lib.reports.verify`
