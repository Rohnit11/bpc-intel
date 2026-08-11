"""What gross margin survives at Rs1,500-3,000, and what discount breaks it — [PREMIUM-SKIN].

Phase 4 of docs/premium-skincare-brief.md asks a question no fetcher can answer:
run the cost stack from a Korean ODM's ex-works price to the consumer's MRP and
report what is left. This module is that arithmetic, made deterministic so the
answer can be re-derived when an assumption changes rather than re-argued.

Everything here is an [ESTIMATE] in CLAUDE.md's sense — a model, not a
measurement. The rule that makes it publishable is that no input is invented:
every entry in ASSUMPTIONS carries a source, a confidence and a low/high range,
and anything the research could not establish is `None` and propagates as a
refusal to compute rather than as a plugged-in guess.

Three arithmetic points that most India cosmetics P&Ls get wrong, and which this
module is built around:

1. **MRP is GST-inclusive.** India's maximum retail price already contains the
   output tax. A brand's revenue line is MRP/(1+GST), never MRP. Skipping this
   overstates revenue by the GST rate on every single unit.
2. **IGST on import and GST on platform commission are input tax credits, not
   costs.** They are working capital, and they net off against output GST. Only
   Basic Customs Duty and the Social Welfare Surcharge stick to the P&L. A model
   that expenses IGST double-counts tax and can make a viable band look dead.
3. **The discount is taken off MRP, but the platform commission is taken off the
   discounted price.** So a discount costs the brand less than its headline
   depth — the commission shrinks with it. Break-even discount depth is therefore
   higher than a naive "margin / MRP" reading suggests, and the difference is
   material at 22-26% commission.

Value basis (CLAUDE.md rule 3): `mrp` and `street` are MRP-basis retail;
everything from `net_revenue` down is NET_REALISATION. The two are never compared
without the GST and commission bridge between them being shown.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Optional

logger = logging.getLogger("bpc_intel.premium_skin_entry")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ANALYSIS_PATH = (PROJECT_ROOT / "data" / "manual" / "analysis"
                 / "premium_skin_unit_economics.json")

INR_PER_USD = 96.23     # config/exchange_rates.yaml, pinned 2026-07-21
KRW_PER_USD = 1478.40   # config/exchange_rates.yaml, pinned 2026-07-21


@dataclass(frozen=True)
class Assumption:
    """One model input, with the evidence that licenses it.

    An Assumption whose `value` is None is an unresolved input: the model
    refuses to produce a figure that depends on it rather than substituting a
    plausible number. That is the difference between a standing gap and
    contamination.
    """

    value: Optional[float]
    unit: str
    low: Optional[float] = None
    high: Optional[float] = None
    source: str = ""
    url: Optional[str] = None
    confidence: str = "ESTIMATE"
    note: str = ""

    @property
    def resolved(self) -> bool:
        return self.value is not None

    def as_dict(self) -> dict:
        return {
            "value": self.value, "unit": self.unit,
            "low": self.low, "high": self.high,
            "source": self.source, "url": self.url,
            "confidence": self.confidence, "note": self.note,
        }


@dataclass
class CostStack:
    """The per-unit cost stack for one entry lane.

    All monetary fields are INR per unit unless the name says otherwise. Rates
    are fractions (0.18, not 18).
    """

    lane: str
    label: str

    # --- Make -------------------------------------------------------------
    exw_unit_cost_inr: float          # ex-works finished good, incl. primary pack
    dev_cost_inr_total: float         # formulation/NRE/stability, whole launch
    units_amortised: int              # units the one-off costs spread across

    # --- Move -------------------------------------------------------------
    freight_per_unit_inr: float
    clearing_per_unit_inr: float

    # --- Tax and registration --------------------------------------------
    bcd_rate: float                   # Basic Customs Duty, on CIF. Sticks.
    swc_rate: float                   # Social Welfare Surcharge, on BCD. Sticks.
    igst_import_rate: float           # creditable — carried for cash-flow only
    reg_cost_inr_total: float         # CDSCO/BIS registration, whole launch

    # --- Sell -------------------------------------------------------------
    gst_output_rate: float            # embedded in MRP
    channel_take_rate: float          # platform commission or retailer margin
    distributor_margin: float         # 0.0 for direct-to-platform lanes
    logistics_per_unit_inr: float     # 3PL pick-pack-ship, forward
    returns_rate: float
    return_cost_per_return_inr: float
    return_writeoff_rate: float       # share of returned units unsellable
    cac_per_unit_inr: float
    listing_fee_inr_total: float = 0.0

    # --- Provenance -------------------------------------------------------
    notes: list[str] = field(default_factory=list)

    @property
    def amortised_oneoff_inr(self) -> float:
        """Development, registration and listing costs per unit."""
        if self.units_amortised <= 0:
            raise ValueError("units_amortised must be positive")
        total = (self.dev_cost_inr_total + self.reg_cost_inr_total
                 + self.listing_fee_inr_total)
        return total / self.units_amortised

    @property
    def cif_inr(self) -> float:
        """Cost-insurance-freight value the duty is assessed on."""
        return self.exw_unit_cost_inr + self.freight_per_unit_inr

    @property
    def sticking_duty_inr(self) -> float:
        """Duty that stays in the P&L. IGST is creditable and excluded."""
        bcd = self.cif_inr * self.bcd_rate
        return bcd + bcd * self.swc_rate

    @property
    def igst_outlay_inr(self) -> float:
        """Creditable import IGST — working capital, not margin."""
        return (self.cif_inr + self.sticking_duty_inr) * self.igst_import_rate

    @property
    def landed_cogs_inr(self) -> float:
        """Everything it costs to have one sellable unit in an India warehouse."""
        return (self.exw_unit_cost_inr + self.freight_per_unit_inr
                + self.clearing_per_unit_inr + self.sticking_duty_inr
                + self.amortised_oneoff_inr)

    @property
    def returns_cost_inr(self) -> float:
        """Expected returns cost per unit SOLD, not per unit returned."""
        write_off = self.return_writeoff_rate * self.landed_cogs_inr
        return self.returns_rate * (self.return_cost_per_return_inr + write_off)

    @property
    def fixed_per_unit_inr(self) -> float:
        """Per-unit costs that do not scale with the selling price."""
        return (self.landed_cogs_inr + self.logistics_per_unit_inr
                + self.returns_cost_inr + self.cac_per_unit_inr)

    @property
    def price_scaling_take(self) -> float:
        """Share of the consumer price taken by channel before the brand sees it."""
        return self.channel_take_rate + self.distributor_margin


def waterfall(mrp_inr: float, discount: float, stack: CostStack) -> dict:
    """One unit's P&L from shelf price to contribution.

    Args:
        mrp_inr: List price in INR, GST-inclusive (India MRP convention).
        discount: Fraction off list actually charged, 0.0-1.0.
        stack: The lane's cost stack.

    Returns:
        Every line of the waterfall, plus margins as percentages of net revenue.
        `contribution_inr` is after CAC; `gross_profit_inr` is before it.
    """
    if not 0.0 <= discount < 1.0:
        raise ValueError(f"discount must be in [0, 1), got {discount}")
    street = mrp_inr * (1.0 - discount)
    net_revenue = street / (1.0 + stack.gst_output_rate)
    channel_cost = street * stack.price_scaling_take
    gross_profit = net_revenue - channel_cost - stack.landed_cogs_inr
    opex = (stack.logistics_per_unit_inr + stack.returns_cost_inr)
    contribution = gross_profit - opex - stack.cac_per_unit_inr
    return {
        "mrp_inr": round(mrp_inr, 2),
        "discount_pct": round(discount * 100, 1),
        "street_inr": round(street, 2),
        "gst_removed_inr": round(street - net_revenue, 2),
        "net_revenue_inr": round(net_revenue, 2),
        "channel_cost_inr": round(channel_cost, 2),
        "landed_cogs_inr": round(stack.landed_cogs_inr, 2),
        "of_which_exw_inr": round(stack.exw_unit_cost_inr, 2),
        "of_which_freight_clearing_inr": round(
            stack.freight_per_unit_inr + stack.clearing_per_unit_inr, 2),
        "of_which_sticking_duty_inr": round(stack.sticking_duty_inr, 2),
        "of_which_amortised_oneoff_inr": round(stack.amortised_oneoff_inr, 2),
        "logistics_inr": round(stack.logistics_per_unit_inr, 2),
        "returns_inr": round(stack.returns_cost_inr, 2),
        "cac_inr": round(stack.cac_per_unit_inr, 2),
        "gross_profit_inr": round(gross_profit, 2),
        "contribution_inr": round(contribution, 2),
        "gross_margin_pct": round(100 * gross_profit / net_revenue, 1),
        "contribution_margin_pct": round(100 * contribution / net_revenue, 1),
        "igst_working_capital_inr": round(stack.igst_outlay_inr, 2),
    }


def breakeven_discount(mrp_inr: float, stack: CostStack,
                       after_cac: bool = True) -> Optional[float]:
    """The discount depth at which the unit stops paying for itself.

    Solved rather than searched. Every price-scaling term is linear in the
    street price S, so contribution(S) = S*(1/(1+g) - take) - fixed, and the
    break-even street price falls straight out. Returns None when the unit never
    breaks even at any price (the scaling coefficient is non-positive), which is
    itself the finding: the channel take exceeds the ex-GST revenue share.

    Args:
        mrp_inr: List price in INR.
        stack: The lane's cost stack.
        after_cac: Include customer acquisition cost in the fixed block. False
            gives the gross-margin break-even, which is the right test for a
            channel that carries its own traffic (offline retail).

    Returns:
        Discount as a fraction of MRP, or None if unreachable. A NEGATIVE value
        means the unit does not clear even at full MRP.
    """
    coefficient = 1.0 / (1.0 + stack.gst_output_rate) - stack.price_scaling_take
    if coefficient <= 0:
        return None
    fixed = (stack.landed_cogs_inr + stack.logistics_per_unit_inr
             + stack.returns_cost_inr)
    if after_cac:
        fixed += stack.cac_per_unit_inr
    breakeven_street = fixed / coefficient
    return 1.0 - breakeven_street / mrp_inr


def sensitivity(stack: CostStack, mrps: tuple[float, ...],
                discounts: tuple[float, ...]) -> list[dict]:
    """Contribution margin across a price x discount grid.

    Args:
        stack: The lane's cost stack.
        mrps: List prices to test.
        discounts: Discount depths to test, as fractions.

    Returns:
        One row per cell, carrying both margin percentages and the rupee
        contribution — a thin percentage on a big number and a fat percentage on
        a small one are different businesses.
    """
    rows = []
    for mrp in mrps:
        for disc in discounts:
            w = waterfall(mrp, disc, stack)
            rows.append({
                "mrp_inr": mrp,
                "discount_pct": round(disc * 100, 1),
                "street_inr": w["street_inr"],
                "in_band_at_street": 1500.0 <= w["street_inr"] <= 3000.0,
                "gross_margin_pct": w["gross_margin_pct"],
                "contribution_margin_pct": w["contribution_margin_pct"],
                "contribution_inr": w["contribution_inr"],
            })
    return rows


def cogs_ratio_required(mrp_inr: float, discount: float, stack: CostStack,
                        target_contribution_pct: float) -> float:
    """The ex-works cost that would hit a target contribution margin.

    Inverts the waterfall on the one input a founder actually negotiates. Answers
    "what do I need the ODM quote to be", which is a more useful question than
    "what margin does this quote give me".

    Args:
        mrp_inr: List price in INR.
        discount: Expected discount depth as a fraction.
        stack: The lane's cost stack (its exw_unit_cost_inr is ignored).
        target_contribution_pct: Desired contribution margin, e.g. 40.0.

    Returns:
        Required ex-works cost in INR per unit. Negative means the target is
        unreachable at this price even with a free product.
    """
    street = mrp_inr * (1.0 - discount)
    net_revenue = street / (1.0 + stack.gst_output_rate)
    target = net_revenue * target_contribution_pct / 100.0
    # Everything in fixed_per_unit except the ex-works cost and the duty that
    # rides on it, both of which are what we are solving for.
    duty_multiplier = (1.0 + stack.bcd_rate * (1.0 + stack.swc_rate))
    non_exw_fixed = (
        stack.freight_per_unit_inr * duty_multiplier
        + stack.clearing_per_unit_inr
        + stack.amortised_oneoff_inr
        + stack.logistics_per_unit_inr
        + stack.returns_cost_inr
        + stack.cac_per_unit_inr
    )
    channel_cost = street * stack.price_scaling_take
    headroom = net_revenue - channel_cost - non_exw_fixed - target
    # The write-off component of returns also scales with landed COGS; ignoring
    # it here understates the required cost by returns_rate * writeoff_rate,
    # which is sub-1% at the rates on file. Recorded rather than silently held.
    return headroom / duty_multiplier


# ---------------------------------------------------------------------------
# Assumptions. Every entry below was fetched on 2026-08-10 and its URL verified,
# or is marked UNVERIFIED and swept rather than plugged.
#
# The confidence labels are deliberately harsh. The two ODM cost pages are
# sourcing-agency marketing content: they have a commercial interest in the
# numbers looking approachable, no methodology is published, and they cannot be
# audited. They are LOW under CLAUDE.md's rubric and the only thing rescuing
# them is that two independent agencies quote overlapping ranges. Treat the
# ODM cost band as an order-of-magnitude input, never as a quote.
# ---------------------------------------------------------------------------

_ODM = "https://oemkorea.com/blog/korean-oem-pricing-explained"
_ALTA = ("https://altameet.com/blog/"
         "how-much-does-it-cost-to-manufacture-cosmetics-in-korea-2026-complete-guide")
_EXIM = "https://www.eximguru.com/indian-customs-duty/33049910-face-creams.aspx"
_HONASA = ("https://www.storyboard18.com/advertising/"
           "mamaearth-parent-ups-marketing-spend-to-rs-744-crore-in-fy25-"
           "eyes-rs-5000-crore-arr-milestone-80137.htm")
_CEPA_IN = "https://cepaindia.com/how-to-import-cosmetics-from-korea-into-india/"

ASSUMPTIONS: dict[str, Assumption] = {
    "exw_serum_usd": Assumption(
        8.50, "usd_per_unit", low=5.00, high=12.00,
        source="OEMKorea, Korean OEM Pricing Explained", url=_ODM,
        confidence="LOW",
        note="Serum with PREMIUM actives, ex-factory, mid-tier manufacturer at "
             "1,000-3,000 MOQ with stock packaging. The commodity-actives band "
             "is $2.50-5.50; the pigmentation hero is a premium-actives product "
             "so the higher band applies. Cross-checked against Altameet's "
             "$5-10 for a 30ml serum, which overlaps. Stock packaging is stated "
             "as INCLUDED, so no separate packaging line is added — OEMKorea "
             "notes packaging alone is $1.20-2.50 on a 30ml dropper and is "
             "'sometimes more than the formula itself', i.e. it is a breakdown "
             "of this figure, not an addition to it."),
    "exw_sunscreen_usd": Assumption(
        6.00, "usd_per_unit", low=3.00, high=9.00,
        source="OEMKorea + Altameet (union of two independent ranges)",
        url=_ODM, confidence="LOW",
        note="OEMKorea $3.00-8.00; Altameet $4-9 for 50ml. Union taken because "
             "neither publishes a method and the overlap is the only "
             "corroboration available."),
    "exw_cleanser_usd": Assumption(
        3.50, "usd_per_unit", low=1.20, high=6.00,
        source="OEMKorea + Altameet", url=_ODM, confidence="LOW"),
    "exw_moisturiser_usd": Assumption(
        4.75, "usd_per_unit", low=2.00, high=8.00,
        source="OEMKorea + Altameet", url=_ODM, confidence="LOW"),
    "moq_units_per_sku": Assumption(
        1000, "units", low=1000, high=3000,
        source="OEMKorea; Altameet; corroborated by Georgetown Journal of "
               "International Affairs already on file in korea_findings.yaml",
        url=_ODM, confidence="LOW",
        note="The repo's existing Georgetown citation ('batches as small as "
             "1,000 units') is the strongest support for the floor. Modelled at "
             "the floor because a first-time foreign brand has no leverage."),
    "volume_discount_5k": Assumption(
        0.30, "fraction", low=0.20, high=0.40,
        source="OEMKorea", url=_ODM, confidence="LOW",
        note="Per-unit cost drop from a 1,000-unit to a 5,000-unit order. A "
             "further 10-20% from 5,000 to 10,000. This is the single largest "
             "controllable lever on landed cost and it argues against the "
             "4-SKU-at-MOQ launch shape."),
    "dev_fee_usd_per_formula": Assumption(
        1250.0, "usd", low=500.0, high=2000.0,
        source="Altameet (corroborated by OEMKorea)", url=_ALTA,
        confidence="LOW"),
    "stability_test_usd_per_formula": Assumption(
        550.0, "usd", low=300.0, high=800.0,
        source="Altameet", url=_ALTA, confidence="LOW"),
    "cert_test_usd_per_sku": Assumption(
        2000.0, "usd", low=1000.0, high=3000.0,
        source="Altameet", url=_ALTA, confidence="LOW",
        note="Testing and certifications, total per SKU, excluding SPF."),
    "patch_test_usd_per_sku": Assumption(
        2500.0, "usd", low=1500.0, high=3500.0,
        source="OEMKorea", url=_ODM, confidence="LOW"),
    "spf_test_usd_per_formula": Assumption(
        10000.0, "usd", low=5000.0, high=15000.0,
        source="OEMKorea", url=_ODM, confidence="LOW",
        note="SUNSCREEN ONLY, and the largest single one-off in the launch. At "
             "a 1,000-unit MOQ this is $5-15 a unit — on a product whose whole "
             "ex-works cost is $3-9. It is the reason the sunscreen hero cannot "
             "be launched at the same order size as the serum."),
    "custom_mould_usd": Assumption(
        None, "usd", low=2000.0, high=8000.0,
        source="Altameet", url=_ALTA, confidence="LOW",
        note="Excluded from the base case: stock packaging is assumed, which is "
             "what the ex-works quotes are priced on. Carried so the cost of "
             "choosing bespoke packaging is visible."),
    "lead_time_months": Assumption(
        4.5, "months", low=3.0, high=6.0,
        source="Altameet (development, sampling, production, testing, shipping)",
        url=_ALTA, confidence="LOW",
        note="Excludes CDSCO registration, which the same research put at 3-6 "
             "months and which can only partly run in parallel."),
    "bcd_rate": Assumption(
        0.20, "fraction", low=0.20, high=0.20,
        source="EximGuru, Indian customs duty for tariff item 33049910",
        url=_EXIM, confidence="LOW",
        note="STALE: the page's most recent entry is dated 02-Feb-2018 (BCD "
             "raised from 10% to 20%). Not verified against a current CBIC "
             "notification. Treated as the MFN/no-preference scenario."),
    "swc_rate": Assumption(
        0.10, "fraction", low=0.10, high=0.10,
        source="EximGuru (Social Welfare Surcharge, levied on the BCD)",
        url=_EXIM, confidence="LOW", note="Same staleness caveat as bcd_rate."),
    "igst_import_rate": Assumption(
        0.18, "fraction", low=0.18, high=0.18,
        source="EximGuru", url=_EXIM, confidence="LOW",
        note="Creditable. Affects working capital, never margin."),
    "gst_output_rate": Assumption(
        0.18, "fraction", low=0.18, high=0.18,
        source="EximGuru (IGST at import on 33049910 implies the domestic rate)",
        url=_EXIM, confidence="LOW",
        note="Embedded in MRP. NOT re-verified against the Sept-2025 GST slab "
             "restructure — a slab move would change every revenue line here."),
    "cepa_bcd_rate": Assumption(
        None, "fraction", low=0.0, high=0.20,
        source="UNVERIFIED — see note", url=None, confidence="ESTIMATE",
        note="India-Korea CEPA (in force 2010, Notification 152/2009-Customs) "
             "grants preferential duty on Korean-origin goods against a Form AK "
             "certificate of origin. Multiple secondary pages assert HS 3304 "
             "enters DUTY-FREE under it, but no page stating a 3304 rate could "
             "actually be fetched and verified: statura.in confirms only the "
             "mechanism, sunshinecargo.in covers other chapters, the "
             "worldtradescanner notification text timed out and cybex/nkgabc "
             "returned 403/409. So the rate is swept 0-20%, not assumed. This "
             "is the single largest unresolved swing factor in the model."),
    "cdsco_reg_cost_inr": Assumption(
        None, "inr", low=0.0, high=500000.0,
        source="NOT FOUND — fee schedule not retrieved", url=_CEPA_IN,
        confidence="ESTIMATE",
        note="Lead time 3-6 months per CEPA India (LOW, and the page cites the "
             "superseded Form 42/43 rather than the Cosmetics Rules 2020 "
             "COS-1/COS-2 the repo already records, so it is partly out of "
             "date). No government fee schedule was retrievable. Swept."),
    "freight_clearing_pct_of_exw": Assumption(
        None, "fraction", low=0.0, high=0.15,
        source="NOT FOUND — no fetchable Korea-India rate for 2026", url=None,
        confidence="ESTIMATE",
        note="Swept rather than invented. The sweep's purpose is to show "
             "whether freight is decision-relevant at all, which is a more "
             "honest output than a plausible-looking point estimate."),
    "channel_take_rate": Assumption(
        0.24, "fraction", low=0.22, high=0.26,
        source="Sylvr (Nykaa commission guide), already on file in "
               "data/sources.csv as IN skincare trade_margin",
        url=None, confidence="LOW",
        note="Repo figure, not re-fetched. 18% GST on the commission is "
             "creditable and excluded."),
    "adspend_ratio": Assumption(
        0.36, "fraction", low=0.36, high=0.36,
        source="Storyboard18 reporting Honasa Consumer FY25 results",
        url=_HONASA, confidence="MEDIUM",
        note="Rs743.65cr advertising on Rs2,067cr revenue, FY25 (FY24: "
             "Rs661.28cr, +12.5%). A listed, scaled Indian beauty company with "
             "an established brand portfolio spends 36 paise of every revenue "
             "rupee on advertising — and still saw PAT fall 34% to Rs72.6cr. "
             "This is a FLOOR for an unknown premium entrant, not a target. "
             "Basis mismatch stated: it is an advertising-to-revenue ratio for "
             "a mass-market portfolio, not a CAC for a premium single-SKU "
             "trial, and Honasa's revenue is NET_REALISATION."),
    "returns_rate": Assumption(
        None, "fraction", low=0.02, high=0.15,
        source="NOT FOUND — no India online beauty return rate retrieved",
        url=None, confidence="ESTIMATE", note="Swept."),
    "logistics_per_unit_inr": Assumption(
        None, "inr", low=40.0, high=120.0,
        source="NOT FOUND — no India 3PL beauty rate card retrieved",
        url=None, confidence="ESTIMATE", note="Swept."),
}

# The launch set. Four SKUs, because ODM MOQs bind per formulation and the
# brief specifies a range — but Phase 3 established that consumer demand is
# sequential single-SKU trial, so this is a supply-side shape, not a basket.
LAUNCH_SET: tuple[tuple[str, str, bool], ...] = (
    ("pigmentation_serum", "exw_serum_usd", False),
    ("sunscreen", "exw_sunscreen_usd", True),      # carries SPF testing
    ("cleanser", "exw_cleanser_usd", False),
    ("moisturiser", "exw_moisturiser_usd", False),
)


def oneoff_usd_per_sku(is_sunscreen: bool, bound: str = "value") -> float:
    """One-off development and testing cost for a single SKU, in USD.

    Args:
        is_sunscreen: Whether to include SPF testing, which applies only to a
            sunscreen and is the largest single item.
        bound: "value", "low" or "high" — which end of each assumption to take.

    Returns:
        Total one-off USD for that SKU.
    """
    def pick(key: str) -> float:
        a = ASSUMPTIONS[key]
        return float(getattr(a, bound) if bound != "value" else a.value)

    total = (pick("dev_fee_usd_per_formula")
             + pick("stability_test_usd_per_formula")
             + pick("cert_test_usd_per_sku")
             + pick("patch_test_usd_per_sku"))
    if is_sunscreen:
        total += pick("spf_test_usd_per_formula")
    return total


def _mid(key: str, fallback_bound: str = "mid") -> float:
    """An assumption's point value, or the midpoint of its swept range."""
    a = ASSUMPTIONS[key]
    if a.resolved:
        return float(a.value)
    if a.low is None or a.high is None:
        raise ValueError(f"{key} is unresolved and has no range to sweep")
    return (a.low + a.high) / 2.0


def build_stack(sku: str, exw_key: str, is_sunscreen: bool, *,
                units_per_sku: int, cepa: bool,
                freight_pct: Optional[float] = None,
                returns_rate: Optional[float] = None,
                logistics_inr: Optional[float] = None,
                cdsco_inr: Optional[float] = None,
                cac_inr: Optional[float] = None,
                mrp_for_cac: float = 2400.0) -> CostStack:
    """Assemble the lane-(c) cost stack for one SKU.

    Args:
        sku: SKU label.
        exw_key: ASSUMPTIONS key holding its ex-works USD cost.
        is_sunscreen: Adds SPF testing to the one-off block.
        units_per_sku: Order size, which drives both amortisation and the
            volume discount on ex-works cost.
        cepa: True applies a zero preferential BCD (the unverified CEPA case);
            False applies the MFN 20%.
        freight_pct, returns_rate, logistics_inr, cdsco_inr: Unresolved inputs.
            None takes the midpoint of the swept range.
        cac_inr: Customer acquisition cost per unit. None derives it from the
            Honasa advertising-to-revenue ratio applied to net revenue at
            `mrp_for_cac`.
        mrp_for_cac: The price the CAC ratio is applied to.

    Returns:
        A populated CostStack.
    """
    exw_usd = ASSUMPTIONS[exw_key].value
    # Volume discount is quoted for the 1,000 -> 5,000 step; scale it linearly
    # in log-volume terms rather than pretending it is a cliff at 5,000.
    if units_per_sku > 1000:
        import math
        step = math.log(units_per_sku / 1000.0) / math.log(5.0)
        exw_usd *= (1.0 - min(step, 1.0) * ASSUMPTIONS["volume_discount_5k"].value)
    exw_inr = exw_usd * INR_PER_USD

    freight_pct = freight_pct if freight_pct is not None else _mid("freight_clearing_pct_of_exw")
    gst = ASSUMPTIONS["gst_output_rate"].value
    if cac_inr is None:
        net_rev = mrp_for_cac / (1.0 + gst)
        cac_inr = net_rev * ASSUMPTIONS["adspend_ratio"].value

    return CostStack(
        lane="c_korean_odm_own_india_brand",
        label=f"{sku} @ {units_per_sku}u, CEPA={'yes' if cepa else 'no'}",
        exw_unit_cost_inr=exw_inr,
        dev_cost_inr_total=oneoff_usd_per_sku(is_sunscreen) * INR_PER_USD,
        units_amortised=units_per_sku,
        freight_per_unit_inr=exw_inr * freight_pct,
        clearing_per_unit_inr=0.0,   # folded into freight_pct
        bcd_rate=0.0 if cepa else ASSUMPTIONS["bcd_rate"].value,
        swc_rate=ASSUMPTIONS["swc_rate"].value,
        igst_import_rate=ASSUMPTIONS["igst_import_rate"].value,
        reg_cost_inr_total=(cdsco_inr if cdsco_inr is not None
                            else _mid("cdsco_reg_cost_inr")),
        gst_output_rate=gst,
        channel_take_rate=ASSUMPTIONS["channel_take_rate"].value,
        distributor_margin=0.0,
        logistics_per_unit_inr=(logistics_inr if logistics_inr is not None
                                else _mid("logistics_per_unit_inr")),
        returns_rate=(returns_rate if returns_rate is not None
                      else _mid("returns_rate")),
        return_cost_per_return_inr=(logistics_inr if logistics_inr is not None
                                    else _mid("logistics_per_unit_inr")),
        return_writeoff_rate=0.5,
        cac_per_unit_inr=cac_inr,
    )


def launch_cash_at_risk(units_per_sku: int, cepa: bool,
                        freight_pct: Optional[float] = None) -> dict:
    """The cheque a founder writes before the first unit sells.

    The brief's third binding consequence is range economics: ODM MOQs apply
    per formulation, so a 4-SKU launch is four MOQs. This prices that.
    """
    freight_pct = freight_pct if freight_pct is not None else _mid("freight_clearing_pct_of_exw")
    rows, total = [], 0.0
    for sku, exw_key, is_ss in LAUNCH_SET:
        stack = build_stack(sku, exw_key, is_ss, units_per_sku=units_per_sku,
                            cepa=cepa, freight_pct=freight_pct)
        goods = stack.exw_unit_cost_inr * units_per_sku
        freight = stack.freight_per_unit_inr * units_per_sku
        duty = stack.sticking_duty_inr * units_per_sku
        oneoff = stack.dev_cost_inr_total
        line = goods + freight + duty + oneoff
        total += line
        rows.append({
            "sku": sku, "units": units_per_sku,
            "exw_unit_inr": round(stack.exw_unit_cost_inr, 0),
            "goods_inr": round(goods, 0), "freight_inr": round(freight, 0),
            "sticking_duty_inr": round(duty, 0),
            "oneoff_dev_test_inr": round(oneoff, 0),
            "total_inr": round(line, 0),
        })
    igst = sum(build_stack(s, k, ss, units_per_sku=units_per_sku, cepa=cepa,
                           freight_pct=freight_pct).igst_outlay_inr * units_per_sku
               for s, k, ss in LAUNCH_SET)
    return {
        "units_per_sku": units_per_sku, "cepa_assumed": cepa,
        "by_sku": rows,
        "total_inr": round(total, 0),
        "total_usd": round(total / INR_PER_USD, 0),
        "creditable_igst_outlay_inr": round(igst, 0),
        "cash_including_creditable_igst_inr": round(total + igst, 0),
        "note": ("Excludes CDSCO registration (fee not retrievable), India "
                 "entity setup, warehousing deposits, launch marketing and any "
                 "working capital between landing stock and being paid by the "
                 "platform. It is a floor on the cheque, not the cheque."),
    }


def decision_sensitivity(mrp: float = 2400.0, discount: float = 0.10,
                         units_per_sku: int = 1000) -> list[dict]:
    """How much each unresolved input actually moves the answer.

    The point of sweeping rather than assuming: an input whose whole plausible
    range moves contribution margin by a percentage point is not worth another
    research cycle, and one that moves it by twenty is the only thing worth
    researching. This ranks them.
    """
    swept = {
        "freight_clearing_pct_of_exw": "freight_pct",
        "returns_rate": "returns_rate",
        "logistics_per_unit_inr": "logistics_inr",
        "cdsco_reg_cost_inr": "cdsco_inr",
    }
    out = []
    for key, kwarg in swept.items():
        a = ASSUMPTIONS[key]
        margins = []
        for bound in (a.low, a.high):
            stack = build_stack("pigmentation_serum", "exw_serum_usd", False,
                                units_per_sku=units_per_sku, cepa=False,
                                **{kwarg: bound})
            margins.append(waterfall(mrp, discount, stack)["contribution_margin_pct"])
        out.append({
            "input": key, "low": a.low, "high": a.high,
            "contribution_margin_at_low_pct": margins[0],
            "contribution_margin_at_high_pct": margins[1],
            "swing_pp": round(abs(margins[0] - margins[1]), 1),
            "resolved": a.resolved,
        })
    # CEPA is a binary, not a range, so it is swept separately.
    m = []
    for cepa in (True, False):
        stack = build_stack("pigmentation_serum", "exw_serum_usd", False,
                            units_per_sku=units_per_sku, cepa=cepa)
        m.append(waterfall(mrp, discount, stack)["contribution_margin_pct"])
    out.append({
        "input": "cepa_bcd_rate", "low": "0% (CEPA claimed)",
        "high": "20% (MFN, no preference)",
        "contribution_margin_at_low_pct": m[0],
        "contribution_margin_at_high_pct": m[1],
        "swing_pp": round(abs(m[0] - m[1]), 1), "resolved": False,
    })
    # Order size is a decision, not an unknown, but it belongs in the ranking.
    m = []
    for units in (1000, 5000):
        stack = build_stack("pigmentation_serum", "exw_serum_usd", False,
                            units_per_sku=units, cepa=False)
        m.append(waterfall(mrp, discount, stack)["contribution_margin_pct"])
    out.append({
        "input": "units_per_sku (a decision, not an unknown)",
        "low": 1000, "high": 5000,
        "contribution_margin_at_low_pct": m[0],
        "contribution_margin_at_high_pct": m[1],
        "swing_pp": round(abs(m[0] - m[1]), 1), "resolved": True,
    })
    return sorted(out, key=lambda r: -r["swing_pp"])


def max_sustainable_cac(mrp: float, discount: float, stack: CostStack) -> dict:
    """The most a unit can spend acquiring its buyer and still break even.

    The decision-useful inversion. A landed-cost model says whether the product
    is cheap enough; this says whether the *brand* is affordable, which is the
    binding question once Phase 3 has established that demand enters via a
    concern the brand does not yet own and that hype-led acquisition is 4.7x
    over-represented among 1-star reviews.

    Returns:
        The rupee ceiling, the same figure as a share of net revenue, and the
        Honasa FY25 advertising ratio for comparison. A negative ceiling means
        the unit cannot pay for any acquisition at all.
    """
    zero_cac = CostStack(**{**stack.__dict__, "cac_per_unit_inr": 0.0})
    w = waterfall(mrp, discount, zero_cac)
    ceiling = w["contribution_inr"]
    return {
        "mrp_inr": mrp,
        "discount_pct": round(discount * 100, 1),
        "max_cac_inr": round(ceiling, 0),
        "max_cac_as_pct_of_net_revenue": round(
            100 * ceiling / w["net_revenue_inr"], 1),
        "honasa_fy25_adspend_ratio_pct": round(
            100 * ASSUMPTIONS["adspend_ratio"].value, 1),
        "clears_at_honasa_intensity": bool(
            ceiling >= w["net_revenue_inr"] * ASSUMPTIONS["adspend_ratio"].value),
    }


def build() -> dict:
    """Run every scenario and return the analysis payload."""
    mrps = (1900.0, 2400.0, 2900.0)
    discounts = (0.0, 0.10, 0.20, 0.30)
    scenarios = {}
    for cepa in (True, False):
        for units in (1000, 5000):
            key = f"cepa_{'yes' if cepa else 'no'}_units_{units}"
            per_sku = {}
            for sku, exw_key, is_ss in LAUNCH_SET:
                stack = build_stack(sku, exw_key, is_ss,
                                    units_per_sku=units, cepa=cepa)
                per_sku[sku] = {
                    "landed_cogs_inr": round(stack.landed_cogs_inr, 0),
                    "cogs_pct_of_mrp_2400": round(
                        100 * stack.landed_cogs_inr / 2400.0, 1),
                    "breakeven_discount_pct_after_cac": (
                        round(100 * d, 1)
                        if (d := breakeven_discount(2400.0, stack)) is not None
                        else None),
                    "breakeven_discount_pct_before_cac": (
                        round(100 * d, 1)
                        if (d := breakeven_discount(2400.0, stack,
                                                    after_cac=False)) is not None
                        else None),
                    "grid": sensitivity(stack, mrps, discounts),
                }
            scenarios[key] = per_sku
    hero = build_stack("pigmentation_serum", "exw_serum_usd", False,
                       units_per_sku=1000, cepa=False)
    return {
        "generated_at": date.today().isoformat(),
        "geography": "IN",
        "segment": "skincare",
        "lane": "c_korean_odm_own_india_brand",
        "band_inr": [1500, 3000],
        "fx": {"inr_per_usd": INR_PER_USD, "pinned": "2026-07-21",
               "source": "config/exchange_rates.yaml"},
        "assumptions": {k: v.as_dict() for k, v in ASSUMPTIONS.items()},
        "unresolved_inputs": [k for k, v in ASSUMPTIONS.items() if not v.resolved],
        "scenarios": scenarios,
        "decision_sensitivity": decision_sensitivity(),
        "launch_cash_at_risk": {
            "moq_1000_no_cepa": launch_cash_at_risk(1000, cepa=False),
            "moq_1000_cepa": launch_cash_at_risk(1000, cepa=True),
            "moq_5000_no_cepa": launch_cash_at_risk(5000, cepa=False),
        },
        "max_sustainable_cac": {
            f"{sku}_cepa_{'yes' if cepa else 'no'}_units_{units}_mrp_{int(m)}"
            f"_disc_{int(d * 100)}": max_sustainable_cac(
                m, d, build_stack(sku, exw_key, is_ss, units_per_sku=units,
                                  cepa=cepa))
            for sku, exw_key, is_ss in LAUNCH_SET
            if sku in ("pigmentation_serum", "sunscreen")
            for cepa in (True, False)
            for units in (1000, 5000, 10000)
            for m in (1900.0, 2400.0, 2900.0)
            for d in (0.0, 0.10)
        },
        "required_exw_for_40pct_contribution_usd": {
            f"mrp_{int(m)}_disc_{int(d*100)}": round(
                cogs_ratio_required(m, d, hero, 40.0) / INR_PER_USD, 2)
            for m in mrps for d in (0.0, 0.10, 0.20)
        },
        "method_note": (
            "Every figure is [ESTIMATE] under CLAUDE.md rule 1(d): a model, not "
            "a measurement. Inputs carry a source, a confidence and a range in "
            "`assumptions`; inputs that could not be sourced are listed in "
            "`unresolved_inputs` and are SWEPT across a plausible range rather "
            "than plugged with a point value, with `decision_sensitivity` "
            "ranking how much each one actually moves the answer. MRP is "
            "GST-inclusive so revenue is MRP/(1+GST); import IGST and the GST "
            "on platform commission are input tax credits and are excluded from "
            "margin (reported separately as working capital); only BCD and the "
            "Social Welfare Surcharge stick. Arithmetic is covered by "
            "tests/test_premium_skin_entry.py."),
    }


def main() -> None:
    """Run the model and write the artifact."""
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    payload = build()
    ANALYSIS_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                             encoding="utf-8")
    logger.info("Wrote %s", ANALYSIS_PATH)
    for row in payload["decision_sensitivity"]:
        logger.info("swing %5.1fpp  %s", row["swing_pp"], row["input"])


__all__ = [
    "Assumption", "CostStack", "waterfall", "breakeven_discount",
    "sensitivity", "cogs_ratio_required", "oneoff_usd_per_sku",
    "build_stack", "launch_cash_at_risk", "decision_sensitivity", "build",
    "main", "ASSUMPTIONS", "LAUNCH_SET", "INR_PER_USD", "KRW_PER_USD",
    "ANALYSIS_PATH",
]


if __name__ == "__main__":
    main()
