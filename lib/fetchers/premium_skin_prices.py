"""India online skincare price sweep for the Rs1,500-3,000 band — [PREMIUM-SKIN].

Phase 1 of docs/premium-skincare-brief.md asks one question the repo cannot
answer from file: does the Rs1,500-3,000 MRP band survive discounting online?
Answering it needs BOTH a list price and a transaction price for the same SKU on
the same date, across the whole competitive set — Korean, homegrown and other
foreign brands alike.

Three platforms, three different jobs:

- **Nykaa** (`nykaa`) — the MRP anchor. Nykaa sells as an authorised retailer and
  its cards carry an accessible "Regular price X. Discounted price Y. N% Off."
  string, so list and street come from one card on one date.
- **Tira** (`tira`) — the second MRP anchor, and a cross-check on Nykaa's list
  price. Tira labels the two prices literally ("MRP:" / "Deal Price:"), which is
  the cleanest MRP evidence available online. Where Tira and Nykaa disagree on
  MRP for the same SKU, that disagreement is itself a finding.
- **Amazon.in** (`amazon`) — street price ONLY. Amazon's strike-through is set by
  third-party sellers, not the brand, and the sweep routinely sees absurd values
  (Rs94,900 against a Rs949 product — a per-100ml unit-price artefact). Records
  carry `mrp_untrusted: true` and the transform must never treat Amazon as an
  MRP source.

All three are JavaScript SPAs: a plain HTTP GET returns the app shell with no
prices, so each search is rendered with headless Chromium and parsed from the
rendered DOM. Read-only, one pass over public search pages, rate-limited.

Prices are point-in-time snapshots of a relevance-ranked result page, not a
census of either platform's catalogue — `to_data_points()` therefore stays
raw-only and promotion to DataPoints is a curation pass
(lib/transforms/premium_skin_band.py).

Requires Playwright + its Chromium build:
    pip install playwright && python -m playwright install chromium
"""
from __future__ import annotations

import logging
import re
import time
from urllib.parse import quote

from lib.fetchers._base import save_raw

logger = logging.getLogger("bpc_intel.fetchers.premium_skin_prices")

_RATE_LIMIT_SECONDS = 3.0
_PAGE_TIMEOUT_MS = 45000
_RENDER_TIMEOUT_MS = 25000

# Headless Chromium's own UA. Nykaa/Tira/Amazon all gate their SPA render on a
# browser-shaped UA; the project UA string used elsewhere gets an empty shell.
_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")

# Playwright's BUNDLED Chromium is refused by two of the three platforms: Nykaa
# resets the HTTP/2 handshake (ERR_HTTP2_PROTOCOL_ERROR on every navigation) and
# Tira returns "Access Denied". Locally-installed Chrome (channel="chrome")
# renders all three headless. Falls back to bundled Chromium if Chrome is absent,
# in which case expect Amazon-only coverage.
_CHROME_CHANNEL = "chrome"
_CHROMIUM_ARGS = ["--disable-blink-features=AutomationControlled"]

# A rupee sign alone is not a usable readiness signal: all three sites ship
# hidden <option> price filters ("Under ₹500"), so `text=₹` resolves to
# invisible nodes and the wait times out. Wait on the product card instead.
_READY_SELECTOR = {
    "nykaa": 'div[class*="productWrapper"]',
    "tira": 'div[class*="productCartPrice"]',
    "amazon": 'div[data-component-type="s-search-result"]',
}

# Phase 1 competitive set: all three groups, per docs/premium-skincare-brief.md.
# Korean list seeded from config/corridor.yaml's carried brands.
#
# Revised for Phase 4 (2026-08-10) on docs/premium-skincare-phase3.md §9.7:
# - Limese dropped. Phase 3 established it is a K-beauty importer/multi-brand
#   retailer, not a homegrown brand — it belongs in config/corridor.yaml's
#   conduits, and querying it as a brand can only return other people's product.
# - The twelve Indian-origin brands that actually hold in-band single SKUs
#   (Phase 3 §5) added. Phase 1 swept the wrong domestic brands: Minimalist et
#   al. top out below the band, while these were only ever caught incidentally
#   by concern-led format queries, never by a brand query.
# - D'you, Put Simply and Quench added. All three already run the Korean-ODM +
#   Indian-brand lane this thread is costing, and none was ever queried.
BRAND_GROUPS: dict[str, list[str]] = {
    "korean": [
        "Anua", "Beauty of Joseon", "COSRX", "Innisfree", "Laneige", "Etude",
        "Medicube", "TirTir", "Mixsoon", "Hince", "Dr Melaxin", "Isntree",
        "Some By Mi", "Dr.Jart+", "The Face Shop",
    ],
    "homegrown": [
        "Minimalist", "Dot & Key", "Foxtale", "Pilgrim", "Plum",
        "Forest Essentials", "Kama Ayurveda", "Deconstruct", "Earth Rhythm",
        # Phase 3 §5 — Indian-origin brands with in-band single SKUs.
        "RAS Luxury Oils", "Suganda", "Yuderma", "Ethiglo", "WildGlow", "BiE",
        "The Derma Co", "Miduty", "Fixderma", "Aminu",
        # Phase 3 §5 — the Korean-ODM + Indian-brand incumbents.
        "D'you", "Put Simply", "Quench Botanics",
    ],
    "other_foreign": [
        "Cetaphil", "La Roche-Posay", "The Ordinary", "Paula's Choice",
        "Clinique", "Kiehl's", "Bioderma", "Sebamed",
    ],
}

# Hero-format queries. The brief weights SKU depth toward pigmentation/
# brightening serums and sunscreens, so those are swept by format as well as by
# brand — a brand query alone returns bestsellers, not the hero shelf.
HERO_QUERIES: list[tuple[str, str]] = [
    ("pigmentation_serum", "pigmentation serum"),
    ("pigmentation_serum", "dark spot correcting serum"),
    ("pigmentation_serum", "melasma serum"),
    ("brightening_serum", "brightening serum"),
    ("brightening_serum", "vitamin c serum"),
    ("brightening_serum", "niacinamide serum"),
    ("brightening_serum", "alpha arbutin serum"),
    ("brightening_serum", "tranexamic acid serum"),
    ("sunscreen", "sunscreen spf 50"),
    ("sunscreen", "korean sunscreen"),
    ("sunscreen", "sunscreen no white cast"),
    ("korean_general", "korean skincare serum"),
]

_MONEY = r"([\d,]+(?:\.\d+)?)"
_NYKAA_DISCOUNTED = re.compile(
    rf"Regular price\s*₹\s*{_MONEY}\s*\.\s*Discounted price\s*₹\s*{_MONEY}\s*\.\s*(\d+)%\s*Off",
    re.I)
_NYKAA_FLAT = re.compile(rf"^\s*Price\s*₹\s*{_MONEY}\s*\.", re.I)
_RUPEES = re.compile(rf"₹\s*{_MONEY}")


def _money(text: str | None) -> float | None:
    """The first rupee amount in `text`, or None."""
    if not text:
        return None
    m = _RUPEES.search(text)
    return float(m.group(1).replace(",", "")) if m else None


def parse_nykaa_price(price_line: str | None) -> tuple[float | None, float | None, int | None]:
    """Split a Nykaa card's accessible price string into (mrp, street, discount%).

    Nykaa renders one of two forms in a screen-reader span:
    "Regular price ₹1570. Discounted price ₹1413. 10% Off." (discounted), or
    "Price ₹1570." (undiscounted, where list and street are the same number).

    Args:
        price_line: The span's text, or None.

    Returns:
        (mrp, street_price, discount_pct). All None when unparseable. For the
        undiscounted form, mrp == street_price and discount_pct is 0.
    """
    if not price_line:
        return None, None, None
    m = _NYKAA_DISCOUNTED.search(price_line)
    if m:
        return (float(m.group(1).replace(",", "")),
                float(m.group(2).replace(",", "")),
                int(m.group(3)))
    m = _NYKAA_FLAT.search(price_line)
    if m:
        value = float(m.group(1).replace(",", ""))
        return value, value, 0
    return None, None, None


# --- In-page extractors -----------------------------------------------------
# Each returns raw card fields; price arithmetic stays in Python so it is
# testable without a browser.

_JS_NYKAA = """() => {
  const slugName = (href) => {
    if (!href) return null;
    const m = href.split('?')[0].match(/^\\/([^\\/]+)\\/p\\//);
    if (!m) return null;
    return m[1].replace(/-/g, ' ').replace(/\\b\\w/g, ch => ch.toUpperCase());
  };
  const cards = [...document.querySelectorAll('div[class*="productWrapper"]')];
  return cards.map(c => {
    const a = c.querySelector('a[href]');
    const img = c.querySelector('img[alt]');
    const h2 = c.querySelector('h2');
    let priceLine = null;
    c.querySelectorAll('span').forEach(s => {
      const t = (s.textContent || '').trim();
      if (/^(Regular price|Price)\\s*\\u20B9/.test(t)) priceLine = t;
    });
    const tags = [...c.querySelectorAll('li')].map(l => l.innerText.trim());
    const rating = c.querySelector('div[aria-label*="star rating"]');
    const href = a ? a.getAttribute('href') : null;
    // Lazy-loaded cards have an empty img alt, so fall back to the (sometimes
    // truncated) h2 and finally to the URL slug, which is never truncated.
    const alt = img ? img.getAttribute('alt') : null;
    const heading = h2 ? h2.innerText.trim() : null;
    let name = alt || heading || slugName(href);
    if (name && name.endsWith('...')) name = slugName(href) || name;
    return {
      name: name,
      name_source: alt ? 'alt' : (heading && !heading.endsWith('...') ? 'h2' : 'slug'),
      url: href,
      price_line: priceLine,
      tags: tags,
      rating_label: rating ? rating.getAttribute('aria-label') : null,
      card_text: (c.innerText || '').replace(/\\n+/g, ' | ').slice(0, 400)
    };
  });
}"""

_JS_TIRA = """() => {
  // Anchor on the price block and climb to the FIRST ancestor that contains a
  // product link. That ancestor must contain exactly one such link, or the
  // price-to-product pairing is ambiguous and the row is dropped.
  //
  // This matters: searching downward from a link (or climbing without the
  // one-link check) walks past the card into the grid container and pairs a
  // product with the first price it finds anywhere inside — which is how an
  // Anua sunscreen came back at Rs72,000 wearing La Mer's price. A missing row
  // is a gap; a mispaired one is a fabricated price.
  const blocks = [...document.querySelectorAll('div[class*="productCartPrice"]')];
  const seen = new Set();
  const out = [];
  blocks.forEach(block => {
    let node = block.parentElement, hops = 0, card = null, link = null;
    while (node && hops < 8) {
      const links = node.querySelectorAll('a[href*="/product"]');
      if (links.length === 1) { card = node; link = links[0]; break; }
      if (links.length > 1) break;   // ambiguous: skip this block entirely
      node = node.parentElement; hops++;
    }
    if (!link) return;
    const href = (link.getAttribute('href') || '').split('?')[0];
    if (!href || seen.has(href)) return;
    seen.add(href);
    const deal = block.querySelector('.discount-price, p[class*="discountPrice"]');
    const actual = block.querySelector('.actual-price, p[class*="actualPrice"]');
    const pct = block.querySelector('.discount-percentage, p[class*="discountPercentage"]');
    // The card renders as: [tags] "Add to Wishlist" brand rating "|" count
    // PRODUCT NAME ... "Deal Price:" ... The name is the last non-empty line
    // before the price block.
    const lines = (link.innerText || '').split('\\n')
      .map(s => s.trim()).filter(Boolean);
    const priceIdx = lines.findIndex(l => /^Deal Price/i.test(l) || /^\\u20B9/.test(l));
    let name = null;
    if (priceIdx > 0) name = lines[priceIdx - 1];
    if (!name || /^\\d/.test(name) || name.length < 8) {
      const m = href.match(/\\/product\\/(.+?)-\\d+$/);
      if (m) name = m[1].replace(/-/g, ' ').replace(/\\b\\w/g, ch => ch.toUpperCase());
    }
    out.push({
      name: name ? name.slice(0, 220) : null,
      url: href,
      deal_price: deal ? deal.textContent : null,
      mrp: actual ? actual.textContent : null,
      discount_text: pct ? pct.textContent : null,
      card_text: card ? (card.innerText || '').replace(/\\n+/g, ' | ').slice(0, 400) : null
    });
  });
  return out;
}"""

_JS_AMAZON = """() => {
  const cards = [...document.querySelectorAll('div[data-component-type="s-search-result"]')];
  return cards.map(c => {
    const price = c.querySelector('.a-price .a-offscreen');
    const strike = c.querySelector('.a-price.a-text-price .a-offscreen');
    const h2 = c.querySelector('h2');
    const alt = c.querySelector('img.s-image');
    const link = c.querySelector('a.a-link-normal[href]');
    return {
      name: alt ? alt.getAttribute('alt') : (h2 ? h2.innerText : null),
      heading: h2 ? h2.innerText : null,
      asin: c.getAttribute('data-asin'),
      url: link ? link.getAttribute('href') : null,
      street_text: price ? price.textContent : null,
      strike_text: strike ? strike.textContent : null,
      sponsored: (c.innerText || '').slice(0, 40).toLowerCase().includes('sponsored')
    };
  });
}"""


def _search_urls(platform: str, term: str) -> str:
    """The public search URL for `term` on `platform`."""
    q = quote(term)
    return {
        "nykaa": f"https://www.nykaa.com/search/result/?q={q}",
        "tira": f"https://www.tirabeauty.com/products/?q={q}",
        "amazon": f"https://www.amazon.in/s?k={q}",
    }[platform]


def _scrape(page, platform: str, term: str) -> tuple[list[dict], str]:
    """Render one search page and return its parsed product cards.

    Args:
        page: An open Playwright page.
        platform: "nykaa", "tira" or "amazon".
        term: The search term.

    Returns:
        (products, resolved_url). Products are normalised dicts (name, url, mrp,
        street_price, discount_pct, plus platform-specific extras).
        `resolved_url` is the URL actually landed on — brand searches redirect
        (Nykaa "Anua" -> /brands/anua/c/...), and only the landed URL may be
        cited as the source.
    """
    page.goto(_search_urls(platform, term),
              timeout=_PAGE_TIMEOUT_MS, wait_until="domcontentloaded")
    page.wait_for_selector(_READY_SELECTOR[platform], timeout=_RENDER_TIMEOUT_MS)
    time.sleep(2.0)  # let the grid settle / lazy images resolve

    extractor = {"nykaa": _JS_NYKAA, "tira": _JS_TIRA, "amazon": _JS_AMAZON}[platform]
    rows = page.evaluate(extractor)
    if platform in ("tira", "nykaa"):
        # Both lazy-load below the fold AND drop off-screen rows from the DOM,
        # so a single extraction at the end would miss whichever half is not
        # currently rendered. Extract after every scroll step and merge by URL.
        merged = {(r.get("url") or f"_{i}"): r for i, r in enumerate(rows)}
        for _ in range(4):
            page.mouse.wheel(0, 5000)
            time.sleep(1.8)
            for i, r in enumerate(page.evaluate(extractor)):
                key = r.get("url") or f"_{len(merged)}_{i}"
                # Prefer the record that resolved a real name over a slug guess.
                prev = merged.get(key)
                if prev is None or (prev.get("name_source") == "slug"
                                    and r.get("name_source") != "slug"):
                    merged[key] = r
        rows = list(merged.values())

    if platform == "nykaa":
        out = []
        for r in rows:
            mrp, street, pct = parse_nykaa_price(r.get("price_line"))
            if not r.get("name") or street is None:
                continue
            url = r.get("url") or ""
            out.append({
                "name": r["name"],
                "url": f"https://www.nykaa.com{url}" if url.startswith("/") else url,
                "mrp": mrp, "street_price": street, "discount_pct": pct,
                "tags": r.get("tags") or [],
                "rating_label": r.get("rating_label"),
                "mrp_untrusted": False,
            })
        return out, page.url

    if platform == "tira":
        out = []
        for r in rows:
            street = _money(r.get("deal_price"))
            mrp = _money(r.get("mrp")) or street
            if street is None:
                continue
            url = r.get("url") or ""
            pct = None
            if mrp and street and mrp > 0:
                pct = round((mrp - street) / mrp * 100)
            out.append({
                "name": (r.get("name") or "").strip() or None,
                "url": f"https://www.tirabeauty.com{url}" if url.startswith("/") else url,
                "mrp": mrp, "street_price": street, "discount_pct": pct,
                "card_text": r.get("card_text"),
                "mrp_untrusted": False,
            })
        return out, page.url

    out = []
    for r in rows:
        street = _money(r.get("street_text"))
        if street is None or not r.get("name"):
            continue
        name = r["name"]
        sponsored = bool(r.get("sponsored"))
        if name.startswith("Sponsored Ad - "):
            name, sponsored = name[len("Sponsored Ad - "):], True
        out.append({
            "name": name,
            "url": (f"https://www.amazon.in/dp/{r['asin']}" if r.get("asin") else None),
            "asin": r.get("asin"),
            "mrp": None,               # seller-set; never trusted as MRP
            "seller_list_price": _money(r.get("strike_text")),
            "street_price": street,
            "discount_pct": None,
            "sponsored": sponsored,
            "mrp_untrusted": True,
        })
    return out, page.url


def _terms() -> list[tuple[str, str, str]]:
    """The full sweep list as (query_type, group_or_format, term)."""
    terms: list[tuple[str, str, str]] = []
    for group, brands in BRAND_GROUPS.items():
        terms += [("brand", group, b) for b in brands]
    terms += [("hero_format", fmt, q) for fmt, q in HERO_QUERIES]
    return terms


def fetch(platforms: tuple[str, ...] = ("nykaa", "tira", "amazon"),
          amazon_hero_only: bool = True) -> list[dict]:
    """Sweep India online skincare prices across the Phase 1 competitive set.

    Args:
        platforms: Which platforms to sweep.
        amazon_hero_only: Restrict Amazon to hero-format queries plus Korean
            brands. Amazon contributes street price only, so a full 33-brand
            sweep there buys little for the runtime it costs.

    Returns:
        One record per (platform, term) with its parsed products. Never raises;
        a failed render is logged and skipped so one bad page cannot lose a run.
    """
    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import TimeoutError as PlaywrightTimeout
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.error(
            "Playwright not installed. Run: pip install playwright && "
            "python -m playwright install chromium. Skipping price sweep.")
        return []

    all_terms = _terms()
    records: list[dict] = []
    try:
        with sync_playwright() as pw:
            try:
                browser = pw.chromium.launch(
                    headless=True, channel=_CHROME_CHANNEL, args=_CHROMIUM_ARGS)
            except PlaywrightError:
                logger.warning(
                    "Chrome channel unavailable; falling back to bundled "
                    "Chromium. Nykaa and Tira will likely refuse to render.")
                browser = pw.chromium.launch(headless=True, args=_CHROMIUM_ARGS)
            ctx = browser.new_context(
                user_agent=_UA, viewport={"width": 1440, "height": 900},
                locale="en-IN")
            page = ctx.new_page()
            for platform in platforms:
                terms = all_terms
                if platform == "amazon" and amazon_hero_only:
                    terms = [t for t in all_terms
                             if t[0] == "hero_format" or t[1] == "korean"]
                for idx, (qtype, group, term) in enumerate(terms):
                    if idx:
                        time.sleep(_RATE_LIMIT_SECONDS)
                    products, landed, err = None, None, None
                    for attempt in range(2):  # one retry; renders flake
                        try:
                            products, landed = _scrape(page, platform, term)
                            break
                        except (PlaywrightError, PlaywrightTimeout) as exc:
                            err = str(exc)[:200]
                            if attempt == 0:
                                time.sleep(_RATE_LIMIT_SECONDS)
                    if products is None:
                        logger.error("%s render failed for '%s': %s",
                                     platform, term, err)
                        records.append({
                            "platform": platform, "query_type": qtype,
                            "group": group, "search_term": term,
                            "url": _search_urls(platform, term),
                            "error": err, "products": []})
                        continue
                    records.append({
                        "platform": platform, "query_type": qtype,
                        "group": group, "search_term": term,
                        "url": _search_urls(platform, term),
                        "landed_url": landed,
                        "product_count": len(products),
                        "products": products,
                    })
                    logger.info("%s '%s' (%s/%s): %d products",
                                platform, term, qtype, group, len(products))
            browser.close()
    except (PlaywrightError, PlaywrightTimeout) as exc:
        logger.error("price sweep browser session failed: %s", exc)
    return records


def to_data_points(raw_records: list[dict]) -> list:
    """Point-in-time price snapshots are not market statistics — raw-only.

    Args:
        raw_records: Records from fetch().

    Returns:
        Always []. Band membership, discount depth and the retention headline
        are a curation pass — see lib/transforms/premium_skin_band.py.
    """
    logger.info("%d price snapshots kept raw-only (curate before ledgering)",
                len(raw_records))
    return []


def main() -> None:
    """Run the sweep and persist it to data/raw/."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    records = fetch()
    total = sum(r.get("product_count", 0) for r in records)
    path = save_raw("premium_skin_prices", records)
    logger.info("Wrote %d records (%d products) to %s",
                len(records), total, path)


if __name__ == "__main__":
    main()
