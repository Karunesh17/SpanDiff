"""Canonical, project-partitioned paths for owned evidence storage."""

from __future__ import annotations

from pathlib import Path
import re


class StorageBoundaryError(ValueError):
    """Raised when a requested path is outside owned storage."""


_PROJECT_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")
_EXPERIMENT_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")


def _validate_id(value: str, pattern: re.Pattern[str], label: str) -> str:
    if not isinstance(value, str) or not pattern.fullmatch(value):
        raise StorageBoundaryError(f"{label}: invalid identifier")
    return value


class OwnedStorage:
    """Resolve paths below ``home/projects/<project>/experiments/<id>`` only."""

    def __init__(self, home: str | Path, project_id: str | None = None):
        self.home = Path(home).expanduser().resolve(strict=False)
        self.bound_project_id = None if project_id is None else _validate_id(project_id, _PROJECT_ID, "project_id")

    def project_root(self, project_id: str) -> Path:
        project_id = _validate_id(project_id, _PROJECT_ID, "project_id")
        if self.bound_project_id is not None and project_id != self.bound_project_id:
            raise StorageBoundaryError("project_id: does not match the storage project")
        return self._owned(self.home / "projects" / project_id)

    def experiment_root(self, project_id: str, experiment_id: str) -> Path:
        experiment_id = _validate_id(experiment_id, _EXPERIMENT_ID, "experiment_id")
        return self._owned(self.project_root(project_id) / "experiments" / experiment_id)

    def resolve(self, project_id: str, experiment_id: str, relative_path: str | Path = ".") -> Path:
        """Resolve a relative artifact path and reject traversal or symlink escape."""
        root = self.experiment_root(project_id, experiment_id)
        relative = Path(relative_path)
        if relative.is_absolute() or any(part == ".." for part in relative.parts):
            raise StorageBoundaryError("path: must be relative and stay within the experiment")
        return self._owned(root / relative)

    def _owned(self, candidate: Path) -> Path:
        resolved = candidate.resolve(strict=False)
        if not resolved.is_relative_to(self.home):
            raise StorageBoundaryError("path: resolves outside owned storage")
        return resolved
