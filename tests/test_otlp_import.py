import json
import unittest

from spandiff.collection import ImportValidationError, import_otlp_json


def payload(extra=None):
    span = {
        "traceId": "0" * 32, "spanId": "1" * 16, "name": "GET /orders",
        "startTimeUnixNano": "10", "endTimeUnixNano": "20",
        "attributes": {"http.method": "GET", "authorization": "seeded-secret", "db.statement": "SELECT secret"},
    }
    if extra:
        span.update(extra)
    return json.dumps({"resourceSpans": [{"resource": {"attributes": {"service.name": "orders", "host.name": "private"}}, "scopeSpans": [{"spans": [span]}]}]})


class OtlpImportTests(unittest.TestCase):
    def test_valid_import_sanitizes_and_deduplicates(self):
        document = json.loads(payload())
        document["resourceSpans"][0]["scopeSpans"][0]["spans"].append(document["resourceSpans"][0]["scopeSpans"][0]["spans"][0])
        result = import_otlp_json(json.dumps(document))
        self.assertEqual(len(result.spans), 1)
        self.assertEqual(result.issues[0].code, "duplicate_span")
        self.assertEqual(result.spans[0].attributes, {"http.method": "GET"})
        self.assertNotIn("seeded-secret", repr(result))

    def test_conflicting_duplicate_is_incomplete(self):
        document = json.loads(payload())
        second = dict(document["resourceSpans"][0]["scopeSpans"][0]["spans"][0])
        second["name"] = "different"
        document["resourceSpans"][0]["scopeSpans"][0]["spans"].append(second)
        result = import_otlp_json(json.dumps(document))
        self.assertFalse(result.complete)
        self.assertEqual(result.issues[0].code, "conflicting_duplicate_span")

    def test_malformed_and_oversized_inputs_fail(self):
        with self.assertRaisesRegex(ImportValidationError, "invalid JSON"):
            import_otlp_json("{")
        with self.assertRaisesRegex(ImportValidationError, "max_bytes"):
            import_otlp_json(payload(), max_bytes=10)
        with self.assertRaisesRegex(ImportValidationError, "invalid traceId"):
            import_otlp_json(payload({"traceId": "bad"}))


if __name__ == "__main__":
    unittest.main()
