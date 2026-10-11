"""ReferralIQ entry point: navigation, theme and shared chrome. Run: streamlit run app.py"""
import streamlit as st

from core import components as ui, config

st.set_page_config(page_title="ReferralIQ | Healthcare Venture Intelligence", page_icon=None, layout="wide")
ui.inject_css()

pages = [
    st.Page("views/01_Investment_Overview.py", title="Investment Overview", default=True),
    st.Page("views/02_Deal_Screener.py", title="Deal Screener", url_path="screener"),
    st.Page("views/03_Company_Diligence.py", title="Company Diligence", url_path="diligence"),
    st.Page("views/04_Pilot_Economics.py", title="Pilot Economics", url_path="pilot"),
    st.Page("views/05_Venture_Returns.py", title="Venture Returns", url_path="venture"),
    st.Page("views/06_Evidence_and_Gates.py", title="Evidence and Gates", url_path="evidence"),
]
with st.sidebar:
    st.markdown("**ReferralIQ**")
    st.caption(f"As of {config.AS_OF_LABEL}  \nModel contract {config.MODEL_VERSION}")
    st.caption(config.DISCLAIMER)
    if config.is_read_only():
        st.caption("Read-only showcase mode: editing is disabled. Scenario what-if inputs stay interactive and are never saved.")
    else:
        st.caption("Local analyst mode: notes and gate updates are saved to the local database on this machine.")
st.navigation(pages).run()
