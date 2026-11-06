# Validation gaps and safe continuation plan

Full audit mode was used, but this is a **partial, source-only audit with incomplete validation**. No complete security assurance is claimed. Required OS execution isolation is not established, and both mandatory validator CLIs reject Windows file-opening capabilities. Independent source verification and supplemental in-memory schema checks do not replace those requirements.

## Candidate status

Independently retained needs_validation records: **0**. Unvalidated candidate fingerprints: **0**. Four prior fingerprints received independent source rejection and a distinct final record review; [findings.json](./findings.json) preserves those decisions. They must not be described as confirmed or needs_validation findings. A changed future integration can introduce a new boundary and warrant a new review.

## Run-level blockers — no severity assigned

| Gap | Exact unresolved capability or fact | Safe resolution |
| --- | --- | --- |
| OS-enforced target execution | No verified backend combines external-network denial, empty allowlisted environment, read-only target/toolchain, scratch-only writes and low CPU/memory/process/file-size/disk/wall-clock limits. WSL is not installed; Docker CLI presence alone is insufficient. | Provide an already available isolated backend enforcing all controls. Use only local dependencies; no downloads, shared Docker resources or live endpoints. Use dummy fixtures and stop at minimum results. |
| Artifact promotion | Trusted no-follow, handle-relative, bounded regular-file promotion with identity/link-count verification is not established. | Establish the skill's exact parent-side promotion protocol before retaining any target-written output. Keep allowlists and byte limits explicit; do not copy/glob scratch. Source-only JSON messages are not execution evidence. |
| Mandatory validator CLIs | Both official scripts exit 1 because required no-follow/nonblocking OS file flags are unavailable in Windows Node. | Run the unmodified validators on an OS with the required file protections against regular bounded report files. Do not disable guards. Supplemental exported-function checks here passed but do not satisfy this gate. See exact commands/errors in [validation-log.json](./validation-log.json). |
| Runtime and platform behavior | No current tests/builds/fixtures, default Git runner, browser renderer or real Compose/HTTP integration were executed. Historical tests are not audit evidence. | In the approved sandbox, run narrow offline tests first with dummy data, controlled temp/cache/HOME, read-only source or a disposable scratch source copy, and strict process-tree termination. No network dependency installation. |
| External integration authority | Source does not establish a lower-trust file submitter, link writer, experiment selector, real transport, Docker runner, cleanup handler ACLs or external agent tool identity. | Owner reviews the exact integration source and ACL/ownership/action bindings without reading credential values or probing deployed services. Do not assume hosted multitenancy, external readers or shared workers merely to preserve a lead. |
| Dependencies and release | No lockfile/current authoritative resolved dependency set, advisory analysis or hosted CI policy was established. No tracked CI/IAM/deployment policy implements those controls. | Owner supplies a non-secret resolved dependency inventory and release/CI policy for review. Local offline advisory data may support follow-up; do not contact registries or publish during validation. |

## Bounded regression work once isolation exists

These check source-hardening contracts; they do not imply a currently demonstrated unauthorized effect.

1. Two disposable project/experiment trees: exercise explicit traversal, outside-home links and within-home cross-scope links; compare the returned path with selected scope. Start at [src/spandiff/evidence/storage.py:40](../src/spandiff/evidence/storage.py#L40). A real security claim additionally needs a source-visible lower-trust writer and protected consumer.
2. Fake-runner adapter tests: compare colliding identifier pairs and stop-only/failed-start teardown arguments, without starting Docker. Start at [src/spandiff/adapters/compose.py:29](../src/spandiff/adapters/compose.py#L29) and [src/spandiff/adapters/compose.py:67](../src/spandiff/adapters/compose.py#L67). Test actual daemon ownership only in an independently isolated dummy fixture if a real integration exists.
3. Tiny configured byte/sample caps: verify reject-before-read/allocation and reject-before-request behavior with fake requesters and bounded files, not large stress payloads. Start at [src/spandiff/cli/__init__.py:61](../src/spandiff/cli/__init__.py#L61) and [src/spandiff/collection/runner.py:57](../src/spandiff/collection/runner.py#L57).
4. Deterministic fake-clock timeout then repeated flush; subset cleanup with two dummy registered resources; callback identity mismatch and ResultV1 state consistency. Start at [src/spandiff/collection/flush.py:34](../src/spandiff/collection/flush.py#L34), [src/spandiff/orchestration/cleanup.py:62](../src/spandiff/orchestration/cleanup.py#L62) and [src/spandiff/orchestration/coordinator.py:36](../src/spandiff/orchestration/coordinator.py#L36).
5. Dummy privacy markers through every intended export channel and hostile markup through HTML/waterfall; no real credentials. Agent evaluations should verify actual host tool/action authorization and cross-context isolation, rather than only checking safety strings, if an agent runtime is integrated.
6. Default Git and normalization checks must use disposable repositories/inputs, bounded output, strict resource limits and no external processes selected from target configuration. Existing fake-runner tests alone do not establish those runtime contracts.

No live-probe instructions, real accounts, production calls, paid API spending, stress tests or third-party systems are part of this plan.
