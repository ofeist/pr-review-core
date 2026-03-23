# Handoff: agentic demo review builder

## Role
Builder

## Branch
`feature/agentic-demo-review`

## Context
Implement the thin slice from `agentic/tasks/TASK-agentic-demo-review.md`: add a deterministic `--agentic-demo` mode to the review CLI that renders staged `Plan`, `Review`, `QA`, and `Final Recommendation` sections without adding real multi-agent orchestration.

## Scope checked
- CLI flag wiring
- review pipeline staged demo rendering
- focused tests and snapshot coverage
- short user-facing documentation note

## Done
- Added `--agentic-demo` to the review CLI.
- Passed the flag through to `run_review(...)`.
- Added deterministic staged output rendering in the review pipeline.
- Kept normal output unchanged when the flag is not set.
- Added a CLI test for staged output headings.
- Added snapshot coverage for fake adapter demo output.
- Added a short README note describing the mode as a deterministic showcase.

## Not done
- No real planner/reviewer/QA execution.
- No multiple model calls.
- No workdir/workflow automation.
- No GitHub App or backend work.

## Artifacts changed
- `src/core/review/cli.py`
- `src/core/review/pipeline.py`
- `tests/review/test_cli.py`
- `tests/review/test_markdown_snapshots.py`
- `tests/review/snapshots/fake_agentic_demo_raw_small.md`
- `README.md`

## Risks
- The staged output is presentation logic layered on one review pass and could be mistaken for real orchestration if described loosely.
- The renderer depends on the canonical markdown section names (`Summary`, `Intent`, `Change Summary`, `Findings`).
- Local verification must use `PYTHONPATH=src` in this environment because `python` otherwise imports an older installed `core` package from `site-packages`.

## Verification
Ran:
- `PYTHONPATH=src python -m unittest -v tests/review/test_cli.py`
- `PYTHONPATH=src python -m unittest -v tests/review/test_markdown_snapshots.py`

Passed:
- CLI tests: `9` tests passed.
- Markdown snapshot tests: `4` tests passed.

Not run:
- broader review suite
- `make ci-local`
- review/QA workdir validation

## Operational notes
- No env var, deploy, webhook, staging, migration, or generated artifact changes.

## Open questions / blockers
- None for this slice.

## Next
- Push the feature branch.
- Review in `repo-review/` against `origin/feature/agentic-demo-review`.
- If accepted, run QA in `repo-qa/` with the same branch tip.
