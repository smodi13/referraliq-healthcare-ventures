"""Load and validate the Phase 2 CSVs and workbook tables without mutating them."""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from .config import COMPANY_CSV, CORRECTIONS_CSV, SOURCE_CSV, WORKBOOK

COMPANY_COLUMNS = [
    "name", "segment", "buyer", "capabilities", "public_stage", "funding_event", "valuation",
    "financing_comment", "source_ids", "direct_fit", "use_case", "key_risk", "recommended_role",
    "strategic", "workflow", "pilot", "defensibility", "entry", "confidence", "score",
]
SOURCE_COLUMNS = ["id", "publisher", "date", "claim", "url", "category", "limitations"]
DIMENSIONS = ["strategic", "workflow", "pilot", "defensibility", "entry", "confidence"]

_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_YM = re.compile(r"^\d{4}-\d{2}$")
_YEAR = re.compile(r"^\d{4}$")
_ACCESSED = re.compile(r"accessed\s+(\d{4}-\d{2}-\d{2})")
_UPDATED = re.compile(r"updated\s+(\d{4}-\d{2}-\d{2})")
_EVENT_DATE = re.compile(r"\(([A-Z][a-z]{2}\s+\d{4}|\d{4})\)")
_EVENT_DATE2 = re.compile(r"\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})\b")


@dataclass
class Issue:
    severity: str  # error | warning | info
    code: str
    message: str
    ref: str = ""


@dataclass
class LoadResult:
    companies: list[dict] = field(default_factory=list)
    sources: list[dict] = field(default_factory=list)
    links: list[dict] = field(default_factory=list)
    issues: list[Issue] = field(default_factory=list)

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == "error"]


def classify_date(raw: str) -> dict:
    """Separate publication date from access date. Never treats access date as publication."""
    s = (raw or "").strip()
    out = dict(kind="unknown", published=None, accessed=None, note="Date could not be classified")
    acc = _ACCESSED.search(s)
    if acc:
        out["accessed"] = acc.group(1)
    if _ISO.match(s):
        try:
            date.fromisoformat(s)
            return dict(kind="published", published=s, accessed=None, note="Publication date")
        except ValueError:
            return dict(kind="invalid", published=None, accessed=None, note="Impossible calendar date")
    if _YM.match(s):
        mm = int(s[5:7])
        if 1 <= mm <= 12:
            return dict(kind="published_month", published=s, accessed=None, note="Publication month only")
        return dict(kind="invalid", published=None, accessed=None, note="Impossible month")
    if _YEAR.match(s):
        return dict(kind="published_year", published=s, accessed=None, note="Publication year only")
    if s.lower().startswith("undated"):
        out.update(kind="undated", note="Undated page; only the access date is known")
        return out
    upd = _UPDATED.search(s)
    if upd:
        out.update(kind="updated", published=s.split("/")[0].strip(), note=f"Year given; page updated {upd.group(1)}")
        return out
    if acc:
        out.update(kind="annual_report", published=s.split("/")[0].strip(), note="Publication period given; access date recorded separately")
        return out
    return out


def parse_event_date(funding_event: str) -> str | None:
    """Extract the stated date of a financing event, or None if the text gives none."""
    m = _EVENT_DATE.search(funding_event or "") or _EVENT_DATE2.search(funding_event or "")
    return m.group(1) if m else None


def _read_csv(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        return list(reader.fieldnames or []), [dict(r) for r in reader]


def evidence_class(category: str) -> str:
    """Coarse authorship class of a source, used to separate vendor claims from independent evidence."""
    c = (category or "").lower()
    if c.startswith("secondary summary"):
        return "Secondary summary"
    if "industry case" in c:
        return "Unclassified"
    if "company" in c or "vendor" in c:
        return "Vendor or company authored"
    if "regulator" in c or c.startswith("primary"):
        return "Official or regulator"
    if any(w in c for w in ("press", "research", "survey", "industry")):
        return "Independent press or research"
    return "Unclassified"


def split_ids(cell: str) -> list[str]:
    return [p.strip() for p in (cell or "").split(";") if p.strip()]


def _apply_corrections(rows: list[dict], path: Path, issues: list) -> None:
    """Overlay approved citation corrections on register rows, keeping the original URL for lineage."""
    if not path.exists():
        return
    by_id = {r["id"]: r for r in rows}
    for c in _read_csv(path)[1]:
        r = by_id.get(c["id"])
        if r is None:
            issues.append(Issue("warning", "correction_target_missing", f"Correction for unknown source {c['id']}", c["id"]))
            continue
        r["original_url"] = r["url"]
        if c.get("new_url"):
            r["url"] = c["new_url"]
        if c.get("new_category"):
            r["category"] = c["new_category"]
        if c.get("limitations_new"):
            r["original_limitations"] = r["limitations"]
            r["limitations"] = c["limitations_new"]
        if c.get("limitations_append"):
            r["limitations"] = (r["limitations"].rstrip(". ") + ". " + c["limitations_append"]).strip()
        r["correction_note"] = c.get("correction_note", "")
        r["corrected_on"] = c.get("approved_on", "")


def load_package(company_csv: Path = COMPANY_CSV, source_csv: Path = SOURCE_CSV, corrections_csv: Path | None = None) -> LoadResult:
    res = LoadResult()
    if corrections_csv is None and Path(source_csv) == SOURCE_CSV:
        corrections_csv = CORRECTIONS_CSV
    c_cols, c_rows = _read_csv(company_csv)
    s_cols, s_rows = _read_csv(source_csv)

    for cols, need, label in ((c_cols, COMPANY_COLUMNS, "company"), (s_cols, SOURCE_COLUMNS, "source")):
        missing = [c for c in need if c not in cols]
        if missing:
            res.issues.append(Issue("error", "missing_columns", f"{label} CSV lacks columns: {', '.join(missing)}"))
    if res.errors:
        return res

    seen_src: set[str] = set()
    for i, r in enumerate(s_rows, start=2):
        sid = (r["id"] or "").strip()
        if not sid:
            res.issues.append(Issue("error", "blank_source_id", f"Source row {i} has no id"))
            continue
        if sid in seen_src:
            res.issues.append(Issue("error", "duplicate_source_id", f"Duplicate source id {sid}", sid))
            continue
        seen_src.add(sid)
        u = urlparse(r["url"] or "")
        url_ok = u.scheme in ("http", "https") and bool(u.netloc)
        if not url_ok:
            res.issues.append(Issue("error", "invalid_url", f"{sid}: URL is not a valid http(s) URL", sid))
        d = classify_date(r["date"])
        if d["kind"] in ("unknown", "invalid"):
            res.issues.append(Issue("warning", "unclassified_date", f"{sid}: {d['note']} ('{r['date']}')", sid))
        elif d["kind"] in ("undated", "updated", "annual_report", "published_month", "published_year"):
            res.issues.append(Issue("info", "imprecise_date", f"{sid}: {d['note']}", sid))
        res.sources.append(dict(r, id=sid, url_valid=url_ok, original_url="", correction_note="", corrected_on="", date_kind=d["kind"],
                                published=d["published"], accessed=d["accessed"], date_note=d["note"]))

    if corrections_csv:
        _apply_corrections(res.sources, Path(corrections_csv), res.issues)
        for s in res.sources:
            s["url_valid"] = urlparse(s["url"]).scheme in ("http", "https")

    seen_names: set[str] = set()
    for i, r in enumerate(c_rows, start=2):
        name = (r["name"] or "").strip()
        if not name:
            res.issues.append(Issue("error", "blank_company_name", f"Company row {i} has no name"))
            continue
        if name.casefold() in seen_names:
            res.issues.append(Issue("error", "duplicate_company", f"Duplicate company {name}", name))
            continue
        seen_names.add(name.casefold())
        row = dict(r, name=name)
        bad = False
        for k in DIMENSIONS:
            try:
                v = float(r[k])
                if not 1 <= v <= 5:
                    raise ValueError
                row[k] = v
            except (TypeError, ValueError):
                res.issues.append(Issue("error", "bad_dimension", f"{name}: {k}='{r[k]}' is not a number from 1 to 5", name))
                bad = True
        try:
            row["score"] = float(r["score"])
        except (TypeError, ValueError):
            res.issues.append(Issue("error", "bad_score", f"{name}: score='{r['score']}' is not numeric", name))
            bad = True
        if bad:
            continue
        row["event_date"] = parse_event_date(r["funding_event"])
        res.companies.append(row)
        ids = split_ids(r["source_ids"])
        if not ids:
            res.issues.append(Issue("warning", "no_sources", f"{name}: no source ids listed", name))
        dup = {x for x in ids if ids.count(x) > 1}
        for d_ in dup:
            res.issues.append(Issue("warning", "duplicate_link", f"{name}: source {d_} listed twice", name))
        for sid in dict.fromkeys(ids):
            if sid not in seen_src:
                res.issues.append(Issue("error", "broken_source_ref", f"{name}: source {sid} not in registry", name))
            else:
                res.links.append(dict(company=name, source_id=sid, origin="company_screen.csv"))
    return res


def workbook_table(sheet: str, header_first_cell: str) -> list[dict]:
    """Read a plain-text table from the Phase 2 workbook (read-only, formulas not evaluated)."""
    import openpyxl

    wb = openpyxl.load_workbook(WORKBOOK, read_only=True, data_only=False)
    rows = [[c for c in r] for r in wb[sheet].iter_rows(values_only=True)]
    wb.close()
    for i, r in enumerate(rows):
        if r and r[0] == header_first_cell:
            hdr = [h for h in r if h is not None]
            out = []
            for rr in rows[i + 1:]:
                if not rr or rr[0] is None:
                    break
                out.append({h: rr[j] for j, h in enumerate(hdr)})
            return out
    raise ValueError(f"Table starting '{header_first_cell}' not found in {sheet}")


def workbook_gates() -> list[dict]:
    return workbook_table("DILIGENCE GATES", "ID")


def workbook_competitive_check() -> list[dict]:
    return workbook_table("COMPETITIVE CHECK", "Option")
