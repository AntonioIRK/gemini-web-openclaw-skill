#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "validate_install.sh checks environment and post-login session basics."
echo "It assumes Gemini login was already completed in the persistent browser profile."

"$ROOT/scripts/ensure_env.sh"
"$ROOT/scripts/gemini_web_doctor.sh"
"$ROOT/scripts/gemini_web_inspect_home.sh"
