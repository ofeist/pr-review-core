#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  examples/review-bitbucket-pr.sh --target <branch> --source <branch> [options]
  examples/review-bitbucket-pr.sh --pr-id <id> [options]

Options:
  --target <branch>       Target/base branch for git diff target...source mode.
  --source <branch>       Source/feature branch for git diff target...source mode.
  --pr-id <id>            Bitbucket Data Center PR ID: refs/pull-requests/<id>/{from,to}.
  --pr-title <text>       PR title passed to prompt context and output Intent section.
  --pr-body <text>        PR description passed to prompt context and output Intent section.
  --repository <text>     Repository identifier passed to prompt context.
  --remote <name>         Git remote name. Default: origin.
  --adapter <name>        Adapter passed to core.review.cli. Default: openai-compat.
  --python-bin <path>     Python executable with pr-review-core installed. Default: python.
  --output <path>         Output markdown file. Default: /tmp/pr-review.md.
  --post-comment          Post the generated review to the Bitbucket PR comment endpoint.
  --print-review          Print generated review markdown to stdout.
  --fail-on-error         Fail when review generation or comment posting fails.
  --help                  Show this help.

Optional Bitbucket Data Center metadata/comment environment for --pr-id mode:
  BITBUCKET_BASE_URL or BB_BASE_URL
  BITBUCKET_PROJECT or BB_PROJECT
  BITBUCKET_REPO or BB_REPO or GIT_REPO_NAME
  BITBUCKET_TOKEN or BB_TOKEN

OpenAI-compatible/Qwen/vLLM recommended environment:
  OPENAI_COMPAT_BASE_URL="http://vllm.internal:8000/v1"
  OPENAI_COMPAT_MODEL="Qwen/Qwen3.5-Coder"
  OPENAI_COMPAT_MAX_OUTPUT_TOKENS="2000"
  OPENAI_COMPAT_DISABLE_THINKING="1"
  REVIEW_DISABLE_REASONING_PROMPT="1"

Notes:
  - This script reviews git diff output, not Bitbucket's REST diff format.
  - No secrets should be hardcoded in this file; use environment variables or CI credentials.
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

die() {
  echo "ERROR: $*" >&2
  exit 1
}

fail_or_warn() {
  local message="$1"
  if truthy "$FAIL_ON_ERROR"; then
    die "$message"
  fi
  warn "$message"
  exit 0
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

fetch_bitbucket_metadata() {
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

  [[ -z "$PR_TITLE" ]] && PR_TITLE="$(printf '%s' "$json" | json_field title)"
  [[ -z "$PR_BODY" ]] && PR_BODY="$(printf '%s' "$json" | json_field description)"
}

write_no_changes_review() {
  mkdir -p "$(dirname "$OUTPUT")"
  cat > "$OUTPUT" <<EOF_REVIEW
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

review_diff_file() {
  local diff_file="$1"
  local base_ref="$2"
  local head_ref="$3"
  mkdir -p "$(dirname "$OUTPUT")"

  if [[ ! -s "$diff_file" ]]; then
    write_no_changes_review
    return 0
  fi

  local review_args=(
    "$PYTHON_BIN" -m core.review.cli
    --input-format raw
    --from-file "$diff_file"
    --adapter "$ADAPTER"
  )

  [[ -n "$REPOSITORY" ]] && review_args+=(--repository "$REPOSITORY")
  [[ -n "$base_ref" ]] && review_args+=(--base-ref "$base_ref")
  [[ -n "$head_ref" ]] && review_args+=(--head-ref "$head_ref")
  [[ -n "$PR_TITLE" ]] && review_args+=(--pr-title "$PR_TITLE")
  [[ -n "$PR_BODY" ]] && review_args+=(--pr-body "$PR_BODY")

  local error_file
  error_file="$(mktemp)"
  if ! "${review_args[@]}" > "$OUTPUT" 2>"$error_file"; then
    local error_text
    error_text="$(cat "$error_file")"
    rm -f "$error_file"
    [[ -n "$error_text" ]] && echo "$error_text" >&2
    fail_or_warn "AI review failed."
  fi
  rm -f "$error_file"
}

build_comment_prefix() {
  case "$ADAPTER" in
    openai-compat) printf 'Model: `%s`\n\n' "${OPENAI_COMPAT_MODEL:-unknown}" ;;
    ollama) printf 'Model: `%s`\n\n' "${OLLAMA_MODEL:-unknown}" ;;
    *) printf 'Adapter: `%s`\n\n' "$ADAPTER" ;;
  esac
}

post_comment() {
  truthy "$POST_COMMENT" || return 0

  [[ -n "$PR_ID" ]] || die "--post-comment requires --pr-id."
  [[ -n "$BB_BASE_URL" ]] || die "--post-comment requires BB_BASE_URL or BITBUCKET_BASE_URL."
  [[ -n "$BB_PROJECT" ]] || die "--post-comment requires BB_PROJECT or BITBUCKET_PROJECT."
  [[ -n "$BB_REPO" ]] || die "--post-comment requires BB_REPO, BITBUCKET_REPO, or GIT_REPO_NAME."
  [[ -n "$BB_TOKEN" ]] || die "--post-comment requires BB_TOKEN or BITBUCKET_TOKEN."

  local payload_file prefix_file response_file
  payload_file="$(mktemp)"
  prefix_file="$(mktemp)"
  response_file="$(mktemp)"
  trap 'rm -f "$payload_file" "$prefix_file" "$response_file"' RETURN

  build_comment_prefix > "$prefix_file"
  "$PYTHON_BIN" - "$prefix_file" "$OUTPUT" > "$payload_file" <<'PY'
import json
import sys
from pathlib import Path

prefix = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace")
content = Path(sys.argv[2]).read_text(encoding="utf-8", errors="replace")
print(json.dumps({"text": prefix + content}, ensure_ascii=False))
PY

  local comments_url="${BB_BASE_URL%/}/rest/api/1.0/projects/${BB_PROJECT}/repos/${BB_REPO}/pull-requests/${PR_ID}/comments"
  if ! curl -fsSL \
    -H "Authorization: Bearer ${BB_TOKEN}" \
    -H "Content-Type: application/json" \
    -X POST \
    --data-binary "@${payload_file}" \
    "$comments_url" > "$response_file" 2>&1; then
    cat "$response_file" >&2
    fail_or_warn "Bitbucket comment post failed."
  fi

  rm -f "$payload_file" "$prefix_file" "$response_file"
  trap - RETURN
}

REMOTE="origin"
ADAPTER="${ADAPTER:-${ADAPTER_TYPE:-openai-compat}}"
PYTHON_BIN="${PYTHON_BIN:-python}"
OUTPUT="/tmp/pr-review.md"
TARGET=""
SOURCE=""
PR_ID=""
PR_TITLE="${PR_TITLE:-${CHANGE_TITLE:-}}"
PR_BODY="${PR_BODY:-${CHANGE_DESCRIPTION:-}}"
REPOSITORY="${REPOSITORY:-}"
POST_COMMENT="0"
PRINT_REVIEW="0"
FAIL_ON_ERROR="0"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGET="${2:?}"; shift 2 ;;
    --source) SOURCE="${2:?}"; shift 2 ;;
    --pr-id) PR_ID="${2:?}"; shift 2 ;;
    --pr-title) PR_TITLE="${2:?}"; shift 2 ;;
    --pr-body) PR_BODY="${2:?}"; shift 2 ;;
    --repository) REPOSITORY="${2:?}"; shift 2 ;;
    --remote) REMOTE="${2:?}"; shift 2 ;;
    --adapter) ADAPTER="${2:?}"; shift 2 ;;
    --python-bin) PYTHON_BIN="${2:?}"; shift 2 ;;
    --output) OUTPUT="${2:?}"; shift 2 ;;
    --post-comment) POST_COMMENT="1"; shift ;;
    --print-review) PRINT_REVIEW="1"; shift ;;
    --fail-on-error) FAIL_ON_ERROR="1"; shift ;;
    --help|-h) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 1 ;;
  esac
done

ADAPTER="$(normalize_adapter "$ADAPTER")"
BB_BASE_URL="${BB_BASE_URL:-${BITBUCKET_BASE_URL:-}}"
BB_PROJECT="${BB_PROJECT:-${BITBUCKET_PROJECT:-}}"
BB_REPO="${BB_REPO:-${BITBUCKET_REPO:-${GIT_REPO_NAME:-}}}"
BB_TOKEN="${BB_TOKEN:-${BITBUCKET_TOKEN:-}}"
REPOSITORY="${REPOSITORY:-${BB_PROJECT:+${BB_PROJECT}/${BB_REPO}}}"

if [[ "$ADAPTER" == "openai-compat" ]]; then
  [[ -z "${OPENAI_COMPAT_DISABLE_THINKING:-}" ]] && warn "Set OPENAI_COMPAT_DISABLE_THINKING=1 for direct Qwen/vLLM thinking control."
  [[ -z "${REVIEW_DISABLE_REASONING_PROMPT:-}" ]] && warn "Set REVIEW_DISABLE_REASONING_PROMPT=1 to add prompt-level no-reasoning guidance."
fi

if [[ -n "$PR_ID" && ( -n "$TARGET" || -n "$SOURCE" ) ]]; then
  die "Use either --pr-id OR --target/--source mode, not both."
fi

DIFF_FILE="$(mktemp)"
trap 'rm -f "$DIFF_FILE"' EXIT

if [[ -n "$PR_ID" ]]; then
  fetch_bitbucket_metadata
  info "Fetching Bitbucket PR refs for PR ${PR_ID}"
  git fetch "$REMOTE" \
    "refs/pull-requests/${PR_ID}/from:refs/remotes/${REMOTE}/pr/${PR_ID}/from" \
    "refs/pull-requests/${PR_ID}/to:refs/remotes/${REMOTE}/pr/${PR_ID}/to"
  BASE_REF="${REMOTE}/pr/${PR_ID}/to"
  HEAD_REF="${REMOTE}/pr/${PR_ID}/from"
  git diff --no-ext-diff --no-color "${BASE_REF}...${HEAD_REF}" > "$DIFF_FILE"
  review_diff_file "$DIFF_FILE" "$BASE_REF" "$HEAD_REF"
elif [[ -n "$TARGET" && -n "$SOURCE" ]]; then
  info "Fetching remote refs from ${REMOTE}"
  git fetch "$REMOTE"
  BASE_REF="${REMOTE}/${TARGET}"
  HEAD_REF="${REMOTE}/${SOURCE}"
  git diff --no-ext-diff --no-color "${BASE_REF}...${HEAD_REF}" > "$DIFF_FILE"
  review_diff_file "$DIFF_FILE" "$BASE_REF" "$HEAD_REF"
else
  usage
  die "Provide either --pr-id OR both --target and --source."
fi

post_comment

if truthy "$PRINT_REVIEW"; then
  cat "$OUTPUT"
fi

info "Review written to: ${OUTPUT}"
