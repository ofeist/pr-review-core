# Handoff: noise filter high-signal regression builder

## Role
Builder

## Branch
`feature/noise-filter-high-signal-regression`

## Context
Fix the review noise filter so high-signal findings such as hardcoded secrets are not dropped while low-signal findings do not survive due to weak evidence matching like the generic phrase `line `.

## Scope checked
- noise-filter evidence matching
- high-signal finding retention for hardcoded secrets and commented-out config contradictions
- changelog note for review-output behavior fix

## Done
- Removed the overly broad `line ` evidence marker from the noise filter.
- Added more concrete evidence markers for high-signal cases such as `hardcoded`, `commented out`, `committed`, `plaintext`, `directly in the script`, and `credential`.
- Added regression tests that cover:
  - hardcoded secret findings being retained
  - generic `new line` phrasing no longer counting as evidence
  - commented-out `OPENAI_COMPAT_DISABLE_THINKING` logic mismatch being retained
- Added a changelog note under `Unreleased`.

## Not done
- No adapter request changes.
- No output-normalizer behavior changes.
- No Jenkins/Bitbucket wrapper changes.

## Artifacts changed
- `src/core/review/noise_filter.py`
- `tests/review/test_noise_filter.py`
- `CHANGELOG.md`

## Risks
- Additional concrete evidence markers may still be too narrow for some valid findings or too broad for others.
- This is a targeted fix, not a broader redesign of the filtering model.

## Verification
Ran:
- `PYTHONPATH=src python -m unittest -v tests/review/test_noise_filter.py`
- replayed provided real-output samples through normalize/filter path with `PYTHONPATH=src`

Passed:
- `18` noise-filter tests passed
- hardcoded-secret sample now retains the security finding
- `<think>` sample retains both the hardcoded-secret and commented-out flag logic findings

Not run:
- broader review test suite
- reviewer / QA workdir validation

## Operational notes
- This slice changes review-output behavior and should be treated as release-policy relevant.

## Open questions / blockers
- None for this slice.

## Next
- Push the feature branch.
- Review against `origin/feature/noise-filter-high-signal-regression`.
