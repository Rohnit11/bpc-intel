"""Value-basis tagging, comparability checks, and basis normalisation."""
from __future__ import annotations

import logging

from lib.transforms.mrp_normalise import mrp_to_net_realisation, net_realisation_to_mrp
from lib.transforms.schema import DataPoint

logger = logging.getLogger("bpc_intel.value_basis")

VALID_BASES = {"RETAIL", "NET_REALISATION", "WHOLESALE", "EXPORT_FOB", "PRODUCTION"}

# India RETAIL<->NET_REALISATION is convertible via MRP margins.
# Korea EXPORT_FOB / PRODUCTION / RETAIL are structurally different measures.
_CONVERTIBLE_PAIRS = {
    frozenset({"RETAIL", "NET_REALISATION"}),
}


def tag_value_basis(value: float, basis: str) -> dict:
    """Wrap a number with its value-basis metadata.

    Args:
        value: The numeric value.
        basis: One of VALID_BASES.

    Returns:
        {"value": value, "value_basis": basis}.

    Raises:
        ValueError: If basis is not a recognised value basis.
    """
    if basis not in VALID_BASES:
        raise ValueError(f"Unknown value basis '{basis}'; must be one of {sorted(VALID_BASES)}")
    return {"value": value, "value_basis": basis}


def are_comparable(dp1: DataPoint, dp2: DataPoint) -> tuple[bool, str]:
    """Determine whether two data points can be directly compared.

    Args:
        dp1: First data point.
        dp2: Second data point.

    Returns:
        (comparable, reason).
    """
    if dp1.metric != dp2.metric:
        return False, f"different metrics ({dp1.metric} vs {dp2.metric})"
    if dp1.value_basis != dp2.value_basis:
        pair = frozenset({dp1.value_basis, dp2.value_basis})
        if pair in _CONVERTIBLE_PAIRS:
            return False, (
                f"different value bases ({dp1.value_basis} vs {dp2.value_basis}) — "
                "convertible via lib/transforms/mrp_normalise.py; normalise first"
            )
        return False, (
            f"different value bases ({dp1.value_basis} vs {dp2.value_basis}) — "
            "structurally different measures, NOT convertible"
        )
    if dp1.currency != dp2.currency:
        return False, (
            f"different currencies ({dp1.currency} vs {dp2.currency}) — "
            "convert via lib/transforms/currency.py first"
        )
    if dp1.unit != dp2.unit:
        return False, f"different units ({dp1.unit} vs {dp2.unit})"
    return True, "same metric, basis, currency and unit"


def normalise_to_basis(dp: DataPoint, target_basis: str) -> DataPoint:
    """Return a copy of a DataPoint converted to a target value basis.

    Only India RETAIL<->NET_REALISATION conversion is supported (via MRP
    margins). Korea EXPORT_FOB / PRODUCTION / RETAIL are flagged
    non-convertible.

    Args:
        dp: The data point to convert.
        target_basis: The desired value basis.

    Returns:
        A new DataPoint on the target basis, confidence downgraded to
        ESTIMATE with methodology recorded.

    Raises:
        ValueError: If the conversion is not supported.
    """
    if target_basis not in VALID_BASES:
        raise ValueError(f"Unknown target basis '{target_basis}'")
    if dp.value_basis == target_basis:
        return dp

    pair = frozenset({dp.value_basis, target_basis})
    if pair not in _CONVERTIBLE_PAIRS:
        raise ValueError(
            f"{dp.value_basis} -> {target_basis} is not convertible: these are "
            "structurally different measures (e.g. Korea export FOB vs domestic retail)."
        )
    if dp.geography != "IN":
        raise ValueError(
            "RETAIL<->NET_REALISATION conversion uses India MRP trade margins and "
            f"applies to geography IN only (got {dp.geography})."
        )

    if dp.value_basis == "RETAIL" and target_basis == "NET_REALISATION":
        new_value, margin, note = mrp_to_net_realisation(dp.value, dp.segment)
    else:
        new_value, margin, note = net_realisation_to_mrp(dp.value, dp.segment)

    return dp.model_copy(update={
        "value": new_value,
        "value_basis": target_basis,
        "confidence": "ESTIMATE",
        "methodology": (
            f"Converted from {dp.value_basis} using assumed trade margin "
            f"{margin:.0%}. {note}. Original value: {dp.value} ({dp.value_basis})."
        ),
    })


__all__ = ["VALID_BASES", "tag_value_basis", "are_comparable", "normalise_to_basis"]
