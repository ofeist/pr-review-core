# Phase 3 Thin Slices

## Purpose
Break **Phase 3 - GitHub-First Integration (MVP)** into small, end-to-end slices that deliver incremental value and keep rollout risk low.

## Status
- Slice 0: done
- Slice 1: done
- Slice 2: done
- Slice 3: pending
- Slice 4: pending
- Slice 5: pending
- Slice 6: pending
- Slice 7: pending
- Slice 8: pending

## Phase 3 Goal (from roadmap)
Fully automate AI PR review comments on GitHub:
- trigger on PR opened/updated
- extract diff
- run review pipeline
- publish/update PR comment
- keep secrets in CI only
- handle failure/timeout gracefully

## Working Rules
- Keep GitHub-specific logic outside `core/`.
- Keep local/CI behavior aligned (same review command where possible).
- Ship fake-adapter path first, then OpenAI path.
- Avoid duplicate PR comments; prefer update-in-place.

## Slice Plan

### Slice 0 - GitHub Integration Contract
Objective: define minimal interface for GitHub workflow and comment behavior before wiring actions.

Deliverables:
- Add `adapters/github/README.md` with event model and boundaries.
- Define comment marker strategy (stable hidden marker in bot comment body).
- Define required workflow permissions and secrets.

Tests:
- Documentation checklist review (manual).

Done when:
- Team can answer: trigger events, input/output contract, comment update strategy, and secret requirements without ambiguity.

### Slice 1 - Workflow Skeleton (No Comment Yet)
Objective: get deterministic PR-triggered pipeline execution in GitHub Actions.

Deliverables:
- Add `.github/workflows/ai-review.yml`.
- Trigger on `pull_request` (`opened`, `synchronize`, `reopened`).
- Checkout repo and run baseline command with fake adapter.
- Store markdown output as workflow artifact.

Tests:
- Open/update PR and confirm workflow runs.
- Confirm artifact contains markdown output.

Done when:
- PR events reliably execute workflow and produce review artifact.

### Slice 2 - Diff Extraction Robustness
Objective: make diff extraction stable across fork/non-fork and merge-base scenarios.

Deliverables:
- Add script under `adapters/github/scripts/` to compute and extract PR diff.
- Handle base/head refs safely.
- Fail with explicit error for unsupported/empty contexts.

Tests:
- Repo PR test with normal branch PR.
- Empty-diff PR test.

Done when:
- Workflow consistently passes valid diff to review CLI in target test repository.

### Slice 3 - Publish PR Comment (Create-Only)
Objective: publish first AI review comment to PR.

Deliverables:
- Add comment publish step via GitHub API (`actions/github-script` or equivalent).
- Post markdown from workflow output.
- Add bot header and stable marker token.

Tests:
- PR run creates one AI review comment.

Done when:
- End-to-end flow posts visible comment on PR.

### Slice 4 - Comment Upsert (No Duplicates)
Objective: update existing bot comment instead of spamming new comments.

Deliverables:
- Query PR comments for marker.
- If found, update existing comment.
- If not found, create new comment.

Tests:
- Re-run workflow on same PR; verify single comment gets updated.

Done when:
- Repeated PR updates do not increase bot-comment count.

### Slice 5 - OpenAI Path + Secret Controls
Objective: enable real model path while keeping fake as safe default.

Deliverables:
- Workflow switch for adapter mode (`fake` vs `openai`).
- Read `OPENAI_API_KEY` from GitHub secrets only.
- Optional env support: `OPENAI_MODEL`, `OPENAI_TIMEOUT_SECONDS`.

Tests:
- Fake mode still works without secrets.
- OpenAI mode works when secrets are set.
- Missing-secret path fails with clear recoverable output.

Done when:
- Secure and explicit model mode selection works in CI.

### Slice 6 - Failure and Timeout UX
Objective: degrade gracefully on model/runtime failures.

Deliverables:
- Add timeout limits in workflow job/steps.
- On failure, post/update controlled fallback comment:
- summary of failure class (no stack trace)
- explicit no-review outcome
- Ensure logs include enough detail for maintainers.

Tests:
- Simulate adapter failure and timeout; verify graceful PR comment and non-leaky output.

Done when:
- Failed runs produce useful but safe PR feedback.

### Slice 7 - Noise/Size Guards in Workflow
Objective: keep comment quality and size practical for real PRs.

Deliverables:
- Skip comment on empty diff or ignored-only changes.
- Add max-comment-size safeguard with truncation notice.
- Preserve canonical markdown sections.

Tests:
- Empty-diff PR -> no spam comment.
- Oversized output -> truncated but valid markdown comment.

Done when:
- Workflow avoids spam and handles large outputs safely.

### Slice 8 - Hardening + Exit Pack
Objective: finalize Phase 3 with reproducibility and onboarding clarity.

Deliverables:
- Add CI docs section in root `README.md` (setup, permissions, secrets, troubleshooting).
- Add `adapters/github/README.md` runbook for maintenance.
- Add workflow test checklist in `ops/`.
- Capture known limitations and follow-ups for Phase 4.

Tests:
- Manual acceptance run on test repository with:
- open PR
- update PR
- rerun same commit
- failure simulation

Done when:
- New maintainer can configure and validate GitHub MVP flow without tribal knowledge.

## Phase 3 Acceptance Checklist
- PR trigger executes reliably on opened/synchronize/reopened.
- Diff extraction is stable for normal PR cases.
- Review markdown is generated in CI.
- Bot comment is posted and updated in place (no duplicates).
- Fake and OpenAI modes both supported.
- Secrets are consumed only via GitHub Secrets.
- Failure/timeout behavior is graceful and non-leaky.
- Empty/oversized outputs are handled safely.
- Setup and runbooks are documented.

## Exit Condition
Phase 3 is complete when end-to-end AI comment upsert works on a test GitHub repository across repeated PR updates with documented setup and graceful failure handling.

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

## Execution Notes
- Keep fake mode as default until OpenAI path is verified.
- Validate each slice on a disposable test PR before moving to the next.
- Commit after each slice with test evidence in commit message.



