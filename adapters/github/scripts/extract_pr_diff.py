#!/usr/bin/env python3
"""Extract a PR diff robustly for GitHub Actions workflows."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


class DiffExtractError(Exception):
    """Raised when PR diff extraction cannot proceed."""


def run_git(args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        text=True,
        capture_output=True,
    )
    if check and result.returncode != 0:
        raise DiffExtractError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result


def object_exists(sha: str) -> bool:
    result = subprocess.run(
        ["git", "cat-file", "-e", f"{sha}^{{commit}}"],
        text=True,
        capture_output=True,
    )
    return result.returncode == 0


def try_fetch_object(ref: str) -> bool:
    result = subprocess.run(
        ["git", "fetch", "--no-tags", "--depth=1", "origin", ref],
        text=True,
        capture_output=True,
    )
    return result.returncode == 0


def ensure_commit(sha: str, *, pr_number: int, role: str) -> str:
    if object_exists(sha):
        return sha

    # First try direct object fetch.
    try_fetch_object(sha)
    if object_exists(sha):
        return sha

    # For head commits in fork PRs, try pull ref fetch.
    if role == "head":
        pull_ref = f"refs/pull/{pr_number}/head"
        if try_fetch_object(pull_ref):
            fetched = run_git(["rev-parse", "FETCH_HEAD"], check=True).stdout.strip()
            if fetched and object_exists(fetched):
                return fetched

    raise DiffExtractError(
        f"Unable to resolve {role} commit '{sha}'. "
        f"Tried direct fetch and PR ref fallback."
    )


def choose_diff_range(base_sha: str, head_sha: str) -> tuple[str, str]:
    merge_base = subprocess.run(
        ["git", "merge-base", base_sha, head_sha],
        text=True,
        capture_output=True,
    )

    if merge_base.returncode == 0:
        return f"{base_sha}...{head_sha}", "triple-dot"
    return f"{base_sha}..{head_sha}", "two-dot"


def write_diff(diff_text: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(diff_text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract pull-request diff")
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--head-sha", required=True)
    parser.add_argument("--pr-number", required=True, type=int)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    base_sha = args.base_sha.strip()
    head_sha = args.head_sha.strip()
    if not base_sha or not head_sha:
        print("Error: base/head SHA must be non-empty.", file=sys.stderr)
        return 2

    try:
        run_git(["rev-parse", "--is-inside-work-tree"], check=True)
        resolved_base = ensure_commit(base_sha, pr_number=args.pr_number, role="base")
        resolved_head = ensure_commit(head_sha, pr_number=args.pr_number, role="head")

        diff_range, range_mode = choose_diff_range(resolved_base, resolved_head)
        diff = run_git(["diff", "--no-color", diff_range], check=True).stdout

        write_diff(diff, Path(args.output))

        if not diff.strip():
            print(
                f"Warning: extracted diff is empty ({range_mode} range {diff_range}).",
                file=sys.stderr,
            )
        else:
            print(
                f"Extracted diff using {range_mode} range {diff_range} "
                f"({len(diff.splitlines())} lines).",
                file=sys.stderr,
            )

        return 0
    except DiffExtractError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
