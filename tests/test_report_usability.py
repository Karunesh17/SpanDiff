import unittest

from spandiff.reporting import ResultV1, render_html


class ReportUsabilityTests(unittest.TestCase):
    def test_long_unicode_zero_and_malformed_content_stays_readable(self):
        long_name = "注文-" + ("very-long-name-" * 20) + "🚀"
        html = render_html(ResultV1(
            "exp-零", "incomplete", (long_name,), {"complete": False},
            ({"finding_id": "f<svg>", "rule_id": "x&y", "uncertainty": "unknown <b>"},),
            {"note": "<img src=x onerror=alert(1)> café"}, "cleanup_pending"
        ))
        self.assertIn("🚀", html)
        self.assertIn("&lt;img src=x onerror=alert(1)&gt;", html)
        self.assertIn("state-incomplete", html)
        self.assertIn("state-cleanup", html)
        self.assertIn("@media (max-width: 42rem)", html)
        self.assertIn("@media print", html)

    def test_empty_result_is_explicit_and_has_no_external_assets_or_scripts(self):
        html = render_html(ResultV1("empty", "complete", (), {}, (), {}, "not_applicable"))
        self.assertIn("No findings recorded", html)
        self.assertIn("No coverage data recorded", html)
        self.assertIn("None recorded", html)
        self.assertNotRegex(html.lower(), r"<(script|img|iframe|object|embed)\\b")
        self.assertNotRegex(html.lower(), r"(?:src|href)\\s*=\\s*['\"](?:https?:|//)")


if __name__ == "__main__":
    unittest.main()
