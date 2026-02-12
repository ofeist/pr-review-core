# core/diff Module

Deterministic diff parsing module for the project core.

## Purpose
Convert raw unified git diff text into a structured, testable representation.

This module is intentionally limited:
- It reads and parses diff content.
- It does not perform code review decisions.
- It does not call LLMs.
- It does not talk to GitHub or Bitbucket.

## Responsibilities
- `read_diff.py`: load raw diff text from `from_string`, `from_file`, or `stdin`.
- `parse_diff.py`: convert unified diff text into `DiffFile[]`.
- `filters.py`: remove noisy files after parsing.
- `types.py`: define canonical dataclasses used by the rest of core.

## Data Model
Defined in `src/core/diff/types.py`:
- `ChangeType`: `add`, `remove`, `context`
- `Change`: one line-level change
- `DiffHunk`: hunk metadata and list of changes
- `DiffFile`: file path and hunks (`language` optional)

## Supported Input
- Unified diff format (`git diff` default)
- Text files
- Typical source-code PR diffs

## Not Supported (Current)
- Binary file diffs
- Rename-only metadata handling
- File mode-only changes
- Submodule-specific parsing

Unsupported or noisy sections should be skipped safely instead of crashing.

## Parsing Rules
- Split files by `diff --git a/... b/...` headers.
- Parse hunks from `@@ -old,len +new,len @@`.
- Parse line prefixes: `+` as `add`, `-` as `remove`, and leading space as `context`.

## Filtering Rules
Filtering is a separate step and currently ignores patterns such as:
- lockfiles: `package-lock.json`, `yarn.lock`, `poetry.lock`
- generated/vendor directories: `vendor/`, `node_modules/`, `dist/`, `build/`
- minified assets: `*.min.js`, `*.min.css`

## CLI
Print parsed and filtered JSON from stdin diff:

```bash
PYTHONPATH=src git diff origin/main...HEAD | python -m core.diff.cli
```

## Boundaries
Belongs in this module:
- deterministic text parsing
- stable output shape
- parser-level resilience

Does not belong in this module:
- AI prompt design
- bug/security/performance judgment
- confidence scoring
- PR metadata handling
- comment publishing

## Testing Direction
Current legacy smoke scripts are in `tests/legacy/`. The next step is fixture-based tests covering:
- empty diffs
- multi-file diffs
- multi-hunk files
- noisy headers and lines
- ignored file patterns
