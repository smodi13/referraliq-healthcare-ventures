import pytest

from core import data_loader as dl, scoring

DIMS = list(scoring.ORIGINAL_WEIGHTS)


def row(v, name="X"):
    return dict(name=name, **{d: v for d in DIMS})


def test_original_scores_reproduced():
    res = dl.load_package()
    assert scoring.audit_original(res.companies, tol=1e-9) == []


def test_bounds():
    assert scoring.score(row(5)) == pytest.approx(100)
    assert scoring.score(row(1)) == pytest.approx(20)


def test_reject_out_of_range():
    with pytest.raises(ValueError):
        scoring.score(row(6))
    with pytest.raises(ValueError):
        scoring.score(row(0))


def test_weights_normalized_and_validated():
    n = scoring.normalize_weights({"a": 1, "b": 3})
    assert n == {"a": 25.0, "b": 75.0}
    with pytest.raises(ValueError):
        scoring.normalize_weights({"a": -1, "b": 2})
    with pytest.raises(ValueError):
        scoring.normalize_weights({"a": 0, "b": 0})


def test_zero_weight_dimension_ignored():
    r = dict(row(3), strategic=5)
    w = {d: 0 for d in DIMS}
    w["strategic"] = 10
    assert scoring.score(r, w) == pytest.approx(100)


def test_default_ranking_matches_phase1_and_resets():
    res = dl.load_package()
    base = [r["name"] for r in sorted(res.companies, key=lambda r: (-r["score"], r["name"]))]
    assert [r["name"] for r in scoring.rank(res.companies)] == base
    equal = scoring.rank(res.companies, {d: 1 for d in DIMS})
    assert len(equal) == 12 and [r["name"] for r in scoring.rank(res.companies, scoring.ORIGINAL_WEIGHTS)] == base


def test_tie_order_is_stable_by_name():
    r = scoring.rank([row(3, "Zed"), row(3, "Alpha")])
    assert [x["name"] for x in r] == ["Alpha", "Zed"]


def test_entry_sensitivity_keeps_original_scores_and_moves_silna():
    res = dl.load_package()
    base = {c["name"]: c["score"] for c in res.companies}
    sens = scoring.entry_sensitivity(res.companies)
    orig = {r["name"]: r for r in sens["original"]}
    assert all(orig[n]["whatif_score"] == pytest.approx(base[n]) for n in base)  # Phase 1 scores reproduced
    assert orig["Silna Health"]["whatif_rank"] == 4
    cap = {r["name"]: r for r in sens["cap"]}
    assert cap["Silna Health"]["whatif_score"] == pytest.approx(77.0)
    assert cap["Silna Health"]["whatif_rank"] > orig["Silna Health"]["whatif_rank"]
    assert cap["Tennr"]["whatif_score"] == pytest.approx(86.0)  # disclosed valuation, unchanged
    assert all(c["score"] == base[c["name"]] for c in res.companies)  # inputs not mutated
    neutral = {r["name"]: r for r in sens["neutral"]}
    assert neutral["Silna Health"]["whatif_score"] == pytest.approx(77.0)
    no_entry = {r["name"]: r for r in sens["no_entry"]}
    assert no_entry["Tennr"]["whatif_rank"] == 1 and no_entry["Silna Health"]["whatif_rank"] > 4


def test_valuation_unknown_flags_expected_companies():
    res = dl.load_package()
    unknown = {c["name"] for c in res.companies if scoring.valuation_unknown(c)}
    assert "Silna Health" in unknown and "Tennr" not in unknown and "Assort Health" not in unknown
