import unittest

from spandiff.normalization import OperationObservation, group_operations


class GroupingTests(unittest.TestCase):
    def test_reordering_does_not_change_multiset_groups(self):
        observations = [
            OperationObservation("db", "internal", "sql", "select from orders"),
            OperationObservation("http", "client", "request", "GET /users/{id}"),
            OperationObservation("db", "internal", "sql", "select from orders"),
        ]
        first = group_operations(observations)
        second = group_operations(reversed(observations))
        self.assertEqual([(g.group_id, len(g.members)) for g in first], [(g.group_id, len(g.members)) for g in second])

    def test_explicit_operation_id_takes_precedence(self):
        groups = group_operations([
            OperationObservation("db", "internal", "sql", "shape-a", operation_id="orders.lookup"),
            OperationObservation("db", "internal", "sql", "shape-b", operation_id="orders.lookup"),
        ])
        self.assertEqual(len(groups), 1)
        self.assertFalse(groups[0].ambiguous)


if __name__ == "__main__":
    unittest.main()
