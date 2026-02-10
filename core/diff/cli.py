# core/diff/cli.py

import json
import sys
from core.diff.read_diff import read_diff, DiffReadError
from core.diff.parse_diff import parse_diff
from core.diff.filters import filter_diff_files

def main():
    try:
        # 1️⃣ read diff
        raw = read_diff()
    except DiffReadError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # 2️⃣ parse diff
    files = parse_diff(raw)

    # 3️⃣ filter noise
    filtered_files = filter_diff_files(files)

    # 4️⃣ serialize to JSON
    output = [
        {
            "path": f.path,
            "hunks": [
                {
                    "old_start": h.old_start,
                    "old_length": h.old_length,
                    "new_start": h.new_start,
                    "new_length": h.new_length,
                    "changes": [{"type": c.type.value, "content": c.content} for c in h.changes],
                }
                for h in f.hunks
            ],
        }
        for f in filtered_files
    ]

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
