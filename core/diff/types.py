# core/diff/types.py

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class ChangeType(str, Enum):
    ADD = "add"
    REMOVE = "remove"
    CONTEXT = "context"


@dataclass(frozen=True)
class Change:
    """
    Single line-level change inside a diff hunk.
    """
    type: ChangeType
    content: str


@dataclass(frozen=True)
class DiffHunk:
    """
    A contiguous block of changes in a file.
    """
    old_start: int
    old_length: int
    new_start: int
    new_length: int
    changes: List[Change]


@dataclass(frozen=True)
class DiffFile:
    """
    All changes related to a single file.
    """
    path: str
    hunks: List[DiffHunk]
    language: Optional[str] = None
