# RELEASE_CANDIDATE_REPORT (Phase 4.6)

Release candidate for a GitHub repository and Streamlit hosting. Not pushed, not deployed.

## 1. Changes implemented
| Task | Change |
|---|---|
| Fail-closed read-only | Read-only is the default. Editing needs `REFERRALIQ_ANALYST_MODE=1`. `REFERRALIQ_PUBLIC=1`, `REFERRALIQ_READONLY=1` and a `/mount/src` hosted checkout path force read-only. Enforced by repository guards and a `mode=ro` SQLite handle; private notes, flags, decisions and gate edits never appear. |
| Silna rationale | Screening limitation on Overview and Screener; entry-rating sensitivity (cap, all-neutral, no-entry). Silna #4 on the Phase 1 score; #6 under each sensitivity (tied at 77.0 with Plenful in two of them). Phase 1 scores unchanged; labeled not a revised score. Recommendation unchanged. |
| S15 | Index page replaced by the Apr 30, 2025 PR Newswire release ($50M Series B, $76M cumulative, not a valuation). |
| S26 | Index page replaced by the PR Newswire release (Jun 25, 2026; original announcement June 24, 2026). $1.2B valuation labeled company-reported and historical. |
| S28 | Reclassified as an AHA Trailblazers report sponsored by Ailevate, figures attributed to the 2024 CAQH Index; not vendor validation, not an Intermountain baseline. |
| S07, S32 | S07 re-read on recheck (HTTP 200, $258B in text). S32 article dated July 16, 2026 confirmed from excerpts; full text not read (HTTP 403). |
| Workbook | Publication copy with MARKET FRAMEWORK showing "Not calculated" for missing inputs. Original untouched. |
| Evidence labels | Six labels: reported, verified (official or independent), vendor-reported, analyst judgment, modeled, unverified. |

## 2. Original files preserved
Checksums unchanged for `model_contract.json`, `model_fixtures.json`, `Pilot_ROI_and_Venture_Model.xlsx`, both PDFs, `data/company_screen.csv`, `data/source_register.csv`, `qa/model_validation.py`, `README_FIRST.md`, `PHASE3_CLAUDE_CODE_HANDOFF.md` (`python scripts/validate_source_package.py`; enforced by a test). Corrections are overlays in `data_corrections/`; the workbook copy is in `publication/`. Checkpoints: `../checkpoints/referraliq_phase45_baseline.tgz` (sha256 5a063e3ee140741e0d2504dc165500e6501c2d0a3aa75b873f2a4d7e4752e21e).

## 3. Source corrections completed
S15, S26, S28 applied with lineage (original URL, correction note, approval date). The loaded registry has exactly 36 source IDs and the screen 12 companies. Review: 31 confirmed (4 via excerpt or approved replacement), 5 partial. See SOURCE_VERIFICATION_REPORT.md.

## 4. Financial reconciliation
All 18 fixture keys across Downside, Base and Upside: maximum absolute difference 0.0 (54 values; FINANCIAL_RECONCILIATION.md). Original workbook and the publication copy both recalculate to the fixtures in LibreOffice; every cell of every sheet except MARKET FRAMEWORK D12 and D14 is identical. No input, formula or fixture changed.

## 5. Test results
- `python -m pytest -q`: 138 passed, 0 failed, 0 skipped (audit/phase46_pytest.txt). Core coverage 97.1 percent.
- Python 3.12.1, 3.13.15, 3.14.3: clean venv, full suite, app start with no environment variables (read-only), seed (audit/compat_py31*.txt).
- Suites: financial parity and edge cases, independent model (1,000 random scenarios), scoring and sensitivity, source registry integrity and corrections, database and migration, read-only (function guard, SQLite `mode=ro`, default and hosted overrides), exports, publication workbook, UI smoke.
- Browser (Chromium): default-env server shows read-only and no edit forms; analyst-mode server shows forms; four document downloads byte-identical to their sources; evidence detail for S15, S28, S07 checked; overview and screener visual check.

## 6. Remaining research limitations
All Silna usage and outcome claims are vendor-reported. No verified ARR, margin, retention, terms or round. Notable's current status is unknown (S31, S24 are 2020 to 2021). Publication dates for 16 of 36 sources are not visible on the page. S32 full text not read. Private-company inputs in the model are hypothetical. No screen-reader pass.

## 7. Publication readiness
Ready for your approval. No credentials, no private notes, no database file in the candidate; public seed data is in `data/`, `data_corrections/` and the workbook; startup is clean; Python 3.12 recommended and tested; dependencies pinned; README current; the recommendation remains ADVANCE TO DILIGENCE.

## 8. Exact commands to deploy (after approval)
See DEPLOYMENT_GUIDE.md. Summary:
```bash
unzip ReferralIQ_Release_Candidate.zip && cd ReferralIQ
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements-dev.txt && python -m pytest -q
git init -b main && git add . && git commit -m "ReferralIQ release candidate"
gh repo create referraliq --private --source=. --push
# share.streamlit.io: New app > repo referraliq > branch main > app.py > Python 3.12. Set no secrets or variables.
```

## 9. Approvals still required from you
1. Publication itself (repository creation and hosting account).
2. Repository visibility and license (none included).
3. Whether to keep `audit/` screenshots in the public repository (excluded from this candidate).
4. A browser read of S32 (Healthcare Dive) and page dates for the sources that show none.
