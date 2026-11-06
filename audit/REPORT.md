# SpanDiff security audit report

Full audit mode was used, but this is a **partial, source-only audit with incomplete validation**. No complete security assurance is claimed. Required OS execution isolation is not established, and both mandatory validator CLIs reject Windows file-opening capabilities. Independent source verification and supplemental in-memory schema checks do not replace those requirements.

## Run identity, scope and provenance

- Target: $REPOSITORY_ROOT; branch **main**; commit **e04968ec258882fd3b5b944b329bc79414f7d06f**. Initial and final tracked/untracked porcelain status are empty; all 96 recorded textual source hashes are unchanged. Existing changes were preserved; none existed initially.
- Profile: **standard**, full-repository application-source scope. No user-set agent budget. 25 isolated fresh contexts, 31 delegated turn attempts including three serialization turns and three recovered usage-limit retries. Initial plan reserved 16 candidate/final verifier calls; actual work used eight. No independence or severity gate was relaxed.
- Skill: [Cloudflare security-audit](https://github.com/cloudflare/security-audit-skill), already installed at $SKILL_DIRECTORY. Installed content version: folder hash **ccbc33ed119b28c3ef7b44a7e2081ab191ad63af**; SKILL.md SHA-256 **2A68AB5531DFCCEDAC2B054E0814F2B6517DAAE9887B3EE40AFCC5D8A7063C3A**. No tagged version/upstream commit is asserted for the installed copy; [skill-manifest.json](./skill-manifest.json) pins all 20 installed files. No installation was necessary.
- Prior run: prior run-1 (historical local run; not included) was incomplete. Its eight planned units and four unresolved claims informed current work, after source re-reading. No prior confirmed finding, exclusion or runtime result was carried forward.
- Execution policy: **sandboxed-source-and-local-only**. No target code, tests, builds, fixtures, browser reports or applications were executed. Only trusted parent audit tooling, local read-only source/Git inspection and user-requested public skill documentation were accessed. No target/production or third-party test services were contacted; no credentials, publication, commit or push occurred.
- Six binary planning DOCX documents, generated/ignored build and environment contents, Git-history secret scanning, external dependency advisory resolution and external deployment/operator policies were excluded. These are explicit scope/validation limits, not covered assurances.

## Security posture and confirmed findings

The implemented product is a local CLI plus disconnected library contracts. Trusted repository configuration and injected privileged callbacks are intended authority. Trace/result text is lower-trust, but no hosted authentication service, shared requester, automatic artifact reader, LLM tool dispatcher or real Docker execution backend is integrated. Several narrow guarantees should be strengthened before such integrations. The absence of demonstrated findings does **not** mean the repository is secure.

| Severity | Confirmed count |
| --- | ---: |
| critical | 0 |
| high | 0 |
| medium | 0 |
| low | 0 |
| informational | 0 |

| Severity | Finding | Observed result |
| --- | --- | --- |
| None confirmed | — | No qualifying bounded execution evidence was produced. |

## NEEDS VALIDATION — independently retained candidates

| Candidate | Exact blocker |
| --- | --- |
| None retained | No source-grounded candidate survived independent review as needs_validation. This does not remove the run-level validation gaps below. |

There are **0 unvalidated ledger candidates**. The four ledger units with candidate status remain linked to **rejected** final records for audit history; they are not unresolved vulnerabilities. See [findings.json](./findings.json), [FINDINGS-DETAIL.md](./FINDINGS-DETAIL.md), and [NEEDS-VALIDATION.md](./NEEDS-VALIDATION.md).

## Prior claims rejected after independent review

These are not findings and receive no severity. Rejection concerns the proposed security lineage, not a claim that the underlying helper behavior is ideal. Every record retains its source trace, evidence and reason in [findings.json](./findings.json); four fresh Phase 5 reviewers additionally checked the final records.

### spandiff/compose/experiment-name-collision

Lossy normalization makes exp/a and exp-a derive identical ownership strings. This establishes a namespace correctness concern, but the repository exposes only a trusted library constructor with an injected runner, not a lower-trust experiment selector or an unauthorized resource operation. Network and volume ownership strings are not consumed by the adapter commands.

**Independent disposition:** Rejected as a security candidate because the first trace element is trusted library configuration rather than a demonstrated lower-trust boundary. Source searches found ComposeAdapter construction only in tests, and no CLI/service or lifecycle attachment allowing a separate principal to choose a colliding identifier. Actual network and volume names and concurrent cross-cleanup are also not established by the stored ownership strings. Collision-resistant naming could improve correctness, but inventing a multi-principal shared-daemon integration is required to turn this observation into an unauthorized effect. No target code was executed because the required OS sandbox is unavailable; that limitation does not preserve a candidate that lacks a source-grounded boundary.

- **entrypoint** [src/spandiff/adapters/compose.py:29](../src/spandiff/adapters/compose.py#L29) — ComposeAdapter.__init__: A library caller supplies the experiment identifier and optional privileged runner; this is not established as a lower-trust entrypoint.
- **propagation** [src/spandiff/adapters/compose.py:35](../src/spandiff/adapters/compose.py#L35) — ComposeAdapter.__init__: Lowercasing, regex replacement, and stripping can map distinct identifiers to the same string.
- **sink** [src/spandiff/adapters/compose.py:70](../src/spandiff/adapters/compose.py#L70) — ComposeAdapter.stop: With a caller-supplied runner, cleanup passes the derived project selector in a Compose down --volumes argument tuple; no cross-owner execution is demonstrated.

### spandiff/import/prelimit-full-read

Source confirms that the local operator-selected baseline file is fully read and imported before the candidate file is read and imported. Each read_text call precedes the importer's UTF-8 byte check. This establishes potentially unbounded pre-check local input buffering, but the implemented interface does not establish attacker submission to another principal's shared worker or a meaningful shared resource effect.

**Independent disposition:** Reject as a security finding under the applicable resource-exhaustion gate: the source-visible pre-limit full read is real, but the established interface requires a local operator to select and run an import and the established cost is that process's memory/CPU. No implemented remote submission boundary, shared worker pool, multitenant service, paid callback, persistent resource retention or other-principal availability effect is shown on this path. A hypothetical future shared-service wrapper is a new deployment assumption rather than a decisive missing fact for this local interface. File size limits before reads would be useful hardening; they do not establish the required meaningful shared effect. No target code, tests, imports, fixtures, builds or network were executed because the approved OS-enforced sandbox with network denial, allowlisted empty environment, read-only target/tools, scratch-only writes and explicit resource/wall-clock limits is unavailable. Thus no memory measurements or runtime consequences are claimed; this source-based gate rejection does not rely on execution or promoted artifacts.

- **entrypoint** [src/spandiff/cli/__init__.py:34](../src/spandiff/cli/__init__.py#L34) — main: The local CLI operator supplies required --baseline and --candidate file paths; dispatch at line 44 calls _import_pair. No upload or shared-service interface is implemented here.
- **propagation** [src/spandiff/cli/__init__.py:61](../src/spandiff/cli/__init__.py#L61) — _import_pair: The complete baseline UTF-8 text is passed to import_otlp_json before line 62 reads the candidate text. A baseline failure prevents the candidate read; both raw file strings are not necessarily retained together.
- **propagation** [src/spandiff/cli/__init__.py:62](../src/spandiff/cli/__init__.py#L62) — _import_pair: After baseline import succeeds, the complete candidate UTF-8 text is passed to the same importer while the baseline ImportResult remains retained.
- **sink** [src/spandiff/collection/otlp_json.py:67](../src/spandiff/collection/otlp_json.py#L67) — import_otlp_json: The size check allocates text.encode('utf-8') after receiving the full string, and rejects encoded length exceeding the default 50,000,000 bytes before JSON parsing.

### spandiff/limits/scenario-consumer-gap

ScenarioRunner does not receive RepositoryConfig.limits and uses caller-selected warmup and sample counts. This is a source-visible integration hardening gap, but the implemented local application does not expose scenario execution to a lower-trust requester or allocate another principal's shared capacity.

**Independent disposition:** Rejected as a security finding because ScenarioRunner.run is a library method whose caller supplies both the Scenario and requester callback, and source review establishes no implemented path from untrusted configuration authors to another principal's worker, quota or service allocation. Selecting excessive work for one's own injected callback is a reliability/hardening concern. The concurrency claim additionally lacks a concurrency effect because the runner is sequential. A hypothetical hosted integration would introduce a new trust boundary rather than validate this repository's trace. No target execution occurred because the required OS-enforced sandbox was unavailable; runtime absence does not preserve a candidate whose essential security boundary is unsupported by source.

- **entrypoint** [src/spandiff/collection/runner.py:57](../src/spandiff/collection/runner.py#L57) — ScenarioRunner.run: Actual execution entry is a library call supplying a Scenario; this is not an authenticated or lower-trust request handler.
- **propagation** [src/spandiff/collection/runner.py:58](../src/spandiff/collection/runner.py#L58) — ScenarioRunner.run: Caller-selected warmups and samples are iterated sequentially and retained as Sample records.
- **sink** [src/spandiff/collection/runner.py:72](../src/spandiff/collection/runner.py#L72) — ScenarioRunner._sample: Each iteration invokes the privileged requester callback provided by the same library integrator and passes the scenario timeout.

### spandiff/storage/resolve-shared-home-symlink

The resolver can canonicalize an artifact alias into a different project or experiment beneath the same home. This is a narrower containment guarantee than the experiment-relative wording suggests, but the repository exposes only a path-returning helper and establishes no lower-trust link producer or privileged reader/writer using its result.

**Independent disposition:** Reject as a security finding for this repository's established local-operator trust model. The source supports a helper containment/contract hardening gap, but the proposed trace begins with an ordinary library call and ends with a returned path, not unauthorized disclosure or mutation. No source-visible lower-trust principal can plant links for a more privileged storage consumer, no such consumer is integrated, and no affected owner or protected operation is established. An external integration would introduce a new trust boundary rather than supply a missing observation on an existing path. A two-project fixture would demonstrate only the already source-visible return scope. No target execution was performed because the required OS sandbox is unavailable; that does not prevent source-based rejection of the claimed security lineage.

- **entrypoint** [src/spandiff/evidence/storage.py:40](../src/spandiff/evidence/storage.py#L40) — OwnedStorage.resolve: Public library caller supplies selectors; this is not itself an established lower-trust request entrypoint.
- **propagation** [src/spandiff/evidence/storage.py:46](../src/spandiff/evidence/storage.py#L46) — OwnedStorage.resolve: Appends the artifact path to the canonical experiment root and calls _owned.
- **sink** [src/spandiff/evidence/storage.py:49](../src/spandiff/evidence/storage.py#L49) — OwnedStorage._owned: Canonicalizes links, checks home containment at line 50, and returns a Path at line 52; performs no artifact read or write.


## Highest-priority hardening and regression suggestions

These are source-grounded engineering priorities, **not severity-ranked vulnerabilities**. They have no demonstrated unauthorized effect in the current implementation.

| Priority | Source and narrow change | Why not a finding |
| --- | --- | --- |
| 1. Bind owned paths to the selected scope | [src/spandiff/evidence/storage.py:40](../src/spandiff/evidence/storage.py#L40). Constrain canonical project/experiment/artifact results to the selected root, then use an atomic no-follow access contract when integrating file reads/writes. Add within-home cross-project and cross-experiment link cases plus Windows junction/drive-relative cases. | Current helper returns paths only; no unauthorized reader/writer integration is implemented. |
| 2. Bind Compose teardown to collision-resistant ownership | [src/spandiff/adapters/compose.py:34](../src/spandiff/adapters/compose.py#L34). Derive an unambiguous digest-backed namespace from full project/experiment identity, record created resource ownership, and verify it at destructive teardown. Test case/punctuation and project/experiment delimiter collisions, stop-only and failed-start cleanup through a fake runner. | Only trusted library callers and injected runners are implemented; the collision is not a demonstrated cross-owner operation. |
| 3. Apply bounds before allocation and side effects | [src/spandiff/cli/__init__.py:61](../src/spandiff/cli/__init__.py#L61); [src/spandiff/collection/runner.py:57](../src/spandiff/collection/runner.py#L57). Read at most the configured byte cap plus one before decoding; apply one limit policy to combined warmups/samples, request deadlines, total spans/issues and output. Test with tiny caps and a fake requester, avoiding stress. | The present costs belong to the selecting local operator; no shared-service availability boundary is implemented. |
| 4. Preserve failed collector state on replay | [src/spandiff/collection/flush.py:34](../src/spandiff/collection/flush.py#L34). Retain and return the original finalization outcome; a repeated call must not turn a timeout into successful completion. Add timeout-then-repeat and late-span regressions. | Source shows a reliability/evidence-state defect; no authoritative security consumer is connected. |
| 5. Compute cleanup state over the whole experiment | [src/spandiff/orchestration/cleanup.py:62](../src/spandiff/orchestration/cleanup.py#L62). After subset cleanup, derive aggregate state from all registered resources. Define registration-after-cleanup behavior and handler ownership-token verification. Test two resources, cleaning one, then retrying the remaining one. | No implemented downstream authorization or retention consequence establishes a security finding. |
| 6. Define transport policy before wiring outbound execution | [src/spandiff/security/destination.py:29](../src/spandiff/security/destination.py#L29). Require complete address checks including IP literals and empty resolution, bind validated addresses to actual connections, revalidate redirects, and preserve/reject port and IPv6 forms explicitly. Reject network-path scenario references before URL joining. | The policy is standalone and ScenarioRunner supplies no concrete HTTP transport. |
| 7. Make privacy and agent authority contracts explicit | [src/spandiff/security/sanitizer.py:38](../src/spandiff/security/sanitizer.py#L38); [skills/spandiff/SKILL.md:28](../skills/spandiff/SKILL.md#L28). Specify which names/routes/identities and lifecycle/report fields may be exported; strip URL userinfo before introducing a diagnostic consumer. Treat agent instructions as guidance, with host-side resource/action authorization for any future tools. Use dummy secret markers and actual model/tool behavior tests only in an approved sandbox. | No current credential-to-unauthorized-reader lineage, model client, RAG store or tool dispatcher is implemented. |
| 8. Bound concrete Git/parser operations and strengthen evidence semantics | [src/spandiff/orchestration/revisions.py:37](../src/spandiff/orchestration/revisions.py#L37); [src/spandiff/orchestration/snapshot.py:35](../src/spandiff/orchestration/snapshot.py#L35); [src/spandiff/normalization/sql.py:18](../src/spandiff/normalization/sql.py#L18); [src/spandiff/reporting/result.py:44](../src/spandiff/reporting/result.py#L44). Bound captured output and deadlines, stream patch hashing, define process-tree cancellation, cap parser input/tree/cardinality, and normalize metadata-only failures. Validate result state/coverage consistency and callback variant/revision/batch identity; use stable semantic group keys. Add bounded fake/local fixture regressions once isolation is available. | No shared-process, approval or privilege consumer establishes security impact for these robustness gaps. |
| 9. Prepare reproducible release and integration checks | [pyproject.toml:1](../pyproject.toml#L1); [docs/PLATFORM.md:5](../docs/PLATFORM.md#L5). Use reviewed dependency constraints/hashes for release inputs, add least-privilege CI when CI exists, update stale implementation claims, and test actual Linux/Windows/Compose integration in isolation. | Floating ranges and absent automation alone are not vulnerabilities; no dependency CVE status or hosted CI policy was established. |

All 30 distinct hunter notes remain in [hunter-results.json](./hunter-results.json) and the ledger bookkeeping; this table consolidates related recommendations.

## Positive source patterns and applicability

- SafeLoader subclass, duplicate/unknown-field rejection and argv command shape: [src/spandiff/config/loader.py:13](../src/spandiff/config/loader.py#L13); [src/spandiff/config/model.py:176](../src/spandiff/config/model.py#L176). No eval/pickle/unsafe YAML object-construction path was identified.
- Parameterized lifecycle/resource queries, experiment-qualified relationships, enabled SQLite foreign keys and transactional migration: [src/spandiff/orchestration/lifecycle.py:48](../src/spandiff/orchestration/lifecycle.py#L48); [src/spandiff/evidence/database.py:204](../src/spandiff/evidence/database.py#L204). These are local scoping controls, not hosted tenant authentication.
- HTML text escaping and restricted local-fragment anchors, with no emitted scripts or external assets: [src/spandiff/reporting/html.py:27](../src/spandiff/reporting/html.py#L27). SQL normalization parses shapes rather than executing queries: [src/spandiff/normalization/sql.py:18](../src/spandiff/normalization/sql.py#L18).
- Span/resource attribute allowlists and explicit incomplete import state: [src/spandiff/security/sanitizer.py:10](../src/spandiff/security/sanitizer.py#L10); [src/spandiff/cli/__init__.py:66](../src/spandiff/cli/__init__.py#L66). These do not promise universal content redaction.
- Agent skill denies trace-derived authority, but its safety language is guidance, not deterministic confinement: [skills/spandiff/SKILL.md:8](../skills/spandiff/SKILL.md#L8). No model client, RAG/vector store, cross-session memory, API-spend loop, tool permission handler or MCP server is implemented.
- Authentication/session/CSRF and cloud-IAM/ingress defects have no implemented server/policy surface in tracked source. No file-upload endpoint, archive extraction, mobile/IPC endpoint or privileged CI workflow exists. SSRF review reaches a standalone policy plus injected requester, not a concrete fetch: [src/spandiff/security/destination.py:29](../src/spandiff/security/destination.py#L29); [src/spandiff/collection/runner.py:49](../src/spandiff/collection/runner.py#L49). Dependency ranges are visible, but current resolved versions/CVE status and hosted CI protections are not established: [pyproject.toml:1](../pyproject.toml#L1).

## Coverage, tests and workflow gaps

Coverage ledger: **21 units**; covered 17; candidate 4 (all independently resolved rejected); blocked 0; deferred 0; out-of-scope units 0; planned/in-progress 0. Excluded surfaces and evidence types are named above and in architecture/block maps, even though no runnable unit exists for an absent server or deployment.

Four independent reconnaissance contexts mapped product, principals, inputs/sinks and local execution. Seven first-wave hunters reviewed 18 units. The immediate critic found three gaps; three fresh second-wave hunters closed Compose teardown, normalization cost/error paths and actual Git runner buffering/cancellation. The post-wave-2 critic and a distinct final-clean critic both returned no additional accepted units or reassignments. This accepts **source assignment sufficiency only**, not exhaustive or runtime coverage.

Static test inventory: **34 modules / 92 test methods**. Tests were read, not run; no passing test count or coverage percentage is claimed. Key gaps are within-home links ([tests/test_storage.py:33](../tests/test_storage.py#L33)), collision/teardown cases ([tests/test_compose_adapter.py:30](../tests/test_compose_adapter.py#L30)), timeout replay ([tests/test_flush.py:16](../tests/test_flush.py#L16)), actual transport enforcement ([tests/test_destination.py:13](../tests/test_destination.py#L13)), and real model/tool behavior versus fixture-text assertions ([tests/test_evaluations.py:7](../tests/test_evaluations.py#L7)). Existing Git/Compose tests use fakes. Historical validation documentation is not current execution evidence; Linux/Compose verification remains explicitly unperformed in [docs/PLATFORM.md:5](../docs/PLATFORM.md#L5).

Required official CLIs were attempted at seeding, assignment/result ledger updates, candidate consolidation, critic updates, Phase 4, Phase 5 and before Phase 6. Both exit **1** with **OS no-follow and nonblocking input protection is unavailable** on Windows Node v26.13.0. 72 CLI attempts are recorded so far in [validation-log.json](./validation-log.json). The unmodified exported validateDocument functions report no schema/ledger errors on these parent-created JSON documents, but this is supplemental and does not count as a mandatory CLI pass. No safeguards were patched or disabled.

WSL --list --quiet reports WSL not installed. A Docker executable alone does not prove the required network, filesystem, environment, process, CPU/memory/file/disk/time envelope. Race-safe artifact promotion is not established either; no target-controlled execution artifacts were retained. The three initial candidate-verifier usage-limit failures were retried successfully and left no unresolved record.

The terminal run status is **incomplete**, reason **required_os_sandbox_and_validator_cli_file_guards_unavailable**. Safe next steps are specified in [NEEDS-VALIDATION.md](./NEEDS-VALIDATION.md). Reports and supplemental checks do not substitute for the missing controls.
