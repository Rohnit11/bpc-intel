# Premium Skincare — Phase 2 output: fit & real problems

> **Answers Q2** ("do Korean formulations actually suit Indian skin tone?") from
> `docs/premium-skincare-brief.md`, and delivers the "real problems" output the
> brief specifies as a deliverable in its own right. Run 2026-08-10.
> Namespace `[PREMIUM-SKIN]`.
>
> **Read this before Phase 3.** Everything below is on disk; nothing is carried
> in chat.

## 0. Verdict

**The brief's central premise about white cast is wrong, and the failure mode it
called "under-researched" is the real one.**

The brief states that "white cast on deeper skin is K-beauty's single
most-complained-about failure" and treats it as the cleanest expression of the
skin-tone argument. In 3,287 Nykaa reviews of in-band SKUs, it is not:

| Korean sunscreen, all sampled reviews (n=365) | Count | Rate |
|---|---|---|
| Says the product **leaves** a white cast | 11 | 3.0% |
| Says the product leaves **no** white cast | 68 | 18.6% |

**Indian buyers mention white cast on Korean sunscreen six times more often to
say it is absent than to complain about it.** Korean sunscreen does not have a
white-cast problem in this market — it has a *reputation* for having solved one.
That reputation is a real asset, and an entrant who leads with "finally, no
white cast" is selling the incumbent's existing proof point.

What Korean sunscreen actually gets complained about, among buyers who leave 1-
or 2-star reviews:

| Complaint | Share of Korean sunscreen negative reviews (n=78) |
|---|---|
| **Irritation** (stinging, burning, itching, redness, eye sting) | **19.2%** |
| **Heavy / greasy / doesn't survive humidity** | **15.4%** |
| Value for money | 10.3% |
| White cast | 7.7% |
| Breakouts | 7.7% |
| No visible effect on pigmentation | 5.1% |

The brief flagged climate/texture mismatch as "a real and under-researched
failure mode." It is real, it ranks second, and it is not confined to
sunscreen — heaviness in humidity is the single most-asserted complaint in the
whole negative corpus after irritation.

**Three consequences for the product:**

1. **Do not build the brand on white cast.** It is a solved problem in the
   consumer's mind and the market gives Korean formulations credit for solving
   it. Competing there is competing on the incumbent's strength.
2. **Texture-for-humidity and tolerability are the open lanes.** They are the
   top two complaints, they are formulation problems an ODM brief can actually
   specify, and no brand in the band owns them.
3. **The skin-tone argument survives, but through a different mechanism than the
   brief assumed** — visible-light photoprotection, not cosmetic invisibility.
   See §6. That mechanism argument is strong and evidenced; the consumer
   complaint data does *not* independently corroborate it, because consumers
   cannot perceive the thing it is about.

## 1. Scope and caveats (read before quoting any number here)

- **Nykaa only.** Tira exposes no comparable review endpoint and Amazon.in gates
  review pagination behind a login. Amazon's absence matters
  disproportionately: Phase 1 found it undercuts the authorised channel by ~20%
  and carries counterfeit-adjacent listings, so it is where authenticity
  complaints would live. **The authenticity theme here is understated by
  construction, not measured as low.**
- **These are statistics about reviews, not about users.** A complaint rate is
  the share of *reviews* raising a theme. Nothing here says what share of buyers
  experienced anything.
- **Two frames, never pooled.** The corpus is (a) every retrievable 1- and
  2-star review, n=651, and (b) the first three pages of Nykaa's default "most
  useful" ordering, n=2,676, which is overwhelmingly 5-star. Pooling them and
  dividing by 3,287 would produce a rate that is an artefact of the sampling
  design. Rates are computed within frame throughout.
- **Polarity-checked, not keyword-counted.** "No white cast" is praise. Every
  match is tested against a negation window before it counts, and the
  clause-boundary handling is the most-tested code in the module
  (`tests/test_premium_skin_fit.py`). Without it the §0 finding inverts.
- **Sample is the Phase 1 in-band SKU set**, restricted to the two hero formats
  plus Korean moisturisers and toners/essences: 109 SKUs targeted, 95 with any
  review, 14 with none. 100% of sampled reviews are Nykaa "Verified Buyer".
- **Point-in-time, with an interruption.** The sweep ran 2026-08-10, but the
  host slept mid-run and the wall-clock span is ~01:26 to 08:10. Reviews are a
  historical corpus rather than live state, so the gap does not corrupt the
  data — but this is not the single-instant snapshot the Phase 1 price sweep
  was, and it should not be described as one.
- **ORGANISED online retail only.** Offline stays deferred to Phase 4.

## 2. The complaint hierarchy, whole corpus

Within the 651 negative reviews across every covered format and brand group:

| Complaint | Asserted | Rate |
|---|---|---|
| Irritation | 113 | 17.4% |
| Value for money | 106 | 16.3% |
| Heavy / greasy / humidity | 90 | 13.8% |
| Breakouts | 89 | 13.7% |
| No effect on pigmentation | 53 | 8.1% |
| White cast | 38 | 5.8% |
| Fragrance | 14 | 2.2% |
| Pilling | 8 | 1.2% |
| **Tone mismatch / no shade** | **~0** | **~0%** |

**Tone mismatch is a non-question in this band.** It fired once in 3,287
reviews. That is consistent with Phase 1's structural finding: only 10 of 327
in-band SKUs carry any tint, shade, cushion or colour-correcting word in the
name. Pure skincare has no shade ladder, so "shade range" — the secondary half
of Q2 — turns out to have almost no surface area inside Rs1,500-3,000. The
brief anticipated this ("narrower than efficacy"); the data says it is narrower
still.

**The reassurance signal is the more useful half of the white-cast data.** In
the most-useful frame, white cast is negated 198 times against 51 assertions,
and heaviness is negated 208 times against 156 assertions. Buyers spend their
positive reviews pre-empting exactly two anxieties: *will it look grey on me*
and *will it feel heavy*. That is the category's purchase-anxiety structure, and
it is a packaging-and-claims input more than a formulation one.

### Negative-review share by brand group — a census, not a sample

Nykaa reports written-review counts per star level, so this is a count of the
population, not an estimate over it. 11,786 written reviews across the sampled
SKUs:

| Group | Written reviews | 1-2 star | Share |
|---|---|---|---|
| Korean | 8,424 | 511 | **6.1%** |
| Other observed | 2,649 | 121 | 4.6% |
| Homegrown | 407 | 43 | 10.6% |
| Other foreign (named) | 306 | 68 | **22.2%** |

**Korean products in this band are well-liked, and the non-Korean foreign brands
are not.** A 22.2% negative share for the named other-foreign set against 6.1%
for Korean is the widest gap in the analysis. Korean brands also carry 71% of
all written reviews on in-band SKUs — they own the review base as decisively as
Phase 1 showed they own the shelf.

This cuts against a naive "Korean products fail Indian skin" thesis and it
should be stated plainly: **the consumer evidence does not support the claim that
Korean formulations are a poor fit for Indian consumers.** It supports a
narrower claim — that they have two specific, addressable weaknesses.

## 3. Skin tone: what the data can and cannot say

**1,275 of 3,287 reviews (38.8%) carry a self-declared skin tone** from the
reviewer's Nykaa beauty profile. This is the first skin-tone data in the repo;
Section 2 of the brief recorded the field as entirely greenfield.

The composition is the finding:

| Tone group (Nykaa's own ladder) | Reviews | Share of tone-declaring |
|---|---|---|
| Fair (Fair, Light) | 825 | **64.7%** |
| Wheatish (Medium, Medium Dark) | 364 | 28.5% |
| Dusky (Dark, Deep) | 86 | **6.7%** |

**Fewer than 7% of tone-declaring reviewers of premium-band skincare on Nykaa
identify as Dark or Deep.** That is a striking skew against any plausible
distribution of Indian skin tone. Three readings are available and this data
cannot separate them: deeper-tone consumers may be under-represented among
buyers in this band; among reviewers; or among people who complete a Nykaa
beauty profile. All three are commercially significant and all three point the
same way — **the premium band's visible consumer base is disproportionately
fair-skinned.**

On whether complaints differ by tone, the honest answer is that **the cells are
too small to carry a conclusion**:

| Frame | Fair | Wheatish | Dusky |
|---|---|---|---|
| Negative reviews, n | 124 | 66 | **16** |
| — white cast asserted | 4.0% | 9.1% | 0.0% |
| Most-useful reviews, n | 705 | 302 | **72** |
| — white cast asserted | 2.3% | 2.3% | 4.2% |

The direction is faintly consistent with white cast mattering more as tone
deepens — wheatish buyers assert it at more than twice the fair rate among
negative reviews, and dusky buyers assert it most in the most-useful frame — but
n=16 dusky negative reviews cannot support a claim, and the wheatish and dusky
signals point in opposite directions across the two frames. **Recorded as
directional, not concluded.** Closing this properly needs either a much larger
corpus or primary research, and it is the strongest candidate for commissioned
work in Phase 4.

What the tone data *does* establish: heaviness in humidity is the top complaint
for wheatish (21.2%) and dusky (25.0%) negative reviewers alike, ahead of
anything tone-specific. The texture problem is not a fair-skin problem.

## 4. Hero product 1 — pigmentation / brightening serum

The lane Phase 1 found holds price best has the worst product story:

| Complaint | Share of negative reviews (n=59) |
|---|---|
| **Breakouts** | **18.6%** |
| **No visible effect on pigmentation** | **16.9%** |
| Heavy / greasy / humidity | 11.9% |
| Irritation | 11.9% |
| Value for money | 10.2% |
| White cast / tone mismatch | 0% / 0% |

Two things matter here.

**One in six unhappy buyers of a pigmentation serum says it did not work.** For
a product whose entire promise is a visible outcome on pigmentation, that is the
category's core claim failing in front of the customer. Pigmentation serums also
have the *lowest* negative-review share of any format (4.0% of written reviews),
so this is a small group failing loudly rather than a broad failure — but it is
failing on the one axis that matters.

**Breakouts are the top complaint, and that is worse than it looks.** India's
PIH burden is acne-driven: more than 70% of Indians with an acne history carry
post-inflammatory marks before 35 (Indian J Dermatol, in
`config/premium_skin_fit_findings.yaml`). A brightening serum that causes
breakouts manufactures the exact condition it is sold to treat. Anua's
pigmentation-adjacent SKUs show breakout in 44% of their negative reviews
(n=25 — small, flagged); COSRX shows breakout and irritation at 20.6% each
across the largest single-brand negative corpus in the sweep (n=170).

**Product consequence:** the hero serum's brief writes itself — non-comedogenic
proven on Indian skin, tolerability-first actives, and an efficacy claim the
brand can actually substantiate. That is a harder ODM brief than "put
niacinamide in it," and it is the defensible one.

## 5. Hero product 2 — sunscreen

| Complaint | Share of sunscreen negative reviews (n=267) |
|---|---|
| **Heavy / greasy / humidity** | **19.9%** |
| **Irritation** | **19.5%** |
| Value for money | 17.6% |
| White cast | 9.4% |
| Breakouts | ~8% |

Sunscreen is where white cast is most alive (9.4% of negatives, the highest of
any format) and still only fourth. Irritation at 19.5% is the more actionable
number: sunscreen sits on the whole face daily, and eye-sting and stinging on
application are the two phrasings that recur.

**Brand-level, one result stands out:**

| Brand | Negative reviews | Top complaint |
|---|---|---|
| Innisfree | 44 | **White cast, 31.8%** |
| COSRX | 170 | Breakouts / irritation, 20.6% each |
| Beauty of Joseon | 116 | Heavy/greasy, 14.7% |
| Bioderma | 63 | Heavy/greasy, 28.6% |
| The Face Shop | 53 | Irritation, 20.8% |
| Forest Essentials | 43 | Heavy/greasy, 30.2% |
| Laneige | 18 | Heavy/greasy, 22.2% |

**Innisfree is the exception that proves the rule** — a Korean brand with a
genuine, brand-specific white-cast problem at nearly 32% of its negative
reviews, roughly five times the corpus average. Phase 1 separately found
Innisfree sunscreens listing at Rs1,650 and falling out of the band on a routine
10% discount. One brand carries both the price-floor problem and the white-cast
problem; that is a competitor to take share from, not a category verdict.

**Bioderma is the informative counter-case.** It sells the tinted sunscreens
that §6 says skin of colour actually needs, and heaviness is its top complaint
at 28.6% — nearly double the Korean rate. The visible-light trade-off is
already visible in the review data: the formulation that protects against the
right wavelength is the one buyers call heavy.

## 6. The skin-tone argument that survives — and it is not the one in the brief

The consumer data says white cast is largely solved. The dermatology literature
says something the consumer cannot see, and it is the stronger argument:

- Visible light (400-700 nm), not only UV, drives melasma and PIH in skin of
  colour, and conventional broad-spectrum sunscreens do not block it.
- Blocking visible light requires an **opaque** film — iron oxides plus
  **pigmentary-grade (non-micronized)** titanium dioxide. The micronized
  inorganic filters used precisely *because* they are cosmetically invisible do
  not deliver it.
- Iron oxides are not classed as UV filters and appear under "inactive
  ingredients," so **a product can be SPF 50+ PA++++ and offer no visible-light
  protection at all.**
- The effect size is clinical, not cosmetic: in melasma patients on 4%
  hydroquinone, ordinary SPF-50 gave a 62% mean MASI reduction against **78%**
  for a tinted iron-oxide sunscreen.

Sources and quotes in `config/premium_skin_fit_findings.yaml` under
`photoprotection_and_skin_tone`.

**So the concept's real skin-tone claim is:** Korean sunscreen's signature
virtue — invisible, weightless, no cast — is structurally the *absence* of
protection against the wavelength that drives India's dominant dermatological
concern. Nobody in the band sells the alternative: 10 of 327 in-band SKUs carry
any tint word, 7 of them sunscreens, mostly Bioderma's. The one named Korean
entry is d'Alba's **tone-up** sunscreen — a product designed to deliberately
lighten the appearance of skin, which is the opposite of what a melanin-rich
consumer needs.

**Three warnings before this becomes the brand story.**

1. **Consumers do not perceive this.** Visible-light protection has no felt
   benefit and no visible result on a timescale a buyer can attribute. The
   complaint data shows zero demand pull for it. This is a claim that must be
   *taught*, which is expensive, and Phase 3 should test whether it lands at all.
2. **The trade-off is real and lands on the top complaint.** Tinted formulas are
   heavier — Bioderma's own review data proves it — and heaviness is the #1
   sunscreen complaint in this market. Solving the invisible problem worsens the
   felt one.
3. **Tinting reintroduces shade matching**, which the literature names as
   tinted sunscreen's main limitation, and which a single hero SKU cannot solve.
   That is a range-architecture and inventory decision, not a formulation tweak,
   and it argues further for the range-led launch the brief already specifies.

## 7. Regulatory: not an ingredient problem, a claims problem

Two plausible-sounding objections died on contact with the primary standards:

- **UV filters are not a barrier.** IS 4707 (Part 4):2022 was updated "in line
  with the latest EC 1223/2009" and lists 29 permitted filters, including
  bemotrizinol/Tinosorb S at 10%, bisoctrizole/Tinosorb M at 10%, Uvinul A Plus
  at 10%, ethylhexyl triazone at 5%, and TiO₂/ZnO at 25%. A Korean SPF formula
  can come to India on filter grounds as-is.
- **Brightening actives are not restricted.** IS 4707 (Part 2):2017 carries no
  entry for arbutin, kojic acid, tranexamic acid, glutathione, niacinamide or
  retinol. Hydroquinone appears only in hair-dye and professional artificial-nail
  contexts. *Bounded: the 2017 fourth revision plus its four amendments was what
  was readable; a Part 2:2025 revision is reported to exist and was not
  obtainable. Re-check before Phase 4 costs anything.*

**Where India does constrain the concept is language.** Korea's MFDS grants
"whitening" as an approvable product function — one of its defined functional
cosmetic categories. ASCI's guidelines bar advertising that communicates
discrimination by skin colour, shows darker skin as unattractive or unhappy, or
associates skin colour with social standing. **The same formulation cannot carry
the same story in both markets.** An efficacy-on-pigmentation claim transfers; a
whitening or fairness claim does not. For an own-brand play this is a positioning
constraint to design around from day one, not a compliance detail.

Import mechanics, from the Cosmetics Rules 2020 itself: the registration
certificate is valid **in perpetuity subject to a retention fee before five
years** (not the three-year expiry several consultancies state); no
animal-tested cosmetic may be imported; and any change to composition,
labelling, testing or specification must be notified within 30 days. That last
clause means an ODM reformulation is a regulatory event, not just a supply-chain
one.

## 8. Climate

The temperature-texture mismatch has a measured coefficient: sebum excretion rate
rises roughly **10% per 1°C** of local temperature, acne is significantly more
frequent in hot or humid regions, and in an Indian study 82 of 171 acne patients
(47.95%) reported seasonal variation, significantly worse in summer. The same
review is explicit that the humidity relationship specifically still needs
quantitative work, so heat is the better-evidenced driver.

This is the mechanism under the #1 complaint. A formulation whose occlusivity was
tuned for a temperate winter market sits on skin producing materially more sebum
for most of the Indian year — and 13.8% of all negative reviews say so in their
own words. **Of everything in Phase 2, this is the finding with the strongest
agreement between mechanism and consumer evidence**, and it is the one an ODM
brief can act on most directly.

## 9. What this does not answer, and what Phase 3/4 must not assume

- **No product-specific clinical evidence exists.** Nobody has tested these
  formulations on Fitzpatrick IV-VI skin and published it, and this phase did
  not either. Everything in §6 is mechanism-level. An honest Phase 4 position
  is: the mechanism argument is strong, the product-specific proof does not
  exist and would have to be created.
- **The dusky-tone cells are too small.** n=16 negative reviews. Do not let any
  Phase 4 rating rest on them.
- **Amazon is missing**, so authenticity is understated by construction.
- **Review data is a self-selection instrument.** People who hate a product and
  people who love it write; the middle does not. The negative-share census
  (§2) is the only number here that escapes that, and only for written reviews.
- **Complaint counts are not incidence.** 19.9% of unhappy sunscreen buyers
  citing heaviness is not 19.9% of buyers experiencing it. The population floors
  in `premium_skin_fit.json` are floors, and they are low (0.5-6.5%) precisely
  because most reviews are positive.
- **Nothing here prices anything.** Phase 4 owns the P&L.

## 10. Where the data lives

| Artifact | Path |
|---|---|
| Raw sweep (109 SKUs, 3,287 reviews, every URL) | `data/raw/premium_skin_reviews_20260810T022519Z.json` |
| Complaint analysis (all splits, floors, tone cross-tabs) | `data/manual/analysis/premium_skin_fit.json` |
| Qualitative findings (20 entries, every URL fetched) | `config/premium_skin_fit_findings.yaml` |
| DataPoints (32 rows, `[PREMIUM-SKIN]`) | `data/sources.csv`, `data/processed/IN_skincare.json`, `data/processed/IN_sun_care.json` |
| Fetcher | `lib/fetchers/premium_skin_reviews.py` |
| Transform | `lib/transforms/premium_skin_fit.py` |
| Tests (35) | `tests/test_premium_skin_fit.py` |

`data/sources.csv` went from 790 to 822 rows. One additive metric name was
introduced in `lib/transforms/schema.py` — `complaint_share` — because a share
of a *review* population is not a market share, an assortment share or a
penetration rate, and filing it under any of those would make it read as a
statement about consumers. No existing data is affected.

`config/premium_skin_fit_findings.yaml` is picked up automatically by
`lib/chat_index.py`, which globs `config/*_findings.yaml`. No wiring needed.
The dashboard export is Phase 5's job and was not touched.

## 11. Carry into Phase 3

1. **Test whether "no white cast" still sells.** It is the incumbent's proof
   point, not a gap. If Q3's demand work finds "Korean" is load-bearing, this is
   probably why — and an entrant needs a different distinctive claim.
2. **Test whether visible-light protection can be taught.** §6 is the strongest
   skin-tone argument available and it has zero observed consumer pull. If it
   cannot be taught at Rs1,900-2,400, the concept's differentiation falls back
   to texture and tolerability, which are real but far less defensible.
3. **The fair-skin skew in the reviewer base (§3) is a Phase 3 demand question.**
   If the premium band's buyers really are disproportionately fair-skinned, then
   "formulated for Indian skin tone" is aimed at a consumer who is not currently
   in the band — an acquisition thesis, not a share-shift one. That materially
   changes the size of the prize.
4. **Texture-for-humidity is the lane with mechanism and consumer evidence
   agreeing.** Carry it into the ODM brief regardless of what Phase 3 finds.
5. **Innisfree is the identified share donor** — a Korean brand with both a
   white-cast problem and a price-floor problem in the same SKUs.
