"""Build the sanitized independent-review ZIP from an explicit allowlist, with manifest, secret scan,
absolute-path scan and em dash scan. Usage: python scripts/build_review_package.py OUT.zip"""
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(sys.argv[1])
TOP = sys.argv[2] if len(sys.argv) > 2 else "ReferralIQ_Phase4_Review"
NO_SCREENSHOTS = "--no-screenshots" in sys.argv
EM = chr(0x2014)

INCLUDE_DIRS = ["core", "views", "scripts", "tests", "assets", "data", "data_proposed", "data_corrections", "publication", "qa", "audit", ".streamlit"]
INCLUDE_FILES = [
    "app.py", "requirements.txt", "requirements-dev.txt", ".gitignore", "model_contract.json", "model_fixtures.json",
    "Pilot_ROI_and_Venture_Model.xlsx", "Investment_Committee_Memo.pdf", "Executive_Investment_Brief.pdf",
    "PHASE3_CLAUDE_CODE_HANDOFF.md", "README_FIRST.md", "README.md", "IMPLEMENTATION_REPORT.md", "RELEASE_AUDIT.md",
    "ISSUE_LOG.md", "FINANCIAL_RECONCILIATION.md", "SOURCE_VERIFICATION_REPORT.md", "UI_REVIEW.md", "DEPLOYMENT_GUIDE.md",
    "REVIEWER_GUIDE.md", "REVIEW_BEFORE_SHARING.md", "HANDOFF_FOR_CHATGPT.md", "RED_TEAM_REVIEW.md",
    "INDEPENDENT_REVIEW_PRIORITIES.md", "RELEASE_CANDIDATE_REPORT.md",
]
EXCLUDE_PARTS = {"__pycache__", ".pytest_cache", ".venv", "local_data", ".playwright-mcp", ".git"}
EXCLUDE_SUFFIX = {".pyc", ".db", ".sqlite", ".tgz", ".zip", ".log"}
ORIGINAL = {  # protected Phase 1 and Phase 2 research
    "model_contract.json", "model_fixtures.json", "Pilot_ROI_and_Venture_Model.xlsx", "Investment_Committee_Memo.pdf",
    "Executive_Investment_Brief.pdf", "PHASE3_CLAUDE_CODE_HANDOFF.md", "README_FIRST.md", "data/company_screen.csv",
    "data/source_register.csv", "qa/model_validation.py", "qa/test_results.txt", "qa/workbook_audit.py", "qa/workbook_audit_results.txt",
}
PURPOSE = [
    ("model_contract.json", "Frozen model contract 2.0.0 (canonical inputs and formulas)"),
    ("model_fixtures.json", "Golden numerical fixtures (canonical outputs)"),
    ("data/", "Phase 1 and 2 research datasets (canonical)"),
    ("data_proposed/", "Proposed citation corrections awaiting analyst approval"),
    ("qa/", "Original Phase 2 QA oracle and results (never run directly)"),
    (".pdf", "Original investment document"), (".xlsx", "Original financial workbook"),
    ("core/", "Application logic"), ("views/", "Streamlit pages"), ("tests/", "Automated tests"),
    ("scripts/", "Maintenance and audit scripts"), ("assets/", "Styling"), (".streamlit/", "Streamlit configuration"),
    ("audit/screenshots/", "Browser review screenshots (app only, no personal data)"), ("audit/", "Audit evidence"),
    ("requirements", "Dependency specification"), (".md", "Documentation or report"), (".py", "Application entry point"),
]
SECRET = re.compile(r"(AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|xox[bp]-[A-Za-z0-9-]+|-----BEGIN [A-Z ]*PRIVATE KEY|"
                    r"(?i:(api[_-]?key|secret|password|token))\s*[=:]\s*['\"][^'\"\s]{8,})")
ABS = re.compile(r"/Users/[A-Za-z0-9_.-]+|/private/(tmp|var)/|/var/folders/|C:\\\\Users")
IP = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")


def purpose(rel: str) -> str:
    for key, text in PURPOSE:
        if rel.startswith(key) or rel.endswith(key) or rel == key:
            return text
    return "Supporting file"


def collect() -> list[Path]:
    files = []
    for d in INCLUDE_DIRS:
        for p in sorted((ROOT / d).rglob("*")):
            if NO_SCREENSHOTS and "screenshots" in p.relative_to(ROOT).parts:
                continue
            if p.is_file() and not (set(p.relative_to(ROOT).parts) & EXCLUDE_PARTS) and p.suffix not in EXCLUDE_SUFFIX:
                files.append(p)
    for f in INCLUDE_FILES:
        if (ROOT / f).exists():
            files.append(ROOT / f)
    # compat logs are plain text and are included even though *.log is excluded elsewhere
    return sorted(set(files))


def main() -> int:
    problems, rows = [], []
    for p in collect():
        rel = p.relative_to(ROOT).as_posix()
        data = p.read_bytes()
        if p.suffix.lower() in {".md", ".py", ".txt", ".json", ".csv", ".toml", ".css", ".gitignore", ""} and rel not in ORIGINAL:
            txt = data.decode("utf-8", "ignore")
            if SECRET.search(txt):
                problems.append(f"possible secret pattern in {rel}")
            if ABS.search(txt) and not rel.startswith("tests/") and rel != "scripts/build_review_package.py":
                problems.append(f"absolute path pattern in {rel}")
            if EM in txt:
                problems.append(f"em dash in {rel}")
        rows.append(dict(path=rel, bytes=len(data), purpose=purpose(rel), sha256=hashlib.sha256(data).hexdigest(),
                         source_type="original research" if rel in ORIGINAL else "generated or new",
                         canonical=rel in ORIGINAL))
    if problems:
        print("\n".join(problems))
        return 1
    manifest = dict(project="ReferralIQ", package="Phase 4.6 package", as_of="2026-10-10", files=rows)
    md = ["# PACKAGE_MANIFEST", "", f"{len(rows)} files. Canonical means a protected Phase 1 or Phase 2 original, unmodified (checksummed in audit/source_inventory.json).", "",
          "| Path | Bytes | Purpose | Type | Canonical | SHA-256 |", "|---|---|---|---|---|---|"]
    md += [f"| {r['path']} | {r['bytes']} | {r['purpose']} | {r['source_type']} | {'yes' if r['canonical'] else 'no'} | {r['sha256']} |" for r in rows]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        OUT.unlink()
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for r in rows:
            z.write(ROOT / r["path"], f"{TOP}/{r['path']}")
        z.writestr(f"{TOP}/PACKAGE_MANIFEST.md", "\n".join(md) + "\n")
        z.writestr(f"{TOP}/PACKAGE_MANIFEST.json", json.dumps(manifest, indent=2))
    (OUT.with_name(OUT.stem + "_MANIFEST.json")).write_text(json.dumps(manifest, indent=2))
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes, {len(rows)} files + 2 manifests)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
