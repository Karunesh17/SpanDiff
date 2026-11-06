import unittest

from spandiff.reporting import ResultValidationError, result_from_dict, result_from_json


VALID = {
    "schema_version": 1, "experiment_id": "exp-1", "result_state": "complete",
    "variants": ["baseline", "candidate"], "coverage": {"complete": True},
    "findings": [{"finding_id": "f1", "sample_ids": ["s1"], "uncertainty": "low"}],
    "provenance": {"source": "synthetic"}, "cleanup_state": "clean",
}


class ResultTests(unittest.TestCase):
    def test_result_round_trip_preserves_evidence_ids(self):
        result = result_from_dict(VALID)
        restored = result_from_json(result.to_json())
        self.assertEqual(restored.to_dict(), VALID)

    def test_unsupported_version_and_unsafe_values_fail(self):
        with self.assertRaisesRegex(ResultValidationError, "schema_version"):
            result_from_dict({**VALID, "schema_version": 2})
        with self.assertRaises(ResultValidationError):
            result_from_dict({**VALID, "coverage": {"bad": object()}})


if __name__ == "__main__":
    unittest.main()
