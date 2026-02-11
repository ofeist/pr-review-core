# Phase 2 Thin Slices

## Purpose
Break **Phase 2 - Review Core** into small, end-to-end slices that each deliver measurable value and reduce integration risk.

## Phase 2 Goal (from roadmap)
Convert parsed diff into high-signal AI review text with:
- strict rubric: bugs, security, performance, readability, breaking changes
- noise control
- model adapter abstraction
- chunking and per-file fallback

## Working Rules
- Keep core platform-agnostic.
- Every slice must be runnable locally.
- Favor deterministic behavior before model sophistication.
- Do not include PR platform API work in Phase 2.

## Slice Plan

### Slice 0 - Review I/O Contract
Objective: define stable interfaces before implementation.

Deliverables:
- Add `core/review/types.py` with canonical dataclasses for request, finding, summary, and final output.
- Add `core/review/README.md` with boundaries and data flow.

Done when:
- Types import cleanly from tests and stubs.
- Contract is explicit enough to implement prompt and model layers without guesswork.

Tests:
- Dataclass instantiation smoke test.
- Serialization shape test.

### Slice 1 - Deterministic Prompt Builder (No LLM)
Objective: generate repeatable prompt text from parsed diffs.

Deliverables:
- Add `core/review/prompt_builder.py`.
- Include rubric sections: bugs, security, performance, readability/maintainability, breaking changes.
- Include explicit anti-noise rules in prompt instructions.

Done when:
- Same input yields byte-identical prompt output.
- Prompt always contains all rubric and policy sections.

Tests:
- Snapshot tests for prompt output.
- Fixtures for empty, small, and large parsed diffs.

### Slice 2 - Model Adapter Interface + Fake Adapter
Objective: isolate model calls behind one contract.

Deliverables:
- Add `core/review/model_adapter.py` protocol/interface.
- Add `core/review/adapters/fake.py` with deterministic output.
- Wire adapter selection into local review pipeline path.

Done when:
- End-to-end review runs with fake adapter only.
- No direct model SDK calls exist outside adapter implementations.

Tests:
- Adapter contract tests.
- End-to-end pipeline test using fake adapter.

### Slice 3 - Output Normalizer
Objective: normalize raw model text into reliable markdown.

Deliverables:
- Add `core/review/output_normalizer.py`.
- Enforce sections: summary, findings, explicit "no issues found" path.
- Repair simple markdown defects when possible.

Done when:
- Output always renders as valid markdown with required sections.
- Empty or malformed adapter output falls back to a safe template.

Tests:
- Malformed output normalization tests.
- No-issue output tests.

### Slice 4 - OpenAI Adapter (First Real Model)
Objective: implement first production model adapter.

Deliverables:
- Add `core/review/adapters/openai_adapter.py`.
- Add env-based config: `OPENAI_API_KEY`, model id.
- Map request/response to internal contract.

Done when:
- Local run can call model and return normalized markdown.
- Timeout and API errors return controlled failure results.

Tests:
- Unit tests for request building.
- Mocked response parsing tests.
- Documented manual integration check.

### Slice 5 - Noise Control Post-Filter
Objective: remove low-value findings after model output.

Deliverables:
- Add `core/review/noise_filter.py`.
- Enforce rules: no style-only comments, no obvious restatements, no speculative claims, dedupe near-duplicates.

Done when:
- Noise fixtures are filtered out.
- High-signal findings remain intact.

Tests:
- Rule-level fixture tests.
- Over-filter regression tests.

### Slice 6 - Chunking for Large Diffs
Objective: handle token limits safely.

Deliverables:
- Add `core/review/chunking.py`.
- Chunk strategy: by file first, then by hunk size threshold.
- Merge per-chunk findings into one final review.

Done when:
- Large diff runs without truncation failure.
- Merged output is coherent and non-duplicative.

Tests:
- Chunk boundary tests.
- Merge determinism tests.

### Slice 7 - Per-File Fallback Mode
Objective: recover when full-diff review fails.

Deliverables:
- Add fallback orchestration in review pipeline.
- Flow: try full diff, fallback to per-file on failure/limit, then merge and dedupe.

Done when:
- Simulated full-review failure still returns usable markdown.
- Failure reason is logged without stack-trace leakage in user output.

Tests:
- Forced failure fallback test.
- Output quality regression test.

### Slice 8 - Review CLI Command
Objective: make Phase 2 operable for local and CI execution.

Deliverables:
- Add CLI entrypoint (example: `python -m core.review.cli`).
- Support input from raw diff or parsed diff JSON.
- Run full flow: prompt build, adapter call, normalization, noise filtering.
- Add flags for model, chunk size, and fallback behavior.

Done when:
- One command produces final markdown from real diff input.
- Exit codes are stable for success, recoverable error, and fatal error.

Tests:
- CLI smoke tests.
- Argument validation tests.

### Slice 9 - Hardening and Exit Pack
Objective: close Phase 2 with reproducibility and team usability.

Deliverables:
- Add fixture suite for representative scenarios.
- Finalize `core/review/README.md` usage and boundaries.
- Add troubleshooting notes for timeout/token/empty-output cases.
- Add final acceptance checklist section.

Done when:
- Prompt assembly is deterministic.
- Markdown output is reliable across fixtures.
- Team can run validation locally without tribal knowledge.

Tests:
- Full pipeline fixture regression.
- Markdown snapshot shape tests.

## Phase 2 Acceptance Checklist
- Prompt builder is deterministic.
- Rubric sections are always present.
- Noise-control behavior is enforced.
- Adapter abstraction is in place.
- OpenAI adapter works as first real model implementation.
- Large diffs are processed using chunking.
- Per-file fallback works on full-review failure.
- CLI output is stable markdown.
- Fixture tests cover nominal and failure paths.

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
10. Slice 9

## Execution Notes
- Keep slices small enough for same-day completion when possible.
- Commit after each slice with tests.
- If quality drops after a slice, stop and fix before continuing.
