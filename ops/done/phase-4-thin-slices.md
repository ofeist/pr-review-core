# Phase 4 Thin Slices

## Purpose
Break **Phase 4 - Packaging and Distribution Readiness** into small, end-to-end slices that make the core engine installable, versioned, and safely reusable across repositories.

## Status
- Slice 0: done
- Evidence: contract freeze documented in `ops/IMPLEMENTATION-GUARDRAILS.md` and baseline review suite green (`60 tests`).
- Slice 1: done
- Evidence: `pyproject.toml` added, version baseline `0.1.0`, wheel build succeeded, wheel install/import smoke check passed.
- Slice 2: done
- Evidence: package code moved to `src/core`, `pyproject.toml` discovery updated to `where = ["src"]`, review suite passed (`60 tests`), and `make smoke-package` passed.
- Slice 3: done
- Evidence: install matrix documented (`pip install .` and `pip install ".[openai]"`), optional dependency behavior covered by adapter test for missing `openai` package, and review suite remains green.
- Slice 4: done
- Evidence: added `.github/workflows/package-smoke.yml` (PR/tag/manual), validates build/install and fixture-driven CLI smoke output shape, uploads `dist/*` and smoke markdown artifacts, and local smoke/tests passed (`make smoke-package`, review suite `61 tests`).
- Slice 5: done
- Evidence: added `ops/versioning-policy.md` (bump/deprecation rules), `ops/release-checklist.md` (tag/release runbook with dry-run steps), and `CHANGELOG.md` starter with `0.1.0` baseline.
- Slice 6: done
- Evidence: added `ops/consumer-integration.md` with install + quickstart + GitHub/Bitbucket interim usage, updated root `README.md` with consumer quickstart and guide link, and validated raw/parsed CLI commands against fixtures in isolated venv.
- Slice 7: done
- Evidence: added `ops/compatibility-policy.md` with explicit CLI/markdown compatibility expectations and warn->grace->removal deprecation rules, plus regression tests in `tests/review/test_contract_compatibility.py` for required flags and heading order.
- Slice 8: done
- Evidence: added `ops/done/phase-4-exit-validation.md` checklist with installed-package E2E validation results (fake adapter path), recorded OpenAI validation status/constraints, and documented Phase 5 handoff notes.

## Phase 4 Goal (from roadmap)
Make the project reusable as a versioned Python package with a stable CLI/output contract, release checks, and practical integration guidance.

## Working Rules
- Preserve `core/` platform-agnostic boundaries.
- Keep provider-specific orchestration outside package internals.
- Prefer backward-compatible CLI/output changes.
- Keep fake adapter path deterministic for tests and local smoke checks.

## Slice Plan

### Slice 0 - Contract Freeze Baseline
Objective: lock current behavior before packaging changes.

Deliverables:
- Record stable markdown sections and meaning (`Summary`, `Intent`, `Change Summary`, `Findings`).
- Record stable CLI flags currently used in CI.
- Add explicit compatibility note to docs.

Tests:
- Existing full review test suite passes unchanged.

Done when:
- Team agrees what is contract vs internal implementation detail.

### Slice 1 - Python Package Skeleton
Objective: make repository installable as a Python package.

Deliverables:
- Add `pyproject.toml` with package metadata.
- Define package discovery and minimum Python version.
- Add initial version strategy (`0.x`).

Tests:
- Local build success (`python -m build`).
- Install wheel in clean environment.

Done when:
- Package builds and installs without manual patching.

### Slice 2 - `src/` Layout Migration
Objective: move package code to `src/core` to prevent accidental imports from repository root.

Deliverables:
- Move package code from `core/` to `src/core/`.
- Update packaging discovery to `where = ["src"]`.
- Keep CLI/module behavior unchanged for consumers.
- Update tests/tooling paths as needed without changing functional expectations.

Tests:
- Full existing review test suite passes after migration.
- Package build/install smoke still passes from the new layout.
- Import smoke verifies installed package usage (not root-folder leakage).

Done when:
- Repository uses `src/` layout and all previous tests still pass with no behavior regression.

### Slice 3 - Dependency and Extras Model
Objective: separate core install from optional provider/model dependencies.

Deliverables:
- Define base dependencies minimal set.
- Add optional extras (for example `openai`).
- Document install matrix (`pip install ...[openai]`).

Tests:
- Base install works without optional extras.
- OpenAI adapter path works when extras are installed.

Done when:
- Missing optional deps fail with controlled errors and docs match behavior.

### Slice 4 - Release Smoke Workflow
Objective: ensure artifacts are valid before publishing.

Deliverables:
- Add CI workflow for package build + install smoke.
- Add CLI smoke run on fixture diff.
- Add artifact retention for wheel/sdist in CI.

Tests:
- Workflow green on PR and tag contexts.
- Smoke output shape check (`## AI Review` etc.).

Done when:
- Packaging regressions are caught before release.

### Slice 5 - Versioning and Tagging Policy
Objective: make upgrades predictable for downstream repos.

Deliverables:
- Define version bump rules (patch/minor/breaking).
- Add release checklist for tagging and notes.
- Add changelog starter format.

Tests:
- Dry-run release checklist verification (manual).

Done when:
- Team can produce a tagged release with clear upgrade guidance.

### Slice 6 - Consumer Documentation
Objective: document real usage in external repositories.

Deliverables:
- Add quickstart: install + run on diff input.
- Add GitHub integration usage (package install in workflow).
- Add Bitbucket interim usage (script/API wrapper around CLI).

Tests:
- Docs commands validated against fixtures.

Done when:
- New repo can integrate package in under 30 minutes.

### Slice 7 - Compatibility Gates and Deprecation Rules
Objective: prevent accidental breaking changes after first package release.

Deliverables:
- Define CLI compatibility expectations in docs.
- Define markdown contract compatibility expectations.
- Add deprecation policy (warn -> grace period -> removal).

Tests:
- Regression tests for contract-critical output shape and flags.

Done when:
- Future changes have an explicit path that avoids surprise breakage.

### Slice 8 - Phase 4 Exit Validation
Objective: confirm readiness to ship package for broader reuse.

Deliverables:
- Validation checklist document in `ops/`.
- One end-to-end run from installed package in CI-like environment.
- Record known limitations and next-phase handoff notes.

Tests:
- End-to-end package invocation test with fake and openai modes (where available).

Done when:
- Package can be consumed reliably by external repos with documented expectations.

## Phase 4 Acceptance Checklist
- Package builds and installs from source and wheel.
- Console entrypoint works for review generation flow.
- Optional dependency model is documented and tested.
- Release smoke workflow validates package artifact usability.
- Versioning and changelog process is documented.
- Integration docs exist for GitHub and Bitbucket interim usage.
- Compatibility/deprecation policy is explicit.

## Exit Condition
Phase 4 is complete when the project is a versioned, documented, and CI-validated package that external repositories can install and run with stable contracts.

## Suggested Order
1. Slice 0
2. Slice 1
3. Slice 2
4. Slice 3
5. Slice 4
6. Slice 5
7. Slice 6
8. Slice 7
9. Slice 8

## Execution Notes
- Keep the current repo-local workflow path working during packaging rollout.
- Avoid behavior drift while introducing packaging primitives.
- Prefer one commit per slice with test evidence and doc updates.
