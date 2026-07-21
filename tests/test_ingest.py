"""Manual ingest pipeline tests — one mock CSV per handler."""
from __future__ import annotations

import pytest

from lib.ingest import capitaliq_csv, generic_csv, passport_csv, statista_csv
from lib.ingest.ingest import detect_handler, ingest, ingest_folder


class TestHandlerDetection:
    @pytest.mark.parametrize("name,expected", [
        ("capitaliq_hul.csv", "capitaliq"),
        ("capiq_export.csv", "capitaliq"),
        ("passport_korea.csv", "passport"),
        ("euromonitor_india.csv", "passport"),
        ("statista_bpc.csv", "statista"),
        ("bmi_forecast.csv", "generic"),
    ])
    def test_detect(self, name, expected):
        assert detect_handler(name) == expected


class TestCapitalIQ:
    def test_parse(self, tmp_path):
        csv = tmp_path / "capitaliq_test.csv"
        csv.write_text(
            "Company,Geography,Metric,Currency,Unit,FY2022,FY2023,FY2024\n"
            "Hindustan Unilever,India,Total Revenue,INR,cr,58154,61896,63000\n"
            "AmorePacific,South Korea,Total Revenue,KRW,tn,4.13,3.9,4.25\n",
            encoding="utf-8",
        )
        points = capitaliq_csv.parse(csv)
        assert len(points) == 6
        hul = [p for p in points if "Hindustan" in p.notes]
        assert all(p.geography == "IN" and p.period_type == "FY" for p in hul)
        assert all(p.value_basis == "NET_REALISATION" and p.confidence == "HIGH" for p in points)
        amore = [p for p in points if "AmorePacific" in p.notes]
        assert {p.period for p in amore} == {"FY22", "FY23", "FY24"}
        assert next(p for p in amore if p.period == "FY24").value == pytest.approx(4.25)

    def test_missing_columns_raises(self, tmp_path):
        csv = tmp_path / "capitaliq_bad.csv"
        csv.write_text("Company,Revenue\nX,100\n", encoding="utf-8")
        with pytest.raises(ValueError, match="missing required columns"):
            capitaliq_csv.parse(csv)


class TestPassport:
    def test_market_size(self, tmp_path):
        csv = tmp_path / "passport_kr.csv"
        csv.write_text(
            "Category,Geography,Unit,2022,2023,2024\n"
            "Skin Care,South Korea,USD mn,6100,6250,6400\n"
            "Colour Cosmetics,South Korea,USD mn,2100,2150,2200\n",
            encoding="utf-8",
        )
        points = passport_csv.parse(csv)
        assert len(points) == 6
        assert all(p.value_basis == "RETAIL" and p.confidence == "HIGH" for p in points)
        assert all(p.source_name == "Euromonitor Passport" for p in points)
        skin24 = next(p for p in points if p.segment == "skincare" and p.period == "2024")
        assert skin24.value == 6400 and skin24.unit == "usd_mn"

    def test_brand_share_detected(self, tmp_path):
        csv = tmp_path / "passport_shares.csv"
        csv.write_text(
            "Company,Geography,2023,2024\n"
            "AmorePacific,South Korea,22.1,22.4\n"
            "LG H&H,South Korea,20.0,19.5\n",
            encoding="utf-8",
        )
        points = passport_csv.parse(csv)
        assert all(p.metric == "market_share" and p.unit == "percent" for p in points)
        assert any("AmorePacific" in p.notes for p in points)

    def test_geography_override(self, tmp_path):
        csv = tmp_path / "passport_noheader.csv"
        csv.write_text("Category,Unit,2024\nSkin Care,INR bn,1200\n", encoding="utf-8")
        points = passport_csv.parse(csv, geography="IN")
        assert len(points) == 1
        assert points[0].geography == "IN"
        assert "MRP-inclusive" in points[0].notes


class TestStatista:
    def test_parse(self, tmp_path):
        csv = tmp_path / "statista_india.csv"
        csv.write_text("Year,Revenue\n2022,28.0\n2023,30.5\n2024,33.1\n", encoding="utf-8")
        points = statista_csv.parse(
            csv, geography="IN", segment="total_bpc",
            metric="market_size", unit="usd_bn",
        )
        assert len(points) == 3
        assert all(p.currency == "USD" and p.confidence == "MEDIUM" for p in points)
        assert next(p for p in points if p.period == "2024").value == pytest.approx(33.1)

    def test_bad_segment_raises(self, tmp_path):
        csv = tmp_path / "statista_x.csv"
        csv.write_text("Year,Value\n2024,1\n", encoding="utf-8")
        with pytest.raises(ValueError, match="not in taxonomy"):
            statista_csv.parse(csv, geography="IN", segment="petcare",
                               metric="market_size", unit="usd_bn")


class TestGeneric:
    def test_parse_with_mapping(self, tmp_path):
        csv = tmp_path / "bmi_forecast.csv"
        csv.write_text(
            "Segment,Country,Val\nSkin Care,India,15.2\nHair Care,India,8.1\n",
            encoding="utf-8",
        )
        mapping = {
            "column_map": {"category": "Segment", "geography": "Country", "value": "Val"},
            "metric": "market_size", "unit": "usd_bn", "currency": "USD",
            "period": "2028", "period_type": "CY", "value_basis": "RETAIL",
            "confidence": "LOW", "source_name": "BMI Research",
        }
        points = generic_csv.parse(csv, mapping)
        assert len(points) == 2
        assert all(p.period == "2028" and p.source_name == "BMI Research" for p in points)

    def test_missing_mapping_key_raises(self, tmp_path):
        csv = tmp_path / "x.csv"
        csv.write_text("a,b\n1,2\n", encoding="utf-8")
        with pytest.raises(KeyError):
            generic_csv.parse(csv, {"column_map": {"value": "b"}})


class TestOrchestratorEndToEnd:
    def test_ingest_capitaliq_merges_and_refreshes_gaps(self, tmp_path, monkeypatch):
        # Redirect processed dir, sources.csv, and gaps register to a sandbox
        processed = tmp_path / "processed"
        processed.mkdir()
        sources = tmp_path / "sources.csv"
        sources.write_text(
            "claim,value,unit,currency,geography,segment,period,period_type,"
            "value_basis,source_name,url,date_accessed,confidence,notes\n",
            encoding="utf-8",
        )
        gaps_file = tmp_path / "gaps.md"

        import lib.transforms.merge as merge_mod
        import lib.ingest.ingest as orch
        monkeypatch.setattr(merge_mod, "PROCESSED_DIR", processed)
        monkeypatch.setattr(merge_mod, "SOURCES_CSV", sources)
        monkeypatch.setattr(orch, "GAPS_REGISTER", gaps_file)

        import lib.analysis.gaps as gaps_mod
        monkeypatch.setattr(gaps_mod, "PROJECT_ROOT", tmp_path)
        # scan_gaps reads processed_dir default from its own PROJECT_ROOT;
        # pass explicitly via a wrapper
        orig_scan = gaps_mod.scan_gaps
        monkeypatch.setattr(orch, "scan_gaps",
                            lambda: orig_scan(processed_dir=processed))

        csv = tmp_path / "capitaliq_amore.csv"
        csv.write_text(
            "Company,Geography,Metric,Currency,Unit,FY2024\n"
            "AmorePacific,South Korea,Total Revenue,KRW,tn,4.25\n",
            encoding="utf-8",
        )
        result = ingest(csv)
        assert result["handler"] == "capitaliq"
        assert result["points"] == 1
        assert result["added"] == 1
        assert (processed / "KR_total_bpc.json").exists()
        assert gaps_file.exists()

        # Idempotent: second run adds nothing
        result2 = ingest(csv)
        assert result2["added"] == 0

    def test_ingest_folder_batches_and_skips_bad(self, tmp_path, monkeypatch):
        processed = tmp_path / "processed"
        processed.mkdir()
        sources = tmp_path / "sources.csv"
        sources.write_text(
            "claim,value,unit,currency,geography,segment,period,period_type,"
            "value_basis,source_name,url,date_accessed,confidence,notes\n",
            encoding="utf-8",
        )
        import lib.analysis.gaps as gaps_mod
        import lib.ingest.ingest as orch
        import lib.transforms.merge as merge_mod
        monkeypatch.setattr(merge_mod, "PROCESSED_DIR", processed)
        monkeypatch.setattr(merge_mod, "SOURCES_CSV", sources)
        monkeypatch.setattr(orch, "GAPS_REGISTER", tmp_path / "gaps.md")
        orig_scan = gaps_mod.scan_gaps
        monkeypatch.setattr(orch, "scan_gaps", lambda: orig_scan(processed_dir=processed))

        manual = tmp_path / "manual"
        manual.mkdir()
        (manual / ".gitkeep").write_text("", encoding="utf-8")
        (manual / "capitaliq_good.csv").write_text(
            "Company,Geography,Metric,Currency,Unit,FY2024\n"
            "Nykaa,India,Total Revenue,INR,cr,10022\n", encoding="utf-8")
        (manual / "capitaliq_bad.csv").write_text(
            "Company,Revenue\nX,1\n", encoding="utf-8")  # missing columns -> skipped

        summary = ingest_folder(manual)
        assert summary["files_processed"] == 2
        assert summary["total_added"] == 1
        assert "error" in summary["per_file"]["capitaliq_bad.csv"]
        assert summary["per_file"]["capitaliq_good.csv"]["added"] == 1
