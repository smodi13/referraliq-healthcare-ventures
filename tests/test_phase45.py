import json
import re
import sqlite3

import pytest
from streamlit.testing.v1 import AppTest

from core import config, data_loader as dl, exports, repository as repo, scenarios as sc

WRITES = [
    "INSERT INTO companies (name, score) VALUES ('Hack', 99)",
    "UPDATE companies SET score = 100 WHERE name = 'Tennr'",
    "UPDATE score_snapshots SET score = 0",
    "DELETE FROM sources WHERE id = 'S10'",
    "UPDATE sources SET claim = 'edited'",
    "UPDATE diligence_gates SET status = 'Pass'",
    "INSERT INTO analyst_notes (entity_type, entity_id, body, created_at) VALUES ('c','1','x','now')",
    "DELETE FROM company_source_links",
    "DROP TABLE import_audit",
    "PRAGMA user_version = 7",
]


@pytest.fixture
def db_path(tmp_path):
    p = tmp_path / "ro.db"
    c = repo.connect(p)
    repo.seed(c)
    repo.add_note(c, "company", "1", "private local analyst note")
    repo.set_gate_status(c, "G01", "In Progress", "private gate note", [])
    c.close()
    return p


@pytest.mark.parametrize("sql", WRITES)
def test_sqlite_readonly_handle_rejects_every_write(db_path, sql):
    c = repo.connect(db_path, readonly=True)
    with pytest.raises(sqlite3.OperationalError):
        c.execute(sql)
        c.commit()
    c.close()
    chk = repo.connect(db_path)  # database unchanged
    assert chk.execute("SELECT COUNT(*) FROM companies").fetchone()[0] == 12
    assert chk.execute("SELECT score FROM companies WHERE name='Tennr'").fetchone()[0] == 86.0
    assert chk.execute("SELECT COUNT(*) FROM sources").fetchone()[0] == 36


def test_readonly_downloads_exclude_local_private_data(db_path, monkeypatch):
    monkeypatch.setenv("REFERRALIQ_READONLY", "1")
    c = repo.connect(db_path, readonly=True)
    gates = repo.gates(c)
    txt = exports.to_csv(gates, ["id", "name", "status", "current_evidence", "evidence_source_ids", "updated_at"])
    assert "private local analyst note" not in txt and "private gate note" not in txt and "In Progress" not in txt
    assert repo.notes(c) == []


def test_sessions_do_not_share_edited_scenarios():
    def page(extra=""):
        code = (f"import runpy, sys, streamlit as st\nsys.path.insert(0, {str(config.ROOT)!r})\nst.page_link = lambda *a, **k: None\n{extra}"
                f"runpy.run_path({str(config.ROOT / 'views' / '04_Pilot_Economics.py')!r})\n")
        return AppTest.from_string(code, default_timeout=90).run()
    a = page()
    next(n for n in a.number_input if n.label.startswith("Cash realization")).set_value(5.0).run()
    assert any("Modified" in w.value for w in a.warning)
    b = page()  # a second visitor
    assert not any("Modified" in w.value for w in b.warning)
    assert sc.preset("Base")["cash_realization"] == 0.5


def test_standing_question_visible_on_gates_tab():
    code = (f"import runpy, sys, streamlit as st\nsys.path.insert(0, {str(config.ROOT)!r})\nst.page_link = lambda *a, **k: None\n"
            f"runpy.run_path({str(config.ROOT / 'views' / '06_Evidence_and_Gates.py')!r})\n")
    at = AppTest.from_string(code, default_timeout=90).run()
    assert any("What relevant capabilities, contracts, integrations" in i.value for i in at.info)


FORBIDDEN = [
    r"remains active", r"is currently (using|handling)", r"currently handles", r"exclusive (arrangement|partner)",
    r"is (actively )?fundraising", r"is raising", r"endorsed by Intermountain(?! Health or)", r"official (Intermountain|Ventures)",
    r"Tenn r", r"guaranteed", r"predicts? (success|returns)",
]


def test_app_copy_has_no_overstated_relationship_or_affiliation_claims():
    files = [config.ROOT / "core" / "content.py", config.ROOT / "app.py", config.ROOT / "core" / "config.py",
             *sorted((config.ROOT / "views").glob("*.py"))]
    hits = []
    for f in files:
        txt = f.read_text()
        for pat in FORBIDDEN:
            for m in re.finditer(pat, txt, re.I):
                line = txt[max(0, m.start() - 60): m.end() + 60].replace("\n", " ")
                if re.search(r"(not|no|never|do not|does not|cannot|without)\b", line, re.I):
                    continue  # negated disclaimer
                hits.append(f"{f.name}: {line}")
    assert not hits, hits


def test_company_name_spelling_matches_register():
    names = {c["name"] for c in dl.load_package().companies}
    assert "Tennr" in names and not any("Tenn r" in n for n in names)


def test_source_review_covers_every_register_row_and_records_corrections():
    rev = json.loads((config.AUDIT_DIR / "source_review.json").read_text())["sources"]
    ids = [s["id"] for s in dl.load_package().sources]
    assert [r["id"] for r in rev] == ids and len(ids) == 36
    by = {r["id"]: r for r in rev}
    assert by["S15"]["supports_claim"].startswith("Yes") and by["S15"]["replacement_status"].startswith("Approved")
    assert by["S26"]["supports_claim"].startswith("Yes") and "1.2 billion" in by["S26"]["review_note"]
    assert by["S28"]["supports_claim"] == "Yes" and "ailevate" in by["S28"]["review_note"].lower()
    assert by["S07"]["supports_claim"] == "Yes" and "intermittent" in by["S07"]["review_note"].lower()
    assert by["S32"]["supports_claim"].startswith("Yes, via") and "403" in by["S32"]["review_note"]


def test_raw_register_file_unchanged_and_corrections_are_an_overlay():
    import csv
    raw = {r["id"]: r for r in csv.DictReader(open(config.SOURCE_CSV, encoding="utf-8"))}
    assert len(raw) == 36
    assert raw["S15"]["url"].lower().startswith("https://www.prnewswire.com/news/plenful")
    assert "assorthealth.com/press" in raw["S26"]["url"]
    loaded = {s["id"]: s for s in dl.load_package().sources}
    assert len(loaded) == 36 and set(loaded) == set(raw)
    assert loaded["S15"]["url"].endswith("302442027.html") and loaded["S15"]["original_url"] == raw["S15"]["url"]
    assert loaded["S26"]["url"].endswith("302808634.html") and loaded["S26"]["original_url"] == raw["S26"]["url"]
    assert "not a valuation" in loaded["S15"]["limitations"].lower()
    assert "index supports" not in loaded["S15"]["limitations"].lower()  # stale index-page caveat replaced
    assert "not a current october 2026 valuation" in loaded["S26"]["limitations"].lower()
    assert "June 24, 2026" in loaded["S26"]["correction_note"] and "June 25, 2026" in loaded["S26"]["correction_note"]
    assert loaded["S28"]["url"] == raw["S28"]["url"]
    low = loaded["S28"]["limitations"].lower()
    assert "ailevate" in low and "2024 caqh index" in low and "not a validation of any screened vendor" in low and "not a measured intermountain" in low
    assert loaded["S01"]["original_url"] == "" and loaded["S01"]["url"] == raw["S01"]["url"]  # untouched rows


def test_corrections_persist_to_database_and_old_schema_migrates(tmp_path):
    p = tmp_path / "old.db"
    import sqlite3
    old = sqlite3.connect(p)  # database created before correction columns existed
    old.executescript("CREATE TABLE sources (id TEXT PRIMARY KEY, publisher TEXT, date_raw TEXT, claim TEXT, url TEXT, category TEXT, limitations TEXT, date_kind TEXT, published TEXT, accessed TEXT, date_note TEXT, url_valid INTEGER);")
    old.commit(); old.close()
    c = repo.connect(p)
    repo.seed(c)
    s = {r["id"]: r for r in repo.sources(c)}
    assert len(s) == 36 and s["S26"]["original_url"].endswith("/press") and s["S26"]["corrected_on"] == "2026-10-10"
    assert s["S15"]["url"].startswith("https://www.prnewswire.com/news-releases/plenful-raises-50m")
    assert len(repo.companies(c)) == 12


def test_styles_define_keyboard_focus_ring():
    css = (config.ROOT / "assets" / "styles.css").read_text()
    assert "stSidebarNavLink" in css and ":focus-visible" in css


# ---- Phase 4.6: fail-closed read-only ----------------------------------------------------
def _clear(monkeypatch):
    for k in ("REFERRALIQ_ANALYST_MODE", "REFERRALIQ_READONLY", "REFERRALIQ_PUBLIC"):
        monkeypatch.delenv(k, raising=False)


def test_default_environment_is_read_only(monkeypatch):
    _clear(monkeypatch)
    assert config.is_read_only() is True


def test_analyst_mode_requires_explicit_opt_in(monkeypatch):
    _clear(monkeypatch)
    for bad in ("0", "no", "", "false", "analyst"):
        monkeypatch.setenv("REFERRALIQ_ANALYST_MODE", bad)
        assert config.is_read_only() is True, bad
    monkeypatch.setenv("REFERRALIQ_ANALYST_MODE", "1")
    assert config.is_read_only() is False


def test_public_flag_and_hosted_path_override_analyst_mode(monkeypatch, tmp_path):
    _clear(monkeypatch)
    monkeypatch.setenv("REFERRALIQ_ANALYST_MODE", "1")
    monkeypatch.setenv("REFERRALIQ_PUBLIC", "1")
    assert config.is_read_only() is True
    monkeypatch.delenv("REFERRALIQ_PUBLIC")
    monkeypatch.setenv("REFERRALIQ_READONLY", "1")
    assert config.is_read_only() is True
    monkeypatch.delenv("REFERRALIQ_READONLY")
    assert config.is_read_only() is False
    monkeypatch.setattr(config, "ROOT", type(config.ROOT)("/mount/src/referraliq"))
    assert config.hosted_checkout() and config.is_read_only() is True


def test_writes_blocked_by_default_without_any_env(monkeypatch, tmp_path):
    c = repo.connect(tmp_path / "d.db")
    repo.seed(c)
    _clear(monkeypatch)
    with pytest.raises(repo.ReadOnlyError):
        repo.add_note(c, "company", "1", "x")
    with pytest.raises(repo.ReadOnlyError):
        repo.set_gate_status(c, "G01", "Pass", "x", ["S31"])
    with pytest.raises(repo.ReadOnlyError):
        repo.add_decision(c, "Pass", "x")
    with pytest.raises(repo.ReadOnlyError):
        repo.set_flag(c, "S10", True)
    c.close()


def test_default_ui_shows_no_edit_controls_and_analyst_mode_does(monkeypatch):
    def page(path):
        code = (f"import runpy, sys, streamlit as st\nsys.path.insert(0, {str(config.ROOT)!r})\nst.page_link = lambda *a, **k: None\n"
                f"runpy.run_path({str(config.ROOT / 'views' / path)!r})\n")
        return AppTest.from_string(code, default_timeout=90).run()
    _clear(monkeypatch)
    ro = page("06_Evidence_and_Gates.py")
    assert not any("Record" in b.label for b in ro.button)
    monkeypatch.setenv("REFERRALIQ_ANALYST_MODE", "1")
    an = page("06_Evidence_and_Gates.py")
    assert any("Record" in b.label for b in an.button)


def test_evidence_kinds_used_in_copy_are_defined():
    from core import content
    used = {k for *_, k in content.STRENGTHS} | {k for *_, k in content.RISKS}
    src = (config.ROOT / "views" / "01_Investment_Overview.py").read_text()
    used |= set(re.findall(r'"(VERIFIED|REPORTED|VENDOR|ANALYST|MODELED|UNKNOWN)"\)', src))
    assert used and used <= set(content.EVIDENCE_KINDS) and len(content.EVIDENCE_KINDS) == 6


def test_silna_entry_rating_limitation_is_on_overview_and_screener():
    from core import content
    assert "undisclosed valuation is an unknown" in content.SCREEN_LIMITATION
    for page in ("01_Investment_Overview.py", "02_Deal_Screener.py"):
        assert "SCREEN_LIMITATION" in (config.ROOT / "views" / page).read_text()
    best_entry_claim = (config.ROOT / "views" / "01_Investment_Overview.py").read_text()
    assert "best entry rating" not in best_entry_claim
