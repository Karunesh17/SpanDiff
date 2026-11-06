import unittest

from spandiff.comparison.calibration import CalibrationError, calibrate


class CalibrationTests(unittest.TestCase):
    def test_reproducible_workload_qualified_overhead_is_descriptive(self):
        result = calibrate("orders GET /orders, 2 deterministic orders", [100, 110, 105], [120, 130, 125])
        self.assertEqual(result.uninstrumented_median_ns, 105)
        self.assertEqual(result.instrumented_median_ns, 125)
        self.assertEqual(result.overhead_ns, 20)
        self.assertEqual(result.uninstrumented_samples, 3)
        self.assertIn("advisory", result.recommendation)
        self.assertNotIn("p99", result.to_dict())

    def test_noisy_data_is_labeled_and_invalid_batches_fail(self):
        self.assertEqual(calibrate("workload", [1, 100], [2, 200], noise_ratio=0.2).noise_label, "noisy")
        with self.assertRaisesRegex(CalibrationError, "both batches"):
            calibrate("workload", [], [1])


if __name__ == "__main__":
    unittest.main()
