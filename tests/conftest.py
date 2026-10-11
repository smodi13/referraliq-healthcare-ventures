import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
# Keep the developer database untouched by tests and smoke runs.
os.environ.setdefault("REFERRALIQ_DB", str(ROOT / "local_data" / "test_session.db"))
os.environ["REFERRALIQ_ANALYST_MODE"] = "1"  # most tests exercise the analyst workflow; read-only tests override explicitly
os.environ.pop("REFERRALIQ_READONLY", None)
os.environ.pop("REFERRALIQ_PUBLIC", None)
