import unittest

from spandiff.collection import assess_coverage


class CoverageTests(unittest.TestCase):
    def test_missing_roots_make_coverage_incomplete(self):
        result = assess_coverage(request_denominator=10, rooted_requests=9)
        self.assertFalse(result.complete)
        self.assertIn("missing_request_roots", result.reasons)

    def test_missing_denominator_does_not_invent_per_request_metrics(self):
        result = assess_coverage(request_denominator=None, rooted_requests=5)
        self.assertFalse(result.complete)
        self.assertIsNone(result.request_denominator)
        self.assertIn("missing_request_denominator", result.reasons)

    def test_complete_coverage_has_no_reasons(self):
        result = assess_coverage(request_denominator=5, rooted_requests=5)
        self.assertTrue(result.complete)
        self.assertEqual(result.reasons, ())


if __name__ == "__main__":
    unittest.main()
