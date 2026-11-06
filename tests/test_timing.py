import unittest

from spandiff.comparison.timing import TimingSample, TimingSpan, summarize_timings


class TimingTests(unittest.TestCase):
    def test_medians_batches_and_overlaps_are_summarized_separately(self):
        summary = summarize_timings("baseline", [
            TimingSample("s1", "batch-a", 100, (
                TimingSpan("root", 0, 80, kind="server"),
                TimingSpan("op-1", 10, 40), TimingSpan("op-2", 20, 60),
                TimingSpan("bg", 90, 140, background=True),
            )),
            TimingSample("s2", "batch-b", 200, (
                TimingSpan("root", 0, 100, kind="server"), TimingSpan("op", 0, 100),
            )),
        ])
        self.assertEqual(summary.sample_count, 2)
        self.assertEqual(dict(summary.batch_counts), {"batch-a": 1, "batch-b": 1})
        self.assertEqual(summary.client.median_ns, 150)
        self.assertEqual(summary.server.median_ns, 90)
        self.assertEqual(summary.operation.median_ns, 75)
        self.assertEqual(summary.background.median_ns, 50)

    def test_missing_and_incomparable_values_remain_unavailable(self):
        summary = summarize_timings("candidate", [
            TimingSample("s1", "batch-a", None, (), comparable=False),
            TimingSample("s2", "batch-a", 10, (TimingSpan("op", 1, 4),)),
        ])
        self.assertEqual(summary.sample_count, 1)
        self.assertIsNone(summary.server.median_ns)
        self.assertEqual(summary.operation.median_ns, 3)
        self.assertEqual(summary.background.available_samples, 0)


if __name__ == "__main__":
    unittest.main()
