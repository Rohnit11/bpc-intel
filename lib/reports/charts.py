"""Chart generation (matplotlib) — saves PNGs to reports/latest/charts/.

Every chart draws only from processed DataPoints; nothing is hardcoded. Each
function returns the saved file path (or None if there is no data to plot).
"""
from __future__ import annotations

import logging
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt  # noqa: E402

from lib.analysis._load import load_points  # noqa: E402
from lib.analysis.share import compute_shares  # noqa: E402

logger = logging.getLogger("bpc_intel.charts")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHARTS_DIR = PROJECT_ROOT / "reports" / "latest" / "charts"

_SEGMENTS = [
    "skincare", "sun_care", "colour_cosmetics", "fragrances", "hair_care",
    "bath_shower", "deodorants", "oral_care", "mens_grooming", "baby_child",
    "dermocosmetics", "emerging_adjacencies",
]


def _ensure_dir(charts_dir: Path) -> Path:
    charts_dir.mkdir(parents=True, exist_ok=True)
    return charts_dir


def _korea_export_data() -> dict[str, "DataPoint"]:
    """Best export_value DataPoint (usd_bn) per Korea segment, for charting.

    Shared by the PNG chart below and lib/web_export.py's chart JSON, so both
    surfaces plot exactly the same picked figures.
    """
    data: dict[str, "DataPoint"] = {}
    for seg in _SEGMENTS:
        exports = [
            dp for dp in load_points("KR", seg)
            if dp.metric == "export_value" and dp.unit == "usd_bn"
            and "World" not in (dp.notes or "") and "India" not in (dp.notes or "")
        ]
        if not exports:
            # fall back to any export figure (e.g. MFDS totals)
            exports = [dp for dp in load_points("KR", seg)
                       if dp.metric == "export_value" and dp.unit == "usd_bn"]
        if exports:
            data[seg] = max(exports, key=lambda d: d.value)
    return data


def korea_export_by_segment(charts_dir: str | Path = CHARTS_DIR) -> str | None:
    """Bar chart of Korea export values (EXPORT_FOB) by segment, latest year.

    Returns:
        Path to the saved PNG, or None if no export data.
    """
    charts_dir = _ensure_dir(Path(charts_dir))
    data = _korea_export_data()
    if not data:
        return None

    items = sorted(data.items(), key=lambda kv: kv[1].value, reverse=True)
    labels = [k.replace("_", " ") for k, _ in items]
    values = [dp.value for _, dp in items]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.barh(labels, values, color="#2b6cb0")
    ax.invert_yaxis()
    ax.set_xlabel("Export value (US$ bn, FOB)")
    ax.set_title("Korea cosmetics exports by segment (latest available)")
    for i, v in enumerate(values):
        ax.text(v, i, f" {v:g}", va="center", fontsize=8)
    fig.tight_layout()
    out = charts_dir / "korea_exports_by_segment.png"
    fig.savefig(out, dpi=120)
    plt.close(fig)
    logger.info("Saved chart %s", out)
    return str(out)


def india_listed_player_shares(charts_dir: str | Path = CHARTS_DIR) -> str | None:
    """Bar chart of India listed-player revenue shares (with coverage caveat).

    Returns:
        Path to the saved PNG, or None if no share data.
    """
    charts_dir = _ensure_dir(Path(charts_dir))
    res = compute_shares("IN", "total_bpc")
    if not res.get("shares"):
        return None
    shares = res["shares"][:8]
    labels = [s["company"].split(" (")[0] for s in shares]
    values = [s["share_pct"] for s in shares]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    colors = ["#c05621" if s["non_pure_play"] else "#2b6cb0" for s in shares]
    ax.bar(labels, values, color=colors)
    ax.set_ylabel("Share of summed listed-player revenue (%)")
    ax.set_title("India: revenue share of listed BPC players\n(orange = conglomerate, non-BPC-pure)")
    ax.tick_params(axis="x", rotation=30)
    for i, v in enumerate(values):
        ax.text(i, v, f"{v:g}%", ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    out = charts_dir / "india_listed_shares.png"
    fig.savefig(out, dpi=120)
    plt.close(fig)
    logger.info("Saved chart %s", out)
    return str(out)


def _corridor_trade_data() -> dict[str, dict]:
    """Summed [CORRIDOR] Korea->India export value (US$ mn) per segment.

    Returns {segment: {"value_mn": float, "points": [DataPoint, ...]}} so
    callers can both plot the total and cite every contributing DataPoint.
    Shared by the PNG chart below and lib/web_export.py's chart JSON.
    """
    data: dict[str, dict] = {}
    for seg in _SEGMENTS + ["total_bpc"]:
        for dp in load_points("KR", seg):
            if (dp.metric == "export_value" and dp.notes
                    and "[CORRIDOR]" in dp.notes and "India" in dp.notes):
                bucket = data.setdefault(seg, {"value_mn": 0.0, "points": []})
                bucket["value_mn"] += dp.value * 1000  # bn -> mn
                bucket["points"].append(dp)
    return {k: v for k, v in data.items() if k != "total_bpc" and v["value_mn"] > 0}


def corridor_trade_by_hs(charts_dir: str | Path = CHARTS_DIR) -> str | None:
    """Bar chart of Korea->India cosmetics exports by segment (corridor).

    Returns:
        Path to the saved PNG, or None if no corridor trade data.
    """
    charts_dir = _ensure_dir(Path(charts_dir))
    data = _corridor_trade_data()
    if not data:
        return None

    items = sorted(data.items(), key=lambda kv: kv[1]["value_mn"], reverse=True)
    labels = [k.replace("_", " ") for k, _ in items]
    values = [v["value_mn"] for _, v in items]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.barh(labels, values, color="#6b46c1")
    ax.invert_yaxis()
    ax.set_xlabel("Korea → India exports (US$ mn, 2024, UN Comtrade)")
    ax.set_title("K-beauty corridor: Korea → India cosmetics exports by segment")
    for i, v in enumerate(values):
        ax.text(v, i, f" {v:.2f}", va="center", fontsize=8)
    fig.tight_layout()
    out = charts_dir / "corridor_trade_by_segment.png"
    fig.savefig(out, dpi=120)
    plt.close(fig)
    logger.info("Saved chart %s", out)
    return str(out)


def generate_all(charts_dir: str | Path = CHARTS_DIR) -> list[str]:
    """Generate every chart; return the list of paths actually written."""
    paths = [
        korea_export_by_segment(charts_dir),
        india_listed_player_shares(charts_dir),
        corridor_trade_by_hs(charts_dir),
    ]
    return [p for p in paths if p]


__all__ = [
    "korea_export_by_segment", "india_listed_player_shares",
    "corridor_trade_by_hs", "generate_all",
]
