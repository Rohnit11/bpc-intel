"""Report builders: full snapshot, corridor brief, Korea-vs-India comparison.

Templates render from lib/reports/_context.py, which reads only processed data
and the analysis layer. Reports are written to reports/latest/ and the prior
version archived to reports/archive/.
"""
from __future__ import annotations

import logging
import shutil
from datetime import date, datetime, timezone
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from lib.reports import _context, charts

logger = logging.getLogger("bpc_intel.reports")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = PROJECT_ROOT / "lib" / "reports" / "templates"
LATEST_DIR = PROJECT_ROOT / "reports" / "latest"
ARCHIVE_DIR = PROJECT_ROOT / "reports" / "archive"

_SEGMENTS = [
    "skincare", "sun_care", "colour_cosmetics", "fragrances", "hair_care",
    "bath_shower", "deodorants", "oral_care", "mens_grooming", "baby_child",
    "dermocosmetics", "emerging_adjacencies",
]


def _env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(enabled_extensions=(), default=False),
        trim_blocks=True, lstrip_blocks=True,
    )


def _archive_existing(name: str) -> None:
    """Move an existing latest/<name> into archive/ with a timestamp."""
    existing = LATEST_DIR / name
    if existing.exists():
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        shutil.copy2(existing, ARCHIVE_DIR / f"{existing.stem}_{stamp}{existing.suffix}")


def generate_full_report() -> str:
    """Render the full snapshot report with charts.

    Returns:
        Path to the written Markdown report.
    """
    LATEST_DIR.mkdir(parents=True, exist_ok=True)
    chart_paths = charts.generate_all()
    chart_names = [Path(p).name for p in chart_paths]
    ctx = _context.full_context()

    md = _env().get_template("full_report.md.j2").render(ctx=ctx, charts=chart_names)
    _archive_existing("snapshot.md")
    out = LATEST_DIR / "snapshot.md"
    out.write_text(md, encoding="utf-8")
    logger.info("Wrote full report to %s (%d chars, %d charts)", out, len(md), len(chart_names))
    return str(out)


def generate_corridor_brief() -> str:
    """Render the K-beauty corridor brief.

    Returns:
        Path to the written Markdown brief.
    """
    LATEST_DIR.mkdir(parents=True, exist_ok=True)
    ctx = {"generated": date.today().isoformat()}
    corridor = _context.corridor_context()
    md = _env().get_template("corridor_brief.md.j2").render(ctx=ctx, corridor=corridor)
    _archive_existing("corridor_brief.md")
    out = LATEST_DIR / "corridor_brief.md"
    out.write_text(md, encoding="utf-8")
    logger.info("Wrote corridor brief to %s (%d chars)", out, len(md))
    return str(out)


def generate_comparison(metric: str = "market_size") -> str:
    """Render a Korea-vs-India comparison for one metric.

    Args:
        metric: A DataPoint metric (default "market_size").

    Returns:
        Path to the written Markdown comparison.
    """
    LATEST_DIR.mkdir(parents=True, exist_ok=True)
    segments = []
    for seg in _SEGMENTS + ["total_bpc"]:
        kr = _context.segment_metric("KR", seg, metric)
        in_ = _context.segment_metric("IN", seg, metric)
        if kr or in_:
            segments.append({"name": seg, "kr": kr[0] if kr else None,
                             "in_": in_[0] if in_ else None})
    md = _env().get_template("comparison.md.j2").render(
        metric=metric, generated=date.today().isoformat(), segments=segments)
    out = LATEST_DIR / f"comparison_{metric}.md"
    out.write_text(md, encoding="utf-8")
    logger.info("Wrote comparison (%s) to %s", metric, out)
    return str(out)


def generate_india_value_chain_brief() -> str:
    """Render the India value-chain brief (pricing, sourcing, competition, demand).

    Returns:
        Path to the written Markdown brief.
    """
    LATEST_DIR.mkdir(parents=True, exist_ok=True)
    ctx = _context.india_value_chain_context()
    md = _env().get_template("india_value_chain.md.j2").render(ctx=ctx)
    _archive_existing("india_value_chain.md")
    out = LATEST_DIR / "india_value_chain.md"
    out.write_text(md, encoding="utf-8")
    logger.info("Wrote India value-chain brief to %s (%d chars)", out, len(md))
    return str(out)


def generate_segment_brief(geography: str, segment: str) -> str:
    """Render a one-page brief for a single geography × segment.

    Args:
        geography: "KR" or "IN".
        segment: Taxonomy segment id.

    Returns:
        Path to the written Markdown brief.
    """
    LATEST_DIR.mkdir(parents=True, exist_ok=True)
    points: list[dict] = []
    for metric in ("market_size", "growth_yoy", "cagr_forecast", "market_share",
                   "export_value", "production_value", "revenue", "channel_share",
                   "per_capita_spend"):
        points.extend(_context.segment_metric(geography, segment, metric))
    md = _env().get_template("segment_brief.md.j2").render(
        geography=geography, segment=segment,
        generated=date.today().isoformat(), points=points)
    out = LATEST_DIR / f"segment_{geography}_{segment}.md"
    out.write_text(md, encoding="utf-8")
    logger.info("Wrote segment brief %s/%s to %s", geography, segment, out)
    return str(out)


if __name__ == "__main__":
    import sys

    what = sys.argv[1] if len(sys.argv) > 1 else "full"
    if what == "full":
        print(generate_full_report())
    elif what == "corridor":
        print(generate_corridor_brief())
    elif what == "comparison":
        print(generate_comparison(sys.argv[2] if len(sys.argv) > 2 else "market_size"))
    elif what == "segment" and len(sys.argv) >= 4:
        print(generate_segment_brief(sys.argv[2], sys.argv[3]))
    elif what == "india":
        print(generate_india_value_chain_brief())
    else:
        print("Usage: python -m lib.reports.snapshot "
              "[full | corridor | comparison [metric] | segment <KR|IN> <segment> | india]")
