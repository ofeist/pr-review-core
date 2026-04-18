# Release Checklist

Use this checklist before creating a release tag.

Release order is strict: merge normal PRs first, let release-please create/update the release PR, merge that release PR, then tag the exact generated version.

## 1. Normal PR Prep
- Confirm the normal PR branch is up to date with `main`.
- Confirm each normal PR has exactly one release label (`release:patch|release:minor|release:major`).
- Labeling reference: `ops/versioning-automation.md` ("How to Set Release Label").
- Do not manually bump `pyproject.toml` for routine releases.

## 2. Validation Before Merge
- Run review suite:
  - `PYTHONPATH=src python3 -m unittest -q tests/review/test_types.py tests/review/test_prompt_builder.py tests/review/test_model_adapter.py tests/review/test_output_normalizer.py tests/review/test_openai_adapter.py tests/review/test_noise_filter.py tests/review/test_chunking.py tests/review/test_fallback.py tests/review/test_cli.py tests/review/test_pipeline_fixtures.py tests/review/test_markdown_snapshots.py`
- Run package smoke:
  - `make smoke-package`
- Verify package-smoke CI workflow is green on the PR.

## 3. Release PR Verification
- After normal PRs are merged, wait for `chore(release): vX.Y.Z`.
- Confirm the release PR updates:
  - `pyproject.toml`
  - `.release-please-manifest.json`
  - `CHANGELOG.md`
- Confirm the generated version and changelog match the intended bump.
- Merge the release PR only after the package-smoke workflow is green.

## 4. Dry-Run Verification (Manual)
- Build artifacts exist under `dist/`.
- Installed wheel can run CLI from outside repository root.
- Smoke output contains canonical markdown headings.
- For exact venv/build/install steps, follow `ops/package-testing.md` ("Create Latest Version Package").

## 5. Tag and Release
- Pull updated `main` after the release PR merge:
  - `git switch main`
  - `git pull --ff-only`
- Read the release version from `pyproject.toml` or `.release-please-manifest.json`.
- Create annotated tag: `git tag -a v<version> -m "Release v<version>"`
- Push tag: `git push origin v<version>`
- Confirm tag-triggered package smoke workflow succeeds.
- Confirm tag-triggered release-consistency workflow succeeds.
- Confirm tag-triggered release-assets workflow succeeds.
- Confirm GitHub Release contains both assets:
  - `pr_review_core-<version>-py3-none-any.whl`
  - `pr_review_core-<version>.tar.gz`

## 6. Post-Release
- Confirm changelog is merged on `main`.
- Announce release with compatibility impact summary.
