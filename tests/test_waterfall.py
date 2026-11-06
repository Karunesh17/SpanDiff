import unittest

from spandiff.reporting.waterfall import WaterfallError, WaterfallSpan, render_waterfall


class WaterfallTests(unittest.TestCase):
    def test_overlapping_spans_keep_individual_units_and_text_order(self):
        html = render_waterfall([
            WaterfallSpan("a", "parallel <db>", 0, 50, "operation"),
            WaterfallSpan("b", "queue", 20, 80, "background", True),
        ], observation_start_ns=0, observation_end_ns=100)
        self.assertIn("Observation: 100 ns", html)
        self.assertIn("50 ns", html)
        self.assertIn("60 ns", html)
        self.assertIn("parallel &lt;db&gt;", html)
        self.assertLess(html.index("parallel &lt;db&gt;"), html.index("queue"))
        self.assertIn("background", html)
        self.assertIn("bars show position and individual duration, not a sum", html)

    def test_invalid_bounds_fail(self):
        with self.assertRaisesRegex(WaterfallError, "outside observation"):
            render_waterfall([WaterfallSpan("a", "bad", 0, 10)], observation_start_ns=5, observation_end_ns=20)


if __name__ == "__main__":
    unittest.main()
