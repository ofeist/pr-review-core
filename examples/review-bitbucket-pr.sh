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
  --remote <name>         Git remote name (default: origin)
  --adapter <name>        Adapter passed to core.review.cli (default: openai_compat)
  --python-bin <path>     Python executable to run CLI (default: python)
  --output <path>         Output markdown file (default: /tmp/pr-review.md)
  --help                  Show this help

Examples:
  examples/review-bitbucket-pr.sh --target main --source feature/my-change
  examples/review-bitbucket-pr.sh --pr-id 123

Required environment for openai_compat adapter:
  OPENAI_COMPAT_BASE_URL
  OPENAI_COMPAT_MODEL
  OPENAI_COMPAT_API_KEY (if your endpoint requires auth)
USAGE
}

REMOTE="origin"
ADAPTER="openai_compat"
PYTHON_BIN="${PYTHON_BIN:-python}"
OUTPUT="/tmp/pr-review.md"
TARGET=""
SOURCE=""
PR_ID=""

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

if [[ -n "$PR_ID" && ( -n "$TARGET" || -n "$SOURCE" ) ]]; then
  echo "Use either --pr-id OR --target/--source mode, not both." >&2
  exit 1
fi

if [[ -n "$PR_ID" ]]; then
  git fetch "$REMOTE" \
    "refs/pull-requests/$PR_ID/from:refs/remotes/$REMOTE/pr/$PR_ID/from" \
    "refs/pull-requests/$PR_ID/to:refs/remotes/$REMOTE/pr/$PR_ID/to"

  git diff --no-color "$REMOTE/pr/$PR_ID/to...$REMOTE/pr/$PR_ID/from" \
    | "$PYTHON_BIN" -m core.review.cli --input-format raw --adapter "$ADAPTER" \
    > "$OUTPUT"

elif [[ -n "$TARGET" && -n "$SOURCE" ]]; then
  git fetch "$REMOTE"

  git diff --no-color "$REMOTE/$TARGET...$REMOTE/$SOURCE" \
    | "$PYTHON_BIN" -m core.review.cli --input-format raw --adapter "$ADAPTER" \
    > "$OUTPUT"
else
  echo "You must provide either --pr-id OR both --target and --source." >&2
  usage
  exit 1
fi

echo "Review written to: $OUTPUT"
