# Phase 4.2 Thin Slices - OpenAI-Compat Fallback and Ollama Adapter

## Purpose
Unblock local/self-hosted usage where `/v1/responses` is reachable but returns empty text, while preserving a clean path to a dedicated Ollama adapter.

## Status
- Slice 0: done
- Evidence: guardrails added in `ops/IMPLEMENTATION-GUARDRAILS.md` to lock Phase 4.2 contract decisions: opt-in-only fallback flag (`OPENAI_COMPAT_ENABLE_OLLAMA_FALLBACK=1`), explicit fallback trigger scope, dedicated `ollama` adapter boundary, and no-break requirement for existing adapters.
- Slice 1: pending
- Slice 2: pending
- Slice 3: pending
- Slice 4: pending
- Slice 5: pending
- Slice 6: pending

## Phase 4.2 Goal
Deliver reliable local model execution with:
- no regressions to existing `fake`/`openai`/`openai-compat` behavior by default
- opt-in compatibility fallback for current users
- explicit dedicated `ollama` adapter path for long-term maintainability

## Working Rules
- Keep existing adapter contracts stable.
- Do not silently change `openai-compat` default behavior.
- Gate fallback behavior behind explicit env config.
- Preserve markdown/CLI contracts and recoverable failure behavior.
- Add docs and tests in each functional slice.

## Slice Plan

### Slice 0 - Contract Decision and Guardrails
Objective: define exact behavior boundaries before coding.

Deliverables:
- Confirm fallback is opt-in only (for example `OPENAI_COMPAT_ENABLE_OLLAMA_FALLBACK=1`).
- Confirm fallback trigger condition (`responses` call succeeds but extracted text is empty, or controlled runtime path).
- Confirm dedicated adapter name: `ollama`.
- Document no-break rule for existing adapters.

Tests:
- Doc-level contract checklist.

Done when:
- Fallback semantics and adapter boundaries are explicit and agreed.

### Slice 1 - Opt-In Fallback Path in OpenAI-Compat
Objective: unblock current environments quickly.

Deliverables:
- Add optional fallback path in `openai-compat` adapter:
  - first try `responses` route
  - if opt-in enabled and response is empty, call Ollama native generate endpoint
- Keep normal `openai-compat` behavior unchanged when fallback env is off.

Tests:
- Unit test for fallback-disabled unchanged behavior.
- Unit test for fallback-enabled success path.

Done when:
- Existing configs stay stable and opt-in path can produce non-empty text.

### Slice 2 - Error Handling, Timeout, and Secret Safety for Fallback
Objective: ensure fallback path is production-safe.

Deliverables:
- Add controlled timeout for fallback HTTP path.
- Wrap fallback runtime failures with concise `AdapterRuntimeError`.
- Keep secret redaction behavior for all wrapped errors.

Tests:
- Timeout and network-failure tests for fallback path.
- Secret-leak regression test for fallback errors.

Done when:
- Fallback failure mode is actionable and non-leaky.

### Slice 3 - Dedicated Ollama Adapter Skeleton
Objective: create clean long-term adapter boundary.

Deliverables:
- Add `src/core/review/adapters/ollama_adapter.py`.
- Add env contract:
  - `OLLAMA_BASE_URL` (required)
  - `OLLAMA_MODEL` (required)
  - `OLLAMA_TIMEOUT_SECONDS` (optional, default 30)
- Implement strict env validation.

Tests:
- Config validation tests for missing/invalid env.

Done when:
- `ollama` adapter can be instantiated from env with controlled config errors.

### Slice 4 - Registry/CLI Integration for Ollama
Objective: make dedicated adapter selectable.

Deliverables:
- Register `ollama` in pipeline registry.
- Ensure unknown-adapter error lists `ollama` when configured.
- Keep current adapters unaffected.

Tests:
- CLI adapter selection regression for `--adapter ollama`.
- Registry presence test with env configured.

Done when:
- `--adapter ollama` is selectable via CLI.

### Slice 5 - Docs and Consumer Usage
Objective: make usage clear and avoid confusion between adapter modes.

Deliverables:
- Document selection guidance:
  - `openai-compat` for OpenAI-compatible endpoints
  - `ollama` for native `/api/generate`
- Add working examples for both paths.
- Document fallback env flag and expected behavior.

Tests:
- Doc command sanity checks (where feasible).

Done when:
- User can pick correct adapter mode without trial-and-error.

### Slice 6 - Exit Validation and Queue Handoff
Objective: close track with evidence and next-step clarity.

Deliverables:
- Add `ops/phase-4-2-exit-validation.md` with command outcomes:
  - `fake`
  - `openai-compat` (with and without fallback flag)
  - `ollama`
- Record known provider quirks and residual limitations.
- Update active queue and done docs.

Tests:
- End-to-end fixture command validation.

Done when:
- Local/self-hosted model flows are validated and documented.

## Acceptance Checklist
- Opt-in fallback works and is non-default.
- Existing adapter behavior remains stable.
- Dedicated `ollama` adapter is selectable and tested.
- Error handling stays controlled and non-leaky.
- Docs clearly distinguish adapter modes.
- Exit validation evidence is recorded.

## Exit Condition
This track is complete when local/self-hosted usage is reliable via either:
- `openai-compat` with explicit fallback enabled, or
- dedicated `ollama` adapter,
with stable contracts and clear documentation.
