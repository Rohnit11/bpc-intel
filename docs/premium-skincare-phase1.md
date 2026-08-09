# Premium Skincare — Phase 1 output: supply & competitive set

> **Answers Q1** ("is Rs1,500-3,000 a real transaction band, or an MRP fiction
> that discounting collapses?") and the "who's already there" question, from
> `docs/premium-skincare-brief.md`. Run 2026-08-09. Namespace `[PREMIUM-SKIN]`.
>
> **Read this before Phase 2.** Everything below is on disk; nothing is carried
> in chat.

## 0. Verdict

**The band holds online. The kill condition is not met.**

Of the face-skincare SKUs that *list* inside Rs1,500-3,000, **79.6% on Nykaa
(179 of 225) and 87.3% on Tira (89 of 102) still transact inside it** on the
sweep date. Median discount off list is **10% on both platforms**, and 27%
(Nykaa) / 22% (Tira) of in-band SKUs carry no discount at all.

This contradicts the working assumption the brief inherited from
`price_ladder.json` — that brands are "papering the masstige gap with discounts
on premium-listed SKUs". At a 10% median, most of the band's list prices survive
contact with the platform. **The band is a real transaction band, not an MRP
fiction.**

But the finding underneath it matters more than the headline:

> **The band's floor is porous; the band itself is not.** Retention is a
> function of how close a SKU lists to Rs1,500, not of how hard it is
> discounted.

| MRP rung | SKUs | Held the band at street | Retention |
|---|---|---|---|
| Rs1,500-1,750 | 82 | 41 | **50.0%** |
| Rs1,750-2,000 | 79 | 68 | 86.1% |
| Rs2,000-2,500 | 109 | 106 | **97.2%** |
| Rs2,500-3,000 | 57 | 53 | 93.0% |

The median discount is ~10% across all four rungs. A SKU listing at Rs1,650
lands at Rs1,485 and drops out; a SKU listing at Rs2,000 lands at Rs1,800 and
stays in. Nothing about the band collapses — the bottom Rs250 of it is simply
one routine discount away from being a Rs1,400 band.

**Operator consequence:** list at **Rs1,900+** and a standard 10% platform
discount still clears Rs1,700. List at Rs1,500-1,650 — where most Korean
sunscreen sits today — and the band is decorative.

## 1. Scope and caveats (read before quoting any number here)

- **ONLINE ONLY.** Nykaa, Tira and Amazon.in. Offline is deferred to Phase 4 per
  the brief. Online is the discount-heaviest channel in the market, so a band
  that survives *here* is very likely to survive offline too — this verdict is
  directionally conservative. The reverse inference is not available: nothing
  here tells us what Nykaa Luxe, Tira stores or the chemist channel do.
- **Organised retail only.** Every observation is a listed platform price.
- **A sample, not a census.** Relevance-ranked brand pages and hero-format
  searches, deduplicated by product URL: 33 named brands + 12 format queries per
  platform. Retention shares are therefore ESTIMATE-confidence with methodology
  recorded, not measured market statistics.
- **Point-in-time.** One sweep, 2026-08-09. Indian platform discounting is
  event-driven (a "Freedom Sale" banner was live during the sweep), so this is
  one frame, not a series. **Repeat the sweep off-sale before Phase 4 costs
  anything** — see §6.
- **MRP basis.** All list prices are MRP (CLAUDE.md rule 3), which embeds
  25-45% trade margin (rule 10). Normalise via `lib/transforms/mrp_normalise.py`
  before reconciling against net realisation.
- **Non-skincare excluded.** A general beauty platform's search returns its whole
  catalogue: 369 SKUs were dropped as out of scope (199 colour cosmetics, 50
  hair, 37 body/bath, 36 accessories, 18 fragrance, 18 other, 11 appliances),
  plus 154 kits/bundles, which are baskets rather than price points. A residue
  of unfilterable cases remains — a makeup kit whose name carries no category
  word ("Nudestix Mini Nudies") cannot be caught by any rule and is one of
  perhaps a handful still counted.

## 2. Who is actually in the band

327 in-band-by-MRP SKU observations across Nykaa and Tira, from **64 distinct
brands**. Attribution is strict — only the brands the brief names get a group
label, because a price listing is not evidence of a brand's country of origin.

| Group | SKUs ≥Rs1,200 | In band by MRP | Held band | Retention | Median discount | Zero-discount |
|---|---|---|---|---|---|---|
| Korean (named) | 241 | 169 | 135 | 79.9% | 10% | 10.1% |
| Other foreign (named) | 132 | 53 | 49 | 92.5% | 0% | 58.5% |
| Homegrown (named) | 29 | 13 | 13 | **100%** | 0% | **100%** |
| Outside the named 33 | 152 | 92 | 71 | 77.2% | 11% | 23.9% |

Three things fall out of this table.

**(a) The band is crowded, and it is mostly Korean.** Korean brands supply
roughly half of everything listing in the band. Anua alone contributes 33 in-band
SKU observations, Medicube 21, COSRX 16, Beauty of Joseon 16, Mixsoon 14, The
Face Shop 13. The deck's "competitive intensity: Low" reading does not survive
contact with the shelf — see §5.

**(b) The named homegrown D2C brands are not in this band at all.** Of 29
homegrown SKUs at Rs1,200+, **Forest Essentials (15) and Kama Ayurveda (12)
account for 27**; Minimalist contributes one SKU and Plum one. Minimalist, Dot &
Key, Foxtale, Pilgrim, Deconstruct and Earth Rhythm are essentially absent above
Rs1,200. The Indian brands that *are* in the band are premium Ayurveda, they
hold **100% of list price**, and they discount nothing. That is a different
competitor with a different model, not a D2C price fight.

**(c) The band contains many brands the brief never named** — 92 in-band SKU
observations, 28% of the total, across 40 brands. By in-band SKU count: Celimax (6), RAS Luxury
Oils (4), Mizon (4), SKIN1004 (6 across two spellings), Uriage (3), Thank You
Farmer (3), Torriden (3), TonyMoly (3), Klairs (3), Round Lab (2), d'Alba (2),
Dr. Althea (2), Sulwhasoo (2), Fixderma (2), The Derma Co (2), Axis-Y (2),
Aestura (2), plus Missha, ISDIN, Eucerin, Bioheal and others. **The Phase 1
competitive set as defined by the brief is too narrow.** Several of these are
recognisably Korean and several recognisably Indian, but this sweep is not
evidence of origin and none is claimed here — resolving them is a Phase 3 task.

## 3. Hero product 1 — pigmentation / brightening serum

**This lane holds price better than any other, and Korean brands hold it
perfectly: 15 of 15 in-band Korean SKUs stayed in-band (100% retention).**
Overall lane retention is 83.3% (35 of 42), median discount 11%.

The lane splits 15 Korean / 27 outside-the-named-set, and is real and populated
at Rs1,550-3,000: Dr.Melaxin TX-Serum (Rs3,000),
Celimax Pore Dark Spot (Rs2,999), COSRX Snail Radiance Dual Essence (Rs2,800),
Innisfree Vitamin C Enzyme (Rs2,650), Medicube Glutathione Glow (Rs2,500),
COSRX Niacinamide 15 (Rs2,100), TIRTIR Niacinamide 20% (Rs2,050), Anua
Niacinamide 10 + TXA 4 (Rs2,000), TIRTIR Vitamin C24 (Rs2,000).

**The competitive fact that matters:** the brief predicted this would be the most
crowded lane domestically (Minimalist, Deconstruct, The Ordinary). At
Rs1,500-3,000 it is not. **Zero named-homegrown brands and zero named
other-foreign brands have an in-band pigmentation/brightening serum.** The
Ordinary lists 5 in-band SKUs but none in this lane. The domestic pigmentation
fight is happening *below* Rs1,500.

What is in the lane from outside the named set is the more interesting signal —
a cluster of Indian brands pricing pigmentation seriously at Rs1,590-2,499:
RAS Luxury Oils (three separate in-band pigmentation SKUs at Rs1,790-1,990),
Suganda Arbutin Tranexamic (Rs1,599), BiE Zero Dark Spot (Rs1,850), Yuderma
Melarid (Rs1,800), Ethiglo (Rs1,590), Biluma (Rs1,641), The Derma Co × Dr. V
(Rs1,599), WILDGLOW (Rs2,499), Gunam Azelaic-Tranexamic (Rs2,400).
**Q3's premise — "is the band being closed domestically while we plan?" — needs
testing against these brands, not against Minimalist.**

## 4. Hero product 2 — sunscreen

**This is the weakest cell in the entire analysis, and it is precisely where the
concept wants to compete.**

| Group | In band by MRP | Held band | Retention |
|---|---|---|---|
| Korean | 24 | 10 | **41.7%** |
| Other foreign | 8 | 7 | 87.5% |
| Homegrown | 3 | 3 | 100% |

Sunscreen overall retains 70.9% — the lowest of any format. Korean sunscreen
retains 41.7%: **most Korean sunscreen that lists in the band does not sell in
it.**

The cause is §0's mechanism, not aggressive discounting. Fallers' median list is
Rs1,650 against holders' Rs1,844, and **the median discount is 10% for both
groups**. Korean sunscreen is clustered against the floor:

- Beauty of Joseon Relief Sun (Rice+Probiotics *and* Aqua-Fresh), Rs1,500 MRP on
  Tira → Rs1,425 at a mere 5% off. Out of band.
- Beauty of Joseon Relief Sunscreen, Rs1,570 on Nykaa → Rs1,413 at 10%. Out.
- Innisfree Hyaluron Moist / UV Active Poreless, Rs1,650 → Rs1,485 at 10%. Out.
- The Face Shop Rice Water Bright, Rs1,550 → Rs1,318 at 15%. Out.

A separate group fails for the opposite reason — genuine deep discounting:
Dr.Jart+ Every Sun Day sunscreen stick (Rs2,400-2,450 → Rs960-980, **60% off**),
Dr.Jart+ Cicapair colour-correcting SPF (Rs1,950 → Rs780, 60% off), Mixsoon Bean
Sunstick (Rs2,399 → Rs1,200, 50% off), Anua Zero-Cast (Rs1,750 → Rs1,313, 25%).

**Both failure modes argue the same thing for an entrant: a Korean-formulation
sunscreen priced at Rs1,500-1,650 is not a premium sunscreen in this market, it
is a Rs1,300 sunscreen with a Rs1,570 sticker.** The corridor whitespace the repo
already flagged for sunscreen is real, but it is not at the bottom of the band.

Note the three homegrown in-band sunscreens all hold full price: Kama Ayurveda
Amsuman SPF50 (Rs2,895) and Forest Essentials' two Sun Fluids (Rs1,575) —
zero discount on all three.

## 5. Contradictions the brief asked us to resolve

**1b.1 — "competitive intensity: Low" (deck) vs "rivalry HIGH" (`porter_skincare.json`).**
At band level the deck is wrong and `porter_skincare.json` is right. 333 in-band
SKU observations from 40+ distinct brands, in a band the deck describes as served
only by "Emerging" players, is not low intensity. The tier is *thin in Indian
ownership*, which is a different statement from thin in competition. **Resolved
in favour of HIGH rivalry**, with the qualification that rivalry is currently
expressed through assortment breadth rather than price war — a 10% median
discount is orderly, not a knife fight.

**1b.3 — ownership logic.** Confirmed and sharpened. The band's occupants are
overwhelmingly foreign-owned; the only named Indian brands holding it are Forest
Essentials and Kama Ayurveda, both premium Ayurveda rather than
science/actives-led. A Korean-brand import widens the "90% foreign-owned" stat.
The India-brand-ownership lane (Korean ODM + own India brand) remains the only
one of the four that changes it.

**1b.4 — tier vocabulary.** Everything in this document keys to the literal
Rs1,500-3,000 MRP interval. The word "premium" is not used as a filter anywhere
in the pipeline.

**New contradiction found: MRP is platform-set, not brand-set.** 27 candidate
cross-platform pairs disagree on list price. Most are unverifiable because Nykaa
rarely states pack size in the product title, but the hero SKU was verified
directly on its product page:

> Beauty of Joseon Relief Sunscreen Rice + Probiotics, **50ml on both platforms**:
> **Nykaa MRP Rs1,570** ([PDP](https://www.nykaa.com/beauty-of-joseon-relief-sunscreen-rice-probiotics-spf-50-pa/p/16900408), size confirmed on page) vs
> **Tira MRP Rs1,500** ([PDP](https://www.tirabeauty.com/product/beauty-of-joseon-relief-sun-rice-probiotics-with-spf-50-pa-50-ml-7597907)).

A Rs70 (4.7%) gap on an identical pack. For an imported brand there is no single
national MRP being enforced — the platform sets it. That is a live lever for an
entrant *and* a live risk: whoever controls the listing controls the band
membership of the SKU.

## 6. What this does not answer, and what Phase 4 must not assume

- **Amazon undercuts the authorised platforms hard, and counterfeits sit below
  that.** The genuine Beauty of Joseon Relief Sun 50ml transacts at **Rs1,125 on
  Amazon** ([ASIN B09JVNZVH3](https://www.amazon.in/dp/B09JVNZVH3)) against
  Rs1,413 on Nykaa and Rs1,425 on Tira — ~20% below the authorised channel and
  well below the band. Beneath that sit lookalike listings at **Rs666** trading
  on near-miss brand names — "Beauty of **Korean** Relief Sun"
  ([B0H5Q59V69](https://www.amazon.in/dp/B0H5Q59V69)) and an unbranded "Korean
  Sunscreen Cream, Relief Sun" ([B0H5Q3KJTH](https://www.amazon.in/dp/B0H5Q3KJTH)) —
  plus "Beauty of Relief Sun Aqua-Fresh" at Rs949. **Marketplace leakage and
  brand-name counterfeiting belong in the Phase 4 risk register.** Amazon MRPs
  are seller-set and were excluded from all band arithmetic here (one strike-
  through read Rs94,900 against a Rs949 product).
- **No offline data.** Unchanged from the brief. Phase 4.
- **One frame, mid-sale.** Re-run `python -m lib.fetchers.premium_skin_prices`
  off-sale and compare before any pricing decision is costed. The fetcher and
  transform are deterministic and re-runnable; a second sweep is ~25 minutes.
- **Origin of the 40+ unnamed brands is unresolved** and deliberately not
  guessed. Phase 3.
- **Nothing here says anyone is making money at these prices.** Retention is a
  price-realisation statistic, not a margin statistic. Phase 4 owns the P&L.

## 7. Where the data lives

| Artifact | Path |
|---|---|
| Raw sweep (every URL fetched, 117 records / 3,593 products) | `data/raw/premium_skin_prices_20260809T184135Z.json` |
| Band analysis (all splits, per-SKU rows, conflicts) | `data/manual/analysis/premium_skin_band.json` |
| DataPoints (331 rows, `[PREMIUM-SKIN]`) | `data/sources.csv`, `data/processed/IN_skincare.json`, `data/processed/IN_sun_care.json` |
| Fetcher | `lib/fetchers/premium_skin_prices.py` |
| Transform | `lib/transforms/premium_skin_band.py` |
| Tests (61) | `tests/test_premium_skin_band.py` |

`data/sources.csv` went from 459 to 790 rows. Re-running the transform after
changing a filter creates *new* points rather than replacing old ones (merge
identity includes the value), so a superseded retention figure will sit beside
the current one unless the `[PREMIUM-SKIN]` points are purged from
`data/processed/` first and rewritten. That was done here; if you re-run,
do the same or the ledger will carry two contradictory answers.

Two additive metric names were introduced in `lib/transforms/schema.py` —
`assortment_share` and `discount_depth` — because band retention is a statistic
about a SKU sample, and filing it under `market_share` or `trade_margin` would
have made it read as a market statistic it is not. No existing data is affected.

## 8. Carry into Phase 2

1. **Price the hero SKUs at Rs1,900-2,400, not Rs1,500-1,700.** The floor is the
   risk, not the ceiling. Anything listing below ~Rs1,850 exits the band on a
   routine discount.
2. **Korean sunscreen's band problem is a pricing-architecture problem**, and it
   coexists with the white-cast problem Phase 2 investigates. If Phase 2 confirms
   the tone failure, the entrant has both a product and a price reason to sit
   above the incumbent Korean cluster rather than beside it.
3. **The pigmentation lane is the strongest price-holder and has no named
   domestic competitor in-band** — but it does have an unnamed one (RAS, Suganda,
   BiE, Yuderma, Biluma, Ethiglo). Phase 2's complaint mining should cover those
   listings, not only the Korean ones.
4. **Watch the platform, not just the brand.** MRP differs by platform on the
   same pack, and Amazon leaks ~20% below the authorised channel.
