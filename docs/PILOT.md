# Three-repository pilot record

SD-36 is not complete. The acceptance contract requires real observations from
three independent supported repositories, including setup time after
prerequisites, manual steps, finding usefulness, repeated-use observations,
and blockers. This workspace contains only SpanDiff and its synthetic orders
fixture, so no external-repository observations are claimed.

## Observed pilot candidates — 2026-11-06

These are public shallow clones kept outside the workspace at
`D:\Temp\spandiff-pilot-20261106`. Their checkout files were not modified.

| Repository and revision | Observed setup/workload facts | Checks run | Outcome/blocker |
| --- | --- | --- | --- |
| [darioblanco/fastapi-example](https://github.com/darioblanco/fastapi-example) `193609b1bdeb871965885b95a97010fa31a08e0a` | Poetry project; `container/docker-compose.yml`; app service `app`; PostgreSQL and healthchecks present; README documents `/docs` and test commands | Python syntax compilation; SpanDiff doctor | Syntax passed. Doctor recognized adapter, Compose file, service, and fixture contract; exit 4 because Git/Docker/Compose are unavailable in PATH. No application run. |
| [caarmen/fastapi-postgres-docker-example](https://github.com/caarmen/fastapi-postgres-docker-example) `d3227f556313dca9272aaede903b60379a7c5d15` | `requirements.txt`; `compose.yml`; server service; PostgreSQL dependency; root endpoint documented; repository README warns that a password is committed in its `.env` | Python syntax compilation; SpanDiff doctor | Syntax passed. Doctor recognized adapter, Compose file, service, fixture contract; exit 4 because Git/Docker/Compose are unavailable and the named `POSTGRES_PASSWORD` reference is not set. No secret value was read or recorded. |
| [MariyaSha/Simple_API_Example](https://github.com/MariyaSha/Simple_API_Example) `db80a4ebfe87b2c27874fdde5f08808b0cf32a71` | `requirements.txt`; `nj_server.py`; documented `/warehouse/tomatoes` endpoint; no Compose file or test suite found | Python syntax compilation; SpanDiff doctor | Syntax passed. Doctor recognized the config but reported the missing Compose file; exit 4 because Git/Docker/Compose and Compose configuration are unavailable. No application run. |

Clone/setup duration after prerequisites was not measured separately, because
the required Docker/Compose and repository dependency environments were not
available. Finding usefulness and repeated-use observations therefore remain
unverified rather than being inferred from static inspection.

## Required record per repository

| Field | Observation |
| --- | --- |
| Repository identity | Pending selected supported repository |
| Prerequisite completion time | Pending real observation |
| Manual steps | Pending real observation |
| First-run result | Pending real observation |
| Repeated-use result | Pending real observation |
| Finding usefulness | Pending user/operator observation |
| Blockers | Pending real observation |
| Secret review | Must confirm no credentials or private data are recorded |

Targets, once supplied, must be distinguished from achieved results. No
repository credentials or private URLs belong in this record.
