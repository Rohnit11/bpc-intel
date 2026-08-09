"""Build the data context passed to report templates.

Everything here is read from data/processed/ and the analysis layer — no
number originates in this module. Each figure surfaces its source and
confidence so templates can show provenance.
"""
from __future__ import annotations

import logging
from datetime import date

import yaml

from lib.analysis._load import PROCESSED_DIR, load_points
from lib.analysis.share import compute_shares
from lib.analysis.sizing import bottom_up_size, reconcile, top_down_size
from lib.transforms.schema import DataPoint, PROJECT_ROOT

logger = logging.getLogger("bpc_intel.reports.context")

_SEGMENTS = [
    "skincare", "sun_care", "colour_cosmetics", "fragrances", "hair_care",
    "bath_shower", "deodorants", "oral_care", "mens_grooming", "baby_child",
    "dermocosmetics", "emerging_adjacencies",
]


# A brief summarises; the ledger enumerates. A single price sweep can add
# hundreds of SKU-level observations, which would turn the value-chain brief's
# pricing section into a product catalogue. Past this many points a segment
# collapses to a per-basis summary plus a sample, and readers are pointed at
# data/sources.csv for the full set.
PRICE_SAMPLE_LIMIT = 8


def _price_view(points: list[DataPoint]) -> dict:
    """A bounded view of a segment's retail prices.

    Args:
        points: That segment's retail_price DataPoints, in ledger order.

    Returns:
        {"examples": [...], "summary": [...], "omitted": int}. Under the limit
        every point is an example and the summary is empty, so small segments
        render exactly as before. Over it, the summary reports how many points
        exist and the span they cover, grouped by (currency, value_basis) —
        never across bases, per CLAUDE.md rule 3. Only count and span are
        reported: these are query-driven assortment samples, not a census, so a
        central figure would invite being quoted as "the" price.
    """
    if len(points) <= PRICE_SAMPLE_LIMIT:
        return {"examples": [_fmt(dp) for dp in points], "summary": [], "omitted": 0}

    groups: dict[tuple[str, str], list[DataPoint]] = {}
    for dp in points:
        groups.setdefault((dp.currency, dp.value_basis), []).append(dp)

    summary = []
    for (currency, basis), grp in sorted(groups.items()):
        values = sorted(dp.value for dp in grp)
        summary.append({
            "currency": currency, "value_basis": basis, "unit": grp[0].unit,
            "count": len(grp), "low": values[0], "high": values[-1],
        })
    return {
        "examples": [_fmt(dp) for dp in points[:PRICE_SAMPLE_LIMIT]],
        "summary": summary,
        "omitted": len(points) - PRICE_SAMPLE_LIMIT,
    }


def _fmt(dp: DataPoint) -> dict:
    """Flatten a DataPoint to a template-friendly dict."""
    return {
        "value": dp.value, "unit": dp.unit, "currency": dp.currency,
        "period": dp.period, "value_basis": dp.value_basis,
        "confidence": dp.confidence, "source": dp.source_name,
        "url": dp.source_url, "notes": dp.notes, "metric": dp.metric,
        "tier": dp.tier,
    }


def segment_metric(geography: str, segment: str, metric: str) -> list[dict]:
    """All DataPoints for a geography/segment/metric, newest-source-first."""
    pts = [dp for dp in load_points(geography, segment) if dp.metric == metric]
    return [_fmt(dp) for dp in pts]


def headline(geography: str) -> dict:
    """Headline figures for a geography: total size, growth, exports, per-capita."""
    tp = load_points(geography, "total_bpc")
    out: dict = {"geography": geography}
    td = top_down_size(geography, "total_bpc")
    out["market_size"] = _fmt(td) if td else None
    for metric in ("growth_yoy", "cagr_forecast", "per_capita_spend"):
        vals = [dp for dp in tp if dp.metric == metric]
        out[metric] = _fmt(vals[0]) if vals else None
    exports = [dp for dp in tp if dp.metric == "export_value"
               and "World" not in (dp.notes or "") and "India" not in (dp.notes or "")]
    out["total_export"] = _fmt(max(exports, key=lambda d: d.value)) if exports else None
    return out


def reconciliation(geography: str) -> dict:
    """Top-down vs bottom-up reconciliation for a geography (total BPC)."""
    td = top_down_size(geography, "total_bpc")
    bu = bottom_up_size(geography, "total_bpc")
    return reconcile(td, bu)


def segment_rows(geography: str) -> list[dict]:
    """One row per segment: best market size + growth/forecast if present."""
    rows = []
    for seg in _SEGMENTS:
        size = top_down_size(geography, seg)
        pts = load_points(geography, seg)
        growths = [dp for dp in pts if dp.metric == "growth_yoy"]
        # Prefer a growth figure on the same basis as the displayed size, so a
        # RETAIL size is not paired with an EXPORT_FOB growth rate.
        growth = None
        if growths:
            if size is not None:
                growth = next((g for g in growths if g.value_basis == size.value_basis), None)
            growth = growth or growths[0]
        cagr = next((dp for dp in pts if dp.metric == "cagr_forecast"), None)
        exp = [dp for dp in pts if dp.metric == "export_value"
               and "India" not in (dp.notes or "") and "World" not in (dp.notes or "")]
        if not (size or growth or cagr or exp):
            continue
        rows.append({
            "segment": seg,
            "size": _fmt(size) if size else None,
            "growth": _fmt(growth) if growth else None,
            "cagr": _fmt(cagr) if cagr else None,
            "export": _fmt(max(exp, key=lambda d: d.value)) if exp else None,
        })
    return rows


def corridor_context() -> dict:
    """Everything for the K-beauty corridor brief."""
    with (PROJECT_ROOT / "config" / "corridor.yaml").open(encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)["corridor"]

    # [CORRIDOR]-tagged data points: shelf prices feed the pricing table,
    # everything else (market sizes, CAGRs, import values) feeds sizing.
    sizing_pts: list[dict] = []
    pricing_pts: list[dict] = []
    trade_pts: list[dict] = []
    for seg in _SEGMENTS + ["total_bpc"]:
        for dp in load_points("IN", seg):
            if dp.notes and "[CORRIDOR]" in dp.notes:
                row = _fmt(dp) | {"segment": seg}
                (pricing_pts if dp.metric == "retail_price" else sizing_pts).append(row)
        for dp in load_points("KR", seg):
            if dp.notes and "[CORRIDOR]" in dp.notes and "India" in dp.notes:
                trade_pts.append(_fmt(dp) | {"segment": seg})

    return {
        "headline": cfg.get("headline", {}),
        "conduits": cfg.get("conduits", []),
        "india_side_players": cfg.get("india_side_players", {}),
        "qcommerce": cfg.get("qcommerce_assortment", {}),
        "whitespace": cfg.get("whitespace", []),
        "regulation": cfg.get("regulation", {}),
        "sizing": sorted(sizing_pts, key=lambda p: p["period"]),
        "pricing": sorted(pricing_pts, key=lambda p: -p["value"]),
        "trade": sorted(trade_pts, key=lambda p: -p["value"]),
    }


def shares(geography: str) -> dict:
    """Listed-player revenue shares for a geography."""
    return compute_shares(geography, "total_bpc")


_INDIA_BRIEF_SEGMENTS = [
    "total_bpc", "skincare", "sun_care", "dermocosmetics",
    "fragrances", "mens_grooming", "hair_care",
]


def india_value_chain_context() -> dict:
    """Assemble the India value-chain brief context (data + sourced findings)."""
    with (PROJECT_ROOT / "config" / "india_findings.yaml").open(encoding="utf-8") as fh:
        findings = yaml.safe_load(fh)

    segments = []
    for seg in _INDIA_BRIEF_SEGMENTS:
        pts = load_points("IN", seg)
        size = top_down_size("IN", seg)
        imports = {"World": None, "Korea": None, "China": None}
        for dp in pts:
            if dp.metric == "import_value":
                for origin in imports:
                    if origin in (dp.notes or ""):
                        imports[origin] = _fmt(dp)
        segments.append({
            "segment": seg,
            "size": _fmt(size) if size else None,
            "growth": [_fmt(dp) for dp in pts if dp.metric in ("growth_yoy", "cagr_forecast")],
            "imports": imports,
            "import_dependence": next((_fmt(dp) for dp in pts if dp.metric == "import_dependence"), None),
            "prices": _price_view([dp for dp in pts if dp.metric == "retail_price"]),
            "margins": [_fmt(dp) for dp in pts if dp.metric in ("gross_margin",)],
        })

    # Company operating margins (cost structure) — latest per company.
    tp = load_points("IN", "total_bpc")
    from lib.analysis._load import company_name, period_end_year
    opm: dict[str, dict] = {}
    for dp in tp:
        if dp.metric != "operating_margin":
            continue
        name = company_name(dp)
        if name and (name not in opm or period_end_year(dp.period) > opm[name]["_yr"]):
            opm[name] = {"company": name, "value": dp.value, "period": dp.period,
                         "_yr": period_end_year(dp.period)}

    return {
        "generated": date.today().isoformat(),
        "segments": segments,
        "operating_margins": sorted(opm.values(), key=lambda d: -d["value"]),
        "findings": findings,
    }


def full_context() -> dict:
    """Assemble the whole context object for the full snapshot report."""
    gaps_path = PROJECT_ROOT / "reports" / "latest" / "gaps_register.md"
    gaps_md = gaps_path.read_text(encoding="utf-8") if gaps_path.exists() else ""
    return {
        "generated": date.today().isoformat(),
        "korea": {
            "headline": headline("KR"),
            "segments": segment_rows("KR"),
            "shares": shares("KR"),
            "reconciliation": reconciliation("KR"),
        },
        "india": {
            "headline": headline("IN"),
            "segments": segment_rows("IN"),
            "shares": shares("IN"),
            "reconciliation": reconciliation("IN"),
        },
        "corridor": corridor_context(),
        "gaps_md": gaps_md,
    }


__all__ = [
    "headline", "reconciliation", "segment_rows", "corridor_context",
    "shares", "segment_metric", "full_context",
]
