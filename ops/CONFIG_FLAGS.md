# Config Flags

Canonical operations-facing index of runtime configuration for `pr-review-core`.

Adapter-local details are also documented in `src/core/review/README.md`.

## Review Behavior

| Variable | Default | Values | Purpose |
| --- | --- | --- | --- |
| `REVIEW_DISABLE_REASONING_PROMPT` | unset/disabled | `1`, `true`, `yes`, `on` | Adds a prompt instruction telling thinking-capable/proxied models to return only review markdown and omit chain-of-thought/reasoning text. Useful when middleware such as AnythingLLM does not forward provider-specific request fields. |

## OpenAI Adapter

Used with `--adapter openai`.

| Variable | Required | Default | Purpose |
| --- | --- | --- | --- |
| `OPENAI_API_KEY` | yes | none | API key for OpenAI. |
| `OPENAI_MODEL` | no | `gpt-4.1-mini` | Model name. |
| `OPENAI_TIMEOUT_SECONDS` | no | `30` | Request timeout in seconds. Must be `> 0`. |
| `OPENAI_MAX_OUTPUT_TOKENS` | no | `1200` | Hard output-token cap. This limits maximum generation length; it does not by itself make the model concise. |

## OpenAI-Compatible Adapter

Used with `--adapter openai-compat`.

| Variable | Required | Default | Purpose |
| --- | --- | --- | --- |
| `OPENAI_COMPAT_BASE_URL` | yes | none | OpenAI-compatible base URL, usually ending in `/v1`. |
| `OPENAI_COMPAT_MODEL` | yes | none | Model name or workspace slug, depending on provider. |
| `OPENAI_COMPAT_API_KEY` | provider-specific | empty | API key for providers that require auth. |
| `OPENAI_COMPAT_TIMEOUT_SECONDS` | no | `30` | Request timeout in seconds. Must be `> 0`. |
| `OPENAI_COMPAT_MAX_OUTPUT_TOKENS` | no | `1200` | Hard output-token cap for Responses API and chat-completions fallback. |
| `OPENAI_COMPAT_ENABLE_OLLAMA_FALLBACK` | no | disabled | Truthy values (`1`, `true`, `yes`, `on`) allow native Ollama `/api/generate` fallback when OpenAI-compatible output is empty. |
| `OPENAI_COMPAT_DISABLE_THINKING` | no | disabled | Truthy values force the chat-completions path and send `extra_body.chat_template_kwargs.enable_thinking=false` for Qwen/vLLM-style endpoints. Also sends `think=false` on opt-in native Ollama fallback. |

Notes:
- `OPENAI_COMPAT_DISABLE_THINKING` is intended for direct vLLM/SGLang/Qwen-compatible servers.
- If a proxy such as AnythingLLM sits between this package and vLLM, provider-specific request fields may be dropped. Use `REVIEW_DISABLE_REASONING_PROMPT=1` as the proxy-safe fallback.

## Ollama Adapter

Used with `--adapter ollama`.

| Variable | Required | Default | Purpose |
| --- | --- | --- | --- |
| `OLLAMA_BASE_URL` | yes | none | Native Ollama base URL, for example `http://localhost:11434`. |
| `OLLAMA_MODEL` | yes | none | Ollama model name. |
| `OLLAMA_TIMEOUT_SECONDS` | no | `30` | Request timeout in seconds. Must be `> 0`. |
| `OLLAMA_THINK` | no | unset | Optional native Ollama `think` control. Accepted values: `true`, `false`, `1`, `0`, `yes`, `no`, `on`, `off`. Use `false` for Qwen PR review automation. |

Notes:
- This slice intentionally supports boolean `OLLAMA_THINK` only.
- Ollama thinking levels such as `low`, `medium`, and `high` are out of scope for now.

## Anything Chat Adapter

Used with `--adapter anything-chat`.

| Variable | Required | Default | Purpose |
| --- | --- | --- | --- |
| `ANYTHING_CHAT_URL` | yes | none | Custom SSE-style Anything chat endpoint URL. |
| `ANYTHING_CHAT_API_KEY` | no | empty | Bearer token for endpoints that require auth. |
| `ANYTHING_CHAT_TIMEOUT_SECONDS` | no | `30` | Request timeout in seconds. Must be `> 0`. |

## Jenkins/Bitbucket Wrapper

Used by `examples/ai-pr-review.sh`.

| Variable | Default | Purpose |
| --- | --- | --- |
| `CHANGE_ID` | none | Bitbucket PR ID from Jenkins. |
| `CHANGE_TARGET` | none | Target branch from Jenkins multibranch PR build. |
| `BB_BASE_URL` / `BITBUCKET_BASE_URL` | none | Bitbucket Data Center base URL. |
| `BB_PROJECT` / `BITBUCKET_PROJECT` | none | Bitbucket project key. |
| `BB_REPO` / `BITBUCKET_REPO` / `GIT_REPO_NAME` | none | Bitbucket repository slug. |
| `BB_TOKEN` / `BITBUCKET_TOKEN` | none | Token for PR metadata/comment API. |
| `ADAPTER_TYPE` | `openai-compat` | Adapter passed to `core.review.cli`. |
| `PYTHON_BIN` | auto-detected | Python executable with `pr-review-core` installed. |
| `OUTPUT_FILE` | `out/pr-review.md` | Review markdown output path. |
| `DIFF_FILE` | `out/pr.diff` | Raw diff output path. |
| `GIT_REMOTE` | `origin` | Git remote used for fetch/diff. |
| `PR_TITLE` | fetched when possible | Explicit PR title for `### Intent`. |
| `PR_BODY` | fetched when possible | Explicit PR description for `### Intent`. |
| `POST_REVIEW_COMMENT` | `0` | Truthy values post `OUTPUT_FILE` back to the Bitbucket PR. |
