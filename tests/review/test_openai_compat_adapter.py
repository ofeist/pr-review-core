import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from core.review.adapters.openai_compat_adapter import (
    AdapterConfigError,
    AdapterRuntimeError,
    OpenAICompatModelAdapter,
)


class _FakeResponsesApi:
    def __init__(self, response_to_return=None, error_to_raise=None):
        self.response_to_return = response_to_return
        self.error_to_raise = error_to_raise
        self.last_kwargs = None

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        if self.error_to_raise is not None:
            raise self.error_to_raise
        return self.response_to_return


class _FakeClient:
    def __init__(self, responses_api):
        self.responses = responses_api


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

    def test_generate_review_builds_expected_request(self) -> None:
        fake_response = SimpleNamespace(output_text="## AI Review\n\n### Summary\nok")
        responses_api = _FakeResponsesApi(response_to_return=fake_response)
        adapter = OpenAICompatModelAdapter(
            base_url="http://localhost:11434/v1",
            model="qwen2.5-coder",
            api_key="test-key",
            timeout_seconds=22,
            max_output_tokens=456,
            client=_FakeClient(responses_api),
        )

        output = adapter.generate_review("prompt text")

        self.assertIn("## AI Review", output)
        self.assertEqual(responses_api.last_kwargs["model"], "qwen2.5-coder")
        self.assertEqual(responses_api.last_kwargs["max_output_tokens"], 456)
        self.assertEqual(responses_api.last_kwargs["timeout"], 22)
        self.assertEqual(
            responses_api.last_kwargs["input"][0]["content"][0]["text"],
            "prompt text",
        )

    def test_generate_review_fallback_extracts_structured_output(self) -> None:
        fake_response = SimpleNamespace(
            output=[
                SimpleNamespace(
                    content=[
                        SimpleNamespace(text="## AI Review"),
                        SimpleNamespace(text="### Summary"),
                        SimpleNamespace(text="Recovered response"),
                    ]
                )
            ]
        )
        responses_api = _FakeResponsesApi(response_to_return=fake_response)
        adapter = OpenAICompatModelAdapter(
            base_url="http://localhost:11434/v1",
            model="qwen2.5-coder",
            client=_FakeClient(responses_api),
        )

        output = adapter.generate_review("prompt text")
        self.assertIn("Recovered response", output)

    def test_generate_review_wraps_api_errors(self) -> None:
        responses_api = _FakeResponsesApi(error_to_raise=RuntimeError("boom"))
        adapter = OpenAICompatModelAdapter(
            base_url="http://localhost:11434/v1",
            model="qwen2.5-coder",
            client=_FakeClient(responses_api),
        )

        with self.assertRaises(AdapterRuntimeError):
            adapter.generate_review("prompt text")

    def test_generate_review_empty_response_is_controlled_error(self) -> None:
        responses_api = _FakeResponsesApi(response_to_return=SimpleNamespace(output_text=""))
        adapter = OpenAICompatModelAdapter(
            base_url="http://localhost:11434/v1",
            model="qwen2.5-coder",
            client=_FakeClient(responses_api),
        )

        with self.assertRaises(AdapterRuntimeError) as ctx:
            adapter.generate_review("prompt text")

        self.assertIn("did not contain text output", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
