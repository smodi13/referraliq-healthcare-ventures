# UI_REVIEW

Tool: Playwright Chromium against `streamlit run app.py` (Streamlit 1.56.0). Screenshots in `audit/screenshots/`.

## Automated matrix (36 loads)
6 pages x 3 widths (1440, 1024, 390) x 2 schemes (light, dark). Per load: H1 present, no Streamlit exception element, no dialog, no page-level horizontal overflow, theme background correct, chart count. Result: all 36 passed. One finding (Overview at 390 had inner horizontal overflow from the brief table) was fixed and rechecked (scrollWidth equals clientWidth).

| Page | 1440 | 1024 | 390 | Light | Dark | Charts rendered |
|---|---|---|---|---|---|---|
| Investment Overview | pass | pass | pass | pass | pass | 0 |
| Deal Screener | pass | pass | pass | pass | pass | 1 |
| Company Diligence | pass | pass | pass | pass | pass | 1 |
| Pilot Economics | pass | pass | pass | pass | pass | 6 |
| Venture Returns | pass | pass | pass | pass | pass | 1 |
| Evidence and Gates | pass | pass | pass | pass | pass | 0 |

## Viewed by eye (screenshots read)
Overview 1440 light, dark, 390; Deal Screener 1440; Company Diligence 1440; Evidence 1440; Pilot 1440 dark and 390; Venture 1440 and 1024; cold deep link. Remaining matrix screenshots exist as files (`matrix_*`) but were checked programmatically, not read individually.

## Navigation
Sidebar links, active page indicator, cold deep links, browser back, forward and reload on `/pilot` verified. Selected company and scenario carry across pages. Filters and edited inputs reset on page change (P4-103).

## Interactions tested (AppTest and browser)
Pilot edit then restore returns the original metrics; completion rate 0 gives $0 capacity; venture check above round shows a validation error; screener empty state, combined filters and clear; what-if weights and reset; scenario carried to Overview; company switch from screener; downloads (see below).

## Downloads
Browser download of the executive brief (67,820 bytes, 1 page), memo (83,109 bytes, 6 pages) and Excel model (41,010 bytes, 14 sheets) were byte-identical to the originals. CSV exports are covered by unit tests for formula escaping.

## Numerical presentation
USD in whole dollars with parentheses for negatives, USD millions with m suffix, multiples with x, percentages to one decimal. Chart axes carry units and dollar tick formats. Heatmap colors center on 1.00x and 0%.

## Limitations
Streamlit supplies keyboard focus and contrast; no custom audit was run. Charts have no alt text. The sidebar collapses on mobile (hamburger) as designed by Streamlit.

## Phase 4.5 additions
- Hidden-state check: Pilot cash realization set to 30% (cash savings $2,470, net ($41,480), as computed by 8,232 x 30%); after visiting Venture Returns and returning, base values returned and no "modified" flag; Overview stayed on the frozen Base preset.
- Screener filter persistence: Direct fit "Medium" gave 6 of 12; after a round trip it still showed 6 of 12.
- Downloads: screener CSV 13 lines, evidence CSV 37, gate CSV 11 (all Unknown), venture CSV labeled ILLUSTRATIVE; no local paths in any.
- Keyboard: Tab order sidebar links, header buttons, page content, scenario buttons, restore button; sidebar links now show a 2px focus outline.
- Chart descriptions added under the score chart, both waterfalls, the preset comparison and the MOIC heatmap.
- Not done: screen reader pass; contrast measurement beyond theme defaults.
