import builtins
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from core.review.adapters.openai_adapter import (
    AdapterConfigError,
    AdapterRuntimeError,
    OpenAIModelAdapter,
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


class OpenAIAdapterConfigTest(unittest.TestCase):
    def test_from_env_requires_api_key(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(AdapterConfigError):
                OpenAIModelAdapter.from_env()

    def test_from_env_reads_values(self) -> None:
        with patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "test-key",
                "OPENAI_MODEL": "gpt-test",
                "OPENAI_TIMEOUT_SECONDS": "42",
            },
            clear=True,
        ):
            adapter = OpenAIModelAdapter.from_env()

        self.assertEqual(adapter.api_key, "test-key")
        self.assertEqual(adapter.model, "gpt-test")
        self.assertEqual(adapter.timeout_seconds, 42)

    def test_from_env_uses_defaults_for_empty_optional_values(self) -> None:
        with patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "test-key",
                "OPENAI_MODEL": "",
                "OPENAI_TIMEOUT_SECONDS": "",
            },
            clear=True,
        ):
            adapter = OpenAIModelAdapter.from_env()

        self.assertEqual(adapter.model, "gpt-4.1-mini")
        self.assertEqual(adapter.timeout_seconds, 30)


class OpenAIAdapterRuntimeTest(unittest.TestCase):
    def test_generate_review_builds_expected_request(self) -> None:
        fake_response = SimpleNamespace(output_text="## AI Review\n\n### Summary\nok")
        responses_api = _FakeResponsesApi(response_to_return=fake_response)
        client = _FakeClient(responses_api)
        adapter = OpenAIModelAdapter(
            api_key="test-key",
            model="gpt-test",
            timeout_seconds=15,
            max_output_tokens=321,
            client=client,
        )

        output = adapter.generate_review("prompt text")

        self.assertIn("## AI Review", output)
        self.assertEqual(responses_api.last_kwargs["model"], "gpt-test")
        self.assertEqual(responses_api.last_kwargs["max_output_tokens"], 321)
        self.assertEqual(responses_api.last_kwargs["timeout"], 15)
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
        adapter = OpenAIModelAdapter(
            api_key="test-key",
            model="gpt-test",
            client=_FakeClient(responses_api),
        )

        output = adapter.generate_review("prompt text")
        self.assertIn("Recovered response", output)

    def test_generate_review_wraps_api_errors(self) -> None:
        responses_api = _FakeResponsesApi(error_to_raise=RuntimeError("boom"))
        adapter = OpenAIModelAdapter(
            api_key="test-key",
            model="gpt-test",
            client=_FakeClient(responses_api),
        )

        with self.assertRaises(AdapterRuntimeError):
            adapter.generate_review("prompt text")

    def test_get_client_missing_openai_dependency_is_controlled_error(self) -> None:
        adapter = OpenAIModelAdapter(
            api_key="test-key",
            model="gpt-test",
        )

        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name == "openai":
                raise ImportError("simulated missing dependency")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=fake_import):
            with self.assertRaises(AdapterConfigError) as ctx:
                adapter._get_client()

        self.assertIn("openai package is not installed", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
