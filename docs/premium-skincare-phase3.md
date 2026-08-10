# Premium Skincare — Phase 3 output: demand, and whether "Korean" is load-bearing

> **Answers Q3** ("is 'Korean' load-bearing for the Indian premium buyer, or
> incidental?") from `docs/premium-skincare-brief.md`, plus the two demand
> questions attached to it: who buys at Rs1,500-3,000, and are Indian D2C brands
> closing the band. Run 2026-08-10. Namespace `[PREMIUM-SKIN]`.
>
> Per the brief, this is a **positioning input, not a go/no-go**. Nothing below
> kills the concept. Several things below change what the brand leads with.
>
> **Read this before Phase 4.** Everything is on disk; nothing is carried in chat.

## 0. Verdict

**"Korean" is not load-bearing. It is not even spoken.** Across 2,676
positive-frame Nykaa reviews of in-band SKUs, Korean provenance is invoked in
2.2% — behind repurchase intent (10.8%), the pigmentation concern (10.8%),
actives (9.9%), reported results (7.7%) and price (6.5% accept / 3.7% resist).
On the 2,143 reviews of **Korean-origin** SKUs specifically it reaches 2.6%,
against 11.3% naming an active: buyers of Korean products talk about the
ingredient **4.3x more often** than about Korea.

The strong test is the contrast, and it is categorical:

| Reviews of in-band SKUs, positive frame | n | Mention Korea / K-beauty | Name an active |
|---|---:|---:|---:|
| Korean-origin SKUs | 2,143 | 56 (**2.6%**) | 11.3% |
| Indian-origin SKUs | 333 | **0 (0.0%)** | 4.5% |
| Other-foreign SKUs | 179 | 2 (1.1%) | 3.4% |

Not one of 333 reviewers of an Indian in-band SKU reached for Korea as a
benchmark. At the Korean-SKU rate you would expect ~9. **Korea is not a category
reference point buyers use; it is a fact about products that happen to be
Korean.** And of the 81 reviews that do cite Korean origin or the Korean
aesthetic, 67 (82.7%) name no active and report no result — so the provenance
buyer exists but is 2.5% of the frame and is not mechanism-literate.

Search demand says the same at a different scale. In one comparable Google Trends
payload for India (trailing 12 months): `sunscreen` 60.2, `dermatologist` 15.6,
`niacinamide` 12.1, `vitamin c serum` 9.2, **`korean skincare` 0.6**. On a
five-year window against a non-saturating anchor: `niacinamide` 53.9, `cosrx`
8.3, `glass skin` 6.7, `k beauty` 3.6, `korean skincare` 2.4.

**What this does not license.** Reviews are written after purchase, about the
experience, and people do not restate what they take for granted; the control
proves the instrument is blunt, because *all* provenance language is near-absent
(other-origin terms fired once in 2,676 reviews). So the finding is bounded:
**the word "Korean" is not part of the vocabulary Indian buyers use in this
band.** That is a claim about salience, not proof that Korean manufacturing does
not sell product. It is exactly enough to settle the positioning question the
brief asked, and not enough to demote Korea as a manufacturing decision.

**Consequence for the brand.** Korea becomes a supply-side quality decision, and
the brand leads on the concern (pigmentation), the mechanism (named actives), and
the reason to come back. The one Indian founder who has run this experiment
longest agrees, and names the mechanism: *"With an influx of Korean brands that
are so readily available, being made in Korea is hardly an edge anymore"*
(Shamika Haldipurkar, D'you — [The Nod Mag](https://thenodmag.com/content/indian-skincare-brands-made-in-korea)).

**Two findings that outrank the Q3 answer for Phase 4.** Both are new:

1. **The band is a budget event, not a basket top-up.** Nykaa's Beauty AOV is
   **Rs2,173** (Q3FY26, HIGH — company filing). One in-band SKU *is* an average
   order. And India's highest-income cohort (>USD15k p.a.) spends **USD140 a
   year on all BPC** at 18 purchase occasions — ~Rs748 an occasion. A Rs1,900 SKU
   is 2.5x that, and 14.1% of that cohort's entire annual budget [ESTIMATE, §3].
2. **The lane is occupied.** "Formulate in Korea, tune to Indian skin and
   weather, sell as an Indian brand" has been executed since 2020 by **D'you**
   (Rs1,680-3,500) and since 2022 by **Put Simply** (Rs825-1,699), plus Quench.
   Put Simply's founder states the brief almost verbatim. The repo had none of
   them on file.

---

## 1. Scope and caveats (read before quoting any number here)

- **Two evidence bases, different weights.** (a) The 3,287-review Nykaa corpus
  from Phase 2, re-mined for purchase-driver language — statistics about
  **reviews**, never about buyers. (b) Documents fetched 2026-08-10: two Nykaa
  investor presentations (HIGH, company filings), one MOFSL initiation note on
  Nykaa (MEDIUM, brokerage citing Redseer and company data), one trade-press
  piece, one magazine feature, two brand storefronts, two aggregator pages (LOW).
- **Frames are never pooled.** The corpus is every retrievable 1-2 star review
  plus the top pages of Nykaa's "most useful" ordering (overwhelmingly 5-star).
  Rates are computed inside a frame. "Positive frame" = most-useful, n=2,676;
  "negative frame" = n=651.
- **Origin, not Phase 1's brand groups.** Phase 1's `other_observed` bucket mixes
  Korean brands (Klairs, SKIN1004, d'Alba, belif, Aestura, Celimax, Torriden,
  Thank You Farmer, Round Lab) with European ones (Uriage, ISDIN, Eucerin), so it
  cannot answer a question about origin. Every SKU is re-keyed by brand
  provenance in `lib/transforms/premium_skin_demand.py`; brands whose origin is
  not established stay `unclassified` (21 of 3,287 reviews) rather than being
  guessed into a bucket.
- **Online only, organised only.** As in Phases 1-2. India's BPC market is 52%
  unorganised offline / 28% organised offline / **20% online** in FY25 (Redseer
  via MOFSL). Every observation in this thread lives in that 20%, and Nykaa is
  27-29% of it. Offline stays deferred to Phase 4 — and §6 argues that deferral
  is now the largest open risk to Phase 1's verdict.
- **Google Trends is a relative index.** No DataPoints, matching
  `lib/fetchers/trends_google.py`. Google rate-limited roughly half the sweep
  across four attempts: of six baskets, four landed on both time windows,
  `origin_terms` landed only its 12-month window, `origin_terms_fine` only its
  5-year window, `premium_intent` never landed, and all three related-query pulls
  were refused. The raw files record every failure with an `error` key rather than
  omitting the row.
- **Nykaa exposes no demographics.** No income, city, age or channel field on a
  review. The buyer-cohort half of this phase is therefore answered entirely from
  disclosed platform and brokerage data, and the gaps are named in §7.

---

## 2. The demand vocabulary, ranked

What buyers actually volunteer, positive frame (n=2,676). Rates are the share of
reviews invoking a theme at all; the split shows how many assert it versus
pre-emptively deny it.

| Driver | Mentions | Rate | Asserted / negated |
|---|---:|---:|---|
| Repurchase / loyalty | 289 | **10.8%** | 286 / 3 |
| Pigmentation concern | 288 | **10.8%** | 273 / 15 |
| Ingredient / actives | 264 | **9.9%** | 254 / 10 |
| Reported result | 207 | 7.7% | 200 / 7 |
| Price — worth it | 173 | 6.5% | 170 / 3 |
| Routine / multi-step | 103 | 3.8% | 97 / 6 |
| Price — resistance | 99 | 3.7% | 98 / 1 |
| **Korean provenance** | 59 | **2.2%** | 55 / 4 |
| Climate / humidity | 54 | 2.0% | 39 / 15 |
| Social / hype | 51 | 1.9% | 50 / 1 |
| Derm authority | 29 | 1.1% | 29 / 0 |
| Korean aesthetic (glass skin) | 27 | 1.0% | 27 / 0 |
| Discount mentioned | 23 | 0.9% | 22 / 1 |
| Word of mouth | 7 | 0.3% | 7 / 0 |
| Other origin (Japan/France/etc.) | 1 | 0.0% | 1 / 0 |

Three readings the brief should absorb:

**(a) Repurchase language is the single most common thing a satisfied in-band
buyer says** — 10.8%, and 286 of 289 asserted ("third bottle", "holy grail", "my
go-to", "using it for months"). This is the first repeat-purchase evidence in the
repo for this band, which §2 of the brief listed as missing. It is not a
retention rate; it is what loyalty *sounds like* here, and it is a stronger
theme than every acquisition driver.

**(b) Derm authority is nearly absent (1.1%) — except where the price is
highest.** By MRP third: 0.8% at Rs1,500-1,999, 0.5% at Rs2,000-2,499, **4.3% at
Rs2,500-3,000**. Price resistance moves the same way (3.1% / 3.2% / **7.9%**).
Above Rs2,500 buyers start demanding a reason, and clinical authority is the
reason they reach for.

**(c) The negative frame is a price frame.** In 651 1-2 star reviews the top
theme is "not worth the money" — `price_worth` fires 59 times and **53 of those
are negations**, with price resistance asserted 46 times more. Then social/hype at
8.9%, versus 1.9% in the positive frame: **hype-acquired buyers are 4.7x
over-represented among unhappy ones.** Buying attention in this band converts
into 1-star reviews.

---

## 3. Who buys at Rs1,500-3,000 — the affordability arithmetic

The brief asked for income cohort, metro/Tier 2-3, age and channel. What
disclosed data supports:

| Fact | Value | Source, confidence |
|---|---|---|
| Nykaa Beauty AOV | **Rs2,173** (Q3FY26); Rs2,009 (Q1FY26), +4% YoY | Nykaa investor presentations, **HIGH** |
| Beauty transacting customers | 18.7mn AUTC, +26% YoY; ~42mn cumulative | Nykaa Q3FY26, HIGH |
| Annual BPC spend per consumer | USD30 / 50 / 79 / 116 / **140** across five income cohorts (entry-level <USD3k p.a. → high-income >USD15k p.a.) | MOFSL Exhibit 12, MEDIUM |
| Annual BPC purchase frequency | 16 / 16 / 17 / 17 / **18** across the same cohorts | MOFSL Exhibit 14, MEDIUM |
| Channel mix FY25 → FY30E | unorganised offline 52→34%, organised offline 28→32%, online 20→34% | Redseer via MOFSL, MEDIUM |
| India BPC market | USD24bn FY25 → USD40-45bn FY30E (~12% CAGR); online USD5bn → USD14-15bn | Redseer via MOFSL, MEDIUM |
| Skincare category growth | 13% CAGR FY25-30, fastest of the beauty categories | Redseer via MOFSL, MEDIUM |
| Gen Z | 26% of population, ~50% of consumption; "shaped by Korean beauty and ingredient-led formulations" | Anchit Nayar (Nykaa) via BeautyMatter, MEDIUM |

**The 5x/1.1x asymmetry is the finding.** Spend rises 4.7x from the bottom income
cohort to the top; frequency rises from 16 to 18 occasions. MOFSL states it
plainly: *"purchase frequency does not necessarily decline with rising income
levels; instead, consumers often maintain similar buying intervals while moving up
to more premium, value-conscious products."* **Indian premiumisation is
price-per-unit, not frequency.** That is the strongest argument in this phase
*for* a price-led entry: the market grows by trading up the same ~17 occasions.

**And it caps the prize** [ESTIMATE, ledgered with methodology and sensitivity]:

- USD140 × Rs96.23 (pinned FX) = **Rs13,472** — the entire annual BPC budget of
  India's highest-income cohort, across all categories and all channels.
- ÷ 18 occasions = **~Rs748 per purchase occasion**.
- A Rs1,900 in-band SKU (Phase 1's recommended floor) = **2.5x an average
  occasion**, and **14.1%** of that cohort's whole annual budget. At Rs1,500 it is
  11.1%; at Rs2,900, 21.5%. Against the mid-level-professional cohort (USD116):
  13.4% / 17.0% / 26.0%.
- **A four-SKU routine at Rs1,900 each (Rs7,600) is 56.4% of that annual budget.**

Basis mismatch stated deliberately: the denominator is annual outlay across all
BPC including mass personal care, the numerator is one skincare MRP. It is an
affordability index, nothing more. But the direction is unambiguous and it
qualifies the brief's third binding consequence: **range economics hold on the
ODM/MOQ side and do not transfer to the consumer.** Nobody in this cohort buys a
four-SKU premium routine in one order. Sequential single-SKU adoption, with the
range assembled over months, is the only realistic demand path — which makes
repurchase (§2a) the metric that matters and trial cost the binding constraint.

**What is missing:** no source fetched in this phase discloses an income, age or
Tier 2/3 split of *premium-band* transactions. Nykaa's disclosures are
platform-wide. The closest proxies are its store network (56% of its 116
multi-brand Beauty stores in Tier 2 and 3 cities) and its eB2B arm (~88% of House
of Nykaa GMV from Tier 2+ cities) — both offline, both Phase 4 material.

---

## 4. Is "Korean" load-bearing? The full answer

### 4.1 Review language: no (§0 for the headline table)

By hero format, positive frame:

| Driver | Korean sunscreen (n=657) | Pigmentation serum (n=693) |
|---|---:|---:|
| Korean provenance | 3.8% | 2.0% |
| Ingredient / actives | 6.7% | **12.8%** |
| Reported result | 4.0% | **16.7%** |
| Pigmentation concern | 3.2% | **27.7%** |
| Repurchase / loyalty | **12.0%** | 7.6% |
| Climate / humidity | **4.7%** | 0.3% |
| Price — worth it | 6.5% | 6.6% |

**The two hero products are sold on completely different logics.** The
pigmentation serum is a *problem-and-proof* purchase: a quarter of happy
reviewers name the concern, a sixth report a result. The sunscreen is a *habit*
purchase: nobody claims a result, they claim they keep buying it, and climate
comes up 15x more often than on serums (Phase 2's finding that heaviness in
humidity is the live sunscreen failure, seen from the demand side).

By self-declared skin tone (positive frame; tone is declared on 1,275 of 3,287
reviews and skews fair, per Phase 2):

| Tone group | n | Korean provenance | Pigmentation concern |
|---|---:|---:|---:|
| Fair / Light | 705 | 1.7% | 6.8% |
| Medium / Medium Dark | 302 | 2.0% | 11.6% |
| Dark / Deep | 72 | **0.0%** | **16.7%** |

Small cell at the deep end, so directional only — but the direction is
consistent: **the deeper the declared tone, the more the review is about
pigmentation and the less it is about Korea.** The customer the skin-tone thesis
is aimed at is the least provenance-driven customer in the corpus.

### 4.2 Search demand: no, by one to two orders of magnitude

India, trailing 12 months. Google normalises each payload to its own maximum, so
terms are only comparable when they were requested together — which is why
`lib/fetchers/premium_skin_demand_trends.py` sends each basket as one payload and
carries `sunscreen` in every basket as a shared anchor. The anchor came back at
60.21-60.26 across all four baskets below, so chaining them onto one scale is
sound to about a percent:

| Term | Index (mean) |
|---|---:|
| sunscreen | 60.2 |
| acne | 32.8 |
| dermatologist | 15.6 |
| niacinamide | 12.1 |
| pigmentation | 10.9 |
| vitamin c serum | 9.2 |
| dark spots | 4.5 |
| melasma | 2.0 |
| glass skin | 1.7 |
| beauty of joseon | 1.5 |
| cosrx | 1.4 |
| k beauty | 1.0 |
| **korean skincare** | **0.6** |
| korean sunscreen | 0.2 |

Caveats that bind: the `sunscreen` anchor peaks every Indian summer and crushes
small terms into an integer 0-2 index, so read orders of magnitude and never
trends; brand terms are hostage to the exact string (`minimalist skincare`
returned 0.0, which is about the phrase, not the brand). A five-year window
against `niacinamide` as anchor gives better resolution at the bottom:
`niacinamide` 53.9, `cosrx` 8.3, `glass skin` 6.7, `k beauty` 3.6,
`korean skincare` 2.4.

Two things fall out:

- **The aesthetic outsearches the provenance.** `glass skin` beats
  `korean skincare` on both windows. If any part of the Korean story has pull, it
  is the *look*, not the *passport*.
- **`foxtale` (6.7) outsearches `beauty of joseon` (1.5) and `cosrx` (1.4) by
  ~4.5x** — an Indian D2C brand whose SKUs top out at Rs695, commanding more
  search demand from below the band than the Korean incumbents command inside it.
- **Acne (32.8) outranks pigmentation (10.9) by 3x.** Phase 2 found Indian PIH is
  acne-driven and starts young; demand confirms the entry point is acne. A
  pigmentation hero sells the *sequel* to the concern that brings people into the
  category — an acquisition cost the brief has not priced.

### 4.3 Supply-side: provenance is losing scarcity, fast

Of the nine global brand launches Nykaa featured in Q3FY26, **four are Korean**
(Fwee, Parnell, Ariul, d'Alba Piedmont); three of eight in Q1FY26 are Korean
skincare. MOFSL's log of prestige launches records TIRTIR, Numbuzin, AXIS-Y
(3QFY25), Dr. Jart and Aestura (4QFY25-2QFY26). Korean brands enter through the
**prestige** slate and are absent from the ultra-luxury slate (Chanel, La Prairie,
YSL, Armani, Dr. Barbara Sturm) — prestige is precisely the Rs1,500-3,000 rung.

And the push is partly *Korean* in origin, not Indian: Personal Care Insights
(Apr-2026) reports Korean firms accelerating into India to offset SWANA
volatility and stricter EU rules, with APR launching Medicube and Amorepacific
introducing Illiyoon, both via Nykaa. **The supply of Korean competitors in this
band is a function of Korean export diversification, so it can intensify faster
than Indian demand grows.** That is a Phase 4 risk-register line, and it is the
mechanism behind Haldipurkar's "hardly an edge anymore".

---

## 5. Is the band being closed domestically? Yes — by brands the brief never named

Re-keying the Phase 1 price sweep to origin, restricted to the 36 **brand-neutral**
queries (concern and format terms like "pigmentation serum", "sunscreen spf 50" —
the only part of the sweep whose origin composition means anything, since the 81
brand queries were 45 Korean to 20 homegrown by design):

| Origin | In-band single-SKU observations | Distinct brands | Median MRP | Still in-band at street price |
|---|---:|---:|---:|---:|
| Korea | 126 | 29 | Rs2,000 | 78.6% |
| **India** | **34** | **12** | Rs1,800 | **88.2%** |
| Other foreign | 15 | 8 | Rs2,700 | 93.3% |
| Unclassified | 16 | 6 | Rs1,980 | 50.0% |

The twelve Indian brands holding in-band single SKUs on concern-led search: **RAS
Luxury Oils, Suganda, Yuderma, Ethiglo, WildGlow, BiE, The Derma Co, TBC The Bath
& Care, Miduty, Fixderma, Aminu, Forest Essentials** (plus Kama Ayurveda across
the whole sweep). Minimalist, Dot & Key, Foxtale, Pilgrim, Deconstruct, Earth
Rhythm and Plum remain absent — **Phase 1's categorical finding survives
re-testing, and was answering a question about the wrong brands.**

Two things make this cohort a sharper threat than the D2C names:

1. **They hold price better.** 88.2% of Indian in-band SKUs still transact
   in-band against 78.6% of Korean ones. On the whole sweep it is 92.3% versus
   79.6%. The discount pressure in this band is *Korean* pressure.
2. **They already own the demand vocabulary.** In positive reviews, **RAS Luxury
   Oils: 50.0% name a pigmentation concern and 30.1% report a result. Suganda:
   50.0% and 15.9%.** Compare COSRX (16.0% / 8.2%) and Anua (12.5% / 10.8%). The
   concern-and-proof language the brief wants to own is being spoken best by
   small Indian brands at Rs1,599-1,990.

Structurally this keeps coming: 800+ D2C BPC brands launched in India since 2020,
D2C is ~15% of BPC and forecast to compound 22-27% to 2030, and the platform is
itself a competitor — Dot & Key (Nykaa-owned) runs a Rs1,500cr+ GMV rate and
ranks #1 in skin, moisturiser and sunscreen on Nykaa.

**And the exact lane has incumbents.** Indian brands formulating in Korea, from
[The Nod Mag](https://thenodmag.com/content/indian-skincare-brands-made-in-korea)
and their own storefronts:

| Brand | Launched | Prices (own site, 2026-08-10) | Position vs band |
|---|---|---|---|
| **D'you** (Shamika Haldipurkar) | 2020 | hustle serum Rs3,200; in my defence Rs3,500; embrace Rs3,400; unkissed SPF50 Rs2,200; good grease Rs2,000; inbalance Rs1,680 | 3 SKUs in-band, 3 above, **no discount** |
| **Put Simply** (Anirudh Kastia) | 2022 | Beat The Sun Rs1,099→Rs825; Ray Away Rs1,499→Rs899; Daily Affermation Rs1,699→Rs899; duos Rs2,598→Rs1,599 | below band on singles |
| Quench | not stated | not researched | unknown |

Same manufacturing geography, prices four times apart. **Korean formulation does
not set a price point; brand architecture does.** Kastia's stated brief is the
owner's: he *"wanted to create a skincare range developed in Korea specifically
for Indian skin and weather"*, and on Phase 2's live failure mode: *"The
ingredient mix, textures, and characteristics are carefully selected to suit our
skin and weather."* Put Simply's storefront also confirms Phase 2 from the
marketing side — every sunscreen leads with **"Zero White Cast"** and the trust
stack reads *"Dermatologically tested / Sensitive skin-friendly / Made in
Korea"*, with provenance third.

**Correction to Phase 1's competitive set:** Limese is not a homegrown brand. Its
own About page describes an importer and multi-brand retailer of Korean skincare
(founder Dale Deugcheon Han; Seoul sourcing, Mumbai operations; By Wishtrend,
COSRX, I'M FROM, Dear Klairs, Numbuzin, One Thing, OOTD, P. Calm, Rom&nd,
Treecell; 20+ brands, 350+ products). It belongs in `config/corridor.yaml`'s
conduit list, not the homegrown competitive set. Phase 1's "coverage gap" on
Limese is therefore closed as a mis-classification, not a gap.

---

## 6. What Phase 3 changes about earlier phases

1. **Phase 1's Rs1,900 floor gets a second, independent reason.** Phase 1 set it
   on discount retention. §3 adds that Rs1,900 is already 2.5x an average
   purchase occasion for the top income cohort — so the floor is where
   affordability and discount-retention meet, not a comfortable middle.
2. **The routine-vs-SKU question Phase 1 flagged for Phase 3 is answered: SKU.**
   Only 3.8% of positive reviews describe a routine at all, and a four-SKU
   routine is 56.4% of the top cohort's annual BPC budget. Launch a range for
   MOQ and shelf reasons; do not model consumer demand as routine adoption.
3. **Phase 1's "no Indian D2C in the band" holds but was the wrong question.**
   §5: twelve Indian-origin brands hold in-band single SKUs, and they hold price
   better than the Korean cluster.
4. **Phase 2's white-cast conclusion is corroborated from the marketing side.**
   Korean-made brands selling to India lead with "zero white cast" as
   table stakes.
5. **The offline deferral is now the biggest open risk to the whole thread.**
   About two-thirds of Nykaa store GMV is premium brands, offline rose from 3.4%
   (1QFY22) to 9.0% (3QFY25) of its BPC GMV, and 52% of India's BPC is still
   unorganised offline. Premium concentrates in the channel this thread has never
   observed. Phase 4 must treat offline as primary, not as a section.
6. **The deck's ~22% tier CAGR now has a MEDIUM-confidence neighbour.** Redseer
   via MOFSL puts all-India skincare at 13% CAGR FY25-30. Different scopes (a
   whole category versus one MRP band) so not a refutation — but any Phase 4
   model leaning on 22% must say why the band grows at 1.7x the category.

---

## 7. What this does not answer

- **No demographic split of premium-band buyers.** Income, age and Tier 2/3 data
  is platform-wide or category-wide. No fetchable source breaks out who transacts
  at Rs1,500-3,000. Left open rather than modelled.
- **K-beauty India sizing is *more* settled than expected — one source is the
  outlier.** The repo already held four estimates that cluster on level
  (~USD330-400m) and growth (19-26%): TheBK/Beauty Kyungjae USD400m 2024 → USD1.6bn
  2030 at 25.9% (MEDIUM), Economic Times Retail 25.9% (MEDIUM), EMR INR3,139cr
  2025 at 26.3% (LOW), The Report Cubes USD335m 2026 at 19.17% (LOW). Phase 3
  added Future Market Insights' 7.4% and it is a discard, not a data point — its
  own method is a global Sephora shelf-space model apportioned to a country.
  **Working range: 19-26% growth on a ~USD330-400m base, i.e. 1.4-1.7% of India's
  USD24bn BPC market.** Small, fast, and not the same thing as the Rs1,500-3,000
  band, which contains far more non-Korean product than Korean.
- **Two Trends baskets never landed** (`premium_intent`, and the 12-month cut of
  `origin_terms_fine`) — Google rate-limited them across four attempts. Retry:
  `python -m lib.fetchers.premium_skin_demand_trends premium_intent origin_terms_fine`
- **D'you, Put Simply and Quench were never in the Phase 1 sweep** because they
  were never queried, and D'you sells mainly from its own site. Add them to the
  brand list in `lib/fetchers/premium_skin_prices.py` before Phase 4 prices
  anything, and check whether D'you lists on Nykaa/Amazon at all.
- **Quench is unresearched.** Named as formulating in Korea; no prices, no
  founder, no positioning on file.
- **Review language cannot measure motivation.** §0 states the bound. If the
  owner wants a causal read on whether "Korean" sells, that needs a conjoint or
  an A/B on claim language — a primary-research spend, not a desk task.
- **No offline anything.** Still.

---

## 8. Where the data lives

| Output | Path |
|---|---|
| Demand-language analysis (all cuts, origin map, encroachment) | `data/manual/analysis/premium_skin_demand.json` |
| Qualitative findings, every URL fetched | `config/premium_skin_demand_findings.yaml` |
| Review-language DataPoints (18 rows, `driver_share`) | `data/sources.csv`, notes `[PREMIUM-SKIN]` |
| Sourced demand DataPoints + affordability ESTIMATEs (14 claims) | `data/manual/research_drops/premium_skin_demand.json` → `data/sources.csv` |
| Comparative search-demand raw | `data/raw/premium_skin_demand_trends_*.json` (4 files, partial by design) |
| Re-runnable: review-language mining | `lib/transforms/premium_skin_demand.py` |
| Re-runnable: comparative Trends baskets | `lib/fetchers/premium_skin_demand_trends.py` |
| Tests (origin keying, polarity, frames, encroachment) | `tests/test_premium_skin_demand.py` — 67 tests |

Schema additions this phase: `driver_share` (share of a review population citing
a purchase driver) and `spend_ratio` (one purchase as % of annual per-consumer
spend, always ESTIMATE), in `lib/transforms/schema.py`.

---

## 9. Carry into Phase 4

1. **Positioning is settled: lead with the concern and the mechanism, not the
   passport.** Pigmentation concern + named actives + a reason to repurchase.
   "Formulated in Korea" is a trust marker to place third, exactly where Put
   Simply places it — not a headline. Korea stays a manufacturing-quality
   decision, which is what the brief said either answer would imply.
2. **Cost the acquisition problem, not just the landed cost.** Demand enters via
   acne (3x pigmentation in search), the concern-and-proof vocabulary is already
   owned by RAS Luxury Oils and Suganda at Rs1,599-1,990, and hype-led
   acquisition is 4.7x over-represented among 1-star reviews. Phase 4's unit
   economics need a CAC line and a review-quality risk, not only COGS.
3. **Model single-SKU trial, then repurchase.** Rs1,900 is 14.1% of the top
   cohort's annual BPC budget; a four-SKU routine is 56.4%. Launch the range for
   MOQ economics, but forecast revenue as sequential single-SKU adoption with
   repurchase as the growth engine.
4. **Price above Rs2,500 only with clinical proof.** Derm-authority language is
   1.1% overall but 4.3% in the Rs2,500-3,000 third, where price resistance also
   more than doubles. Above Rs2,500 the buyer demands a reason; ISDIN's reviews
   (20% derm authority) show what that sounds like.
5. **Treat the Korean-ODM lane as contested, and go study the incumbents.**
   D'you holds Rs2,000-3,500 at zero discount from its own site; Put Simply sits
   below the band and discounts 25-47%. Two opposite answers from the same
   manufacturing base. Phase 4 should reverse-engineer both P&Ls before choosing
   lane (c), and add "an Indian brand already did this, better funded" to the
   risk register.
6. **Make offline primary.** §6.5. Premium concentrates offline; two-thirds of
   Nykaa store GMV is premium; the band's discount problem is an online problem.
7. **Re-sweep prices with the corrected brand list** (add D'you, Put Simply,
   Quench, plus the twelve Indian in-band brands from §5) and re-classify Limese
   as a conduit before any Phase 4 pricing.
