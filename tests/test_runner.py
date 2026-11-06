import unittest
from dataclasses import replace

from spandiff.collection import Response, ScenarioRunner
from spandiff.config import parse_config


CONFIG = """
schema_version: 1
project: orders-api
adapter: fastapi-compose
compose_file: compose.yml
app_service: api
health_path: /health
fixtures: fixtures-v1
scenarios:
  read:
    method: GET
    path: /orders
    assertions:
      status: 200
      json: {items: list}
limits: {}
"""


class RunnerTests(unittest.TestCase):
    def test_defaults_record_five_warmups_and_thirty_measured(self):
        scenario = parse_config(CONFIG).scenarios["read"]
        calls = []
        runner = ScenarioRunner(lambda method, path, headers, timeout: (calls.append(headers) or Response(200, {"items": "list"})), token_factory=lambda: "a" * 32)
        result = runner.run(scenario)
        self.assertEqual(len(result.warmups), 5)
        self.assertEqual(len(result.measured), 30)
        self.assertEqual(len(calls), 35)
        self.assertTrue(all(sample.assertion_ok for sample in result.measured))
        self.assertTrue(all(header["traceparent"].startswith("00-") for header in calls))

    def test_assertion_failure_is_explicit_and_write_resets_each_sample(self):
        scenario = replace(parse_config(CONFIG).scenarios["read"], samples=2, write=True)
        resets = []
        runner = ScenarioRunner(lambda *args: Response(500, {}), reset=lambda: resets.append(True) or True, token_factory=lambda: "b" * 32)
        result = runner.run(scenario)
        self.assertEqual(len(resets), 2)
        self.assertFalse(result.measured[0].assertion_ok)
        self.assertIn("expected status", result.measured[0].assertion_error)


if __name__ == "__main__":
    unittest.main()
