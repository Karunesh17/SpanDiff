# SpanDiff architecture and audit scope

Full audit mode, standard profile; all tracked application source, tests, example/configuration, packaging and agent-skill inputs. Target: `$REPOSITORY_ROOT`, branch `main`, commit `e04968ec258882fd3b5b944b329bc79414f7d06f`; initial Git porcelain status empty. No target code execution is approved because the required complete OS sandbox is not available.

## Product, principals and authority

SpanDiff is a local Python trace-comparison CLI and evidence-interpretation skill. The local operator intentionally selects trace/config/output files. The repository/configuration author is trusted to select fixture commands and Compose definitions; execution is intended for trusted repositories and synthetic test data (README.md:58). A library integrator supplies privileged callbacks. Trace/result producers supply lower-trust content to parsers, renderers and an external coding agent. Project identifiers scope local storage; there is no implemented remote authentication, user/account service or hosted multitenancy contract.

Protected resources are local source/worktrees, evidence and journals, caller-provided credential values, experiment-owned resources and an interpreting agent's existing authority. OS user permissions, real callback implementations, shared-service deployment and external agent permissions are not established by this repository.

## Stack, entries and local operation

Python >=3.11, setuptools>=68, PyYAML>=6,<7, SQLGlot>=27,<28 (pyproject.toml:1). Console `spandiff` and module execution call `spandiff.cli:main` (pyproject.toml:14; src/spandiff/__main__.py:3). CLI exposes version, import and doctor only (src/spandiff/cli/__init__.py:23). Documentation that says trace files are not read is stale relative to this dispatch (README.md:56).

Import reads baseline/candidate UTF-8 JSON, sanitizes attributes, deduplicates spans, and emits counts/path provenance in an always-incomplete ResultV1 because no request denominator exists (cli/__init__.py:59; collection/otlp_json.py:63). Doctor parses YAML, checks executable/file presence and credential-reference presence without starting services (orchestration/doctor.py:44). Library execution is not connected to a run/compare CLI.

Offline tests could use `python -B -m unittest discover -s tests -v` with dependencies already installed. Tests create temporary JSON, SQLite/journals, directories, child processes and loopback sockets. Builds require a scratch source copy and locally present setuptools/pip; normal editable install can fetch dependencies and is prohibited. No build, test, import, browser rendering or fixture processing ran in this audit.

## Source-to-sink boundaries

- YAML file -> SafeLoader with duplicate-key rejection -> strict field/schema/argv/reference model; configuration is not command-executed during parsing (config/loader.py:13; config/model.py:176).
- OTLP-like JSON file -> byte check -> JSON parser -> validated IDs/timestamps -> sanitized attributes and retained span fields (collection/otlp_json.py:63). Names/parent/kind/status are separate from allowlisted attributes.
- Library SQL/HTTP observations -> normalization -> semantic groups -> structural findings and timing summaries -> count-budget verdicts (normalization/sql.py:18; normalization/http.py:24; normalization/grouping.py:28; comparison/structural.py:28; reporting/verdict.py:29). No automatic CLI pipeline joins these stages.
- Caller project/experiment/artifact selectors -> optional project binding -> path resolution -> shared-home containment (evidence/storage.py:26). SQLite uses experiment-qualified relationships and enabled foreign keys (evidence/database.py:204).
- Lifecycle details -> JSON and parameterized transactional journal; registered resource selectors -> experiment-filtered lookup -> injected cleanup handler (orchestration/lifecycle.py:48; cleanup.py:43).
- Git refs -> argv subprocess -> commit validation -> owned worktree paths; dirty diff -> digest/filename manifest (orchestration/revisions.py:37; snapshot.py:45). Defaults inherit process environment and capture output.
- Repository Compose config + selected environment references -> injected runner; derived ownership namespace -> start/down commands (adapters/compose.py:29). Actual Docker policy is external. No tracked runnable Compose/Docker deployment or CI workflow is present; the example references missing files/scripts.
- Scenario -> injected requester with trace headers; standalone DestinationPolicy checks allowlisted host and optional DNS answers, with no source attachment to transport (collection/runner.py:49; security/destination.py:29).
- Result -> escaped HTML/restricted fragment anchors and separate escaped waterfall -> offline reader (reporting/html.py:27; waterfall.py:24). Result text -> external coding agent, with written no-authority/citation instructions (skills/spandiff/SKILL.md:8,28). No model client, RAG index, model tool dispatcher or paid API loop is implemented.

## Prior evidence and domain selection

Prior run-1 is incomplete, its eight units remain planned, and its four needs_validation records have no qualifying execution evidence. Current source at each prior trace was re-read; current work includes all four leads and all prior gaps. No prior confirmed exclusion exists. The earlier chat reconnaissance is context, not validation evidence.

Selected domains: AI/LLM for agent consumption of report data; client-side for offline HTML; data isolation/lifecycle for project evidence and cleanup; cloud/deployment for Compose authority; resource exhaustion for imported files/callback work; supply chain for packaging and dependencies. Ordinary classes cover injection, access, files/SSRF/deserialization, secrets, logic, leakage, chains, wildcard and obvious exposures.

No HTTP server/session/cookie or identity protocol implements CSRF/auth bypass; no upload endpoint/archive extraction, RPC/broker, native memory code, desktop/mobile/IPC endpoint, cloud IAM policy or deployed ingress is source-visible. These absent surfaces are applicability exclusions, not assurances about an external integration. Dependency CVE status and unobserved deployments cannot be established offline. OTLP and W3C tracing are source-grounded protocol references, not competing-product security baselines.
