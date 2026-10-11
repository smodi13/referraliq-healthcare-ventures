"""Phase 1 screening score: weighted 1-5 dimensions, sum(weight*value)/5 on a 100 point scale."""
from __future__ import annotations

import math
from typing import Mapping

ORIGINAL_WEIGHTS: dict[str, float] = {
    "strategic": 25, "workflow": 20, "pilot": 15, "defensibility": 15, "entry": 15, "confidence": 10,
}
DEFINITIONS = {
    "strategic": "Strategic fit with a health system and its venture arm (analyst judgment).",
    "workflow": "Relevance to referral and prior authorization workflow.",
    "pilot": "Feasibility of a controlled commercial pilot.",
    "defensibility": "Apparent defensibility of product, data and network position.",
    "entry": "Attractiveness of equity entry (higher means a more plausible entry price or stage).",
    "confidence": "Analyst confidence in the public evidence behind the other ratings.",
}


def normalize_weights(w: Mapping[str, float]) -> dict[str, float]:
    """Scale non-negative weights so they total 100. Raises on negative or all-zero input."""
    for k, v in w.items():
        if not isinstance(v, (int, float)) or not math.isfinite(v) or v < 0:
            raise ValueError(f"Weight for {k} must be a non-negative number")
    total = sum(w.values())
    if total <= 0:
        raise ValueError("At least one weight must be positive")
    return {k: v * 100 / total for k, v in w.items()}


def score(row: Mapping, weights: Mapping[str, float] | None = None) -> float:
    """Weighted score on 100 points. Dimension values outside 1 to 5 are rejected, not clipped."""
    w = normalize_weights(weights or ORIGINAL_WEIGHTS)
    total = 0.0
    for k, wt in w.items():
        v = row[k]
        if not isinstance(v, (int, float)) or not 1 <= v <= 5:
            raise ValueError(f"{k} must be between 1 and 5, got {v!r}")
        total += wt * v
    return total / 5


def rank(rows: list[dict], weights: Mapping[str, float] | None = None) -> list[dict]:
    """Return rows with `whatif_score` and `whatif_rank`; ties break by name for stability."""
    out = [dict(r, whatif_score=round(score(r, weights), 4)) for r in rows]
    out.sort(key=lambda r: (-r["whatif_score"], r["name"]))
    for i, r in enumerate(out, start=1):
        r["whatif_rank"] = i
    return out


def audit_original(rows: list[dict], tol: float = 0.1) -> list[str]:
    """Differences between the stored Phase 1 score and the recomputed score."""
    return [f"{r['name']}: stored {r['score']} vs computed {score(r):.2f}" for r in rows
            if abs(score(r) - r["score"]) > tol]


NEUTRAL_ENTRY = 3.0


def valuation_unknown(row: Mapping) -> bool:
    v = str(row.get("valuation", "")).lower()
    return "undisclosed" in v or "not verified" in v


def entry_sensitivity(rows: list[dict], neutral: float = NEUTRAL_ENTRY) -> dict[str, list[dict]]:
    """Alternative rankings that stop an unknown valuation from earning an above-neutral entry rating.

    These are sensitivities, not revised scores; Phase 1 values are never modified. Variants:
    original, cap (undisclosed-valuation entry ratings above neutral are held at neutral),
    neutral (every undisclosed-valuation entry rating is set to neutral), no_entry (entry dimension weighted 0).
    """
    def build(transform, weights=None):
        return rank([transform(dict(r)) for r in rows], weights)

    def cap(r):
        if valuation_unknown(r):
            r["entry"] = min(r["entry"], neutral)
        return r

    def neutralize(r):
        if valuation_unknown(r):
            r["entry"] = neutral
        return r

    no_entry = dict(ORIGINAL_WEIGHTS, entry=0)
    return {"original": build(lambda r: r), "cap": build(cap), "neutral": build(neutralize),
            "no_entry": build(lambda r: r, no_entry)}
