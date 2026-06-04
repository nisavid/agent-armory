# Harbor Driver Gate

Status: Source Disposition Ledger

## Scope Boundary

Issue [#190](https://github.com/nisavid/agent-armory/issues/190)
evaluates Harbor against ADR 0022 and the accepted Agent Test Jig driver
rubric. The question is whether Harbor should become the first Jig Driver for
Armory or remain source material for later driver design.

This ledger does not adopt Harbor, select a Jig Driver, revise ADR 0022,
mutate downstream Agent Test Jig issues, run a new prototype, execute a cloud
sandbox, use provider credentials, implement a runner, or add UI. Harbor
evidence is retained as source material for driver selection and final Harbor
projection.

Plain text coverage terms for validation: ADR 0022, Jig Driver, Docker, cloud
sandbox, Daytona, Modal, E2B, Runloop, Tensorlake, Islo, CoreWeave Sandboxes,
W&B Sandboxes, network policy, no-network, allowlist, sidecar, artifact
manifest.json, best-effort, cleanup, reproducibility, portability, Codex
workflow compatibility, maintenance cost, Docker credentials,
verifier/reward tampering, artifact integrity, credential handling,
unsupported isolation claims, and provider account state.

## Portable Source Inventory

Sources were checked on 2026-06-04 against Harbor documentation and live
public Harbor issue state. Firecrawl extraction output, GitHub CLI JSON, raw
tool output, local command output, and source snippets are instance-scoped
scratch evidence. Durable project evidence is the source URL set and curated
conclusions below.

| source_id | source identity | evidence class | retained use |
| --- | --- | --- | --- |
| HDG001 | [Cloud Sandboxes](https://www.harborframework.com/docs/run-jobs/cloud-sandboxes) | documentation-supported | Harbor exposes local Docker execution and cloud sandbox providers: Daytona, Modal, E2B, Runloop, Tensorlake, Islo, CoreWeave Sandboxes, and W&B Sandboxes. Daytona and Islo are documented as multi-container-capable; Daytona carries provider-specific internet restrictions and account requirements. |
| HDG002 | [Tasks](https://www.harborframework.com/docs/tasks) | documentation-supported | Harbor task environments declare Linux runtime, Dockerfile or docker-compose surfaces, resource controls, `public`, `no-network`, and `allowlist` network policy values, verifier scripts, sidecar/service shapes, timeout controls, and reward output files. |
| HDG003 | [Artifact Collection](https://www.harborframework.com/docs/run-jobs/results-and-artifacts) | documentation-supported | Harbor artifacts can be collected by convention or config and recorded through artifact `manifest.json` entries. Collection is best-effort; Docker volume mounts and cloud-provider download behavior differ. |
| HDG004 | [Harbor issue 1687](https://github.com/harbor-framework/harbor/issues/1687) | live-issue-supported | Docker credentials for sandbox environments remain an active public concern, including private image and rate-limit implications. |
| HDG005 | [Harbor issue 1694](https://github.com/harbor-framework/harbor/issues/1694) | live-issue-supported | Stateful sidecar behavior and verifier-mode sidecar reachability remain active public concerns. |
| HDG006 | [Harbor issue 1779](https://github.com/harbor-framework/harbor/issues/1779) | live-issue-supported | Verifier/reward tampering remains an active public concern when agent code can affect verifier reward files. |
| HDG007 | [Harbor issue 1795](https://github.com/harbor-framework/harbor/issues/1795) | live-issue-supported | Modal compose/network behavior remains an active public concern, including provider-specific network assumptions. |

Accepted Armory inputs:

- [ADR 0022](../adr/0022-defer-agent-test-jig-driver-selection.md) defers
  first Jig Driver selection until an implementation gate applies the driver
  rubric with executable constraints in view.
- [Agent Test Jigs](../../specs/agent-test-jigs/) defines the Jig Driver role,
  driver lifecycle expectations, result needs, and accepted driver rubric.
- [Harbor Jig Source Map](harbor-jig-source-map.md) maps Harbor environment,
  cloud sandbox, network policy, verifier/reward tampering, and provider
  boundaries into Armory vocabulary.
- [Harbor-Neighbor Tool Catalog](harbor-neighbor-tool-catalog.md) classifies
  Harbor-linked sandbox providers as driver-gate input, not accepted drivers.
- [Harbor Agent Equipment A/B Prototype Results](harbor-agent-equipment-ab-prototype-results.md)
  is the only accepted Harbor execution evidence for this evaluation.
- [Harbor ATIF And Job Artifact Evaluation](harbor-atif-job-artifacts-evaluation.md)
  records artifact and result-shape evidence without selecting a driver.

## Driver Gate Matrix

| gate | Harbor evidence | gate result |
| --- | --- | --- |
| Safety | Harbor exposes container and cloud sandbox execution controls, but public issues still cover Docker credentials, sidecar reachability, Modal network behavior, and verifier/reward tampering. | Partial. Useful source material, not enough to trust as the first safety boundary. |
| Isolation from host state | Local Docker execution and cloud sandbox providers can isolate some state, but provider behavior differs and unsupported isolation claims are not encoded as an Armory capability contract. | Weak for first-driver adoption. Every claimed isolation boundary would need provider-specific proof. |
| Reproducibility | Harbor task definitions, timeouts, resources, and artifacts help describe runs, but provider account state, image pulls, rate limits, internet restrictions, and cloud runtime drift affect repeatability. | Partial. Good vocabulary; insufficient reproducibility guarantee. |
| Simplicity and local iteration speed | The #187 prototype shows local Harbor can run a bounded A/B task, but it depended on host container compatibility and did not prove general runner ergonomics. | Useful only as bounded prototype evidence. |
| Observability | Job results, trial results, trajectories when emitted, verifier outputs, viewer affordances, and artifact manifest.json files create useful evidence surfaces. | Strong as design input for #164 and #169; not a driver selection by itself. |
| Effect controls | Harbor supports network policy values including public, no-network, and allowlist, and cloud providers add their own controls. | Promising, but Armory still needs explicit driver capability output and fail-closed unsupported-control handling. |
| Fixture and mock support | Dockerfile, docker-compose, sidecar, setup, and verifier scripts can support fixtures and services. | Promising supporting driver-component idea; not proven as an Armory lifecycle contract. |
| Cleanup reliability | Harbor job execution and artifact collection expose cleanup pressure, but the reviewed sources do not establish residue detection or cleanup guarantees for every provider. | Unproven. The first driver needs teardown evidence for driver-owned state. |
| Portability | Harbor spans Docker and multiple cloud sandbox providers, but provider feature parity is uneven. Daytona, Modal, E2B, Runloop, Tensorlake, Islo, CoreWeave Sandboxes, and W&B Sandboxes require separate capability claims. | Partial. Breadth increases evaluation value and maintenance cost at the same time. |
| Codex workflow compatibility | Harbor can be invoked from a Codex-mediated repo session and produced bounded #187 evidence. Codex approval, sandbox, worktree, and local-container behavior remain separate controls. | Compatible as a research workflow; not accepted as the first hidden driver boundary. |
| Maintenance cost | Adopting Harbor as the first driver would bring Harbor schema, CLI, Docker, cloud provider, artifact, viewer, credential, sidecar, and network-policy churn into the first implementation slice. | High for a first driver. Prefer a smaller Armory-native gate first. |

## Recommendation

The primary recommendation is to defer Harbor as the first Jig Driver.

Treat Harbor as a research reference and source of supporting
driver-component ideas, not as the selected first driver. Harbor should inform
driver vocabulary, artifact and result evidence, sandbox-provider comparison,
network policy handling, sidecar fixture needs, and verifier tamper-boundary
design. It should not own the first Armory driver contract until #163 or a
successor issue can prove the selected driver with Armory-native capability
output, cleanup evidence, unsupported-control handling, and fixture/result
semantics.

This recommendation does not reject Harbor as a future component. It rejects
only selecting Harbor now as the first driver on the evidence available to #190.

## Security Review

Security-relevant conclusions:

- Verifier/reward tampering is a first-order driver risk. Reward files and
  verifier outputs are evidence inputs, not trusted assertion truth without a
  declared tamper boundary.
- Docker credentials and provider credentials are outside this ledger's
  execution scope. Any future Harbor-backed driver must prevent credential
  disclosure through tasks, images, artifacts, trajectories, logs, and viewer
  surfaces.
- Network effects require explicit capability reporting. `public`,
  `no-network`, and `allowlist` policy values are useful inputs, but provider
  behavior must be proven before Armory accepts network-isolation claims.
- Sidecar and compose behavior must be tested per provider before fixtures,
  mock services, or verifier sidecars become driver guarantees.
- Artifact integrity is not implied by best-effort artifact collection. A
  missing, empty, or failed artifact manifest entry must affect evidence
  sufficiency instead of being treated as success.
- Cloud provider trust and provider account state cannot become hidden test
  prerequisites for core Jig Runner claims.
- Local path disclosure remains a durability risk. Durable project evidence
  must summarize raw paths, logs, trajectories, artifacts, and provider state
  instead of preserving them.

## Downstream Routing

| route | accepted input from this ledger | not owned here |
| --- | --- | --- |
| [#183](https://github.com/nisavid/agent-armory/issues/183) | Adds the Harbor driver-gate child output to the parent external-tool evaluation. | Final Harbor disposition before #191. |
| [#190](https://github.com/nisavid/agent-armory/issues/190) | Completes the driver-gate ledger with a defer-Harbor recommendation. | Further Harbor execution, ADR revision, or Agent Test Jig issue mutation. |
| [#163](https://github.com/nisavid/agent-armory/issues/163) | Use Harbor as comparison evidence when selecting the first Jig Driver. Apply the ADR 0022 rubric before writing driver code. | Selecting Harbor, a hybrid local driver, process sandbox, container-first driver, or provider-backed driver in this ledger. |
| [#191](https://github.com/nisavid/agent-armory/issues/191) | Use this ledger as the driver-gate child evidence for final Harbor disposition. | Final projection, issue closure coherence, or parent evaluation completion before all child evidence is reconciled. |

## Deferments And Nonportable Claims

- No new Harbor run, cloud sandbox run, Harbor registry operation, Opik
  integration, model call, or provider credential use is accepted by #190.
- No PRD, ADR, schema revision, public API change, first Jig Driver selection,
  Harbor adoption decision, or Agent Test Jig issue mutation is introduced by
  this ledger.
- #187 remains the only accepted Harbor execution evidence for this evaluation.
  It supports bounded prototype behavior only and does not establish general
  driver suitability.
- Harbor docs and public issues are evidence, not Armory normative behavior.
- Harbor's Docker, cloud sandbox, network policy, sidecar, artifact, cleanup,
  credential, reproducibility, portability, Codex compatibility, and
  maintenance surfaces require Armory-native proof before they can become
  driver guarantees.

## Security Privacy And Durability

This change set records a documentation ledger and structural Markdown
validator coverage. It introduces no Harbor execution, subprocess invocation,
cloud sandbox operation, registry write, credential handling, LLM provider
call, local filesystem mutation outside committed docs/tests/validator files,
or external disclosure beyond normal public source retrieval and issue/PR
projection.

Do not commit or post credentials, raw logs, local paths, host-local paths,
raw trajectories, transcripts, model outputs, viewer screenshots, provider
account state, external service usage, raw Firecrawl output, raw GitHub API
output, or raw tool output. Portable review summaries may name public source
URLs, public issue numbers, committed Armory paths, and curated conclusions.
Instance-scoped scratch evidence stays outside this record.

## Closeout Evidence

Triage result: issue #190 was open with `dependency:blocked`, while live
blockers #184, #185, and #187 were closed. The first execution step replaced
only the dependency label with `dependency:unblocked`, preserving the other
labels.

Grill-with-docs result: no interactive grill was needed for #190. The evidence
does not change Armory glossary terms, ADR 0022, or downstream Agent Test Jig
issue projection. It applies the accepted driver gate and records a bounded
recommendation.

Prototype result: no new prototype was run for #190. The #187 bounded
prototype ledger is the accepted prototype input.

Impeccable result: non-applicable. This change includes no UI surface or
visual design work.

TDD result: Armory Integrity Validation guards this ledger's path, status,
required sections, required source URLs, required downstream routes, required
coverage terms, primary recommendation, and host-local path rejection.

Security closeout: this ledger and validator change add no dynamic file
selection, writes beyond committed repository files, subprocess execution,
network calls, credential handling, or untrusted path input. Codex Security
diff review focuses on disclosure safety, artifact integrity, credential
handling, provider state, and public projection boundaries.

Documentation closeout: this ledger and the Harbor External Tool Evaluation
record update are the committed documentation changes for issue #190. Existing
Agent Test Jig and ADR docs already carry the general driver-selection gate,
so no ADR 0022 or issue-projection edit is accepted by this change.

Ralph review closeout: Cross-Boundary Coherence and Story Quality Ralph Review
Cycle results belong in the PR body and final issue projection after the
final diff, validation, and security checks are complete.
