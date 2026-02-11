# pr-review-core

Platform-agnostic core for AI-assisted pull request review.

## Vision
This project is building a reusable PR review engine with this strategy:
- Build GitHub-first for fast iteration and adoption.
- Keep core logic platform-agnostic.
- Add Bitbucket integration after core and GitHub flow are stable.

The detailed roadmap is in `ops/ROADMAP.md`.

## Current Scope
Today, this repository contains the Diff Foundation (Phase 1):
- Read diff input from stdin, file, or raw string.
- Parse unified git diff into deterministic Python dataclasses.
- Filter noisy files (lockfiles, vendor/generated, minified assets).
- Output stable JSON through a CLI entrypoint.

Out of scope right now:
- PR platform integration (GitHub/Bitbucket APIs)
- LLM prompting and model calls
- Automated comment publishing
- Billing, analytics, and multi-tenant APIs

## Repository Layout
- `core/diff/types.py`: canonical data model (`DiffFile`, `DiffHunk`, `Change`, `ChangeType`)
- `core/diff/read_diff.py`: input reader
- `core/diff/parse_diff.py`: unified diff parser
- `core/diff/filters.py`: ignore/noise filtering
- `core/diff/cli.py`: parse + filter + JSON output
- `core/diff/README.md`: module-level diff parser contract
- `ops/ROADMAP.md`: project roadmap and phase plan
- `ops/roadmap-hr.txt`: Croatian planning notes
- `ops/roadmap-en.txt`: English translation of planning notes

## Quick Usage
Parse a git diff and print JSON:

```bash
git diff origin/main...HEAD | python -m core.diff.cli
```

Use parser directly in Python:

```python
from core.diff.read_diff import read_diff
from core.diff.parse_diff import parse_diff
from core.diff.filters import filter_diff_files

raw = read_diff(from_string="""diff --git a/a.py b/a.py\n@@ -1,0 +1,1 @@\n+print('hi')\n""")
files = parse_diff(raw)
filtered = filter_diff_files(files)
```

## Roadmap Snapshot
- Phase 1: Diff Foundation (implemented, now stabilizing with stronger tests/docs)
- Phase 2: Review Core (prompt builder, rubric, model adapter, chunking)
- Phase 3: GitHub MVP integration (PR trigger to comment flow)
- Phase 4: GitHub App and commercial readiness
- Phase 5: Bitbucket adapter and parity

See `ops/ROADMAP.md` for details and exit criteria.

