import html

import streamlit as st

from core import components as ui, config, content, financial_math as fm, repository, scenarios as sc, scoring
from core.formatting import mult, pct, usd, md

ui.page_header("ReferralIQ | Healthcare Venture Intelligence",
               "Independent investment research workspace: referral and prior authorization AI")
ui.banner(config.DISCLAIMER + " Funding references are historical "
          "public snapshots; every forward-looking number is a hypothetical analyst assumption.", "info")

con = ui.db()
cos = {c["name"]: c for c in repository.companies(con)}
gates = {g["id"]: g for g in repository.gates(con)}
decisions = repository.decisions(con)

st.markdown(
    f'<div class="riq-decision"><div class="label">Current research recommendation</div>'
    f'<div class="value">{config.DEFAULT_RECOMMENDATION}</div></div>', unsafe_allow_html=True)
st.write(md(content.RECOMMENDATION_REASON))
r0 = fm.evaluate(sc.preset("Base"))
n_unknown = sum(1 for g in gates.values() if g["status"] == "Unknown")
brief = [
    ("What is being evaluated", "Provider-side referral and prior authorization automation: whether a controlled pilot, and separately an equity position in a vendor, is justified.", "ANALYST"),
    ("Leading diligence candidate", f"Silna Health, which announced $27M of seed and Series A funding in March 2025 [S10]. Not a confirmed investable security.", "REPORTED"),
    ("Why it is a diligence hypothesis", "Focused care-readiness workflows and an earlier-stage profile. Its 4 of 5 entry rating partly rests on an undisclosed valuation, which is an unknown, not a verified attractive price. Not a verified superior investment.", "ANALYST"),
    ("Why it is not approved", "No verified ARR, margin, retention, terms or open round. Acute-care scale unproven. Notable overlap unresolved.", "UNKNOWN"),
    ("Hypothetical Base economics", f"90-day pilot {usd(r0['pilot_net'])}; annual run-rate {usd(r0['runrate_net'])}; first scaled year {usd(r0['first_year_net'])}; gross MOIC {mult(r0['venture_moic'])}.", "MODELED"),
    ("Primary risks", "Financial: unverified private investment terms. Implementation: real-world workflow integration and measurable cash savings.", "UNKNOWN"),
    ("Evidence still missing", f"{n_unknown} of {len(gates)} diligence gates are Unknown. Blockers: incumbent overlap (G01), company quality (G07), entry terms (G08).", "UNKNOWN"),
    ("Next action", "Document the Notable and incumbent gap (G01), then request ARR, retention and customer references. Pilot only if G01 and G02 clear.", "ANALYST"),
]
st.markdown("**The 90-second brief**")
rows_html = "".join(
    f"<tr><td><b>{html.escape(a)}</b></td><td>{html.escape(b)}</td><td>{ui.tag(k)}</td></tr>" for a, b, k in brief)
st.markdown(f'<table class="riq-brief" style="width:100%">{rows_html}</table>', unsafe_allow_html=True)
bl = st.columns(4)
bl[0].page_link(ui.NAV_PAGES["diligence"], label="Company diligence")
bl[1].page_link(ui.NAV_PAGES["pilot"], label="Pilot economics")
bl[2].page_link(ui.NAV_PAGES["venture"], label="Venture returns")
bl[3].page_link(ui.NAV_PAGES["evidence"], label="Evidence and gates")
ui.evidence_legend()

c1, c2 = st.columns(2)
for col, (title, items) in zip((c1, c2), content.WHAT_WOULD_CHANGE.items()):
    with col, st.container(border=True):
        st.markdown(md(f"**{title}**"))
        for it in items:
            st.markdown(md(f"- {it}"))
if decisions:
    d = decisions[0]
    st.info(f"Latest local analyst review record ({d['created_at'][:10]}): **{d['recommendation']}**. "
            "This is a personal local note and does not replace the research recommendation above.")

st.subheader("Decision status ladder")
ladder = st.columns(4)
rows = [
    ("Invest (equity)", "Not supported", "Needs G07, G08 and G09 resolved with primary evidence."),
    ("Pilot (commercial)", "Conditional", "Only after G01 incumbent check and G02 safety and security."),
    ("Monitor", "Fallback", "If evidence gathering stalls or no round is available."),
    ("Pass", "Not indicated", "Triggered by a failed gate or an uninvestable entry price."),
]
for col, (a, b, c) in zip(ladder, rows):
    with col, st.container(border=True):
        st.markdown(md(f"**{a}**"))
        st.markdown(f'<span class="riq-tag">{b}</span>', unsafe_allow_html=True)
        st.caption(md(c))
st.caption(md("Current position: advance to structured diligence. Product fit and equity investability are separate questions."))

st.subheader("Two decisions, kept separate")
t1, t2 = st.columns(2)
for col, (name, t) in zip((t1, t2), content.TRACKS.items()):
    with col, st.container(border=True):
        st.markdown(md(f"**{name}**"))
        st.write(md(t["question"]))
        st.markdown(md(f"*Position:* {t['position']}"))
        st.markdown(md(f"*Evidence needed:* {t['evidence']}"))
        st.caption(md(f"Gates: {t['gates']}"))

st.subheader("Four priority roles")
roles = ["Silna Health", "Tennr", "Rhyme", "Notable"]
role_note = {
    "Silna Health": "Lead equity diligence subject. Not a confirmed investable security.",
    "Tennr": "Commercial and product benchmark. Highest Phase 1 screening score.",
    "Rhyme": "Payer-provider authorization network comparator.",
    "Notable": "Incumbent-vendor diligence check. Historical Intermountain relationship, current status unverified.",
}
for col, n in zip(st.columns(4), roles):
    c = cos[n]
    with col, st.container(border=True):
        st.markdown(md(f"**{n}**"))
        st.caption(md(c["recommended_role"]))
        st.metric("Phase 1 analyst score", f"{c['score']:.0f} / 100", help="Directional analyst screening score, not a probability of success.")
        st.caption(md(role_note[n]))
        st.caption(md(f"Historical financing: {c['funding_event']}"))

_sens = scoring.entry_sensitivity([dict(c) for c in cos.values()])
_o = next(r for r in _sens["original"] if r["name"] == "Silna Health")
_c = next(r for r in _sens["cap"] if r["name"] == "Silna Health")
st.info(md(content.SCREEN_LIMITATION + f" Silna ranks #{_o['whatif_rank']} originally and #{_c['whatif_rank']} if its entry rating is held at neutral (tie with Plenful at {_c['whatif_score']:.0f}). "
           "See the Deal Screener for the full sensitivity."))

st.subheader("Strengths and disconfirming risks")
s_col, r_col = st.columns(2)
for col, title, items in ((s_col, "Five investment strengths", content.STRENGTHS), (r_col, "Five disconfirming risks", content.RISKS)):
    with col:
        st.markdown(md(f"**{title}**"))
        for head, body, cite, kind in items:
            st.markdown(md(f"**{head}.** {body} _[{cite}]_") + "<br>" + ui.tag(kind), unsafe_allow_html=True)

st.subheader("Illustrative scenario summary")
ui.hypothetical_banner()
name = ui.scenario_selector("overview")
r = fm.evaluate(sc.preset(name))
m = st.columns(4)
m[0].metric("90-day pilot net cash", usd(r["pilot_net"]), help="Three months including one-time setup. Hypothetical.")
m[1].metric("Scaled annual run-rate net cash", usd(r["runrate_net"]), help="Steady-state year after full adoption. Hypothetical.")
m[2].metric("First scaled-year net cash", usd(r["first_year_net"]), help="Ramp-adjusted benefits less full recurring cost and rollout setup. Hypothetical.")
m[3].metric("Gross MOIC / IRR (6 yr)", f"{mult(r['venture_moic'])} / {pct(r['venture_irr'])}", help="Hypothetical gross, not net fund IRR.")
st.caption("The pilot and first scaled year are alternative sequential decisions and are never added together. "
           "A negative pilot is a planned evidence expense, and a positive run-rate does not by itself justify equity.")

st.subheader("Three blockers before any investment recommendation")
for gid in ("G01", "G07", "G08"):
    g = gates[gid]
    with st.container(border=True):
        a, b = st.columns([4, 1])
        a.markdown(md(f"**{gid} {g['name']}**: {g['criterion']}"))
        a.caption(md(f"Current evidence: {g['current_evidence']}"))
        b.markdown(f'<span class="riq-tag">{g["status"]}</span>', unsafe_allow_html=True)
st.page_link(ui.NAV_PAGES["evidence"], label="Open all ten diligence gates and the evidence registry")

st.subheader("Where to go next")
n1, n2, n3, n4 = st.columns(4)
n1.page_link(ui.NAV_PAGES["screener"], label="Compare the 12 companies")
n2.page_link(ui.NAV_PAGES["diligence"], label="Review a company dossier")
n3.page_link(ui.NAV_PAGES["pilot"], label="Stress-test pilot economics")
n4.page_link(ui.NAV_PAGES["venture"], label="Hypothetical venture returns")

st.subheader("Original research documents")
d1, d2, d3, d4 = st.columns(4)
XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
with d1:
    ui.file_download("Executive brief (PDF)", config.BRIEF_PDF, "application/pdf", "dl_brief")
with d2:
    ui.file_download("Investment committee memo (PDF)", config.MEMO_PDF, "application/pdf", "dl_memo")
with d3:
    ui.file_download("Excel model (original)", config.WORKBOOK, XLSX, "dl_xlsx")
with d4:
    ui.file_download("Excel model (publication copy)", config.PUBLICATION_WORKBOOK, XLSX, "dl_xlsx_pub")
st.caption("The original workbook is unchanged. The publication copy differs only on the MARKET FRAMEWORK sheet, where missing inputs show "
           "'Not calculated' instead of 0. No market size is estimated in either file.")
with st.expander("Definitions"):
    for k, v in content.DEFINITIONS.items():
        st.markdown(md(f"**{k}**: {v}"))
ui.footer()
