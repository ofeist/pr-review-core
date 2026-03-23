# Workdirs

## Purpose
This repository uses three local workdirs:
- `repo/`
- `repo-review/`
- `repo-qa/`

These are usually Git worktrees, not three independent clones.

## Starting state
- `repo/` stays attached to `main`
- `repo-review/` and `repo-qa/` are typically created detached so they do not compete for the same branch attachment
- this detached state is only a safe initialization detail, not the normal day-to-day workflow

## Ownership model
- `repo/` owns the active `feature/*` branch
- `repo-review/` is for review and optional review patches
- `repo-qa/` is for validation and optional QA patches
- one writer owns the `feature/*` branch at a time

## Normal branch usage
- push the owner `feature/*` branch early so the other workdirs can branch from `origin/feature/*`
- Reviewer should not attach the same active `feature/*` branch in `repo-review/`
- QA should not attach the same active `feature/*` branch in `repo-qa/`
- Reviewer should create `review/*` only if a real patch is needed
- QA should create `qa/*` only if a real fix is needed

## Refreshing after owner changes
- run `git fetch origin` in review and QA workdirs
- rebase temporary `review/*` or `qa/*` branches onto `origin/feature/*`
- if a patch branch is tiny and disposable, recreating it from the new owner tip is often simpler

## Integrating review or QA changes
- integrate accepted review/QA commits back into `feature/*` explicitly
- prefer `git cherry-pick` for small review/QA commits
- avoid ad-hoc merging unless there is a strong reason

## Normal flow
1. Create task doc
2. Create `feature/*` branch in `repo/`
3. Push `feature/*` early
4. Implement in `repo/`
5. Review in `repo-review/`
6. Validate in `repo-qa/`
7. Integrate approved changes back into `feature/*` explicitly
8. Push and open PR to `main`