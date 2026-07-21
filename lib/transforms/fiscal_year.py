"""Fiscal-year / calendar-year period parsing and alignment.

India: FY24 = Apr 2023 - Mar 2024. Korea: calendar year (CY2024 or 2024).
"""
from __future__ import annotations

import logging
import re

logger = logging.getLogger("bpc_intel.fiscal_year")

_FY_RE = re.compile(r"^FY(\d{2}|\d{4})$")
_CY_RE = re.compile(r"^(?:CY)?(\d{4})$")
_HALF_RE = re.compile(r"^(H[12])_(\d{4})$")
_QUARTER_RE = re.compile(r"^(Q[1-4])_?(FY)?(\d{2,4})$")
_RANGE_RE = re.compile(r"^(\d{4})-(\d{4})$")


def _fy_end_year(digits: str) -> int:
    """Expand 2- or 4-digit FY digits to a full end year (FY24 -> 2024)."""
    year = int(digits)
    return year + 2000 if year < 100 else year


def parse_period(period_str: str) -> dict:
    """Parse a period string into structured metadata.

    Handles "FY24", "CY2024", "2024", "H1_2025", "Q3_FY25", "2020-2024".

    Args:
        period_str: The period string.

    Returns:
        Dict with keys: raw, period_type ("FY"|"CY"|"H1"|"H2"|"Q1".."Q4"|"range"),
        start (YYYY-MM), end (YYYY-MM).

    Raises:
        ValueError: If the string matches no known period format.
    """
    s = period_str.strip()

    m = _FY_RE.match(s)
    if m:
        end_year = _fy_end_year(m.group(1))
        return {
            "raw": s, "period_type": "FY",
            "start": f"{end_year - 1}-04", "end": f"{end_year}-03",
        }

    m = _HALF_RE.match(s)
    if m:
        half, year = m.group(1), int(m.group(2))
        start, end = (("01", "06") if half == "H1" else ("07", "12"))
        return {
            "raw": s, "period_type": half,
            "start": f"{year}-{start}", "end": f"{year}-{end}",
        }

    m = _QUARTER_RE.match(s)
    if m:
        quarter, is_fy, digits = m.group(1), m.group(2), m.group(3)
        q = int(quarter[1])
        if is_fy:
            end_year = _fy_end_year(digits)
            start_month = 4 + (q - 1) * 3  # FY Q1 starts April
            start_year = end_year - 1 if start_month <= 12 else end_year
            months = [(start_month + i - 1) % 12 + 1 for i in range(3)]
            years = [start_year + ((start_month + i - 1) // 12) for i in range(3)]
            return {
                "raw": s, "period_type": quarter,
                "start": f"{years[0]}-{months[0]:02d}",
                "end": f"{years[-1]}-{months[-1]:02d}",
            }
        year = _fy_end_year(digits)
        start_month = 1 + (q - 1) * 3
        return {
            "raw": s, "period_type": quarter,
            "start": f"{year}-{start_month:02d}", "end": f"{year}-{start_month + 2:02d}",
        }

    m = _RANGE_RE.match(s)
    if m:
        return {
            "raw": s, "period_type": "range",
            "start": f"{m.group(1)}-01", "end": f"{m.group(2)}-12",
        }

    m = _CY_RE.match(s)
    if m:
        year = int(m.group(1))
        return {"raw": s, "period_type": "CY", "start": f"{year}-01", "end": f"{year}-12"}

    raise ValueError(f"Unrecognised period format: '{period_str}'")


def fy_to_cy_range(fy_str: str) -> tuple[str, str]:
    """Convert an Indian FY label to its calendar month range.

    Args:
        fy_str: e.g. "FY24".

    Returns:
        (start, end) as YYYY-MM strings, e.g. ("2023-04", "2024-03").

    Raises:
        ValueError: If not a valid FY label.
    """
    parsed = parse_period(fy_str)
    if parsed["period_type"] != "FY":
        raise ValueError(f"'{fy_str}' is not a fiscal-year label")
    return parsed["start"], parsed["end"]


def align_periods(kr_period: str, in_period: str) -> str:
    """Describe the overlap/offset between a Korea period and an India period.

    Args:
        kr_period: Korea period string (typically CY).
        in_period: India period string (typically FY).

    Returns:
        A human-readable note on how the two periods align, for report captions.
    """
    kr = parse_period(kr_period)
    ind = parse_period(in_period)
    overlap_start = max(kr["start"], ind["start"])
    overlap_end = min(kr["end"], ind["end"])
    if overlap_start > overlap_end:
        return (
            f"Korea {kr_period} ({kr['start']}..{kr['end']}) and India {in_period} "
            f"({ind['start']}..{ind['end']}) do not overlap."
        )
    return (
        f"Korea {kr_period} covers {kr['start']}..{kr['end']}; India {in_period} covers "
        f"{ind['start']}..{ind['end']}; overlap {overlap_start}..{overlap_end}. "
        "Comparisons are directional, not period-exact."
    )


__all__ = ["parse_period", "fy_to_cy_range", "align_periods"]
