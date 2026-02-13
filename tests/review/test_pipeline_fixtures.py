import json
import unittest
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

from core.diff.filters import filter_diff_files
from core.diff.parse_diff import parse_diff
from core.review.adapters.openai_compat_adapter import OpenAICompatModelAdapter
from core.review import cli
from core.review.chunking import chunk_diff_files
from core.review.pipeline import run_review

FIXTURES = Path(__file__).parent / "fixtures"


@dataclass
class AlwaysFailAdapter:
    name: str = "always-fail"

    def generate_review(self, prompt: str) -> str:
        raise RuntimeError("simulated adapter failure")


class PipelineFixtureRegressionTest(unittest.TestCase):
    def _read(self, name: str) -> str:
        return (FIXTURES / name).read_text(encoding="utf-8-sig")

    def test_raw_small_fixture_end_to_end(self) -> None:
        raw = self._read("raw_small.diff")
        files = filter_diff_files(parse_diff(raw))

        output = run_review(files, adapter_name="fake")

        self.assertIn("## AI Review", output)
        self.assertIn("### Summary", output)
        self.assertIn("### Intent", output)
        self.assertIn("### Findings", output)
        self.assertIn("No issues found.", output)

    def test_raw_large_fixture_chunking_boundary(self) -> None:
        raw = self._read("raw_large.diff")
        files = filter_diff_files(parse_diff(raw))

        chunks = chunk_diff_files(files, max_changes_per_chunk=8)

        self.assertGreater(len(chunks), 1)
        for chunk in chunks:
            count = sum(len(h.changes) for f in chunk for h in f.hunks)
            self.assertLessEqual(count, 8)

    def test_parsed_small_json_fixture(self) -> None:
        parsed = json.loads(self._read("parsed_small.json"))
        files = cli._files_from_json(parsed)

        output = run_review(files, adapter_name="fake")
        self.assertIn("## AI Review", output)

    def test_empty_input_is_recoverable_error_in_cli(self) -> None:
        code = cli.main(["--input-format", "raw", "--from-file", str(FIXTURES / "model_empty_output.md")])
        # This fixture is not a raw diff, so parse yields no files but still valid review path.
        # Ensure command is stable and non-fatal.
        self.assertIn(code, (0, 1))

    def test_malformed_parsed_json_is_recoverable(self) -> None:
        code = cli.main(
            [
                "--input-format",
                "parsed-json",
                "--from-file",
                str(FIXTURES / "parsed_malformed.json"),
            ]
        )
        self.assertEqual(code, 1)

    def test_adapter_error_path_with_fallback_disabled_raises(self) -> None:
        raw = self._read("raw_small.diff")
        files = filter_diff_files(parse_diff(raw))

        with self.assertRaises(RuntimeError):
            run_review(
                files,
                adapter_override=AlwaysFailAdapter(),
                fallback_enabled=False,
            )

    def test_adapter_error_path_with_fallback_enabled_returns_safe_output(self) -> None:
        raw = self._read("raw_small.diff")
        files = filter_diff_files(parse_diff(raw))

        output = run_review(
            files,
            adapter_override=AlwaysFailAdapter(),
            fallback_enabled=True,
            max_changes_per_chunk=4,
        )

        self.assertIn("## AI Review", output)
        self.assertIn("Review could not be generated", output)
        self.assertIn("No issues found.", output)

    def test_openai_compat_adapter_on_fixture_path(self) -> None:
        raw = self._read("raw_small.diff")
        files = filter_diff_files(parse_diff(raw))

        class _Responses:
            @staticmethod
            def create(**kwargs):
                del kwargs
                return SimpleNamespace(output_text="## AI Review\n\n### Summary\ncompat-ok")

        class _Client:
            responses = _Responses()

        adapter = OpenAICompatModelAdapter(
            base_url="http://localhost:11434/v1",
            model="qwen2.5-coder",
            client=_Client(),
        )
        output = run_review(files, adapter_override=adapter)
        self.assertIn("## AI Review", output)
        self.assertIn("### Summary", output)
        self.assertIn("### Intent", output)
        self.assertIn("### Findings", output)


if __name__ == "__main__":
    unittest.main()

