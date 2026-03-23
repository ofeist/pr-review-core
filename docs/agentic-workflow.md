# Agentic Workflow

Use the workflow like this:

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

## 3. Create the owner feature branch
- in `repo/`
```bash
git checkout -b feature/<task-slug>
git push -u origin feature/<task-slug>
```

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

## 11. Merge only when evidence is good enough
- code correct
- checks run
- rollout risks understood
- docs/config/generated artifacts updated if needed

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
