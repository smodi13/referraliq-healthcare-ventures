# ReferralIQ | Phase 3 engineering handoff

**Freeze date:** 2026-10-10  
**Status:** Phase 2 analytical logic frozen at model contract `2.0.0`.  
**Purpose:** Build a professional, source-linked venture sourcing and diligence dashboard around validated public information and clearly labeled scenario analytics.

## 1. The product to build

Build a polished Streamlit application that behaves like a junior investment analyst's research workspace. This is a **candidate-authored independent demonstration**, not software deployed at Intermountain Health and not an endorsement of a named startup. Prefer careful provenance and a clear decision workflow over novelty or AI animations.

**Primary audience:** A managing director, venture principal or investment associate reviewing a healthcare AI investment screen.  
**Primary question:** What is known, what is still unknown, why does Silna warrant diligence, and when would an investment or pilot be justified?  
**Default decision:** `DILIGENCE`, not `INVEST`.

## 2. Handoff files and authority order

| Artifact | Use | Authority |
|---|---|---|
| `model_contract.json` | Exact scenario field IDs and calculation definitions | Canonical model input contract |
| `model_fixtures.json` | Golden reference output cases for parity tests | Canonical numeric outputs |
| `Pilot_ROI_and_Venture_Model.xlsx` | Business-facing, editable model for reviewing results | Spreadsheet presentation of the same contract |
| `qa/model_validation.py` | Independent pure-Python reference and edge-case tests | Test oracle |
| `data/company_screen.csv` | The 12-company Phase 1 initial screen | Time-stamped analyst-curated screen, not a live feed |
| `data/source_register.csv` | 36 source records including added Phase 2 sources | Claim provenance |
| `Investment_Committee_Memo.pdf` | Final analytical context and cautious recommendation | Memo narrative, not app code specification |

Never silently diverge from the JSON contract. If a mathematical assumption or field definition changes, increment the model version, update the workbook and test oracle, and obtain an explicit analyst review.

## 3. Architecture

Use Python 3.12+, Streamlit, Plotly, SQLite, and pytest or unittest. Use Pandas for analysis and CSV import, but preserve the source field IDs from the frozen contract. Suggested repository:

```text
referraliq/
  app.py
  requirements.txt
  README.md
  pages/
    01_Investment_Overview.py
    02_Deal_Screen.py
    03_Company_Diligence.py
    04_Pilot_Economics.py
    05_Venture_Returns.py
    06_Evidence_and_Gates.py
  core/
    financial_math.py
    source_validation.py
    rankings.py
    csv_import.py
    database.py
  data/
    company_screen.csv
    source_register.csv
    model_contract.json
    model_fixtures.json
  tests/
    test_parity.py
    test_assumptions.py
    test_data_quality.py
    test_ranking.py
  .gitignore
```

### Pages

**Investment overview:** Prominent recommendation, latest evidence date, top four candidate roles and investment blockers. Distinguish product-fit ranking from investability. Show a banner saying data are historical public sources and underwriting inputs are hypothetical.

**Deal screen:** Filter by workflow, buyer, source confidence, and research status. Expose scoring weights with a 100-point normalization and show data gaps, rather than false precision. The current score is a directional analyst assessment; do not misrepresent as an ML prediction.

**Company diligence:** Company factual snapshot, dated round disclosures, specific product workflow, source-linked claims, uncertainty fields, screenshots avoided where copyright is unclear, active questions and evidence tags. Never show a current investment valuation unless dated evidence exists.

**Pilot economics:** Full downside/base/upside controls and both 90-day and scaled run-rate views. Separately label staff capacity value, realizable cash, fees, clinical oversight, one-time setup and rollout ramp. Include a break-even slider and a table of monthly pilot results. The base scenario should match the fixtures exactly before rounding.

**Venture returns:** Pre-money/post-money, check, dilution, exit ARR, exit EV/ARR, equity factor, gross proceeds, MOIC and IRR. Label every private-company metric as `ILLUSTRATIVE`. Show a 2D exit sensitivity table and list unmodeled term-sheet rights. Do not imply that a company is actively fundraising.

**Evidence and gates:** Source dates, URLs, vendor vs primary/independent classifications and ten diligence gates. Every current gate starts `Unknown`. A management quote is not an internally verified performance result.

## 4. Business logic requirements

- Recreate formulas from `model_contract.json` and use `model_fixtures.json` for three-scenario parity. Do not independently invent ROI formulas.
- For the pilot, each of months 1, 2 and 3 has distinct adoption ramp. Pilot setup applies only in month 1.
- Do not add the 90-day pilot net cash and a new full-scale year net cash into a synthetic first-year total. Contract credits, overlapping fees and implementation recovery have not been established.
- Cash realization is a *separate* fraction of recovered staff capacity value. Default base = 50% assumption, not an observed result.
- Show a zero baseline appropriately, and guard against divide-by-zero, empty CSVs, negative input, nonfinite values and rates outside 0 to 1.
- The venture 3x hurdle is **not** an official Intermountain return threshold, but an illustrative reverse-underwriting example.
- A 6-year holding period is assumed; do not present gross IRR as a net fund IRR.
- Market sizing should show `Insufficient sourced inputs` until actual buyer counts, segment fit and defensible ACV are present.

## 5. Data controls and security

1. Only public, non-PHI records in hosted examples. Do not collect patient-level data, screenshots of charts, names, MRNs, claim numbers or insurance IDs.
2. Local SQLite is acceptable for an analyst's demo. It is not a production system of record. Clearly state that limitation.
3. Keep source URL, original source date, last-checked date, analyst confidence and claim status for each substantive company field.
4. Make stale fields visible and prevent undated funding figures from being described as current.
5. Validate CSV schemas, strip executable spreadsheet text on export, and never execute data-field content as Python or SQL.
6. Do not scrape authenticated PitchBook, LinkedIn or other restricted sites. A permitted public RSS feed can be a later enhancement, not an MVP dependency.
7. Add no API keys or secrets to GitHub. Use `.gitignore` and environment variables if authorized third-party feeds are added later.
8. Cite all investment-relevant claims. Do not show fake live financing data or fabricated company revenue.

## 6. Build plan and acceptance criteria

### Milestone 1: Contract and company data, 1 working day

- Validate both CSV schemas and parse `model_contract.json`.
- Build immutable source registry and per-company claim lineage.
- Tests: reject missing company names, duplicate source IDs, unsupported dates, and false current funding status.

**Acceptance:** 12 companies and 36 source rows imported with no invented facts; company facts drill through to dated URLs.

### Milestone 2: Financial engines, 1 working day

- Implement `core/financial_math.py` as deterministic pure Python.
- Port reference tests from `qa/model_validation.py`.
- Test edge conditions, including zero pilot cases, zero cash conversion, higher vendor cost, increasing dilution and invalid rates.

**Acceptance:** All three Golden Fixtures match unrounded to 1e-6 absolute tolerance. Zero division and invalid inputs produce controlled user messages. The spreadsheet and app reconcile.

### Milestone 3: Professional investor interface, 1-2 working days

- Build Overview, Deal Screen, Company Diligence, Pilot Economics and Venture Returns.
- Add USD/millions unit labels, scenario legends, click-through references and responsibly empty status values.
- Distinguish operational ROI from equity performance, and prioritize the current decision recommendation above visual dashboards.

**Acceptance:** A first-time reviewer can answer: candidate, thesis, dealbreaker, credible source, scenario economics and next action in 90 seconds.

### Milestone 4: Gate tracker, export and finish, 1 working day

- Diligence gate status with timestamped analyst notes.
- CSV export for reviewed company scores and updated diligence status.
- Strong README, one-command local start, deployed demo if feasible, and screenshot evidence for QA.

**Acceptance:** Tests pass on clean install, no secrets or PHI, exported data are schema-valid, no broken references or misleading live-data claims. Mobile width and dark/light themes checked.

## 7. Copyable Claude Code prompt

```text
We are building ReferralIQ, a professional healthcare venture capital research dashboard for an independent job application portfolio project. I have attached a frozen Phase 2 research/model package.

Start by reading PHASE3_CLAUDE_CODE_HANDOFF.md, model_contract.json, model_fixtures.json, data/company_screen.csv, data/source_register.csv, and qa/model_validation.py.

Do NOT invent financial facts, company ARR, funding terms, current portfolio relationships, pricing or clinical performance. All scenario inputs are clearly hypothetical and all facts must retain dated URLs. The investment recommendation is DILIGENCE FIRST, not INVEST. Distinguish staff capacity value from realized cash. Distinguish 90-day pilot, full scaled annual run rate and first scaled year. Keep a current incumbent-vendor comparison with Notable and never state the historical relationship is proven active today.

Propose a data schema and clean project structure first. Then implement the Streamlit application in four milestones listed in the handoff. Build core/financial_math.py first, reproduce model_fixtures.json to 1e-6 tolerance, and add rigorous unit tests before building charts. Create a professional restrained user interface and publish a concise README and reproducible setup instructions. No scraped or protected data. Do not use em dashes in application text or documentation.

Finish by presenting exactly: tests run and their results; known limitations; local execution instructions; an artifact/screenshot checklist; and a list of remaining high-risk claims requiring human confirmation.
```

## 8. Candidate preparation during engineering

- Be able to explain **why base run-rate is positive yet first scaled year negative**.
- Explain why the **pilot loses cash** and why spending to test performance may still be rational.
- Verify the Notable incumbent issue without claiming knowledge of 2026 contracts.
- Explain **why cumulative funding dollars are not company valuation**.
- Know the difference between estimated capacity savings, actual cash savings, equity MOIC and gross IRR.
- Review all source links and capture dates immediately before external submission.
- Prepare a 60-90 second presentation and a 3-minute version with an explicit disconfirming observation.
- Consider recruiting one healthcare operations professional or finance mentor to critique the chosen workflow denominators, not to create undocumented operating data.

## 9. Stop conditions and priority

If deployment work runs behind schedule, send the one-page executive brief, memo and validated Excel model before the interactive dashboard. Do not miss an opportunity to share useful analytical work simply to polish UI details. Never sacrifice correctness or provenance to make the app look more predictive than it is.
