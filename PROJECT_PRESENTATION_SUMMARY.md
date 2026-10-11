# Project presentation summary

## Investment analysis
- **Scope:** AI automation of provider-side referral and prior authorization workflows. 12 companies screened from public sources.
- **Conclusion:** advance Silna Health to structured diligence; benchmark Tennr; evaluate Rhyme; verify the historical Notable
  relationship before any vendor decision. No equity recommendation without verified metrics, references and entry terms.
- **Why not invest now:** every Silna usage and outcome claim is vendor-reported; no ARR, margin, retention, terms or open round is
  verified; Silna's entry rating partly rests on an undisclosed valuation, which is an unknown, not a price advantage.
- **Economics (hypothetical):** Base 90-day pilot about -$39,834; run-rate about +$25,776 per year; first scaled year about -$31,268;
  gross MOIC 2.97x and IRR 19.9% over six years; Downside 0.32x; Upside 13.5x.

## Research methodology
- Weighted six-dimension screen (25/20/15/15/15/10), analyst judgment, reproduced exactly (max difference 0).
- 36-source register with publisher, date, limitations, link check and analyst read; three citations corrected through a documented
  overlay with lineage; vendor claims kept distinct from independent or official evidence.
- Ten diligence gates drawn from the workbook, all Unknown, each with an owner and an outcome if not met.

## Technical implementation
- Python 3.12, Streamlit, Plotly, pandas, SQLite, openpyxl, pytest. Pure finance engine from a frozen contract (version 2.0.0).
- 138 tests: fixture parity (54 values), an independent closed-form model on 1,000 random scenarios, scoring, source integrity,
  database and migration, read-only enforcement, exports, UI smoke tests. Also run on Python 3.13 and 3.14.
- Read-only by default; write attempts rejected in the data layer; SQLite opened read-only; what-if inputs are per session.

## Limitations
Hypothetical private-company inputs; vendor-reported capabilities; judgment-based scores; incomplete page dates; no accessibility
audit; not affiliated with Intermountain.
