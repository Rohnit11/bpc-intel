# Premium Skincare — Research Brief

> **Scope:** India skincare, MRP band **Rs1,500-3,000**, Korea-origin products,
> fit for Indian skin tone. Written 2026-08-09 as the standing brief for this
> research thread. A new chat should read THIS FILE first and nothing else.
>
> **Namespace:** everything from this thread is tagged `[PREMIUM-SKIN]` so it
> stays separable from the corridor work. See "Where things go" below.

## 0. Decision context (set by the owner, 2026-08-09)

This is **not** a neutral market study. The owner intends to **build a brand in
this band**. Research must therefore be operator-grade: real costs, real
margins, real competitors, real consumer complaints — not a tier overview.

**Working concept:** formulate the product **in Korea**, tuned to **Indian skin
tone**, sold under **our own brand**. That is the Korean-ODM + India-brand-
ownership lane. All four entry lanes still get compared evenly in Phase 4, but
this is the one to pressure-test hardest — including the case against it.

**Product scope:** a **full routine / range**, not a single SKU — but with two
hero products carrying the thesis:

- **Pigmentation / brightening serum** — India's dominant derm concern, and the
  sharpest test of whether Korean actives work on melanin-rich skin. Also the
  most crowded lane domestically (Minimalist, Deconstruct, The Ordinary).
- **Sunscreen** — already flagged as corridor whitespace in the repo, and white
  cast on deeper skin is K-beauty's single most-complained-about failure. The
  cleanest expression of the skin-tone argument.

The formulation base is Korean skincare, adapted for the Indian market. Research
across all skincare formats in the band, but weight depth toward these two.

Three consequences that bind every phase:

1. **Offline is deferred to Phase 4** (owner's call, 2026-08-09). Phases 1-3 run
   online-only — Nykaa, Amazon, Tira online, Flipkart, Blinkit/Zepto. The repo
   has **no offline data at all** and most of it is not web-accessible, so it
   waits until channel strategy is live at Phase 4. Consequence to state out
   loud in Phase 1: the online-vs-offline pricing question stays open, and
   online prices are the discount-heaviest in the market — so any "the band
   collapses under discounting" finding is an online finding, not a verdict on
   the band as a whole.
2. **"Real problems" is a first-class output.** Not just whether products fit
   Indian skin, but what consumers actually complain about, in their words, at
   volume. That is the product brief writing itself.
3. **Range economics, not SKU economics.** Phase 4 costs a launch set, so ODM
   MOQs apply per formulation — a 4-SKU range at 1,000-unit MOQ each is a very
   different cheque from one hero SKU. Model it that way from the start.

---

## 1. The question, stated precisely

The India BPC deck (July 2026) flags Skincare **Premium (Rs1,500-3,000)** as the
most underserved tier: ~10% share, ~22% CAGR (fastest in skincare), competitive
intensity "Low", representative brands listed only as "Emerging". Separately it
notes homegrown brands hold ~10% of luxury/prestige skincare (90% foreign-owned).

The hypothesis under test: **Korean skincare formulated for Indian skin tone
fills this band.**

That is a hypothesis, not a finding. The deck's whitespace claim is
tier-generic, not Korea-specific, and says nothing about skin tone. The job is
to prove or kill it, not to confirm it.

### 1a. The reframe (from the 2026-08-09 repo audit — read this before researching)

The band is **not empty**. Korean SKUs already list inside it:

| SKU | MRP | Street price | Source |
|---|---|---|---|
| Anua Heartleaf 77% Toner 250ml | Rs2,050 Nykaa / Rs2,999 Amazon | Rs1,743 | IN_skincare.json |
| Innisfree Green Tea Seed Serum | Rs2,200 | Rs1,650 | IN_skincare.json |
| Etude SoonJung Hydro Barrier Cream 75ml | Rs1,600 | Rs1,200 Blinkit | IN_skincare.json |
| Beauty of Joseon Ginseng Essence 150ml | Rs1,500 | Rs1,500 Blinkit | IN_skincare.json |
| Beauty of Joseon Relief Sunscreen SPF50+ | Rs1,570 | Rs1,256 | price_ladder.json |
| COSRX Snail 96 Essence 100ml | Rs1,490 | Rs969 | IN_skincare.json |

Every one of them **lists in-band and transacts below it.** `price_ladder.json`
already records this: brands are "papering the masstige gap with discounts on
premium-listed SKUs rather than pricing a true masstige tier."

**So the real question is not "is the band empty" but:**

> **Q1. Is Rs1,500-3,000 a real transaction band in India skincare, or an MRP
> fiction that discounting collapses? If it collapses, what would let an
> entrant hold price there?**

Two supporting questions:

> **Q2. Do Korean formulations actually suit Indian skin tone** — shade range,
> white cast, actives aimed at pigmentation/melasma (the dominant Indian derm
> concern) vs Korean-market brightening/barrier priorities? *(Repo has ZERO
> data here. Genuinely greenfield.)*

> **Q3. Is "Korean" load-bearing for the Indian premium buyer, or incidental?**
> If Indian D2C (Pilgrim, Limese, Foxtale/Hula Hoop, Minimalist) is already
> pricing into the band, the gap may close without Korean brands at all.

### 1b. Known contradictions to resolve (do not paper over these)

1. **Competitive intensity.** Deck says "Low" for this tier.
   `data/manual/analysis/porter_skincare.json` (IN) rates skincare rivalry
   **HIGH** and buyer power **HIGH**. Both cannot be right. Resolve at band
   level — it is possible the tier is thin while the category is brutal.
2. **Deck source quality.** The deck's tier table triangulates IMARC, Grand
   View, Mordor — all **LOW confidence** under CLAUDE.md's rubric.
   **Owner's decision (2026-08-09): accept them tagged LOW with the aggregator
   caveat visible, do not spend tokens re-fetching paywalled reports.**
   Consistent with how the repo already holds other aggregator figures. But
   never let a LOW deck figure carry a conclusion on its own — if the 22% CAGR
   or ~10% share becomes load-bearing for the entry decision, flag that it is
   resting on aggregator triangulation and say so out loud.
3. **Ownership logic.** The deck's "90% foreign-owned" is framed as the
   whitespace. Korean brands are foreign-owned too — a Korean entrant widens
   that stat rather than fixing it. Only an India-manufactured Korean-formulation
   play changes it. Keep the two entry modes distinct throughout.
4. **Tier vocabulary.** `config/taxonomy.yaml` has 3 tiers (premium/masstige/
   mass) with **no MRP bounds**; the deck has 5 with bounds. The repo's
   "premium" would silently swallow the deck's Rs3,000+ Luxury tier. **Always
   key to the literal Rs1,500-3,000 MRP band, never the word "premium" alone.**
5. **"Gap" is overloaded.** `/gaps` in this repo means *missing data points*.
   This thread's "gap" is *market whitespace*. Never mix the two registers.

---

## 2. What the repo already has (do not re-derive)

Audited 2026-08-09. A new chat should trust this list and not re-scan.

**Has, and is directly reusable:**
- ~20 India skincare price DataPoints incl. the in-band SKUs above —
  `data/processed/IN_skincare.json`
- Price ladder with a `premium` rung already defined at Rs2,050-2,999, plus the
  discount-papering analysis — `data/manual/analysis/price_ladder.json`
- Porter five-forces for IN + KR skincare — `data/manual/analysis/porter_skincare.json`
- Corridor registry: conduits (Nykaa, Tira, Flipkart, Amazon, q-commerce), brands
  carried, CDSCO import path, Blinkit assortment snapshot — `config/corridor.yaml`
- 18 player profiles incl. AmorePacific, APR/Medicube, Anua, Beauty of Joseon,
  Nykaa, Minimalist — `data/manual/analysis/profiles/`
- Qualitative findings: Korea ODM economics, Olive Young, channels
  (`config/korea_findings.yaml`); India supply chain, D2C funding, q-commerce
  shares (`config/india_findings.yaml`); corridor (`config/corridor_findings.yaml`)
- Trade margin: Nykaa commission 22-26% + 18% GST; MRP embeds 25-45% trade margin
- India skincare size US$9.06bn (2025, IMARC, LOW); imports US$844m HS3304, of
  which Korea US$140m (Comtrade, HIGH)

**Does NOT have — this is the research frontier:**
- Any skin-tone, shade-range, undertone, white-cast, or Fitzpatrick data. None.
- **Any offline/physical-retail data whatsoever.** Every India price and
  assortment point on file is online (Nykaa, Amazon, Blinkit, Tira online).
  Nykaa Luxe, Tira stores, Sephora India, Shoppers Stop, chemist/derm channel —
  all unresearched.
- Any tier-level (MRP-band) market size, share, or growth for India skincare
- Transaction-price (vs MRP) series — everything on file is a single-date snapshot
- Ingredient/actives mapping: Korean formulations vs Indian dermatological concerns
- Consumer-side evidence: reviews, complaints, repeat purchase in this band
- Non-Korean foreign competitors in this band (Cetaphil, La Roche-Posay, The
  Ordinary, Paula's Choice et al.) — not in `companies.yaml`, not profiled
- Landed-cost economics: Korean ODM per-unit cost, MOQs at our volumes, freight,
  duty, CDSCO registration cost and lead time

---

## 3. Phases

Run one phase per chat session. Each phase ends by writing to files, so the next
session starts from disk, not from conversation history. **This is the token
discipline — do not carry findings between sessions in chat.**

### Phase 1 — Supply & competitive set: who is in the band, at what price?
**Answers Q1 + the "who's already there" question.** Highest leverage, run first.

> **DONE 2026-08-09. Output: `docs/premium-skincare-phase1.md`.** Read that, not
> this section, for what was found. Headline: the band **holds** online — 79.6%
> (Nykaa) / 87.3% (Tira) of in-band-by-MRP SKUs still transact in-band, median
> discount 10%. Kill condition not met. The real risk is the **floor**:
> retention is 50% for SKUs listing at Rs1,500-1,750 but 97% at Rs2,000-2,500.
> Korean sunscreen — a hero product — sits against that floor and retains only
> 41.7%. Phase 2 should assume a Rs1,900+ list price, not Rs1,500-1,700.
> Two corrections to this brief's own assumptions are recorded there: **not one
> named Indian D2C brand sells a single SKU inside the band** — they reach it
> only via multi-product combos, and only Forest Essentials and Kama Ayurveda
> hold it with real SKUs, at 100% of list — and the competitive set is 64
> brands, not the 33 named below. Coverage gaps: Some By Mi and Limese.

Three brand groups, all of them, not just Korean:
- **Korean** — start from `config/corridor.yaml` (Anua, Beauty of Joseon, COSRX,
  Innisfree, Laneige, Etude, Medicube, TirTir, Mixsoon, Hince, Dr. Melaxin,
  Isntree, Some By Mi, Dr.Jart+, The Face Shop)
- **Homegrown** — Minimalist, Dot & Key, Foxtale, Pilgrim, Limese, Plum,
  Forest Essentials, Kama Ayurveda, Deconstruct, Earth Rhythm
- **Other foreign** — Cetaphil, La Roche-Posay, The Ordinary, Paula's Choice,
  Clinique, Kiehl's, Bioderma, Sebamed. These compete for the same wallet and
  the deck ignores them.

For each: capture current **MRP and transaction price** for any SKU listing
Rs1,200+ (cast wide, filter after). Compute discount depth per SKU, then the
headline number: **what share of in-band-by-MRP SKUs are still in-band by
street price?**

Weight SKU-level depth toward **pigmentation/brightening serums and
sunscreens** (the two hero products), but capture the full band so the
competitive picture is complete.

**Offline is out of scope for this phase** — deferred to Phase 4. Say so
explicitly in the output: these are online prices, which are the
discount-heaviest in the market, so the verdict below is an online verdict.

- Deliverable: DataPoints into `data/sources.csv` (notes tagged
  `[PREMIUM-SKIN]`), plus a written verdict on whether the band survives
  discounting **online**.
- **Kill condition:** if essentially nothing transacts in-band online, say so
  plainly — but flag it as channel-specific until Phase 4 checks offline, not
  as a verdict on the band itself.

### Phase 2 — Fit & real problems
**Answers Q2.** The greenfield half. Most novel, most defensible output.
Owner's call: cover **both** efficacy and shade, **weighted to efficacy**.

> **DONE 2026-08-10. Output: `docs/premium-skincare-phase2.md`.** Read that, not
> this section, for what was found. Headline: **this brief's white-cast premise
> below is wrong.** Across 3,287 Nykaa reviews of in-band SKUs, buyers mention
> white cast on Korean sunscreen 6x more often to say it is ABSENT (68 mentions)
> than to complain of it (11). Korean sunscreen has a reputation for having
> solved white cast, not a white-cast problem — Innisfree excepted, at 31.8% of
> its negative reviews. The real complaints are **irritation (19.2% of Korean
> sunscreen negatives) and heaviness in humidity (15.4%)**, so the "climate /
> texture mismatch" this brief called under-researched is the live failure mode.
> Pigmentation serums fail differently: breakouts (18.6%) and no visible effect
> (16.9%) top their negatives. **Shade is a non-question** — tone mismatch fired
> once in 3,287 reviews, because only 10 of 327 in-band SKUs are tinted at all.
> The skin-tone argument that survives is **visible-light photoprotection**
> (tinted iron-oxide formulas: 78% vs 62% MASI reduction), which consumers
> cannot perceive and show zero pull for. New skin-tone data: 1,275 reviews
> carry a self-declared tone and only **6.7% are Dark/Deep** — the band's
> visible buyer base skews fair. Regulatory: India restricts neither the UV
> filters nor the brightening actives; it restricts the **claim language**.

- **Actives mapping (primary).** What Korean premium formulations actually
  target (barrier repair, brightening, hydration) vs India's dominant concerns
  (hyperpigmentation, melasma, tanning, oily/humid-climate acne, sensitivity to
  actives on darker skin). Source from dermatology literature and Indian derm
  associations, not brand marketing.
- **Shade & appearance (secondary).** White cast on SPF, shade counts and
  undertone range on tinted SKUs, cushions, BB. Korean shade ladders vs Indian
  skin-tone distribution. Narrower than efficacy — pure skincare has no shade —
  but far more visible and easier to evidence.
- **Real problems (a deliverable in its own right).** Systematic review mining
  across Nykaa/Amazon/Tira listings for the Phase 1 SKUs: "too light", "white
  cast", "ashy", "didn't suit my tone", "broke me out", "too heavy for Indian
  summer", "no shade for me", "pilling under sunscreen". **Count and quantify —
  frequency by complaint type, by brand, by product format.** Do not cherry-pick
  quotes. This output is the product brief writing itself, so treat it as
  primary evidence, not colour.
- Climate angle: Korean formulations are built for a temperate, low-humidity
  winter market. India is hot and humid most of the year. Texture/occlusivity
  mismatch is a real and under-researched failure mode.
- Regulatory: whether CDSCO/BIS IS 4707 constrains actives common in Korean
  formulations (certain brightening agents especially).
- Deliverable: `config/premium_skin_fit_findings.yaml`, same schema as
  `korea_findings.yaml` (text / source / url, one entry per finding, every URL
  actually fetched). Complaint counts are quantitative — they go to
  `sources.csv` with methodology stated (sample size, date, listing URLs).

### Phase 3 — Demand: is "Korean" load-bearing?
**Answers Q3.**

> **DONE 2026-08-10. Output: `docs/premium-skincare-phase3.md`.** Read that, not
> this section, for what was found. Headline: **"Korean" is not load-bearing — it
> is barely spoken.** Korean provenance is invoked in 2.2% of 2,676 positive-frame
> reviews of in-band SKUs, behind repurchase intent (10.8%), pigmentation concern
> (10.8%), actives (9.9%), results (7.7%) and price (6.5%). On Korean-origin SKUs
> it reaches 2.6% against 11.3% naming an active (4.3x); on Indian-origin SKUs it
> is **0 of 333** — Korea is not a benchmark buyers reach for. Search agrees:
> `korean skincare` indexes 0.6 against `niacinamide` 12.1 and `dermatologist`
> 15.6 in India, and `glass skin` outsearches every Korea term. So Korea becomes a
> **manufacturing-quality decision**, and the brand leads on concern + mechanism +
> repurchase — the outcome this brief said would follow either answer.
> Two findings outrank that: **(1) the band is a budget event** — Nykaa's Beauty
> AOV is Rs2,173 (HIGH), and India's top income cohort spends USD140/yr on ALL
> BPC across 18 occasions (~Rs748 each), so a Rs1,900 SKU is 2.5x an occasion and
> 14.1% of that cohort's annual budget, and a 4-SKU routine is 56.4% of it — the
> range-economics consequence in §0.3 holds for MOQs and does NOT transfer to the
> consumer, so model sequential single-SKU trial. **(2) The Korean-ODM +
> Indian-brand lane already has incumbents**: D'you (2020, Rs1,680-3,500, zero
> discount) and Put Simply (2022, Rs825-1,699, "Made in Korea" third in its trust
> stack), plus Quench. Also: twelve Indian-origin brands DO hold in-band single
> SKUs (RAS Luxury Oils, Suganda, Yuderma, Ethiglo, WildGlow, BiE, The Derma Co,
> TBC, Miduty, Fixderma, Aminu, Forest Essentials) and hold price better than the
> Korean cluster (88% vs 79% band retention) — Phase 1's finding was true of the
> named D2C brands only. **Correction: Limese is a K-beauty importer/retailer, not
> a homegrown brand** — move it to `config/corridor.yaml` conduits.

- Who buys India premium skincare at Rs1,500-3,000: income cohort, metro vs
  Tier 2/3, age, channel.
- Is the purchase driver "Korean" specifically, or efficacy/ingredient/derm-cred
  with Korea incidental? Search-trend and review-language evidence.
  **This is a positioning input, not a go/no-go** (owner's call, 2026-08-09).
  If "Korean" is load-bearing, it anchors the brand story. If it is incidental,
  Korea becomes a manufacturing-quality decision rather than a positioning one,
  and the brand leads on efficacy-for-Indian-skin instead. Either answer is
  useful; neither kills the concept. Run it before Phase 4 so the entry
  economics are costed against the right positioning.
- Are Indian D2C brands already pricing into the band? If Minimalist/Foxtale/
  Pilgrim are at Rs1,500+, the band is being closed domestically while we plan.
- Deliverable: findings YAML entries + any sizing DataPoints.

### Phase 4 — Entry: pros and cons, operator-grade
Runs only after 1-3. Owner is building here, so this phase carries real numbers,
not a framework tour.

> **DONE 2026-08-10. Output: `docs/premium-skincare-phase4.md`.** Read that, not
> this section, for what was found. Headline: **the band is real and the product
> is cheap enough to make — the plan fails on order size, then on cost of
> demand.** At the 4-SKU-at-1,000-unit-MOQ shape §0.3 assumes, landed COGS is
> **80.4% of a Rs2,400 MRP for the serum and 107.3% for the sunscreen**: the unit
> loses money at full price, zero discount, no marketing. At 5,000 units/SKU the
> same SKUs land at 38.4% / 37.2% and break even before marketing at a 28-30%
> discount. **Order size swings contribution margin 57.3pp — more than every
> unresolved research question combined, and it is a decision, not an unknown.**
> Then acquisition kills it: of 36 modelled price × volume × duty cells, exactly
> **one** clears Honasa Consumer's FY25 advertising intensity (Rs743.65cr on
> Rs2,067cr revenue = **36%**). Lane ratings: **(a) import a Korean brand — NOT
> RECOMMENDED** (widens the 90%-foreign stat, worst price retention of any origin
> group); **(b) India manufacture — STRUCTURALLY FAVOURED**, because it deletes
> duty (11.0pp), freight (8.5pp), CDSCO import registration and the ODM's
> site-registration lock-in, blocked only on whether an Indian maker can do the
> sunscreen; **(c) Korean ODM + own brand — VIABLE ONLY ABOVE ~5,000 UNITS/SKU
> AND AT LOW CAC**; **(d) JV/licence — INSUFFICIENT, unrated.** Porter re-rated at
> band level: 1b.1 **resolved against the deck** (rivalry HIGH), supplier power
> upgraded LOW→**MEDIUM** (one-off costs sink with one manufacturer; sunscreen
> non-recurring cost is 2.7x its goods cost on SPF testing alone), and substitutes
> — which the category Porter could not rate — is now **HIGH** (Indian D2C a tier
> below, plus the same Korean SKU leaking 20% cheaper on Amazon).
> **Price re-sweep done** (frame 2, less-discounted): band holds at 83.5% Nykaa,
> the **Rs1,900 floor is confirmed** (55.1% retention at Rs1,500-1,750 vs 96.8% at
> Rs2,000-2,500), homegrown in-band SKUs go **13 → 74** once the right brands are
> swept, and **D'you lists on both Nykaa and Tira at Rs2,100-3,500 with zero
> discount on all 14 observations** — closing Phase 3's open question.
> **Offline remains only partially researched and is still the largest open risk**
> — the pass commissioned for it did not complete, so §6 names what is missing
> rather than modelling it. Top open item: **can an Indian manufacturer make a
> competitive sunscreen?** That one question decides between lanes (b) and (c).

- Porter at **band level** — resolve the deck-vs-`porter_skincare.json`
  contradiction (item 1b.1).
- **Primary lane, pressure-tested hardest: (c) Korean ODM manufacture + own
  India brand.** Cosmax / Kolmar Korea / Cosmecca — the repo already holds their
  economics (sub-6-month concept-to-shelf, MOQs from ~1,000 units, per
  `korea_findings.yaml`). Needs: actual MOQ and per-unit cost at our volumes,
  whether an ODM will formulate *specifically* for Indian skin tone or only
  adapt an existing base, IP/exclusivity terms, lead times, and who else they
  already make for in India. **Build the case against it too** — an honest
  entry analysis that only supports the owner's prior is worthless.
- Compared evenly against: (a) import a Korean brand via a conduit;
  (b) India-manufactured Korean-formulation own-brand; (d) JV/licence with a
  Korean brand.
- **Unit economics, real:** Korean ODM cost -> freight -> customs duty ->
  CDSCO registration cost and lead time -> India warehousing -> platform
  commission (22-26% + 18% GST, on file) -> 25-45% MRP trade margin. What gross
  margin actually survives at Rs1,500-3,000, and **what discount depth breaks
  it** — Phase 1 tells us competitors discount 20-35%, so model whether we can
  match that and live.
- **Offline lands here** (deferred from Phase 1). Two parts: (i) who from the
  Phase 1 competitive set actually has physical presence, and where — Nykaa
  Luxe, Tira stores, Sephora India, Shoppers Stop, Health & Glow, chemist/derm
  channel; (ii) offline economics — listing fees, retailer margin, minimum
  volumes. Offline typically holds closer to MRP than online, so this is where
  Phase 1's discount verdict either gets confirmed or overturned. Much of this
  is not web-accessible; mark what is desk-sourced vs unverified rather than
  inferring.
- Risk register: discount war, CDSCO lead time, ODM formulating the same base
  for a competitor, Indian D2C closing the band first, "Korean" losing salience,
  climate/texture mismatch surfacing post-launch.
- Deliverable: `data/manual/analysis/premium_skin_entry.json`, following the
  rating + rationale + evidence + `evidence_strength` shape used by
  `porter_skincare.json`. INSUFFICIENT renders as "research needed", never a
  hedged guess.

### Phase 5 — Dashboard section
Only after there is real data to show.

- New route `web/app/premium-skincare/`, new nav entry in
  `web/components/nav-bar.tsx` (currently 1 line per section — additive, low risk).
- Section label: **Premium Skincare**.
- Export path via `lib/web_export.py` so the bundle picks up the new findings
  file and analysis JSON, same as existing sections.
- Deploys to both Vercel projects from main.

---

## 4. Where things go

| Output | Destination | Tag |
|---|---|---|
| Quantitative claims | `data/sources.csv` (mandatory) | `[PREMIUM-SKIN]` in notes |
| Qualitative findings (Phase 2, fit) | `config/premium_skin_fit_findings.yaml` | — |
| Qualitative findings (Phase 3, demand) | `config/premium_skin_demand_findings.yaml` | — |
| Phase 1 prices + verdict | `data/manual/analysis/premium_skin_band.json`, `docs/premium-skincare-phase1.md` | `[PREMIUM-SKIN]` |
| Phase 2 complaints + verdict | `data/manual/analysis/premium_skin_fit.json`, `docs/premium-skincare-phase2.md` | `[PREMIUM-SKIN]` |
| Phase 3 demand + verdict | `data/manual/analysis/premium_skin_demand.json`, `docs/premium-skincare-phase3.md` | `[PREMIUM-SKIN]` |
| Phase 3 sourced demand claims | `data/manual/research_drops/premium_skin_demand.json` | `[PREMIUM-SKIN]` |
| Entry analysis | `data/manual/analysis/premium_skin_entry.json` | — |
| Phase 4 unit economics (model output) | `data/manual/analysis/premium_skin_unit_economics.json` | `[PREMIUM-SKIN]` |
| Phase 4 price frame 2 | `data/manual/analysis/premium_skin_band_frame2.json`, `docs/premium-skincare-phase4.md` | `[PREMIUM-SKIN]` |
| Phase 4 sourced entry claims | `data/manual/research_drops/premium_skin_entry.json` | `[PREMIUM-SKIN]` |
| Dashboard | `web/app/premium-skincare/` | — |

Phase 1 also added two re-runnable scripts: `lib/fetchers/premium_skin_prices.py`
(Nykaa/Tira/Amazon price sweep, ~25 min) and `lib/transforms/premium_skin_band.py`
(band arithmetic). Re-run both off-sale before Phase 4 prices anything.

Phase 2 added two more: `lib/fetchers/premium_skin_reviews.py` (Nykaa review
API mining, ~30 min, carries self-declared skin tone) and
`lib/transforms/premium_skin_fit.py` (complaint classification with negation
handling — "no white cast" is praise, and treating it as a complaint inverts the
Phase 2 headline).

Phase 3 added two more: `lib/transforms/premium_skin_demand.py` (purchase-driver
mining over the same review corpus, re-keyed to manufacturer ORIGIN because
Phase 1's `brand_group` mixes Korean and European brands in `other_observed`;
also carries the in-band-by-origin encroachment count off the Phase 1 price
sweep) and `lib/fetchers/premium_skin_demand_trends.py` (comparative Google
Trends baskets — one payload per basket so the indices are actually comparable,
unlike `trends_google.py` which fetches each keyword separately; Google
rate-limits hard, so it takes a basket list as CLI args to finish an interrupted
sweep). Schema gained `driver_share` and `spend_ratio` metrics.

Phase 4 added one more: `lib/transforms/premium_skin_entry.py` (the unit-economics
model — landed-cost waterfall, closed-form break-even discount, max sustainable
CAC, launch cash at risk, and a sensitivity ranking that sweeps every input that
could not be sourced instead of plugging it). Inputs that stayed unresolved are
listed in the artifact's `unresolved_inputs` and are swept, not guessed. Three
pipeline corrections landed with it, all recorded in phase4 §3.2: Limese dropped
as a brand (it is a conduit), a too-short `Quench` alias removed after it matched
competitors' product, and an `ingestible` scope exclusion added so nutraceutical
SKUs stop counting as face skincare.

**Caution when re-running:** `lib/transforms/premium_skin_band.run()` writes to
`premium_skin_band.json` as a side effect regardless of which raw file it is
given, so a frame-2 run clobbers the Phase 1 artifact. Restore it from git after
(`git checkout -- data/manual/analysis/premium_skin_band.json`) or write the new
frame to its own path first, as Phase 4 did.

Nothing here overwrites corridor or skincare files. The `[PREMIUM-SKIN]` tag
mirrors the existing `[CORRIDOR]` convention so this thread stays filterable and
removable.

---

## 5. Rules that still bind

All of CLAUDE.md, without exception. The ones this thread will hit hardest:

- **Rule 1/6:** no number from model knowledge; no URL cited that was not
  actually fetched. A search snippet is not a source — fetch the page.
- **Rule 3:** `value_basis` mandatory. India shelf prices are `MRP`. If a
  transaction price is recorded, it is still MRP-basis retail but the notes must
  distinguish list from street.
- **Rule 4:** currency + USD equivalent, FX pinned in `config/exchange_rates.yaml`.
- **Rule 8:** state organised vs unorganised coverage on every India number.
- **Rule 9:** FY24 not "2024" for Indian company data; CY for Korea.
- **Rule 10:** MRP embeds 25-45% trade margin — normalise via
  `lib/transforms/mrp_normalise.py` before any reconciliation.
- A standing gap is information. A fabricated number is contamination. Leave the
  cell open and say why.

---

## 6. Token discipline

- **One phase per session.** Do not run Phase 1 and 2 in one chat.
- **Start every session by reading this file only.** Not the deck, not the whole
  repo. Section 2 above already records what exists — trust it.
- **End every session by writing to files.** Findings live on disk, never in
  chat history.
- Use subagents for parallel brand/SKU sweeps (3+ entities = parallel per
  CLAUDE.md working style) — they keep bulk retrieval out of the main context.
- Do not re-read `data/processed/IN_skincare.json` in full unless a phase needs
  it; the in-band SKUs are already transcribed in section 1a.
