# /ingest <filepath>

Process a manually-dropped subscription data file into the system.

## Usage

```
/ingest data/manual/capitaliq_hul_financials.csv
/ingest data/manual/passport_korea_marketsize.csv
```

Or from a terminal:
```
python -m lib.ingest.ingest data/manual/<file>.csv [handler]
```

Batch mode — drop several exports in `data/manual/` and process them all at
once (handler auto-detected per file; bad files are skipped, not fatal):
```
python -m lib.ingest.ingest --folder
```

## Handler selection

Handler is chosen by filename prefix; force it with a second argument or the
`handler=` kwarg:

| Prefix | Handler | Source |
|---|---|---|
| `capitaliq_*`, `capiq_*` | capitaliq | S&P Capital IQ Pro financials |
| `passport_*`, `*euromonitor*` | passport | Euromonitor Passport |
| `statista_*` | statista | Statista chart exports |
| anything else | generic | BMI Research, IBEF, freeform (needs a mapping) |

## Expected CSV shapes

**Capital IQ** — metric rows × year columns:
```
Company,Geography,Metric,Currency,Unit,FY2022,FY2023,FY2024
Hindustan Unilever,India,Total Revenue,INR,cr,58154,61896,63000
```
Export path: company → Financials → Income Statement → Export → CSV (annual).

**Passport** — category rows × year columns, plus a Unit column (or pass
`unit_hint="USD mn"`) and a Geography column (or pass `geography="KR"`):
```
Category,Geography,Unit,2022,2023,2024
Skin Care,South Korea,USD mn,6100,6250,6400
```

**Statista** — two columns; you supply the metadata:
```python
from lib.ingest.ingest import ingest
ingest("data/manual/statista_india_bpc.csv",
       handler="statista", geography="IN", segment="total_bpc",
       metric="market_size", unit="usd_bn")
```

## What happens

1. Detect file type → select handler.
2. Parse to DataPoints (validated against schema.py + taxonomy.yaml).
3. Merge into `data/processed/` — a matching claim from a lower-confidence
   source is replaced; same/higher confidence coexists (idempotent, no dupes).
4. Append new rows to `data/sources.csv`.
5. Re-run gaps analysis → refresh `reports/latest/gaps_register.md`.
6. Report: "Ingested N points from {file}. M new, K updated. Gaps now G."

## Notes

- Capital IQ and Passport data land as `confidence: HIGH` (primary sources).
- India Passport values are flagged MRP-inclusive; normalise with
  `lib/transforms/mrp_normalise.py` before reconciling against net revenue.
- Nothing is entered by hand — every number comes from the exported file.
