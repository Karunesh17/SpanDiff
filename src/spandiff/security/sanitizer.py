"""Default-deny sanitization for trace metadata and diagnostics."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
import re
from urllib.parse import urlsplit, urlunsplit


_ALLOWED_SPAN = {
    "http.method", "http.route", "http.status_code", "http.request.method",
    "http.response.status_code", "rpc.method", "rpc.service", "db.system",
    "db.operation.name", "db.namespace", "server.address", "server.port",
    "messaging.system", "span.kind", "operation.name",
}
_ALLOWED_RESOURCE = {
    "service.name", "service.version", "telemetry.sdk.name",
    "telemetry.sdk.version", "deployment.environment",
}
_SENSITIVE_NAME = re.compile(
    r"(?:authorization|cookie|token|secret|password|api[_-]?key|credential|body|"
    r"query|bind|statement|sql|user[_-]?agent|set-cookie)", re.IGNORECASE
)
_MAX_VALUE_LENGTH = 512
_MAX_DIAGNOSTIC_LENGTH = 2000


def _safe_value(value: object) -> str | int | float | bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value[:_MAX_VALUE_LENGTH]
    return str(value)[:_MAX_VALUE_LENGTH]


def _sanitize(attributes: Mapping[object, object], allowed: set[str]) -> dict[str, str | int | float | bool]:
    clean: dict[str, str | int | float | bool] = {}
    for key, value in attributes.items():
        if not isinstance(key, str) or key not in allowed or _SENSITIVE_NAME.search(key):
            continue
        clean[key] = _safe_value(value)
    return clean


def sanitize_span_attributes(attributes: Mapping[object, object]) -> dict[str, str | int | float | bool]:
    """Retain only explicitly approved span metadata."""
    return _sanitize(attributes, _ALLOWED_SPAN)


def sanitize_resource_attributes(attributes: Mapping[object, object]) -> dict[str, str | int | float | bool]:
    """Retain only explicitly approved resource metadata."""
    return _sanitize(attributes, _ALLOWED_RESOURCE)


def sanitize_url(value: str) -> str:
    """Remove URL query and fragment values while retaining scheme/host/path."""
    try:
        parsed = urlsplit(value)
    except ValueError:
        return "<invalid-url>"
    if not parsed.scheme or not parsed.netloc:
        return "<invalid-url>"
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))[:_MAX_VALUE_LENGTH]


def safe_diagnostic(message: object, secret_values: Iterable[object] = ()) -> str:
    """Bound and redact diagnostic text before it is persisted or displayed."""
    result = str(message)
    for secret in secret_values:
        if secret is None:
            continue
        value = str(secret)
        if value:
            result = result.replace(value, "<redacted>")
    result = "".join(char if char >= " " or char in "\r\n\t" else "?" for char in result)
    return result[:_MAX_DIAGNOSTIC_LENGTH]
