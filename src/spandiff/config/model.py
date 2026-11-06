"""Strict, side-effect-free repository configuration model."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import PurePosixPath
import re
from typing import Any, Mapping


class ConfigurationError(ValueError):
    """Raised when configuration is malformed or violates schema rules."""


def _error(path: str, message: str) -> ConfigurationError:
    return ConfigurationError(f"{path}: {message}")


def _mapping(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise _error(path, "must be a mapping")
    if any(not isinstance(key, str) for key in value):
        raise _error(path, "keys must be strings")
    return value


def _unknown(data: Mapping[str, Any], allowed: set[str], path: str) -> None:
    unknown = sorted(set(data) - allowed)
    if unknown:
        raise _error(f"{path}.{unknown[0]}", "unknown field")


def _required(data: Mapping[str, Any], name: str, path: str) -> Any:
    if name not in data:
        raise _error(f"{path}.{name}", "is required")
    return data[name]


def _string(value: Any, path: str, *, pattern: str | None = None) -> str:
    if not isinstance(value, str) or not value.strip():
        raise _error(path, "must be a non-empty string")
    if pattern and not re.fullmatch(pattern, value):
        raise _error(path, "has an invalid format")
    return value


def _positive_int(value: Any, path: str, *, minimum: int = 1) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise _error(path, f"must be an integer >= {minimum}")
    return value


def _finite_number(value: Any, path: str, *, minimum: float = 0.0) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise _error(path, "must be a finite number")
    result = float(value)
    if result != result or result in (float("inf"), float("-inf")) or result < minimum:
        raise _error(path, f"must be finite and >= {minimum}")
    return result


def _argv(value: Any, path: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value or any(not isinstance(item, str) or not item for item in value):
        raise _error(path, "must be a non-empty argument array of strings")
    return tuple(value)


@dataclass(frozen=True)
class ResponseAssertions:
    status: int | None = None
    json: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Scenario:
    name: str
    method: str
    path: str
    assertions: ResponseAssertions
    warmup: int = 5
    samples: int = 30
    concurrency: int = 1
    timeout_seconds: float = 10.0
    budgets: Mapping[str, int] = field(default_factory=dict)
    write: bool = False


@dataclass(frozen=True)
class ExecutionLimits:
    command_timeout_seconds: float = 300.0
    readiness_timeout_seconds: float = 60.0
    request_timeout_seconds: float = 30.0
    flush_timeout_seconds: float = 30.0
    cleanup_timeout_seconds: float = 60.0
    max_output_bytes: int = 1_048_576
    max_trace_bytes: int = 50_000_000
    max_spans: int = 100_000
    max_samples: int = 1_000
    max_concurrency: int = 32


@dataclass(frozen=True)
class RepositoryConfig:
    schema_version: int
    project: str
    adapter: str
    compose_file: str
    app_service: str
    health_path: str
    fixtures: str
    prepare_command: tuple[str, ...] | None
    reset_command: tuple[str, ...] | None
    allow_shell: bool
    credentials: Mapping[str, str]
    scenarios: Mapping[str, Scenario]
    limits: ExecutionLimits


_ROOT_FIELDS = {"schema_version", "project", "adapter", "compose_file", "app_service", "health_path", "fixtures", "prepare_command", "reset_command", "allow_shell", "credentials", "scenarios", "limits"}
_SCENARIO_FIELDS = {"method", "path", "expected_status", "assertions", "warmup", "samples", "concurrency", "timeout_seconds", "budgets", "write"}
_ASSERTION_FIELDS = {"status", "json"}
_LIMIT_FIELDS = set(ExecutionLimits.__dataclass_fields__)


def _parse_assertions(data: Mapping[str, Any], path: str, expected_status: Any = None) -> ResponseAssertions:
    _unknown(data, _ASSERTION_FIELDS, path)
    status = data.get("status", expected_status)
    if status is not None:
        status = _positive_int(status, f"{path}.status")
        if status > 599:
            raise _error(f"{path}.status", "must be an HTTP status code")
    json_values = data.get("json", {})
    if not isinstance(json_values, dict):
        raise _error(f"{path}.json", "must be a mapping")
    return ResponseAssertions(status=status, json=dict(json_values))


def _parse_scenario(name: str, raw: Any, path: str) -> Scenario:
    data = _mapping(raw, path)
    _unknown(data, _SCENARIO_FIELDS, path)
    method = _string(_required(data, "method", path), f"{path}.method", pattern=r"[A-Za-z]+")
    route = _string(_required(data, "path", path), f"{path}.path")
    if not route.startswith("/") or "?" in route:
        raise _error(f"{path}.path", "must be an HTTP path without query values")
    assertions_raw = data.get("assertions", {})
    assertions = _parse_assertions(_mapping(assertions_raw, f"{path}.assertions"), f"{path}.assertions", data.get("expected_status"))
    budgets_raw = data.get("budgets", {})
    budgets = _mapping(budgets_raw, f"{path}.budgets")
    parsed_budgets: dict[str, int] = {}
    for key, value in budgets.items():
        parsed_budgets[_string(key, f"{path}.budgets key")] = _positive_int(value, f"{path}.budgets.{key}", minimum=0)
    write = data.get("write", False)
    if not isinstance(write, bool):
        raise _error(f"{path}.write", "must be a boolean")
    return Scenario(name, method.upper(), route, assertions,
                    _positive_int(data.get("warmup", 5), f"{path}.warmup", minimum=0),
                    _positive_int(data.get("samples", 30), f"{path}.samples"),
                    _positive_int(data.get("concurrency", 1), f"{path}.concurrency"),
                    _finite_number(data.get("timeout_seconds", 10), f"{path}.timeout_seconds", minimum=0.001),
                    parsed_budgets, write)


def _parse_limits(raw: Any) -> ExecutionLimits:
    data = _mapping(raw, "limits")
    _unknown(data, _LIMIT_FIELDS, "limits")
    values = {}
    for field_name, default in ExecutionLimits.__dataclass_fields__.items():
        value = data.get(field_name, default.default)
        if field_name.endswith("_seconds"):
            values[field_name] = _finite_number(value, f"limits.{field_name}", minimum=0.001)
        else:
            values[field_name] = _positive_int(value, f"limits.{field_name}")
    return ExecutionLimits(**values)


def config_from_mapping(raw: Any) -> RepositoryConfig:
    data = _mapping(raw, "config")
    _unknown(data, _ROOT_FIELDS, "config")
    version = _required(data, "schema_version", "config")
    if version != 1:
        raise _error("config.schema_version", "unsupported schema version; expected 1")
    credentials_raw = _mapping(data.get("credentials", {}), "config.credentials")
    credentials: dict[str, str] = {}
    for name, env_name in credentials_raw.items():
        _string(name, "config.credentials key", pattern=r"[A-Za-z_][A-Za-z0-9_]*")
        credentials[name] = _string(env_name, f"config.credentials.{name}", pattern=r"[A-Z_][A-Z0-9_]*")
    scenarios_raw = _mapping(_required(data, "scenarios", "config"), "config.scenarios")
    if not scenarios_raw:
        raise _error("config.scenarios", "must contain at least one scenario")
    scenarios = {name: _parse_scenario(name, value, f"config.scenarios.{name}") for name, value in scenarios_raw.items()}
    reset = data.get("reset_command")
    reset_args = None if reset is None else _argv(reset, "config.reset_command")
    prepare = data.get("prepare_command")
    prepare_args = None if prepare is None else _argv(prepare, "config.prepare_command")
    allow_shell = data.get("allow_shell", False)
    if not isinstance(allow_shell, bool):
        raise _error("config.allow_shell", "must be a boolean")
    if allow_shell and not (reset_args or prepare_args):
        raise _error("config.allow_shell", "cannot be enabled without a command")
    for name, scenario in scenarios.items():
        if scenario.write and reset_args is None:
            raise _error(f"config.scenarios.{name}.write", "write scenarios require config.reset_command")
    health = _string(_required(data, "health_path", "config"), "config.health_path")
    if not health.startswith("/") or "?" in health:
        raise _error("config.health_path", "must be a read-only HTTP path without query values")
    adapter = _string(_required(data, "adapter", "config"), "config.adapter")
    if adapter != "fastapi-compose":
        raise _error("config.adapter", "unsupported adapter; expected fastapi-compose")
    compose_file = _string(_required(data, "compose_file", "config"), "config.compose_file")
    if compose_file.startswith("/") or ".." in PurePosixPath(compose_file).parts:
        raise _error("config.compose_file", "must be a relative path without parent traversal")
    app_service = _string(_required(data, "app_service", "config"), "config.app_service", pattern=r"[a-zA-Z0-9][a-zA-Z0-9_.-]*")
    return RepositoryConfig(
        1, _string(_required(data, "project", "config"), "config.project", pattern=r"[A-Za-z0-9][A-Za-z0-9_.-]*"),
        adapter, compose_file, app_service, health,
        _string(_required(data, "fixtures", "config"), "config.fixtures"), prepare_args, reset_args,
        allow_shell, credentials, scenarios, _parse_limits(data.get("limits", {})))
