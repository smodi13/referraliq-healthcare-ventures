# DEPLOYMENT_GUIDE

Nothing has been published. No account, repository or hosting service was created. Follow this only after you approve.

## Local launch (macOS)
```bash
cd ReferralIQ_Phase2
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt     # runtime only: requirements.txt
python -m pytest -q                     # 138 tests expected
streamlit run app.py                    # http://localhost:8501
```

## Is Streamlit Community Cloud still appropriate?
Yes. The app is a single Streamlit entry point, needs no secrets or paid APIs, bundles all data (about 1.5 MB with PDFs and workbook), and uses local SQLite that is rebuilt from the CSVs at startup. Hosted storage is ephemeral, which is acceptable because the public demo is read-only.

## Steps for a safe read-only demo
1. Complete REVIEW_BEFORE_SHARING.md (source dates, wording, facts).
2. Create a new repository, private first. `.venv/`, `local_data/` and `.playwright-mcp/` are in `.gitignore`.
3. In Streamlit Community Cloud choose "New app", main file `app.py`, Advanced settings, Python 3.12 (recommended; 3.13 and 3.14 also passed).
4. Set no secrets and no environment variables. The app fails closed: with nothing set it is read-only, the SQLite handle is read-only, and the
   `/mount/src` checkout path also forces read-only. Do NOT set `REFERRALIQ_ANALYST_MODE` on a hosted app (it would be overridden by the
   checkout path rule, but leave it unset anyway).
5. Deploy. Open the home URL and each sub-page URL once; confirm the sidebar says "Read-only showcase mode", the Evidence page shows no
   "Record gate update" form, and the dossier shows no "Save note" form.
6. Set visibility as intended and share.

## Environment variables
| Name | Default | Purpose |
|---|---|---|
| `REFERRALIQ_ANALYST_MODE` | unset | `1`, `true` or `yes` enables local analyst editing. Without it the app is read-only. |
| `REFERRALIQ_PUBLIC` | unset | `1` forces read-only even if analyst mode is set |
| `REFERRALIQ_READONLY` | unset | legacy alias of `REFERRALIQ_PUBLIC` |
| `REFERRALIQ_DB` | `local_data/referraliq.db` | Database path; falls back to a temp directory if unwritable |

Precedence: `REFERRALIQ_PUBLIC` or `REFERRALIQ_READONLY` or a `/mount/src` path, then analyst mode, otherwise read-only. This is a safeguard
for a research demo, not authentication.

## Exact commands (after you approve publication)
```bash
cd ReferralIQ_Release_Candidate            # the unpacked release candidate
git init -b main
git add .
git commit -m "ReferralIQ release candidate"
gh repo create referraliq --private --source=. --push      # or create the repo in the GitHub UI and `git remote add origin ... && git push -u origin main`
# Streamlit Community Cloud (browser): share.streamlit.io > New app > repository referraliq, branch main, main file app.py, Python 3.12
```

## Startup behavior
On first run the app creates the database and imports the CSVs and workbook gate table in one transaction (idempotent; analyst notes and gate status survive reseeding). `scripts/validate_source_package.py` verifies reference-file checksums; `scripts/seed_database.py` reseeds manually.

## Fixture verification before every release
```bash
python -m pytest -q tests/test_financial_parity.py
python scripts/generate_audit_reports.py   # rewrites FINANCIAL_RECONCILIATION.md and SOURCE_VERIFICATION_REPORT.md
```
`scripts/verify_sources.py` re-runs the polite HTTP link check (36 requests, 1 second apart).

## Rollback
The Phase 3 baseline is `../checkpoints/referraliq_phase3_baseline.tgz`.

## Tested Python versions (Phase 4.5)
| Version | Clean install | 138 tests | App start (read-only) | Seed |
|---|---|---|---|---|
| 3.12.1 | yes | pass | health ok, /venture 200 | ok |
| 3.13.15 | yes | pass | health ok, /venture 200 | ok |
| 3.14.3 | yes | pass | health ok, /venture 200 | ok |
Dependencies were not upgraded; `requirements.txt` pins streamlit 1.56.0, plotly 6.6.0, pandas 3.0.1, openpyxl 3.1.5. Streamlit Community Cloud itself was not tested.

## Hosting limitations
Ephemeral disk (database rebuilt at start, which is fine for read-only); no secrets needed; Streamlit Cloud serves the app at its own URL and may show its own chrome ("Deploy" menu is hidden for visitors). The `uv`-managed Python 3.13 used for testing lives in the user uv directory and does not affect system Python.
