# FINANCIAL_RECONCILIATION

Model contract 2.0.0, fixtures 2.0.0, tolerance 1e-06 absolute.
Three independent routes are compared: (1) frozen JSON fixtures, (2) the app engine `core/financial_math.py`, (3) the original Excel workbook recalculated by LibreOffice (headless) on a temporary copy. A second closed-form implementation (`tests/independent_model.py`) is used for randomized cross-checks.

## Downside: fixtures vs app engine vs workbook

| Output | Fixture | App | Abs diff (app) | Workbook (recalc) | Abs diff (wb) | Result |
|---|---|---|---|---|---|---|
| pilot_capacity | 1057.92 | 1057.92 | 0 | 1057.92 | 0 | PASS |
| pilot_cash | 264.48 | 264.48 | 0 | 264.48 | 0 | PASS |
| pilot_cost | 66900 | 66900 | 0 | 66900 | 0 | PASS |
| pilot_net | -66635.52 | -66635.52 | 0 | -66635.52 | 0 | PASS |
| runrate_capacity | 65664 | 65664 | 0 | 65664 | 0 | PASS |
| runrate_cash | 16416 | 16416 | 0 | 16416 | 0 | PASS |
| recurring_cost | 166800 | 166800 | 0 | 166800 | 0 | PASS |
| runrate_net | -150384 | -150384 | 0 | -150384 | 0 | PASS |
| runrate_coverage | 0.09841726619 | 0.09841726619 | 0 | 0.09841726619 | 4.16e-17 | PASS |
| first_year_net | -196950.4 | -196950.4 | 0 | -196950.4 | 0 | PASS |
| breakeven_cash_realization | 2.540204678 | 2.540204678 | 0 | 2.540204678 | 3.11e-15 | PASS |
| venture_post_money | 140 | 140 | 0 | 140 | 0 | PASS |
| venture_initial_ownership | 0.01428571429 | 0.01428571429 | 0 | 0.01428571429 | 1.39e-17 | PASS |
| venture_exit_ownership | 0.007142857143 | 0.007142857143 | 0 | 0.007142857143 | 2.6e-18 | PASS |
| venture_exit_equity | 90 | 90 | 0 | 90 | 0 | PASS |
| venture_proceeds | 0.6428571429 | 0.6428571429 | 0 | 0.6428571429 | 2.22e-16 | PASS |
| venture_moic | 0.3214285714 | 0.3214285714 | 0 | 0.3214285714 | 3.89e-16 | PASS |
| venture_irr | -0.1723486781 | -0.1723486781 | 0 | -0.1723486781 | 5.55e-17 | PASS |

## Base: fixtures vs app engine vs workbook

| Output | Fixture | App | Abs diff (app) | Workbook (recalc) | Abs diff (wb) | Result |
|---|---|---|---|---|---|---|
| pilot_capacity | 8232 | 8232 | 0 | 8232 | 0 | PASS |
| pilot_cash | 4116 | 4116 | 0 | 4116 | 0 | PASS |
| pilot_cost | 43950 | 43950 | 0 | 43950 | 0 | PASS |
| pilot_net | -39834 | -39834 | 0 | -39834 | 0 | PASS |
| runrate_capacity | 296352 | 296352 | 0 | 296352 | 0 | PASS |
| runrate_cash | 148176 | 148176 | 0 | 148176 | 0 | PASS |
| recurring_cost | 122400 | 122400 | 0 | 122400 | 0 | PASS |
| runrate_net | 25776 | 25776 | 0 | 25776 | 0 | PASS |
| runrate_coverage | 1.210588235 | 1.210588235 | 0 | 1.210588235 | 2.22e-15 | PASS |
| first_year_net | -31268 | -31268 | 0 | -31268 | 0 | PASS |
| breakeven_cash_realization | 0.4130223518 | 0.4130223518 | 0 | 0.4130223518 | 0 | PASS |
| venture_post_money | 105 | 105 | 0 | 105 | 0 | PASS |
| venture_initial_ownership | 0.01904761905 | 0.01904761905 | 0 | 0.01904761905 | 5.2e-17 | PASS |
| venture_exit_ownership | 0.01238095238 | 0.01238095238 | 0 | 0.01238095238 | 1.73e-17 | PASS |
| venture_exit_equity | 480 | 480 | 0 | 480 | 0 | PASS |
| venture_proceeds | 5.942857143 | 5.942857143 | 0 | 5.942857143 | 3.55e-15 | PASS |
| venture_moic | 2.971428571 | 2.971428571 | 0 | 2.971428571 | 1.78e-15 | PASS |
| venture_irr | 0.1990230972 | 0.1990230972 | 0 | 0.1990230972 | 1.94e-16 | PASS |

## Upside: fixtures vs app engine vs workbook

| Output | Fixture | App | Abs diff (app) | Workbook (recalc) | Abs diff (wb) | Result |
|---|---|---|---|---|---|---|
| pilot_capacity | 32400 | 32400 | 0 | 32400 | 0 | PASS |
| pilot_cash | 19440 | 19440 | 0 | 19440 | 0 | PASS |
| pilot_cost | 51050 | 51050 | 0 | 51050 | 0 | PASS |
| pilot_net | -31610 | -31610 | 0 | -31610 | 0 | PASS |
| runrate_capacity | 810000 | 810000 | 0 | 810000 | 0 | PASS |
| runrate_cash | 486000 | 486000 | 0 | 486000 | 0 | PASS |
| recurring_cost | 138600 | 138600 | 0 | 138600 | 0 | PASS |
| runrate_net | 347400 | 347400 | 0 | 347400 | 0 | PASS |
| runrate_coverage | 3.506493506 | 3.506493506 | 0 | 3.506493506 | 3.55e-15 | PASS |
| first_year_net | 249500 | 249500 | 0 | 249500 | 0 | PASS |
| breakeven_cash_realization | 0.1711111111 | 0.1711111111 | 0 | 0.1711111111 | 1.11e-16 | PASS |
| venture_post_money | 80 | 80 | 0 | 80 | 0 | PASS |
| venture_initial_ownership | 0.025 | 0.025 | 0 | 0.025 | 0 | PASS |
| venture_exit_ownership | 0.01875 | 0.01875 | 0 | 0.01875 | 3.47e-18 | PASS |
| venture_exit_equity | 1440 | 1440 | 0 | 1440 | 0 | PASS |
| venture_proceeds | 27 | 27 | 0 | 27 | 3.55e-15 | PASS |
| venture_moic | 13.5 | 13.5 | 0 | 13.5 | 1.78e-15 | PASS |
| venture_irr | 0.5430818442 | 0.5430818442 | 0 | 0.5430818442 | 2.22e-16 | PASS |

**Maximum absolute difference, app vs fixtures: 0.**

## Randomized cross-check

1000 random multi-input scenarios (8 inputs changed at once, seed 20261010): engine vs independent closed-form model, maximum relative difference 1.08e-13. Result: PASS.

## Edge cases and validation messages

| Case | Input change (from Base) | Result | Pass |
|---|---|---|---|
| Zero monthly pilot volume | {'pilot_monthly_cases': 0} | calculated; pilot net -43,950.00, run-rate net 25,776.00, MOIC 2.971, IRR 0.199 | PASS |
| Zero eligible share | {'eligible_share': 0} | calculated; pilot net -43,950.00, run-rate net -122,400.00, MOIC 2.971, IRR 0.199 | PASS |
| Zero automation (completion) rate | {'completion_rate': 0} | calculated; pilot net -43,950.00, run-rate net -122,400.00, MOIC 2.971, IRR 0.199 | PASS |
| Zero cash realization | {'cash_realization': 0} | calculated; pilot net -43,950.00, run-rate net -122,400.00, MOIC 2.971, IRR 0.199 | PASS |
| Zero vendor cost (scaled) | {'scale_vendor_monthly': 0} | calculated; pilot net -39,834.00, run-rate net 121,776.00, MOIC 2.971, IRR 0.199 | PASS |
| Very high vendor cost ($1,000,000 per month) | {'scale_vendor_monthly': 1000000} | calculated; pilot net -39,834.00, run-rate net -11,878,224.00, MOIC 2.971, IRR 0.199 | PASS |
| Negative loaded hourly cost | {'loaded_hourly_cost': -5} | rejected with message: loaded_hourly_cost cannot be negative | PASS |
| Eligible share 120% | {'eligible_share': 1.2} | rejected with message: eligible_share must be between 0 and 100 percent (0 to 1) | PASS |
| Missing input (hold_years removed) | {'hold_years': None} | rejected with message: Missing input: hold_years | PASS |
| Empty string input | {'pilot_setup': ''} | rejected with message: pilot_setup must be a number | PASS |
| Extremely large input (1e308 cases) | {'pilot_monthly_cases': 1e+308} | rejected with message: Inputs are too large to compute a finite result (pilot_capacity, pilot_cash, pilot_net) | PASS |
| Non-finite input (NaN) | {'exit_arr_m': nan} | rejected with message: exit_arr_m must be finite | PASS |
| Non-finite input (infinity) | {'exit_arr_m': inf} | rejected with message: exit_arr_m must be finite | PASS |
| Zero investment amount | {'investor_check_m': 0} | rejected with message: investor_check_m must be positive | PASS |
| Check larger than round | {'investor_check_m': 26} | rejected with message: Investor check cannot exceed the total round size | PASS |
| Zero exit ARR | {'exit_arr_m': 0} | calculated; pilot net -39,834.00, run-rate net 25,776.00, MOIC 0, IRR -1 | PASS |
| Full dilution (100%) | {'ownership_dilution': 1.0} | calculated; pilot net -39,834.00, run-rate net 25,776.00, MOIC 0, IRR -1 | PASS |
| Zero holding period | {'hold_years': 0} | rejected with message: hold_years must be positive | PASS |
| Negative holding period | {'hold_years': -3} | rejected with message: hold_years cannot be negative | PASS |
| Negative economic outcome (Downside preset) | Downside preset | calculated; pilot net -66,635.52, run-rate net -150,384.00, MOIC 0.3214, IRR -0.1723 | PASS |

## Cross-checks against the investment memo and workbook narrative

| Memo or workbook statement | Source | Recomputed | Match |
|---|---|---|---|
| Base 90-day pilot net cash ($39,834) loss | memo/brief | -39834 | PASS |
| Base annual capacity value $296,352 | memo/brief | 296352 | PASS |
| Base annual benefit $148,176 vs cost $122,400 | memo/brief | 148176 | PASS |
| Base coverage 1.21x | memo/brief | 1.21 | PASS |
| Base break-even cash realization 41.3% | memo/brief | 0.413 | PASS |
| Max base vendor fee at 1.20x about $8,090 | memo/brief | 8090 | PASS |
| Exit ARR for 3.0x about $80.8m | memo/brief | 80.8 | PASS |
| Base gross MOIC 2.97x | memo/brief | 2.97 | PASS |
| Base gross IRR 19.9% | memo/brief | 0.199 | PASS |
| Downside first-year net ($196,950) | memo/brief | -196950 | PASS |

## Sensitivity monotonicity (Base preset)

Raising vendor fee lowers run-rate net cash; raising dilution lowers exit ownership and MOIC; raising exit ARR or multiple raises MOIC; raising completion rate raises capacity value. All verified in `tests/test_financial_edge_cases.py` and `tests/test_phase4_audit.py`.

## Conceptual separations checked in the app

- Capacity value and cash savings are separate metrics and charts; cash = capacity x cash realization.
- 90-day pilot, annual run-rate and first scaled year are never summed; the UI states this.
- Venture outputs use USD millions and carry the hypothetical banner; IRR is labeled gross.
- The 3.0x hurdle is labeled an analyst-created illustration, not an Intermountain requirement.

## Financial limitations (consistency is not plausibility)

Reproducing the model exactly shows the arithmetic is implemented as specified. It does not show the inputs are achievable.
Most important unverified inputs, all analyst-created:
1. Cash realization (50% Base): the share of recovered staff time that becomes real cash. Break-even is 41.3%, so a modest miss flips run-rate net cash negative.
2. Automation completion rate (60% Base) and eligible share (70% Base): no measured baseline exists; the model has no exception-handling or rework cost beyond the audit line.
3. Net minutes saved (7 Base): the CAQH benchmark (S28) shows a 14 minute manual-to-automated difference industry-wide; 7 net minutes is an assumption, not a derived value.
4. Vendor, support and audit fees: no quote exists. Base headroom to the 1.20x hurdle is about $90 per month.
5. Entry pre-money, round size, check size, exit ARR, EV/ARR multiples, dilution: hypothetical. No Silna financing, ARR or terms are verified.
6. Not modeled: liquidation preferences, participation, debt, option pool, follow-on checks, fund fees and carry, interim cash flows, pilot fee credits against rollout.
7. Pilot and first scaled year are alternative sequential decisions and are never summed; no combined cash flow is claimed.

**Overall financial audit result: PASS**
