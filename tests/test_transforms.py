"""Transform tests: currency, MRP normalisation, fiscal year, value basis."""
from __future__ import annotations

from datetime import date

import pytest

from lib.transforms.currency import convert
from lib.transforms.fiscal_year import align_periods, fy_to_cy_range, parse_period
from lib.transforms.mrp_normalise import (
    DEFAULT_MARGINS,
    mrp_to_net_realisation,
    net_realisation_to_mrp,
)
from lib.transforms.schema import DataPoint
from lib.transforms.value_basis import are_comparable, normalise_to_basis, tag_value_basis


class TestCurrency:
    def test_identity(self):
        amount, rate = convert(100.0, "USD", "USD")
        assert amount == 100.0
        assert "identity" in rate

    def test_usd_to_krw_and_back(self):
        krw, rate_used = convert(1.0, "USD", "KRW")
        assert krw > 1000
        assert "USD/KRW" in rate_used
        usd, _ = convert(krw, "KRW", "USD")
        assert usd == pytest.approx(1.0)

    def test_usd_to_inr_records_rate_and_date(self):
        inr, rate_used = convert(1.0, "USD", "INR")
        assert inr > 50
        assert "2026" in rate_used  # date recorded for auditability

    def test_cross_rate_via_usd(self):
        inr, rate_used = convert(1_000_000.0, "KRW", "INR")
        assert inr > 0
        assert "cross via USD" in rate_used

    def test_missing_pair_raises(self):
        with pytest.raises(KeyError):
            convert(1.0, "EUR", "KRW")


class TestMrpNormalise:
    def test_round_trip(self):
        for category in DEFAULT_MARGINS:
            net, margin, _ = mrp_to_net_realisation(100.0, category)
            mrp, _, _ = net_realisation_to_mrp(net, category)
            assert mrp == pytest.approx(100.0), category
            assert 0.0 < margin < 1.0

    def test_skincare_default_margin(self):
        net, margin, note = mrp_to_net_realisation(100.0, "skincare")
        assert margin == 0.35
        assert net == pytest.approx(65.0)
        assert "benchmark" in note

    def test_explicit_margin_override(self):
        net, margin, note = mrp_to_net_realisation(100.0, "skincare", margin_assumption=0.30)
        assert margin == 0.30
        assert net == pytest.approx(70.0)
        assert "explicitly supplied" in note

    def test_unknown_category_raises(self):
        with pytest.raises(KeyError):
            mrp_to_net_realisation(100.0, "petcare")

    def test_bad_margin_raises(self):
        with pytest.raises(ValueError):
            mrp_to_net_realisation(100.0, "skincare", margin_assumption=1.5)


class TestFiscalYear:
    def test_fy24(self):
        assert fy_to_cy_range("FY24") == ("2023-04", "2024-03")

    def test_fy_4_digit(self):
        assert fy_to_cy_range("FY2025") == ("2024-04", "2025-03")

    def test_cy(self):
        p = parse_period("CY2024")
        assert p["period_type"] == "CY"
        assert (p["start"], p["end"]) == ("2024-01", "2024-12")

    def test_bare_year(self):
        assert parse_period("2024")["period_type"] == "CY"

    def test_half(self):
        p = parse_period("H1_2025")
        assert (p["start"], p["end"]) == ("2025-01", "2025-06")

    def test_range(self):
        p = parse_period("2020-2024")
        assert p["period_type"] == "range"
        assert (p["start"], p["end"]) == ("2020-01", "2024-12")

    def test_fy_quarter(self):
        p = parse_period("Q1_FY25")
        assert (p["start"], p["end"]) == ("2024-04", "2024-06")

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            parse_period("sometime in 2024")

    def test_align_kr_cy_vs_in_fy(self):
        note = align_periods("2024", "FY25")
        assert "overlap 2024-04..2024-12" in note

    def test_align_no_overlap(self):
        note = align_periods("2020", "FY25")
        assert "do not overlap" in note


def _dp(**overrides) -> DataPoint:
    base = dict(
        geography="IN",
        segment="skincare",
        metric="market_size",
        value=100.0,
        unit="inr_cr",
        currency="INR",
        period="FY25",
        period_type="FY",
        value_basis="RETAIL",
        source_name="Test",
        date_accessed=date(2026, 7, 21),
        confidence="MEDIUM",
    )
    base.update(overrides)
    return DataPoint(**base)


class TestValueBasis:
    def test_tag(self):
        assert tag_value_basis(5.0, "RETAIL") == {"value": 5.0, "value_basis": "RETAIL"}

    def test_tag_invalid(self):
        with pytest.raises(ValueError):
            tag_value_basis(5.0, "GMV")

    def test_comparable_same(self):
        ok, _ = are_comparable(_dp(), _dp(value=200.0))
        assert ok

    def test_not_comparable_different_basis(self):
        ok, reason = are_comparable(_dp(), _dp(value_basis="NET_REALISATION"))
        assert not ok
        assert "normalise first" in reason

    def test_not_comparable_structural(self):
        kr_export = _dp(geography="KR", currency="KRW", period="2024", period_type="CY",
                        value_basis="EXPORT_FOB", metric="market_size", unit="inr_cr")
        ok, reason = are_comparable(_dp(), kr_export)
        assert not ok
        assert "NOT convertible" in reason

    def test_normalise_retail_to_net(self):
        out = normalise_to_basis(_dp(), "NET_REALISATION")
        assert out.value == pytest.approx(65.0)  # skincare margin 0.35
        assert out.confidence == "ESTIMATE"
        assert out.methodology and "trade margin" in out.methodology

    def test_normalise_structural_raises(self):
        with pytest.raises(ValueError):
            normalise_to_basis(_dp(value_basis="EXPORT_FOB"), "RETAIL")

    def test_normalise_non_india_raises(self):
        kr = _dp(geography="KR", currency="KRW")
        with pytest.raises(ValueError):
            normalise_to_basis(kr, "NET_REALISATION")
