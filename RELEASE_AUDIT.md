# RELEASE_AUDIT

Date: October 10, 2026 (model as-of date). Python 3.14.3, Streamlit 1.56.0. This audit challenged the Phase 3 build rather than trusting its report.

## Evidence summary

| Item | Result | Evidence |
|---|---|---|
| Automated tests | 124 passed, 0 failed, 0 skipped on Python 3.12.1, 3.13.15, 3.14.3 | audit/compat_py31*.txt, audit/phase45_pytest.txt |
| Core coverage (pytest-cov) | 97.4 percent of 696 statements in `core/`; view files not measured | audit/coverage.json |
| Fixture parity (app) | max absolute difference 0.0 over 54 values | FINANCIAL_RECONCILIATION.md, audit/finance_parity_report.json |
| Workbook parity | LibreOffice recalculation of the original workbook matches fixtures to 1e-6 | FINANCIAL_RECONCILIATION.md |
| Random cross-check | 1,000 multi-input scenarios, relative diff below 1e-9 vs an independent model | tests/test_phase4_audit.py |
| Source integrity | 12 companies, 36 sources, 0 errors, reference checksums unchanged | scripts/validate_source_package.py |
| Source review | 36 read: 27 support claim, 7 partial, 1 not on linked page (S15), 1 inaccessible (S32) | SOURCE_VERIFICATION_REPORT.md |
| Browser matrix | 36 of 36 loads passed | UI_REVIEW.md |
| Clean clone | rsync copy, fresh venv per Python version, tests, app start in read-only mode | audit/compat_py3*.txt |
| Secrets and paths scan | none found | grep scan, test_exports |
| Em dash scan | none in project files | tests/test_data_integrity.py |

## Findings by role
- QA: 15 issues fixed, 7 open and non-blocking (ISSUE_LOG.md).
- Investment analyst: the recommendation follows from the evidence. Strongest support: historical Silna funding (S10) and regulatory catalyst (S04, S35). Weakest: everything about Silna's performance and terms, since all linked evidence is company authored. Most important unknown: incumbent overlap with Notable (G01). Largest valuation uncertainty: no verified ARR or round. Strongest argument against: base pilot and first scaled year are cash negative and pricing headroom is about $90 per month; strongest alternative: Tennr as the product benchmark and the incumbent stack. Evidence that would change the call: documented incumbent gap and verified company metrics. Next action: G01.
- Model auditor: no formula issues. Two oracle conventions kept for parity (zero-denominator ratios return 0; equity factor limited to 0 to 1) with UI labels for the former.
- Security: read-only enforced in the data layer; hidden local analyst data; no secrets; exports escaped.

## Acceptance criteria

| # | Criterion | Status | Note |
|---|---|---|---|
| 1 | Original files preserved | PASS | checksum test |
| 2 | Three scenarios match fixtures | PASS | |
| 3 | Critical financial tests pass | PASS | |
| 4 | Scores reproduce methodology | PASS | max diff 0 |
| 5 | 12 company records accessible | PASS | selector and DB tests |
| 6 | 36 sources accounted for | PASS | |
| 7 | Source validation documented | PASS | link level only; claim support NOT VERIFIED by a human |
| 8 | No factual data invented | PASS | no new facts added; content traced to memo, workbook, CSV |
| 9 | Six pages render | PASS | browser and AppTest |
| 10 | Navigation reliable | PASS | deep link, back, forward, reload |
| 11 | Inputs update results | PASS | |
| 12 | Downloads work | PASS | browser download, byte-identical |
| 13 | Desktop, tablet, mobile inspected | PASS | programmatic for all, visual for a subset |
| 14 | Light and dark inspected | PASS | |
| 15 | No blocking browser errors | PASS | only P4-104 |
| 16 | No critical security problems | PASS | |
| 17 | Read-only prevents persistent edits | PASS locally (function guard plus SQLite mode=ro) | hosted environment NOT VERIFIED |
| 18 | No secrets or sensitive data | PASS | |
| 19 | Outputs consistent with memo | PASS | FINANCIAL_RECONCILIATION.md |
| 20 | Clean-install start | PASS on 3.12.1, 3.13.15, 3.14.3 | P4-101 resolved |
| 21 | Uncertainties disclosed | PASS | |
| 22 | No em dash | PASS | |
| 23 | Independence disclosed | PASS | every page and sidebar |
| 24 | Deploy and review docs | PASS | DEPLOYMENT_GUIDE.md, REVIEWER_GUIDE.md |
| 25 | Issues documented by severity | PASS | ISSUE_LOG.md |

Release status: ready for human review. Not published. Public deployment requires your approval.

## Phase 4.5 addendum
- Source review of all 36 records, with S15, S26, S28 resolved or proposed (SOURCE_VERIFICATION_REPORT.md, data_proposed/).
- Read-only now also opens SQLite with `mode=ro` (ten write statements rejected in tests).
- Live read-only server run against a database holding private notes, a Fail gate and a decision record showed none of them.
- Browser: pilot edit, leave, return shows base values and no stale state; screener filters persist; screener, evidence, gate and venture CSV downloads checked for local paths (none); keyboard tab order logical, focus ring added to sidebar links.
- Red-team review and independent review priorities added. No change to the recommendation.
- Release status: ready for independent review. Not deployed. Open items: ISSUE_LOG.md.

## Phase 4.6 addendum (independent review corrections)
- Read-only fails closed (default, analyst opt-in, public flag and hosted-path overrides), verified on live servers started with and without the opt-in.
- Silna entry-rating limitation and sensitivity added; Phase 1 scores and the recommendation unchanged.
- S15, S26, S28 corrections applied as an approved overlay with lineage; the raw register file is unchanged (checksummed).
- Publication workbook copy built by patching one sheet part; scenario sheets reconcile; original untouched.
- Evidence labels reduced to six analyst-recognizable classes.
- Test results: audit/phase46_pytest.txt, audit/compat_py31*.txt. Financial parity unchanged (max difference 0.0).
