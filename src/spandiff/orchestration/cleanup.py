"""Owned, resumable cancellation and cleanup coordination."""

from __future__ import annotations

from dataclasses import dataclass
import sqlite3
from collections.abc import Callable, Mapping, Sequence

from spandiff.orchestration.lifecycle import LifecycleJournal


class CleanupError(RuntimeError):
    """Raised when cleanup input is not an owned registered resource."""


@dataclass(frozen=True)
class OwnedResource:
    resource_id: str
    kind: str
    ownership_token: str
    locator: str


@dataclass(frozen=True)
class CleanupReport:
    cleaned: tuple[str, ...]
    pending: tuple[str, ...]


CleanupHandler = Callable[[OwnedResource], None]


class CleanupManager:
    """Clean only resources registered for one experiment."""

    def __init__(self, connection: sqlite3.Connection, experiment_id: str,
                 handlers: Mapping[str, CleanupHandler]):
        self.connection = connection
        self.journal = LifecycleJournal(connection, experiment_id)
        self.experiment_id = experiment_id
        self.handlers = dict(handlers)

    def _resources(self, resource_ids: Sequence[str] | None) -> list[OwnedResource]:
        rows = self.connection.execute(
            "SELECT resource_id, kind, ownership_token, locator FROM resources "
            "WHERE experiment_id = ? ORDER BY resource_id", (self.experiment_id,),
        ).fetchall()
        registered = {row[0]: OwnedResource(*row) for row in rows}
        selected = list(registered) if resource_ids is None else list(resource_ids)
        if len(set(selected)) != len(selected) or any(not isinstance(value, str) or not value for value in selected):
            raise CleanupError("cleanup: resource IDs must be unique, non-empty strings")
        unknown = [value for value in selected if value not in registered]
        if unknown:
            raise CleanupError(f"cleanup: resource is not registered for experiment: {unknown[0]}")
        return [registered[value] for value in selected]

    def cancel(self, detail: str = "cancelled") -> None:
        state = self.journal.state()
        if state.stage not in {"cancelled", "cleanup_pending", "cleaned"}:
            self.journal.transition("cancelled", result_state="incomplete", detail={"reason": detail})

    def cleanup(self, resource_ids: Sequence[str] | None = None) -> CleanupReport:
        resources = self._resources(resource_ids)
        cleaned: list[str] = []
        pending: list[str] = []
        for resource in resources:
            state = self.connection.execute(
                "SELECT cleanup_state FROM resources WHERE experiment_id = ? AND resource_id = ?",
                (self.experiment_id, resource.resource_id),
            ).fetchone()[0]
            if state == "cleaned":
                cleaned.append(resource.resource_id)
                continue
            handler = self.handlers.get(resource.kind)
            if handler is None:
                self._mark_pending(resource.resource_id, "unsupported_kind")
                pending.append(resource.resource_id)
                continue
            try:
                handler(resource)
            except Exception as exc:
                self._mark_pending(resource.resource_id, type(exc).__name__)
                pending.append(resource.resource_id)
                continue
            self.connection.execute(
                "UPDATE resources SET cleanup_state = 'cleaned', last_error_code = NULL "
                "WHERE experiment_id = ? AND resource_id = ?",
                (self.experiment_id, resource.resource_id),
            )
            self.connection.commit()
            cleaned.append(resource.resource_id)
        self._set_experiment_cleanup("pending" if pending else "clean")
        return CleanupReport(tuple(cleaned), tuple(pending))

    def _mark_pending(self, resource_id: str, error_code: str) -> None:
        self.connection.execute(
            "UPDATE resources SET cleanup_state = 'pending', last_error_code = ? "
            "WHERE experiment_id = ? AND resource_id = ?",
            (error_code[:80], self.experiment_id, resource_id),
        )
        self.connection.commit()

    def _set_experiment_cleanup(self, state: str) -> None:
        self.connection.execute(
            "UPDATE experiments SET cleanup_state = ? WHERE experiment_id = ?",
            (state, self.experiment_id),
        )
        self.connection.commit()
