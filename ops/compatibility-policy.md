# Compatibility Policy

## Purpose
Define compatibility expectations for consumers of `pr-review-core` and provide a predictable deprecation path.

## Contract Surfaces
The following are compatibility-sensitive:

- CLI flags for `python -m core.review.cli` used in automation.
- Markdown section headings and ordering in final review output.

## CLI Compatibility Expectations
The following flags are contract-critical and should not be removed/renamed without deprecation:

- `--input-format`
- `--from-file`
- `--adapter`
- `--repository`
- `--base-ref`
- `--head-ref`
- `--pr-title`
- `--pr-body`
- `--max-changes-per-chunk`
- `--fallback-mode`

Defaults may evolve, but semantic intent of these flags should remain stable.

## Markdown Compatibility Expectations
Expected stable section structure:

1. `## AI Review`
2. `### Summary`
3. `### Intent`
4. `### Change Summary`
5. `### Findings`

Notes:
- Wording inside sections may improve over time.
- Section names/order are treated as contract to avoid downstream parser breakage.
- Empty actionable findings state remains: `- No issues found.`

## Deprecation Policy
For compatibility-sensitive changes, follow this sequence:

1. Warn:
- Add release notes/changelog entry that deprecation starts.
- Keep old behavior/flag working.

2. Grace period:
- Keep dual support for at least one minor release when feasible.
- Provide explicit migration example.

3. Removal:
- Remove only after prior warning + grace period.
- Document breaking change and migration in changelog/release notes.

## Regression Gates
Every PR that touches contract-sensitive logic should include:

- CLI regression tests for required flags.
- Markdown contract regression tests for section presence/order.
- Updated changelog/ops docs for any compatibility-impacting change.
