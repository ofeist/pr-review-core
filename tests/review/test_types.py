import json
import unittest
from dataclasses import asdict

from core.review.types import (
    FindingCategory,
    FindingSeverity,
    ReviewFinding,
    ReviewRequest,
    ReviewResult,
    ReviewSummary,
)


class ReviewTypesTest(unittest.TestCase):
    def test_imports_and_instantiation(self) -> None:
        req = ReviewRequest(
            repository="acme/repo",
            base_ref="main",
            head_ref="feature/login",
            diff_text="diff --git a/a.py b/a.py",
        )
        finding = ReviewFinding(
            category=FindingCategory.BUG,
            severity=FindingSeverity.HIGH,
            path="src/auth/login.py",
            summary="Possible null dereference before guard.",
            evidence="`user.email` used before checking `user is None`.",
            suggestion="Add early return when user is None.",
        )
        summary = ReviewSummary(
            total_findings=1,
            critical_findings=0,
            high_findings=1,
            medium_findings=0,
            low_findings=0,
            no_issues_found=False,
        )
        result = ReviewResult(summary=summary, findings=[finding], markdown="## Review")

        self.assertEqual(req.repository, "acme/repo")
        self.assertEqual(result.summary.total_findings, 1)

    def test_asdict_shape(self) -> None:
        finding = ReviewFinding(
            category=FindingCategory.SECURITY,
            severity=FindingSeverity.CRITICAL,
            path="src/api/auth.py",
            summary="Token verification bypass risk.",
        )
        payload = asdict(finding)

        self.assertEqual(payload["category"], "security")
        self.assertEqual(payload["severity"], "critical")
        self.assertEqual(payload["path"], "src/api/auth.py")

    def test_json_serializable(self) -> None:
        summary = ReviewSummary(
            total_findings=0,
            critical_findings=0,
            high_findings=0,
            medium_findings=0,
            low_findings=0,
            no_issues_found=True,
        )
        result = ReviewResult(summary=summary, findings=[], markdown="No issues found.")

        serialized = json.dumps(asdict(result))
        self.assertIn('"no_issues_found": true', serialized)


if __name__ == "__main__":
    unittest.main()
