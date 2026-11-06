import unittest

from spandiff.config import ConfigurationError, parse_config


VALID = """
schema_version: 1
project: orders-api
adapter: fastapi-compose
compose_file: compose.yml
app_service: api
health_path: /health
fixtures: fixtures-v1
reset_command: [python, reset.py]
credentials:
  token: ORDERS_TEST_TOKEN
scenarios:
  read:
    method: GET
    path: /orders
    expected_status: 200
    write: false
limits: {}
"""


class ConfigTests(unittest.TestCase):
    def test_valid_fixture_loads_without_resolving_credentials(self):
        config = parse_config(VALID)
        self.assertEqual(config.project, "orders-api")
        self.assertEqual(config.credentials, {"token": "ORDERS_TEST_TOKEN"})
        self.assertEqual(config.scenarios["read"].assertions.status, 200)

    def test_unknown_fields_have_actionable_paths(self):
        with self.assertRaisesRegex(ConfigurationError, r"config\.scenarios\.read\.typo: unknown field"):
            parse_config(VALID.replace("    write: false", "    write: false\n    typo: true"))

    def test_unsupported_schema_version_is_rejected(self):
        with self.assertRaisesRegex(ConfigurationError, "config.schema_version"):
            parse_config(VALID.replace("schema_version: 1", "schema_version: 2"))

    def test_write_requires_reset_contract(self):
        with self.assertRaisesRegex(ConfigurationError, "write.*reset_command"):
            parse_config(VALID.replace("reset_command: [python, reset.py]\n", "").replace("write: false", "write: true"))

    def test_commands_are_argument_arrays(self):
        with self.assertRaisesRegex(ConfigurationError, "prepare_command.*argument array"):
            parse_config(VALID.replace("limits: {}", "prepare_command: python reset.py\nlimits: {}"))

    def test_secret_value_shape_is_rejected(self):
        with self.assertRaisesRegex(ConfigurationError, r"credentials\.token"):
            parse_config(VALID.replace("token: ORDERS_TEST_TOKEN", "token: actual-secret-value"))

    def test_malformed_yaml_is_rejected(self):
        with self.assertRaisesRegex(ConfigurationError, "invalid YAML"):
            parse_config("schema_version: [")


if __name__ == "__main__":
    unittest.main()
