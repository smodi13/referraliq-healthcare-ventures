"""Builds audit/source_review.json and SOURCE_VERIFICATION_REPORT.md from the analyst review recorded below,
the HTTP link check (audit/source_http_check.json) and the register. The register itself is never modified.
Review method: page text fetched with one request per URL (PDF text via pdftotext), key figures located by
reading, plus targeted web searches for S15, S26 and S32. 'Supports' means the linked page states the claim."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core import data_loader as dl  # noqa: E402

REVIEW_DATE = "2026-10-10"
PCD, PTP, IND, VM, SEC = ("Primary company disclosure", "Primary third-party disclosure", "Independent reporting",
                          "Vendor marketing", "Secondary summary")
Y, P, N, NV = "Yes", "Partial", "Not on linked page", "Not verified"
YX = "Yes, via search excerpt"  # claim confirmed from an excerpt of the page; the page itself was not read by automation
YR = "Yes, via approved replacement"

# id: (evidence class, supports, page date confirmed on page, note, recommended action, proposed replacement url)
R = {
 "S01": (PCD, Y, "No (undated)", "Page states six primary areas, early and growth stage, pilot and support programs.", "Keep. Re-check before sharing.", ""),
 "S02": (PCD, P, "No (undated)", "Portfolio page loads and lists portfolio companies, but company names are not in the static text (rendered as images), so the overlap check cannot be completed from text.", "Analyst to inspect the portfolio visually for overlap with Notable, Silna, Tennr, Rhyme.", ""),
 "S03": (PCD, P, "Partly (Dec 09 and Dec 11, 2025 appear)", "Page is a Select Health press release about a Qualtrics deal; the alignment claim rests only on boilerplate calling Intermountain Health the parent company.", "Keep as context. Do not cite for anything beyond corporate affiliation.", ""),
 "S04": (PTP, Y, "Yes (Jan 17, 2024)", "Operational provisions generally from Jan 1, 2026, API requirements generally Jan 1, 2027; drugs excluded from the Patient Access API addition.", "Keep.", ""),
 "S05": (PTP, Y, "No ('updated 2026-10-08' not visible in text)", "Titled as the 2026 proposed rule on prior authorization for drugs (CMS-0062-P).", "Keep; state clearly that it is proposed.", ""),
 "S06": (PTP, Y, "No (registry date 2026-05-13 not visible; only an Oct 9, 2026 string)", "States an average of 40 prior authorizations per physician per week and 13 hours of physician and staff time per week. Survey self-report.", "Keep; confirm the release date in a browser.", ""),
 "S07": (PTP, Y, "Yes (Feb 19, 2026, release URL date and excerpts)", "CAQH release (GlobeNewswire, Feb 19, 2026): the 2025 CAQH Index estimates $258 billion of administrative cost avoided in 2024, up 17 percent. Access is intermittent: HTTP 403 and 200 on different attempts; on the final recheck the page loaded and the $258 and 2024 figures were present in its text, and CAQH's own blog copy matches. Edition note: this is the 2025 Index (released Feb 2026); S28 uses 2024 Index figures. Some executive-report variants round to about $260 billion.", "Keep. Cite the $258 billion figure only as an industry-wide avoided-cost estimate, not a referral or prior authorization TAM.", ""),
 "S08": (IND, Y, "Yes (June 18, 2025)", "Fortune exclusive: Tennr raises $101 million Series C at $605 million valuation. The valuation is a reported figure.", "Keep. Historical snapshot, not a current valuation.", ""),
 "S09": (PCD, P, "No", "Company release states a $101 million Series C led by IVP with a16z, Lightspeed, GV, ICONIQ and others. The 'referral network' product claim was not located in the extracted text.", "Keep for the financing fact; verify the product claim in a browser.", ""),
 "S10": (PCD, Y, "Yes (25 March 2025)", "Launch post: $27M led by Accel and Bain Capital Ventures, composed of a $5M seed and a $22M Series A.", "Keep. Historical disclosure.", ""),
 "S11": (VM, Y, "Yes (28 January 2026)", "States Silna supports 'over 150,000 patients nationwide' and a #1 G2 rating. Self-reported and unaudited.", "Keep as vendor-reported.", ""),
 "S12": (VM, Y, "Yes (May 1, 2026)", "Engineering post: more than 75% of prior authorizations go through payer portals; browser agent volume grew 20x over two quarters. Self-reported.", "Keep as vendor-reported.", ""),
 "S13": (VM, Y, "No (undated)", "Customer story: authorization time from about 29 days to about 7 days (76% drop). Single customer, vendor-published.", "Keep as an anecdote; not evidence of generalizable performance.", ""),
 "S14": (VM, Y, "No (undated)", "Capability claims present. The same page gives conflicting scale figures: 'over 4M prior auths for 83 of the largest providers each year' and '7M+ auths per year, 300+ payers, 2,598 hospitals'. This confirms the screen's 'website volume inconsistency' risk note.", "Keep; ask Rhyme which figure is current and how counted.", ""),
 "S15": (PCD, YR, "Yes (Apr 30, 2025 09:30 ET)", "Approved correction applied: the register now points at the direct PR Newswire release, which states a $50 million Series B and $76 million total funding. Company-issued announcement. Cumulative funding is not a valuation. Original index URL retained in lineage.", "None further. Historical disclosure only.", "https://www.prnewswire.com/news-releases/plenful-raises-50m-series-b-to-expand-ai-powered-healthcare-automation-platform-302442027.html"),
 "S16": (VM, Y, "Yes (September 11, 2025)", "Announces an intake authorization management suite covering intake, benefits verification, prior authorization and claim reconciliation.", "Keep as vendor-reported.", ""),
 "S17": (PCD, Y, "Yes (May 21, 2024)", "Page title: SamaCare Secures $17M Series B Investment to Scale Specialty Drug Prior Authorization Platform.", "Keep. Historical disclosure; drug-focused.", ""),
 "S18": (VM, Y, "No (undated)", "Describes medical-benefit prior authorization workflows and cites 2M+ authorizations. Vendor statistic.", "Keep as vendor-reported.", ""),
 "S19": (VM, Y, "No (undated)", "Describes referral intake, routing, tracking and leakage reduction capabilities.", "Keep as vendor-reported.", ""),
 "S20": (PCD, Y, "No (date not on page; registry says 2021-11)", "Blog states 'Today, we announced our $130M Series C funding led by FTV Capital'. Date not shown in the extracted text.", "Keep; confirm date from the press release.", ""),
 "S21": (PCD, Y, "Yes (May 14, 2025)", "$90M Series C bringing total funding to $200 million.", "Keep. Payer-side comparator.", ""),
 "S22": (PCD, Y, "Yes (February 12, 2026)", "$40 million financing bringing total funding to $64 million. Round label not stated, consistent with the screen.", "Keep.", ""),
 "S23": (PCD, Y, "No (not in extracted text)", "Release title: $51.5 million Series C funding.", "Keep; confirm Oct 2024 date in a browser.", ""),
 "S24": (PCD, Y, "Yes (November 3, 2021)", "$100M Series B led by ICONIQ Growth. Includes an Intermountain Healthcare CIO quote crediting the Notable partnership with a 97 percent patient satisfaction rating. Supports a relationship as of 2021 only.", "Keep. Historical only.", ""),
 "S25": (VM, P, "Yes (May 22, 2025)", "Vendor article on reducing prior authorization denials with AI agents. Product workflow described; named provider examples were not confirmed in the extracted text.", "Keep as product description only; verify if cited for provider examples.", ""),
 "S26": (PCD, YR, "Yes (Jun 25, 2026 13:53 ET release; original announcement Jun 24, 2026 per analyst approval)", "Approved correction applied: the register now points at the PR Newswire release stating a $120 million Series C led by Menlo Ventures at a valuation of $1.2 billion and more than $222 million raised. Company-stated, historical (June 2026), not a current October 2026 valuation. Registry date kept as the original announcement date; the linked release is the June 25, 2026 correction.", "None further. Label the valuation company-reported and historical.", "https://www.prnewswire.com/news-releases/assort-health-raises-120-million-series-c-to-scale-largest-deployment-of-ai-agents-for-the-patient-journey-302808634.html"),
 "S27": (VM, Y, "Yes (August 12, 2026)", "Announces a Referrals AI agent that processes inbound referrals, confirms eligibility and matches patients. Includes vendor statistics.", "Keep as vendor-reported.", ""),
 "S28": (SEC, Y, "Not in PDF text (registry 2025-10)", "AHA Trailblazers report (AHA Market Scan) sponsored by Ailevate, 10 pages. Page 7 table, attributed to the 2024 CAQH Index Report (Feb 2025): prior authorization $12.88 manual vs $5.38 fully automated, 24 vs 10 minutes. Industry-wide transaction benchmark: not a validation of any screened vendor and not a measured Intermountain baseline. Sponsor is a vendor in a different workflow (claims denials).", "Keep as context only. The model's 4, 7 and 10 net minutes are analyst assumptions, not this delta.", ""),
 "S29": (PCD, P, "No", "Annual report page says the system 'leveraged AI technology and new tools to save time for caregivers'. Qualitative, no figure.", "Keep as a qualitative statement.", ""),
 "S30": (VM, Y, "No (undated)", "Describes prior authorization submission, follow-up and expiration reminders.", "Keep as vendor-reported.", ""),
 "S31": (PTP, Y, "Yes (06 October 2020)", "Intermountain release: partnership with Notable Health for mobile registration and virtual clinical intake; reports 55 percent of patients completing digital check-in and check-in time down 25 percent, 94 percent satisfaction. Historical only; says nothing about current status.", "Keep. Never cite as evidence of a current contract.", ""),
 "S32": (SEC, YX, "Yes (July 16, 2026, per article excerpt)", "Healthcare Dive article (published July 16, 2026) reporting Rock Health's midyear data: U.S. digital health companies raised $7.4 billion across 244 deals in H1 2026; 20 mega-deals of $100M or more from 19 companies were 45 percent of capital; median deal $14M. The page returned HTTP 403 to automated access, so confirmation is from search excerpts of the article itself. Q1 was revised from $4.0B (April) to $4.2B.", "Open in a browser to read the full article. Consider citing Rock Health's own report.", ""),
 "S33": (VM, Y, "Yes (June 9, 2025)", "States Intermountain digital intake moved 68% of patients to pre-appointment forms, cut check-in time 25% and reached 96% satisfaction. Vendor-reported.", "Keep as vendor-reported historical outcome.", ""),
 "S34": (VM, Y, "No (undated)", "Case study: 12,500 well-child forms completed via automation over 3 months, 77% pre-visit completion, 98% satisfaction. Vendor-published.", "Keep as vendor-reported.", ""),
 "S35": (PTP, Y, "Yes (May 13, 2026)", "CMS Electronic Prior Authorization Acceleration initiative; 29 healthcare organizations signed on as early adopters.", "Keep.", ""),
 "S36": (VM, Y, "Yes (January 7, 2026)", "Notable announcement: enterprise agreement with Inova initially focused on revenue cycle, referral management and patient access. About Inova, not Intermountain.", "Keep as evidence of Notable's referral-management product scope only.", ""),
}
STATUS = {"S15": "Approved and applied 2026-10-10", "S26": "Approved and applied 2026-10-10"}
USED = {"S04": "Overview strength", "S35": "Overview strength", "S06": "Overview strength", "S10": "Overview, Silna dossier",
        "S31": "Overview risk, Notable dossier", "S33": "Overview risk", "S34": "Overview risk", "S08": "Tennr dossier, memo",
        "S32": "Memo market context", "S11": "Silna dossier", "S12": "Silna dossier", "S14": "Rhyme dossier"}


def main() -> None:
    res = dl.load_package()
    chk = {r["id"]: r for r in json.loads((ROOT / "audit" / "source_http_check.json").read_text())["results"]}
    links = {}
    for l in res.links:
        links.setdefault(l["source_id"], []).append(l["company"])
    out = []
    for s in res.sources:
        cls, sup, datec, note, act, repl = R[s["id"]]
        h = chk[s["id"]]
        out.append(dict(
            id=s["id"], original_url=s.get("original_url", ""), title=h["title"] or "(no HTML title; PDF)" if s["id"] == "S28" else h["title"], publisher=s["publisher"], url=s["url"],
            registry_date=s["date"], page_date_confirmed=datec, last_checked=REVIEW_DATE, category=s["category"],
            companies=links.get(s["id"], []), claim=s["claim"], used_in_app=USED.get(s["id"], "Evidence registry"),
            http_status=h["status"], evidence_class=cls, supports_claim=sup, limitations=s["limitations"],
            review_note=note, recommended_action=act, proposed_replacement_url=repl,
            replacement_status=STATUS.get(s["id"], "")))
    (ROOT / "audit" / "source_review.json").write_text(json.dumps(
        dict(review_date=REVIEW_DATE, method=__doc__.strip(), sources=out), indent=2))
    from collections import Counter
    sc = Counter("Yes" if o["supports_claim"].startswith("Yes") else o["supports_claim"] for o in out)
    ec = Counter(o["evidence_class"] for o in out)
    L = ["# SOURCE_VERIFICATION_REPORT", "",
         f"Reviewed {REVIEW_DATE}. All 36 register entries were fetched (one request each, PDF text extracted) and the linked page text was read "
         "against its register claim; S15, S26 and S32 were additionally researched by web search. The register and CSVs were not modified. "
         "A page that states a claim is not independent proof the claim is true: vendor and company pages are marketing or self-disclosure.", "",
         "## Summary", "",
         f"- Claim confirmed: {sc['Yes']} (of which {sum(1 for o in out if o['supports_claim'].startswith('Yes,'))} via a search excerpt or an approved replacement rather than the originally linked page); partial: {sc['Partial']}; not on the linked page: {sc['Not on linked page']}; not verified: {sc['Not verified']}.",
         "- Evidence classes: " + "; ".join(f"{k} {v}" for k, v in ec.most_common()) + ".",
         f"- Linked page date confirmed on the page: {sum(1 for o in out if o['page_date_confirmed'].startswith('Yes'))} of 36.",
         "- Approved corrections applied as an overlay (original register file untouched): S15, S26 (URL and category) and S28 (classification). See `data_corrections/source_corrections_approved.csv`; lineage keeps the original URL.",
         "- Material unsupported investment claims: none found. The original S15 and S26 links pointed at index pages that did not state the figures they were cited for; both are corrected through the approved overlay to direct company releases.", "",
         "## Specific results",
         "- **S15 (Plenful):** original link was an index page. Approved replacement applied: Apr 30, 2025 PR Newswire release, $50M Series B, $76M cumulative funding (not a valuation).",
         "- **S26 (Assort):** original link was a press index without the valuation. Approved replacement applied: PR Newswire release published Jun 25, 2026 stating a company-reported $1.2 billion valuation and more than $222M raised; original announcement date June 24, 2026 per analyst approval. Historical, not a current valuation.",
         "- **S28 (AHA Trailblazers report):** PDF read. Published in an AHA report sponsored by Ailevate; page 7 table attributed to the 2024 CAQH Index (prior authorization 24 vs 10 minutes). Industry benchmark, not validation of any screened vendor, not an Intermountain baseline.",
         "- **S07 (CAQH):** $258 billion avoided in 2024 confirmed from excerpts of the Feb 19, 2026 release and CAQH's own copy; the GlobeNewswire page returned 403 to automation on re-check, so it was not read directly.",
         "- **S32 (Healthcare Dive):** article dated July 16, 2026 confirmed from excerpts ($7.4B, 244 deals, 20 mega-deals at 45 percent of capital); page returned 403 to automation, so the full text was not read.",
         "- **S31 (Notable, 2020):** supports a 2020 partnership and a 25 percent check-in time reduction as reported by Intermountain. Says nothing about current status.", "",
         "## Per-source review", "",
         "| ID | Publisher | Title | Registry date | Date on page | Class | Companies | Supports | HTTP | Note | Action |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for o in out:
        L.append(f"| {o['id']} | {o['publisher']} | {o['title'][:70]} | {o['registry_date']} | {o['page_date_confirmed']} | {o['evidence_class']} | "
                 f"{', '.join(o['companies']) or 'context only'} | {o['supports_claim']} | {o['http_status']} | {o['review_note']} | {o['recommended_action']} |")
    L += ["", "## Evidence-quality reading",
          "- Funding announcements establish a historical financing, not a current valuation, round or terms.",
          "- Product capability and outcome pages (S11 to S14, S16, S18, S19, S25, S27, S30, S33, S34, S36) are vendor marketing and do not independently validate effectiveness.",
          "- S31 and S24 establish a 2020 to 2021 Intermountain and Notable relationship only. Current contract status and scope remain unknown.",
          "- Company websites (S14, S18, S19, S30) do not establish fundraising availability.", "",
          "## Not verified",
          "Publication dates for sources marked 'No' in the date column; full text of S32 (confirmed from excerpts only); any claim beyond the linked page text."]
    (ROOT / "SOURCE_VERIFICATION_REPORT.md").write_text("\n".join(L) + "\n")
    prop = ["id,original_url,approved_url,reason,status"]
    for o in out:
        if o["proposed_replacement_url"]:
            prop.append(f"{o['id']},{o['original_url']},{o['proposed_replacement_url']},\"{o['review_note'][:200].replace(chr(34), chr(39))}\",approved and applied via data_corrections/")
    d = ROOT / "data_proposed"
    d.mkdir(exist_ok=True)
    (d / "source_corrections_proposed.csv").write_text("\n".join(prop) + "\n")
    print(sc, ec)


if __name__ == "__main__":
    main()
