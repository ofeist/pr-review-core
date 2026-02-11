# GitHub Adapter Runbook

Phase 3 GitHub integration runbook for PR review automation.

## Purpose
This adapter connects GitHub PR events to core review generation and PR comment upsert.

## Scope Boundaries
Adapter responsibilities:
- receive PR event context from GitHub Actions
- extract PR diff safely
- run review command
- upsert managed PR comment

Out of scope:
- diff parsing internals (`core/diff`)
- review logic internals (`core/review`)
- hosted backend/billing features

## Workflow Entry Point
- `.github/workflows/ai-review.yml`

Trigger:
- `pull_request`: `opened`, `synchronize`, `reopened`

## Managed Comment Contract
Marker:
- `<!-- ai-pr-review:managed -->`

Rules:
- every managed comment must include marker
- reruns search by marker
- if found: update existing comment
- if not found: create new comment

## Diff Extraction
Script:
- `adapters/github/scripts/extract_pr_diff.py`

Behavior:
- resolves base/head commits
- attempts direct fetch and PR head fallback
- uses `base...head` when merge-base exists, else `base..head`
- writes diff to artifact path

## Adapter Modes
Configured via repository variable:
- `AI_REVIEW_ADAPTER_MODE`:
- `fake`
- `openai`

OpenAI mode:
- uses `OPENAI_API_KEY` from GitHub Secrets
- optional vars: `OPENAI_MODEL`, `OPENAI_TIMEOUT_SECONDS`

## Required GitHub Permissions
- `contents: read`
- `pull-requests: write`
- `issues: write`

## Guardrails
- Graceful fallback on extraction/review failure.
- Controlled fallback markdown for timeout/cancel/failure.
- Empty/ignored-only diff handling.
- Comment size guard via `AI_REVIEW_MAX_COMMENT_CHARS`.

## Operational Checklist
1. Confirm workflow permissions are set.
2. Confirm marker comment upsert behavior on repeated PR updates.
3. Confirm fake mode works without secrets.
4. Confirm openai mode works with secrets.
5. Confirm failure mode posts controlled fallback.
6. Confirm oversize guard truncates safely.

## Known Limitations (Phase 3)
- Workflow-driven integration only (no GitHub App).
- No advanced policy engine for org/team-specific rules.
- Comment upsert uses marker search in first page of PR comments.

## Phase 4 Follow-ups
- Migrate to GitHub App architecture.
- Move orchestration from workflow script logic to service endpoint.
- Add deeper observability and retry control.
- Improve comment targeting and pagination robustness.
