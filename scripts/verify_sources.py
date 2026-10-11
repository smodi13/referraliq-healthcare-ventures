"""Polite one-request-per-source link check. Records HTTP status and whether the claim's key figures appear
in the static page text. A reachable page does NOT prove the claim; an unreachable page does NOT disprove it.
Output: audit/source_http_check.json. Does not bypass logins, paywalls or rate limits."""
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core import data_loader as dl  # noqa: E402

UA = "ReferralIQ-source-check/1.0 (independent portfolio project; single read-only request per URL)"


def key_tokens(claim: str) -> list[str]:
    toks = re.findall(r"\$?\d[\d,.]*\s?[MBKmbk]?\b", claim)
    out = []
    for t in toks:
        core = re.sub(r"[^\d.]", "", t)
        if len(core) >= 2 and core not in out:
            out.append(core)
    return out[:6]


def fetch(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/pdf,*/*;q=0.5"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            body = r.read(1_500_000)
            return dict(status=r.status, final_url=r.geturl(), ctype=r.headers.get("Content-Type", ""), body=body)
    except urllib.error.HTTPError as e:
        return dict(status=e.code, final_url=url, ctype="", body=b"")
    except Exception as e:  # network, TLS, timeout
        return dict(status=None, final_url=url, ctype="", body=b"", error=type(e).__name__ + ": " + str(e)[:120])


def main() -> None:
    res = dl.load_package()
    out = []
    for s in res.sources:
        r = fetch(s["url"])
        text = r["body"].decode("utf-8", "ignore") if "pdf" not in r["ctype"].lower() else ""
        plain = re.sub(r"<[^>]+>", " ", text)
        toks = key_tokens(s["claim"])
        found = [t for t in toks if t in plain.replace(",", "")]
        m = re.search(r"<title[^>]*>(.*?)</title>", text, re.S | re.I)
        st = r["status"]
        if st is None:
            label = "NETWORK ERROR (not verified)"
        elif st in (401, 403, 429):
            label = f"BLOCKED OR RESTRICTED HTTP {st} (inaccessible to this check, not disproven)"
        elif st in (404, 410):
            label = f"NOT FOUND HTTP {st} (link may be stale; claim not disproven)"
        elif 200 <= st < 300 and "pdf" in r["ctype"].lower():
            label = "REACHABLE PDF (text not parsed; claim support not checked)"
        elif 200 <= st < 300 and toks and found:
            label = "REACHABLE, key figures present in page text (claim support still needs human read)"
        elif 200 <= st < 300:
            label = "REACHABLE, key figures not found in static text (JS-rendered, paywalled or different wording)"
        else:
            label = f"HTTP {st} (not verified)"
        out.append(dict(id=s["id"], publisher=s["publisher"], date=s["date"], category=s["category"], url=s["url"],
                        status=st, final_url=r["final_url"], redirected=r["final_url"].rstrip("/") != s["url"].rstrip("/"),
                        title=(re.sub(r"\s+", " ", m.group(1)).strip()[:140] if m else ""), tokens=toks, tokens_found=found,
                        result=label, error=r.get("error", "")))
        print(s["id"], st, label[:60], flush=True)
        time.sleep(1.0)
    (ROOT / "audit" / "source_http_check.json").write_text(json.dumps(
        dict(checked_at=datetime.now(timezone.utc).isoformat(timespec="seconds"), user_agent=UA, results=out), indent=2))


if __name__ == "__main__":
    main()
