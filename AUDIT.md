# SpanDiff security audit publication

This repository contains the tracked SpanDiff source snapshot reviewed at commit `e04968ec258882fd3b5b944b329bc79414f7d06f` and the final source-review reports. The publication is a new repository snapshot, not a copy of the original Git history.

**The audit remains incomplete.** No compliant target execution sandbox was available, and mandatory validator CLI file protections were unavailable on the Windows audit host. No target tests or application code ran. Supplemental schema checks passed. Zero confirmed findings does not establish security.

- [Main report](./audit/REPORT.md)
- [Architecture](./audit/architecture.md)
- [Confirmed findings detail](./audit/FINDINGS-DETAIL.md)
- [Validation gaps and continuation plan](./audit/NEEDS-VALIDATION.md)
- [Structured records](./audit/findings.json)
- [Coverage ledger](./audit/coverage-ledger.json)
- [Run and publication metadata](./audit/run-metadata.json)

The reports record 0 confirmed findings across all severities, 0 retained needs-validation findings, and 4 independently rejected prior claims. Hardening recommendations are separate from vulnerabilities. The coverage ledger preserves those four resolved candidate units for audit history.

Publication copies replace local machine paths with placeholders and convert source links for GitHub. Original local reports remain unchanged. Audit support JSON preserves source checks, critics, independent record decisions and validation failures. Scratch prompts, execution environments, caches and build products are excluded.
