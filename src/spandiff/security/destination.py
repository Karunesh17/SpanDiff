"""Approved HTTP destination and redirect policy."""

from __future__ import annotations

from dataclasses import dataclass
import ipaddress
from urllib.parse import urlsplit
from collections.abc import Callable, Iterable

from .sanitizer import safe_diagnostic


class DestinationError(ValueError):
    """Raised when a destination is not approved for an experiment."""


@dataclass(frozen=True)
class DestinationPolicy:
    allowed_hosts: frozenset[str]
    reject_private: bool = True

    @classmethod
    def from_hosts(cls, hosts: Iterable[str], *, reject_private: bool = True) -> "DestinationPolicy":
        normalized = frozenset(host.lower().rstrip(".") for host in hosts if host)
        if not normalized:
            raise DestinationError("allowlist: at least one host is required")
        return cls(normalized, reject_private)

    def validate(self, url: str, *, resolver: Callable[[str], Iterable[str]] | None = None) -> str:
        parsed = urlsplit(url)
        host = (parsed.hostname or "").lower().rstrip(".")
        if parsed.scheme not in {"http", "https"} or not host:
            raise DestinationError("destination: only HTTP(S) URLs with a host are allowed")
        if host not in self.allowed_hosts:
            raise DestinationError(f"destination: host is not approved: {host}")
        addresses = list(resolver(host)) if resolver else []
        if self.reject_private:
            for address in addresses:
                try:
                    if ipaddress.ip_address(address).is_private or ipaddress.ip_address(address).is_loopback:
                        raise DestinationError("destination: private or loopback address is not allowed")
                except ValueError:
                    raise DestinationError("destination: resolver returned an invalid address")
        return f"{parsed.scheme}://{host}{parsed.path or '/'}"

    def validate_redirect(self, original: str, location: str, *, resolver: Callable[[str], Iterable[str]] | None = None) -> str:
        original_host = (urlsplit(original).hostname or "").lower().rstrip(".")
        target_host = (urlsplit(location).hostname or "").lower().rstrip(".")
        if target_host != original_host:
            raise DestinationError(safe_diagnostic("destination: redirect changes host from %s to %s" % (original_host, target_host)))
        validated = self.validate(location, resolver=resolver)
        return validated
