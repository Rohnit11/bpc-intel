"""Market-share computation from summed company revenues.

Always emits a coverage qualifier: shares are of the summed listed-player
base, not the true market, and conglomerate revenues are not BPC-pure.
"""
from __future__ import annotations

import logging

from lib.analysis._load import company_role, latest_company_revenues, load_points

logger = logging.getLogger("bpc_intel.share")

_NON_PURE_PLAY = {"Hindustan Unilever", "Godrej Consumer Products", "LG H&H"}


def compute_shares(geography: str, segment: str = "total_bpc") -> dict:
    """Compute each company's share of the summed listed-player revenue base.

    Args:
        geography: "KR" or "IN".
        segment: Segment id (company revenues live at total_bpc).

    Returns:
        Dict with the shared currency/unit, a ranked list of
        {company, revenue, share_pct}, and a mandatory qualifier. Companies
        whose currency/unit differ from the majority are excluded and named.
    """
    revs = latest_company_revenues(load_points(geography, segment))
    if not revs:
        return {"geography": geography, "segment": segment, "shares": [],
                "qualifier": "No company revenues available."}

    # Brand market share compares BRAND OWNERS only. ODM manufacturers and
    # retailers operate at different value-chain levels — their revenue is not
    # a brand share, so exclude and name them.
    non_brand = {n: company_role(n) for n in revs if company_role(n) in ("odm", "retailer")}
    brand_revs = {n: dp for n, dp in revs.items() if n not in non_brand}
    if not brand_revs:
        return {"geography": geography, "segment": segment, "shares": [],
                "qualifier": f"No brand-owner revenues (only {', '.join(non_brand)})."}

    from collections import Counter
    combos = Counter((dp.currency, dp.unit) for dp in brand_revs.values())
    (currency, unit), _ = combos.most_common(1)[0]
    included = {n: dp for n, dp in brand_revs.items() if (dp.currency, dp.unit) == (currency, unit)}
    excluded = sorted(n for n, dp in brand_revs.items() if (dp.currency, dp.unit) != (currency, unit))

    base = sum(dp.value for dp in included.values())
    shares = sorted(
        ({"company": n, "revenue": dp.value, "period": dp.period,
          "share_pct": round(dp.value / base * 100.0, 1) if base else 0.0,
          "non_pure_play": n in _NON_PURE_PLAY}
         for n, dp in included.items()),
        key=lambda s: s["share_pct"], reverse=True,
    )

    coverage = round(
        (1 - len([1 for n in included if n in _NON_PURE_PLAY]) / len(included)) * 100, 0
    ) if included else 0
    qualifier = (
        f"Shares of summed revenue for {len(included)} listed BRAND OWNERS "
        f"({currency} {unit}, NET_REALISATION). Does NOT include "
        "unorganised/unlisted players. "
    )
    if any(s["non_pure_play"] for s in shares):
        qualifier += (
            "Conglomerate members (HUL/Godrej/LG H&H) carry non-BPC revenue, "
            "so their shares overstate BPC position. "
        )
    if non_brand:
        roles = ', '.join(f"{n} ({r})" for n, r in sorted(non_brand.items()))
        qualifier += (
            f"Excluded as different value-chain levels (not brand shares): {roles}. "
        )
    if excluded:
        qualifier += f"Excluded (different currency/unit): {', '.join(excluded)}. "

    logger.info("Shares %s/%s: %d players, base %s %s",
                geography, segment, len(included), round(base, 2), unit)
    return {
        "geography": geography, "segment": segment,
        "currency": currency, "unit": unit, "base": round(base, 3),
        "shares": shares, "qualifier": qualifier.strip(),
    }


__all__ = ["compute_shares"]
