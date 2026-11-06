"""Comparable timing summaries with explicit unavailable metrics."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import median
from collections.abc import Mapping, Sequence


@dataclass(frozen=True)
class TimingSpan:
    span_id: str
    start_ns: int
    end_ns: int
    parent_id: str | None = None
    kind: str = "internal"
    background: bool = False

    @property
    def duration_ns(self) -> int:
        return max(0, self.end_ns - self.start_ns)


@dataclass(frozen=True)
class TimingSample:
    sample_id: str
    batch_id: str
    client_duration_ns: int | None
    spans: tuple[TimingSpan, ...]
    comparable: bool = True


@dataclass(frozen=True)
class MetricSummary:
    median_ns: int | None
    minimum_ns: int | None
    maximum_ns: int | None
    variation_ns: int | None
    available_samples: int


@dataclass(frozen=True)
class TimingSummary:
    variant: str
    sample_count: int
    batch_counts: Mapping[str, int]
    client: MetricSummary
    server: MetricSummary
    operation: MetricSummary
    background: MetricSummary


def _metric(values: Sequence[int | None]) -> MetricSummary:
    available = [value for value in values if value is not None]
    if not available:
        return MetricSummary(None, None, None, None, 0)
    minimum = min(available)
    maximum = max(available)
    return MetricSummary(int(median(available)), minimum, maximum, maximum - minimum, len(available))


def _union_duration(spans: Sequence[TimingSpan]) -> int | None:
    if not spans:
        return None
    intervals = sorted((span.start_ns, span.end_ns) for span in spans if span.end_ns >= span.start_ns)
    if not intervals:
        return None
    total = 0
    start, end = intervals[0]
    for next_start, next_end in intervals[1:]:
        if next_start <= end:
            end = max(end, next_end)
        else:
            total += end - start
            start, end = next_start, next_end
    return total + end - start


def _server_duration(sample: TimingSample) -> int | None:
    roots = [span for span in sample.spans if span.parent_id is None and span.kind == "server" and not span.background]
    return roots[0].duration_ns if len(roots) == 1 else None


def _operation_duration(sample: TimingSample) -> int | None:
    spans = [span for span in sample.spans if span.kind == "internal" and not span.background]
    return _union_duration(spans)


def _background_duration(sample: TimingSample) -> int | None:
    return _union_duration([span for span in sample.spans if span.background])


def summarize_timings(variant: str, samples: Sequence[TimingSample], *, comparable_only: bool = True) -> TimingSummary:
    """Summarize measured samples without fabricating missing timing values."""
    selected = [sample for sample in samples if sample.comparable or not comparable_only]
    return TimingSummary(
        variant=variant,
        sample_count=len(selected),
        batch_counts={batch: sum(sample.batch_id == batch for sample in selected)
                      for batch in sorted({sample.batch_id for sample in selected})},
        client=_metric([sample.client_duration_ns for sample in selected]),
        server=_metric([_server_duration(sample) for sample in selected]),
        operation=_metric([_operation_duration(sample) for sample in selected]),
        background=_metric([_background_duration(sample) for sample in selected]),
    )
