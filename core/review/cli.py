"""CLI for running review core locally and in CI."""

import argparse
import json
import sys
from typing import Any, List

from core.diff.filters import filter_diff_files
from core.diff.parse_diff import parse_diff
from core.diff.read_diff import DiffReadError, read_diff
from core.diff.types import Change, ChangeType, DiffFile, DiffHunk
from core.review.pipeline import run_review

EXIT_OK = 0
EXIT_RECOVERABLE = 1
EXIT_FATAL = 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate AI review markdown from diff input.")
    parser.add_argument(
        "--input-format",
        choices=["auto", "raw", "parsed-json"],
        default="auto",
        help="Input mode: raw git diff, parsed JSON, or auto-detect.",
    )
    parser.add_argument(
        "--from-file",
        default="",
        help="Read input from file path instead of stdin.",
    )
    parser.add_argument(
        "--adapter",
        default="fake",
        help="Review adapter name (default: fake).",
    )
    parser.add_argument(
        "--repository",
        default="",
        help="Repository identifier shown in prompt context.",
    )
    parser.add_argument(
        "--base-ref",
        default="",
        help="Base ref shown in prompt context.",
    )
    parser.add_argument(
        "--head-ref",
        default="",
        help="Head ref shown in prompt context.",
    )
    parser.add_argument(
        "--max-changes-per-chunk",
        type=int,
        default=200,
        help="Maximum number of diff changes per chunk.",
    )
    parser.add_argument(
        "--fallback-mode",
        choices=["on", "off"],
        default="on",
        help="Fallback behavior when full-diff review fails.",
    )
    return parser


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)

    if args.max_changes_per_chunk <= 0:
        print("Error: --max-changes-per-chunk must be > 0", file=sys.stderr)
        return EXIT_FATAL

    try:
        input_text = _read_input_text(args.from_file)
    except DiffReadError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return EXIT_RECOVERABLE

    if not input_text.strip():
        print("Error: empty input", file=sys.stderr)
        return EXIT_RECOVERABLE

    try:
        files = _load_diff_files(input_text, input_format=args.input_format)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return EXIT_RECOVERABLE
    except Exception as exc:  # pragma: no cover - defensive wrapper
        print(f"Fatal: failed to parse input ({exc})", file=sys.stderr)
        return EXIT_FATAL

    try:
        output = run_review(
            files,
            adapter_name=args.adapter,
            repository=args.repository,
            base_ref=args.base_ref,
            head_ref=args.head_ref,
            max_changes_per_chunk=args.max_changes_per_chunk,
            fallback_enabled=(args.fallback_mode == "on"),
        )
    except Exception as exc:
        print(f"Error: review generation failed ({exc})", file=sys.stderr)
        return EXIT_RECOVERABLE

    print(output, end="")
    return EXIT_OK


def _read_input_text(from_file: str) -> str:
    if from_file:
        return read_diff(from_file=from_file)
    return read_diff()


def _load_diff_files(input_text: str, *, input_format: str) -> List[DiffFile]:
    mode = input_format
    if mode == "auto":
        mode = "parsed-json" if _looks_like_json(input_text) else "raw"

    if mode == "raw":
        files = parse_diff(input_text)
        return filter_diff_files(files)

    if mode == "parsed-json":
        try:
            data = json.loads(input_text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid parsed JSON input: {exc}") from exc
        return _files_from_json(data)

    raise ValueError(f"Unsupported input format: {input_format}")


def _looks_like_json(input_text: str) -> bool:
    stripped = input_text.lstrip()
    return stripped.startswith("[") or stripped.startswith("{")


def _files_from_json(data: Any) -> List[DiffFile]:
    if not isinstance(data, list):
        raise ValueError("Parsed JSON input must be a list of files.")

    files: List[DiffFile] = []
    for file_obj in data:
        if not isinstance(file_obj, dict):
            raise ValueError("Each file entry must be an object.")

        path = file_obj.get("path", "")
        if not isinstance(path, str) or not path:
            raise ValueError("Each file entry must include non-empty 'path'.")

        language = file_obj.get("language")
        if language is not None and not isinstance(language, str):
            raise ValueError("'language' must be a string when provided.")

        hunks_raw = file_obj.get("hunks", [])
        if not isinstance(hunks_raw, list):
            raise ValueError("'hunks' must be a list.")

        hunks: List[DiffHunk] = []
        for hunk_obj in hunks_raw:
            if not isinstance(hunk_obj, dict):
                raise ValueError("Each hunk must be an object.")

            try:
                old_start = int(hunk_obj.get("old_start", hunk_obj.get("oldStart")))
                old_length = int(hunk_obj.get("old_length", hunk_obj.get("oldLength", 1)))
                new_start = int(hunk_obj.get("new_start", hunk_obj.get("newStart")))
                new_length = int(hunk_obj.get("new_length", hunk_obj.get("newLength", 1)))
            except (TypeError, ValueError) as exc:
                raise ValueError("Hunk start/length values must be integers.") from exc

            changes_raw = hunk_obj.get("changes", [])
            if not isinstance(changes_raw, list):
                raise ValueError("'changes' must be a list.")

            changes: List[Change] = []
            for change_obj in changes_raw:
                if not isinstance(change_obj, dict):
                    raise ValueError("Each change must be an object.")

                raw_type = change_obj.get("type")
                if not isinstance(raw_type, str):
                    raise ValueError("Each change must include string 'type'.")

                try:
                    change_type = ChangeType(raw_type)
                except ValueError as exc:
                    raise ValueError(f"Unsupported change type: {raw_type}") from exc

                content = change_obj.get("content", "")
                if not isinstance(content, str):
                    raise ValueError("Each change 'content' must be a string.")

                changes.append(Change(type=change_type, content=content))

            hunks.append(
                DiffHunk(
                    old_start=old_start,
                    old_length=old_length,
                    new_start=new_start,
                    new_length=new_length,
                    changes=changes,
                )
            )

        files.append(DiffFile(path=path, hunks=hunks, language=language))

    return files


if __name__ == "__main__":
    sys.exit(main())
