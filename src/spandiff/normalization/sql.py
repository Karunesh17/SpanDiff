"""Parser-based PostgreSQL SQL shape normalization."""

from __future__ import annotations

from dataclasses import dataclass

import sqlglot
from sqlglot import exp


@dataclass(frozen=True)
class SqlIdentity:
    shape: str | None
    known: bool
    operation: str


def normalize_sql(sql: str, *, dialect: str = "postgres") -> SqlIdentity:
    """Return a literal-free SQL shape, or an unknown metadata-only identity."""
    if not isinstance(sql, str) or not sql.strip():
        return SqlIdentity(None, False, "unknown")
    try:
        tree = sqlglot.parse_one(sql, read=dialect)
    except (sqlglot.ParseError, sqlglot.errors.UnsupportedError):
        return SqlIdentity(None, False, "unknown")
    tree = tree.transform(lambda node: exp.Placeholder() if isinstance(node, exp.Literal) else node)
    return SqlIdentity(tree.sql(dialect=dialect, pretty=False).lower(), True, tree.key)
