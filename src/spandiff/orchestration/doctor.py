"""Read-only prerequisite checks for a configured repository."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import shutil
from collections.abc import Mapping

from spandiff.config import ConfigurationError, RepositoryConfig, load_config


@dataclass(frozen=True)
class DoctorCheck:
    name: str
    ok: bool
    detail: str


@dataclass(frozen=True)
class DoctorReport:
    checks: tuple[DoctorCheck, ...]

    @property
    def ok(self) -> bool:
        return all(check.ok for check in self.checks)


def _tool_check(name: str, candidates: tuple[str, ...], finder=shutil.which) -> DoctorCheck:
    found = next((candidate for candidate in candidates if finder(candidate)), None)
    if found:
        return DoctorCheck(name, True, f"available: {found}")
    return DoctorCheck(name, False, f"missing prerequisite; install one of: {', '.join(candidates)}")


def _path_check(name: str, root: Path, configured: str) -> DoctorCheck:
    path = (root / configured).resolve(strict=False)
    if path.is_file():
        return DoctorCheck(name, True, "configured file is present")
    return DoctorCheck(name, False, f"missing configured file: {configured}")


def check_config(config: RepositoryConfig, *, repo_root: str | Path, environment: Mapping[str, str] | None = None,
                 finder=shutil.which) -> DoctorReport:
    root = Path(repo_root).resolve(strict=True)
    environment = os.environ if environment is None else environment
    checks = [
        _tool_check("git", ("git",), finder),
        _tool_check("docker", ("docker",), finder),
        _tool_check("compose", ("docker-compose", "docker"), finder),
        DoctorCheck("adapter", config.adapter == "fastapi-compose", "fastapi-compose adapter configured" if config.adapter == "fastapi-compose" else "unsupported adapter"),
        _path_check("compose_file", root, config.compose_file),
        DoctorCheck("app_service", bool(config.app_service), f"service configured: {config.app_service}"),
        DoctorCheck("fixture_contract", bool(config.fixtures), f"fixture identity configured: {config.fixtures}"),
    ]
    for name, variable in config.credentials.items():
        checks.append(DoctorCheck(f"credential.{name}", variable in environment,
                                  f"environment reference {variable} is set" if variable in environment else f"missing environment reference {variable}"))
    return DoctorReport(tuple(checks))


def run_doctor(config_path: str | Path, *, repo_root: str | Path | None = None,
               environment: Mapping[str, str] | None = None, finder=shutil.which) -> DoctorReport:
    """Load configuration and run checks without spawning a process."""
    config_file = Path(config_path).resolve(strict=True)
    config = load_config(config_file)
    return check_config(config, repo_root=repo_root or config_file.parent, environment=environment, finder=finder)
