"""Model adapter contract for review generation."""

from typing import Protocol


class ModelAdapter(Protocol):
    """Minimal interface for model adapters used by the review pipeline."""

    name: str

    def generate_review(self, prompt: str) -> str:
        """Return markdown review text for a given prompt."""
