import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

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

    def test_filters_issue_claim_without_evidence(self) -> None:
        raw = (
            "## AI Review\n\n"
            "### Summary\n"
            "One possible issue.\n\n"
            "### Findings\n"
            "- Potential SQL injection risk in query builder.\n"
        )

        output = filter_review_markdown(raw)
        self.assertIn("- No issues found.", output)
        self.assertNotIn("Potential SQL injection risk", output)

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

    def test_filters_backward_compatibility_affirmation(self) -> None:
        raw = (
            "## AI Review\n\n"
            "### Summary\n"
            "Reviewed 1 chunk(s). Kept 1 unique finding(s).\n\n"
            "### Findings\n"
            "- The changes are non-breaking and backward compatible, only enhancing filtering and normalization behavior.\n"
        )

        output = filter_review_markdown(raw)
        self.assertIn("- No issues found.", output)
        self.assertNotIn("non-breaking and backward compatible", output)

    def test_filters_meta_quality_statements_from_real_output(self) -> None:
        raw = (
            "## AI Review\n\n"
            "### Summary\n"
            "Reviewed 1 chunk(s). Kept 3 unique finding(s).\n\n"
            "### Findings\n"
            "- The added filtering helper _is_non_actionable_without_risk_evidence() ensures only comments with risk signals or evidence remain, which reduces false positives in findings.\n"
            "- The overall changes maintain backward compatibility as they only add filtering rules and fallback logic without modifying existing public interfaces or semantics.\n"
            "- No security, performance, or breaking change concerns were found in this diff.\n"
        )

        output = filter_review_markdown(raw)
        self.assertIn("- No issues found.", output)
        self.assertNotIn("ensures only comments", output)
        self.assertNotIn("maintain backward compatibility", output)
        self.assertNotIn("No security, performance, or breaking change concerns", output)

    def test_filters_positive_quality_findings_from_latest_real_output(self) -> None:
        raw = (
            "## AI Review\n\n"
            "### Summary\n"
            "Reviewed 1 chunk(s). Kept 2 unique finding(s).\n\n"
            "### Findings\n"
            "- The new build_change_summary function correctly produces a concise and deterministic summary of changed files, additions, removals, and hunks capped by max_files, which enhances review clarity without causing breaking changes.\n"
            "- The fallback logic in output_normalizer.py to recover plain lines as bullet findings inside the findings section addresses imperfect formatting gracefully, improving resilience to malformed model outputs.\n"
        )

        output = filter_review_markdown(raw)
        self.assertIn("- No issues found.", output)
        self.assertNotIn("correctly produces", output)
        self.assertNotIn("improving resilience", output)

    def test_filters_negated_breaking_statement_from_real_output(self) -> None:
        raw = (
            "## AI Review\n\n"
            "### Summary\n"
            "Reviewed 1 chunk(s). Kept 1 unique finding(s).\n\n"
            "### Findings\n"
            "- The new build_change_summary function and its integration enhance readability and add useful neutral context about changed files and counts without breaking compatibility.\n"
        )

        output = filter_review_markdown(raw)
        self.assertIn("- No issues found.", output)
        self.assertNotIn("without breaking compatibility", output)

    def test_filters_test_coverage_affirmation_from_real_output(self) -> None:
        raw = (
            "## AI Review\n\n"
            "### Summary\n"
            "Reviewed 1 chunk(s). Kept 1 unique finding(s).\n\n"
            "### Findings\n"
            "- Comprehensive test coverage across filtering and normalization modules ensures the new features behave as intended and guard against regressions.\n"
        )

        output = filter_review_markdown(raw)
        self.assertIn("- No issues found.", output)
        self.assertNotIn("Comprehensive test coverage", output)

    def test_filters_generic_review_commentary_from_latest_output(self) -> None:
        raw = (
            "## AI Review\n\n"
            "### Summary\n"
            "Reviewed 1 chunk(s).\n\n"
            "### Findings\n"
            "- generate_review catches all exceptions from the client call and wraps them as AdapterRuntimeError, which is good defensive error handling. However, the catch-all may mask potentially critical exceptions (e.g., programming errors). Consider limiting the catch to expected client or network exceptions if possible.\n"
            "- client is stored as an instance attribute after initialization, preventing unnecessary re-instantiations, which is a good performance optimization.\n"
            "- Documentation in ops/phase-4-1-thin-slices.md is updated accurately to reflect slice completion with evidence, supporting traceability of development progress.\n"
        )

        output = filter_review_markdown(raw)
        self.assertIn("- No issues found.", output)
        self.assertNotIn("good defensive error handling", output)
        self.assertNotIn("good performance optimization", output)
        self.assertNotIn("traceability of development progress", output)

    def test_keeps_hardcoded_secret_finding_from_real_output(self) -> None:
        raw = (
            "## AI Review\n\n"
            "### Summary\n"
            "This PR modifies the Jenkins stage and introduces a hardcoded secret.\n\n"
            "### Findings\n"
            '- **Security Issue**: A hardcoded secret (`secret = "21423agdfsagfsadg55525"`) has been added directly in the script; this must be removed immediately and managed via Jenkins Credentials or environment variables to prevent exposure in version control.\n'
            "- **Readability/Maintainability**: The variable `dummyVariable` appears to be debug code or a placeholder with no functional purpose and should be removed before merging.\n"
            "- **Configuration Risk**: The comment regarding `OPENAI_COMPAT_MAX_OUTPUT_TOKENS` was moved to the new line but now describes a variable that was present in the previous version; ensure the comment accurately reflects the current context of why the value was reduced from 20000 to 15000.\n"
        )

        output = filter_review_markdown(raw)
        self.assertIn("hardcoded secret", output)
        self.assertNotIn("- No issues found.", output)

    def test_does_not_treat_generic_new_line_phrase_as_evidence(self) -> None:
        raw = (
            "## AI Review\n\n"
            "### Summary\n"
            "This PR changes a config comment.\n\n"
            "### Findings\n"
            "- **Configuration Risk**: The comment regarding `OPENAI_COMPAT_MAX_OUTPUT_TOKENS` was moved to the new line but now describes a variable that was present in the previous version; ensure the comment accurately reflects the current context of why the value was reduced from 20000 to 15000.\n"
        )

        output = filter_review_markdown(raw)
        self.assertIn("- No issues found.", output)
        self.assertNotIn("OPENAI_COMPAT_MAX_OUTPUT_TOKENS", output)

    def test_keeps_commented_out_flag_logic_finding(self) -> None:
        raw = (
            "## AI Review\n\n"
            "### Summary\n"
            "This PR claims to disable thinking but leaves the flag disabled in code.\n\n"
            "### Findings\n"
            '- **Logic Error:** The PR title states "disable thinking", but the corresponding environment variable `OPENAI_COMPAT_DISABLE_THINKING` is commented out (`//`), meaning the setting will not actually be applied.\n'
        )

        output = filter_review_markdown(raw)
        self.assertIn("commented out", output)
        self.assertNotIn("- No issues found.", output)


if __name__ == "__main__":
    unittest.main()
