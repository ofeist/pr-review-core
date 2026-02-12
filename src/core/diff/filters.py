# core/diff/filters.py

import fnmatch
from typing import List

from core.diff.types import DiffFile

# Hardcoded ignore patterns
IGNORE_PATTERNS = [
    "package-lock.json",
    "yarn.lock",
    "poetry.lock",
    "node_modules/*",
    "vendor/*",
    "dist/*",
    "build/*",
    "*.min.js",
    "*.min.css",
]


def filter_diff_files(files: List[DiffFile]) -> List[DiffFile]:
    """
    Remove files matching ignore patterns.
    """
    filtered = []

    for file in files:
        if _should_ignore(file.path):
            continue
        filtered.append(file)

    return filtered


def _should_ignore(path: str) -> bool:
    for pattern in IGNORE_PATTERNS:
        if fnmatch.fnmatch(path, pattern) or path.startswith(pattern.rstrip("/*")):
            return True
    return False
