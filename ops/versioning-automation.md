# Versioning Automation Plan

## Status
Slice 0-2 complete. Slice 3 pending.

## Goal
Implement robust release/version automation with human-in-loop approvals and policy checks.

## Scope
- Automated release PR flow
- Automated tag/release asset publishing
- CI policy checks for version/changelog consistency

## Non-Goals (Initial)
- Fully autonomous no-approval releases
- Multi-registry publishing expansion

## Human-in-Loop Phase 0
Decision points:
- Bump type approval (`patch|minor|major`)
- Release PR merge approval
- Final tag/release approval

Phase 0 decisions (locked):
- Exactly one release intent label is required on every merged PR:
  - `release:patch`
  - `release:minor`
  - `release:major`
- Contract-sensitive changes (CLI flags/markdown contract/deprecation removals) must use `release:major` and include migration notes in `CHANGELOG.md`.
- Release automation creates/updates release PR, but does not auto-merge it.
- Human approver merges release PR after checklist verification.
- Tag/release remains human-approved in Phase 0.

Approval gate:
- At least one maintainer approval required on release PR.
- `ops/release-checklist.md` must be completed before merge/tag.
- Package smoke workflow must be green on release PR.

## Proposed Tooling
- Release PR automation: `release-please` (GitHub Action, Release PR mode)
- Policy checks: GitHub Actions
- Artifact publishing: GitHub Releases (`.whl` + `.tar.gz`)

## Required Inputs
- `pyproject.toml` version source of truth
- `CHANGELOG.md` release notes
- Release labels and PR conventions

## Open Questions
- Keep manual tag in Phase 0 or move to merge-triggered tag in Slice 3?
- Should `release:major` be blocked during `0.x` unless explicit override label is present?
- Should docs-only PRs default to `release:patch` or use `release:skip` (future)?

## Next Actions
1. Prepare Slice 3 tag/release asset publishing workflow.
2. Add version/tag/changelog consistency guards (Slice 4).
3. Update consumer pinning/upgrade docs (Slice 5).

## Implemented in Slice 1
- Added release PR workflow:
  - `.github/workflows/release-please.yml`
- Added release-please configuration:
  - `release-please-config.json`
  - `.release-please-manifest.json`
- Current mode is PR automation only (`skip-github-release: true`) to preserve human-approved tag/release flow in Phase 0.

## Implemented in Slice 2
- Added PR policy workflow:
  - `.github/workflows/release-policy.yml`
- Enforced exactly one release intent label on PRs:
  - `release:patch`
  - `release:minor`
  - `release:major`
- Enforced contract-sensitive policy:
  - contract-sensitive files require `release:major`
  - contract-sensitive files require `CHANGELOG.md` update
  - changelog diff must include a migration note
- Added explicit skip path for release automation PRs to avoid blocking release-please maintenance PR flow.
