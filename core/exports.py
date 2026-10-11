"""Safe CSV export. Cells starting with = + - @ (or tab/CR) are prefixed so Excel treats them as text."""
from __future__ import annotations

import csv
import io
from typing import Iterable

_DANGEROUS = ("=", "+", "-", "@", "\t", "\r")


def safe_cell(v):
    if isinstance(v, str) and v.startswith(_DANGEROUS):
        return "'" + v
    return v


def to_csv(rows: Iterable[dict], columns: list[str]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(columns)
    for r in rows:
        w.writerow([safe_cell(r.get(c, "")) for c in columns])
    return buf.getvalue()
