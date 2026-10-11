"""Analyst narrative drawn from the Phase 2 memo, brief and workbook. Facts carry source ids."""

RECOMMENDATION_REASON = (
    "Advance Silna Health to structured diligence, benchmark Tennr and Rhyme, and validate current Notable "
    "coverage first. No equity investment and no production deployment is supported by public information alone."
)
WHAT_WOULD_CHANGE = {
    "What would make this recommendation more favorable": [
        "Documented incumbent gap: current Notable and other modules cannot deliver the referral workflow at lower incremental cost (G01).",
        "Verified ARR, gross margin, net retention and customer references from the company (G07).",
        "A live term sheet whose downside case is still acceptable (G08).",
    ],
    "What would stop or reverse it": [
        "An incumbent module already covers the workflow at lower incremental cost.",
        "Failed security or clinical-oversight review (G02).",
        "Recurring cash benefit below the 1.20x recurring-cost hurdle at validated volume and price (G04).",
    ],
}

TRACKS = {
    "A. Commercial deployment": dict(
        question="Does a controlled pilot make operational and financial sense?",
        position="Permit a tightly controlled design-phase pilot only if the incumbent gap and safety review are confirmed.",
        evidence="Aggregate workflow baselines, vendor quote, exception rates, quality guardrails, security approval.",
        gates="G01, G02, G03, G04, G05, G06, G10"),
    "B. Equity investment": dict(
        question="Would a venture investment make sense at specific, verifiable terms?",
        position="No investment approval on public information. Silna remains the first candidate to diligence.",
        evidence="Actual ARR, gross margin, retention, sales efficiency, burn, cap table and signed entry terms.",
        gates="G07, G08, G09"),
}

STRENGTHS = [
    ("Regulatory tailwind", "CMS-0057-F adds prior authorization process obligations from 2026 and payer API requirements from 2027, largely for non-drug services. This supports the digitization rationale but does not guarantee demand for any vendor.", "S04, S35", "VERIFIED"),
    ("Documented administrative burden", "An AMA physician survey reports about 40 prior authorizations per physician per week. These are survey responses, not measured per-referral savings.", "S06", "REPORTED"),
    ("Silna is a focused, early candidate", "Silna announced $27M of combined seed and Series A funding in March 2025 around care-readiness workflows. This is a historical disclosure, not evidence of a current round.", "S10", "REPORTED"),
    ("Pilot design limits downside", "The base 90-day pilot is modeled as a planned measurement expense. The hypothetical loss is bounded by pilot setup and fees.", "Model v2.0.0", "MODELED"),
    ("Hypothetical base economics are positive at run-rate", "Under illustrative assumptions, base recurring benefit covers recurring cost 1.21x. These are analyst assumptions, not observed results.", "Model v2.0.0", "MODELED"),
]
RISKS = [
    ("Incumbent overlap", "Intermountain publicly announced a Notable partnership in 2020. The current contractual scope is unknown, and a new product must beat the incumbent stack, not only a manual baseline.", "S31, S33, S34", "UNKNOWN"),
    ("Scale and fit unproven", "Silna's acute-care scalability and workflow coverage are not established; company evidence requires validation.", "S10, S11, S12", "UNKNOWN"),
    ("No verified round or terms", "No active financing, valuation, ARR or cap table is verified for any screened company. Historical rounds are not deal terms.", "S08, S10", "UNKNOWN"),
    ("Thin pricing headroom", "In the base case the maximum monthly vendor fee that preserves 1.20x coverage is about $8,090 against an illustrative $8,000.", "Model v2.0.0", "MODELED"),
    ("Venture outcome dispersion", "Hypothetical gross MOIC ranges from 0.32x (downside) to 13.5x (upside). EV/ARR multiples are sensitivity levers, not comparable medians.", "S32, Model v2.0.0", "MODELED"),
]

UNKNOWNS = [
    "Current annual recurring revenue and growth",
    "Gross margin, net revenue retention and churn",
    "Customer references, contracts and concentration",
    "Current financing terms, valuation and round availability",
    "EHR integration effort and security review status",
    "Independently validated automation accuracy and exception rates",
    "Current vendor pricing and implementation terms",
    "Live customer adoption and operating outcomes",
]

NOTABLE_NOTE = (
    "Intermountain publicly announced a strategic partnership with Notable in October 2020 for patient "
    "registration, insurance eligibility and intake automation (S31). Later Notable-published case "
    "studies describe Intermountain intake and pediatric form workflows (S33, S34). These are historical, "
    "partly vendor-reported items. The current contract status and current workflow scope are unverified, "
    "and this project has no access to confidential information."
)

EXCLUSIONS = [
    "Liquidation preferences, participation rights and seniority",
    "Cap table detail, option pool reshaping and convertible notes",
    "Senior debt and enterprise-to-equity bridge adjustments (a single factor is used)",
    "Follow-on investment checks and pro rata decisions",
    "Fund management fees, carried interest and fund expenses",
    "Timing of interim cash flows and transaction costs",
]

DEFINITIONS = {
    "MOIC": "Multiple on invested capital: gross proceeds divided by the amount invested.",
    "IRR": "Internal rate of return. Here a single-cash-flow annualized gross rate: MOIC^(1/years) - 1.",
    "ARR": "Annual recurring revenue.",
    "EHR": "Electronic health record system.",
    "Capacity value": "Staff time recovered, valued at a loaded hourly cost. Not cash unless it is redeployed or avoids spend.",
    "Cash realization": "The assumed share of capacity value that becomes real cash expense reduction.",
}

EVIDENCE_KINDS = {
    "VERIFIED": ("VERIFIED, OFFICIAL OR INDEPENDENT", "Stated in a regulator, institutional or independent source we read. Establishes the fact stated, not future performance."),
    "REPORTED": ("REPORTED, PUBLIC DISCLOSURE", "A figure or event in a public disclosure (company release, survey or press). The disclosure exists and is historical; its content is not independently audited."),
    "VENDOR": ("VENDOR-REPORTED CAPABILITY", "A product capability or outcome published by the vendor about itself. Not independently validated."),
    "ANALYST": ("ANALYST JUDGMENT", "An inference or rating by the analyst from the evidence."),
    "MODELED": ("MODELED, HYPOTHETICAL", "An output of the scenario model built on hypothetical inputs. Not an observed result."),
    "UNKNOWN": ("UNVERIFIED, CURRENT STATUS UNKNOWN", "Not established by available evidence, or only true as of a past date. Needs diligence."),
}

STANDING_QUESTION = (
    "What relevant capabilities, contracts, integrations and operational workflows already exist within Intermountain? "
    "Public sources show only a historical Notable intake and registration relationship (S31, S24); current scope, "
    "contract status and any referral or prior authorization coverage are unknown."
)

SCREEN_LIMITATION = (
    "Screening limitation: Silna's 4 of 5 entry rating reflects an earlier-stage financing history and an undisclosed "
    "valuation. An undisclosed valuation is an unknown, not evidence of an attractive entry price, and an earlier stage "
    "does not automatically mean better pricing. Silna is a diligence hypothesis, not a verified superior investment. "
    "Product fit (Tennr scores highest) and equity diligence priority are different questions. The Phase 1 scores are "
    "unchanged; the sensitivity below is not a revised official score."
)
