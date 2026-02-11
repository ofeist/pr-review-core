"""Simple review pipeline for local execution and tests."""

from typing import Dict, List

from core.diff.types import DiffFile
from core.review.adapters.fake import FakeModelAdapter
from core.review.adapters.openai_adapter import AdapterConfigError, OpenAIModelAdapter
from core.review.chunking import chunk_diff_files, merge_chunk_markdowns
from core.review.model_adapter import ModelAdapter
from core.review.noise_filter import filter_review_markdown
from core.review.output_normalizer import normalize_review_markdown
from core.review.prompt_builder import build_review_prompt


def _adapter_registry() -> Dict[str, ModelAdapter]:
    registry: Dict[str, ModelAdapter] = {
        "fake": FakeModelAdapter(),
    }

    try:
        registry["openai"] = OpenAIModelAdapter.from_env()
    except AdapterConfigError:
        # OpenAI adapter is optional in local/test runs.
        pass

    return registry


def get_adapter(name: str) -> ModelAdapter:
    registry = _adapter_registry()
    if name not in registry:
        known = ", ".join(sorted(registry.keys()))
        raise ValueError(f"Unknown adapter '{name}'. Known adapters: {known}")
    return registry[name]


def run_review(
    files: List[DiffFile],
    *,
    adapter_name: str = "fake",
    repository: str = "",
    base_ref: str = "",
    head_ref: str = "",
    max_changes_per_chunk: int = 200,
) -> str:
    """Run prompt build + adapter generation end-to-end."""

    adapter = get_adapter(adapter_name)
    chunks = chunk_diff_files(files, max_changes_per_chunk=max_changes_per_chunk)

    chunk_outputs: List[str] = []
    for idx, chunk in enumerate(chunks, start=1):
        prompt = build_review_prompt(
            chunk,
            repository=repository,
            base_ref=base_ref,
            head_ref=head_ref,
        )
        raw_output = adapter.generate_review(prompt)
        normalized = normalize_review_markdown(raw_output)
        filtered = filter_review_markdown(normalized)
        chunk_outputs.append(filtered)

    return merge_chunk_markdowns(chunk_outputs)
