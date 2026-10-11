"""Display formatters. They never change stored values; negatives use a plain minus sign."""
from __future__ import annotations

import math


def _ok(v) -> bool:
    return isinstance(v, (int, float)) and math.isfinite(v)


def usd(v, dp: int = 0) -> str:
    if not _ok(v):
        return "n/a"
    s = f"{abs(v):,.{dp}f}"
    return f"(${s})" if round(v, dp) < 0 else f"${s}"


def musd(v, dp: int = 1) -> str:
    if not _ok(v):
        return "n/a"
    return f"(${abs(v):,.{dp}f}m)" if round(v, dp) < 0 else f"${v:,.{dp}f}m"


def pct(v, dp: int = 1) -> str:
    return f"{v * 100:,.{dp}f}%" if _ok(v) else "n/a"


def mult(v, dp: int = 2) -> str:
    return f"{v:,.{dp}f}x" if _ok(v) else "n/a"


def num(v, dp: int = 0) -> str:
    return f"{v:,.{dp}f}" if _ok(v) else "n/a"


def tone(v) -> str:
    return "negative" if _ok(v) and v < 0 else "positive"


def no_em_dash(text: str) -> str:
    """Defensive display filter for any untrusted text."""
    return text.replace(chr(0x2014), ", ").replace(chr(0x2013), "-") if isinstance(text, str) else text


def md(text: str) -> str:
    """Escape dollar signs so Streamlit markdown does not render paired amounts as LaTeX."""
    return text.replace("$", "\\$") if isinstance(text, str) else text
