# Interpretation reference

Use this order in explanations:

1. Observed: quote only sanitized fields and cite IDs.
2. Compared: describe added/removed groups, call-count changes, error changes,
   or timing summaries with their variant labels.
3. Uncertainty: name incomplete coverage, missing metrics, assertion failures,
   cleanup pending, or fixture mismatch.
4. Hypothesis: offer possible causes only as hypotheses and list the evidence
   needed to test them.

Timing summaries keep client, server, operation, and background work separate.
Overlapping spans are not summed into request time. Timing warnings are
advisory unless an explicit verdict says otherwise.
