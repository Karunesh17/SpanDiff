from pathlib import Path
import tempfile
import unittest

from spandiff.evidence import open_database
from spandiff.orchestration import LifecycleError, LifecycleJournal


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.connection = open_database(Path(self.directory.name) / "evidence.sqlite")
        self.connection.execute("INSERT INTO projects VALUES ('p', 'h', 'project', 'now')")
        self.connection.execute("INSERT INTO experiments VALUES ('e', 'p', 1, 'base', 'candidate', NULL, 'cfg', 'tool', 'created', 'unknown', 'none', 'now')")
        self.connection.commit()
        self.journal = LifecycleJournal(self.connection, "e")

    def tearDown(self):
        self.connection.close()
        self.directory.cleanup()

    def test_transitions_are_durable_and_resources_are_owned(self):
        self.assertEqual(self.journal.transition("prepared").stage, "prepared")
        self.journal.register_resource("container-1", "container", "token-1", "compose://container-1")
        self.journal.transition("running")
        state = self.journal.transition("finalized", result_state="complete")
        self.assertEqual(state.result_state, "complete")
        self.assertEqual(self.connection.execute("SELECT COUNT(*) FROM lifecycle_events").fetchone()[0], 3)

    def test_invalid_transition_and_cleanup_pending_preserve_result(self):
        with self.assertRaises(LifecycleError):
            self.journal.transition("finalized")
        self.journal.transition("failed", result_state="failed")
        state = self.journal.transition("cleanup_pending", cleanup_state="pending")
        self.assertEqual(state.result_state, "failed")
        self.assertEqual(state.cleanup_state, "pending")


if __name__ == "__main__":
    unittest.main()
