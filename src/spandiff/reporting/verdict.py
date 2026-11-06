"""Count-budget verdicts and stable process exit mapping."""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Mapping, Sequence


class VerdictError(ValueError):
    """Raised for invalid verdict inputs."""


@dataclass(frozen=True)
class Verdict:
    state: str
    exit_code: int
    budget_violations: Mapping[str, int]
    timing_warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "state": self.state,
            "exit_code": self.exit_code,
            "budget_violations": dict(self.budget_violations),
            "timing_warnings": list(self.timing_warnings),
        }


def evaluate_verdict(*, complete: bool, observed_counts: Mapping[str, int],
                     budgets: Mapping[str, int], timing_warnings: Sequence[str] = ()) -> Verdict:
    """Evaluate count budgets; incompleteness takes precedence over budgets.

    Timing thresholds are advisory in the initial release and therefore never
    change the exit code. Invalid inputs use exit 3, matching CLI input errors.
    """
    if not isinstance(complete, bool):
        raise VerdictError("complete: must be a boolean")
    violations: dict[str, int] = {}
    for name, observed in observed_counts.items():
        if not isinstance(name, str) or not name:
            raise VerdictError("observed_counts: keys must be non-empty strings")
        if isinstance(observed, bool) or not isinstance(observed, int) or observed < 0:
            raise VerdictError(f"observed_counts.{name}: must be a non-negative integer")
    for name, budget in budgets.items():
        if not isinstance(name, str) or not name:
            raise VerdictError("budgets: keys must be non-empty strings")
        if isinstance(budget, bool) or not isinstance(budget, int) or budget < 0:
            raise VerdictError(f"budgets.{name}: must be a non-negative integer")
        observed = observed_counts.get(name, 0)
        if observed > budget:
            violations[name] = observed - budget
    warnings = tuple(str(item) for item in timing_warnings)
    if not complete:
        return Verdict("incomplete", 2, violations, warnings)
    if violations:
        return Verdict("budget_violation", 1, violations, warnings)
    return Verdict("pass", 0, {}, warnings)
