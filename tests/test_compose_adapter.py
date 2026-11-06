from pathlib import Path
import subprocess
import tempfile
import unittest

from spandiff.adapters import AdapterError, ComposeAdapter
from spandiff.config import parse_config


CONFIG = """
schema_version: 1
project: orders-api
adapter: fastapi-compose
compose_file: compose.yml
app_service: api
health_path: /health
fixtures: fixtures-v1
credentials:
  token: ORDERS_TEST_TOKEN
scenarios:
  read:
    method: GET
    path: /orders
limits:
  readiness_timeout_seconds: 1
"""


class ComposeAdapterTests(unittest.TestCase):
    def test_commands_are_unique_and_credentials_stay_in_memory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "compose.yml").write_text("services: {}", encoding="utf-8")
            calls = []
            def runner(args, cwd, environment):
                calls.append((args, environment))
                return subprocess.CompletedProcess(args, 0)
            adapter = ComposeAdapter(parse_config(CONFIG), root, "exp-1", runner)
            adapter.start({"ORDERS_TEST_TOKEN": "secret-value"})
        self.assertIn("spandiff-orders-api-exp-1", calls[0][0])
        self.assertNotIn("secret-value", repr(calls[0][0]))
        self.assertEqual(calls[0][1], {"ORDERS_TEST_TOKEN": "secret-value"})

    def test_missing_compose_or_credential_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            adapter = ComposeAdapter(parse_config(CONFIG), root, "exp-1", lambda *args: None)
            with self.assertRaises(AdapterError):
                adapter.validate()
            with self.assertRaisesRegex(AdapterError, "missing environment reference"):
                adapter.approved_environment({})

    def test_readiness_is_bounded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "compose.yml").write_text("services: {}", encoding="utf-8")
            adapter = ComposeAdapter(parse_config(CONFIG), root, "exp-1", lambda *args: None)
            now = [0.0]
            with self.assertRaisesRegex(AdapterError, "timed out"):
                adapter.wait_ready(lambda: False, timeout_seconds=1, poll_seconds=1,
                                   clock=lambda: now[0], sleeper=lambda amount: now.__setitem__(0, now[0] + amount))


if __name__ == "__main__":
    unittest.main()
