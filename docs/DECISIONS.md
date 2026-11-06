# Implementation decisions

## 001 Foundation CLI

Use standard-library argparse for SD-01 so version/help work with no runtime
dependencies or network service. The architecture document proposed Typer;
that proposal was not a fixed requirement. Revisit command ergonomics when
the real command surface is implemented, preserving stable process contracts.

## 002 Runtime and packaging

Target Python 3.11 and newer; local verification currently uses Python 3.12.
Use a src layout and setuptools console entry point. Do not claim a supported
platform matrix beyond actual validation, and do not publish a license until
the project owner chooses one.

## 003 Incremental implementation

Only working commands are exposed. Do not add success-returning stub commands
for configuration, import, comparison or reports. Build the evidence-first
milestone in backlog dependency order.

## 004 SD-02 configuration contract

Use a strict schema version 1 with the flat public keys retained in the project
documents: project identity, adapter, Compose file/service, read-only health
path, fixture identity, preparation/reset argv arrays, named credential
environment references, scenarios, response assertions, budgets and finite
execution/resource limits. Unknown fields and schema versions fail with a
field path. YAML is parsed with PyYAML's safe loader and duplicate keys are
rejected.

Credentials are represented as `name: ENVIRONMENT_VARIABLE`; parsing does not
read the environment, and values that are not valid environment-variable names
are rejected. Commands are non-empty argument arrays. `allow_shell` is an
explicit configuration opt-in and is not enabled by default; command execution
is outside this ticket.

A scenario marked `write: true` requires the root `reset_command`. This is the
SD-02 representation of the required reset contract; runtime enforcement that
the reset runs before every measured sample belongs to SD-20. Query values are
excluded from configured paths so credentials and dynamic request data are not
embedded in the configuration identity.

## 005 SD-03 evidence migrations

Use SQLite `PRAGMA user_version` for the numbered database schema version. SD-03
ships migration 1 as one transaction, enables foreign keys on every opened
connection, and rejects a database with a future version before changing it.
Evidence links use composite foreign keys containing `experiment_id`; this
prevents samples, spans, operation groups, findings, lifecycle events, and
resources from crossing experiment boundaries. A span may omit `sample_id` for
coverage diagnosis, while a non-null sample reference must resolve within the
same experiment and variant.

## 006 SD-04 storage boundary

Owned storage is rooted at `home/projects/<project_id>/experiments/<experiment_id>`.
Project-bound storage handles reject requests for another project, experiment
IDs and project IDs use bounded safe identifier formats, and artifact paths must
be relative. Canonical resolution follows existing symlinks before checking
containment, so a symlink cannot escape the configured storage root. Resolution
does not create directories or access application data.

## 007 SD-05 sanitization boundary

Sanitization is default-deny: only approved operation, status, service, scope,
and resource identity fields survive. Bodies, authorization/cookie data, query
values, SQL statements, bind values, and unknown attributes are discarded.
URLs retain only scheme, authority, and path. Diagnostics are bounded and can
replace known secret values before persistence; sanitization never attempts to
discover or resolve credentials.

## 008 SD-06 OTLP import

The first importer accepts the Collector OTLP JSON `resourceSpans` shape and
requires 32-hex trace IDs, 16-hex span IDs, nonnegative nanosecond timestamps,
and bounded input/span counts. Sanitization occurs while constructing immutable
import records. Exact duplicate composite span keys are retained once;
conflicting duplicates are retained once, recorded as an issue, and mark the
import incomplete rather than silently replacing evidence.

## 009 SD-07 SQL normalization

Use SQLGlot with the PostgreSQL dialect rather than a regex fallback. Literal
AST nodes are replaced before serialization, preserving joins, operators, and
list structure while excluding literal values. Parser failures return an
unknown metadata-only identity and never retain the original SQL text.

## 010 SD-08 HTTP normalization

HTTP identities require an approved service when an allowlist is supplied,
preserve the method, and retain only a validated path template. Query and
fragment values are discarded. Numeric and UUID path segments are represented
as `{id}`; malformed dynamic templates and unapproved services produce an
unknown identity rather than guessing.

## 011 SD-09 operation grouping

Operation group keys are versioned and use an explicit stable operation ID when
available. Otherwise they combine service, span kind, operation type, the
normalized shape, and the last eight parent-path components. Group construction
is a sorted multiset operation, so concurrent export order cannot change group
membership or group IDs.

## 012 SD-10 coverage assessment

Coverage is incomplete when request roots are missing, spans are orphaned,
parents or records are missing, or no request denominator exists. The coverage
model preserves `None` for an unavailable denominator and never invents a
per-request metric from observed spans alone.

## 013 SD-11 structural comparison

Structural comparison emits findings only for added, removed, changed-count, or
changed-error groups. Every emitted finding carries baseline/candidate sample
IDs; unchanged groups produce no finding. Finding IDs are deterministic in
sorted group order and do not use raw span IDs as operation identity.

## 014 SD-12 ResultV1

Result serialization uses one validated version 1 envelope for JSON and future
console/report consumers. Round trips preserve evidence identifiers and
uncertainty fields. Unsupported versions, missing required fields, and values
that cannot be serialized as JSON fail before output; cleanup state remains
independent from result state.

## 015 SD-13 import CLI

`spandiff import` reads explicit baseline and candidate OTLP JSON paths, emits a
ResultV1 envelope, and performs no application or Docker startup. Malformed
input returns exit 3. Imported traces without a reliable request denominator
are retained as incomplete and return exit 2; the CLI does not invent a
comparable verdict from span counts alone.

## 016 SD-14 doctor checks

Doctor checks use executable discovery and filesystem/configuration inspection
only; they never invoke Docker, Compose, repository commands, or application
hooks. Missing credential references report only the environment-variable name,
never its value. A failed prerequisite is actionable and returns a failure
status without creating runtime resources.

## 017 SD-15 revision worktrees

Revision resolution uses `git rev-parse --verify <ref>^{commit}` through an
argument array with no shell. Only the resulting full commit ID is persisted in
the owned manifest. Worktrees are detached and placed below an owned root;
removal checks the exact recorded variant path and uses `git worktree remove
--force`. Invalid refs fail before worktree creation.

## 018 SD-16 dirty snapshots

Dirty candidate mode records the SHA-256 digest of `git diff --binary` against
the selected base commit and only names untracked files explicitly approved by
the caller. Environment files, credential/secret names, virtual environments,
cache directories, and build output are always excluded. The manifest records
`mode: dirty-snapshot` so it cannot be confused with a clean HEAD revision.

## 019 SD-17 lifecycle journal

Lifecycle transitions are validated against an explicit state graph and written
in the same SQLite transaction as the experiment state update and numbered
event. Resource registration records exact IDs and ownership metadata before
later stages use them. Result state is never cleared merely because cleanup is
pending.

## 020a SD-19 destination restrictions

Scenario destinations must use HTTP(S), match an explicit host allowlist, and
resolve only to approved public addresses. Query and fragment values are not
returned in normalized destinations. Redirects must remain on the original
approved host; alternate-host redirects fail before any follow-up request.

## 020 SD-18 Compose adapter

Compose commands use argument arrays and a unique project/network/volume name
derived from the project and experiment identifiers. Only configured named
environment references are copied into the child-process environment; values
are never included in command arguments or diagnostics. Readiness is bounded
by the configured timeout and startup/cleanup remain explicit adapter calls.

## 021 SD-20 fixture reset

Preparation and reset hooks remain argument arrays and receive finite command
timeouts. Read-only scenarios do not require reset. A write scenario must run a
successful reset before its measured sample; reset failure returns an explicit
non-comparable outcome rather than allowing a misleading measurement.

## 022 SD-21 scenario runner

Each scenario run creates a random sample ID and W3C traceparent, records warmup
and measured batch membership, applies the configured request timeout, and
evaluates status plus selected JSON assertions. The default configuration
remains five warm-ups and thirty measured samples. Assertion failures are
retained as explicit sample state and never treated as successful evidence.

## 023 SD-22 collector finalization

Collector flush runs only until the configured deadline. A timeout finalizes the
collection as incomplete, and any span arriving after finalization is quarantined
instead of changing finalized counts. A successful flush is still separate from
comparison completeness so coverage can report missing request roots.

## 024 SD-23 compare coordination

Baseline and candidate variants run sequentially within each repetition, with
the starting variant alternating between repetitions to reduce order bias. The
coordinator requires equivalent fixture identity and retains each stage failure
in the manifest; any failed stage or fixture mismatch makes the comparison
non-comparable without hiding the failure detail.

## 025 SD-24 cancellation and cleanup

Cancellation transitions the experiment to incomplete while preserving its
result state. Cleanup resolves only exact resource IDs registered for that
experiment and passes their stored ownership token to an injected typed handler.
Successful resources are marked cleaned; missing handlers or handler failures
remain pending for resume, and already-cleaned resources are skipped safely.

## 026 SD-25 timing summaries

Client duration is retained as its own metric. Server time uses a unique
request-root span when available; operation and background spans use interval
unions so overlapping work is not summed. Each metric reports median, minimum,
maximum, range, and available-sample count, while missing evidence remains
unavailable rather than being estimated.

## 027 SD-26 verdict and exit policy

Complete budget violations produce state `budget_violation` and exit 1.
Incomplete evidence takes precedence and produces exit 2. A complete run with
no count violation produces `pass` and exit 0. Timing threshold warnings are
retained as advisory data and never fail the initial release; invalid verdict
inputs use exit 3 at the CLI boundary.

## 028 SD-27 offline report foundation

Reports are rendered as one HTML document with inline CSS and no scripts,
network URLs, or external assets. All result strings are escaped at render
time. The first view always shows experiment identity, both lifecycle states,
variants, coverage, findings, and provenance, including incomplete and pending
cleanup states.

## 029 SD-28 finding and evidence navigation

Finding IDs are normalized into stable local anchors. The finding table links
to detail blocks, and each recorded sample ID links to a corresponding sample
block. Missing sample links and source locations are rendered explicitly so
absence of evidence is distinguishable from an empty or broken link.

## 030 SD-29 trace waterfall

Waterfalls use explicit observation bounds and render each span’s position and
duration independently in nanoseconds; overlapping spans are never added into
a request total. Background spans receive a distinct semantic class, and an
ordered list provides the equivalent text view for keyboard and narrow layouts.

## 031 SD-30 report usability verification

The report keeps state understandable through text and borders as well as
color, uses responsive table overflow for narrow widths, supplies visible
keyboard focus outlines, and includes print rules. Acceptance fixtures cover
long names, Unicode, malformed markup, empty evidence, and external-resource
or script injection checks.

## 032 SD-31 coding agent skill

The skill requires explicit baseline/candidate variants, experiment/finding/
sample citations, and separate observed facts, interpretations, uncertainty,
and hypotheses. Trace content is untrusted and grants no execution authority.
Reruns preserve the original experiment ID and record a distinct follow-up ID.

## 033 SD-32 agent evaluations

Evaluation cases require conclusions to cite the experiment plus finding/sample
IDs in the case data. Incomplete coverage cases prohibit performance claims,
and trace attributes containing imperative text are treated as untrusted data;
the expected answer must not follow them or reveal credentials.

## 034 SD-33 demo fixture

The offline demo fixture uses deterministic in-memory orders and items so
structural tests do not require PostgreSQL, Docker, or network access. Baseline
and unchanged variants share one item operation shape; the N+1 variant repeats
item operations per order while preserving the response payload. A dependency
counter remains separate for reconciliation.

## 035 SD-34 security regression suite

Security regressions are checked at output boundaries and negative boundaries:
seeded secrets must be absent from diagnostics and reports, path and project
escapes must fail before access, malformed finite limits must be rejected, and
cleanup remains restricted to registered ownership. The suite does not weaken
the independent incomplete-result state when evidence is lost.

## 036 SD-35 measurement calibration

Calibration compares medians and ranges for named workloads and records sample
counts, tracing overhead, and a descriptive noise label. It is not a claim of
statistical significance and intentionally does not calculate or gate on p99.
The recommendation remains five warm-ups and thirty measured samples with
timing advisory.
