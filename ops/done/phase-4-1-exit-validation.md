# Phase 4.1 Exit Validation

## Purpose
Confirm Phase 4.1 (`openai-compat` adapter) is integrated, documented, and ready for handoff.

## Validation Date
- Date: 2026-02-13

## Checklist
- [x] `openai-compat` adapter is selectable via CLI/runtime.
- [x] Regression and contract gates are green.
- [x] Package smoke is green for install/build path.
- [x] Adapter docs and consumer examples are present.
- [x] Known limitations and follow-up notes are recorded.

## Command Results
Fixture used:
- `tests/review/fixtures/raw_small.diff`

### Fake Adapter
Command:
```bash
PYTHONPATH=src python3 -m core.review.cli --input-format raw --from-file tests/review/fixtures/raw_small.diff --adapter fake
```

Observed result:
- Exit code: `0`
- Verified headings:
  - `## AI Review`
  - `### Summary`
  - `### Intent`
  - `### Change Summary`
  - `### Findings`

### OpenAI Adapter
Command:
```bash
PYTHONPATH=src python3 -m core.review.cli --input-format raw --from-file tests/review/fixtures/raw_small.diff --adapter openai
```

Observed result:
- Exit code: `1` (recoverable)
- Error:
  - `Unknown adapter 'openai'. Known adapters: fake`

Interpretation:
- Expected when OpenAI env config is absent in this environment.

### OpenAI-Compatible Adapter
Command:
```bash
OPENAI_COMPAT_BASE_URL=http://localhost:11434/v1 OPENAI_COMPAT_MODEL=qwen2.5-coder \
PYTHONPATH=src python3 -m core.review.cli --input-format raw --from-file tests/review/fixtures/raw_small.diff --adapter openai-compat
```

Observed result:
- Exit code: `0`
- Runtime warning observed:
  - `Client.__init__() got an unexpected keyword argument 'proxies'`
- Output fell back to controlled safe markdown:
  - `Review could not be generated from model output.`

Interpretation:
- CLI contract remains stable (safe output), but provider/client version compatibility must be aligned for live inference.

## Known Limitations and Provider Quirks
- `openai` adapter remains config-gated by environment; without valid config it is not registered.
- `openai-compat` runtime depends on OpenAI client/provider compatibility.
- In this environment, the client stack produced `proxies` init mismatch, causing safe fallback output instead of model text.
- Local endpoints may require `OPENAI_COMPAT_API_KEY`, even if optional by contract.

## Follow-up Notes
- Validate one live `openai-compat` run in CI or a controlled env with:
  - provider endpoint available
  - verified compatible `openai` package/client stack
  - optional key configured where required
- If provider-specific incompatibilities persist, add provider notes under `ops/consumer-integration.md`.
