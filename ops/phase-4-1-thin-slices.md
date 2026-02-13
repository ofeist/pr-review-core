# Phase 4.1 Thin Slices - OpenAI-Compatible Adapter

## Purpose
Break implementation of an OpenAI-compatible model adapter into small, testable slices that enable support for multiple backends (OpenAI-compatible hosted APIs, self-hosted vLLM, local Ollama-compatible gateways) without changing core review contracts.

## Status
- Slice 0: done
- Evidence: adapter/env contract and failure semantics documented (`openai-compat` name, env vars, config/runtime error expectations).
- Slice 1: done
- Evidence: added `src/core/review/adapters/openai_compat_adapter.py` with strict env parsing and timeout validation; added `tests/review/test_openai_compat_adapter.py` config/runtime validation tests.
- Slice 2: done
- Evidence: implemented `generate_review()` request path and response extraction (`output_text` + structured fallback), with request-payload/runtime/empty-response tests in `tests/review/test_openai_compat_adapter.py`.
- Slice 3: done
- Evidence: registered `openai-compat` in `src/core/review/pipeline.py`; added CLI adapter selection regression in `tests/review/test_cli.py`; added adapter-registry presence and unknown-adapter message coverage in `tests/review/test_model_adapter.py`.
- Slice 4: pending
- Slice 5: pending
- Slice 6: pending
- Slice 7: pending

## Phase 4.1 Goal
Add a production-usable `openai-compat` adapter to `core/review` with:
- deterministic behavior
- controlled config/runtime errors
- stable markdown output contract
- docs and smoke coverage suitable for external consumers

## Working Rules
- Keep adapter logic in `src/core/review/adapters/`.
- Do not change existing `fake`/`openai` adapter behavior.
- Preserve CLI and markdown compatibility contracts.
- Keep defaults safe and explicit.
- Prioritize predictable failure messages over silent fallback.

## Slice Plan

### Slice 0 - Contract and Env Spec
Objective: define adapter contract and env surface before coding.

Deliverables:
- Document adapter name: `openai-compat`.
- Define env vars:
  - `OPENAI_COMPAT_BASE_URL` (required)
  - `OPENAI_COMPAT_MODEL` (required)
  - `OPENAI_COMPAT_API_KEY` (optional; required by some providers)
  - `OPENAI_COMPAT_TIMEOUT_SECONDS` (optional, default 30)
- Define expected error classes/messages for config/runtime failures.

Tests:
- Doc-level checklist review.

Done when:
- Team agrees on adapter identity, env contract, and failure semantics.

### Slice 1 - Adapter Skeleton and Config Validation
Objective: add adapter module with strict config parsing.

Deliverables:
- Add `src/core/review/adapters/openai_compat_adapter.py`.
- Implement `from_env()` validation and defaults.
- Validate timeout integer and positive constraints.

Tests:
- Unit tests for missing/invalid env config.

Done when:
- Invalid config fails fast with clear `AdapterConfigError` messages.

### Slice 2 - Request/Response Path
Objective: implement request call and robust text extraction.

Deliverables:
- Implement `generate_review(prompt)` call path.
- Use OpenAI-compatible endpoint/client semantics.
- Extract text from both primary and fallback response fields.

Tests:
- Request payload test (model/input/tokens/timeout).
- Structured-output fallback parsing test.
- Empty-output controlled error test.

Done when:
- Adapter returns non-empty markdown text for valid mocked responses.

### Slice 3 - Registry and CLI Integration
Objective: wire adapter into runtime selection flow.

Deliverables:
- Register adapter in pipeline registry as `openai-compat`.
- Ensure unknown-adapter errors include `openai-compat` when available.
- Keep behavior unchanged for existing adapters.

Tests:
- CLI adapter selection regression test.
- Registry presence test with env configured.

Done when:
- `--adapter openai-compat` is selectable and operational.

### Slice 4 - Error Handling and Diagnostics
Objective: improve operability under provider/network failures.

Deliverables:
- Wrap provider errors as `AdapterRuntimeError` with concise message.
- Keep sensitive values (keys/tokens) out of errors/logs.
- Ensure timeout/config errors stay distinguishable.

Tests:
- Runtime exception wrapping tests.
- Secret-leak regression assertion in error strings.

Done when:
- Failures are actionable and non-leaky.

### Slice 5 - Docs and Consumer Usage
Objective: make setup and usage straightforward for consumers.

Deliverables:
- Update install/config docs with `openai-compat` examples.
- Add provider examples (hosted OpenAI-compatible, self-hosted vLLM, local gateway).
- Add package-testing command examples for `openai-compat`.

Tests:
- Docs command sanity run where feasible.

Done when:
- Consumer can configure adapter without code changes.

### Slice 6 - Regression and Contract Gates
Objective: ensure no regression to stable contracts.

Deliverables:
- Add tests confirming markdown section shape unchanged.
- Add CLI flag compatibility checks unchanged.
- Add adapter-specific fixture path tests.

Tests:
- Full review suite green.
- Package smoke green.

Done when:
- New adapter passes tests without contract drift.

### Slice 7 - Exit Validation and Handoff
Objective: close adapter work with explicit validation record.

Deliverables:
- Add validation note in `ops/` with:
  - fake/openai/openai-compat command results
  - known limitations/provider quirks
  - follow-up notes if provider-specific adapters are needed
- Update active execution queue status.

Tests:
- End-to-end command validation on fixture input.

Done when:
- Adapter is documented, test-covered, and ready for normal use.

## Acceptance Checklist
- `openai-compat` adapter can be selected via CLI.
- Env configuration is explicit and validated.
- Runtime errors are controlled and non-leaky.
- Existing adapters remain unchanged.
- Markdown/CLI contracts remain stable.
- Docs include clear setup and usage examples.
- Validation evidence is recorded.

## Exit Condition
This track is complete when `openai-compat` works end-to-end from CLI with stable output, comprehensive tests, and clear operational docs.

## Suggested Order
1. Slice 0
2. Slice 1
3. Slice 2
4. Slice 3
5. Slice 4
6. Slice 5
7. Slice 6
8. Slice 7

## Execution Notes
- Start with mocked tests before real provider integration checks.
- Keep provider assumptions minimal and configurable.
- Prefer additive changes to avoid compatibility churn.
