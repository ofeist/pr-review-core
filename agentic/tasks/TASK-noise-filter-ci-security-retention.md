# Task

## ID
noise-filter-ci-security-retention

## Branch
feature/noise-filter-ci-security-retention

## Goal
Fix the review noise filter so high-signal security findings are not dropped just because they mention CI,
pipeline, or workflow context.

## Scope
- Update `src/core/review/noise_filter.py`.
- Keep high-signal security findings that mention terms such as `pipeline`, `workflow`, or `CI` when they clearly
describe a real issue.
- Preserve the existing filtering of low-signal CI/meta commentary.
- Add focused regression tests in `tests/review/test_noise_filter.py`.
- Add a changelog note because this changes review-output behavior.

## Out of Scope
- Adapter request changes.
- Prompt redesign.
- Output-normalizer behavior changes.
- Jenkins/Bitbucket wrapper changes.
- Broad retuning of all maintainability or style findings.

## Risks
- If the CI/meta filter is loosened too broadly, noisy workflow commentary may return.
- If the change is too narrow, some real security findings may still be dropped.
- Because this changes filtered review output, release-policy implications should be checked explicitly.

## Verification Plan
- Run `python -m unittest -v tests/review/test_noise_filter.py`.
- Replay real model outputs where:
  - a hardcoded secret is described as being in a `pipeline script`
  - a commented-out config contradiction is present
  - maintainability-only leftovers are still filtered
- Confirm that the security finding survives while low-signal CI commentary does not.

## Notes
- This slice is based on real Bitbucket/Jenkins runs where a hardcoded-secret finding was lost after filtering
because the text mentioned `pipeline script`.
- Keep the fix narrowly targeted to high-signal security retention in CI context.
