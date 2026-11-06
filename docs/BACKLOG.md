# Feature backlog

Retained ticket prompts from the SpanDiff Feature Ticket List. Only SD-01 is implemented.

## SD-01 Package skeleton

Milestone: M1 | Requirement: PRD-13 | Dependencies: None

**Prompt:** Create the Python package and console entry point under src/spandiff with the architecture folders, pyproject metadata and a version command. Keep behavior otherwise empty.

**Acceptance:** A clean install exposes spandiff; version exits 0; package imports without Docker.

## SD-02 Configuration model

Milestone: M1 | Requirement: PRD-01 | Dependencies: 01

**Prompt:** Implement schema_version 1 validation for project, adapter, Compose service, scenarios, assertions, budgets, finite limits and named credential references. Parse YAML safely and reject unknown versions.

**Acceptance:** Valid fixture loads; bad field paths are actionable; shell commands require explicit opt-in; no secret values are accepted as credential config.

## SD-03 Evidence migrations

Milestone: M1 | Requirement: PRD-04 | Dependencies: 01

**Prompt:** Implement the project-partitioned SQLite tables and composite keys defined in the Technical Architecture document, with foreign keys and transactional numbered migrations.

**Acceptance:** Fresh and existing supported databases open; future versions fail safely; cross-experiment references are rejected.

## SD-04 Storage path boundary

Milestone: M1 | Requirement: PRD-12 | Dependencies: 02

**Prompt:** Implement canonical owned-storage resolution, project identity partitioning and experiment-ID validation, including symlink escape rejection.

**Acceptance:** Traversal and cross-project access fail; paths with spaces work; legitimate owned paths resolve.

## SD-05 Sanitization pipeline

Milestone: M1 | Requirement: PRD-12 | Dependencies: 02

**Prompt:** Implement a default-deny span/resource attribute sanitizer plus safe diagnostic formatting. Remove bodies, credentials, bind values and URL query values before persistence.

**Acceptance:** Seeded secrets never appear in sanitizer output or error text; unknown attributes are discarded; permitted operation metadata remains.

## SD-06 OTLP import validation

Milestone: M1 | Requirement: PRD-03 | Dependencies: 03,04,05

**Prompt:** Implement a bounded importer for the selected pinned Collector OTLP JSON format. Validate IDs, timestamps and schema, sanitize records and persist only safe evidence with import provenance.

**Acceptance:** Valid golden input imports; malformed or oversized input is rejected safely; duplicate span keys do not inflate counts; conflicting duplicates are recorded.

## SD-07 SQL shape normalization

Milestone: M1 | Requirement: PRD-05 | Dependencies: 05

**Prompt:** Implement PostgreSQL parser-based normalization that removes literals and retains meaningful operators, joins and list structure. On parse failure discard raw SQL and return unknown metadata-only identity.

**Acceptance:** Literal variants share a safe shape; distinct joins/operators remain distinguishable; malformed SQL leaks no values.

## SD-08 HTTP operation normalization

Milestone: M1 | Requirement: PRD-05 | Dependencies: 05

**Prompt:** Implement outgoing HTTP identity from approved service, method and reliable templated path. Remove query values and handle unknown dynamic routes using validated rules.

**Acceptance:** Secret query values and dynamic identifiers do not persist; distinct approved methods and templates remain distinct.

## SD-09 Operation grouping

Milestone: M1 | Requirement: PRD-05 | Dependencies: 06,07,08

**Prompt:** Implement versioned semantic aliases and multiset grouping using service, kind, type, normalized shape and bounded parent path; prefer stable explicit operation IDs.

**Acceptance:** Reordered concurrent spans group consistently; renamed or ambiguous identities are flagged; raw span IDs never define identity.

## SD-10 Coverage assessment

Milestone: M1 | Requirement: PRD-06 | Dependencies: 06

**Prompt:** Implement request-root correlation assessment and coverage summaries from available sample metadata, exporter health, orphan spans, missing parents and dropped records.

**Acceptance:** Missing roots and dropped evidence make affected scenarios incomplete; import without request denominators never invents per-request metrics.

## SD-11 Structural comparison

Milestone: M1 | Requirement: PRD-05 | Dependencies: 09,10

**Prompt:** Implement added/absent groups, repeated call counts and changed error patterns across comparable samples, retaining finding IDs and sample references.

**Acceptance:** N+1 and new HTTP fixtures are detected; unchanged fixture has no invented differences; every count resolves to samples.

## SD-12 Result JSON contract

Milestone: M1 | Requirement: PRD-07 | Dependencies: 11

**Prompt:** Implement validated ResultV1 serialization and safe inspect JSON output using the shared result model with provenance, coverage, findings and cleanup state.

**Acceptance:** Round trip preserves evidence IDs and uncertainty; unsupported versions fail; output contains no secrets.

## SD-13 Import CLI command

Milestone: M1 | Requirement: PRD-03 | Dependencies: 02,06,12

**Prompt:** Wire baseline/candidate file import to sanitized storage, comparison and JSON generation with explicit provenance and missing-context handling.

**Acceptance:** Valid trace pair produces an experiment; invalid input exits 3; insufficient comparability exits 2.

## SD-14 Doctor checks

Milestone: M2 | Requirement: PRD-01 | Dependencies: 02

**Prompt:** Implement read-only prerequisite checks for Git, Docker/Compose, adapter config, fixture contract, instrumentation and named environment references.

**Acceptance:** Missing prerequisites have actionable messages; no application starts; credential values are never printed.

## SD-15 Revision worktrees

Milestone: M2 | Requirement: PRD-02 | Dependencies: 04

**Prompt:** Implement explicit baseline/candidate revision resolution and owned temporary worktrees without modifying the active checkout.

**Acceptance:** Resolved commit IDs persist; invalid refs stop safely; checkout contents remain unchanged; owned worktrees can be removed.

## SD-16 Dirty snapshot

Milestone: M2 | Requirement: PRD-02 | Dependencies: 15,05

**Prompt:** Implement explicit --candidate worktree snapshots recording a tracked patch digest and approved untracked file allowlist. Exclude environment files, credentials and build output.

**Acceptance:** Requested edits appear in snapshot; exclusions hold; the manifest distinguishes dirty snapshot from HEAD.

## SD-17 Lifecycle journal

Milestone: M2 | Requirement: PRD-10 | Dependencies: 03,04

**Prompt:** Implement durable lifecycle transitions and owned-resource registration before stage advancement, with independent result and cleanup states.

**Acceptance:** Interrupted transitions preserve recoverable state; invalid transitions fail; cleanup_pending does not erase results.

## SD-18 Compose environment adapter

Milestone: M2 | Requirement: PRD-08 | Dependencies: 15,17

**Prompt:** Implement the FastAPI Compose adapter startup with randomized ownership, isolated networks/volumes, approved environment injection and bounded readiness.

**Acceptance:** Two experiments cannot collide; readiness timeout is explicit; containers lack host socket and evidence-store access.

## SD-19 Destination restrictions

Milestone: M2 | Requirement: PRD-12 | Dependencies: 18

**Prompt:** Implement approved destination and egress checks for scenario HTTP requests, including redirects and destination resolution. Reject unapproved and production endpoints.

**Acceptance:** Redirect and alternate-host negative fixtures fail; approved synthetic dependency requests work; diagnostics are sanitized.

## SD-20 Fixture preparation and reset

Milestone: M2 | Requirement: PRD-08 | Dependencies: 18,19

**Prompt:** Implement preparation and reset hooks as argument arrays with finite timeouts and equivalent fixture identity. Require reset before each write sample.

**Acceptance:** Read-only fixtures prepare reproducibly; writes without reset are rejected; failed reset suppresses comparability.

## SD-21 Scenario request runner

Milestone: M2 | Requirement: PRD-08 | Dependencies: 20

**Prompt:** Implement warm-up and measured requests with random sample IDs, trace context, client timing, status/JSON assertions and recorded batch membership.

**Acceptance:** Default scenario records 5 warm-ups and 30 measured samples; assertion failures are explicit; credentials never enter evidence.

## SD-22 Collector lifecycle and flush

Milestone: M2 | Requirement: PRD-06 | Dependencies: 18,21,10

**Prompt:** Integrate the pinned Collector format with pre-persistence redaction, bounded shutdown flush, request-root correlation and finalization deadlines.

**Acceptance:** Real instrumented sample reaches evidence; missing exporter data yields incomplete; late spans cannot silently change finalized counts.

## SD-23 Compare coordinator

Milestone: M2 | Requirement: PRD-08 | Dependencies: 16,17,20,21,22

**Prompt:** Implement compare orchestration across sequential variants with equivalent fixtures and alternating batch order, calling existing stage interfaces.

**Acceptance:** Known scenario completes both variants; manifests record revisions and environment fingerprints; stage failures retain safe evidence.

## SD-24 Cancellation and cleanup

Milestone: M3 | Requirement: PRD-10 | Dependencies: 17,18

**Prompt:** Implement cancellation of owned process groups/containers and resumable clean <id> using exact registered resource IDs and ownership labels.

**Acceptance:** Cancellation at each stage cleans resources or lists cleanup_pending; unrelated resources survive; repeated cleanup is safe.

## SD-25 Timing summaries

Milestone: M3 | Requirement: PRD-09 | Dependencies: 11,21

**Prompt:** Implement per-variant medians, sample counts, batch membership and variation summaries from comparable samples, separating client, server and operation time.

**Acceptance:** Overlapping spans are never summed into request time; unavailable metrics remain unavailable; background work is separate.

## SD-26 Verdict and exit policy

Milestone: M3 | Requirement: PRD-09 | Dependencies: 10,11,25

**Prompt:** Implement count-budget verdicts, incomplete gating and advisory absolute/relative timing thresholds. Map states to exits 0 through 4 consistently.

**Acceptance:** Complete budget violation exits 1; incomplete exits 2; timing warnings do not fail initial release; JSON and CLI agree.

## SD-27 Offline report foundation

Milestone: M3 | Requirement: PRD-07 | Dependencies: 12,26

**Prompt:** Implement self-contained escaped HTML using the Frontend Specification tokens, semantic headings, variant metadata, state and coverage summary.

**Acceptance:** Report loads without network requests or scripts; hostile strings render as text; incomplete and cleanup states are prominent.

## SD-28 Finding and evidence navigation

Milestone: M3 | Requirement: PRD-07 | Dependencies: 27

**Prompt:** Add finding table/detail anchors and sample/span detail sections to the offline report, with explicit uncertainty and reliable evidence references.

**Acceptance:** Every finding links to its samples within two activations; missing source location is explicit; all anchor targets exist.

## SD-29 Trace waterfall

Milestone: M3 | Requirement: PRD-07 | Dependencies: 28

**Prompt:** Implement static CSS waterfall and equivalent ordered span text, distinguishing overlapping and background work with units and observation bounds.

**Acceptance:** Parallel fixture does not imply summed elapsed time; keyboard and narrow-layout readers can inspect every span.

## SD-30 Report usability verification

Milestone: M3 | Requirement: PRD-07 | Dependencies: 27,28,29

**Prompt:** Add report acceptance fixtures for long names, zero samples, large bounded traces, Unicode, malformed markup, narrow width, zoom and print. Correct defects found.

**Acceptance:** Evidence remains readable; state is conveyed without color; no external asset or secret is present; documented keyboard/contrast checks pass.

## SD-31 Coding agent skill

Milestone: M4 | Requirement: PRD-11 | Dependencies: 12,23,26

**Prompt:** Create skills/spandiff/SKILL.md and evidence, adapter, interpretation and troubleshooting references. Require explicit variants and finding/sample citations; preserve uncertainty and rerun requested fixes.

**Acceptance:** Skill handles unsupported repos and incomplete data; trace instructions grant no authority; verification retains original and follow-up experiment IDs.

## SD-32 Agent evaluations

Milestone: M4 | Requirement: PRD-11 | Dependencies: 31

**Prompt:** Create evaluations using known regressions, incomplete evidence and misleading trace instructions to verify evidence-grounded explanation and permission boundaries.

**Acceptance:** Conclusions cite existing IDs; no unsupported source cause is asserted as fact; prompt-like trace content is ignored as instruction.

## SD-33 Instrumented demo fixture

Milestone: M5 | Requirement: PRD-08 | Dependencies: 23,24,26

**Prompt:** Build the FastAPI orders example with deterministic PostgreSQL data, unchanged and N+1 variants, outgoing HTTP substitute and counters to cross-check span counts.

**Acceptance:** Repeated runs detect known structural changes; unchanged variant stays stable; application counters reconcile with evidence.

## SD-34 Security regression suite

Milestone: M5 | Requirement: PRD-12 | Dependencies: 05,24,27,33

**Prompt:** Exercise seeded secrets across success/failure logs and artifacts, path escapes, cross-project access, HTML injection, limits and cleanup ownership.

**Acceptance:** No seeded secret persists; negative boundary checks fail safely; evidence loss is incomplete; unrelated resources are untouched.

## SD-35 Measurement calibration

Milestone: M5 | Requirement: PRD-09 | Dependencies: 25,33

**Prompt:** Run unchanged-code batches and instrumented/uninstrumented fixture experiments. Record workload, sample size, variation and tracing overhead; recommend timing defaults without enabling p99 gating.

**Acceptance:** Calibration results are reproducible and workload-qualified; noisy data is labeled; no unsupported statistical certainty is claimed.

## SD-36 Three repository pilot

Milestone: M5 | Requirement: PRD-01 | Dependencies: 31,33

**Prompt:** Apply setup workflow to three independent supported repositories and record time after prerequisites, manual steps, finding usefulness and repeated use.

**Acceptance:** Pilot record contains real observations and blockers; targets are distinguished from achieved results; no repository secrets are included.

## SD-37 Platform packaging checks

Milestone: M6 | Requirement: PRD-13 | Dependencies: 24,26,34

**Prompt:** Validate install, paths with spaces, subprocess cancellation, port collisions and Docker integration on Linux and Windows with Docker Desktop. Publish only verified support.

**Acceptance:** Supported-platform matrix matches passing checks; missing dependencies and cancellations have stable outcomes.

## SD-38 CI artifact workflow

Milestone: M6 | Requirement: PRD-13 | Dependencies: 30,32,35,36,37

**Prompt:** Add an opt-in CI workflow using scoped test credentials, stable exits and sanitized HTML/JSON artifact publication with retention. Document installation and dependency notices.

**Acceptance:** Artifacts are sanitized; budget/incomplete/failure states remain distinct; no automatic PR comment or external upload beyond configured CI artifacts is introduced.
