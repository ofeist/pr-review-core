"""OpenAI-compatible adapter skeleton with env validation."""

import os
from dataclasses import dataclass
from typing import Optional


class AdapterConfigError(Exception):
    """Raised when adapter configuration is missing or invalid."""


class AdapterRuntimeError(Exception):
    """Raised when adapter execution fails."""


@dataclass
class OpenAICompatModelAdapter:
    """Model adapter skeleton for OpenAI-compatible endpoints.

    Slice 1 scope:
    - config/env parsing and validation
    - explicit runtime placeholder until request path is implemented
    """

    base_url: str
    model: str
    api_key: str = ""
    timeout_seconds: int = 30
    max_output_tokens: int = 1200
    name: str = "openai-compat"

    @classmethod
    def from_env(cls) -> "OpenAICompatModelAdapter":
        base_url = os.getenv("OPENAI_COMPAT_BASE_URL", "").strip()
        model = os.getenv("OPENAI_COMPAT_MODEL", "").strip()
        api_key = os.getenv("OPENAI_COMPAT_API_KEY", "").strip()
        timeout_raw = os.getenv("OPENAI_COMPAT_TIMEOUT_SECONDS", "").strip()

        if not base_url:
            raise AdapterConfigError("OPENAI_COMPAT_BASE_URL is required for openai-compat adapter.")
        if not model:
            raise AdapterConfigError("OPENAI_COMPAT_MODEL is required for openai-compat adapter.")

        timeout_seconds = 30
        if timeout_raw:
            try:
                timeout_seconds = int(timeout_raw)
            except ValueError as exc:
                raise AdapterConfigError("OPENAI_COMPAT_TIMEOUT_SECONDS must be an integer.") from exc
        if timeout_seconds <= 0:
            raise AdapterConfigError("OPENAI_COMPAT_TIMEOUT_SECONDS must be > 0.")

        return cls(
            base_url=base_url,
            model=model,
            api_key=api_key,
            timeout_seconds=timeout_seconds,
        )

    def generate_review(self, prompt: str) -> str:
        if not prompt.strip():
            raise AdapterRuntimeError("Prompt must not be empty.")
        raise AdapterRuntimeError(
            "openai-compat adapter request path is not implemented yet (planned in next slice)."
        )
