from pathlib import Path
import subprocess
import tempfile
import unittest

from spandiff.orchestration import ResolvedRevision, RevisionError, RevisionManager


COMMIT = "a" * 40


class FakeGit:
    def __init__(self, returncode=0, stdout=COMMIT, stderr=""):
        self.calls = []
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

    def __call__(self, args, cwd):
        self.calls.append((tuple(args), cwd))
        return subprocess.CompletedProcess(args, self.returncode, self.stdout, self.stderr)


class RevisionTests(unittest.TestCase):
    def test_resolves_and_persists_commit_ids_without_shell(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            repo.mkdir()
            root = Path(directory) / "owned"
            fake = FakeGit()
            manager = RevisionManager(repo, root, fake)
            resolved = manager.resolve("baseline", "main")
            manager.persist(root / "manifest.json", [resolved])
            self.assertEqual(resolved.commit, COMMIT)
            self.assertEqual(fake.calls[0][0], ("git", "rev-parse", "--verify", "main^{commit}"))
            self.assertEqual((root / "manifest.json").exists(), True)

    def test_invalid_reference_stops_before_worktree_creation(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            repo.mkdir()
            fake = FakeGit(returncode=128, stdout="", stderr="unknown ref")
            manager = RevisionManager(repo, Path(directory) / "owned", fake)
            with self.assertRaisesRegex(RevisionError, "invalid revision reference"):
                manager.resolve("candidate", "missing")
            self.assertEqual(len(fake.calls), 1)
            self.assertFalse((Path(directory) / "owned" / "worktrees").exists())

    def test_worktree_destination_is_owned_and_removable(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            repo.mkdir()
            root = Path(directory) / "owned"
            fake = FakeGit()
            manager = RevisionManager(repo, root, fake)
            worktree = manager.create(ResolvedRevision("candidate", "HEAD", COMMIT))
            manager.remove(worktree)
            self.assertEqual(fake.calls[0][0][:4], ("git", "worktree", "add", "--detach"))
            self.assertEqual(fake.calls[1][0][:4], ("git", "worktree", "remove", "--force"))


if __name__ == "__main__":
    unittest.main()
