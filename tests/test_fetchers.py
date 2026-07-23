"""Fetcher smoke tests.

Network-dependent tests SKIP (not fail) when the source is unreachable or an
API key is unconfigured — per the build spec, that is acceptable. What must
always pass: module contracts (fetch/to_data_points/run exist), graceful
degradation (no key -> empty list, never an exception), and converter
correctness on canned payloads.
"""
from __future__ import annotations

from datetime import date

import pytest

from lib.fetchers import (
    academic_openalex,
    india_screener,
    korea_dart,
    news_tavily,
    qcommerce_tracker,
    trade_comtrade,
    trends_google,
)

ALL_FETCHERS = [
    news_tavily, korea_dart, india_screener, trade_comtrade,
    trends_google, academic_openalex, qcommerce_tracker,
]


class TestContract:
    @pytest.mark.parametrize("mod", ALL_FETCHERS, ids=lambda m: m.__name__)
    def test_implements_contract(self, mod):
        assert callable(mod.fetch)
        assert callable(mod.to_data_points)
        assert callable(mod.run)


class TestGracefulDegradation:
    def test_tavily_no_key_returns_empty(self, monkeypatch):
        monkeypatch.setattr(news_tavily, "load_api_key", lambda _: None)
        assert news_tavily.fetch() == []

    def test_dart_no_key_returns_empty(self, monkeypatch):
        monkeypatch.setattr(korea_dart, "load_api_key", lambda _: None)
        assert korea_dart.fetch() == []

    def test_qcommerce_disabled_returns_empty(self, monkeypatch):
        monkeypatch.setattr(qcommerce_tracker, "is_enabled", lambda: False)
        assert qcommerce_tracker.fetch() == []

    def test_raw_only_converters_return_empty(self):
        assert news_tavily.to_data_points([{"results": []}]) == []
        assert trends_google.to_data_points([{}]) == []
        assert academic_openalex.to_data_points([{}]) == []
        assert qcommerce_tracker.to_data_points([{}]) == []


class TestQueryManifests:
    def test_tavily_manifest_includes_corridor(self):
        manifest = news_tavily.queries()
        assert len(manifest) > len(news_tavily.SEGMENT_QUERIES)
        corridor = [q for q in manifest if q["corridor"]]
        assert corridor, "corridor.yaml queries must be in the Tavily manifest"
        assert all(q["geography"] == "IN" for q in corridor)

    def test_comtrade_hs_codes_from_corridor_config(self):
        assert set(trade_comtrade._hs_codes()) == set(trade_comtrade.HS_SEGMENT_MAP)


class TestConverters:
    def test_comtrade_to_data_points(self):
        raw = [{
            "hs": "3304", "partner": "India", "year": 2024,
            "rows": [{"primaryValue": 30_000_000.0}, {"primaryValue": 20_000_000.0}],
        }]
        points = trade_comtrade.to_data_points(raw)
        assert len(points) == 1
        dp = points[0]
        assert dp.value == pytest.approx(0.05)
        assert dp.segment == "skincare"
        assert dp.value_basis == "EXPORT_FOB"
        assert "[CORRIDOR]" in dp.notes

    def test_india_imports_to_data_points(self):
        raw = [{"hs": "3304", "partner": "Korea", "year": 2024, "flow": "import",
                "rows": [{"primaryValue": 140_060_000.0}]}]
        pts = trade_comtrade.india_imports_to_data_points(raw)
        assert len(pts) == 1
        dp = pts[0]
        assert dp.geography == "IN" and dp.metric == "import_value"
        assert dp.value_basis == "IMPORT_CIF"
        assert dp.value == pytest.approx(0.14006)
        assert "[CORRIDOR]" in dp.notes  # Korea origin

    def test_comtrade_world_not_corridor_tagged(self):
        raw = [{"hs": "3305", "partner": "World", "year": 2024,
                "rows": [{"primaryValue": 1_000_000.0}]}]
        dp = trade_comtrade.to_data_points(raw)[0]
        assert dp.segment == "hair_care"
        assert "[CORRIDOR]" not in dp.notes

    def test_comtrade_zero_value_skipped(self):
        raw = [{"hs": "3303", "partner": "India", "year": 2024, "rows": []}]
        assert trade_comtrade.to_data_points(raw) == []

    def test_dart_to_data_points(self):
        raw = [{
            "company": "AmorePacific", "year": 2025,
            "rows": [{
                "account_id": "ifrs-full_Revenue", "sj_div": "CIS",
                "thstrm_amount": "4,250,000,000,000",
            }],
        }]
        points = korea_dart.to_data_points(raw)
        assert len(points) == 1
        assert points[0].value == pytest.approx(4.25)
        assert points[0].unit == "krw_tn"
        assert points[0].confidence == "HIGH"

    def test_screener_to_data_points(self):
        pl_csv = ",Mar 2023,Mar 2024\nSales +,\"1,000\",\"1,200\"\nExpenses,900,950\n"
        raw = [{"company": "Testco", "slug": "TEST",
                "url": "https://www.screener.in/company/TEST/consolidated/",
                "tables": [pl_csv]}]
        points = india_screener.to_data_points(raw)
        assert len(points) == 2
        by_period = {p.period: p.value for p in points}
        assert by_period == {"FY23": 1000.0, "FY24": 1200.0}
        assert all(p.value_basis == "NET_REALISATION" for p in points)


class TestLiveSmoke:
    """Actual network calls — skip cleanly when offline/blocked."""

    def test_openalex_reachable(self):
        records = academic_openalex.fetch()
        if not records:
            pytest.skip("OpenAlex unreachable from this network")
        assert all("counts_by_year" in r for r in records)

    def test_comtrade_preview_reachable(self):
        records = trade_comtrade.fetch()
        if not records:
            pytest.skip("Comtrade preview unreachable (rate limit or network)")
        points = trade_comtrade.to_data_points(records)
        for dp in points:
            assert dp.date_accessed == date.today()
