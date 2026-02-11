import unittest
from pathlib import Path

from core.diff.filters import filter_diff_files
from core.diff.parse_diff import parse_diff
from core.review.noise_filter import filter_review_markdown
from core.review.output_normalizer import normalize_review_markdown
from core.review.pipeline import run_review

FIXTURES = Path(__file__).parent / "fixtures"
SNAPSHOTS = Path(__file__).parent / "snapshots"


class MarkdownSnapshotTest(unittest.TestCase):
    def _read_fixture(self, name: str) -> str:
        return (FIXTURES / name).read_text(encoding="utf-8-sig")

    def _read_snapshot(self, name: str) -> str:
        return (SNAPSHOTS / name).read_text(encoding="utf-8-sig")

    def test_snapshot_fake_review_from_raw_small(self) -> None:
        raw = self._read_fixture("raw_small.diff")
        files = filter_diff_files(parse_diff(raw))

        output = run_review(files, adapter_name="fake")
        expected = self._read_snapshot("fake_review_raw_small.md")

        self.assertEqual(output, expected)

    def test_snapshot_normalize_empty_output(self) -> None:
        empty = self._read_fixture("model_empty_output.md")
        output = normalize_review_markdown(empty)
        expected = self._read_snapshot("normalized_empty.md")

        self.assertEqual(output, expected)

    def test_shape_for_noisy_model_output_after_filtering(self) -> None:
        noisy = self._read_fixture("model_noisy_output.md")
        normalized = normalize_review_markdown(noisy)
        filtered = filter_review_markdown(normalized)

        self.assertTrue(filtered.startswith("## AI Review\n\n### Summary\n"))
        self.assertIn("\n### Findings\n", filtered)


if __name__ == "__main__":
    unittest.main()

