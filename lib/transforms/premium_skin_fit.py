"""What do Indian buyers actually complain about? — [PREMIUM-SKIN] Phase 2.

Curation pass over data/raw/premium_skin_reviews_*.json. The brief
(docs/premium-skincare-brief.md, Phase 2) asks for "real problems" as a
first-class deliverable and is explicit about the standard: *count and
quantify — frequency by complaint type, by brand, by product format. Do not
cherry-pick quotes.* This module does the counting.

## The one thing that would break this analysis

Indian sunscreen reviews are saturated with the phrase "white cast" — and the
overwhelming majority of those mentions are **praise**: "no white cast", "zero
white cast", "doesn't leave a white cast". A keyword tally would report the
category's most reassured-about attribute as its most complained-about one and
invert the finding completely.

Every match is therefore polarity-checked against a negation window before it
is counted, and the two are reported separately:

- **asserted** — the review says the product HAS the problem.
- **negated** — the review says it does NOT ("no white cast", "never broke me
  out", "not greasy at all").

The negated count is not noise to be discarded. A theme that buyers keep
pre-emptively reassuring each other about is the category's dominant purchase
anxiety, which is a product-brief input in its own right, so both rates are
carried through to the output and to the ledger.

## Denominators, and why there is more than one

The corpus is deliberately NOT a random sample (see
lib/fetchers/premium_skin_reviews.py): it is every retrievable 1- and 2-star
review, plus the top pages of Nykaa's default "most useful" ordering, which is
almost entirely 5-star. Pooling those and dividing by the total would produce a
complaint rate that is an artefact of the sampling design. So:

- Rates are computed **within frame**, never across it.
- `negative` frame rates are the *composition* of complaints among unhappy
  buyers.
- `most_useful` frame rates are the rate at which a complaint survives into a
  review that is otherwise positive — the strongest evidence that a failure is
  real rather than a disgruntled-buyer artefact.
- A **population lower bound** is available where the rating distribution is
  known: share of written reviews that are 1-2 star (a census, from the API's
  own per-star counts) x complaint composition within them. It is a floor, not
  an estimate, because 3-5 star reviews also carry complaints; it is labelled
  as a floor everywhere it appears.

Nothing here is a statement about consumers. It is a statement about reviews.
"""
from __future__ import annotations

import json
import logging
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from lib.transforms.schema import DataPoint

logger = logging.getLogger("bpc_intel.premium_skin_fit")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
ANALYSIS_PATH = PROJECT_ROOT / "data" / "manual" / "analysis" / "premium_skin_fit.json"

# Nykaa's six-level self-declared tone ladder, grouped as the platform groups
# it. "Fair"/"Light" = fair tones, "Medium"/"Medium Dark" = wheatish,
# "Dark"/"Deep" = dusky. Kept as the platform's own vocabulary rather than
# mapped onto Fitzpatrick: these are self-reported marketing categories, not a
# clinical phototype, and pretending otherwise would launder them.
TONE_GROUPS: dict[str, str] = {
    "Fair": "fair", "Light": "fair",
    "Medium": "wheatish", "Medium Dark": "wheatish",
    "Dark": "dusky", "Deep": "dusky",
}

# Complaint themes. Patterns are deliberately narrow: a theme that fires on a
# generic word ("oily" — which is also a skin type, "oily skin") produces a
# number that means nothing. Where a word is ambiguous it is required to appear
# in a phrase that disambiguates it.
THEMES: dict[str, list[str]] = {
    "white_cast": [
        r"white ?cast", r"whitish cast", r"grey cast", r"gray cast",
        r"ashy", r"ash[iy] (?:look|finish|tint)", r"looks? white",
        r"makes? (?:me|my (?:face|skin)) look (?:white|pale|ghost)",
        r"ghost(?:ly)? (?:face|look)", r"white ?patch",
    ],
    "tone_mismatch": [
        r"too (?:light|fair|white) for (?:my|indian)", r"no shade for me",
        r"(?:doesn'?t|does not|didn'?t) (?:match|suit) my (?:skin ?)?tone",
        r"shade (?:range|match)", r"not (?:suitable |suited )?for (?:dusky|dark|brown|indian) skin",
        r"(?:dusky|deep|dark|wheatish|brown) skin ?tone", r"no (?:shade|colour|color) (?:option|range)",
    ],
    "breakout_acne": [
        r"broke (?:me |my skin )?out", r"break ?outs?", r"breaking out",
        r"purg(?:e|ing)", r"caused? (?:me )?(?:acne|pimples?|zits?)",
        r"(?:acne|pimples?|zits?|cystic) (?:after|since|because)",
        r"clogg?ed (?:my )?pores", r"comedogenic", r"whiteheads?", r"blackheads? (?:after|increased)",
    ],
    "heavy_greasy_humid": [
        r"greasy", r"too heavy", r"heavy on (?:my )?(?:skin|face)", r"sticky",
        r"tacky", r"oily (?:film|finish|residue|look|feel|mess)",
        r"makes? (?:my )?(?:face|skin) (?:oily|greasy|shiny)",
        r"(?:humid|humidity|summer|sweat)\w*", r"suffocating", r"occlusive",
        r"doesn'?t (?:absorb|sink in)", r"takes? (?:for)?ever to absorb",
    ],
    "pilling": [
        r"pill(?:s|ed|ing)\b", r"balls? up", r"rolls? off", r"roll(?:s|ed|ing) into",
        r"flakes? (?:off|under)", r"peel(?:s|ed|ing) off (?:my )?(?:skin|face)",
    ],
    "irritation": [
        r"burn(?:s|ed|ing|t)\b", r"sting(?:s|ing)", r"itch(?:y|ing|es)",
        r"rash(?:es)?", r"allerg(?:y|ic|ies)", r"irritat(?:e|ed|es|ing|ion)",
        r"red(?:ness)?\b", r"react(?:ed|ion) (?:on|to)", r"sensitive skin (?:issue|problem)",
        r"eyes? (?:burn|sting|water)",
    ],
    "no_efficacy_pigmentation": [
        r"no (?:visible )?(?:difference|change|result|effect)",
        r"(?:didn'?t|does ?n'?t|did not) work", r"(?:no|zero) (?:improvement|results?)",
        r"(?:dark ?spots?|pigmentation|melasma|tan(?:ning)?|blemish\w*|marks?) "
        r"(?:(?:are |is |still |have |has )?(?:still |not )?(?:there|same|unchanged|gone nowhere))",
        r"waste of (?:money|time)", r"no (?:brighten|lighten|fad)\w*",
    ],
    "fragrance": [
        r"(?:strong|bad|weird|awful|overpowering|unpleasant|artificial) (?:smell|scent|fragrance|odou?r)",
        r"smells? (?:bad|weird|awful|strange|like)", r"fragrance (?:is |was )?(?:strong|too much)",
        r"perfum(?:e|ed) (?:smell|scent)",
    ],
    "value_for_money": [
        r"(?:too |very |so )?(?:expensive|overpriced|pricey|costly)",
        r"not worth (?:the )?(?:money|price|it|hype)", r"waste of money",
        r"(?:quantity|amount) is (?:too )?(?:less|small|little)", r"tiny (?:bottle|tube|jar)",
    ],
    "authenticity": [
        r"\bfake\b", r"duplicate", r"counterfeit", r"not (?:the )?original",
        r"not genuine", r"different from (?:the )?(?:original|store)",
    ],
    "packaging": [
        r"leak(?:s|ed|ing|age)", r"(?:arrived|came|received) (?:damaged|broken|open)",
        r"(?:seal|cap|pump) (?:was )?(?:broken|missing|damaged)", r"spilled",
    ],
}

_THEME_RE = {name: re.compile("|".join(pats), re.I) for name, pats in THEMES.items()}

# Words that flip a match from "has this problem" to "does not have it",
# checked in a short window BEFORE it, plus the trailing "-free" construction
# ("white cast free"). Windowed rather than sentence-scoped because review prose
# carries almost no punctuation to scope on.
_NEG_WINDOW = 66
_NEGATION = re.compile(
    r"\b(?:no|not|non|never|without|zero|free (?:of|from)|"
    r"doesn'?t|does not|didn'?t|did not|won'?t|wasn'?t|isn'?t|"
    r"hasn'?t|haven'?t|avoids?|prevents?|nil)\b", re.I)
# A negation stops carrying at a sentence end OR at a contrastive conjunction:
# in "no white cast on my hand but it left a white cast on my face", the "no"
# governs the first mention only. Without this, the clause that reports the
# failure is scored as praise.
_NEG_BOUNDARY = re.compile(
    r"[.!?;]|\b(?:but|however|though|although|yet|except|unless|whereas)\b", re.I)
_TRAILING_NEG = re.compile(r"^[^.!?]{0,20}\b(?:free|-free)\b", re.I)


def polarity(text: str, start: int, end: int) -> str:
    """Whether a theme match at [start:end] is asserted or negated.

    "leaves no white cast" and "white cast free" are the product NOT having the
    problem; "slight white cast" is it having one. Getting this backwards would
    invert the headline, so the window is checked on both sides and truncated
    at the nearest clause boundary.

    Args:
        text: The full review text.
        start: Match start offset.
        end: Match end offset.

    Returns:
        "negated" or "asserted".
    """
    window = text[max(0, start - _NEG_WINDOW):start]
    boundaries = list(_NEG_BOUNDARY.finditer(window))
    if boundaries:
        window = window[boundaries[-1].end():]
    if _NEGATION.search(window):
        return "negated"
    if _TRAILING_NEG.match(text[end:end + 24]):
        return "negated"
    return "asserted"


def classify(review: dict) -> dict[str, str]:
    """The themes a review raises, and whether each is asserted or negated.

    Args:
        review: A parsed review record (title + description are both scanned).

    Returns:
        {theme: "asserted" | "negated"}. A review that both asserts and negates
        the same theme ("no white cast on me but my sister got one") resolves to
        "asserted": the failure was reported, and under-counting a real
        complaint is the worse error for a product brief.
    """
    text = f"{review.get('title') or ''}. {review.get('description') or ''}"
    out: dict[str, str] = {}
    for theme, rx in _THEME_RE.items():
        verdicts = {polarity(text, m.start(), m.end()) for m in rx.finditer(text)}
        if not verdicts:
            continue
        out[theme] = "asserted" if "asserted" in verdicts else "negated"
    return out


def latest_raw(raw_dir: str | Path | None = None) -> Path:
    """The newest premium_skin_reviews_*.json in data/raw/."""
    directory = Path(raw_dir) if raw_dir else RAW_DIR
    files = sorted(directory.glob("premium_skin_reviews_*.json"))
    if not files:
        raise FileNotFoundError(
            f"No premium_skin_reviews_*.json in {directory}. Run "
            "`python -m lib.fetchers.premium_skin_reviews` first.")
    return files[-1]


def flatten(payload: dict) -> list[dict]:
    """One row per review, carrying its SKU's attributes.

    Args:
        payload: The raw file's parsed contents.

    Returns:
        Review rows with brand, brand_group, format, mrp and frame attached,
        each classified into themes. SKUs with no reviews contribute nothing.
    """
    rows: list[dict] = []
    for sku in payload["records"]:
        for rv in sku.get("reviews") or []:
            themes = classify(rv)
            rows.append({
                "product_id": sku["product_id"],
                "sku_name": sku["name"],
                "brand": sku.get("brand"),
                "brand_group": sku["brand_group"],
                "format": sku["format"],
                "mrp": sku.get("mrp"),
                "review_url": sku.get("review_url"),
                "rating": rv.get("rating"),
                "frame": rv.get("frame"),
                "skin_tone": rv.get("skin_tone"),
                "tone_group": TONE_GROUPS.get(rv.get("skin_tone") or ""),
                "skin_type": rv.get("skin_type"),
                "is_verified_buyer": rv.get("is_verified_buyer"),
                "created_on": rv.get("created_on"),
                "themes": themes,
            })
    return rows


def _theme_stats(rows: list[dict]) -> dict:
    """Asserted/negated counts and rates for every theme over `rows`."""
    n = len(rows)
    asserted: Counter = Counter()
    negated: Counter = Counter()
    for r in rows:
        for theme, pol in r["themes"].items():
            (asserted if pol == "asserted" else negated)[theme] += 1
    out = {}
    for theme in THEMES:
        a, g = asserted[theme], negated[theme]
        out[theme] = {
            "asserted": a,
            "negated": g,
            "mentioned": a + g,
            "asserted_pct": round(a / n * 100, 1) if n else None,
            "negated_pct": round(g / n * 100, 1) if n else None,
            "mentioned_pct": round((a + g) / n * 100, 1) if n else None,
        }
    return {"n_reviews": n, "themes": out}


def _split(rows: list[dict], key) -> dict:
    """_theme_stats for each value of `key`, sorted by sample size."""
    buckets: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        value = key(r)
        if value is not None:
            buckets[str(value)].append(r)
    return {k: _theme_stats(v)
            for k, v in sorted(buckets.items(), key=lambda kv: -len(kv[1]))}


def rating_distribution(payload: dict) -> dict:
    """Written-review rating distribution, by brand group and by format.

    Unlike the theme counts, this IS a census: the API reports the total number
    of written reviews at each star level for a SKU, not a sample of them. It
    is what makes a population floor computable.

    Args:
        payload: The raw file's parsed contents.

    Returns:
        Overall and per-split totals with the 1-2 star share.
    """
    def blank():
        return {str(i): 0 for i in range(1, 6)}

    overall, by_group, by_format = blank(), defaultdict(blank), defaultdict(blank)
    skus_counted = 0
    for sku in payload["records"]:
        dist = sku.get("rating_distribution") or {}
        if not any(dist.get(str(i)) for i in range(1, 6)):
            continue
        skus_counted += 1
        for star in range(1, 6):
            v = dist.get(str(star)) or 0
            overall[str(star)] += v
            by_group[sku["brand_group"]][str(star)] += v
            by_format[sku["format"]][str(star)] += v

    def summarise(d):
        total = sum(d.values())
        neg = d["1"] + d["2"]
        return {"counts": dict(d), "written_reviews": total,
                "negative_1_2_star": neg,
                "negative_share_pct": round(neg / total * 100, 1) if total else None}

    return {
        "skus_with_reviews": skus_counted,
        "overall": summarise(overall),
        "by_brand_group": {k: summarise(v) for k, v in by_group.items()},
        "by_format": {k: summarise(v) for k, v in by_format.items()},
    }


def population_floor(negative_share_pct: float | None,
                     asserted_pct_in_negatives: float | None) -> float | None:
    """A floor on how often a theme appears across ALL written reviews.

    Only 1- and 2-star reviews were sampled exhaustively, so the product of the
    negative share and the theme's rate within negatives is the contribution
    from unhappy reviews alone. Reviews at 3-5 stars raise complaints too and
    are not counted here, which is exactly why this is a floor and never an
    estimate.

    Args:
        negative_share_pct: Share of written reviews rated 1-2 star.
        asserted_pct_in_negatives: Theme's asserted rate within 1-2 star reviews.

    Returns:
        The floor as a percentage, or None if either input is missing.
    """
    if negative_share_pct is None or asserted_pct_in_negatives is None:
        return None
    return round(negative_share_pct * asserted_pct_in_negatives / 100, 2)


def analyse(payload: dict) -> dict:
    """Full Phase 2 complaint analysis over one raw review sweep.

    Args:
        payload: The raw file's parsed contents.

    Returns:
        The analysis artifact written to
        data/manual/analysis/premium_skin_fit.json.
    """
    rows = flatten(payload)
    negative = [r for r in rows if r["frame"] in ("negative", "both")]
    useful = [r for r in rows if r["frame"] in ("most_useful", "both")]
    dist = rating_distribution(payload)

    coverage = {
        "skus_targeted": len(payload["records"]),
        "skus_with_any_review": sum(1 for s in payload["records"] if s.get("reviews")),
        "skus_with_zero_reviews": sum(1 for s in payload["records"]
                                      if not s.get("reviews")),
        "skus_errored": sum(1 for s in payload["records"] if s.get("error")),
        "reviews_analysed": len(rows),
        "reviews_negative_frame": len(negative),
        "reviews_most_useful_frame": len(useful),
        "reviews_with_declared_skin_tone": sum(1 for r in rows if r["tone_group"]),
        "reviews_with_declared_skin_type": sum(1 for r in rows if r["skin_type"]),
        "verified_buyer_share_pct": (
            round(sum(1 for r in rows if r["is_verified_buyer"]) / len(rows) * 100, 1)
            if rows else None),
    }

    # The headline table: theme rates inside negative reviews, by brand group,
    # with the population floor attached.
    floors: dict[str, dict] = {}
    for group, stats in dist["by_brand_group"].items():
        grp_neg = [r for r in negative if r["brand_group"] == group]
        if not grp_neg:
            continue
        grp_stats = _theme_stats(grp_neg)
        floors[group] = {
            "negative_share_of_written_reviews_pct": stats["negative_share_pct"],
            "n_negative_reviews_analysed": grp_stats["n_reviews"],
            "themes": {
                theme: {
                    "asserted_pct_within_negatives": v["asserted_pct"],
                    "population_floor_pct": population_floor(
                        stats["negative_share_pct"], v["asserted_pct"]),
                }
                for theme, v in grp_stats["themes"].items() if v["asserted"]
            },
        }

    return {
        "coverage": coverage,
        "rating_distribution": dist,
        "negative_frame": {
            "overall": _theme_stats(negative),
            "by_brand_group": _split(negative, lambda r: r["brand_group"]),
            "by_format": _split(negative, lambda r: r["format"]),
            "by_brand": {k: v for k, v in
                         _split(negative, lambda r: r["brand"]).items()
                         if v["n_reviews"] >= 10},
            "by_tone_group": _split(negative, lambda r: r["tone_group"]),
            "by_skin_type": _split(negative, lambda r: r["skin_type"]),
        },
        "most_useful_frame": {
            "overall": _theme_stats(useful),
            "by_brand_group": _split(useful, lambda r: r["brand_group"]),
            "by_format": _split(useful, lambda r: r["format"]),
            "by_tone_group": _split(useful, lambda r: r["tone_group"]),
        },
        "population_floors_by_brand_group": floors,
        "korean_sunscreen": _theme_stats(
            [r for r in rows if r["brand_group"] == "korean"
             and r["format"] == "sunscreen"]),
        "korean_sunscreen_negative": _theme_stats(
            [r for r in negative if r["brand_group"] == "korean"
             and r["format"] == "sunscreen"]),
        "pigmentation_serum_negative": _theme_stats(
            [r for r in negative
             if r["format"] == "serum_pigmentation_brightening"]),
        "tone_declaration_by_group": {
            k: dict(Counter(r["tone_group"] or "undeclared" for r in rows
                            if r["brand_group"] == k))
            for k in {r["brand_group"] for r in rows}
        },
    }


def to_data_points(analysis: dict, accessed: date, raw_file: str) -> list[DataPoint]:
    """Ledger the complaint rates that carry the Phase 2 argument.

    Only themes with a material asserted count are ledgered — a rate computed
    over two reviews is not a finding, and filing it as one would put noise in
    front of an entry decision.

    Args:
        analysis: Output of analyse().
        accessed: Sweep date.
        raw_file: Raw file holding every review and URL behind these numbers.

    Returns:
        DataPoints for data/processed/ and data/sources.csv, all ESTIMATE
        confidence with methodology attached: these are sample statistics over
        a deliberately non-random review corpus, not measured market facts.
    """
    points: list[DataPoint] = []
    method_base = (
        "Sample = Nykaa written reviews for Nykaa SKUs listing inside "
        "Rs1,500-3,000 MRP in the Phase 1 sweep, restricted to the two hero "
        "formats (sunscreen, pigmentation/brightening serum) plus Korean "
        "moisturisers and toners/essences. Two frames, never pooled: every "
        "retrievable 1- and 2-star review ('negative'), and the first 3 pages "
        "of Nykaa's default 'most useful' ordering, which is overwhelmingly "
        "5-star. Themes are regex-matched then polarity-checked against a "
        "negation window, so 'no white cast' counts as NEGATED (the product "
        "lacks the problem) and never as a complaint. A review is the unit of "
        "observation: these are statistics about REVIEWS, not about users or "
        "buyers. Every review and URL is in data/raw/" + raw_file + "."
    )

    def _ledger(theme: str, value: float, seg: str, sub: str | None,
                kind: str, scope: str, n: int, extra: str) -> None:
        points.append(DataPoint(
            geography="IN", segment=seg, sub_segment=sub,
            metric="complaint_share", value=float(value), unit="percent",
            currency="INR", period=str(accessed.year), period_type="CY",
            value_basis="NA",
            source_name="Nykaa review sweep (bpc-intel)", source_url=None,
            date_accessed=accessed, confidence="ESTIMATE",
            methodology=method_base,
            notes=(f"[PREMIUM-SKIN] {kind}: '{theme}' — {scope}. n={n} reviews. "
                   f"{extra} ORGANISED online retail (Nykaa) only; offline "
                   f"deferred to Phase 4. A share of REVIEWS, not of users."),
        ))

    # 1. Composition within negative reviews, by brand group.
    for group, stats in analysis["negative_frame"]["by_brand_group"].items():
        n = stats["n_reviews"]
        if n < 30:
            continue
        for theme, v in stats["themes"].items():
            if v["asserted"] < 5:
                continue
            _ledger(theme, v["asserted_pct"], "skincare", None,
                    "COMPLAINT COMPOSITION IN 1-2 STAR REVIEWS",
                    f"brand group '{group}', all covered formats", n,
                    f"{v['asserted']} of {n} negative reviews assert it. "
                    f"Composition within unhappy buyers, NOT a prevalence rate "
                    f"across all buyers.")

    # 2. Korean sunscreen, the hero cell the brief cares most about.
    ks = analysis["korean_sunscreen_negative"]
    for theme, v in ks["themes"].items():
        if v["asserted"] >= 5:
            _ledger(theme, v["asserted_pct"], "sun_care", "sun_protection",
                    "COMPLAINT COMPOSITION IN 1-2 STAR REVIEWS",
                    "Korean sunscreen SKUs in the Rs1,500-3,000 band",
                    ks["n_reviews"],
                    f"{v['asserted']} of {ks['n_reviews']} negative reviews "
                    f"assert it.")

    # 3. The reassurance signal: how often POSITIVE reviews pre-empt a theme.
    ku = analysis["korean_sunscreen"]["themes"].get("white_cast") or {}
    if (ku.get("mentioned") or 0) >= 20:
        _ledger("white_cast", ku["mentioned_pct"], "sun_care", "sun_protection",
                "THEME MENTION RATE (asserted + negated)",
                "all sampled reviews of Korean sunscreen SKUs in the band",
                analysis["korean_sunscreen"]["n_reviews"],
                f"{ku['mentioned']} reviews mention white cast at all; "
                f"{ku['negated']} of them say the product does NOT leave one "
                f"and {ku['asserted']} say it does. Read as purchase-anxiety "
                f"salience, not as a defect rate.")

    # 4. Negative-review share of written reviews — a census, not a sample.
    for group, stats in analysis["rating_distribution"]["by_brand_group"].items():
        if (stats["written_reviews"] or 0) < 200 or stats["negative_share_pct"] is None:
            continue
        points.append(DataPoint(
            geography="IN", segment="skincare", metric="complaint_share",
            value=float(stats["negative_share_pct"]), unit="percent",
            currency="INR", period=str(accessed.year), period_type="CY",
            value_basis="NA",
            source_name="Nykaa review sweep (bpc-intel)", source_url=None,
            date_accessed=accessed, confidence="ESTIMATE",
            methodology=(
                "Census of WRITTEN reviews (not ratings) on the sampled SKUs: "
                "Nykaa reports a total review count per star level per product "
                "and these are summed across the brand group's SKUs. The SKU "
                "set is a sample (Phase 1 in-band hero-format SKUs); the star "
                "split within it is not. Star-level counts exclude "
                "rating-only entries with no written review. Raw: data/raw/"
                + raw_file + "."),
            notes=(f"[PREMIUM-SKIN] NEGATIVE-REVIEW SHARE: {stats['negative_1_2_star']} "
                   f"of {stats['written_reviews']} written reviews on "
                   f"'{group}' in-band SKUs are 1-2 star. ORGANISED online "
                   f"retail (Nykaa) only. A share of REVIEWS, not of users."),
        ))
    return points


def run(raw_path: str | Path | None = None, write: bool = True) -> dict:
    """Analyse the latest review sweep and write the analysis artifact.

    Args:
        raw_path: A specific raw file; defaults to the newest sweep.
        write: Whether to write data/manual/analysis/premium_skin_fit.json.

    Returns:
        The analysis payload.
    """
    path = Path(raw_path) if raw_path else latest_raw()
    payload = json.loads(path.read_text(encoding="utf-8"))
    analysis = analyse(payload)
    analysis["generated_at"] = payload.get("fetched_at", "")
    analysis["source_raw_file"] = path.name
    analysis["geography"] = "IN"
    analysis["scope"] = (
        "ONLINE ONLY (Nykaa written reviews). Tira exposes no review API and "
        "Amazon.in gates review pagination behind a login, so neither is "
        "sampled — see docs/premium-skincare-phase2.md for what that leaves "
        "unanswered. Organised retail only. Statistics describe REVIEWS, not "
        "users or buyers.")
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
    cov = analysis["coverage"]
    logger.info("%d reviews across %d SKUs (%d negative, %d most-useful); "
                "%d carry a declared skin tone",
                cov["reviews_analysed"], cov["skus_with_any_review"],
                cov["reviews_negative_frame"], cov["reviews_most_useful_frame"],
                cov["reviews_with_declared_skin_tone"])


if __name__ == "__main__":
    main()


__all__ = ["run", "analyse", "flatten", "classify", "polarity",
           "rating_distribution", "population_floor", "to_data_points",
           "latest_raw", "main", "THEMES", "TONE_GROUPS"]
