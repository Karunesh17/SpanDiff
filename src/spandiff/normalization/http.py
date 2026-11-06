"""Safe HTTP operation identity normalization."""

from __future__ import annotations

from dataclasses import dataclass
import re
from urllib.parse import urlsplit


@dataclass(frozen=True)
class HttpIdentity:
    service: str
    method: str
    path: str | None
    known: bool


_METHOD = re.compile(r"^[A-Za-z]+$")
_UUID = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$")
_NUMERIC = re.compile(r"^[0-9]+$")
_TEMPLATE = re.compile(r"^\{[A-Za-z][A-Za-z0-9_-]*\}$")


def normalize_http(service: str, method: str, target: str, *, allowed_services: set[str] | None = None) -> HttpIdentity:
    """Normalize an HTTP operation without retaining query values or dynamic IDs."""
    if not isinstance(service, str) or not service or (allowed_services is not None and service not in allowed_services):
        return HttpIdentity("unknown", "UNKNOWN", None, False)
    if not isinstance(method, str) or not _METHOD.fullmatch(method):
        return HttpIdentity(service, "UNKNOWN", None, False)
    parsed = urlsplit(target)
    path = parsed.path if parsed.scheme or parsed.netloc else target.split("?", 1)[0].split("#", 1)[0]
    if not path.startswith("/") or "//" in path or not path:
        return HttpIdentity(service, method.upper(), None, False)
    segments = []
    for segment in path.split("/"):
        if not segment:
            continue
        if _UUID.fullmatch(segment) or _NUMERIC.fullmatch(segment):
            segments.append("{id}")
        elif _TEMPLATE.fullmatch(segment):
            segments.append(segment)
        elif "{" in segment or "}" in segment:
            return HttpIdentity(service, method.upper(), None, False)
        else:
            segments.append(segment)
    return HttpIdentity(service, method.upper(), "/" + "/".join(segments), True)
