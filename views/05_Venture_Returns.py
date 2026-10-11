import pandas as pd
import streamlit as st

from core import charts, components as ui, content, exports, financial_math as fm, scenarios as sc
from core.formatting import mult, musd, pct, md

ui.page_header("Hypothetical Venture Returns", "Gross, illustrative, pre-fund-fee underwriting workbench")
ui.hypothetical_banner()
ui.banner("Entry terms, exit ARR and multiples are analyst-created. No Silna financing, valuation, revenue or check size "
          "is verified, and no company is represented as currently raising.", "info")

name = ui.scenario_selector("venture")
vals, changed = ui.scenario_inputs("venture", name, {"Entry terms": ["exit_premoney_m", "round_raise_m", "investor_check_m", "ownership_dilution"],
                                                      "Exit assumptions": ["exit_arr_m", "exit_rev_multiple", "equity_value_factor", "hold_years"]})
if changed:
    st.warning(md(f"Modified what-if inputs: {', '.join(changed)}."))
errs = fm.validate_inputs(vals)
if errs:
    for e in errs:
        st.error(md(e))
    st.stop()
r = fm.evaluate(vals)

st.caption("Entry-stage values: pre-money, round, check, dilution. Exit-stage values: ARR, multiple, equity factor, holding period. "
           "USD millions throughout.")
a = st.columns(4)
a[0].metric("Post-money", musd(r["venture_post_money"]), help="Pre-money plus round size. Hypothetical.")
a[1].metric("Initial ownership", pct(r["venture_initial_ownership"], 2), help="Check divided by post-money.")
a[2].metric("Ownership at exit", pct(r["venture_exit_ownership"], 2), help="After cumulative follow-on dilution.")
a[3].metric("Exit equity value", musd(r["venture_exit_equity"]))
b = st.columns(3)
b[0].metric("Gross exit proceeds", musd(r["venture_proceeds"], 2))
b[1].metric("Gross MOIC", mult(r["venture_moic"]))
b[2].metric("Gross IRR (annualized)", pct(r["venture_irr"]), help="Gross, illustrative, before fund fees and carry. Not a net fund IRR.")
st.caption(md("Gross IRR is a single-cash-flow annualization over the holding period and must not be read as net fund IRR."))

st.subheader("Exit sensitivity: gross MOIC")
arrs = [20, 40, 60, 80, 100, 120, 160]
mults = [3, 4, 5, 6, 7, 8, 9]
z = fm.sensitivity(vals, "exit_rev_multiple", mults, "exit_arr_m", arrs, "venture_moic")
st.plotly_chart(charts.heatmap("Gross MOIC by exit ARR and EV/ARR multiple", z, [f"{m}x" for m in mults], [f"${a_}m" for a_ in arrs],
                               "Exit EV / ARR multiple", "Exit ARR (USD millions)", ".2f", midpoint=1.0, ztitle="MOIC"),
                width="stretch")
st.caption("Chart description: grid of gross MOIC by exit ARR (rows) and EV/ARR multiple (columns); red cells are below 1.00x. Values are printed in each cell and downloadable as CSV.")
st.caption(md(f"Fixed: pre-money {musd(vals['exit_premoney_m'])}, round {musd(vals['round_raise_m'])}, check {musd(vals['investor_check_m'], 2)}, "
              f"dilution {pct(vals['ownership_dilution'], 0)}, hold {vals['hold_years']:g} years, equity factor {vals['equity_value_factor']:g}. "
              "Cells below 1.00x lose capital."))
if st.toggle("Show gross IRR grid", key="irr_grid"):
    zi = fm.sensitivity(vals, "exit_rev_multiple", mults, "exit_arr_m", arrs, "venture_irr")
    st.plotly_chart(charts.heatmap("Gross IRR by exit ARR and EV/ARR multiple", zi, [f"{m}x" for m in mults], [f"${a_}m" for a_ in arrs],
                                   "Exit EV / ARR multiple", "Exit ARR (USD millions)", ".1%", midpoint=0.0, ztitle="IRR"),
                    width="stretch")
rows = [dict(exit_arr_m=y, exit_rev_multiple=x, gross_moic=z[i][j]) for i, y in enumerate(arrs) for j, x in enumerate(mults)]
st.download_button("Download sensitivity grid (CSV, HYPOTHETICAL)", exports.to_csv(rows, ["exit_arr_m", "exit_rev_multiple", "gross_moic"]),
                   file_name="referraliq_venture_sensitivity.csv", mime="text/csv", key="dl_vc_sens")

st.subheader("Reverse underwriting against an illustrative 3.0x hurdle")
st.caption(md("The 3.0x figure is an analyst-created example. It is not an Intermountain Ventures return requirement."))
need = fm.required_exit_arr_for_moic(vals, 3.0)
cap = fm.max_premoney_for_moic(vals, 3.0)
c = st.columns(2)
c[0].metric("Exit ARR needed for 3.0x", musd(need) if need is not None else "Not calculable",
            help="Holding check, entry terms, dilution and multiple fixed. Assumes no preference waterfall.")
c[1].metric("Highest pre-money that still returns 3.0x", musd(cap) if cap is not None else "Not calculable",
            help="Holding round, dilution and exit assumptions fixed.")
st.caption(md("An analytical tool: it shows what must be true, not what will happen, and not an obtainable current round."))

st.subheader("Frozen presets side by side")
names = sc.scenario_names()
allr = {n: fm.evaluate(sc.preset(n)) for n in names}
st.dataframe(pd.DataFrame({n: {"Post-money": musd(allr[n]["venture_post_money"]), "Initial ownership": pct(allr[n]["venture_initial_ownership"], 2),
                               "Exit ownership": pct(allr[n]["venture_exit_ownership"], 2), "Exit equity value": musd(allr[n]["venture_exit_equity"]),
                               "Gross proceeds": musd(allr[n]["venture_proceeds"], 2), "Gross MOIC": mult(allr[n]["venture_moic"]),
                               "Gross IRR": pct(allr[n]["venture_irr"])} for n in names}), width="stretch")

with st.expander("Not modeled (exclusions)", expanded=True):
    for e in content.EXCLUSIONS:
        st.markdown(md(f"- {e}"))
    st.markdown("Dilution reduces ownership; valuation compression is a separate effect captured by the multiple. "
                "The memo's Silna reference is historical funding only, and cumulative capital raised is not a valuation.")
out = [dict(scenario=name, label="ILLUSTRATIVE", kind="input", metric=k_, value=v) for k_, v in vals.items() if k_ in sc.VENTURE_FIELDS] + \
      [dict(scenario=name, label="ILLUSTRATIVE", kind="output", metric=k_, value=v) for k_, v in r.items() if k_.startswith("venture_")]
st.download_button("Download assumptions and results (CSV, ILLUSTRATIVE)", exports.to_csv(out, ["scenario", "label", "kind", "metric", "value"]),
                   file_name=f"referraliq_venture_{name.lower()}.csv", mime="text/csv", key="dl_vc_scn")
ui.footer()
