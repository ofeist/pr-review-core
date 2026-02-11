# GitHub Adapter Contract (Phase 3 Slice 0)

This document defines the minimum GitHub integration contract for the Phase 3 MVP.

## Scope
GitHub adapter responsibilities:
- react to PR lifecycle events in GitHub Actions
- extract PR diff context
- run review generation command
- create/update a PR comment with review markdown

Out of scope for this adapter:
- diff parsing internals (`core/diff`)
- review generation internals (`core/review`)
- billing, tenancy, hosted control plane

## Trigger Model
Primary trigger:
- `pull_request` with activity types:
- `opened`
- `synchronize`
- `reopened`

Expected behavior:
- each relevant PR event runs exactly one review workflow job
- workflow must be idempotent from a comment perspective (upsert, not spam)

## I/O Contract
Workflow input context:
- repository
- pull request number
- base ref / head ref
- token and optional model secrets

Workflow output:
- canonical markdown review text
- PR comment create/update via GitHub API

## Comment Marker Strategy
Use a stable hidden marker in bot comments so reruns update the same comment.

Recommended marker:
- `<!-- ai-pr-review:managed -->`

Rules:
- marker must be present in every managed comment body
- upsert algorithm searches PR comments for this marker
- if found: update existing comment
- if not found: create new comment

## Required GitHub Permissions
Workflow permissions (minimum):
- `contents: read`
- `pull-requests: write`

If listing comments via Issues API path:
- `issues: write`

## Secrets and Configuration
Required for OpenAI mode:
- `OPENAI_API_KEY`

Optional:
- `OPENAI_MODEL`
- `OPENAI_TIMEOUT_SECONDS`

Rules:
- secrets must only come from GitHub Secrets
- never commit keys or tokens to repository
- fake mode must work without secrets

## Failure Behavior Contract
On review failure:
- do not leak stack traces into PR comment
- publish/update controlled fallback message
- keep logs detailed enough for maintainers

On empty diff / ignored-only diff:
- skip comment or post concise "no actionable changes" message (single upserted comment)

## Test Checklist (Slice 0)
- Trigger events are explicitly defined.
- Marker strategy and upsert rules are explicit.
- Required permissions are listed.
- Required/optional secrets are listed.
- Adapter boundaries vs `core/` are clear.
