import unittest

from core.review.noise_filter import filter_review_markdown


class NoiseFilterTest(unittest.TestCase):
    def test_filters_style_only_findings(self) -> None:
        raw = (
            "## AI Review\n\n"
            "### Summary\n"
            "Quick review.\n\n"
            "### Findings\n"
            "- Formatting looks inconsistent in this file.\n"
            "- Indentation style should follow team convention.\n"
        )

        output = filter_review_markdown(raw)
        self.assertIn("### Findings", output)
        self.assertIn("- No issues found.", output)

    def test_filters_speculative_without_evidence(self) -> None:
        raw = (
            "## AI Review\n\n"
            "### Summary\n"
            "Potential concern.\n\n"
            "### Findings\n"
            "- This might be a problem.\n"
        )

        output = filter_review_markdown(raw)
        self.assertIn("- No issues found.", output)

    def test_deduplicates_near_duplicate_findings(self) -> None:
        raw = (
            "## AI Review\n\n"
            "### Summary\n"
            "Review done.\n\n"
            "### Findings\n"
            "- Missing auth guard before token use.\n"
            "- Missing auth guard before token use!\n"
        )

        output = filter_review_markdown(raw)
        self.assertEqual(output.count("Missing auth guard before token use"), 1)

    def test_keeps_high_signal_finding(self) -> None:
        raw = (
            "## AI Review\n\n"
            "### Summary\n"
            "One high-risk issue found.\n\n"
            "### Findings\n"
            "- Null dereference risk in auth path because token is accessed before user None-check.\n"
        )

        output = filter_review_markdown(raw)
        self.assertIn("Null dereference risk", output)
        self.assertNotIn("- No issues found.", output)

    def test_filters_meta_and_incomplete_fragment_findings(self) -> None:
        raw = (
            "## AI Review\n\n"
            "### Summary\n"
            "Review done.\n\n"
            "### Findings\n"
            "- The change from model = os.getenv(...) to\n"
            "- Installing openai dependency in CI each run might slow down workflows.\n"
            "- Introducing a check for timeout_seconds <= 0 improves robustness because it avoids invalid values.\n"
        )

        output = filter_review_markdown(raw)
        self.assertNotIn("The change from", output)
        self.assertNotIn("Installing openai dependency in CI", output)
        self.assertIn("timeout_seconds <= 0", output)

    def test_filters_non_actionable_affirmations(self) -> None:
        raw = (
            "## AI Review\n\n"
            "### Summary\n"
            "Review done.\n\n"
            "### Findings\n"
            "- No security issues, performance regressions, or breaking changes are evident.\n"
            "- The new filtering logic remains maintainable and readable by using clear helper functions.\n"
            "- Null dereference risk because token is used before user check.\n"
        )

        output = filter_review_markdown(raw)
        self.assertNotIn("No security issues", output)
        self.assertNotIn("maintainable and readable", output)
        self.assertIn("Null dereference risk", output)


if __name__ == "__main__":
    unittest.main()
