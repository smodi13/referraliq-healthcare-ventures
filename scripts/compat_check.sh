#!/bin/bash
# Usage: scripts/compat_check.sh /path/to/python PORT
# Clean copy of the project, fresh venv from requirements-dev.txt, tests, then app start and health probe.
set -u
PY="$1"; PORT="$2"
SRC="$(cd "$(dirname "$0")/.." && pwd)"
W="$(mktemp -d)"
rsync -a --exclude .venv --exclude local_data --exclude .playwright-mcp --exclude __pycache__ --exclude .pytest_cache --exclude screenshots "$SRC"/ "$W"/
cd "$W" || exit 1
echo "python: $($PY --version 2>&1)"
$PY -m venv .venv && .venv/bin/pip install -q -r requirements-dev.txt 2>&1 | grep -v "notice" | tail -3
echo "installed: $(.venv/bin/pip list 2>/dev/null | grep -i -E '^(streamlit|plotly|pandas|openpyxl|pytest) ' | tr -s ' ' '=' | tr '\n' ' ')"
.venv/bin/python -c "import core.financial_math, core.repository, core.components; print('imports ok')"
.venv/bin/python -m pytest -q 2>&1 | tail -2
env -u REFERRALIQ_ANALYST_MODE -u REFERRALIQ_READONLY -u REFERRALIQ_PUBLIC .venv/bin/python -m streamlit run app.py --server.port "$PORT" --server.headless true > server.log 2>&1 &
SP=$!
sleep 7
echo "health (default env, expected read-only): $(curl -s localhost:$PORT/_stcore/health)"
echo "venture route http: $(curl -s -o /dev/null -w '%{http_code}' localhost:$PORT/venture)"
.venv/bin/python scripts/seed_database.py --db "$W/seed_check.db" | tail -1
kill $SP 2>/dev/null
echo "workdir (deleted): $W"
cd / && rm -rf "$W"
