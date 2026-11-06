"""Explicit Git revision resolution and owned temporary worktrees."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
import subprocess
from collections.abc import Callable, Sequence

from spandiff.evidence import StorageBoundaryError


class RevisionError(RuntimeError):
    """Raised when a revision or owned worktree operation is unsafe."""


@dataclass(frozen=True)
class ResolvedRevision:
    name: str
    requested_ref: str
    commit: str


@dataclass(frozen=True)
class OwnedWorktree:
    variant: str
    commit: str
    path: Path


_COMMIT = re.compile(r"^[0-9a-fA-F]{40}$")
_VARIANT = re.compile(r"^[a-z][a-z0-9-]{0,31}$")


def _default_runner(args: Sequence[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=False)


class RevisionManager:
    """Resolve refs and manage only worktrees under the supplied owned root."""

    def __init__(self, repository: str | Path, owned_root: str | Path,
                 runner: Callable[[Sequence[str], Path], subprocess.CompletedProcess[str]] | None = None):
        self.repository = Path(repository).resolve(strict=True)
        self.owned_root = Path(owned_root).resolve(strict=False)
        self.runner = runner or _default_runner

    def resolve(self, name: str, reference: str) -> ResolvedRevision:
        if not _VARIANT.fullmatch(name):
            raise RevisionError("variant: invalid name")
        if not isinstance(reference, str) or not reference.strip():
            raise RevisionError(f"{name}: revision reference is required")
        result = self.runner(("git", "rev-parse", "--verify", f"{reference}^{{commit}}"), self.repository)
        commit = result.stdout.strip()
        if result.returncode != 0 or not _COMMIT.fullmatch(commit):
            detail = result.stderr.strip() or "reference was not resolved to a commit"
            raise RevisionError(f"{name}: invalid revision reference: {detail}")
        return ResolvedRevision(name, reference, commit.lower())

    def create(self, revision: ResolvedRevision) -> OwnedWorktree:
        destination = self._destination(revision.name)
        if destination.exists():
            raise RevisionError(f"{revision.name}: owned worktree destination already exists")
        destination.parent.mkdir(parents=True, exist_ok=True)
        result = self.runner(("git", "worktree", "add", "--detach", str(destination), revision.commit), self.repository)
        if result.returncode != 0:
            detail = result.stderr.strip() or "git worktree add failed"
            raise RevisionError(f"{revision.name}: cannot create worktree: {detail}")
        return OwnedWorktree(revision.name, revision.commit, destination)

    def remove(self, worktree: OwnedWorktree) -> None:
        destination = self._destination(worktree.variant)
        if destination != worktree.path.resolve(strict=False):
            raise RevisionError(f"{worktree.variant}: worktree path is not owned")
        result = self.runner(("git", "worktree", "remove", "--force", str(destination)), self.repository)
        if result.returncode != 0:
            detail = result.stderr.strip() or "git worktree remove failed"
            raise RevisionError(f"{worktree.variant}: cannot remove worktree: {detail}")

    def persist(self, path: str | Path, revisions: Sequence[ResolvedRevision]) -> None:
        output = Path(path).resolve(strict=False)
        if not output.parent.resolve(strict=False).is_relative_to(self.owned_root):
            raise StorageBoundaryError("revision manifest: path is outside owned storage")
        output.parent.mkdir(parents=True, exist_ok=True)
        payload = {"revisions": [{"name": item.name, "requested_ref": item.requested_ref, "commit": item.commit} for item in revisions]}
        output.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")

    def _destination(self, variant: str) -> Path:
        if not _VARIANT.fullmatch(variant):
            raise RevisionError("variant: invalid name")
        candidate = (self.owned_root / "worktrees" / variant).resolve(strict=False)
        if not candidate.is_relative_to(self.owned_root):
            raise StorageBoundaryError("worktree: destination escapes owned storage")
        return candidate
