# Task 1 — Integrity audit of the wave-2 claims

**Model: Sonnet. No web access needed. Runs in parallel with Task 3.**
**Read `docs/agent-protocol.md` first. Read nothing else in the repo.**

## Context

A research wave merged 105 new claims into `data/processed/`, taking the repo
from 346 to 450 DataPoints and closing 33 of 42 open core-metric gaps. The
claims came from six agents working in isolation. Nobody has checked them
against each other. That is your job.

You are auditing **already-merged** data. You do not add numbers and you do not
research.

## Your single write target

`docs/audit-wave-2.md` — a findings report. Create it. Touch nothing else.
You may NOT edit `data/processed/`, `data/sources.csv`, or any drop file; you
recommend fixes, the main session applies them.

## Step 1 — mechanical scan (cheap, do this first)

```bash
python -m scripts.research_kit audit
```

Every finding it prints is a *prompt for review*, not an automatic failure.
Triage each one: real problem, or acceptable-with-reason. Say which.

It currently returns **70 findings across 13 files**, distributed like this:

| File | Findings | Wave |
|---|---|---|
| `colour_hair_subs.json` | 18 | 1 (pre-existing) |
| `kr_segments_b.json` | 13 | **2** |
| `dermocosmetics.json` | 12 | 1 (pre-existing) |
| `mens_grooming.json` | 11 | 1 (pre-existing) |
| `channel_shares.json` | 9 | 1 (pre-existing) |
| `sun_care.json` | 4 | 1 (pre-existing) |
| `in_skincare_subs.json` | 2 | 1 (pre-existing) |
| `margins_penetration.json` | 1 | 1 (pre-existing) |

Two things follow from that distribution, and both should shape your report:

- **54 of 70 findings are on wave-1 files**, merged before this wave. That is
  pre-existing debt, not a regression introduced now. Report it separately so
  it does not block shipping wave 2 — but do report it, because it is real.
- **Five of the six wave-2 files return zero findings.** The exception is
  `kr_segments_b.json` (13), whose agent was killed by a session limit
  mid-work. Treat that file as the least-supervised in the wave and give it
  the closest reading — it is the most likely place for an unfinished or
  unreviewed claim.

## Step 2 — judgement checks the scanner cannot make

Load the processed data with a script, not by reading files into context:

```bash
python -c "
import json,glob,collections
rows=[]
for f in glob.glob('data/processed/*.json'):
    for p in json.load(open(f,encoding='utf-8'))['data_points']:
        rows.append(p)
print(len(rows))
"
```

Then check these five things, each with a targeted query rather than a full read:

1. **Cross-reference pairs are symmetric.** Where two sources conflict on the
   same cell, the wave's convention is that BOTH are recorded and EACH names
   the other in `notes` with "do not average". Find cells with 2+ `market_size`
   claims for the same period and confirm the notes actually cross-reference.
   A one-sided pair is a real defect — the dashboard will show two numbers with
   only one carrying the caveat.
2. **`value_basis` is never conflated.** Korea has RETAIL, EXPORT_FOB and
   PRODUCTION figures sitting in the same segment files now. Confirm no claim
   compares or derives across bases. The MFDS production figures are the ones
   to watch.
3. **The known double-count trap.** MFDS reports lotion/cream **and**
   essence/oil as one line. It was filed under `facial_moisturisers` only, with
   a note saying it must not be added to any `serums_ampoules` figure. Verify
   that note survived the merge and that no serums claim double-counts it.
4. **India coverage statements.** Every India size/share claim should state
   organised vs unorganised coverage, or explicitly say the source is silent.
5. **`[CORRIDOR]` tagging.** K-beauty-inside-India figures must carry it.

## Step 3 — the outlier sweep

Flag any claim where the number is implausible against its neighbours, and say
what you'd do about it. Two known live examples to assess, both already
recorded as unresolved pairs:

- Aggregator "Korea serum/toner/moisturiser market" figures sit roughly **30x
  below** Korea's own MFDS production statistics. Scope and basis differences
  do not explain a gap that size.
- IMARC's India **bath soap alone** (USD 3,406mn, 2025) exceeds IMARC's own
  wider **bath & shower** category (USD 1.8bn, 2025) that IMARC says contains
  it. One of the two is wrong.
- Renub rebased India oral care down ~40% between two of its own publications
  with no stated definitional change.

For each: is recording both sides sufficient, or should one side be withdrawn?
Recommend, with a reason. Precedent: a fragrances `niche_artisanal` 80% share
was withdrawn pre-merge because flagged-in-notes is not enough protection once
a figure renders on the dashboard as a share.

## Output format for `docs/audit-wave-2.md`

```markdown
# Wave-2 integrity audit
## Verdict
<2 sentences: is this data safe to publish as-is?>
## Must fix before publish
- <finding> — <file/cell> — <recommended action>
## Should fix
## Accepted with reason
## Scanner findings triaged
<the audit output, each line marked REAL or OK-because-X>
```

Rank by severity. If nothing must be fixed, say so plainly — do not invent
findings to look thorough.

## Report back

Under 200 words, per the protocol's report contract. Lead with the verdict.
