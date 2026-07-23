"""Blinkit beauty assortment snapshots via a headless browser — opt-in only.

Disabled by default. Requires `enabled: true` in config/qcommerce_enabled.yaml.
Blinkit's search page is a JavaScript SPA behind a location gate, so a plain
HTTP GET returns only the app shell (no products). This fetcher therefore
renders each search with headless Chromium (Playwright) and parses the rendered
product list. A default store's catalogue is served without setting a pincode.

Requires Playwright + its Chromium build:
    pip install playwright && python -m playwright install chromium

When enabled: 5+ second delays between searches, an identifying user agent,
category/brand search pages only. Captured per product: name, pack, selling
price, MRP (strike-through), discount %, in-stock/coming-soon. The corridor
K-brand watchlist is flagged. Prices are point-in-time snapshots, so
to_data_points() stays raw-only — promotion to DataPoints is a curation pass.
"""
from __future__ import annotations

import logging
import re
import time
from urllib.parse import quote

from lib.fetchers._base import USER_AGENT, load_yaml, save_raw

logger = logging.getLogger("bpc_intel.fetchers.qcommerce")

_RATE_LIMIT_SECONDS = 5.0
_PAGE_TIMEOUT_MS = 45000
_RENDER_TIMEOUT_MS = 20000

# Corridor watchlist: K-brands whose q-commerce presence signals Tier 2/3 reach.
KBRAND_WATCHLIST = [
    "COSRX", "Anua", "Beauty of Joseon", "Laneige", "Innisfree",
    "Some By Mi", "Isntree", "Mixsoon", "Etude", "The Face Shop",
]

_CATEGORY_TERMS = ["korean skincare", "korean sunscreen"]

_MINS_RE = re.compile(r"^\d+\s*MINS$", re.I)
_PACK_RE = re.compile(
    r"^\d[\d.]*\s*(?:x\s*\d[\d.]*\s*)?"
    r"(?:g|kg|ml|l|pcs?|pieces?|sheets?|units?|combo|n)\b", re.I)
_PRICE_RE = re.compile(r"^₹\s*([\d,]+(?:\.\d+)?)")
_OFF_RE = re.compile(r"^(\d+)%\s*OFF$", re.I)


def is_enabled() -> bool:
    """Whether the user has explicitly opted in via config/qcommerce_enabled.yaml."""
    try:
        return bool(load_yaml("qcommerce_enabled.yaml").get("enabled", False))
    except FileNotFoundError:
        return False


def is_kbrand(name: str) -> str | None:
    """The watchlist K-brand a product name belongs to, or None."""
    low = name.lower()
    for brand in KBRAND_WATCHLIST:
        if brand.lower() in low:
            return brand
    return None


def _price(line: str) -> float | None:
    m = _PRICE_RE.match(line)
    return float(m.group(1).replace(",", "")) if m else None


def parse_products(text: str) -> list[dict]:
    """Parse a rendered Blinkit search page's text into product records.

    Anchors on the per-card "N MINS" delivery line; status flags ("X% OFF",
    "Out of Stock", "Coming Soon") precede it, and name/pack/price(s) follow.

    Args:
        text: The rendered page body text (Playwright inner_text or equivalent).

    Returns:
        One dict per product: name, pack, price_sale, price_mrp, discount_pct,
        in_stock, coming_soon, kbrand.
    """
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    products: list[dict] = []
    i, n = 0, len(lines)
    while i < n:
        if not _MINS_RE.match(lines[i]):
            i += 1
            continue
        # Flags sit immediately before the MINS anchor.
        discount = None
        out_of_stock = coming_soon = False
        j = i - 1
        while j >= 0:
            mo = _OFF_RE.match(lines[j])
            if mo:
                discount = int(mo.group(1))
            elif lines[j].lower() == "out of stock":
                out_of_stock = True
            elif lines[j].lower() == "coming soon":
                coming_soon = True
            else:
                break
            j -= 1
        # name, optional pack, then one or two prices.
        name = lines[i + 1] if i + 1 < n else None
        k = i + 2
        pack = None
        if k < n and _PACK_RE.match(lines[k]):
            pack, k = lines[k], k + 1
        prices: list[float] = []
        while k < n and _PRICE_RE.match(lines[k]):
            prices.append(_price(lines[k]))
            k += 1
        if name and prices:
            products.append({
                "name": name, "pack": pack,
                "price_sale": prices[0],
                "price_mrp": prices[1] if len(prices) > 1 else None,
                "discount_pct": discount,
                "in_stock": not out_of_stock,
                "coming_soon": coming_soon,
                "kbrand": is_kbrand(name),
            })
        i = max(k, i + 1)
    return products


def fetch() -> list[dict]:
    """Render Blinkit searches for the K-brand watchlist + category terms.

    Returns:
        Raw records (one per search term) with parsed products; empty list when
        disabled (the default), when Playwright/Chromium is unavailable, or on
        failure. Never raises.
    """
    if not is_enabled():
        logger.warning(
            "qcommerce_tracker is disabled. Review the ToS implications and set "
            "enabled: true in config/qcommerce_enabled.yaml to activate."
        )
        return []
    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import TimeoutError as PlaywrightTimeout
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.error(
            "Playwright not installed. Run: pip install playwright && "
            "python -m playwright install chromium. Skipping q-commerce fetch."
        )
        return []

    terms = list(KBRAND_WATCHLIST) + _CATEGORY_TERMS
    records: list[dict] = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page(user_agent=USER_AGENT)
            for idx, term in enumerate(terms):
                if idx:
                    time.sleep(_RATE_LIMIT_SECONDS)
                try:
                    page.goto(f"https://blinkit.com/s/?q={quote(term)}",
                              timeout=_PAGE_TIMEOUT_MS, wait_until="domcontentloaded")
                    page.wait_for_selector("text=₹", timeout=_RENDER_TIMEOUT_MS)
                    time.sleep(1.5)  # let the product grid settle
                    text = page.inner_text("body")
                except (PlaywrightError, PlaywrightTimeout) as exc:
                    logger.error("q-commerce render failed for '%s': %s", term, exc)
                    continue
                products = parse_products(text)
                kbrand = [p for p in products if p["kbrand"]]
                records.append({
                    "platform": "blinkit", "search_term": term,
                    "corridor": is_kbrand(term) is not None,
                    "product_count": len(products),
                    "kbrand_count": len(kbrand),
                    "products": products,
                })
                logger.info("Blinkit '%s': %d products (%d K-brand)",
                            term, len(products), len(kbrand))
            browser.close()
    except (PlaywrightError, PlaywrightTimeout) as exc:
        logger.error("q-commerce browser session failed: %s", exc)
    return records


def to_data_points(raw_records: list[dict]) -> list:
    """Point-in-time price snapshots are not market statistics — raw-only.

    Args:
        raw_records: Records from fetch().

    Returns:
        Always []; assortment/price analysis is a curation pass over raw
        products (see kbrand_snapshot()).
    """
    logger.info("%d q-commerce snapshots kept raw-only (curate before ledgering)",
                len(raw_records))
    return []


def kbrand_snapshot(raw_records: list[dict]) -> list[dict]:
    """Flatten watchlist K-brand products across searches, deduped by name+pack.

    A curation aid: the corridor-relevant slice of a raw capture, for review
    before any prices are promoted to DataPoints.

    Args:
        raw_records: Records from fetch().

    Returns:
        Unique K-brand product dicts, each tagged with its search_term.
    """
    seen: set[tuple] = set()
    out: list[dict] = []
    for rec in raw_records:
        for p in rec.get("products", []):
            if not p.get("kbrand"):
                continue
            key = (p["name"], p.get("pack"))
            if key in seen:
                continue
            seen.add(key)
            out.append({**p, "search_term": rec["search_term"]})
    return out


def run(output_dir: str = "data/raw/") -> str:
    """Full pipeline: fetch -> save raw. Returns raw path or ''."""
    records = fetch()
    if not records:
        return ""
    return str(save_raw("qcommerce", records, output_dir))


__all__ = ["is_enabled", "is_kbrand", "parse_products", "fetch",
           "to_data_points", "kbrand_snapshot", "run", "KBRAND_WATCHLIST"]
