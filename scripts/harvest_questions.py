"""Harvest unanswered chatbot questions from Neon into a committed backlog.

Run by .github/workflows/harvest-questions.yml on a schedule (and manually).
Writes data/manual/question_backlog.json + docs/question-backlog.md so the
gaps are reviewable in git and answerable by /answer-gaps.

Requires DATABASE_URL. Exits 0 with no output when there is nothing to harvest,
so the workflow can skip opening an empty PR.
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKLOG_JSON = PROJECT_ROOT / "data" / "manual" / "question_backlog.json"
BACKLOG_MD = PROJECT_ROOT / "docs" / "question-backlog.md"


def fetch_open_questions(dsn: str) -> list[dict]:
    import psycopg

    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, question, asked_at, retrieved_facts, retrieved_passages,
                   refusal_reason
            FROM chat_questions
            WHERE answered = false AND status = 'open'
            ORDER BY asked_at ASC
            LIMIT 500
            """
        )
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def render_markdown(rows: list[dict]) -> str:
    # Questions where retrieval found nothing are true research gaps; questions
    # where it found data but the model still refused point at a retrieval or
    # prompt problem instead. Separating them keeps the fix aimed correctly.
    research_gaps = [r for r in rows if (r["retrieved_facts"] or 0) == 0]
    retrieval_gaps = [r for r in rows if (r["retrieved_facts"] or 0) > 0]

    lines = [
        "# Question backlog",
        "",
        f"_Harvested {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} — "
        f"{len(rows)} unanswered question(s)._",
        "",
        "Questions the assistant could not answer from the current corpus. "
        "Answer them with `/answer-gaps`, which routes findings through the "
        "governed research pipeline (`lib/ingest/research_drop.py`) so new "
        "claims arrive with a source URL, value_basis and confidence — never "
        "as free-floating prose.",
        "",
        f"## Research gaps ({len(research_gaps)})",
        "",
        "No matching data in the repository — these need actual research.",
        "",
    ]
    if research_gaps:
        lines += ["| # | Question | First asked |", "|---|---|---|"]
        for r in research_gaps:
            q = str(r["question"]).replace("|", "\\|")
            lines.append(f"| {r['id']} | {q} | {r['asked_at']:%Y-%m-%d} |")
    else:
        lines.append("_None._")

    lines += [
        "",
        f"## Retrieval gaps ({len(retrieval_gaps)})",
        "",
        "Relevant data WAS retrieved but the assistant still declined — likely a "
        "retrieval-ranking or prompt issue rather than missing data. Check these "
        "before commissioning new research.",
        "",
    ]
    if retrieval_gaps:
        lines += ["| # | Question | Facts hit | First asked |", "|---|---|---|---|"]
        for r in retrieval_gaps:
            q = str(r["question"]).replace("|", "\\|")
            lines.append(
                f"| {r['id']} | {q} | {r['retrieved_facts']} | {r['asked_at']:%Y-%m-%d} |"
            )
    else:
        lines.append("_None._")

    themes = Counter()
    for r in rows:
        for word in str(r["question"]).lower().split():
            if len(word) > 4:
                themes[word] += 1
    if themes:
        top = ", ".join(f"{w} ({n})" for w, n in themes.most_common(10))
        lines += ["", "## Recurring terms", "", top]

    lines.append("")
    return "\n".join(lines)


def main() -> int:
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        print("DATABASE_URL not set — nothing to harvest.", file=sys.stderr)
        return 0

    rows = fetch_open_questions(dsn)
    if not rows:
        print("No unanswered questions.")
        return 0

    BACKLOG_JSON.parent.mkdir(parents=True, exist_ok=True)
    BACKLOG_MD.parent.mkdir(parents=True, exist_ok=True)

    payload = [
        {
            "id": r["id"],
            "question": r["question"],
            "asked_at": r["asked_at"].isoformat(),
            "retrieved_facts": r["retrieved_facts"],
            "retrieved_passages": r["retrieved_passages"],
            "refusal_reason": r["refusal_reason"],
        }
        for r in rows
    ]
    BACKLOG_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    BACKLOG_MD.write_text(render_markdown(rows), encoding="utf-8")
    print(f"Harvested {len(rows)} unanswered question(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
