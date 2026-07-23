# /india

Generate the India value-chain brief: pricing, cost-of-making, import-vs-make,
supply chain, competitive dynamics, and consumer demand across skincare/sun/
derma, fragrances, men's grooming, hair care, and the K-beauty corridor.

Draws on: UN Comtrade India imports (import-dependence), Screener operating
margins (cost structure), curated Tavily research (config/india_findings.yaml
+ lib/ingest/india_curated.py). Every figure shows basis/period/confidence.

Run: `python -m lib.reports.snapshot india`
