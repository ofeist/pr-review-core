# Consumer Integration Guide

This guide shows how external repositories can consume `pr-review-core` as a package.

## 1. Install

Choose one installation mode.

- From local checkout (development):
  - `python -m pip install .`
- With OpenAI/OpenAI-compatible adapter support:
  - `python -m pip install ".[openai]"`
- From a tagged GitHub release:
  - `python -m pip install "git+https://github.com/ofeist/pr-review-core.git@v0.3.0"`
- From GitHub Release wheel asset (exact immutable artifact):
  - `python -m pip install "https://github.com/ofeist/pr-review-core/releases/download/v0.3.0/pr_review_core-0.3.0-py3-none-any.whl"`

## 1.1 Pinning Policy for Consumers
- Always pin exact versions in CI/production:
  - Good: `pr-review-core==0.3.0`
  - Good: `git+https://github.com/ofeist/pr-review-core.git@v0.3.0`
  - Avoid: `pr-review-core>=0.3.0`
- Upgrade on a planned cadence (for example biweekly/monthly) with changelog review.
- Test upgrades in a branch before rolling into default branch pipelines.

## 2. Quickstart

Run a local review from a raw diff file:

```bash
python -m core.review.cli \
  --input-format raw \
  --from-file path/to/pr.diff \
  --adapter fake
```

Run review via parsed JSON path:

```bash
python -m core.diff.cli < path/to/pr.diff > parsed.json
python -m core.review.cli \
  --input-format parsed-json \
  --from-file parsed.json \
  --adapter fake
```

## 3. GitHub Integration (Package Mode)

In your GitHub workflow job:

```yaml
- name: Setup Python
  uses: actions/setup-python@v5
  with:
    python-version: "3.12"

- name: Install pr-review-core
  run: |
    python -m pip install --upgrade pip
    python -m pip install "git+https://github.com/ofeist/pr-review-core.git@v0.3.0"

- name: Generate review markdown
  run: |
    python -m core.review.cli \
      --input-format raw \
      --from-file artifacts/pr.diff \
      --adapter fake \
      > artifacts/review.md
```

For OpenAI mode, install with extras and set secrets:

```bash
python -m pip install "git+https://github.com/ofeist/pr-review-core.git@v0.3.0#egg=pr-review-core[openai]"
```

Required secret:
- `OPENAI_API_KEY`

Adapter env vars (required/optional/defaults) are centralized in:
- `src/core/review/README.md` ("Adapter Env Matrix (Canonical)")

Examples:

```bash
# Hosted OpenAI-compatible provider
OPENAI_COMPAT_BASE_URL="https://api.example.ai/v1" \
OPENAI_COMPAT_MODEL="provider/model-name" \
python -m core.review.cli --input-format raw --from-file artifacts/pr.diff --adapter openai-compat

# Self-hosted vLLM
OPENAI_COMPAT_BASE_URL="http://vllm.internal:8000/v1" \
OPENAI_COMPAT_MODEL="Qwen/Qwen2.5-Coder-7B-Instruct" \
python -m core.review.cli --input-format raw --from-file artifacts/pr.diff --adapter openai-compat

# Local gateway (Ollama-compatible endpoint)
OPENAI_COMPAT_BASE_URL="http://localhost:11434/v1" \
OPENAI_COMPAT_MODEL="qwen2.5-coder" \
python -m core.review.cli --input-format raw --from-file artifacts/pr.diff --adapter openai-compat

# Local gateway with explicit fallback enabled
OPENAI_COMPAT_BASE_URL="http://localhost:11434/v1" \
OPENAI_COMPAT_MODEL="qwen3:32b" \
OPENAI_COMPAT_ENABLE_OLLAMA_FALLBACK="1" \
python -m core.review.cli --input-format raw --from-file artifacts/pr.diff --adapter openai-compat
```

Example:

```bash
OLLAMA_BASE_URL="http://localhost:11434" \
OLLAMA_MODEL="qwen3:32b" \
python -m core.review.cli --input-format raw --from-file artifacts/pr.diff --adapter ollama
```

## 4. Bitbucket Interim Integration (Script/API Wrapper)

Use Bitbucket API for extraction/publication and `pr-review-core` for review generation.

```bash
#!/usr/bin/env bash
set -euo pipefail

# 1) Fetch PR diff from Bitbucket REST API.
curl -fsSL \
  -H "Authorization: Bearer ${BITBUCKET_TOKEN}" \
  "${BITBUCKET_API_URL}/repositories/${BB_WORKSPACE}/${BB_REPO}/pullrequests/${PR_ID}/diff" \
  > pr.diff

# 2) Generate review markdown.
python -m core.review.cli \
  --input-format raw \
  --from-file pr.diff \
  --adapter fake \
  > review.md

# 3) Publish comment back to the PR.
curl -fsSL \
  -H "Authorization: Bearer ${BITBUCKET_TOKEN}" \
  -H 'Content-Type: application/json' \
  -X POST \
  -d "{\"content\":{\"raw\":$(jq -Rs . < review.md)}}" \
  "${BITBUCKET_API_URL}/repositories/${BB_WORKSPACE}/${BB_REPO}/pullrequests/${PR_ID}/comments"
```

Keep Bitbucket-specific logic (auth, retries, pagination, comment upsert strategy) in your wrapper scripts/services, not in `core/`.

## 4.1 Bitbucket Data Center with Jenkins

Recommended split:
- Jenkins handles PR build orchestration.
- Bitbucket Data Center provides PR metadata/diff/comment APIs.
- `pr-review-core` generates review markdown from raw diff input.

Typical flow:
1. Jenkins checks out the PR source branch and fetches the target branch.
2. Jenkins builds a raw diff with `git diff origin/<target>...HEAD`.
3. Jenkins runs `python -m core.review.cli` and writes `review.md`.
4. Jenkins archives `review.md` and optionally posts it to the Bitbucket PR.

Minimal Jenkins pipeline example:

```groovy
pipeline {
  agent any

  environment {
    PR_REVIEW_VERSION = '0.3.0'
    OPENAI_COMPAT_BASE_URL = credentials('openai_compat_base_url')
    OPENAI_COMPAT_API_KEY = credentials('openai_compat_api_key')
    OPENAI_COMPAT_MODEL = 'qwen3:32b'
    OPENAI_COMPAT_TIMEOUT_SECONDS = '300'
    OPENAI_COMPAT_MAX_OUTPUT_TOKENS = '2000'
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

    stage('Build Diff') {
      steps {
        sh '''
          git fetch origin "${CHANGE_TARGET}"
          git diff --no-color "origin/${CHANGE_TARGET}...HEAD" > pr.diff
        '''
      }
    }

    stage('Run Review') {
      steps {
        sh '''
          . .venv-pr-review/bin/activate
          python -m core.review.cli \
            --input-format raw \
            --from-file pr.diff \
            --adapter openai_compat \
            > review.md
        '''
      }
    }

    stage('Archive Review') {
      steps {
        archiveArtifacts artifacts: 'review.md', fingerprint: true
      }
    }
  }
}
```

To publish back to Bitbucket DC, add a final step that posts `review.md` to the PR comments endpoint:

```bash
curl -fsSL \
  -H "Authorization: Bearer ${BITBUCKET_TOKEN}" \
  -H 'Content-Type: application/json' \
  -X POST \
  -d "{\"text\": $(jq -Rs . < review.md)}" \
  "${BITBUCKET_BASE_URL}/rest/api/1.0/projects/${BITBUCKET_PROJECT}/repos/${BITBUCKET_REPO}/pull-requests/${BITBUCKET_PR_ID}/comments"
```

Operational guidance:
- Start by archiving `review.md` only.
- Add PR comment posting after the review output looks acceptable.
- Keep Bitbucket/Jenkins-specific retry/upsert logic outside `core/`.

## 5. Validation Commands

These commands are used to validate consumer docs against fixture input:

```bash
python -m core.review.cli --input-format raw --from-file tests/review/fixtures/raw_small.diff --adapter fake
python -m core.diff.cli < tests/review/fixtures/raw_small.diff > /tmp/parsed.json
python -m core.review.cli --input-format parsed-json --from-file /tmp/parsed.json --adapter fake
```
