"""Bounded collector flush and immutable finalization state."""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Callable
import time


@dataclass(frozen=True)
class FlushResult:
    flushed: bool
    complete: bool
    accepted_spans: int
    quarantined_spans: int
    detail: str


class CollectorSession:
    def __init__(self, flush_callback: Callable[[], bool], *, clock: Callable[[], float] = time.monotonic):
        self.flush_callback = flush_callback
        self.clock = clock
        self.finalized = False
        self.accepted = 0
        self.quarantined = 0

    def accept(self, span: object) -> bool:
        if self.finalized:
            self.quarantined += 1
            return False
        self.accepted += 1
        return True

    def flush(self, timeout_seconds: float) -> FlushResult:
        if self.finalized:
            return FlushResult(True, self.quarantined == 0, self.accepted, self.quarantined, "already finalized")
        deadline = self.clock() + timeout_seconds
        flushed = False
        while self.clock() <= deadline:
            if self.flush_callback():
                flushed = True
                break
        self.finalized = True
        return FlushResult(flushed, flushed and self.quarantined == 0, self.accepted, self.quarantined,
                           "flushed" if flushed else "flush timeout")
