# Versioning Automation Thin Slices

## Purpose
Define an execution-first plan for robust, human-assisted release/version automation in `pr-review-core`.

## Why This Track Exists
- Manual version bumps are easy to miss under delivery pressure.
- Contract-sensitive changes (CLI flags/markdown format) require explicit guardrails.
- We want automation that reduces human error without losing release control.

## Status
- Slice 0: done
- Slice 1: done
- Slice 2: done
- Slice 3: done
- Slice 4: done
- Slice 5: done
- Slice 6: done

Evidence:
- `ops/versioning-automation.md` now contains locked Phase 0 decisions:
  - required release intent labels
  - contract-sensitive change policy
  - human approval gates for release PR and tag/release
  - selected tooling baseline (`release-please`)
- Release PR skeleton implemented:
  - `.github/workflows/release-please.yml`
  - `release-please-config.json`
  - `.release-please-manifest.json`
- Label and policy enforcement implemented:
  - `.github/workflows/release-policy.yml`
  - requires exactly one release label (`release:patch|release:minor|release:major`) on PRs
  - enforces `release:major` for contract-sensitive file changes
  - requires changelog migration note for contract-sensitive changes
- Tag and release asset publishing implemented:
  - `.github/workflows/release-assets.yml`
  - builds wheel/sdist on `v*` tags
  - runs package-install + CLI smoke gate before release publishing
  - creates GitHub Release and uploads `.whl` + `.tar.gz`
- Version consistency guards implemented:
  - `.github/workflows/release-consistency.yml`
  - validates tag version matches `pyproject.toml`
  - validates tag version matches `.release-please-manifest.json`
  - validates `CHANGELOG.md` contains the tagged version section
  - release-assets workflow now includes the same consistency gate before build/publish steps
- Consumer pinning and upgrade guidance implemented:
  - `README.md` install examples updated to `v0.2.0` and explicit pinning notes
  - `ops/consumer-integration.md` updated with exact pin strategy and wheel-asset install example
  - `ops/versioning-policy.md` updated with recommended consumer upgrade cadence
- Exit validation and rollout decision documented:
  - `ops/done/versioning-automation-exit-validation.md`
  - decision recorded: GO with human-in-loop final release approval

## Operating Model
- Start with human-in-loop approvals.
- Automate release mechanics (bump/changelog/tag/release assets).
- Enforce policy via CI checks.
- Move to higher automation only after 1-2 stable release cycles.

## Slice Plan

### Slice 0 - Policy Baseline and Human-in-Loop Gate
Objective: lock explicit release intent and approval flow before automation.

Deliverables:
- Confirm release intent labels (`release:patch|minor|major`).
- Define approval gate for release PR merge.
- Document Phase 0 rollout in `ops/versioning-automation.md`.

Tests:
- Manual checklist review.

Done when:
- Team can explain who decides bump and where that decision is recorded.

### Slice 1 - Release Automation Skeleton
Objective: add workflow that creates/updates a release PR from `main`.

Deliverables:
- CI workflow for automated release PR generation.
- PR title/body template with version and changelog summary.

Tests:
- Dry-run on test branch.

Done when:
- Merged changes trigger deterministic release PR updates.

### Slice 2 - Label/Policy Enforcement
Objective: fail fast when release intent is missing or inconsistent.

Deliverables:
- CI check requiring one release label on feature PRs.
- Rule for contract-sensitive changes requiring migration/changelog note.

Tests:
- Negative tests (missing label, wrong label).

Done when:
- Non-compliant PRs are blocked before merge.

### Slice 3 - Tag + GitHub Release Asset Publishing
Objective: publish immutable versioned artifacts from tags.

Deliverables:
- Workflow to build wheel/sdist on `v*` tags.
- Create GitHub Release and attach `dist/*` assets.
- Keep package smoke gate in release flow.

Tests:
- Tag dry-run on test repo/tag namespace.

Done when:
- `vX.Y.Z` tag produces GitHub Release with wheel and sdist assets.

### Slice 4 - Version Consistency Guards
Objective: ensure version metadata/tag/changelog stay aligned.

Deliverables:
- CI check: tag version matches `pyproject.toml`.
- CI check: changelog contains tagged version section.

Tests:
- Mismatch scenario tests.

Done when:
- Inconsistent release metadata fails deterministically.

### Slice 5 - Consumer Pinning and Upgrade Guidance
Objective: reduce downstream breakage through explicit pinning and upgrade notes.

Deliverables:
- Update docs with strict pin examples (`==` and release-tag installs).
- Add upgrade cadence guidance to release docs.

Tests:
- Doc command validation against a clean environment.

Done when:
- Consumer docs provide one clear and repeatable install/upgrade path.

### Slice 6 - Exit Validation and Rollout Decision
Objective: validate that automation is reliable enough to become default.

Deliverables:
- Exit checklist with evidence from at least one real automated release.
- Decision note: keep human-in-loop only, or increase automation level.

Tests:
- One end-to-end live release rehearsal.

Done when:
- Team can ship tagged releases with minimal manual steps and clear rollback path.

## Acceptance Checklist
- Release intent is explicit per PR.
- Release PR is generated automatically and reviewed by human.
- Tagged releases publish wheel/sdist assets.
- Version/changelog/tag consistency is enforced.
- Consumer install path is documented and reproducible.

## Exit Condition
This track is complete when release/versioning is automation-first, policy-enforced, and still human-approved at the final merge/tag decision.
