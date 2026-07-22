"""Curated facts extracted from Tavily news sweeps.

Tavily returns news leads, not structured statistics — turning a headline into
a DataPoint is a judgment call, so it is done here by hand with each claim
carrying its exact source URL (the durable provenance, since data/raw/ is
gitignored). This mirrors lib/ingest/baseline_parser.py's discipline.

Each entry records where it came from and why it earned its confidence level
per CLAUDE.md: Euromonitor/government = HIGH; named trade press / consulting
via a credible outlet = MEDIUM; market-research aggregators (IMARC, TechSci,
P&S, EMR, Mordor, Credence) = LOW. Corridor facts (K-beauty inside India)
carry [CORRIDOR] in notes.

Run:  python -m lib.ingest.news_curated
"""
from __future__ import annotations

import logging
from datetime import date

from lib.transforms.merge import upsert_data_points
from lib.transforms.schema import DataPoint

logger = logging.getLogger("bpc_intel.ingest.news_curated")

# Sweep date these were curated from (data/raw/tavily_20260722T213101Z.json).
ACCESSED = date(2026, 7, 22)

FACTS: list[dict] = [
    # --- Korea skincare domestic RETAIL (fills a gap: we had exports only) ---
    dict(geography="KR", segment="skincare", metric="market_size", value=7.653,
         unit="krw_tn", currency="KRW", period="2025", period_type="CY",
         value_basis="RETAIL", confidence="HIGH",
         source_name="Euromonitor International (via marketresearch.com)",
         source_url="https://www.marketresearch.com/seek/Skin-Care-South-Korea/1554/1229/1.html",
         notes="Domestic retail value; +1% YoY; population 51.7m cited"),
    dict(geography="KR", segment="skincare", metric="growth_yoy", value=1.0,
         unit="percent", currency="KRW", period="2025", period_type="CY",
         value_basis="RETAIL", confidence="HIGH",
         source_name="Euromonitor International (via marketresearch.com)",
         source_url="https://www.marketresearch.com/seek/Skin-Care-South-Korea/1554/1229/1.html",
         notes="Korea skincare domestic retail growth"),

    # --- K-beauty in India: the headline CORRIDOR sizing ---
    dict(geography="IN", segment="total_bpc", metric="market_size", value=0.4,
         unit="usd_bn", currency="USD", period="2024", period_type="CY",
         value_basis="RETAIL", confidence="MEDIUM",
         source_name="Economic Times Retail (consulting estimate)",
         source_url="https://retail.economictimes.indiatimes.com/news/health-and-beauty/indias-k-beauty-market-forecast-15-billion-by-2030/123190386",
         notes="[CORRIDOR] Korean-beauty market IN India; fastest-growing BPC segment"),
    dict(geography="IN", segment="total_bpc", metric="market_size", value=1.5,
         unit="usd_bn", currency="USD", period="2030", period_type="CY",
         value_basis="RETAIL", confidence="MEDIUM",
         source_name="Economic Times Retail (consulting estimate)",
         source_url="https://retail.economictimes.indiatimes.com/news/health-and-beauty/indias-k-beauty-market-forecast-15-billion-by-2030/123190386",
         notes="[CORRIDOR] K-beauty in India, 2030 forecast"),
    dict(geography="IN", segment="total_bpc", metric="cagr_forecast", value=25.9,
         unit="percent", currency="USD", period="2024-2030", period_type="range",
         value_basis="RETAIL", confidence="MEDIUM",
         source_name="Economic Times Retail (consulting estimate)",
         source_url="https://retail.economictimes.indiatimes.com/news/health-and-beauty/indias-k-beauty-market-forecast-15-billion-by-2030/123190386",
         notes="[CORRIDOR] K-beauty in India forecast CAGR 2024-2030"),
    dict(geography="IN", segment="total_bpc", metric="market_size", value=3139.31,
         unit="inr_cr", currency="INR", period="2025", period_type="CY",
         value_basis="RETAIL", confidence="LOW",
         source_name="Expert Market Research",
         source_url="https://www.expertmarketresearch.com/reports/india-k-beauty-products-market",
         notes="[CORRIDOR] Alt K-beauty India estimate (~US$0.33bn); CAGR ~26.3% 2026-2035"),

    # --- India sun care (fills an empty segment) ---
    dict(geography="IN", segment="sun_care", metric="market_size", value=0.89312,
         unit="usd_bn", currency="USD", period="2024", period_type="CY",
         value_basis="RETAIL", confidence="LOW",
         source_name="TechSci Research",
         source_url="https://www.techsciresearch.com/report/india-sunscreen-market/26904.html",
         notes="India sunscreen market; among fastest q-commerce risers"),
    dict(geography="IN", segment="sun_care", metric="cagr_forecast", value=6.8,
         unit="percent", currency="USD", period="2024-2030", period_type="range",
         value_basis="RETAIL", confidence="LOW",
         source_name="TechSci Research",
         source_url="https://www.techsciresearch.com/report/india-sunscreen-market/26904.html",
         notes="India sunscreen forecast CAGR to 2030"),

    # --- India dermocosmetics (fills an empty segment) ---
    dict(geography="IN", segment="dermocosmetics", metric="market_size", value=0.2803,
         unit="usd_bn", currency="USD", period="2024", period_type="CY",
         value_basis="RETAIL", confidence="LOW",
         source_name="P&S Market Research",
         source_url="https://www.psmarketresearch.com/market-analysis/india-skincare-dermacosmetics-market",
         notes="India skincare dermacosmetics; 2030 forecast US$0.505bn"),

    # --- India men's grooming (corroborates baseline ~US$2.3bn 2024) ---
    dict(geography="IN", segment="mens_grooming", metric="market_size", value=2.45,
         unit="usd_bn", currency="USD", period="2025", period_type="CY",
         value_basis="RETAIL", confidence="LOW",
         source_name="IMARC Group",
         source_url="https://www.imarcgroup.com/india-male-grooming-products-market",
         notes="India male grooming; corroborates baseline US$2.3bn (2024); CAGR 6.66%"),
    dict(geography="IN", segment="mens_grooming", metric="cagr_forecast", value=12.2,
         unit="percent", currency="USD", period="2025-2035", period_type="range",
         value_basis="RETAIL", confidence="LOW",
         source_name="Future Market Insights",
         source_url="https://www.futuremarketinsights.com/reports/mens-skincare-products-market",
         notes="India MEN'S SKINCARE (sub-slice) CAGR; faster than overall grooming"),

    # --- India q-commerce (corroborates baseline; channel context) ---
    dict(geography="IN", segment="total_bpc", metric="market_size", value=3.9,
         unit="usd_bn", currency="USD", period="2023", period_type="CY",
         value_basis="RETAIL", confidence="LOW",
         source_name="BlueWeave Consulting",
         source_url="https://www.blueweaveconsulting.com/report/india-quick-commerce-market",
         notes="India q-commerce ALL categories (not BPC-only); CAGR ~39.9% to 2030; value_basis_uncertain"),
]


def parse() -> list[DataPoint]:
    """Build DataPoints from the curated facts table.

    Returns:
        Validated DataPoints.
    """
    points = [DataPoint(**dict(f, date_accessed=ACCESSED)) for f in FACTS]
    logger.info("Built %d curated DataPoints from Tavily sweep", len(points))
    return points


def run() -> dict:
    """Merge curated facts into processed data + sources.csv.

    Returns:
        Per-file merge summary.
    """
    points = parse()
    summary = upsert_data_points(points)
    corridor = sum(1 for p in points if p.notes and "[CORRIDOR]" in p.notes)
    logger.info("Merged %d curated facts (%d corridor-tagged)", len(points), corridor)
    return {"points": len(points), "corridor": corridor, "merge": summary}


if __name__ == "__main__":
    import json

    print(json.dumps(run(), indent=2))
