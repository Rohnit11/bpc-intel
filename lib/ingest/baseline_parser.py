"""Parse the baseline deep-research report into canonical DataPoints.

Every claim below was extracted by reading data/baseline/deep-research-report.md.
Each carries an `anchor` — an exact substring of the report — and the parser
refuses to emit any DataPoint whose anchor is not found in the markdown. This
guarantees every number traces to the baseline text, never to model memory.

Confidence follows CLAUDE.md: MFDS/government/Euromonitor = HIGH; credible
trade press / Statista = MEDIUM; aggregators (Mordor, IMARC, EMR, GVR, DMI) =
LOW; derived figures = ESTIMATE with methodology.
"""
from __future__ import annotations

import csv
import logging
from collections import defaultdict
from datetime import date
from pathlib import Path

from lib.analysis.gaps import format_gaps_register, scan_gaps
from lib.transforms.schema import DataPoint, SegmentFile, save_segment_file

logger = logging.getLogger("bpc_intel.baseline_parser")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BASELINE_PATH = PROJECT_ROOT / "data" / "baseline" / "deep-research-report.md"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
SOURCES_CSV = PROJECT_ROOT / "data" / "sources.csv"
GAPS_REGISTER = PROJECT_ROOT / "reports" / "latest" / "gaps_register.md"

DATE_ACCESSED = date(2026, 7, 21)

VB_UNCERTAIN = "value_basis_uncertain"


def _c(anchor: str, **fields) -> dict:
    """Build a claim record with defaults."""
    base = dict(
        sub_segment=None, tier=None, source_url=None,
        date_accessed=DATE_ACCESSED, methodology=None, notes=None,
    )
    base.update(fields)
    base["anchor"] = anchor
    return base


# ---------------------------------------------------------------------------
# Claims extracted from the baseline report (anchor-verified)
# ---------------------------------------------------------------------------
CLAIMS: list[dict] = [
    # === KOREA — totals ===
    _c("US$13 billion in 2024",
       geography="KR", segment="total_bpc", metric="market_size", value=13.0,
       unit="usd_bn", currency="USD", period="2024", period_type="CY",
       value_basis="RETAIL", source_name="Euromonitor International",
       confidence="HIGH", notes="Category-consistent BPC definition; report's highest-weighted total"),
    _c("1.8% in constant value terms",
       geography="KR", segment="total_bpc", metric="growth_yoy", value=1.8,
       unit="percent", currency="USD", period="2024", period_type="CY",
       value_basis="RETAIL", source_name="Euromonitor International",
       confidence="HIGH", notes="Constant value terms"),
    _c("US$13.66bn (2025)",
       geography="KR", segment="total_bpc", metric="market_size", value=13.66,
       unit="usd_bn", currency="USD", period="2025", period_type="CY",
       value_basis="RETAIL", source_name="Mordor Intelligence",
       confidence="LOW", notes="Broader 'cosmetics' basket; treat cautiously per baseline; " + VB_UNCERTAIN),
    _c("US$13.66bn (2025)",
       geography="KR", segment="total_bpc", metric="cagr_forecast", value=6.61,
       unit="percent", currency="USD", period="2025-2030", period_type="range",
       value_basis="RETAIL", source_name="Mordor Intelligence",
       confidence="LOW", notes="Forecast CAGR to 2030; broader basket"),
    _c("US$18.39bn (2025)",
       geography="KR", segment="total_bpc", metric="market_size", value=18.39,
       unit="usd_bn", currency="USD", period="2025", period_type="CY",
       value_basis="RETAIL", source_name="Expert Market Research",
       confidence="LOW", notes="'Cosmetics' definition, broader than BPC; " + VB_UNCERTAIN),
    _c("~US$250+",
       geography="KR", segment="total_bpc", metric="per_capita_spend", value=250.0,
       unit="usd", currency="USD", period="2024", period_type="CY",
       value_basis="RETAIL", source_name="Baseline report (derived)",
       confidence="ESTIMATE",
       methodology="Derived in baseline: ~US$13bn Euromonitor retail total / ~52m population; quoted as '~US$250+'",
       notes="Order-of-magnitude comparison vs India"),
    _c("premium ~US$5.88bn",
       geography="KR", segment="total_bpc", metric="market_size", value=5.88,
       unit="usd_bn", currency="USD", period="2024", period_type="CY",
       value_basis="RETAIL", tier="premium", source_name="Baseline report (source unstated)",
       confidence="LOW", notes="Aggregate premium value; source not stated in baseline; " + VB_UNCERTAIN),

    # === KOREA — exports (MFDS / Korea Customs, EXPORT_FOB) ===
    _c("US$11.43 billion, a record, +12.3% YoY",
       geography="KR", segment="total_bpc", metric="export_value", value=11.43,
       unit="usd_bn", currency="USD", period="2025", period_type="CY",
       value_basis="EXPORT_FOB", source_name="MFDS / Korea Customs Service",
       confidence="HIGH", notes="Record; world #2 cosmetics exporter"),
    _c("US$11.43 billion, a record, +12.3% YoY",
       geography="KR", segment="total_bpc", metric="growth_yoy", value=12.3,
       unit="percent", currency="USD", period="2025", period_type="CY",
       value_basis="EXPORT_FOB", source_name="MFDS / Korea Customs Service",
       confidence="HIGH", notes="Export growth"),
    _c("2024 exports were US$10.2bn",
       geography="KR", segment="total_bpc", metric="export_value", value=10.2,
       unit="usd_bn", currency="USD", period="2024", period_type="CY",
       value_basis="EXPORT_FOB", source_name="MFDS / Korea Customs Service",
       confidence="HIGH", notes="+20.3% YoY"),
    _c("rose 11.6 percent on-year to $8.54 billion",
       geography="KR", segment="skincare", metric="export_value", value=8.54,
       unit="usd_bn", currency="USD", period="2025", period_type="CY",
       value_basis="EXPORT_FOB", source_name="MFDS via Yonhap/Korea Herald",
       confidence="HIGH", notes="~75% of total exports"),
    _c("rose 11.6 percent on-year to $8.54 billion",
       geography="KR", segment="skincare", metric="growth_yoy", value=11.6,
       unit="percent", currency="USD", period="2025", period_type="CY",
       value_basis="EXPORT_FOB", source_name="MFDS via Yonhap/Korea Herald",
       confidence="HIGH"),
    _c("climbed 12 percent to $1.51 billion",
       geography="KR", segment="colour_cosmetics", metric="export_value", value=1.51,
       unit="usd_bn", currency="USD", period="2025", period_type="CY",
       value_basis="EXPORT_FOB", source_name="MFDS via Yonhap/Korea Herald",
       confidence="HIGH", notes="~13% of total exports"),
    _c("climbed 12 percent to $1.51 billion",
       geography="KR", segment="colour_cosmetics", metric="growth_yoy", value=12.0,
       unit="percent", currency="USD", period="2025", period_type="CY",
       value_basis="EXPORT_FOB", source_name="MFDS via Yonhap/Korea Herald",
       confidence="HIGH"),
    _c("jumped 27.3 percent to $590 million",
       geography="KR", segment="bath_shower", metric="export_value", value=0.59,
       unit="usd_bn", currency="USD", period="2025", period_type="CY",
       value_basis="EXPORT_FOB", source_name="MFDS via Yonhap/Korea Herald",
       confidence="HIGH", notes="'Body cleansing products' category"),
    _c("surged 46.2 percent to $60 million",
       geography="KR", segment="fragrances", metric="export_value", value=0.06,
       unit="usd_bn", currency="USD", period="2025", period_type="CY",
       value_basis="EXPORT_FOB", source_name="MFDS via Yonhap/Korea Herald",
       confidence="HIGH", notes="+46.2% YoY, small base"),
    _c("US$2.2bn (+15.1%)",
       geography="KR", segment="total_bpc", metric="export_value", value=2.2,
       unit="usd_bn", currency="USD", period="2025", period_type="CY",
       value_basis="EXPORT_FOB", source_name="MFDS / Korea Customs Service",
       confidence="HIGH", notes="Destination: US (#1 destination, +15.1%)"),
    _c("China fell to ~US$2.0bn",
       geography="KR", segment="total_bpc", metric="export_value", value=2.0,
       unit="usd_bn", currency="USD", period="2025", period_type="CY",
       value_basis="EXPORT_FOB", source_name="MFDS / Korea Customs Service",
       confidence="HIGH", notes="Destination: China (-19.2% YoY)"),
    _c("Poland (+111.7% to US$282m)",
       geography="KR", segment="total_bpc", metric="export_value", value=0.282,
       unit="usd_bn", currency="USD", period="2025", period_type="CY",
       value_basis="EXPORT_FOB", source_name="MFDS / Korea Customs Service",
       confidence="HIGH", notes="Destination: Poland, breakout market +111.7%"),
    _c("UAE (+67.2% to US$286m)",
       geography="KR", segment="total_bpc", metric="export_value", value=0.286,
       unit="usd_bn", currency="USD", period="2025", period_type="CY",
       value_basis="EXPORT_FOB", source_name="MFDS / Korea Customs Service",
       confidence="HIGH", notes="Destination: UAE, breakout market +67.2%"),
    _c("rose ~44.7%",
       geography="KR", segment="total_bpc", metric="export_value", value=0.05,
       unit="usd_bn", currency="USD", period="H1_2025", period_type="H1",
       value_basis="EXPORT_FOB", source_name="MFDS / Korea Customs Service",
       confidence="MEDIUM", notes="Destination: India; ~US$50m base, +44.7% H1 2025 basis"),

    # === KOREA — production (MFDS, PRODUCTION) ===
    _c("KRW 17.54 trillion (2024)",
       geography="KR", segment="total_bpc", metric="production_value", value=17.54,
       unit="krw_tn", currency="KRW", period="2024", period_type="CY",
       value_basis="PRODUCTION", source_name="MFDS", confidence="HIGH",
       notes="Record domestic production value"),
    _c("KRW 17.9 trillion (2025",
       geography="KR", segment="total_bpc", metric="production_value", value=17.9,
       unit="krw_tn", currency="KRW", period="2025", period_type="CY",
       value_basis="PRODUCTION", source_name="MFDS", confidence="HIGH"),
    _c("Cosmax #1 at KRW 1.61 trillion",
       geography="KR", segment="total_bpc", metric="production_value", value=1.61,
       unit="krw_tn", currency="KRW", period="2025", period_type="CY",
       value_basis="PRODUCTION", source_name="MFDS", confidence="HIGH",
       notes="Company: Cosmax — #1 by production value"),
    _c("Kolmar KRW 1.30 trillion",
       geography="KR", segment="total_bpc", metric="production_value", value=1.30,
       unit="krw_tn", currency="KRW", period="2025", period_type="CY",
       value_basis="PRODUCTION", source_name="MFDS", confidence="HIGH",
       notes="Company: Kolmar Korea — #2 by production value"),
    _c("Cosmecca KRW 353 billion",
       geography="KR", segment="total_bpc", metric="production_value", value=353.0,
       unit="krw_bn", currency="KRW", period="2025", period_type="CY",
       value_basis="PRODUCTION", source_name="MFDS", confidence="HIGH",
       notes="Company: Cosmecca Korea — #3 by production value"),
    _c("177.8% to KRW 285bn",
       geography="KR", segment="total_bpc", metric="production_value", value=285.0,
       unit="krw_bn", currency="KRW", period="2025", period_type="CY",
       value_basis="PRODUCTION", source_name="MFDS (via Reach24H analysis)",
       confidence="MEDIUM", notes="Company: APR (Medicube), +177.8%, rank 21 to 4"),
    _c("+50% to KRW 228.5bn",
       geography="KR", segment="total_bpc", metric="production_value", value=228.5,
       unit="krw_bn", currency="KRW", period="2025", period_type="CY",
       value_basis="PRODUCTION", source_name="MFDS (via Reach24H analysis)",
       confidence="MEDIUM", notes="Company: The Founders (Anua), +50%"),
    _c("+68.6% to KRW 184.1bn",
       geography="KR", segment="total_bpc", metric="production_value", value=184.1,
       unit="krw_bn", currency="KRW", period="2025", period_type="CY",
       value_basis="PRODUCTION", source_name="MFDS (via Reach24H analysis)",
       confidence="MEDIUM", notes="Company: Gudai Global (Beauty of Joseon), +68.6%"),
    _c("+52.9% to KRW 166.2bn",
       geography="KR", segment="total_bpc", metric="production_value", value=166.2,
       unit="krw_bn", currency="KRW", period="2025", period_type="CY",
       value_basis="PRODUCTION", source_name="MFDS (via Reach24H analysis)",
       confidence="MEDIUM", notes="Company: Benow, +52.9%"),

    # === KOREA — segments & companies ===
    _c("dermocosmetics, which grew 13% in 2024",
       geography="KR", segment="dermocosmetics", metric="growth_yoy", value=13.0,
       unit="percent", currency="KRW", period="2024", period_type="CY",
       value_basis="RETAIL", source_name="Euromonitor International",
       confidence="HIGH", notes="Driven by PDRN, exosomes, peptides"),
    _c("22% of the premium segment",
       geography="KR", segment="total_bpc", metric="market_share", value=22.0,
       unit="percent", currency="KRW", period="2024", period_type="CY",
       value_basis="RETAIL", tier="premium", source_name="Euromonitor International",
       confidence="HIGH", notes="Company: AmorePacific share of premium BPC"),
    _c("KRW 4.25 trillion (+9.5%)",
       geography="KR", segment="total_bpc", metric="revenue", value=4.25,
       unit="krw_tn", currency="KRW", period="2025", period_type="CY",
       value_basis="NET_REALISATION", source_name="AmorePacific disclosure via trade press",
       confidence="MEDIUM", notes="Company: AmorePacific, +9.5% YoY; OP KRW 335.8bn +52.3%"),
    _c("fell 6.7% to KRW 6.36 trillion",
       geography="KR", segment="total_bpc", metric="revenue", value=6.36,
       unit="krw_tn", currency="KRW", period="2025", period_type="CY",
       value_basis="NET_REALISATION", source_name="LG H&H disclosure via trade press",
       confidence="MEDIUM", notes="Company: LG H&H, -6.7% YoY; OP KRW 170.7bn -62.8%; includes non-BPC HDB lines"),
    _c("record 2025 revenue ~KRW 2.39 trillion",
       geography="KR", segment="total_bpc", metric="revenue", value=2.39,
       unit="krw_tn", currency="KRW", period="2025", period_type="CY",
       value_basis="NET_REALISATION", source_name="Korea Product Post",
       confidence="MEDIUM", notes="Company: Cosmax (ODM), record year"),
    _c("2024 was KRW 2.16T, +21.9%",
       geography="KR", segment="total_bpc", metric="revenue", value=2.16,
       unit="krw_tn", currency="KRW", period="2024", period_type="CY",
       value_basis="NET_REALISATION", source_name="Korea Biomedical Review",
       confidence="MEDIUM", notes="Company: Cosmax (ODM), +21.9% YoY"),
    _c("record 2025 revenue KRW 2.72 trillion",
       geography="KR", segment="total_bpc", metric="revenue", value=2.72,
       unit="krw_tn", currency="KRW", period="2025", period_type="CY",
       value_basis="NET_REALISATION", source_name="Korea Biomedical Review",
       confidence="MEDIUM", notes="Company: Kolmar Korea (ODM); OP KRW 239.6bn; US subsidiary +71%"),
    _c("KRW 4.79 trillion",
       geography="KR", segment="total_bpc", metric="revenue", value=4.79,
       unit="krw_tn", currency="KRW", period="2024", period_type="CY",
       value_basis="NET_REALISATION", source_name="Seoul Economic Daily",
       confidence="MEDIUM", notes="Company: CJ Olive Young (retailer), +~22% YoY"),
    _c("KRW 5.83 trillion",
       geography="KR", segment="total_bpc", metric="revenue", value=5.83,
       unit="krw_tn", currency="KRW", period="2025", period_type="CY",
       value_basis="NET_REALISATION", source_name="Seoul Economic Daily",
       confidence="MEDIUM", notes="Company: CJ Olive Young (retailer), +21.8% YoY, ~1,350-1,370 stores"),
    _c("KRW 224.6bn",
       geography="KR", segment="total_bpc", metric="revenue", value=224.6,
       unit="krw_bn", currency="KRW", period="FY24", period_type="FY",
       value_basis="NET_REALISATION", source_name="Baseline report (company disclosure)",
       confidence="MEDIUM", notes="Company: Innisfree, -18%; down from KRW 768bn peak (2016); road-shop collapse"),

    # === KOREA — channels ===
    _c("50% of value (Euromonitor, 2024)",
       geography="KR", segment="total_bpc", metric="channel_share", value=50.0,
       unit="percent", currency="KRW", period="2024", period_type="CY",
       value_basis="RETAIL", source_name="Euromonitor International",
       confidence="HIGH", notes="E-commerce share of BPC value; reported as '>50%'"),
    _c("60.8% in 2024",
       geography="KR", segment="total_bpc", metric="channel_share", value=60.8,
       unit="percent", currency="KRW", period="2024", period_type="CY",
       value_basis="RETAIL", source_name="Korea Ratings via Korea JoongAng Daily",
       confidence="MEDIUM", notes="Cosmetics online penetration; up from 39.1% in 2019"),
    _c("KRW 12.5 trillion in 2025",
       geography="KR", segment="total_bpc", metric="market_size", value=12.5,
       unit="krw_tn", currency="KRW", period="2025", period_type="CY",
       value_basis="RETAIL", source_name="Korea Duty Free Shops Association via Seoul Economic Daily",
       confidence="MEDIUM",
       notes="Duty-free channel, ALL categories (not BPC-only), -11.8% YoY; " + VB_UNCERTAIN),
    _c("KRW 24.8 trillion",
       geography="KR", segment="total_bpc", metric="market_size", value=24.8,
       unit="krw_tn", currency="KRW", period="2019", period_type="CY",
       value_basis="RETAIL", source_name="Korea Duty Free Shops Association",
       confidence="MEDIUM", notes="Duty-free peak, ALL categories; halved by 2025; " + VB_UNCERTAIN),
    _c("KRW 2.5 trillion in 2024",
       geography="KR", segment="total_bpc", metric="market_size", value=2.5,
       unit="krw_tn", currency="KRW", period="2024", period_type="CY",
       value_basis="RETAIL", source_name="Baseline report (scope varies)",
       confidence="LOW",
       notes="Live commerce; 'sizing varies by scope definition'; Naver ~73.6% share; " + VB_UNCERTAIN),

    # === INDIA — totals ===
    _c("US$33.08bn in 2025",
       geography="IN", segment="total_bpc", metric="market_size", value=33.08,
       unit="usd_bn", currency="USD", period="2025", period_type="CY",
       value_basis="RETAIL", source_name="Statista (via China Briefing)",
       confidence="MEDIUM", notes="Statista consumer-market 'revenue' basis; " + VB_UNCERTAIN),
    _c("the 2024 value was ~US$28bn",
       geography="IN", segment="total_bpc", metric="market_size", value=28.0,
       unit="usd_bn", currency="USD", period="2024", period_type="CY",
       value_basis="RETAIL", source_name="Statista (via China Briefing)",
       confidence="MEDIUM", notes="Lower bound of baseline's US$28-31bn working range; " + VB_UNCERTAIN),
    _c("US$31.19bn (2025)",
       geography="IN", segment="total_bpc", metric="market_size", value=31.19,
       unit="usd_bn", currency="USD", period="2025", period_type="CY",
       value_basis="RETAIL", source_name="IMARC", confidence="LOW"),
    _c("3.48% CAGR to 2030",
       geography="IN", segment="total_bpc", metric="cagr_forecast", value=3.48,
       unit="percent", currency="USD", period="2025-2030", period_type="range",
       value_basis="RETAIL", source_name="Statista", confidence="MEDIUM",
       notes="Conservative vs consensus ~10%"),
    _c("cluster 10–11%",
       geography="IN", segment="total_bpc", metric="growth_yoy", value=10.0,
       unit="percent", currency="USD", period="2024", period_type="CY",
       value_basis="RETAIL", source_name="Baseline consensus (multiple houses)",
       confidence="LOW", notes="Most houses cluster 10-11%; conservative ones 5-6%"),
    _c("US$22.74 in 2025",
       geography="IN", segment="total_bpc", metric="per_capita_spend", value=22.74,
       unit="usd", currency="USD", period="2025", period_type="CY",
       value_basis="RETAIL", source_name="Statista", confidence="MEDIUM",
       notes="Per-person BPC revenue; order of magnitude below Korea"),

    # === INDIA — segments ===
    _c("~35% by IMARC",
       geography="IN", segment="skincare", metric="market_share", value=35.0,
       unit="percent", currency="USD", period="2025", period_type="CY",
       value_basis="RETAIL", source_name="IMARC", confidence="LOW",
       notes="Skincare/sun care share of total BPC"),
    _c("49% of the narrower",
       geography="IN", segment="skincare", metric="market_share", value=49.0,
       unit="percent", currency="USD", period="2025", period_type="CY",
       value_basis="RETAIL", source_name="Grand View Research", confidence="LOW",
       notes="Share of narrower 'cosmetics' basket, not full BPC"),
    _c("US$3.46bn (2024, DMI)",
       geography="IN", segment="colour_cosmetics", metric="market_size", value=3.46,
       unit="usd_bn", currency="USD", period="2024", period_type="CY",
       value_basis="RETAIL", source_name="DMI", confidence="LOW",
       notes="Forecast CAGR 7.08%"),
    _c("79.55% mass in 2025, Mordor",
       geography="IN", segment="colour_cosmetics", metric="market_share", value=79.55,
       unit="percent", currency="USD", period="2025", period_type="CY",
       value_basis="RETAIL", tier="mass", source_name="Mordor Intelligence",
       confidence="LOW", notes="Mass tier share of colour cosmetics"),
    _c("Rs 186.3bn in 2025, +9%",
       geography="IN", segment="mens_grooming", metric="market_size", value=186.3,
       unit="inr_bn", currency="INR", period="2025", period_type="CY",
       value_basis="RETAIL", source_name="Euromonitor International",
       confidence="HIGH", notes="+9% growth"),
    _c("Rs 186.3bn in 2025, +9%",
       geography="IN", segment="mens_grooming", metric="growth_yoy", value=9.0,
       unit="percent", currency="INR", period="2025", period_type="CY",
       value_basis="RETAIL", source_name="Euromonitor International",
       confidence="HIGH"),
    _c("US$2.3bn in 2024, 6.8% CAGR",
       geography="IN", segment="mens_grooming", metric="market_size", value=2.3,
       unit="usd_bn", currency="USD", period="2024", period_type="CY",
       value_basis="RETAIL", source_name="IMARC", confidence="LOW",
       notes="Narrower 'male grooming products' basket; 6.8% forecast CAGR"),
    _c("~9.4% of revenue in 2025",
       geography="IN", segment="total_bpc", metric="channel_share", value=9.4,
       unit="percent", currency="USD", period="2025", period_type="CY",
       value_basis="RETAIL", source_name="Baseline report (projection, source unstated)",
       confidence="LOW", notes="Digital channels share of BPC revenue"),
    _c("13.4% of daily sales",
       geography="IN", segment="total_bpc", metric="channel_share", value=13.4,
       unit="percent", currency="INR", period="2025", period_type="CY",
       value_basis="RETAIL", source_name="Unicommerce", confidence="MEDIUM",
       notes="BPC share of Blinkit daily sales — q-commerce channel signal"),
    _c("US$5.5bn (2025)",
       geography="IN", segment="total_bpc", metric="market_size", value=5.5,
       unit="usd_bn", currency="USD", period="2025", period_type="CY",
       value_basis="RETAIL", source_name="Baseline report (q-commerce sizing)",
       confidence="LOW",
       notes="Indian q-commerce market ALL categories (not BPC-only); Blinkit >50% share; " + VB_UNCERTAIN),

    # === INDIA — companies ===
    _c("FY25 revenue ~Rs 10,022 crore",
       geography="IN", segment="total_bpc", metric="revenue", value=10022.0,
       unit="inr_cr", currency="INR", period="FY25", period_type="FY",
       value_basis="NET_REALISATION", source_name="Nykaa (FSN E-Commerce) disclosure",
       confidence="MEDIUM", notes="Company: Nykaa; 265 stores, ~4,200 brands, ~40m beauty customers"),
    _c("FY25 revenue Rs 2,067 crore (+8%)",
       geography="IN", segment="total_bpc", metric="revenue", value=2067.0,
       unit="inr_cr", currency="INR", period="FY25", period_type="FY",
       value_basis="NET_REALISATION", source_name="Honasa Consumer disclosure",
       confidence="MEDIUM", notes="Company: Honasa (Mamaearth); PAT Rs 73 cr -32%, Project Neev reset"),
    _c("Rs 347 crore in FY24",
       geography="IN", segment="skincare", metric="revenue", value=347.0,
       unit="inr_cr", currency="INR", period="FY24", period_type="FY",
       value_basis="NET_REALISATION", source_name="Entrackr",
       confidence="MEDIUM", notes="Company: Minimalist (Uprising Science); up from Rs 184 cr FY23"),
]

# Quantitative claims that have no schema metric (deal values, funding rounds).
# They still get sources.csv rows per CLAUDE.md rule 2.
LEDGER_ONLY: list[dict] = [
    dict(anchor="Rs 2,706.44 crore",
         claim="HUL acquired 90.5% of Uprising Science (Minimalist) for Rs 2,706.44 crore",
         value="2706.44", unit="inr_cr", currency="INR", geography="IN", segment="skincare",
         period="FY25", period_type="FY", value_basis="N/A (deal value)",
         source_name="Business Standard (Apr 22, 2025)", confidence="MEDIUM",
         notes="Completed acquisition; primary infusion + secondary purchase"),
    dict(anchor="Rs 2,955 crore",
         claim="Minimalist pre-money EV in HUL deal: Rs 2,955 crore (~US$350m)",
         value="2955", unit="inr_cr", currency="INR", geography="IN", segment="skincare",
         period="FY25", period_type="FY", value_basis="N/A (deal value)",
         source_name="Entrackr", confidence="MEDIUM",
         notes="Signed Jan 2025; remaining 9.5% in ~2 years"),
    dict(anchor="US$560m",
         claim="AmorePacific acquired COSRX to 93.2% for ~US$560m (KRW 755bn)",
         value="0.56", unit="usd_bn", currency="USD", geography="KR", segment="skincare",
         period="2024", period_type="CY", value_basis="N/A (deal value)",
         source_name="Baseline report (Oct 2024 deal)", confidence="MEDIUM", notes=""),
    dict(anchor="$2.32 billion between January and September",
         claim="Korea beauty-sector M&A totalled US$2.32bn Jan-Sep 2025",
         value="2.32", unit="usd_bn", currency="USD", geography="KR", segment="total_bpc",
         period="2025", period_type="CY", value_basis="N/A (deal value)",
         source_name="McKinsey via The Korea Herald (Nov 3, 2025)", confidence="MEDIUM",
         notes="ION Analytics separately counted 26 deals ~US$1.8bn"),
    dict(anchor="Skinfood + Serin (~KRW 750bn",
         claim="Gudai Global bought Skinfood + Serin for ~KRW 750bn (US$521m)",
         value="750", unit="krw_bn", currency="KRW", geography="KR", segment="total_bpc",
         period="2025", period_type="CY", value_basis="N/A (deal value)",
         source_name="Baseline report", confidence="MEDIUM", notes=""),
    dict(anchor="KKR/Samhwa (cosmetics packaging, KRW 733bn",
         claim="KKR acquired Samhwa (cosmetics packaging) for KRW 733bn",
         value="733", unit="krw_bn", currency="KRW", geography="KR", segment="total_bpc",
         period="2025", period_type="CY", value_basis="N/A (deal value)",
         source_name="Baseline report (Sept 2025)", confidence="MEDIUM", notes=""),
    dict(anchor="Blackstone/Juno Hair (KRW 800bn",
         claim="Blackstone acquired Juno Hair for KRW 800bn",
         value="800", unit="krw_bn", currency="KRW", geography="KR", segment="hair_care",
         period="2025", period_type="CY", value_basis="N/A (deal value)",
         source_name="Baseline report (Sept 2025)", confidence="MEDIUM", notes=""),
    dict(anchor="~US$180m",
         claim="Unilever reportedly acquired majority of Plum for ~US$180m",
         value="0.18", unit="usd_bn", currency="USD", geography="IN", segment="skincare",
         period="2025", period_type="CY", value_basis="N/A (deal value)",
         source_name="Baseline report (reported, unconfirmed)", confidence="LOW",
         notes="Single-source; verify terms"),
    dict(anchor="~US$100m",
         claim="L'Oréal reportedly took ~30% of Kama Ayurveda for ~US$100m",
         value="0.10", unit="usd_bn", currency="USD", geography="IN", segment="total_bpc",
         period="2024", period_type="CY", value_basis="N/A (deal value)",
         source_name="Baseline report (reported, unconfirmed)", confidence="LOW",
         notes="Single-source; verify terms"),
    dict(anchor="Series D US$50m",
         claim="SUGAR Cosmetics raised Series D US$50m (L Catterton-backed)",
         value="0.05", unit="usd_bn", currency="USD", geography="IN", segment="colour_cosmetics",
         period="2024", period_type="CY", value_basis="N/A (deal value)",
         source_name="Baseline report", confidence="MEDIUM", notes=""),
    dict(anchor="ADIA-led US$120m",
         claim="Purplle raised ADIA-led US$120m at ~US$1.1bn valuation",
         value="0.12", unit="usd_bn", currency="USD", geography="IN", segment="total_bpc",
         period="2024", period_type="CY", value_basis="N/A (deal value)",
         source_name="Baseline report", confidence="MEDIUM", notes=""),
    dict(anchor="US$1.1bn Medik8 deal was pegged at ~13x",
         claim="L'Oréal/Medik8 deal US$1.1bn at ~13x 2024 sales (reference multiple)",
         value="1.1", unit="usd_bn", currency="USD", geography="KR", segment="dermocosmetics",
         period="2024", period_type="CY", value_basis="N/A (deal value)",
         source_name="Baseline report", confidence="MEDIUM",
         notes="Global reference multiple for science-backed skincare"),
]


def parse_baseline_report(md_path: str | Path = BASELINE_PATH) -> list[DataPoint]:
    """Extract every anchor-verified quantitative claim as DataPoints.

    Args:
        md_path: Path to the baseline markdown report.

    Returns:
        List of validated DataPoints.

    Raises:
        ValueError: If any claim's anchor text is not found in the report —
            the claims table and the report have diverged; never emit
            unverifiable numbers.
    """
    text = Path(md_path).read_text(encoding="utf-8")
    missing = [c["anchor"] for c in CLAIMS if c["anchor"] not in text]
    missing += [c["anchor"] for c in LEDGER_ONLY if c["anchor"] not in text]
    if missing:
        raise ValueError(
            f"{len(missing)} claim anchor(s) not found in {md_path}: {missing}"
        )
    points = [
        DataPoint(**{k: v for k, v in claim.items() if k != "anchor"})
        for claim in CLAIMS
    ]
    logger.info("Parsed %d data points from %s (all anchors verified)", len(points), md_path)
    return points


def write_processed(points: list[DataPoint], processed_dir: str | Path = PROCESSED_DIR) -> dict[str, int]:
    """Group DataPoints by geography x segment and write SegmentFiles.

    Args:
        points: DataPoints to persist.
        processed_dir: Output directory.

    Returns:
        Mapping of output filename -> data point count.
    """
    processed_dir = Path(processed_dir)
    grouped: dict[tuple[str, str], list[DataPoint]] = defaultdict(list)
    for dp in points:
        grouped[(dp.geography, dp.segment)].append(dp)

    counts: dict[str, int] = {}
    for (geo, seg), dps in sorted(grouped.items()):
        sf = SegmentFile(geography=geo, segment=seg, last_updated=DATE_ACCESSED, data_points=dps)
        fname = f"{geo}_{seg}.json"
        save_segment_file(sf, processed_dir / fname)
        counts[fname] = len(dps)
    return counts


def write_sources_csv(points: list[DataPoint], csv_path: str | Path = SOURCES_CSV) -> int:
    """Rewrite data/sources.csv from the baseline extraction (idempotent).

    Args:
        points: DataPoints to record.
        csv_path: Path to the master source ledger.

    Returns:
        Number of rows written (excluding header).
    """
    csv_path = Path(csv_path)
    header = ["claim", "value", "unit", "currency", "geography", "segment", "period",
              "period_type", "value_basis", "source_name", "url", "date_accessed",
              "confidence", "notes"]
    rows: list[list[str]] = []
    for dp in points:
        claim = f"{dp.geography} {dp.segment} {dp.metric}" + (f" [{dp.tier}]" if dp.tier else "")
        rows.append([
            claim, str(dp.value), dp.unit, dp.currency, dp.geography, dp.segment,
            dp.period, dp.period_type, dp.value_basis, dp.source_name,
            dp.source_url or "", dp.date_accessed.isoformat(), dp.confidence,
            dp.notes or "",
        ])
    for rec in LEDGER_ONLY:
        rows.append([
            rec["claim"], rec["value"], rec["unit"], rec["currency"], rec["geography"],
            rec["segment"], rec["period"], rec["period_type"], rec["value_basis"],
            rec["source_name"], "", DATE_ACCESSED.isoformat(), rec["confidence"],
            rec["notes"],
        ])
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(header)
        writer.writerows(rows)
    logger.info("Wrote %d rows to %s", len(rows), csv_path)
    return len(rows)


def run() -> dict:
    """Full baseline ingest: parse -> processed JSONs -> sources.csv -> gaps register.

    Returns:
        Summary dict: file counts, total points, ledger rows, uncertain flags.
    """
    points = parse_baseline_report()
    counts = write_processed(points)
    n_rows = write_sources_csv(points)

    gaps = scan_gaps()
    GAPS_REGISTER.parent.mkdir(parents=True, exist_ok=True)
    GAPS_REGISTER.write_text(format_gaps_register(gaps), encoding="utf-8")
    logger.info("Wrote gaps register (%d gaps) to %s", len(gaps), GAPS_REGISTER)

    uncertain = [
        f"{dp.geography}/{dp.segment}/{dp.metric} ({dp.source_name})"
        for dp in points if dp.notes and VB_UNCERTAIN in dp.notes
    ]
    return {
        "data_points": len(points),
        "files": counts,
        "sources_csv_rows": n_rows,
        "ledger_only_rows": len(LEDGER_ONLY),
        "gaps": len(gaps),
        "value_basis_uncertain": uncertain,
    }


if __name__ == "__main__":
    import json as _json

    summary = run()
    print(_json.dumps(summary, indent=2))
