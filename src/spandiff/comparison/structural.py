"""Evidence-linked structural comparison."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class GroupSummary:
    count_per_request: float
    error_count: int
    sample_ids: tuple[str, ...]


@dataclass(frozen=True)
class StructuralFinding:
    finding_id: str
    rule_id: str
    group_id: str
    baseline_count: float | None
    candidate_count: float | None
    baseline_errors: int | None
    candidate_errors: int | None
    sample_ids: tuple[str, ...]


def compare_groups(baseline: Mapping[str, GroupSummary], candidate: Mapping[str, GroupSummary]) -> tuple[StructuralFinding, ...]:
    findings: list[StructuralFinding] = []
    for index, group_id in enumerate(sorted(set(baseline) | set(candidate)), start=1):
        before = baseline.get(group_id)
        after = candidate.get(group_id)
        if before is None:
            findings.append(StructuralFinding(f"finding-{index}", "added_operation", group_id, None, after.count_per_request, None, after.error_count, after.sample_ids))
        elif after is None:
            findings.append(StructuralFinding(f"finding-{index}", "removed_operation", group_id, before.count_per_request, None, before.error_count, None, before.sample_ids))
        elif before.count_per_request != after.count_per_request:
            findings.append(StructuralFinding(f"finding-{index}", "changed_call_count", group_id, before.count_per_request, after.count_per_request, before.error_count, after.error_count, before.sample_ids + after.sample_ids))
        elif before.error_count != after.error_count:
            findings.append(StructuralFinding(f"finding-{index}", "changed_error_pattern", group_id, before.count_per_request, after.count_per_request, before.error_count, after.error_count, before.sample_ids + after.sample_ids))
    return tuple(findings)
