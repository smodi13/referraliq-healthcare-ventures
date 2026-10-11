import hashlib
import json
import re
from pathlib import Path

import pytest

from core import config, data_loader as dl

ROOT = config.ROOT


def write(tmp_path, name, text):
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return p


def test_real_package_counts_and_integrity():
    r = dl.load_package()
    assert len(r.companies) == 12 and len(r.sources) == 36
    assert not r.errors
    assert len({c["name"].casefold() for c in r.companies}) == 12


def test_reference_files_unchanged():
    saved = json.loads(config.MANIFEST_JSON.read_text())["sha256"]
    for f, h in saved.items():
        assert hashlib.sha256((ROOT / f).read_bytes()).hexdigest() == h, f"{f} changed"


def test_no_em_dash_in_project_files():
    skip = {".git", ".venv", "__pycache__", "local_data", ".pytest_cache"}
    originals = set(config.REFERENCE_FILES) | {"qa/test_results.txt", "qa/workbook_audit_results.txt", "qa/workbook_audit.py"}
    bad = []
    for p in ROOT.rglob("*"):
        rel = p.relative_to(ROOT)
        if p.is_dir() or skip & set(rel.parts) or str(rel) in originals or p.suffix in {".pdf", ".xlsx", ".db", ".png"}:
            continue
        try:
            if chr(0x2014) in p.read_text(encoding="utf-8"):
                bad.append(str(rel))
        except UnicodeDecodeError:
            pass
    assert not bad, bad


@pytest.mark.parametrize("raw,kind", [
    ("2025-06-18", "published"), ("2021-11", "published_month"), ("2025", "published_year"),
    ("Undated / accessed 2026-10-10", "undated"), ("Undated, accessed 2026-10-10", "undated"),
    ("2026 / updated 2026-10-08", "updated"), ("2025 annual report / accessed 2026-10-10", "annual_report"),
    ("2025-13-45", "invalid"), ("last tuesday", "unknown"),
])
def test_date_classification(raw, kind):
    assert dl.classify_date(raw)["kind"] == kind


def test_access_date_is_not_publication_date():
    d = dl.classify_date("Undated / accessed 2026-10-10")
    assert d["published"] is None and d["accessed"] == "2026-10-10"


def test_event_dates():
    assert dl.parse_event_date("$101M Series C (Jun 2025)") == "Jun 2025"
    assert dl.parse_event_date("$40M Feb 2026 financing, $64M total") == "Feb 2026"
    assert dl.parse_event_date("Recent financing amount not verified") is None


SRC_HDR = "id,publisher,date,claim,url,category,limitations\n"
CO_HDR = ",".join(dl.COMPANY_COLUMNS) + "\n"


def co_row(name="Acme", sids="S1", **kw):
    f = dict(name=name, segment="s", buyer="b", capabilities="c", public_stage="A", funding_event="$1M (Jan 2025)",
             valuation="v", financing_comment="f", source_ids=sids, direct_fit="High", use_case="u", key_risk="k",
             recommended_role="r", strategic=3, workflow=3, pilot=3, defensibility=3, entry=3, confidence=3, score=60)
    f.update(kw)
    return ",".join(str(f[c]) for c in dl.COMPANY_COLUMNS) + "\n"


def codes(res):
    return {i.code for i in res.issues}


def test_missing_columns(tmp_path):
    c = write(tmp_path, "c.csv", "name,segment\nA,B\n")
    s = write(tmp_path, "s.csv", "id,publisher\nS1,x\n")
    assert "missing_columns" in codes(dl.load_package(c, s))


def test_duplicates_and_broken_refs(tmp_path):
    s = write(tmp_path, "s.csv", SRC_HDR + "S1,P,2025-01-01,cl,https://a.com,Primary,l\nS1,P,2025-01-01,cl,https://a.com,Primary,l\n")
    c = write(tmp_path, "c.csv", CO_HDR + co_row("Acme", "S1;S9") + co_row("ACME", "S1"))
    res = dl.load_package(c, s)
    assert {"duplicate_source_id", "duplicate_company", "broken_source_ref"} <= codes(res)
    assert len(res.companies) == 1


def test_bad_url_scores_and_blank_name(tmp_path):
    s = write(tmp_path, "s.csv", SRC_HDR + "S1,P,2025-02-30,cl,ftp://x,Primary,l\n")
    c = write(tmp_path, "c.csv", CO_HDR + co_row("Acme", "S1", strategic=9) + co_row("", "S1") + co_row("B", "S1", score="abc"))
    res = dl.load_package(c, s)
    assert {"invalid_url", "bad_dimension", "blank_company_name", "bad_score", "unclassified_date"} <= codes(res)


def test_unlinked_context_source_is_ok(tmp_path):
    s = write(tmp_path, "s.csv", SRC_HDR + "S1,P,2025-01-01,cl,https://a.com,Primary,l\nS2,P,2025-01-01,cl,https://b.com,Primary,l\n")
    c = write(tmp_path, "c.csv", CO_HDR + co_row("Acme", "S1"))
    res = dl.load_package(c, s)
    assert not res.errors and len(res.sources) == 2 and len(res.links) == 1
