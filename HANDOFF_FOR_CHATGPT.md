# HANDOFF_FOR_CHATGPT

Self-contained brief for an independent review of ReferralIQ (Phase 4.5, October 10, 2026). Treat every statement here as a claim to verify, not as evidence. Start with `INDEPENDENT_REVIEW_PRIORITIES.md`.

## What this is
ReferralIQ is an independent candidate portfolio project for an Investment Analyst, Ventures role at Intermountain Ventures. It is NOT an Intermountain application, was not commissioned or endorsed by Intermountain Health or Intermountain Ventures, and is not connected to any of their systems. It is built from public sources. All private-company financial scenarios (valuation, round, check, ARR, multiples, dilution, vendor fees, savings) are hypothetical analyst assumptions. It is not a live data feed and the research is not exhaustive.

## Objective
Decide, with traceable evidence, whether to explore (a) an equity investment in Silna Health, (b) a controlled commercial pilot, (c) alternative referral and prior authorization AI vendors, or (d) defer. Commercial and equity decisions are kept separate.

## Current recommendation
ADVANCE TO DILIGENCE. Equity investment not supported by public information. Pilot conditional on confirming the incumbent gap (Notable) and a safety and security review. Roles: Silna (priority equity diligence), Tennr (commercial and product benchmark), Rhyme (payer-provider workflow comparator), Notable (historical Intermountain relationship; current status and scope unknown).

## Architecture
Streamlit 1.56.0, Plotly, pandas, SQLite (stdlib), pytest.
- `app.py`: navigation and chrome. `views/01..06_*.py`: six pages (named `views/` because a `pages/` folder breaks cold deep links).
- `core/financial_math.py`: pure, Streamlit-free finance engine from `model_contract.json` 2.0.0. `core/scenarios.py` frozen presets and field metadata.
- `core/data_loader.py` CSV and workbook import, date classification, authorship classification. `core/repository.py` SQLite schema, idempotent seed, guarded writes, read-only enforcement. `core/scoring.py`, `core/exports.py` (CSV formula escaping), `core/formatting.py`, `core/charts.py`, `core/components.py`, `core/content.py`.
- `scripts/`: seed, package validation (checksums), source HTTP check, source review builder, audit report generator, compatibility check, review package builder.
- `tests/`: 138 tests including an independent closed-form model (`tests/independent_model.py`).

## Authority and protected files
`model_contract.json`, `model_fixtures.json`, `qa/model_validation.py` (never run directly: its `__main__` rewrites the fixtures), `data/company_screen.csv`, `data/source_register.csv`, the two PDFs and the workbook. SHA-256 values are in `audit/source_inventory.json` and enforced by `tests/test_data_integrity.py`. Proposed corrections live separately in `data_proposed/`.

## Methodology
- Screening: 12 companies, six dimensions rated 1 to 5, weights 25/20/15/15/15/10, score = weighted sum / 5 (all 12 stored scores reproduce exactly). Analyst judgment, not prediction. What-if weights never overwrite originals.
- Finance: 90-day pilot (three ramp months, setup once), annual run-rate, first scaled year; capacity value is not cash (cash realization is a separate 0 to 1 input); venture block uses USD millions: post-money, ownership, dilution, exit value, gross MOIC and IRR. Pilot and first scaled year are alternative decisions and never summed.
- Evidence: 36 sources, each with publisher, date, claim, limitations, an HTTP link check and an analyst read (31 confirmed, of which 4 via a search excerpt or an approved replacement rather than the originally linked page; 5 partial).

## Important assumptions (all hypothetical)
Base: 2,000 pilot cases per month, 70% eligible, 60% completed, 7 net minutes saved, $42 per hour, 50% cash realization, pilot fees $3,000 + $1,100 + $550 per month and $30,000 setup; scaled 12,000 cases per month, fees $8,000 + $1,500 + $700 per month, $20,000 rollout, 75% first-year ramp; venture $80M pre-money, $25M round, $2M check, 35% dilution, $80M exit ARR at 6.0x, 6 years.

## How to run and test
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest -q                         # 138 tests expected
streamlit run app.py                         # http://localhost:8501
streamlit run app.py                         # read-only by default (fail closed)
REFERRALIQ_ANALYST_MODE=1 streamlit run app.py   # local analyst editing (opt-in)
python scripts/validate_source_package.py    # checksum and import integrity
```

## Results to verify (not to trust)
- 138 tests pass on Python 3.12.1, 3.13.15 and 3.14.3 (`audit/compat_py31*.txt`). Core coverage 97 percent (`audit/coverage.json`, Phase 4 run).
- Fixture parity: 54 values, max absolute difference 0.0 (`FINANCIAL_RECONCILIATION.md`, `audit/finance_parity_report.json`). Original workbook recalculated in LibreOffice matches. 1,000 random scenarios agree with the independent model.
- Browser matrix 6 pages x 3 widths x 2 themes clean; downloads byte-identical to originals; CSV exports checked.

## Read-only behavior (fail closed, Phase 4.6)
Read-only is the default. Editing requires the deliberate opt-in `REFERRALIQ_ANALYST_MODE=1`; `REFERRALIQ_PUBLIC=1`, `REFERRALIQ_READONLY=1` and a hosted `/mount/src` checkout path always force read-only. In read-only mode every analyst write raises `ReadOnlyError`, SQLite is opened with `mode=ro`, views show canonical Unknown gate state and no notes, flags or decisions, and edit forms are hidden. What-if inputs live only in the visitor's session. Not authentication; not a multi-user system.

## Phase 4.6 changes (response to the independent review)
Fail-closed read-only; Silna entry-rating limitation and sensitivity (Phase 1 scores unchanged); approved citation corrections for S15, S26 and S28 as an overlay with lineage; S07 and S32 re-verified; publication copy of the workbook (MARKET FRAMEWORK shows Not calculated); six evidence labels (reported, verified, vendor-reported, analyst judgment, modeled, unverified). No financial input, formula or fixture changed.

## Known limitations and open items
See `ISSUE_LOG.md`. Open: publication dates unconfirmed for 16 of 36 sources; S32 full text read only through search excerpts; no screen-reader pass; no hosted deployment tested. Not deployed or published.

## Source quality concerns
Evidence for every screened company that has linked sources is dominated by company or vendor authored material. Only Tennr has independent reporting (Fortune, S08). Silna's usage and outcome claims (S11 to S13) are vendor-reported. Notable relationship evidence (S31, S24) is 2020 to 2021; S33 and S34 are vendor case studies; none establishes current status.

## Files that deserve detailed review
`core/financial_math.py`, `tests/independent_model.py`, `tests/test_phase4_audit.py`, `core/repository.py`, `tests/test_phase45.py`, `core/content.py`, `views/01_Investment_Overview.py`, `views/06_Evidence_and_Gates.py`, `SOURCE_VERIFICATION_REPORT.md`, `RED_TEAM_REVIEW.md`, the original memo, brief and workbook.
