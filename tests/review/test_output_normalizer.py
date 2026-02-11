import unittest

from core.review.output_normalizer import normalize_review_markdown


class OutputNormalizerTest(unittest.TestCase):
    def test_empty_output_falls_back_to_safe_template(self) -> None:
        output = normalize_review_markdown("")

        self.assertIn("## AI Review", output)
        self.assertIn("### Summary", output)
        self.assertIn("### Findings", output)
        self.assertIn("No model output was produced.", output)
        self.assertIn("- No issues found.", output)

    def test_malformed_output_gets_structured(self) -> None:
        raw = "Potential null check issue near login handler"
        output = normalize_review_markdown(raw)

        self.assertIn("## AI Review", output)
        self.assertIn("### Summary", output)
        self.assertIn("Potential null check issue near login handler", output)
        self.assertIn("### Findings", output)
        self.assertIn("- No issues found.", output)

    def test_existing_sections_are_preserved_and_normalized(self) -> None:
        raw = (
            "### Summary\n"
            "Found a high-risk auth bug.\n"
            "\n"
            "### Findings\n"
            "* Missing null guard before token dereference\n"
        )
        output = normalize_review_markdown(raw)

        self.assertIn("Found a high-risk auth bug.", output)
        self.assertIn("- Missing null guard before token dereference", output)


if __name__ == "__main__":
    unittest.main()
