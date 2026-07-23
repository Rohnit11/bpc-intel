"""Curated K-beauty corridor product & players facts (Tavily corridor sweep).

Product-level depth on the Korea -> India corridor: K-beauty market sizing in
India, hero-SKU shelf prices, and the India-side of the trade (platforms
curating Korean brands + Indian D2C brands riding the Korean wave, registered
in config/corridor.yaml). Hand-curated with each claim's source URL (data/raw/
is gitignored). Every fact is [CORRIDOR]-tagged.

Confidence per CLAUDE.md: aggregators = LOW; retailer listings / trade press =
MEDIUM.

Run:  python -m lib.ingest.corridor_curated
"""
from __future__ import annotations

import logging
from datetime import date

from lib.transforms.merge import upsert_data_points
from lib.transforms.schema import DataPoint

logger = logging.getLogger("bpc_intel.ingest.corridor_curated")

ACCESSED = date(2026, 7, 23)

FACTS: list[dict] = [
    # ---- K-beauty-in-India market sizing (corridor) ----
    dict(segment="total_bpc", metric="market_size", value=32424.0, unit="inr_cr",
         currency="INR", period="2035", value_basis="RETAIL", confidence="LOW",
         source_name="Expert Market Research",
         source_url="https://www.expertmarketresearch.com/reports/india-k-beauty-products-market",
         notes="[CORRIDOR] K-beauty in India 2035 forecast; from INR 3139.31cr (2025) "
               "base at ~26.3% CAGR"),
    dict(segment="total_bpc", metric="cagr_forecast", value=26.3, unit="percent",
         currency="INR", period="2026-2035", value_basis="RETAIL", confidence="LOW",
         source_name="Expert Market Research",
         source_url="https://www.expertmarketresearch.com/reports/india-k-beauty-products-market",
         notes="[CORRIDOR] India K-beauty products market forecast CAGR 2026-2035; "
               "fastest-growing beauty sub-trend, K-pop/K-drama pull"),

    # ---- Hero-SKU shelf prices in India (MRP, corridor) ----
    dict(segment="sun_care", metric="retail_price", value=1570.0, unit="inr",
         currency="INR", period="2026", value_basis="MRP", confidence="MEDIUM",
         source_name="Nykaa (retailer listing)",
         source_url="https://www.nykaa.com/brands/beauty-of-joseon/c/26410",
         notes="[CORRIDOR] Beauty of Joseon Relief Sunscreen SPF50+; MRP Rs1570, Nykaa "
               "sale Rs1256 (20% off) as of 2026-07-23; category bestseller; promo-dependent"),
    dict(segment="skincare", metric="retail_price", value=1490.0, unit="inr",
         currency="INR", period="2026", value_basis="MRP", confidence="MEDIUM",
         source_name="Nykaa (retailer listing)",
         source_url="https://www.nykaa.com/cosrx-advanced-snail-96-mucin-power-essence/p/757628",
         notes="[CORRIDOR] COSRX Advanced Snail 96 Mucin Power Essence 100ml; MRP Rs1490, "
               "Nykaa sale Rs969 (35% off), Amazon ~Rs949 as of 2026-07-23; hero SKU; promo-dependent"),
    dict(segment="skincare", metric="retail_price", value=2050.0, unit="inr",
         currency="INR", period="2026", value_basis="MRP", confidence="MEDIUM",
         sub_segment="toners_essences",
         source_name="Nykaa (retailer listing)",
         source_url="https://www.nykaa.com/anua-heartleaf-77percent-soothing-toner/p/20736553",
         notes="[CORRIDOR] Anua Heartleaf 77% Soothing Toner 250ml; Nykaa list Rs2050 (sale "
               "Rs1743); Amazon MRP Rs2999/buy Rs1999 as of 2026-07-23; MRP varies by platform"),
    dict(segment="skincare", metric="retail_price", value=600.0, unit="inr",
         currency="INR", period="2026", value_basis="MRP", confidence="MEDIUM",
         sub_segment="lip_care_non_colour",
         source_name="Nykaa (retailer listing)",
         source_url="https://www.nykaa.com/laneige-lip-sleeping-mask-berry/p/15227410",
         notes="[CORRIDOR] Laneige Lip Sleeping Mask Berry 8g; MRP Rs600, Nykaa sale Rs510 "
               "(15% off); 20g Rs1136 as of 2026-07-23"),
    dict(segment="skincare", metric="retail_price", value=2200.0, unit="inr",
         currency="INR", period="2026", value_basis="MRP", confidence="MEDIUM",
         sub_segment="serums_ampoules",
         source_name="Nykaa (retailer listing)",
         source_url="https://www.nykaa.com/dp/innisfree-serum",
         notes="[CORRIDOR] Innisfree Green Tea Seed Serum; MRP Rs2200, Nykaa/Amazon sale Rs1650 "
               "(25% off) as of 2026-07-23"),

    # ---- q-commerce (Blinkit) snapshot prices, 2026-07-23 ----
    dict(segment="skincare", metric="retail_price", value=625.0, unit="inr",
         currency="INR", period="2026", value_basis="MRP", confidence="MEDIUM",
         sub_segment="facial_cleansers",
         source_name="Blinkit (q-commerce snapshot)",
         source_url="https://blinkit.com/s/?q=the%20face%20shop",
         notes="[CORRIDOR] The Face Shop Rice Water Bright Foaming Cleanser 100ml; Blinkit Rs625 "
               "in stock as of 2026-07-23; entry-price K-beauty on the q-commerce rail"),
    dict(segment="skincare", metric="retail_price", value=850.0, unit="inr",
         currency="INR", period="2026", value_basis="MRP", confidence="MEDIUM",
         source_name="Blinkit (q-commerce snapshot)",
         source_url="https://blinkit.com/s/?q=laneige",
         notes="[CORRIDOR] Laneige Water Sleeping Mask 25ml; MRP Rs850, Blinkit Rs765 as of 2026-07-23"),
    dict(segment="skincare", metric="retail_price", value=850.0, unit="inr",
         currency="INR", period="2026", value_basis="MRP", confidence="MEDIUM",
         sub_segment="serums_ampoules",
         source_name="Blinkit (q-commerce snapshot)",
         source_url="https://blinkit.com/s/?q=innisfree",
         notes="[CORRIDOR] Innisfree Green Tea Seed Hyaluronic Face Serum 30ml; MRP Rs850, Blinkit "
               "Rs680 as of 2026-07-23 (distinct from the larger Green Tea Seed Serum ~Rs2200)"),
    dict(segment="skincare", metric="retail_price", value=1600.0, unit="inr",
         currency="INR", period="2026", value_basis="MRP", confidence="MEDIUM",
         sub_segment="facial_moisturisers",
         source_name="Blinkit (q-commerce snapshot)",
         source_url="https://blinkit.com/s/?q=etude",
         notes="[CORRIDOR] Etude SoonJung Hydro Barrier Face Cream 75ml (derma); MRP Rs1600, "
               "Blinkit Rs1200 as of 2026-07-23"),
    dict(segment="skincare", metric="retail_price", value=1500.0, unit="inr",
         currency="INR", period="2026", value_basis="MRP", confidence="MEDIUM",
         sub_segment="toners_essences",
         source_name="Blinkit (q-commerce snapshot)",
         source_url="https://blinkit.com/s/?q=beauty%20of%20joseon",
         notes="[CORRIDOR] Beauty of Joseon Ginseng Skin Essence Water 150ml; Blinkit Rs1500 "
               "in stock as of 2026-07-23"),
]


def parse() -> list[DataPoint]:
    """Build [CORRIDOR] DataPoints from the curated corridor facts (geography IN)."""
    points = [DataPoint(geography="IN", period_type=_ptype(f["period"]),
                        date_accessed=ACCESSED, **f) for f in FACTS]
    logger.info("Built %d curated corridor DataPoints", len(points))
    return points


def _ptype(period: str) -> str:
    if period.upper().startswith("FY"):
        return "FY"
    if "-" in period:
        return "range"
    return "CY"


def run() -> dict:
    """Merge curated corridor facts into processed data + sources.csv."""
    points = parse()
    return {"points": len(points), "merge": upsert_data_points(points)}


if __name__ == "__main__":
    import json

    print(json.dumps(run(), indent=2))
