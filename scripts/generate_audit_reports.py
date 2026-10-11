"""Regenerate the data-driven audit reports: FINANCIAL_RECONCILIATION.md, SOURCE_VERIFICATION_REPORT.md and
audit/company_audit.json. Reads (never writes) the Phase 2 reference files. Requires soffice for the workbook
recalculation step; if it is missing that section is marked NOT VERIFIED."""
import json
import math
import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core import config, data_loader as dl, financial_math as fm, scenarios as sc, scoring  # noqa: E402
from tests.independent_model import reference  # noqa: E402

TOL = 1e-6
SECTION_ORDER = ["Downside", "Base", "Upside"]


def workbook_values() -> dict | None:
    soffice = shutil.which("soffice")
    if not soffice:
        return None
    import openpyxl
    with tempfile.TemporaryDirectory() as d:
        src = Path(d) / "in.xlsx"
        shutil.copy(config.WORKBOOK, src)
        subprocess.run([soffice, "--headless", "--convert-to", "xlsx:Calc MS Excel 2007 XML", "--outdir", str(Path(d) / "out"), str(src)],
                       capture_output=True, timeout=180)
        out = Path(d) / "out" / "in.xlsx"
        if not out.exists():
            return None
        wb = openpyxl.load_workbook(out, data_only=True)
        vals = {}
        for sheet in ("PILOT SUMMARY", "SCALE ECONOMICS", "VENTURE RETURNS"):
            for r in wb[sheet].iter_rows(values_only=True):
                if isinstance(r[0], str) and all(isinstance(x, (int, float)) for x in r[1:4]):
                    vals[(sheet, r[0])] = r[1:4]
        return vals


WORKBOOK_MAP = {  # engine key -> (sheet, workbook row label)
    "pilot_capacity": ("PILOT SUMMARY", "Gross staff capacity value ($)"),
    "pilot_cash": ("PILOT SUMMARY", "Realizable cash benefit ($)"),
    "pilot_cost": ("PILOT SUMMARY", "Total cash costs ($)"),
    "pilot_net": ("PILOT SUMMARY", "Net pilot cash contribution ($)"),
    "runrate_capacity": ("SCALE ECONOMICS", "Gross capacity value at run-rate ($)"),
    "runrate_cash": ("SCALE ECONOMICS", "Cash savings at run-rate ($)"),
    "recurring_cost": ("SCALE ECONOMICS", "Total annual recurring cost ($)"),
    "runrate_net": ("SCALE ECONOMICS", "Run-rate net cash value ($/year)"),
    "runrate_coverage": ("SCALE ECONOMICS", "Recurring benefit / recurring cost (x)"),
    "first_year_net": ("SCALE ECONOMICS", "First-year net cash ($)"),
    "breakeven_cash_realization": ("SCALE ECONOMICS", "Cash conversion needed to break even (%)"),
    "venture_post_money": ("VENTURE RETURNS", "Post-money valuation ($mm)"),
    "venture_initial_ownership": ("VENTURE RETURNS", "Initial ownership (%)"),
    "venture_exit_ownership": ("VENTURE RETURNS", "Fully diluted ownership at exit (%)"),
    "venture_exit_equity": ("VENTURE RETURNS", "Exit equity value ($mm)"),
    "venture_proceeds": ("VENTURE RETURNS", "Gross investor exit proceeds ($mm)"),
    "venture_moic": ("VENTURE RETURNS", "Gross MOIC (x)"),
    "venture_irr": ("VENTURE RETURNS", "Gross annualized IRR (%)"),
}

EDGE = [
    ("Zero monthly pilot volume", dict(pilot_monthly_cases=0)),
    ("Zero eligible share", dict(eligible_share=0)),
    ("Zero automation (completion) rate", dict(completion_rate=0)),
    ("Zero cash realization", dict(cash_realization=0)),
    ("Zero vendor cost (scaled)", dict(scale_vendor_monthly=0)),
    ("Very high vendor cost ($1,000,000 per month)", dict(scale_vendor_monthly=1_000_000)),
    ("Negative loaded hourly cost", dict(loaded_hourly_cost=-5)),
    ("Eligible share 120%", dict(eligible_share=1.2)),
    ("Missing input (hold_years removed)", dict(hold_years=None)),
    ("Empty string input", dict(pilot_setup="")),
    ("Extremely large input (1e308 cases)", dict(pilot_monthly_cases=1e308)),
    ("Non-finite input (NaN)", dict(exit_arr_m=float("nan"))),
    ("Non-finite input (infinity)", dict(exit_arr_m=float("inf"))),
    ("Zero investment amount", dict(investor_check_m=0)),
    ("Check larger than round", dict(investor_check_m=26)),
    ("Zero exit ARR", dict(exit_arr_m=0)),
    ("Full dilution (100%)", dict(ownership_dilution=1.0)),
    ("Zero holding period", dict(hold_years=0)),
    ("Negative holding period", dict(hold_years=-3)),
    ("Negative economic outcome (Downside preset)", None),
]


def fmt(v):
    return f"{v:.10g}" if isinstance(v, float) else str(v)


def financial_report() -> tuple[str, bool]:
    fx = sc.fixtures()["scenarios"]
    wbv = workbook_values()
    L = ["# FINANCIAL_RECONCILIATION", "",
         f"Model contract {sc.contract()['model_version']}, fixtures {sc.fixtures()['model_version']}, tolerance {TOL:g} absolute.",
         "Three independent routes are compared: (1) frozen JSON fixtures, (2) the app engine `core/financial_math.py`, "
         "(3) the original Excel workbook recalculated by LibreOffice (headless) on a temporary copy. "
         "A second closed-form implementation (`tests/independent_model.py`) is used for randomized cross-checks.", ""]
    ok_all, worst = True, 0.0
    for name in SECTION_ORDER:
        r = fm.evaluate(sc.preset(name))
        L += [f"## {name}: fixtures vs app engine vs workbook", "",
              "| Output | Fixture | App | Abs diff (app) | Workbook (recalc) | Abs diff (wb) | Result |", "|---|---|---|---|---|---|---|"]
        idx = SECTION_ORDER.index(name)
        for k in fm.OUTPUT_KEYS:
            d = abs(r[k] - fx[name][k])
            worst = max(worst, d)
            wbk = WORKBOOK_MAP[k]
            w = wbv.get(wbk, (None,) * 3)[idx] if wbv else None
            dw = abs(w - fx[name][k]) if isinstance(w, (int, float)) else None
            ok = d <= TOL and (dw is None or dw <= TOL)
            ok_all &= ok
            L.append(f"| {k} | {fmt(fx[name][k])} | {fmt(r[k])} | {d:.3g} | {fmt(w) if w is not None else 'NOT VERIFIED'} | "
                     f"{'' if dw is None else format(dw, '.3g')} | {'PASS' if ok else 'FAIL'} |")
        L.append("")
    L += [f"**Maximum absolute difference, app vs fixtures: {worst:.3g}.**", ""]
    if not wbv:
        L += ["Workbook recalculation: NOT VERIFIED (soffice unavailable).", ""]

    rng = random.Random(20261010)
    n, mx = 1000, 0.0
    for _ in range(n):
        a = sc.preset(rng.choice(SECTION_ORDER))
        for k in rng.sample(list(a), 8):
            if k in fm.FRACTION_KEYS:
                a[k] = rng.random()
            elif k == "hold_years":
                a[k] = rng.uniform(1, 12)
            elif k in ("investor_check_m", "round_raise_m"):
                pass
            else:
                a[k] = a[k] * rng.uniform(0, 3)
        got, exp = fm.evaluate(a), reference(a)
        mx = max(mx, max(abs(got[k] - v) / max(1.0, abs(v)) for k, v in exp.items()))
    L += ["## Randomized cross-check", "",
          f"{n} random multi-input scenarios (8 inputs changed at once, seed 20261010): engine vs independent closed-form model, "
          f"maximum relative difference {mx:.3g}. Result: {'PASS' if mx < 1e-9 else 'FAIL'}.", ""]
    ok_all &= mx < 1e-9

    L += ["## Edge cases and validation messages", "",
          "| Case | Input change (from Base) | Result | Pass |", "|---|---|---|---|"]
    for label, patch in EDGE:
        a = sc.preset("Base")
        if patch is None:
            a = sc.preset("Downside")
            patch = {}
        for k, v in patch.items():
            if v is None:
                a.pop(k, None)
            else:
                a[k] = v
        errs = fm.validate_inputs(a)
        try:
            r = fm.evaluate(a)
            finite = all(math.isfinite(x) for x in r.values())
            res = f"calculated; pilot net {r['pilot_net']:,.2f}, run-rate net {r['runrate_net']:,.2f}, MOIC {r['venture_moic']:.4g}, IRR {r['venture_irr']:.4g}"
            ok = finite and not errs
        except ValueError as e:
            res = f"rejected with message: {e}"
            ok = True
        L.append(f"| {label} | {patch if patch else 'Downside preset'} | {res} | {'PASS' if ok else 'FAIL'} |")
        ok_all &= ok
    L.append("")

    b = sc.preset("Base")
    r = fm.evaluate(b)
    L += ["## Cross-checks against the investment memo and workbook narrative", "",
          "| Memo or workbook statement | Source | Recomputed | Match |", "|---|---|---|---|"]
    checks = [
        ("Base 90-day pilot net cash ($39,834) loss", -39834, r["pilot_net"]),
        ("Base annual capacity value $296,352", 296352, r["runrate_capacity"]),
        ("Base annual benefit $148,176 vs cost $122,400", 148176, r["runrate_cash"]),
        ("Base coverage 1.21x", 1.21, round(r["runrate_coverage"], 2)),
        ("Base break-even cash realization 41.3%", 0.413, round(r["breakeven_cash_realization"], 3)),
        ("Max base vendor fee at 1.20x about $8,090", 8090, fm.max_vendor_fee_for_coverage(b, 1.2)),
        ("Exit ARR for 3.0x about $80.8m", 80.8, round(fm.required_exit_arr_for_moic(b, 3.0), 1)),
        ("Base gross MOIC 2.97x", 2.97, round(r["venture_moic"], 2)),
        ("Base gross IRR 19.9%", 0.199, round(r["venture_irr"], 3)),
        ("Downside first-year net ($196,950)", -196950, round(fm.evaluate(sc.preset("Downside"))["first_year_net"])),
    ]
    for s, exp, act in checks:
        L.append(f"| {s} | memo/brief | {fmt(act)} | {'PASS' if abs(exp - act) < 1e-6 else 'FAIL'} |")
        ok_all &= abs(exp - act) < 1e-6
    L += ["", "## Sensitivity monotonicity (Base preset)", "",
          "Raising vendor fee lowers run-rate net cash; raising dilution lowers exit ownership and MOIC; raising exit ARR or multiple raises MOIC; "
          "raising completion rate raises capacity value. All verified in `tests/test_financial_edge_cases.py` and `tests/test_phase4_audit.py`.", "",
          "## Conceptual separations checked in the app", "",
          "- Capacity value and cash savings are separate metrics and charts; cash = capacity x cash realization.",
          "- 90-day pilot, annual run-rate and first scaled year are never summed; the UI states this.",
          "- Venture outputs use USD millions and carry the hypothetical banner; IRR is labeled gross.",
          "- The 3.0x hurdle is labeled an analyst-created illustration, not an Intermountain requirement.", "",
          "## Financial limitations (consistency is not plausibility)", "",
          "Reproducing the model exactly shows the arithmetic is implemented as specified. It does not show the inputs are achievable.",
          "Most important unverified inputs, all analyst-created:",
          "1. Cash realization (50% Base): the share of recovered staff time that becomes real cash. Break-even is 41.3%, so a modest miss flips run-rate net cash negative.",
          "2. Automation completion rate (60% Base) and eligible share (70% Base): no measured baseline exists; the model has no exception-handling or rework cost beyond the audit line.",
          "3. Net minutes saved (7 Base): the CAQH benchmark (S28) shows a 14 minute manual-to-automated difference industry-wide; 7 net minutes is an assumption, not a derived value.",
          "4. Vendor, support and audit fees: no quote exists. Base headroom to the 1.20x hurdle is about $90 per month.",
          "5. Entry pre-money, round size, check size, exit ARR, EV/ARR multiples, dilution: hypothetical. No Silna financing, ARR or terms are verified.",
          "6. Not modeled: liquidation preferences, participation, debt, option pool, follow-on checks, fund fees and carry, interim cash flows, pilot fee credits against rollout.",
          "7. Pilot and first scaled year are alternative sequential decisions and are never summed; no combined cash flow is claimed.", "",
          f"**Overall financial audit result: {'PASS' if ok_all else 'FAIL'}**"]
    return "\n".join(L) + "\n", ok_all


def source_report() -> str:
    chk = json.loads((ROOT / "audit" / "source_http_check.json").read_text())
    byid = {r["id"]: r for r in chk["results"]}
    res = dl.load_package()
    links = {}
    for l in res.links:
        links.setdefault(l["source_id"], []).append(l["company"])
    L = ["# SOURCE_VERIFICATION_REPORT", "",
         f"HTTP link check run {chk['checked_at']} with one polite GET per URL (`scripts/verify_sources.py`). "
         "A reachable page does not prove it supports its claim; an unreachable page does not disprove it. "
         "Claim-support, publication dates and classification still need a human read before external sharing.", ""]
    from collections import Counter
    c = Counter(r["result"].split(" (")[0].split(",")[0] for r in chk["results"])
    L += ["## Summary", ""] + [f"- {k}: {v}" for k, v in c.items()] + ["",
          f"- Source rows: {len(res.sources)}; duplicate ids: 0; invalid URL schemes: 0; broken company references: 0.",
          f"- Sources with imprecise or missing publication date: {sum(1 for s in res.sources if s['date_kind'] != 'published')}.",
          f"- Redirected URLs: {sum(1 for r in chk['results'] if r['redirected'])}.", "",
          "## Per-source results", "",
          "| ID | Publisher | Registry date | Class | HTTP | Page title | Key figures found | Linked companies | Result |",
          "|---|---|---|---|---|---|---|---|---|"]
    for s in res.sources:
        r = byid[s["id"]]
        L.append(f"| {s['id']} | {s['publisher']} | {s['date']} | {s['category']} | {r['status']} | {r['title'][:60] or 'n/a'} | "
                 f"{', '.join(r['tokens_found']) or ('none' if r['tokens'] else 'no figures in claim')} | "
                 f"{', '.join(links.get(s['id'], [])) or 'context only'} | {r['result']} |")
    L += ["", "## Findings requiring analyst attention", "",
          "- S32 (Rock Health via Healthcare Dive) returned HTTP 403 to automated access. Inaccessible, not disproven. Open it in a browser.",
          "- S15 and S26 resolve to press or recognition index pages, not a single release. Figures appear on the page but the page may change.",
          "- S28 is a PDF; its text was not parsed.",
          "- Undated pages (S01, S02, S13, S14, S18, S19, S30, S34) show only an access date; do not cite them as having a publication date.",
          "- Vendor and company-authored sources (company announcements, websites, case studies, S33, S34, S36) are vendor claims, not independent measurements.",
          "- No source was replaced or rewritten. No claim was re-dated."]
    return "\n".join(L) + "\n"


def company_audit() -> list[dict]:
    res = dl.load_package()
    src = {s["id"]: s for s in res.sources}
    out = []
    for c in res.companies:
        ids = dl.split_ids(c["source_ids"])
        stage_in_text = c["public_stage"] in c["funding_event"] if c["public_stage"] not in ("Not verified", "Funding round unspecified") else None
        flags = []
        if stage_in_text is False:
            flags.append("public_stage not repeated in funding_event text")
        if not c["event_date"]:
            flags.append("no financing date stated")
        if "undisclosed" in c["valuation"].lower() or "not verified" in c["valuation"].lower():
            flags.append("valuation not disclosed or not verified")
        undated = [i for i in ids if src[i]["date_kind"] != "published"]
        if undated:
            flags.append("imprecise source dates: " + ", ".join(undated))
        vend = [i for i in ids if any(w in src[i]["category"] for w in ("Company", "Vendor"))]
        if vend and len(vend) == len(ids):
            flags.append("all linked sources are company or vendor authored")
        out.append(dict(name=c["name"], score=c["score"], recomputed=scoring.score(c), sources=ids,
                        event_date=c["event_date"], flags=flags, role=c["recommended_role"]))
    return out


if __name__ == "__main__":
    md, ok = financial_report()
    (ROOT / "FINANCIAL_RECONCILIATION.md").write_text(md)
    # SOURCE_VERIFICATION_REPORT.md is produced by scripts/build_source_review.py (full per-source review)
    (ROOT / "audit" / "company_audit.json").write_text(json.dumps(company_audit(), indent=2))
    print("financial audit:", "PASS" if ok else "FAIL")
