"""Does the Rs1,500-3,000 MRP band survive discounting online? — [PREMIUM-SKIN].

Curation pass over data/raw/premium_skin_prices_*.json (Phase 1 of
docs/premium-skincare-brief.md). The fetcher records list and street price for
the same SKU on the same date; this module turns that into the one number
Phase 1 exists to produce:

    of the SKUs that LIST inside Rs1,500-3,000, what share still TRANSACTS
    inside Rs1,500-3,000?

Definitions that matter, because the brief warns the vocabulary collides:

- **Band** is the literal MRP interval Rs1,500-3,000 inclusive, never the word
  "premium" (config/taxonomy.yaml's `premium` tier carries no MRP bounds and
  would swallow the Rs3,000+ luxury tier).
- **In-band by MRP** keys on the platform's list price. **In-band by street**
  keys on the price actually charged on the sweep date.
- SKUs listing ABOVE Rs3,000 that discount INTO the band are counted
  separately as `entrants_from_above` — they are competitors inside the band
  even though they are not "of" it.
- Kits, combos and discovery sets are excluded from band arithmetic: a
  Rs3,250 five-piece set is a basket, not a price point. They are counted and
  reported separately so the exclusion is visible.

Per-platform, never pooled: Nykaa and Tira disagree on the MRP of the same SKU
(Beauty of Joseon Relief Sun lists at Rs1,570 on Nykaa and Rs1,500 on Tira), so
pooling would average away a real finding. Amazon is street-price-only and is
excluded from band arithmetic entirely — its strike-through is seller-set.

Everything here is ONLINE. Per the brief, offline is deferred to Phase 4, and
online is the discount-heaviest channel in the market, so the verdict this
module supports is a channel verdict, not a verdict on the band as such.
"""
from __future__ import annotations

import json
import logging
import re
import statistics
from collections import Counter
from datetime import date
from pathlib import Path

from lib.transforms.schema import DataPoint

logger = logging.getLogger("bpc_intel.premium_skin_band")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
ANALYSIS_PATH = PROJECT_ROOT / "data" / "manual" / "analysis" / "premium_skin_band.json"

BAND_LOW, BAND_HIGH = 1500.0, 3000.0
CAST_WIDE_FLOOR = 1200.0   # brief: capture Rs1,200+, filter after
INR_PER_USD = 96.23        # config/exchange_rates.yaml, pinned 2026-07-21

# Brand attribution is deliberately strict: only the brands the brief names get
# a group. Anything else is recorded by name under "other_observed" rather than
# guessed at — asserting a brand's country of origin is a Phase 2/3 question and
# a price sweep is not evidence for it.
_BRAND_ALIASES: dict[str, tuple[str, str]] = {}


def _register(group: str, canonical: str, *aliases: str) -> None:
    """Register a brand and its match aliases under a group."""
    for alias in (canonical, *aliases):
        _BRAND_ALIASES[alias.lower()] = (canonical, group)


_register("korean", "Anua")
_register("korean", "Beauty of Joseon", "Beauty Of Joseon", "Beauty of Relief")
_register("korean", "COSRX")
_register("korean", "Innisfree")
_register("korean", "Laneige")
_register("korean", "Etude", "Etude House")
_register("korean", "Medicube")
_register("korean", "TirTir", "Tir Tir")
_register("korean", "Mixsoon")
_register("korean", "Hince")
_register("korean", "Dr. Melaxin", "Dr Melaxin", "Melaxin")
_register("korean", "Isntree")
_register("korean", "Some By Mi", "SomeByMi")
_register("korean", "Dr.Jart+", "Dr. Jart", "Dr Jart", "Dr.Jart")
_register("korean", "The Face Shop", "Thefaceshop")

_register("homegrown", "Minimalist")
_register("homegrown", "Dot & Key", "Dot and Key", "Dot&Key")
_register("homegrown", "Foxtale", "FoxTale")
_register("homegrown", "Pilgrim")
_register("homegrown", "Limese")
_register("homegrown", "Plum")
_register("homegrown", "Forest Essentials")
_register("homegrown", "Kama Ayurveda", "Kama")
_register("homegrown", "Deconstruct")
_register("homegrown", "Earth Rhythm")

_register("other_foreign", "Cetaphil")
_register("other_foreign", "La Roche-Posay", "La Roche Posay", "LaRoche-Posay")
_register("other_foreign", "The Ordinary")
_register("other_foreign", "Paula's Choice", "Paulas Choice", "Paula s Choice")
_register("other_foreign", "Clinique")
_register("other_foreign", "Kiehl's", "Kiehls", "Kiehl s")
_register("other_foreign", "Bioderma")
_register("other_foreign", "Sebamed")

# Scope lock. Broad relevance-ranked searches on a general beauty platform
# return the whole catalogue, not just skincare: the raw sweep surfaced hair
# straighteners, jewellery, sling bags, eyeglass frames, vanity boxes and
# lipsticks alongside serums. CLAUDE.md locks this system to BPC, and this
# thread to face skincare + sun care, so anything matching these patterns is
# dropped before any band arithmetic and counted under `out_of_scope`.
#
# Deliberately specific rather than broad: "body lotion" is excluded but "lotion"
# is not (Korean face lotions are emulsions), and "makeup remover" survives as a
# cleanser while "lipstick" does not.
_OUT_OF_SCOPE: list[tuple[str, re.Pattern]] = [
    ("accessories_apparel", re.compile(
        r"\b(bangle|earring|necklace|bracelet|pendant|jewellery|jewelry|ring\b|"
        r"hoop\b|sling bag|handbag|wallet|belt|scarf|sunglass|eyeglass|"
        r"frame only|watch|trousseau|vanity box|hair band|headband)\b", re.I)),
    ("appliance_device", re.compile(
        r"\b(straightener|hair dryer|blow dry|curler|trimmer|shaver|epilator|"
        r"massager|device|booster pro|age-r|led mask|steamer|brush set|"
        r"applicator|sponge|puff|tweezer|scissor|clipper)\b", re.I)),
    ("colour_cosmetics", re.compile(
        r"\b(lipstick|lip gloss|lip tint|lip crayon|lip liner|lip colou?r|"
        r"lip plumper|mascara|eyeliner|eye liner|liquid liner|kajal|"
        r"eyeshadow|eye shadow|foundation|concealer|compact|blush|highlighter|"
        r"bronzer|contour|setting spray|nail polish|nail paint|nail enamel|"
        r"cushion|bb cream|cc cream|tint\b)\b", re.I)),
    ("hair_care", re.compile(
        r"\b(shampoo|conditioner|hair oil|hair serum|hair mask|hair colou?r|"
        r"hair spa|scalp|dandruff|hair fall|hair growth|hair density|"
        r"for hair|lash and brow|lash & brow|lash serum|brow serum)\b", re.I)),
    ("body_bath", re.compile(
        r"\b(body lotion|body wash|body butter|body oil|body cream|body scrub|"
        r"body treatment|body cleanser|body cleansing|shower gel|shower oil|"
        r"bath salt|soap bar|hand wash|hand cream|foot cream|massage oil|"
        r"cold pressed|intimate)\b", re.I)),
    ("fragrance", re.compile(
        r"\b(perfume|eau de|edp|edt|body mist|deodorant|roll-on|attar)\b", re.I)),
    ("other_non_skincare", re.compile(
        r"\b(toothpaste|mouthwash|supplement|capsules?|tablets?|gummies|"
        r"effervescent|sanitary|condom|diaper|candle|diffuser)\b", re.I)),
]


def scope_exclusion(name: str) -> str | None:
    """Why a SKU falls outside face skincare / sun care, if it does.

    Args:
        name: Product title as listed.

    Returns:
        The exclusion reason key, or None when the SKU is in scope.
    """
    for reason, pattern in _OUT_OF_SCOPE:
        if pattern.search(name or ""):
            return reason
    return None


# Format classification. Order matters: bundles are caught before anything else
# so a "Sunscreen + Serum Duo" never lands in the sunscreen population, and
# eye/lip products are caught before the generic serum rule.
_FORMAT_RULES: list[tuple[str, re.Pattern]] = [
    ("bundle", re.compile(
        r"\b(kit|combo|set|duo|trio|bundle|regimen|routine|pack of|\d\s*pcs|"
        r"discovery|gift)\b", re.I)),
    ("eye_lip", re.compile(r"\b(eye|lip)\b", re.I)),
    ("sunscreen", re.compile(
        r"\b(sunscreen|sun\s*cream|sun\s*stick|sun\s*serum|sun\s*fluid|"
        r"sunblock|spf)\b|\bsun\s*:", re.I)),
    ("serum_pigmentation_brightening", re.compile(
        r"(serum|ampoule|essence|booster)(?=.*("
        r"bright|pigment|dark\s*spot|blemish|glow|radian|tone|vitamin\s*c|"
        r"niacinamide|arbutin|tranexamic|melasma|kojic|glutathione|whiten))"
        r"|((bright|pigment|dark\s*spot|blemish|glow|radian|tone|vitamin\s*c|"
        r"niacinamide|arbutin|tranexamic|melasma|kojic|glutathione)"
        r"(?=.*(serum|ampoule|essence|booster)))", re.I)),
    ("serum_other", re.compile(r"\b(serum|ampoule|booster)\b", re.I)),
    ("toner_essence", re.compile(r"\b(toner|essence|mist|softener)\b", re.I)),
    ("cleanser", re.compile(
        r"\b(cleanser|face\s*wash|cleansing|foam|micellar|makeup\s*remover)\b", re.I)),
    ("mask_exfoliant", re.compile(
        r"\b(mask|peel|scrub|exfoliat|pad(s)?)\b", re.I)),
    ("moisturiser", re.compile(
        r"\b(cream|moistur|lotion|emulsion|balm|gel)\b", re.I)),
]


# Format -> (segment, sub_segment) in config/taxonomy.yaml. Formats with no
# honest home in the taxonomy map to a bare segment rather than the nearest
# lookalike: "mask_exfoliant" covers peels, scrubs and toner pads, so filing it
# under `sheet_masks` would misstate what was measured. Sunscreen is its own
# segment (sun_care), not a skincare sub-segment.
_TAXONOMY_MAP: dict[str, tuple[str, str | None]] = {
    "sunscreen": ("sun_care", "sun_protection"),
    "serum_pigmentation_brightening": ("skincare", "serums_ampoules"),
    "serum_other": ("skincare", "serums_ampoules"),
    "toner_essence": ("skincare", "toners_essences"),
    "moisturiser": ("skincare", "facial_moisturisers"),
    "cleanser": ("skincare", "facial_cleansers"),
    "mask_exfoliant": ("skincare", None),
    "eye_lip": ("skincare", None),
    "other": ("skincare", None),
}


def classify_format(name: str) -> str:
    """The product format a SKU name describes.

    Args:
        name: Product title as listed.

    Returns:
        One of the `_FORMAT_RULES` keys, or "other" when nothing matches.
    """
    for label, pattern in _FORMAT_RULES:
        if pattern.search(name or ""):
            return label
    return "other"


def attribute_brand(name: str) -> tuple[str | None, str]:
    """Match a SKU name to a brief-named brand.

    Args:
        name: Product title as listed.

    Returns:
        (canonical_brand, group). Both fall back to (None, "other_observed")
        when the title matches no brand the brief names — origin is never
        inferred from a listing.
    """
    low = (name or "").lower()
    best: tuple[str, str] | None = None
    best_len = 0
    for alias, (canonical, group) in _BRAND_ALIASES.items():
        # Longest alias wins so "Dot & Key" beats a stray "key".
        if len(alias) > best_len and re.search(rf"(?<![a-z]){re.escape(alias)}", low):
            best, best_len = (canonical, group), len(alias)
    return best if best else (None, "other_observed")


def latest_raw(raw_dir: str | Path | None = None) -> Path:
    """The most recent premium_skin_prices raw file.

    Args:
        raw_dir: Directory of raw fetcher output.

    Returns:
        Path to the newest matching file.

    Raises:
        FileNotFoundError: If no sweep has been run.
    """
    raw_dir = Path(raw_dir) if raw_dir is not None else RAW_DIR
    files = sorted(raw_dir.glob("premium_skin_prices_*.json"))
    if not files:
        raise FileNotFoundError(
            f"No premium_skin_prices_*.json in {raw_dir}. "
            "Run: python -m lib.fetchers.premium_skin_prices")
    return files[-1]


def flatten(payload: dict) -> list[dict]:
    """Collapse the sweep's per-query records into one row per SKU per platform.

    A SKU surfaced by several queries (its brand page and a hero-format search)
    is one observation, not several, so rows are deduplicated on
    (platform, product URL). The query that found it is retained for
    traceability, and `found_via` accumulates every query that surfaced it.

    Args:
        payload: Parsed raw JSON from the fetcher.

    Returns:
        Deduplicated SKU observations with brand, group and format attached.
    """
    rows: dict[tuple[str, str], dict] = {}
    for rec in payload.get("records", []):
        if rec.get("error"):
            continue
        platform = rec["platform"]
        for p in rec.get("products", []):
            name = (p.get("name") or "").strip()
            url = p.get("url") or ""
            if not name or not url:
                continue
            key = (platform, url.split("?")[0])
            brand, group = attribute_brand(name)
            existing = rows.get(key)
            if existing:
                existing["found_via"].append(rec["search_term"])
                continue
            rows[key] = {
                "platform": platform,
                "name": name,
                "url": url,
                "brand": brand,
                "brand_group": group,
                "out_of_scope": scope_exclusion(name),
                "format": classify_format(name),
                "mrp": p.get("mrp"),
                "street_price": p.get("street_price"),
                "discount_pct": p.get("discount_pct"),
                "seller_list_price": p.get("seller_list_price"),
                "mrp_untrusted": p.get("mrp_untrusted", False),
                "sponsored": p.get("sponsored", False),
                "found_via": [rec["search_term"]],
                "found_via_url": rec.get("landed_url") or rec.get("url"),
            }
    return list(rows.values())


def _discount_depth(mrp: float, street: float) -> float:
    """Discount from list to street, as a percentage of list."""
    return round((mrp - street) / mrp * 100, 1)


# Pack sizes and filler words carry no identity, so they are dropped before
# comparing two platforms' titles for the same product.
_NOISE_TOKENS = frozenset({
    "ml", "g", "gm", "gms", "kg", "l", "oz", "pa", "spf", "the", "for", "with",
    "and", "of", "in", "a", "korean", "skin", "skincare", "face", "most",
    "loved", "new", "pack", "size", "ct",
})


# Leading words that are never a whole brand name on their own.
_MULTIWORD_PREFIXES = frozenset({
    "the", "dr", "dr.", "la", "round", "thank", "some", "beauty", "forest",
    "kama", "earth", "dot", "paula", "paula's", "skin", "axis", "estee",
    "st", "first", "good", "holika", "nature", "tony", "banila", "pure",
})

_SIZE_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(ml|g|gm|gms|l|oz)\b", re.I)


def pack_size(name: str) -> tuple[float, str] | None:
    """The pack size a product title declares, if any.

    Args:
        name: Product title as listed.

    Returns:
        (amount, unit) with unit lowercased and gm/gms normalised to g, or None
        when the title declares no size. Nykaa often omits it where Tira states
        it, so a None is common and must not be read as "sizes match".
    """
    m = _SIZE_RE.search(name or "")
    if not m:
        return None
    unit = m.group(2).lower()
    return float(m.group(1)), {"gm": "g", "gms": "g"}.get(unit, unit)


def _token_similarity(a: str, b: str) -> float:
    """Jaccard overlap of two product titles' meaningful tokens.

    Args:
        a: One product title.
        b: The other product title.

    Returns:
        Overlap in 0.0-1.0. 0.0 when either title has no meaningful tokens.
    """
    def toks(name: str) -> set[str]:
        raw = re.sub(r"[^a-z0-9]+", " ", (name or "").lower()).split()
        return {t for t in raw if t not in _NOISE_TOKENS and not t.isdigit()}

    ta, tb = toks(a), toks(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def _summarise(skus: list[dict]) -> dict:
    """Band-retention statistics for one population of SKUs.

    Args:
        skus: SKU rows carrying trustworthy `mrp` and `street_price`.

    Returns:
        Counts and shares for band membership, retention and discount depth.
        Shares are None (not zero) when the denominator is zero — an empty cell
        is information, a fabricated 0% is not.
    """
    in_band_mrp = [s for s in skus if BAND_LOW <= s["mrp"] <= BAND_HIGH]
    held = [s for s in in_band_mrp if BAND_LOW <= s["street_price"] <= BAND_HIGH]
    fell = [s for s in in_band_mrp if s["street_price"] < BAND_LOW]
    above = [s for s in skus if s["mrp"] > BAND_HIGH]
    entrants = [s for s in above if BAND_LOW <= s["street_price"] <= BAND_HIGH]
    depths = [_discount_depth(s["mrp"], s["street_price"]) for s in in_band_mrp]
    n = len(in_band_mrp)
    return {
        "skus_considered": len(skus),
        "in_band_by_mrp": n,
        "held_band_at_street": len(held),
        "fell_below_band": len(fell),
        "retention_pct": round(len(held) / n * 100, 1) if n else None,
        "collapse_pct": round(len(fell) / n * 100, 1) if n else None,
        "listed_above_band": len(above),
        "entrants_from_above": len(entrants),
        "in_band_street_population": len(held) + len(entrants),
        "discount_depth_pct": {
            "median": round(statistics.median(depths), 1) if depths else None,
            "mean": round(statistics.fmean(depths), 1) if depths else None,
            "max": max(depths) if depths else None,
            "zero_discount_skus": sum(1 for d in depths if d == 0),
            "zero_discount_pct": (round(sum(1 for d in depths if d == 0) / n * 100, 1)
                                  if n else None),
        },
    }


def analyse(rows: list[dict]) -> dict:
    """Compute the Phase 1 band verdict from flattened SKU observations.

    Args:
        rows: Output of flatten().

    Returns:
        The analysis payload: per-platform headline, group and format splits,
        the cross-platform MRP disagreements, and the excluded populations.
    """
    out_of_scope = [r for r in rows if r["out_of_scope"]]
    in_scope = [r for r in rows if not r["out_of_scope"]]
    bundles = [r for r in in_scope if r["format"] == "bundle"]
    amazon = [r for r in in_scope if r["platform"] == "amazon"]

    # Band arithmetic needs a trustworthy list price AND a street price.
    priced = [
        r for r in in_scope
        if not r["mrp_untrusted"] and r["format"] != "bundle"
        and isinstance(r.get("mrp"), (int, float))
        and isinstance(r.get("street_price"), (int, float))
        and r["mrp"] >= CAST_WIDE_FLOOR
    ]

    platforms = sorted({r["platform"] for r in priced})
    by_platform = {p: _summarise([r for r in priced if r["platform"] == p])
                   for p in platforms}
    by_group = {
        g: _summarise([r for r in priced if r["brand_group"] == g])
        for g in ("korean", "homegrown", "other_foreign", "other_observed")
    }
    hero_formats = ("sunscreen", "serum_pigmentation_brightening", "serum_other")
    by_format = {f: _summarise([r for r in priced if r["format"] == f])
                 for f in sorted({r["format"] for r in priced})}

    # Korean vs homegrown inside the hero formats — the brief's sharpest split.
    hero_group = {}
    for f in hero_formats:
        hero_group[f] = {
            g: _summarise([r for r in priced
                           if r["format"] == f and r["brand_group"] == g])
            for g in ("korean", "homegrown", "other_foreign")
        }

    # Same SKU, different platforms, different list price. Exact name matching
    # fails here — the platforms title the same product differently ("Relief
    # Sunscreen Rice + Probiotics" vs "Relief Sun : Rice + Probiotics ... Most
    # Loved Korean Sunscreen (50 ml)") — so pairs are matched on token overlap,
    # constrained to the same attributed brand, and the similarity score is kept
    # in the output so every pair stays auditable.
    nykaa = [r for r in priced if r["platform"] == "nykaa"]
    mrp_conflicts = []
    for r in priced:
        if r["platform"] != "tira" or not r["brand"]:
            continue
        best, best_score = None, 0.0
        for cand in nykaa:
            if cand["brand"] != r["brand"]:
                continue
            score = _token_similarity(r["name"], cand["name"])
            if score > best_score:
                best, best_score = cand, score
        if best and best_score >= 0.6 and best["mrp"] != r["mrp"]:
            # A price gap between two different pack sizes is not a disagreement
            # about MRP. Only pairs whose sizes are both stated AND equal count
            # as confirmed; the rest are kept but flagged, because Nykaa
            # frequently omits the size Tira states.
            size_t, size_n = pack_size(r["name"]), pack_size(best["name"])
            if size_t and size_n and size_t != size_n:
                continue
            mrp_conflicts.append({
                "match_similarity": round(best_score, 2),
                "brand": r["brand"],
                "size_verified": bool(size_t and size_n),
                "pack_size": f"{size_t[0]:g}{size_t[1]}" if size_t else None,
                "name_tira": r["name"], "name_nykaa": best["name"],
                "mrp_tira": r["mrp"], "mrp_nykaa": best["mrp"],
                "mrp_gap_inr": round(abs(best["mrp"] - r["mrp"]), 2),
                "street_tira": r["street_price"], "street_nykaa": best["street_price"],
                "url_tira": r["url"], "url_nykaa": best["url"],
            })
    mrp_conflicts.sort(key=lambda c: (not c["size_verified"], -c["mrp_gap_inr"]))

    in_band_skus = sorted(
        [r for r in priced if BAND_LOW <= r["mrp"] <= BAND_HIGH],
        key=lambda r: (-r["mrp"], r["name"]))

    # The brief names 33 brands; the band contains more. Counting the ones it
    # does not name is a Phase 1 answer to "who is already there", so they are
    # surfaced by leading-token guess — labelled a guess, and with no claim
    # about any of them being Korean, Indian or otherwise.
    unnamed: Counter = Counter()
    for r in in_band_skus:
        if r["brand"]:
            continue
        toks = (r["name"] or "").split()
        if not toks:
            continue
        lead = toks[0].strip(",").lower()
        n = 2 if (lead in _MULTIWORD_PREFIXES and len(toks) > 1) else 1
        unnamed[" ".join(toks[:n])] += 1

    return {
        "band": {"low_inr": BAND_LOW, "high_inr": BAND_HIGH,
                 "definition": "literal MRP interval, inclusive; not taxonomy 'premium'"},
        "headline_by_platform": by_platform,
        "by_brand_group": by_group,
        "by_format": by_format,
        "hero_formats_by_group": hero_group,
        "mrp_conflicts_across_platforms": mrp_conflicts,
        "mrp_conflicts_size_verified": [c for c in mrp_conflicts if c["size_verified"]],
        "excluded": {
            "out_of_scope_skus": len(out_of_scope),
            "out_of_scope_by_reason": {
                reason: sum(1 for r in out_of_scope if r["out_of_scope"] == reason)
                for reason in sorted({r["out_of_scope"] for r in out_of_scope})
            },
            "bundles_kits_sets": len(bundles),
            "amazon_rows_street_only": len(amazon),
            "note": ("Out-of-scope SKUs (makeup, hair, body, fragrance, "
                     "appliances, accessories) are dropped first: a general "
                     "beauty platform's search returns its whole catalogue, not "
                     "just skincare. Bundles are baskets, not price points. "
                     "Amazon carries no trustworthy MRP (seller-set "
                     "strike-through) so it is excluded from band arithmetic "
                     "and used only as a street-price cross-check."),
        },
        "in_band_brands_outside_named_set": [
            {"brand_guess": b, "in_band_sku_observations": n}
            for b, n in unnamed.most_common(40)
        ],
        "in_band_by_mrp_skus": in_band_skus,
        "all_priced_skus": priced,
    }


def to_data_points(analysis: dict, accessed: date, raw_file: str) -> list[DataPoint]:
    """Ledger the band-retention headline and the per-SKU in-band prices.

    Args:
        analysis: Output of analyse().
        accessed: Sweep date.
        raw_file: Name of the raw sweep file holding every URL fetched.

    Returns:
        DataPoints for data/processed/ and data/sources.csv. Retention shares
        are ESTIMATE-confidence (they are computed over a sample of
        relevance-ranked listing pages, not a catalogue census) and carry their
        methodology; individual SKU prices are HIGH (observed on the page).

        Aggregate rows carry NO source_url on purpose: they are computed over
        dozens of listing pages, so citing any single one of them would
        misattribute the statistic. The raw file named in the methodology holds
        the full URL list.
    """
    points: list[DataPoint] = []
    platform_names = {"nykaa": "Nykaa", "tira": "Tira", "amazon": "Amazon.in"}

    for platform, stats in analysis["headline_by_platform"].items():
        if not stats["in_band_by_mrp"]:
            continue
        base_note = (
            f"[PREMIUM-SKIN] {platform_names[platform]} online, sweep {accessed}. "
            f"Of {stats['in_band_by_mrp']} face-skincare SKUs LISTING inside "
            f"Rs1,500-3,000 MRP, {stats['held_band_at_street']} still transacted "
            f"inside the band and {stats['fell_below_band']} fell below Rs1,500. "
            f"ORGANISED retail only (single online platform). Kits/sets excluded. "
            f"ONLINE ONLY - the discount-heaviest channel; offline deferred to "
            f"Phase 4, so this is a channel finding, not a verdict on the band."
        )
        method = (
            "Sample = products returned on relevance-ranked brand and "
            "hero-format search/brand pages for the Phase 1 competitive set "
            "(33 named brands + 12 format queries), deduplicated by product "
            "URL, restricted to MRP >= Rs1,200, bundles and non-skincare "
            "(makeup/hair/body/fragrance/appliances) excluded. List and street "
            "price read from the same card on the same date. Not a catalogue "
            f"census, so the share is a sample statistic. Every URL fetched is "
            f"listed in data/raw/{raw_file}."
        )
        points.append(DataPoint(
            geography="IN", segment="skincare", metric="assortment_share",
            value=float(stats["retention_pct"]), unit="percent", currency="INR",
            period=str(accessed.year), period_type="CY", value_basis="MRP",
            source_name=f"{platform_names[platform]} listing sweep (bpc-intel)",
            source_url=None, date_accessed=accessed,
            confidence="ESTIMATE", methodology=method,
            notes=f"BAND RETENTION (share of in-band-MRP SKUs still in-band at street). {base_note}",
        ))
        median = stats["discount_depth_pct"]["median"]
        if median is not None:
            points.append(DataPoint(
                geography="IN", segment="skincare", metric="discount_depth",
                value=float(median), unit="percent", currency="INR",
                period=str(accessed.year), period_type="CY", value_basis="NA",
                source_name=f"{platform_names[platform]} listing sweep (bpc-intel)",
                source_url=None, date_accessed=accessed,
                confidence="ESTIMATE", methodology=method,
                notes=(f"MEDIAN DISCOUNT DEPTH off MRP on SKUs listing inside "
                       f"Rs1,500-3,000. This is a platform discount off list, "
                       f"NOT a trade margin to a distributor. {base_note}"),
            ))

    # Per-SKU prices: MRP and the street price actually charged.
    for sku in analysis["in_band_by_mrp_skus"]:
        seg, sub = _TAXONOMY_MAP.get(sku["format"], ("skincare", None))
        depth = _discount_depth(sku["mrp"], sku["street_price"])
        usd = round(sku["mrp"] / INR_PER_USD, 2)
        note = (
            f"[PREMIUM-SKIN] {sku['name']} - {platform_names[sku['platform']]}. "
            f"LIST Rs{sku['mrp']:.0f} (=US${usd} at 96.23 INR/USD pinned "
            f"2026-07-21); STREET Rs{sku['street_price']:.0f} on {accessed} "
            f"({depth}% off list). Brand group: {sku['brand_group']}"
            + (f" ({sku['brand']})" if sku["brand"] else "")
            + f". Format: {sku['format']}. ORGANISED online retail. "
            f"MRP embeds 25-45% trade margin (CLAUDE.md rule 10) - normalise "
            f"before reconciling against net realisation."
        )
        points.append(DataPoint(
            geography="IN", segment=seg, sub_segment=sub, metric="retail_price",
            value=float(sku["mrp"]), unit="inr", currency="INR",
            period=str(accessed.year), period_type="CY", value_basis="MRP",
            source_name=f"{platform_names[sku['platform']]} product listing",
            source_url=sku["url"], date_accessed=accessed, confidence="HIGH",
            notes=note,
        ))
    return points


def run(raw_path: str | Path | None = None, write: bool = True) -> dict:
    """Analyse the latest sweep and write the analysis artifact.

    Args:
        raw_path: A specific raw file; defaults to the newest sweep.
        write: Whether to write data/manual/analysis/premium_skin_band.json.

    Returns:
        The analysis payload.
    """
    path = Path(raw_path) if raw_path else latest_raw()
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = flatten(payload)
    analysis = analyse(rows)
    stamp = payload.get("fetched_at", "")
    analysis["generated_at"] = stamp
    analysis["source_raw_file"] = path.name
    analysis["geography"] = "IN"
    analysis["scope"] = (
        "ONLINE ONLY (Nykaa, Tira, Amazon.in). Offline/physical retail deferred "
        "to Phase 4 per docs/premium-skincare-brief.md. Organised retail only.")
    if write:
        ANALYSIS_PATH.parent.mkdir(parents=True, exist_ok=True)
        ANALYSIS_PATH.write_text(
            json.dumps(analysis, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info("Wrote %s", ANALYSIS_PATH)
    return analysis


def main() -> None:
    """Analyse the latest sweep, write the artifact, and ledger the DataPoints."""
    from lib.transforms.merge import upsert_data_points

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    path = latest_raw()
    payload = json.loads(path.read_text(encoding="utf-8"))
    analysis = run(path)

    accessed = date.fromisoformat(payload["fetched_at"][:4] + "-"
                                  + payload["fetched_at"][4:6] + "-"
                                  + payload["fetched_at"][6:8])
    points = to_data_points(analysis, accessed, path.name)
    summary = upsert_data_points(points)
    for fname, counts in summary.items():
        logger.info("%s: %s", fname, counts)
    for platform, stats in analysis["headline_by_platform"].items():
        logger.info("%s: %s/%s in-band SKUs held the band at street (%s%%)",
                    platform, stats["held_band_at_street"],
                    stats["in_band_by_mrp"], stats["retention_pct"])


__all__ = ["run", "analyse", "flatten", "to_data_points", "classify_format",
           "attribute_brand", "latest_raw", "main", "BAND_LOW", "BAND_HIGH"]


if __name__ == "__main__":
    main()
