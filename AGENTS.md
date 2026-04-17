# AGENTS

## Purpose
This repository uses a pragmatic agentic workflow for small, reviewable slices.
The human orchestrator sets scope and acceptance. Agents help with implementation, review, QA, docs, and operational follow-through.

## Core workflow
- Prefer thin slices over broad refactors.
- Keep one clear owner branch for product/code changes.
- Use review findings and QA evidence to tighten a slice before merge.
- Treat docs, env wiring, deploy workflows, and runtime behavior as one system when a change crosses those boundaries.

## Branch policy
- Do not push product/code changes directly to `main`.
- Use a feature branch for application, migration, infra, and workflow changes unless the user explicitly requests otherwise.
- Direct commits on `main` are acceptable for small docs/ops/TODO housekeeping when explicitly intended.
- Keep review/QA patch branches short-lived and integrate them back explicitly.

## Diff discipline
- Keep diffs small and task-focused.
- Do not perform unrelated refactors during feature work.
- Preserve existing comments and user-facing wording unless the task requires changing them.
- Do not rename env vars, API fields, database columns, or public behavior casually.
- Call out migration, rollout, or billing risk explicitly when present.

## API discipline
- Prefer additive API changes over breaking changes in thin slices.
- Preserve response shape and field names unless the task explicitly changes the API contract.
- If an API contract changes, update tests, generated docs, and rollout notes together.

## Architecture discipline
- Prefer evolutionary changes over broad redesign inside a thin slice.
- If a better abstraction is obvious but not required for the slice, capture it as a follow-up instead of expanding scope.
- Separate immediate delivery work from longer-term architecture cleanup deliberately.

## Generated artifacts
- Commit `www/docs/openapi.json` whenever it was regenerated and changed.
- Do not hand-edit generated artifacts unless that is the explicit task.

## Config and deploy coupling
When adding or changing config, check the full chain:
- app settings / config readers
- env templates under `deploy/envs/`
- `deploy/docker-compose*.yaml`
- GitHub Actions workflows under `.github/workflows/`
- docs and runbooks under `ops/` and `docs/`
- the env overview document: `ops/CONFIG_FLAGS.md`

A config change is not complete until the runtime consumers and deploy path agree.
Keep `ops/CONFIG_FLAGS.md` aligned when env vars are added, removed, renamed, or semantically changed.

## Verification ladder
Choose the smallest verification that proves the slice, then escalate only as needed:
- focused unit or file-level tests first
- targeted integration tests next
- `make ci-local` when the slice affects broader app behavior or generated docs
- staging deploy/smoke for deploy, billing, webhook, migration, or infra-sensitive changes
- prod only after staging passes and rollout risk is understood

## Versioning and release discipline
- Treat version bumps and release tags as deliberate release artifacts, not afterthoughts.
- When behavior, deploy wiring, or billing semantics change materially, note whether a release tag or version bump is required.
- Prefer creating new versioned objects over mutating old ones in place when semantics change cleanly, especially for pricing and rollout-sensitive configuration.

## Billing and Stripe changes
- Treat billing changes as rollout-sensitive.
- Preserve backward compatibility deliberately when possible.
- Check schema, webhook flow, pusher/worker flow, env vars, deploy workflows, and ops docs together.
- Never assume Stripe config is complete until the runtime env and webhook path are verified.

## Reviewer expectations
Reviewer should focus on:
- logic bugs
- edge cases
- migration safety
- rollout/config risk
- missing tests
- unintended scope expansion

Findings should come before summary.

## QA expectations
QA should focus on:
- whether the slice actually works in the intended environment
- whether config/deploy wiring matches the code
- whether generated artifacts and docs were updated when needed
- whether residual risks are clearly stated

## Definition of done
A slice is done when:
- the code change is complete for the agreed scope
- relevant tests/checks were run
- generated artifacts are updated if needed
- config/deploy/doc wiring is updated if needed
- known risks and follow-ups are explicitly noted