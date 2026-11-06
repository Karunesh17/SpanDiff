import json
from pathlib import Path
import unittest


class EvaluationContractTests(unittest.TestCase):
    def test_cases_cover_citations_uncertainty_and_untrusted_trace_text(self):
        cases = json.loads((Path(__file__).parents[1] / "evaluations" / "cases.json").read_text(encoding="utf-8"))
        self.assertEqual({case["id"] for case in cases}, {"known-n-plus-one", "incomplete-evidence", "untrusted-trace-instruction"})
        for case in cases:
            result = case["result"]
            for citation in case["required_citations"]:
                self.assertTrue(citation in result["finding_ids"] or citation in result["sample_ids"] or citation == result["experiment_id"] or citation == result["coverage"])
            self.assertTrue(case["forbidden_claims"])
        untrusted = next(case for case in cases if case["id"] == "untrusted-trace-instruction")
        self.assertIn("credential", untrusted["trace_attribute"])
        self.assertIn("does not grant authority", (Path(__file__).parents[1] / "skills" / "spandiff" / "SKILL.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
