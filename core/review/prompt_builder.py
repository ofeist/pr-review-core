"""Deterministic prompt assembly for review generation."""

from typing import List

from core.diff.types import Change, DiffFile, DiffHunk

RUBRIC_ITEMS = [
    "bugs",
    "security issues",
    "performance risks",
    "readability and maintainability",
    "breaking changes",
]

NOISE_CONTROL_RULES = [
    "Do not comment on formatting-only issues.",
    "Do not restate obvious code changes without risk.",
    "Do not speculate without evidence from the diff.",
]


def build_review_prompt(
    files: List[DiffFile],
    *,
    repository: str = "",
    base_ref: str = "",
    head_ref: str = "",
) -> str:
    """Build deterministic prompt text from parsed diff files."""

    lines: List[str] = []
    lines.append("You are a senior software engineer performing pull-request review.")
    lines.append("Focus only on actionable, high-signal findings.")
    lines.append("")

    if repository:
        lines.append(f"Repository: {repository}")
    if base_ref or head_ref:
        lines.append(f"Comparison: {base_ref or '?'} -> {head_ref or '?'}")
    if repository or base_ref or head_ref:
        lines.append("")

    lines.append("Review rubric:")
    for item in RUBRIC_ITEMS:
        lines.append(f"- {item}")
    lines.append("")

    lines.append("Noise control rules:")
    for rule in NOISE_CONTROL_RULES:
        lines.append(f"- {rule}")
    lines.append("")

    lines.append("Output requirements:")
    lines.append("- Return markdown suitable for a PR comment.")
    lines.append("- Include a concise summary and concrete findings.")
    lines.append("- If no issues are found, say 'No issues found.' explicitly.")
    lines.append("")

    lines.append("Parsed diff input:")
    if not files:
        lines.append("(no changed files)")
    else:
        for file_obj in _sort_files(files):
            lines.append(f"FILE: {file_obj.path}")
            for hunk in _sort_hunks(file_obj.hunks):
                lines.append(
                    f"HUNK: -{hunk.old_start},{hunk.old_length} +{hunk.new_start},{hunk.new_length}"
                )
                for change in hunk.changes:
                    lines.append(_format_change(change))
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _sort_files(files: List[DiffFile]) -> List[DiffFile]:
    return sorted(files, key=lambda file_obj: file_obj.path)


def _sort_hunks(hunks: List[DiffHunk]) -> List[DiffHunk]:
    return sorted(hunks, key=lambda hunk: (hunk.new_start, hunk.old_start))


def _format_change(change: Change) -> str:
    if change.type.value == "add":
        return f"+ {change.content}"
    if change.type.value == "remove":
        return f"- {change.content}"
    return f"  {change.content}"
