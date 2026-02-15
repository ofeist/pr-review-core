# Versioning Automation Plan

## Status
Placeholder (to be filled during Slice 0-2).

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

## Proposed Tooling
- Release PR automation: TBD
- Policy checks: GitHub Actions
- Artifact publishing: GitHub Releases (`.whl` + `.tar.gz`)

## Required Inputs
- `pyproject.toml` version source of truth
- `CHANGELOG.md` release notes
- Release labels and PR conventions

## Open Questions
- Which automation engine (`release-please` vs `python-semantic-release`)?
- Label scheme final form?
- One-step tag from release PR or separate manual tag step?

## Next Actions
1. Execute Slice 0 in `ops/versioning-automation-thin-slices.md`.
2. Choose tooling and lock policy.
3. Implement Slice 1 workflow skeleton.
