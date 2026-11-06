import os
from pathlib import Path
import tempfile
import unittest

from spandiff.evidence import OwnedStorage, StorageBoundaryError


class StorageBoundaryTests(unittest.TestCase):
    def test_legitimate_paths_and_spaces_resolve(self):
        with tempfile.TemporaryDirectory(prefix="SpanDiff home ") as directory:
            storage = OwnedStorage(directory)
            path = storage.resolve("orders-api", "exp-01", "evidence/baseline.jsonl")
            self.assertTrue(path.is_relative_to(Path(directory).resolve()))
            self.assertTrue(str(path).endswith(os.path.join("exp-01", "evidence", "baseline.jsonl")))

    def test_traversal_and_cross_project_paths_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = OwnedStorage(directory, "project-a")
            for relative in ("../other/secret", "C:\\outside"):
                with self.subTest(relative=relative), self.assertRaises(StorageBoundaryError):
                    storage.resolve("project-a", "exp-01", relative)
            with self.assertRaises(StorageBoundaryError):
                storage.resolve("project-b", "exp-01", "safe.json")

    def test_invalid_identifiers_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = OwnedStorage(directory)
            for project, experiment in (("../project", "exp-01"), ("project", "../exp"), ("", "exp-01"), ("project", "EXP")):
                with self.subTest(project=project, experiment=experiment), self.assertRaises(StorageBoundaryError):
                    storage.experiment_root(project, experiment)

    def test_symlink_escape_is_rejected_when_supported(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            outside = base.parent / f"{base.name}-outside"
            outside.mkdir()
            try:
                link = base / "projects" / "project" / "experiments" / "exp" / "escape"
                link.parent.mkdir(parents=True)
                link.symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symbolic links are unavailable")
            storage = OwnedStorage(base)
            with self.assertRaises(StorageBoundaryError):
                storage.resolve("project", "exp", "escape/file.json")
            outside.rmdir()


if __name__ == "__main__":
    unittest.main()
