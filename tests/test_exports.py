import csv
import io

from core import exports


def test_formula_injection_escaped():
    out = exports.to_csv([dict(a="=1+1", b="+cmd", c="-2", d="@SUM", e="ok", f=-5.5)], list("abcdef"))
    row = list(csv.reader(io.StringIO(out)))[1]
    assert row[:4] == ["'=1+1", "'+cmd", "'-2", "'@SUM"] and row[4] == "ok" and row[5] == "-5.5"


def test_punctuation_and_ids_preserved():
    out = exports.to_csv([dict(name='Acme, "Inc."', ids="S08, S09")], ["name", "ids"])
    row = list(csv.reader(io.StringIO(out)))[1]
    assert row == ['Acme, "Inc."', "S08, S09"]


def test_no_absolute_user_paths_in_gate_export():
    from core import repository as repo
    import tempfile, pathlib
    with tempfile.TemporaryDirectory() as d:
        c = repo.connect(pathlib.Path(d) / "x.db")
        repo.seed(c)
        txt = exports.to_csv(repo.gates(c), ["id", "name", "status", "criterion", "current_evidence"])
        assert "/Users/" not in txt
