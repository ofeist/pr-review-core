# core/review Module

Review-layer core contracts and logic.

## Purpose
Transform parsed diff data into high-signal, normalized review output.

## Boundaries
- Input: structured diff data from `core/diff`.
- Output: review findings, summary, and markdown suitable for PR comments.

This layer does not parse raw unified diff and does not publish comments to
GitHub/Bitbucket APIs.
