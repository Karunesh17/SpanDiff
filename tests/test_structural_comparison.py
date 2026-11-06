import unittest

from spandiff.comparison import GroupSummary, compare_groups


class StructuralComparisonTests(unittest.TestCase):
    def test_added_and_n_plus_one_findings_have_samples(self):
        result = compare_groups(
            {"db": GroupSummary(1, 0, ("b1",))},
            {"db": GroupSummary(3, 0, ("c1",)), "http": GroupSummary(1, 0, ("c2",))},
        )
        self.assertEqual([finding.rule_id for finding in result], ["changed_call_count", "added_operation"])
        self.assertEqual(result[0].sample_ids, ("b1", "c1"))
        self.assertEqual(result[1].sample_ids, ("c2",))

    def test_unchanged_groups_do_not_create_findings(self):
        result = compare_groups(
            {"db": GroupSummary(1, 0, ("b1",))},
            {"db": GroupSummary(1, 0, ("c1",))},
        )
        self.assertEqual(result, ())


if __name__ == "__main__":
    unittest.main()
