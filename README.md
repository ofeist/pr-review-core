# pr-review-core

Platform-agnostic core for AI-assisted pull request review.

`pr-review-core` turns git diffs into stable PR-review markdown. It is designed to be embedded in GitHub Actions, Bitbucket/Jenkins pipelines, or custom wrappers without coupling the review engine to one hosting platform.

## Why This Exists

- Keep review logic separate from GitHub/Bitbucket-specific automation.
- Reuse the same review pipeline across repositories and CI systems.
- Support local, hosted, and self-hosted model backends behind a consistent CLI.
- Produce predictable markdown output that is suitable for PR comments and artifacts.

## What It Does

- Reads raw unified diffs or parsed diff JSON.
- Chunks large diffs and falls back safely when full review fails.
- Normalizes output into stable markdown sections.
- Passes PR title/body into prompt context so `### Intent` is meaningful.
- Supports multiple adapters: `fake`, `openai`, `openai-compat`, `ollama`, `anything-chat`.
- Works as a local CLI or as a small building block inside CI wrappers.

## Install

Base install:

```bash
python -m pip install .
```

With OpenAI and OpenAI-compatible adapter support:

```bash
python -m pip install ".[openai]"
```

For release wheels, exact version pinning, and package smoke validation, see `ops/package-testing.md`.

## Quick Start

Local fake-adapter review from git diff:

```bash
git diff origin/main...HEAD | python -m core.review.cli --input-format raw --adapter fake
```

OpenAI-compatible review, for example vLLM/Qwen:

```bash
export OPENAI_COMPAT_BASE_URL="http://localhost:8000/v1"
export OPENAI_COMPAT_MODEL="Qwen/Qwen3.5-Coder"
export OPENAI_COMPAT_DISABLE_THINKING="1"
export REVIEW_DISABLE_REASONING_PROMPT="1"

git diff origin/main...HEAD | python -m core.review.cli --input-format raw --adapter openai-compat
```

Review from a diff file:

```bash
python -m core.review.cli \
  --input-format raw \
  --from-file path/to/pr.diff \
  --adapter fake
```

## Adapters

| Adapter | Purpose |
| --- | --- |
| `fake` | Deterministic local/testing adapter. |
| `openai` | OpenAI API adapter. |
| `openai-compat` | OpenAI-compatible endpoints such as vLLM or gateways. |
| `ollama` | Native Ollama API adapter. |
| `anything-chat` | Custom SSE-style Anything chat endpoint. |

For the full adapter env matrix and CLI details, see `src/core/review/README.md`.
For the operations-facing env/config index, see `ops/CONFIG_FLAGS.md`.

## Integration Examples

- GitHub, Bitbucket, and Jenkins consumer guidance: `ops/consumer-integration.md`
- Jenkins + Bitbucket wrapper example: `examples/ai-pr-review.sh`
- Bitbucket helper for branch/PR flows: `examples/review-bitbucket-pr.sh`

These wrappers keep platform-specific auth, comment posting, and orchestration outside the core package.

## Documentation

- `src/core/review/README.md`: review pipeline, adapters, CLI, env matrix
- `ops/CONFIG_FLAGS.md`: canonical runtime configuration reference
- `ops/consumer-integration.md`: package-mode GitHub/Bitbucket/Jenkins integration
- `ops/package-testing.md`: build/install/smoke validation
- `CHANGELOG.md`: release notes and compatibility-relevant changes

## Project Scope

This repository contains the reusable PR review engine.

It does not aim to be a hosted control plane, billing system, or tenant-management backend. Platform-specific automation belongs in wrappers, workflows, and consumer repositories.

## Development

Run the test suite:

```bash
PYTHONPATH=src pytest -q
```

Run package smoke validation:

```bash
make smoke-package
```

## Contributing

Contributions that improve review quality, adapter support, packaging, and integration ergonomics are welcome. Keep platform-specific orchestration outside the core package unless it is needed to preserve a stable reusable interface.

## License

MIT
