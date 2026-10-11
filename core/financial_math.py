"""Contract-exact ReferralIQ finance engine (model contract 2.0.0).

Pure functions, no Streamlit imports. Units: pilot and scale money in USD, venture money in
USD millions, rates as decimal fractions in [0, 1]. All inputs are analyst-created
hypothetical assumptions, never reported company or Intermountain financials.
"""
from __future__ import annotations

import math
from typing import Mapping

REQUIRED_KEYS = [
    "pilot_monthly_cases", "scale_monthly_cases", "eligible_share", "completion_rate",
    "net_minutes_saved", "loaded_hourly_cost", "cash_realization", "pilot_vendor_monthly",
    "scale_vendor_monthly", "scale_support_monthly", "scale_audit_monthly",
    "pilot_support_monthly", "pilot_audit_monthly", "pilot_setup", "scale_rollout_setup",
    "first_year_ramp", "ramp_m1", "ramp_m2", "ramp_m3", "exit_premoney_m", "round_raise_m",
    "investor_check_m", "exit_arr_m", "exit_rev_multiple", "ownership_dilution", "hold_years",
    "equity_value_factor",
]
FRACTION_KEYS = [
    "eligible_share", "completion_rate", "cash_realization", "first_year_ramp", "ramp_m1",
    "ramp_m2", "ramp_m3", "ownership_dilution", "equity_value_factor",
]
OUTPUT_KEYS = [
    "pilot_capacity", "pilot_cash", "pilot_cost", "pilot_net", "runrate_capacity", "runrate_cash",
    "recurring_cost", "runrate_net", "runrate_coverage", "first_year_net",
    "breakeven_cash_realization", "venture_post_money", "venture_initial_ownership",
    "venture_exit_ownership", "venture_exit_equity", "venture_proceeds", "venture_moic",
    "venture_irr",
]


def validate_inputs(a: Mapping) -> list[str]:
    """Return human-readable problems; an empty list means the inputs are calculable."""
    errs: list[str] = []
    for k in REQUIRED_KEYS:
        v = a.get(k)
        if k not in a:
            errs.append(f"Missing input: {k}")
        elif isinstance(v, bool) or not isinstance(v, (int, float)):
            errs.append(f"{k} must be a number")
        elif not math.isfinite(v):
            errs.append(f"{k} must be finite")
        elif v < 0:
            errs.append(f"{k} cannot be negative")
        elif k in FRACTION_KEYS and v > 1:
            errs.append(f"{k} must be between 0 and 100 percent (0 to 1)")
    if errs:
        return errs
    if a["investor_check_m"] <= 0:
        errs.append("investor_check_m must be positive")
    if a["hold_years"] <= 0:
        errs.append("hold_years must be positive")
    if a["exit_premoney_m"] + a["round_raise_m"] <= 0:
        errs.append("Post-money valuation (pre-money + round) must be positive")
    if a["investor_check_m"] > a["round_raise_m"]:
        errs.append("Investor check cannot exceed the total round size")
    return errs


def _check(a: Mapping) -> None:
    errs = validate_inputs(a)
    if errs:
        raise ValueError("; ".join(errs))


def pilot_months(a: Mapping) -> list[dict]:
    """Month-by-month 90-day pilot table. Setup is charged once, in month 1."""
    _check(a)
    fee = a["pilot_vendor_monthly"] + a["pilot_support_monthly"] + a["pilot_audit_monthly"]
    rows = []
    for i, k in enumerate(("ramp_m1", "ramp_m2", "ramp_m3"), start=1):
        eligible = a["pilot_monthly_cases"] * a["eligible_share"]
        completed = eligible * a["completion_rate"] * a[k]
        hours = completed * a["net_minutes_saved"] / 60
        capacity = hours * a["loaded_hourly_cost"]
        cash = capacity * a["cash_realization"]
        setup = a["pilot_setup"] if i == 1 else 0.0
        rows.append(dict(
            month=i, ramp=a[k], eligible_cases=eligible, completed_cases=completed,
            hours_recovered=hours, capacity_value=capacity, cash_savings=cash,
            vendor_fee=a["pilot_vendor_monthly"], support_fee=a["pilot_support_monthly"],
            audit_fee=a["pilot_audit_monthly"], recurring_cost=fee, setup=setup,
            total_cost=fee + setup, net_cash=cash - fee - setup,
        ))
    return rows


def scale_detail(a: Mapping) -> dict:
    """Annual steady-state and first-scaled-year line items (USD)."""
    _check(a)
    requests = a["scale_monthly_cases"] * 12
    completed = requests * a["eligible_share"] * a["completion_rate"]
    hours = completed * a["net_minutes_saved"] / 60
    capacity = hours * a["loaded_hourly_cost"]
    cash = capacity * a["cash_realization"]
    vendor = 12 * a["scale_vendor_monthly"]
    support = 12 * a["scale_support_monthly"]
    audit = 12 * a["scale_audit_monthly"]
    recurring = 12 * (a["scale_vendor_monthly"] + a["scale_support_monthly"] + a["scale_audit_monthly"])
    fy_cash = cash * a["first_year_ramp"]
    per_min = capacity / a["net_minutes_saved"] if a["net_minutes_saved"] else 0.0
    cash_per_min = per_min * a["cash_realization"]
    return dict(
        breakeven_minutes=(recurring / cash_per_min) if cash_per_min else None,
        rollout_payback_months=(a["scale_rollout_setup"] / ((cash - recurring) / 12)) if cash - recurring > 0 else None,
        annual_requests=requests, annual_completed_cases=completed, annual_hours_recovered=hours,
        annual_fte_equivalent=hours / 2080, capacity_value=capacity, cash_savings=cash,
        vendor_cost=vendor, support_cost=support, audit_cost=audit, recurring_cost=recurring,
        runrate_net=cash - recurring, first_year_cash_savings=fy_cash,
        first_year_recurring_cost=recurring, first_year_setup=a["scale_rollout_setup"],
        first_year_net=fy_cash - recurring - a["scale_rollout_setup"],
    )


def evaluate(a: Mapping) -> dict[str, float]:
    """Return exactly the 18 fixture keys. Mirrors the contract formulas and the QA oracle."""
    _check(a)
    months = pilot_months(a)
    s = scale_detail(a)
    pilot_capacity = sum(m["capacity_value"] for m in months)
    pilot_cash = sum(m["cash_savings"] for m in months)
    pilot_cost = 3 * (a["pilot_vendor_monthly"] + a["pilot_support_monthly"] + a["pilot_audit_monthly"]) + a["pilot_setup"]
    post = a["exit_premoney_m"] + a["round_raise_m"]
    own0 = a["investor_check_m"] / post
    own1 = own0 * (1 - a["ownership_dilution"])
    exit_equity = a["exit_arr_m"] * a["exit_rev_multiple"] * a["equity_value_factor"]
    proceeds = own1 * exit_equity
    moic = proceeds / a["investor_check_m"]
    irr = moic ** (1 / a["hold_years"]) - 1 if moic > 0 else -1.0
    rec = s["recurring_cost"]
    cap = s["capacity_value"]
    out = {
        "pilot_capacity": pilot_capacity, "pilot_cash": pilot_cash, "pilot_cost": pilot_cost,
        "pilot_net": pilot_cash - pilot_cost,
        "runrate_capacity": cap, "runrate_cash": s["cash_savings"], "recurring_cost": rec,
        "runrate_net": s["runrate_net"],
        "runrate_coverage": s["cash_savings"] / rec if rec else 0,
        "first_year_net": s["first_year_net"],
        "breakeven_cash_realization": rec / cap if cap else 0,
        "venture_post_money": post, "venture_initial_ownership": own0,
        "venture_exit_ownership": own1, "venture_exit_equity": exit_equity,
        "venture_proceeds": proceeds, "venture_moic": moic, "venture_irr": irr,
    }
    bad = [k for k, v in out.items() if not math.isfinite(v)]
    if bad:  # e.g. absurdly large inputs overflow to infinity; never show that as a result
        raise ValueError("Inputs are too large to compute a finite result (" + ", ".join(bad) + ")")
    return out


def interpret(a: Mapping, r: Mapping | None = None) -> dict:
    """UI-facing labels for ratios the oracle reports as 0 when the denominator is 0."""
    r = r or evaluate(a)
    s = scale_detail(a)
    be = None if s["capacity_value"] == 0 else r["breakeven_cash_realization"]
    return dict(
        coverage=None if s["recurring_cost"] == 0 else r["runrate_coverage"],
        coverage_label="No recurring cost modeled" if s["recurring_cost"] == 0 else f"{r['runrate_coverage']:.2f}x",
        breakeven=be,
        breakeven_feasible=be is not None and be <= 1,
        breakeven_note=(
            "Not calculable: zero capacity value." if be is None else
            "Break-even needs more than 100% cash realization, which is unachievable under these assumptions."
            if be > 1 else "Break-even is within the achievable 0 to 100% range."),
    )


def max_vendor_fee_for_coverage(a: Mapping, target: float = 1.2) -> float | None:
    """Highest scaled monthly vendor fee that still gives `target`x benefit to recurring cost."""
    s = scale_detail(a)
    if target <= 0:
        return None
    return s["cash_savings"] / target / 12 - a["scale_support_monthly"] - a["scale_audit_monthly"]


def required_exit_arr_for_moic(a: Mapping, target_moic: float = 3.0) -> float | None:
    """Exit ARR (USD m) needed for `target_moic` holding every other input fixed, or None."""
    _check(a)
    own1 = a["investor_check_m"] / (a["exit_premoney_m"] + a["round_raise_m"]) * (1 - a["ownership_dilution"])
    denom = own1 * a["exit_rev_multiple"] * a["equity_value_factor"]
    if denom <= 0 or target_moic <= 0:
        return None
    return target_moic * a["investor_check_m"] / denom


def max_premoney_for_moic(a: Mapping, target_moic: float = 3.0) -> float | None:
    """Highest entry pre-money (USD m) that still reaches `target_moic`, or None if impossible."""
    _check(a)
    exit_equity = a["exit_arr_m"] * a["exit_rev_multiple"] * a["equity_value_factor"]
    keep = 1 - a["ownership_dilution"]
    if target_moic <= 0 or exit_equity <= 0 or keep <= 0:
        return None
    post = exit_equity * keep / target_moic  # moic = keep * exit_equity / post
    pre = post - a["round_raise_m"]
    return pre if pre > 0 else None


def sensitivity(a: Mapping, x_key: str, x_vals, y_key: str, y_vals, output: str) -> list[list[float]]:
    """Grid of `output` for every (y, x) pair, each cell computed by the shared engine."""
    grid = []
    for y in y_vals:
        row = []
        for x in x_vals:
            b = dict(a)
            b[x_key] = x
            b[y_key] = y
            row.append(evaluate(b)[output])
        grid.append(row)
    return grid
