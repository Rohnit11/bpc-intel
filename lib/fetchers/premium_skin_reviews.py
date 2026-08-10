"""India online skincare review mining for the Rs1,500-3,000 band — [PREMIUM-SKIN].

Phase 2 of docs/premium-skincare-brief.md asks whether Korean formulations
actually suit Indian skin, and demands that "real problems" be *counted*, not
quoted: frequency by complaint type, by brand, by product format. This fetcher
supplies the corpus.

**Source: Nykaa's own review API**, reached from inside a rendered nykaa.com
page. `https://www.nykaa.com/gateway-api/products/{id}/reviews` returns the
full review record the page then truncates in the DOM behind a "...Read More"
string — rating, title, untruncated body, creation date, verified-buyer flag,
helpful count, and (on roughly 4 in 10 reviews) the reviewer's **self-declared
skin tone and skin type** from their Nykaa beauty profile.

That skin-tone field is why this fetcher exists at all. The brief records that
the repo has *zero* skin-tone data and calls it genuinely greenfield; Nykaa's
six-level tone ladder (Fair / Light / Medium / Medium Dark / Dark / Deep,
grouped fair / wheatish / dusky) attached to a review of a specific SKU is the
one place online where an Indian consumer's tone and their verdict on a Korean
product sit in the same record.

Three sampling frames per SKU, kept separate because they answer different
questions and must never be pooled:

- **rating_distribution** — `reviewCount` under each STAR_n filter. The count of
  *written* reviews at each star level. Cheap (5 calls) and it is the
  denominator that turns a complaint tally into a complaint rate.
- **negative corpus** (`filters=STAR_1` / `STAR_2`) — every retrievable 1- and
  2-star review. This is the complaint corpus: what buyers say when they are
  unhappy. Composition *within* negatives, never a prevalence rate.
- **most-useful corpus** (`filters=DEFAULT`) — Nykaa's default ordering, which
  is overwhelmingly 5-star. Useless as a representative sample and not treated
  as one; it is here because a complaint that surfaces inside a *five-star*
  review ("love it, but slight white cast") is the strongest available evidence
  that the failure is real rather than a disgruntled-buyer artefact.

Two honesty constraints are enforced in the record itself:

1. `reviewCount` under a star filter regularly exceeds the rows the API will
   actually serve (a 1-star filter claiming 50 yields 28). Both numbers are
   recorded — `claimed` and `retrieved` — and the transform must use
   `retrieved` as its denominator for anything it counts and `claimed` only
   for the rating distribution.
2. A plain HTTP GET of the API returns 403 (Akamai). Every call is issued from
   a live nykaa.com page context, one page load per run, rate-limited.

Nykaa only. Tira exposes no comparable endpoint and Amazon.in gates review
pagination behind a login; both are recorded as coverage gaps in the Phase 2
write-up rather than half-sampled.

Requires Playwright + locally-installed Chrome (bundled Chromium is refused —
see lib/fetchers/premium_skin_prices.py for the same constraint):
    pip install playwright && python -m playwright install chromium
"""
from __future__ import annotations

import json
import logging
import re
import time
from pathlib import Path

from lib.fetchers._base import save_raw

logger = logging.getLogger("bpc_intel.fetchers.premium_skin_reviews")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BAND_PATH = PROJECT_ROOT / "data" / "manual" / "analysis" / "premium_skin_band.json"

_RATE_LIMIT_SECONDS = 1.1
_PAGE_TIMEOUT_MS = 45000

_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
_CHROME_CHANNEL = "chrome"
_CHROMIUM_ARGS = ["--disable-blink-features=AutomationControlled"]

# Any nykaa.com page works as a fetch origin; a category page is lighter than a
# PDP and does not bias the session toward one product.
_ORIGIN_PAGE = "https://www.nykaa.com/skin/c/8377"

# The hero formats the brief weights depth toward, plus the Korean formats where
# the climate/occlusivity failure mode would show up if it is real.
HERO_FORMATS = ("sunscreen", "serum_pigmentation_brightening")
CLIMATE_FORMATS = ("moisturiser", "toner_essence")

_MAX_NEGATIVE_PAGES = 6      # 1- and 2-star each; ~120 reviews per SKU ceiling
_MAX_DEFAULT_PAGES = 3       # 60 most-useful reviews per SKU
_PRODUCT_ID = re.compile(r"/p/(\d+)")

_FETCH_JS = """async (url) => {
  const r = await fetch(url, {headers: {'Accept': 'application/json'},
                              credentials: 'include'});
  const t = await r.text();
  try { return {status: r.status, json: JSON.parse(t)}; }
  catch (e) { return {status: r.status, text: t.slice(0, 300)}; }
}"""


def product_id(url: str) -> str | None:
    """The Nykaa product id embedded in a PDP URL.

    Args:
        url: A Nykaa product URL, e.g. ".../beauty-of-joseon.../p/16900408?...".

    Returns:
        The id as a string, or None if the URL carries no /p/<id> segment.
    """
    m = _PRODUCT_ID.search(url or "")
    return m.group(1) if m else None


def _api_url(pid: str, page: int, filters: str) -> str:
    """The review-API path for one page of one filter."""
    return (f"/gateway-api/products/{pid}/reviews"
            f"?pageNo={page}&filters={filters}&domain=nykaa")


def review_url(listing_url: str) -> str | None:
    """The public all-reviews page for a Nykaa PDP URL.

    Derived from the listing URL rather than assembled from the id alone: the
    slug is part of the path, and a URL this project cites must be one that
    actually resolves (CLAUDE.md rule 6).

    Args:
        listing_url: A Nykaa PDP URL containing "/p/<id>".

    Returns:
        The ".../reviews/<id>?ptype=review" URL, or None if the input carries
        no product id.
    """
    pid = product_id(listing_url)
    if not pid:
        return None
    base = (listing_url or "").split("?")[0]
    return re.sub(rf"/p/{pid}$", f"/reviews/{pid}?ptype=review", base)


def load_targets(band_path: str | Path | None = None) -> list[dict]:
    """The SKUs to mine, drawn from the Phase 1 band analysis.

    Only Nykaa SKUs listing inside Rs1,500-3,000 by MRP are eligible, because
    the review API is Nykaa's and the band is the thread's subject. Within
    those: every hero-format SKU regardless of brand group (the comparison
    "do Korean products fail where others do not?" needs the non-Korean arm),
    plus Korean moisturisers and toners/essences, where a temperate-market
    texture would surface as heaviness in Indian humidity.

    Args:
        band_path: Override for data/manual/analysis/premium_skin_band.json.

    Returns:
        One dict per SKU with product_id, name, brand, brand_group, format,
        mrp, street_price and the listing URL. Deduplicated by product id.
    """
    path = Path(band_path) if band_path else BAND_PATH
    band = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, dict] = {}
    for sku in band["in_band_by_mrp_skus"]:
        if sku["platform"] != "nykaa":
            continue
        fmt, group = sku["format"], sku["brand_group"]
        if not (fmt in HERO_FORMATS
                or (group == "korean" and fmt in CLIMATE_FORMATS)):
            continue
        pid = product_id(sku["url"])
        if not pid or pid in out:
            continue
        out[pid] = {
            "product_id": pid,
            "name": sku["name"],
            "brand": sku["brand"],
            "brand_group": group,
            "format": fmt,
            "mrp": sku["mrp"],
            "street_price": sku["street_price"],
            "listing_url": sku["url"],
            "review_url": review_url(sku["url"]),
        }
    return list(out.values())


def parse_review(row: dict) -> dict:
    """Flatten one API review record, lifting skin tone and type out of metadata.

    Args:
        row: A `response.reviewData[]` element.

    Returns:
        A flat dict. `skin_tone` and `skin_type` are None when the reviewer has
        not filled in that part of their Nykaa beauty profile — which is the
        majority case and must be carried as a null, not imputed.
    """
    tone = skin_type = None
    for form in (row.get("metaData") or {}).get("portfolioForm") or []:
        attrs = form.get("attributes") or [{}]
        if form.get("attributeType") == "skinTone":
            tone = attrs[0].get("value")
        elif form.get("attributeType") == "skinType":
            skin_type = attrs[0].get("value")
    return {
        "review_id": row.get("id"),
        "rating": row.get("rating"),
        "title": (row.get("title") or "").strip(),
        "description": (row.get("description") or "").strip(),
        "created_on": row.get("createdOn"),
        "is_verified_buyer": bool(row.get("isBuyer")),
        "like_count": row.get("likeCount"),
        "skin_tone": tone,
        "skin_type": skin_type,
        "has_images": bool(row.get("images")),
    }


def _call(page, url: str) -> dict | None:
    """One rate-limited API call from the page context; None on failure."""
    time.sleep(_RATE_LIMIT_SECONDS)
    try:
        res = page.evaluate(_FETCH_JS, url)
    except Exception as exc:                      # noqa: BLE001 - render flake
        logger.warning("review API call failed for %s: %s", url, str(exc)[:150])
        return None
    if res.get("status") != 200 or not res.get("json"):
        logger.warning("review API %s returned %s", url, res.get("status"))
        return None
    return res["json"]


def _collect(page, pid: str, filters: str, max_pages: int) -> tuple[list[dict], int | None]:
    """Paginate one filter to exhaustion or `max_pages`.

    Returns:
        (reviews, claimed_count). `claimed_count` is the API's own reviewCount
        for that filter, which is routinely LARGER than the rows it will serve;
        both are kept so the transform can use the honest denominator.
    """
    rows: dict[int, dict] = {}
    claimed = None
    empty_streak = 0
    for pno in range(1, max_pages + 1):
        data = _call(page, _api_url(pid, pno, filters))
        if data is None:
            break
        if claimed is None:
            claimed = data.get("reviewCount")
        batch = (data.get("response") or {}).get("reviewData") or []
        if not batch:
            empty_streak += 1
            if empty_streak >= 2:     # one empty page mid-run is not the end
                break
            continue
        empty_streak = 0
        for row in batch:
            parsed = parse_review(row)
            if parsed["review_id"] is not None:
                rows.setdefault(parsed["review_id"], parsed)
    return list(rows.values()), claimed


def fetch(targets: list[dict] | None = None, limit: int | None = None) -> list[dict]:
    """Mine Nykaa reviews for the Phase 2 SKU set.

    Args:
        targets: SKU dicts from load_targets(); loaded from disk when omitted.
        limit: Cap the number of SKUs (for a smoke run).

    Returns:
        One record per SKU. Never raises: a SKU whose calls all fail is
        recorded with `error` set and an empty corpus, so a partial run is
        still an honest run.
    """
    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.error("Playwright not installed. Run: pip install playwright && "
                     "python -m playwright install chromium.")
        return []

    skus = targets if targets is not None else load_targets()
    if limit:
        skus = skus[:limit]
    records: list[dict] = []

    with sync_playwright() as pw:
        try:
            browser = pw.chromium.launch(headless=True, channel=_CHROME_CHANNEL,
                                         args=_CHROMIUM_ARGS)
        except PlaywrightError:
            logger.warning("Chrome channel unavailable; bundled Chromium will "
                           "likely be refused by Nykaa.")
            browser = pw.chromium.launch(headless=True, args=_CHROMIUM_ARGS)
        ctx = browser.new_context(user_agent=_UA,
                                  viewport={"width": 1440, "height": 900},
                                  locale="en-IN")
        page = ctx.new_page()
        page.goto(_ORIGIN_PAGE, timeout=_PAGE_TIMEOUT_MS,
                  wait_until="domcontentloaded")
        time.sleep(3.0)

        for idx, sku in enumerate(skus, 1):
            pid = sku["product_id"]
            rec = dict(sku)

            head = _call(page, _api_url(pid, 1, "DEFAULT"))
            if head is None:
                rec.update({"error": "DEFAULT page 1 failed", "reviews": [],
                            "written_review_count": None,
                            "rating_distribution": {}, "retrieved": {}})
                records.append(rec)
                logger.warning("[%d/%d] %s: no response", idx, len(skus),
                               sku["name"][:50])
                continue
            rec["written_review_count"] = head.get("reviewCount")

            # Rating distribution: reviewCount under each star filter.
            distribution: dict[str, int | None] = {}
            for star in range(1, 6):
                data = _call(page, _api_url(pid, 1, f"STAR_{star}"))
                distribution[str(star)] = data.get("reviewCount") if data else None
            rec["rating_distribution"] = distribution

            reviews: dict[int, dict] = {}
            retrieved: dict[str, int] = {}

            for star in (1, 2):
                rows, _claimed = _collect(page, pid, f"STAR_{star}",
                                          _MAX_NEGATIVE_PAGES)
                for r in rows:
                    r["frame"] = "negative"
                    reviews.setdefault(r["review_id"], r)
                retrieved[f"star_{star}"] = len(rows)

            default_rows, _ = _collect(page, pid, "DEFAULT", _MAX_DEFAULT_PAGES)
            for r in default_rows:
                if r["review_id"] in reviews:
                    reviews[r["review_id"]]["frame"] = "both"
                else:
                    r["frame"] = "most_useful"
                    reviews[r["review_id"]] = r
            retrieved["most_useful"] = len(default_rows)

            rec["retrieved"] = retrieved
            rec["reviews"] = list(reviews.values())
            records.append(rec)
            logger.info("[%d/%d] %s (%s): %d reviews (%d neg, %d useful) of "
                        "%s written", idx, len(skus), sku["name"][:45],
                        sku["brand_group"], len(rec["reviews"]),
                        retrieved["star_1"] + retrieved["star_2"],
                        retrieved["most_useful"], rec["written_review_count"])
        browser.close()
    return records


def to_data_points(raw_records: list[dict]) -> list:
    """Reviews are a text corpus, not a measurement — raw-only.

    Args:
        raw_records: Records from fetch().

    Returns:
        Always []. Complaint counting and its methodology live in
        lib/transforms/premium_skin_fit.py.
    """
    total = sum(len(r.get("reviews") or []) for r in raw_records)
    logger.info("%d reviews across %d SKUs kept raw-only (classify before "
                "ledgering)", total, len(raw_records))
    return []


def main() -> None:
    """Run the review sweep and persist it to data/raw/."""
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    records = fetch()
    total = sum(len(r.get("reviews") or []) for r in records)
    path = save_raw("premium_skin_reviews", records)
    logger.info("Wrote %d SKUs (%d reviews) to %s", len(records), total, path)


if __name__ == "__main__":
    main()


__all__ = ["fetch", "load_targets", "parse_review", "product_id", "review_url",
           "to_data_points", "main", "HERO_FORMATS", "CLIMATE_FORMATS"]
