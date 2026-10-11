"""Streamlit UI helpers shared by all pages. The only core module that imports Streamlit."""
from __future__ import annotations

import html
from pathlib import Path

import streamlit as st

from . import config, repository, scenarios as sc
from .formatting import no_em_dash

NAV_PAGES = {
    "overview": "views/01_Investment_Overview.py",
    "screener": "views/02_Deal_Screener.py",
    "diligence": "views/03_Company_Diligence.py",
    "pilot": "views/04_Pilot_Economics.py",
    "venture": "views/05_Venture_Returns.py",
    "evidence": "views/06_Evidence_and_Gates.py",
}


@st.cache_resource
def _seeded() -> bool:
    con = repository.connect()
    try:
        repository.seed(con)
    finally:
        con.close()
    return True


def db():
    """One connection per browser session (reruns may land on different threads, hence shared=True).
    Never stored in a module-level cache, so sessions do not share state."""
    _seeded()
    con = st.session_state.get("_db_con")
    if con is None:
        con = st.session_state["_db_con"] = repository.connect(shared=True, readonly=config.is_read_only())
    return con


def inject_css() -> None:
    css = (config.ROOT / "assets" / "styles.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def banner(text: str, kind: str = "warn") -> None:
    cls = "riq-banner info" if kind == "info" else "riq-banner"
    st.markdown(f'<div class="{cls}">{html.escape(no_em_dash(text))}</div>', unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "") -> None:
    st.title(title)
    if subtitle:
        st.caption(subtitle)
    st.caption(f"Research as of {config.AS_OF_LABEL} | Model contract {config.MODEL_VERSION} | "
               "Public sources and hypothetical scenarios, not a live data feed.")


def hypothetical_banner() -> None:
    banner("Hypothetical investment terms and company financials. Not a company forecast or investment offer. "
           "Nothing here is a verified Silna, vendor or Intermountain metric.")


def footer() -> None:
    st.divider()
    st.markdown(f'<div class="riq-foot">{html.escape(config.DISCLAIMER)} All outputs require a final human '
                "investment review.</div>", unsafe_allow_html=True)


def read_only() -> bool:
    return config.is_read_only()


def file_download(label: str, path: Path, mime: str, key: str) -> None:
    if path.exists():
        st.download_button(label, path.read_bytes(), file_name=path.name, mime=mime, key=key)
    else:
        st.caption(f"{path.name} not found")


def scenario_selector(key: str) -> str:
    names = sc.scenario_names()
    cur = st.session_state.get("scenario", "Base")
    pick = st.segmented_control("Scenario preset", names, default=cur if cur in names else "Base", key=f"seg_{key}")
    pick = pick or cur
    st.session_state["scenario"] = pick
    return pick


def selected_company(names: list[str]) -> str:
    cur = st.session_state.get("company", names[0])
    return cur if cur in names else names[0]


def link_cell_config():
    return st.column_config.LinkColumn("URL", display_text="open source")


def _reset_cb(prefix: str, scenario: str) -> None:
    for k in [k for k in st.session_state if str(k).startswith(f"{prefix}:{scenario}:")]:
        del st.session_state[k]


def scenario_inputs(prefix: str, scenario: str, groups: dict[str, list[str]], cols: int = 3) -> tuple[dict, list[str]]:
    """Render grouped number inputs seeded from the frozen preset. Returns (inputs, changed_keys)."""
    base = sc.preset(scenario)
    vals = dict(base)
    st.button("Restore default values", key=f"reset_{prefix}_{scenario}", on_click=_reset_cb, args=(prefix, scenario))
    for group, keys in groups.items():
        with st.expander(group, expanded=group in ("Volume and Eligibility", "Realization")):
            cs = st.columns(cols)
            for i, k in enumerate(keys):
                m = sc.FIELDS[k]
                wkey = f"{prefix}:{scenario}:{k}"
                label = f"{m['label']} ({m['unit']})"
                with cs[i % cols]:
                    if m["kind"] == "pct":
                        w = st.number_input(label, 0.0, 100.0, round(base[k] * 100, 6), 1.0, format="%.1f", key=wkey, help=m["tip"])
                        v = w / 100
                        vals[k] = base[k] if abs(v - base[k]) < 1e-9 else v
                    elif m["kind"] == "int":
                        vals[k] = float(st.number_input(label, 0, None, int(base[k]), int(m["step"]), key=wkey, help=m["tip"]))
                    else:
                        w = st.number_input(label, 0.0, None, float(base[k]), float(m["step"]), key=wkey, help=m["tip"])
                        vals[k] = w
    changed = [k for k in vals if k in base and vals[k] != base[k]]
    return vals, changed


def tag(kind: str) -> str:
    """Inline HTML label for an evidence status. Kind is a key of content.EVIDENCE_KINDS."""
    from .content import EVIDENCE_KINDS
    label, tip = EVIDENCE_KINDS[kind]
    return f'<span class="riq-tag riq-{kind.lower()}" title="{html.escape(tip)}">{html.escape(label)}</span>'


def evidence_legend() -> None:
    from .content import EVIDENCE_KINDS
    st.markdown(" ".join(tag(k) for k in EVIDENCE_KINDS), unsafe_allow_html=True)
    st.caption("Every claim on the overview carries one of these six labels. Reported means disclosed, not independently verified; modeled means hypothetical.")
