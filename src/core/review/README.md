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
- `--adapter fake|openai`
- `--max-changes-per-chunk <int>`
- `--fallback-mode on|off`
- `--repository`, `--base-ref`, `--head-ref`

## OpenAI Configuration
Required for `--adapter openai`:
- `OPENAI_API_KEY`

Optional:
- `OPENAI_MODEL` (default: `gpt-4.1-mini`)
- `OPENAI_TIMEOUT_SECONDS` (default: `30`)

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
