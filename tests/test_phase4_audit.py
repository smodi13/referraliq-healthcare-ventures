import random

import pytest

from core import config, financial_math as fm, repository as repo, scenarios as sc
from tests.independent_model import reference


def random_inputs(rng):
    a = sc.preset(rng.choice(sc.scenario_names()))
    for k in rng.sample(list(a), 8):
        if k in fm.FRACTION_KEYS:
            a[k] = rng.random()
        elif k == "hold_years":
            a[k] = rng.uniform(1, 12)
        elif k == "investor_check_m":
            a[k] = rng.uniform(0.1, a["round_raise_m"])
        elif k == "round_raise_m":
            a[k] = max(a["investor_check_m"], rng.uniform(1, 100))
        else:
            a[k] = a[k] * rng.uniform(0, 3)
    a["investor_check_m"] = min(a["investor_check_m"], a["round_raise_m"])
    return a


def test_engine_matches_independent_model_on_random_sequences():
    rng = random.Random(20261010)
    worst = 0.0
    for _ in range(1000):
        a = random_inputs(rng)
        got, exp = fm.evaluate(a), reference(a)
        for k, v in exp.items():
            worst = max(worst, abs(got[k] - v) / max(1.0, abs(v)))
    assert worst < 1e-9


def test_sequential_edits_are_order_independent():
    a = sc.preset("Base")
    b = dict(a)
    for k, v in (("completion_rate", 0.3), ("scale_vendor_monthly", 11000.0), ("exit_arr_m", 50.0)):
        b[k] = v
    c = dict(a)
    for k, v in reversed((("completion_rate", 0.3), ("scale_vendor_monthly", 11000.0), ("exit_arr_m", 50.0))):
        c[k] = v
    assert fm.evaluate(b) == fm.evaluate(c)
    assert fm.evaluate(sc.preset("Base"))["pilot_net"] == pytest.approx(-39834)  # presets untouched


@pytest.mark.parametrize("patch", [dict(pilot_monthly_cases=1e308), dict(loaded_hourly_cost=1e308, scale_monthly_cases=1e300)])
def test_extremely_large_inputs_never_return_infinity(patch):
    a = sc.preset("Base")
    a.update(patch)
    with pytest.raises(ValueError):
        fm.evaluate(a)


def test_full_dilution_and_zero_everything():
    r = fm.evaluate(dict(sc.preset("Base"), ownership_dilution=1.0))
    assert r["venture_exit_ownership"] == 0 and r["venture_moic"] == 0 and r["venture_irr"] == -1
    z = dict(sc.preset("Base"), pilot_monthly_cases=0, scale_monthly_cases=0, exit_arr_m=0)
    r = fm.evaluate(z)
    assert r["runrate_net"] == -r["recurring_cost"]


def test_very_high_vendor_cost_is_loss_not_error():
    r = fm.evaluate(dict(sc.preset("Base"), scale_vendor_monthly=1e7))
    assert r["runrate_net"] < 0 and fm.interpret(dict(sc.preset("Base"), scale_vendor_monthly=1e7))["breakeven_feasible"] is False


def test_workbook_extra_metrics_reconcile():
    # values taken from the LibreOffice-recalculated original workbook (SCALE ECONOMICS, VENTURE RETURNS)
    exp = {"Downside": (-2260, 40.6432748538012, 280), "Base": (8090, 5.78231292517007, 80.7692307692308),
           "Upside": (31200, 2.85185185185185, 35.5555555555556)}
    for n, (fee, minutes, arr) in exp.items():
        a = sc.preset(n)
        assert fm.max_vendor_fee_for_coverage(a, 1.2) == pytest.approx(fee, abs=1e-6)
        assert fm.scale_detail(a)["breakeven_minutes"] == pytest.approx(minutes, abs=1e-9)
        assert fm.required_exit_arr_for_moic(a, 3.0) == pytest.approx(arr, abs=1e-9)


# ---- read-only enforcement ---------------------------------------------------------------
@pytest.fixture
def con(tmp_path):
    c = repo.connect(tmp_path / "ro.db")
    repo.seed(c)
    yield c
    c.close()


def test_read_only_blocks_every_write(con, monkeypatch):
    repo.add_note(con, "company", "1", "private local note")
    repo.set_gate_status(con, "G01", "In Progress", "x", [])
    repo.add_decision(con, "Monitor", "why")
    monkeypatch.setenv("REFERRALIQ_READONLY", "1")
    assert config.is_read_only()
    with pytest.raises(repo.ReadOnlyError):
        repo.add_note(con, "company", "1", "x")
    with pytest.raises(repo.ReadOnlyError):
        repo.set_gate_status(con, "G01", "Pass", "x", ["S31"])
    with pytest.raises(repo.ReadOnlyError):
        repo.set_flag(con, "S31", True)
    with pytest.raises(repo.ReadOnlyError):
        repo.add_decision(con, "Pass", "x")


def test_read_only_hides_local_analyst_data(con, monkeypatch):
    repo.add_note(con, "company", "1", "private local note")
    repo.set_gate_status(con, "G01", "Fail", "x", [])
    repo.add_decision(con, "Pass", "private rationale")
    monkeypatch.setenv("REFERRALIQ_READONLY", "1")
    assert repo.notes(con) == [] and repo.decisions(con) == [] and repo.gate_history(con) == [] and repo.flags(con) == {}
    assert {g["status"] for g in repo.gates(con)} == {"Unknown"}
    assert len(repo.companies(con)) == 12 and len(repo.sources(con)) == 36  # canonical data still readable


def test_read_only_does_not_block_canonical_seed(tmp_path, monkeypatch):
    monkeypatch.setenv("REFERRALIQ_READONLY", "1")
    c = repo.connect(tmp_path / "fresh.db")
    repo.seed(c)
    assert len(repo.companies(c)) == 12


def test_unwritable_db_dir_falls_back_to_temp(monkeypatch, tmp_path):
    import pathlib
    real_mkdir = pathlib.Path.mkdir

    def boom(self, *a, **k):
        if "blocked" in str(self):
            raise PermissionError("nope")
        return real_mkdir(self, *a, **k)
    monkeypatch.setattr(pathlib.Path, "mkdir", boom)
    c = repo.connect(tmp_path / "blocked" / "x.db")
    c.execute("SELECT 1")
