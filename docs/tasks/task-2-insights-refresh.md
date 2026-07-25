# Task 2 — Refresh analyst insights against the new data

**Model: Sonnet. No web access needed.**
**Depends on Tasks 1 and 3 landing first — the data must be final.**
**Read `docs/agent-protocol.md` first. Read nothing else in the repo except
what this brief names.**

## Context

`data/manual/insights/*.json` holds the dashboard's "Analyst read" panels —
commentary that interprets existing DataPoints. A research wave just added 105
claims and closed 33 of 42 gaps, so some of that commentary is now stale or
factually wrong.

There are 13 insight files:
`baby_child, bath_shower, colour_cosmetics, deodorants, dermocosmetics,
emerging_adjacencies, fragrances, hair_care, mens_grooming, oral_care,
skincare, sun_care, total_bpc`.

## Your single write target

The files inside `data/manual/insights/` — and only those. Do not touch
`data/processed/`, `data/sources.csv`, drop files, `lib/`, or `web/`.
Do not run `lib.web_export` (the main session does that; it copies these files
verbatim into the web bundle).

## The binding constraint on this task

Insights **interpret** DataPoints. They are never a new source of numbers.
Specifically:

- Every figure you cite must already exist in `data/processed/`. Quote it as it
  is recorded — same value, same period, same basis.
- **Never derive an implied statistic by combining two DataPoints.** No
  "which implies a X% share", no computed ratios across claims.
- Always name the `confidence` and `value_basis` when leaning on a figure.
- For any KR-vs-IN "combined" read: `value_usd_bn` only, and only when both
  sides actually have it. Never net across `value_basis`.
- A segment whose data is thin should say so. "Research needed" is a valid
  analyst read; a hedged guess is not.

## Method (cheap)

1. Find what changed. Do not read all 13 insight files into context — query
   first:

```bash
python -c "
import json,glob,collections
new=collections.defaultdict(list)
for f in glob.glob('data/processed/*.json'):
    d=json.load(open(f,encoding='utf-8'))
    for p in d['data_points']:
        if str(p.get('date_accessed','')).startswith('2026-07-25'):
            new[(p['geography'],p['segment'])].append(p['metric'])
for k,v in sorted(new.items()): print(k, sorted(set(v)))
"
```

2. That prints exactly which segment × geography pairs gained data today. **Only
   open the insight files for those segments.** Leave the rest untouched.
3. For each affected file: read it, check every factual assertion against the
   current processed data, and correct only what the new data makes wrong.

## What counts as "made wrong"

Fix these:
- A claim that a figure is unavailable, when it now exists.
- A stated number that has been superseded or contradicted by a new claim.
- A trend or ranking that the new data reverses.
- A confidence characterisation that no longer holds (e.g. "only a
  LOW-confidence estimate exists" when a HIGH government figure landed).

Do **not** rewrite prose for style, tighten wording, or restructure panels.
Minimum edit that restores factual accuracy. Preserve each file's existing
JSON shape exactly.

## Specific things the wave changed that likely affect commentary

- **KR skincare** gained the first primary (HIGH) sub-segment data in the repo:
  MFDS 2024 production values for facial moisturisers, sheet masks and
  cleansers, on a PRODUCTION basis in KRW. Any insight saying KR sub-segment
  data does not exist is now wrong.
- **KR bath_shower, fragrances, oral_care** gained production values and sizes.
- **IN bath_shower, deodorants, oral_care** went from little or nothing to
  sized (all LOW confidence, aggregator-sourced).
- **KR fragrances** carries a ~2.5x aggregator dispersion — commentary must not
  quote a single headline size as settled.
- Several cells remain **standing on purpose**, notably IN `toners_essences`
  market size and 8 remaining `growth_yoy` cells. If an insight promises those
  numbers, correct it to say they remain open.

## Report back

Under 200 words. List each file you changed and the one-line reason. List the
files you deliberately left alone. If a segment's data changed but the existing
commentary is still accurate, say so — that is a real finding, not a gap.
