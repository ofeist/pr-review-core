# test_parse_diff.py
# Mini end-to-end test: read raw diff string → parse → DiffFile[]

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from core.diff.parse_diff import parse_diff

# --- MINI RAW DIFF STRING ---
diff = """
diff --git a/test.py b/test.py
@@ -1,1 +1,2 @@
 print("hello")
+print("world")
"""

# --- PARSE DIFF ---
files = parse_diff(diff)

# --- PRINT OUTPUT ---
print("=== Parsed DiffFile[] ===")
for f in files:
    print(f)
    for hunk in f.hunks:
        print("  Hunk:", hunk.old_start, hunk.new_start)
        for change in hunk.changes:
            print("    ", change.type, repr(change.content))

# --- EXPECTED ---
# 1 file
# 1 hunk
# 2 changes: context + add
