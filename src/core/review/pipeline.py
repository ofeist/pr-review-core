"""Simple review pipeline for local execution and tests."""

import logging
from typing import Dict, List, Optional

from core.diff.types import DiffFile
from core.review.adapters.fake import FakeModelAdapter
from core.review.adapters.openai_adapter import AdapterConfigError, OpenAIModelAdapter
from core.review.adapters.openai_compat_adapter import (
    AdapterConfigError as OpenAICompatAdapterConfigError,
    OpenAICompatModelAdapter,
)
from core.review.chunking import (
    build_change_summary,
    build_intent_summary,
    build_pr_summary,
    chunk_diff_files,
    merge_chunk_markdowns,
)
from core.review.model_adapter import ModelAdapter
from core.review.noise_filter import filter_review_markdown
from core.review.output_normalizer import normalize_review_markdown
from core.review.prompt_builder import build_review_prompt

LOGGER = logging.getLogger(__name__)


def _adapter_registry() -> Dict[str, ModelAdapter]:
    registry: Dict[str, ModelAdapter] = {
        "fake": FakeModelAdapter(),
    }

    try:
        registry["openai"] = OpenAIModelAdapter.from_env()
    except AdapterConfigError:
        # OpenAI adapter is optional in local/test runs.
        pass

    try:
        registry["openai-compat"] = OpenAICompatModelAdapter.from_env()
    except OpenAICompatAdapterConfigError:
        # OpenAI-compatible adapter is optional in local/test runs.
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
    fallback_enabled: bool = True,
    adapter_override: Optional[ModelAdapter] = None,
    pr_title: str = "",
    pr_body: str = "",
) -> str:
    """Run review generation with full-diff then fallback orchestration."""

    adapter = adapter_override if adapter_override is not None else get_adapter(adapter_name)
    change_summary_lines = build_change_summary(files)
    summary_prefix = build_pr_summary(files)
    intent_summary = build_intent_summary(pr_title, pr_body)

    # Step 1: try single full-diff review first.
    try:
        full_output = _review_one_payload(
            files,
            adapter=adapter,
            repository=repository,
            base_ref=base_ref,
            head_ref=head_ref,
            pr_title=pr_title,
            pr_body=pr_body,
        )
        return merge_chunk_markdowns(
            [full_output],
            change_summary_lines=change_summary_lines,
            summary_prefix=summary_prefix,
            intent_summary=intent_summary,
        )
    except Exception as exc:
        if not fallback_enabled:
            raise RuntimeError("Full-diff review failed and fallback mode is disabled.") from exc
        LOGGER.warning("Full-diff review failed, falling back to per-file mode: %s", exc)

    # Step 2: fallback to per-file reviews, with chunking within each file if needed.
    fallback_outputs: List[str] = []
    for file_obj in files:
        file_chunks = chunk_diff_files([file_obj], max_changes_per_chunk=max_changes_per_chunk)
        for chunk in file_chunks:
            try:
                chunk_output = _review_one_payload(
                    chunk,
                    adapter=adapter,
                    repository=repository,
                    base_ref=base_ref,
                    head_ref=head_ref,
                    pr_title=pr_title,
                    pr_body=pr_body,
                )
                fallback_outputs.append(chunk_output)
            except Exception as exc:
                LOGGER.warning("Fallback chunk review failed for file '%s': %s", file_obj.path, exc)

    if fallback_outputs:
        return merge_chunk_markdowns(
            fallback_outputs,
            change_summary_lines=change_summary_lines,
            summary_prefix=summary_prefix,
            intent_summary=intent_summary,
        )

    # Step 3: controlled final fallback if everything failed.
    change_summary_block = "\n".join(change_summary_lines) if change_summary_lines else "- Not available."
    return (
        "## AI Review\n"
        "\n"
        "### Summary\n"
        "Review could not be generated from model output.\n"
        "\n"
        "### Intent\n"
        f"{intent_summary}\n"
        "\n"
        "### Change Summary\n"
        f"{change_summary_block}\n"
        "\n"
        "### Findings\n"
        "- No issues found.\n"
    )


def _review_one_payload(
    files: List[DiffFile],
    *,
    adapter: ModelAdapter,
    repository: str,
    base_ref: str,
    head_ref: str,
    pr_title: str,
    pr_body: str,
) -> str:
    prompt = build_review_prompt(
        files,
        repository=repository,
        base_ref=base_ref,
        head_ref=head_ref,
        pr_title=pr_title,
        pr_body=pr_body,
    )
    raw_output = adapter.generate_review(prompt)
    normalized = normalize_review_markdown(raw_output)
    return filter_review_markdown(normalized)
