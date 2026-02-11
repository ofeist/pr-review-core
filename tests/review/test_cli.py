import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

from core.review import cli


class ReviewCliTest(unittest.TestCase):
    def _run_main(self, argv, stdin_text=""):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with patch("sys.stdin", io.StringIO(stdin_text)):
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = cli.main(argv)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_cli_raw_diff_from_stdin_success(self) -> None:
        raw_diff = (
            "diff --git a/src/app.py b/src/app.py\n"
            "@@ -1,1 +1,2 @@\n"
            " def hello():\n"
            "+    return 'hi'\n"
        )

        code, out, err = self._run_main(["--input-format", "raw", "--adapter", "fake"], raw_diff)

        self.assertEqual(code, 0)
        self.assertIn("## AI Review", out)
        self.assertIn("### Summary", out)
        self.assertEqual(err, "")

    def test_cli_parsed_json_from_stdin_success(self) -> None:
        parsed_json = """
[
  {
    "path": "src/auth/login.py",
    "hunks": [
      {
        "old_start": 1,
        "old_length": 1,
        "new_start": 1,
        "new_length": 2,
        "changes": [
          {"type": "context", "content": "def login(user):"},
          {"type": "add", "content": "    return user"}
        ]
      }
    ]
  }
]
"""

        code, out, err = self._run_main(["--input-format", "parsed-json", "--adapter", "fake"], parsed_json)

        self.assertEqual(code, 0)
        self.assertIn("## AI Review", out)
        self.assertIn("### Findings", out)
        self.assertEqual(err, "")

    def test_cli_invalid_parsed_json_is_recoverable(self) -> None:
        code, out, err = self._run_main(["--input-format", "parsed-json"], "{not-json}")

        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("Invalid parsed JSON input", err)

    def test_cli_argument_validation_exit_code(self) -> None:
        code, out, err = self._run_main(["--max-changes-per-chunk", "0"], "x")

        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("must be > 0", err)


if __name__ == "__main__":
    unittest.main()
