# Phase 5 Thin Slices

## Purpose
Break **Phase 5 - GitHub App & Commercial Readiness** into small, end-to-end slices that move from workflow-only automation to product-grade GitHub App architecture.

## Status
- Slice 0: done
- Slice 1: pending
- Slice 2: pending
- Slice 3: pending
- Slice 4: pending
- Slice 5: pending
- Slice 6: pending
- Slice 7: pending
- Slice 8: pending
- Slice 9: pending

## Phase 5 Goal (from roadmap)
Move from repo-local workflow integration to a product-ready GitHub App model with centralized backend logic, onboarding, and monetization foundations.

## Working Rules
- Keep `core/` platform-agnostic and reusable.
- Keep GitHub App integration in adapter/service layers.
- Favor reversible migrations and staged rollout.
- Preserve fake mode for deterministic testing.

## Slice Plan

### Slice 0 - App Contract and Boundaries
Objective: define architecture and contracts before implementation.

Deliverables:
- Add `adapters/github-app/README.md` with component boundaries.
- Define event handling contract (webhook payload -> review request -> comment upsert).
- Define auth contract (App ID, private key, installation token flow).

Tests:
- Architecture checklist review (manual).

Done when:
- Team can describe responsibilities and handoff points without ambiguity.

### Slice 1 - GitHub App Skeleton
Objective: create minimal app scaffolding and webhook endpoint.

Deliverables:
- Add backend service skeleton (`api/github_app/` or equivalent).
- Add `/webhook/github` endpoint with signature verification.
- Support health endpoint and basic structured logging.

Tests:
- Signature verification unit tests.
- Local webhook replay smoke test.

Done when:
- Verified webhook requests are accepted; invalid signatures are rejected.

### Slice 2 - Installation Auth Layer
Objective: implement installation token generation and API client factory.

Deliverables:
- JWT generation from app private key.
- Installation token exchange utility.
- GitHub API client wrapper for installation-scoped operations.

Tests:
- Token flow unit tests (mocked GitHub API).
- Error-path tests for expired/invalid credentials.

Done when:
- Service can obtain installation-scoped client deterministically.

### Slice 3 - PR Event Intake and Deduping
Objective: reliably process PR opened/synchronize/reopened events once.

Deliverables:
- Parse and normalize PR event payload.
- Idempotency key strategy (repo + PR + head SHA).
- Lightweight event persistence for dedupe/retry control.

Tests:
- Duplicate event tests.
- Out-of-order event handling tests.

Done when:
- Same event cannot trigger duplicate review jobs.

### Slice 4 - Diff Fetch and Review Orchestration
Objective: run existing review core from backend orchestration.

Deliverables:
- Server-side diff fetch from GitHub API or git strategy.
- Invoke `core/review` pipeline with adapter selection.
- Persist run status and generated markdown.

Tests:
- End-to-end orchestration test with fake adapter.
- Failure-path tests (diff fetch/model failure).

Done when:
- Backend can produce review markdown for a PR event without workflow logic.

### Slice 5 - Comment Upsert via App Identity
Objective: publish and update managed comments using app installation identity.

Deliverables:
- Reuse marker strategy for comment upsert.
- Add deterministic body template with metadata.
- Ensure no duplicate managed comments.

Tests:
- Create-then-update integration tests (mocked API).
- Marker collision tests.

Done when:
- Repeated events update one managed comment.

### Slice 6 - Retry, Timeout, and Queueing Basics
Objective: make processing reliable under transient failures.

Deliverables:
- Add job queue or retry scheduler abstraction.
- Exponential backoff for recoverable errors.
- Timeout control per processing stage.

Tests:
- Retry policy tests.
- Timeout fallback tests.

Done when:
- Transient failures recover without duplicate comments or stuck jobs.

### Slice 7 - Onboarding UX and Repo Controls
Objective: make installation and repository-level controls usable.

Deliverables:
- Installation landing and setup checklist.
- Repo-level config model (adapter mode, max comment size, feature flags).
- Basic opt-in/opt-out controls.

Tests:
- Configuration validation tests.
- Onboarding flow manual checklist.

Done when:
- New repo can be enabled with predictable defaults and minimal steps.

### Slice 8 - Billing and Plan Gates Foundation
Objective: add minimal monetization plumbing for open-core model.

Deliverables:
- Plan model (free vs paid capability gates).
- Billing provider stub/integration point (Stripe-ready abstraction).
- Server-side feature gating hooks.

Tests:
- Plan gate unit tests.
- Unauthorized feature access tests.

Done when:
- Feature availability can be controlled by plan in backend.

### Slice 9 - Hardening and Exit Pack
Objective: finish Phase 5 with operational readiness and documentation.

Deliverables:
- Runbook for incident handling and retries.
- Deployment doc (env vars, secrets, key rotation).
- Migration notes from workflow-only MVP to app-based flow.
- Phase 5 validation checklist in `ops/`.

Tests:
- Staging end-to-end test on test GitHub App installation.
- Failure drills (bad signature, token expiry, API rate limit).

Done when:
- Team can deploy, operate, and troubleshoot GitHub App flow without tribal knowledge.

## Phase 5 Acceptance Checklist
- GitHub webhook signature verification is enforced.
- Installation token auth is reliable.
- PR events are deduped and processed idempotently.
- Review orchestration runs from backend using `core/review`.
- Comment upsert works under app identity.
- Retry/timeout behavior is operationally safe.
- Onboarding and repo controls are usable.
- Plan gates exist for paid features.
- Docs and runbooks are complete.

## Exit Condition
Phase 5 is complete when the GitHub App backend can receive PR events, generate reviews, upsert comments reliably, and enforce basic plan gating with operational runbooks in place.

## Suggested Order
1. Slice 0
2. Slice 1
3. Slice 2
4. Slice 3
5. Slice 4
6. Slice 5
7. Slice 6
8. Slice 7
9. Slice 8
10. Slice 9

## Execution Notes
- Keep workflow-based MVP as fallback until app path is stable.
- Validate each slice on staging installation before production rollout.
- Commit per slice with test evidence and migration notes.


