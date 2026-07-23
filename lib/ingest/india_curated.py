"""Curated India value-chain facts from the Tavily india_research sweep.

Hand-curated with each claim's source URL (data/raw/ is gitignored). Covers
pricing, cost-of-making, import-dependence, segment sizing, competitive
dynamics, and demand — the India value-chain research. Confidence per
CLAUDE.md: aggregators = LOW; named trade press/consulting = MEDIUM; derived
ratios = ESTIMATE with methodology.

Run:  python -m lib.ingest.india_curated
"""
from __future__ import annotations

import logging
from datetime import date

from lib.transforms.merge import upsert_data_points
from lib.transforms.schema import DataPoint

logger = logging.getLogger("bpc_intel.ingest.india_curated")

ACCESSED = date(2026, 7, 23)

FACTS: list[dict] = [
    # ---- Segment sizing (fill gaps: hair care, fragrances, serum sub) ----
    dict(segment="hair_care", metric="market_size", value=4.1, unit="usd_bn",
         period="2026", value_basis="RETAIL", confidence="LOW",
         source_name="Mordor Intelligence",
         source_url="https://www.mordorintelligence.com/industry-reports/india-hair-care-and-styling-products-market-industry",
         notes="India hair care; 'skinification' shift to actives/serums"),
    dict(segment="hair_care", metric="cagr_forecast", value=4.73, unit="percent",
         period="2026-2031", value_basis="NA", confidence="LOW",
         source_name="Mordor Intelligence",
         source_url="https://www.mordorintelligence.com/industry-reports/india-hair-care-and-styling-products-market-industry",
         notes="India hair care forecast CAGR"),
    dict(segment="fragrances", metric="market_size", value=2.6, unit="usd_bn",
         period="2024", value_basis="RETAIL", confidence="LOW",
         source_name="Industry (FMCG analysis via LinkedIn)",
         source_url="https://www.linkedin.com/posts/vishekpratap_fmcg-indianmarket-fragrance-activity-7359092677608419328-Pnhv",
         notes="India perfume+DEODORANT combined; CAGR ~11.1% to US$6.7bn by 2033; "
               "broader than perfume-only"),
    dict(segment="fragrances", metric="market_size", value=0.281, unit="usd_bn",
         period="FY24", value_basis="RETAIL", confidence="LOW",
         source_name="Markets and Data",
         source_url="https://www.marketsandata.com/industry-reports/india-perfume-market",
         notes="India PERFUME-ONLY (narrower); CAGR 15.23% to US$0.873bn FY2032"),
    dict(segment="skincare", metric="market_size", value=9.06, unit="usd_bn",
         period="2025", value_basis="RETAIL", confidence="LOW",
         source_name="IMARC Group",
         source_url="https://www.imarcgroup.com/india-skincare-market",
         notes="India skincare total; facial care leads; to US$18.38bn by 2034 (CAGR 7.49%)"),
    dict(segment="skincare", metric="market_size", value=0.140, unit="usd_bn",
         period="2026", value_basis="RETAIL", confidence="LOW", sub_segment="serums_ampoules",
         source_name="MarkNtel Advisors",
         source_url="https://www.marknteladvisors.com/research-library/india-facial-serum-market-study.html",
         notes="India facial SERUM sub-segment; to US$0.223bn by 2032"),
    dict(segment="sun_care", metric="market_size", value=0.5766, unit="usd_bn",
         period="2025", value_basis="RETAIL", confidence="LOW",
         source_name="IMARC Group",
         source_url="https://www.imarcgroup.com/india-sunscreen-market",
         notes="India sunscreen; cf TechSci US$0.893bn (2024) — definitional spread; CAGR 6.07%"),

    # ---- K-beauty corridor: alternative India sizing ----
    dict(segment="total_bpc", metric="market_size", value=0.335, unit="usd_bn",
         period="2026", value_basis="RETAIL", confidence="LOW",
         source_name="The Report Cubes",
         source_url="https://www.thereportcubes.com/report-store/k-beauty-products-market-india",
         notes="[CORRIDOR] K-beauty in India; CAGR 19.17% to US$1.36bn by 2034; "
               "cf Economic Times 25.9% CAGR"),

    # ---- Pricing & cost-of-making (the crux) ----
    dict(segment="skincare", metric="retail_price", value=600.0, unit="inr",
         currency="INR", period="2026", value_basis="MRP", confidence="LOW",
         sub_segment="serums_ampoules",
         source_name="The D2C Pulse",
         source_url="https://thed2cpulse.com/growth-strategy/gross-margins-for-d2c-brands-in-india",
         notes="30ml serum MRP typically Rs500-700 (midpoint 600); manufacturing "
               "cost Rs80-120/unit"),
    dict(segment="skincare", metric="gross_margin", value=80.0, unit="percent",
         currency="INR", period="2026", value_basis="NA", confidence="LOW",
         source_name="The D2C Pulse",
         source_url="https://thed2cpulse.com/growth-strategy/gross-margins-for-d2c-brands-in-india",
         notes="Serum gross markup 75-85% pre-deductions (COGS Rs80-120 vs MRP Rs500-700); "
               "true margin lower after packaging/shipping/returns"),
    dict(segment="skincare", metric="market_share", value=40.0, unit="percent",
         period="2025", value_basis="RETAIL", confidence="LOW", tier="mass",
         source_name="IMA Pro research",
         source_url="https://gaurav.imapro.in/research/india-skincare-market-report",
         notes="Mass tier (<Rs200) share; Pond's, Nivea, Himalaya, Lakme, Garnier"),

    # ---- Import dependence (derived: import vs make) ----
    dict(segment="skincare", metric="import_dependence", value=9.3, unit="percent",
         period="2024", value_basis="NA", confidence="ESTIMATE",
         source_name="Derived (UN Comtrade / IMARC)",
         methodology="India skincare imports US$844m (Comtrade HS3304, 2024) / India "
                     "skincare market US$9.06bn (IMARC 2025) = ~9%. Most volume made/filled "
                     "domestically; premium & K-beauty tiers imported.",
         notes="Import-vs-make: India skincare is ~91% domestically supplied by value"),
    dict(segment="fragrances", metric="import_dependence", value=12.8, unit="percent",
         period="2024", value_basis="NA", confidence="ESTIMATE",
         source_name="Derived (UN Comtrade / industry)",
         methodology="India fragrance imports US$332m (Comtrade HS3303, 2024) / perfume+deo "
                     "market US$2.6bn = ~13%. Premium perfume import-heavy (UAE largest source, "
                     "then France); mass perfume/deo domestically filled.",
         notes="Import-vs-make: premium fragrance import-reliant, mass domestic"),

    # ---- Competitive dynamics: key revenue / deal anchors ----
    dict(segment="fragrances", metric="revenue", value=1200.0, unit="inr_cr",
         currency="INR", period="FY25", value_basis="NET_REALISATION", confidence="MEDIUM",
         source_name="Economic Times (startups)",
         source_url="https://m.economictimes.com/tech/startups/investors-catch-a-big-whiff-of-money-in-d2c-fragrance-firms/articleshow/128079803.cms",
         notes="Company: Vini Cosmetics (Fogg) — FY25 operating revenue; KKR owns 54% "
               "(US$625m, 2021, US$1.2bn valuation)"),

    # ---- Consumer demand ----
    dict(segment="total_bpc", metric="growth_yoy", value=160.0, unit="percent",
         period="2025", value_basis="RETAIL", confidence="MEDIUM",
         source_name="RedSeer (via Unicommerce)",
         source_url="https://unicommerce.com/blog/beauty-trends-quick-commerce",
         notes="Beauty on QUICK COMMERCE channel YoY growth (channel, not overall market)"),
    dict(segment="total_bpc", metric="market_size", value=27.0, unit="usd_bn",
         period="2025", value_basis="RETAIL", confidence="MEDIUM",
         source_name="RedSeer (via Outlook Business)",
         source_url="https://www.outlookbusiness.com/markets/indias-beauty-products-market-projected-to-reach-39-bn-by-2030-report",
         notes="India BPC ~US$27bn now to US$39bn by 2030; cf Statista US$33.08bn (basket diff)"),
    dict(segment="sun_care", metric="growth_yoy", value=170.0, unit="percent",
         period="2026", value_basis="RETAIL", confidence="LOW",
         source_name="1digitalstack / quick-commerce report",
         source_url="https://www.linkedin.com/posts/samiran-mathur_1ds-sunscreen-qcom-report-apr26-activity-7458503608859250688-2W9u",
         notes="Sunscreen on q-commerce projected ~2.7x (i.e. ~+170%) 2026 vs 2025; Tier 2/3 surge"),
]


def parse() -> list[DataPoint]:
    """Build DataPoints from the curated India value-chain facts.

    Returns:
        Validated DataPoints (geography defaults to IN).
    """
    points = [DataPoint(geography="IN", currency=f.get("currency", "USD"),
                        period_type=_ptype(f["period"]), date_accessed=ACCESSED,
                        **{k: v for k, v in f.items() if k != "currency"})
              for f in FACTS]
    logger.info("Built %d curated India value-chain DataPoints", len(points))
    return points


def _ptype(period: str) -> str:
    if period.upper().startswith("FY"):
        return "FY"
    if "-" in period:
        return "range"
    return "CY"


def run() -> dict:
    """Merge curated India facts into processed data + sources.csv."""
    points = parse()
    summary = upsert_data_points(points)
    return {"points": len(points), "merge": summary}


if __name__ == "__main__":
    import json

    print(json.dumps(run(), indent=2))
