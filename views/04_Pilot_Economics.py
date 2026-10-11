import pandas as pd
import streamlit as st

from core import charts, components as ui, exports, financial_math as fm, scenarios as sc
from core.formatting import mult, num, pct, usd, md

ui.page_header("Pilot ROI Simulator", "90-day pilot, steady-state run-rate and first scaled year, kept strictly separate")
ui.banner("All inputs are illustrative analyst assumptions in USD. They are not Intermountain costs, vendor quotes "
          "or observed vendor performance. Staff capacity value is not cash savings.")

name = ui.scenario_selector("pilot")
vals, changed = ui.scenario_inputs("pilot", name, sc.PILOT_FIELD_GROUPS)
if changed:
    st.warning(md(f"Modified what-if inputs ({len(changed)}): {', '.join(changed)}. These are scenario parameters, not company facts."))
else:
    st.caption(md(f"Inputs equal the frozen {name} preset (contract {sc.contract()['model_version']})."))

errs = fm.validate_inputs(vals)
if errs:
    for e in errs:
        st.error(md(e))
    st.stop()

r = fm.evaluate(vals)
months = fm.pilot_months(vals)
sd = fm.scale_detail(vals)
it = fm.interpret(vals, r)

tab_p, tab_s, tab_c = st.tabs(["90-Day Pilot", "Scaled Deployment Economics", "Scenarios and Sensitivity"])

with tab_p:
    k = st.columns(4)
    k[0].metric("Capacity value (90 days)", usd(r["pilot_capacity"]), help="Recovered staff time valued at loaded cost. Not cash.")
    k[1].metric("Cash savings (90 days)", usd(r["pilot_cash"]), help="Capacity value times cash realization.")
    k[2].metric("Pilot cost (90 days)", usd(r["pilot_cost"]), help="Three months of fees plus one-time setup.")
    k[3].metric("Pilot net cash (90 days)", usd(r["pilot_net"]))
    st.caption("A cash-negative learning pilot is a planned evidence expense, not proof the product failed. "
               "The 90-day figure is never annualized and is not added to scaled-year results.")
    tbl = pd.DataFrame([dict(
        Month=f"Month {m['month']}", **{"Adoption ramp": pct(m["ramp"], 0), "Eligible cases": num(m["eligible_cases"], 0),
        "Completed cases": num(m["completed_cases"], 1), "Hours recovered": num(m["hours_recovered"], 1),
        "Capacity value (USD)": usd(m["capacity_value"], 2), "Cash savings (USD)": usd(m["cash_savings"], 2),
        "Fees: vendor + support + audit (USD)": usd(m["recurring_cost"]), "One-time setup (USD)": usd(m["setup"]),
        "Net cash (USD)": usd(m["net_cash"], 2)}) for m in months])
    tot = dict(Month="Total", **{"Adoption ramp": "", "Eligible cases": num(sum(m["eligible_cases"] for m in months), 0),
        "Completed cases": num(sum(m["completed_cases"] for m in months), 1), "Hours recovered": num(sum(m["hours_recovered"] for m in months), 1),
        "Capacity value (USD)": usd(r["pilot_capacity"], 2), "Cash savings (USD)": usd(r["pilot_cash"], 2),
        "Fees: vendor + support + audit (USD)": usd(sum(m["recurring_cost"] for m in months)),
        "One-time setup (USD)": usd(vals["pilot_setup"]), "Net cash (USD)": usd(r["pilot_net"], 2)})
    st.dataframe(pd.concat([tbl, pd.DataFrame([tot])]), hide_index=True, width="stretch")
    fees = sum(m["recurring_cost"] for m in months)
    st.plotly_chart(charts.waterfall("90-day pilot: capacity value to net cash (USD)", [
        ("Capacity value", r["pilot_capacity"], "relative"),
        ("Not realized as cash", -(r["pilot_capacity"] - r["pilot_cash"]), "relative"),
        ("Cash savings", 0, "total"),
        ("Vendor, support, audit fees", -fees, "relative"),
        ("One-time setup", -vals["pilot_setup"], "relative"),
        ("Pilot net cash", 0, "total")]), width="stretch")
    st.caption("Chart description: waterfall from 90-day capacity value, less the part not realized as cash, less fees and one-time setup, to net cash. The table above lists the same values.")
    c1, c2 = st.columns(2)
    labels = [f"Month {m['month']}" for m in months]
    c1.plotly_chart(charts.line_ramp("Completed cases per month (cases)", labels, [m["completed_cases"] for m in months], "cases"), width="stretch")
    c2.plotly_chart(charts.grouped_bars("Monthly cash savings vs total cost (USD)", labels, {
        "Cash savings": [m["cash_savings"] for m in months], "Fees plus setup": [m["total_cost"] for m in months]}, "USD"), width="stretch")
    st.info("Recovered staff time is usually redeployed capacity. It becomes cash only through avoided hiring, overtime or "
            "contractor spend, which is why cash realization is a separate assumption. Real feasibility depends on operational, "
            "security and clinical validation.")

with tab_s:
    st.caption("Hypothetical after scaled operating deployment. Pilot and first scaled year are alternative sequential decisions; "
               "pilot fees are not assumed to be credited against rollout (contract credits are unestablished).")
    a = st.columns(4)
    a[0].metric("Annual capacity value", usd(sd["capacity_value"]), help=f"{num(sd['annual_hours_recovered'])} hours, about {sd['annual_fte_equivalent']:.1f} FTE equivalent at 2,080 hours. Reporting equivalent, not headcount.")
    a[1].metric("Annual realizable cash", usd(sd["cash_savings"]))
    a[2].metric("Annual recurring cost", usd(sd["recurring_cost"]))
    a[3].metric("Steady-state net cash (per year)", usd(sd["runrate_net"]))
    b = st.columns(4)
    b[0].metric("First-year cash savings (ramped)", usd(sd["first_year_cash_savings"]))
    b[1].metric("First-year recurring cost", usd(sd["first_year_recurring_cost"]))
    b[2].metric("First-year rollout setup", usd(sd["first_year_setup"]))
    b[3].metric("First scaled-year net cash", usd(sd["first_year_net"]))
    st.markdown(
        f"**Benefit to recurring cost:** {it['coverage_label']} &nbsp;|&nbsp; **Break-even cash realization:** "
        f"{'n/a' if it['breakeven'] is None else pct(it['breakeven'])} (current assumption {pct(vals['cash_realization'])})")
    (st.success if it["breakeven_feasible"] else st.error)(md(it["breakeven_note"]))
    mv = fm.max_vendor_fee_for_coverage(vals, 1.2)
    if mv is not None and mv <= 0:
        st.caption("No scaled vendor fee preserves 1.20x coverage at these assumptions (support and audit costs alone exceed the benefit).")
    elif mv is not None:
        st.caption(md(f"Maximum scaled monthly vendor fee that preserves 1.20x coverage: {usd(mv)} "
                      f"(assumed {usd(vals['scale_vendor_monthly'])}). The 1.20x hurdle is the memo's illustrative test."))
    x = st.columns(3)
    x[0].metric("Minutes saved per case needed for break-even", "n/a" if sd["breakeven_minutes"] is None else f"{sd['breakeven_minutes']:.1f}",
                help="Holding cash realization and volume fixed.")
    x[1].metric("Months to recover rollout setup", "No payback" if sd["rollout_payback_months"] is None else f"{sd['rollout_payback_months']:.1f}",
                help="Rollout setup divided by monthly run-rate net cash.")
    x[2].metric("FTE equivalent of hours recovered", f"{sd['annual_fte_equivalent']:.1f}", help="Reporting equivalent at 2,080 hours. Not a headcount reduction.")
    st.info("Why first-year can be negative while run-rate is positive: year one earns only the ramp share of benefits "
            "but pays full recurring cost plus one-time rollout setup.")
    st.plotly_chart(charts.waterfall("First scaled year: capacity value to net cash (USD)", [
        ("Annual capacity value", sd["capacity_value"], "relative"),
        ("Not realized as cash", -(sd["capacity_value"] - sd["cash_savings"]), "relative"),
        ("Not yet ramped", -(sd["cash_savings"] - sd["first_year_cash_savings"]), "relative"),
        ("Year-one cash savings", 0, "total"),
        ("Recurring cost", -sd["recurring_cost"], "relative"),
        ("Rollout setup", -sd["first_year_setup"], "relative"),
        ("First-year net cash", 0, "total")]), width="stretch")
    st.caption("Chart description: waterfall from annual capacity value, less the part not realized as cash, less the unramped share, recurring cost and rollout setup, to first-year net cash.")

with tab_c:
    names = sc.scenario_names()
    allr = {n: fm.evaluate(sc.preset(n)) for n in names}
    st.plotly_chart(charts.grouped_bars("Frozen presets: net cash by horizon (USD)", names, {
        "90-day pilot net": [allr[n]["pilot_net"] for n in names],
        "Annual run-rate net": [allr[n]["runrate_net"] for n in names],
        "First scaled-year net": [allr[n]["first_year_net"] for n in names]}, "USD"), width="stretch")
    st.caption("Chart description: grouped bars of 90-day net, annual run-rate net and first scaled-year net cash in USD for the Downside, Base and Upside presets.")
    st.markdown(md("**Annual run-rate net cash (USD per year): cash realization vs scaled monthly vendor fee**"))
    xs = [4000, 6000, 8000, 10000, 12000, 14000, 16000]
    ys = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    z = fm.sensitivity(vals, "scale_vendor_monthly", xs, "cash_realization", ys, "runrate_net")
    st.plotly_chart(charts.heatmap("Run-rate net cash, USD per year", z, [usd(x) for x in xs], [pct(y, 0) for y in ys],
                                   "Scaled vendor fee (USD per month)", "Cash realization", ",.0f", midpoint=0, ztitle="USD/yr"),
                    width="stretch")
    st.caption(md("Other inputs held at the values above. Zero is operating break-even."))
    grid = pd.DataFrame(z, index=[pct(y, 0) for y in ys], columns=[usd(x) for x in xs])
    rows = [dict(cash_realization=y, scale_vendor_monthly=x, runrate_net_usd=z[i][j]) for i, y in enumerate(ys) for j, x in enumerate(xs)]
    st.download_button("Download sensitivity grid (CSV)", exports.to_csv(rows, ["cash_realization", "scale_vendor_monthly", "runrate_net_usd"]),
                       file_name="referraliq_pilot_sensitivity.csv", mime="text/csv", key="dl_pilot_sens")
    out = [dict(scenario=name, kind="input", metric=k_, value=v) for k_, v in vals.items()] + \
          [dict(scenario=name, kind="output", metric=k_, value=v) for k_, v in r.items()]
    st.download_button("Download scenario inputs and outputs (CSV)", exports.to_csv(out, ["scenario", "kind", "metric", "value"]),
                       file_name=f"referraliq_pilot_{name.lower()}.csv", mime="text/csv", key="dl_pilot_scn")
st.caption(md("Model workbook for cross-checking: Pilot_ROI_and_Venture_Model.xlsx (download from the Investment Overview page)."))
ui.footer()
