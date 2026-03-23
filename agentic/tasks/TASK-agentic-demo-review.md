# Task

## ID
agentic-demo-review

## Branch
feature/agentic-demo-review

## Goal
Add a deterministic `--agentic-demo` mode to the review CLI so the project can showcase a planner -> reviewer -> QA -> final recommendation workflow shape without implementing real multi-agent orchestration.

## Scope
- Add `--agentic-demo` flag to the review CLI.
- Pass the flag through to the review pipeline.
- When enabled, transform normal review output into staged demo sections:
  - Plan
  - Review
  - QA
  - Final Recommendation
- Keep the feature deterministic and compatible with the `fake` adapter path.
- Add focused automated tests for CLI behavior and staged markdown output.
- Add a short documentation note describing the feature as a demo/showcase mode.

## Out of Scope
- Real multi-agent execution.
- Separate planner/reviewer/QA model calls.
- Workdir automation or branch orchestration.
- GitHub App, webhook, or backend service work.
- Changes to default review behavior when `--agentic-demo` is not enabled.

## Risks
- Users may overinterpret the feature as real orchestration unless the demo nature is stated clearly.
- A markdown post-processing approach may become fragile if the canonical review output changes.
- Scope may expand if the slice starts trying to implement real agent coordination.

## Verification Plan
- Run focused CLI tests for the new flag and output shape.
- Run markdown snapshot tests covering the staged demo output.
- Manually run the CLI with `--adapter fake --agentic-demo` on an existing diff fixture and inspect the output.

## Notes
- This slice is intended as a showcase feature first, with limited practical value as a structured review presentation mode.
- Keep the implementation small and reversible.
