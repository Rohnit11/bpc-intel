"""Tests for the Phase 4 unit-economics model — [PREMIUM-SKIN].

The model's job is to be *arithmetically* trustworthy: its inputs are estimates,
so the only thing that can be verified is that the arithmetic does what the
docstring claims. These tests therefore concentrate on the three things the
module says most India cosmetics P&Ls get wrong (GST-inclusive MRP, creditable
IGST, commission taken off the discounted price) plus the break-even solver,
which is closed-form and must agree with the waterfall it inverts.
"""
from __future__ import annotations

import pytest

from lib.transforms.premium_skin_entry import (
    Assumption,
    CostStack,
    breakeven_discount,
    cogs_ratio_required,
    sensitivity,
    waterfall,
)


def make_stack(**overrides) -> CostStack:
    """A deliberately round-numbered stack so expected values stay hand-checkable."""
    base = dict(
        lane="test",
        label="test lane",
        exw_unit_cost_inr=200.0,
        dev_cost_inr_total=0.0,
        units_amortised=1000,
        freight_per_unit_inr=50.0,
        clearing_per_unit_inr=10.0,
        bcd_rate=0.20,
        swc_rate=0.10,
        igst_import_rate=0.18,
        reg_cost_inr_total=0.0,
        gst_output_rate=0.18,
        channel_take_rate=0.25,
        distributor_margin=0.0,
        logistics_per_unit_inr=60.0,
        returns_rate=0.10,
        return_cost_per_return_inr=100.0,
        return_writeoff_rate=0.50,
        cac_per_unit_inr=300.0,
    )
    base.update(overrides)
    return CostStack(**base)


class TestCostStack:
    def test_cif_is_exw_plus_freight_not_clearing(self):
        # Clearing is paid in India, after the assessable value is struck.
        assert make_stack().cif_inr == 250.0

    def test_sticking_duty_is_bcd_plus_surcharge_on_bcd(self):
        # CIF 250 * 20% = 50 BCD; 10% surcharge on the BCD itself = 5.
        assert make_stack().sticking_duty_inr == pytest.approx(55.0)

    def test_igst_is_excluded_from_landed_cogs(self):
        stack = make_stack()
        # IGST is creditable, so it must not appear in COGS...
        assert stack.landed_cogs_inr == pytest.approx(200 + 50 + 10 + 55)
        # ...but it is still reported, because it is real cash out the door.
        assert stack.igst_outlay_inr == pytest.approx((250 + 55) * 0.18)

    def test_igst_rate_change_does_not_move_margin(self):
        lo = waterfall(2000, 0.1, make_stack(igst_import_rate=0.05))
        hi = waterfall(2000, 0.1, make_stack(igst_import_rate=0.28))
        assert lo["contribution_inr"] == hi["contribution_inr"]
        assert lo["igst_working_capital_inr"] != hi["igst_working_capital_inr"]

    def test_oneoff_costs_amortise_over_units(self):
        stack = make_stack(dev_cost_inr_total=100_000.0,
                           reg_cost_inr_total=50_000.0,
                           listing_fee_inr_total=50_000.0,
                           units_amortised=4000)
        assert stack.amortised_oneoff_inr == pytest.approx(50.0)

    def test_zero_units_amortised_raises(self):
        with pytest.raises(ValueError):
            _ = make_stack(units_amortised=0).amortised_oneoff_inr

    def test_returns_cost_is_per_unit_sold(self):
        stack = make_stack()
        # 10% of units come back; each costs 100 to handle plus half of landed COGS.
        expected = 0.10 * (100.0 + 0.50 * 315.0)
        assert stack.returns_cost_inr == pytest.approx(expected)


class TestWaterfall:
    def test_mrp_is_gst_inclusive(self):
        w = waterfall(2360.0, 0.0, make_stack())
        # 2360 at 18% GST is exactly 2000 of revenue.
        assert w["net_revenue_inr"] == pytest.approx(2000.0)
        assert w["gst_removed_inr"] == pytest.approx(360.0)

    def test_treating_mrp_as_revenue_would_overstate_by_the_gst_rate(self):
        w = waterfall(2000.0, 0.0, make_stack())
        assert w["net_revenue_inr"] < 2000.0
        # Waterfall lines are rounded to paise, so compare at that resolution.
        assert w["net_revenue_inr"] * 1.18 == pytest.approx(2000.0, abs=0.02)

    def test_channel_commission_is_charged_on_the_discounted_price(self):
        full = waterfall(2000.0, 0.0, make_stack())
        cut = waterfall(2000.0, 0.20, make_stack())
        assert full["channel_cost_inr"] == pytest.approx(500.0)
        assert cut["channel_cost_inr"] == pytest.approx(400.0)

    def test_a_discount_costs_less_than_its_headline_depth(self):
        """The commission shrinks with the price, so the brand eats under 100%."""
        stack = make_stack()
        full = waterfall(2000.0, 0.0, stack)
        cut = waterfall(2000.0, 0.20, stack)
        headline = 2000.0 * 0.20
        actually_lost = full["contribution_inr"] - cut["contribution_inr"]
        assert actually_lost < headline
        # It is exactly the discount net of GST and commission (to paise).
        assert actually_lost == pytest.approx(headline * (1 / 1.18 - 0.25),
                                              abs=0.02)

    def test_gross_margin_is_before_cac_and_contribution_after(self):
        w = waterfall(2500.0, 0.10, make_stack())
        assert w["gross_profit_inr"] > w["contribution_inr"]
        assert (w["gross_profit_inr"] - w["contribution_inr"]
                == pytest.approx(w["logistics_inr"] + w["returns_inr"]
                                 + w["cac_inr"]))

    def test_cogs_components_sum_to_landed_cogs(self):
        w = waterfall(2000.0, 0.0, make_stack())
        parts = (w["of_which_exw_inr"] + w["of_which_freight_clearing_inr"]
                 + w["of_which_sticking_duty_inr"]
                 + w["of_which_amortised_oneoff_inr"])
        assert parts == pytest.approx(w["landed_cogs_inr"])

    @pytest.mark.parametrize("bad", [-0.1, 1.0, 1.5])
    def test_impossible_discounts_raise(self, bad):
        with pytest.raises(ValueError):
            waterfall(2000.0, bad, make_stack())


class TestBreakevenDiscount:
    def test_agrees_with_the_waterfall_it_inverts(self):
        stack = make_stack()
        d = breakeven_discount(2000.0, stack)
        assert waterfall(2000.0, d, stack)["contribution_inr"] == pytest.approx(0.0)

    def test_before_cac_breakeven_is_deeper_than_after_cac(self):
        stack = make_stack()
        assert (breakeven_discount(2000.0, stack, after_cac=False)
                > breakeven_discount(2000.0, stack, after_cac=True))

    def test_higher_mrp_buys_discount_headroom(self):
        stack = make_stack()
        assert (breakeven_discount(2900.0, stack)
                > breakeven_discount(1900.0, stack))

    def test_negative_when_the_unit_never_clears_at_full_price(self):
        stack = make_stack(exw_unit_cost_inr=1500.0)
        assert breakeven_discount(1600.0, stack) < 0

    def test_none_when_channel_take_exceeds_ex_gst_revenue(self):
        """A 90% take rate leaves nothing to scale — no price rescues it."""
        assert breakeven_discount(2000.0, make_stack(channel_take_rate=0.90)) is None

    def test_distributor_margin_stacks_onto_channel_take(self):
        direct = breakeven_discount(2000.0, make_stack())
        via_distributor = breakeven_discount(
            2000.0, make_stack(distributor_margin=0.15))
        assert via_distributor < direct


class TestSensitivityAndInversion:
    def test_band_membership_is_computed_on_street_not_list(self):
        rows = sensitivity(make_stack(), mrps=(1600.0,), discounts=(0.0, 0.10))
        assert rows[0]["in_band_at_street"] is True     # 1600 lists and holds
        assert rows[1]["in_band_at_street"] is False    # 1440 falls out

    def test_grid_covers_every_combination(self):
        rows = sensitivity(make_stack(), mrps=(1900.0, 2400.0),
                           discounts=(0.0, 0.15, 0.30))
        assert len(rows) == 6

    def test_required_cogs_hits_the_target_margin(self):
        stack = make_stack()
        needed = cogs_ratio_required(2400.0, 0.10, stack, 40.0)
        achieved = waterfall(2400.0, 0.10,
                             make_stack(exw_unit_cost_inr=needed))
        # Tolerance covers the returns write-off term the inversion documents
        # as omitted; it must stay sub-percentage-point.
        assert achieved["contribution_margin_pct"] == pytest.approx(40.0, abs=0.5)

    def test_required_cogs_goes_negative_when_target_is_unreachable(self):
        assert cogs_ratio_required(1500.0, 0.30, make_stack(), 60.0) < 0


class TestAssumption:
    def test_unresolved_assumption_is_flagged_not_defaulted(self):
        a = Assumption(value=None, unit="inr", source="NOT FOUND")
        assert a.resolved is False
        assert a.as_dict()["value"] is None

    def test_resolved_assumption_round_trips(self):
        a = Assumption(value=12.5, unit="percent", low=10.0, high=15.0,
                       source="CBIC", url="https://example.gov.in",
                       confidence="HIGH")
        d = a.as_dict()
        assert a.resolved and d["low"] == 10.0 and d["confidence"] == "HIGH"
