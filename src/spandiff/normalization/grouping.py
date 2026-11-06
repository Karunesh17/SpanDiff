"""Versioned semantic operation grouping."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class OperationObservation:
    service: str
    kind: str
    operation_type: str
    shape: str
    parent_path: tuple[str, ...] = ()
    operation_id: str | None = None


@dataclass(frozen=True)
class OperationGroup:
    group_id: str
    identity_version: int
    members: tuple[OperationObservation, ...]
    ambiguous: bool = False


def _key(observation: OperationObservation) -> tuple[str, ...]:
    if observation.operation_id:
        return ("explicit", observation.operation_id)
    return (
        "semantic", observation.service, observation.kind,
        observation.operation_type, observation.shape,
        "/".join(observation.parent_path[-8:]),
    )


def group_operations(observations: Iterable[OperationObservation]) -> tuple[OperationGroup, ...]:
    grouped: dict[tuple[str, ...], list[OperationObservation]] = defaultdict(list)
    for observation in observations:
        grouped[_key(observation)].append(observation)
    result = []
    for index, (key, members) in enumerate(sorted(grouped.items()), start=1):
        explicit = key[0] == "explicit"
        result.append(OperationGroup(f"group-{index}", 1, tuple(members), ambiguous=not explicit and len({m.shape for m in members}) > 1))
    return tuple(result)
