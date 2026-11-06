"""Evidence-based structural and timing comparison. Implementation pending its backlog ticket."""
from .structural import GroupSummary, StructuralFinding, compare_groups
from .timing import MetricSummary, TimingSample, TimingSpan, TimingSummary, summarize_timings
from .calibration import CalibrationError, CalibrationResult, calibrate

__all__ = ["GroupSummary", "StructuralFinding", "compare_groups", "MetricSummary",
           "TimingSample", "TimingSpan", "TimingSummary", "summarize_timings",
           "CalibrationError", "CalibrationResult", "calibrate"]
