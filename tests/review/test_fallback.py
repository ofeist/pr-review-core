import unittest
from dataclasses import dataclass, field
from typing import List

from core.diff.types import Change, ChangeType, DiffFile, DiffHunk
from core.review.pipeline import run_review


@dataclass
class FailFullThenSucceedAdapter:
    """Fails first call (full review), succeeds in fallback calls."""

    name: str = "fail-then-ok"
    calls: List[str] = field(default_factory=list)

    def generate_review(self, prompt: str) -> str:
        self.calls.append(prompt)
        if len(self.calls) == 1:
            raise RuntimeError("simulated full review failure")
        return (
            "## AI Review\n\n"
            "### Summary\n"
            "Fallback review chunk completed.\n\n"
            "### Findings\n"
            "- Missing auth guard before token use.\n"
        )


class FallbackPipelineTest(unittest.TestCase):
    def _files(self) -> List[DiffFile]:
        return [
            DiffFile(
                path="src/a.py",
                hunks=[
                    DiffHunk(
                        old_start=1,
                        old_length=1,
                        new_start=1,
                        new_length=2,
                        changes=[
                            Change(ChangeType.CONTEXT, "def a():"),
                            Change(ChangeType.ADD, "    return 'a'"),
                        ],
                    )
                ],
            ),
            DiffFile(
                path="src/b.py",
                hunks=[
                    DiffHunk(
                        old_start=1,
                        old_length=1,
                        new_start=1,
                        new_length=2,
                        changes=[
                            Change(ChangeType.CONTEXT, "def b():"),
                            Change(ChangeType.ADD, "    return 'b'"),
                        ],
                    )
                ],
            ),
        ]

    def test_fallback_runs_per_file_when_full_review_fails(self) -> None:
        adapter = FailFullThenSucceedAdapter()

        output = run_review(
            self._files(),
            adapter_override=adapter,
            max_changes_per_chunk=50,
        )

        self.assertIn("## AI Review", output)
        self.assertIn("### Summary", output)
        self.assertIn("### Findings", output)
        self.assertIn("Reviewed 2 chunk(s).", output)
        self.assertIn("Missing auth guard before token use.", output)

        # 1 full attempt + 2 per-file fallback attempts
        self.assertEqual(len(adapter.calls), 3)

    def test_failure_reason_not_leaked_in_output(self) -> None:
        adapter = FailFullThenSucceedAdapter()

        output = run_review(self._files(), adapter_override=adapter)

        self.assertNotIn("simulated full review failure", output)
        self.assertNotIn("Traceback", output)


if __name__ == "__main__":
    unittest.main()
