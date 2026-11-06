"""Bounded fixture preparation and reset contract."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
from collections.abc import Callable, Sequence

from spandiff.config import RepositoryConfig, Scenario


class FixtureError(RuntimeError):
    """Raised when fixture preparation or reset cannot proceed safely."""


@dataclass(frozen=True)
class FixtureOutcome:
    fixture_id: str
    prepared: bool
    reset_ok: bool
    comparable: bool
    detail: str


class FixtureManager:
    def __init__(self, config: RepositoryConfig, repository: str | Path,
                 runner: Callable[[Sequence[str], Path, float], subprocess.CompletedProcess[str]] | None = None):
        self.config = config
        self.repository = Path(repository).resolve(strict=True)
        self.runner = runner

    def prepare(self) -> FixtureOutcome:
        if self.config.prepare_command is None:
            return FixtureOutcome(self.config.fixtures, True, True, True, "no preparation command configured")
        self._run(self.config.prepare_command, self.config.limits.command_timeout_seconds, "prepare")
        return FixtureOutcome(self.config.fixtures, True, True, True, "prepared")

    def before_sample(self, scenario: Scenario) -> FixtureOutcome:
        if not scenario.write:
            return FixtureOutcome(self.config.fixtures, True, True, True, "read-only scenario")
        if self.config.reset_command is None:
            raise FixtureError(f"scenario {scenario.name}: write scenario requires reset_command")
        try:
            self._run(self.config.reset_command, self.config.limits.command_timeout_seconds, "reset")
        except FixtureError as exc:
            return FixtureOutcome(self.config.fixtures, True, False, False, str(exc))
        return FixtureOutcome(self.config.fixtures, True, True, True, "reset")

    def _run(self, command: Sequence[str], timeout: float, label: str) -> None:
        if self.runner is None:
            raise FixtureError(f"{label}: no runner configured")
        result = self.runner(tuple(command), self.repository, timeout)
        if result.returncode != 0:
            raise FixtureError(f"{label}: command failed with exit {result.returncode}")
