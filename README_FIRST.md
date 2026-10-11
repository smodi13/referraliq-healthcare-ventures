# ReferralIQ Phase 2 | Independent investment research

**Research as of 10 October 2026. All forward-looking scenario metrics are hypothetical.**

This package includes:

1. `Executive_Investment_Brief.pdf`, one-page attachment for hiring team outreach.
2. `Investment_Committee_Memo.pdf`, six-page institutional-style research memo.
3. `Pilot_ROI_and_Venture_Model.xlsx`, 14-tab auditable workbook with 90-day pilot, scaled operating analysis, venture equity returns, two sensitivity grids, provenance and decision gates.
4. `PHASE3_CLAUDE_CODE_HANDOFF.md`, software implementation specification and copyable development prompt.
5. `model_contract.json`, frozen scenario semantics and input values.
6. `model_fixtures.json`, independently calculated expected outputs for app parity.
7. `qa/model_validation.py`, nine automated finance logic and boundary tests.
8. `data/company_screen.csv` and `data/source_register.csv`, the curated Phase 1 screen and Phase 2 source updates.

## How to audit

Open the Excel workbook in Microsoft Excel. Start with `START HERE`, then review `ASSUMPTIONS`, `PILOT MONTHLY`, `PILOT SUMMARY`, `SCALE ECONOMICS`, `VENTURE INPUTS`, `VENTURE RETURNS`, `DILIGENCE GATES`, and `SOURCE REGISTER`. Blue numbers are *unverified hypothetical inputs*. Green references link across tabs. No model value should be mistaken for private company records.

Run `python qa/model_validation.py`. Expected result: **9 tests passed**. An independent `model_fixtures.json` is written. Compare its base outputs to the visible Excel dashboard. Tests verify invalid assumptions, zero volume, zero cash conversion, dilution, vendor sensitivity and venture boundary returns.

## Core model findings

- Base pilot net cash: **($39,834)** across a three-month evaluation with upfront setup.
- Base scaled run-rate net cash: **$25,776 per year** after recurring fees and oversight.
- Base first scaled year net cash: **($31,268)** after ramp and incremental rollout setup.
- Base recurring benefit / cost: **1.21x**, with break-even cash conversion **41.3%**.
- Base hypothetical venture gross return: **2.97x MOIC / 19.9% gross IRR** over six years.

These numbers are scenario illustrations, not verified company financial results or measured Intermountain operating outcomes. A negative pilot P&L does not automatically invalidate a carefully governed evidence study. A positive run-rate does not automatically justify equity investment.

## Clinical and diligence caveats

All company funding references are historical snapshots, not current financing offers. No vendor price sheet, private startup financials, real internal operating baseline or confidential patient records were used. The current status of the historical Intermountain / Notable collaboration is unverified. CMS-0057-F has payer and service scope limits, including important non-drug distinctions. A robust investment recommendation requires real term sheets, ARR quality, margin, churn, debt and liquidation waterfall details as well as legal and clinical approval.

## Outreach guidance

Send **only the one-page brief as the first attachment**, with a concise invitation to view the complete memo, spreadsheet and optional later dashboard. Describe this as independent candidate research. Avoid attaching a large ZIP in cold outreach; link to a well-labeled project folder instead.
