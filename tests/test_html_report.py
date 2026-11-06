import unittest

from spandiff.reporting import ResultV1, render_html


class HtmlReportTests(unittest.TestCase):
    def test_report_is_self_contained_and_escapes_hostile_strings(self):
        html = render_html(ResultV1(
            "exp-<script>", "incomplete", ("base<&", "candidate"),
            {"complete": False, "reason": "missing <root>"},
            ({"finding_id": "f&1", "rule_id": "new", "uncertainty": "high"},),
            {"source": "fixture </script>"}, "pending"
        ))
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("state-incomplete", html)
        self.assertIn("state-cleanup", html)
        self.assertNotIn("<script", html.lower())
        self.assertNotIn("src=\"http", html.lower())
        self.assertNotIn("href=\"http", html.lower())

    def test_empty_sections_remain_semantic(self):
        html = render_html(ResultV1("exp", "complete", (), {}, (), {}, "not_applicable"))
        self.assertIn("<h2>Variants</h2>", html)
        self.assertIn("<h2>Coverage summary</h2>", html)
        self.assertIn("<h2>Findings</h2>", html)

    def test_findings_link_to_sample_details_and_missing_source_is_explicit(self):
        html = render_html(ResultV1(
            "exp", "complete", ("baseline",), {},
            ({"finding_id": "f1", "rule_id": "added", "sample_ids": ["s1"], "uncertainty": "medium"},),
            {}, "clean"
        ))
        self.assertIn('href="#finding-f1"', html)
        self.assertIn('id="finding-f1"', html)
        self.assertIn('href="#sample-s1"', html)
        self.assertIn('id="sample-s1"', html)
        self.assertIn("Not recorded", html)


if __name__ == "__main__":
    unittest.main()
