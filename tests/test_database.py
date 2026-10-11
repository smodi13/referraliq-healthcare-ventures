import sqlite3

import pytest

from core import data_loader as dl, repository as repo


@pytest.fixture
def con(tmp_path):
    c = repo.connect(tmp_path / "t.db")
    yield c
    c.close()


def counts(c):
    return {t: c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            for t in ("companies", "sources", "company_source_links", "diligence_gates")}


def test_seed_counts_and_idempotent(con):
    repo.seed(con)
    first = counts(con)
    assert first["companies"] == 12 and first["sources"] == 36 and first["diligence_gates"] == 10
    repo.seed(con)
    assert counts(con) == first


def test_gates_start_unknown_and_survive_reseed(con):
    repo.seed(con)
    assert {g["status"] for g in repo.gates(con)} == {"Unknown"}
    repo.set_gate_status(con, "G01", "In Progress", "asked procurement", ["S31"])
    repo.add_note(con, "company", "1", "note")
    repo.seed(con)
    assert next(g for g in repo.gates(con) if g["id"] == "G01")["status"] == "In Progress"
    assert len(repo.notes(con)) == 1 and len(repo.gate_history(con)) == 1


def test_gate_validation(con):
    repo.seed(con)
    with pytest.raises(ValueError):
        repo.set_gate_status(con, "G01", "Maybe", "", [])
    with pytest.raises(ValueError):
        repo.set_gate_status(con, "G01", "Pass", "x", ["S999"])
    with pytest.raises(ValueError):
        repo.set_gate_status(con, "G99", "Pass", "x", [])


def test_foreign_keys_enforced(con):
    repo.seed(con)
    with pytest.raises(sqlite3.IntegrityError):
        con.execute("INSERT INTO company_source_links VALUES (1,'NOPE','x')")


def test_failed_import_rolls_back(con, monkeypatch):
    repo.init_schema(con)
    res = dl.load_package()
    res.links.append(dict(company="Ghost Co", source_id="S01", origin="x"))  # KeyError mid-transaction
    with pytest.raises(KeyError):
        repo.seed(con, res)
    assert counts(con)["companies"] == 0 and counts(con)["sources"] == 0


def test_integrity_errors_block_seed(con):
    res = dl.load_package()
    res.issues.append(dl.Issue("error", "x", "boom"))
    with pytest.raises(ValueError):
        repo.seed(con, res)


def test_sql_injection_text_is_stored_literally(con):
    repo.seed(con)
    repo.add_note(con, "company", "1'; DROP TABLE companies;--", "x'); DROP TABLE sources;--")
    assert counts(con)["companies"] == 12
    assert repo.notes(con)[0]["body"].startswith("x')")


def test_decision_requires_rationale(con):
    repo.seed(con)
    with pytest.raises(ValueError):
        repo.add_decision(con, "Pass", "  ")
    repo.add_decision(con, "Monitor", "waiting", "me")
    assert repo.decisions(con)[0]["recommendation"] == "Monitor"


def test_notable_has_memo_cited_links(con):
    repo.seed(con)
    nid = con.execute("SELECT id FROM companies WHERE name='Notable'").fetchone()[0]
    assert {"S31", "S33", "S34", "S36", "S24", "S25"} <= {s["id"] for s in repo.company_sources(con, nid)}
