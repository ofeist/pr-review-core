# Release Checklist

Use this checklist before creating a release tag.

## 1. Branch and Version Prep
- Confirm release branch is up to date with `main`.
- Confirm `pyproject.toml` version is correct for intended bump.
- Confirm `CHANGELOG.md` has release notes for the target version.

## 2. Validation
- Run review suite:
  - `PYTHONPATH=src python3 -m unittest -q tests/review/test_types.py tests/review/test_prompt_builder.py tests/review/test_model_adapter.py tests/review/test_output_normalizer.py tests/review/test_openai_adapter.py tests/review/test_noise_filter.py tests/review/test_chunking.py tests/review/test_fallback.py tests/review/test_cli.py tests/review/test_pipeline_fixtures.py tests/review/test_markdown_snapshots.py`
- Run package smoke:
  - `make smoke-package`
- Verify package-smoke CI workflow is green on the PR.

## 3. Dry-Run Verification (Manual)
- Build artifacts exist under `dist/`.
- Installed wheel can run CLI from outside repository root.
- Smoke output contains canonical markdown headings.
- For exact venv/build/install steps, follow `ops/package-testing.md` ("Create Latest Version Package").

## 4. Tag and Release
- Create annotated tag: `git tag -a v<version> -m "Release v<version>"`
- Push tag: `git push origin v<version>`
- Confirm tag-triggered package smoke workflow succeeds.

## 5. Post-Release
- Confirm changelog is merged on `main`.
- Announce release with compatibility impact summary.
