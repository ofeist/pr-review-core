import os
import unittest
from unittest.mock import patch

from core.review.adapters.openai_compat_adapter import (
    AdapterConfigError,
    AdapterRuntimeError,
    OpenAICompatModelAdapter,
)


class OpenAICompatAdapterConfigTest(unittest.TestCase):
    def test_from_env_requires_base_url(self) -> None:
        with patch.dict(
            os.environ,
            {
                "OPENAI_COMPAT_BASE_URL": "",
                "OPENAI_COMPAT_MODEL": "qwen2.5-coder",
            },
            clear=True,
        ):
            with self.assertRaises(AdapterConfigError):
                OpenAICompatModelAdapter.from_env()

    def test_from_env_requires_model(self) -> None:
        with patch.dict(
            os.environ,
            {
                "OPENAI_COMPAT_BASE_URL": "http://localhost:11434/v1",
                "OPENAI_COMPAT_MODEL": "",
            },
            clear=True,
        ):
            with self.assertRaises(AdapterConfigError):
                OpenAICompatModelAdapter.from_env()

    def test_from_env_reads_values(self) -> None:
        with patch.dict(
            os.environ,
            {
                "OPENAI_COMPAT_BASE_URL": "http://localhost:11434/v1",
                "OPENAI_COMPAT_MODEL": "qwen2.5-coder",
                "OPENAI_COMPAT_API_KEY": "test-key",
                "OPENAI_COMPAT_TIMEOUT_SECONDS": "45",
            },
            clear=True,
        ):
            adapter = OpenAICompatModelAdapter.from_env()

        self.assertEqual(adapter.base_url, "http://localhost:11434/v1")
        self.assertEqual(adapter.model, "qwen2.5-coder")
        self.assertEqual(adapter.api_key, "test-key")
        self.assertEqual(adapter.timeout_seconds, 45)

    def test_from_env_uses_default_timeout_when_empty(self) -> None:
        with patch.dict(
            os.environ,
            {
                "OPENAI_COMPAT_BASE_URL": "http://localhost:11434/v1",
                "OPENAI_COMPAT_MODEL": "qwen2.5-coder",
                "OPENAI_COMPAT_TIMEOUT_SECONDS": "",
            },
            clear=True,
        ):
            adapter = OpenAICompatModelAdapter.from_env()

        self.assertEqual(adapter.timeout_seconds, 30)

    def test_from_env_timeout_must_be_integer(self) -> None:
        with patch.dict(
            os.environ,
            {
                "OPENAI_COMPAT_BASE_URL": "http://localhost:11434/v1",
                "OPENAI_COMPAT_MODEL": "qwen2.5-coder",
                "OPENAI_COMPAT_TIMEOUT_SECONDS": "abc",
            },
            clear=True,
        ):
            with self.assertRaises(AdapterConfigError):
                OpenAICompatModelAdapter.from_env()

    def test_from_env_timeout_must_be_positive(self) -> None:
        with patch.dict(
            os.environ,
            {
                "OPENAI_COMPAT_BASE_URL": "http://localhost:11434/v1",
                "OPENAI_COMPAT_MODEL": "qwen2.5-coder",
                "OPENAI_COMPAT_TIMEOUT_SECONDS": "0",
            },
            clear=True,
        ):
            with self.assertRaises(AdapterConfigError):
                OpenAICompatModelAdapter.from_env()


class OpenAICompatAdapterRuntimeTest(unittest.TestCase):
    def test_generate_review_requires_non_empty_prompt(self) -> None:
        adapter = OpenAICompatModelAdapter(
            base_url="http://localhost:11434/v1",
            model="qwen2.5-coder",
        )

        with self.assertRaises(AdapterRuntimeError):
            adapter.generate_review("   ")

    def test_generate_review_placeholder_error(self) -> None:
        adapter = OpenAICompatModelAdapter(
            base_url="http://localhost:11434/v1",
            model="qwen2.5-coder",
        )

        with self.assertRaises(AdapterRuntimeError) as ctx:
            adapter.generate_review("review this diff")

        self.assertIn("not implemented", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
