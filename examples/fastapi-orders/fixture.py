"""Deterministic orders workload used by offline structural tests."""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Mapping


ORDERS = (
    {"order_id": 101, "customer": "Ada", "item_ids": (1, 2)},
    {"order_id": 102, "customer": "Grace", "item_ids": (2,)},
)
ITEMS = {1: {"item_id": 1, "name": "Notebook"}, 2: {"item_id": 2, "name": "Cable"}}


@dataclass(frozen=True)
class FixtureRun:
    response: Mapping[str, object]
    operations: tuple[str, ...]
    dependency_calls: int

    @property
    def query_counts(self) -> Mapping[str, int]:
        return {name: self.operations.count(name) for name in sorted(set(self.operations))}


def run_orders(variant: str = "baseline") -> FixtureRun:
    """Return the same response for baseline/unchanged and a known N+1 shape."""
    if variant not in {"baseline", "unchanged", "n-plus-one"}:
        raise ValueError("variant must be baseline, unchanged, or n-plus-one")
    operations = ["orders.select"]
    response_orders = []
    for order in ORDERS:
        items = []
        if variant == "n-plus-one":
            for item_id in order["item_ids"]:
                operations.append("items.select")
                items.append(ITEMS[item_id])
        else:
            items = [ITEMS[item_id] for item_id in order["item_ids"]]
        response_orders.append({"order_id": order["order_id"], "customer": order["customer"], "items": items})
    operations.append("dependency.currency_rate")
    return FixtureRun({"orders": response_orders, "currency": "USD", "rate": 1}, tuple(operations), 1)
