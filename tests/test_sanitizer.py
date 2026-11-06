import unittest

from spandiff.security import (
    safe_diagnostic,
    sanitize_resource_attributes,
    sanitize_span_attributes,
    sanitize_url,
)


class SanitizerTests(unittest.TestCase):
    def test_span_sanitizer_is_default_deny(self):
        secret = "seeded-token-123"
        clean = sanitize_span_attributes({
            "http.method": "GET",
            "http.route": "/orders/{id}",
            "authorization": secret,
            "http.query": "token=" + secret,
            "db.statement": "SELECT secret",
            "request.body": secret,
            "unknown.attribute": secret,
        })
        self.assertEqual(clean, {"http.method": "GET", "http.route": "/orders/{id}"})
        self.assertNotIn(secret, repr(clean))

    def test_resource_sanitizer_keeps_only_identity_metadata(self):
        clean = sanitize_resource_attributes({
            "service.name": "orders-api",
            "service.version": "1",
            "authorization": "secret",
            "host.name": "developer-machine",
        })
        self.assertEqual(clean, {"service.name": "orders-api", "service.version": "1"})

    def test_url_and_diagnostic_redaction(self):
        secret = "seeded-cookie"
        self.assertEqual(sanitize_url("https://example.test/orders?id=" + secret), "https://example.test/orders")
        diagnostic = safe_diagnostic("request failed token=" + secret, [secret])
        self.assertNotIn(secret, diagnostic)
        self.assertIn("<redacted>", diagnostic)


if __name__ == "__main__":
    unittest.main()
