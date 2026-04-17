import io
from unittest.mock import patch

from core.diff.read_diff import read_diff


class BinaryStdin:
    def __init__(self, payload: bytes):
        self.buffer = io.BytesIO(payload)

    def isatty(self) -> bool:
        return False


def test_read_diff_from_binary_stdin_replaces_invalid_utf8_bytes():
    payload = (
        b"diff --git a/test.txt b/test.txt\n"
        b"@@ -0,0 +1,2 @@\n"
        b"+normal line\n"
        b"+bad line: \xff\xfe\xfd\n"
    )

    with patch("sys.stdin", BinaryStdin(payload)):
        result = read_diff()

    assert "+normal line" in result
    assert "+bad line: \ufffd\ufffd\ufffd" in result


def test_read_diff_from_file_replaces_invalid_utf8_bytes(tmp_path):
    diff_path = tmp_path / "pr.diff"
    diff_path.write_bytes(
        b"diff --git a/test.txt b/test.txt\n"
        b"@@ -0,0 +1,1 @@\n"
        b"+bad line: \xff\n"
    )

    result = read_diff(from_file=str(diff_path))

    assert "+bad line: \ufffd" in result
