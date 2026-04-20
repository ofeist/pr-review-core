#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  examples/ai-pr-review.sh

Jenkins + Bitbucket Data Center wrapper for pr-review-core.

Expected Jenkins/Bitbucket environment:
  CHANGE_ID                         Pull request ID.
  CHANGE_TARGET                     Target/base branch from Jenkins multibranch PR builds.
  BB_BASE_URL / BITBUCKET_BASE_URL  Bitbucket Data Center base URL.
  BB_PROJECT / BITBUCKET_PROJECT    Bitbucket project key.
  BB_REPO / BITBUCKET_REPO          Bitbucket repo slug. GIT_REPO_NAME is also accepted.
  BB_TOKEN / BITBUCKET_TOKEN        Bitbucket token for metadata/comment API.

Review configuration:
  ADAPTER_TYPE                      Adapter passed to core.review.cli. Default: openai-compat.
  PYTHON_BIN                        Python executable with pr-review-core installed. Auto-detected.
  OUTPUT_FILE                       Review markdown path. Default: out/pr-review.md.
  DIFF_FILE                         Raw git diff path. Default: out/pr.diff.
  GIT_REMOTE                        Git remote name. Default: origin.
  PR_TITLE                          Explicit PR title. Fetched from Bitbucket if missing.
  PR_BODY                           Explicit PR description. Fetched from Bitbucket if missing.
  POST_REVIEW_COMMENT               Truthy value posts OUTPUT_FILE back to Bitbucket. Default: 0.
  FAIL_ON_REVIEW_ERROR              Truthy value fails the build on review/post failure. Default: 0.
  PRINT_REVIEW                      Truthy value prints review markdown to logs. Default: 1.
  COMMENT_PREFIX                    Optional markdown prefix added before the posted comment.

OpenAI-compatible/Qwen/vLLM recommended environment:
  OPENAI_COMPAT_BASE_URL            Example: http://vllm.internal:8000/v1
  OPENAI_COMPAT_MODEL               Example: Qwen/Qwen3.5-Coder or qwen3:32b
  OPENAI_COMPAT_API_KEY             Required only if your endpoint/proxy requires auth.
  OPENAI_COMPAT_MAX_OUTPUT_TOKENS   Example: 2000
  OPENAI_COMPAT_DISABLE_THINKING=1  Sends provider-level Qwen/vLLM thinking-disable controls.
  REVIEW_DISABLE_REASONING_PROMPT=1 Adds prompt-level instruction to omit reasoning text.

Notes:
  - This script uses git diff, not Bitbucket's diff API, because pr-review-core expects git diff format.
  - Review failures are non-blocking by default so CI does not fail because the model/proxy is down.
  - No secrets should be hardcoded in this file; use Jenkins credentials/env injection.
USAGE
}

truthy() {
  case "${1:-}" in
    1|true|TRUE|yes|YES|on|ON) return 0 ;;
    *) return 1 ;;
  esac
}

info() {
  echo "INFO: $*" >&2
}

warn() {
  echo "WARNING: $*" >&2
}

fail_or_warn() {
  local message="$1"
  if truthy "$FAIL_ON_REVIEW_ERROR"; then
    echo "ERROR: ${message}" >&2
    exit 1
  fi
  warn "${message}"
  exit 0
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
  elif command -v python >/dev/null 2>&1; then
    command -v python
  else
    die "No Python executable found. Set PYTHON_BIN."
  fi
}

json_field() {
  local field="$1"
  "$PYTHON_BIN" -c 'import json, sys; data=json.load(sys.stdin); print(data.get(sys.argv[1]) or "")' "$field"
}

normalize_adapter() {
  case "$1" in
    openai_compat) printf '%s\n' "openai-compat" ;;
    *) printf '%s\n' "$1" ;;
  esac
}

fetch_pr_metadata() {
  [[ -n "$PR_ID" ]] || return 0
  [[ -z "$PR_TITLE" || -z "$PR_BODY" ]] || return 0

  if [[ -z "$BB_BASE_URL" || -z "$BB_PROJECT" || -z "$BB_REPO" || -z "$BB_TOKEN" ]]; then
    warn "Bitbucket metadata env incomplete; Intent may be 'Intent not provided.'"
    return 0
  fi

  local api_url="${BB_BASE_URL%/}/rest/api/1.0/projects/${BB_PROJECT}/repos/${BB_REPO}/pull-requests/${PR_ID}"
  local json
  if ! json="$(curl -fsSL -H "Authorization: Bearer ${BB_TOKEN}" "$api_url")"; then
    warn "Failed to fetch Bitbucket PR metadata; Intent may be incomplete. URL: ${api_url}"
    return 0
  fi

  if [[ -z "$PR_TITLE" ]]; then
    PR_TITLE="$(printf '%s' "$json" | json_field title)"
  fi
  if [[ -z "$PR_BODY" ]]; then
    PR_BODY="$(printf '%s' "$json" | json_field description)"
  fi
}

build_diff() {
  mkdir -p "$(dirname "$DIFF_FILE")"

  if [[ -n "$CHANGE_TARGET" ]]; then
    info "Fetching target branch ${GIT_REMOTE}/${CHANGE_TARGET}"
    git fetch "$GIT_REMOTE" "refs/heads/${CHANGE_TARGET}:refs/remotes/${GIT_REMOTE}/${CHANGE_TARGET}" \
      || git fetch "$GIT_REMOTE" "$CHANGE_TARGET"

    BASE_REF="${GIT_REMOTE}/${CHANGE_TARGET}"
    HEAD_REF="HEAD"
    git diff --no-ext-diff --no-color "${BASE_REF}...${HEAD_REF}" > "$DIFF_FILE"
    return 0
  fi

  if [[ -n "$PR_ID" ]]; then
    info "Fetching Bitbucket PR refs for PR ${PR_ID}"
    git fetch "$GIT_REMOTE" \
      "refs/pull-requests/${PR_ID}/from:refs/remotes/${GIT_REMOTE}/pr/${PR_ID}/from" \
      "refs/pull-requests/${PR_ID}/to:refs/remotes/${GIT_REMOTE}/pr/${PR_ID}/to"

    BASE_REF="${GIT_REMOTE}/pr/${PR_ID}/to"
    HEAD_REF="${GIT_REMOTE}/pr/${PR_ID}/from"
    git diff --no-ext-diff --no-color "${BASE_REF}...${HEAD_REF}" > "$DIFF_FILE"
    return 0
  fi

  die "Set CHANGE_TARGET or CHANGE_ID/BITBUCKET_PR_ID so the script can build a PR diff."
}

write_no_changes_review() {
  mkdir -p "$(dirname "$OUTPUT_FILE")"
  cat > "$OUTPUT_FILE" <<EOF_REVIEW
## AI Review

### Summary
No changes to review.

### Intent
${PR_TITLE:-${PR_BODY:-Intent not provided.}}

### Change Summary
- Not available.

### Findings
- No issues found.
EOF_REVIEW
}

run_review() {
  mkdir -p "$(dirname "$OUTPUT_FILE")"

  local review_args=(
    "$PYTHON_BIN" -m core.review.cli
    --input-format raw
    --from-file "$DIFF_FILE"
    --adapter "$ADAPTER_TYPE"
  )

  [[ -n "$REPOSITORY" ]] && review_args+=(--repository "$REPOSITORY")
  [[ -n "$BASE_REF" ]] && review_args+=(--base-ref "$BASE_REF")
  [[ -n "$HEAD_REF" ]] && review_args+=(--head-ref "$HEAD_REF")
  [[ -n "$PR_TITLE" ]] && review_args+=(--pr-title "$PR_TITLE")
  [[ -n "$PR_BODY" ]] && review_args+=(--pr-body "$PR_BODY")

  info "Running AI PR review with adapter '${ADAPTER_TYPE}'"
  local error_file
  error_file="$(mktemp)"
  if ! "${review_args[@]}" > "$OUTPUT_FILE" 2>"$error_file"; then
    local error_text
    error_text="$(cat "$error_file")"
    rm -f "$error_file"
    warn "AI review failed (non-blocking by default)."
    [[ -n "$error_text" ]] && echo "$error_text" >&2
    fail_or_warn "AI review failed. Review output was not generated."
  fi
  rm -f "$error_file"
}

build_comment_prefix() {
  if [[ -n "$COMMENT_PREFIX" ]]; then
    printf '%s\n\n' "$COMMENT_PREFIX"
    return 0
  fi

  case "$ADAPTER_TYPE" in
    openai-compat)
      printf 'Model: `%s`\n\n' "${OPENAI_COMPAT_MODEL:-unknown}"
      ;;
    ollama)
      printf 'Model: `%s`\n\n' "${OLLAMA_MODEL:-unknown}"
      ;;
    anything-chat)
      printf 'Adapter: `anything-chat`\n\n'
      ;;
    *)
      printf 'Adapter: `%s`\n\n' "$ADAPTER_TYPE"
      ;;
  esac
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
  local prefix_file
  prefix_file="$(mktemp)"
  trap 'rm -f "$payload_file" "$prefix_file"' RETURN

  build_comment_prefix > "$prefix_file"
  "$PYTHON_BIN" - "$prefix_file" "$OUTPUT_FILE" > "$payload_file" <<'PY'
import json
import sys
from pathlib import Path

prefix = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace")
content = Path(sys.argv[2]).read_text(encoding="utf-8", errors="replace")
print(json.dumps({"text": prefix + content}, ensure_ascii=False))
PY

  local comments_url="${BB_BASE_URL%/}/rest/api/1.0/projects/${BB_PROJECT}/repos/${BB_REPO}/pull-requests/${PR_ID}/comments"
  info "Posting AI review comment to Bitbucket PR ${PR_ID}"
  local response_file
  response_file="$(mktemp)"
  if ! curl -fsSL \
    -H "Authorization: Bearer ${BB_TOKEN}" \
    -H "Content-Type: application/json" \
    -X POST \
    --data-binary "@${payload_file}" \
    "$comments_url" > "$response_file" 2>&1; then
    local response
    response="$(cat "$response_file")"
    rm -f "$payload_file" "$prefix_file" "$response_file"
    trap - RETURN
    warn "Failed to post AI review comment."
    [[ -n "$response" ]] && echo "$response" >&2
    fail_or_warn "Bitbucket comment post failed."
  fi

  rm -f "$payload_file" "$prefix_file" "$response_file"
  trap - RETURN
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  usage
  exit 0
fi

PYTHON_BIN="$(resolve_python_bin)"
ADAPTER_TYPE="$(normalize_adapter "${ADAPTER_TYPE:-${ADAPTER:-openai-compat}}")"
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
FAIL_ON_REVIEW_ERROR="${FAIL_ON_REVIEW_ERROR:-0}"
PRINT_REVIEW="${PRINT_REVIEW:-1}"
COMMENT_PREFIX="${COMMENT_PREFIX:-}"
REPOSITORY="${REPOSITORY:-${BB_PROJECT:+${BB_PROJECT}/${BB_REPO}}}"
BASE_REF="${BASE_REF:-}"
HEAD_REF="${HEAD_REF:-}"

if [[ "$ADAPTER_TYPE" == "openai-compat" ]]; then
  if [[ -z "${OPENAI_COMPAT_DISABLE_THINKING:-}" ]]; then
    warn "OPENAI_COMPAT_DISABLE_THINKING is not set. Set it to 1 for direct Qwen/vLLM thinking control."
  fi
  if [[ -z "${REVIEW_DISABLE_REASONING_PROMPT:-}" ]]; then
    warn "REVIEW_DISABLE_REASONING_PROMPT is not set. Set it to 1 to add prompt-level no-reasoning guidance."
  fi
fi

fetch_pr_metadata
build_diff

if [[ ! -s "$DIFF_FILE" ]]; then
  write_no_changes_review
else
  run_review
fi

post_review_comment

if truthy "$PRINT_REVIEW"; then
  echo "----- ${OUTPUT_FILE} -----"
  cat "$OUTPUT_FILE"
fi

info "Diff written to: ${DIFF_FILE}"
info "Review written to: ${OUTPUT_FILE}"
