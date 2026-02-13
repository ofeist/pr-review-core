import os
import unittest
from unittest.mock import patch

from core.diff.types import Change, ChangeType, DiffFile, DiffHunk
from core.review.adapters.fake import FakeModelAdapter
from core.review.pipeline import get_adapter, run_review


class FakeAdapterContractTest(unittest.TestCase):
    def test_fake_adapter_has_contract_shape(self) -> None:
        adapter = FakeModelAdapter()
        self.assertEqual(adapter.name, "fake")
        output = adapter.generate_review("test prompt")
        self.assertIsInstance(output, str)
        self.assertIn("## AI Review", output)


class PipelineSmokeTest(unittest.TestCase):
    def test_get_adapter_returns_fake(self) -> None:
        adapter = get_adapter("fake")
        self.assertEqual(adapter.name, "fake")

    def test_get_adapter_returns_openai_compat_when_env_configured(self) -> None:
        with patch.dict(
            os.environ,
            {
                "OPENAI_COMPAT_BASE_URL": "http://localhost:11434/v1",
                "OPENAI_COMPAT_MODEL": "qwen2.5-coder",
            },
            clear=False,
        ):
            adapter = get_adapter("openai-compat")
        self.assertEqual(adapter.name, "openai-compat")

    def test_unknown_adapter_lists_openai_compat_when_available(self) -> None:
        with patch.dict(
            os.environ,
            {
                "OPENAI_COMPAT_BASE_URL": "http://localhost:11434/v1",
                "OPENAI_COMPAT_MODEL": "qwen2.5-coder",
            },
            clear=False,
        ):
            with self.assertRaises(ValueError) as ctx:
                get_adapter("does-not-exist")
        message = str(ctx.exception)
        self.assertIn("Known adapters:", message)
        self.assertIn("fake", message)
        self.assertIn("openai-compat", message)

    def test_get_adapter_returns_ollama_when_env_configured(self) -> None:
        with patch.dict(
            os.environ,
            {
                "OLLAMA_BASE_URL": "http://localhost:11434",
                "OLLAMA_MODEL": "qwen3:32b",
            },
            clear=False,
        ):
            adapter = get_adapter("ollama")
        self.assertEqual(adapter.name, "ollama")

    def test_unknown_adapter_lists_ollama_when_available(self) -> None:
        with patch.dict(
            os.environ,
            {
                "OLLAMA_BASE_URL": "http://localhost:11434",
                "OLLAMA_MODEL": "qwen3:32b",
            },
            clear=False,
        ):
            with self.assertRaises(ValueError) as ctx:
                get_adapter("does-not-exist")
        message = str(ctx.exception)
        self.assertIn("Known adapters:", message)
        self.assertIn("fake", message)
        self.assertIn("ollama", message)

    def test_run_review_fake_adapter_end_to_end(self) -> None:
        files = [
            DiffFile(
                path="src/app.py",
                hunks=[
                    DiffHunk(
                        old_start=1,
                        old_length=1,
                        new_start=1,
                        new_length=2,
                        changes=[
                            Change(ChangeType.CONTEXT, "def hello():"),
                            Change(ChangeType.ADD, "    return 'hi'"),
                        ],
                    )
                ],
            )
        ]

        output = run_review(
            files,
            adapter_name="fake",
            repository="acme/repo",
            base_ref="main",
            head_ref="feature/hi",
        )

        self.assertIn("## AI Review", output)
        self.assertIn("### Summary", output)
        self.assertIn("### Findings", output)
        self.assertIn("No issues found.", output)


if __name__ == "__main__":
    unittest.main()
