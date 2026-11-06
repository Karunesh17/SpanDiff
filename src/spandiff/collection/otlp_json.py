"""Bounded importer for sanitized OTLP JSON evidence."""

from __future__ import annotations

from dataclasses import dataclass
import json
import re
from typing import Any, Mapping

from spandiff.security import sanitize_resource_attributes, sanitize_span_attributes


class ImportValidationError(ValueError):
    """Raised when bounded OTLP JSON cannot be safely imported."""


@dataclass(frozen=True)
class ImportedSpan:
    trace_id: str
    span_id: str
    parent_id: str | None
    name: str
    kind: str
    service: str
    start_ns: int
    end_ns: int
    status: str
    attributes: Mapping[str, str | int | float | bool]
    resource: Mapping[str, str | int | float | bool]


@dataclass(frozen=True)
class ImportIssue:
    code: str
    detail: str


@dataclass(frozen=True)
class ImportResult:
    spans: tuple[ImportedSpan, ...]
    issues: tuple[ImportIssue, ...]
    complete: bool


_TRACE_ID = re.compile(r"^[0-9a-fA-F]{32}$")
_SPAN_ID = re.compile(r"^[0-9a-fA-F]{16}$")


def _required_string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value:
        raise ImportValidationError(f"{path}: must be a non-empty string")
    return value


def _timestamp(value: Any, path: str) -> int:
    if isinstance(value, str) and value.isdigit():
        value = int(value)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ImportValidationError(f"{path}: must be a non-negative nanosecond timestamp")
    return value


def import_otlp_json(text: str, *, max_bytes: int = 50_000_000, max_spans: int = 100_000) -> ImportResult:
    """Import a bounded OTLP ExportTraceServiceRequest JSON document."""
    if not isinstance(text, str):
        raise ImportValidationError("input: must be text")
    if len(text.encode("utf-8")) > max_bytes:
        raise ImportValidationError(f"input: exceeds max_bytes={max_bytes}")
    try:
        document = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ImportValidationError(f"input: invalid JSON at line {exc.lineno}, column {exc.colno}") from exc
    if not isinstance(document, dict):
        raise ImportValidationError("input: root must be an object")
    resource_spans = document.get("resourceSpans")
    if not isinstance(resource_spans, list):
        raise ImportValidationError("resourceSpans: must be an array")

    unique: dict[tuple[str, str], ImportedSpan] = {}
    issues: list[ImportIssue] = []
    for resource_index, resource_entry in enumerate(resource_spans):
        if not isinstance(resource_entry, dict):
            raise ImportValidationError(f"resourceSpans[{resource_index}]: must be an object")
        resource = resource_entry.get("resource", {})
        if not isinstance(resource, dict):
            raise ImportValidationError(f"resourceSpans[{resource_index}].resource: must be an object")
        resource_attrs = resource.get("attributes", {})
        if not isinstance(resource_attrs, dict):
            raise ImportValidationError(f"resourceSpans[{resource_index}].resource.attributes: must be an object")
        clean_resource = sanitize_resource_attributes(resource_attrs)
        service = str(clean_resource.get("service.name", "unknown"))
        for scope_index, scope_entry in enumerate(resource_entry.get("scopeSpans", [])):
            if not isinstance(scope_entry, dict):
                raise ImportValidationError(f"scopeSpans[{scope_index}]: must be an object")
            for span_index, raw in enumerate(scope_entry.get("spans", [])):
                path = f"resourceSpans[{resource_index}].scopeSpans[{scope_index}].spans[{span_index}]"
                if not isinstance(raw, dict):
                    raise ImportValidationError(f"{path}: must be an object")
                trace_id = _required_string(raw.get("traceId"), f"{path}.traceId")
                span_id = _required_string(raw.get("spanId"), f"{path}.spanId")
                if not _TRACE_ID.fullmatch(trace_id) or not _SPAN_ID.fullmatch(span_id):
                    raise ImportValidationError(f"{path}: invalid traceId/spanId")
                attributes = raw.get("attributes", {})
                if not isinstance(attributes, dict):
                    raise ImportValidationError(f"{path}.attributes: must be an object")
                span = ImportedSpan(
                    trace_id.lower(), span_id.lower(), raw.get("parentSpanId"),
                    _required_string(raw.get("name"), f"{path}.name"),
                    str(raw.get("kind", "SPAN_KIND_UNSPECIFIED")), service,
                    _timestamp(raw.get("startTimeUnixNano"), f"{path}.startTimeUnixNano"),
                    _timestamp(raw.get("endTimeUnixNano"), f"{path}.endTimeUnixNano"),
                    str(raw.get("status", {}).get("code", "STATUS_CODE_UNSET")) if isinstance(raw.get("status", {}), dict) else "STATUS_CODE_UNSET",
                    sanitize_span_attributes(attributes), clean_resource,
                )
                if span.end_ns < span.start_ns:
                    raise ImportValidationError(f"{path}.endTimeUnixNano: precedes start timestamp")
                key = (span.trace_id, span.span_id)
                prior = unique.get(key)
                if prior is None:
                    if len(unique) >= max_spans:
                        raise ImportValidationError(f"input: exceeds max_spans={max_spans}")
                    unique[key] = span
                elif prior != span:
                    issues.append(ImportIssue("conflicting_duplicate_span", f"{trace_id}/{span_id}"))
                else:
                    issues.append(ImportIssue("duplicate_span", f"{trace_id}/{span_id}"))
    return ImportResult(tuple(unique.values()), tuple(issues), not any(i.code == "conflicting_duplicate_span" for i in issues))
