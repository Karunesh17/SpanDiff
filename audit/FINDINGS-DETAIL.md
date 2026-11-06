# Confirmed findings detail

Full audit mode was used, but this is a **partial, source-only audit with incomplete validation**. No complete security assurance is claimed. Required OS execution isolation is not established, and both mandatory validator CLIs reject Windows file-opening capabilities. Independent source verification and supplemental in-memory schema checks do not replace those requirements.

Confirmed findings: **0**. There are no confirmed medium, high or critical records and therefore no qualifying exploit reproduction, observed security impact or severity rationale to present. No target code was executed and no runtime effect is claimed.

The four prior claims were independently rejected, not silently omitted or relabeled as needs_validation. Their complete ordered source traces, evidence, strongest controls and reasons are in [findings.json](./findings.json) and the rejection section of [REPORT.md](./REPORT.md). Source-hardening recommendations and regression suggestions are separate from findings.

Runtime and workflow limitations are documented in [NEEDS-VALIDATION.md](./NEEDS-VALIDATION.md), [run-metadata.json](./run-metadata.json) and [validation-log.json](./validation-log.json). The lack of confirmed findings is not a security assurance.
