import os
import unittest
from urllib.error import URLError
from unittest.mock import patch

from core.review.adapters.workspace_chat_adapter import (
    AdapterConfigError,
    AdapterRuntimeError,
    WorkspaceChatModelAdapter,
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


class WorkspaceChatAdapterConfigTest(unittest.TestCase):
    def test_from_env_requires_url(self) -> None:
        with patch.dict(os.environ, {"WORKSPACE_CHAT_URL": ""}, clear=True):
            with self.assertRaises(AdapterConfigError):
                WorkspaceChatModelAdapter.from_env()

    def test_from_env_reads_values(self) -> None:
        with patch.dict(
            os.environ,
            {
                "WORKSPACE_CHAT_URL": "http://localhost:5001/api/workspace/demo/thread/123/stream-chat",
                "WORKSPACE_CHAT_API_KEY": "test-key",
                "WORKSPACE_CHAT_TIMEOUT_SECONDS": "45",
            },
            clear=True,
        ):
            adapter = WorkspaceChatModelAdapter.from_env()

        self.assertEqual(adapter.url, "http://localhost:5001/api/workspace/demo/thread/123/stream-chat")
        self.assertEqual(adapter.api_key, "test-key")
        self.assertEqual(adapter.timeout_seconds, 45)

    def test_from_env_timeout_must_be_integer(self) -> None:
        with patch.dict(
            os.environ,
            {
                "WORKSPACE_CHAT_URL": "http://localhost:5001/api/workspace/demo/thread/123/stream-chat",
                "WORKSPACE_CHAT_TIMEOUT_SECONDS": "abc",
            },
            clear=True,
        ):
            with self.assertRaises(AdapterConfigError):
                WorkspaceChatModelAdapter.from_env()


class WorkspaceChatAdapterRuntimeTest(unittest.TestCase):
    def test_generate_review_requires_non_empty_prompt(self) -> None:
        adapter = WorkspaceChatModelAdapter(url="http://localhost:5001/api/workspace/demo/thread/123/stream-chat")

        with self.assertRaises(AdapterRuntimeError):
            adapter.generate_review("   ")

    def test_generate_review_posts_prompt_and_collects_stream(self) -> None:
        adapter = WorkspaceChatModelAdapter(
            url="http://localhost:5001/api/workspace/demo/thread/123/stream-chat",
            api_key="test-key",
            timeout_seconds=12,
        )
        body = (
            'data: {"type":"textResponseChunk","textResponse":"## AI Review\\n\\n","close":false,"error":false}\n'
            'data: {"type":"textResponseChunk","textResponse":"### Summary\\nlooks good","close":false,"error":false}\n'
            'data: {"type":"finalizeResponseStream","close":true,"error":false}\n'
        )

        with patch(
            "core.review.adapters.workspace_chat_adapter.urllib.request.urlopen",
            return_value=_FakeHttpResponse(body),
        ) as urlopen_mock:
            output = adapter.generate_review("prompt text")

        self.assertIn("## AI Review", output)
        self.assertIn("looks good", output)
        request = urlopen_mock.call_args.args[0]
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.full_url, adapter.url)
        self.assertEqual(request.headers["Authorization"], "Bearer test-key")
        self.assertEqual(request.headers["Content-type"], "application/json")
        self.assertIn('"message": "prompt text"', request.data.decode("utf-8"))
        self.assertEqual(urlopen_mock.call_args.kwargs["timeout"], 12)

    def test_generate_review_allows_missing_auth(self) -> None:
        adapter = WorkspaceChatModelAdapter(url="http://localhost:5001/api/workspace/demo/thread/123/stream-chat")
        body = 'data: {"type":"textResponseChunk","textResponse":"hello","close":true,"error":false}\n'

        with patch(
            "core.review.adapters.workspace_chat_adapter.urllib.request.urlopen",
            return_value=_FakeHttpResponse(body),
        ) as urlopen_mock:
            output = adapter.generate_review("prompt text")

        self.assertEqual(output, "hello")
        request = urlopen_mock.call_args.args[0]
        self.assertNotIn("Authorization", request.headers)

    def test_generate_review_wraps_transport_errors(self) -> None:
        adapter = WorkspaceChatModelAdapter(url="http://localhost:5001/api/workspace/demo/thread/123/stream-chat")

        with patch(
            "core.review.adapters.workspace_chat_adapter.urllib.request.urlopen",
            side_effect=URLError("network down"),
        ):
            with self.assertRaises(AdapterRuntimeError) as ctx:
                adapter.generate_review("prompt text")

        self.assertIn("Workspace chat request failed:", str(ctx.exception))

    def test_generate_review_raises_on_stream_error_event(self) -> None:
        adapter = WorkspaceChatModelAdapter(url="http://localhost:5001/api/workspace/demo/thread/123/stream-chat")
        body = 'data: {"type":"textResponseChunk","message":"bad upstream","close":true,"error":true}\n'

        with patch(
            "core.review.adapters.workspace_chat_adapter.urllib.request.urlopen",
            return_value=_FakeHttpResponse(body),
        ):
            with self.assertRaises(AdapterRuntimeError) as ctx:
                adapter.generate_review("prompt text")

        self.assertIn("Workspace chat stream returned an error:", str(ctx.exception))

    def test_generate_review_empty_response_is_controlled_error(self) -> None:
        adapter = WorkspaceChatModelAdapter(url="http://localhost:5001/api/workspace/demo/thread/123/stream-chat")
        body = 'data: {"type":"finalizeResponseStream","close":true,"error":false}\n'

        with patch(
            "core.review.adapters.workspace_chat_adapter.urllib.request.urlopen",
            return_value=_FakeHttpResponse(body),
        ):
            with self.assertRaises(AdapterRuntimeError) as ctx:
                adapter.generate_review("prompt text")

        self.assertIn("did not contain text output", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
