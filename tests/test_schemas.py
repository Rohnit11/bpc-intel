"""Schema conformance tests."""
from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from lib.transforms.schema import (
    DataPoint,
    SegmentFile,
    load_segment_file,
    save_segment_file,
    validate_data_point,
    validate_segment,
)


def _dp(**overrides) -> DataPoint:
    base = dict(
        geography="KR",
        segment="skincare",
        metric="market_size",
        value=13.0,
        unit="usd_bn",
        currency="USD",
        period="2024",
        period_type="CY",
        value_basis="RETAIL",
        source_name="Euromonitor",
        date_accessed=date(2026, 7, 21),
        confidence="HIGH",
    )
    base.update(overrides)
    return DataPoint(**base)


class TestValidDataPoints:
    def test_kr_retail_market_size(self):
        assert _dp().value == 13.0

    def test_in_fy_net_realisation(self):
        dp = _dp(geography="IN", currency="INR", period="FY25", period_type="FY",
                 value_basis="NET_REALISATION", unit="inr_cr", value=10022.0)
        assert dp.period_type == "FY"

    def test_export_fob_with_url(self):
        dp = _dp(metric="export_value", value_basis="EXPORT_FOB", value=11.43,
                 source_url="https://www.mfds.go.kr")
        assert dp.source_url is not None

    def test_estimate_with_methodology(self):
        dp = _dp(confidence="ESTIMATE", methodology="Top-down from Passport total x share")
        assert dp.confidence == "ESTIMATE"

    def test_sub_segment_and_tier(self):
        dp = _dp(sub_segment="sheet_masks", tier="mass")
        assert validate_data_point(dp) == (True, "")


class TestInvalidDataPoints:
    def test_bad_geography(self):
        with pytest.raises(ValidationError):
            _dp(geography="US")

    def test_bad_value_basis(self):
        with pytest.raises(ValidationError):
            _dp(value_basis="GMV")

    def test_estimate_without_methodology(self):
        with pytest.raises(ValidationError):
            _dp(confidence="ESTIMATE", methodology=None)

    def test_bad_metric(self):
        with pytest.raises(ValidationError):
            _dp(metric="brand_love_index")


class TestTaxonomyValidation:
    def test_known_segment(self):
        assert validate_segment("skincare")

    def test_known_sub_segment(self):
        assert validate_segment("skincare", "serums_ampoules")

    def test_unknown_segment(self):
        assert not validate_segment("petcare")

    def test_unknown_sub_segment(self):
        assert not validate_segment("skincare", "lipstick")

    def test_data_point_with_bad_segment_fails_full_validation(self):
        dp = _dp(segment="petcare")
        ok, reason = validate_data_point(dp)
        assert not ok and "taxonomy" in reason


class TestSegmentFileRoundTrip:
    def test_save_and_load(self, tmp_path):
        sf = SegmentFile(
            geography="KR", segment="skincare",
            last_updated=date(2026, 7, 21), data_points=[_dp()],
        )
        path = save_segment_file(sf, tmp_path / "KR_skincare.json")
        loaded = load_segment_file(path)
        assert loaded.geography == "KR"
        assert len(loaded.data_points) == 1
        assert loaded.data_points[0].value == 13.0
