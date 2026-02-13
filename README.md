# pr-review-core

Platform-agnostic core for AI-assisted pull request review.

## Vision
This project builds a reusable PR review engine with this strategy:
- Build GitHub-first for fast iteration and adoption.
- Keep core logic platform-agnostic.
- Add Bitbucket integration after GitHub flow is stable.

Roadmap: `ops/ROADMAP.md`

## Current Scope
Implemented in this repository:
- Phase 1: diff parsing foundation (`src/core/diff`)
- Phase 2: review core (`src/core/review`)
- Phase 3 MVP: GitHub Actions PR workflow with comment upsert
- Phase 4: packaging and distribution readiness completed

Out of scope right now:
- GitHub App backend (Phase 5)
- Billing, tenancy, hosted control plane
- Bitbucket adapter (Phase 6)

## Repository Layout
- `src/core/README.md`: architecture boundaries
- `src/core/diff/README.md`: diff parsing module contract
- `src/core/review/README.md`: review module contract and CLI
- `.github/workflows/ai-review.yml`: GitHub PR review workflow
- `.github/workflows/package-smoke.yml`: package build/install/smoke validation workflow
- `adapters/github/README.md`: GitHub adapter runbook
- `adapters/github/scripts/extract_pr_diff.py`: robust PR diff extraction script
- `CHANGELOG.md`: release notes and user-visible changes
- `ops/ROADMAP.md`: project roadmap
- `ops/done/phase-4-thin-slices.md`: Phase 4 execution slices (completed)
- `ops/next-thin-slices.md`: active execution queue (phase-agnostic)
- `ops/phase-5-thin-slices.md`: Phase 5 draft slices
- `ops/versioning-policy.md`: version bump and compatibility policy
- `ops/compatibility-policy.md`: CLI/markdown compatibility and deprecation rules
- `ops/release-checklist.md`: release/tag checklist
- `ops/package-testing.md`: local package build/install validation steps
- `ops/done/phase-4-exit-validation.md`: Phase 4 readiness validation and handoff notes
- `ops/consumer-integration.md`: consumer quickstart for GitHub/Bitbucket integration
- `ops/IMPLEMENTATION-GUARDRAILS.md`: implementation boundaries and contract guardrails
- `ops/done/phase-3-validation-checklist.md`: Phase 3 manual acceptance checklist

## Install Matrix
- Base/core only:
  - `python -m pip install .`
- With OpenAI adapter support:
  - `python -m pip install ".[openai]"`

Notes:
- Base install is sufficient for `--adapter fake`.
- `--adapter openai` requires both `OPENAI_API_KEY` and the `openai` extra.

For package validation steps, see `ops/package-testing.md`.

## Consumer Quickstart
Install in a consumer repository:

```bash
python -m pip install "git+https://github.com/ofeist/pr-review-core.git@v0.1.0"
```

Run on a diff file:

```bash
python -m core.review.cli --input-format raw --from-file path/to/pr.diff --adapter fake
```

For full GitHub and Bitbucket interim integration patterns, see `ops/consumer-integration.md`.

## Local Usage
Raw diff review:

```bash
PYTHONPATH=src git diff origin/main...HEAD | python -m core.review.cli --input-format raw --adapter fake
```

Parsed JSON review:

```bash
PYTHONPATH=src git diff origin/main...HEAD | python -m core.diff.cli | python -m core.review.cli --input-format parsed-json --adapter fake
```

For installed-package workflows (including direct stdin from `git diff`), see `ops/package-testing.md`.

## GitHub Actions Setup (Phase 3 MVP)
Workflow file:
- `.github/workflows/ai-review.yml`

Trigger:
- `pull_request`: `opened`, `synchronize`, `reopened`

Required workflow permissions:
- `contents: read`
- `pull-requests: write`
- `issues: write`

### Configuration
Repository Variables:
- `AI_REVIEW_ADAPTER_MODE`: `fake` (default) or `openai`
- `OPENAI_MODEL` (optional)
- `OPENAI_TIMEOUT_SECONDS` (optional)
- `AI_REVIEW_MAX_COMMENT_CHARS` (optional, default `60000`)

Repository Secrets:
- `OPENAI_API_KEY` (required only for `openai` mode)

### Behavior Summary
- Extracts PR diff via `adapters/github/scripts/extract_pr_diff.py`.
- Runs `core.review.cli` in selected adapter mode.
- Upserts one managed PR comment using marker `<!-- ai-pr-review:managed -->`.
- Handles failure and timeout with controlled fallback markdown.
- Handles empty/ignored-only diffs with "No actionable code changes" output.
- Truncates oversized comment output and points to workflow artifact.

## Troubleshooting
- Missing OpenAI key in `openai` mode:
Workflow posts controlled fallback summary instead of hard failing.

- Duplicate comments:
Ensure marker `<!-- ai-pr-review:managed -->` remains unchanged.

- No actionable changes:
Expected behavior for empty or fully ignored diffs.

- Oversized output:
Workflow truncates comment and keeps full/previewed content in artifact.

## Roadmap Snapshot
- Phase 1: Diff Foundation
- Phase 2: Review Core
- Phase 3: GitHub MVP integration
- Phase 4: Packaging and distribution readiness
- Phase 5: GitHub App and commercial readiness
- Phase 6: Bitbucket adapter parity

See `ops/ROADMAP.md` for full details.
