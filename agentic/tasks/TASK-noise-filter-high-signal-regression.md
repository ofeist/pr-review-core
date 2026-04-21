# Task

## ID
noise-filter-high-signal-regression

## Branch
feature/noise-filter-high-signal-regression

## Goal
Fix the review noise filter so high-signal findings such as hardcoded secrets are not dropped while low-signal findings do not survive because of weak evidence matching such as the generic marker `line `.

## Scope
- Update `src/core/review/noise_filter.py`.
- Narrow the evidence-matching logic so generic phrases like `new line` do not count as concrete evidence.
- Preserve or strengthen retention of high-signal security and configuration findings.
- Add focused regression tests in `tests/review/test_noise_filter.py`.
- Add a changelog note because this changes review-output behavior.

## Out of Scope
- Changing adapter request behavior.
- Changing `OPENAI_COMPAT_DISABLE_THINKING`.
- Changing output-normalizer `<think>` stripping behavior.
- Broad prompt redesign.
- Wrapper-script changes in Jenkins or Bitbucket examples.

## Risks
- If the filter is loosened too much, low-signal findings may reappear.
- If the filter remains too strict, real security findings may still be lost.
- Because review-output behavior changes, release-policy and changelog requirements need to be handled explicitly.

## Verification Plan
- Run `PYTHONPATH=src python -m unittest -v tests/review/test_noise_filter.py`.
- Optionally run `PYTHONPATH=src python -m unittest -v tests/review/test_output_normalizer.py`.
- Replay the provided raw model outputs through the normalize/filter path and confirm that the hardcoded-secret finding is retained.

## Notes
- This slice is driven by an observed false-negative / false-positive mix in real Jenkins + Bitbucket usage.
- Keep the diff narrow and add regression fixtures directly to the noise-filter tests instead of broad refactoring.
