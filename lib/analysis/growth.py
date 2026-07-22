"""Growth computations: CAGR, YoY, indexed series."""
from __future__ import annotations

import logging

from lib.transforms.schema import DataPoint

logger = logging.getLogger("bpc_intel.growth")


def cagr(start_value: float, end_value: float, years: float) -> float:
    """Compound annual growth rate as a percentage.

    Args:
        start_value: Value at the start of the period (must be > 0).
        end_value: Value at the end of the period (must be > 0).
        years: Number of years spanned (must be > 0).

    Returns:
        CAGR in percent (e.g. 12.5 for 12.5%).

    Raises:
        ValueError: If any input is non-positive.
    """
    if start_value <= 0 or end_value <= 0 or years <= 0:
        raise ValueError("cagr requires positive start_value, end_value, and years")
    return ((end_value / start_value) ** (1.0 / years) - 1.0) * 100.0


def yoy_growth(current: float, prior: float) -> float:
    """Year-on-year growth as a percentage.

    Args:
        current: Current-period value.
        prior: Prior-period value (must be non-zero).

    Returns:
        YoY growth in percent.

    Raises:
        ValueError: If prior is zero.
    """
    if prior == 0:
        raise ValueError("yoy_growth requires non-zero prior value")
    return (current / prior - 1.0) * 100.0


def indexed_growth(series: list[DataPoint], base_period: str) -> list[dict]:
    """Rebase a time series to 100 at a base period.

    Args:
        series: DataPoints sharing a metric/geography/segment, across periods.
        base_period: The period to set to 100 (e.g. "2020" or "FY20").

    Returns:
        List of {period, value, index} dicts, sorted by period. The base
        period has index 100.0.

    Raises:
        ValueError: If the base period is absent or has a non-positive value.
    """
    by_period = {dp.period: dp.value for dp in series}
    if base_period not in by_period:
        raise ValueError(f"base_period '{base_period}' not in series periods {list(by_period)}")
    base = by_period[base_period]
    if base <= 0:
        raise ValueError(f"base value for '{base_period}' must be positive, got {base}")
    return [
        {"period": p, "value": v, "index": round(v / base * 100.0, 1)}
        for p, v in sorted(by_period.items())
    ]


__all__ = ["cagr", "yoy_growth", "indexed_growth"]
