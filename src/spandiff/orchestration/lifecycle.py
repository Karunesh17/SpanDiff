"""Durable lifecycle journal with independent result and cleanup state."""

from __future__ import annotations

from dataclasses import dataclass
import json
import sqlite3
from typing import Any


class LifecycleError(RuntimeError):
    """Raised when a lifecycle transition or resource operation is invalid."""


_TRANSITIONS = {
    "created": {"prepared", "failed", "cancelled"},
    "prepared": {"running", "failed", "cancelled"},
    "running": {"finalized", "failed", "cancelled"},
    "finalized": {"cleaned", "cleanup_pending"},
    "cleanup_pending": {"cleaned", "cleanup_pending"},
    "failed": {"cleanup_pending", "cleaned"},
    "cancelled": {"cleanup_pending", "cleaned"},
    "cleaned": set(),
}


@dataclass(frozen=True)
class LifecycleState:
    stage: str
    result_state: str
    cleanup_state: str


class LifecycleJournal:
    def __init__(self, connection: sqlite3.Connection, experiment_id: str):
        self.connection = connection
        self.experiment_id = experiment_id

    def state(self) -> LifecycleState:
        row = self.connection.execute(
            "SELECT state, result_state, cleanup_state FROM experiments WHERE experiment_id = ?",
            (self.experiment_id,),
        ).fetchone()
        if row is None:
            raise LifecycleError("experiment: not found")
        return LifecycleState(*row)

    def transition(self, stage: str, *, result_state: str | None = None,
                   cleanup_state: str | None = None, detail: dict[str, Any] | None = None) -> LifecycleState:
        current = self.state()
        if stage not in _TRANSITIONS.get(current.stage, set()):
            raise LifecycleError(f"lifecycle: cannot transition {current.stage} -> {stage}")
        next_result = current.result_state if result_state is None else result_state
        next_cleanup = current.cleanup_state if cleanup_state is None else cleanup_state
        detail_json = json.dumps(detail or {}, sort_keys=True, separators=(",", ":"))
        try:
            self.connection.execute("BEGIN IMMEDIATE")
            sequence = self.connection.execute(
                "SELECT COALESCE(MAX(event_sequence), 0) + 1 FROM lifecycle_events WHERE experiment_id = ?",
                (self.experiment_id,),
            ).fetchone()[0]
            self.connection.execute(
                "UPDATE experiments SET state = ?, result_state = ?, cleanup_state = ? WHERE experiment_id = ?",
                (stage, next_result, next_cleanup, self.experiment_id),
            )
            self.connection.execute(
                "INSERT INTO lifecycle_events VALUES (?, ?, ?, datetime('now'), ?)",
                (self.experiment_id, sequence, stage, detail_json),
            )
            self.connection.commit()
        except sqlite3.Error as exc:
            self.connection.rollback()
            raise LifecycleError(f"lifecycle: transition failed: {exc}") from exc
        return LifecycleState(stage, next_result, next_cleanup)

    def register_resource(self, resource_id: str, kind: str, ownership_token: str, locator: str) -> None:
        if not all(isinstance(value, str) and value for value in (resource_id, kind, ownership_token, locator)):
            raise LifecycleError("resource: identifiers and ownership fields are required")
        try:
            self.connection.execute(
                "INSERT INTO resources VALUES (?, ?, ?, ?, ?, 'owned', NULL)",
                (self.experiment_id, resource_id, kind, ownership_token, locator),
            )
            self.connection.commit()
        except sqlite3.IntegrityError as exc:
            self.connection.rollback()
            raise LifecycleError("resource: duplicate or unknown experiment") from exc
