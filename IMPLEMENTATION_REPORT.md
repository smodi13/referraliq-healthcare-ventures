> Superseded in part by Phase 4: see RELEASE_AUDIT.md and ISSUE_LOG.md. Pages now live in `views/`; test count is 106.

# ReferralIQ Implementation Report

Python 3.14.3, Streamlit 1.56.0, Plotly 6.6.0, pandas 3.0.1, pytest 9.1.1. Model contract 2.0.0, research as of October 10, 2026.

## Architecture
- `core/financial_math.py` pure finance engine (no Streamlit); `scenarios.py` frozen presets and field metadata
- `core/data_loader.py`, `repository.py` (SQLite), `scoring.py`, `exports.py`, `formatting.py`, `charts.py`, `components.py`, `content.py`
- `views/01..06` six Streamlit pages wired through `app.py` `st.navigation`
- `scripts/` seed and read-only validation; `tests/`; `audit/` manifest, parity report, notes, screenshots

## Results
- Source integrity: 12 companies, 36 sources, 0 errors, 12 informational date-precision notes; reference checksums unchanged.
- Parity: all 18 fixture keys for Downside, Base, Upside match with max absolute difference 0.0 (tolerance 1e-6). See `audit/finance_parity_report.json`.
- Tests: 85 passed (see `audit/test_run_summary.md`).
- Live server: `streamlit run app.py` responded `ok` on /_stcore/health and served all pages.

## UI validation actually performed
Real Chromium (Playwright; Phase 4 extended this to all 6 pages at 1440, 1024, 390 and both themes) against the running server: Overview desktop 1440 wide, Pilot Economics, Venture Returns and Deal Screener desktop, Overview at 390 wide (`audit/screenshots/`). Defects found and fixed: LaTeX rendering of paired dollar amounts, incorrect waterfall total labels, misleading negative heatmap scale, truncated screener table, redundant banner copy. NOT visually inspected in a browser: Company Diligence and Evidence and Gates (covered only by AppTest smoke tests), dark theme, 1024 px tablet width.

## Decisions to review
- Gates: the ten workbook gates (G01 to G10) are used verbatim; none were invented.
- Added memo-cited source links for the four shortlist companies from the workbook COMPETITIVE CHECK, labeled by origin.
- Contract field `exit_premoney_m` is shown as the entry pre-money with an explanation.
- Reverse-underwriting and max-vendor-fee helpers are derived algebraically from the contract formulas (verified by test against the engine); they add no new assumptions. The 1.20x hurdle comes from the memo.
- Break-even above 100% is flagged infeasible; zero-denominator ratios show "not calculable" in the UI while parity values follow the oracle.

## Known limitations
See README. Additionally: sub-page deep links opened cold show a harmless Streamlit "Page not found" dialog; URLs not re-fetched; no hosted deployment was made; read-only mode is a flag, not authentication.
