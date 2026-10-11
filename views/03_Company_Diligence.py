import html
import pandas as pd
import streamlit as st

from core.formatting import md
from core import charts, components as ui, content, data_loader as dl, repository, scoring

ui.page_header("Company Due Diligence", "Source-linked dossier: what is known, what is not, and what to ask next")

con = ui.db()
cos = repository.companies(con)
names = [c["name"] for c in cos]
want = ui.selected_company(names)
if st.session_state.get("_company_pushed") != want:  # selection arrived from another page
    st.session_state["company_select"] = want
name = st.selectbox("Company", names, key="company_select")
st.session_state["company"] = st.session_state["_company_pushed"] = name
c = next(x for x in cos if x["name"] == name)
srcs = repository.company_sources(con, c["id"])
flags = repository.flags(con)

st.header(name)
m = st.columns(3)
m[0].markdown(md(f"**Segment**  \n{c['segment']}"))
m[1].markdown(md(f"**Buyer**  \n{c['buyer']}"))
m[2].markdown(md(f"**Use case**  \n{c['use_case']}"))
st.markdown(f'<span class="riq-tag">{html.escape(c["recommended_role"])}</span><span class="riq-tag">Direct fit: {html.escape(c["direct_fit"])}</span>',
            unsafe_allow_html=True)

tab_over, tab_fund, tab_score, tab_src, tab_unknown, tab_notes = st.tabs(
    ["Overview and risks", "Funding history", "Screening score", "Evidence", "What remains unknown", "Analyst notes"])

with tab_over:
    a, b = st.columns(2)
    with a:
        st.markdown(md("**Business overview and product capabilities**"))
        st.write(md(c["capabilities"]))
        st.caption("Capability descriptions come from the Phase 1 screen and vendor-published material. "
                   "They are not independently validated performance results.")
        st.markdown(md("**Strategic alignment with Intermountain**"))
        st.write(f"Strategic fit rated {c['strategic']:.0f} of 5. Analyst role: {c['recommended_role']}. "
                 "Alignment is an analyst judgment from public information; it does not imply Intermountain interest, "
                 "permission to pilot, or an existing relationship (the single exception is the historical Notable announcement, described on the Notable dossier).")
    with b:
        st.markdown(md("**Primary risk (as recorded in the screen)**"))
        st.write(md(c["key_risk"]))
        st.markdown(md("**Financing commentary**"))
        st.write(md(c["financing_comment"]))
        st.markdown(md("**Analyst recommendation**"))
        st.write(md(f"{c['recommended_role']} (Phase 1 score {c['score']:.0f} of 100, rank {c['original_rank']} of {len(cos)})."))
    if name == "Notable":
        st.warning(md(content.NOTABLE_NOTE))
        st.info(md("**Standing question:** " + content.STANDING_QUESTION))
    st.markdown(md("**Market positioning and competitors**"))
    st.caption(md("Shortlist comparison from the Phase 2 workbook (COMPETITIVE CHECK). Contracts and live financing are unverified."))
    comp = pd.DataFrame(dl.workbook_competitive_check())
    comp = comp[["Option", "Strategic role", "Public anchor", "Central challenge", "Decision status", "Source IDs"]]
    st.dataframe(comp, hide_index=True, width="stretch")
    others = [x["name"] for x in cos if x["segment"] == c["segment"] and x["name"] != name]
    st.caption(md("Other screened companies in the same segment label: " + (", ".join(others) if others else "none in this screen") + "."))

with tab_fund:
    st.markdown(md("**Historical financing disclosure (dated, sourced)**"))
    f = st.columns(3)
    f[0].metric("Reported stage", c["public_stage"])
    f[1].metric("Disclosure date", c["funding_event_date"] or "Not stated")
    f[2].metric("Valuation disclosure", c["valuation"].split(" (")[0] if "reported" in c["valuation"].lower() else "Not verified")
    st.write(md(c["funding_event"]))
    st.write(md(c["valuation"] if "reported" in c["valuation"].lower() else "Valuation: not verified (undisclosed in the sources reviewed)."))
    ui.banner(f"Historical snapshot only. Current private valuation: Not verified. Current fundraising availability: "
              "Not verified. A past financing announcement does not mean the company is raising now, and cumulative "
              "capital raised is not a valuation.")
    fs = [s for s in srcs if s["id"] in dl.split_ids(c["source_ids_raw"])]
    if fs:
        st.dataframe(pd.DataFrame([dict(Source=s["id"], Publisher=s["publisher"], Date=s["date_raw"], Type=s["category"], Claim=s["claim"], URL=s["url"]) for s in fs]),
                     hide_index=True, width="stretch", column_config={"URL": ui.link_cell_config()})

with tab_score:
    dims = list(scoring.ORIGINAL_WEIGHTS)
    vals = [c[d] for d in dims]
    st.plotly_chart(charts.hbar("Phase 1 dimension ratings (1 to 5)", [f"{d.title()} (weight {scoring.ORIGINAL_WEIGHTS[d]:.0f})" for d in dims],
                                vals, "Rating (1 to 5)", text_fmt="%{x:.0f}"), width="stretch")
    hi = max(dims, key=lambda d: c[d]); lo = min(dims, key=lambda d: c[d])
    st.write(f"Highest rated dimension: **{hi}** ({c[hi]:.0f}). Lowest rated: **{lo}** ({c[lo]:.0f}). "
             f"Weighted score {scoring.score(c):.0f} of 100. {scoring.DEFINITIONS[lo]}")
    st.caption(md("Ordinal analyst ratings, not a valuation or probability."))

with tab_src:
    st.caption(md("Links come from the Phase 1 screen; entries marked 'workbook COMPETITIVE CHECK' are memo-cited additions."))
    if not srcs:
        st.info(md("No sources are linked to this company."))
    for s in srcs:
        flagged = s["id"] in flags
        with st.expander(f"{s['id']} | {s['publisher']} | {s['date_raw']}" + ("  [flagged for verification]" if flagged else "")):
            st.markdown(md(f"**Claim:** {s['claim']}"))
            st.markdown(md(f"**Classification:** {s['category']} ({dl.evidence_class(s['category'])})  |  **Date status:** {s['date_note']}"))
            st.markdown(md(f"**Limitations:** {s['limitations']}"))
            st.markdown(md(f"[Open source]({s['url']})  (link provided in the register; not re-checked by this app)"))
            if s["date_kind"] != "published":
                st.caption(md("Warning: no precise publication date. The access date is not the publication date."))
            if "Company" in s["category"] or "Vendor" in s["category"]:
                st.caption(md("Vendor or company-authored: a marketing or announcement claim, not an independent measurement."))
            if not ui.read_only():
                chk = st.checkbox("Requires verification", value=flagged, key=f"flag_{s['id']}_{c['id']}")
                if chk != flagged:
                    repository.set_flag(con, s["id"], chk)
                    st.rerun()
    n_imprecise = sum(1 for s in srcs if s["date_kind"] != "published")
    n_vendor = sum(1 for s in srcs if dl.evidence_class(s["category"]) == "Vendor or company authored")
    q = st.columns(3)
    q[0].metric("Linked sources", len(srcs))
    q[1].metric("Vendor or company authored", n_vendor, help="Marketing or announcement claims, not independent measurements.")
    q[2].metric("Imprecise or missing dates", n_imprecise)
    if srcs and n_vendor == len(srcs):
        st.warning("Every linked source is vendor or company authored. Independent corroboration is needed.")

with tab_unknown:
    st.markdown(md("**Not verified for any screened company**"))
    for u in content.UNKNOWNS:
        st.markdown(md(f"- {u}: Unknown"))
    st.caption(md("Unknown is not a negative finding. These items require primary diligence."))

with tab_notes:
    notes = repository.notes(con, "company", str(c["id"]))
    if ui.read_only():
        st.caption(md("Read-only showcase mode: notes cannot be added."))
    else:
        with st.form("note_form", clear_on_submit=True):
            body = st.text_area("Add an analyst note (public, non-PHI information only)")
            if st.form_submit_button("Save note"):
                try:
                    repository.add_note(con, "company", str(c["id"]), body)
                    st.success(md("Note saved locally."))
                    st.rerun()
                except ValueError as e:
                    st.error(md(str(e)))
    if not notes:
        st.info(md("No analyst notes yet. Notes are stored locally in SQLite, separate from the original research facts."))
    for n in notes:
        st.markdown(md(f"**{n['author']}**, {n['created_at']}"))
        st.text(n["body"])
    st.caption(md("Local SQLite is a demo store, not a secure enterprise CRM."))
ui.footer()
