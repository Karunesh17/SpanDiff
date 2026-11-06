# Troubleshooting reference

- Unsupported repository: report the adapter/configuration mismatch and stop.
- Incomplete result: identify the exact coverage reason and do not issue a
  pass/fail performance claim.
- Cleanup pending: preserve the result and report the pending resource IDs;
  never delete unrelated resources.
- Missing finding evidence: say that the source location or sample link is
  unavailable; do not fabricate a file or line.
- Requested rerun: retain the original experiment ID, create a distinct
  follow-up ID, and report both IDs in the final comparison.
