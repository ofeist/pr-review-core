# Project Roadmap

## Vision
Build a platform-agnostic AI PR review engine that starts GitHub-first for fastest adoption, then adds Bitbucket integration for enterprise differentiation.

## Current State (as found in this repo)
- Core diff module exists in `core/diff`:
- `types.py` defines canonical dataclasses (`DiffFile`, `DiffHunk`, `Change`, `ChangeType`).
- `read_diff.py` reads diff input from string, file, or stdin.
- `parse_diff.py` parses unified diff (`diff --git`, hunks, line changes) into structured objects.
- `filters.py` removes lockfiles/vendor/generated/minified noise.
- `cli.py` provides end-to-end parse + filter + JSON output.
- Basic manual test scripts are present: `test_sanity.py`, `test_read_diff.py`, `test_parse_diff.py`.
- `core/diff/README.md` defines explicit scope boundaries (parser only, no PR/LLM/platform logic).

## Product & Platform Strategy
- Develop GitHub-first for speed of iteration, distribution, and early traction.
- Keep architecture platform-agnostic by separating core logic from platform adapters.
- Add Bitbucket adapter after core + GitHub path is stable and validated.

## Architecture Direction
- `core/`
- Diff parsing, filtering, prompt building, review rules, LLM adapters.
- `adapters/github/`
- PR event handling, metadata fetch, comment publishing.
- `adapters/bitbucket/`
- PR event handling, metadata fetch, comment publishing.
- `cli/`
- Local testing and CI-driven execution.
- `api/` (optional, later)
- Hosted control plane for multi-tenant app, billing, analytics, policies.

## Phase Roadmap

### Phase 1 - Diff Foundation (Completed / Stabilize)
Goal: deterministic diff-to-JSON pipeline.
- Confirm parser behavior on real-world diffs (including noisy and edge-ish unified diffs).
- Harden test coverage with fixture-based tests (not only manual scripts).
- Normalize docs and examples to match actual Python implementation and CLI usage.

Exit criteria:
- Stable structured output for representative diffs.
- Reproducible tests for parsing + filtering.

### Phase 2 - Review Core
Goal: convert parsed diff into high-signal AI review text.
- Implement prompt builder with strict review rubric:
- Bugs
- Security issues
- Performance risks
- Readability/maintainability
- Breaking changes
- Add noise control rules:
- No style-only comments
- No obvious restatements
- No speculative claims without evidence
- Add model adapter abstraction (OpenAI first, others optional).
- Support chunking for large diffs and per-file review fallback.

Exit criteria:
- Deterministic prompt assembly.
- Reliable markdown review output for PR comments.

### Phase 3 - GitHub-First Integration (MVP)
Goal: fully automated AI PR comment flow on GitHub.
- Implement GitHub Action workflow trigger on PR open/update.
- Connect flow:
- Extract diff
- Parse/filter
- Call LLM
- Publish PR comment
- Add secure secret handling (API keys/tokens only via CI secrets).
- Add safety behavior for failures/timeouts (graceful fallback comment or skip).

Exit criteria:
- End-to-end comment posted automatically on test repository PRs.

### Phase 4 - GitHub App & Commercial Readiness
Goal: move from repo-local automation to product-grade integration.
- Build GitHub App with webhook-driven backend.
- Centralize logic server-side for maintainability and billing support.
- Introduce paid tiers (open-core model):
- Open: base PR review
- Paid: advanced rules, analytics, team policies, hosted convenience

Exit criteria:
- Multi-repo onboarding and basic billing flow operational.

### Phase 5 - Bitbucket Adapter
Goal: expand to Atlassian ecosystem without rewriting core.
- Implement Bitbucket webhook/event adapter.
- Implement PR comment publisher via Bitbucket REST API.
- Reuse same core parser/review engine and model adapters.
- Add platform-specific auth, retries, and rate-limit handling.

Exit criteria:
- Same core review quality and workflow parity on Bitbucket PRs.

## Quality Gates (all phases)
- Security:
- No secrets in git.
- CI/CD secret management only.
- Reliability:
- Graceful handling of empty diffs, unsupported/binary diffs, and API failures.
- Observability:
- Structured logs for pipeline stages and model call outcomes.
- UX quality:
- High signal-to-noise; explicit "no issues found" when applicable.

## Immediate Next Actions
1. Convert existing ad-hoc tests into fixture-based automated tests for `core/diff`.
2. Implement prompt builder + review rubric module in `core`.
3. Add initial LLM adapter and local CLI command for offline review generation.
4. Create GitHub Action MVP to post PR comments from generated markdown.

