#!/usr/bin/env python
"""Token-cheap CLI for research agents.

Exists so an agent never has to read CLAUDE.md, schema.py, taxonomy.yaml,
exchange_rates.yaml, or re-write a growing JSON drop file. Every subcommand
prints a short, complete answer.

    python -m scripts.research_kit skeleton          # claim template + enums
    python -m scripts.research_kit cells             # open gaps, compact
    python -m scripts.research_kit fx 5751.5 KRW     # USD equivalent, pinned
    python -m scripts.research_kit add <file> '<json>'   # append ONE claim
    python -m scripts.research_kit check <file>      # validate a drop
    python -m scripts.research_kit audit [file...]   # rule-compliance scan

`add` is the important one: it appends a single claim to a drop file and
validates it immediately, so an agent spends ~300 tokens per claim instead of
re-emitting a 20 KB file on every addition.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.ingest.research_drop import parse_drop  # noqa: E402
from lib.transforms.schema import taxonomy_segments  # noqa: E402

DROPS = ROOT / "data" / "manual" / "research_drops"
ACCESSED = "2026-07-25"

# Pinned in config/exchange_rates.yaml, 2026-07-21.
FX = {"KRW": 1478.40, "INR": 96.23}

SKELETON = {
    "geography": "KR|IN",
    "segment": "<taxonomy id>",
    "sub_segment": "<taxonomy id or null>",
    "metric": "market_size|growth_yoy|cagr_forecast|cagr_historical|market_share|"
              "revenue|export_value|production_value|channel_share|per_capita_spend|"
              "penetration_rate|import_value|import_dependence|retail_price|"
              "gross_margin|operating_margin|adspend_ratio|trade_margin",
    "value": 0.0,
    "unit": "usd_bn|usd_mn|krw_tn|krw_bn|inr_cr|percent|usd|inr",
    "currency": "USD|KRW|INR",
    "period": "2025 | FY25 | 2026-2034",
    "period_type": "CY|FY|H1|H2|Q1|Q2|Q3|Q4|range",
    "value_basis": "RETAIL|NET_REALISATION|WHOLESALE|EXPORT_FOB|PRODUCTION|"
                   "IMPORT_CIF|MRP|NA",
    "tier": "premium|masstige|mass|null",
    "source_name": "<publisher>",
    "source_url": "<URL you personally fetched>",
    "confidence": "HIGH|MEDIUM|LOW|ESTIMATE",
    "methodology": "<required iff confidence=ESTIMATE: arithmetic + sensitivity>",
    "notes": "<scope caveats, cross-refs, India coverage, [CORRIDOR] if applicable>",
}

RULES = """RULES (complete — do not read other repo files)
1 source_url is mandatory unless confidence=ESTIMATE, and must be a page you
  actually fetched. Never cite an unfetched URL.
2 Never average or reconcile conflicting sources. Record BOTH as separate
  claims; each notes field names the other and says "do not average".
3 Korea = CY periods. India company/fiscal data = FY periods (FY25 = Apr24-Mar25).
4 Korea: RETAIL / EXPORT_FOB / PRODUCTION are three different measures - never
  conflate. Flag duty-free if included.
5 India: state organised vs unorganised coverage in notes, or say
  "organised/unorganised coverage not stated". MRP includes 25-45% trade margin.
6 K-beauty-inside-India figures carry "[CORRIDOR]" in notes.
7 Scope caveats go in notes prefixed "SCOPE CAVEAT:".
8 confidence: HIGH=govt/filing/Passport, MEDIUM=credible secondary,
  LOW=aggregator (IMARC/Mordor/GVR/TechSci/EMR/MarkNtel), ESTIMATE=derived.
9 No defensible number => leave the cell empty. A standing gap is information;
  a fabricated number is contamination.
10 Give original currency; put the USD equivalent in notes naming the pinned
  rate (USD/KRW 1478.40, USD/INR 96.23, pinned 2026-07-21). Use `fx`."""


def _load(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"accessed": ACCESSED, "claims": []}


def cmd_skeleton() -> int:
    print(json.dumps(SKELETON, indent=2))
    print()
    print(RULES)
    return 0


def cmd_cells() -> int:
    p = ROOT / "web" / "public" / "data" / "gaps.json"
    if not p.exists():
        print("gaps.json missing - run: python -m lib.web_export")
        return 1
    for g in json.loads(p.read_text(encoding="utf-8")):
        sub = f"/{g['sub_segment']}" if g.get("sub_segment") else ""
        print(f"{g['geography']} {g['segment']}{sub} {g['metric']}")
    return 0


def cmd_fx(value: str, currency: str) -> int:
    cur = currency.upper()
    if cur not in FX:
        print(f"unknown currency {cur}; known: {', '.join(FX)}")
        return 1
    print(f"{float(value)} {cur} = USD {float(value) / FX[cur]:,.4f} "
          f"(pinned {FX[cur]}, 2026-07-21)")
    return 0


def cmd_add(file: str, blob: str) -> int:
    """Append ONE claim to a drop file, then validate the whole file."""
    path = Path(file)
    if not path.is_absolute():
        path = DROPS / path.name
    try:
        claim = json.loads(blob)
    except json.JSONDecodeError as exc:
        print(f"FAIL bad JSON: {exc}")
        return 1
    if not isinstance(claim, dict):
        print("FAIL expected a single claim object")
        return 1

    payload = _load(path)
    payload.setdefault("accessed", ACCESSED)
    payload.setdefault("claims", []).append(claim)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                    encoding="utf-8")

    points, errors = parse_drop(path)
    if errors:
        # Roll back so a bad claim never poisons the file.
        payload["claims"].pop()
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                        encoding="utf-8")
        for e in errors:
            print(f"FAIL {e}")
        print("(claim rejected, file unchanged)")
        return 1
    print(f"OK {path.name}: {len(points)} claims")
    return 0


def cmd_check(files: list[str]) -> int:
    ok = True
    for f in files:
        path = Path(f)
        if not path.is_absolute():
            path = DROPS / path.name
        points, errors = parse_drop(path)
        if errors:
            ok = False
            for e in errors:
                print(f"FAIL {e}")
        else:
            print(f"OK   {path.name}: {len(points)} valid claims")
    return 0 if ok else 1


def cmd_audit(files: list[str]) -> int:
    """Mechanical rule-compliance scan. Flags what a human should look at."""
    paths = [Path(f) if Path(f).is_absolute() else DROPS / Path(f).name
             for f in files] or sorted(DROPS.glob("*.json"))
    tax = taxonomy_segments()
    findings = 0
    for path in paths:
        payload = _load(path)
        for i, c in enumerate(payload.get("claims", [])):
            tag = f"{path.name}[{i}] {c.get('geography')} {c.get('segment')}" \
                  f"{'/' + c['sub_segment'] if c.get('sub_segment') else ''} " \
                  f"{c.get('metric')}"
            notes = (c.get("notes") or "")
            low = notes.lower()
            def flag(msg: str) -> None:
                nonlocal findings
                findings += 1
                print(f"{tag}: {msg}")

            if c.get("confidence") != "ESTIMATE" and not c.get("source_url"):
                flag("no source_url")
            if c.get("confidence") == "ESTIMATE" and not c.get("methodology"):
                flag("ESTIMATE without methodology")
            if c.get("geography") == "IN" and c.get("metric") in {
                    "market_size", "revenue", "market_share"} \
                    and "organis" not in low and "unorganis" not in low:
                flag("India size/share without organised-coverage statement")
            if c.get("geography") == "KR" and c.get("value_basis") == "RETAIL" \
                    and "duty" not in low:
                flag("KR RETAIL without duty-free treatment noted")
            if c.get("value_basis") == "NA" and c.get("unit") not in {
                    "percent"} :
                flag(f"value_basis NA but unit={c.get('unit')}")
            if c.get("metric") == "growth_yoy" and c.get("period_type") == "range":
                flag("growth_yoy with range period (should be a single period)")
            seg, sub = c.get("segment"), c.get("sub_segment")
            if seg in tax and sub and sub not in tax[seg]:
                flag(f"sub_segment '{sub}' not in taxonomy for '{seg}'")
    print(f"\n{findings} finding(s) across {len(paths)} file(s). "
          "Findings are prompts for review, not automatic failures.")
    return 0


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 1
    cmd, rest = args[0], args[1:]
    if cmd == "skeleton":
        return cmd_skeleton()
    if cmd == "cells":
        return cmd_cells()
    if cmd == "fx" and len(rest) == 2:
        return cmd_fx(*rest)
    if cmd == "add" and len(rest) == 2:
        return cmd_add(*rest)
    if cmd == "check" and rest:
        return cmd_check(rest)
    if cmd == "audit":
        return cmd_audit(rest)
    print(__doc__)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
