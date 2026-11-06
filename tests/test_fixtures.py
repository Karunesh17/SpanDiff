from pathlib import Path
import subprocess
import tempfile
import unittest

from spandiff.config import parse_config
from spandiff.orchestration import FixtureManager


BASE = """
schema_version: 1
project: orders-api
adapter: fastapi-compose
compose_file: compose.yml
app_service: api
health_path: /health
fixtures: fixtures-v1
prepare_command: [python, prepare.py]
reset_command: [python, reset.py]
scenarios:
  read:
    method: GET
    path: /orders
  write:
    method: POST
    path: /orders
    write: true
limits: {}
"""


class FixtureTests(unittest.TestCase):
    def test_prepare_and_write_reset_use_bounded_argv(self):
        calls = []
        def runner(args, cwd, timeout):
            calls.append((args, timeout))
            return subprocess.CompletedProcess(args, 0)
        with tempfile.TemporaryDirectory() as directory:
            manager = FixtureManager(parse_config(BASE), Path(directory), runner)
            self.assertTrue(manager.prepare().comparable)
            self.assertTrue(manager.before_sample(parse_config(BASE).scenarios["write"]).comparable)
        self.assertEqual([call[0] for call in calls], [("python", "prepare.py"), ("python", "reset.py")])

    def test_failed_reset_suppresses_comparability(self):
        def runner(args, cwd, timeout):
            return subprocess.CompletedProcess(args, 1)
        with tempfile.TemporaryDirectory() as directory:
            manager = FixtureManager(parse_config(BASE), Path(directory), runner)
            outcome = manager.before_sample(parse_config(BASE).scenarios["write"])
        self.assertFalse(outcome.comparable)
        self.assertFalse(outcome.reset_ok)

    def test_read_only_scenario_does_not_need_reset(self):
        read_only = BASE.replace("reset_command: [python, reset.py]", "").replace("  write:\n    method: POST\n    path: /orders\n    write: true\n", "")
        config = parse_config(read_only)
        with tempfile.TemporaryDirectory() as directory:
            outcome = FixtureManager(config, Path(directory), None).before_sample(config.scenarios["read"])
        self.assertTrue(outcome.comparable)


if __name__ == "__main__":
    unittest.main()
