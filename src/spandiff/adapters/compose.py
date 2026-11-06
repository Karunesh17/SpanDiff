"""Safe Docker Compose environment adapter command contract."""

from __future__ import annotations

from dataclasses import dataclass
import re
from pathlib import Path
import time
from collections.abc import Callable, Mapping, Sequence

from spandiff.config import RepositoryConfig


class AdapterError(RuntimeError):
    """Raised when adapter prerequisites or lifecycle operations fail."""


@dataclass(frozen=True)
class ComposeOwnership:
    project_name: str
    network_name: str
    volume_name: str


_SAFE = re.compile(r"[^a-z0-9-]+")


class ComposeAdapter:
    def __init__(self, config: RepositoryConfig, repository: str | Path, experiment_id: str,
                 runner: Callable[..., object] | None = None):
        self.config = config
        self.repository = Path(repository).resolve(strict=True)
        self.experiment_id = experiment_id
        safe_project = _SAFE.sub("-", config.project.lower()).strip("-")
        safe_experiment = _SAFE.sub("-", experiment_id.lower()).strip("-")
        self.ownership = ComposeOwnership(f"spandiff-{safe_project}-{safe_experiment}",
                                          f"spandiff-{safe_project}-{safe_experiment}-net",
                                          f"spandiff-{safe_project}-{safe_experiment}-vol")
        self.runner = runner

    def validate(self) -> None:
        compose_file = (self.repository / self.config.compose_file).resolve(strict=False)
        if not compose_file.is_file() or not compose_file.is_relative_to(self.repository):
            raise AdapterError("compose_file: missing or outside repository")
        if not self.config.app_service:
            raise AdapterError("app_service: is required")

    def command(self, *arguments: str) -> tuple[str, ...]:
        return ("docker", "compose", "-p", self.ownership.project_name, "-f",
                self.config.compose_file, *arguments)

    def approved_environment(self, environment: Mapping[str, str]) -> dict[str, str]:
        missing = [name for name, variable in self.config.credentials.items() if variable not in environment]
        if missing:
            raise AdapterError(f"credentials: missing environment reference {missing[0]}")
        return {variable: environment[variable] for variable in self.config.credentials.values()}

    def start(self, environment: Mapping[str, str]) -> None:
        self.validate()
        if self.runner is None:
            raise AdapterError("adapter: no runner configured")
        approved = self.approved_environment(environment)
        result = self.runner(self.command("up", "-d", self.config.app_service), self.repository, approved)
        if getattr(result, "returncode", 1) != 0:
            raise AdapterError("compose: startup failed")

    def stop(self) -> None:
        if self.runner is None:
            raise AdapterError("adapter: no runner configured")
        result = self.runner(self.command("down", "--volumes"), self.repository, {})
        if getattr(result, "returncode", 1) != 0:
            raise AdapterError("compose: cleanup failed")

    def wait_ready(self, check: Callable[[], bool], timeout_seconds: float | None = None,
                   poll_seconds: float = 0.1, clock: Callable[[], float] = time.monotonic,
                   sleeper: Callable[[float], None] = time.sleep) -> None:
        timeout = self.config.limits.readiness_timeout_seconds if timeout_seconds is None else timeout_seconds
        deadline = clock() + timeout
        while clock() < deadline:
            if check():
                return
            sleeper(min(poll_seconds, max(0.0, deadline - clock())))
        raise AdapterError(f"readiness: timed out after {timeout:g} seconds")
