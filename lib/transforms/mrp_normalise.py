"""MRP <-> net realisation normalisation (India-specific).

Indian retail values are typically quoted MRP-inclusive; company revenues are
net of trade margins. The gap is 25-45% depending on category.
"""
from __future__ import annotations

import logging

logger = logging.getLogger("bpc_intel.mrp_normalise")

DEFAULT_MARGINS: dict[str, float] = {
    "skincare": 0.35, "colour_cosmetics": 0.40, "hair_care": 0.30,
    "fragrances": 0.45, "bath_shower": 0.25, "deodorants": 0.30,
    "oral_care": 0.25, "mens_grooming": 0.35, "baby_child": 0.30,
    "dermocosmetics": 0.38, "sun_care": 0.35, "emerging_adjacencies": 0.40,
}


def _resolve_margin(category: str, margin_assumption: float | None) -> float:
    """Pick the trade margin to apply for a category.

    Args:
        category: Taxonomy segment id.
        margin_assumption: Explicit margin override (0-1), or None for default.

    Returns:
        The margin as a fraction of MRP.

    Raises:
        KeyError: If category has no default margin and no override was given.
        ValueError: If the margin is outside (0, 1).
    """
    margin = margin_assumption if margin_assumption is not None else DEFAULT_MARGINS[category]
    if not 0.0 < margin < 1.0:
        raise ValueError(f"margin must be in (0, 1), got {margin}")
    return margin


def mrp_to_net_realisation(
    mrp_value: float,
    category: str,
    margin_assumption: float | None = None,
) -> tuple[float, float, str]:
    """Convert an MRP-basis value to net realisation.

    Args:
        mrp_value: Value on MRP (consumer retail) basis.
        category: Taxonomy segment id, used to pick the default margin.
        margin_assumption: Optional explicit margin override (fraction of MRP).

    Returns:
        (net_value, margin_used, methodology_note).
    """
    margin = _resolve_margin(category, margin_assumption)
    net = mrp_value * (1.0 - margin)
    note = (
        f"net_realisation = MRP x (1 - {margin:.2f}); margin "
        f"{'assumed from industry benchmark for ' + category if margin_assumption is None else 'explicitly supplied'}"
    )
    return net, margin, note


def net_realisation_to_mrp(
    net_value: float,
    category: str,
    margin_assumption: float | None = None,
) -> tuple[float, float, str]:
    """Convert a net-realisation value back to MRP basis (inverse).

    Args:
        net_value: Value on net-realisation basis.
        category: Taxonomy segment id, used to pick the default margin.
        margin_assumption: Optional explicit margin override (fraction of MRP).

    Returns:
        (mrp_value, margin_used, methodology_note).
    """
    margin = _resolve_margin(category, margin_assumption)
    mrp = net_value / (1.0 - margin)
    note = (
        f"MRP = net_realisation / (1 - {margin:.2f}); margin "
        f"{'assumed from industry benchmark for ' + category if margin_assumption is None else 'explicitly supplied'}"
    )
    return mrp, margin, note


__all__ = ["DEFAULT_MARGINS", "mrp_to_net_realisation", "net_realisation_to_mrp"]
