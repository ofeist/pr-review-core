"""Normalize model output into stable PR-comment markdown."""

import re
from typing import List


def normalize_review_markdown(raw: str) -> str:
    """Return canonical markdown with Summary and Findings sections.

    The function is defensive: empty or malformed outputs are converted
    into a safe, explicit "No issues found." structure.
    """

    text = _strip_reasoning_blocks(raw or "").strip()
    if not text:
        return _fallback_markdown()

    summary = _extract_summary(text)
    findings = _extract_findings(text)

    if not summary:
        summary = "No summary was provided by the model output."

    if not findings:
        findings = ["No issues found."]

    lines: List[str] = [
        "## AI Review",
        "",
        "### Summary",
        summary,
        "",
        "### Findings",
    ]
    lines.extend(f"- {item}" for item in findings)

    return "\n".join(lines).rstrip() + "\n"


def _extract_summary(text: str) -> str:
    section = _extract_section(text, "summary")
    if section:
        return _first_non_empty_line(section)

    for line in text.splitlines():
        candidate = line.strip()
        if not candidate:
            continue
        if candidate.startswith("#"):
            continue
        if candidate.startswith("-") or candidate.startswith("*"):
            continue
        return candidate

    return ""


def _strip_reasoning_blocks(text: str) -> str:
    """Remove visible reasoning leakage before section extraction."""

    without_complete_blocks = re.sub(
        r"<think\b[^>]*>.*?</think>",
        "",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    match = re.search(r"(?im)^\s*(?:## AI Review|### Summary)\s*$", without_complete_blocks)
    if not match:
        return without_complete_blocks

    think_match = re.search(r"<think\b[^>]*>", without_complete_blocks, flags=re.IGNORECASE)
    if think_match and think_match.start() < match.start():
        return without_complete_blocks[match.start():]

    return without_complete_blocks


def _extract_findings(text: str) -> List[str]:
    section = _extract_section(text, "findings")
    findings = _extract_bullets(section) if section else []

    if findings:
        return findings

    # Fallback: if section exists but bullets are missing, recover line items.
    if section:
        recovered = _extract_plain_findings(section)
        if recovered:
            return recovered

    # Fallback: take bullet lines from the whole output.
    findings = _extract_bullets(text)
    return findings


def _extract_section(text: str, section_name: str) -> str:
    lines = text.splitlines()
    start = None

    for idx, line in enumerate(lines):
        normalized = line.strip().lower()
        if normalized == f"### {section_name}":
            start = idx + 1
            break

    if start is None:
        return ""

    chunk: List[str] = []
    for line in lines[start:]:
        if line.strip().startswith("### "):
            break
        chunk.append(line)

    return "\n".join(chunk).strip()


def _extract_bullets(text: str) -> List[str]:
    items: List[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
        elif stripped.startswith("*"):
            items.append(stripped[1:].strip())
    return [item for item in items if item]


def _extract_plain_findings(text: str) -> List[str]:
    findings: List[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        findings.append(stripped)
    return findings


def _first_non_empty_line(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def _fallback_markdown() -> str:
    return (
        "## AI Review\n"
        "\n"
        "### Summary\n"
        "No model output was produced.\n"
        "\n"
        "### Findings\n"
        "- No issues found.\n"
    )
