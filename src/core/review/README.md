# core/review Module

Review-layer core logic for converting parsed diffs into stable markdown reviews.

## Purpose
Transform structured diff data into high-signal review output with:
- deterministic prompt construction
- adapter-based model calls
- output normalization
- noise filtering
- chunking and fallback orchestration

## Scope Boundaries
Input:
- structured diff data (`DiffFile[]`) from `core/diff`

Output:
- canonical markdown suitable for PR comments

Out of scope:
- raw unified diff parsing (handled by `core/diff`)
- GitHub/Bitbucket webhook handlers and comment publishing

## Key Components
- `types.py`: review contracts (request/finding/summary/result)
- `prompt_builder.py`: deterministic review prompt generation
- `model_adapter.py`: adapter protocol
- `adapters/fake.py`: deterministic local adapter
- `adapters/openai_adapter.py`: OpenAI adapter with env config
- `output_normalizer.py`: canonical markdown shape enforcement
- `noise_filter.py`: post-filter for low-signal findings
- `chunking.py`: large-diff chunking and chunk-output merge
- `pipeline.py`: full-first review flow + per-file fallback
- `cli.py`: local/CI entrypoint

## Install Matrix
- Base/core only:
  - `python -m pip install .`
- With OpenAI and OpenAI-compatible adapter support:
  - `python -m pip install ".[openai]"`

Notes:
- Base install supports `--adapter fake`.
- Base install supports `--adapter ollama`.
- `--adapter openai` requires `OPENAI_API_KEY` and installed OpenAI extra.
- `--adapter openai-compat` requires `OPENAI_COMPAT_BASE_URL`, `OPENAI_COMPAT_MODEL`, and installed OpenAI extra.
- `OPENAI_COMPAT_API_KEY` is optional and provider-specific.

## Adapter Env Matrix (Canonical)

Use this section as the source of truth for adapter environment variables.

| Adapter | Required | Optional |
| --- | --- | --- |
| `fake` | none | none |
| `openai` | `OPENAI_API_KEY` | `OPENAI_MODEL` (default `gpt-4.1-mini`), `OPENAI_TIMEOUT_SECONDS` (default `30`) |
| `openai-compat` | `OPENAI_COMPAT_BASE_URL`, `OPENAI_COMPAT_MODEL` | `OPENAI_COMPAT_API_KEY`, `OPENAI_COMPAT_TIMEOUT_SECONDS` (default `30`), `OPENAI_COMPAT_ENABLE_OLLAMA_FALLBACK` (`1\|true\|yes\|on`) |
| `ollama` | `OLLAMA_BASE_URL`, `OLLAMA_MODEL` | `OLLAMA_TIMEOUT_SECONDS` (default `30`) |

## CLI Usage
Raw diff input:

```bash
PYTHONPATH=src git diff origin/main...HEAD | python -m core.review.cli --input-format raw --adapter fake
```

Parsed JSON input:

```bash
PYTHONPATH=src git diff origin/main...HEAD | python -m core.diff.cli | python -m core.review.cli --input-format parsed-json --adapter fake
```

From file:

```bash
PYTHONPATH=src python -m core.review.cli --input-format raw --from-file path/to/diff.txt --adapter fake
```

Useful flags:
- `--adapter fake|openai|openai-compat|ollama`
- `--max-changes-per-chunk <int>`
- `--fallback-mode on|off`
- `--repository`, `--base-ref`, `--head-ref`

Provider notes:
- OpenAI-compatible providers should use `.../v1` base URL.
- Enable `OPENAI_COMPAT_ENABLE_OLLAMA_FALLBACK` when `responses` output is empty and you want native Ollama fallback.
- Use `ollama` adapter for direct `/api/generate` behavior.

## Exit Codes
- `0`: success
- `1`: recoverable error (invalid input/review generation failure)
- `2`: fatal/argument validation error

## Troubleshooting
- `No diff input provided...`
Use stdin pipe or `--from-file`.

- `Invalid parsed JSON input...`
Ensure parsed mode receives JSON list in the `core.diff.cli` output shape.

- `Unknown adapter ...`
Use `--adapter fake` for local tests, or configure OpenAI env vars.

- Empty/noisy model output
Pipeline normalizes output and preserves safe fallback with explicit `No issues found.`

- Full review fails
With `--fallback-mode on` (default), pipeline retries in per-file mode and merges results.
