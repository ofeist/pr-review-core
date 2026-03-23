#!/usr/bin/env bash
set -euo pipefail

BASE_REF="${1:-origin/main}"

if ! git rev-parse --verify "$BASE_REF" >/dev/null 2>&1; then
  echo "Base ref not found: $BASE_REF" >&2
  exit 1
fi

FILES="$(git diff --name-only "$BASE_REF"...HEAD)"

echo "Changed files relative to $BASE_REF:"
if [ -n "$FILES" ]; then
  printf '%s\n' "$FILES"
else
  echo "  (none)"
fi

echo
cat <<'OUT'
Suggested verification ladder for this repo:
1. Run focused tests for the files or behavior you changed.
2. If app behavior, generated docs, or multiple layers changed, run `make ci-local`.
3. If deploy, billing, webhook, migration, or env wiring changed, plan a staging validation.
4. Use prod only after staging passes and rollout risk is understood.
OUT

if printf '%s\n' "$FILES" | grep -Eq '^(deploy/|\.github/workflows/|ops/|docs/).+'; then
  echo
  echo "This diff touches deploy/workflow/docs paths. Check config coupling and rollout notes."
fi
if printf '%s\n' "$FILES" | grep -Eq '^(api/|db/|tests/).+'; then
  echo
  echo "This diff touches app/db/test paths. Prefer targeted tests before broader checks."
fi