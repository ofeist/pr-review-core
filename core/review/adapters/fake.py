"""Fake deterministic adapter for local development and tests."""

from dataclasses import dataclass


@dataclass(frozen=True)
class FakeModelAdapter:
    """Deterministic adapter that never calls external services."""

    name: str = "fake"

    def generate_review(self, prompt: str) -> str:
        # Deterministic summary based on prompt length only.
        prompt_size = len(prompt)
        return (
            "## AI Review\n"
            "\n"
            "### Summary\n"
            f"Fake adapter processed prompt ({prompt_size} chars).\n"
            "\n"
            "### Findings\n"
            "- No issues found.\n"
        )
