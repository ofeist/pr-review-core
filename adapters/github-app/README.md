# GitHub App Contract (Phase 4 Slice 0)

This document defines boundaries and contracts for the GitHub App architecture introduced in Phase 4.

## Purpose
Move from workflow-only PR automation to a centralized app/backend model that handles PR events, review orchestration, and comment upsert.

## Architecture Boundaries
### Core (`core/`)
Responsibilities:
- diff parsing and filtering
- review generation pipeline
- model adapter abstraction

Must remain platform-agnostic.

### GitHub App Adapter (`adapters/github-app/`)
Responsibilities:
- receive and validate GitHub webhook events
- normalize PR event payload into review requests
- obtain installation-scoped auth
- call backend orchestration entrypoints
- upsert managed PR comments

Out of scope:
- billing and plan pricing logic (separate service layer)
- low-level review heuristics (belongs to `core/review`)

### Backend Service (`api/` or equivalent)
Responsibilities:
- webhook endpoint handling
- idempotent event processing
- orchestration, retries, and observability
- persistence for event/run state

## Event Handling Contract
Source events:
- `pull_request` (`opened`, `synchronize`, `reopened`)

Normalized event payload (conceptual):
- `event_id`: unique delivery identifier
- `repo_owner`
- `repo_name`
- `installation_id`
- `pr_number`
- `base_sha`
- `head_sha`
- `head_ref`
- `base_ref`
- `timestamp`

Processing guarantees:
- idempotent processing by `(repo, pr_number, head_sha)` key
- duplicate deliveries do not create duplicate comments/jobs
- failures are retryable with bounded attempts

## Auth Contract
Required app credentials:
- `GITHUB_APP_ID`
- `GITHUB_APP_PRIVATE_KEY`
- `GITHUB_WEBHOOK_SECRET`

Token flow:
1. create app JWT
2. exchange JWT for installation access token
3. use installation token for GitHub API calls

Security rules:
- secrets from environment/secret manager only
- never commit private key/webhook secret
- redact secrets from logs

## PR Comment Contract
Managed comment marker:
- `<!-- ai-pr-review:managed -->`

Upsert behavior:
- find existing comment containing marker
- update if found
- create if not found

Body requirements:
- stable header
- execution metadata (adapter mode, status)
- normalized markdown from review pipeline
- no stack traces or raw exception dumps

## Failure Contract
On processing failure:
- classify error (`auth`, `webhook_signature`, `diff_fetch`, `review_runtime`, `comment_api`)
- emit structured logs with correlation id
- write controlled fallback comment content when safe/appropriate

On non-actionable diff:
- produce concise "No actionable code changes" summary
- keep one managed comment updated

## Non-Goals (Slice 0)
- no endpoint implementation yet
- no token exchange code yet
- no persistence schema yet

## Slice 0 Checklist
- boundaries between adapter/core/backend are explicit
- event payload contract is defined
- auth flow contract is defined
- comment marker/upsert strategy is defined
- failure contract is defined
