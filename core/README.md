# core Architecture

This folder contains platform-agnostic core logic for PR review.

## Layer Boundaries

### `core/diff`
Responsibility:
- Read raw git diff input.
- Parse unified diff text into structured change data.
- Apply file-level noise filters.

Input:
- raw diff text

Output:
- `DiffFile[]` and related diff dataclasses from `core/diff/types.py`

Out of scope:
- LLM calls
- Prompt design
- PR comments
- Risk/severity decisions

### `core/review` (Phase 2)
Responsibility:
- Build review prompts from parsed diff data.
- Call model adapters (OpenAI first).
- Normalize and filter model output.
- Produce final markdown review text.

Input:
- parsed diff data (`DiffFile[]`)

Output:
- review findings/summary and final markdown (review-layer types)

Out of scope:
- parsing raw git diff format
- GitHub/Bitbucket API publishing

## Why Two Type Modules
- `core/diff/types.py` models **what changed in code**.
- `core/review/types.py` models **what the review says about those changes**.

These are different domains, so separate types prevent coupling and confusion.

## End-to-End Data Flow
1. Raw diff text
2. `core/diff.read_diff` -> `core/diff.parse_diff` -> `core/diff.filters`
3. Structured diff (`DiffFile[]`)
4. `core/review` pipeline (prompt -> model -> normalize/filter)
5. Final markdown review text

## Design Rules
- Keep modules deterministic where possible.
- Keep interfaces explicit and testable.
- Avoid cross-layer leakage:
- diff layer must not import review-layer concepts
- review layer must not re-parse unified diff text

## Non-Goals in `core`
- Platform adapter logic (`adapters/github`, `adapters/bitbucket`)
- Webhook handling
- PR comment publishing APIs
- Billing/tenant concerns
