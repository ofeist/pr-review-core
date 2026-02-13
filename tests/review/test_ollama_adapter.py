import os
import unittest
from unittest.mock import patch

from core.review.adapters.ollama_adapter import AdapterConfigError, OllamaModelAdapter


class OllamaAdapterConfigTest(unittest.TestCase):
    def test_from_env_requires_base_url(self) -> None:
        with patch.dict(
            os.environ,
            {
                "OLLAMA_BASE_URL": "",
                "OLLAMA_MODEL": "qwen3:32b",
            },
            clear=True,
        ):
            with self.assertRaises(AdapterConfigError):
                OllamaModelAdapter.from_env()

    def test_from_env_requires_model(self) -> None:
        with patch.dict(
            os.environ,
            {
                "OLLAMA_BASE_URL": "http://localhost:11434",
                "OLLAMA_MODEL": "",
            },
            clear=True,
        ):
            with self.assertRaises(AdapterConfigError):
                OllamaModelAdapter.from_env()

    def test_from_env_reads_values(self) -> None:
        with patch.dict(
            os.environ,
            {
                "OLLAMA_BASE_URL": "http://localhost:11434",
                "OLLAMA_MODEL": "qwen3:32b",
                "OLLAMA_TIMEOUT_SECONDS": "45",
            },
            clear=True,
        ):
            adapter = OllamaModelAdapter.from_env()

        self.assertEqual(adapter.base_url, "http://localhost:11434")
        self.assertEqual(adapter.model, "qwen3:32b")
        self.assertEqual(adapter.timeout_seconds, 45)
        self.assertEqual(adapter.name, "ollama")

    def test_from_env_uses_default_timeout_when_empty(self) -> None:
        with patch.dict(
            os.environ,
            {
                "OLLAMA_BASE_URL": "http://localhost:11434",
                "OLLAMA_MODEL": "qwen3:32b",
                "OLLAMA_TIMEOUT_SECONDS": "",
            },
            clear=True,
        ):
            adapter = OllamaModelAdapter.from_env()

        self.assertEqual(adapter.timeout_seconds, 30)

    def test_from_env_timeout_must_be_integer(self) -> None:
        with patch.dict(
            os.environ,
            {
                "OLLAMA_BASE_URL": "http://localhost:11434",
                "OLLAMA_MODEL": "qwen3:32b",
                "OLLAMA_TIMEOUT_SECONDS": "abc",
            },
            clear=True,
        ):
            with self.assertRaises(AdapterConfigError):
                OllamaModelAdapter.from_env()

    def test_from_env_timeout_must_be_positive(self) -> None:
        with patch.dict(
            os.environ,
            {
                "OLLAMA_BASE_URL": "http://localhost:11434",
                "OLLAMA_MODEL": "qwen3:32b",
                "OLLAMA_TIMEOUT_SECONDS": "0",
            },
            clear=True,
        ):
            with self.assertRaises(AdapterConfigError):
                OllamaModelAdapter.from_env()


if __name__ == "__main__":
    unittest.main()
