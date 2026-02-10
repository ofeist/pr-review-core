# pr-review-core

# Diff Parser – Scope & Specification

This module is responsible for **reading and parsing git diffs** into a
structured, deterministic format that can be consumed by the review engine.

It is intentionally **dumb and limited**.

---

## Purpose

- Take a raw `git diff` (unified diff format)
- Convert it into structured data (`DiffFile`, `DiffHunk`, `Change`)
- Do **nothing else**

This module:
- does NOT know what a PR is
- does NOT talk to GitHub / Bitbucket
- does NOT call any LLM
- does NOT make decisions

---

## Supported Input

### ✅ Supported
- Unified diff (default `git diff` output)
- Text-based source files
- Diffs generated via:
  ```bash
  git diff origin/main...HEAD
  ```

❌ Not Supported (for now)

Binary files

Rename-only diffs

File mode changes

Submodules

These cases should be ignored or skipped gracefully.

Parsing Rules
Files
Diff is split by diff --git

File path is extracted from diff header

Each file becomes one DiffFile object

Hunks
Hunks are identified by:

@@ -old_start,old_len +new_start,new_len @@
Hunks without meaningful changes may be ignored

Lines
+ → added line

- → removed line

→ context line

Context-only hunks do not need to be preserved.

Ignored Files & Directories
The following are excluded by default:

Lock files:

package-lock.json

yarn.lock

poetry.lock

Vendor / generated directories:

vendor/

node_modules/

dist/

build/

Minified assets:

*.min.js

*.min.css

Filtering happens after parsing, as a separate step.

Output Data Model (Conceptual)
The parser outputs a list of files with hunks and line-level changes.

Example (simplified):

[
  {
    "path": "src/auth/login.py",
    "language": "python",
    "hunks": [
      {
        "old_start": 12,
        "new_start": 14,
        "changes": [
          { "type": "add", "content": "if not user:" },
          { "type": "add", "content": "    return None" }
        ]
      }
    ]
  }
]
Exact class / dataclass definitions live in code.

Responsibility Boundaries
The diff parser is responsible for:

reading diff input

parsing it into a structured format

The diff parser is NOT responsible for:

language semantics

code quality analysis

prompt construction

noise filtering

confidence scoring

If a feature requires knowledge of:

PR metadata

repository rules

AI behavior

→ it does NOT belong here.

Design Philosophy
Deterministic

Side-effect free

Easy to test with static diff fixtures

Optimized for clarity over completeness

80% correct and predictable > 100% clever.

Testing Strategy
Static diff fixtures

Real diffs from small PRs

JSON snapshot comparison

No integration tests with git hosting platforms.

