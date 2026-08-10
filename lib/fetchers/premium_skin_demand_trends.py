"""Is "Korean" load-bearing? — comparative search demand, [PREMIUM-SKIN] Phase 3.

`lib/fetchers/trends_google.py` already tracks the corridor keywords, but it
fetches each one in its **own** payload. Google Trends normalises every payload
to its own maximum, so four separate 0-100 series are four separate scales:
"Korean skincare" peaking at 100 in its own series says nothing about whether
more or fewer Indians search it than search "niacinamide". That file's design is
correct for trend *shape* over time and useless for the Phase 3 question, which
is a question about **relative size**.

This module fixes exactly that. Keywords are grouped into baskets and every
basket is sent as a SINGLE payload, so within a basket the indices are directly
comparable. Cross-basket comparison is only valid through the shared anchor
keyword (`ANCHOR`), which appears in every basket: dividing by the anchor's mean
puts every basket on one approximate scale. Approximate, not exact — Trends
resamples and rounds per payload, and an anchor that saturates at 100 in one
basket compresses everything below it. Every ratio this produces is directional.

What is NOT claimed here:

- **Not volume.** The index is relative search interest, normalised, not counts.
- **Not demand.** People search for problems and ingredients, not for provenance
  they take for granted. A low "Korean skincare" index is evidence about the
  SEARCH TERM's salience, not proof that Korean origin does not sell product.
- **Not DataPoints.** Following `trends_google.to_data_points`, nothing here
  enters `data/sources.csv`: there is no defensible unit or value_basis for a
  normalised index. It is raw evidence for the written findings only.
"""
from __future__ import annotations

import logging
import time

from lib.fetchers._base import save_raw

logger = logging.getLogger("bpc_intel.fetchers.premium_skin_demand_trends")

_RATE_LIMIT_SECONDS = 12.0   # Trends 429s aggressively on back-to-back payloads
_RETRIES = 3

# The keyword every basket carries, so baskets can be chained onto one scale.
# "sunscreen" is chosen because it is the category's highest-volume generic in
# India, stable across seasons in aggregate, and — unlike a brand or an active —
# it cannot be argued to favour either side of the origin-vs-efficacy question.
ANCHOR = "sunscreen"

# Two timeframes, because the question has two halves: how big is the interest
# now (12-m), and is Korean provenance gaining or fading (5-y)?
TIMEFRAMES = ["today 12-m", "today 5-y"]

# Max 5 keywords per Trends payload, anchor included.
BASKETS: dict[str, dict] = {
    "origin_vs_mechanism": {
        "question": (
            "Does Indian search demand run on Korean provenance or on actives "
            "and clinical authority?"),
        "keywords": [ANCHOR, "korean skincare", "niacinamide", "vitamin c serum",
                     "dermatologist"],
        "regional": True,
    },
    "origin_terms": {
        "question": (
            "Which Korean-provenance term carries any weight at all, against "
            "the category generic?"),
        "keywords": [ANCHOR, "korean skincare", "k beauty", "korean sunscreen",
                     "glass skin"],
        "regional": True,
    },
    # The coarse baskets above all carry the "sunscreen" anchor, which peaks at
    # 100 every Indian summer and compresses every provenance term into an
    # integer 0-2 index. That is fine for establishing the order of magnitude
    # and useless for anything finer, so this basket drops the saturating anchor
    # and scales the provenance terms against a mid-volume ingredient instead.
    # Read it, not `origin_terms`, for the ranking WITHIN provenance language.
    "origin_terms_fine": {
        "question": (
            "Ranked against a mid-volume ingredient rather than the category "
            "generic: which provenance term actually carries weight?"),
        "keywords": ["niacinamide", "korean skincare", "k beauty", "glass skin",
                     "cosrx"],
        "regional": True,
    },
    "concerns": {
        "question": (
            "Which skin concern pulls hardest — the demand the range must "
            "answer to."),
        "keywords": [ANCHOR, "pigmentation", "dark spots", "melasma", "acne"],
        "regional": False,
    },
    "korean_vs_homegrown_brands": {
        "question": (
            "Do the Korean brands already in the band out-search the Indian "
            "D2C brands sitting a tier below it?"),
        "keywords": [ANCHOR, "cosrx", "beauty of joseon", "minimalist skincare",
                     "foxtale"],
        "regional": False,
    },
    "premium_intent": {
        "question": (
            "Is there search behaviour that reads as premium/derm intent rather "
            "than cheapest-option intent?"),
        "keywords": [ANCHOR, "korean skincare", "best sunscreen for indian skin",
                     "sunscreen for oily skin", "spf 50"],
        "regional": False,
    },
}

# Related-query pulls, run separately: these expose the language buyers attach
# to a term (does "korean sunscreen" co-occur with brands, with concerns, or
# with price?). Kept to the origin terms — that is where the Phase 3 question is.
RELATED_TERMS = ["korean skincare", "korean sunscreen", "k beauty"]

GEO = "IN"


def _client():
    """A pytrends session, or None if unavailable."""
    try:
        from pytrends.request import TrendReq
    except ImportError:
        logger.error("pytrends not installed — run: pip install pytrends")
        return None
    try:
        return TrendReq(hl="en-US", tz=0)
    except Exception as exc:  # noqa: BLE001 — pytrends raises raw exceptions
        logger.exception("pytrends session init failed: %s", exc)
        return None


def _payload(client, keywords: list[str], timeframe: str) -> bool:
    """Build one Trends payload, retrying through rate limits.

    Args:
        client: pytrends TrendReq.
        keywords: Up to 5 keywords, compared on one scale.
        timeframe: A Trends timeframe string.

    Returns:
        True if the payload was accepted.
    """
    for attempt in range(_RETRIES):
        try:
            client.build_payload(keywords, geo=GEO, timeframe=timeframe)
            return True
        except Exception as exc:  # noqa: BLE001
            wait = _RATE_LIMIT_SECONDS * (attempt + 2)
            logger.warning("payload failed (%s); retry in %.0fs", exc, wait)
            time.sleep(wait)
    return False


def _series(client, keywords: list[str]) -> dict:
    """Interest-over-time plus per-keyword means for the built payload."""
    iot = client.interest_over_time()
    if iot.empty:
        return {"interest_over_time": [], "means": {}}
    frame = iot.drop(columns=["isPartial"], errors="ignore")
    means = {k: round(float(frame[k].mean()), 2) for k in keywords if k in frame}
    # Direction: last quarter of the window against the first, per keyword. The
    # 5-y read of this is the "is Korean fading?" number.
    n = len(frame)
    quarter = max(1, n // 4)
    trend = {}
    for k in keywords:
        if k not in frame:
            continue
        first = float(frame[k].head(quarter).mean())
        last = float(frame[k].tail(quarter).mean())
        trend[k] = {
            "first_quarter_mean": round(first, 2),
            "last_quarter_mean": round(last, 2),
            "change_pct": round((last - first) / first * 100, 1) if first else None,
        }
    return {
        "interest_over_time": frame.reset_index().astype(str).to_dict("records"),
        "means": means,
        "direction": trend,
    }


def fetch(only: list[str] | None = None, related: bool = True) -> list[dict]:
    """Every basket x timeframe, plus regional and related-query pulls.

    Google rate-limits hard: a full run typically gets 3-4 payloads through
    before 429s set in, and the block persists for the rest of the session. So
    `only` exists to finish an interrupted sweep on a later run rather than
    re-requesting what already landed.

    Args:
        only: Basket names to fetch (default all). Unknown names are ignored.
        related: Whether to pull related queries after the baskets.

    Returns:
        Raw records; empty list if pytrends is unavailable or blocked
        throughout. Partial results are returned rather than discarded — a
        basket that 429s is recorded with an `error` key so the gap is visible
        in the raw file instead of silently absent.
    """
    client = _client()
    if client is None:
        return []

    selected = {k: v for k, v in BASKETS.items() if only is None or k in only}
    records: list[dict] = []
    first = True
    for name, basket in selected.items():
        for timeframe in TIMEFRAMES:
            if not first:
                time.sleep(_RATE_LIMIT_SECONDS)
            first = False
            rec = {
                "basket": name, "question": basket["question"],
                "keywords": basket["keywords"], "anchor": ANCHOR,
                "geo": GEO, "timeframe": timeframe,
                "comparable_within_payload": True,
            }
            if not _payload(client, basket["keywords"], timeframe):
                rec["error"] = "payload rejected after retries"
                records.append(rec)
                continue
            try:
                rec.update(_series(client, basket["keywords"]))
                if basket["regional"] and timeframe == "today 12-m":
                    region = client.interest_by_region(resolution="REGION")
                    if not region.empty:
                        rec["by_state"] = (region.sort_values(
                            basket["keywords"][1], ascending=False)
                            .head(15).reset_index().astype(str).to_dict("records"))
                logger.info("basket '%s' %s: %s", name, timeframe, rec.get("means"))
            except Exception as exc:  # noqa: BLE001
                rec["error"] = str(exc)
                logger.exception("basket '%s' %s failed", name, timeframe)
            records.append(rec)

    for term in (RELATED_TERMS if related else []):
        time.sleep(_RATE_LIMIT_SECONDS)
        rec = {"related_for": term, "geo": GEO, "timeframe": TIMEFRAMES[0]}
        if not _payload(client, [term], TIMEFRAMES[0]):
            rec["error"] = "payload rejected after retries"
            records.append(rec)
            continue
        try:
            rq = client.related_queries().get(term) or {}
            for key in ("top", "rising"):
                frame = rq.get(key)
                rec[key] = (frame.astype(str).to_dict("records")
                            if frame is not None and not frame.empty else [])
            logger.info("related '%s': %d top, %d rising",
                        term, len(rec.get("top") or []), len(rec.get("rising") or []))
        except Exception as exc:  # noqa: BLE001
            rec["error"] = str(exc)
            logger.exception("related_queries failed for '%s'", term)
        records.append(rec)

    return records


def to_data_points(raw_records: list[dict]) -> list:
    """A normalised index has no unit or value_basis — no DataPoints, by design.

    Args:
        raw_records: Records from fetch().

    Returns:
        Always [], matching lib/fetchers/trends_google.to_data_points.
    """
    logger.info("Trends indices are relative; %d records kept raw-only",
                len(raw_records))
    return []


def run(output_dir: str = "data/raw/", only: list[str] | None = None,
        related: bool = True) -> str:
    """Fetch the requested baskets and save raw. Returns the raw path, or ''."""
    records = fetch(only=only, related=related)
    if not records:
        return ""
    return str(save_raw("premium_skin_demand_trends", records, output_dir))


def main() -> None:
    """CLI: `python -m lib.fetchers.premium_skin_demand_trends [basket ...]`.

    Named baskets restrict the run (use it to retry what a 429 ate); with no
    arguments every basket and the related-query pulls are attempted.
    """
    import sys

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    only = sys.argv[1:] or None
    path = run(only=only, related=only is None)
    logger.info("Raw: %s", path or "NOTHING WRITTEN (pytrends blocked)")


if __name__ == "__main__":
    main()


__all__ = ["fetch", "to_data_points", "run", "main", "BASKETS", "ANCHOR",
           "TIMEFRAMES", "RELATED_TERMS"]
