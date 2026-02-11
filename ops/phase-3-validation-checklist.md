# Phase 3 Validation Checklist

Manual acceptance checklist for GitHub MVP integration.

## Preconditions
- Workflow file exists: `.github/workflows/ai-review.yml`
- Repo permissions allow workflow write to PR comments.
- Test repository has Actions enabled.

## Configuration Matrix
- Fake mode:
- `AI_REVIEW_ADAPTER_MODE=fake`
- no OpenAI secret required

- OpenAI mode:
- `AI_REVIEW_ADAPTER_MODE=openai`
- `OPENAI_API_KEY` secret set
- optional `OPENAI_MODEL`, `OPENAI_TIMEOUT_SECONDS`

## Scenario Tests
1. Open PR (new branch)
- Expected: workflow runs, managed comment created.

2. Update PR (new commit)
- Expected: workflow reruns, same managed comment updated.

3. Re-run workflow on same commit
- Expected: no duplicate managed comment.

4. Empty or ignored-only diff
- Expected: comment summary says no actionable code changes.

5. OpenAI mode without secret
- Expected: controlled fallback comment, no stack trace.

6. Extraction/review failure simulation
- Expected: controlled fallback comment with failure class.

7. Oversized output simulation
- Expected: truncated comment with artifact pointer.

## Evidence to Collect
- Workflow run URLs
- PR URL
- Screenshot or copy of managed comment before/after update
- Artifact presence (`ai-review-markdown`)

## Exit Criteria
- All scenario tests pass in target test repository.
- One managed comment is consistently upserted.
- No secret leakage in logs or comments.
- Failure and timeout behavior remains user-safe.
