# Validation

SD-01 validation performed on Windows with bundled Python 3.12.14.

- Built a wheel offline with setuptools; no runtime dependencies downloaded.
- Installed the wheel into a new isolated .venv.
- Installed console entry point returned SpanDiff 0.1.0.dev0.
- CLI help loaded without Docker.
- All 5 unittest checks passed, including module execution, version, help and invalid-command exit 3.
- The target path includes spaces and the build/install/tests succeeded there.

Python 3.11, Linux, Docker execution and later-ticket behavior have not been validated.

SD-02 validation performed on Windows with the local Python 3.12.14 `.venv`.

- Reinstalled the updated package editable and installed PyYAML 6.0.3 from the declared `PyYAML>=6.0,<7` range.
- The focused configuration suite passed 7 tests.
- Complete unittest discovery passed 12 tests.
- Checks covered valid loading, unsupported schema versions, unknown field paths, malformed YAML, argument-array commands, credential-value rejection, and write/reset validation.
- Configuration parsing performed no application startup or Docker execution.
Source edits were validated by reinstalling editable mode in the local `.venv`.

SD-03 validation performed on Windows with the local Python 3.12.14 `.venv`.

- Focused evidence database suite passed 4 tests.
- Complete unittest discovery passed 16 tests.
- Checks covered fresh migration, supported database reopen, future-version
  rejection without mutation, transactional rollback, enabled foreign keys,
  and cross-experiment sample/span reference rejection.

SD-04 validation performed on Windows with the local Python 3.12.14 `.venv`.

- Focused storage boundary suite passed 4 tests with 1 platform skip because
  symbolic-link creation was unavailable in the test environment.
- Complete unittest discovery passed 20 tests with 1 expected skip.
- Checks covered paths containing spaces, traversal, absolute paths, invalid
  identifiers, project-bound cross-project access, and symlink escape logic.

SD-05 validation performed on Windows with the local Python 3.12.14 `.venv`.

- Focused sanitizer suite passed 3 tests.
- Complete unittest discovery passed 23 tests with 1 expected platform skip.
- Seeded token, body, authorization, query, SQL, bind, and unknown attributes were absent from sanitized output; URL values and diagnostics were bounded.

SD-06 validation performed on Windows with the local Python 3.12.14 `.venv`.

- Focused OTLP import suite passed 3 tests.
- Complete unittest discovery passed 26 tests with 1 expected platform skip.
- Checks covered valid sanitized import, exact duplicate collapse, conflicting duplicate incompleteness, malformed JSON, invalid IDs, and byte/span limits.

SD-07 validation performed on Windows with the local Python 3.12.14 `.venv`.

- Reinstalled editable package with SQLGlot 27.29.0 from the declared `sqlglot>=27.0,<28` range.
- Focused SQL normalization suite passed 3 tests.
- Complete unittest discovery passed 29 tests with 1 expected platform skip.
- Checks covered literal equivalence, preserved join/operator distinctions, and parse failure without raw SQL retention.

SD-08 validation performed on Windows with the local Python 3.12.14 `.venv`.

- Focused HTTP normalization suite passed 3 tests.
- Complete unittest discovery passed 32 tests with 1 expected platform skip.
- Checks covered query removal, numeric-ID templating, method distinction, approved-service filtering, and ambiguous-route rejection.

SD-09 validation performed on Windows with the local Python 3.12.14 `.venv`.

- Focused grouping suite passed 2 tests.
- Complete unittest discovery passed 34 tests with 1 expected platform skip.
- Checks covered ordering-independent multiset grouping and explicit operation-ID precedence.

SD-10 validation performed on Windows with the local Python 3.12.14 `.venv`.

- Focused coverage suite passed 3 tests.
- Complete unittest discovery passed 37 tests with 1 expected platform skip.
- Checks covered missing roots, missing request denominators, complete coverage, and explicit incompleteness reasons.

SD-11 validation performed on Windows with the local Python 3.12.14 `.venv`.

- Focused structural comparison suite passed 2 tests.
- Complete unittest discovery passed 39 tests with 1 expected platform skip.
- Checks covered added operations, changed repeated-call counts, sample-linked findings, and unchanged groups without invented differences.

SD-12 validation performed on Windows with the local Python 3.12.14 `.venv`.

- Focused ResultV1 suite passed 2 tests.
- Complete unittest discovery passed 41 tests with 1 expected platform skip.
- Checks covered JSON round-trip preservation of evidence IDs, unsupported versions, required fields, cleanup state, and unsafe values.

SD-13 validation performed on Windows with the local Python 3.12.14 `.venv`.

- Focused CLI suite passed 7 tests.
- Complete unittest discovery passed 43 tests with 1 expected platform skip.
- Checks covered valid baseline/candidate import output, incomplete exit 2 when no request denominator exists, malformed input exit 3, and no application startup.

SD-14 validation performed on Windows with the local Python 3.12.14 `.venv`.

- Focused doctor suite passed 2 tests.
- Complete unittest discovery passed 45 tests with 1 expected platform skip.
- Checks covered actionable missing prerequisites, configured Compose files, named environment references without values, and no application/container startup.

SD-15 validation performed on Windows with the local Python 3.12.14 `.venv`.

- Focused revision suite passed 3 tests.
- Complete unittest discovery passed 48 tests with 1 expected platform skip.
- Checks covered argument-array ref resolution, invalid-reference rejection before worktree creation, persisted commit IDs, owned worktree destinations, and exact removal commands.

SD-16 validation performed on Windows with the local Python 3.12.14 `.venv`.

- Focused dirty snapshot suite passed 2 tests.
- Complete unittest discovery passed 50 tests with 1 expected platform skip.
- Checks covered tracked patch hashing, explicit untracked allowlists, missing-file rejection, and exclusion of environment files and build output.

SD-17 validation performed on Windows with the local Python 3.12.14 `.venv`.

- Focused lifecycle suite passed 2 tests.
- Complete unittest discovery passed 52 tests with 1 expected platform skip.
- Checks covered valid transition journaling, invalid transition rejection, owned resource registration, and cleanup-pending state without erasing result state.

SD-18 validation performed on Windows with the local Python 3.12.14 `.venv`.

- Focused Compose adapter suite passed 3 tests.
- Complete unittest discovery passed 55 tests with 1 expected platform skip.
- Checks covered unique Compose ownership names, argument-array commands, approved in-memory credentials, missing prerequisites, and bounded readiness timeout.

SD-19 validation performed on Windows with the local Python 3.12.14 `.venv`.

- Focused destination suite passed 3 tests.
- Complete unittest discovery passed 58 tests with 1 expected platform skip.
- Checks covered approved destinations, query removal, unapproved hosts, private/loopback resolution, and alternate-host redirects.

SD-20 validation performed on Windows with the local Python 3.12.14 `.venv`.

- Focused fixture suite passed 3 tests.
- Complete unittest discovery passed 61 tests with 1 expected platform skip.
- Checks covered bounded preparation/reset argv execution, read-only scenarios without reset, write reset enforcement, and failed-reset comparability suppression.

SD-21 validation performed on Windows with the local Python 3.12.14 `.venv`.

- Focused scenario runner suite passed 2 tests.
- Complete unittest discovery passed 63 tests with 1 expected platform skip.
- Checks covered five warm-ups/30 measured defaults, random W3C trace context, explicit response assertion failures, and reset-before-write samples.

SD-22 validation performed on Windows with the local Python 3.12.14 `.venv`.

- Focused collector flush suite passed 2 tests.
- Complete unittest discovery passed 65 tests with 1 expected platform skip.
- Checks covered successful finalization, bounded flush timeout incompleteness, and quarantine of late spans.

SD-23 validation performed on Windows with the local Python 3.12.14 `.venv`.

- Focused compare coordinator suite passed 2 tests.
- Complete unittest discovery passed 67 tests with 1 expected platform skip.
- Checks covered sequential baseline/candidate execution, alternating batch order,
  fixture identity enforcement, and retained stage failures.

SD-24 validation performed on Windows with the local Python 3.12.14 `.venv`.

- Focused cleanup suite passed 2 tests.
- Complete unittest discovery passed 69 tests with 1 expected platform skip.
- The updated package was installed into the local editable `.venv`.
- Checks covered cancellation to incomplete state, exact registered-resource
  ownership, pending cleanup failures, unknown-resource rejection, and safe
  repeated cleanup.

SD-25 validation performed on Windows with the local Python 3.12.14 `.venv`.

- Focused timing summary suite passed 2 tests.
- Complete unittest discovery passed 71 tests with 1 expected platform skip.
- The updated package was installed into the local editable `.venv`.
- Checks covered medians, batch membership, variation, overlapping interval
  unions, separate background work, and unavailable metrics.

SD-26 validation performed on Windows with the local Python 3.12.14 `.venv`.

- Focused verdict suite passed 3 tests.
- Complete unittest discovery passed 74 tests with 1 expected platform skip.
- The updated package was installed into the local editable `.venv`.
- Checks covered pass, complete budget violation, incomplete precedence,
  advisory timing warnings, and invalid input rejection.

SD-27 validation performed on Windows with the local Python 3.12.14 `.venv`.

- Focused HTML report suite passed 2 tests.
- Complete unittest discovery passed 76 tests with 1 expected platform skip.
- The updated package was installed into the local editable `.venv`.
- Checks covered self-contained inline CSS, semantic sections, escaped hostile
  strings, prominent incomplete/cleanup states, and absence of scripts or
  external resources.

SD-28 validation performed on Windows with the local Python 3.12.14 `.venv`.

- Focused HTML navigation suite passed 3 tests.
- Complete unittest discovery passed 77 tests with 1 expected platform skip.
- The updated package was installed into the local editable `.venv`.
- Checks covered finding/detail anchors, sample links, anchor targets, escaped
  identifiers, and explicit missing source locations.

SD-29 validation performed on Windows with the local Python 3.12.14 `.venv`.

- Focused waterfall suite passed 2 tests.
- Complete unittest discovery passed 79 tests with 1 expected platform skip.
- The updated package was installed into the local editable `.venv`.
- Checks covered observation bounds, individual nanosecond units, overlap-safe
  positioning, background spans, escaping, and ordered text fallback.

SD-30 validation performed on Windows with the local Python 3.12.14 `.venv`.

- Focused report usability suite passed 2 tests.
- Complete unittest discovery passed 81 tests with 1 expected platform skip.
- The updated package was installed into the local editable `.venv`.
- Checks covered long names, zero evidence, Unicode, malformed markup
  escaping, narrow-layout CSS, print CSS, keyboard focus, and no scripts or
  external assets.

SD-31 validation performed on Windows with the local Python 3.12.14 `.venv`.

- Focused skill contract suite passed 1 test.
- Complete unittest discovery passed 82 tests with 1 expected platform skip.
- The updated package was installed into the local editable `.venv`.
- Checks covered explicit variant/citation requirements, uncertainty guidance,
  follow-up experiment IDs, safety references, and rejection of trace authority.

SD-32 validation performed on Windows with the local Python 3.12.14 `.venv`.

- Focused evaluation contract suite passed 1 test.
- Complete unittest discovery passed 83 tests with 1 expected platform skip.
- The updated package was installed into the local editable `.venv`.
- Checks covered known regression citations, incomplete-evidence restraint,
  forbidden causal claims, and prompt-like trace instruction rejection.

SD-33 validation performed on Windows with the local Python 3.12.14 `.venv`.

- Focused demo fixture suite passed 2 tests.
- Complete unittest discovery passed 85 tests with 1 expected platform skip.
- The updated package was installed into the local editable `.venv`.
- Checks covered stable unchanged output, known N+1 operation counts, outgoing
  dependency counter reconciliation, and invalid variant rejection without
  side effects.

SD-34 validation performed on Windows with the local Python 3.12.14 `.venv`.

- Focused security regression suite passed 3 tests.
- Complete unittest discovery passed 88 tests with 1 expected platform skip.
- The updated package was installed into the local editable `.venv`.
- Checks covered seeded secret absence, path and project boundaries, hostile
  report content, invalid finite limits, and safe failure behavior.

SD-35 validation performed on Windows with the local Python 3.12.14 `.venv`.

- Focused calibration suite passed 2 tests.
- Complete unittest discovery passed 90 tests with 1 expected platform skip.
- The updated package was installed into the local editable `.venv`.
- Checks covered reproducible workload labels, sample counts, median overhead,
  variation, noisy-data labeling, advisory recommendations, and no p99 field.

SD-36 status review performed on Windows with the local Python 3.12.14 `.venv`.

- No pilot completion is claimed: three independent external repositories and
  real operator observations are not present in this workspace.
- Added [PILOT.md](./PILOT.md) as an explicit, secret-free record template.

SD-37 status review performed on Windows with the local Python 3.12.14 `.venv`.

- Focused local platform suite passed 2 tests.
- Verified editable package import, paths containing spaces, subprocess
  cancellation, and port collision behavior.
- Linux and Docker Desktop checks were not run; SD-37 remains incomplete.

SD-36 pilot execution performed on Windows on 2026-11-06.

- Three public repositories were shallow-cloned at recorded revisions outside
  the workspace.
- Python syntax compilation passed for all three repositories.
- SpanDiff doctor ran against all three temporary configurations; all returned
  exit 4 due to unavailable Git/Docker/Compose prerequisites, with the third
  repository additionally missing Compose configuration.
- No application was started, no repository credentials were read, and no
  pilot completion claim is made because setup duration, finding usefulness,
  and repeated-use observations require runnable environments.
