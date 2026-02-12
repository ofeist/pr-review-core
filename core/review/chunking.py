"""Chunking and merge utilities for large-diff review flows."""

from __future__ import annotations

import re
from typing import List, Optional

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


def build_change_summary(files: List[DiffFile], max_files: int = 8) -> List[str]:
    """Build deterministic, neutral change-summary bullets from parsed diff."""

    if not files:
        return ["- No changed files detected."]

    lines: List[str] = []
    for file_obj in sorted(files, key=lambda f: f.path)[:max_files]:
        additions = 0
        removals = 0
        for hunk in file_obj.hunks:
            for change in hunk.changes:
                if change.type.value == "add":
                    additions += 1
                elif change.type.value == "remove":
                    removals += 1
        lines.append(f"- `{file_obj.path}` (+{additions}/-{removals}, hunks: {len(file_obj.hunks)})")

    hidden_count = max(0, len(files) - max_files)
    if hidden_count:
        lines.append(f"- {hidden_count} additional file(s) changed.")

    return lines


def build_pr_summary(files: List[DiffFile], max_files: int = 3) -> str:
    """Build one-line PR-oriented summary text for the markdown Summary section."""

    if not files:
        return "No changed files detected."

    sorted_paths = [f.path for f in sorted(files, key=lambda f: f.path)]
    visible_paths = sorted_paths[:max_files]
    hidden_count = max(0, len(sorted_paths) - len(visible_paths))

    if len(sorted_paths) == 1:
        summary = f"Changed 1 file: `{visible_paths[0]}`."
    else:
        visible = ", ".join(f"`{path}`" for path in visible_paths)
        summary = f"Changed {len(sorted_paths)} files: {visible}."

    if hidden_count:
        summary += f" (+{hidden_count} more)"

    return summary


def build_intent_summary(pr_title: str = "", pr_body: str = "", max_chars: int = 240) -> str:
    """Build deterministic one-line intent summary from PR metadata."""

    title = _clean_intent_text(pr_title)
    body = _clean_intent_text(pr_body)
    if not title and not body:
        return "Intent not provided."

    if title:
        return _truncate(_first_sentence(title), max_chars)

    return _truncate(_first_sentence(body), max_chars)


def merge_chunk_markdowns(
    markdowns: List[str],
    *,
    change_summary_lines: Optional[List[str]] = None,
    summary_prefix: Optional[str] = None,
    intent_summary: Optional[str] = None,
) -> str:
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
        stats = f"Reviewed {chunk_count} chunk(s). Kept {len(findings)} unique finding(s)."
    else:
        stats = f"Reviewed {chunk_count} chunk(s). No actionable findings after filtering."
    summary = f"{summary_prefix} {stats}".strip() if summary_prefix else stats

    out: List[str] = [
        "## AI Review",
        "",
        "### Summary",
        summary,
        "",
        "### Intent",
        (intent_summary or "Intent not provided."),
        "",
        "### Change Summary",
    ]
    if change_summary_lines:
        out.extend(change_summary_lines)
    else:
        out.append("- Not available.")

    out.extend([
        "",
        "### Findings",
    ])

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


def _normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    if max_chars <= 3:
        return "." * max_chars
    return text[: max_chars - 3].rstrip() + "..."


def _clean_intent_text(text: str) -> str:
    if not text:
        return ""

    cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
    cleaned = re.sub(r"```.*?```", " ", cleaned, flags=re.S)
    cleaned = cleaned.replace("`", " ")

    lines: List[str] = []
    for raw_line in cleaned.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#"):
            continue
        line = re.sub(r"^[-*+]\s+", "", line)
        line = re.sub(r"^\d+\.\s+", "", line)
        line = line.strip(":- ")
        if not line:
            continue
        if line.lower() in {"what was implemented", "files changed", "validation"}:
            continue
        lines.append(line)

    compact = _normalize_ws(" ".join(lines))
    compact = re.sub(
        r"^(what was implemented|implementation summary|summary)\s*[:\-]+\s*",
        "",
        compact,
        flags=re.I,
    )
    # If title/body leaked list-style continuation like ": - item", keep only the lead clause.
    compact = re.sub(r":\s*-\s+.*$", "", compact)
    compact = re.sub(r"\s*-\s*$", "", compact)
    compact = re.sub(r"\s*[:\-]\s*$", "", compact)
    compact = _normalize_ws(compact)
    return compact


def _first_sentence(text: str) -> str:
    if not text:
        return ""
    match = re.search(r"^(.{1,220}?[.!?])(?:\s|$)", text)
    if match:
        return match.group(1).strip()
    return text
