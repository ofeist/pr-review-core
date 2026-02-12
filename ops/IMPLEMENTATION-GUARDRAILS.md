# Implementation Guardrails

## Purpose
This document defines how to implement, extend, and consume the open-source AI PR review project without architectural drift.

## Scope Boundaries
- In scope (open source):
- `core/diff`: diff reading, parsing, filtering, deterministic structures.
- `core/review`: prompt building, adapters, normalization, noise filtering, markdown generation.
- CI adapter flows and reference automation (`adapters/github`, workflow integration).
- Out of scope (should stay external/private by default):
- Secrets and credential material.
- Billing, tenancy, customer-specific policy packs.
- Organization-specific risk/compliance rules that are not generally reusable.

## Integration Modes
### GitHub (Current Stable)
- Preferred path today: GitHub Actions + `core.review.cli`.
- Flow: PR event -> diff extract -> parse/filter -> review generation -> managed comment upsert.
- Configuration:
- Secrets: `OPENAI_API_KEY`.
- Variables: adapter mode/model/timeout/comment-size limits.

### Bitbucket (Interim Until Phase 5)
- Use script/API glue around the same core engine.
- Flow: fetch PR diff via Bitbucket API -> run `core.review.cli` -> publish comment via Bitbucket API.
- Keep Bitbucket-specific auth/event/comment logic outside `core/`.

## Output Contract
Review markdown must preserve section semantics:
- `### Summary`
- Technical run summary (review/chunk/filter outcome).
- `### Intent`
- PR purpose from metadata (title/body), single clean line.
- `### Change Summary`
- Deterministic file-level change bullets.
- `### Findings`
- Actionable issues only; otherwise `- No issues found.`

## Quality Guardrails
- No secrets in git history, files, fixtures, or tests.
- `core/` remains platform-agnostic; no provider-specific API logic in core modules.
- New filtering/tuning logic requires regression tests from real noisy outputs.
- Determinism first:
- stable ordering,
- stable formatting,
- predictable fallback behavior.
- Every behavior change in review output must include snapshot/test updates.

## Change and Delivery Policy
- Work in isolated branches (`bugfix/...`, `feat/...`).
- Keep slices small and end-to-end.
- For each slice, define and verify:
- objective,
- acceptance criteria,
- tests/evidence.
- Avoid open-ended prompt/filter tuning loops:
- set acceptance criteria before tuning,
- stop when criteria are met,
- record residual limitations explicitly.

## Reuse Strategy Across Repositories
- Treat this project as an engine dependency, not copy-paste source.
- Prefer pinned versions/tags when consumed from other repos.
- Upgrade on a planned cadence (for example biweekly/monthly) with changelog review.
- Keep local integration wrappers thin (provider glue only).

## Security and Operations Baseline
- Use CI secret stores only (GitHub/Bitbucket secrets).
- Enforce timeout and controlled fallback comments in automation.
- Preserve managed-comment marker strategy for idempotent upserts.
- Add structured logs for stage outcomes (extract, actionable diff, review, publish).

## Compatibility Promise (Pragmatic)
- Backward compatibility target for markdown shape and CLI flags used in CI.
- If a breaking change is necessary:
- document it in roadmap/ops notes,
- provide migration guidance,
- update fixtures/tests in the same change.
- Deprecation path:
- Additive changes first (new optional flags/metadata).
- Soft migration period with dual support where feasible.
- Removal only after explicit migration note in docs/changelog.

## Versioning Baseline
- Current packaging baseline uses `0.x` series (`0.1.0`).
- During `0.x`, treat markdown/CLI contract changes as compatibility-sensitive and document them explicitly.

## Decision Rule for Future Work
When deciding where new logic belongs:
1. If reusable across platforms, place it in `core/`.
2. If provider-specific, place it in adapter/service layer.
3. If customer/commercial-specific, keep it outside open-source core.
