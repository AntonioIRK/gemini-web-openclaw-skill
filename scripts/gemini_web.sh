#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PY_DEFAULT="$ROOT/.venv/bin/python"
else
  PY_DEFAULT="python3"
fi
PY="${PYTHON:-$PY_DEFAULT}"
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
exec "$PY" -m openclaw_gemini_web.cli "$@"
