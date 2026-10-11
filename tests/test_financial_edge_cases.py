import math

import pytest

from core import financial_math as fm, scenarios as sc


def base(**kw):
    a = sc.preset("Base")
    a.update(kw)
    return a


def test_zero_pilot_volume_still_pays_setup_and_fees():
    r = fm.evaluate(base(pilot_monthly_cases=0))
    assert r["pilot_capacity"] == 0 and r["pilot_net"] == -r["pilot_cost"]


@pytest.mark.parametrize("k", ["eligible_share", "completion_rate"])
def test_zero_share_gives_zero_capacity(k):
    r = fm.evaluate(base(**{k: 0}))
    assert r["pilot_capacity"] == 0 and r["runrate_capacity"] == 0
    assert fm.interpret(base(**{k: 0}))["breakeven"] is None


def test_zero_cash_realization():
    r = fm.evaluate(base(cash_realization=0))
    assert r["pilot_cash"] == 0 and r["runrate_cash"] == 0 and r["runrate_net"] < 0


def test_zero_vendor_cost_and_no_scale():
    a = base(scale_vendor_monthly=0, scale_support_monthly=0, scale_audit_monthly=0)
    r = fm.evaluate(a)
    assert r["recurring_cost"] == 0 and r["runrate_net"] == r["runrate_cash"]
    assert fm.interpret(a)["coverage"] is None
    assert fm.evaluate(base(scale_monthly_cases=0))["runrate_capacity"] == 0


def test_zero_exit_returns():
    r = fm.evaluate(base(exit_arr_m=0))
    assert r["venture_proceeds"] == 0 and r["venture_moic"] == 0 and r["venture_irr"] == -1
    assert fm.evaluate(base(exit_rev_multiple=0))["venture_moic"] == 0
    assert fm.evaluate(base(equity_value_factor=0))["venture_moic"] == 0


@pytest.mark.parametrize("patch", [
    dict(pilot_monthly_cases=-1), dict(loaded_hourly_cost=-5), dict(scale_vendor_monthly=-1), dict(exit_rev_multiple=-1),
    dict(cash_realization=-0.1), dict(cash_realization=1.1), dict(eligible_share=1.2), dict(completion_rate=2),
    dict(ownership_dilution=-0.1), dict(ownership_dilution=1.5), dict(hold_years=0), dict(investor_check_m=0),
    dict(investor_check_m=30), dict(pilot_monthly_cases=float("nan")), dict(exit_arr_m=float("inf")),
    dict(pilot_setup="abc"), dict(pilot_setup=None),
])
def test_invalid_inputs_rejected(patch):
    a = base(**patch)
    assert fm.validate_inputs(a)
    with pytest.raises(ValueError):
        fm.evaluate(a)


def test_missing_key_rejected():
    a = base()
    del a["hold_years"]
    with pytest.raises(ValueError, match="hold_years"):
        fm.evaluate(a)


def test_nonpositive_post_money():
    a = base(exit_premoney_m=0, round_raise_m=0, investor_check_m=0.0001)
    assert fm.validate_inputs(a)


def test_monotonicity():
    lo = fm.evaluate(base(ownership_dilution=0.1))
    hi = fm.evaluate(base(ownership_dilution=0.6))
    assert hi["venture_exit_ownership"] < lo["venture_exit_ownership"] and hi["venture_moic"] < lo["venture_moic"]
    cheap = fm.evaluate(base(scale_vendor_monthly=6000))
    pricey = fm.evaluate(base(scale_vendor_monthly=14000))
    assert pricey["runrate_net"] < cheap["runrate_net"] and pricey["runrate_net"] < 0
    assert fm.evaluate(base(exit_arr_m=100))["venture_moic"] > fm.evaluate(base(exit_arr_m=50))["venture_moic"]
    assert fm.evaluate(base(exit_rev_multiple=8))["venture_moic"] > fm.evaluate(base(exit_rev_multiple=4))["venture_moic"]
    assert fm.evaluate(base(completion_rate=0.8))["runrate_capacity"] > fm.evaluate(base(completion_rate=0.4))["runrate_capacity"]


def test_check_equal_to_round_is_allowed():
    assert fm.evaluate(base(investor_check_m=25))["venture_initial_ownership"] == pytest.approx(25 / 105)


def test_sensitivity_uses_engine():
    z = fm.sensitivity(base(), "scale_vendor_monthly", [8000], "cash_realization", [0.5], "runrate_net")
    assert z[0][0] == pytest.approx(25776)
