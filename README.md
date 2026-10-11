# ReferralIQ | Healthcare Venture Investment Intelligence

Independent candidate research project. It was not prepared, commissioned or endorsed by Intermountain Health or Intermountain
Ventures and is not connected to any of their systems. Research as of October 10, 2026. Financial model contract 2.0.0.

**Live dashboard:** https://referraliq-healthcare-ventures.streamlit.app
**Source code:** https://github.com/smodi13/referraliq-healthcare-ventures

## Research objective

Evaluate AI-powered referral and prior authorization automation from the perspective of a strategic healthcare investor: should a
health-system venture group explore equity in a vendor, run a controlled commercial pilot, evaluate alternatives, or wait for
evidence? The commercial decision and the equity decision are kept separate.

## Investment recommendation

**ADVANCE TO DILIGENCE.** This is not an investment approval.

- **Silna Health:** priority equity diligence candidate (a diligence hypothesis, not a verified superior investment).
- **Tennr:** commercial and product benchmark.
- **Rhyme:** payer-provider workflow comparator.
- **Notable:** historical Intermountain relationship (2020 to 2021 public evidence); current contract status and scope unknown.
- No equity recommendation without verified company metrics, customer references and acceptable entry terms.

## What is in the dashboard

| Page | Purpose |
|---|---|
| Investment Overview | Recommendation, 90-second brief, strengths and risks, evidence labels, document downloads |
| Deal Screener | 12 companies, filters, Phase 1 scores, what-if weights, entry-rating sensitivity, CSV export |
| Company Diligence | Dated financing disclosures, source-linked claims, unknowns, competitor comparison |
| Pilot Economics | 90-day pilot, annual run-rate, first scaled year, break-even, sensitivity (hypothetical inputs) |
| Venture Returns | Ownership, dilution, exit value, gross MOIC and IRR, heatmap, 3.0x reverse underwriting (hypothetical) |
| Evidence and Gates | 36-source registry with review status, ten diligence gates (all Unknown) |

## Evidence

- **12 companies** in the Phase 1 screen; scores are analyst judgments (weights 25/20/15/15/15/10), not predictions.
- **36 source records** with publisher, historical date, limitations, link check and an analyst read. Three citations were corrected
  through an approved overlay (`data_corrections/`) with the original URL kept as lineage; `data/source_register.csv` is unchanged.
- Six evidence labels are used: reported, verified, vendor-reported, analyst judgment, modeled, unverified.

## Financial model

Frozen contract in `model_contract.json`; golden outputs in `model_fixtures.json`. The Excel workbook is the original
(`Pilot_ROI_and_Venture_Model.xlsx`); `publication/` holds a copy whose only change is that the MARKET FRAMEWORK sheet shows
"Not calculated" instead of 0 when inputs are missing. Staff capacity value is not cash savings; the 90-day pilot and the first
scaled year are alternative decisions and are never added together.

## Verified test results

Run on the exact published files with Python 3.12.1 (also passed on 3.13.15 and 3.14.3):

- `python -m pytest -q`: **138 passed**, 0 failed, 0 skipped.
- Financial parity: 54 fixture values across Downside, Base and Upside, **maximum absolute difference 0.0** (tolerance 1e-6).
- Independent closed-form model agrees on 1,000 randomized scenarios; the original workbook recalculated in LibreOffice matches.
- Core coverage 97.1 percent (pytest-cov, `core/` only).
- Source package checksum validation: protected research files unchanged.

## Technology

Python 3.12, Streamlit, Plotly, pandas, SQLite (standard library), openpyxl, pytest. No paid APIs, no secrets.

## Run locally

```bash
git clone https://github.com/smodi13/referraliq-healthcare-ventures.git
cd referraliq-healthcare-ventures
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py        # http://localhost:8501
```

Tests: `pip install -r requirements-dev.txt && python -m pytest -q`.

## Read-only by default

The app is read-only unless local analyst mode is deliberately enabled with `REFERRALIQ_ANALYST_MODE=1`. `REFERRALIQ_PUBLIC=1`,
`REFERRALIQ_READONLY=1` and a hosted checkout path always force read-only. Writes are refused in the data layer and the SQLite
handle is opened read-only. What-if scenario inputs stay interactive and live only in the visitor's session. This is a deployment
safeguard for a research demonstration, not authentication and not a multi-user system. See `DEPLOYMENT_GUIDE.md`.

## Limitations

- Private-company financial data, valuations, round terms, ARR, multiples, dilution and vendor fees are **hypothetical**.
- Company disclosures and case studies are vendor-reported, not independently validated customer outcomes.
- Historical financing announcements do not establish current valuations or open rounds.
- Screening scores are analyst judgments; the universe is not exhaustive.
- Publication dates are not visible on the page for 16 of 36 sources; the Healthcare Dive article (S32) was confirmed from excerpts only.
- No screen-reader accessibility audit has been performed.
- All outputs require a final human investment review.

## More documentation

`REVIEWER_GUIDE.md`, `RED_TEAM_REVIEW.md`, `SOURCE_VERIFICATION_REPORT.md`, `FINANCIAL_RECONCILIATION.md`,
`RELEASE_CANDIDATE_REPORT.md`, `ISSUE_LOG.md`, `DEPLOYMENT_GUIDE.md`.
