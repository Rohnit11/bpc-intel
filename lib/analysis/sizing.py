"""Market sizing: top-down, bottom-up, and their reconciliation.

The reconciliation is deliberately conservative. Bottom-up sizing by summing
listed-company revenues is NOT a clean market size in this domain because:
  * Conglomerates (HUL, Godrej, LG H&H) report revenue far beyond BPC.
  * Company revenue is NET_REALISATION; market sizes are usually RETAIL.
  * Listed players exclude unorganised/unlisted competitors.
So reconcile() surfaces the gap AND names the definitional mismatches rather
than pretending to a single number (CLAUDE.md rule 7).
"""
from __future__ import annotations

import logging
from datetime import date

from lib.analysis._load import latest_company_revenues, load_points, period_end_year
from lib.transforms.schema import DataPoint

logger = logging.getLogger("bpc_intel.sizing")

_CONFIDENCE_RANK = {"HIGH": 3, "MEDIUM": 2, "LOW": 1, "ESTIMATE": 0}

# Conglomerates whose reported revenue materially exceeds their BPC business.
_NON_PURE_PLAY = {
    "Hindustan Unilever", "Godrej Consumer Products", "LG H&H",
}


def top_down_size(geography: str, segment: str) -> DataPoint | None:
    """Best available total-market figure for a geography × segment.

    Prefers RETAIL basis, then higher confidence, then more recent period.

    Args:
        geography: "KR" or "IN".
        segment: Taxonomy segment id (or "total_bpc").

    Returns:
        The chosen market_size DataPoint, or None if none exist.
    """
    current_year = date.today().year
    sizes = [
        dp for dp in load_points(geography, segment)
        if dp.metric == "market_size"
        # [CORRIDOR] figures are a K-beauty subset, not the segment total.
        and not (dp.notes and "[CORRIDOR]" in dp.notes)
    ]
    if not sizes:
        return None

    def key(dp: DataPoint) -> tuple:
        end_year = period_end_year(dp.period)
        return (
            0 if end_year > current_year else 1,   # prefer actuals over forecasts
            1 if dp.value_basis == "RETAIL" else 0,
            _CONFIDENCE_RANK.get(dp.confidence, 0),
            end_year,
        )

    best = max(sizes, key=key)
    logger.info("Top-down %s/%s: %s %s (%s, %s, %s)", geography, segment,
                best.value, best.unit, best.value_basis, best.confidence, best.source_name)
    return best


def bottom_up_size(geography: str, segment: str) -> dict | None:
    """Sum of latest listed-company revenues, with a coverage qualifier.

    Args:
        geography: "KR" or "IN".
        segment: Taxonomy segment id. Company revenues are stored at the
            total_bpc level, so bottom-up is meaningful primarily there.

    Returns:
        Dict with total, currency/unit, contributing companies, and an
        explicit qualifier string; or None if no company revenues exist.
    """
    points = load_points(geography, segment)
    revs = latest_company_revenues(points)
    if not revs:
        return None

    # Only sum revenues sharing one currency+unit (don't mix KRW tn with INR cr).
    from collections import Counter
    combos = Counter((dp.currency, dp.unit) for dp in revs.values())
    (currency, unit), _ = combos.most_common(1)[0]
    included = {n: dp for n, dp in revs.items() if (dp.currency, dp.unit) == (currency, unit)}
    excluded = {n: dp for n, dp in revs.items() if (dp.currency, dp.unit) != (currency, unit)}

    total = sum(dp.value for dp in included.values())
    non_pure = sorted(n for n in included if n in _NON_PURE_PLAY)

    qualifier = (
        f"Sum of latest reported revenue for {len(included)} listed players "
        f"({currency} {unit}), NET_REALISATION basis. Coverage excludes "
        "unorganised/unlisted competitors. NOT a market size: "
    )
    if non_pure:
        qualifier += (
            f"{', '.join(non_pure)} report revenue well beyond BPC "
            "(conglomerate/total-company figures). "
        )
    if excluded:
        qualifier += f"Excluded (different currency/unit): {', '.join(sorted(excluded))}. "

    result = {
        "geography": geography, "segment": segment,
        "value": round(total, 3), "currency": currency, "unit": unit,
        "value_basis": "NET_REALISATION",
        "companies": {n: dp.value for n, dp in included.items()},
        "non_pure_play": non_pure,
        "qualifier": qualifier.strip(),
    }
    logger.info("Bottom-up %s/%s: %s %s from %d companies",
                geography, segment, result["value"], unit, len(included))
    return result


def reconcile(td: DataPoint | None, bu: dict | None) -> dict:
    """Compare top-down and bottom-up, compute the gap, name the mismatches.

    Args:
        td: Top-down DataPoint (from top_down_size).
        bu: Bottom-up dict (from bottom_up_size).

    Returns:
        A reconciliation report: values, gap %, publishable flag, and a list
        of definitional mismatches. Per CLAUDE.md rule 7, a gap >20% is
        flagged not-publishable until the mismatch is resolved.
    """
    report: dict = {
        "top_down": None if td is None else {
            "value": td.value, "unit": td.unit, "currency": td.currency,
            "value_basis": td.value_basis, "confidence": td.confidence,
            "period": td.period, "source": td.source_name,
        },
        "bottom_up": bu,
        "gap_pct": None,
        "publishable": False,
        "mismatches": [],
        "date": date.today().isoformat(),
    }
    mism = report["mismatches"]

    if td is None or bu is None:
        report["note"] = "Cannot reconcile: " + (
            "no top-down figure. " if td is None else ""
        ) + ("no bottom-up figure. " if bu is None else "")
        return report

    if (td.currency, td.unit) != (bu["currency"], bu["unit"]):
        mism.append(
            f"Unit/currency differ (top-down {td.currency} {td.unit} vs "
            f"bottom-up {bu['currency']} {bu['unit']}) - convert before comparing."
        )
    if td.value_basis != bu["value_basis"]:
        mism.append(
            f"Value basis differs (top-down {td.value_basis} vs bottom-up "
            f"{bu['value_basis']}). India RETAIL vs NET_REALISATION differ by the "
            "MRP trade margin (lib/transforms/mrp_normalise.py)."
        )
    if bu["non_pure_play"]:
        mism.append(
            f"Bottom-up base is inflated by non-pure-play conglomerates "
            f"({', '.join(bu['non_pure_play'])}) reporting non-BPC revenue."
        )

    # Only compute a numeric gap when bases are actually comparable.
    if not mism:
        gap = abs(td.value - bu["value"]) / td.value * 100.0
        report["gap_pct"] = round(gap, 1)
        report["publishable"] = gap <= 20.0
        if gap > 20.0:
            mism.append(f"Gap {gap:.1f}% exceeds 20% threshold — do not publish; investigate.")
    else:
        report["note"] = (
            "Numeric gap not computed: bases are not directly comparable "
            "(see mismatches). Bottom-up here is a coverage indicator, not a "
            "market-size cross-check."
        )
    return report


__all__ = ["top_down_size", "bottom_up_size", "reconcile"]
