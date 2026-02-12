"""Review-layer canonical types.

These dataclasses represent review inputs/outputs and are intentionally
separate from diff parsing types.
"""

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import List, Optional


class FindingCategory(str, Enum):
    BUG = "bug"
    SECURITY = "security"
    PERFORMANCE = "performance"
    READABILITY = "readability"
    BREAKING_CHANGE = "breaking_change"


class FindingSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class ReviewRequest:
    """Input payload for review generation."""

    repository: str
    base_ref: str
    head_ref: str
    diff_text: Optional[str] = None


@dataclass(frozen=True)
class ReviewFinding:
    """One issue identified by the review layer."""

    category: FindingCategory
    severity: FindingSeverity
    path: str
    summary: str
    evidence: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass(frozen=True)
class ReviewSummary:
    """Aggregate counts and high-level verdict for a review result."""

    total_findings: int
    critical_findings: int
    high_findings: int
    medium_findings: int
    low_findings: int
    no_issues_found: bool


@dataclass(frozen=True)
class ReviewResult:
    """Final review output contract consumed by downstream adapters."""

    summary: ReviewSummary
    findings: List[ReviewFinding] = field(default_factory=list)
    markdown: str = ""


def to_dict(value: object) -> dict:
    """Serialize a review dataclass object into a plain dict."""

    return asdict(value)
