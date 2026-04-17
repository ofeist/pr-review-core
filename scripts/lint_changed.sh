#!/usr/bin/env bash
set -euo pipefail

BASE_REF="${1:-origin/main}"

if ! git rev-parse --verify "$BASE_REF" >/dev/null 2>&1; then
  echo "Base ref not found: $BASE_REF" >&2
  exit 1
fi

echo "Comparing working tree against $BASE_REF"
FILES="$(git diff --name-only "$BASE_REF"...HEAD)"

if [ -z "$FILES" ]; then
  echo "No changed files relative to $BASE_REF"
  exit 0
fi

echo
printf '%s\n' "$FILES"

echo
if printf '%s\n' "$FILES" | grep -Eq '^(api/|tests/).+\.py$'; then
  echo "Python changes detected: run targeted Python checks first"
fi
if printf '%s\n' "$FILES" | grep -Eq '^(www/|docs/|ops/).+'; then
  echo "Docs/web changes detected: verify wording, generated docs, and user-facing text"
fi
if printf '%s\n' "$FILES" | grep -Eq '^(deploy/|\.github/workflows/).+'; then
  echo "Deploy/workflow changes detected: inspect env wiring and rollout path carefully"
fi