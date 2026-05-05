#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON:-python3}"

command -v "$PYTHON_BIN" >/dev/null

"$PYTHON_BIN" - <<'PY'
import sys
if sys.version_info < (3, 11):
    raise SystemExit(f"Python 3.11+ is required, found {sys.version.split()[0]}")
print(f"Using Python {sys.version.split()[0]}")
PY

if [[ ! -d "$ROOT/.venv" ]]; then
  "$PYTHON_BIN" -m venv "$ROOT/.venv"
fi

source "$ROOT/.venv/bin/activate"
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e "$ROOT[dev]"
python -m playwright install chromium

cat <<EOF

Setup complete.

Next steps:
  1. source "$ROOT/.venv/bin/activate"
  2. "$ROOT/scripts/gemini_web_login.sh"
  3. "$ROOT/scripts/gemini_web_doctor.sh"
  4. "$ROOT/scripts/gemini_web_inspect_home.sh"

EOF
