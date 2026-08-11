"""Report-layer tests: company roles, share role-filtering, rendering."""
from __future__ import annotations

from datetime import date

import pytest

from lib.analysis import share
from lib.analysis._load import company_name, company_role
from lib.transforms.schema import DataPoint


def _rev(company, period, value, geo="KR", currency="KRW", unit="krw_tn", conf="HIGH"):
    return DataPoint(
        geography=geo, segment="total_bpc", metric="revenue", value=value, unit=unit,
        currency=currency, period=period, period_type="CY", value_basis="NET_REALISATION",
        source_name="Test", date_accessed=date(2026, 7, 23), confidence=conf,
        notes=f"Company: {company} — test",
    )


def _price(value, currency="INR", unit="inr", basis="MRP", notes="a price"):
    return DataPoint(
        geography="IN", segment="skincare", metric="retail_price", value=value,
        unit=unit, currency=currency, period="2026", period_type="CY",
        value_basis=basis, source_name="Test listing",
        date_accessed=date(2026, 8, 9), confidence="HIGH", notes=notes,
    )


class TestPriceView:
    def test_small_segment_renders_every_point(self):
        from lib.reports._context import PRICE_SAMPLE_LIMIT, _price_view
        pts = [_price(100 + i) for i in range(PRICE_SAMPLE_LIMIT)]
        view = _price_view(pts)
        assert len(view["examples"]) == PRICE_SAMPLE_LIMIT
        assert view["summary"] == []
        assert view["omitted"] == 0

    def test_bulk_sku_drop_is_bounded_and_counted(self):
        # A price sweep adding hundreds of SKUs must not become a catalogue.
        from lib.reports._context import PRICE_SAMPLE_LIMIT, _price_view
        view = _price_view([_price(1000 + i) for i in range(327)])
        assert len(view["examples"]) == PRICE_SAMPLE_LIMIT
        assert view["omitted"] == 327 - PRICE_SAMPLE_LIMIT
        assert len(view["summary"]) == 1
        assert view["summary"][0]["count"] == 327
        assert view["summary"][0]["low"] == 1000
        assert view["summary"][0]["high"] == 1326

    def test_spans_never_cross_value_basis_or_currency(self):
        # CLAUDE.md rule 3: a span across mixed bases is meaningless.
        from lib.reports._context import _price_view
        pts = ([_price(1000 + i, basis="MRP") for i in range(20)]
               + [_price(50 + i, basis="WHOLESALE") for i in range(20)]
               + [_price(10 + i, currency="USD", unit="usd") for i in range(20)])
        summary = _price_view(pts)["summary"]
        assert len(summary) == 3
        keys = {(g["currency"], g["value_basis"]) for g in summary}
        assert keys == {("INR", "MRP"), ("INR", "WHOLESALE"), ("USD", "MRP")}
        for g in summary:
            assert g["count"] == 20
            assert g["low"] < g["high"]


class TestCompanyNameCleaning:
    def test_strips_trailing_descriptor(self):
        dp = _rev("LG H&H, -6.7% YoY", "2025", 6.36)
        assert company_name(dp) == "LG H&H"

    def test_strips_amorepacific_descriptor(self):
        dp = _rev("AmorePacific, +9.5% YoY", "2025", 4.25)
        assert company_name(dp) == "AmorePacific"


class TestCompanyRole:
    def test_brand(self):
        assert company_role("AmorePacific") == "brand"
        assert company_role("Hindustan Unilever") == "brand"

    def test_odm(self):
        assert company_role("Cosmax") == "odm"
        assert company_role("Kolmar Korea") == "odm"

    def test_retailer(self):
        assert company_role("CJ Olive Young") == "retailer"
        assert company_role("Nykaa (FSN E-Commerce)") == "retailer"

    def test_unknown(self):
        assert company_role("Some Random Co") == "unknown"


class TestShareRoleFiltering:
    def test_excludes_odm_and_retailer(self, tmp_path, monkeypatch):
        import json

        import lib.analysis._load as loader
        processed = tmp_path / "processed"
        processed.mkdir()
        pts = [
            _rev("AmorePacific", "2025", 4.25),
            _rev("LG H&H", "2025", 6.36),
            _rev("Cosmax", "2025", 2.39),           # odm — excluded
            _rev("CJ Olive Young", "2025", 5.83),   # retailer — excluded
        ]
        payload = {"geography": "KR", "segment": "total_bpc", "last_updated": "2026-07-23",
                   "data_points": [json.loads(p.model_dump_json()) for p in pts]}
        (processed / "KR_total_bpc.json").write_text(json.dumps(payload), encoding="utf-8")
        monkeypatch.setattr(loader, "PROCESSED_DIR", processed)

        res = share.compute_shares("KR", "total_bpc")
        names = {s["company"] for s in res["shares"]}
        assert names == {"AmorePacific", "LG H&H"}  # only brand owners
        assert "Cosmax" in res["qualifier"] and "odm" in res["qualifier"]
        assert "CJ Olive Young" in res["qualifier"] and "retailer" in res["qualifier"]
        assert sum(s["share_pct"] for s in res["shares"]) == pytest.approx(100.0, abs=0.2)


class TestRendering:
    def test_full_report_renders(self):
        from lib.reports.snapshot import generate_full_report
        path = generate_full_report()
        text = open(path, encoding="utf-8").read()
        assert "BPC Market Intelligence Snapshot" in text
        assert "K-beauty corridor" in text
        # No unrendered Jinja tokens
        assert "{{" not in text and "{%" not in text

    def test_corridor_brief_renders(self):
        from lib.reports.snapshot import generate_corridor_brief
        path = generate_corridor_brief()
        text = open(path, encoding="utf-8").read()
        assert "K-beauty Corridor Brief" in text
        assert "{{" not in text

    def test_india_value_chain_brief_renders(self):
        from lib.reports.snapshot import generate_india_value_chain_brief
        path = generate_india_value_chain_brief()
        text = open(path, encoding="utf-8").read()
        assert "India Beauty & Personal Care" in text
        assert "Import vs make" in text and "Consumer demand" in text
        assert "{{" not in text and "{%" not in text
