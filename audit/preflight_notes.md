# Preflight notes (October 10, 2026)

- Package: 12 companies, 36 sources, all semicolon source ids resolve (21 company-source links from the CSV).
- Stored Phase 1 scores equal sum(weight x rating)/5 with weights 25/20/15/15/15/10 for all 12 rows (max diff 0).
- 12 sources have imprecise dates (7 undated with access date, 1 updated page, 1 annual report, 2 month-only, 1 year-plus-access). Shown as such, never as publication dates.
- Ten diligence gates (G01 to G10) exist only in the workbook DILIGENCE GATES tab; the memo lists a different five-gate summary. The ten workbook gates are used, all start Unknown, none are proposed additions.
- Notable's CSV links are S24 and S25; the workbook COMPETITIVE CHECK also cites S31, S33, S34, S36. These are added as memo-cited links with their origin recorded.
- Contract field `exit_premoney_m` is the ENTRY pre-money despite its name. Kept verbatim and explained in the UI.
- The oracle returns 0 (not infinity) for coverage with zero recurring cost and for break-even with zero capacity. Parity keeps the oracle values; the UI shows "not calculable" labels.
- The oracle requires equity_value_factor in [0, 1]; the same rule is enforced.
- `qa/model_validation.py` rewrites model_fixtures.json when run as a script; it was not executed.
- The working directory sits inside a home-directory git repository with unrelated pending changes; no git operations were performed.
