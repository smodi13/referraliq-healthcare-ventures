# ISSUE_LOG

Updated in Phase 4.5. Phase 4.5 checkpoint: `../checkpoints/referraliq_phase4_baseline.tgz` (sha256 9b10984bb2d8721cc79fafa7306132ee0ad41502458657a01857e85ae40c139b).
Severity scale in Phase 4.5: CRITICAL data exposure or materially wrong analysis; HIGH important workflow broken or essential claim materially unsupported; MEDIUM noticeable functional, provenance or usability problem; LOW cosmetic or minor.

Baseline before Phase 4: 85 tests passed (`audit/baseline_pytest.txt`). Checkpoint archive of the Phase 3 build: `../checkpoints/referraliq_phase3_baseline.tgz` (sha256 875fd6e6809a69f2c31056f6a6703b69ff5a1cc8a10fb1685d3c1486a3733c72).
Severity: BLOCKER unsafe or materially wrong; HIGH important behavior broken; MEDIUM usability or reliability; LOW polish.
No BLOCKER was found. No financial formula or fixture was changed.

## Final disposition of the seven issues left open after Phase 4

| ID | Affected feature | Phase 4.5 finding | Impact on a reviewer | Affects finance / research / deployment | Severity now | Action and evidence | Status |
|---|---|---|---|---|---|---|---|
| P4-101 | Python compatibility | Clean-copy venv, `requirements-dev.txt`, full suite and app start executed on 3.12.1, 3.13.15 and 3.14.3. Python 3.13 was installed by `uv` into the user's uv directory only; system Python untouched. | Hosting version risk | Deployment | LOW | audit/compat_py312.txt, compat_py313.txt, compat_py314.txt; 124 tests passed on each. Recommended runtime 3.12. | RESOLVED |
| P4-102 | Source claim support | All 36 pages read against claims (PDF text extracted); 27 support, 7 partial, 1 not on linked page, 1 inaccessible. No central memo claim unsupported. 16 of 36 page dates confirmed on page. | Credibility of evidence table | Research | MEDIUM | SOURCE_VERIFICATION_REPORT.md, audit/source_review.json | OPEN (reduced): publication dates and S07, S32 need a human browser read |
| P4-103 | Widget state | Screener filters now survive page changes (browser verified: 6 of 12 kept after round trip). Edited pilot and venture inputs deliberately reset to the frozen preset; verified no stale or hidden state (cash realization 30% then navigate away and back returns base values; overview stays on frozen preset). | Minor convenience | None | LOW | tests/test_ui_smoke.py, browser run | RESOLVED by fix and by design |
| P4-104 | Console 404s | `/pilot/_stcore/health` and `host-config` 404 on cold subpath loads; app renders and works. | None visible | None | LOW | browser console logs | ACCEPTED (Streamlit behavior) |
| P4-105 | Accessibility | Tab order logical; buttons show focus rings; sidebar links had no ring, now have an explicit 2px outline (verified). Chart text descriptions added under five charts. Not a full WCAG audit. | Inclusive use | None | LOW | browser keyboard run, UI_REVIEW.md | OPEN (partial): no screen reader pass |
| P4-106 | S15, S26, S28 | S15 index page does not state the $50M; S26 index page does not state the $1.2B valuation and the registry date is one day earlier than the release; S28 PDF read and supports 24 vs 10 minutes on page 7. | Two citations point at index pages | Research | MEDIUM (S15, S26), resolved (S28) | Replacements proposed in data_proposed/source_corrections_proposed.csv; originals untouched | S28 RESOLVED; S15, S26 OPEN pending analyst approval |
| P4-107 | Public deployment | Not deployed by instruction. Locally simulated: clean copy with fresh DB in read-only mode serves health ok on 3.12, 3.13 and 3.14; real read-only server with a DB containing private notes showed none and showed gates Unknown. | Hosted behavior unconfirmed | Deployment | LOW | audit/compat_*.txt, tests/test_phase45.py | OPEN: NOT VERIFIED on a hosting service |

## New issues found in Phase 4.5

| ID | Component | Sev | Description | Correction | Evidence | Status |
|---|---|---|---|---|---|---|
| P45-001 | Read-only | MEDIUM | Guard was only in Python functions; a bypass of the repository module would still reach a writable SQLite handle. | Read-only mode opens the database with SQLite `mode=ro`; ten write statements (insert, update, delete, drop, pragma) all rejected. | tests/test_phase45.py | RESOLVED |
| P45-002 | Navigation | LOW | Sidebar links had no explicit keyboard focus ring. | CSS outline. | browser run | RESOLVED |
| P45-003 | Deal Screener | LOW | Filters reset on page change. | Persisted via session keys. | browser run | RESOLVED |
| P45-004 | Evidence registry | MEDIUM | Review results for each source were not visible in the app. | Registry columns and detail show analyst review result, date status and any proposed replacement. | views/06 | RESOLVED |
| P45-005 | Gates | LOW | The question "what capabilities, contracts, integrations and workflows already exist within Intermountain" was implicit. | Standing question shown on the gates tab and on the Notable dossier. | tests/test_phase45.py | RESOLVED |
| P45-006 | Sources | LOW | S07 returned 200 on the first check and 403 on the second. Transient access control. | Documented; first-check figures retained. | audit/source_http_check.json | OPEN |
| P45-007 | Register | LOW | S26 registry date (2026-06-24) differs from the release (Jun 25, 2026). S05, S06 and others have dates not visible on the page. | Flagged; original not edited. | SOURCE_VERIFICATION_REPORT.md | OPEN |

Release blockers: none. Unresolved: P4-102, P4-105, P4-106 (S15, S26), P4-107, P45-006, P45-007; accepted: P4-104.

## Phase 4.6: independent review corrections

| ID | Component | Sev | Finding | Correction | Evidence | Status |
|---|---|---|---|---|---|---|
| P46-001 | Read-only | HIGH | Public mode depended on an environment variable being set; omitting it would have enabled editing. | Fail closed: read-only unless `REFERRALIQ_ANALYST_MODE=1`; `REFERRALIQ_PUBLIC`, `REFERRALIQ_READONLY` and the `/mount/src` hosted path always force read-only. Enforced in the repository layer and at the SQLite handle. | tests/test_phase45.py (5 new tests); live default-env server showed no forms | RESOLVED |
| P46-002 | Screening interpretation | MEDIUM | Silna's 4 of 5 entry rating partly rests on an undisclosed valuation, which was read as an attractive price. | Limitation text on Overview and Screener; entry-rating sensitivity (cap, all-neutral, no-entry); Phase 1 scores untouched. Silna #4 original, #6 under each sensitivity. Recommendation unchanged. | tests/test_scoring.py, views/02 | RESOLVED |
| P46-003 | S15 citation | MEDIUM | Index page cited for the $50M Series B. | Approved overlay to the Apr 30, 2025 PR Newswire release; cumulative $76M labeled not a valuation; original URL kept as lineage; stale limitation replaced. | tests/test_phase45.py | RESOLVED |
| P46-004 | S26 citation | MEDIUM | Index page cited for the $1.2B valuation. | Approved overlay to the PR Newswire release (Jun 25, 2026); original announcement June 24, 2026 and correction June 25, 2026 both recorded; valuation labeled company-reported and historical. | tests/test_phase45.py | RESOLVED |
| P46-005 | S28 classification | LOW | Not clear that the PDF is an AHA report sponsored by Ailevate, with CAQH-attributed figures. | Category and limitations updated; explicit that it is not vendor validation or an Intermountain baseline. | tests/test_phase45.py | RESOLVED |
| P46-006 | S07, S32 | LOW | Verification status incomplete. | S07 reached on recheck (200, figures in text); S32 article dated July 16, 2026 confirmed from excerpts, full text not read (403). | SOURCE_VERIFICATION_REPORT.md | S07 RESOLVED; S32 OPEN (full text) |
| P46-007 | Workbook | MEDIUM | MARKET FRAMEWORK showed $0 market size when inputs were missing. | Publication copy shows "Not calculated"; original untouched; only one sheet part differs; scenario sheets reconcile after LibreOffice recalculation. | tests/test_publication_workbook.py | RESOLVED |
| P46-008 | Evidence labels | MEDIUM | "Verified fact" was applied to company announcements. | Six labels: reported, verified (official or independent), vendor-reported, analyst judgment, modeled, unverified. | tests/test_ui_smoke.py | RESOLVED |

Release blockers after Phase 4.6: none. Remaining open: P4-102 (dates on page), P4-105 (screen reader pass), P4-107 (hosted test), P45-006, P45-007 (registry date notes), S32 full text.

## Resolved in Phase 4 (unchanged)

| ID | Component | Sev | Description and reproduction | Root cause | Correction | Evidence |
|---|---|---|---|---|---|---|
| P4-001 | Read-only mode | HIGH | With `REFERRALIQ_READONLY=1` only buttons were hidden. Calling the repository write functions still persisted data, and a copied local DB would have shown private notes and gate edits publicly. | Guard lived in the UI layer, flag read once at import. | `ReadOnlyError` guard in every write function; read-only views return canonical Unknown gate state and no notes, flags, decisions or history; flag evaluated at call time. | tests/test_phase4_audit.py (4 tests), test_ui_smoke read-only test |
| P4-002 | Navigation | MEDIUM | Opening `/pilot` in a cold tab showed a "Page not found" dialog. | Legacy `pages/` directory auto-discovery conflicted with `st.navigation`. | Renamed `pages/` to `views/`. | audit/screenshots/deeplink_cold_pilot.png; 36 page loads without dialog |
| P4-003 | Company Diligence | HIGH | Selecting a company in the Deal Screener, then opening Diligence, kept showing the previously viewed company. | Selectbox kept its own keyed state, ignoring the pushed selection. | Push selection into widget state when it changes externally. | tests/test_ui_smoke.py::test_diligence_follows_selection_from_other_page |
| P4-004 | Finance engine | MEDIUM | Input 1e308 pilot cases returned infinite outputs without an error. | Validation checked inputs, not outputs. | Output finiteness guard raises a clear message. | FINANCIAL_RECONCILIATION.md edge table, test_phase4_audit |
| P4-005 | Theme | MEDIUM | Dark system theme was ignored (theme config forced light); navy chart bars were invisible on dark. | `[theme]` without dark variant; fixed navy. | `[theme.light]` and `[theme.dark]`; mid-slate chart colors; tag text inherits theme color. | audit/screenshots/matrix_*_dark.png |
| P4-006 | Evidence page | MEDIUM | Registry table hid claim, limitations and URL beyond the fold; 36 expanders made the page very long. | Column order and expander loop. | Reordered columns, added authorship class and link-check column, single source detail selector. | 06_evidence_1440_light.png |
| P4-007 | Deal Screener | MEDIUM | Risk, evidence and gaps columns were off screen. | Column order. | Reordered; added independent-source count. | 02_screener_1440_light.png |
| P4-008 | Evidence quality | MEDIUM | 11 of 12 companies are supported only by vendor or company-authored sources; this was not visible. | Missing authorship classification. | `evidence_class`, dossier warning, screener column. | audit/company_audit.json |
| P4-009 | Formatting | LOW | Negative currency used a minus sign, inconsistent with the workbook. | Formatter. | Parentheses, e.g. ($39,834). | tests/test_formatting.py |
| P4-010 | Pilot page | LOW | Downside max vendor fee showed -$2,260 with no explanation. | Raw number. | Explicit "no fee preserves 1.20x" message; added break-even minutes and rollout payback matching the workbook. | tests/test_phase4_audit.py::test_workbook_extra_metrics_reconcile |
| P4-011 | Data access | LOW | One SQLite connection leaked per rerun. | Connection per call. | One connection per browser session. | ResourceWarning count reduced |
| P4-012 | Diligence copy | LOW | "Notable item below" appeared on every dossier. | Static text. | Reworded. | code |
| P4-013 | Overview | LOW | Status tags wrapped; narrow screens overflowed horizontally in the brief table. | CSS. | nowrap on desktop, wrap and tighter padding under 640 px. | matrix run, overflow false |
| P4-014 | Overview | MEDIUM | No fast answer to the seven investor questions; claims lacked a status class. | Design gap. | 90-second brief table and four evidence-status labels (verified fact, analyst interpretation, illustrative assumption, unverified). | 01_overview_1440_light.png |
| P4-015 | Test suite | LOW | Smoke tests relied on legacy page discovery to switch pages. | AppTest limitation. | Direct page harness with stubbed `page_link`. | tests/test_ui_smoke.py |

