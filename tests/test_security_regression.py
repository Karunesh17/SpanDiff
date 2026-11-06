import tempfile
import unittest
from pathlib import Path

from spandiff.config import ConfigurationError, parse_config
from spandiff.evidence.storage import OwnedStorage, StorageBoundaryError
from spandiff.reporting import ResultV1, render_html
from spandiff.security.sanitizer import safe_diagnostic, sanitize_span_attributes


class SecurityRegressionTests(unittest.TestCase):
    def test_seeded_secret_is_absent_from_success_and_failure_surfaces(self):
        secret = "seeded-secret-123"
        clean = sanitize_span_attributes({"http.route": "/orders", "authorization": secret, "token": secret})
        diagnostic = safe_diagnostic(f"request failed with {secret}", (secret,))
        report = render_html(ResultV1("exp", "incomplete", ("baseline", "candidate"), {"error": diagnostic}, (), {"detail": diagnostic}, "pending"))
        self.assertNotIn(secret, repr(clean))
        self.assertNotIn(secret, diagnostic)
        self.assertNotIn(secret, report)

    def test_path_escape_and_cross_project_access_fail_safely(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = OwnedStorage(directory, "project-a")
            with self.assertRaises(StorageBoundaryError):
                storage.resolve("project-a", "exp-1", "../../outside")
            with self.assertRaises(StorageBoundaryError):
                storage.project_root("project-b")

    def test_limits_and_malformed_config_are_rejected(self):
        config = """
schema_version: 1
project: orders
adapter: fastapi-compose
compose_file: compose.yml
app_service: app
health_path: /health
fixtures: fixtures
scenarios:
  read:
    method: GET
    path: /orders
limits:
  max_spans: 0
"""
        with self.assertRaisesRegex(ConfigurationError, "limits.max_spans"):
            parse_config(config)


if __name__ == "__main__":
    unittest.main()
