import unittest

from spandiff.reporting.verdict import VerdictError, evaluate_verdict


class VerdictTests(unittest.TestCase):
    def test_complete_budget_violation_is_exit_one(self):
        verdict = evaluate_verdict(complete=True, observed_counts={"n_plus_one": 3}, budgets={"n_plus_one": 1})
        self.assertEqual(verdict.state, "budget_violation")
        self.assertEqual(verdict.exit_code, 1)
        self.assertEqual(verdict.budget_violations, {"n_plus_one": 2})

    def test_incomplete_takes_precedence_and_timing_is_advisory(self):
        verdict = evaluate_verdict(complete=False, observed_counts={"added": 5}, budgets={"added": 0}, timing_warnings=("slow",))
        self.assertEqual((verdict.state, verdict.exit_code), ("incomplete", 2))
        self.assertEqual(verdict.timing_warnings, ("slow",))

    def test_pass_and_invalid_inputs(self):
        self.assertEqual(evaluate_verdict(complete=True, observed_counts={}, budgets={}, timing_warnings=("slow",)).exit_code, 0)
        with self.assertRaisesRegex(VerdictError, "observed_counts.x"):
            evaluate_verdict(complete=True, observed_counts={"x": -1}, budgets={})


if __name__ == "__main__":
    unittest.main()
