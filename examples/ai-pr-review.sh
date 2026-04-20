#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  examples/ai-pr-review.sh

Jenkins + Bitbucket Data Center wrapper for pr-review-core.

Expected Jenkins/Bitbucket environment:
  CHANGE_ID                 Pull request ID
  CHANGE_TARGET             Target/base branch (for Jenkins multibranch PR builds)
  BB_BASE_URL               Bitbucket Data Center base URL (or BITBUCKET_BASE_URL)
  BB_PROJECT                Bitbucket project key (or BITBUCKET_PROJECT)
  BB_REPO                   Bitbucket repo slug (or BITBUCKET_REPO or GIT_REPO_NAME)
  BB_TOKEN                  Bitbucket token for metadata/comment API (or BITBUCKET_TOKEN)

Optional environment:
  ADAPTER_TYPE              Adapter passed to core.review.cli (default: openai-compat)
  PYTHON_BIN                Python executable with pr-review-core installed
  OUTPUT_FILE               Review markdown path (default: out/pr-review.md)
  DIFF_FILE                 Raw diff path (default: out/pr.diff)
  GIT_REMOTE                Git remote name (default: origin)
  PR_TITLE                  Use this title instead of fetching from Bitbucket
  PR_BODY                   Use this description instead of fetching from Bitbucket
  POST_REVIEW_COMMENT       1/true/yes/on to post OUTPUT_FILE back to Bitbucket
  REVIEW_DISABLE_REASONING_PROMPT
                            1/true/yes/on to add no-reasoning prompt guidance

Required environment for openai-compat adapter:
  OPENAI_COMPAT_BASE_URL
  OPENAI_COMPAT_MODEL
  OPENAI_COMPAT_API_KEY (if your endpoint requires auth)
  OPENAI_COMPAT_DISABLE_THINKING=1 is recommended for direct Qwen/vLLM endpoints.

What this script does:
  1. Builds the review diff with git diff.
  2. Fetches PR title/body from Bitbucket API when available.
  3. Passes title/body to core.review.cli so ### Intent is populated.
  4. Optionally posts the review markdown back to the Bitbucket PR.
USAGE
}

truthy() {
  case "${1:-}" in
    1|true|TRUE|yes|YES|on|ON) return 0 ;;
    *) return 1 ;;
  esac
}

warn() {
  echo "WARNING: $*" >&2
}

die() {
  echo "ERROR: $*" >&2
  exit 1
}

resolve_python_bin() {
  if [[ -n "${PYTHON_BIN:-}" ]]; then
    printf '%s\n' "$PYTHON_BIN"
  elif [[ -x ".venv/Scripts/python.exe" ]]; then
    printf '%s\n' ".venv/Scripts/python.exe"
  elif [[ -x ".venv-pr-review/bin/python" ]]; then
    printf '%s\n' ".venv-pr-review/bin/python"
  elif [[ -x ".venv/bin/python" ]]; then
    printf '%s\n' ".venv/bin/python"
  elif command -v python3 >/dev/null 2>&1; then
    command -v python3
  else
    command -v python || die "No Python executable found. Set PYTHON_BIN."
  fi
}

json_field() {
  local field="$1"
  "$PYTHON_BIN" -c 'import json, sys; data=json.load(sys.stdin); print(data.get(sys.argv[1]) or "")' "$field"
}

fetch_pr_metadata() {
  [[ -n "$PR_ID" ]] || return 0
  [[ -z "$PR_TITLE" || -z "$PR_BODY" ]] || return 0

  if [[ -z "$BB_BASE_URL" || -z "$BB_PROJECT" || -z "$BB_REPO" || -z "$BB_TOKEN" ]]; then
    warn "Bitbucket metadata env incomplete; ### Intent may be 'Intent not provided.'"
    return 0
  fi

  local api_url="${BB_BASE_URL%/}/rest/api/1.0/projects/${BB_PROJECT}/repos/${BB_REPO}/pull-requests/${PR_ID}"
  local json
  if ! json="$(curl -fsSL -H "Authorization: Bearer ${BB_TOKEN}" "$api_url")"; then
    warn "Failed to fetch Bitbucket PR metadata from ${api_url}; ### Intent may be incomplete."
    return 0
  fi

  if [[ -z "$PR_TITLE" ]]; then
    PR_TITLE="$(printf '%s' "$json" | json_field title)"
  fi
  if [[ -z "$PR_BODY" ]]; then
    PR_BODY="$(printf '%s' "$json" | json_field description)"
  fi
}

fetch_and_build_diff() {
  mkdir -p "$(dirname "$DIFF_FILE")"

  if [[ -n "$CHANGE_TARGET" ]]; then
    git fetch "$GIT_REMOTE" "refs/heads/${CHANGE_TARGET}:refs/remotes/${GIT_REMOTE}/${CHANGE_TARGET}" \
      || git fetch "$GIT_REMOTE" "$CHANGE_TARGET"
    git diff --no-color "${GIT_REMOTE}/${CHANGE_TARGET}...HEAD" > "$DIFF_FILE"
    return 0
  fi

  if [[ -n "$PR_ID" ]]; then
    git fetch "$GIT_REMOTE" \
      "refs/pull-requests/${PR_ID}/from:refs/remotes/${GIT_REMOTE}/pr/${PR_ID}/from" \
      "refs/pull-requests/${PR_ID}/to:refs/remotes/${GIT_REMOTE}/pr/${PR_ID}/to"
    git diff --no-color "${GIT_REMOTE}/pr/${PR_ID}/to...${GIT_REMOTE}/pr/${PR_ID}/from" > "$DIFF_FILE"
    return 0
  fi

  die "Set CHANGE_TARGET or CHANGE_ID so the script can build a PR diff."
}

run_review() {
  mkdir -p "$(dirname "$OUTPUT_FILE")"

  local review_args=(
    "$PYTHON_BIN" -m core.review.cli
    --input-format raw
    --from-file "$DIFF_FILE"
    --adapter "$ADAPTER_TYPE"
  )

  if [[ -n "$PR_TITLE" ]]; then
    review_args+=(--pr-title "$PR_TITLE")
  fi
  if [[ -n "$PR_BODY" ]]; then
    review_args+=(--pr-body "$PR_BODY")
  fi

  "${review_args[@]}" > "$OUTPUT_FILE"
}

post_review_comment() {
  if ! truthy "$POST_REVIEW_COMMENT"; then
    return 0
  fi

  [[ -n "$PR_ID" ]] || die "POST_REVIEW_COMMENT requires CHANGE_ID or BITBUCKET_PR_ID."
  [[ -n "$BB_BASE_URL" ]] || die "POST_REVIEW_COMMENT requires BB_BASE_URL or BITBUCKET_BASE_URL."
  [[ -n "$BB_PROJECT" ]] || die "POST_REVIEW_COMMENT requires BB_PROJECT or BITBUCKET_PROJECT."
  [[ -n "$BB_REPO" ]] || die "POST_REVIEW_COMMENT requires BB_REPO, BITBUCKET_REPO, or GIT_REPO_NAME."
  [[ -n "$BB_TOKEN" ]] || die "POST_REVIEW_COMMENT requires BB_TOKEN or BITBUCKET_TOKEN."

  local payload_file
  payload_file="$(mktemp)"
  trap 'rm -f "$payload_file"' RETURN
  "$PYTHON_BIN" - "$OUTPUT_FILE" > "$payload_file" <<'PY'
import json
import sys

with open(sys.argv[1], "r", encoding="utf-8", errors="replace") as handle:
    text = handle.read()
print(json.dumps({"text": text}))
PY

  local comments_url="${BB_BASE_URL%/}/rest/api/1.0/projects/${BB_PROJECT}/repos/${BB_REPO}/pull-requests/${PR_ID}/comments"
  curl -fsSL \
    -H "Authorization: Bearer ${BB_TOKEN}" \
    -H "Content-Type: application/json" \
    -X POST \
    --data-binary "@${payload_file}" \
    "$comments_url" >/dev/null

  rm -f "$payload_file"
  trap - RETURN
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  usage
  exit 0
fi

PYTHON_BIN="$(resolve_python_bin)"
ADAPTER_TYPE="${ADAPTER_TYPE:-${ADAPTER:-openai-compat}}"
if [[ "$ADAPTER_TYPE" == "openai_compat" ]]; then
  ADAPTER_TYPE="openai-compat"
fi

OUTPUT_FILE="${OUTPUT_FILE:-out/pr-review.md}"
DIFF_FILE="${DIFF_FILE:-out/pr.diff}"
GIT_REMOTE="${GIT_REMOTE:-origin}"
PR_ID="${CHANGE_ID:-${BITBUCKET_PR_ID:-${BB_PR_ID:-}}}"
CHANGE_TARGET="${CHANGE_TARGET:-${BITBUCKET_TARGET_BRANCH:-}}"
BB_BASE_URL="${BB_BASE_URL:-${BITBUCKET_BASE_URL:-}}"
BB_PROJECT="${BB_PROJECT:-${BITBUCKET_PROJECT:-}}"
BB_REPO="${BB_REPO:-${BITBUCKET_REPO:-${GIT_REPO_NAME:-}}}"
BB_TOKEN="${BB_TOKEN:-${BITBUCKET_TOKEN:-}}"
PR_TITLE="${PR_TITLE:-${CHANGE_TITLE:-}}"
PR_BODY="${PR_BODY:-${CHANGE_DESCRIPTION:-}}"
POST_REVIEW_COMMENT="${POST_REVIEW_COMMENT:-0}"

fetch_pr_metadata
fetch_and_build_diff

if [[ ! -s "$DIFF_FILE" ]]; then
  mkdir -p "$(dirname "$OUTPUT_FILE")"
  printf '## AI Review\n\n### Summary\nNo changes to review.\n\n### Intent\n%s\n\n### Change Summary\n- Not available.\n\n### Findings\n- No issues found.\n' "${PR_TITLE:-${PR_BODY:-Intent not provided.}}" > "$OUTPUT_FILE"
else
  run_review
fi

post_review_comment

echo "Diff written to: ${DIFF_FILE}"
echo "Review written to: ${OUTPUT_FILE}"
