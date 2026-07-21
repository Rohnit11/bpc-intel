"""Multi-currency conversion using pinned rates from config/exchange_rates.yaml."""
from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path

import yaml

logger = logging.getLogger("bpc_intel.currency")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RATES_PATH = PROJECT_ROOT / "config" / "exchange_rates.yaml"


@lru_cache(maxsize=1)
def _load_rates() -> list[dict]:
    """Load pinned rates from config/exchange_rates.yaml.

    Returns:
        List of rate records: {base, quote, rate, date, source}.
    """
    with RATES_PATH.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)["rates"]


def _find_rate(from_currency: str, to_currency: str, rate_date: str | None) -> tuple[float, str]:
    """Find a conversion rate, direct or inverted.

    Args:
        from_currency: ISO code of the source currency.
        to_currency: ISO code of the target currency.
        rate_date: Optional specific rate date to require.

    Returns:
        (rate, rate_description) where rate_description records the pinned
        rate, its direction, and its date for auditability.

    Raises:
        KeyError: If no pinned rate exists for the pair.
    """
    for rec in _load_rates():
        if rate_date is not None and rec["date"] != rate_date:
            continue
        if rec["base"] == from_currency and rec["quote"] == to_currency:
            return rec["rate"], f"{rec['base']}/{rec['quote']}={rec['rate']} ({rec['date']})"
        if rec["base"] == to_currency and rec["quote"] == from_currency:
            return 1.0 / rec["rate"], (
                f"inverse of {rec['base']}/{rec['quote']}={rec['rate']} ({rec['date']})"
            )
    raise KeyError(
        f"No pinned rate for {from_currency}->{to_currency}"
        + (f" on {rate_date}" if rate_date else "")
        + f" in {RATES_PATH}"
    )


def convert(
    amount: float,
    from_currency: str,
    to_currency: str,
    rate_date: str | None = None,
) -> tuple[float, str]:
    """Convert an amount between currencies using pinned rates.

    Cross rates (e.g. KRW->INR) are computed via USD when no direct pin exists.

    Args:
        amount: The amount in from_currency.
        from_currency: ISO code, e.g. "KRW".
        to_currency: ISO code, e.g. "USD".
        rate_date: Optional specific rate date (YYYY-MM-DD) to require.

    Returns:
        (converted_amount, rate_used) — rate_used documents the exact pinned
        rate(s) and date(s) applied.

    Raises:
        KeyError: If no usable pinned rate chain exists for the pair.
    """
    if from_currency == to_currency:
        return amount, "identity (no conversion)"
    try:
        rate, desc = _find_rate(from_currency, to_currency, rate_date)
        return amount * rate, desc
    except KeyError:
        # Cross via USD
        leg1, desc1 = _find_rate(from_currency, "USD", rate_date)
        leg2, desc2 = _find_rate("USD", to_currency, rate_date)
        return amount * leg1 * leg2, f"cross via USD: {desc1}; {desc2}"


__all__ = ["convert"]
