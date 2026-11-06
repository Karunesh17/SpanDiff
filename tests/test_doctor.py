from pathlib import Path
import tempfile
import unittest

from spandiff.orchestration import run_doctor


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
limits: {}
"""


class DoctorTests(unittest.TestCase):
    def test_missing_prerequisites_are_actionable_without_values(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "compose.yml").write_text("services: {}", encoding="utf-8")
            config = root / "spandiff.yml"
            config.write_text(CONFIG, encoding="utf-8")
            report = run_doctor(config, environment={}, finder=lambda _: None)
        self.assertFalse(report.ok)
        text = " ".join(check.detail for check in report.checks)
        self.assertIn("missing prerequisite", text)
        self.assertIn("ORDERS_TEST_TOKEN", text)
        self.assertNotIn("secret-value", text)

    def test_doctor_does_not_start_application(self):
        calls = []
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "compose.yml").write_text("services: {}", encoding="utf-8")
            config = root / "spandiff.yml"
            config.write_text(CONFIG, encoding="utf-8")
            report = run_doctor(config, environment={"ORDERS_TEST_TOKEN": "secret-value"}, finder=lambda name: calls.append(name) or name)
        self.assertTrue(any(check.name == "compose_file" and check.ok for check in report.checks))
        self.assertEqual(calls, ["git", "docker", "docker-compose"])
        self.assertNotIn("secret-value", repr(report))


if __name__ == "__main__":
    unittest.main()
