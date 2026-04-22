# Consumer Integration Guide

Use this guide when you want to consume `pr-review-core` from another repository or CI system.

This document focuses on practical integration patterns. Core adapter/env details live in `src/core/review/README.md`, and the full runtime env index lives in `ops/CONFIG_FLAGS.md`.

## Install

Choose one installation mode and pin it exactly in CI.

From a local checkout during development:

```bash
python -m pip install .
```

With OpenAI / OpenAI-compatible adapter support:

```bash
python -m pip install ".[openai]"
```

From an exact Git tag:

```bash
python -m pip install "git+https://github.com/ofeist/pr-review-core.git@v<version>"
```

From an exact GitHub Release wheel asset:

```bash
python -m pip install "https://github.com/ofeist/pr-review-core/releases/download/v<version>/pr_review_core-<version>-py3-none-any.whl[openai]"
```

## Pinning Policy

- Pin exact versions in CI and production.
- Avoid floating ranges such as `>=`.
- Upgrade deliberately after changelog review.
- Test upgrades in a branch before changing the default branch pipeline.

Good examples:
- `pr-review-core==<version>`
- `git+https://github.com/ofeist/pr-review-core.git@v<version>`
- direct wheel URL for `v<version>`

## Quick Start

Review a raw diff file:

```bash
python -m core.review.cli \
  --input-format raw \
  --from-file path/to/pr.diff \
  --adapter fake
```

Review via parsed JSON path:

```bash
python -m core.diff.cli < path/to/pr.diff > parsed.json
python -m core.review.cli \
  --input-format parsed-json \
  --from-file parsed.json \
  --adapter fake
```

Review directly from `git diff`:

```bash
git diff origin/main...HEAD | python -m core.review.cli --input-format raw --adapter fake
```

## Adapter Examples

For the full adapter env matrix, see `src/core/review/README.md`.

Hosted OpenAI-compatible provider:

```bash
OPENAI_COMPAT_BASE_URL="https://api.example.ai/v1" \
OPENAI_COMPAT_MODEL="provider/model-name" \
python -m core.review.cli --input-format raw --from-file artifacts/pr.diff --adapter openai-compat
```

Self-hosted vLLM / Qwen:

```bash
OPENAI_COMPAT_BASE_URL="http://vllm.internal:8000/v1" \
OPENAI_COMPAT_MODEL="Qwen/Qwen3.5-Coder" \
OPENAI_COMPAT_DISABLE_THINKING="1" \
REVIEW_DISABLE_REASONING_PROMPT="1" \
OPENAI_COMPAT_MAX_OUTPUT_TOKENS="2000" \
python -m core.review.cli --input-format raw --from-file artifacts/pr.diff --adapter openai-compat
```

AnythingLLM or another proxy in front of a thinking-capable model:

```bash
OPENAI_COMPAT_BASE_URL="http://anythingllm:3001/api/v1/openai" \
OPENAI_COMPAT_MODEL="workspace-slug" \
OPENAI_COMPAT_DISABLE_THINKING="1" \
REVIEW_DISABLE_REASONING_PROMPT="1" \
OPENAI_COMPAT_MAX_OUTPUT_TOKENS="2000" \
python -m core.review.cli --input-format raw --from-file artifacts/pr.diff --adapter openai-compat
```

Native Ollama:

```bash
OLLAMA_BASE_URL="http://localhost:11434" \
OLLAMA_MODEL="qwen3:32b" \
OLLAMA_THINK="false" \
python -m core.review.cli --input-format raw --from-file artifacts/pr.diff --adapter ollama
```

## GitHub Integration

Minimal workflow shape:

```yaml
- name: Setup Python
  uses: actions/setup-python@v5
  with:
    python-version: "3.12"

- name: Install pr-review-core
  run: |
    python -m pip install --upgrade pip
    python -m pip install "git+https://github.com/ofeist/pr-review-core.git@v<version>"

- name: Generate review markdown
  run: |
    python -m core.review.cli \
      --input-format raw \
      --from-file artifacts/pr.diff \
      --adapter fake \
      > artifacts/review.md
```

If you need OpenAI or OpenAI-compatible adapters, install with the `openai` extra and set the required env vars/secrets.

## Bitbucket Integration

Bitbucket-specific auth, retries, comment upsert policy, and pagination should stay in your wrapper scripts or services, not in `core/`.

### Bitbucket Cloud / generic API wrapper

Minimal shape:

```bash
#!/usr/bin/env bash
set -euo pipefail

curl -fsSL \
  -H "Authorization: Bearer ${BITBUCKET_TOKEN}" \
  "${BITBUCKET_API_URL}/repositories/${BB_WORKSPACE}/${BB_REPO}/pullrequests/${PR_ID}/diff" \
  > pr.diff

python -m core.review.cli \
  --input-format raw \
  --from-file pr.diff \
  --adapter fake \
  > review.md

curl -fsSL \
  -H "Authorization: Bearer ${BITBUCKET_TOKEN}" \
  -H 'Content-Type: application/json' \
  -X POST \
  -d "{\"content\":{\"raw\":$(jq -Rs . < review.md)}}" \
  "${BITBUCKET_API_URL}/repositories/${BB_WORKSPACE}/${BB_REPO}/pullrequests/${PR_ID}/comments"
```

### Bitbucket Data Center + Jenkins

Recommended split:
- Jenkins orchestrates checkout/build steps.
- Git builds the diff.
- Bitbucket REST provides PR metadata and comment endpoints.
- `pr-review-core` generates markdown only.

Recommended wrapper:
- `examples/ai-pr-review.sh`

Important:
- The package wheel does not install `examples/` scripts.
- Copy `examples/ai-pr-review.sh` into the consumer repo, Jenkins shared library, or another CI-owned location before use.

Typical flow:
1. Jenkins fetches the PR target branch.
2. Jenkins builds `git diff origin/<target>...HEAD`.
3. Jenkins fetches PR title/body from Bitbucket Data Center.
4. Jenkins runs `core.review.cli` and passes title/body so `### Intent` is populated.
5. Jenkins archives `review.md` and optionally posts it back to the PR.

Minimal Jenkins pipeline example using the wrapper:

```groovy
pipeline {
  agent any

  environment {
    PR_REVIEW_VERSION = '<version>'
    OPENAI_COMPAT_BASE_URL = credentials('openai_compat_base_url')
    OPENAI_COMPAT_API_KEY = credentials('openai_compat_api_key')
    OPENAI_COMPAT_MODEL = 'qwen3:32b'
    OPENAI_COMPAT_TIMEOUT_SECONDS = '300'
    OPENAI_COMPAT_MAX_OUTPUT_TOKENS = '2000'
    OPENAI_COMPAT_DISABLE_THINKING = '1'
    REVIEW_DISABLE_REASONING_PROMPT = '1'
    BB_BASE_URL = 'https://bitbucket.example.com'
    BB_PROJECT = 'PROJECT'
    BB_REPO = 'repo-slug'
  }

  stages {
    stage('Setup') {
      steps {
        sh '''
          python3 -m venv .venv-pr-review
          . .venv-pr-review/bin/activate
          python -m pip install --upgrade pip
          python -m pip install "https://github.com/ofeist/pr-review-core/releases/download/v${PR_REVIEW_VERSION}/pr_review_core-${PR_REVIEW_VERSION}-py3-none-any.whl[openai]"
        '''
      }
    }

    stage('Run Review') {
      steps {
        withCredentials([string(credentialsId: 'bitbucket-pr-review-token', variable: 'BB_TOKEN')]) {
          sh '''
            PYTHON_BIN=".venv-pr-review/bin/python" \
            OUTPUT_FILE="review.md" \
            POST_REVIEW_COMMENT="0" \
            examples/ai-pr-review.sh
          '''
        }
      }
    }

    stage('Archive Review') {
      steps {
        archiveArtifacts artifacts: 'review.md,out/pr.diff', fingerprint: true
      }
    }
  }
}
```

If you do not use the wrapper, pass metadata explicitly:

```bash
PR_JSON="$(curl -fsSL \
  -H "Authorization: Bearer ${BB_TOKEN}" \
  "${BB_BASE_URL}/rest/api/1.0/projects/${BB_PROJECT}/repos/${BB_REPO}/pull-requests/${CHANGE_ID}")"

PR_TITLE="$(printf '%s' "$PR_JSON" | python -c 'import json,sys; print((json.load(sys.stdin).get("title") or ""))')"
PR_BODY="$(printf '%s' "$PR_JSON" | python -c 'import json,sys; print((json.load(sys.stdin).get("description") or ""))')"

git fetch origin "refs/heads/${CHANGE_TARGET}:refs/remotes/origin/${CHANGE_TARGET}"
git diff --no-color "origin/${CHANGE_TARGET}...HEAD" > pr.diff

python -m core.review.cli \
  --input-format raw \
  --from-file pr.diff \
  --adapter openai-compat \
  --pr-title "$PR_TITLE" \
  --pr-body "$PR_BODY" \
  > review.md
```

To publish back to Bitbucket Data Center without the wrapper:

```bash
curl -fsSL \
  -H "Authorization: Bearer ${BITBUCKET_TOKEN}" \
  -H 'Content-Type: application/json' \
  -X POST \
  -d "{\"text\": $(python -c 'import json,sys; print(json.dumps(sys.stdin.read()))' < review.md)}" \
  "${BITBUCKET_BASE_URL}/rest/api/1.0/projects/${BITBUCKET_PROJECT}/repos/${BITBUCKET_REPO}/pull-requests/${BITBUCKET_PR_ID}/comments"
```

Alternative local/manual helper for Bitbucket PR refs:

```bash
examples/review-bitbucket-pr.sh --pr-id "$CHANGE_ID" \
  --pr-title "$PR_TITLE" \
  --pr-body "$PR_BODY" \
  --python-bin ".venv-pr-review/bin/python" \
  --adapter openai-compat \
  --output review.md
```

Operational recommendation:
- Start by archiving `review.md` only.
- Add PR comment posting after the review quality is acceptable.
- Keep Bitbucket/Jenkins retry and comment-upsert behavior outside the core package.

## Validation Commands

```bash
python -m core.review.cli --input-format raw --from-file tests/review/fixtures/raw_small.diff --adapter fake
python -m core.diff.cli < tests/review/fixtures/raw_small.diff > /tmp/parsed.json
python -m core.review.cli --input-format parsed-json --from-file /tmp/parsed.json --adapter fake
```
