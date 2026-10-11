"""Frozen scenario presets from model_contract.json. Presets are never mutated."""
from __future__ import annotations

import copy
import json
from functools import lru_cache

from .config import CONTRACT_JSON, FIXTURES_JSON


@lru_cache(maxsize=1)
def _contract() -> dict:
    return json.loads(CONTRACT_JSON.read_text(encoding="utf-8"))


def contract() -> dict:
    return copy.deepcopy(_contract())


def scenario_names() -> list[str]:
    return list(_contract()["scenario_names"])


def preset(name: str) -> dict[str, float]:
    """Defensive copy of one frozen preset; also the reset function."""
    return copy.deepcopy(_contract()["scenarios"][name])


def fixtures() -> dict:
    return json.loads(FIXTURES_JSON.read_text(encoding="utf-8"))


def changed_keys(inputs: dict, name: str) -> list[str]:
    base = _contract()["scenarios"][name]
    return [k for k, v in inputs.items() if k in base and v != base[k]]


# Field metadata for UI controls: label, unit, kind (usd/pct/num/int/musd), tooltip.
FIELDS: dict[str, dict] = {
    "pilot_monthly_cases": dict(label="Pilot cases per month", unit="cases", kind="int", step=100,
        tip="Referral or authorization requests entering the pilot workflow each month, before eligibility screening."),
    "scale_monthly_cases": dict(label="Scaled cases per month", unit="cases", kind="int", step=500,
        tip="Monthly request volume after full rollout, before eligibility screening."),
    "eligible_share": dict(label="Eligible share", unit="% of cases", kind="pct",
        tip="Share of requests the product can address at all. Distinct from how many it completes."),
    "completion_rate": dict(label="Automation completion rate", unit="% of eligible", kind="pct",
        tip="Share of eligible cases completed without manual rework. Applies to eligible cases only."),
    "net_minutes_saved": dict(label="Net minutes saved per completed case", unit="minutes", kind="num", step=0.5,
        tip="Staff minutes recovered per completed case after review and exception handling."),
    "loaded_hourly_cost": dict(label="Loaded hourly labor cost", unit="USD per hour", kind="usd", step=1.0,
        tip="Wage plus benefits proxy used to value recovered staff time."),
    "cash_realization": dict(label="Cash realization", unit="% of capacity value", kind="pct",
        tip="Portion of recovered staff capacity assumed to become real cash (avoided hiring, overtime, contractors). Not the automation rate."),
    "pilot_vendor_monthly": dict(label="Pilot vendor fee", unit="USD per month", kind="usd", step=250.0, tip="Illustrative vendor subscription during the pilot."),
    "pilot_support_monthly": dict(label="Pilot support and oversight", unit="USD per month", kind="usd", step=100.0, tip="Internal support and clinical oversight cost during the pilot."),
    "pilot_audit_monthly": dict(label="Pilot audit and QA", unit="USD per month", kind="usd", step=50.0, tip="Sampling and audit cost during the pilot."),
    "pilot_setup": dict(label="Pilot setup (one time, month 1)", unit="USD", kind="usd", step=1000.0, tip="Charged once in month 1 only."),
    "scale_vendor_monthly": dict(label="Scaled vendor fee", unit="USD per month", kind="usd", step=250.0, tip="Illustrative recurring vendor fee at scale."),
    "scale_support_monthly": dict(label="Scaled support and oversight", unit="USD per month", kind="usd", step=100.0, tip="Recurring internal support cost at scale."),
    "scale_audit_monthly": dict(label="Scaled audit and QA", unit="USD per month", kind="usd", step=50.0, tip="Recurring audit cost at scale."),
    "scale_rollout_setup": dict(label="Scaled rollout setup (one time)", unit="USD", kind="usd", step=1000.0,
        tip="Incremental implementation cost in the first scaled year. Pilot setup is not credited here (no contract reconciliation)."),
    "first_year_ramp": dict(label="First scaled year ramp", unit="% of run-rate benefit", kind="pct", tip="Share of full run-rate cash benefit achieved in year one. Recurring costs are charged in full."),
    "ramp_m1": dict(label="Adoption ramp, month 1", unit="% of full", kind="pct", tip="Month 1 adoption multiplier."),
    "ramp_m2": dict(label="Adoption ramp, month 2", unit="% of full", kind="pct", tip="Month 2 adoption multiplier."),
    "ramp_m3": dict(label="Adoption ramp, month 3", unit="% of full", kind="pct", tip="Month 3 adoption multiplier."),
    "exit_premoney_m": dict(label="Pre-money valuation (contract key exit_premoney_m)", unit="USD millions", kind="musd", step=5.0,
        tip="HYPOTHETICAL entry pre-money valuation. The contract key name says 'exit' for legacy reasons; it is the entry pre-money."),
    "round_raise_m": dict(label="Round size", unit="USD millions", kind="musd", step=1.0, tip="HYPOTHETICAL total primary raise."),
    "investor_check_m": dict(label="Investor check", unit="USD millions", kind="musd", step=0.25, tip="HYPOTHETICAL check. Must be positive and no larger than the round."),
    "exit_arr_m": dict(label="Exit ARR", unit="USD millions", kind="musd", step=5.0, tip="HYPOTHETICAL annual recurring revenue at exit. Not a verified company metric."),
    "exit_rev_multiple": dict(label="Exit EV / ARR multiple", unit="x", kind="num", step=0.5, tip="Sensitivity lever, not an empirical comparable median."),
    "equity_value_factor": dict(label="Enterprise to equity factor", unit="x (0 to 1)", kind="num", step=0.05, tip="Share of enterprise value reaching equity holders. 1.0 means no debt or preference drag."),
    "ownership_dilution": dict(label="Follow-on dilution", unit="% cumulative", kind="pct", tip="Cumulative ownership dilution from later rounds and option pool."),
    "hold_years": dict(label="Holding period", unit="years", kind="num", step=0.5, tip="Years from entry to exit, used for gross IRR."),
}

PILOT_FIELD_GROUPS = {
    "Volume and Eligibility": ["pilot_monthly_cases", "scale_monthly_cases", "eligible_share", "completion_rate"],
    "Productivity": ["net_minutes_saved", "loaded_hourly_cost"],
    "Realization": ["cash_realization"],
    "Adoption Ramp": ["ramp_m1", "ramp_m2", "ramp_m3", "first_year_ramp"],
    "Vendor Fees": ["pilot_vendor_monthly", "scale_vendor_monthly"],
    "Support and Audit": ["pilot_support_monthly", "pilot_audit_monthly", "scale_support_monthly", "scale_audit_monthly"],
    "Setup and Rollout": ["pilot_setup", "scale_rollout_setup"],
}
VENTURE_FIELDS = ["exit_premoney_m", "round_raise_m", "investor_check_m", "ownership_dilution",
                  "exit_arr_m", "exit_rev_multiple", "equity_value_factor", "hold_years"]
