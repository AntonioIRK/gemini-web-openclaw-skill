#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

forbidden_re='^(\.gemini-web-profile/|\.gemini-storybook-profile/|tmp/|playwright-report/|test-results/|\.venv/)|(^|/)(Cookies|Login Data|Web Data)$|\.sqlite(-journal)?$|\.trace\.zip$|\.har$'

tracked="$(git ls-files)"
if printf '%s\n' "$tracked" | grep -E "$forbidden_re" >/dev/null; then
  echo "Tracked private/runtime artifacts detected:" >&2
  printf '%s\n' "$tracked" | grep -E "$forbidden_re" >&2
  exit 1
fi

echo "Repo hygiene OK"
