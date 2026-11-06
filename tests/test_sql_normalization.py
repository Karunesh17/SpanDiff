import unittest

from spandiff.normalization import normalize_sql


class SqlNormalizationTests(unittest.TestCase):
    def test_literals_share_a_shape(self):
        first = normalize_sql("SELECT id FROM orders WHERE status = 'new' AND total > 10")
        second = normalize_sql("SELECT id FROM orders WHERE status = 'paid' AND total > 99")
        self.assertTrue(first.known)
        self.assertEqual(first.shape, second.shape)
        self.assertNotIn("new", first.shape)
        self.assertNotIn("10", first.shape)

    def test_joins_and_operators_remain_distinguishable(self):
        join = normalize_sql("SELECT o.id FROM orders o JOIN users u ON u.id = o.user_id")
        no_join = normalize_sql("SELECT o.id FROM orders o WHERE o.user_id = 1")
        self.assertNotEqual(join.shape, no_join.shape)

    def test_parse_failure_discards_raw_sql(self):
        result = normalize_sql("SELECT 'seeded-secret' FROM (")
        self.assertFalse(result.known)
        self.assertIsNone(result.shape)
        self.assertNotIn("seeded-secret", repr(result))


if __name__ == "__main__":
    unittest.main()
