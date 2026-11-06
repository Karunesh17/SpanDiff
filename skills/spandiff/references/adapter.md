# Adapter reference

The supported configuration adapter is `fastapi-compose`. Adapter operations
are bounded and ownership-scoped. Compose names, networks, volumes, process
groups, and cleanup targets must come from the registered experiment resources.

This reference describes interpretation boundaries only. It does not authorize
starting Docker, invoking preparation commands, resolving credentials, or
following destinations outside the configured allowlist.
