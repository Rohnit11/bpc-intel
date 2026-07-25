# Task 3 — Close the 9 residual gap cells

**Model: Sonnet. Web research. Runs in parallel with Task 1.**
**Read `docs/agent-protocol.md` first — especially the fetch budget and the
blocked-domain list. Read nothing else in the repo.**

## Context

A research wave closed 33 of 42 open core-metric gaps. Nine survive, and they
are hard for a structural reason: **eight of them are `growth_yoy`**, and
aggregator reports publish base-year levels and forward CAGRs, not year-on-year
prints. Three separate agents last wave tried and failed to find India
`growth_yoy` from aggregators. Do not repeat that sweep.

Confirm the live list before you start (it should match):

```bash
python -m scripts.research_kit cells
```

Expected:

```
KR deodorants cagr_forecast
KR baby_child growth_yoy
KR emerging_adjacencies growth_yoy
IN fragrances growth_yoy
IN bath_shower growth_yoy
IN deodorants growth_yoy
IN oral_care growth_yoy
IN baby_child growth_yoy
IN emerging_adjacencies growth_yoy
```

## Your single write target

`data/manual/research_drops/residual_gaps.json` — build it with
`research_kit add`, one claim at a time. Never re-write the file wholesale.
Never run `--all`, `lib.web_export`, or git.

## Where `growth_yoy` actually comes from

This is the whole point of the task. Aggregators will not give it to you. These
will:

1. **Two years of the same source.** If a publisher gives a level for 2023 and
   for 2024 on pages you both fetch, the YoY is arithmetic. Record it as
   `confidence: ESTIMATE` with `methodology` showing the two inputs, both URLs,
   and the arithmetic. This is how last wave got KR bath_shower (+9.88%) and
   fragrances (+14.67%) — from the MFDS two-year annex table. It is the highest-
   yield technique here.
2. **Government series.** KR: MFDS (식약처) production statistics carry a
   prior-year column; 의약외품 (quasi-drug) statistics cover deodorants and
   some baby lines. KOSIS and KHIDI publish annual series.
3. **Company results commentary.** India: Dabur, Godrej Consumer, HUL, Emami
   and Colgate quarterly and annual results discuss category growth explicitly
   ("the deodorants category grew X%"). That is a category `growth_yoy`
   statement from a primary source — HIGH or MEDIUM confidence, far better than
   anything an aggregator gives. Investor presentations and earnings-call
   transcripts are the richest seam.
4. **NielsenIQ / Kantar FMCG releases.** They publish category-level growth,
   though often only for aggregate HPC — check whether the specific category is
   broken out before spending fetches.

**Do not** convert a CAGR into a YoY. They are different measures and the
substitution would be fabrication.

## Per-cell method

1. Search. 2. Fetch only pages whose snippet already shows a number for your
exact geography and category. 3. Cap at **6 fetches per cell** — at the cap with
nothing defensible, stop and record the cell as standing.

A derived two-year YoY needs: both source URLs actually fetched, both levels
quoted in `methodology`, the arithmetic shown, and a sensitivity note if either
input is soft.

## Rules that will bite on these specific cells

- **India:** state organised vs unorganised coverage. It matters most for
  `emerging_adjacencies` (ayurvedic/herbal has a very large unorganised tail)
  and `baby_child`.
- **Korea:** RETAIL, EXPORT_FOB and PRODUCTION are three different measures.
  A production-basis YoY is a real and useful number — just tag it `PRODUCTION`
  and say so in notes. Do not present it as retail growth.
- **`emerging_adjacencies` is a composite.** If you can only size or grow a
  component, file it under the taxonomy sub-segment — `beauty_devices`,
  `ingestible_nutricosmetics`, `clean_vegan`, `kbeauty_derivative`,
  `halal_certified`, `ayurvedic_herbal` — never as the whole segment.
- Any K-beauty-inside-India figure carries `[CORRIDOR]` in notes.
- `growth_yoy` takes a single period (`"2024"`, `period_type: "CY"`), never a
  range.

## Known dead ends — do not spend fetches here

Last wave burned real budget on these. `grandviewresearch.com/horizon/*` (403),
`statista.com/outlook/*` (values render as `****`), `dataintelo.com` (403),
`marketresearch.com` (403), `euromonitor.com` (paywalled),
`researchandmarkets.com` (410), `theprint.in` (bot interstitial),
`sphericalinsights.com` (TLS failure). A Euromonitor deodorants-India figure
("INR 63.5bn, 10% growth") circulates in search snippets but could not be
verified on any fetchable page — do not cite it from a snippet.

## Expected outcome

**Closing 4–5 of 9 would be a good result. Closing 0 with honest reasoning is
an acceptable one.** These cells survived a six-agent wave. The failure mode to
avoid is manufacturing a number to close a cell — a standing gap is
information, a fabricated number is contamination.

## Report back

Under 200 words, per the protocol's report contract.
