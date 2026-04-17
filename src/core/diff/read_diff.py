# core/diff/read_diff.py

import sys
from typing import Optional


class DiffReadError(Exception):
    """Raised when diff input cannot be read."""


def read_diff(
    *,
    from_file: Optional[str] = None,
    from_string: Optional[str] = None,
) -> str:
    """
    Read a raw git diff from one of the supported sources.

    Priority:
    1. from_string
    2. from_file
    3. stdin

    Returns:
        Raw diff as a string.

    Raises:
        DiffReadError if no input is available or input is invalid.
    """

    if from_string is not None:
        if not isinstance(from_string, str):
            raise DiffReadError("from_string must be a string")
        return from_string.strip()

    if from_file is not None:
        try:
            with open(from_file, "rb") as f:
                return f.read().decode("utf-8", errors="replace").strip()
        except OSError as e:
            raise DiffReadError(f"Failed to read diff file: {e}") from e

    if not sys.stdin.isatty():
        try:
            if hasattr(sys.stdin, "buffer"):
                data = sys.stdin.buffer.read().decode("utf-8", errors="replace").strip()
            else:
                data = sys.stdin.read().strip()
        except OSError as e:
            raise DiffReadError(f"Failed to read diff from stdin: {e}") from e
        if data:
            return data

    raise DiffReadError(
        "No diff input provided. Use from_string, from_file, or pipe via stdin."
    )
