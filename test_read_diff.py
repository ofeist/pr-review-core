# test_read_diff.py

from core.diff.read_diff import read_diff, DiffReadError

# --- TEST 1: read from string ---
try:
    raw_diff = read_diff(from_string="""
diff --git a/a.py b/a.py
@@ -0,0 +1 @@
+print('hi')
""")
    print("READ FROM STRING:")
    print(raw_diff)
except DiffReadError as e:
    print(f"Error: {e}")

# --- TEST 2: read from stdin/file ---
# Ovo testiraj ručno u CLI:
# git diff | python test_read_diff.py
# ili python test_read_diff.py
try:
    raw_diff_cli = read_diff()  # bez from_string
    if raw_diff_cli:
        print("\nREAD FROM CLI / STDIN:")
        print(raw_diff_cli)
    else:
        print("\nNo diff found from CLI / file")
except DiffReadError as e:
    print(f"Error: {e}")
