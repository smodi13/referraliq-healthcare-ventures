# INDEPENDENT_REVIEW_PRIORITIES

For a second reviewer. Each item names where to look and what would count as a finding. Mark anything you cannot verify as NOT VERIFIED.

| # | Priority | Files | Questions |
|---|---|---|---|
| 1 | Model methodology and reconciliation | `model_contract.json`, `model_fixtures.json`, `core/financial_math.py`, `tests/independent_model.py`, `FINANCIAL_RECONCILIATION.md`, `Pilot_ROI_and_Venture_Model.xlsx` | Do formulas match the contract? Is `exit_premoney_m` correctly treated as entry pre-money? Are the zero-denominator conventions (coverage 0, break-even 0) acceptable? |
| 2 | Unsupported assumptions in the thesis | `Investment_Committee_Memo.pdf`, `core/content.py`, `views/01_Investment_Overview.py`, `RED_TEAM_REVIEW.md` | Is any claim stated as fact that is only vendor-reported, hypothetical or unknown? Are strengths and risks balanced? |
| 3 | Silna vs Tennr vs Rhyme | `data/company_screen.csv`, `views/02_Deal_Screener.py`, `views/03_Company_Diligence.py`, `RED_TEAM_REVIEW.md` | Is the case for Silna as first diligence candidate defensible given entry rating 4 versus Tennr 2? Is Rhyme's role fair given the S14 inconsistency? |
| 4 | Notable characterization | `core/content.py` (`NOTABLE_NOTE`, `STANDING_QUESTION`), sources S24, S25, S31, S33, S34, S36, `tests/test_phase45.py` (copy scan) | Does any copy imply an active contract, current handling, exclusivity or dissatisfaction? |
| 5 | Source quality and staleness | `SOURCE_VERIFICATION_REPORT.md`, `audit/source_review.json`, `data/source_register.csv`, `data_proposed/source_corrections_proposed.csv` | Are evidence classes right? Are replacements for S15 and S26 acceptable? Is S28 correctly read (page 7)? |
| 6 | Scoring methodology | `core/scoring.py`, `tests/test_scoring.py`, `views/02_Deal_Screener.py` | Are weights described honestly as judgment? Does reset restore originals? |
| 7 | Recommendations and gates | `views/06_Evidence_and_Gates.py`, workbook tab DILIGENCE GATES (G01 to G10), `core/repository.py` | Do gates map to the thesis? Can a status change alter the default recommendation (it must not)? |
| 8 | Database and read-only safety | `core/repository.py`, `core/components.py`, `tests/test_phase45.py`, `tests/test_phase4_audit.py`, `core/exports.py` | Can any path write in read-only mode? Do exports leak local notes or paths? SQL parameterized? |
| 9 | Impression on a VC professional | `views/*.py`, `UI_REVIEW.md`, `audit/screenshots/` | Is the first screen clear in 90 seconds? Anything overstated or cluttered? |
| 10 | Changes before public deployment | `DEPLOYMENT_GUIDE.md`, `ISSUE_LOG.md`, `REVIEW_BEFORE_SHARING.md` | What must be fixed or approved first (S15, S26 replacements, source dates, hosting test)? |
