# Agentic Workflow

Use the workflow like this:

## Workdirs
- `repo/`, `repo-review/`, and `repo-qa/` are the working directories used by the workflow.
- In practice these are usually Git worktrees, not three independent clones.
- Typical local setup:
  - `repo/` owns the active `feature/*` branch
  - `repo-review/` stays on `main`
  - `repo-qa/` stays detached or on `main`
- Review and QA should inspect `origin/feature/<task-slug>` and only create `review/*` or `qa/*` branches when they need to produce a patch.

## 1. Pick one thin slice
- one concrete change only
- not "improve everything"
- write down:
  - goal
  - scope
  - out of scope
  - risks

## 2. Create a task doc
- use:
  - `agentic/tasks/TASK_TEMPLATE.md`
- fill in at least:
  - `ID`
  - `Branch`
  - `Goal`
  - `Scope`
  - `Out of scope`
  - `Verification plan`
- if the task is already a single thin slice, the task doc is enough; do not create another "thin slices" planning document unless the work is large enough to need one

## 3. Create the owner feature branch
- in `repo/`
```bash
git checkout -b feature/<task-slug>
git push -u origin feature/<task-slug>
```

If the workflow docs/templates themselves are new and other workdirs need them, commit and push those baseline docs on `main` first. Product/code changes should still go on the feature branch.

## 4. Run the planner
- use:
  - `agentic/prompts/PLANNER_PROMPT.txt`
- inputs:
  - `AGENTS.md`
  - your task doc
- output should be:
  - a short execution plan
  - risks
  - suggested checks

## 5. Build in the owner workdir
- still in `repo/`
- use:
  - `agentic/prompts/BUILDER_PROMPT.txt`
- implement the slice only
- update docs/env/workflows/generated files if the change requires them

## 6. Write builder handoff
- use:
  - `agentic/handoffs/HANDOFF_TEMPLATE.md`
- record:
  - what changed
  - what was run
  - what was not run
  - rollout notes if relevant

## 7. Review in `repo-review/`
- inspect:
  - `origin/feature/<task-slug>`
- if patch needed:
  - create `review/<task-slug>`
- use:
  - `agentic/prompts/REVIEWER_PROMPT.txt`
- produce findings first
- optional small review patch
- not every finding must be accepted, but any rejected finding should be recorded with explicit rationale in the handoff or PR notes

## 8. QA in `repo-qa/`
- validate:
  - `origin/feature/<task-slug>`
- if fix needed:
  - create `qa/<task-slug>`
- use:
  - `agentic/prompts/QA_PROMPT.txt`
- run the smallest correct verification:
  - focused tests
  - `make ci-local` if broader
  - staging if rollout-sensitive

## 9. Integrate accepted fixes
- back in `repo/`
- usually:
```bash
git cherry-pick <review-or-qa-commit>
```

## 10. Push and open PR
```bash
git push origin feature/<task-slug>
```
- then PR to `main`
- check repo PR policy early:
  - required release labels
  - compatibility-sensitive file rules
  - changelog or migration-note requirements when contract-sensitive files changed
- keep detailed release/versioning rules in:
  - `ops/versioning-policy.md`
  - `ops/compatibility-policy.md`
  - `.github/workflows/release-policy.yml`

## 11. Merge only when evidence is good enough
- code correct
- checks run
- rollout risks understood
- docs/config/generated artifacts updated if needed
- for showcase slices, limited workflow or documentation updates that directly explain the showcased flow can remain in scope if that intent is explicit

## 12. Reset Workdirs After Merge
- delete the feature branch only after no workdir still uses it
- only one worktree can own a branch name at a time
- when `main` is blocked, detach the workdir currently holding it before attaching `main` elsewhere
- keep `repo-review/` and `repo-qa/` detached when idle unless they actively need a branch
- after merge, refresh other workdirs with `git fetch origin`

That is the normal loop.

## Short version
1. choose one thin slice
2. create task doc
3. create `feature/...` and push it
4. run planner
5. build
6. handoff
7. review
8. QA
9. cherry-pick fixes
10. PR
11. reset workdirs after merge
