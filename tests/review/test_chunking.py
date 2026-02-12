import unittest

from core.diff.types import Change, ChangeType, DiffFile, DiffHunk
from core.review.chunking import build_intent_summary, chunk_diff_files, merge_chunk_markdowns
from core.review.pipeline import run_review


class ChunkingBoundaryTest(unittest.TestCase):
    def test_chunk_diff_files_respects_max_changes(self) -> None:
        files = [
            DiffFile(
                path="src/a.py",
                hunks=[
                    DiffHunk(
                        old_start=1,
                        old_length=3,
                        new_start=1,
                        new_length=3,
                        changes=[
                            Change(ChangeType.CONTEXT, "a"),
                            Change(ChangeType.ADD, "b"),
                            Change(ChangeType.ADD, "c"),
                        ],
                    ),
                    DiffHunk(
                        old_start=10,
                        old_length=3,
                        new_start=10,
                        new_length=3,
                        changes=[
                            Change(ChangeType.CONTEXT, "d"),
                            Change(ChangeType.ADD, "e"),
                            Change(ChangeType.ADD, "f"),
                        ],
                    ),
                ],
            )
        ]

        chunks = chunk_diff_files(files, max_changes_per_chunk=4)

        self.assertEqual(len(chunks), 2)
        for chunk in chunks:
            change_count = sum(len(h.changes) for f in chunk for h in f.hunks)
            self.assertLessEqual(change_count, 4)

    def test_chunk_diff_files_splits_large_hunk(self) -> None:
        big_hunk = DiffHunk(
            old_start=1,
            old_length=7,
            new_start=1,
            new_length=7,
            changes=[
                Change(ChangeType.CONTEXT, "l1"),
                Change(ChangeType.ADD, "l2"),
                Change(ChangeType.ADD, "l3"),
                Change(ChangeType.ADD, "l4"),
                Change(ChangeType.ADD, "l5"),
                Change(ChangeType.ADD, "l6"),
                Change(ChangeType.ADD, "l7"),
            ],
        )
        files = [DiffFile(path="src/b.py", hunks=[big_hunk])]

        chunks = chunk_diff_files(files, max_changes_per_chunk=3)

        self.assertEqual(len(chunks), 3)
        total = sum(len(h.changes) for c in chunks for f in c for h in f.hunks)
        self.assertEqual(total, 7)


class ChunkMergeTest(unittest.TestCase):
    def test_merge_chunk_markdowns_dedupes_and_is_deterministic(self) -> None:
        m1 = (
            "## AI Review\n\n"
            "### Summary\n"
            "Chunk one.\n\n"
            "### Findings\n"
            "- Missing auth guard before token use.\n"
            "- No issues found.\n"
        )
        m2 = (
            "## AI Review\n\n"
            "### Summary\n"
            "Chunk two.\n\n"
            "### Findings\n"
            "- Missing auth guard before token use!\n"
            "- Potential performance regression in loop due to repeated DB call.\n"
        )

        merged_first = merge_chunk_markdowns([m1, m2])
        merged_second = merge_chunk_markdowns([m1, m2])

        self.assertEqual(merged_first, merged_second)
        self.assertIn("Kept 2 unique finding(s).", merged_first)
        self.assertIn("### Intent", merged_first)
        self.assertIn("Intent not provided.", merged_first)
        self.assertEqual(merged_first.count("Missing auth guard before token use"), 1)

    def test_run_review_uses_chunking_and_merges(self) -> None:
        files = [
            DiffFile(
                path="src/c.py",
                hunks=[
                    DiffHunk(
                        old_start=1,
                        old_length=5,
                        new_start=1,
                        new_length=5,
                        changes=[
                            Change(ChangeType.CONTEXT, "a"),
                            Change(ChangeType.CONTEXT, "b"),
                            Change(ChangeType.ADD, "c"),
                            Change(ChangeType.ADD, "d"),
                            Change(ChangeType.ADD, "e"),
                        ],
                    )
                ],
            )
        ]

        output = run_review(files, adapter_name="fake", max_changes_per_chunk=2)
        self.assertIn("Reviewed 1 chunk(s).", output)
        self.assertIn("### Findings", output)


class IntentSummaryTest(unittest.TestCase):
    def test_prefers_clean_title_for_intent(self) -> None:
        intent = build_intent_summary(
            pr_title="Add PR intent section to AI review output.",
            pr_body="- details\n- more details\n",
        )
        self.assertEqual(intent, "Add PR intent section to AI review output.")

    def test_uses_clean_body_when_title_missing(self) -> None:
        intent = build_intent_summary(
            pr_title="",
            pr_body=(
                "### What was implemented\n"
                "- Added PR metadata flow end-to-end.\n"
                "- Added Intent section.\n"
            ),
        )
        self.assertEqual(intent, "Added PR metadata flow end-to-end.")

    def test_fallback_when_both_missing(self) -> None:
        self.assertEqual(build_intent_summary("", ""), "Intent not provided.")

    def test_strips_what_was_implemented_heading_prefix(self) -> None:
        intent = build_intent_summary(
            pr_title="What was implemented - Added PR metadata flow end-to-end: - ",
            pr_body="",
        )
        self.assertEqual(intent, "Added PR metadata flow end-to-end")

    def test_strips_heading_list_spillover_tail(self) -> None:
        intent = build_intent_summary(
            pr_title="Added PR metadata flow end-to-end: - workflow -> CLI -> pipeline -> prompt",
            pr_body="",
        )
        self.assertEqual(intent, "Added PR metadata flow end-to-end")

    def test_prefers_body_when_title_looks_truncated(self) -> None:
        intent = build_intent_summary(
            pr_title="docs(validation): complete phase-4 slice-8 exit checklist and handoff…",
            pr_body="docs(validation): complete phase-4 slice-8 exit checklist and handoff notes.",
        )
        self.assertEqual(
            intent,
            "docs(validation): complete phase-4 slice-8 exit checklist and handoff notes.",
        )


if __name__ == "__main__":
    unittest.main()

