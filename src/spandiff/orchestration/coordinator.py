"""Sequential baseline/candidate compare coordination."""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Callable, Mapping


class CoordinationError(RuntimeError):
    """Raised when comparable variant orchestration cannot proceed."""


@dataclass(frozen=True)
class VariantRun:
    variant: str
    revision: str
    fixture_id: str
    batch_id: str
    success: bool
    detail: str


@dataclass(frozen=True)
class CompareManifest:
    baseline_revision: str
    candidate_revision: str
    fixture_id: str
    runs: tuple[VariantRun, ...]
    comparable: bool


class CompareCoordinator:
    def __init__(self, run_variant: Callable[[str, str, str, str], VariantRun]):
        self.run_variant = run_variant

    def run(self, baseline_revision: str, candidate_revision: str, fixture_id: str,
            *, repeat: int = 1, start_with: str = "baseline") -> CompareManifest:
        if repeat < 1 or start_with not in {"baseline", "candidate"}:
            raise CoordinationError("compare: invalid repeat or batch order")
        runs = []
        for repetition in range(repeat):
            first = start_with if repetition % 2 == 0 else ("candidate" if start_with == "baseline" else "baseline")
            order = (first, "candidate" if first == "baseline" else "baseline")
            for variant in order:
                revision = baseline_revision if variant == "baseline" else candidate_revision
                batch_id = f"batch-{repetition + 1}-{variant}"
                try:
                    result = self.run_variant(variant, revision, fixture_id, batch_id)
                except Exception as exc:
                    result = VariantRun(variant, revision, fixture_id, batch_id, False, f"stage failed: {type(exc).__name__}")
                runs.append(result)
        comparable = all(run.success and run.fixture_id == fixture_id for run in runs)
        return CompareManifest(baseline_revision, candidate_revision, fixture_id, tuple(runs), comparable)
