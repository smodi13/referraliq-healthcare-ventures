from core import formatting as f


def test_money_formats_use_parentheses_for_negatives():
    assert f.usd(-39834) == "($39,834)" and f.usd(25776) == "$25,776" and f.usd(-0.2) == "$0"
    assert f.usd(1250000) == "$1,250,000" and f.usd(float("nan")) == "n/a"
    assert f.musd(-1.357) == "($1.4m)" and f.musd(80) == "$80.0m"


def test_multiples_percent_and_numbers():
    assert f.mult(2.971428) == "2.97x" and f.pct(0.199023) == "19.9%" and f.num(1680.0, 1) == "1,680.0"
    assert f.pct(float("inf")) == "n/a"


def test_md_escapes_dollars_and_em_dash_filter():
    assert f.md("$8,090 vs $8,000") == "\\$8,090 vs \\$8,000"
    assert f.no_em_dash("a" + chr(0x2014) + "b") == "a, b"
