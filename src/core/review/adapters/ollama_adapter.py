"""Ollama adapter with strict environment configuration validation."""

import json
import os
import urllib.request
from dataclasses import dataclass
from typing import Optional


class AdapterConfigError(Exception):
    """Raised when adapter configuration is missing or invalid."""


class AdapterRuntimeError(Exception):
    """Raised when adapter execution fails."""


@dataclass
class OllamaModelAdapter:
    """Model adapter for native Ollama generate endpoint."""

    base_url: str
    model: str
    timeout_seconds: int = 30
    name: str = "ollama"

    @classmethod
    def from_env(cls) -> "OllamaModelAdapter":
        base_url = os.getenv("OLLAMA_BASE_URL", "").strip()
        model = os.getenv("OLLAMA_MODEL", "").strip()
        timeout_raw = os.getenv("OLLAMA_TIMEOUT_SECONDS", "").strip()

        if not base_url:
            raise AdapterConfigError("OLLAMA_BASE_URL is required for ollama adapter.")
        if not model:
            raise AdapterConfigError("OLLAMA_MODEL is required for ollama adapter.")

        timeout_seconds = 30
        if timeout_raw:
            try:
                timeout_seconds = int(timeout_raw)
            except ValueError as exc:
                raise AdapterConfigError("OLLAMA_TIMEOUT_SECONDS must be an integer.") from exc
        if timeout_seconds <= 0:
            raise AdapterConfigError("OLLAMA_TIMEOUT_SECONDS must be > 0.")

        return cls(base_url=base_url, model=model, timeout_seconds=timeout_seconds)

    def generate_review(self, prompt: str) -> str:
        if not prompt.strip():
            raise AdapterRuntimeError("Prompt must not be empty.")

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        request = urllib.request.Request(
            url=self._generate_url(),
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                body = response.read().decode("utf-8", errors="replace")
            data = json.loads(body)
        except Exception as exc:  # pragma: no cover - defensive wrapper
            raise AdapterRuntimeError(f"Ollama request failed: {exc}") from exc

        text: Optional[str] = data.get("response")
        if isinstance(text, str) and text.strip():
            return text.strip()
        raise AdapterRuntimeError("Ollama response did not contain text output.")

    def _generate_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/api/generate"
