"""Analysis-layer tests: growth math, sizing reconciliation, shares."""
from __future__ import annotations

from datetime import date

import pytest

from lib.analysis import share, sizing
from lib.analysis.growth import cagr, indexed_growth, yoy_growth
from lib.transforms.schema import DataPoint


class TestGrowth:
    def test_cagr_doubling_over_3y(self):
        assert cagr(100, 200, 3) == pytest.approx(25.99, abs=0.01)

    def test_cagr_flat(self):
        assert cagr(100, 100, 5) == pytest.approx(0.0)

    def test_yoy(self):
        assert yoy_growth(112.3, 100) == pytest.approx(12.3, abs=0.01)

    def test_yoy_zero_prior_raises(self):
        with pytest.raises(ValueError):
            yoy_growth(100, 0)

    def test_cagr_nonpositive_raises(self):
        with pytest.raises(ValueError):
            cagr(0, 100, 3)

    def test_indexed(self):
        series = [
            _rev("Testco", "FY22", 100.0), _rev("Testco", "FY23", 120.0),
            _rev("Testco", "FY24", 150.0),
        ]
        out = indexed_growth(series, "FY22")
        idx = {r["period"]: r["index"] for r in out}
        assert idx["FY22"] == 100.0 and idx["FY24"] == 150.0

    def test_indexed_missing_base_raises(self):
        with pytest.raises(ValueError):
            indexed_growth([_rev("X", "FY22", 100.0)], "FY19")


def _size(geo, seg, value, basis="RETAIL", conf="HIGH", unit="usd_bn",
          currency="USD", period="2024") -> DataPoint:
    return DataPoint(
        geography=geo, segment=seg, metric="market_size", value=value, unit=unit,
        currency=currency, period=period, period_type="CY", value_basis=basis,
        source_name="Test", date_accessed=date(2026, 7, 22), confidence=conf,
    )


def _rev(company, period, value, geo="IN", currency="INR", unit="inr_cr") -> DataPoint:
    return DataPoint(
        geography=geo, segment="total_bpc", metric="revenue", value=value, unit=unit,
        currency=currency, period=period, period_type="FY", value_basis="NET_REALISATION",
        source_name="Test", date_accessed=date(2026, 7, 22), confidence="HIGH",
        notes=f"Company: {company} — test",
    )


class TestTopDown:
    def test_prefers_retail_then_confidence(self, tmp_path, monkeypatch):
        _write(tmp_path, monkeypatch, "IN", "skincare", [
            _size("IN", "skincare", 10.0, basis="NET_REALISATION", conf="HIGH"),
            _size("IN", "skincare", 12.0, basis="RETAIL", conf="LOW"),
        ])
        best = sizing.top_down_size("IN", "skincare")
        assert best.value == 12.0  # RETAIL wins over higher confidence

    def test_none_when_absent(self, tmp_path, monkeypatch):
        _write(tmp_path, monkeypatch, "IN", "fragrances", [])
        assert sizing.top_down_size("IN", "fragrances") is None

    def test_excludes_corridor_subset_and_forecasts(self, tmp_path, monkeypatch):
        corridor = _size("IN", "total_bpc", 1.5, currency="USD", unit="usd_bn", period="2030")
        corridor.notes = "[CORRIDOR] K-beauty in India 2030 forecast"
        _write(tmp_path, monkeypatch, "IN", "total_bpc", [
            corridor,
            _size("IN", "total_bpc", 33.08, currency="USD", unit="usd_bn",
                  conf="MEDIUM", period="2025"),
        ])
        best = sizing.top_down_size("IN", "total_bpc")
        assert best.value == 33.08  # corridor subset + forecast excluded

    def test_excludes_channel_gmv_from_total(self, tmp_path, monkeypatch):
        # A channel GMV figure (larger, more recent, RETAIL) must NOT be
        # picked as the market total — it sizes one channel, not the market.
        channel = _size("IN", "total_bpc", 56000.0, unit="inr_cr", currency="INR",
                        conf="MEDIUM", period="FY26")
        channel.notes = "Channel: e-commerce (all online) — India online BPC market"
        _write(tmp_path, monkeypatch, "IN", "total_bpc", [
            channel,
            _size("IN", "total_bpc", 33.08, currency="USD", unit="usd_bn",
                  conf="MEDIUM", period="2025"),
        ])
        best = sizing.top_down_size("IN", "total_bpc")
        assert best.value == 33.08  # channel GMV excluded from the total


class TestBottomUp:
    def test_sums_brand_owners_latest_per_company(self, tmp_path, monkeypatch):
        _write(tmp_path, monkeypatch, "IN", "total_bpc", [
            _rev("Nykaa", "FY25", 10022.0),               # retailer -> excluded
            _rev("Hindustan Unilever", "FY24", 60000.0),
            _rev("Hindustan Unilever", "FY25", 63000.0),  # latest wins over FY24
            _rev("Honasa", "FY25", 2067.0),
        ])
        bu = sizing.bottom_up_size("IN", "total_bpc")
        # Nykaa is a retailer — summing it with the brands it sells double-counts.
        assert "Nykaa (FSN E-Commerce)" not in bu["companies"]
        assert "Nykaa (FSN E-Commerce)" in bu["excluded_value_chain"]
        # Brand owners only, latest period per company: HUL FY25 + Honasa.
        assert bu["companies"]["Hindustan Unilever"] == 63000.0
        assert bu["value"] == pytest.approx(65067.0)
        assert "Hindustan Unilever" in bu["non_pure_play"]
        assert "NOT a market size" in bu["qualifier"]


class TestReconcile:
    def test_flags_basis_mismatch_no_numeric_gap(self, tmp_path, monkeypatch):
        _write(tmp_path, monkeypatch, "IN", "total_bpc", [
            _size("IN", "total_bpc", 30.0, basis="RETAIL", currency="USD", unit="usd_bn"),
            _rev("Hindustan Unilever", "FY25", 63000.0),
        ])
        td = sizing.top_down_size("IN", "total_bpc")
        bu = sizing.bottom_up_size("IN", "total_bpc")
        rep = sizing.reconcile(td, bu)
        assert rep["gap_pct"] is None  # not comparable
        assert any("Value basis" in m or "Unit/currency" in m for m in rep["mismatches"])
        assert any("non-pure-play" in m for m in rep["mismatches"])
        assert rep["publishable"] is False

    def test_clean_reconcile_within_threshold(self):
        td = _size("KR", "skincare", 100.0, basis="RETAIL", currency="USD", unit="usd_bn")
        bu = {"currency": "USD", "unit": "usd_bn", "value": 90.0,
              "value_basis": "RETAIL", "non_pure_play": [], "companies": {}}
        rep = sizing.reconcile(td, bu)
        assert rep["gap_pct"] == pytest.approx(10.0)
        assert rep["publishable"] is True

    def test_gap_over_threshold_not_publishable(self):
        td = _size("KR", "skincare", 100.0, basis="RETAIL", currency="USD", unit="usd_bn")
        bu = {"currency": "USD", "unit": "usd_bn", "value": 50.0,
              "value_basis": "RETAIL", "non_pure_play": [], "companies": {}}
        rep = sizing.reconcile(td, bu)
        assert rep["gap_pct"] == pytest.approx(50.0)
        assert rep["publishable"] is False
        assert any("exceeds 20%" in m for m in rep["mismatches"])


class TestShares:
    def test_shares_sum_to_100_with_qualifier(self, tmp_path, monkeypatch):
        _write(tmp_path, monkeypatch, "IN", "total_bpc", [
            _rev("Nykaa", "FY25", 10000.0), _rev("Honasa", "FY25", 2000.0),
            _rev("Hindustan Unilever", "FY25", 8000.0),
        ])
        res = share.compute_shares("IN", "total_bpc")
        assert sum(s["share_pct"] for s in res["shares"]) == pytest.approx(100.0, abs=0.2)
        # Nykaa is a retailer/platform -> excluded from BRAND shares; HUL leads.
        assert res["shares"][0]["company"] == "Hindustan Unilever"
        assert "Nykaa (FSN E-Commerce)" in res["qualifier"]
        assert "unorganised" in res["qualifier"]


# --- helpers to redirect the analysis loader to a temp processed dir ---
def _write(tmp_path, monkeypatch, geo, seg, points):
    import json

    import lib.analysis._load as loader
    processed = tmp_path / "processed"
    processed.mkdir(exist_ok=True)
    payload = {
        "geography": geo, "segment": seg, "last_updated": "2026-07-22",
        "data_points": [json.loads(p.model_dump_json()) for p in points],
    }
    (processed / f"{geo}_{seg}.json").write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(loader, "PROCESSED_DIR", processed)
