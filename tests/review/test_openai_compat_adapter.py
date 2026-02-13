import os
import unittest
from types import SimpleNamespace
from urllib.error import URLError
from urllib.parse import urlparse
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


class _FakeOpenAIAPIError(Exception):
    pass


_FakeOpenAIAPIError.__module__ = "openai"


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
        responses_api = _FakeResponsesApi(error_to_raise=_FakeOpenAIAPIError("boom"))
        adapter = OpenAICompatModelAdapter(
            base_url="http://localhost:11434/v1",
            model="qwen2.5-coder",
            client=_FakeClient(responses_api),
        )

        with self.assertRaises(AdapterRuntimeError) as ctx:
            adapter.generate_review("prompt text")
        self.assertIn("OpenAI-compatible request failed:", str(ctx.exception))

    def test_generate_review_does_not_wrap_unexpected_programming_errors(self) -> None:
        responses_api = _FakeResponsesApi(error_to_raise=ValueError("bad local wiring"))
        adapter = OpenAICompatModelAdapter(
            base_url="http://localhost:11434/v1",
            model="qwen2.5-coder",
            client=_FakeClient(responses_api),
        )

        with self.assertRaises(ValueError):
            adapter.generate_review("prompt text")

    def test_generate_review_redacts_keys_from_wrapped_errors(self) -> None:
        leaked = "request failed api_key=test-key Bearer sk-abc123 OPENAI_API_KEY=shared-key"
        responses_api = _FakeResponsesApi(error_to_raise=_FakeOpenAIAPIError(leaked))
        adapter = OpenAICompatModelAdapter(
            base_url="http://localhost:11434/v1",
            model="qwen2.5-coder",
            api_key="test-key",
            client=_FakeClient(responses_api),
        )

        with patch.dict(os.environ, {"OPENAI_API_KEY": "shared-key"}, clear=False):
            with self.assertRaises(AdapterRuntimeError) as ctx:
                adapter.generate_review("prompt text")

        message = str(ctx.exception)
        self.assertIn("OpenAI-compatible request failed:", message)
        self.assertNotIn("test-key", message)
        self.assertNotIn("shared-key", message)
        self.assertNotIn("sk-abc123", message)
        self.assertIn("api_key=***", message)
        self.assertIn("Bearer ***", message)

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

    def test_generate_review_empty_response_with_fallback_disabled_is_unchanged(self) -> None:
        responses_api = _FakeResponsesApi(response_to_return=SimpleNamespace(output_text=""))
        adapter = OpenAICompatModelAdapter(
            base_url="http://localhost:11434/v1",
            model="qwen2.5-coder",
            client=_FakeClient(responses_api),
        )

        with patch.dict(os.environ, {"OPENAI_COMPAT_ENABLE_OLLAMA_FALLBACK": "0"}, clear=False):
            with self.assertRaises(AdapterRuntimeError) as ctx:
                adapter.generate_review("prompt text")
        self.assertIn("did not contain text output", str(ctx.exception))

    def test_generate_review_empty_response_uses_opt_in_ollama_fallback(self) -> None:
        responses_api = _FakeResponsesApi(response_to_return=SimpleNamespace(output_text=""))
        adapter = OpenAICompatModelAdapter(
            base_url="http://localhost:11434/v1",
            model="qwen3:32b",
            client=_FakeClient(responses_api),
        )

        with patch.dict(os.environ, {"OPENAI_COMPAT_ENABLE_OLLAMA_FALLBACK": "1"}, clear=False):
            with patch(
                "core.review.adapters.openai_compat_adapter.urllib.request.urlopen",
                return_value=_FakeHttpResponse('{"response":"fallback hello"}'),
            ) as urlopen_mock:
                output = adapter.generate_review("prompt text")

        self.assertEqual(output, "fallback hello")
        request = urlopen_mock.call_args.args[0]
        self.assertEqual(urlparse(request.full_url).path, "/api/generate")
        body = request.data.decode("utf-8")
        self.assertIn('"model": "qwen3:32b"', body)
        self.assertIn('"prompt": "prompt text"', body)

    def test_generate_review_fallback_wraps_timeout_error(self) -> None:
        responses_api = _FakeResponsesApi(response_to_return=SimpleNamespace(output_text=""))
        adapter = OpenAICompatModelAdapter(
            base_url="http://localhost:11434/v1",
            model="qwen3:32b",
            client=_FakeClient(responses_api),
        )

        with patch.dict(os.environ, {"OPENAI_COMPAT_ENABLE_OLLAMA_FALLBACK": "1"}, clear=False):
            with patch(
                "core.review.adapters.openai_compat_adapter.urllib.request.urlopen",
                side_effect=TimeoutError("timed out"),
            ):
                with self.assertRaises(AdapterRuntimeError) as ctx:
                    adapter.generate_review("prompt text")
        self.assertIn("Ollama fallback request failed:", str(ctx.exception))
        self.assertIn("timed out", str(ctx.exception))

    def test_generate_review_fallback_wraps_and_redacts_error_text(self) -> None:
        responses_api = _FakeResponsesApi(response_to_return=SimpleNamespace(output_text=""))
        adapter = OpenAICompatModelAdapter(
            base_url="http://localhost:11434/v1",
            model="qwen3:32b",
            api_key="test-key",
            client=_FakeClient(responses_api),
        )

        leaked = "network fail api_key=test-key OPENAI_API_KEY=shared-key Bearer sk-abc123"
        with patch.dict(
            os.environ,
            {
                "OPENAI_COMPAT_ENABLE_OLLAMA_FALLBACK": "1",
                "OPENAI_API_KEY": "shared-key",
            },
            clear=False,
        ):
            with patch(
                "core.review.adapters.openai_compat_adapter.urllib.request.urlopen",
                side_effect=URLError(leaked),
            ):
                with self.assertRaises(AdapterRuntimeError) as ctx:
                    adapter.generate_review("prompt text")

        message = str(ctx.exception)
        self.assertIn("Ollama fallback request failed:", message)
        self.assertNotIn("test-key", message)
        self.assertNotIn("shared-key", message)
        self.assertNotIn("sk-abc123", message)
        self.assertIn("api_key=***", message)
        self.assertIn("Bearer ***", message)


if __name__ == "__main__":
    unittest.main()
