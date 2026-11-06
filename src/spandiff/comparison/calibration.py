"""Workload-qualified, descriptive tracing calibration summaries."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import median
from collections.abc import Sequence


class CalibrationError(ValueError):
    """Raised for invalid calibration observations."""


@dataclass(frozen=True)
class CalibrationResult:
    workload: str
    uninstrumented_samples: int
    instrumented_samples: int
    uninstrumented_median_ns: int
    instrumented_median_ns: int
    overhead_ns: int
    overhead_ratio: float
    variation_range_ns: int
    noise_label: str
    recommendation: str

    def to_dict(self) -> dict[str, object]:
        return self.__dict__.copy()


def calibrate(workload: str, uninstrumented: Sequence[int], instrumented: Sequence[int], *, noise_ratio: float = 0.20) -> CalibrationResult:
    """Return descriptive calibration data; no p99 metric or gating is enabled."""
    if not isinstance(workload, str) or not workload.strip():
        raise CalibrationError("workload: must be a non-empty description")
    if not uninstrumented or not instrumented:
        raise CalibrationError("samples: both batches must contain observations")
    for label, values in (("uninstrumented", uninstrumented), ("instrumented", instrumented)):
        if any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in values):
            raise CalibrationError(f"{label}: samples must be non-negative integers")
    if noise_ratio < 0:
        raise CalibrationError("noise_ratio: must be non-negative")
    base = int(median(uninstrumented))
    traced = int(median(instrumented))
    ratio = 0.0 if base == 0 else (traced - base) / base
    all_values = list(uninstrumented) + list(instrumented)
    variation = max(all_values) - min(all_values)
    spread_ratio = 0.0 if traced == 0 else variation / traced
    label = "noisy" if spread_ratio > noise_ratio else "stable-enough-for-descriptive-use"
    recommendation = "retain five warm-ups and thirty measured samples; treat timing as advisory"
    return CalibrationResult(workload.strip(), len(uninstrumented), len(instrumented), base, traced,
                             traced - base, round(ratio, 6), variation, label, recommendation)
