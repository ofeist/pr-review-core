# Phase 4.2 Exit Validation

## Purpose
Confirm Phase 4.2 local/self-hosted adapter track is completed with documented behavior for `openai-compat` fallback and dedicated `ollama` mode.

## Validation Date
- Date: 2026-02-13

## Checklist
- [x] `openai-compat` fallback behavior is implemented and documented.
- [x] Dedicated `ollama` adapter is available via CLI selection.
- [x] Command outcomes recorded for `fake`, `openai-compat` (with and without fallback), and `ollama`.
- [x] Review regression suite remains green.
- [x] Known limitations and follow-up notes are recorded.

## Fixture Used
- `tests/review/fixtures/raw_small.diff`

## Command Results

### Fake Adapter
Command:
```bash
PYTHONPATH=src python3 -m core.review.cli --input-format raw --from-file tests/review/fixtures/raw_small.diff --adapter fake
```

Observed result:
- Exit code: `0`
- Canonical headings present:
  - `## AI Review`
  - `### Summary`
  - `### Intent`
  - `### Change Summary`
  - `### Findings`

### OpenAI-Compatible (Fallback Disabled)
Command:
```bash
OPENAI_COMPAT_BASE_URL=http://localhost:11434/v1 OPENAI_COMPAT_MODEL=qwen3:32b \
PYTHONPATH=src python3 -m core.review.cli --input-format raw --from-file tests/review/fixtures/raw_small.diff --adapter openai-compat
```

Observed result:
- Exit code: `0`
- Runtime warning in stderr:
  - `Client.__init__() got an unexpected keyword argument 'proxies'`
- Output remained safe fallback markdown:
  - `Review could not be generated from model output.`

### OpenAI-Compatible (Fallback Enabled)
Command:
```bash
OPENAI_COMPAT_BASE_URL=http://localhost:11434/v1 OPENAI_COMPAT_MODEL=qwen3:32b OPENAI_COMPAT_ENABLE_OLLAMA_FALLBACK=1 \
PYTHONPATH=src python3 -m core.review.cli --input-format raw --from-file tests/review/fixtures/raw_small.diff --adapter openai-compat
```

Observed result:
- Exit code: `0`
- Same OpenAI client initialization warning observed in this environment.
- Output remained safe fallback markdown.

Interpretation:
- Fallback is opt-in and wired, but this environment’s OpenAI client compatibility issue occurs before useful model text is returned.

### Ollama Adapter
Command:
```bash
OLLAMA_BASE_URL=http://localhost:11434 OLLAMA_MODEL=qwen3:32b \
PYTHONPATH=src python3 -m core.review.cli --input-format raw --from-file tests/review/fixtures/raw_small.diff --adapter ollama
```

Observed result:
- Exit code: `0`
- Runtime warning in stderr:
  - `Ollama request failed: <urlopen error [Errno 1] Operation not permitted>`
- Output remained safe fallback markdown.

## Regression Suite
Command:
```bash
PYTHONPATH=src python3 -m unittest discover -s tests/review -p 'test_*.py'
```

Observed result:
- `Ran 99 tests ... OK`

## Known Limitations and Quirks
- `openai-compat` behavior depends on local `openai` package/runtime compatibility; this environment reported `proxies` init mismatch.
- Local `ollama` runtime call was blocked in this environment (`Operation not permitted`), so live generation was not validated here.
- Timeout values may need tuning for slow local models:
  - `OPENAI_COMPAT_TIMEOUT_SECONDS`
  - `OLLAMA_TIMEOUT_SECONDS`

## Handoff Notes
- Track is complete from implementation/contract/docs perspective.
- For live model verification, run the same commands in an environment where local network access to Ollama is permitted.
- Next active execution track: `ops/phase-5-thin-slices.md`.
