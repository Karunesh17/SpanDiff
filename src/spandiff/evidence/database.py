"""Project-partitioned SQLite evidence database and numbered migrations."""

from __future__ import annotations

import sqlite3
from pathlib import Path


LATEST_SCHEMA_VERSION = 1


class MigrationError(RuntimeError):
    """Raised when a database cannot be safely migrated."""


_MIGRATION_1 = (
    """
    CREATE TABLE projects (
        project_id TEXT PRIMARY KEY,
        canonical_root_hash TEXT NOT NULL UNIQUE,
        display_name TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE experiments (
        experiment_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        schema_version INTEGER NOT NULL,
        baseline_revision TEXT NOT NULL,
        candidate_revision TEXT NOT NULL,
        snapshot_hash TEXT,
        config_hash TEXT NOT NULL,
        tool_version TEXT NOT NULL,
        state TEXT NOT NULL,
        result_state TEXT NOT NULL,
        cleanup_state TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects(project_id)
    )
    """,
    """
    CREATE TABLE variants (
        experiment_id TEXT NOT NULL,
        variant TEXT NOT NULL CHECK (variant IN ('baseline', 'candidate')),
        revision TEXT NOT NULL,
        image_digest TEXT NOT NULL,
        lock_hash TEXT NOT NULL,
        fixture_id TEXT NOT NULL,
        environment_fingerprint TEXT NOT NULL,
        instrumentation_json TEXT NOT NULL,
        PRIMARY KEY (experiment_id, variant),
        FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
    )
    """,
    """
    CREATE TABLE samples (
        experiment_id TEXT NOT NULL,
        variant TEXT NOT NULL,
        sample_id TEXT NOT NULL,
        scenario_id TEXT NOT NULL,
        batch_id TEXT NOT NULL,
        sequence INTEGER NOT NULL,
        assertion_state TEXT NOT NULL,
        client_duration_ns INTEGER,
        coverage_state TEXT NOT NULL,
        PRIMARY KEY (experiment_id, variant, sample_id),
        FOREIGN KEY (experiment_id, variant)
            REFERENCES variants(experiment_id, variant)
    )
    """,
    """
    CREATE TABLE spans (
        experiment_id TEXT NOT NULL,
        variant TEXT NOT NULL,
        trace_id TEXT NOT NULL,
        span_id TEXT NOT NULL,
        sample_id TEXT,
        parent_id TEXT,
        kind TEXT NOT NULL,
        service TEXT NOT NULL,
        scope TEXT NOT NULL,
        start_ns INTEGER NOT NULL,
        end_ns INTEGER NOT NULL,
        status TEXT NOT NULL,
        attributes_json TEXT NOT NULL,
        evidence_path TEXT NOT NULL,
        PRIMARY KEY (experiment_id, variant, trace_id, span_id),
        FOREIGN KEY (experiment_id, variant, sample_id)
            REFERENCES samples(experiment_id, variant, sample_id)
    )
    """,
    """
    CREATE TABLE operation_groups (
        experiment_id TEXT NOT NULL,
        group_id TEXT NOT NULL,
        identity_version INTEGER NOT NULL,
        identity_json TEXT NOT NULL,
        ambiguity_state TEXT NOT NULL,
        PRIMARY KEY (experiment_id, group_id),
        FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
    )
    """,
    """
    CREATE TABLE group_spans (
        experiment_id TEXT NOT NULL,
        group_id TEXT NOT NULL,
        variant TEXT NOT NULL,
        trace_id TEXT NOT NULL,
        span_id TEXT NOT NULL,
        PRIMARY KEY (experiment_id, group_id, variant, trace_id, span_id),
        FOREIGN KEY (experiment_id, group_id)
            REFERENCES operation_groups(experiment_id, group_id),
        FOREIGN KEY (experiment_id, variant, trace_id, span_id)
            REFERENCES spans(experiment_id, variant, trace_id, span_id)
    )
    """,
    """
    CREATE TABLE findings (
        experiment_id TEXT NOT NULL,
        finding_id TEXT NOT NULL,
        group_id TEXT,
        rule_id TEXT NOT NULL,
        severity TEXT NOT NULL,
        budget_state TEXT NOT NULL,
        summary_json TEXT NOT NULL,
        uncertainty_json TEXT NOT NULL,
        PRIMARY KEY (experiment_id, finding_id),
        FOREIGN KEY (experiment_id, group_id)
            REFERENCES operation_groups(experiment_id, group_id)
    )
    """,
    """
    CREATE TABLE finding_samples (
        experiment_id TEXT NOT NULL,
        finding_id TEXT NOT NULL,
        variant TEXT NOT NULL,
        sample_id TEXT NOT NULL,
        PRIMARY KEY (experiment_id, finding_id, variant, sample_id),
        FOREIGN KEY (experiment_id, finding_id)
            REFERENCES findings(experiment_id, finding_id),
        FOREIGN KEY (experiment_id, variant, sample_id)
            REFERENCES samples(experiment_id, variant, sample_id)
    )
    """,
    """
    CREATE TABLE lifecycle_events (
        experiment_id TEXT NOT NULL,
        event_sequence INTEGER NOT NULL,
        stage TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        sanitized_detail_json TEXT NOT NULL,
        PRIMARY KEY (experiment_id, event_sequence),
        FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
    )
    """,
    """
    CREATE TABLE resources (
        experiment_id TEXT NOT NULL,
        resource_id TEXT NOT NULL,
        kind TEXT NOT NULL,
        ownership_token TEXT NOT NULL,
        locator TEXT NOT NULL,
        cleanup_state TEXT NOT NULL,
        last_error_code TEXT,
        PRIMARY KEY (experiment_id, resource_id),
        FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
    )
    """,
    "CREATE INDEX samples_scenario_variant ON samples(scenario_id, variant)",
    "CREATE INDEX spans_sample ON spans(sample_id)",
    "CREATE INDEX findings_rule ON findings(rule_id)",
    "CREATE INDEX lifecycle_sequence ON lifecycle_events(experiment_id, event_sequence)",
)


def _current_version(connection: sqlite3.Connection) -> int:
    return int(connection.execute("PRAGMA user_version").fetchone()[0])


def migrate(connection: sqlite3.Connection) -> int:
    """Apply supported migrations transactionally and return the schema version."""
    current = _current_version(connection)
    if current > LATEST_SCHEMA_VERSION:
        raise MigrationError(
            f"unsupported future database schema version {current}; "
            f"maximum supported version is {LATEST_SCHEMA_VERSION}"
        )
    if current == LATEST_SCHEMA_VERSION:
        return current
    try:
        connection.execute("BEGIN IMMEDIATE")
        if current == 0:
            for statement in _MIGRATION_1:
                connection.execute(statement)
            connection.execute(f"PRAGMA user_version = {LATEST_SCHEMA_VERSION}")
        connection.commit()
    except sqlite3.Error as exc:
        connection.rollback()
        raise MigrationError(f"migration to schema version {LATEST_SCHEMA_VERSION} failed: {exc}") from exc
    return LATEST_SCHEMA_VERSION


def open_database(path: str | Path) -> sqlite3.Connection:
    """Open an evidence database, enable FK enforcement, and migrate it."""
    connection = sqlite3.connect(str(path))
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        migrate(connection)
    except Exception:
        connection.close()
        raise
    return connection
