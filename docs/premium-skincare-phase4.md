# Premium Skincare — Phase 4 output: entry, operator-grade

> Executes Phase 4 of `docs/premium-skincare-brief.md`: band-level Porter, the
> four entry lanes with the primary one pressure-tested hardest, real unit
> economics, offline, and a risk register. Run 2026-08-10. Namespace
> `[PREMIUM-SKIN]`.
>
> **Read this before Phase 5.** Everything is on disk; nothing is carried in chat.

## 0. Verdict

**The band is real, the product is affordable to make, and the plan still does
not clear — because the binding constraint is neither the band nor the COGS. It
is order size, and after that, the cost of demand.**

Three findings, in the order they bind:

**(1) At the launch shape the brief specifies, the unit loses money at full
price.** A 4-SKU range at 1,000-unit MOQ each lands the pigmentation serum at
**80.4% of a Rs2,400 MRP** and the sunscreen at **107.3%** — before marketing,
before returns, at zero discount. The same SKUs at 5,000 units per SKU land at
**38.4%** and **37.2%** and break even before marketing at a 28-30% discount,
which is far deeper than the 10% the band actually charges. Order size swings
contribution margin by **57.3 percentage points**, more than every unresolved
research question in the model combined — and it is a decision, not an unknown.

**(2) The cost of demand kills it before the cost of goods does.** Of 36
modelled price × volume × duty cells for the two hero SKUs, exactly **one**
clears the advertising intensity that a listed Indian beauty company actually
runs at: Honasa Consumer spent **Rs743.65cr on advertising against Rs2,067cr of
revenue in FY25 — 36%** — and still saw profit fall 34%. The one cell that
clears is sunscreen at 10,000 units, Rs2,900 MRP, 10% discount, with CEPA duty
relief assumed. Phase 3 already showed demand enters via acne (3x pigmentation
in search), that the concern-and-proof vocabulary is owned by RAS Luxury Oils
and Suganda at Rs1,599-1,990, and that hype-acquired buyers are 4.7x
over-represented among 1-star reviews. This phase prices that: acquisition is
the constraint, and COGS is not.

**(3) The lane with the best cost structure is not the brief's primary lane.**
Every input the model ranks as decision-relevant on the import lane — customs
duty (11.0pp of margin), freight and clearing (8.5pp), CDSCO import
registration and its 3-6 month lead time, the manufacturing-site lock-in that
gives the ODM its leverage — is deleted by **lane (b), India manufacture under
Indian brand ownership**. And the empirical record agrees: Indian-origin brands
hold the band at **87.8%** against the Korean cluster's **81.3%**, at 54.1%
zero-discount against 22.8%. Lane (b) is blocked on exactly one unverified
question — whether an Indian manufacturer can make a competitive sunscreen —
and that question is now the highest-value open item in the whole thread.

**What this does not say.** It does not say the band is a bad market or that the
concept is dead. It says the *shape* is wrong: four SKUs at MOQ, priced against
an untested brand, is the version that fails. One hero at volume, sold on the
concern rather than the passport, against a cost stack that avoids the border,
is the version the evidence supports.

---

## 1. Scope and caveats (read before quoting any number here)

- **The unit economics are a MODEL, not a measurement.** Every figure is
  `[ESTIMATE]` under CLAUDE.md rule 1(d). Inputs carry a source, a confidence
  and a range in `premium_skin_unit_economics.json`; the arithmetic is covered
  by 28 tests. The arithmetic is trustworthy. **The inputs are not audited.**
- **Every cost input is LOW confidence.** The ODM per-unit costs come from two
  sourcing-agency marketing pages, which have a commercial interest in the
  numbers looking approachable and publish no methodology. They are used because
  they independently quote overlapping ranges, and for no better reason. The
  duty rates come from a page whose most recent entry is dated **2018**.
- **Unresolved inputs are SWEPT, not plugged.** Freight, returns, 3PL cost,
  CDSCO fee and CEPA duty treatment could not be sourced. Rather than inventing
  plausible values, the model runs each across its plausible range and reports
  how much it moves the answer — which turns out to be the more useful output
  (§4.3). Nothing in this document rests on a number nobody could find.
- **Offline is only partially researched, and that is the largest caveat here.**
  Phase 3 concluded offline must be primary in Phase 4. The research pass
  commissioned for it did not complete, so §6 documents what is on file and
  names precisely what is missing rather than modelling it.
- **Four research sweeps were commissioned for this phase and all four were cut
  off by a session limit** before writing their findings. What survives is what
  was verified directly afterwards, and it is thinner than intended —
  particularly on ODM terms, offline economics and lane (d). Ranked openly in §9.
- **Online prices only, organised retail only**, as in Phases 1-3.

---

## 2. Porter at band level — contradiction 1b.1 resolved

The brief's first contradiction: the deck rates competitive intensity **Low**
for this tier; `porter_skincare.json` rates India skincare rivalry **HIGH**.

**Resolved in favour of HIGH.** The deck is measuring the wrong thing. At band
level the second price frame finds **385 in-band-by-MRP SKU observations from
60+ brands**, with 171 from Korean brands alone. A tier the deck describes as
served only by "Emerging" players carries Anua, Medicube, COSRX, Beauty of
Joseon, Mixsoon and The Face Shop at assortment depth. The deck's reading is a
statement about *Indian ownership* of the tier, not about competition in it, and
the two were being conflated — exactly the distinction the brief's item 1b.3
warned about.

| Force | Category (`porter_skincare.json`) | **Band level (this phase)** | Change |
|---|---|---|---|
| Rivalry | HIGH | **HIGH** | Confirmed |
| Buyer power | HIGH | **HIGH** | Confirmed, sharpened |
| Supplier power | LOW | **MEDIUM** | **Upgraded** |
| New-entrant threat | HIGH | **HIGH** | Confirmed |
| Substitutes | *unrated (INSUFFICIENT)* | **HIGH** | **Now rateable** |

Two of these are genuine changes, and both come from looking at the band rather
than the category.

**Supplier power LOW → MEDIUM.** The category view is right that Korea's ODM
base is commoditised. But at the volumes an entrant actually places, three
things hand the supplier leverage. The one-off block dominates: development,
stability, patch and certification testing land at ~Rs606,000 per ordinary SKU
and **Rs1,568,000 for the sunscreen** once SPF testing (USD5,000-15,000 per
formula) is included — the sunscreen's non-recurring cost is **2.7x its goods
cost** at a 1,000-unit order, and it is sunk with one manufacturer. Per-unit
cost then falls 20-40% from 1,000 to 5,000 units, so the price depends on a
commitment the entrant cannot make on day one. And CDSCO registration is tied to
the manufacturing site, so switching ODM means re-registering.

**Substitutes unrated → HIGH.** The category Porter left this open for want of
cross-category substitution evidence. At band level it is rateable, because the
substitute for a Rs1,900 SKU is not another category — it is the same benefit
bought cheaper, by two routes Phase 1 measured directly:

- **Vertical.** Indian D2C sells the same actives a full tier down — Minimalist
  ceiling Rs1,347, Deconstruct Rs799, Pilgrim and Foxtale Rs695 — and `foxtale`
  outsearches `beauty of joseon` and `cosrx` by ~4.5x from *below* the band.
- **Grey.** The identical Korean SKU leaks ~20% below the authorised channel
  (Beauty of Joseon Relief Sun 50ml: Rs1,125 on Amazon vs Rs1,413 on Nykaa),
  with near-miss counterfeits at Rs666. **A brand cannot price against a
  competitor that is its own product.**

**Overall: unattractive at the launch shape the brief specifies, conditionally
attractive at scale.** Four forces HIGH and the fifth upgraded — but the binding
constraint Phase 4 found is arithmetic, not structural. See §4.

---

## 3. The price re-sweep — the band holds on a cleaner frame

The brief required the Phase 1 sweep to be re-run before Phase 4 priced
anything, and Phase 3 required the brand list to be corrected first. Both done.

| | Frame 1 (2026-08-09) | **Frame 2 (2026-08-10)** |
|---|---|---|
| Nykaa in-band SKUs / retention | 225 / 79.6% | 272 / **83.5%** |
| Tira in-band SKUs / retention | 102 / 87.3% | 113 / **84.1%** |
| Nykaa zero-discount share | 27.1% | **37.9%** |
| Tira zero-discount share | 21.6% | **37.2%** |
| Tira median discount | 10% | **5%** |

Frame 1 ran mid-"Freedom Sale". Frame 2 is materially less discounted — zero-
discount SKUs rose by ~10 points on both platforms and Tira's median discount
halved — and **the band holds anyway.** Phase 1's verdict was directionally
conservative, as it claimed.

**The floor finding survives unchanged**, which is the number that actually
drives pricing:

| MRP rung | SKUs | Held band | Retention (frame 2) | *(frame 1)* |
|---|---|---|---|---|
| Rs1,500-1,750 | 98 | 54 | **55.1%** | *50.0%* |
| Rs1,750-2,000 | 92 | 80 | 87.0% | *86.1%* |
| Rs2,000-2,500 | 126 | 122 | **96.8%** | *97.2%* |
| Rs2,500-3,000 | 69 | 66 | 95.7% | *93.0%* |

**List at Rs1,900+.** Confirmed on independent data, and Phase 3 reached the
same floor from affordability. Korean sunscreen still retains only **48.0%**
(was 41.7%) — the weakest cell in the analysis remains the concept's hero lane.

### 3.1 What the corrected brand list found

Re-keying with Phase 3's corrections changes the domestic picture materially.
**Homegrown in-band SKUs go from 13 to 74**, because Phase 1 swept the wrong
Indian brands:

| Group | In-band SKUs | Retention | Median discount | Zero-discount |
|---|---:|---:|---:|---:|
| Korean | 171 | 81.3% | 10% | 22.8% |
| **Homegrown** | **74** | **87.8%** | **0%** | **54.1%** |
| Other foreign | 51 | 94.1% | 0% | 68.6% |
| Outside the named set | 84 | 77.4% | 10% | 33.3% |

Fifteen Indian-origin brands now hold in-band single SKUs: RAS Luxury Oils (12),
BiE (11), Aminu (9), Forest Essentials (8), Kama Ayurveda (7), **D'you (7)**,
Yuderma (4), WildGlow (3), Plum (3), The Derma Co (3), Fixderma (2), Miduty (2),
Put Simply, Suganda, Ethiglo. **Phase 3's finding that Indian brands hold price
better than the Korean cluster is confirmed on a second frame.**

**D'you's open question is closed.** Phase 3 asked whether it lists on the
platforms at all. It does — **14 priced observations across both Nykaa and Tira,
at Rs2,100-3,500, at zero discount on every single one.** An Indian brand,
Korean-formulated, holding the top of the band at full price on the same
platforms where Korean brands discount 10-60%. Put Simply appears at
Rs1,499-1,699 discounting 20-25%. **Same manufacturing geography, opposite price
architecture** — Phase 3's conclusion that brand architecture sets price, not
formulation origin, now has shelf evidence on both sides.

### 3.2 Three corrections made to the pipeline

Recorded because they change published numbers:

1. **Limese removed** from the homegrown brand list (Phase 3: it is a K-beauty
   importer, a conduit, not a brand).
2. **A bare `Quench` alias was registered and then removed.** It matched a
   Thalgo "Moisture Quenching Serum" and a TBC "Yoga Quench Water Cream" — a
   brand alias short enough to be an ordinary product-description word
   attributes competitors' product to it. **Quench Botanics is not carried on
   Nykaa or Tira under that name.**
3. **An `ingestible` scope exclusion was added.** Widening the brand list pulled
   in Miduty, largely a nutraceutical brand, whose softgels, marine collagen and
   liposomal NMN were being counted as face skincare. 27 SKUs now excluded.
   Matched on unambiguous dosage forms only — never on "collagen", "probiotics"
   or "omega", which all appear on genuine topicals.

---

## 4. Unit economics — what actually survives at Rs1,500-3,000

Model: `lib/transforms/premium_skin_entry.py`. Output:
`data/manual/analysis/premium_skin_unit_economics.json`. Tests:
`tests/test_premium_skin_entry.py` (28).

### 4.1 Three things the model is built to get right

Most India cosmetics P&Ls get these wrong, and each error is large enough to
flip a verdict:

1. **MRP is GST-inclusive.** Revenue is MRP/(1+GST), never MRP. Skipping this
   overstates revenue by the GST rate on every unit.
2. **Import IGST and GST on platform commission are input tax credits, not
   costs.** They are working capital and net off against output GST. Expensing
   them double-counts tax and can make a viable band look dead. Only Basic
   Customs Duty and the Social Welfare Surcharge stick.
3. **The discount comes off MRP but the commission comes off the discounted
   price**, so a discount costs the brand less than its headline depth — the
   commission shrinks with it. At 24% commission the brand eats about 60 paise
   of each rupee discounted, not 100.

### 4.2 The headline table

Landed COGS as a share of a Rs2,400 MRP, and the discount at which the unit stops
paying for itself:

| Scenario | Serum COGS | Sunscreen COGS | Serum break-even discount (before marketing) |
|---|---:|---:|---:|
| 1,000 units/SKU, MFN duty | Rs1,929 (**80.4%**) | Rs2,576 (**107.3%**) | **−43.9%** |
| 1,000 units/SKU, CEPA | Rs1,736 (72.3%) | Rs2,439 (101.6%) | −30.1% |
| **5,000 units/SKU, MFN duty** | Rs922 (**38.4%**) | Rs894 (**37.2%**) | **+28.1%** |
| 5,000 units/SKU, CEPA | Rs787 (32.8%) | Rs798 (33.3%) | +37.8% |

A negative break-even discount means the unit does not clear **even at full MRP
with no discount at all**. At MOQ, the sunscreen costs more to land than it
sells for.

**The cheque.** A 4-SKU launch at 1,000 units each is **Rs6.26m (~USD65,000)** in
goods, freight, sticking duty and development/testing, plus Rs0.52m of
creditable IGST. At 5,000 units it is **Rs13.4m (~USD140,000)**. Both exclude
CDSCO registration, entity setup, warehousing, launch marketing and the working
capital between landing stock and being paid by the platform — this is a floor
on the cheque, not the cheque.

Note what dominates at MOQ: the sunscreen's **Rs1,568,549 of one-off
development and testing against Rs577,380 of goods.** SPF testing at
USD5,000-15,000 per formula is the single largest line in the launch, and it
falls entirely on the hero SKU that best expresses the skin-tone thesis.

### 4.3 What the discount depth breaks — and what CAC breaks first

The brief asked whether we can match competitors' 20-35% discounting and live.
**At 5,000 units, yes on goods — the serum breaks even at a 28.1% discount
before marketing.** But that is the wrong test, because marketing is the larger
number.

Applying Honasa's FY25 advertising intensity (**36% of revenue**) as the CAC
line, of **36 modelled cells across both heroes, price, volume and duty
treatment, exactly one clears**: sunscreen, 10,000 units, Rs2,900 MRP, 10%
discount, CEPA assumed. The maximum sustainable CAC at the more realistic
5,000-unit/Rs2,400 case is **Rs405 per unit (22.1% of net revenue)** for the
serum — well under what a brand with no mental availability would actually pay
in a band where hype-led acquisition converts into 1-star reviews.

Honasa is an imperfect benchmark and the basis mismatch is stated deliberately:
it is an advertising-to-revenue ratio for a scaled mass-market portfolio, not a
CAC for premium single-SKU trial. It is used as a **floor** — a company with
established brands and volume spends 36 paise per revenue rupee — not a target.

### 4.4 Which unknowns actually matter

The model sweeps every input that could not be sourced and ranks how much its
full plausible range moves contribution margin:

| Input | Swing | Status |
|---|---:|---|
| **Units per SKU (1,000 → 5,000)** | **57.3pp** | **A decision, not an unknown** |
| CDSCO registration cost (Rs0-500k) | 28.5pp | Unresolved — but only because it amortises over 1,000 units |
| **CEPA duty treatment (0% vs 20% BCD)** | **11.0pp** | **Unresolved — worth one phone call** |
| Freight + clearing (0-15% of ex-works) | 8.5pp | Unresolved, not decisive |
| Returns rate (2-15%) | 7.4pp | Unresolved, not decisive |
| 3PL per unit (Rs40-120) | 4.8pp | Unresolved, not decisive |

**This ranking is the most useful thing in the phase.** The decision the founder
controls outweighs every fact nobody could find. Freight, returns and logistics
— the three inputs a naive model would have guessed and then leaned on — cannot
change the answer between them. And the two that could (order size, CEPA) are
one decision and one phone call.

---

## 5. The four lanes

Full ratings, rationale and evidence in
`data/manual/analysis/premium_skin_entry.json`.

| Lane | Rating |
|---|---|
| (a) Import a Korean brand via a conduit | **NOT RECOMMENDED** |
| (b) India-manufactured Korean-formulation own brand | **STRUCTURALLY FAVOURED, blocked on one capability question** |
| (c) Korean ODM + own India brand *(the brief's primary lane)* | **VIABLE ONLY ABOVE ~5,000 UNITS/SKU, AND ONLY AT LOW CAC** |
| (d) JV or licence with a Korean brand | **INSUFFICIENT — not rated** |

**(a) fails on three counts at once.** It is the position the band is already
saturated with; Korean-origin SKUs hold price worst of any origin group (81.3%
vs 87.8% Indian); and it widens the deck's "90% foreign-owned" statistic the
brief's item 1b.3 says only Indian brand ownership fixes. Its one advantage — a
ready-made brand — is worth least here, because Phase 3 showed Korean provenance
is invoked in 2.2% of positive reviews and indexes 0.6 in search.

**(b) deletes every decision-relevant import cost** — duty (11.0pp), freight
(8.5pp), CDSCO import registration and its 3-6 month lead time, and the
site-registration lock-in that gives the ODM its leverage. It is also the lane
the evidence shows working: Indian-origin brands hold the band better, and RAS
Luxury Oils and Suganda already own the concern-and-proof vocabulary at
Rs1,599-1,990. **It is not rated FAVOURED outright for exactly one reason:
whether an Indian manufacturer can make a competitive sunscreen — permitted UV
filters, achievable textures — is unverified in both directions.**

**(d) is not rated.** No fetched source established a single India-Korea beauty
JV or licensing precedent, royalty rate or term structure. Per the brief,
INSUFFICIENT renders as research needed, never as a hedged guess.

### 5.1 The case against the primary lane

The brief asks for this to be built honestly. Seven arguments, all evidenced,
in `premium_skin_entry.json:case_against_the_primary_lane`. In short:

1. **The asset the lane buys has no measured demand pull.** Lane (c) pays an
   import stack to obtain Korean manufacture — a claim invoked in 2.2% of
   reviews, 0 of 333 Indian-SKU reviews, and indexing 0.6 in search. The founder
   who has run the lane longest says it plainly: *"being made in Korea is hardly
   an edge anymore"* (Shamika Haldipurkar, D'you).
2. **The economics do not work at the brief's order size** (§4.2). The ex-works
   cost required to hit a 40% contribution margin at 1,000 units is *negative*
   at every price in the band — unreachable with free product.
3. **The lane has better-funded incumbents, and they are on the shelf** — D'you
   at zero discount across 14 observations, Put Simply below the band.
4. **The sunscreen hero carries a one-off 2.7x its goods cost.**
5. **Formula exclusivity is unestablished** — the ODM may make the same base for
   a competitor.
6. **Korean formulation increases exposure to the failure mode Phase 2 actually
   found** — irritation (19.2%) and heaviness in humidity (15.4%), a temperate
   formulation meeting a tropical market.
7. **The skin-tone argument that survives is invisible to buyers** — tinted
   iron-oxide photoprotection, which Phase 2 found consumers cannot perceive and
   show zero pull for.

**The strongest counter-argument**, stated fairly: sunscreen formulation is the
one thing Korea plausibly supplies that India may not, and it is the lane's only
unhedged advantage. It is also unverified in both directions. **That single
question decides between (b) and (c)**, and it is the highest-value open item in
the thread.

---

## 6. Offline — partially researched, and still the largest open risk

Phase 3 concluded offline must be treated as primary here. **It has not been,
and this is the honest statement of that gap rather than a modelled substitute.**
The research pass commissioned for it did not complete.

**On file:** Nykaa runs 116 multi-brand Beauty stores, 56% in Tier 2/3 cities;
~two-thirds of Nykaa store GMV is premium brands; Nykaa offline rose from 3.4%
(1QFY22) to 9.0% (3QFY25) of BPC GMV; India BPC channel mix FY25 is 52%
unorganised offline / 28% organised offline / 20% online.

**Not established, and not inferred:** retailer and distributor margins on
premium skincare; listing and slotting fees for a new brand; minimum volume
commitments; consignment vs outright purchase and payment terms; beauty-advisor
cost and who bears it; the chemist and dermatologist-detailing channel; and the
brand-by-chain physical presence map for the Phase 1 competitive set.

**Much of this is not web-accessible** — which is itself the finding. It needs
trade conversations, not another desk pass, and it should not be modelled until
it has them.

**What it means for the verdict.** Phase 1's discount verdict remains an
*online* verdict. Offline typically holds closer to MRP, so price realisation is
more likely understated than overstated by this thread. But the cost side moves
the other way: offline adds retailer margin **on top of** the platform
commission already in the model. Neither effect is measured, so they are not
netted.

---

## 7. Risk register

Ten risks with severity, rationale and mitigation in
`premium_skin_entry.json:risk_register`. The three rated HIGH:

- **Order-size trap.** The launch shape the brief specifies is the shape that
  cannot work. Viability needs ~5,000 units/SKU committed *before* any demand
  evidence — Rs13.4m of goods and one-offs. Volume is simultaneously the only
  real margin lever and the largest inventory risk. *Mitigation: sequence rather
  than launch a range. Phase 3 already established demand is sequential
  single-SKU trial; the range exists for MOQ and shelf reasons only.*
- **Cost of demand exceeds cost of goods.** One of 36 cells clears Honasa
  intensity. *Mitigation: treat CAC as the binding constraint and test any plan
  against the model's max-sustainable-CAC ceiling.*
- **Every cost input is LOW confidence.** *Mitigation: re-run the model against
  a real quote and a current CBIC tariff before committing capital. The model is
  built to be re-run, not to be believed.*

Also carried: CEPA unverified, marketplace leakage and counterfeiting, ODM
formulating the same base for a competitor, Korean supply intensifying faster
than Indian demand, the porous band floor, Indian brands closing the band, and
post-launch climate/texture mismatch.

---

## 8. What Phase 4 changes about earlier phases

1. **Phase 1's Rs1,900 floor is confirmed on independent, less-discounted
   data** (§3) — 55.1% retention at Rs1,500-1,750 vs 96.8% at Rs2,000-2,500.
2. **Phase 1's homegrown group was wrong by construction**, not by measurement:
   13 in-band SKUs became 74 once the right brands were swept. The categorical
   finding about *named D2C brands* survives; the group statistic does not.
3. **Phase 3's "Indian brands hold price better" is confirmed** on a second
   frame (87.8% vs 81.3%).
4. **Phase 3's open question on D'you is closed** — it lists on both Nykaa and
   Tira, 14 observations, zero discount throughout.
5. **Quench Botanics is not carried on either platform** under that name.
6. **The deck's "competitive intensity: Low" is formally resolved against**
   (§2), and the substitutes force that the category Porter could not rate is
   now rated HIGH at band level.

---

## 9. What this does not answer, ranked by value

1. **Can an Indian contract manufacturer make a competitive sunscreen?**
   Permitted UV filters in India vs Korea, and achievable textures. **This single
   question decides between lanes (b) and (c).**
2. **A real ODM quote** at 1,000 / 5,000 / 10,000 units, with exclusivity terms,
   and whether they will formulate for Indian conditions or adapt a base. Every
   cost input here is agency marketing content.
3. **Offline economics in full** (§6). Not web-accessible; needs trade
   conversations.
4. **India-Korea CEPA treatment of HS 3304**, verified against a current CBIC
   notification. Worth 11.0pp of contribution margin. Multiple secondary pages
   assert duty-free entry; none stating a 3304 rate could be fetched and
   verified, so it is swept, not assumed.
5. **Current BCD/SWS/GST on HS 3304 for 2026.** The only retrievable rates were
   dated 2018 and pre-date the Sept-2025 GST restructure.
6. **CDSCO fee schedule and realistic lead time** under the Cosmetics Rules 2020.
   Only a 3-6 month estimate was retrievable, from a page still citing the
   superseded Form 42/43.
7. **India D2C beauty CAC benchmarks** beyond an advertising-to-revenue ratio,
   and contribution margins for *premium* rather than mass Indian brands.
8. **Lane (d) entirely** — no JV or licensing precedent or terms.

---

## 10. Where the data lives

| Output | Path |
|---|---|
| Entry analysis (Porter band-level, 4 lanes, case against, offline, risks) | `data/manual/analysis/premium_skin_entry.json` |
| Unit economics model output (scenarios, sensitivity, cash at risk, CAC ceilings) | `data/manual/analysis/premium_skin_unit_economics.json` |
| Price frame 2 (band arithmetic, corrected brand list) | `data/manual/analysis/premium_skin_band_frame2.json` |
| Raw sweep, frame 2 (141 records / 3,868 products) | `data/raw/premium_skin_prices_20260810T042850Z.json` |
| Sourced Phase 4 claims → `data/sources.csv` | `data/manual/research_drops/premium_skin_entry.json` |
| Re-runnable: unit economics model | `lib/transforms/premium_skin_entry.py` |
| Tests (28, arithmetic only — inputs are estimates) | `tests/test_premium_skin_entry.py` |

Frame 1 (`premium_skin_band.json`) is untouched and remains the Phase 1 artifact.
Note that `premium_skin_band.run()` writes to `premium_skin_band.json` as a side
effect, so a frame-2 run must be followed by restoring frame 1 from git — done
here.
