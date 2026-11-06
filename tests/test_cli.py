"""Verify the entry point in both source and installed environments."""

import subprocess
import sys
import json
import tempfile
from pathlib import Path
import unittest

from spandiff import __version__
from spandiff.cli import main


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "spandiff", *args],
            capture_output=True, text=True, timeout=10,
        )

    def test_version_flag(self):
        result = self.run_cli("--version")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), f"SpanDiff {__version__}")
        self.assertEqual(result.stderr, "")

    def test_version_command(self):
        result = self.run_cli("version")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), f"SpanDiff {__version__}")

    def test_help_and_empty_command(self):
        for args in [("--help",), ()]:
            with self.subTest(args=args):
                result = self.run_cli(*args)
                self.assertEqual(result.returncode, 0)
                self.assertIn("usage: spandiff", result.stdout)
                self.assertIn("not implemented yet", result.stdout)

    def test_unknown_command_is_an_error(self):
        result = self.run_cli("does-not-exist")
        self.assertEqual(result.returncode, 3)
        self.assertIn("invalid choice", result.stderr)

    def test_callable_entry_point(self):
        self.assertEqual(main(["version"]), 0)

    def test_import_pair_emits_incomplete_result_without_request_denominator(self):
        payload = '{"resourceSpans": []}'
        with tempfile.TemporaryDirectory() as directory:
            baseline = Path(directory) / "baseline.json"
            candidate = Path(directory) / "candidate.json"
            baseline.write_text(payload, encoding="utf-8")
            candidate.write_text(payload, encoding="utf-8")
            result = self.run_cli("import", "--baseline", str(baseline), "--candidate", str(candidate))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["result_state"], "incomplete")

    def test_import_invalid_input_returns_three(self):
        with tempfile.TemporaryDirectory() as directory:
            baseline = Path(directory) / "baseline.json"
            candidate = Path(directory) / "candidate.json"
            baseline.write_text("{", encoding="utf-8")
            candidate.write_text("{}", encoding="utf-8")
            result = self.run_cli("import", "--baseline", str(baseline), "--candidate", str(candidate))
        self.assertEqual(result.returncode, 3)


if __name__ == "__main__":
    unittest.main()
