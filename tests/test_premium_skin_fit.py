"""Phase 2 review-mining tests — [PREMIUM-SKIN].

Covers the two places a wrong answer would be invisible in the output:

1. **Polarity.** Indian sunscreen reviews say "no white cast" far more often
   than they say "white cast". If negation detection fails, the analysis
   reports the category's most reassured-about attribute as its most
   complained-about one, and every downstream conclusion inverts. Most of this
   file is that one risk.
2. **Denominators.** The corpus is two non-random frames; a rate computed
   across the pool would be an artefact of the sampling design, and the
   population floor must stay a floor.
"""
from __future__ import annotations

import pytest

from lib.fetchers.premium_skin_reviews import parse_review, product_id, review_url
from lib.transforms.premium_skin_fit import (
    TONE_GROUPS,
    analyse,
    classify,
    flatten,
    polarity,
    population_floor,
    rating_distribution,
)


def _review(desc: str, title: str = "", **kw) -> dict:
    base = {"title": title, "description": desc, "rating": kw.pop("rating", 1),
            "frame": kw.pop("frame", "negative"), "skin_tone": kw.pop("tone", None),
            "skin_type": None, "is_verified_buyer": True, "created_on": None}
    base.update(kw)
    return base


class TestPolarity:
    """'no white cast' is praise. Counting it as a complaint inverts Phase 2."""

    @pytest.mark.parametrize("text", [
        "It blends in leaving no white cast at all.",
        "Zero white cast on my skin.",
        "Absorbs fast and doesn't leave a white cast.",
        "Lightweight, no white cast, no stickiness.",
        "It did not leave any white cast even on my dusky skin.",
        "White cast free formula, finally.",
        "Never broke me out.",
        "Not greasy at all in Mumbai humidity.",
    ])
    def test_negated_phrasings_do_not_count_as_complaints(self, text):
        themes = classify(_review(text))
        assert themes, f"pattern never fired on: {text}"
        assert all(v == "negated" for v in themes.values()), themes

    @pytest.mark.parametrize("text", [
        "Leaves a horrible white cast on my face.",
        "There is a slight white cast which I hate.",
        "Makes me look white and ashy in photos.",
        "It broke me out within three days.",
        "Very greasy and sticky in this humidity.",
        "It pills under my makeup every single time.",
    ])
    def test_asserted_phrasings_count_as_complaints(self, text):
        themes = classify(_review(text))
        assert themes, f"pattern never fired on: {text}"
        assert "asserted" in themes.values(), themes

    def test_praise_then_complaint_resolves_to_asserted(self):
        # Under-counting a real failure is the worse error for a product brief.
        themes = classify(_review(
            "No white cast on my hand but it left a white cast on my face."))
        assert themes["white_cast"] == "asserted"

    def test_negation_does_not_leak_across_a_sentence_boundary(self):
        # "no" belongs to the previous sentence; the cast is still asserted.
        themes = classify(_review(
            "There is no fragrance. White cast is very visible on me."))
        assert themes["white_cast"] == "asserted"

    def test_distant_negation_is_not_applied(self):
        text = ("I do not usually write reviews but let me tell you about this "
                "product because honestly it left a terrible white cast.")
        assert polarity(text, text.index("white cast"),
                        text.index("white cast") + 10) == "asserted"


class TestThemes:
    def test_oily_skin_type_is_not_a_greasiness_complaint(self):
        # "oily skin" is a skin type, not a complaint about the product.
        assert "heavy_greasy_humid" not in classify(
            _review("I have oily skin and this worked well."))

    def test_greasy_finish_is_a_complaint(self):
        themes = classify(_review("Makes my face oily within an hour."))
        assert themes.get("heavy_greasy_humid") == "asserted"

    def test_tone_mismatch_detected(self):
        themes = classify(_review("Way too light for my dusky skin tone."))
        assert themes.get("tone_mismatch") == "asserted"

    def test_no_efficacy_on_pigmentation(self):
        themes = classify(_review(
            "Used it for three months, no visible difference in dark spots."))
        assert themes.get("no_efficacy_pigmentation") == "asserted"

    def test_title_is_scanned_too(self):
        themes = classify(_review("Nothing much to add.", title="White cast!!"))
        assert themes.get("white_cast") == "asserted"

    def test_clean_review_raises_nothing(self):
        assert classify(_review("Lovely texture, will repurchase.")) == {}


class TestParseReview:
    def test_lifts_skin_tone_and_type_out_of_metadata(self):
        row = {
            "id": 1, "rating": 2, "title": "meh", "description": "ok",
            "isBuyer": True, "likeCount": 3, "images": [],
            "metaData": {"portfolioForm": [
                {"attributeType": "skinTone", "attributes": [{"value": "Deep"}]},
                {"attributeType": "skinType", "attributes": [{"value": "Oily"}]},
            ]},
        }
        parsed = parse_review(row)
        assert parsed["skin_tone"] == "Deep"
        assert parsed["skin_type"] == "Oily"
        assert TONE_GROUPS[parsed["skin_tone"]] == "dusky"

    def test_missing_profile_stays_null_and_is_not_imputed(self):
        parsed = parse_review({"id": 2, "rating": 5, "description": "good"})
        assert parsed["skin_tone"] is None
        assert parsed["skin_type"] is None


class TestUrls:
    def test_product_id_from_pdp_url(self):
        assert product_id(
            "https://www.nykaa.com/beauty-of-joseon-relief-sunscreen/p/16900408"
            "?productId=16900408&pps=18") == "16900408"

    def test_review_url_keeps_the_slug(self):
        assert review_url(
            "https://www.nykaa.com/some-slug/p/123?productId=123") == (
            "https://www.nykaa.com/some-slug/reviews/123?ptype=review")

    def test_url_without_product_id_yields_none(self):
        assert product_id("https://www.nykaa.com/brands/anua/c/3814") is None
        assert review_url("https://www.nykaa.com/brands/anua/c/3814") is None


class TestDenominators:
    def _payload(self):
        return {"records": [{
            "product_id": "1", "name": "K Sunscreen", "brand": "Anua",
            "brand_group": "korean", "format": "sunscreen", "mrp": 1900.0,
            "review_url": "https://www.nykaa.com/k/reviews/1?ptype=review",
            "written_review_count": 100,
            "rating_distribution": {"1": 10, "2": 10, "3": 10, "4": 20, "5": 50},
            "reviews": [
                _review("Terrible white cast.", frame="negative", rating=1),
                _review("Greasy and sticky.", frame="negative", rating=2),
                _review("No white cast, lovely.", frame="most_useful", rating=5),
                _review("Great but slight white cast.", frame="most_useful",
                        rating=5),
            ],
        }]}

    def test_rating_distribution_is_a_census_of_written_reviews(self):
        dist = rating_distribution(self._payload())
        assert dist["overall"]["written_reviews"] == 100
        assert dist["overall"]["negative_1_2_star"] == 20
        assert dist["overall"]["negative_share_pct"] == 20.0

    def test_frames_are_counted_separately_not_pooled(self):
        analysis = analyse(self._payload())
        assert analysis["negative_frame"]["overall"]["n_reviews"] == 2
        assert analysis["most_useful_frame"]["overall"]["n_reviews"] == 2
        assert analysis["coverage"]["reviews_analysed"] == 4

    def test_positive_review_complaint_is_kept(self):
        # "Great but slight white cast" is the strongest evidence a failure is
        # real; it must survive into the most-useful frame as asserted.
        analysis = analyse(self._payload())
        useful = analysis["most_useful_frame"]["overall"]["themes"]["white_cast"]
        assert useful["asserted"] == 1
        assert useful["negated"] == 1

    def test_population_floor_multiplies_and_stays_a_floor(self):
        # 20% of written reviews are negative; 50% of those assert the theme.
        assert population_floor(20.0, 50.0) == 10.0
        assert population_floor(None, 50.0) is None
        assert population_floor(20.0, None) is None

    def test_floor_never_exceeds_the_within_negative_rate(self):
        assert population_floor(20.0, 50.0) < 50.0

    def test_skus_with_no_reviews_contribute_nothing(self):
        payload = self._payload()
        payload["records"].append({
            "product_id": "2", "name": "Empty", "brand": None,
            "brand_group": "korean", "format": "sunscreen", "mrp": 1600.0,
            "written_review_count": 0, "rating_distribution": {},
            "reviews": [],
        })
        analysis = analyse(payload)
        assert analysis["coverage"]["skus_targeted"] == 2
        assert analysis["coverage"]["skus_with_any_review"] == 1
        assert analysis["coverage"]["skus_with_zero_reviews"] == 1
        assert analysis["rating_distribution"]["skus_with_reviews"] == 1


class TestFlatten:
    def test_tone_group_is_mapped_from_declared_tone(self):
        payload = {"records": [{
            "product_id": "1", "name": "S", "brand": "X", "brand_group": "korean",
            "format": "sunscreen", "mrp": 1900.0, "rating_distribution": {},
            "reviews": [_review("White cast.", tone="Deep"),
                        _review("Fine.", tone=None)],
        }]}
        rows = flatten(payload)
        assert rows[0]["tone_group"] == "dusky"
        assert rows[1]["tone_group"] is None
