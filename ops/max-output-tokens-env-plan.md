# Max Output Tokens Env Plan

## Goal
Make model output length configurable through environment variables while preserving current defaults and CLI behavior.

## Problem
Current adapters hardcode `max_output_tokens = 1200` in code:
- `openai`
- `openai-compat`

This is not documented as a configurable setting and is not read from environment variables. For OpenAI-compatible chat-completions fallback, no output-token cap is currently sent.

## Non-Goals
- No CLI flag in this slice.
- No dynamic token sizing based on PR size.
- No prompt/output policy redesign.
- No provider-specific tuning beyond existing adapter boundaries.

## Decision
Add optional env vars:
- `OPENAI_MAX_OUTPUT_TOKENS`
- `OPENAI_COMPAT_MAX_OUTPUT_TOKENS`

Defaults remain unchanged:
- `1200`

Validation:
- Must parse as integer.
- Must be `> 0`.
- Invalid values raise adapter config errors, matching current timeout-env behavior.

## Implementation Scope

### OpenAI Adapter
File:
- `src/core/review/adapters/openai_adapter.py`

Changes:
- Read `OPENAI_MAX_OUTPUT_TOKENS` in `from_env()`.
- Default to `1200` when unset.
- Pass into `OpenAIModelAdapter(max_output_tokens=...)`.
- Keep existing Responses API call using `max_output_tokens=self.max_output_tokens`.

### OpenAI-Compatible Adapter
File:
- `src/core/review/adapters/openai_compat_adapter.py`

Changes:
- Read `OPENAI_COMPAT_MAX_OUTPUT_TOKENS` in `from_env()`.
- Default to `1200` when unset.
- Pass into `OpenAICompatModelAdapter(max_output_tokens=...)`.
- Responses API path continues using `max_output_tokens=self.max_output_tokens`.
- Chat-completions fallback adds `max_tokens=self.max_output_tokens`.

## Tests
Update/add tests in:
- `tests/review/test_openai_adapter.py`
- `tests/review/test_openai_compat_adapter.py`

Coverage:
- Default stays `1200`.
- Valid env override is applied.
- Non-integer env raises config error.
- Zero/negative env raises config error.
- `openai-compat` chat-completions fallback passes `max_tokens`.

Validation commands:
```bash
PYTHONPATH=src pytest -q tests/review/test_openai_adapter.py tests/review/test_openai_compat_adapter.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=src pytest -q
```

## Docs
Update:
- `src/core/review/README.md`
- `ops/consumer-integration.md`
- `ops/package-testing.md` if package testing examples need tuning notes

Document examples:
```bash
export OPENAI_MAX_OUTPUT_TOKENS=2000
export OPENAI_COMPAT_MAX_OUTPUT_TOKENS=2000
```

For Jenkins/vLLM usage, prefer:
```bash
export OPENAI_COMPAT_MAX_OUTPUT_TOKENS=2000
```

## Branch and PR
Branch:
```bash
git switch main
git pull
git switch -c feat/max-output-token-env
```

Commit:
```bash
git commit -m "feat(adapter): add env-configurable max output tokens"
```

PR label:
- `release:minor`

Reason:
- Adds public environment configuration.
- No breaking behavior; default remains unchanged.

## Release Flow
Do not manually edit versions for this feature.

After PR merge:
1. Let `release-please` create/update the release PR.
2. Merge the release PR.
3. Pull `main`.
4. Tag exactly the version from `pyproject.toml` / release PR.

Commands:
```bash
git switch main
git pull
grep -n '^version = ' pyproject.toml
cat .release-please-manifest.json
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

Verify:
- `Release Consistency` passes.
- `Release Assets` passes.
- GitHub Release contains `.whl` and `.tar.gz`.

## Image Rebuild Reminder
After release assets exist, update Jenkins/runtime images to install the new pinned wheel:

```bash
https://github.com/ofeist/pr-review-core/releases/download/vX.Y.Z/pr_review_core-X.Y.Z-py3-none-any.whl
```

Then rebuild and deploy the image. Configure Jenkins/runtime env as needed:

```bash
OPENAI_COMPAT_MAX_OUTPUT_TOKENS=2000
```

## Risk
Low.

Reasons:
- Defaults unchanged.
- Existing env vars unchanged.
- No CLI contract change.
- Validation mirrors existing timeout parsing.

Main compatibility note:
- `openai-compat` chat-completions path will start sending `max_tokens`. This is expected by vLLM and most OpenAI-compatible chat-completions providers.
