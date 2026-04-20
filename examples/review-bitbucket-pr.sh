#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  examples/review-bitbucket-pr.sh --target <branch> --source <branch> [options]
  examples/review-bitbucket-pr.sh --pr-id <id> [options]

Options:
  --target <branch>       Target/base branch (for git diff target...source mode)
  --source <branch>       Source/feature branch (for git diff target...source mode)
  --pr-id <id>            Bitbucket Data Center PR ID (refs/pull-requests/<id>/{from,to})
  --pr-title <text>       PR title passed to the review Intent section
  --pr-body <text>        PR description/body passed to the review Intent section
  --remote <name>         Git remote name (default: origin)
  --adapter <name>        Adapter passed to core.review.cli (default: openai-compat)
  --python-bin <path>     Python executable to run CLI (default: python)
  --output <path>         Output markdown file (default: /tmp/pr-review.md)
  --help                  Show this help

Examples:
  examples/review-bitbucket-pr.sh --target main --source feature/my-change
  examples/review-bitbucket-pr.sh --pr-id 123
  examples/review-bitbucket-pr.sh --pr-id 123 --pr-title "$PR_TITLE" --pr-body "$PR_BODY"

Optional Bitbucket Data Center metadata environment for --pr-id mode:
  BITBUCKET_BASE_URL or BB_BASE_URL
  BITBUCKET_PROJECT or BB_PROJECT
  BITBUCKET_REPO or BB_REPO or GIT_REPO_NAME
  BITBUCKET_TOKEN or BB_TOKEN

Required environment for openai-compat adapter:
  OPENAI_COMPAT_BASE_URL
  OPENAI_COMPAT_MODEL
  OPENAI_COMPAT_API_KEY (if your endpoint requires auth)
  OPENAI_COMPAT_DISABLE_THINKING=1 is recommended for direct Qwen/vLLM endpoints.
  REVIEW_DISABLE_REASONING_PROMPT=1 is recommended when using AnythingLLM/proxies.
USAGE
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

die() {
  echo "ERROR: $*" >&2
  exit 1
}

warn() {
  echo "WARNING: $*" >&2
}

json_field() {
  local field="$1"
  "$PYTHON_BIN" -c 'import json, sys; data=json.load(sys.stdin); print(data.get(sys.argv[1]) or "")' "$field"
}

fetch_bitbucket_metadata() {
  [[ -n "$PR_ID" ]] || return 0
  [[ -z "$PR_TITLE" || -z "$PR_BODY" ]] || return 0

  local base_url="${BITBUCKET_BASE_URL:-${BB_BASE_URL:-}}"
  local project="${BITBUCKET_PROJECT:-${BB_PROJECT:-}}"
  local repo="${BITBUCKET_REPO:-${BB_REPO:-${GIT_REPO_NAME:-}}}"
  local token="${BITBUCKET_TOKEN:-${BB_TOKEN:-}}"

  if [[ -z "$base_url" || -z "$project" || -z "$repo" || -z "$token" ]]; then
    warn "Bitbucket metadata env incomplete; Intent may be 'Intent not provided.'"
    return 0
  fi

  local api_url="${base_url%/}/rest/api/1.0/projects/${project}/repos/${repo}/pull-requests/${PR_ID}"
  local json
  if ! json="$(curl -fsSL -H "Authorization: Bearer ${token}" "$api_url")"; then
    warn "Failed to fetch Bitbucket PR metadata from ${api_url}; Intent may be incomplete."
    return 0
  fi

  if [[ -z "$PR_TITLE" ]]; then
    PR_TITLE="$(printf '%s' "$json" | json_field title)"
  fi
  if [[ -z "$PR_BODY" ]]; then
    PR_BODY="$(printf '%s' "$json" | json_field description)"
  fi
}

write_no_changes_review() {
  mkdir -p "$(dirname "$OUTPUT")"
  local intent="${PR_TITLE:-${PR_BODY:-Intent not provided.}}"
  printf '## AI Review\n\n### Summary\nNo changes to review.\n\n### Intent\n%s\n\n### Change Summary\n- Not available.\n\n### Findings\n- No issues found.\n' "$intent" > "$OUTPUT"
}

review_diff() {
  local diff_range="$1"
  mkdir -p "$(dirname "$OUTPUT")"

  local diff_file
  diff_file="$(mktemp)"
  trap 'rm -f "$diff_file"' RETURN
  git diff --no-color "$diff_range" > "$diff_file"

  if [[ ! -s "$diff_file" ]]; then
    write_no_changes_review
    return 0
  fi

  local review_args=(
    "$PYTHON_BIN" -m core.review.cli
    --input-format raw
    --adapter "$ADAPTER"
  )

  if [[ -n "$PR_TITLE" ]]; then
    review_args+=(--pr-title "$PR_TITLE")
  fi
  if [[ -n "$PR_BODY" ]]; then
    review_args+=(--pr-body "$PR_BODY")
  fi

  "${review_args[@]}" < "$diff_file" > "$OUTPUT"
  rm -f "$diff_file"
  trap - RETURN
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)
      TARGET="$2"
      shift 2
      ;;
    --source)
      SOURCE="$2"
      shift 2
      ;;
    --pr-id)
      PR_ID="$2"
      shift 2
      ;;
    --pr-title)
      PR_TITLE="$2"
      shift 2
      ;;
    --pr-body)
      PR_BODY="$2"
      shift 2
      ;;
    --remote)
      REMOTE="$2"
      shift 2
      ;;
    --adapter)
      ADAPTER="$2"
      shift 2
      ;;
    --python-bin)
      PYTHON_BIN="$2"
      shift 2
      ;;
    --output)
      OUTPUT="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ "$ADAPTER" == "openai_compat" ]]; then
  ADAPTER="openai-compat"
fi

if [[ -n "$PR_ID" && ( -n "$TARGET" || -n "$SOURCE" ) ]]; then
  die "Use either --pr-id OR --target/--source mode, not both."
fi

if [[ -n "$PR_ID" ]]; then
  fetch_bitbucket_metadata

  git fetch "$REMOTE" \
    "refs/pull-requests/$PR_ID/from:refs/remotes/$REMOTE/pr/$PR_ID/from" \
    "refs/pull-requests/$PR_ID/to:refs/remotes/$REMOTE/pr/$PR_ID/to"

  review_diff "$REMOTE/pr/$PR_ID/to...$REMOTE/pr/$PR_ID/from"

elif [[ -n "$TARGET" && -n "$SOURCE" ]]; then
  git fetch "$REMOTE"

  review_diff "$REMOTE/$TARGET...$REMOTE/$SOURCE"
else
  echo "ERROR: You must provide either --pr-id OR both --target and --source." >&2
  usage
  exit 1
fi

echo "Review written to: $OUTPUT"
