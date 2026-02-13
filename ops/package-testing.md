# Package Testing Guide

Use this guide to verify the built package behaves correctly in an isolated environment.

Canonical env matrix for adapters:
- `src/core/review/README.md` ("Adapter Env Matrix (Canonical)")

## Create Latest Version Package (release-candidate flow)

Use this when you want to produce artifacts for the current latest version in the repo.

### 0. Confirm version metadata first

- Update/check `pyproject.toml` version.
- Update/check `CHANGELOG.md` notes for the same version.

Quick check:

```bash
rg -n "^version = " pyproject.toml
```

### 1. Build in an isolated venv

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

### 2. Install wheel in a separate clean venv

```bash
python3 -m venv .venv-install
. .venv-install/bin/activate
python -m pip install --force-reinstall dist/*.whl
python -c "import core; print(core.__version__)"
```

Expected:
- Printed version matches `pyproject.toml`.

### 3. Smoke the installed package from outside repo root

```bash
REPO_ROOT="$(pwd)"
TMP_DIR="$(mktemp -d)"
cd "$TMP_DIR"
"$REPO_ROOT/.venv-install/bin/python" -m core.review.cli --help > /dev/null
rm -rf "$TMP_DIR"
```

Optional full smoke in one command:

```bash
make smoke-package
```

## Fast Path (recommended)

Run the existing smoke target:

```bash
make smoke-package
```

This does all of the following:
- builds `sdist` + wheel
- installs the wheel into `.venv-smoke`
- runs import + CLI smoke from a temp directory (avoids repo-root import leakage)

## Manual Validation (step-by-step)

### 1. Build artifacts

```bash
python3 -m venv .venv-build
. .venv-build/bin/activate
python -m pip install --upgrade pip build
python -m build
```

Expected artifacts:
- `dist/pr_review_core-<version>.tar.gz`
- `dist/pr_review_core-<version>-py3-none-any.whl`

### 2. Install wheel in clean venv

```bash
python3 -m venv .venv-install
. .venv-install/bin/activate
pip install --force-reinstall dist/*.whl
```

### 3. Run fake-adapter CLI smoke

```bash
python -m core.review.cli \
  --input-format raw \
  --from-file tests/review/fixtures/raw_small.diff \
  --adapter fake
```

Expected output includes headings:
- `## AI Review`
- `### Summary`
- `### Intent`
- `### Change Summary`
- `### Findings`

### 4. Validate parsed-json path

```bash
python -m core.diff.cli < tests/review/fixtures/raw_small.diff > /tmp/parsed.json
python -m core.review.cli \
  --input-format parsed-json \
  --from-file /tmp/parsed.json \
  --adapter fake
```

### 5. Run directly from `git diff` (very useful in real repos)

Review branch diff against main:

```bash
git diff origin/main...HEAD | python -m core.review.cli --input-format raw --adapter fake
```

Review only local uncommitted changes:

```bash
git diff | python -m core.review.cli --input-format raw --adapter fake
```

## Optional OpenAI Path

Install with extras and set secret:

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

## Optional OpenAI-Compatible Path

Install with extras:

```bash
pip install --force-reinstall ".[openai]"
```

Example: hosted OpenAI-compatible provider

```bash
export OPENAI_COMPAT_BASE_URL="https://api.example.ai/v1"
export OPENAI_COMPAT_MODEL="provider/model-name"
python -m core.review.cli \
  --input-format raw \
  --from-file tests/review/fixtures/raw_small.diff \
  --adapter openai-compat
```

Example: self-hosted vLLM

```bash
export OPENAI_COMPAT_BASE_URL="http://localhost:8000/v1"
export OPENAI_COMPAT_MODEL="Qwen/Qwen2.5-Coder-7B-Instruct"
python -m core.review.cli \
  --input-format raw \
  --from-file tests/review/fixtures/raw_small.diff \
  --adapter openai-compat
```

Example: local gateway (Ollama-compatible endpoint)

```bash
export OPENAI_COMPAT_BASE_URL="http://localhost:11434/v1"
export OPENAI_COMPAT_MODEL="qwen2.5-coder"
python -m core.review.cli \
  --input-format raw \
  --from-file tests/review/fixtures/raw_small.diff \
  --adapter openai-compat
```

Example: enable opt-in fallback to native Ollama when `responses` output is empty

```bash
export OPENAI_COMPAT_BASE_URL="http://localhost:11434/v1"
export OPENAI_COMPAT_MODEL="qwen3:32b"
export OPENAI_COMPAT_ENABLE_OLLAMA_FALLBACK="1"
python -m core.review.cli \
  --input-format raw \
  --from-file tests/review/fixtures/raw_small.diff \
  --adapter openai-compat
```

## Optional Ollama Native Path

Use this when you want direct `/api/generate` behavior:

```bash
export OLLAMA_BASE_URL="http://localhost:11434"
export OLLAMA_MODEL="qwen3:32b"
python -m core.review.cli \
  --input-format raw \
  --from-file tests/review/fixtures/raw_small.diff \
  --adapter ollama
```

## Common Issues

- `Unknown adapter 'openai'. Known adapters: fake`
  - OpenAI extra or env config is missing.
- `Unknown adapter 'openai-compat'. Known adapters: ...`
  - `OPENAI_COMPAT_BASE_URL`/`OPENAI_COMPAT_MODEL` or OpenAI extra is missing.
- `Unknown adapter 'ollama'. Known adapters: ...`
  - `OLLAMA_BASE_URL` or `OLLAMA_MODEL` is missing.
- Slow local models timeout
  - increase timeout vars from the canonical matrix in `src/core/review/README.md`.
- Output works from repo root but fails after install
  - run smoke from a temp directory to avoid import leakage.
- Missing build tools
  - install `build` in the venv (`pip install build`).
