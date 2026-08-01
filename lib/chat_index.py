"""Build the chatbot's retrieval index from the governed data layer.

The corpus is small (~175k tokens), so this deliberately avoids embeddings
and a vector store. Instead it emits two retrieval surfaces:

  facts[]     — every DataPoint flattened into one searchable record that
                carries its FULL provenance (value_basis, confidence, source,
                url, period). A question like "India sunscreen market size"
                should hit an exact fact, not a paraphrase of one.
  passages[]  — prose chunks (analyst reads, Porter rationales, RTM channel
                notes, risks, qualitative findings, plus heading-chunked
                sections of the baseline research report, generated
                reports/latest briefs, and docs/*.md) for the "why/how"
                questions that no single DataPoint answers.

Structured-first retrieval is the point: paraphrasing a number through a
vector search loses the basis/confidence that this whole system exists to
preserve (CLAUDE.md evidence rules).
"""
from __future__ import annotations

import json
import logging
import re
from datetime import date
from pathlib import Path

import yaml

from lib.analysis._load import load_points
from lib.transforms.schema import PROJECT_ROOT

logger = logging.getLogger("bpc_intel.chat_index")

INSIGHTS_DIR = PROJECT_ROOT / "data" / "manual" / "insights"
ANALYSIS_DIR = PROJECT_ROOT / "data" / "manual" / "analysis"
CONFIG_DIR = PROJECT_ROOT / "config"
BASELINE_REPORT = PROJECT_ROOT / "data" / "baseline" / "deep-research-report.md"
REPORTS_DIR = PROJECT_ROOT / "reports" / "latest"
DOCS_DIR = PROJECT_ROOT / "docs"

_SEGMENTS = [
    "skincare", "sun_care", "colour_cosmetics", "fragrances", "hair_care",
    "bath_shower", "deodorants", "oral_care", "mens_grooming", "baby_child",
    "dermocosmetics", "emerging_adjacencies", "total_bpc",
]
# "total_bpc" reads as "total market" in prose and would tag nearly every
# heading in the corpus — too generic to be a useful retrieval signal.
_TAGGABLE_SEGMENTS = [s for s in _SEGMENTS if s != "total_bpc"]

_GEO_NAME = {"KR": "South Korea", "IN": "India"}


def _fact_text(dp, geo: str, seg: str) -> str:
    """The searchable text for a fact — includes synonyms a user might type."""
    parts = [
        _GEO_NAME.get(geo, geo), geo,
        seg.replace("_", " "),
        (dp.sub_segment or "").replace("_", " "),
        dp.metric.replace("_", " "),
        dp.period, dp.value_basis, dp.confidence,
        dp.source_name or "",
        dp.notes or "",
    ]
    return " ".join(p for p in parts if p)


def build_facts() -> list[dict]:
    """Every DataPoint as a retrieval record with full provenance attached."""
    facts: list[dict] = []
    for geo in ("KR", "IN"):
        for seg in _SEGMENTS:
            for dp in load_points(geo, seg):
                facts.append({
                    "id": f"{geo}_{seg}_{dp.metric}_{dp.period}_{len(facts)}",
                    "kind": "fact",
                    "geography": geo,
                    "segment": seg,
                    "sub_segment": dp.sub_segment,
                    "metric": dp.metric,
                    "value": dp.value,
                    "unit": dp.unit,
                    "currency": dp.currency,
                    "period": dp.period,
                    "value_basis": dp.value_basis,
                    "confidence": dp.confidence,
                    "source": dp.source_name,
                    "url": dp.source_url,
                    "notes": dp.notes,
                    "text": _fact_text(dp, geo, seg),
                })
    logger.info("Indexed %d facts", len(facts))
    return facts


def _passage(pid: str, title: str, text: str, ref: str, **extra) -> dict:
    # Ensure the geography is searchable by the name people actually type.
    # "IN" alone is useless: the retrieval tokenizer treats "in" as a stopword
    # and drops it, so an India passage would carry no geography signal at all
    # while "KR" (not a stopword) survives — India queries would silently lose
    # to Korea ones. Injecting the full name here means no call site can
    # reintroduce that asymmetry by forgetting to format its own title.
    geo = extra.get("geography")
    name = _GEO_NAME.get(geo) if geo else None
    if name and name.lower() not in title.lower():
        title = f"{title} ({name})"
    return {"id": pid, "kind": "passage", "title": title, "text": text,
            "source_ref": ref, **extra}


_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")


def _split_markdown_sections(text: str) -> list[tuple[list[str], str]]:
    """Split markdown into (heading_path, body) chunks at every heading line.

    heading_path is the stack of enclosing heading titles by level, e.g.
    ["2. South Korea Deep Dive", "2.1 The domestic market..."]. A heading
    with no body text before its next (sub)heading is dropped — it's a pure
    section header (or a parent whose only content is its subsections), not
    indexable content on its own.
    """
    stack: list[tuple[int, str]] = []  # (level, title)
    sections: list[tuple[list[str], str]] = []
    body: list[str] = []

    def flush() -> None:
        joined = "\n".join(body).strip()
        if joined:
            sections.append(([title for _, title in stack], joined))
        body.clear()

    for line in text.splitlines():
        m = _HEADING_RE.match(line)
        if not m:
            body.append(line)
            continue
        flush()
        level = len(m.group(1))
        while stack and stack[-1][0] >= level:
            stack.pop()
        stack.append((level, m.group(2).strip()))
    flush()
    return sections


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60] or "section"


def _md_geography(heading_path: list[str]) -> str | None:
    """Geography signal from a chunk's own heading, inherited from its
    nearest ancestor heading that actually states one. Corridor/K-beauty
    headings are treated as inherently cross-cutting (never geo-tagged),
    matching how config/corridor.yaml's own passages are never geo-tagged
    below. A heading naming BOTH countries stops the climb — a section that
    is explicitly comparative shouldn't inherit a single-country tag from an
    ancestor further up.
    """
    for title in reversed(heading_path):
        low = title.lower()
        if "corridor" in low or "k-beauty" in low or "kbeauty" in low:
            return None
        has_kr, has_in = "korea" in low, "india" in low
        if has_kr and has_in:
            return None
        if has_kr:
            return "KR"
        if has_in:
            return "IN"
    return None


def _md_segment(heading: str) -> str | None:
    """Segment signal from a chunk's own (deepest) heading only — no
    inheritance, since a segment-named parent with generic-titled children
    doesn't occur in this corpus and climbing risks mistagging a child that
    covers a different segment. Requires exactly one distinct segment to
    appear, so a heading spanning several segments is left untagged rather
    than pinned to an arbitrary one."""
    low = heading.lower()
    hits = {s for s in _TAGGABLE_SEGMENTS if s.replace("_", " ") in low}
    return hits.pop() if len(hits) == 1 else None


def _markdown_passages(path: Path, id_prefix: str) -> list[dict]:
    """Chunk one long-form markdown file by heading into prose passages."""
    text = path.read_text(encoding="utf-8")
    rel = path.relative_to(PROJECT_ROOT).as_posix()
    out: list[dict] = []
    for i, (heading_path, body) in enumerate(_split_markdown_sections(text)):
        if heading_path:
            crumbs = heading_path[1:][-2:]
            title = f"{heading_path[0]} — {' › '.join(crumbs)}" if crumbs else heading_path[0]
            anchor = _slug(heading_path[-1])
        else:
            title = path.stem.replace("-", " ").replace("_", " ")
            anchor = _slug(path.stem)
        kwargs: dict = {}
        geo = _md_geography(heading_path)
        if geo:
            kwargs["geography"] = geo
        seg = _md_segment(heading_path[-1]) if heading_path else None
        if seg:
            kwargs["segment"] = seg
        out.append(_passage(f"{id_prefix}_{i}", title, body, f"{rel}#{anchor}", **kwargs))
    return out


def build_passages() -> list[dict]:
    """Prose chunks: analyst reads, analysis rationales, qualitative findings."""
    out: list[dict] = []

    # --- Analyst insights (per segment × geography + combined) ---
    if INSIGHTS_DIR.exists():
        for path in sorted(INSIGHTS_DIR.glob("*.json")):
            seg = path.stem
            data = json.loads(path.read_text(encoding="utf-8"))
            for geo in ("KR", "IN"):
                block = data.get(geo) or {}
                body = " ".join(filter(None, [
                    block.get("read"), block.get("trend"), block.get("caveats")]))
                if body:
                    out.append(_passage(
                        f"insight_{seg}_{geo}",
                        f"Analyst read — {seg.replace('_',' ')} ({_GEO_NAME.get(geo,geo)})",
                        body, f"insights/{seg}.json#{geo}",
                        segment=seg, geography=geo))
            combined = (data.get("combined") or {}).get("read")
            if combined:
                out.append(_passage(
                    f"insight_{seg}_combined",
                    f"Analyst read — {seg.replace('_',' ')} (Korea vs India)",
                    combined, f"insights/{seg}.json#combined", segment=seg))

    # --- Entry-analysis artifacts ---
    if ANALYSIS_DIR.exists():
        for path in sorted(ANALYSIS_DIR.rglob("*.json")):
            rel = path.relative_to(ANALYSIS_DIR).with_suffix("").as_posix()
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                logger.warning("Skipping malformed analysis artifact %s", path)
                continue
            out.extend(_passages_from_analysis(rel, data))

    # --- Qualitative config findings: config/{name}_findings.yaml, globbed
    # (not named) so korea_findings.yaml / corridor_findings.yaml / any future
    # geography or theme's findings file is picked up with no code change. ---
    for findings_path in sorted(CONFIG_DIR.glob("*_findings.yaml")):
        stem = findings_path.stem  # e.g. "korea_findings"
        key = stem.removesuffix("_findings")
        geo = {"india": "IN", "korea": "KR"}.get(key)  # corridor -> None: cross-cutting
        # Use the full geography name ("South Korea") so _passage()'s dedup
        # check (below) recognises it's already in the title and doesn't
        # append a second, redundant-looking "(South Korea)" suffix.
        label = _GEO_NAME.get(geo, key.replace("_", " ").title())
        geo_kwargs = {"geography": geo} if geo else {}
        findings = yaml.safe_load(findings_path.read_text(encoding="utf-8")) or {}
        for topic, items in findings.items():
            for i, item in enumerate(items or []):
                out.append(_passage(
                    f"finding_{stem}_{topic}_{i}",
                    f"{label} finding — {topic.replace('_',' ')}",
                    f"{item.get('text','')} (Source: {item.get('source','')})",
                    f"config/{findings_path.name}#{topic}",
                    **geo_kwargs))

    corridor_path = CONFIG_DIR / "corridor.yaml"
    if corridor_path.exists():
        cfg = (yaml.safe_load(corridor_path.read_text(encoding="utf-8")) or {}).get("corridor", {})
        for k, v in (cfg.get("headline") or {}).items():
            out.append(_passage(f"corridor_headline_{k}", f"Corridor — {k}", str(v),
                                "config/corridor.yaml#headline"))
        for i, w in enumerate(cfg.get("whitespace") or []):
            out.append(_passage(f"corridor_whitespace_{i}", "Corridor whitespace", str(w),
                                "config/corridor.yaml#whitespace"))
        for k, v in (cfg.get("regulation") or {}).items():
            out.append(_passage(f"corridor_reg_{k}", f"Regulation — {k}", str(v),
                                "config/corridor.yaml#regulation"))
        qc = cfg.get("qcommerce_assortment") or {}
        if qc.get("insight"):
            out.append(_passage("corridor_qcommerce", "Q-commerce assortment insight",
                                str(qc["insight"]), "config/corridor.yaml#qcommerce"))
        for c in cfg.get("conduits") or []:
            brands = ", ".join(b.get("brand", "") for b in (c.get("kr_brands_carried") or []))
            out.append(_passage(
                f"corridor_conduit_{c.get('name','')}".replace(" ", "_"),
                f"Corridor conduit — {c.get('name')}",
                f"{c.get('notes','')} Brands carried: {brands}",
                "config/corridor.yaml#conduits"))

    # --- Long-form markdown, chunked by heading (not indexed as one blob):
    # the founding baseline research, generated reports/latest briefs, and
    # process docs. Deliberately excludes data/raw/ — those are structured
    # fetcher dumps (DART/Comtrade/gtrends JSON); indexing them as prose
    # would flood retrieval with meaningless fragments, and their figures
    # already exist as governed facts[] with basis/confidence attached. ---
    if BASELINE_REPORT.exists():
        out.extend(_markdown_passages(BASELINE_REPORT, "baseline"))
    if REPORTS_DIR.exists():
        for path in sorted(REPORTS_DIR.glob("*.md")):
            out.extend(_markdown_passages(path, f"report_{path.stem}"))
    if DOCS_DIR.exists():
        for path in sorted(DOCS_DIR.glob("*.md")):
            out.extend(_markdown_passages(path, f"doc_{path.stem}"))

    logger.info("Indexed %d passages", len(out))
    return out


def _passages_from_analysis(rel: str, data: dict) -> list[dict]:
    """Flatten one analysis artifact into prose passages with its judgments."""
    out: list[dict] = []

    def judgment_text(j: dict) -> str:
        bits = [j.get("rationale", "")]
        if j.get("rating"):
            bits.insert(0, f"Rating: {j['rating']}.")
        if j.get("score") is not None:
            bits.insert(0, f"Score: {j['score']}/5.")
        if j.get("evidence_strength"):
            bits.append(f"Evidence strength: {j['evidence_strength']}.")
        if j.get("research_needed"):
            bits.append(f"Research needed: {j['research_needed']}")
        return " ".join(b for b in bits if b)

    if rel.startswith("porter_"):
        seg = rel.replace("porter_", "")
        for geo in ("KR", "IN"):
            block = data.get(geo)
            if not block:
                continue
            for force, j in block.items():
                if not isinstance(j, dict) or not j.get("rationale"):
                    continue
                out.append(_passage(
                    f"{rel}_{geo}_{force}",
                    f"Porter {force.replace('_',' ')} — {seg.replace('_',' ')} ({_GEO_NAME.get(geo,geo)})",
                    judgment_text(j), f"analysis/{rel}.json#{geo}.{force}",
                    segment=seg, geography=geo))

    elif rel == "entry_scorecard":
        for row in data.get("rows", []):
            seg, geo = row.get("segment"), row.get("geography")
            comp = row.get("composite", {})
            crits = "; ".join(
                f"{c}: {j.get('score')}/5 — {j.get('rationale','')}"
                for c, j in (row.get("criteria") or {}).items()
                if isinstance(j, dict) and j.get("score") is not None)
            out.append(_passage(
                f"scorecard_{seg}_{geo}",
                f"Entry scorecard — {str(seg).replace('_',' ')} ({_GEO_NAME.get(geo,geo)})",
                f"Composite {comp.get('score')} based on {comp.get('based_on')} of "
                f"{comp.get('of')} criteria. {comp.get('read','')} {crits}",
                f"analysis/entry_scorecard.json#{seg}.{geo}",
                segment=seg, geography=geo))

    elif rel.startswith("rtm_"):
        geo = rel.replace("rtm_", "")
        for ch in data.get("channels", []):
            out.append(_passage(
                f"{rel}_{ch.get('channel','')}".replace(" ", "_"),
                f"Route to market — {ch.get('channel')} ({_GEO_NAME.get(geo,geo)})",
                f"{ch.get('known','')} Entry implication: {ch.get('entry_implications','')}",
                f"analysis/{rel}.json#{ch.get('channel')}", geography=geo))
        if data.get("summary"):
            out.append(_passage(f"{rel}_summary", f"Route to market summary ({_GEO_NAME.get(geo,geo)})",
                                data["summary"], f"analysis/{rel}.json#summary", geography=geo))

    elif rel == "risk_register":
        for i, r in enumerate(data.get("risks", [])):
            out.append(_passage(
                f"risk_{i}", f"Risk — {r.get('risk')} ({r.get('geography')})",
                f"Severity {r.get('severity')}. {r.get('rationale','')} "
                f"Mitigation: {r.get('mitigation','')}",
                "analysis/risk_register.json", geography=r.get("geography")))

    elif rel == "price_ladder":
        for i, rung in enumerate(data.get("rungs", [])):
            out.append(_passage(
                f"price_{i}",
                f"Price ladder — {str(rung.get('segment','')).replace('_',' ')} ({rung.get('tier')})",
                f"{rung.get('price_range','')} Examples: {', '.join(rung.get('examples') or [])}",
                "analysis/price_ladder.json", segment=rung.get("segment"), geography="IN"))
        if data.get("masstige_gap_note"):
            out.append(_passage("price_masstige_gap", "Price ladder — masstige gap",
                                data["masstige_gap_note"], "analysis/price_ladder.json", geography="IN"))

    elif rel == "corridor_vector":
        for key in ("read", "whitespace_read", "friction_read"):
            if data.get(key):
                out.append(_passage(f"corridor_vector_{key}", f"Corridor vector — {key}",
                                    data[key], "analysis/corridor_vector.json"))
        for c in data.get("conduit_ranking", []):
            out.append(_passage(
                f"corridor_rank_{c.get('conduit','')}".replace(" ", "_"),
                f"Corridor conduit ranking — {c.get('conduit')}",
                c.get("case", ""), "analysis/corridor_vector.json"))

    elif rel in ("demand_drivers", "value_chain"):
        items = data.get("drivers") or data.get("sections") or []
        for i, it in enumerate(items):
            title = it.get("driver") or it.get("topic") or f"item {i}"
            out.append(_passage(
                f"{rel}_{i}", f"{rel.replace('_',' ').title()} — {title}",
                it.get("read", ""), f"analysis/{rel}.json", geography=it.get("geography")))

    elif rel == "entry_mode":
        for r in data.get("reads", []):
            out.append(_passage(
                f"entrymode_{r.get('segment')}_{r.get('geography')}",
                f"Entry mode — {str(r.get('segment','')).replace('_',' ')} "
                f"({_GEO_NAME.get(r.get('geography'), r.get('geography'))})",
                f"Mode: {r.get('mode') or 'research needed'}. {r.get('rationale','')} "
                f"Alternatives: {r.get('alternatives_considered','')}",
                "analysis/entry_mode.json",
                segment=r.get("segment"), geography=r.get("geography")))

    return out


def build_index() -> dict:
    """The full retrieval index shipped to the web app."""
    return {
        "generated_at": date.today().isoformat(),
        "facts": build_facts(),
        "passages": build_passages(),
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    idx = build_index()
    # Actually persist it. This block used to build the index and print counts
    # without writing anything, so `python -m lib.chat_index` looked like it
    # regenerated the index while silently leaving the old one in place — the
    # counts printed were from the fresh build, which made the no-op invisible.
    out_path = PROJECT_ROOT / "web" / "public" / "data" / "chat_index.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(idx, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"facts={len(idx['facts'])} passages={len(idx['passages'])} -> {out_path}")
