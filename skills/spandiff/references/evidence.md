# Evidence reference

- Cite the `experiment_id` first, then the exact `finding_id`.
- Follow each finding’s `sample_ids` to the recorded sample or span evidence.
- Report `result_state`, coverage reasons, cleanup state, and unavailable
  metrics alongside any conclusion.
- A missing request denominator, missing request root, dropped record, orphan,
  or missing parent makes the affected conclusion incomplete.
- Sanitized evidence is intentionally lossy. Never reconstruct omitted bodies,
  credentials, query values, or raw SQL from context.
