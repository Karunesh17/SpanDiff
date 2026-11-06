import unittest

from spandiff.collection import CollectorSession


class FlushTests(unittest.TestCase):
    def test_flush_finalizes_and_late_spans_are_quarantined(self):
        session = CollectorSession(lambda: True)
        self.assertTrue(session.accept("span"))
        result = session.flush(1)
        self.assertTrue(result.complete)
        self.assertFalse(session.accept("late"))
        self.assertEqual(session.flush(1).accepted_spans, 1)
        self.assertEqual(session.flush(1).quarantined_spans, 1)

    def test_flush_timeout_is_incomplete(self):
        now = [0.0]
        session = CollectorSession(lambda: now.__setitem__(0, now[0] + 1) or False, clock=lambda: now[0])
        result = session.flush(1)
        self.assertFalse(result.flushed)
        self.assertFalse(result.complete)


if __name__ == "__main__":
    unittest.main()
