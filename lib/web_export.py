"""Web export: serialize the Python view-model into web/public/data/*.json.

Every figure here is produced by lib/reports/_context.py and the analysis
layer beneath it (lib/analysis/*). This module adds no market-sizing,
reconciliation, or share logic of its own — it only shapes already-computed
results into the JSON bundle the Next.js dashboard reads at build time. The
dashboard cannot display a number this module did not receive from Python.
"""
from __future__ import annotations

import csv
import json
import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import yaml

from lib.analysis._load import load_points
from lib.analysis.gaps import scan_gaps, suggest_source
from lib.chat_index import build_index as build_chat_index
from lib.analysis.share import compute_shares
from lib.reports import charts
from lib.transforms.currency import convert
from lib.reports._context import (
    _fmt,
    corridor_context,
    full_context,
    headline,
    india_value_chain_context,
    reconciliation,
    segment_rows,
    shares,
)
from lib.transforms.schema import PROJECT_ROOT

logger = logging.getLogger("bpc_intel.web_export")

WEB_DATA_DIR = PROJECT_ROOT / "web" / "public" / "data"
INSIGHTS_DIR = PROJECT_ROOT / "data" / "manual" / "insights"
ANALYSIS_DIR = PROJECT_ROOT / "data" / "manual" / "analysis"
CONFIG_DIR = PROJECT_ROOT / "config"
# Transient hand-off file: Node's json-schema-to-typescript reads this to
# generate web/types/schema.ts (see web/scripts/gen-schema-ts.mjs). Not
# committed — only the generated .ts is.
SCHEMA_JSON_PATH = PROJECT_ROOT / "web" / "scripts" / "_generated-schema.json"
SOURCES_CSV = PROJECT_ROOT / "data" / "sources.csv"
TAXONOMY_PATH = PROJECT_ROOT / "config" / "taxonomy.yaml"
EXCHANGE_RATES_PATH = PROJECT_ROOT / "config" / "exchange_rates.yaml"

_SEGMENTS = [
    "skincare", "sun_care", "colour_cosmetics", "fragrances", "hair_care",
    "bath_shower", "deodorants", "oral_care", "mens_grooming", "baby_child",
    "dermocosmetics", "emerging_adjacencies",
]

# Mirrors the "Confidence levels" / "VALUE BASIS" sections of CLAUDE.md —
# copied here (not re-derived) so /methodology can render them verbatim.
CONFIDENCE_LEGEND = {
    "HIGH": "Primary source (company filing, government database, Euromonitor Passport)",
    "MEDIUM": "Credible secondary (Korea Herald, Business Standard, Statista, McKinsey)",
    "LOW": "Aggregator/estimate (Mordor Intelligence, Grand View, IMARC)",
    "ESTIMATE": "Model-derived with methodology shown",
}

VALUE_BASIS_LEGEND = {
    "RETAIL": "Consumer sell-through (MRP-inclusive for India)",
    "NET_REALISATION": "Company revenue (ex-trade margins, for India)",
    "WHOLESALE": "Trade/distributor price",
    "EXPORT_FOB": "Customs/FOB value (Korea exports)",
    "PRODUCTION": "Factory-gate output value",
    "IMPORT_CIF": "Customs import value (cost-insurance-freight)",
    "MRP": "Maximum retail price (India shelf price, tax + margin included)",
    "NA": "Basis not applicable (a ratio, margin, or dependence %)",
}


def _write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Wrote %s", path)


def _git_sha() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT,
            capture_output=True, text=True, check=True,
        )
        return result.stdout.strip()
    except Exception:
        logger.warning("Could not resolve git SHA for meta.json", exc_info=True)
        return None


# Money units this exporter knows how to convert to a common USD-bn scale.
# {unit: (currency, multiplier_to_one_unit_of_that_currency)}.
_UNIT_TO_BASE = {
    "usd_bn": ("USD", 1e9), "usd_mn": ("USD", 1e6), "usd": ("USD", 1.0),
    "krw_tn": ("KRW", 1e12),
    "inr_cr": ("INR", 1e7), "inr_bn": ("INR", 1e9), "inr": ("INR", 1.0),
}


def _with_usd(fig: dict | None) -> dict | None:
    """Attach a derived value_usd_bn (+ the pinned FX rate cited) to a
    market_size Figure, so segment tables can compare KR (KRW/USD) and IN
    (INR/USD) sizes on one axis. This ONLY converts currency at the figure's
    existing value_basis — it never normalises RETAIL vs NET_REALISATION etc.
    (CLAUDE.md rule 7); the original value/unit/basis are left untouched.
    """
    if fig is None or fig.get("metric") != "market_size":
        return fig
    base = _UNIT_TO_BASE.get(fig["unit"])
    if base is None:
        return fig
    currency, multiplier = base
    usd_amount, rate_desc = convert(fig["value"] * multiplier, currency, "USD")
    return {**fig, "value_usd_bn": round(usd_amount / 1e9, 4), "fx_note": rate_desc}


def _augment_market_sizes(block: dict) -> dict:
    """Mutate a {'headline':..., 'segments':[...]} block in place, attaching
    value_usd_bn to every market_size Figure it contains."""
    if block.get("headline") and block["headline"].get("market_size"):
        block["headline"]["market_size"] = _with_usd(block["headline"]["market_size"])
    for row in block.get("segments", []):
        if row.get("size"):
            row["size"] = _with_usd(row["size"])
    return block


def build_geography_bundle(geo: str) -> dict:
    """The per-geography page bundle: headline, segment rows, shares, reconciliation."""
    bundle = {
        "geography": geo,
        "headline": headline(geo),
        "segments": segment_rows(geo),
        "shares": shares(geo),
        "reconciliation": reconciliation(geo),
    }
    return _augment_market_sizes(bundle)


def build_segments_bundle() -> dict[str, dict]:
    """Per-segment drilldown bundles: the computed row (from segment_rows) plus
    every underlying raw DataPoint, for both geographies."""

    def empty_row(seg: str) -> dict:
        return {"segment": seg, "size": None, "growth": None, "cagr": None, "export": None}

    kr_rows = {r["segment"]: r for r in segment_rows("KR")}
    in_rows = {r["segment"]: r for r in segment_rows("IN")}
    out: dict[str, dict] = {}
    for seg in _SEGMENTS:
        kr_row = kr_rows.get(seg, empty_row(seg))
        in_row = in_rows.get(seg, empty_row(seg))
        out[seg] = {
            "segment": seg,
            "KR": {**kr_row, "size": _with_usd(kr_row.get("size")),
                   "points": [_fmt(dp) for dp in load_points("KR", seg)]},
            "IN": {**in_row, "size": _with_usd(in_row.get("size")),
                   "points": [_fmt(dp) for dp in load_points("IN", seg)]},
        }
    return out


def build_sources() -> list[dict]:
    """The full data/sources.csv ledger, typed as rows for the /sources page."""
    with SOURCES_CSV.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def build_gaps() -> list[dict]:
    """Structured gaps register with a suggested-source hint per gap."""
    return [dict(g, suggested_source=suggest_source(g)) for g in scan_gaps()]


def build_charts() -> dict[str, object]:
    """Chart series for Recharts — reuses charts.py's data-prep, not the PNGs."""
    korea_exports = [
        {"label": seg.replace("_", " "), "segment": seg, **_fmt(dp)}
        for seg, dp in sorted(
            charts._korea_export_data().items(), key=lambda kv: kv[1].value, reverse=True,
        )
    ]

    india_shares_res = compute_shares("IN", "total_bpc")
    india_shares = [
        {"label": s["company"], "currency": india_shares_res.get("currency"),
         "unit": india_shares_res.get("unit"), **s}
        for s in india_shares_res.get("shares", [])[:10]
    ]

    corridor_trade = [
        {
            "label": seg.replace("_", " "), "segment": seg,
            "value_usd_mn": round(v["value_mn"], 3),
            "n_sources": len(v["points"]),
            "sources": sorted({dp.source_name for dp in v["points"]}),
        }
        for seg, v in sorted(
            charts._corridor_trade_data().items(), key=lambda kv: kv[1]["value_mn"], reverse=True,
        )
    ]

    return {
        "korea_exports_by_segment": korea_exports,
        "india_listed_shares": india_shares,
        "india_shares_qualifier": india_shares_res.get("qualifier"),
        "corridor_trade_by_segment": corridor_trade,
    }


def build_insights() -> dict[str, dict]:
    """Copy /insights-authored analyst reads verbatim into the bundle.

    Pure serialization: data/manual/insights/<segment>.json is written by
    Claude (see commands/insights.md), never derived here. A segment with no
    insight file yet is simply omitted — the UI treats that as "not written
    yet", not an error.
    """
    if not INSIGHTS_DIR.exists():
        return {}
    out: dict[str, dict] = {}
    for path in sorted(INSIGHTS_DIR.glob("*.json")):
        with path.open(encoding="utf-8") as fh:
            out[path.stem] = json.load(fh)
    return out


def build_analysis() -> dict[str, dict]:
    """Copy /entry-analysis artifacts verbatim into the bundle.

    Pure serialization of data/manual/analysis/**/*.json (Claude-authored, see
    commands/entry-analysis.md) — no new logic. Keys are bundle-relative ids
    with "/" preserved (e.g. "porter_skincare", "profiles/amorepacific"), so
    the loader can address nested artifacts. Absent dir -> {} (not yet run).
    """
    if not ANALYSIS_DIR.exists():
        return {}
    out: dict[str, dict] = {}
    for path in sorted(ANALYSIS_DIR.rglob("*.json")):
        rel = path.relative_to(ANALYSIS_DIR).with_suffix("").as_posix()
        with path.open(encoding="utf-8") as fh:
            out[rel] = json.load(fh)
    return out


def build_findings() -> dict[str, dict]:
    """Copy the qualitative config/{key}_findings.yaml files verbatim into the bundle.

    Pure serialization, YAML -> JSON, of hand-written qualitative context
    (korea/india/corridor, and the [PREMIUM-SKIN] fit + demand files). Each is
    {topic: [{text, source, url}, ...]} and every url in them was actually
    fetched (CLAUDE.md rule 6). Globbed rather than named — the same convention
    lib/chat_index.py already uses — so a future phase's findings file reaches
    the dashboard with no code change here.

    Quantitative claims never live in these files; they are DataPoints in
    sources.csv and computed statistics in the analysis artifacts. Nothing in
    this function derives a figure.
    """
    out: dict[str, dict] = {}
    for path in sorted(CONFIG_DIR.glob("*_findings.yaml")):
        key = path.stem.removesuffix("_findings")
        with path.open(encoding="utf-8") as fh:
            out[key] = yaml.safe_load(fh) or {}
    return out


def build_json_schema() -> dict:
    """JSON Schema for DataPoint + SegmentFile, source for web/types/schema.ts.

    Pydantic already nests DataPoint under SegmentFile's $defs (SegmentFile has
    a data_points: list[DataPoint] field), so one call covers both models.
    """
    from lib.transforms.schema import SegmentFile

    return SegmentFile.model_json_schema()


def build_meta() -> dict:
    """Generation stamp, git SHA, taxonomy/segment names, FX rates, legends."""
    with TAXONOMY_PATH.open(encoding="utf-8") as fh:
        taxonomy = yaml.safe_load(fh)
    with EXCHANGE_RATES_PATH.open(encoding="utf-8") as fh:
        rates = yaml.safe_load(fh)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_sha": _git_sha(),
        "segments": [{"id": s["id"], "name": s["name"]} for s in taxonomy["segments"]],
        "geographies": taxonomy["geographies"],
        "exchange_rates": rates["rates"],
        "confidence_legend": CONFIDENCE_LEGEND,
        "value_basis_legend": VALUE_BASIS_LEGEND,
    }


def export_all() -> list[Path]:
    """Write the full web/public/data/*.json bundle.

    Returns:
        Every file path written.
    """
    written: list[Path] = []

    def emit(rel: str, data: object) -> None:
        path = WEB_DATA_DIR / rel
        _write_json(path, data)
        written.append(path)

    overview = full_context()
    _augment_market_sizes(overview["korea"])
    _augment_market_sizes(overview["india"])
    emit("overview.json", overview)
    emit("korea.json", build_geography_bundle("KR"))
    emit("india.json", build_geography_bundle("IN"))
    emit("corridor.json", corridor_context())
    emit("india_value_chain.json", india_value_chain_context())
    for seg, bundle in build_segments_bundle().items():
        emit(f"segments/{seg}.json", bundle)
    emit("sources.json", build_sources())
    emit("gaps.json", build_gaps())
    for seg, insight in build_insights().items():
        emit(f"insights/{seg}.json", insight)
    for rel, artifact in build_analysis().items():
        emit(f"analysis/{rel}.json", artifact)
    for key, findings in build_findings().items():
        emit(f"findings/{key}.json", findings)
    emit("chat_index.json", build_chat_index())
    charts_out = build_charts()
    for name, data in charts_out.items():
        emit(f"charts/{name}.json", data)
    emit("meta.json", build_meta())

    _write_json(SCHEMA_JSON_PATH, build_json_schema())
    written.append(SCHEMA_JSON_PATH)

    logger.info("Web export complete: %d files to %s", len(written), WEB_DATA_DIR)
    return written


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    paths = export_all()
    print(f"Wrote {len(paths)} files to {WEB_DATA_DIR}")
