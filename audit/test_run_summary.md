# Test run summary (Phase 4)

Command: `python -m pytest -q --cov=core` (Python 3.14.3, pytest 9.1.1, pytest-cov 7.1.0)
Result: 106 passed, 0 failed, 0 skipped. Core coverage 97.4 percent (audit/coverage.json). View files are exercised by UI smoke tests but not measured.
Baseline before Phase 4: 85 passed (audit/baseline_pytest.txt).

| File | Focus |
|---|---|
| test_financial_parity.py | 18 keys x 3 scenarios at 1e-6, hard-coded values, reconciliation |
| test_financial_edge_cases.py | zeros, negatives, NaN, inf, bounds, monotonicity |
| test_phase4_audit.py | 1,000 random scenarios vs independent model, huge inputs, read-only enforcement, workbook extras |
| test_data_integrity.py | counts, checksums, em dash scan, dates, bad CSV schemas |
| test_scoring.py | original reproduction, normalization, ties |
| test_database.py | idempotent seed, rollback, FK, injection text, gates |
| test_exports.py, test_formatting.py | CSV escaping, number formats |
| test_ui_smoke.py | six pages, resets, validation, filters, read-only UI, state carry-over |
