# Deterministic orders fixture

This fixture is intentionally dependency-free for offline tests. It models the
supported FastAPI orders workload: deterministic order data, a local outgoing
dependency substitute, and counters that can be reconciled with imported span
operation groups. The `baseline` and `unchanged` variants use one bounded order
query; `n-plus-one` repeats an item query per order while returning the same
payload.

The fixture does not start a server, connect to PostgreSQL, or access secrets.
The real Compose adapter remains responsible for an integration run.
