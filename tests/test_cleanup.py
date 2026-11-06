import unittest

from spandiff.evidence.database import open_database
from spandiff.orchestration.cleanup import CleanupError, CleanupManager
from spandiff.orchestration.lifecycle import LifecycleJournal


class CleanupTests(unittest.TestCase):
    def setUp(self):
        self.connection = open_database(":memory:")
        self.connection.execute("INSERT INTO projects VALUES ('p', 'project', 'fingerprint', '2026-01-01')")
        self.connection.execute(
            "INSERT INTO experiments (experiment_id, project_id, schema_version, baseline_revision, "
            "candidate_revision, config_hash, tool_version, state, result_state, cleanup_state, created_at) "
            "VALUES ('e', 'p', 1, 'baseline', 'candidate', 'config', 'tool', 'created', "
            "'incomplete', 'not_started', '2026-01-01')"
        )
        self.connection.commit()

    def tearDown(self):
        self.connection.close()

    def test_cancel_cleans_registered_resources_and_repeated_cleanup_is_safe(self):
        calls = []
        lifecycle = LifecycleJournal(self.connection, "e")
        lifecycle.register_resource("container-1", "container", "token-1", "compose://container-1")
        lifecycle.register_resource("network-1", "network", "token-1", "compose://network-1")
        manager = CleanupManager(self.connection, "e", {
            "container": lambda resource: calls.append((resource.resource_id, resource.ownership_token)),
            "network": lambda resource: calls.append((resource.resource_id, resource.ownership_token)),
        })
        manager.cancel()
        report = manager.cleanup()
        self.assertEqual(report.pending, ())
        self.assertEqual(calls, [("container-1", "token-1"), ("network-1", "token-1")])
        self.assertEqual(manager.cleanup().cleaned, ("container-1", "network-1"))
        self.assertEqual(calls.count(("container-1", "token-1")), 1)
        self.assertEqual(manager.journal.state().result_state, "incomplete")

    def test_failure_is_pending_and_unknown_resource_cannot_be_targeted(self):
        LifecycleJournal(self.connection, "e").register_resource(
            "container-1", "container", "token-1", "compose://container-1"
        )
        manager = CleanupManager(self.connection, "e", {
            "container": lambda resource: (_ for _ in ()).throw(RuntimeError("failure"))
        })
        report = manager.cleanup()
        self.assertEqual(report.pending, ("container-1",))
        self.assertEqual(manager.journal.state().cleanup_state, "pending")
        with self.assertRaisesRegex(CleanupError, "not registered"):
            manager.cleanup(("foreign-resource",))


if __name__ == "__main__":
    unittest.main()
