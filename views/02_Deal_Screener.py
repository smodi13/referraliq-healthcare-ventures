import pandas as pd
import streamlit as st

from core.formatting import md
from core import charts, components as ui, content, data_loader as dl, exports, repository, scoring
from core.config import AS_OF_LABEL

ui.page_header("Deal Screener", "Twelve-company Phase 1 screen: product fit, entry and evidence")
ui.banner("Scores are directional analyst judgments on a time-stamped public-source screen, not machine learning "
          "predictions, valuations or probabilities of success. The universe is not exhaustive.")

con = ui.db()
cos = repository.companies(con)
srcs = {s["id"]: s for s in repository.sources(con)}


def row(c: dict) -> dict:
    ss = repository.company_sources(con, c["id"])
    undated = [s["id"] for s in ss if s["date_kind"] != "published"]
    gaps = []
    if "undisclosed" in c["valuation"].lower() or "not verified" in c["valuation"].lower():
        gaps.append("valuation")
    if not c["funding_event_date"]:
        gaps.append("financing date")
    if undated:
        gaps.append(f"{len(undated)} imprecise source date(s)")
    n = len(ss)
    return dict(
        Company=c["name"], Segment=c["segment"], Buyer=c["buyer"], Role=c["recommended_role"],
        Fit=c["direct_fit"], Rank=c["original_rank"], Score=c["score"],
        Strategic=c["strategic"], Workflow=c["workflow"], Pilot=c["pilot"], Defensibility=c["defensibility"],
        Entry=c["entry"], Confidence=c["confidence"],
        Financing=c["funding_event"], FinancingDate=c["funding_event_date"] or "Not stated",
        Risk=c["key_risk"], Sources=n,
        Independent=sum(1 for s in ss if dl.evidence_class(s["category"]) in ("Independent press or research", "Official or regulator")), Evidence=("Multiple sources" if n >= 3 else "Limited sources" if n == 2 else "Single source" if n == 1 else "No sources"),
        Gaps="; ".join(gaps) if gaps else "None flagged", SourceIDs=", ".join(s["id"] for s in ss))


df = pd.DataFrame([row(c) for c in cos])

# ---- optional weight sandbox ------------------------------------------------------------
with st.expander("Score methodology and what-if weights"):
    st.markdown(
        "**Phase 1 formula:** each dimension is rated 1 to 5. Score = sum(weight x rating) / 5 on a 100 point scale. "
        "Recorded weights are 25, 20, 15, 15, 15 and 10. These are analyst judgment weights, not official Intermountain weights. "
        "A score of 20 means all ratings are 1; it is not a zero probability.")
    for k, d in scoring.DEFINITIONS.items():
        st.markdown(md(f"- **{k.title()}**: {d}"))
    st.markdown(md("**How the dimensions map to the questions an investor asks (they are not interchangeable):** "
                   "product fit = workflow; strategic fit = strategic; operational feasibility = pilot; "
                   "investment attractiveness = entry (plus defensibility); data confidence = confidence. "
                   "Commercial value and financial return are not scored here; they come from the Pilot Economics and "
                   "Venture Returns models, with hypothetical inputs."))
    st.markdown(md("**What-if weights** (normalized to 100 automatically; original scores are never overwritten)"))
    st.button("Reset original weights", key="w_reset",
              on_click=lambda: [st.session_state.pop(f"w_{k}", None) for k in scoring.ORIGINAL_WEIGHTS])
    wc = st.columns(6)
    custom = {k: wc[i].number_input(k.title(), 0.0, 100.0, float(w), 5.0, key=f"w_{k}")
              for i, (k, w) in enumerate(scoring.ORIGINAL_WEIGHTS.items())}
try:
    norm = scoring.normalize_weights(custom)
    ranked = scoring.rank([dict(name=r["Company"], **{k: r[k.title()] for k in scoring.ORIGINAL_WEIGHTS}) for r in df.to_dict("records")], custom)
    wi = {r["name"]: (r["whatif_score"], r["whatif_rank"]) for r in ranked}
    df["WhatIfScore"] = df["Company"].map(lambda n: wi[n][0])
    df["WhatIfRank"] = df["Company"].map(lambda n: wi[n][1])
    modified = any(abs(custom[k] - scoring.ORIGINAL_WEIGHTS[k]) > 1e-9 for k in custom)
    if modified:
        st.caption("What-if weights in use (normalized): " + ", ".join(f"{k} {v:.1f}%" for k, v in norm.items()))
except ValueError as e:
    st.error(md(str(e)))
    df["WhatIfScore"], df["WhatIfRank"], modified = df["Score"], df["Rank"], False

# ---- filters ----------------------------------------------------------------------------
def keep(name: str, widget, label: str, *args, **kw):
    """Widget whose value survives navigating to another page and back (Streamlit drops unrendered widget state)."""
    kk, saved = f"flt_{name}", st.session_state.get(f"_keep_{name}")
    if kk not in st.session_state and saved is not None:
        st.session_state[kk] = saved
    v = widget(label, *args, key=kk, **kw)
    st.session_state[f"_keep_{name}"] = v
    return v


f = st.columns(5)
seg = keep("seg", f[0].multiselect, "Sector / segment", sorted(df["Segment"].unique()))
buyer = keep("buyer", f[1].multiselect, "Buyer", sorted(df["Buyer"].unique()))
role = keep("role", f[2].multiselect, "Analyst role", sorted(df["Role"].unique()))
fit = keep("fit", f[3].multiselect, "Direct workflow fit", ["High", "Medium"])
evid = keep("evid", f[4].multiselect, "Evidence depth", sorted(df["Evidence"].unique()))
q = keep("q", st.text_input, "Search company, capability or risk")
view = df.copy()
for col, sel in (("Segment", seg), ("Buyer", buyer), ("Role", role), ("Fit", fit), ("Evidence", evid)):
    if sel:
        view = view[view[col].isin(sel)]
if q:
    ql = q.lower()
    hay = (view["Company"] + " " + view["Segment"] + " " + view["Risk"] + " " + view["Role"]).str.lower()
    view = view[hay.str.contains(ql, regex=False)]

st.caption(md(f"{len(view)} of {len(df)} companies shown. Screen date {AS_OF_LABEL}. Financing entries are historical disclosures."))
if view.empty:
    st.warning(md("No companies match the active filters. Clear a filter or the search box to see the full screen."))
    ui.footer()
    st.stop()

cols = ["Rank", "Company", "Score", "Role", "FinancingDate", "Financing", "Evidence", "Independent", "Gaps", "Risk",
        "Strategic", "Workflow", "Pilot", "Defensibility", "Entry", "Confidence"]
if modified:
    cols = cols[:3] + ["WhatIfScore", "WhatIfRank"] + cols[3:]
sel = st.dataframe(
    view[cols], hide_index=True, width="stretch", height=(len(view) + 1) * 35 + 3, on_select="rerun", selection_mode="single-row", key="screen_tbl",
    column_config={
        "Score": st.column_config.NumberColumn("Phase 1 analyst score", format="%.0f"),
        "WhatIfScore": st.column_config.NumberColumn("What-if weighted score", format="%.1f"),
        "FinancingDate": "Financing date (historical)",
        "Independent": st.column_config.NumberColumn("Independent or official sources", help="Count of linked sources that are not company or vendor authored."),
        "Financing": "Historical financing disclosure",
    })
rows = sel.selection.rows if sel and sel.selection else []
if rows:
    name = view.iloc[rows[0]]["Company"]
    st.session_state["company"] = name
    st.success(md(f"Selected {name}."))
    st.page_link(ui.NAV_PAGES["diligence"], label=f"Open {name} dossier and sources")
else:
    st.caption(md("Select a row to open its dossier."))

# ---- chart ------------------------------------------------------------------------------
col = "WhatIfScore" if modified else "Score"
ordered = view.sort_values(col, ascending=False)
st.plotly_chart(charts.hbar(
    f"{'What-if weighted' if modified else 'Phase 1 analyst'} score (points out of 100, directional)",
    list(ordered["Company"]), list(ordered[col]), "Score (0 to 100)", text_fmt="%{x:.0f}" if not modified else "%{x:.1f}"),
    width="stretch")
st.caption("Chart description: horizontal bars of each company's score out of 100, sorted high to low. The table above lists the same values.")

sens = scoring.entry_sensitivity([dict(c) for c in cos])
by = {k: {r["name"]: r for r in v} for k, v in sens.items()}
with st.container(border=True):
    st.markdown("**Entry-rating sensitivity (not a revised official score)**")
    st.caption(md(content.SCREEN_LIMITATION))
    sil = {k: by[k]["Silna Health"] for k in by}
    st.markdown(md(
        f"Silna ranks **#{sil['original']['whatif_rank']}** on the original Phase 1 score ({sil['original']['whatif_score']:.1f}). "
        f"Holding its undisclosed-valuation entry rating at neutral drops it to **#{sil['cap']['whatif_rank']}** ({sil['cap']['whatif_score']:.1f}); "
        f"with the entry dimension removed it is **#{sil['no_entry']['whatif_rank']}** ({sil['no_entry']['whatif_score']:.1f}). "
        "Ties are ordered by name. Its position as the first equity diligence candidate is therefore a judgment about "
        "diligence priority, not a score lead."))
    srows = []
    for c in cos:
        n = c["name"]
        srows.append({"Company": n, "Original rank": by["original"][n]["whatif_rank"], "Original score": by["original"][n]["whatif_score"],
                      "Unknown valuation": "Yes" if scoring.valuation_unknown(c) else "No",
                      "Cap rank": by["cap"][n]["whatif_rank"], "Cap score": by["cap"][n]["whatif_score"],
                      "All-neutral rank": by["neutral"][n]["whatif_rank"], "All-neutral score": by["neutral"][n]["whatif_score"],
                      "No-entry rank": by["no_entry"][n]["whatif_rank"], "No-entry score": by["no_entry"][n]["whatif_score"]})
    st.dataframe(pd.DataFrame(srows).sort_values("Original rank"), hide_index=True, width="stretch")
    st.caption(md("Cap: undisclosed-valuation entry ratings above 3 are held at 3. All-neutral: every undisclosed-valuation entry rating set to 3 "
                  "(this also lifts companies the analyst rated below neutral). No-entry: entry weight set to 0 and the rest renormalized."))

with st.container(border=True):
    st.markdown(md("**Why Tennr leads product fit while Silna is the first equity diligence candidate**"))
    t = df[df.Company == "Tennr"].iloc[0]
    s = df[df.Company == "Silna Health"].iloc[0]
    st.write(
        f"Tennr scores {t.Score:.0f} with the strongest workflow and defensibility ratings, but its entry rating is {t.Entry:.0f} of 5 because of a historical "
        f"{t.Financing.split(' (')[0]} financing at a reported valuation. Silna scores {s.Score:.0f}; its {s.Entry:.0f} of 5 entry rating rests partly on an "
        "earlier stage and an undisclosed valuation, which is unknown rather than proven attractive. Product fit and equity diligence priority are "
        "different questions, and neither rating confirms an available round or an attractive price.")

st.download_button("Download filtered results (CSV)",
                   exports.to_csv(view.to_dict("records"), list(view.columns)),
                   file_name="referraliq_deal_screen_filtered.csv", mime="text/csv", key="dl_screen")
ui.footer()
