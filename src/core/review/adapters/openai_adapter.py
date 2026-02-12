"""OpenAI adapter implementation for review generation."""

import os
from dataclasses import dataclass
from typing import Any, Optional


class AdapterConfigError(Exception):
    """Raised when adapter configuration is missing or invalid."""


class AdapterRuntimeError(Exception):
    """Raised when adapter execution fails."""


@dataclass
class OpenAIModelAdapter:
    """Model adapter backed by OpenAI Responses API."""

    api_key: str
    model: str
    timeout_seconds: int = 30
    max_output_tokens: int = 1200
    client: Optional[Any] = None
    name: str = "openai"

    @classmethod
    def from_env(cls) -> "OpenAIModelAdapter":
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        model = os.getenv("OPENAI_MODEL", "").strip() or "gpt-4.1-mini"
        timeout_raw = os.getenv("OPENAI_TIMEOUT_SECONDS", "").strip()

        if not api_key:
            raise AdapterConfigError("OPENAI_API_KEY is required for openai adapter.")

        timeout_seconds = 30
        if timeout_raw:
            try:
                timeout_seconds = int(timeout_raw)
            except ValueError as exc:
                raise AdapterConfigError("OPENAI_TIMEOUT_SECONDS must be an integer.") from exc
        if timeout_seconds <= 0:
            raise AdapterConfigError("OPENAI_TIMEOUT_SECONDS must be > 0.")

        return cls(
            api_key=api_key,
            model=model,
            timeout_seconds=timeout_seconds,
        )

    def generate_review(self, prompt: str) -> str:
        if not prompt.strip():
            raise AdapterRuntimeError("Prompt must not be empty.")

        client = self._get_client()

        try:
            response = client.responses.create(
                model=self.model,
                input=[
                    {
                        "role": "user",
                        "content": [{"type": "input_text", "text": prompt}],
                    }
                ],
                max_output_tokens=self.max_output_tokens,
                timeout=self.timeout_seconds,
            )
        except Exception as exc:  # pragma: no cover - defensive wrapper
            raise AdapterRuntimeError(f"OpenAI request failed: {exc}") from exc

        text = self._extract_text(response)
        if not text:
            raise AdapterRuntimeError("OpenAI response did not contain text output.")

        return text

    def _get_client(self) -> Any:
        if self.client is not None:
            return self.client

        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - depends on environment
            raise AdapterConfigError(
                "openai package is not installed. Install it to use openai adapter."
            ) from exc

        self.client = OpenAI(api_key=self.api_key)
        return self.client

    @staticmethod
    def _extract_text(response: Any) -> str:
        # Preferred SDK field.
        output_text = getattr(response, "output_text", None)
        if isinstance(output_text, str) and output_text.strip():
            return output_text.strip()

        # Fallback: parse structured output blocks.
        output = getattr(response, "output", None)
        if not isinstance(output, list):
            return ""

        parts = []
        for item in output:
            content_list = getattr(item, "content", None)
            if not isinstance(content_list, list):
                continue
            for content in content_list:
                text = getattr(content, "text", None)
                if isinstance(text, str) and text.strip():
                    parts.append(text.strip())

        return "\n".join(parts).strip()
