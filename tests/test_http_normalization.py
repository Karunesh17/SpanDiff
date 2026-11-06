import unittest

from spandiff.normalization import normalize_http


class HttpNormalizationTests(unittest.TestCase):
    def test_query_values_are_removed_and_ids_are_templated(self):
        identity = normalize_http("orders", "get", "/orders/123?token=seeded-secret")
        self.assertTrue(identity.known)
        self.assertEqual(identity.method, "GET")
        self.assertEqual(identity.path, "/orders/{id}")
        self.assertNotIn("seeded-secret", repr(identity))

    def test_explicit_templates_and_methods_remain_distinct(self):
        first = normalize_http("orders", "GET", "/orders/{order_id}")
        second = normalize_http("orders", "POST", "/orders/{order_id}")
        self.assertNotEqual(first.method, second.method)
        self.assertEqual(first.path, second.path)

    def test_unapproved_or_ambiguous_routes_are_unknown(self):
        self.assertFalse(normalize_http("production", "GET", "/orders", allowed_services={"orders"}).known)
        self.assertFalse(normalize_http("orders", "GET", "/orders/{bad route}").known)


if __name__ == "__main__":
    unittest.main()
