# test_sanity.py

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from core.diff.types import DiffFile, DiffHunk, Change, ChangeType

# Mini sanity-check
diff = DiffFile(
    path="src/auth/login.py",
    hunks=[
        DiffHunk(
            old_start=10,
            old_length=2,
            new_start=10,
            new_length=4,
            changes=[
                Change(ChangeType.ADD, "if not user:"),
                Change(ChangeType.ADD, "    return None"),
            ],
        )
    ],
    language="python",
)

# Ispis za provjeru
print(diff)
