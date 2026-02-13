import unittest
from pathlib import Path
from types import SimpleNamespace

from core.diff.filters import filter_diff_files
from core.diff.parse_diff import parse_diff
from core.review.adapters.openai_compat_adapter import OpenAICompatModelAdapter
from core.review.cli import build_parser
from core.review.pipeline import run_review

FIXTURES = Path(__file__).parent / "fixtures"


class ContractCompatibilityTest(unittest.TestCase):
    @staticmethod
    def _openai_compat_adapter_with_markdown(markdown: str) -> OpenAICompatModelAdapter:
        class _Responses:
            @staticmethod
            def create(**kwargs):
                del kwargs
                return SimpleNamespace(output_text=markdown)

        class _Client:
            responses = _Responses()

        return OpenAICompatModelAdapter(
            base_url="http://localhost:11434/v1",
            model="qwen2.5-coder",
            client=_Client(),
        )

    def test_cli_required_flags_are_present(self) -> None:
        parser = build_parser()
        help_text = parser.format_help()

        required_flags = [
            "--input-format",
            "--from-file",
            "--adapter",
            "--repository",
            "--base-ref",
            "--head-ref",
            "--pr-title",
            "--pr-body",
            "--max-changes-per-chunk",
            "--fallback-mode",
        ]

        for flag in required_flags:
            self.assertIn(flag, help_text)

    def test_markdown_heading_contract_order(self) -> None:
        raw = (FIXTURES / "raw_small.diff").read_text(encoding="utf-8-sig")
        files = filter_diff_files(parse_diff(raw))

        output = run_review(files, adapter_name="fake")

        expected_order = [
            "## AI Review",
            "### Summary",
            "### Intent",
            "### Change Summary",
            "### Findings",
        ]

        positions = []
        for heading in expected_order:
            pos = output.find(heading)
            self.assertGreaterEqual(pos, 0, f"Missing heading: {heading}")
            positions.append(pos)

        self.assertEqual(positions, sorted(positions), "Headings are out of order")

    def test_markdown_heading_contract_order_with_openai_compat(self) -> None:
        raw = (FIXTURES / "raw_small.diff").read_text(encoding="utf-8-sig")
        files = filter_diff_files(parse_diff(raw))
        adapter = self._openai_compat_adapter_with_markdown(
            "## AI Review\n\n### Summary\nok\n\n### Findings\n- No issues found.\n"
        )

        output = run_review(files, adapter_override=adapter)

        expected_order = [
            "## AI Review",
            "### Summary",
            "### Intent",
            "### Change Summary",
            "### Findings",
        ]
        positions = []
        for heading in expected_order:
            pos = output.find(heading)
            self.assertGreaterEqual(pos, 0, f"Missing heading: {heading}")
            positions.append(pos)
        self.assertEqual(positions, sorted(positions), "Headings are out of order")


if __name__ == "__main__":
    unittest.main()
