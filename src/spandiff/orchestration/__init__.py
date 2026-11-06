"""Experiment lifecycle and source preparation. Implementation pending its backlog ticket."""
from .doctor import DoctorCheck, DoctorReport, check_config, run_doctor
from .revisions import OwnedWorktree, ResolvedRevision, RevisionError, RevisionManager
from .snapshot import DirtySnapshot, DirtySnapshotter
from .lifecycle import LifecycleError, LifecycleJournal, LifecycleState
from .fixtures import FixtureError, FixtureManager, FixtureOutcome
from .coordinator import CompareCoordinator, CompareManifest, CoordinationError, VariantRun
from .cleanup import CleanupError, CleanupManager, CleanupReport, OwnedResource

__all__ = [
    "DoctorCheck", "DoctorReport", "OwnedWorktree", "ResolvedRevision",
    "RevisionError", "RevisionManager", "DirtySnapshot", "DirtySnapshotter",
    "LifecycleError", "LifecycleJournal", "LifecycleState",
    "FixtureError", "FixtureManager", "FixtureOutcome",
    "CompareCoordinator", "CompareManifest", "CoordinationError", "VariantRun",
    "CleanupError", "CleanupManager", "CleanupReport", "OwnedResource",
    "check_config", "run_doctor",
]
