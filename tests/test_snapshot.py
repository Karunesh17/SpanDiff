from pathlib import Path
import hashlib
import subprocess
import tempfile
import unittest

from spandiff.orchestration import DirtySnapshotter, RevisionError


class FakeGit:
    def __init__(self, untracked=b"notes.txt\0.env\0build/out.bin\0"):
        self.untracked = untracked
        self.calls = []

    def __call__(self, args, cwd):
        self.calls.append(tuple(args))
        if args[1] == "diff":
            return subprocess.CompletedProcess(args, 0, b"patch contents", b"")
        return subprocess.CompletedProcess(args, 0, self.untracked, b"")


class SnapshotTests(unittest.TestCase):
    def test_snapshot_records_patch_digest_and_allowlist(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fake = FakeGit()
            snapshotter = DirtySnapshotter(root, fake)
            snapshot = snapshotter.capture("a" * 40, ["notes.txt"])
            self.assertEqual(snapshot.tracked_patch_sha256, hashlib.sha256(b"patch contents").hexdigest())
            self.assertEqual(snapshot.approved_untracked, ("notes.txt",))
            self.assertEqual(snapshot.excluded_untracked, (".env", "build/out.bin"))
            self.assertEqual(fake.calls[0][:3], ("git", "diff", "--binary"))

    def test_unapproved_or_missing_files_do_not_enter_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            snapshotter = DirtySnapshotter(Path(directory), FakeGit())
            snapshot = snapshotter.capture("a" * 40)
            self.assertEqual(snapshot.approved_untracked, ())
            with self.assertRaisesRegex(RevisionError, "not present"):
                snapshotter.capture("a" * 40, ["missing.py"])


if __name__ == "__main__":
    unittest.main()
