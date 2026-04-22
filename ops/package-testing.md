# Package Testing Guide

Use this guide to verify that the packaged artifact behaves correctly outside the source tree.

For the full adapter env matrix, see `src/core/review/README.md`. For the operations-facing env index, see `ops/CONFIG_FLAGS.md`.

## Fast Path

Run the existing smoke target:

```bash
make smoke-package
```

This target:
- builds `sdist` and wheel
- installs the wheel into `.venv-smoke`
- runs import and CLI smoke from a temporary directory
- avoids repo-root import leakage

## Version Check First

Before building, confirm the checked-out version is the one you intend to test.

```bash
grep -n '^version = ' pyproject.toml
cat .release-please-manifest.json
```

For normal releases, do not hand-edit these values. Release-please updates `pyproject.toml`, `.release-please-manifest.json`, and `CHANGELOG.md` in the release PR.

## Manual Build and Install

### 1. Build artifacts in an isolated venv

```bash
rm -rf build dist *.egg-info
python3 -m venv .venv-build
. .venv-build/bin/activate
python -m pip install --upgrade pip build
python -m build
```

Expected artifacts:
- `dist/pr_review_core-<version>.tar.gz`
- `dist/pr_review_core-<version>-py3-none-any.whl`

### 2. Install the wheel in a separate clean venv

```bash
python3 -m venv .venv-install
. .venv-install/bin/activate
python -m pip install --force-reinstall dist/*.whl
python -c "import core; print(core.__version__)"
```

Expected result:
- printed version matches `pyproject.toml` and `.release-please-manifest.json`

### 3. Smoke the installed package from outside repo root

```bash
REPO_ROOT="$(pwd)"
TMP_DIR="$(mktemp -d)"
cd "$TMP_DIR"
"$REPO_ROOT/.venv-install/bin/python" -m core.review.cli --help > /dev/null
rm -rf "$TMP_DIR"
```

## CLI Smoke Checks

### Fake adapter from fixture diff

```bash
python -m core.review.cli \
  --input-format raw \
  --from-file tests/review/fixtures/raw_small.diff \
  --adapter fake
```

Expected output includes these headings:
- `## AI Review`
- `### Summary`
- `### Intent`
- `### Change Summary`
- `### Findings`

### Parsed JSON path

```bash
python -m core.diff.cli < tests/review/fixtures/raw_small.diff > /tmp/parsed.json
python -m core.review.cli \
  --input-format parsed-json \
  --from-file /tmp/parsed.json \
  --adapter fake
```

### Directly from `git diff`

Review branch diff against main:

```bash
git diff origin/main...HEAD | python -m core.review.cli --input-format raw --adapter fake
```

Review only local uncommitted changes:

```bash
git diff | python -m core.review.cli --input-format raw --adapter fake
```

## OpenAI Adapter Path

Install with extras and set the key:

```bash
pip install --force-reinstall ".[openai]"
export OPENAI_API_KEY="..."
```

Then run:

```bash
python -m core.review.cli \
  --input-format raw \
  --from-file tests/review/fixtures/raw_small.diff \
  --adapter openai
```

## OpenAI-Compatible Adapter Path

Install with extras:

```bash
pip install --force-reinstall ".[openai]"
```

Hosted OpenAI-compatible provider:

```bash
export OPENAI_COMPAT_BASE_URL="https://api.example.ai/v1"
export OPENAI_COMPAT_MODEL="provider/model-name"
python -m core.review.cli \
  --input-format raw \
  --from-file tests/review/fixtures/raw_small.diff \
  --adapter openai-compat
```

Self-hosted vLLM / Qwen:

```bash
export OPENAI_COMPAT_BASE_URL="http://localhost:8000/v1"
export OPENAI_COMPAT_MODEL="Qwen/Qwen3.5-Coder"
export OPENAI_COMPAT_MAX_OUTPUT_TOKENS="2000"
export OPENAI_COMPAT_DISABLE_THINKING="1"
export REVIEW_DISABLE_REASONING_PROMPT="1"
python -m core.review.cli \
  --input-format raw \
  --from-file tests/review/fixtures/raw_small.diff \
  --adapter openai-compat
```

AnythingLLM or another proxy in front of a thinking-capable model:

```bash
export OPENAI_COMPAT_BASE_URL="http://anythingllm:3001/api/v1/openai"
export OPENAI_COMPAT_MODEL="workspace-slug"
export OPENAI_COMPAT_DISABLE_THINKING="1"
export REVIEW_DISABLE_REASONING_PROMPT="1"
export OPENAI_COMPAT_MAX_OUTPUT_TOKENS="2000"
python -m core.review.cli \
  --input-format raw \
  --from-file tests/review/fixtures/raw_small.diff \
  --adapter openai-compat
```

Local gateway with opt-in Ollama fallback:

```bash
export OPENAI_COMPAT_BASE_URL="http://localhost:11434/v1"
export OPENAI_COMPAT_MODEL="qwen3:32b"
export OPENAI_COMPAT_ENABLE_OLLAMA_FALLBACK="1"
python -m core.review.cli \
  --input-format raw \
  --from-file tests/review/fixtures/raw_small.diff \
  --adapter openai-compat
```

## Native Ollama Path

Use this when you want direct `/api/generate` behavior:

```bash
export OLLAMA_BASE_URL="http://localhost:11434"
export OLLAMA_MODEL="qwen3:32b"
export OLLAMA_THINK="false"
python -m core.review.cli \
  --input-format raw \
  --from-file tests/review/fixtures/raw_small.diff \
  --adapter ollama
```

## Common Issues

- `Unknown adapter 'openai'`
  - The `openai` extra or required env config is missing.
- `Unknown adapter 'openai-compat'`
  - `OPENAI_COMPAT_BASE_URL` / `OPENAI_COMPAT_MODEL` or the `openai` extra is missing.
- `Unknown adapter 'ollama'`
  - `OLLAMA_BASE_URL` or `OLLAMA_MODEL` is missing.
- Local/self-hosted models time out
  - Increase timeout vars documented in `src/core/review/README.md` and `ops/CONFIG_FLAGS.md`.
- Output works from repo root but fails after install
  - Re-run smoke from a temporary directory to avoid import leakage.
- `python -m build` fails
  - Install `build` into the active venv with `pip install build`.
