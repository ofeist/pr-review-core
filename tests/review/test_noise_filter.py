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
            "- Timeout misconfiguration risk: timeout_seconds <= 0 can break API calls because client timeout becomes invalid.\n"
        )

        output = filter_review_markdown(raw)
        self.assertNotIn("The change from", output)
        self.assertNotIn("Installing openai dependency in CI", output)
        self.assertIn("Timeout misconfiguration risk", output)

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

    def test_filters_non_actionable_lines_from_real_openai_output_pattern(self) -> None:
        raw = (
            "## AI Review\n\n"
            "### Summary\n"
            "Reviewed 1 chunk(s). Kept 3 unique finding(s).\n\n"
            "### Findings\n"
            "- No regressions or breaking changes are introduced; all new filters are additive and maintain prior behavior.\n"
            "- The new fallback in output_normalizer.py to recover plain findings lines in sections without bullets improves robustness in parsing review markdown output.\n"
            "- Tests cover new keyword filtering and normalization paths, increasing confidence in correctness and maintainability of these improvements.\n"
        )

        output = filter_review_markdown(raw)
        self.assertIn("- No issues found.", output)
        self.assertNotIn("No regressions", output)
        self.assertNotIn("improves robustness", output)
        self.assertNotIn("Tests cover", output)

    def test_filters_non_issue_and_praise_lines_from_real_output(self) -> None:
        raw = (
            "## AI Review\n\n"
            "### Summary\n"
            "Reviewed 1 chunk(s). Kept 2 unique finding(s).\n\n"
            "### Findings\n"
            "- The fallback in output_normalizer.py to recover plain lines in a findings section is a helpful robustness improvement to handle imperfectly formatted outputs, with relevant tests confirming expected behavior.\n"
            "- There are no security, performance, or breaking changes introduced by these modifications.\n"
        )

        output = filter_review_markdown(raw)
        self.assertIn("- No issues found.", output)
        self.assertNotIn("helpful robustness improvement", output)
        self.assertNotIn("There are no security, performance, or breaking changes", output)


if __name__ == "__main__":
    unittest.main()
