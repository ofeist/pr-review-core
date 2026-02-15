# Versioning Automation Plan

## Status
Slice 0-5 complete. Slice 6 pending.

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

## How to Set Release Label
Exactly one label is required on each normal PR:
- `release:patch`
- `release:minor`
- `release:major`

### GitHub Web UI
1. Open the PR page.
2. In the right sidebar, click `Labels`.
3. Select exactly one release label.
4. Ensure no second `release:*` label remains.

### GitHub CLI
Set one label:
```bash
gh pr edit <PR_NUMBER> --add-label "release:patch"
```

Replace wrong label(s) with the correct one:
```bash
gh pr edit <PR_NUMBER> --remove-label "release:minor" --remove-label "release:major"
gh pr edit <PR_NUMBER> --add-label "release:patch"
```

Check current labels:
```bash
gh pr view <PR_NUMBER> --json labels --jq '.labels[].name'
```

If labels are missing in the repo, create them once:
```bash
gh label create "release:patch" --color 0e8a16 --description "Non-breaking fixes/docs/refactors"
gh label create "release:minor" --color 1d76db --description "Additive feature changes"
gh label create "release:major" --color b60205 --description "Contract-sensitive or breaking changes"
```

## Open Questions
- Keep manual tag in Phase 0 or move to merge-triggered tag in Slice 3?
- Should `release:major` be blocked during `0.x` unless explicit override label is present?
- Should docs-only PRs default to `release:patch` or use `release:skip` (future)?

## Next Actions
1. Run exit validation and rollout decision (Slice 6).
2. Decide whether to keep manual tagging or move to merge-driven tagging.
3. Decide whether docs-only PRs should use default `release:patch` or future `release:skip`.

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

## Implemented in Slice 3
- Added release asset publishing workflow:
  - `.github/workflows/release-assets.yml`
- Behavior:
  - triggers on `v*` tags and manual dispatch
  - builds wheel/sdist artifacts
  - runs package install + CLI smoke gate
  - creates GitHub Release and uploads `.whl` + `.tar.gz`
- Updated release checklist to require verification of release-assets workflow and attached artifacts.

## Implemented in Slice 4
- Added standalone consistency validation workflow:
  - `.github/workflows/release-consistency.yml`
- Added consistency gate directly in release publishing workflow:
  - `.github/workflows/release-assets.yml`
- Enforced checks:
  - tag version equals `pyproject.toml` version
  - tag version equals `.release-please-manifest.json` version
  - `CHANGELOG.md` contains the release version section

## Implemented in Slice 5
- Updated consumer installation docs to use current pinned version examples (`v0.2.0`).
- Added explicit consumer pinning guidance in `README.md` and `ops/consumer-integration.md`.
- Added wheel asset install example from GitHub Releases.
- Added upgrade cadence guidance in `ops/versioning-policy.md`.
