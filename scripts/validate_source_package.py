"""Read-only preflight: checksums, counts, integrity. Writes audit/source_inventory.json (first run only,
unless --refresh) and audit/preflight_notes.md. Never touches the reference files."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core import config, data_loader as dl, scoring  # noqa: E402


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(refresh: bool = False) -> int:
    config.AUDIT_DIR.mkdir(exist_ok=True)
    current = {f: sha(ROOT / f) for f in config.REFERENCE_FILES}
    if config.MANIFEST_JSON.exists() and not refresh:
        saved = json.loads(config.MANIFEST_JSON.read_text())["sha256"]
        changed = [f for f in current if saved.get(f) != current[f]]
        print("Checksums:", "UNCHANGED" if not changed else f"CHANGED {changed}")
        if changed:
            return 2
    else:
        res = dl.load_package()
        inv = {"model_version": config.MODEL_VERSION, "as_of": config.AS_OF, "sha256": current,
               "companies": len(res.companies), "sources": len(res.sources), "links": len(res.links)}
        config.MANIFEST_JSON.write_text(json.dumps(inv, indent=2))
        print("Wrote", config.MANIFEST_JSON)
    res = dl.load_package()
    print(f"companies={len(res.companies)} sources={len(res.sources)} links={len(res.links)}")
    for i in res.issues:
        print(f"[{i.severity}] {i.code}: {i.message}")
    print("score audit:", scoring.audit_original(res.companies) or "stored scores match weighted formula")
    return 1 if res.errors else 0


if __name__ == "__main__":
    sys.exit(main("--refresh" in sys.argv))
