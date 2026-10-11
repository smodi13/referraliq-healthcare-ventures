"""Second, independently written implementation of the contract formulas (closed form, no shared code
with core.financial_math) used to cross-check the engine on arbitrary inputs."""


def reference(a: dict) -> dict:
    ramps = a["ramp_m1"] + a["ramp_m2"] + a["ramp_m3"]
    per_case_value = a["net_minutes_saved"] / 60 * a["loaded_hourly_cost"]
    pilot_cap = a["pilot_monthly_cases"] * a["eligible_share"] * a["completion_rate"] * ramps * per_case_value
    pilot_cost = 3 * (a["pilot_vendor_monthly"] + a["pilot_support_monthly"] + a["pilot_audit_monthly"]) + a["pilot_setup"]
    run_cap = a["scale_monthly_cases"] * 12 * a["eligible_share"] * a["completion_rate"] * per_case_value
    rec = 12 * (a["scale_vendor_monthly"] + a["scale_support_monthly"] + a["scale_audit_monthly"])
    post = a["exit_premoney_m"] + a["round_raise_m"]
    own0 = a["investor_check_m"] / post
    own1 = own0 * (1 - a["ownership_dilution"])
    eq = a["exit_arr_m"] * a["exit_rev_multiple"] * a["equity_value_factor"]
    moic = own1 * eq / a["investor_check_m"]
    return {
        "pilot_capacity": pilot_cap, "pilot_cash": pilot_cap * a["cash_realization"], "pilot_cost": pilot_cost,
        "pilot_net": pilot_cap * a["cash_realization"] - pilot_cost,
        "runrate_capacity": run_cap, "runrate_cash": run_cap * a["cash_realization"], "recurring_cost": rec,
        "runrate_net": run_cap * a["cash_realization"] - rec,
        "first_year_net": run_cap * a["cash_realization"] * a["first_year_ramp"] - rec - a["scale_rollout_setup"],
        "venture_post_money": post, "venture_initial_ownership": own0, "venture_exit_ownership": own1,
        "venture_exit_equity": eq, "venture_proceeds": own1 * eq, "venture_moic": moic,
        "venture_irr": (moic ** (1 / a["hold_years"]) - 1) if moic > 0 else -1.0,
    }
