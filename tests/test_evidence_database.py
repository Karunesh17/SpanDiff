import sqlite3
import tempfile
import unittest
from pathlib import Path

from spandiff.evidence import MigrationError, open_database


class EvidenceDatabaseTests(unittest.TestCase):
    def test_fresh_database_migrates_and_reopens(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.sqlite"
            connection = open_database(path)
            self.assertEqual(connection.execute("PRAGMA user_version").fetchone()[0], 1)
            self.assertEqual(connection.execute("PRAGMA foreign_keys").fetchone()[0], 1)
            tables = {row[0] for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )}
            self.assertIn("experiments", tables)
            connection.close()
            reopened = open_database(path)
            self.assertEqual(reopened.execute("PRAGMA user_version").fetchone()[0], 1)
            reopened.close()

    def test_future_schema_fails_without_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "future.sqlite"
            connection = sqlite3.connect(path)
            connection.execute("PRAGMA user_version = 99")
            connection.commit()
            connection.close()
            with self.assertRaisesRegex(MigrationError, "future database schema version 99"):
                open_database(path)
            check = sqlite3.connect(path)
            self.assertEqual(check.execute("PRAGMA user_version").fetchone()[0], 99)
            check.close()

    def test_cross_experiment_sample_reference_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            connection = open_database(Path(directory) / "evidence.sqlite")
            connection.execute("INSERT INTO projects VALUES ('p1', 'h1', 'one', '2026-01-01T00:00:00Z')")
            connection.execute("INSERT INTO projects VALUES ('p2', 'h2', 'two', '2026-01-01T00:00:00Z')")
            for experiment, project in (("e1", "p1"), ("e2", "p2")):
                connection.execute(
                    "INSERT INTO experiments VALUES (?, ?, 1, 'base', 'candidate', NULL, 'config', 'tool', 'created', 'unknown', 'none', 'now')",
                    (experiment, project),
                )
                connection.execute(
                    "INSERT INTO variants VALUES (?, 'baseline', 'rev', 'image', 'lock', 'fixture', 'env', '{}')",
                    (experiment,),
                )
            connection.execute(
                "INSERT INTO samples VALUES ('e1', 'baseline', 's1', 'scenario', 'batch', 1, 'pass', NULL, 'complete')"
            )
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    "INSERT INTO spans VALUES ('e2', 'baseline', 'trace', 'span', 's1', NULL, 'internal', 'api', 'scope', 1, 2, 'ok', '{}', 'span.jsonl')"
                )
            connection.commit()
            connection.close()

    def test_failed_migration_rolls_back(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "broken.sqlite"
            connection = sqlite3.connect(path)
            connection.execute("CREATE TABLE projects (project_id TEXT PRIMARY KEY)")
            connection.commit()
            connection.close()
            with self.assertRaises(MigrationError):
                open_database(path)
            check = sqlite3.connect(path)
            self.assertEqual(check.execute("PRAGMA user_version").fetchone()[0], 0)
            check.close()


if __name__ == "__main__":
    unittest.main()
