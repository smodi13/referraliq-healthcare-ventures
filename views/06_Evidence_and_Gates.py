import json

import pandas as pd
import streamlit as st

from core.formatting import md
from core import components as ui, config, content, data_loader as dl, exports, repository

ui.page_header("Evidence and Investment Gates", "Source registry, evidence quality and the ten decision gates")

con = ui.db()
srcs = repository.sources(con)
cmap = repository.source_company_map(con)
srcs_by_id = {s['id']: s for s in srcs}
flags = repository.flags(con)
gates = repository.gates(con)
audit = repository.last_audit(con)

tab_e, tab_g = st.tabs(["Evidence Registry", "Diligence Gates"])

with tab_e:
    chk_file = config.AUDIT_DIR / "source_http_check.json"
    chk, chk_date = {}, ""
    if chk_file.exists():
        raw = json.loads(chk_file.read_text())
        chk = {r["id"]: ("Reachable" if r["status"] and 200 <= r["status"] < 300 else f"HTTP {r['status']} (not verified)" if r["status"] else "Network error")
               for r in raw["results"]}
        chk_date = raw["checked_at"][:10]
    rev_file = config.AUDIT_DIR / "source_review.json"
    rev = {r["id"]: r for r in json.loads(rev_file.read_text())["sources"]} if rev_file.exists() else {}
    df = pd.DataFrame([dict(
        ID=s["id"], Publisher=s["publisher"], Date=s["date_raw"], Type=s["category"], Authorship=dl.evidence_class(s["category"]),
        Companies=", ".join(cmap.get(s["id"], [])) or "Context only", Claim=s["claim"],
        LinkCheck=chk.get(s["id"], "Not checked"),
        ReviewedClaimSupport=rev.get(s["id"], {}).get("supports_claim", "Not reviewed"),
        EvidenceClass=rev.get(s["id"], {}).get("evidence_class", ""),
        CitationCorrected="Yes" if s.get("correction_note") else "", Limitations=s["limitations"], DateStatus=s["date_note"],
        URL=s["url"], Flagged="Yes" if s["id"] in flags else "") for s in srcs])
    undated = int((pd.Series([s["date_kind"] for s in srcs]) != "published").sum())
    invalid = sum(1 for s in srcs if not s["url_valid"])
    k = st.columns(5)
    k[0].metric("Source records", len(df))
    k[1].metric("Imprecise or missing dates", undated, help="Undated pages, month or year only, or updated-page entries.")
    k[2].metric("Failed URL validation", invalid)
    k[3].metric("Context-only sources", int((df.Companies == "Context only").sum()))
    k[4].metric("Flagged for verification", len(flags))
    if chk:
        st.caption(f"Link check: one polite HTTP request per URL on {chk_date}. Reachable means the page loaded; it does not prove the page supports the claim, "
                   "and a blocked page is inaccessible to the check, not disproven.")
    st.caption("Dates shown are original publication dates where known. 'Accessed' dates record when the analyst viewed the page and are "
               "not publication dates. URLs are as supplied in the register and were not re-checked by this application.")
    if audit:
        n_err = sum(1 for i in json.loads(audit["issues_json"]) if i["severity"] == "error")
        st.caption(md(f"Last local import: {audit['run_at']}, {audit['companies']} companies, {audit['sources']} sources, {n_err} errors."))
    f = st.columns(4)
    pub = f[0].multiselect("Publisher", sorted(df.Publisher.unique()))
    typ = f[1].multiselect("Classification", sorted(df.Type.unique()))
    co = f[2].multiselect("Related company", sorted({c for v in cmap.values() for c in v}))
    q = f[3].text_input("Search claims and limitations")
    v = df
    if pub:
        v = v[v.Publisher.isin(pub)]
    if typ:
        v = v[v.Type.isin(typ)]
    if co:
        v = v[v.Companies.apply(lambda s: any(c in s for c in co))]
    if q:
        v = v[(v.Claim + " " + v.Limitations).str.lower().str.contains(q.lower(), regex=False)]
    if v.empty:
        st.warning(md("No sources match the active filters."))
    else:
        st.dataframe(v, hide_index=True, width="stretch", column_config={"URL": ui.link_cell_config()})
    if not v.empty:
        st.markdown("**Source detail and limitations**")
        pick = st.selectbox("Source", list(v.ID), format_func=lambda i: f"{i} | {srcs_by_id[i]['publisher']} | {srcs_by_id[i]['date_raw']}", key="evid_pick")
        s = srcs_by_id[pick]
        st.markdown(md(f"**Claim:** {s['claim']}"))
        st.markdown(md(f"**Limitations:** {s['limitations']}"))
        st.markdown(md(f"**Date status:** {s['date_note']}  |  **Type:** {s['category']} ({dl.evidence_class(s['category'])})"))
        st.markdown(f"[Open source]({s['url']})")
        if s["date_kind"] != "published":
            st.caption("No precise publication date. The access date is not the publication date.")
        r = rev.get(pick)
        if r:
            st.markdown(md(f"**Analyst source review ({r['last_checked']}):** {r['evidence_class']}. Linked page supports claim: **{r['supports_claim']}**. "
                           f"Date on page: {r['page_date_confirmed']}."))
            st.markdown(md(r["review_note"]))
            st.caption(md("Recommended action: " + r["recommended_action"]))
        if s.get("correction_note"):
            st.markdown(md("**Citation correction (approved, lineage kept):** " + s["correction_note"]))
            st.caption(md("Original URL: " + (s.get("original_url") or "unchanged")))
    st.download_button("Download evidence registry (CSV)", exports.to_csv(v.to_dict("records"), list(v.columns)),
                       file_name="referraliq_evidence_registry.csv", mime="text/csv", key="dl_evid")

with tab_g:
    st.caption("Ten gates from the Phase 2 workbook (DILIGENCE GATES, supplied). Every gate starts Unknown. Unknown is not Pass. "
               "Checking boxes never changes the overall recommendation.")
    st.info("**Standing diligence question (G01):** " + content.STANDING_QUESTION)
    counts = pd.Series([g["status"] for g in gates]).value_counts()
    cs = st.columns(5)
    for col, s in zip(cs, repository.GATE_STATUSES):
        col.metric(s, int(counts.get(s, 0)))
    open_blockers = sum(1 for g in gates if g["status"] not in ("Pass", "Not Applicable"))
    st.markdown(md(f"**Open blockers: {open_blockers} of {len(gates)}**"))
    gdf = pd.DataFrame([dict(Gate=g["id"], Name=g["name"], Status=g["status"], Criterion=g["criterion"],
                             CurrentEvidence=g["current_evidence"], OwnerToAsk=g["owner"], IfNotMet=g["outcome_if_not_met"],
                             Origin=g["origin"], Updated=g["updated_at"] or "Not updated", Sources=g["evidence_source_ids"]) for g in gates])
    st.dataframe(gdf, hide_index=True, width="stretch")
    src_ids = [s["id"] for s in srcs]
    if ui.read_only():
        st.caption(md("Read-only showcase mode: gate editing is disabled."))
    else:
        st.markdown(md("**Update a gate (deliberate, timestamped)**"))
        with st.form("gate_form"):
            gid = st.selectbox("Gate", [g["id"] for g in gates], format_func=lambda i: f"{i} {next(g['name'] for g in gates if g['id'] == i)}")
            status = st.selectbox("Status", repository.GATE_STATUSES)
            cite = st.multiselect("Supporting source IDs", src_ids)
            note = st.text_area("Evidence note (required)")
            ack = st.checkbox("I reviewed the cited evidence. A vendor announcement is not independent verification.")
            if st.form_submit_button("Record gate update"):
                if not note.strip():
                    st.error(md("An evidence note is required."))
                elif status == "Pass" and not cite:
                    st.error(md("Pass requires at least one supporting source ID."))
                elif status == "Pass" and not ack:
                    st.error(md("Confirm that you reviewed the evidence before recording Pass."))
                else:
                    try:
                        repository.set_gate_status(con, gid, status, note.strip(), cite)
                        st.success(md(f"{gid} set to {status}."))
                        st.rerun()
                    except ValueError as e:
                        st.error(md(str(e)))
    hist = repository.gate_history(con)
    if hist:
        st.markdown(md("**Status history**"))
        st.dataframe(pd.DataFrame(hist).drop(columns=["id"]), hide_index=True, width="stretch")
    st.download_button("Download gate states and notes (CSV)",
                       exports.to_csv(gdf.to_dict("records") , list(gdf.columns)),
                       file_name="referraliq_gate_status.csv", mime="text/csv", key="dl_gates")

    st.markdown(md("**Investment decision criteria**"))
    st.markdown(
        "- **Invest:** requires G07, G08 and G09 resolved with primary evidence and an explicit reviewed decision record.\n"
        "- **Controlled pilot:** requires G01 and G02 at minimum, then G03 to G06 during the pilot.\n"
        "- **Monitor:** keep watching if evidence is delayed or no round is available.\n"
        "- **Pass:** any failed safety, security or compliance gate, or an uninvestable entry price.\n"
        "- Any failure in clinical safety or contractual compliance supersedes a positive financial result.")
    st.markdown("**Evidence confidence labels:** *Primary or regulator* (highest), *Independent press or research*, "
                "*Company announcement or website* (vendor-authored), *Vendor case study* (vendor-reported outcomes), "
                "*Unknown* (no evidence).")

    st.markdown(md("**Analyst review record**"))
    st.caption("Default research recommendation: " + config.DEFAULT_RECOMMENDATION + ". A record below is a personal local note; "
               "it does not alter that recommendation or represent approval by any organization.")
    if not ui.read_only():
        with st.form("decision_form", clear_on_submit=True):
            rec = st.selectbox("Recommendation being recorded", ["Advance to structured diligence", "Controlled pilot only",
                                                                  "Monitor", "Pass", "Equity investment (requires committee review)"])
            why = st.text_area("Rationale (required)")
            who = st.text_input("Analyst label (optional)")
            if st.form_submit_button("Record review"):
                try:
                    repository.add_decision(con, rec, why, who)
                    st.success(md("Review recorded locally."))
                    st.rerun()
                except ValueError as e:
                    st.error(md(str(e)))
    d = repository.decisions(con)
    if d:
        st.dataframe(pd.DataFrame(d).drop(columns=["id"]), hide_index=True, width="stretch")
ui.footer()
