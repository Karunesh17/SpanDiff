"""Scenario request runner with trace context and assertion evidence."""

from __future__ import annotations

from dataclasses import dataclass
import json
import secrets
import time
from collections.abc import Callable, Mapping

from spandiff.config import Scenario


class ScenarioRunError(RuntimeError):
    """Raised when a scenario cannot be run safely."""


@dataclass(frozen=True)
class Response:
    status: int
    body: Mapping[str, object]


@dataclass(frozen=True)
class Sample:
    sample_id: str
    batch_id: str
    sequence: int
    traceparent: str
    status: int
    client_duration_ns: int
    assertion_ok: bool
    assertion_error: str | None


@dataclass(frozen=True)
class ScenarioRun:
    warmups: tuple[Sample, ...]
    measured: tuple[Sample, ...]


def _matches_expected(actual: object, expected: object) -> bool:
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(key in actual and _matches_expected(actual[key], value) for key, value in expected.items())
    return actual == expected


class ScenarioRunner:
    def __init__(self, requester: Callable[[str, str, Mapping[str, str], float], Response],
                 reset: Callable[[], bool] | None = None, token_factory: Callable[[], str] | None = None,
                 clock: Callable[[], int] = time.perf_counter_ns):
        self.requester = requester
        self.reset = reset
        self.token_factory = token_factory or (lambda: secrets.token_hex(16))
        self.clock = clock

    def run(self, scenario: Scenario, *, batch_id: str = "batch-1") -> ScenarioRun:
        warmups = tuple(self._sample(scenario, batch_id, index, measured=False) for index in range(scenario.warmup))
        measured = []
        for index in range(scenario.samples):
            if scenario.write:
                if self.reset is None or not self.reset():
                    raise ScenarioRunError(f"scenario {scenario.name}: reset failed before measured sample {index}")
            measured.append(self._sample(scenario, batch_id, index, measured=True))
        return ScenarioRun(warmups, tuple(measured))

    def _sample(self, scenario: Scenario, batch_id: str, sequence: int, *, measured: bool) -> Sample:
        sample_id = secrets.token_hex(16)
        trace_id = self.token_factory()
        traceparent = f"00-{trace_id}-{'0' * 16}-01"
        start = self.clock()
        response = self.requester(scenario.method, scenario.path, {"traceparent": traceparent, "x-spandiff-sample-id": sample_id}, scenario.timeout_seconds)
        duration = max(0, self.clock() - start)
        expected_status = scenario.assertions.status
        assertion_error = None
        if expected_status is not None and response.status != expected_status:
            assertion_error = f"expected status {expected_status}, got {response.status}"
        elif scenario.assertions.json and not _matches_expected(response.body, scenario.assertions.json):
            assertion_error = "response JSON assertion failed"
        return Sample(sample_id, batch_id, sequence, traceparent, response.status, duration, assertion_error is None, assertion_error)
