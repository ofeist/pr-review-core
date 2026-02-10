# core/diff/parse_diff.py

import re
from typing import List

from core.diff.types import DiffFile, DiffHunk, Change, ChangeType


DIFF_FILE_HEADER = re.compile(r"^diff --git a/(.+?) b/(.+)$")
HUNK_HEADER = re.compile(
    r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@"
)


def parse_diff(raw_diff: str) -> List[DiffFile]:
    if not raw_diff.strip():
        return []

    files: List[DiffFile] = []
    current_file = None
    current_hunks: List[DiffHunk] = []

    current_hunk_lines = []
    hunk_meta = None

    for line in raw_diff.splitlines():
        file_match = DIFF_FILE_HEADER.match(line)
        if file_match:
            if current_file:
                if hunk_meta and current_hunk_lines:
                    current_hunks.append(_build_hunk(hunk_meta, current_hunk_lines))
                files.append(
                    DiffFile(
                        path=current_file,
                        hunks=current_hunks,
                    )
                )

            current_file = file_match.group(2)
            current_hunks = []
            current_hunk_lines = []
            hunk_meta = None
            continue

        hunk_match = HUNK_HEADER.match(line)
        if hunk_match:
            if hunk_meta and current_hunk_lines:
                current_hunks.append(_build_hunk(hunk_meta, current_hunk_lines))

            hunk_meta = (
                int(hunk_match.group(1)),
                int(hunk_match.group(2) or 1),
                int(hunk_match.group(3)),
                int(hunk_match.group(4) or 1),
            )
            current_hunk_lines = []
           continue

        if hunk_meta:
            if line.startswith("+"):
                current_hunk_lines.append(
                    Change(ChangeType.ADD, line[1:])
                )
            elif line.startswith("-"):
                current_hunk_lines.append(
                    Change(ChangeType.REMOVE, line[1:])
                )
            elif line.startswith(" "):
                current_hunk_lines.append(
                    Change(ChangeType.CONTEXT, line[1:])
                )

    if current_file:
        if hunk_meta and current_hunk_lines:
            current_hunks.append(_build_hunk(hunk_meta, current_hunk_lines))
        files.append(
            DiffFile(
                path=current_file,
                hunks=current_hunks,
            )
        )

    return files


def _build_hunk(meta, changes):
    old_start, old_len, new_start, new_len = meta
    return DiffHunk(
        old_start=old_start,
        old_length=old_len,
        new_start=new_start,
        new_length=new_len,
        changes=changes,
    )
