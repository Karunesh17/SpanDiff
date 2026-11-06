"""Validated ResultV1 serialization."""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Mapping


class ResultValidationError(ValueError):
    """Raised for invalid or unsupported result envelopes."""


@dataclass(frozen=True)
class ResultV1:
    experiment_id: str
    result_state: str
    variants: tuple[str, ...]
    coverage: Mapping[str, Any]
    findings: tuple[Mapping[str, Any], ...]
    provenance: Mapping[str, Any]
    cleanup_state: str
    schema_version: int = 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "experiment_id": self.experiment_id,
            "result_state": self.result_state,
            "variants": list(self.variants),
            "coverage": dict(self.coverage),
            "findings": [dict(finding) for finding in self.findings],
            "provenance": dict(self.provenance),
            "cleanup_state": self.cleanup_state,
        }

    def to_json(self) -> str:
        try:
            return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        except (TypeError, ValueError) as exc:
            raise ResultValidationError(f"result: values are not JSON-safe: {exc}") from exc


def result_from_dict(value: Any) -> ResultV1:
    if not isinstance(value, dict):
        raise ResultValidationError("result: root must be an object")
    if value.get("schema_version") != 1:
        raise ResultValidationError("result.schema_version: unsupported version; expected 1")
    required = ("experiment_id", "result_state", "variants", "coverage", "findings", "provenance", "cleanup_state")
    missing = next((key for key in required if key not in value), None)
    if missing:
        raise ResultValidationError(f"result.{missing}: is required")
    if not isinstance(value["experiment_id"], str) or not value["experiment_id"]:
        raise ResultValidationError("result.experiment_id: must be a non-empty string")
    if not isinstance(value["variants"], list) or not all(isinstance(item, str) for item in value["variants"]):
        raise ResultValidationError("result.variants: must be an array of strings")
    if not isinstance(value["coverage"], dict) or not isinstance(value["provenance"], dict):
        raise ResultValidationError("result.coverage/provenance: must be objects")
    if not isinstance(value["findings"], list) or not all(isinstance(item, dict) for item in value["findings"]):
        raise ResultValidationError("result.findings: must be an array of objects")
    result = ResultV1(value["experiment_id"], value["result_state"], tuple(value["variants"]), value["coverage"], tuple(value["findings"]), value["provenance"], value["cleanup_state"])
    try:
        json.dumps(result.to_dict())
    except (TypeError, ValueError) as exc:
        raise ResultValidationError(f"result: values are not JSON-safe: {exc}") from exc
    return result


def result_from_json(text: str) -> ResultV1:
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ResultValidationError(f"result: invalid JSON at line {exc.lineno}, column {exc.colno}") from exc
    return result_from_dict(value)
