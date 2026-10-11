"""SQLite persistence. Parameterized statements only; seeding never erases analyst annotations."""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from . import data_loader as dl
from . import config
from .config import DB_PATH
from .scoring import DEFINITIONS, ORIGINAL_WEIGHTS

GATE_STATUSES = ["Unknown", "In Progress", "Pass", "Fail", "Not Applicable"]

SCHEMA = f"""
CREATE TABLE IF NOT EXISTS companies (
  id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE COLLATE NOCASE, segment TEXT, buyer TEXT,
  capabilities TEXT, public_stage TEXT, funding_event TEXT, funding_event_date TEXT, valuation TEXT,
  financing_comment TEXT, source_ids_raw TEXT, direct_fit TEXT, use_case TEXT, key_risk TEXT,
  recommended_role TEXT, strategic REAL, workflow REAL, pilot REAL, defensibility REAL, entry REAL,
  confidence REAL, score REAL NOT NULL, original_rank INTEGER);
CREATE TABLE IF NOT EXISTS sources (
  id TEXT PRIMARY KEY, publisher TEXT, date_raw TEXT, claim TEXT, url TEXT, category TEXT,
  limitations TEXT, date_kind TEXT, published TEXT, accessed TEXT, date_note TEXT, url_valid INTEGER,
  original_url TEXT DEFAULT '', correction_note TEXT DEFAULT '', corrected_on TEXT DEFAULT '');
CREATE TABLE IF NOT EXISTS company_source_links (
  company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  source_id TEXT NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
  origin TEXT NOT NULL, PRIMARY KEY (company_id, source_id));
CREATE TABLE IF NOT EXISTS scoring_dimensions (
  key TEXT PRIMARY KEY, weight REAL NOT NULL, definition TEXT);
CREATE TABLE IF NOT EXISTS score_snapshots (
  company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  snapshot TEXT NOT NULL, score REAL NOT NULL, created_at TEXT NOT NULL,
  PRIMARY KEY (company_id, snapshot));
CREATE TABLE IF NOT EXISTS diligence_gates (
  id TEXT PRIMARY KEY, name TEXT, criterion TEXT, current_evidence TEXT, owner TEXT,
  outcome_if_not_met TEXT, origin TEXT NOT NULL CHECK (origin IN ('supplied','proposed')),
  status TEXT NOT NULL DEFAULT 'Unknown' CHECK (status IN ({",".join("'%s'" % s for s in GATE_STATUSES)})),
  evidence_source_ids TEXT DEFAULT '', updated_at TEXT);
CREATE TABLE IF NOT EXISTS gate_history (
  id INTEGER PRIMARY KEY, gate_id TEXT NOT NULL REFERENCES diligence_gates(id),
  old_status TEXT, new_status TEXT, note TEXT, source_ids TEXT, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS analyst_notes (
  id INTEGER PRIMARY KEY, entity_type TEXT NOT NULL, entity_id TEXT NOT NULL, body TEXT NOT NULL,
  author TEXT NOT NULL DEFAULT 'Independent analyst note', created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS claim_flags (
  source_id TEXT PRIMARY KEY REFERENCES sources(id), flagged INTEGER NOT NULL, note TEXT, updated_at TEXT);
CREATE TABLE IF NOT EXISTS decision_records (
  id INTEGER PRIMARY KEY, recommendation TEXT NOT NULL, rationale TEXT NOT NULL,
  analyst_label TEXT, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS import_audit (
  id INTEGER PRIMARY KEY, run_at TEXT NOT NULL, companies INTEGER, sources INTEGER, links INTEGER,
  issues_json TEXT, checksums_json TEXT);
CREATE INDEX IF NOT EXISTS idx_links_source ON company_source_links(source_id);
CREATE INDEX IF NOT EXISTS idx_gates_status ON diligence_gates(status);
CREATE INDEX IF NOT EXISTS idx_notes_entity ON analyst_notes(entity_type, entity_id);
"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class ReadOnlyError(PermissionError):
    """Raised when an analyst write is attempted in read-only (public demo) mode."""


def _guard() -> None:
    if config.is_read_only():
        raise ReadOnlyError("This is a read-only demonstration; edits are disabled.")


def connect(path: Path | str | None = None, shared: bool = False, readonly: bool = False) -> sqlite3.Connection:
    p = Path(path or DB_PATH)
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
    except OSError:  # read-only checkout on a host: fall back to a temp directory
        import tempfile
        p = Path(tempfile.gettempdir()) / "referraliq" / p.name
        p.parent.mkdir(parents=True, exist_ok=True)
    if readonly:  # SQLite refuses every write on this handle, independent of application guards
        con = sqlite3.connect(f"file:{p}?mode=ro", uri=True, check_same_thread=not shared)
    else:
        con = sqlite3.connect(p, check_same_thread=not shared)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


@contextmanager
def tx(con: sqlite3.Connection):
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise


def init_schema(con: sqlite3.Connection) -> None:
    con.executescript(SCHEMA)
    have = {r[1] for r in con.execute("PRAGMA table_info(sources)")}  # migrate databases created before corrections existed
    for col in ("original_url", "correction_note", "corrected_on"):
        if col not in have:
            con.execute(f"ALTER TABLE sources ADD COLUMN {col} TEXT DEFAULT ''")


def seed(con: sqlite3.Connection, load: dl.LoadResult | None = None, gates: list[dict] | None = None,
         competitive: list[dict] | None = None, checksums: dict | None = None) -> dl.LoadResult:
    """Idempotent import in one transaction. Raises (and rolls back) if source integrity fails."""
    load = load or dl.load_package()
    if load.errors:
        raise ValueError("Source integrity errors: " + "; ".join(i.message for i in load.errors))
    gates = gates if gates is not None else dl.workbook_gates()
    competitive = competitive if competitive is not None else dl.workbook_competitive_check()
    init_schema(con)
    ts = now()
    with tx(con):
        for s in load.sources:
            con.execute(
                """INSERT INTO sources (id,publisher,date_raw,claim,url,category,limitations,date_kind,published,accessed,date_note,url_valid,original_url,correction_note,corrected_on)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(id) DO UPDATE SET publisher=excluded.publisher,date_raw=excluded.date_raw,claim=excluded.claim,
                   url=excluded.url,category=excluded.category,limitations=excluded.limitations,date_kind=excluded.date_kind,
                   published=excluded.published,accessed=excluded.accessed,date_note=excluded.date_note,url_valid=excluded.url_valid,
                   original_url=excluded.original_url,correction_note=excluded.correction_note,corrected_on=excluded.corrected_on""",
                (s["id"], s["publisher"], s["date"], s["claim"], s["url"], s["category"], s["limitations"],
                 s["date_kind"], s["published"], s["accessed"], s["date_note"], int(s["url_valid"]),
                 s.get("original_url", ""), s.get("correction_note", ""), s.get("corrected_on", "")))
        ranked = sorted(load.companies, key=lambda c: (-c["score"], c["name"]))
        for i, c in enumerate(ranked, start=1):
            con.execute(
                """INSERT INTO companies (name,segment,buyer,capabilities,public_stage,funding_event,funding_event_date,valuation,
                   financing_comment,source_ids_raw,direct_fit,use_case,key_risk,recommended_role,strategic,workflow,pilot,
                   defensibility,entry,confidence,score,original_rank)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(name) DO UPDATE SET segment=excluded.segment,buyer=excluded.buyer,capabilities=excluded.capabilities,
                   public_stage=excluded.public_stage,funding_event=excluded.funding_event,funding_event_date=excluded.funding_event_date,
                   valuation=excluded.valuation,financing_comment=excluded.financing_comment,source_ids_raw=excluded.source_ids_raw,
                   direct_fit=excluded.direct_fit,use_case=excluded.use_case,key_risk=excluded.key_risk,recommended_role=excluded.recommended_role,
                   strategic=excluded.strategic,workflow=excluded.workflow,pilot=excluded.pilot,defensibility=excluded.defensibility,
                   entry=excluded.entry,confidence=excluded.confidence,score=excluded.score,original_rank=excluded.original_rank""",
                (c["name"], c["segment"], c["buyer"], c["capabilities"], c["public_stage"], c["funding_event"], c["event_date"],
                 c["valuation"], c["financing_comment"], c["source_ids"], c["direct_fit"], c["use_case"], c["key_risk"],
                 c["recommended_role"], c["strategic"], c["workflow"], c["pilot"], c["defensibility"], c["entry"],
                 c["confidence"], c["score"], i))
        ids = {r["name"]: r["id"] for r in con.execute("SELECT id,name FROM companies")}
        for l in load.links:
            con.execute("INSERT OR IGNORE INTO company_source_links VALUES (?,?,?)",
                        (ids[l["company"]], l["source_id"], l["origin"]))
        # Memo-cited links from the workbook competitive check (supplemental, labeled by origin).
        valid_src = {s["id"] for s in load.sources}
        for row in competitive:
            cid = ids.get(str(row.get("Option", "")).strip())
            if cid is None:
                continue
            for sid in dl.split_ids(str(row.get("Source IDs", ""))):
                if sid in valid_src:
                    con.execute("INSERT OR IGNORE INTO company_source_links VALUES (?,?,?)",
                                (cid, sid, "workbook COMPETITIVE CHECK"))
        for k, w in ORIGINAL_WEIGHTS.items():
            con.execute("INSERT INTO scoring_dimensions VALUES (?,?,?) ON CONFLICT(key) DO UPDATE SET weight=excluded.weight,definition=excluded.definition",
                        (k, w, DEFINITIONS[k]))
        for c in load.companies:
            con.execute("INSERT INTO score_snapshots VALUES (?,?,?,?) ON CONFLICT(company_id,snapshot) DO UPDATE SET score=excluded.score",
                        (ids[c["name"]], "phase1_original", c["score"], ts))
        for g in gates:
            # status is deliberately NOT updated on conflict, so reviewer progress survives re-seeding.
            con.execute(
                """INSERT INTO diligence_gates (id,name,criterion,current_evidence,owner,outcome_if_not_met,origin,status)
                   VALUES (?,?,?,?,?,?, 'supplied', 'Unknown')
                   ON CONFLICT(id) DO UPDATE SET name=excluded.name,criterion=excluded.criterion,
                   current_evidence=excluded.current_evidence,owner=excluded.owner,outcome_if_not_met=excluded.outcome_if_not_met""",
                (g["ID"], g["Gate"], g["Specific success criterion"], g["Current evidence"], g["Owner to ask"], g["Outcome if not met"]))
        con.execute("INSERT INTO import_audit (run_at,companies,sources,links,issues_json,checksums_json) VALUES (?,?,?,?,?,?)",
                    (ts, len(load.companies), len(load.sources), len(load.links),
                     json.dumps([i.__dict__ for i in load.issues]), json.dumps(checksums or {})))
    return load


# ---- reads -------------------------------------------------------------------------------
def companies(con) -> list[dict]:
    return [dict(r) for r in con.execute("SELECT * FROM companies ORDER BY original_rank")]


def sources(con) -> list[dict]:
    return [dict(r) for r in con.execute("SELECT * FROM sources ORDER BY id")]


def company_sources(con, company_id: int) -> list[dict]:
    q = """SELECT s.*, l.origin AS link_origin FROM company_source_links l JOIN sources s ON s.id=l.source_id
           WHERE l.company_id=? ORDER BY s.id"""
    return [dict(r) for r in con.execute(q, (company_id,))]


def source_company_map(con) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for r in con.execute("SELECT l.source_id, c.name FROM company_source_links l JOIN companies c ON c.id=l.company_id ORDER BY c.name"):
        out.setdefault(r["source_id"], []).append(r["name"])
    return out


def gates(con) -> list[dict]:
    rows = [dict(r) for r in con.execute("SELECT * FROM diligence_gates ORDER BY id")]
    if config.is_read_only():  # public demo always shows the canonical state, never local edits
        for r in rows:
            r.update(status="Unknown", evidence_source_ids="", updated_at=None)
    return rows


def gate_history(con, gate_id: str | None = None) -> list[dict]:
    if config.is_read_only():
        return []
    if gate_id:
        cur = con.execute("SELECT * FROM gate_history WHERE gate_id=? ORDER BY id DESC", (gate_id,))
    else:
        cur = con.execute("SELECT * FROM gate_history ORDER BY id DESC")
    return [dict(r) for r in cur]


def notes(con, entity_type: str | None = None, entity_id: str | None = None) -> list[dict]:
    if config.is_read_only():
        return []
    if entity_type:
        cur = con.execute("SELECT * FROM analyst_notes WHERE entity_type=? AND entity_id=? ORDER BY id DESC", (entity_type, entity_id))
    else:
        cur = con.execute("SELECT * FROM analyst_notes ORDER BY id DESC")
    return [dict(r) for r in cur]


def flags(con) -> dict[str, dict]:
    if config.is_read_only():
        return {}
    return {r["source_id"]: dict(r) for r in con.execute("SELECT * FROM claim_flags WHERE flagged=1")}


def decisions(con) -> list[dict]:
    if config.is_read_only():
        return []
    return [dict(r) for r in con.execute("SELECT * FROM decision_records ORDER BY id DESC")]


def last_audit(con) -> dict | None:
    r = con.execute("SELECT * FROM import_audit ORDER BY id DESC LIMIT 1").fetchone()
    return dict(r) if r else None


# ---- writes ------------------------------------------------------------------------------
def add_note(con, entity_type: str, entity_id: str, body: str) -> None:
    _guard()
    body = (body or "").strip()
    if not body:
        raise ValueError("Note is empty")
    with tx(con):
        con.execute("INSERT INTO analyst_notes (entity_type,entity_id,body,created_at) VALUES (?,?,?,?)",
                    (entity_type, entity_id, body, now()))


def set_gate_status(con, gate_id: str, status: str, note: str, source_ids: list[str]) -> None:
    _guard()
    if status not in GATE_STATUSES:
        raise ValueError(f"Unknown status {status}")
    known = {r["id"] for r in con.execute("SELECT id FROM sources")}
    bad = [s for s in source_ids if s not in known]
    if bad:
        raise ValueError(f"Unknown source ids: {', '.join(bad)}")
    row = con.execute("SELECT status FROM diligence_gates WHERE id=?", (gate_id,)).fetchone()
    if row is None:
        raise ValueError(f"Unknown gate {gate_id}")
    ts = now()
    with tx(con):
        con.execute("UPDATE diligence_gates SET status=?, evidence_source_ids=?, updated_at=? WHERE id=?",
                    (status, ";".join(source_ids), ts, gate_id))
        con.execute("INSERT INTO gate_history (gate_id,old_status,new_status,note,source_ids,created_at) VALUES (?,?,?,?,?,?)",
                    (gate_id, row["status"], status, note, ";".join(source_ids), ts))


def set_flag(con, source_id: str, flagged: bool, note: str = "") -> None:
    _guard()
    with tx(con):
        con.execute("""INSERT INTO claim_flags VALUES (?,?,?,?)
                       ON CONFLICT(source_id) DO UPDATE SET flagged=excluded.flagged,note=excluded.note,updated_at=excluded.updated_at""",
                    (source_id, int(flagged), note, now()))


def add_decision(con, recommendation: str, rationale: str, analyst_label: str = "") -> None:
    _guard()
    if not rationale.strip():
        raise ValueError("A decision record requires a written rationale")
    with tx(con):
        con.execute("INSERT INTO decision_records (recommendation,rationale,analyst_label,created_at) VALUES (?,?,?,?)",
                    (recommendation, rationale.strip(), analyst_label.strip(), now()))
