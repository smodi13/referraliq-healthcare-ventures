"""Project metadata and stable paths. All paths resolve relative to this file."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
AUDIT_DIR = ROOT / "audit"

COMPANY_CSV = DATA_DIR / "company_screen.csv"
SOURCE_CSV = DATA_DIR / "source_register.csv"
CORRECTIONS_CSV = ROOT / "data_corrections" / "source_corrections_approved.csv"  # approved overlay; originals untouched
CONTRACT_JSON = ROOT / "model_contract.json"
FIXTURES_JSON = ROOT / "model_fixtures.json"
WORKBOOK = ROOT / "Pilot_ROI_and_Venture_Model.xlsx"  # original, never modified
PUBLICATION_WORKBOOK = ROOT / "publication" / "Pilot_ROI_and_Venture_Model_PUBLICATION_COPY.xlsx"
MEMO_PDF = ROOT / "Investment_Committee_Memo.pdf"
BRIEF_PDF = ROOT / "Executive_Investment_Brief.pdf"
MANIFEST_JSON = AUDIT_DIR / "source_inventory.json"

# Immutable Phase 2 reference artifacts (checksummed in audit/source_inventory.json).
REFERENCE_FILES = [
    "model_contract.json", "model_fixtures.json", "Pilot_ROI_and_Venture_Model.xlsx",
    "Investment_Committee_Memo.pdf", "Executive_Investment_Brief.pdf",
    "data/company_screen.csv", "data/source_register.csv",
    "qa/model_validation.py", "PHASE3_CLAUDE_CODE_HANDOFF.md", "README_FIRST.md",
]

DB_PATH = Path(os.environ.get("REFERRALIQ_DB", ROOT / "local_data" / "referraliq.db"))
# Hosted showcase mode: hides every editing control.
_TRUE = {"1", "true", "yes"}


def _env(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in _TRUE


def hosted_checkout() -> bool:
    """True when the code runs from the Streamlit Community Cloud checkout path."""
    return str(ROOT).startswith("/mount/src")


def is_read_only() -> bool:
    """Fail closed: the app is read-only unless local analyst mode is deliberately enabled.

    Editing needs REFERRALIQ_ANALYST_MODE=1. REFERRALIQ_PUBLIC=1 (or the legacy REFERRALIQ_READONLY=1) and a hosted
    checkout path always win over analyst mode. Evaluated at call time. This is a deployment safeguard, not authentication.
    """
    if _env("REFERRALIQ_PUBLIC") or _env("REFERRALIQ_READONLY") or hosted_checkout():
        return True
    return not _env("REFERRALIQ_ANALYST_MODE")

AS_OF = "2026-10-10"
AS_OF_LABEL = "October 10, 2026"
MODEL_VERSION = "2.0.0"
DEFAULT_RECOMMENDATION = "ADVANCE TO DILIGENCE"

DISCLAIMER = (
    "Independent candidate research project. Not prepared, commissioned or endorsed by "
    "Intermountain Health or Intermountain Ventures, and not connected to any of their systems."
)
