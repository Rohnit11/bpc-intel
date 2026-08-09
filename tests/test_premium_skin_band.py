"""Phase 1 band-retention tests — [PREMIUM-SKIN].

Covers the three places a wrong answer would be invisible in the output: the
Nykaa price-string parse, SKU classification (brand + format), and the band
arithmetic itself.
"""
from __future__ import annotations

import pytest

from lib.fetchers.premium_skin_prices import parse_nykaa_price
from lib.transforms.premium_skin_band import (
    BAND_HIGH,
    BAND_LOW,
    _summarise,
    analyse,
    attribute_brand,
    classify_format,
    flatten,
    pack_size,
    scope_exclusion,
)


class TestNykaaPriceParse:
    def test_discounted_form(self):
        mrp, street, pct = parse_nykaa_price(
            "Regular price ₹1570. Discounted price ₹1413. 10% Off.")
        assert (mrp, street, pct) == (1570.0, 1413.0, 10)

    def test_undiscounted_form_sets_street_equal_to_list(self):
        assert parse_nykaa_price("Price ₹1570.") == (1570.0, 1570.0, 0)

    def test_thousands_separator(self):
        mrp, street, _ = parse_nykaa_price(
            "Regular price ₹2,399. Discounted price ₹1,919. 20% Off.")
        assert (mrp, street) == (2399.0, 1919.0)

    @pytest.mark.parametrize("bad", [None, "", "Enjoy Complimentary Gift", "20% Off"])
    def test_unparseable_returns_nones(self, bad):
        assert parse_nykaa_price(bad) == (None, None, None)


class TestClassification:
    @pytest.mark.parametrize("name,expected", [
        ("Beauty of Joseon Relief Sunscreen Rice + Probiotics SPF 50+ PA++++", "sunscreen"),
        ("Beauty Of Joseon Glow Deep Serum For Pigmentation - Rice + Arbutin",
         "serum_pigmentation_brightening"),
        ("Minimalist 10% Niacinamide Face Serum", "serum_pigmentation_brightening"),
        ("COSRX Advanced Snail 96 Mucin Power Essence", "toner_essence"),
        ("Beauty of Joseon Dynasty Cream", "moisturiser"),
        ("Beauty of Joseon Revive Eye Serum", "eye_lip"),
        ("Beauty of Joseon Essential Kit", "bundle"),
        ("Beauty of Joseon Radiant Rice Most Loved Combo - Lotion + Sunscreen", "bundle"),
    ])
    def test_format(self, name, expected):
        assert classify_format(name) == expected

    def test_bundle_wins_over_sunscreen(self):
        # A sunscreen inside a set is a basket, not a band price point.
        assert classify_format("Korean Sunscreen Discovery Set SPF50") == "bundle"

    @pytest.mark.parametrize("name,brand,group", [
        ("Beauty of Joseon Dynasty Cream", "Beauty of Joseon", "korean"),
        ("Minimalist SPF 50 Sunscreen", "Minimalist", "homegrown"),
        ("Dot & Key Vitamin C Sunscreen", "Dot & Key", "homegrown"),
        ("La Roche-Posay Anthelios UVMune 400", "La Roche-Posay", "other_foreign"),
    ])
    def test_brand_attribution(self, name, brand, group):
        assert attribute_brand(name) == (brand, group)

    def test_unknown_brand_is_not_guessed(self):
        # Origin is a Phase 2/3 question; a listing is not evidence for it.
        assert attribute_brand("SKIN1004 Centella Sun Serum") == (None, "other_observed")


class TestScopeLock:
    @pytest.mark.parametrize("name,reason", [
        ("GHD Chronos Styler Black Hair Straightener", "appliance_device"),
        ("Medicube Age-R Booster Pro X2 White", "appliance_device"),
        ("Accessorize London Women Silver Twist Knot Hinge Bangle", "accessories_apparel"),
        ("Gorgio Professional Jewellery Make Up Trousseau Box", "accessories_apparel"),
        ("Clinique Pop Longwear Lipstick", "colour_cosmetics"),
        ("CLINIQUE Chubby Lash Fattening Mascara", "colour_cosmetics"),
        ("TIRTIR Glide & Hide Blurring Concealer", "colour_cosmetics"),
        ("Forest Essentials Organic Almond Cold Pressed Virgin Oil", "body_bath"),
        ("Paula's Choice Weightless Body Treatment 2% BHA Exfoliant", "body_bath"),
        # A "serum" is not automatically a face serum.
        ("The Ordinary Multi Peptide Serum For Hair Density 60 Ml", "hair_care"),
        ("The Ordinary Multi-Peptide Lash And Brow Serum", "hair_care"),
        ("Kama Ayurveda Lavender & Patchouli Calming Body Cleanser", "body_bath"),
        ("Forever New Cassidy Chunky Hinge Hoop", "accessories_apparel"),
    ])
    def test_out_of_scope_is_caught(self, name, reason):
        assert scope_exclusion(name) == reason

    @pytest.mark.parametrize("name", [
        "Beauty of Joseon Relief Sunscreen Rice + Probiotics SPF 50+",
        "Anua Niacinamide 10 Txa 4 Serum (30 ml)",
        "Clinique Take The Day Off Makeup Remover For Lids Lashes Lips",
        "COSRX Advanced Snail Peptide Eye Cream",
        "Kama Ayurveda Kumkumadi Youth Revitalising Facial Oil",
        "Anua Heartleaf 70 Daily Lotion (200 ml)",
        # Eye-makeup remover is a face cleanser; a rose water face mist is a
        # toner. Neither may be caught by the lash or body rules.
        "Clinique Take The Day Off Makeup Remover For Lids Lashes Lips",
        "Kama Ayurveda Pure Rose Water Mist (200ml)",
        # "Colour correcting" describes pigmentation serums as often as makeup,
        # so it must not be an exclusion trigger.
        "Ras Luxury Oils Flaunt Pigmentation Colour Correcting Serum",
    ])
    def test_face_skincare_survives(self, name):
        # Face lotions, facial oils and makeup removers are skincare; the
        # exclusions must be specific enough not to swallow them.
        assert scope_exclusion(name) is None

    def test_out_of_scope_never_reaches_band_arithmetic(self):
        payload = {"records": [{
            "platform": "nykaa", "search_term": "x", "query_type": "brand",
            "group": "korean", "products": [
                {"name": "Clinique Pop Longwear Lipstick",
                 "url": "https://www.nykaa.com/a/p/1", "mrp": 2400.0,
                 "street_price": 2400.0, "mrp_untrusted": False},
                {"name": "COSRX Advanced Snail Peptide Eye Cream",
                 "url": "https://www.nykaa.com/b/p/2", "mrp": 2300.0,
                 "street_price": 2300.0, "mrp_untrusted": False},
            ]}]}
        analysis = analyse(flatten(payload))
        assert analysis["excluded"]["out_of_scope_skus"] == 1
        assert analysis["excluded"]["out_of_scope_by_reason"] == {"colour_cosmetics": 1}
        assert analysis["headline_by_platform"]["nykaa"]["in_band_by_mrp"] == 1


class TestPackSize:
    @pytest.mark.parametrize("name,expected", [
        ("Anua Heartleaf 77 Soothing Toner (250 ml)", (250.0, "ml")),
        ("Minimalist Sunscreen (50g)", (50.0, "g")),
        ("Laneige Sweet Candy Lip Sleeping Mask (20g)", (20.0, "g")),
        ("Beauty of Joseon Dynasty Cream", None),
    ])
    def test_pack_size(self, name, expected):
        assert pack_size(name) == expected

    def test_different_sizes_are_not_an_mrp_conflict(self):
        # Rs1,550 for 30ml vs Rs3,850 for 125ml is two pack sizes, not two
        # opinions about MRP.
        payload = {"records": [
            {"platform": "nykaa", "search_term": "x", "query_type": "brand",
             "group": "other_foreign", "products": [
                 {"name": "Clinique Take The Day Off Cleansing Balm (30 ml)",
                  "url": "https://www.nykaa.com/a/p/1", "mrp": 1550.0,
                  "street_price": 1550.0, "mrp_untrusted": False}]},
            {"platform": "tira", "search_term": "x", "query_type": "brand",
             "group": "other_foreign", "products": [
                 {"name": "Clinique Take The Day Off Cleansing Balm (125 ml)",
                  "url": "https://www.tirabeauty.com/product/x-1", "mrp": 3850.0,
                  "street_price": 3850.0, "mrp_untrusted": False}]},
        ]}
        assert analyse(flatten(payload))["mrp_conflicts_across_platforms"] == []

    def test_same_size_conflict_is_size_verified(self):
        payload = {"records": [
            {"platform": "nykaa", "search_term": "x", "query_type": "brand",
             "group": "korean", "products": [
                 {"name": "Medicube Collagen Jelly Cream (110 ml)",
                  "url": "https://www.nykaa.com/a/p/1", "mrp": 2800.0,
                  "street_price": 2520.0, "mrp_untrusted": False}]},
            {"platform": "tira", "search_term": "x", "query_type": "brand",
             "group": "korean", "products": [
                 {"name": "Medicube Collagen Jelly Cream (110 ml)",
                  "url": "https://www.tirabeauty.com/product/x-1", "mrp": 1600.0,
                  "street_price": 1600.0, "mrp_untrusted": False}]},
        ]}
        conflicts = analyse(flatten(payload))["mrp_conflicts_size_verified"]
        assert len(conflicts) == 1
        assert conflicts[0]["size_verified"] is True
        assert conflicts[0]["pack_size"] == "110ml"


class TestBandArithmetic:
    def _sku(self, mrp, street, **kw):
        base = {"mrp": mrp, "street_price": street, "platform": "nykaa",
                "brand_group": "korean", "format": "sunscreen",
                "mrp_untrusted": False, "name": "x", "url": "u"}
        base.update(kw)
        return base

    def test_retention_counts_only_survivors(self):
        stats = _summarise([
            self._sku(2000, 1800),   # holds
            self._sku(1600, 1400),   # falls below
            self._sku(1500, 1500),   # holds, boundary
            self._sku(3000, 2000),   # holds, boundary list
        ])
        assert stats["in_band_by_mrp"] == 4
        assert stats["held_band_at_street"] == 3
        assert stats["fell_below_band"] == 1
        assert stats["retention_pct"] == 75.0
        assert stats["collapse_pct"] == 25.0

    def test_entrants_from_above_are_separate_from_retention(self):
        stats = _summarise([
            self._sku(2000, 1800),   # in-band lister, holds
            self._sku(3500, 2400),   # lists above, discounts INTO band
        ])
        assert stats["in_band_by_mrp"] == 1
        assert stats["retention_pct"] == 100.0
        assert stats["entrants_from_above"] == 1
        assert stats["in_band_street_population"] == 2

    def test_empty_population_gives_none_not_zero(self):
        # A missing denominator must read as "no data", never as 0%.
        stats = _summarise([])
        assert stats["retention_pct"] is None
        assert stats["discount_depth_pct"]["median"] is None

    def test_band_bounds_are_inclusive(self):
        stats = _summarise([self._sku(BAND_LOW, BAND_LOW),
                            self._sku(BAND_HIGH, BAND_HIGH)])
        assert stats["in_band_by_mrp"] == 2
        assert stats["held_band_at_street"] == 2


class TestFlattenAndAnalyse:
    def _payload(self):
        return {"records": [
            {"platform": "nykaa", "search_term": "Beauty of Joseon",
             "query_type": "brand", "group": "korean",
             "landed_url": "https://www.nykaa.com/brands/beauty-of-joseon/c/26410",
             "products": [
                 {"name": "Beauty of Joseon Relief Sunscreen SPF50",
                  "url": "https://www.nykaa.com/boj-relief/p/1?pps=2",
                  "mrp": 1570.0, "street_price": 1413.0, "discount_pct": 10,
                  "mrp_untrusted": False},
                 {"name": "Beauty of Joseon Essential Kit",
                  "url": "https://www.nykaa.com/boj-kit/p/2",
                  "mrp": 3250.0, "street_price": 3250.0, "discount_pct": 0,
                  "mrp_untrusted": False},
             ]},
            {"platform": "nykaa", "search_term": "korean sunscreen",
             "query_type": "hero_format", "group": "sunscreen",
             "products": [
                 # Same SKU, different query string on the URL — one observation.
                 {"name": "Beauty of Joseon Relief Sunscreen SPF50",
                  "url": "https://www.nykaa.com/boj-relief/p/1?pps=9",
                  "mrp": 1570.0, "street_price": 1413.0, "discount_pct": 10,
                  "mrp_untrusted": False},
             ]},
            {"platform": "amazon", "search_term": "korean sunscreen",
             "query_type": "hero_format", "group": "sunscreen",
             "products": [
                 {"name": "Beauty of Joseon Relief Sun", "url": "https://www.amazon.in/dp/X",
                  "mrp": None, "street_price": 1125.0,
                  "seller_list_price": 94900.0, "mrp_untrusted": True},
             ]},
            {"platform": "tira", "search_term": "Beauty of Joseon",
             "query_type": "brand", "group": "korean", "error": "timeout",
             "products": []},
        ]}

    def test_dedupes_same_sku_across_queries(self):
        rows = flatten(self._payload())
        relief = [r for r in rows if r["url"].endswith("pps=2")]
        assert len(relief) == 1
        assert sorted(relief[0]["found_via"]) == ["Beauty of Joseon", "korean sunscreen"]

    def test_errored_records_contribute_nothing(self):
        assert not [r for r in flatten(self._payload()) if r["platform"] == "tira"]

    def test_amazon_excluded_from_band_arithmetic(self):
        analysis = analyse(flatten(self._payload()))
        assert "amazon" not in analysis["headline_by_platform"]
        assert analysis["excluded"]["amazon_rows_street_only"] == 1

    def test_bundles_excluded_but_counted(self):
        analysis = analyse(flatten(self._payload()))
        assert analysis["excluded"]["bundles_kits_sets"] == 1
        assert all(s["format"] != "bundle" for s in analysis["all_priced_skus"])

    def test_cross_platform_mrp_conflict_is_caught(self):
        # The two platforms title the same SKU differently and list it at
        # different MRPs; that disagreement is a finding, so it must survive
        # the name mismatch.
        payload = {"records": [
            {"platform": "nykaa", "search_term": "Beauty of Joseon",
             "query_type": "brand", "group": "korean", "products": [
                 {"name": "Beauty of Joseon Relief Sunscreen Rice + Probiotics SPF 50+ PA++++",
                  "url": "https://www.nykaa.com/a/p/1", "mrp": 1570.0,
                  "street_price": 1413.0, "mrp_untrusted": False}]},
            {"platform": "tira", "search_term": "Beauty of Joseon",
             "query_type": "brand", "group": "korean", "products": [
                 {"name": "Beauty of Joseon Relief Sun : Rice + Probiotics SPF 50+ "
                          "PA++++ Most Loved Korean Sunscreen (50 ml)",
                  "url": "https://www.tirabeauty.com/product/x-1", "mrp": 1500.0,
                  "street_price": 1425.0, "mrp_untrusted": False}]},
        ]}
        conflicts = analyse(flatten(payload))["mrp_conflicts_across_platforms"]
        assert len(conflicts) == 1
        assert conflicts[0]["mrp_gap_inr"] == 70.0

    def test_different_products_are_not_matched(self):
        payload = {"records": [
            {"platform": "nykaa", "search_term": "b", "query_type": "brand",
             "group": "korean", "products": [
                 {"name": "Beauty of Joseon Dynasty Cream",
                  "url": "https://www.nykaa.com/a/p/1", "mrp": 2090.0,
                  "street_price": 2090.0, "mrp_untrusted": False}]},
            {"platform": "tira", "search_term": "b", "query_type": "brand",
             "group": "korean", "products": [
                 {"name": "Beauty of Joseon Apricot Blossom Peeling Gel (100 ml)",
                  "url": "https://www.tirabeauty.com/product/x-1", "mrp": 1680.0,
                  "street_price": 1600.0, "mrp_untrusted": False}]},
        ]}
        assert analyse(flatten(payload))["mrp_conflicts_across_platforms"] == []

    def test_headline_reflects_surviving_sku(self):
        analysis = analyse(flatten(self._payload()))
        nykaa = analysis["headline_by_platform"]["nykaa"]
        assert nykaa["in_band_by_mrp"] == 1
        assert nykaa["retention_pct"] == 0.0  # Rs1,570 lists in, Rs1,413 falls out
        assert nykaa["fell_below_band"] == 1
