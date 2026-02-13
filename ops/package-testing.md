# Package Testing Guide

Use this guide to verify the built package behaves correctly in an isolated environment.

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

## Common Issues

- `Unknown adapter 'openai'. Known adapters: fake`
  - OpenAI extra or env config is missing.
- Output works from repo root but fails after install
  - run smoke from a temp directory to avoid import leakage.
- Missing build tools
  - install `build` in the venv (`pip install build`).
