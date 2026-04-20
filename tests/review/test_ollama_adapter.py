import os
import unittest
from urllib.parse import urlparse
from unittest.mock import patch

from core.review.adapters.ollama_adapter import (
    AdapterConfigError,
    OllamaModelAdapter,
)


class _FakeHttpResponse:
    def __init__(self, body: str):
        self._body = body

    def read(self):
        return self._body.encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        del exc_type, exc, tb
        return False


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
                "OLLAMA_THINK": "false",
            },
            clear=True,
        ):
            adapter = OllamaModelAdapter.from_env()

        self.assertEqual(adapter.base_url, "http://localhost:11434")
        self.assertEqual(adapter.model, "qwen3:32b")
        self.assertEqual(adapter.timeout_seconds, 45)
        self.assertFalse(adapter.think)
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
        self.assertIsNone(adapter.think)

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

    def test_from_env_think_true_values(self) -> None:
        for value in ("true", "1", "yes", "on"):
            with self.subTest(value=value):
                with patch.dict(
                    os.environ,
                    {
                        "OLLAMA_BASE_URL": "http://localhost:11434",
                        "OLLAMA_MODEL": "qwen3:32b",
                        "OLLAMA_THINK": value,
                    },
                    clear=True,
                ):
                    adapter = OllamaModelAdapter.from_env()
                self.assertTrue(adapter.think)

    def test_from_env_think_false_values(self) -> None:
        for value in ("false", "0", "no", "off"):
            with self.subTest(value=value):
                with patch.dict(
                    os.environ,
                    {
                        "OLLAMA_BASE_URL": "http://localhost:11434",
                        "OLLAMA_MODEL": "qwen3:32b",
                        "OLLAMA_THINK": value,
                    },
                    clear=True,
                ):
                    adapter = OllamaModelAdapter.from_env()
                self.assertFalse(adapter.think)

    def test_from_env_think_must_be_boolean(self) -> None:
        with patch.dict(
            os.environ,
            {
                "OLLAMA_BASE_URL": "http://localhost:11434",
                "OLLAMA_MODEL": "qwen3:32b",
                "OLLAMA_THINK": "medium",
            },
            clear=True,
        ):
            with self.assertRaises(AdapterConfigError):
                OllamaModelAdapter.from_env()


class OllamaAdapterRuntimeTest(unittest.TestCase):
    def test_generate_review_omits_think_when_unset(self) -> None:
        adapter = OllamaModelAdapter(
            base_url="http://localhost:11434",
            model="qwen3:32b",
            think=None,
        )

        with patch(
            "core.review.adapters.ollama_adapter.urllib.request.urlopen",
            return_value=_FakeHttpResponse('{"response":"## AI Review\\n\\n### Summary\\nok"}'),
        ) as urlopen_mock:
            output = adapter.generate_review("prompt text")

        self.assertIn("## AI Review", output)
        request = urlopen_mock.call_args.args[0]
        self.assertEqual(urlparse(request.full_url).path, "/api/generate")
        body = request.data.decode("utf-8")
        self.assertIn('"model": "qwen3:32b"', body)
        self.assertIn('"prompt": "prompt text"', body)
        self.assertNotIn('"think"', body)

    def test_generate_review_sends_think_false(self) -> None:
        adapter = OllamaModelAdapter(
            base_url="http://localhost:11434",
            model="qwen3:32b",
            think=False,
        )

        with patch(
            "core.review.adapters.ollama_adapter.urllib.request.urlopen",
            return_value=_FakeHttpResponse('{"response":"## AI Review\\n\\n### Summary\\nok"}'),
        ) as urlopen_mock:
            adapter.generate_review("prompt text")

        request = urlopen_mock.call_args.args[0]
        body = request.data.decode("utf-8")
        self.assertIn('"think": false', body)

    def test_generate_review_sends_think_true(self) -> None:
        adapter = OllamaModelAdapter(
            base_url="http://localhost:11434",
            model="qwen3:32b",
            think=True,
        )

        with patch(
            "core.review.adapters.ollama_adapter.urllib.request.urlopen",
            return_value=_FakeHttpResponse('{"response":"## AI Review\\n\\n### Summary\\nok"}'),
        ) as urlopen_mock:
            adapter.generate_review("prompt text")

        request = urlopen_mock.call_args.args[0]
        body = request.data.decode("utf-8")
        self.assertIn('"think": true', body)


if __name__ == "__main__":
    unittest.main()
