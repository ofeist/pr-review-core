import unittest

from core.diff.types import Change, ChangeType, DiffFile, DiffHunk
from core.review.prompt_builder import build_review_prompt


class PromptBuilderTest(unittest.TestCase):
    def test_prompt_is_deterministic_for_same_input(self) -> None:
        files = [
            DiffFile(
                path="src/auth/login.py",
                hunks=[
                    DiffHunk(
                        old_start=10,
                        old_length=2,
                        new_start=10,
                        new_length=3,
                        changes=[
                            Change(ChangeType.CONTEXT, "def login(user):"),
                            Change(ChangeType.ADD, "    if user is None:"),
                            Change(ChangeType.ADD, "        return None"),
                        ],
                    )
                ],
            )
        ]

        first = build_review_prompt(
            files,
            repository="acme/repo",
            base_ref="main",
            head_ref="feature/login-guard",
        )
        second = build_review_prompt(
            files,
            repository="acme/repo",
            base_ref="main",
            head_ref="feature/login-guard",
        )

        self.assertEqual(first, second)

    def test_prompt_contains_rubric_and_noise_controls(self) -> None:
        prompt = build_review_prompt([])

        self.assertIn("Review rubric:", prompt)
        self.assertIn("- bugs", prompt)
        self.assertIn("- security issues", prompt)
        self.assertIn("- performance risks", prompt)
        self.assertIn("- readability and maintainability", prompt)
        self.assertIn("- breaking changes", prompt)

        self.assertIn("Noise control rules:", prompt)
        self.assertIn("Do not comment on formatting-only issues.", prompt)
        self.assertIn("Do not restate obvious code changes without risk.", prompt)
        self.assertIn("Do not speculate without evidence from the diff.", prompt)

    def test_prompt_contains_explicit_no_issues_instruction(self) -> None:
        prompt = build_review_prompt([])
        self.assertIn("No issues found.", prompt)
        self.assertIn("(no changed files)", prompt)


if __name__ == "__main__":
    unittest.main()
