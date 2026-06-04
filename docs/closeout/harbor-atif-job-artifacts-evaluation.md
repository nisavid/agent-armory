# Harbor ATIF And Job Artifact Evaluation

Status: Source Disposition Ledger

## Scope Boundary

Issue [#189](https://github.com/nisavid/agent-armory/issues/189)
evaluates Harbor ATIF and job artifacts for current Armory Jig Runner result
needs. It asks whether Harbor `result.json`, `trajectory.json`, artifact
`manifest.json`, job/trial directory shape, and viewer affordances should
influence Armory structured result and evidence work.

This ledger does not adopt Harbor, select a Jig Driver, revise ADR 0022,
change Armory result statuses, implement a runner, create UI, write a PRD, or
write an ADR. Harbor outputs are retained as source material and compatibility
pressure for downstream work.

Plain text coverage terms for validation: result.json, trajectory.json,
artifact manifest.json, job result, trial result, ATIF-v1.7, pass, fail,
inconclusive, disagreement, oracle_error, adjudicator_error, infra_error,
fixture_error, sandbox_error, timeout, flaky, best-effort, raw logs,
host-local paths, model outputs, and viewer screenshots.

## Portable Source Inventory

Sources were checked on 2026-06-04 against Harbor default branch `main`, commit
`700972ab7aa6f27cd32747d9e3dd7ff5211fb7d3`, and latest release `v0.13.1`.
Firecrawl extraction output, GitHub CLI JSON, raw tool output, and source
snippets are instance-scoped scratch evidence. Durable project evidence is the
source URL set and curated conclusions below.

| source_id | source identity | evidence class | retained use |
| --- | --- | --- | --- |
| HAT001 | [Harbor Evals](https://www.harborframework.com/docs/run-jobs/run-evals) | documentation-supported | Job/trial directory shape, job `result.json`, trial `result.json`, `trajectory.json`, verifier output files, and viewer affordances. |
| HAT002 | [Artifact Collection](https://www.harborframework.com/docs/run-jobs/results-and-artifacts) | documentation-supported | Convention artifacts, config-driven artifacts, artifact `manifest.json`, environment support, and best-effort collection semantics. |
| HAT003 | [ATIF RFC](https://github.com/harbor-framework/harbor/blob/main/rfcs/0001-trajectory-format.md) | source-supported | ATIF-v1.7 root fields, step semantics, subagent trajectory handling, metrics, validation intent, and trajectory reference implementation paths. |
| HAT004 | [Harbor source](https://github.com/harbor-framework/harbor) | source-supported | Job result, trial result, artifact manifest, artifact handler, ATIF Pydantic models, trajectory validator, and viewer model/route behavior. |

Implementation source reviewed under HAT004:

- `src/harbor/models/job/result.py`
- `src/harbor/models/trial/result.py`
- `src/harbor/models/trial/artifact_manifest.py`
- `src/harbor/trial/artifact_handler.py`
- `src/harbor/models/trajectories/trajectory.py`
- `src/harbor/models/trajectories/step.py`
- `src/harbor/utils/trajectory_validator.py`
- `src/harbor/viewer/models.py`
- `src/harbor/viewer/server.py`
- `src/harbor/viewer/scanner.py`

## Harbor Output Fit Matrix

| Harbor output | Source-backed shape | Armory fit | Boundary |
| --- | --- | --- | --- |
| job `result.json` | `JobResult` records job identity, timestamps, total trial count, `JobStats`, and embedded `trial_results`. `JobStats` distinguishes completed, errored, running, pending, cancelled, and retries, plus reward, exception, token, and cost aggregates. Source: HAT004. | Useful batch-run source material for #164 result aggregation and suite summaries. | Not an Armory structured result contract. Harbor job stats do not encode every Armory status or assertion provenance directly. |
| trial `result.json` | `TrialResult` records task identity, trial name, task checksum, config, agent info, optional agent result, optional verifier result, optional exception info, timings, and optional per-step results. Source: HAT004. | Useful scenario-attempt source material for #164. It carries exception and timing fields that can inform `infra_error`, `fixture_error`, `sandbox_error`, and `timeout` design. | Trial result still needs Armory normalization before any `pass`, `fail`, `inconclusive`, `disagreement`, `oracle_error`, or `adjudicator_error` status can be trusted. |
| agent `trajectory.json` | Harbor docs show trial `agent/trajectory.json`; ATIF-v1.7 defines required `schema_version`, `agent`, and `steps`, optional run/document ids, metrics, observations, tool calls, multimodal content, continuation refs, and embedded subagent trajectories. Sources: HAT001, HAT003, HAT004. | Useful evidence input for trajectory assertions, review surfaces, and later Study Report observations. | ATIF records interaction history, not pass/fail truth. It does not replace Armory assertion results or disagreement/adjudication records. |
| artifact `manifest.json` | Artifact manifests list `source`, `destination`, `type` (`file` or `directory`), and `status` (`ok`, `failed`, or `empty`). ArtifactHandler writes the manifest after best-effort collection. Sources: HAT002, HAT004. | Useful artifact inventory pressure for #164 evidence policy and scratch/durable classification. | Best-effort collection means a missing or failed artifact cannot silently pass evidence sufficiency. It may indicate artifact collection failure, not task failure. |
| verifier outputs | Harbor docs list verifier `ctrf.json`, `reward.txt`, `test-stdout.txt`, and `test-stderr.txt`; viewer source also exposes `reward.json` and `reward-details.json` when Reward Kit is present. Sources: HAT001, HAT004. | Useful source material for Assertion Provider output handling and reviewer diagnostics. | Raw verifier logs and reward files need provenance, tamper-boundary, and status normalization before Armory can treat them as durable result truth. |
| viewer affordances | Harbor docs and source expose job browsing, trial inspection, trajectory view, verifier output, files, artifacts, comparison grids, token/cost summaries, and AI-generated summaries. Sources: HAT001, HAT004. | Useful UX evidence for #169 after result artifacts exist. | No styled UI implementation or report surface belongs to #189. Viewer screenshots remain scratch unless a downstream issue promotes sanitized assets. |

## Compatibility Gaps

Harbor result and artifact shapes should inform [#164](https://github.com/nisavid/agent-armory/issues/164)
as comparison and source material, but they must not replace Armory statuses.
Current Armory structured result statuses remain:

- `pass`
- `fail`
- `inconclusive`
- `disagreement`
- `oracle_error`
- `adjudicator_error`
- `infra_error`
- `fixture_error`
- `sandbox_error`
- `timeout`
- `flaky`

Gap analysis:

- `pass` and `fail`: Harbor reward or verifier output may imply success or
  failure for a task, but Armory needs typed assertion provenance and cannot
  collapse numeric reward into status without normalization.
- `inconclusive`: Harbor output can show missing verifier, missing artifact,
  empty manifest, partial evidence, or unreadable trajectory, but Armory must
  decide when those conditions block a conclusion.
- `disagreement`: ATIF can preserve evidence that multiple oracles inspect,
  but Harbor result files do not encode Armory oracle disagreement records.
- `oracle_error` and `adjudicator_error`: Harbor `exception_info`, verifier
  outputs, and viewer analysis failures are useful inputs, but Armory needs
  explicit oracle and adjudicator failure boundaries.
- `infra_error`, `fixture_error`, `sandbox_error`, and `timeout`: Harbor trial
  exceptions, timing fields, environment setup timings, verifier timings, and
  artifact collection status can inform these distinctions, but the mapping is
  not one-to-one.
- `flaky`: Harbor tracks attempts and retries at job/trial levels, but Armory
  `flaky` requires a declared repeat policy and mixed terminal outcomes for
  the same scenario, fixture hash, driver version, and target version.

Recommendation: #164 should borrow the separation between job result, trial
result, trajectory, verifier output, and artifact manifest, while keeping an
Armory-native structured result contract.

## Evidence Durability

Durable project evidence for #189:

- this ledger
- the Harbor External Tool Evaluation record update
- validator coverage for this ledger and the Harbor evaluation record
- PR body, review summaries, validation output summaries, and issue closeout

Portable review evidence may name source URLs, Harbor commit/release basis,
file paths inside the Harbor repository, and curated conclusions. Instance-
scoped scratch evidence includes raw logs, local paths, host-local paths,
raw trajectories, raw `trajectory.json`, raw job/trial `result.json`, raw
artifact `manifest.json`, raw verifier files, transcripts, model outputs,
viewer screenshots, Firecrawl output, GitHub CLI JSON, local command output,
and raw tool output.

Scratch evidence is summarized here by scope, disposition, and durable
conclusion. It is not committed as project truth.

## Viewer And Review Surface Notes

Impeccable result: no frontend implementation is appropriate for #189. The
repository does not yet have the `PRODUCT.md` and `DESIGN.md` foundation owned
by [#180](https://github.com/nisavid/agent-armory/issues/180), and
[#169](https://github.com/nisavid/agent-armory/issues/169) owns review report
surface evaluation after result artifacts exist.

Harbor viewer affordances that should inform #169 later:

- browse jobs with filters for agent, model, dataset, provider, and date
- inspect trial result, reward, duration, error, and verifier output
- view trajectories with tool calls, observations, multimodal content, tokens,
  cost, and timing metrics
- compare jobs in a side-by-side task grid
- browse files and artifacts, including artifact manifest data
- generate summaries for failures
- keep keyboard navigation for dense review workflows

These are evidence about review ergonomics, not an accepted Armory UI design.
Viewer screenshots remain scratch unless #169 deliberately creates sanitized
design assets or a durable UX record.

## Downstream Routing

| route | accepted input from this ledger | not owned here |
| --- | --- | --- |
| [#189](https://github.com/nisavid/agent-armory/issues/189) | Closeout for Harbor ATIF and job artifact fit. | Further Harbor execution or UI work. |
| [#164](https://github.com/nisavid/agent-armory/issues/164) | Borrow the job result, trial result, trajectory, verifier output, and artifact manifest separation as source pressure for the Jig Runner CLI and structured results. | Replacing Armory statuses with Harbor status, reward, exception, or manifest fields. |
| [#169](https://github.com/nisavid/agent-armory/issues/169) | Use Harbor viewer affordances as UX evidence after Armory result artifacts exist. | Implementing a report viewer or accepting Harbor's viewer as the Armory surface. |
| [#191](https://github.com/nisavid/agent-armory/issues/191) | Use this ledger as the ATIF/artifact child evidence when projecting final Harbor disposition. | Final Harbor adoption, rejection, issue projection, or parent closeout before #190 is complete. |

## Deferments And Nonportable Claims

- No new Harbor run, cloud sandbox run, Harbor registry operation, Opik
  integration, model call, or provider credential use is accepted by #189.
- No PRD, ADR, schema revision, public API change, Jig Driver selection, or
  Harbor adoption decision is introduced by this ledger.
- The #187 prototype remains the only accepted Harbor execution evidence in
  this evaluation. Its absence of trajectory output is a bounded prototype
  observation, not a general Harbor ATIF conclusion.
- Harbor source and docs are evidence, not Armory normative vocabulary.
- Raw `result.json`, `trajectory.json`, artifact `manifest.json`, logs,
  trajectories, model outputs, viewer screenshots, and host-local paths remain
  scratch unless a downstream issue promotes sanitized fixtures or durable
  examples.

## Security Privacy And Durability

This change set records a documentation ledger and structural Markdown
validator coverage. It introduces no Harbor execution, subprocess invocation,
cloud sandbox operation, registry write, credential handling, LLM provider
call, local filesystem mutation outside committed docs/tests/validator files,
or external disclosure beyond normal public source retrieval and issue/PR
projection.

Security and privacy boundaries:

- Harbor artifact collection is best-effort; failure to collect an artifact
  can hide evidence and must not be treated as task success.
- Harbor verifier output and reward files are evidence inputs, not trusted
  assertion truth without provenance and tamper-boundary review.
- ATIF can contain prompts, tool calls, observations, costs, tokens,
  reasoning-like content, multimodal references, and model metadata. Raw
  trajectories may contain sensitive or host-specific data.
- Viewer summaries may involve model outputs and should remain scratch unless
  a downstream issue defines provider, prompt, redaction, and durability
  controls.
- Do not commit or post credentials, raw logs, local paths, host-local paths,
  raw trajectories, transcripts, model outputs, viewer screenshots, provider
  account state, external service usage, raw Firecrawl output, or raw GitHub
  API output.

## Closeout Evidence

Triage result: issue #189 was open with `dependency:blocked`, while its only
live blocker #187 had closed completed on 2026-06-03. The first execution step
replaced only that dependency label with `dependency:unblocked`, preserving
the other labels.

Grill-with-docs result: no interactive grill was needed for #189. The source
evidence fits current Armory vocabulary, and this ledger does not introduce a
new term, PRD, ADR, schema, or hard-to-reverse architecture decision.

Prototype result: no new prototype was run for #189. The #187 prototype ledger
is the accepted prototype input; its lack of trajectory output remains a
bounded observation.

Impeccable result: viewer affordances were classified as UX evidence only.
No styled UI work is included because #180 owns the missing product/design
foundation and #169 owns report surface evaluation.

TDD result: Armory Integrity Validation guards this ledger's path, status,
required sections, required source URLs, required downstream routes, required
coverage terms, and host-local path rejection.

Security closeout: this ledger and validator change add no dynamic file
selection, writes beyond committed repository files, subprocess execution,
network calls, credential handling, or untrusted path input. Security review
focus is disclosure safety, artifact integrity, trajectory sensitivity, and
public projection boundaries.

Documentation closeout: this ledger and the Harbor External Tool Evaluation
record update are the committed documentation changes for issue #189. Existing
high-level docs already route Harbor evaluation work through the reusable
External Tool Evaluation contract and do not need issue-specific ledger lists.

Ralph review closeout: Cross-Boundary Coherence and Story Quality Ralph Review
Cycle results belong in the PR body and final issue projection after the final
diff, validation, and security checks are complete.
