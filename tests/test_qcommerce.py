"""Parser tests for the q-commerce (Blinkit) tracker.

The live fetch needs a headless browser, but the parser that turns rendered
page text into product records is pure and must be correct — these lock it in
against a real captured Blinkit search page (K-brand watchlist search).
"""
from __future__ import annotations

from lib.fetchers import qcommerce_tracker as qc

# Verbatim shape of a rendered Blinkit search result (captured 2026-07-23),
# covering in-stock, discounted, out-of-stock, and coming-soon cards.
SAMPLE = """Showing results for "anua"
8 MINS
The Face Shop Rice Water Bright Foaming Cleanser
100 ml
₹625
ADD
5% OFF
8 MINS
ClayCo. Face Moisturizer
50 ml
₹949
₹999
ADD
Out of Stock
Coming Soon
8 MINS
Anua Azelaic Acid 10 Hyaluron Face Serum
30 ml
₹2,000
Out of Stock
Coming Soon
8 MINS
Anua Heartleaf Pore Control Cleansing Oil
200 ml
₹1,650
"""


class TestParseProducts:
    def test_parses_all_cards(self):
        products = qc.parse_products(SAMPLE)
        assert len(products) == 4

    def test_in_stock_no_discount(self):
        p = qc.parse_products(SAMPLE)[0]
        assert p["name"].startswith("The Face Shop")
        assert p["pack"] == "100 ml"
        assert p["price_sale"] == 625.0
        assert p["price_mrp"] is None
        assert p["in_stock"] is True
        assert p["kbrand"] == "The Face Shop"

    def test_discounted_card_keeps_mrp_and_pct(self):
        p = qc.parse_products(SAMPLE)[1]  # ClayCo (Indian brand)
        assert p["price_sale"] == 949.0
        assert p["price_mrp"] == 999.0
        assert p["discount_pct"] == 5
        assert p["kbrand"] is None

    def test_out_of_stock_coming_soon(self):
        p = qc.parse_products(SAMPLE)[2]  # Anua Azelaic
        assert p["kbrand"] == "Anua"
        assert p["price_sale"] == 2000.0
        assert p["in_stock"] is False
        assert p["coming_soon"] is True

    def test_price_with_comma_parsed(self):
        p = qc.parse_products(SAMPLE)[3]  # Anua Heartleaf, ₹1,650
        assert p["price_sale"] == 1650.0
        assert p["in_stock"] is False


class TestKbrandHelpers:
    def test_is_kbrand_matches_watchlist(self):
        assert qc.is_kbrand("Beauty of Joseon Rice + Probiotics Sunscreen") == "Beauty of Joseon"
        assert qc.is_kbrand("Lakme 9 to 5 Sunscreen") is None

    def test_kbrand_snapshot_dedupes(self):
        records = [{
            "search_term": "anua", "products": qc.parse_products(SAMPLE),
        }]
        snap = qc.kbrand_snapshot(records)
        names = {p["name"] for p in snap}
        # Only the K-brand cards survive (Face Shop + 2 Anua), ClayCo excluded.
        assert len(snap) == 3
        assert all(qc.is_kbrand(n) for n in names)
