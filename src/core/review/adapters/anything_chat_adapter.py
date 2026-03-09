"""Adapter for custom Anything chat streaming endpoints."""

import json
import os
import urllib.request
from dataclasses import dataclass


class AdapterConfigError(Exception):
    """Raised when adapter configuration is missing or invalid."""


class AdapterRuntimeError(Exception):
    """Raised when adapter execution fails."""


@dataclass
class AnythingChatModelAdapter:
    """Model adapter for custom SSE-style Anything chat endpoints."""

    url: str
    api_key: str = ""
    timeout_seconds: int = 30
    name: str = "anything-chat"

    @classmethod
    def from_env(cls) -> "AnythingChatModelAdapter":
        url = os.getenv("ANYTHING_CHAT_URL", "").strip()
        api_key = os.getenv("ANYTHING_CHAT_API_KEY", "").strip()
        timeout_raw = os.getenv("ANYTHING_CHAT_TIMEOUT_SECONDS", "").strip()

        if not url:
            raise AdapterConfigError("ANYTHING_CHAT_URL is required for anything-chat adapter.")

        timeout_seconds = 30
        if timeout_raw:
            try:
                timeout_seconds = int(timeout_raw)
            except ValueError as exc:
                raise AdapterConfigError("ANYTHING_CHAT_TIMEOUT_SECONDS must be an integer.") from exc
        if timeout_seconds <= 0:
            raise AdapterConfigError("ANYTHING_CHAT_TIMEOUT_SECONDS must be > 0.")

        return cls(url=url, api_key=api_key, timeout_seconds=timeout_seconds)

    def generate_review(self, prompt: str) -> str:
        if not prompt.strip():
            raise AdapterRuntimeError("Prompt must not be empty.")

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        request = urllib.request.Request(
            url=self.url,
            data=json.dumps({"message": prompt}).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                body = response.read().decode("utf-8", errors="replace")
        except Exception as exc:  # pragma: no cover - defensive wrapper
            raise AdapterRuntimeError(f"Anything chat request failed: {exc}") from exc

        text = self._extract_text_from_sse(body)
        if not text:
            raise AdapterRuntimeError("Anything chat response did not contain text output.")
        return text

    @staticmethod
    def _extract_text_from_sse(body: str) -> str:
        parts = []
        for line in body.splitlines():
            stripped = line.strip()
            if not stripped or not stripped.startswith("data:"):
                continue

            payload = stripped[5:].strip()
            if not payload:
                continue

            try:
                event = json.loads(payload)
            except json.JSONDecodeError:
                continue

            if event.get("error") is True:
                message = event.get("message") or event.get("detail") or "Unknown Anything chat error."
                raise AdapterRuntimeError(f"Anything chat stream returned an error: {message}")

            text = event.get("textResponse")
            if isinstance(text, str):
                parts.append(text)

        return "".join(parts).strip()
