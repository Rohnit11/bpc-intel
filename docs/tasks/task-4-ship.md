# Task 4 — Verify and ship wave 2

**Model: Sonnet. No web research.**
**Runs last — after Tasks 1, 2 and 3 have landed.**
**Read `docs/agent-protocol.md` first. Read nothing else in the repo.**

## Context

Wave 2 added 105 claims (346 → 450 DataPoints), closed 33 of 42 core-metric
gaps, and took sub-segment coverage from 19 to 32 of 34. Task 1 audited it,
Task 2 refreshed the analyst insights, Task 3 attacked the residual cells.
Your job is to get it verified, built and merged without breaking production.

Branch: `feat/research-wave-2`.

## Scope you own

`data/processed/*`, `data/sources.csv`, `data/manual/*`, the regenerated
`web/public/data` bundle, `docs/*`, `scripts/research_kit.py`.

**Do not edit `lib/chat_index.py` or any `config/*_findings.yaml`.** If a test
failure points at those, stop and report rather than editing them.

## Sequence — do not reorder

```bash
# 1. Merge any drop Task 3 produced (idempotent; re-merging old drops is safe)
python -m lib.ingest.research_drop --all

# 2. Regenerate the dashboard bundle
python -m lib.web_export

# 3. Schema + pipeline tests
python -m pytest -q

# 4. Web build
cd web && npm run build
```

Baseline before this wave: **126 tests passing**. A lower pass count or a new
failure is a regression — diagnose it, do not paper over it.

`web/AGENTS.md` warns that this Next.js version has breaking changes versus
what you may expect. If the build fails, read the relevant guide under
`node_modules/next/dist/docs/` before changing any web code. Most likely you
will not need to touch `web/` at all — this is a data change.

## Sanity checks before you commit

```bash
# Gap count should be <= 9 and never higher than before
python -c "import json;print(len(json.load(open('web/public/data/gaps.json',encoding='utf-8'))))"

# sources.csv row count should track DataPoint count
python -c "
import json,glob
print('dp:', sum(len(json.load(open(f,encoding='utf-8'))['data_points']) for f in glob.glob('data/processed/*.json')))
"
wc -l < data/sources.csv
```

If the gap count went **up**, something regressed in the merge — investigate
before shipping.

Note: `data/manual/*` is gitignored except `insights/` and `analysis/`, so
research drop files will correctly not appear in `git status`. That is by
design — `data/sources.csv` is the ledger.

## Landing it — this part matters

**Never push directly to `main`.** Vercel blocks builds whose commit author is
not linked to a Vercel seat (`seatBlock`, `blockCode: COMMIT_AUTHOR_REQUIRED`).
Such deployments show as `BLOCKED` with **no build logs at all** — production
silently keeps serving the previous build, which reads exactly like a
successful deploy until someone notices the data is stale. Merge commits
created by GitHub when a PR is merged are authored by the GitHub account and
deploy normally.

```bash
git add -A
git commit   # message below
gh pr create --fill
gh pr merge --squash
```

Suggested commit message:

```
Research wave 2: close 33 of 42 core-metric gaps

105 new claims across KR skincare sub-segments (first primary MFDS
production data in the repo), IN skincare sub-segments, and segment-level
sizes for KR/IN bath_shower, deodorants, oral_care, fragrances, baby_child
and emerging_adjacencies.

346 -> 450 DataPoints. Sub-segment coverage 19 -> 32 of 34.
Conflicting estimates recorded as cross-referenced pairs, never averaged.
Nine growth_yoy/cagr_forecast cells remain open by design.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
```

## After the merge

Confirm the Vercel deployment actually built rather than landing in `BLOCKED`.
A green PR merge is not by itself evidence that production updated.

## Report back

Under 200 words: test count, build result, gap count before/after, PR URL,
deployment state. If anything failed, say so with the actual output rather
than a summary — a failure reported as a success is the worst outcome here.
