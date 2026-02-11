"""Chunking and merge utilities for large-diff review flows."""

from __future__ import annotations

import re
from typing import List

from core.diff.types import Change, DiffFile, DiffHunk


def chunk_diff_files(files: List[DiffFile], max_changes_per_chunk: int = 200) -> List[List[DiffFile]]:
    """Split parsed diff files into deterministic chunks by change count.

    Strategy:
    - Keep file order as provided.
    - Split large files by hunk.
    - Split oversized hunks by change count.
    - Ensure each chunk has at most ``max_changes_per_chunk`` changes.
    """

    if max_changes_per_chunk <= 0:
        raise ValueError("max_changes_per_chunk must be > 0")

    if not files:
        return [[]]

    chunks: List[List[DiffFile]] = []
    current: List[DiffFile] = []
    current_changes = 0

    for file_obj in files:
        pieces = _split_file(file_obj, max_changes_per_chunk)
        for piece in pieces:
            piece_changes = _file_change_count(piece)

            if current and current_changes + piece_changes > max_changes_per_chunk:
                chunks.append(current)
                current = []
                current_changes = 0

            current.append(piece)
            current_changes += piece_changes

    if current:
        chunks.append(current)

    return chunks or [[]]


def merge_chunk_markdowns(markdowns: List[str]) -> str:
    """Merge chunk-level markdown results into one deterministic review."""

    findings: List[str] = []
    seen: set[str] = set()

    for markdown in markdowns:
        for finding in _extract_findings(markdown):
            normalized = _dedupe_key(finding)
            if normalized in seen:
                continue
            seen.add(normalized)
            findings.append(finding)

    chunk_count = len(markdowns)
    if findings:
        summary = f"Reviewed {chunk_count} chunk(s). Kept {len(findings)} unique finding(s)."
    else:
        summary = f"Reviewed {chunk_count} chunk(s). No actionable findings after filtering."

    out: List[str] = [
        "## AI Review",
        "",
        "### Summary",
        summary,
        "",
        "### Findings",
    ]

    if findings:
        out.extend([f"- {item}" for item in findings])
    else:
        out.append("- No issues found.")

    return "\n".join(out).rstrip() + "\n"


def _split_file(file_obj: DiffFile, max_changes_per_chunk: int) -> List[DiffFile]:
    if not file_obj.hunks:
        return [file_obj]

    pieces: List[DiffFile] = []
    current_hunks: List[DiffHunk] = []
    current_changes = 0

    for hunk in file_obj.hunks:
        hunk_parts = _split_hunk(hunk, max_changes_per_chunk)
        for hunk_part in hunk_parts:
            hunk_changes = len(hunk_part.changes)

            if current_hunks and current_changes + hunk_changes > max_changes_per_chunk:
                pieces.append(DiffFile(path=file_obj.path, hunks=current_hunks, language=file_obj.language))
                current_hunks = []
                current_changes = 0

            current_hunks.append(hunk_part)
            current_changes += hunk_changes

    if current_hunks:
        pieces.append(DiffFile(path=file_obj.path, hunks=current_hunks, language=file_obj.language))

    return pieces


def _split_hunk(hunk: DiffHunk, max_changes_per_chunk: int) -> List[DiffHunk]:
    if len(hunk.changes) <= max_changes_per_chunk:
        return [hunk]

    parts: List[DiffHunk] = []
    idx = 0
    cursor_old = hunk.old_start
    cursor_new = hunk.new_start

    while idx < len(hunk.changes):
        block = hunk.changes[idx : idx + max_changes_per_chunk]
        block_old_start = cursor_old
        block_new_start = cursor_new
        old_len = 0
        new_len = 0

        for change in block:
            if change.type.value == "add":
                new_len += 1
                cursor_new += 1
            elif change.type.value == "remove":
                old_len += 1
                cursor_old += 1
            else:
                old_len += 1
                new_len += 1
                cursor_old += 1
                cursor_new += 1

        parts.append(
            DiffHunk(
                old_start=block_old_start,
                old_length=old_len,
                new_start=block_new_start,
                new_length=new_len,
                changes=list(block),
            )
        )

        idx += max_changes_per_chunk

    return parts


def _file_change_count(file_obj: DiffFile) -> int:
    return sum(len(hunk.changes) for hunk in file_obj.hunks)


def _extract_findings(markdown: str) -> List[str]:
    findings: List[str] = []
    in_findings = False

    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if line.lower() == "### findings":
            in_findings = True
            continue
        if line.startswith("### ") and in_findings:
            in_findings = False
        if not in_findings:
            continue
        if line.startswith("- "):
            item = line[2:].strip()
            if item and item.lower() != "no issues found.":
                findings.append(item)

    return findings


def _dedupe_key(text: str) -> str:
    lowered = text.lower().strip()
    lowered = re.sub(r"[^a-z0-9\s]", "", lowered)
    lowered = re.sub(r"\s+", " ", lowered)
    return lowered
