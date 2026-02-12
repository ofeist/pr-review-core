"""Post-filter for low-signal review findings in markdown output."""

import re
from typing import List


RISK_KEYWORDS = {
    "bug",
    "security",
    "vulnerability",
    "race",
    "deadlock",
    "leak",
    "exception",
    "null",
    "none",
    "crash",
    "panic",
    "overflow",
    "injection",
    "xss",
    "sql",
    "auth",
    "token",
    "permission",
    "performance",
    "latency",
    "slow",
    "timeout",
    "breaking",
    "regression",
    "data loss",
}

STYLE_KEYWORDS = {
    "formatting",
    "style",
    "whitespace",
    "indent",
    "indentation",
    "semicolon",
    "quote style",
    "naming convention",
    "lint",
    "pep8",
    "prettier",
}

PRAISE_KEYWORDS = {
    "useful heuristic",
    "good guard",
    "good improvement",
    "improves robustness",
    "maintainable and readable",
    "maintainability",
    "well-named",
    "clear helper functions",
    "valuable",
    "tests cover",
    "increasing confidence",
    "confidence in correctness",
}

META_KEYWORDS = {
    "ci",
    "pipeline",
    "workflow",
    "github actions",
    "pip",
    "dependency",
    "dependencies",
    "installing",
    "test coverage",
    "regression test",
    "unit test",
    "test verifying",
    "valuable for preventing regressions",
    "consider caching",
}

CI_META_KEYWORDS = {
    "continuous integration",
    "pipeline",
    "workflow",
    "github actions",
    "dependency",
    "dependencies",
    "installing",
    "pip",
    "cache",
    "caching",
}

SPECULATIVE_MARKERS = {
    "might",
    "maybe",
    "possibly",
    "could",
    "probably",
    "it seems",
    "appears",
    "i think",
}

EVIDENCE_MARKERS = {
    "because",
    "due to",
    "for example",
    "evidence",
    "in ",
    "at line",
    "when",
    "where",
}


def filter_review_markdown(markdown: str) -> str:
    """Filter low-signal findings and return canonical markdown.

    Assumes input is normalized markdown with Summary/Findings sections.
    """

    lines = markdown.splitlines()
    summary_lines, finding_lines = _split_sections(lines)

    findings = [_strip_bullet(line) for line in finding_lines if _is_bullet(line)]
    filtered = _filter_findings(findings)

    out: List[str] = ["## AI Review", "", "### Summary"]
    if summary_lines:
        out.extend(summary_lines)
    else:
        out.append("No summary was provided.")

    out.extend(["", "### Findings"])
    if filtered:
        out.extend([f"- {item}" for item in filtered])
    else:
        out.append("- No issues found.")

    return "\n".join(out).rstrip() + "\n"


def _split_sections(lines: List[str]) -> tuple[List[str], List[str]]:
    summary: List[str] = []
    findings: List[str] = []
    mode = ""

    for raw in lines:
        line = raw.rstrip("\n")
        stripped = line.strip()
        if stripped.lower() == "### summary":
            mode = "summary"
            continue
        if stripped.lower() == "### findings":
            mode = "findings"
            continue
        if stripped.startswith("### "):
            mode = ""
            continue

        if mode == "summary" and stripped:
            summary.append(stripped)
        elif mode == "findings" and stripped:
            findings.append(stripped)

    return summary, findings


def _filter_findings(findings: List[str]) -> List[str]:
    kept: List[str] = []
    seen: set[str] = set()

    for finding in findings:
        text = finding.strip()
        if not text:
            continue
        if _is_style_only(text):
            continue
        if _is_obvious_restatement(text):
            continue
        if _is_meta_comment(text):
            continue
        if _is_ci_meta_comment(text):
            continue
        if _is_incomplete_fragment(text):
            continue
        if _is_non_actionable_affirmation(text):
            continue
        if _is_non_actionable_without_risk_evidence(text):
            continue
        if _is_speculative_without_evidence(text):
            continue

        key = _dedupe_key(text)
        if key in seen:
            continue

        seen.add(key)
        kept.append(text)

    return kept


def _is_bullet(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("- ") or stripped.startswith("* ")


def _strip_bullet(line: str) -> str:
    stripped = line.strip()
    if stripped.startswith("- ") or stripped.startswith("* "):
        return stripped[2:].strip()
    return stripped


def _contains_any(text: str, markers: set[str]) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in markers)


def _contains_risk_signal(text: str) -> bool:
    return _contains_any(text, RISK_KEYWORDS)


def _is_style_only(text: str) -> bool:
    return _contains_any(text, STYLE_KEYWORDS) and not _contains_risk_signal(text)


def _is_obvious_restatement(text: str) -> bool:
    lowered = text.lower()
    restatement_patterns = (
        "the change from",
        "this change adds",
        "this change removes",
        "line was added",
        "line was removed",
        "code was changed",
        "this file was modified",
    )
    return any(p in lowered for p in restatement_patterns) and not _contains_risk_signal(text)


def _is_speculative_without_evidence(text: str) -> bool:
    return _contains_any(text, SPECULATIVE_MARKERS) and not _contains_any(text, EVIDENCE_MARKERS)


def _is_meta_comment(text: str) -> bool:
    return _contains_any(text, META_KEYWORDS) and not _contains_risk_signal(text)


def _is_ci_meta_comment(text: str) -> bool:
    return _contains_any(text, CI_META_KEYWORDS)


def _is_incomplete_fragment(text: str) -> bool:
    lowered = text.lower().rstrip()
    incomplete_suffixes = (" to", " from", " because", " due to", " by", " with")
    return lowered.endswith(incomplete_suffixes)


def _is_non_actionable_affirmation(text: str) -> bool:
    lowered = text.lower().strip()
    if lowered.startswith("no ") and "issue" in lowered:
        return True
    if "no regressions" in lowered or "no breaking changes" in lowered:
        return True
    return _contains_any(text, PRAISE_KEYWORDS)


def _has_evidence_signal(text: str) -> bool:
    lowered = text.lower()
    if _contains_any(text, EVIDENCE_MARKERS):
        return True
    if " in " in lowered and (".py" in lowered or ".ts" in lowered or ".js" in lowered):
        return True
    return False


def _is_non_actionable_without_risk_evidence(text: str) -> bool:
    # Keep findings that have either concrete risk words or evidence anchors.
    return not _contains_risk_signal(text) and not _has_evidence_signal(text)


def _dedupe_key(text: str) -> str:
    lowered = text.lower().strip()
    lowered = re.sub(r"[^a-z0-9\s]", "", lowered)
    lowered = re.sub(r"\s+", " ", lowered)
    return lowered
