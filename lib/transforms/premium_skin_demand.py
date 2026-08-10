"""Is "Korean" load-bearing, or incidental? — [PREMIUM-SKIN] Phase 3.

Phase 2 mined the same review corpus for what goes WRONG
(`lib/transforms/premium_skin_fit.py`). This module mines it for what buyers
reach for when they explain a product they like: provenance, actives, clinical
authority, social proof, climate fit, price, repurchase, routine. The brief's
Q3 asks whether Korean origin is doing the selling or is incidental to it, and
declares the answer a POSITIONING input, not a go/no-go.

## What a mention rate is, and is not

A review is written after the purchase, about the experience. It is not a
statement of purchase motivation. So:

- A high "korean" mention rate is evidence that provenance is **salient enough
  to volunteer** — real evidence, and the closest thing a review corpus holds
  to a positioning signal.
- A low one is **weak** evidence of a weak driver. Buyers do not restate what
  they took for granted, and a reviewer of a Korean brand has no reason to
  announce that the brand is Korean. Absence here is not proof of absence.

The asymmetry is why the strong test in this module is not the rate itself but
the **contrast**: origin language in reviews of KOREAN-origin SKUs against the
same language in reviews of INDIAN-origin and other-foreign SKUs. If Indian-brand
reviewers reach for Korea as a benchmark, provenance has category-level pull that
does not belong to any brand. If nobody reaches for it anywhere, the term is
inert in the language buyers actually use, whatever the marketing says.

## Origin, not the Phase 1 brand groups

Phase 1's `brand_group` is a *coverage* label: "korean" means the brand was on
the brief's named list, and `other_observed` means it was not. It is therefore
useless for this question — `other_observed` holds Aestura, Celimax, Klairs,
Round Lab, SKIN1004, Torriden, belif and d'Alba (all Korean) alongside Uriage,
ISDIN and Eucerin (all European). This module re-keys every SKU to a
manufacturer-origin label (`ORIGIN`), assigned by brand, and leaves brands whose
origin is not established as `unclassified` rather than guessing them into a
bucket. Origin labels are analyst-assigned brand provenance, auditable in one
table below; they are not market data.

## Frames, unpooled

The corpus is two non-random frames (see `lib/fetchers/premium_skin_reviews.py`):
every retrievable 1-2 star review, and the top pages of Nykaa's default "most
useful" ordering, which is overwhelmingly 5-star. Rates are computed inside a
frame and never across it. `most_useful` is the frame that answers Q3 — it is
where satisfied buyers say what they valued.

Polarity checking is reused wholesale from Phase 2 (`polarity`) so that "not
worth the money" and "no visible difference" are not counted as endorsements.
"""
from __future__ import annotations

import json
import logging
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from lib.transforms.premium_skin_fit import TONE_GROUPS, latest_raw, polarity
from lib.transforms.schema import DataPoint

logger = logging.getLogger("bpc_intel.premium_skin_demand")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ANALYSIS_PATH = PROJECT_ROOT / "data" / "manual" / "analysis" / "premium_skin_demand.json"

# Brand provenance. Key = lowercase substring matched against the SKU name
# (43 of the 109 sampled SKUs carry `brand: None` in the raw sweep, so the SKU
# title is the only brand handle available). Order matters: the first match
# wins, so longer keys precede shorter ones that would also match.
#
# `unclassified` is deliberate. ALBIZZIA, Biluma, Eternal Bright, Gunam and
# LuxaDerme are small listings whose corporate origin this thread has not
# verified; they are excluded from the origin contrast rather than assigned on a
# hunch. Between them they carry ~20 of 3,287 reviews.
ORIGIN: list[tuple[str, str, str]] = [
    # --- Korea ---
    ("beauty of joseon", "Beauty of Joseon", "KR"),
    ("beauty Of joseon", "Beauty of Joseon", "KR"),
    ("thank you farmer", "Thank You Farmer", "KR"),
    ("the face shop", "The Face Shop", "KR"),
    ("round lab", "Round Lab", "KR"),
    ("dr althea", "Dr. Althea", "KR"),
    ("dr.jart", "Dr.Jart+", "KR"),
    ("dr jart", "Dr.Jart+", "KR"),
    ("house of hur", "House of HUR", "KR"),
    ("d alba", "d'Alba", "KR"),
    ("d'alba", "d'Alba", "KR"),
    ("skin1004", "SKIN1004", "KR"),
    ("aestura", "Aestura", "KR"),
    ("apieu", "A'pieu", "KR"),
    ("celimax", "Celimax", "KR"),
    ("klairs", "Klairs", "KR"),
    ("torriden", "Torriden", "KR"),
    ("belif", "belif", "KR"),
    ("innisfree", "Innisfree", "KR"),
    ("isntree", "Isntree", "KR"),
    ("laneige", "Laneige", "KR"),
    ("medicube", "Medicube", "KR"),
    ("mixsoon", "Mixsoon", "KR"),
    ("tirtir", "TirTir", "KR"),
    ("cosrx", "COSRX", "KR"),
    ("etude", "Etude", "KR"),
    ("anua", "Anua", "KR"),
    ("dr.althea", "Dr. Althea", "KR"),
    ("dr.melaxin", "Dr. Melaxin", "KR"),
    ("dr melaxin", "Dr. Melaxin", "KR"),
    ("axis-y", "Axis-Y", "KR"),
    ("tonymoly", "TonyMoly", "KR"),
    ("tony moly", "TonyMoly", "KR"),
    ("sulwhasoo", "Sulwhasoo", "KR"),
    ("numbuzin", "Numbuzin", "KR"),
    ("some by mi", "Some By Mi", "KR"),
    ("hince", "hince", "KR"),
    ("mizon", "Mizon", "KR"),
    ("missha", "Missha", "KR"),
    ("arencia", "Arencia", "KR"),
    ("bioheal", "Bioheal Boh", "KR"),
    ("one thing", "One Thing", "KR"),
    ("mediheal", "Mediheal", "KR"),
    ("laneige", "Laneige", "KR"),
    # --- India ---
    ("forest essentials", "Forest Essentials", "IN"),
    ("kama ayurveda", "Kama Ayurveda", "IN"),
    ("ras luxury", "RAS Luxury Oils", "IN"),
    ("the derma co", "The Derma Co", "IN"),
    ("bath and care", "TBC The Bath & Care", "IN"),
    ("suganda", "Suganda", "IN"),
    ("ethiglo", "Ethiglo", "IN"),
    ("wildglow", "WildGlow", "IN"),
    ("yuderma", "Yuderma", "IN"),
    ("miduty", "Miduty", "IN"),
    ("bie - beauty in everything", "BiE", "IN"),
    ("bie beauty in everything", "BiE", "IN"),
    ("fixderma", "Fixderma", "IN"),
    ("aminu", "Aminu", "IN"),
    ("minimalist", "Minimalist", "IN"),
    ("dot & key", "Dot & Key", "IN"),
    ("dot and key", "Dot & Key", "IN"),
    ("foxtale", "Foxtale", "IN"),
    ("pilgrim", "Pilgrim", "IN"),
    ("deconstruct", "Deconstruct", "IN"),
    ("earth rhythm", "Earth Rhythm", "IN"),
    ("plum ", "Plum", "IN"),
    ("limese", "Limese", "IN"),
    # --- Other foreign ---
    ("la roche", "La Roche-Posay", "other_foreign"),
    ("paula's choice", "Paula's Choice", "other_foreign"),
    ("paulas choice", "Paula's Choice", "other_foreign"),
    ("clinique", "Clinique", "other_foreign"),
    ("bobbi brown", "Bobbi Brown", "other_foreign"),
    ("cetaphil", "Cetaphil", "other_foreign"),
    ("kiehl", "Kiehl's", "other_foreign"),
    ("mario badescu", "Mario Badescu", "other_foreign"),
    ("murad", "Murad", "other_foreign"),
    ("nudestix", "Nudestix", "other_foreign"),
    ("heliocare", "Heliocare", "other_foreign"),
    ("depiwhite", "Depiwhite", "other_foreign"),
    ("bioderma", "Bioderma", "other_foreign"),
    ("the ordinary", "The Ordinary", "other_foreign"),
    ("sebamed", "Sebamed", "other_foreign"),
    ("eucerin", "Eucerin", "other_foreign"),
    ("isdin", "ISDIN", "other_foreign"),
    ("uriage", "Uriage", "other_foreign"),
    ("palmer", "Palmer's", "other_foreign"),
    # --- Origin not established ---
    ("albizzia", "ALBIZZIA", "unclassified"),
    ("biluma", "Biluma", "unclassified"),
    ("eternal bright", "Eternal Bright", "unclassified"),
    ("gunam", "Gunam", "unclassified"),
    ("luxaderme", "LuxaDerme", "unclassified"),
]

# Purchase-driver themes. Narrow by construction: a driver that fires on a
# generic word produces a rate that means nothing. Where a word is ambiguous it
# must appear in a phrase that disambiguates it ("routine" alone is fine —
# reviewers use it only about their own regimen — but "step" needs a qualifier).
DRIVERS: dict[str, list[str]] = {
    # Provenance, the Q3 variable.
    "korea_origin": [
        r"\bkorean?\b", r"\bkoreans\b", r"k-? ?beauty", r"\bkbeauty\b",
        r"\bseoul\b", r"made in korea", r"\bkorea'?s\b",
    ],
    # The Korean beauty *ideal* rather than the country — salience of the
    # aesthetic can outlive salience of the provenance.
    "korean_aesthetic": [
        r"glass ?skin", r"\b10[- ]?step", r"k-?drama", r"korean glow",
        r"korean (?:routine|regimen)",
    ],
    # Other provenances, as the control. If Japan and France score like Korea,
    # origin-in-general is salient and Korea is not special.
    "other_origin": [
        r"japan(?:ese)?\b", r"j-? ?beauty", r"french (?:pharmacy|brand|sunscreen|skincare)",
        r"western (?:brand|skincare|product)", r"american (?:brand|sunscreen)",
        r"\bthai\b", r"european (?:brand|sunscreen|skincare)",
    ],
    "ingredient_actives": [
        r"niacinamide", r"vitamin ?c\b", r"ascorbic", r"snail (?:mucin|secretion)",
        r"\bmucin\b", r"centella", r"\bcica\b", r"madecass\w*", r"hyaluronic",
        r"\bha\b", r"ceramide", r"tranexamic", r"\btxa?\b", r"arbutin", r"kojic",
        r"azelaic", r"retin(?:ol|al|oid)", r"glycolic", r"salicylic", r"\bbha\b",
        r"\baha\b", r"\bpha\b", r"peptide", r"propolis", r"ginseng", r"rice (?:water|extract)",
        r"heartleaf", r"houttuynia", r"panthenol", r"allantoin", r"\bpdrn\b",
        r"collagen", r"adenosine", r"licorice", r"mugwort", r"tea tree",
        r"green tea", r"glutathione", r"thiamidol", r"zinc oxide", r"titanium dioxide",
        r"\bspf ?\d+", r"\bpa\+{2,}", r"galactomyces", r"bifida", r"fermented",
    ],
    "efficacy_result": [
        r"visible (?:difference|change|result|improvement)",
        r"saw (?:a |the )?(?:difference|change|result|improvement)",
        r"(?:really|actually|definitely|genuinely) work(?:s|ed)",
        r"(?:dark ?spots?|pigmentation|marks?|blemish\w*|tan(?:ning)?|melasma|acne|scars?)"
        r"(?:\s+\w+){0,4}\s+(?:reduc\w*|fad\w*|lighten\w*|clear\w*|gone|disappear\w*|"
        r"improv\w*|vanish\w*|lessen\w*)",
        r"in (?:just |only )?\d+ (?:days?|weeks?|months?)",
        r"even(?:ed)? out (?:my )?(?:skin ?)?tone",
        # "brightened"/"brightens" is a reported result; bare "brightening" is
        # usually the product's own descriptor echoed back ("this brightening
        # serum"), which is not evidence of an outcome. 26 of 101 matches on the
        # unrestricted pattern were that echo, so the noun forms are excluded.
        r"brighten(?:ed|s)\b",
        r"brightening\b(?!\s*-?\s*(?:serum|cream|toner|lotion|sunscreen|sun ?cream|"
        r"essence|booster|ampoule|product|gel|complex|care|line|formula|"
        r"ingredient|agent|properties))",
        r"(?:skin|face) (?:looks?|feels?) (?:so |much )?(?:better|clearer|brighter)",
    ],
    "derm_authority": [
        r"derm(?:at)?ologist", r"\bdermat\b", r"skin (?:doctor|specialist)",
        r"my doctor", r"prescrib(?:ed|es)", r"derm(?:atologically)?[ -]tested",
        r"clinically (?:tested|proven)", r"\bderm recommend\w*",
    ],
    "social_hype": [
        r"instagram", r"\binsta\b", r"\breels?\b", r"youtube", r"influencer",
        r"tiktok", r"viral", r"hyped?\b", r"trending", r"saw (?:it|this) on",
        r"everyone(?:'s| is)? (?:talking|using|raving)", r"blogger",
        r"all over (?:my )?(?:feed|social)",
    ],
    "word_of_mouth": [
        r"(?:friend|sister|cousin|mom|mother|colleague|wife|husband|brother)s?"
        r"(?:\s+\w+){0,3}\s+(?:recommend\w*|suggest\w*|told me|uses?|gifted|gave me)",
        r"recommended by (?:my )?(?:friend|sister|mom|mother|cousin|colleague)",
        r"word of mouth",
    ],
    "climate_context": [
        r"humid(?:ity)?", r"indian (?:summer|weather|climate|heat)", r"monsoon",
        r"sweat\w*", r"hot and humid", r"tropical", r"\d\d ?degrees?",
        r"peak summer", r"delhi (?:heat|summer)", r"mumbai (?:humidity|weather)",
    ],
    # Price splits into two themes, not one. A single "price_value" theme would
    # score "worth every penny" and "too expensive" as the same event, and worse:
    # listing "not worth the money" as its own pattern makes the match START at
    # "not", leaving the negation window empty, so the polarity check reports the
    # clearest rejection in the corpus as an endorsement. Acceptance language and
    # resistance language are therefore separate themes, and each is left to the
    # shared negation window to polarise.
    "price_worth": [
        r"worth (?:the |every )?(?:money|price|penny|rupee|it|hype)",
        r"value for money", r"splurge", r"affordable",
    ],
    "price_resistance": [
        r"(?:too |very |so |bit )?(?:expensive|overpriced|pricey|costly)",
        r"(?:quantity|amount) is (?:too )?(?:less|small|little)",
        r"tiny (?:bottle|tube|jar)", r"for this price",
    ],
    "discount_mention": [
        r"on (?:sale|discount|offer)", r"cheaper than", r"during (?:the )?sale",
        r"got it for", r"\bdeal\b",
    ],
    "repurchase_loyalty": [
        r"repurchas\w+", r"(?:buy|buying|bought|order\w*|purchas\w*)"
        r"(?:\s+\w+){0,3}\s+again", r"(?:second|third|fourth|2nd|3rd|another|"
        r"multiple|\d+(?:st|nd|rd|th)) (?:bottle|tube|jar|pack|jar|time|one)",
        r"restock\w*", r"(?:using|used) (?:it |this )?(?:for|since)"
        r"(?:\s+\w+){0,3}\s+(?:months?|years?)", r"holy grail", r"\bhg\b",
        r"never going back", r"my (?:go[ -]?to|staple|favourite|favorite)",
        r"stock(?:ed)? up",
    ],
    "routine_multistep": [
        r"\broutine\b", r"(?:day|night|morning|evening|am|pm) routine",
        r"layer(?:s|ed|ing)\b", r"(?:first|second|third|last) step",
        r"whole (?:range|line|set)", r"\bcombo\b",
        r"(?:after|with|under|over) (?:my )?(?:toner|serum|essence|moisturi[sz]er|sunscreen)",
    ],
    # What they came for — the concern, not the mechanism.
    "pigmentation_concern": [
        r"pigmentation", r"dark ?spots?", r"melasma", r"hyperpigmentation",
        r"tan(?:ning|ned)\b", r"uneven (?:skin ?)?tone", r"blemish\w*",
        r"acne ?marks?", r"dull(?:ness)?\b", r"scars?\b", r"patch(?:es|y)\b",
    ],
}

_DRIVER_RE = {name: re.compile("|".join(pats), re.I) for name, pats in DRIVERS.items()}

# Drivers whose polarity carries meaning. For the rest, "negated" is either
# vanishingly rare or semantically empty ("not Korean"), so the mention rate is
# the statistic and the split is reported only for audit.
POLARITY_MATTERS = {"efficacy_result", "price_worth", "price_resistance",
                    "climate_context"}


def resolve_origin(sku_name: str, declared_brand: str | None) -> tuple[str, str]:
    """The brand and manufacturer origin behind a SKU listing.

    Args:
        sku_name: The listing title as it appears on Nykaa.
        declared_brand: Phase 1's brand field, present for named-list brands only.

    Returns:
        (brand, origin) where origin is "KR", "IN", "other_foreign" or
        "unclassified". A SKU no rule matches returns ("<declared or Unknown>",
        "unclassified") — never a guessed origin.
    """
    haystack = sku_name.lower()
    for key, brand, origin in ORIGIN:
        if key.lower() in haystack:
            return brand, origin
    return (declared_brand or "Unknown"), "unclassified"


def classify_drivers(review: dict) -> dict[str, str]:
    """The purchase drivers a review invokes, with polarity.

    Args:
        review: A parsed review record; title and description are both scanned.

    Returns:
        {driver: "asserted" | "negated"}. As in Phase 2, a review that both
        asserts and negates the same driver resolves to "asserted".
    """
    text = f"{review.get('title') or ''}. {review.get('description') or ''}"
    out: dict[str, str] = {}
    for driver, rx in _DRIVER_RE.items():
        verdicts = {polarity(text, m.start(), m.end()) for m in rx.finditer(text)}
        if not verdicts:
            continue
        out[driver] = "asserted" if "asserted" in verdicts else "negated"
    return out


def flatten(payload: dict) -> list[dict]:
    """One row per review, carrying its SKU's origin, brand, format and price.

    Args:
        payload: The raw review sweep's parsed contents.

    Returns:
        Review rows with drivers classified. SKUs with no reviews contribute
        nothing.
    """
    rows: list[dict] = []
    for sku in payload["records"]:
        brand, origin = resolve_origin(sku["name"], sku.get("brand"))
        mrp = sku.get("mrp")
        for rv in sku.get("reviews") or []:
            text = f"{rv.get('title') or ''} {rv.get('description') or ''}".strip()
            rows.append({
                "product_id": sku["product_id"],
                "sku_name": sku["name"],
                "brand": brand,
                "origin": origin,
                "phase1_brand_group": sku["brand_group"],
                "format": sku["format"],
                "mrp": mrp,
                "mrp_band": _mrp_band(mrp),
                "rating": rv.get("rating"),
                "frame": rv.get("frame"),
                "tone_group": TONE_GROUPS.get(rv.get("skin_tone") or ""),
                "skin_type": rv.get("skin_type"),
                "is_verified_buyer": rv.get("is_verified_buyer"),
                "created_on": rv.get("created_on"),
                "word_count": len(text.split()),
                "drivers": classify_drivers(rv),
            })
    return rows


def _mrp_band(mrp: float | None) -> str | None:
    """Which third of the Rs1,500-3,000 band a SKU lists in."""
    if mrp is None:
        return None
    if mrp < 1500:
        return "below_band"
    if mrp < 2000:
        return "1500_1999"
    if mrp < 2500:
        return "2000_2499"
    if mrp <= 3000:
        return "2500_3000"
    return "above_band"


def _driver_stats(rows: list[dict]) -> dict:
    """Mention/asserted/negated counts and rates for every driver over `rows`."""
    n = len(rows)
    asserted: Counter = Counter()
    negated: Counter = Counter()
    for r in rows:
        for driver, pol in r["drivers"].items():
            (asserted if pol == "asserted" else negated)[driver] += 1
    out = {}
    for driver in DRIVERS:
        a, g = asserted[driver], negated[driver]
        out[driver] = {
            "asserted": a, "negated": g, "mentioned": a + g,
            "mentioned_pct": round((a + g) / n * 100, 1) if n else None,
            "asserted_pct": round(a / n * 100, 1) if n else None,
            "polarity_material": driver in POLARITY_MATTERS,
        }
    return {"n_reviews": n, "drivers": out}


def _split(rows: list[dict], key, min_n: int = 1) -> dict:
    """_driver_stats per value of `key`, largest bucket first."""
    buckets: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        value = key(r)
        if value is not None:
            buckets[str(value)].append(r)
    return {k: _driver_stats(v)
            for k, v in sorted(buckets.items(), key=lambda kv: -len(kv[1]))
            if len(v) >= min_n}


def origin_contrast(rows: list[dict]) -> dict:
    """The Q3 test: origin language by the SKU's own origin.

    Korean-provenance language in reviews of Korean SKUs measures how salient
    provenance is to the people who bought it. The SAME language in reviews of
    Indian and other-foreign SKUs measures whether Korea has become a category
    benchmark that belongs to no brand — the stronger of the two signals,
    because a reviewer of an Indian serum has no prompt to mention Korea at all.

    Args:
        rows: Flattened review rows (one frame at a time — do not pool).

    Returns:
        Per-origin mention rates for korea_origin, korean_aesthetic and
        other_origin, plus the actives:origin ratio.
    """
    out = {}
    for origin in ("KR", "IN", "other_foreign", "unclassified"):
        subset = [r for r in rows if r["origin"] == origin]
        if not subset:
            continue
        stats = _driver_stats(subset)["drivers"]
        korea = stats["korea_origin"]["mentioned"]
        actives = stats["ingredient_actives"]["mentioned"]
        out[origin] = {
            "n_reviews": len(subset),
            "korea_origin_mentions": korea,
            "korea_origin_pct": stats["korea_origin"]["mentioned_pct"],
            "korean_aesthetic_mentions": stats["korean_aesthetic"]["mentioned"],
            "korean_aesthetic_pct": stats["korean_aesthetic"]["mentioned_pct"],
            "other_origin_mentions": stats["other_origin"]["mentioned"],
            "other_origin_pct": stats["other_origin"]["mentioned_pct"],
            "ingredient_actives_pct": stats["ingredient_actives"]["mentioned_pct"],
            "actives_to_origin_ratio": (round(actives / korea, 1) if korea else None),
        }
    return out


def provenance_only(rows: list[dict]) -> dict:
    """How many origin-citing reviews cite ONLY origin — no active, no result.

    A reviewer who says "great Korean product" and nothing else is the pure
    provenance buyer the brand story would be built for. A reviewer who says
    "Korean niacinamide serum, spots faded in 6 weeks" is buying a mechanism and
    reporting where it came from. The split is the sharpest available read on
    whether provenance is load-bearing or descriptive.

    Args:
        rows: Flattened review rows.

    Returns:
        Counts and shares of origin-citing reviews with and without
        actives/efficacy language.
    """
    citing = [r for r in rows if "korea_origin" in r["drivers"]
              or "korean_aesthetic" in r["drivers"]]
    with_mech = [r for r in citing if {"ingredient_actives", "efficacy_result"}
                 & set(r["drivers"])]
    return {
        "n_reviews": len(rows),
        "origin_citing_reviews": len(citing),
        "origin_citing_pct_of_corpus": (
            round(len(citing) / len(rows) * 100, 1) if rows else None),
        "origin_plus_mechanism": len(with_mech),
        "origin_only": len(citing) - len(with_mech),
        "origin_only_pct_of_citing": (
            round((len(citing) - len(with_mech)) / len(citing) * 100, 1)
            if citing else None),
        "origin_only_pct_of_corpus": (
            round((len(citing) - len(with_mech)) / len(rows) * 100, 1)
            if rows else None),
    }


def driver_ranking(rows: list[dict]) -> list[dict]:
    """Drivers ordered by mention rate — the demand vocabulary, ranked.

    Args:
        rows: Flattened review rows (one frame).

    Returns:
        [{driver, mentioned, mentioned_pct}] descending. Ranks the language
        buyers use, not the strength of the underlying motive.
    """
    stats = _driver_stats(rows)
    ranked = sorted(
        ({"driver": k, "mentioned": v["mentioned"],
          "mentioned_pct": v["mentioned_pct"],
          "asserted": v["asserted"], "negated": v["negated"]}
         for k, v in stats["drivers"].items()),
        key=lambda d: -d["mentioned"])
    return ranked


def corpus_shape(rows: list[dict], payload: dict) -> dict:
    """Who the corpus is, so nobody reads it as a consumer sample.

    Reviews carry no income, city, age or channel field on Nykaa, which is
    exactly why the buyer-cohort half of Phase 3 has to be answered from
    disclosed platform data instead. What IS present: verified-buyer status,
    self-declared skin tone and type, review date and length.
    """
    origins = Counter(r["origin"] for r in rows)
    dated = [r["created_on"][:4] for r in rows if r.get("created_on")]
    return {
        "reviews": len(rows),
        "skus_targeted": len(payload["records"]),
        "skus_with_any_review": sum(1 for s in payload["records"] if s.get("reviews")),
        "by_origin": dict(origins),
        "by_frame": dict(Counter(r["frame"] for r in rows)),
        "by_year": dict(sorted(Counter(dated).items())),
        "verified_buyer_share_pct": (
            round(sum(1 for r in rows if r["is_verified_buyer"]) / len(rows) * 100, 1)
            if rows else None),
        "median_word_count": (
            sorted(r["word_count"] for r in rows)[len(rows) // 2] if rows else None),
        "reviews_with_declared_tone": sum(1 for r in rows if r["tone_group"]),
        "fields_absent_from_platform": [
            "income", "city", "state", "age", "channel", "purchase_price_paid"],
    }


# --- Q3(c): is the band being closed domestically? ---------------------------

# Phase 1 answered "no" for the brief's NAMED Indian D2C brands (Minimalist,
# Dot & Key, Foxtale, Pilgrim, Plum, Deconstruct, Earth Rhythm — ceilings
# Rs599-1,347, in-band only via combos). That leaves a different question open:
# what appears in-band when the shopper searches a CONCERN rather than a brand?
# The Phase 1 sweep supports it, because 36 of its 117 queries were
# format/concern terms ("pigmentation serum", "sunscreen spf 50") with no brand
# in them. Those queries are the brand-neutral window; the 81 brand queries are
# not, since the brand list was 45 Korean against 20 homegrown by design and any
# origin share computed over them would just be reading back the query set.
_MULTIPACK = re.compile(
    r"\b(?:combo|pack of|kit\b|set of|duo\b|trio\b|bundle|\d\s*[x×]\s*\d+\s*ml)",
    re.I)


def domestic_encroachment(price_payload: dict) -> dict:
    """Who lists in-band, by origin, when the query names no brand.

    Args:
        price_payload: A parsed data/raw/premium_skin_prices_*.json sweep.

    Returns:
        In-band SKU observations by origin, for brand-neutral queries and for
        the whole sweep, with price and discount medians. Counts are SKU
        OBSERVATIONS from a query-driven sweep, never a census of the band, and
        the whole-sweep numbers are a floor on each origin's presence rather
        than a share of it.
    """
    def _bucket(records: list[dict]) -> dict:
        by_origin: dict[str, list[dict]] = defaultdict(list)
        for rec in records:
            for prod in rec.get("products") or []:
                mrp, street = prod.get("mrp"), prod.get("street_price")
                if not mrp or prod.get("mrp_untrusted") or not 1500 <= mrp <= 3000:
                    continue
                if _MULTIPACK.search(prod.get("name") or ""):
                    continue
                brand, origin = resolve_origin(prod["name"], None)
                by_origin[origin].append({
                    "brand": brand, "name": prod["name"], "mrp": mrp,
                    "street_price": street,
                    "in_band_by_street": bool(street and 1500 <= street <= 3000),
                    "discount_pct": prod.get("discount_pct"),
                    "platform": rec["platform"], "query": rec["search_term"],
                })
        out = {}
        for origin, items in sorted(by_origin.items(), key=lambda kv: -len(kv[1])):
            mrps = sorted(i["mrp"] for i in items)
            held = sum(1 for i in items if i["in_band_by_street"])
            out[origin] = {
                "in_band_observations": len(items),
                "distinct_brands": sorted({i["brand"] for i in items}),
                "median_mrp": mrps[len(mrps) // 2],
                "held_band_by_street_price": held,
                "held_band_pct": round(held / len(items) * 100, 1),
                "examples": sorted(items, key=lambda i: -i["mrp"])[:6],
            }
        return out

    neutral = [r for r in price_payload["records"] if r["query_type"] != "brand"]
    return {
        "method": (
            "In-band-by-MRP (Rs1,500-3,000) single-unit SKU observations from the "
            "Phase 1 price sweep, multipacks and untrusted MRPs excluded, keyed to "
            "manufacturer origin. 'brand_neutral_queries' uses only the "
            "format/concern queries, which name no brand and are therefore the "
            "only part of the sweep whose origin composition means anything."),
        "brand_neutral_queries": {
            "n_queries": len(neutral),
            "query_terms": sorted({r["search_term"] for r in neutral}),
            "by_origin": _bucket(neutral),
        },
        "whole_sweep_floor": {
            "n_queries": len(price_payload["records"]),
            "note": ("Brand queries were 45 Korean / 20 homegrown / 16 other "
                     "foreign by design, so these counts are a FLOOR on each "
                     "origin's in-band presence, not a share of the band."),
            "by_origin": {k: {kk: vv for kk, vv in v.items() if kk != "examples"}
                          for k, v in _bucket(price_payload["records"]).items()},
        },
    }


def latest_prices(raw_dir: str | Path | None = None) -> Path | None:
    """The newest premium_skin_prices_*.json, or None if the sweep is absent."""
    directory = Path(raw_dir) if raw_dir else PROJECT_ROOT / "data" / "raw"
    files = sorted(directory.glob("premium_skin_prices_*.json"))
    return files[-1] if files else None


def analyse(payload: dict, price_payload: dict | None = None) -> dict:
    """Full Phase 3 demand-language analysis over one raw review sweep.

    Args:
        payload: The raw review sweep's parsed contents.
        price_payload: The Phase 1 price sweep, for the domestic-encroachment
            half of Q3. Omitted, that section is reported as absent rather than
            inferred.

    Returns:
        The artifact written to data/manual/analysis/premium_skin_demand.json.
    """
    rows = flatten(payload)
    useful = [r for r in rows if r["frame"] in ("most_useful", "both")]
    negative = [r for r in rows if r["frame"] in ("negative", "both")]

    return {
        "domestic_encroachment": (domestic_encroachment(price_payload)
                                  if price_payload else
                                  {"status": "NOT COMPUTED — no price sweep supplied"}),
        "corpus": corpus_shape(rows, payload),
        "origin_map": [{"brand": b, "origin": o} for _, b, o in ORIGIN],
        "most_useful_frame": {
            "note": ("Nykaa's default ordering, overwhelmingly 5-star. The frame "
                     "that answers Q3: what satisfied buyers volunteer."),
            "n_reviews": len(useful),
            "driver_ranking": driver_ranking(useful),
            "origin_contrast": origin_contrast(useful),
            "provenance_only": provenance_only(useful),
            "by_origin": _split(useful, lambda r: r["origin"], min_n=25),
            "by_format": _split(useful, lambda r: r["format"], min_n=25),
            "by_mrp_band": _split(useful, lambda r: r["mrp_band"], min_n=25),
            "by_brand": _split(useful, lambda r: r["brand"], min_n=40),
            "by_tone_group": _split(useful, lambda r: r["tone_group"], min_n=25),
        },
        "negative_frame": {
            "note": ("Every retrievable 1-2 star review. Read for what fails to "
                     "deliver on a driver, never pooled with the frame above."),
            "n_reviews": len(negative),
            "driver_ranking": driver_ranking(negative),
            "origin_contrast": origin_contrast(negative),
            "by_origin": _split(negative, lambda r: r["origin"], min_n=25),
        },
        "korean_sunscreen_most_useful": _driver_stats(
            [r for r in useful if r["origin"] == "KR" and r["format"] == "sunscreen"]),
        "pigmentation_serum_most_useful": _driver_stats(
            [r for r in useful if r["format"] == "serum_pigmentation_brightening"]),
    }


def to_data_points(analysis: dict, accessed: date, raw_file: str) -> list[DataPoint]:
    """Ledger the driver rates that carry the Phase 3 argument.

    Args:
        analysis: Output of analyse().
        accessed: Sweep date (the review corpus retrieval date).
        raw_file: The raw file holding every review and URL behind these numbers.

    Returns:
        DataPoints, all ESTIMATE: sample statistics over a deliberately
        non-random review corpus, never measured market facts.
    """
    points: list[DataPoint] = []
    method = (
        "Sample = Nykaa written reviews on Nykaa SKUs listing inside Rs1,500-3,000 "
        "MRP in the Phase 1 sweep (hero formats sunscreen and "
        "pigmentation/brightening serum, plus Korean moisturisers and "
        "toners/essences). Two frames, never pooled: every retrievable 1-2 star "
        "review ('negative'), and the first 3 pages of Nykaa's default 'most "
        "useful' ordering, which is overwhelmingly 5-star. Purchase-driver themes "
        "are regex-matched over title+description and polarity-checked against a "
        "negation window (shared with Phase 2), so 'not worth the money' is not "
        "counted as an endorsement. SKUs are re-keyed to manufacturer ORIGIN "
        "(analyst-assigned brand provenance, table in "
        "lib/transforms/premium_skin_demand.py), not to Phase 1's coverage "
        "groups. A review is the unit of observation: these are statistics about "
        "REVIEW LANGUAGE, not about buyers, and a mention rate measures the "
        "salience of a driver, never the share of purchases it caused. Every "
        "review and URL is in data/raw/" + raw_file + "."
    )

    def _ledger(value: float, seg: str, sub: str | None, kind: str,
                scope: str, n: int, extra: str) -> None:
        points.append(DataPoint(
            geography="IN", segment=seg, sub_segment=sub,
            metric="driver_share", value=float(value), unit="percent",
            currency="INR", period=str(accessed.year), period_type="CY",
            value_basis="NA",
            source_name="Nykaa review sweep (bpc-intel)", source_url=None,
            date_accessed=accessed, confidence="ESTIMATE", methodology=method,
            notes=(f"[PREMIUM-SKIN] {kind}: {scope}. n={n} reviews. {extra} "
                   f"ORGANISED online retail (Nykaa) only; offline deferred to "
                   f"Phase 4. A share of REVIEWS, not of buyers."),
        ))

    useful = analysis["most_useful_frame"]

    # 1. The origin contrast, per SKU origin. The Q3 headline.
    for origin, c in useful["origin_contrast"].items():
        if c["n_reviews"] < 50 or origin == "unclassified":
            continue
        _ledger(c["korea_origin_pct"], "skincare", None,
                "DRIVER MENTION RATE 'korean provenance'",
                f"positive-frame reviews of {origin}-origin in-band SKUs",
                c["n_reviews"],
                f"{c['korea_origin_mentions']} of {c['n_reviews']} reviews mention "
                f"Korea/K-beauty at all; actives language runs "
                f"{c['actives_to_origin_ratio']}x that rate "
                f"({c['ingredient_actives_pct']}% of reviews).")

    # 2. The ranked demand vocabulary, positive frame, whole corpus.
    n_useful = useful["n_reviews"]
    for row in useful["driver_ranking"]:
        if row["mentioned"] < 30:
            continue
        _ledger(row["mentioned_pct"], "skincare", None,
                f"DRIVER MENTION RATE '{row['driver']}'",
                "all positive-frame reviews of in-band SKUs", n_useful,
                f"{row['mentioned']} of {n_useful} reviews invoke it "
                f"({row['asserted']} asserted / {row['negated']} negated).")

    # 3. Provenance without mechanism — the pure-origin buyer.
    po = useful["provenance_only"]
    if po["origin_citing_reviews"] >= 30:
        _ledger(po["origin_only_pct_of_corpus"], "skincare", None,
                "DRIVER MENTION RATE 'korean provenance with no actives or "
                "result language'",
                "all positive-frame reviews of in-band SKUs", po["n_reviews"],
                f"{po['origin_only']} of {po['n_reviews']} reviews cite Korean "
                f"origin or the Korean aesthetic without naming an active or a "
                f"result; {po['origin_plus_mechanism']} cite origin alongside "
                f"one. Origin-citing reviews are {po['origin_citing_pct_of_corpus']}% "
                f"of the frame.")

    # 4. Korean sunscreen, the hero cell.
    ks = analysis["korean_sunscreen_most_useful"]
    if ks["n_reviews"] >= 50:
        for driver in ("korea_origin", "ingredient_actives", "climate_context",
                       "repurchase_loyalty"):
            v = ks["drivers"][driver]
            if v["mentioned"] < 10:
                continue
            _ledger(v["mentioned_pct"], "sun_care", "sun_protection",
                    f"DRIVER MENTION RATE '{driver}'",
                    "positive-frame reviews of Korean-origin in-band sunscreen",
                    ks["n_reviews"],
                    f"{v['mentioned']} of {ks['n_reviews']} reviews invoke it.")
    return points


def run(raw_path: str | Path | None = None, write: bool = True) -> dict:
    """Analyse the latest review sweep for demand language and write the artifact.

    Args:
        raw_path: A specific raw file; defaults to the newest sweep.
        write: Whether to write data/manual/analysis/premium_skin_demand.json.

    Returns:
        The analysis payload.
    """
    path = Path(raw_path) if raw_path else latest_raw()
    payload = json.loads(path.read_text(encoding="utf-8"))
    price_path = latest_prices()
    price_payload = (json.loads(price_path.read_text(encoding="utf-8"))
                     if price_path else None)
    analysis = analyse(payload, price_payload)
    analysis["generated_at"] = payload.get("fetched_at", "")
    analysis["source_raw_file"] = path.name
    analysis["source_price_file"] = price_path.name if price_path else None
    analysis["geography"] = "IN"
    analysis["question"] = (
        "Phase 3 / Q3 — is 'Korean' load-bearing for the Indian premium skincare "
        "buyer, or incidental? A positioning input, not a go/no-go.")
    analysis["scope"] = (
        "ONLINE ONLY (Nykaa written reviews on in-band SKUs). Organised retail "
        "only. Statistics describe REVIEW LANGUAGE, not buyers: Nykaa exposes no "
        "income, city, age or channel field, so the buyer-cohort half of Phase 3 "
        "is answered from disclosed platform and company data instead — see "
        "docs/premium-skincare-phase3.md and config/premium_skin_demand_findings.yaml.")
    if write:
        ANALYSIS_PATH.parent.mkdir(parents=True, exist_ok=True)
        ANALYSIS_PATH.write_text(
            json.dumps(analysis, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info("Wrote %s", ANALYSIS_PATH)
    return analysis


def main() -> None:
    """Analyse the latest sweep, write the artifact, and ledger the DataPoints."""
    from lib.transforms.merge import upsert_data_points

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    path = latest_raw()
    payload = json.loads(path.read_text(encoding="utf-8"))
    analysis = run(path)
    stamp = payload["fetched_at"]
    accessed = date.fromisoformat(f"{stamp[:4]}-{stamp[4:6]}-{stamp[6:8]}")
    points = to_data_points(analysis, accessed, path.name)
    summary = upsert_data_points(points)
    for fname, counts in summary.items():
        logger.info("%s: %s", fname, counts)
    contrast = analysis["most_useful_frame"]["origin_contrast"]
    for origin, c in contrast.items():
        logger.info("%s SKUs: %s%% of %d positive reviews mention Korea "
                    "(actives %sx)", origin, c["korea_origin_pct"],
                    c["n_reviews"], c["actives_to_origin_ratio"])


if __name__ == "__main__":
    main()


__all__ = ["run", "analyse", "flatten", "classify_drivers", "resolve_origin",
           "driver_ranking", "origin_contrast", "provenance_only", "corpus_shape",
           "to_data_points", "main", "DRIVERS", "ORIGIN", "POLARITY_MATTERS"]
