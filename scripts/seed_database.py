"""Idempotent database seed: python scripts/seed_database.py [--db PATH]"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core import config, repository  # noqa: E402


def main() -> None:
    db = sys.argv[sys.argv.index("--db") + 1] if "--db" in sys.argv else None
    checks = json.loads(config.MANIFEST_JSON.read_text())["sha256"] if config.MANIFEST_JSON.exists() else {}
    con = repository.connect(db)
    load = repository.seed(con, checksums=checks)
    print(f"Seeded {len(load.companies)} companies, {len(load.sources)} sources, {len(load.links)} csv links into {db or config.DB_PATH}")


if __name__ == "__main__":
    main()
