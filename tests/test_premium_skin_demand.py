"""Phase 3 demand-language tests — [PREMIUM-SKIN].

Covers the three places a wrong answer would be invisible in the output:

1. **Origin keying.** The whole Q3 answer is a contrast between Korean-origin
   and Indian-origin SKUs. Phase 1's `brand_group` cannot supply it — its
   `other_observed` bucket holds Klairs, SKIN1004, d'Alba, belif and Aestura
   (Korean) next to Uriage, ISDIN and Eucerin (European) — so this module
   re-keys by brand. If that mapping mis-files a brand, the headline inverts
   quietly.
2. **Polarity and descriptor echo.** "not worth the money" is not an
   endorsement, and "this brightening serum" is a product name being read back,
   not a reported result. Both would inflate the drivers that carry the phase.
3. **Frames and denominators.** The corpus is two non-random frames; pooling
   them, or counting a review once when it belongs to both, produces rates that
   are artefacts of the sampling design.
"""
from __future__ import annotations

import pytest

from lib.transforms.premium_skin_demand import (
    DRIVERS,
    analyse,
    classify_drivers,
    domestic_encroachment,
    driver_ranking,
    flatten,
    origin_contrast,
    provenance_only,
    resolve_origin,
)


def _review(desc: str, title: str = "", **kw) -> dict:
    base = {"title": title, "description": desc,
            "rating": kw.pop("rating", 5), "frame": kw.pop("frame", "most_useful"),
            "skin_tone": kw.pop("tone", None), "skin_type": None,
            "is_verified_buyer": True, "created_on": "2026-01-01 00:00:00"}
    base.update(kw)
    return base


def _sku(name: str, reviews: list[dict], **kw) -> dict:
    base = {"product_id": kw.pop("pid", "1"), "name": name,
            "brand": kw.pop("brand", None), "brand_group": kw.pop("group", "other_observed"),
            "format": kw.pop("fmt", "sunscreen"), "mrp": kw.pop("mrp", 2000.0),
            "reviews": reviews}
    base.update(kw)
    return base


class TestOriginKeying:
    """Phase 1's coverage groups are not origins. This is where that is fixed."""

    @pytest.mark.parametrize("sku_name,expected_brand", [
        ("Klairs Illuminating Supple Blemish Cream SPF 40 PA++", "Klairs"),
        ("Skin1004 Madagascar Centella Air Fit Suncream Plus", "SKIN1004"),
        ("d'Alba piedmont Waterfull Tone-Up Sunscreen, Vegan", "d'Alba"),
        ("D Alba Waterfull Essence Sun Cream Spf 50 Pa", "d'Alba"),
        ("belif Numero10 Essence - Korean Vegan Water Toner", "belif"),
        ("Aestura Derma Uv365 Barrier Hydro Mineral Sunscreen", "Aestura"),
        ("Thank You Farmer Sun Project Silky Calming Sun Stick", "Thank You Farmer"),
        ("Round Lab1025 Dokdo Sunscreen", "Round Lab"),
        ("Dr.Melaxin Tx-Serum Korean Dark Spot Serum", "Dr. Melaxin"),
        ("Axis-Y Dark Spot Correcting Glow Serum", "Axis-Y"),
        ("hince True Dimension Radiance Balm", "hince"),
    ])
    def test_korean_brands_phase1_filed_as_other_observed(self, sku_name, expected_brand):
        brand, origin = resolve_origin(sku_name, None)
        assert (brand, origin) == (expected_brand, "KR")

    @pytest.mark.parametrize("sku_name", [
        "Uriage Depiderm Anti Dark Spot Serum Brightening Booster",
        "ISDIN Fotoprotector Fusion Water Magic SPF 50 PA ++++",
        "Eucerin Anti Pigment Face Illuminating Serum With Thiamidol",
        "Paula's Choice Skin Balancing Serum",
        "Cetaphil Advanced Recovery Serum",
        "Kiehl's Ultra Facial Barrier Cream",
    ])
    def test_european_and_us_brands_are_not_korean(self, sku_name):
        _, origin = resolve_origin(sku_name, None)
        assert origin == "other_foreign"

    @pytest.mark.parametrize("sku_name,expected_brand", [
        ("Ras Luxury Oils Brightening Anti Pigmentation Serum", "RAS Luxury Oils"),
        ("Suganda Arbutin Tranexamic Acid Serum", "Suganda"),
        ("The Derma Co X Dr. V Skin Renew Hyperpigmentation Serum", "The Derma Co"),
        ("Forest Essentials Sheer Sun Fluid Sunscreen SPF 50", "Forest Essentials"),
        ("Fixderma Aha Lightening Gel", "Fixderma"),
        ("Minimalist Dark Spots Solution 2% Alpha Arbutin", "Minimalist"),
    ])
    def test_indian_brands(self, sku_name, expected_brand):
        brand, origin = resolve_origin(sku_name, None)
        assert (brand, origin) == (expected_brand, "IN")

    def test_unknown_brand_is_never_guessed_into_an_origin(self):
        brand, origin = resolve_origin("Zzyzx Radiance Booster Serum", None)
        assert origin == "unclassified"
        assert brand == "Unknown"

    def test_declared_brand_is_kept_when_no_rule_matches(self):
        brand, origin = resolve_origin("Zzyzx Radiance Serum", "Zzyzx")
        assert (brand, origin) == ("Zzyzx", "unclassified")

    def test_substring_keys_do_not_capture_unrelated_words(self):
        # "plum " carries a trailing space precisely so that a plumping claim
        # from another brand is not filed as the Indian brand Plum.
        _, origin = resolve_origin("Torriden Plumping Dive-In Serum", None)
        assert origin == "KR"


class TestDriverClassification:
    """Mention rates are the phase's output; a loose pattern is a fake finding."""

    @pytest.mark.parametrize("text", [
        "Best Korean sunscreen I have used.",
        "I love K-beauty products.",
        "Great kbeauty find.",
        "Korea knows skincare.",
    ])
    def test_korea_origin_fires_on_provenance_language(self, text):
        assert "korea_origin" in classify_drivers(_review(text))

    def test_provenance_in_the_sku_name_does_not_leak_into_the_review(self):
        # Many in-band listings carry "Korean" in the title ("Mixsoon Korean
        # Centella Sun Cream"). Only the review's own words may be scored, or
        # the corpus would report the retailer's copywriting as buyer language.
        rows = flatten({"records": [
            _sku("Mixsoon Korean Centella Sun Cream",
                 [_review("Lightweight and absorbs fast.")])]})
        assert rows[0]["drivers"].get("korea_origin") is None

    @pytest.mark.parametrize("text,driver", [
        ("Niacinamide 10% with tranexamic acid, my kind of serum.", "ingredient_actives"),
        ("My dermatologist recommended this one.", "derm_authority"),
        ("Bought it after seeing it all over Instagram reels.", "social_hype"),
        ("My sister recommended this to me.", "word_of_mouth"),
        ("Survives Mumbai humidity in peak summer.", "climate_context"),
        ("On my third bottle already, holy grail.", "repurchase_loyalty"),
        ("Fits into my night routine after my toner.", "routine_multistep"),
        ("Helped my dark spots and pigmentation.", "pigmentation_concern"),
        ("Glass skin achieved.", "korean_aesthetic"),
        ("Better than the Japanese sunscreen I was using.", "other_origin"),
    ])
    def test_each_driver_fires_on_its_own_language(self, text, driver):
        assert driver in classify_drivers(_review(text))

    @pytest.mark.parametrize("text,driver", [
        # "not worth the money" is the clearest rejection in the corpus. Listing
        # it as its own pattern would start the match at "not", leaving the
        # negation window empty, and file it as an endorsement — which is why
        # price acceptance and price resistance are separate themes.
        ("Not worth the money at all.", "price_worth"),
        ("Not worth the hype honestly.", "price_worth"),
        ("Not expensive at all for what it does.", "price_resistance"),
        ("No visible difference after two months.", "efficacy_result"),
        ("It is not greasy even in humidity.", "climate_context"),
    ])
    def test_negated_language_is_not_scored_as_endorsement(self, text, driver):
        assert classify_drivers(_review(text))[driver] == "negated"

    @pytest.mark.parametrize("text,driver", [
        ("Worth every penny.", "price_worth"),
        ("Too expensive for the quantity you get.", "price_resistance"),
        ("Got it on sale, otherwise too pricey.", "discount_mention"),
    ])
    def test_price_themes_separate_acceptance_from_resistance(self, text, driver):
        assert classify_drivers(_review(text))[driver] == "asserted"

    @pytest.mark.parametrize("text", [
        "My dark spots faded in 6 weeks.",
        "Saw a visible difference in a month.",
        "This actually works.",
        "My marks brightened noticeably.",
    ])
    def test_efficacy_fires_on_reported_results(self, text):
        assert classify_drivers(_review(text)).get("efficacy_result") == "asserted"

    @pytest.mark.parametrize("text", [
        "Bought this brightening serum for my mom.",
        "A nice brightening cream, will see how it goes.",
        "Their brightening line is popular.",
    ])
    def test_product_descriptor_echo_is_not_a_result(self, text):
        # 26 of 101 matches on an unrestricted "brighten*" pattern were the
        # listing's own words read back. Counting those as outcomes would put a
        # fabricated efficacy rate in front of an entry decision.
        assert "efficacy_result" not in classify_drivers(_review(text))

    def test_a_review_can_carry_several_drivers(self):
        drivers = classify_drivers(_review(
            "Korean niacinamide serum, my dark spots faded in 6 weeks, "
            "repurchasing for sure."))
        assert {"korea_origin", "ingredient_actives", "efficacy_result",
                "pigmentation_concern", "repurchase_loyalty"} <= set(drivers)

    def test_every_driver_pattern_set_is_non_empty(self):
        assert all(pats for pats in DRIVERS.values())


class TestFramesAndDenominators:
    """Two non-random frames. Pooling them would report the sampling design."""

    def _payload(self):
        return {"records": [
            _sku("Anua Rice 70 Glow Milky Toner",
                 [_review("Best Korean toner.", frame="most_useful"),
                  _review("Broke me out, not worth the money.", frame="negative",
                          rating=1),
                  _review("Korean formula but too heavy.", frame="both", rating=2)],
                 mrp=1900.0, fmt="toner_essence"),
            _sku("Ras Luxury Oils Brightening Anti Pigmentation Serum",
                 [_review("My pigmentation reduced a lot.", frame="most_useful")],
                 mrp=1990.0, fmt="serum_pigmentation_brightening"),
        ]}

    def test_both_frame_reviews_are_counted_in_each_frame(self):
        analysis = analyse(self._payload())
        assert analysis["most_useful_frame"]["n_reviews"] == 3   # 2 useful + 1 both
        assert analysis["negative_frame"]["n_reviews"] == 2      # 1 negative + 1 both

    def test_origin_contrast_separates_korean_from_indian_skus(self):
        rows = flatten(self._payload())
        useful = [r for r in rows if r["frame"] in ("most_useful", "both")]
        contrast = origin_contrast(useful)
        assert contrast["KR"]["korea_origin_mentions"] == 2
        assert contrast["IN"]["korea_origin_mentions"] == 0

    def test_provenance_split_is_exhaustive(self):
        rows = flatten(self._payload())
        po = provenance_only(rows)
        assert po["origin_only"] + po["origin_plus_mechanism"] == \
            po["origin_citing_reviews"]

    def test_driver_ranking_is_sorted_by_mentions(self):
        counts = [d["mentioned"] for d in driver_ranking(flatten(self._payload()))]
        assert counts == sorted(counts, reverse=True)

    def test_rates_never_exceed_one_hundred_percent(self):
        analysis = analyse(self._payload())
        for frame in ("most_useful_frame", "negative_frame"):
            for row in analysis[frame]["driver_ranking"]:
                assert 0 <= row["mentioned_pct"] <= 100


class TestDomesticEncroachment:
    """Q3(c): who lists in-band when the query names no brand."""

    def _prices(self):
        def prod(name, mrp, street, **kw):
            base = {"name": name, "mrp": mrp, "street_price": street,
                    "discount_pct": 0, "mrp_untrusted": False}
            base.update(kw)
            return base

        return {"records": [
            {"platform": "nykaa", "query_type": "hero_format",
             "search_term": "pigmentation serum", "products": [
                 prod("Suganda Arbutin Tranexamic Acid Serum", 1599.0, 1599.0),
                 prod("Anua Niacinamide 10 Txa 4 Serum", 2000.0, 1800.0),
                 prod("Minimalist Combo of 3 Serums", 1947.0, 1800.0),
                 prod("Foxtale Vitamin C Serum", 695.0, 625.0),
                 prod("Mystery Serum With No Trusted Price", 2000.0, 2000.0,
                      mrp_untrusted=True),
             ]},
            {"platform": "nykaa", "query_type": "brand",
             "search_term": "COSRX", "products": [
                 prod("COSRX The Niacinamide 15 Serum", 2100.0, 1700.0),
             ]},
        ]}

    def test_brand_neutral_window_excludes_brand_queries(self):
        out = domestic_encroachment(self._prices())
        assert out["brand_neutral_queries"]["n_queries"] == 1
        assert out["whole_sweep_floor"]["n_queries"] == 2
        neutral_kr = out["brand_neutral_queries"]["by_origin"]["KR"]
        assert neutral_kr["in_band_observations"] == 1        # Anua only
        assert out["whole_sweep_floor"]["by_origin"]["KR"]["in_band_observations"] == 2

    def test_multipacks_are_excluded_because_a_basket_is_not_a_price_point(self):
        out = domestic_encroachment(self._prices())
        brands = out["brand_neutral_queries"]["by_origin"]["IN"]["distinct_brands"]
        assert "Suganda" in brands
        assert "Minimalist" not in brands

    def test_out_of_band_and_untrusted_prices_are_excluded(self):
        out = domestic_encroachment(self._prices())
        names = [e["name"] for e in
                 out["brand_neutral_queries"]["by_origin"]["IN"]["examples"]]
        assert not any("Foxtale" in n for n in names)          # Rs695, below band
        counted = sum(v["in_band_observations"]
                      for v in out["brand_neutral_queries"]["by_origin"].values())
        assert counted == 2                                    # Suganda + Anua

    def test_band_retention_by_street_price(self):
        out = domestic_encroachment(self._prices())
        assert out["brand_neutral_queries"]["by_origin"]["IN"]["held_band_pct"] == 100.0
        assert out["brand_neutral_queries"]["by_origin"]["KR"]["held_band_pct"] == 100.0
