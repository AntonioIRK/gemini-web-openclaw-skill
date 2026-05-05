#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PY_DEFAULT="$ROOT/.venv/bin/python"
else
  PY_DEFAULT="python3"
fi
PY="${PYTHON:-$PY_DEFAULT}"
command -v "$PY" >/dev/null
"$PY" --version
"$PY" - <<'PY'
import sys
if sys.version_info < (3, 11):
    raise SystemExit(f"Python 3.11+ is required, found {sys.version.split()[0]}")
PY
if ! "$PY" -c 'import playwright' 2>/dev/null; then
  echo "Playwright is not installed in the current interpreter."
  echo "Run: $ROOT/scripts/setup.sh"
fi
if ! command -v playwright >/dev/null 2>&1; then
  echo "Playwright CLI not on PATH, browser install checks skipped."
else
  playwright --version || true
fi

if ! "$PY" -m playwright --version >/dev/null 2>&1; then
  echo "Python Playwright module is missing for $PY."
  echo "Run: $ROOT/scripts/setup.sh"
fi

echo "Environment check finished."
