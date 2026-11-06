# Implementation status

## Completed

- SD-01: package skeleton and console entry point, version/help, source layout.
- SD-02: strict schema-versioned YAML configuration model, synthetic fixture,
  and focused positive/negative tests.
- SD-03: transactional SQLite schema migration with project partitioning,
  composite foreign keys, indexes, and future-version rejection tests.
- SD-04: canonical project-bound storage path resolution with traversal,
  invalid-ID, cross-project, and symlink-escape protections.
- SD-05: default-deny span/resource sanitization, URL query removal, and
  bounded diagnostic redaction tests.
- SD-06: bounded OTLP JSON import with ID/timestamp validation, sanitization,
  duplicate handling, and conflict incompleteness.
- SD-07: SQLGlot-backed PostgreSQL shape normalization with literal removal
  and metadata-only parse failure behavior.
- SD-08: HTTP operation identity normalization with approved services,
  method/path distinction, query removal, and dynamic-ID templating.
- SD-09: versioned semantic operation grouping with bounded parent paths,
  multiset ordering independence, and explicit operation-ID precedence.
- SD-10: request-root coverage assessment with explicit incomplete reasons and
  no invented per-request denominator.
- SD-11: structural comparison for added/removed operations, changed call
  counts, changed error patterns, and sample-linked findings.
- SD-12: validated ResultV1 JSON envelope with provenance, coverage, findings,
  evidence IDs, and independent cleanup state.
- SD-13: read-only baseline/candidate OTLP import CLI with ResultV1 output and
  stable invalid/incomplete exit behavior.
- SD-14: read-only doctor checks for Git, Docker/Compose, adapter/config,
  fixtures, and named environment references.
- SD-15: explicit Git revision resolution, persisted commit IDs, and owned
  temporary worktree creation/removal using argument arrays.
- SD-16: dirty snapshot manifests with tracked patch digests and approved
  untracked-file allowlists excluding credentials and build output.
- SD-17: durable lifecycle transitions, event journaling, owned resource
  registration, and independent result/cleanup state.
- SD-18: safe Compose adapter command construction with unique ownership,
  approved environment injection, and bounded readiness polling.
- SD-19: approved destination and redirect policy with query removal and
  private/loopback address rejection.
- SD-20: bounded fixture preparation/reset hooks with write-scenario reset
  enforcement and failed-reset comparability suppression.
- SD-21: scenario request runner with warm-ups, measured batches, trace/sample
  context, bounded requests, response assertions, and write resets.
- SD-22: bounded collector flush/finalization with incomplete timeout state and
  late-span quarantine.
- SD-23: sequential baseline/candidate compare coordination with alternating
  batch order, fixture identity checks, and retained stage failures.
- SD-24: cancellation and resumable cleanup for exact registered resources,
  ownership tokens, pending failures, and safe repeated cleanup.
- SD-25: per-variant timing summaries with medians, batch counts, variation,
  non-summing overlap handling, and separate background metrics.
- SD-26: count-budget verdicts with incomplete gating, advisory timing
  warnings, and stable exit codes.
- SD-27: self-contained escaped HTML report foundation with semantic headings,
  variant metadata, coverage, findings, provenance, and prominent state.
- SD-28: finding detail anchors, sample evidence links, explicit uncertainty,
  and explicit missing-source handling in offline reports.
- SD-29: static CSS trace waterfall with bounded observation coordinates,
  overlap-safe individual durations, background distinction, and text fallback.
- SD-30: report usability regression fixtures and responsive/print/accessibility
  hardening for hostile, long, Unicode, empty, and large bounded content.
- SD-31: evidence-grounded coding-agent skill with references for evidence,
  adapters, interpretation, troubleshooting, and authority boundaries.
- SD-32: offline agent evaluation cases for known regressions, incomplete
  evidence, and untrusted trace instructions.
- SD-33: deterministic dependency-free orders fixture with stable/unchanged
  and N+1 variants, outgoing dependency substitute, and reconciled counters.
- SD-34: security regression coverage for seeded secrets, boundary escapes,
  hostile HTML, finite limits, and cleanup ownership.
- SD-35: reproducible workload-qualified calibration with descriptive overhead,
  variation/noise labels, and advisory timing recommendations.
- Source and installed-package checks are recorded in `VALIDATION.md`.

## Next

- SD-36: pilot record template added, but completion is blocked until three
  independent supported repositories provide real observations.
- SD-37: local Windows packaging/path/cancellation/port checks recorded, but
  completion is blocked until Linux and Docker Desktop checks run.
- SD-38: CI artifact workflow remains unimplemented.

## Not implemented

Trace measurement execution, Docker orchestration, HTML reports, CI, and the
coding-agent skill remain unimplemented. Reserved folders are placeholders.
No other backlog ticket is marked complete.
