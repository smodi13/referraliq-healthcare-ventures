# RED_TEAM_REVIEW

Skeptical venture principal's reading of the Silna diligence case. Public sources and the frozen Phase 2 model only. No positive conclusion is manufactured: the supported conclusion is "keep diligence open", not "invest".

## 1. Thesis consistency check

- Recommendation in the app, memo and brief: advance to structured diligence. Consistent across all three. Nothing in the evidence reviewed in this phase argues for upgrading it to invest, and nothing argues for dropping it.
- Roles are consistent: Silna (priority equity diligence), Tennr (commercial and product benchmark), Rhyme (payer-provider workflow comparator), Notable (historical relationship needing current-status verification). The spelling "Tennr" is used throughout.
- The seven concepts the app must keep apart, and where each lives:

| Concept | Where it is expressed | Not to be read as |
|---|---|---|
| Product fit | `workflow` rating, Tennr scores 5 | A reason to buy equity |
| Strategic fit | `strategic` rating | Intermountain interest or permission |
| Investment attractiveness | `entry` rating (Silna 4, Tennr 2, Assort 1) and Venture Returns. Silna's 4 partly rests on an undisclosed valuation, an unknown rather than an attractive price (sensitivity on the Screener) | A verified price |
| Commercial value | Pilot Economics (hypothetical) | Proof of savings |
| Operational feasibility | `pilot` rating and gates G02, G06 | A completed integration review |
| Financial return | Venture Returns (hypothetical) | Net fund IRR |
| Data confidence | `confidence` rating and the source review | Verification of private metrics |

## 2. Why each reason to advance Silna is classified

| Reason | Class | Basis |
|---|---|---|
| Announced $27M ($5M seed, $22M Series A) in March 2025 | Supported (historical disclosure) | S10, company release |
| Reports supporting over 150,000 patients | Vendor-reported, unaudited | S11 |
| Browser-agent volume grew 20x; most prior auths go through payer portals | Vendor-reported | S12 |
| One customer cut authorization time about 29 to 7 days | Anecdote, vendor-published | S13 |
| Earlier stage with undisclosed valuation, entry rated 4 of 5 | Analyst inference, and a screening limitation: an unknown valuation is not an attractive price; Silna drops from #4 to #6 if the rating is held at neutral | CSV entry rating, scoring sensitivity |
| Regulatory tailwind from CMS-0057-F | Supported, but demand for any vendor not guaranteed | S04, S35 |
| Base run-rate covers recurring cost 1.21x | Illustrative assumption | model |
| Acute-care scalability, workflow coverage, current round | Unknown, requires validation | CSV key risk |

## 3. Statements the app must not make, and status

Current revenue, ARR growth, gross margin, retention, NRR, existing hospital customers, present valuation, cap table, investor ownership, current fundraising, exit value, market share, clinical effectiveness, return expectations: all Unknown. The app labels them Unknown (dossier "What remains unknown", gate G07 and G08) and the model labels every private-company input hypothetical. A copy scan (`tests/test_phase45.py`) fails the build on phrases that assert an active partnership, current handling, exclusivity, fundraising or official affiliation.

## 4. Red-team questions

**Why could this be an attractive investment?** Early-stage company with documented seed and Series A funding from named institutional investors, a focused care-readiness workflow, claimed rapid usage growth, and a regulatory driver that raises the value of authorization automation. Entry price is unknown, and there is no disclosed valuation of the size reported for Tennr ($605M) or Assort ($1.2B).

**Why could it be a poor investment?** All performance evidence is self-published. Specialty and behavioral-health focus may not transfer to acute-care health systems. Payer-portal automation is exposed to payer-side change and to larger platforms (Tennr, Assort, Notable, Luma) moving into the same workflow. The hypothetical downside case returns 0.32x, and gross MOIC is highly sensitive to unverified exit ARR and multiples.

**What would cause rejection?** An incumbent module already covering the workflow at lower incremental cost (G01); failed security or clinical-oversight review (G02); customer references unwilling or unable to confirm results; gross margin or net retention far below software norms; a live term sheet with preferences or pricing that make the downside case unacceptable (G08); governance conflict from investing in a vendor Intermountain also buys from (G09).

**What must management provide?** ARR by customer type and cohort; gross margin; net revenue retention and logo churn; automation rate and exception rate by specialty and payer; implementation timeline and EHR integration scope; security attestations and BAA terms; reference customers including at least one health system; cap table, option pool, liability and debt; the use of proceeds.

**What terms would support an investment?** Price and structure that keep the downside case acceptable (the reverse-underwriting view shows a Base pre-money near $79M for 3.0x under the illustrative assumptions, which is an example, not a requirement); no senior preferences that reduce common-equivalent proceeds below the model; information and observer rights; pro rata rights. None of these are known.

**Which alternatives should be evaluated?** Tennr (product benchmark, high entry price), Rhyme (payer network; its own page contradicts itself on volume, S14), Notable (incumbent; S36 shows it sells referral management to another health system), Luma Health (incumbent competitor), Assort (new referral agent, S27; $1.2B valuation), Plenful (pharmacy-specific, $50M Series B, $76M total), and an internal or incumbent-extension option.

**What could Intermountain accomplish through an existing vendor?** Unknown. Public sources show a 2020 intake and registration partnership (S31) and vendor-reported intake and form outcomes (S33, S34). Whether any referral or prior authorization capability is already contracted or could be added is the open standing question (G01).

**When would a commercial pilot beat an equity investment?** When the product works but equity terms are unattractive or unavailable; when a bounded pilot (Base 90-day cost about $44k, hypothetical) buys measurement evidence far cheaper than a $2M hypothetical check; and when buying and investing in the same vendor creates a governance conflict (G09). The two decisions can both be "no" or "pilot only".

## 5. New information found in Phase 4.5 (not applied to the original research)

| Item | Source | Date | Effect on thesis | Proposed correction | Needs analyst approval |
|---|---|---|---|---|---|
| Assort $120M Series C at $1.2B valuation stated by the company | PR Newswire release (approved replacement for S26, applied) | Jun 25, 2026 (original announcement June 24, 2026) | None; consistent with the screen (entry rating 1) | Applied as overlay | Approved |
| Assort total funding more than $222M | same | Jun 25, 2026 | None | Optional note | Yes |
| Plenful $50M Series B, total funding $76M | PR Newswire release (approved replacement for S15, applied) | Apr 30, 2025 | None | Applied as overlay | Approved |
| Rhyme page gives two different volume figures | S14 | undated | Confirms existing key-risk note | None | No |
| Rock Health H1 2026 figures corroborated by other outlets | search summaries (not read directly) | Jul 2026 | None | Consider citing Rock Health directly | Yes |
| Plenful investor "Notable Capital" is a venture firm, not Notable Health | Plenful release | Apr 30, 2025 | None; avoid conflating | None | No |

No shortlist change and no change to the recommendation is proposed. `data_proposed/source_corrections_proposed.csv` holds the two citation replacements; the original register is untouched.
