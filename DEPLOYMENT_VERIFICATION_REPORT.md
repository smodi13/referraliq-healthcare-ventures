# Deployment verification report

Public application: https://referraliq-healthcare-ventures.streamlit.app (Streamlit Community Cloud, Python 3.12.15, Streamlit 1.56.0).
Source: https://github.com/smodi13/referraliq-healthcare-ventures, branch `main`, entry point `app.py`. No secrets or environment
variables are configured. Tested on October 10 to 11, 2026 by an anonymous visitor in a separate browser (no Streamlit or GitHub session).

## Build
Repository cloned to `/mount/src/referraliq-healthcare-ventures`, 38 packages installed with uv under Python 3.12.15 from `requirements.txt`.
The platform replaced pyarrow 26.0.0 with 24.0.0 automatically because of a known segfault; no application change was needed.
First build and start succeeded without errors.

## Public visitor tests (all against the hosted URL)
| Check | Result |
|---|---|
| Six pages load via cold deep links (/, /screener, /diligence, /pilot, /venture, /evidence) | PASS, correct H1, no exception element, independence disclaimer present on each |
| Read-only banner on every page; no gate, decision or note forms | PASS |
| Recommendation shown | ADVANCE TO DILIGENCE |
| Screener company count | 12 of 12; CSV export 12 rows; entry-rating sensitivity present |
| Evidence registry | 36 rows, 36 unique IDs; CSV export 36 rows |
| Overlay | S15 and S26 show the direct PR Newswire URLs; S28 shown as Secondary summary (AHA report sponsored by Ailevate, CAQH-attributed) |
| Gates | 10 Unknown, 0 other; gate CSV all Unknown; standing diligence question visible |
| Notable dossier | historical wording; standing question present; no claim of an active relationship |
| Financial parity, Downside | pilot ($66,636); run-rate ($150,384); first year ($196,950); MOIC 0.32x; IRR -17.2% |
| Financial parity, Base | pilot ($39,834); run-rate $25,776; first year ($31,268); post-money $105.0m; MOIC 2.97x; IRR 19.9% |
| Financial parity, Upside | pilot ($31,610); run-rate $347,400; first year $249,500; post-money $80.0m; MOIC 13.50x; IRR 54.3% |
| What-if edit and reset | cash realization 30% gives cash savings $2,470 and net ($41,480); restore returns ($39,834); no NaN or infinity |
| Navigation | sidebar links, browser back, forward and refresh preserve the page; screener filter persisted across pages |
| Document downloads | brief PDF (1 page), memo PDF (6 pages), original workbook and publication copy: SHA-256 identical to the repository files |
| Layout | 1440, 1024 and 390 px, light and dark: 6 pages at 390 and 1024 light, 6 at 390 dark and 2 at 1024 dark, no exception, no horizontal overflow |
| Console | only platform-level 404s (analytics, user-details probe, subpath health probes); no application exception |

## Public write restrictions
- Hosted checkout path rule makes the app read-only; the sidebar states read-only mode and no edit controls render.
- Repository-layer write rejection, SQLite read-only handle, session isolation of what-if inputs and default read-only are verified by the
  138-test suite and local live servers (see RELEASE_CANDIDATE_REPORT.md). A direct programmatic write attempt cannot be issued
  from the public UI, so rejection on the hosted host itself is verified only through these controls and the absence of write paths.
- This is a deployment safeguard, not authentication.

## Not verified
Hosted cloud server logs after idle sleep and wake; a screen-reader pass; independent validation of vendor claims; cloud Python 3.13 or 3.14.
