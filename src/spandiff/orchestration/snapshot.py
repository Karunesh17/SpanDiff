"""Safe dirty-worktree snapshot manifests."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import subprocess
from collections.abc import Callable, Sequence

from .revisions import RevisionError


_EXCLUDED_PARTS = {".venv", "__pycache__", "build", "dist", "node_modules"}


@dataclass(frozen=True)
class DirtySnapshot:
    base_commit: str
    tracked_patch_sha256: str
    approved_untracked: tuple[str, ...]
    excluded_untracked: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "mode": "dirty-snapshot",
            "base_commit": self.base_commit,
            "tracked_patch_sha256": self.tracked_patch_sha256,
            "approved_untracked": list(self.approved_untracked),
            "excluded_untracked": list(self.excluded_untracked),
        }


def _default_runner(args: Sequence[str], cwd: Path) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(args, cwd=cwd, capture_output=True, check=False)


class DirtySnapshotter:
    def __init__(self, repository: str | Path,
                 runner: Callable[[Sequence[str], Path], subprocess.CompletedProcess[bytes]] | None = None):
        self.repository = Path(repository).resolve(strict=True)
        self.runner = runner or _default_runner

    def capture(self, base_commit: str, approved_untracked: Sequence[str] = ()) -> DirtySnapshot:
        diff = self.runner(("git", "diff", "--binary", "--no-ext-diff", base_commit, "--"), self.repository)
        if diff.returncode != 0:
            raise RevisionError("candidate: cannot read tracked patch")
        untracked_result = self.runner(("git", "ls-files", "--others", "--exclude-standard", "-z"), self.repository)
        if untracked_result.returncode != 0:
            raise RevisionError("candidate: cannot list untracked files")
        untracked = tuple(item for item in untracked_result.stdout.decode("utf-8").split("\0") if item)
        approved = []
        excluded = []
        requested = set(approved_untracked)
        for item in untracked:
            if self._excluded(item):
                excluded.append(item)
            elif item in requested:
                approved.append(item)
        missing = sorted(requested - set(untracked))
        if missing:
            raise RevisionError(f"candidate: approved untracked file is not present: {missing[0]}")
        return DirtySnapshot(base_commit, hashlib.sha256(diff.stdout).hexdigest(), tuple(sorted(approved)), tuple(sorted(excluded)))

    def write_manifest(self, path: str | Path, snapshot: DirtySnapshot) -> None:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(snapshot.to_dict(), sort_keys=True, indent=2) + "\n", encoding="utf-8")

    @staticmethod
    def _excluded(path: str) -> bool:
        parts = Path(path).parts
        name = Path(path).name.lower()
        return any(part.lower() in _EXCLUDED_PARTS for part in parts) or name == ".env" or name.startswith(".env.") or "credential" in name or "secret" in name
