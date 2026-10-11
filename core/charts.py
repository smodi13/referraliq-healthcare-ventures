"""Plotly figure builders. Colors: navy, slate, teal, muted brick for negatives, amber for caution."""
from __future__ import annotations

import plotly.graph_objects as go

NAVY, SLATE, TEAL, NEG, AMBER = "#5B7089", "#8697AB", "#087F8C", "#B4442F", "#B7791F"
_LAYOUT = dict(margin=dict(l=10, r=10, t=50, b=10), font=dict(size=13), hoverlabel=dict(font_size=12))


def _fig(title: str, **kw) -> go.Figure:
    f = go.Figure()
    f.update_layout(title=dict(text=title, font=dict(size=15)), **_LAYOUT, **kw)
    return f


def waterfall(title: str, steps: list[tuple[str, float, str]], unit: str = "USD") -> go.Figure:
    """steps: (label, value, measure) with measure in relative | total."""
    f = _fig(title, yaxis_title=unit, showlegend=False, yaxis_tickformat="$,.0f")
    run, shown = 0.0, []
    for _, v, m in steps:  # totals display the running sum, not their placeholder value
        run += v if m == "relative" else 0
        shown.append(run if m == "total" else v)
    f.add_trace(go.Waterfall(
        x=[s[0] for s in steps], y=[s[1] for s in steps], measure=[s[2] for s in steps],
        text=[(f"(${abs(v):,.0f})" if v < 0 else f"${v:,.0f}") for v in shown], textposition="outside",
        increasing=dict(marker=dict(color=TEAL)), decreasing=dict(marker=dict(color=NEG)),
        totals=dict(marker=dict(color=NAVY)), connector=dict(line=dict(color=SLATE, width=1)),
        hovertemplate="%{x}: %{y:$,.0f}<extra></extra>"))
    return f


def grouped_bars(title: str, categories: list[str], series: dict[str, list[float]], unit: str, colors=None) -> go.Figure:
    f = _fig(title, yaxis_title=unit, barmode="group", legend=dict(orientation="h", y=-0.15),
              yaxis_tickformat="$,.0f" if unit.startswith("USD") else ",.0f")
    palette = colors or [NAVY, TEAL, AMBER, SLATE]
    for (name, vals), c in zip(series.items(), palette):
        f.add_bar(x=categories, y=vals, name=name, marker_color=c,
                  hovertemplate=f"{name}<br>%{{x}}: %{{y:,.0f}} {unit}<extra></extra>")
    f.add_hline(y=0, line_color=SLATE, line_width=1)
    return f


def hbar(title: str, labels: list[str], values: list[float], xtitle: str, colors: list[str] | None = None,
         text_fmt: str = "%{x:.1f}") -> go.Figure:
    f = _fig(title, xaxis_title=xtitle, yaxis=dict(autorange="reversed"), showlegend=False,
             height=max(320, 34 * len(labels) + 90))
    f.add_bar(y=labels, x=values, orientation="h", marker_color=colors or TEAL,
              texttemplate=text_fmt, textposition="outside", cliponaxis=False,
              hovertemplate="%{y}: %{x:.1f}<extra></extra>")
    return f


def heatmap(title: str, z, x, y, xtitle: str, ytitle: str, fmt: str, midpoint: float | None = None,
            ztitle: str = "") -> go.Figure:
    f = _fig(title, xaxis_title=xtitle, yaxis_title=ytitle)
    flat = [v for r in z for v in r]
    kw: dict = {}
    scale = "Blues"
    if midpoint is not None:
        lo, hi = min(min(flat), midpoint), max(max(flat), midpoint)
        frac = (midpoint - lo) / (hi - lo) if hi > lo else 0.0
        kw = dict(zmin=lo, zmax=hi)
        scale = ([[0, NEG], [frac, "#F2F2F2"], [1, TEAL]] if 0 < frac < 1 else [[0, "#F2F2F2"], [1, TEAL]])
    f.add_trace(go.Heatmap(
        z=z, x=[str(v) for v in x], y=[str(v) for v in y], colorscale=scale, **kw,
        text=[[format(v, fmt) for v in r] for r in z], texttemplate="%{text}",
        colorbar=dict(title=ztitle), hovertemplate=f"{xtitle}: %{{x}}<br>{ytitle}: %{{y}}<br>value: %{{text}}<extra></extra>"))
    return f


def line_ramp(title: str, months: list[str], values: list[float], ytitle: str) -> go.Figure:
    f = _fig(title, yaxis_title=ytitle, showlegend=False)
    f.add_bar(x=months, y=values, marker_color=TEAL, text=[f"{v:,.0f}" for v in values], textposition="outside",
              hovertemplate="%{x}: %{y:,.1f} " + ytitle + "<extra></extra>")
    return f
