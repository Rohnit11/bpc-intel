# bpc-intel

**Beauty & Personal Care market intelligence: South Korea × India.**

A CLI-driven, file-based research system. It maintains a structured, fully
sourced knowledge base across 12 BPC sub-segments × 2 geographies, pulls from
free public sources, accepts manual drops from subscription databases, and
generates consulting-grade Markdown reports on command. The repo is the
deliverable — every number traces to a source.

The governing rules live in [CLAUDE.md](CLAUDE.md); the full build plan in
[BUILD-SPEC.md](BUILD-SPEC.md).

---

## Quickstart

```bash
pip install -r requirements.txt          # Python 3.11+

python -m lib.reports.snapshot full      # build the KR×IN snapshot + charts
python -m lib.reports.verify             # confirm every number traces to the ledger
```

Reports land in [`reports/latest/`](reports/latest/). Open the `.md` files in
any Markdown previewer (VS Code renders the tables and inline charts cleanly).

---

## Commands

Each is a thin wrapper over a Python entry point; the docs are in
[`commands/`](commands/).

| Command | What it does | Entry point |
|---|---|---|
| `/report` | Full KR×IN snapshot + charts | `python -m lib.reports.snapshot full` |
| `/corridor` | K-beauty Korea→India corridor brief | `python -m lib.reports.snapshot corridor` |
| `/india` | India value-chain brief (pricing, imports, margins, demand) | `python -m lib.reports.snapshot india` |
| `/compare` | KR vs IN comparison for a metric | `python -m lib.reports.snapshot comparison market_size` |
| `/segment` | One-page brief for a geography × segment | `python -m lib.reports.snapshot segment KR skincare` |
| `/gaps` | Missing segment×geography×metric register | `python -m lib.analysis.gaps` |
| `/ingest` | Process a subscription CSV drop | `python -m lib.ingest.ingest <file>` |
| `/refresh` | Re-fetch every free live source, then rebuild | `python -m lib.fetchers.refresh` |
| `/verify` | Cross-check every number against the ledger | `python -m lib.reports.verify` |

---

## How it works

```
free sources ─▶ lib/fetchers/ ─▶ data/raw/*.json      (timestamped, gitignored)
                     │
                     ▼
              lib/transforms/  (currency · MRP · fiscal year · value basis)
                     │
                     ▼
              data/processed/*.json   +   data/sources.csv   (committed)
                     │                          ▲
                     ▼                          │ every number, with source
              lib/analysis/  (sizing · growth · share · gaps)
                     │
                     ▼
              lib/reports/  (Jinja2 templates + matplotlib) ─▶ reports/latest/
```

**Sources.** Fetchers in [`lib/fetchers/`](lib/fetchers/) pull from Tavily
(news), UN Comtrade (bilateral trade), Screener.in (Indian listed financials),
Google Trends, OpenAlex (research signals), a curated India value-chain research
set, and — once its free key is set — Korea DART (company filings). Subscription
data (Euromonitor Passport, Capital IQ, Statista) enters by dropping a CSV into
`data/manual/` and running `/ingest`.

**Storage.** No database. Everything is flat files: YAML config, JSON data, a
CSV ledger, Markdown reports. Portable, inspectable, git-diffable.
`data/processed/` and `data/sources.csv` are committed; `data/raw/` is
regenerable and gitignored.

**Refresh is manual, not scheduled.** Nothing polls in the background. A refresh
means *running* `/refresh` (or an individual fetcher), which re-pulls from the
web at that moment and idempotently upserts into `data/processed/` +
`data/sources.csv`. Reruns never duplicate rows.

**Analysis.** [`lib/analysis/`](lib/analysis/) computes CAGR/YoY growth,
market share (with explicit coverage qualifiers), and top-down vs bottom-up
sizing reconciliation with a >20% publish gate (CLAUDE.md rule 7). The gaps
scanner walks the taxonomy and reports every missing data point.

---

## The evidence model

Every quantitative claim is a row in [`data/sources.csv`](data/sources.csv):
`claim, value, unit, currency, geography, segment, period, period_type,
value_basis, source_name, url, date_accessed, confidence, notes`.

- **Value basis** is mandatory and never mixed without normalising: `RETAIL`,
  `NET_REALISATION`, `WHOLESALE`, `EXPORT_FOB`, `PRODUCTION`. Korea's domestic
  retail, export FOB, and production value are three different measures.
- **India** figures state organised vs unorganised, use fiscal years (FY24 =
  Apr-2023→Mar-2024), and normalise MRP↔net-realisation (25–45% trade margin)
  before any reconciliation.
- **Confidence**: `HIGH` (primary/filing/Passport), `MEDIUM` (credible
  secondary), `LOW` (aggregator/estimate), `ESTIMATE` (model-derived, methodology
  shown).

`/verify` enforces the core invariant automatically: every number in
`data/processed/` must have a matching ledger row, or the run fails.

---

## Configuration

| File | Purpose |
|---|---|
| `config/taxonomy.yaml` | The 12-segment × 2-geography canonical tree (scope lock) |
| `config/corridor.yaml` | K-beauty Korea→India registry (conduits, brands, whitespace, queries) |
| `config/sources.yaml` | Every source, its access method and cadence |
| `config/companies.yaml` | Named players per segment × geography |
| `config/exchange_rates.yaml` | Pinned FX rates with dates |
| `config/api_keys.yaml` | API keys (gitignored; copy from `.template`) |
| `config/access_status.yaml` | HEC subscription-database access status |
| `config/qcommerce_enabled.yaml` | ToS opt-in for the Blinkit/Zepto tracker |

---

## Testing

```bash
python -m pytest tests/ -q
```

Covers schemas, transforms (currency/MRP/fiscal year), fetcher smoke tests,
ingest, analysis math, report rendering, and the end-to-end reconciliation +
evidence-integrity checks in `tests/test_reconciliation.py`.
