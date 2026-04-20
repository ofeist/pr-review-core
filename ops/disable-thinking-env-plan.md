# Disable Thinking Env Plan

## Goal

Add explicit controls to reduce or disable visible reasoning/thinking output from thinking-capable local models, especially Qwen 3.x/3.5 served through OpenAI-compatible endpoints, Ollama, or proxy layers such as AnythingLLM.

Primary user outcome:
- PR review output should spend tokens on the final review markdown, not long `<think>`/reasoning traces.
- Jenkins/Bitbucket usage should have documented env knobs for Qwen/vLLM/Ollama deployments.

## Problem

Some thinking-capable models generate reasoning before the final answer. This causes practical issues for PR review automation:
- Higher latency.
- Higher output-token usage.
- Final review may be truncated by `OPENAI_COMPAT_MAX_OUTPUT_TOKENS`.
- Review markdown can contain unwanted reasoning traces.

`OPENAI_COMPAT_MAX_OUTPUT_TOKENS` is only a hard output cap. It does not instruct the model to be concise; it cuts off generation when the cap is reached. If thinking consumes the budget, the final answer may be short, empty, or truncated.

## Current State

Current adapter env vars do not include reasoning/thinking controls:
- `OPENAI_COMPAT_*` supports base URL, model, API key, timeout, max output tokens, and Ollama fallback.
- `OLLAMA_*` supports base URL, model, and timeout.
- `anything-chat` supports URL, API key, and timeout.

Current prompt already asks for actionable, high-signal findings, but it does not explicitly instruct the model to suppress chain-of-thought/reasoning.

## Decision

Add three opt-in controls:

```bash
OPENAI_COMPAT_DISABLE_THINKING=1
OLLAMA_THINK=false
REVIEW_DISABLE_REASONING_PROMPT=1
```

### `OPENAI_COMPAT_DISABLE_THINKING`

Purpose:
- Disable Qwen/vLLM-style thinking when using the `openai-compat` adapter directly against vLLM/SGLang/compatible servers.

Behavior:
- Truthy values: `1`, `true`, `yes`, `on`.
- Default: disabled/unset.
- When enabled, chat-completions requests include:

```python
extra_body={
    "chat_template_kwargs": {
        "enable_thinking": False,
    }
}
```

Important compatibility note:
- vLLM documents this control for `/v1/chat/completions`.
- The `openai-compat` adapter currently tries Responses API first and falls back to Chat Completions.
- When `OPENAI_COMPAT_DISABLE_THINKING=1`, prefer/force the chat-completions path so the flag is actually sent to the endpoint where it is expected.

### `OLLAMA_THINK`

Purpose:
- Control native Ollama thinking mode when using the `ollama` adapter.

Behavior:
- Accepted values: `true`, `false`.
- Default: unset, so no `think` field is sent.
- When set, native Ollama payload includes:

```json
"think": false
```

or:

```json
"think": true
```

For PR review, recommended value is:

```bash
OLLAMA_THINK=false
```

### `REVIEW_DISABLE_REASONING_PROMPT`

Purpose:
- Provide a provider-agnostic fallback for middleware/proxy paths that do not forward provider-specific JSON fields, especially AnythingLLM.

Behavior:
- Truthy values: `1`, `true`, `yes`, `on`.
- Default: disabled/unset.
- When enabled, prompt builder adds a concise no-reasoning instruction such as:

```text
Do not include chain-of-thought, hidden reasoning, thinking text, or analysis. Return only the requested review markdown.
```

For Qwen-style models, also consider adding `/no_think` to the same instruction block if tests show it helps and does not harm other providers.

## AnythingLLM Caveat

If the request path is:

```text
pr-review-core openai-compat -> AnythingLLM OpenAI-compatible endpoint -> vLLM
```

then `OPENAI_COMPAT_DISABLE_THINKING=1` may not reach vLLM.

Reason:
- Current AnythingLLM OpenAI-compatible endpoint extracts only a subset of request body fields such as `model`, `messages`, `temperature`, and `stream`.
- Current AnythingLLM Generic OpenAI provider sends downstream chat-completions fields such as `model`, `messages`, `temperature`, and `max_tokens`.
- It does not appear to forward `extra_body`, `chat_template_kwargs`, or `enable_thinking` to the downstream provider.

Therefore:
- For direct vLLM/SGLang: use `OPENAI_COMPAT_DISABLE_THINKING=1`.
- For native Ollama: use `OLLAMA_THINK=false`.
- For AnythingLLM/proxy paths: also use `REVIEW_DISABLE_REASONING_PROMPT=1`.

## Non-Goals

- No native OpenAI `OPENAI_DISABLE_THINKING` in this slice.
- No OpenAI reasoning-model tuning in this slice.
- No CLI flags in this slice.
- No provider auto-detection.
- No dynamic token sizing based on PR size.
- No guarantee that every model/provider will obey no-thinking controls.
- No changes to the stable markdown output contract.

Rationale for no `OPENAI_DISABLE_THINKING`:
- Native OpenAI models do not share Qwen-style `enable_thinking` semantics.
- For OpenAI reasoning models, future controls should use provider-accurate names such as reasoning effort, not a misleading generic disable flag.

## Implementation Scope

### OpenAI-Compatible Adapter

File:
- `src/core/review/adapters/openai_compat_adapter.py`

Changes:
- Read `OPENAI_COMPAT_DISABLE_THINKING` in `from_env()`.
- Store as `disable_thinking: bool` on `OpenAICompatModelAdapter`.
- Add helper for truthy parsing.
- When disabled/unset, preserve current behavior.
- When enabled:
  - route through chat-completions path instead of Responses API
  - include `extra_body={"chat_template_kwargs": {"enable_thinking": False}}`
  - continue sending `max_tokens=self.max_output_tokens`
  - continue honoring timeout and API key behavior

### Ollama Adapter

File:
- `src/core/review/adapters/ollama_adapter.py`

Changes:
- Read `OLLAMA_THINK` in `from_env()`.
- Store as `think: Optional[bool]`.
- Accept only `true`/`false` style values.
- If unset, omit `think` from payload to preserve current behavior.
- If set, include `"think": <bool>` in native `/api/generate` payload.

### OpenAI-Compatible Ollama Fallback

File:
- `src/core/review/adapters/openai_compat_adapter.py`

Changes:
- If `OPENAI_COMPAT_DISABLE_THINKING=1` and the adapter falls back to native Ollama `/api/generate`, include `"think": false` in that fallback payload where supported.
- Keep fallback opt-in behavior unchanged: fallback only runs when `OPENAI_COMPAT_ENABLE_OLLAMA_FALLBACK=1`.

### Prompt Builder

File:
- `src/core/review/prompt_builder.py`

Changes:
- Add optional no-reasoning prompt rule when `REVIEW_DISABLE_REASONING_PROMPT=1`.
- Keep default prompt unchanged unless env is enabled.
- Prefer a concise instruction that does not alter the markdown contract.

Suggested instruction:

```text
Do not include chain-of-thought, hidden reasoning, thinking text, or analysis. Return only the requested review markdown.
```

Optional Qwen-specific addition after testing:

```text
/no_think
```

Only add `/no_think` if it improves Qwen/AnythingLLM behavior without polluting other providers.

## Tests

Update/add tests in:
- `tests/review/test_openai_compat_adapter.py`
- `tests/review/test_ollama_adapter.py`
- `tests/review/test_prompt_builder.py`

Coverage:
- `OPENAI_COMPAT_DISABLE_THINKING` defaults to disabled.
- Truthy `OPENAI_COMPAT_DISABLE_THINKING` is parsed.
- When enabled, `openai-compat` chat-completions request includes:
  - `extra_body.chat_template_kwargs.enable_thinking is False`
  - `max_tokens` still set from `OPENAI_COMPAT_MAX_OUTPUT_TOKENS` / default.
- When disabled, no `extra_body` is sent.
- When enabled, `openai-compat` does not try Responses API first.
- `OLLAMA_THINK=false` sends `"think": false`.
- `OLLAMA_THINK=true` sends `"think": true`.
- Invalid `OLLAMA_THINK` raises adapter config error.
- Unset `OLLAMA_THINK` omits the `think` field.
- `REVIEW_DISABLE_REASONING_PROMPT=1` adds the no-reasoning instruction.
- Unset prompt flag keeps current prompt unchanged.

Validation commands:

```bash
PYTHONPATH=src pytest -q \
  tests/review/test_openai_compat_adapter.py \
  tests/review/test_ollama_adapter.py \
  tests/review/test_prompt_builder.py

PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=src pytest -q
bash -n examples/review-bitbucket-pr.sh examples/ai-pr-review.sh
make smoke-package
```

## Docs and Examples

Update:
- `src/core/review/README.md`
- `README.md` if quick-start env examples need the new knobs
- `ops/package-testing.md`
- `ops/consumer-integration.md`
- `examples/ai-pr-review.sh`
- `examples/review-bitbucket-pr.sh` only if help text should mention the new envs

Document examples:

Direct vLLM/OpenAI-compatible Qwen:

```bash
export OPENAI_COMPAT_BASE_URL="http://vllm-host:8000/v1"
export OPENAI_COMPAT_MODEL="Qwen/Qwen3.5-..."
export OPENAI_COMPAT_DISABLE_THINKING="1"
export OPENAI_COMPAT_MAX_OUTPUT_TOKENS="2000"
```

AnythingLLM proxy path:

```bash
export OPENAI_COMPAT_BASE_URL="http://anythingllm:3001/api/v1/openai"
export OPENAI_COMPAT_MODEL="workspace-slug"
export OPENAI_COMPAT_DISABLE_THINKING="1"      # harmless if AnythingLLM drops it
export REVIEW_DISABLE_REASONING_PROMPT="1"     # fallback that survives proxying
```

Native Ollama:

```bash
export OLLAMA_BASE_URL="http://localhost:11434"
export OLLAMA_MODEL="qwen3.5:32b"
export OLLAMA_THINK="false"
```

Jenkins/Bitbucket wrapper example:

```bash
OPENAI_COMPAT_DISABLE_THINKING="1" \
REVIEW_DISABLE_REASONING_PROMPT="1" \
OPENAI_COMPAT_MAX_OUTPUT_TOKENS="2000" \
PYTHON_BIN=".venv-pr-review/bin/python" \
OUTPUT_FILE="review.md" \
examples/ai-pr-review.sh
```

## Branch and PR

Branch:

```bash
git switch main
git pull --ff-only
git switch -c feat/disable-thinking-env
```

Commit:

```bash
git commit -m "feat(adapter): add reasoning disable controls"
```

PR label:
- `release:minor`

Reason:
- Adds public environment configuration.
- Defaults remain unchanged.
- Backward-compatible behavior.

## Release Flow

Do not manually edit versions for this feature.

After PR merge:
1. Let release-please create/update `chore(release): vX.Y.Z`.
2. Merge the release PR.
3. Pull `main`.
4. Tag exactly the version from the release PR.

Commands:

```bash
git switch main
git pull --ff-only
grep -n '^version = ' pyproject.toml
cat .release-please-manifest.json
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

Verify:
- `Release Consistency` passes.
- `Release Assets` passes.
- GitHub Release contains `.whl` and `.tar.gz`.

## Image/Rebuild Reminder

After release assets exist, update Jenkins/runtime images to install the new pinned wheel:

```bash
https://github.com/ofeist/pr-review-core/releases/download/vX.Y.Z/pr_review_core-X.Y.Z-py3-none-any.whl
```

Then rebuild/deploy the image and set runtime envs as needed:

```bash
OPENAI_COMPAT_DISABLE_THINKING=1
REVIEW_DISABLE_REASONING_PROMPT=1
OPENAI_COMPAT_MAX_OUTPUT_TOKENS=2000
```

## Risk

Low to medium.

Low-risk aspects:
- Defaults unchanged.
- Opt-in only.
- No CLI contract change.
- No markdown contract change.

Medium-risk aspects:
- Provider support varies.
- AnythingLLM may drop provider-specific request fields.
- Qwen 3.5 behavior may vary by serving stack/version/model variant.
- Forcing chat-completions when `OPENAI_COMPAT_DISABLE_THINKING=1` changes the endpoint path for that opt-in mode.

Mitigation:
- Keep all behavior opt-in.
- Document direct-vLLM vs AnythingLLM proxy behavior.
- Add tests that assert payload shape rather than relying on live provider behavior.
- Validate manually with the target Jenkins/Bitbucket/Qwen runtime before release adoption.
