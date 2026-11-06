import unittest

from spandiff.security import DestinationError, DestinationPolicy


class DestinationTests(unittest.TestCase):
    def setUp(self):
        self.policy = DestinationPolicy.from_hosts(["substitute.test"])

    def test_approved_destination_strips_query(self):
        self.assertEqual(self.policy.validate("https://substitute.test/orders?token=secret"), "https://substitute.test/orders")

    def test_unapproved_and_private_destinations_fail(self):
        with self.assertRaises(DestinationError):
            self.policy.validate("https://production.test/orders")
        with self.assertRaises(DestinationError):
            self.policy.validate("http://substitute.test/orders", resolver=lambda host: ["127.0.0.1"])

    def test_redirect_to_alternate_host_fails(self):
        with self.assertRaisesRegex(DestinationError, "redirect changes host"):
            self.policy.validate_redirect("https://substitute.test/orders", "https://other.test/steal")


if __name__ == "__main__":
    unittest.main()
