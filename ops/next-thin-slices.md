# Next Thin Slices

## Purpose
Maintain a phase-agnostic, execution-first queue of immediate slices.

Use this as the active implementation plan when roadmap phase ordering may change.

## Status
- Slice A1 - OpenAI-Compatible Adapter: queued
- Slice A2 - Adapter Selection and Config Docs: queued
- Slice A3 - Compatibility/Regression Gates for New Adapter: queued
- Slice A4 - GitHub App Skeleton (Phase 5 Slice 1 equivalent): queued

## Slice A1 - OpenAI-Compatible Adapter
Objective: support OpenAI-compatible endpoints (self-hosted and hosted) with one adapter.

Deliverables:
- Add `src/core/review/adapters/openai_compat_adapter.py`.
- Env config contract:
  - `OPENAI_COMPAT_BASE_URL`
  - `OPENAI_COMPAT_MODEL`
  - `OPENAI_COMPAT_API_KEY` (optional depending on endpoint)
  - `OPENAI_COMPAT_TIMEOUT_SECONDS` (optional)
- Register adapter in pipeline as `openai-compat`.

Tests:
- Config validation tests.
- Request/response parsing tests.
- Controlled error-path tests.

Done when:
- `--adapter openai-compat` runs end-to-end with fixture input and deterministic markdown shape.

## Slice A2 - Adapter Selection and Config Docs
Objective: document provider-agnostic usage clearly for consumers.

Deliverables:
- Add adapter matrix to docs (fake/openai/openai-compat).
- Add examples for OpenAI-compatible backends (local/self-hosted/hosted).
- Update package-testing guide with openai-compat smoke command.

Tests:
- Docs command validation against fixture diff where possible.

Done when:
- New consumer can configure and run `openai-compat` without code changes.

## Slice A3 - Compatibility/Regression Gates for New Adapter
Objective: ensure new adapter does not regress core contracts.

Deliverables:
- Extend tests for adapter registry and CLI behavior.
- Validate markdown section contract remains unchanged.
- Add one snapshot/fixture regression for adapter output normalization path.

Tests:
- Full review suite green.
- Package smoke green.

Done when:
- New adapter is covered by regression gates and does not alter stable CLI/markdown contracts.

## Slice A4 - GitHub App Skeleton (Phase 5 Slice 1 Equivalent)
Objective: start backend app path after adapter readiness.

Deliverables:
- Minimal backend skeleton.
- `/webhook/github` with signature verification.
- `/health` endpoint and structured logs.

Tests:
- Signature verification tests.
- Local webhook replay smoke.

Done when:
- Valid webhook requests are accepted; invalid signatures are rejected.

## Mapping Notes
- `ops/ROADMAP.md` remains the strategic phase plan.
- `ops/phase-5-thin-slices.md` remains phase-specific draft/detail.
- This file is the active execution queue and may pull slices from different phases.
