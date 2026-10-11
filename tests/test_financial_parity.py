import json
import math

import pytest

from core import financial_math as fm, scenarios as sc
from core.config import AUDIT_DIR

TOL = 1e-6


def test_versions_and_scenarios_match():
    assert sc.contract()["model_version"] == sc.fixtures()["model_version"] == "2.0.0"
    assert set(sc.scenario_names()) == set(sc.fixtures()["scenarios"]) == {"Downside", "Base", "Upside"}


def test_every_fixture_key_all_scenarios_and_report():
    report, bad = {}, []
    for name in sc.scenario_names():
        exp = sc.fixtures()["scenarios"][name]
        act = fm.evaluate(sc.preset(name))
        assert set(exp) == set(act) == set(fm.OUTPUT_KEYS)
        diffs = {k: abs(act[k] - exp[k]) for k in exp}
        report[name] = {k: dict(expected=exp[k], actual=act[k], abs_diff=diffs[k], ok=diffs[k] <= TOL) for k in exp}
        bad += [f"{name}.{k}: expected {exp[k]!r} actual {act[k]!r}" for k, d in diffs.items() if d > TOL]
    AUDIT_DIR.mkdir(exist_ok=True)
    (AUDIT_DIR / "finance_parity_report.json").write_text(json.dumps(
        dict(model_version="2.0.0", tolerance=TOL, passed=not bad, mismatches=bad, scenarios=report), indent=2))
    assert not bad, "\n".join(bad)


@pytest.mark.parametrize("name,expected", [
    ("Downside", dict(pilot_net=-66635.52, runrate_net=-150384, first_year_net=-196950.40, venture_moic=0.3214285714)),
    ("Base", dict(pilot_capacity=8232, pilot_cash=4116, pilot_cost=43950, pilot_net=-39834, runrate_capacity=296352,
                  runrate_cash=148176, recurring_cost=122400, runrate_net=25776, first_year_net=-31268,
                  venture_post_money=105, venture_initial_ownership=0.019047619, venture_exit_ownership=0.012380952,
                  venture_proceeds=5.942857, venture_moic=2.971428571, venture_irr=0.199023097)),
    ("Upside", dict(pilot_net=-31610, runrate_net=347400, first_year_net=249500, venture_moic=13.5)),
])
def test_independent_hard_coded_values(name, expected):
    r = fm.evaluate(sc.preset(name))
    for k, v in expected.items():
        assert r[k] == pytest.approx(v, abs=1e-5), k


def test_monthly_table_reconciles_and_setup_once():
    a = sc.preset("Base")
    m = fm.pilot_months(a)
    r = fm.evaluate(a)
    assert sum(x["net_cash"] for x in m) == pytest.approx(r["pilot_net"], abs=TOL)
    assert [x["setup"] for x in m] == [a["pilot_setup"], 0, 0]
    assert sum(x["capacity_value"] for x in m) == pytest.approx(r["pilot_capacity"], abs=TOL)


def test_scale_detail_reconciles():
    a = sc.preset("Base")
    s, r = fm.scale_detail(a), fm.evaluate(a)
    assert s["runrate_net"] == pytest.approx(r["runrate_net"]) and s["first_year_net"] == pytest.approx(r["first_year_net"])
    assert s["vendor_cost"] + s["support_cost"] + s["audit_cost"] == pytest.approx(s["recurring_cost"])


def test_presets_not_mutated_by_edits():
    a = sc.preset("Base")
    a["cash_realization"] = 0.9
    assert sc.preset("Base")["cash_realization"] == 0.5
    assert sc.changed_keys(a, "Base") == ["cash_realization"]


def test_reverse_underwriting_and_fee_headroom():
    a = sc.preset("Base")
    assert fm.required_exit_arr_for_moic(a, 3.0) == pytest.approx(80.769, abs=1e-3)
    b = dict(a, exit_arr_m=fm.required_exit_arr_for_moic(a, 3.0))
    assert fm.evaluate(b)["venture_moic"] == pytest.approx(3.0)
    c = dict(a, exit_premoney_m=fm.max_premoney_for_moic(a, 3.0))
    assert fm.evaluate(c)["venture_moic"] == pytest.approx(3.0)
    assert fm.max_vendor_fee_for_coverage(a, 1.2) == pytest.approx(8090)
    assert fm.interpret(sc.preset("Downside"))["breakeven_feasible"] is False
