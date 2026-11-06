"""Safe operation shape normalization. Implementation pending its backlog ticket."""
from .sql import SqlIdentity, normalize_sql
from .http import HttpIdentity, normalize_http
from .grouping import OperationGroup, OperationObservation, group_operations

__all__ = [
    "HttpIdentity", "OperationGroup", "OperationObservation", "SqlIdentity",
    "group_operations", "normalize_http", "normalize_sql",
]
