# Versioning Policy

## Scope
This policy defines how `pr-review-core` versions are bumped and how compatibility is communicated for downstream users.

## Baseline
- Current baseline: `0.1.0`
- During `0.x`, treat CLI flags and markdown section contract as compatibility-sensitive.

## Version Bump Rules
- Patch (`0.x.Y`): bug fixes, internal refactors, docs/test-only changes, or non-breaking behavior clarifications.
- Minor (`0.Y.0`): additive features that preserve existing CLI flags and markdown section semantics.
- Breaking (`X.0.0` once reaching `1.0.0`): removals/renames of contract-sensitive flags or markdown sections, or behavior changes requiring migration.

## What Is Contract-Sensitive
- CLI flags documented in `ops/IMPLEMENTATION-GUARDRAILS.md`.
- Markdown sections and meaning:
  - `### Summary`
  - `### Intent`
  - `### Change Summary`
  - `### Findings`

## Deprecation Policy
- Introduce additive options first.
- Keep dual support for at least one minor release when feasible.
- Add migration note to changelog before removal.

## Release Notes Requirements
Every tagged release should include:
- Version and date.
- User-visible changes.
- Compatibility impact statement (`none` or explicit migration required).
- Upgrade instructions if any behavior changed.

## Consumer Upgrade Cadence
- Recommend planned upgrades (weekly/biweekly/monthly), not ad hoc bumps.
- Pin exact versions in CI and production integrations.
- Before adopting a new version:
  - review `CHANGELOG.md`
  - run package smoke in consumer repo
  - validate adapter/env compatibility in staging
