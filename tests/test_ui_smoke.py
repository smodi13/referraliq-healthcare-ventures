"""UI smoke tests. Pages live in views/ (not pages/) so each is executed through a tiny harness that
stubs st.page_link, which needs a registered navigation context that AppTest does not provide."""
import glob

import pytest
from streamlit.testing.v1 import AppTest

from core import config

PAGES = sorted(glob.glob(str(config.ROOT / "views" / "*.py")))
OVERVIEW, SCREENER, DILIGENCE, PILOT, VENTURE, EVIDENCE = PAGES


def run_page(path: str) -> AppTest:
    code = (f"import runpy, sys, streamlit as st\nsys.path.insert(0, {str(config.ROOT)!r})\n"
            f"st.page_link = lambda *a, **k: None\n"
            f"from streamlit.delta_generator import DeltaGenerator\nDeltaGenerator.page_link = lambda self, *a, **k: None\n"
            f"runpy.run_path({path!r})\n")
    return AppTest.from_string(code, default_timeout=90).run()


def test_six_pages_exist():
    assert len(PAGES) == 6


def test_main_app_boots_and_registers_pages():
    at = AppTest.from_file(str(config.ROOT / "app.py"), default_timeout=90).run()
    assert not at.exception


@pytest.mark.parametrize("page", PAGES)
def test_page_renders_without_exception(page):
    at = run_page(page)
    assert not at.exception, [e.value for e in at.exception]
    assert not at.error, [e.value for e in at.error]
    assert len(at.title) == 1


def test_overview_default_recommendation_and_labels():
    at = run_page(OVERVIEW)
    html = " ".join(m.value for m in at.markdown)
    assert "ADVANCE TO DILIGENCE" in html
    for label in ("REPORTED, PUBLIC DISCLOSURE", "VERIFIED, OFFICIAL OR INDEPENDENT", "VENDOR-REPORTED CAPABILITY", "ANALYST JUDGMENT", "MODELED, HYPOTHETICAL", "UNVERIFIED, CURRENT STATUS UNKNOWN"):
        assert label in html
    assert "INVEST" not in html.replace("INVESTMENT", "").replace("INVESTABLE", "")


def test_pilot_reset_and_edit():
    at = run_page(PILOT)
    ni = next(n for n in at.number_input if "Cash realization" in n.label)
    ni.set_value(10.0).run()
    assert any("Modified" in w.value for w in at.warning)
    next(b for b in at.button if "Restore" in b.label).click().run()
    assert not any("Modified" in w.value for w in at.warning)


def test_pilot_results_follow_input_and_return():
    at = run_page(PILOT)
    base = [m.value for m in at.metric][:4]
    next(n for n in at.number_input if n.label.startswith("Automation completion")).set_value(0.0).run()
    assert [m.value for m in at.metric][0] == "$0"
    next(b for b in at.button if "Restore" in b.label).click().run()
    assert [m.value for m in at.metric][:4] == base


def test_venture_invalid_check_shows_error():
    at = run_page(VENTURE)
    next(n for n in at.number_input if n.label.startswith("Investor check")).set_value(40.0).run()
    assert any("cannot exceed" in e.value for e in at.error)


def test_screener_empty_state():
    at = run_page(SCREENER)
    at.text_input[0].set_value("zzzz-no-match").run()
    assert any("No companies match" in w.value for w in at.warning)


def test_screener_weight_change_and_reset():
    at = run_page(SCREENER)
    next(n for n in at.number_input if n.label == "Entry").set_value(90.0).run()
    assert any("What-if weights in use" in c.value for c in at.caption)
    next(b for b in at.button if "Reset original" in b.label).click().run()
    assert not any("What-if weights in use" in c.value for c in at.caption)


def test_diligence_follows_selection_from_other_page():
    code = (f"import runpy, sys, streamlit as st\nsys.path.insert(0, {str(config.ROOT)!r})\n"
            f"st.page_link = lambda *a, **k: None\nst.session_state.setdefault('company', 'Notable')\n"
            f"runpy.run_path({DILIGENCE!r})\n")
    at = AppTest.from_string(code, default_timeout=90).run()
    assert at.selectbox[0].value == "Notable"
    at.selectbox[0].set_value("Rhyme").run()
    assert at.session_state["company"] == "Rhyme"


def test_read_only_mode_hides_editing_controls(monkeypatch):
    monkeypatch.setenv("REFERRALIQ_READONLY", "1")
    at = run_page(EVIDENCE)
    assert not at.exception
    labels = [b.label for b in at.button]
    assert not any("Record" in l for l in labels)
    assert any("read-only" in c.value.lower() for c in at.caption)
    at = run_page(DILIGENCE)
    assert not any("Save note" in b.label for b in at.button)


def test_screener_filters_combine_and_clear():
    at = run_page(SCREENER)
    assert any("12 of 12" in c.value for c in at.caption)
    at.multiselect[3].set_value(["Medium"]).run()  # direct workflow fit
    n_medium = [c.value for c in at.caption if "companies shown" in c.value][0]
    assert "12 of 12" not in n_medium
    at.multiselect[0].set_value([at.multiselect[0].options[0]]).run()  # add a segment filter
    assert any("companies shown" in c.value for c in at.caption) or any("No companies match" in w.value for w in at.warning)
    at.multiselect[3].set_value([]).run()
    at.multiselect[0].set_value([]).run()
    assert any("12 of 12" in c.value for c in at.caption)


def test_scenario_carries_over_from_other_page_to_overview():
    code = (f"import runpy, sys, streamlit as st\nsys.path.insert(0, {str(config.ROOT)!r})\n"
            f"st.page_link = lambda *a, **k: None\n"
            f"from streamlit.delta_generator import DeltaGenerator\nDeltaGenerator.page_link = lambda self, *a, **k: None\n"
            f"st.session_state['scenario'] = 'Upside'\nrunpy.run_path({OVERVIEW!r})\n")
    at = AppTest.from_string(code, default_timeout=90).run()
    assert [m.value for m in at.metric if "pilot" in m.label.lower()][0] == "($31,610)"
