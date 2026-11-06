"""Trace coverage and comparability assessment."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CoverageSummary:
    complete: bool
    request_denominator: int | None
    rooted_requests: int
    orphan_spans: int
    missing_parents: int
    dropped_records: int
    reasons: tuple[str, ...]


def assess_coverage(*, request_denominator: int | None, rooted_requests: int, orphan_spans: int = 0,
                    missing_parents: int = 0, dropped_records: int = 0) -> CoverageSummary:
    reasons: list[str] = []
    if request_denominator is None:
        reasons.append("missing_request_denominator")
    elif request_denominator < 0 or rooted_requests < 0 or rooted_requests > request_denominator:
        reasons.append("invalid_request_correlation")
    elif rooted_requests < request_denominator:
        reasons.append("missing_request_roots")
    if orphan_spans:
        reasons.append("orphan_spans")
    if missing_parents:
        reasons.append("missing_parents")
    if dropped_records:
        reasons.append("dropped_records")
    return CoverageSummary(not reasons, request_denominator, rooted_requests, orphan_spans, missing_parents, dropped_records, tuple(reasons))
