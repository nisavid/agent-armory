# Harbor External Tool Evaluation

Status: External Tool Evaluation Record

Evaluation state: complete

Final disposition: research reference

## Scope

This record coordinates the Harbor evaluation for parent issue
[#183](https://github.com/nisavid/agent-armory/issues/183). It applies the
[External Tool Evaluation](../external-tool-evaluation.md) contract to Harbor
and records the completed durable child issue outputs through final
disposition issue [#191](https://github.com/nisavid/agent-armory/issues/191).

This record is not a Harbor adoption decision, Harbor prototype result,
Agent Test Jig driver selection, Reward Kit acceptance, ATIF result contract,
or ADR 0022 revision. Those outputs belong to their named child issues and
closeout gates.

## Source Inputs

The accepted source-map input is
[#184](https://github.com/nisavid/agent-armory/issues/184) and its durable
[Harbor Jig Source Map](../closeout/harbor-jig-source-map.md). That ledger maps
Harbor's task, dataset, agent, environment, verifier, trial, job, Reward Kit,
judge criteria, ATIF trajectory, artifacts, scoring, cloud sandbox, network
policy, artifact handling, verifier/reward tampering, and auth/provider
boundaries into current Armory jig vocabulary.

The accepted neighbor-tool catalog input is
[#186](https://github.com/nisavid/agent-armory/issues/186) and its durable
[Harbor-Neighbor Tool Catalog](../closeout/harbor-neighbor-tool-catalog.md).
That ledger maps Harbor-linked sandbox providers, Reward Kit, LiteLLM provider
routing, ATIF, Opik fallback context, Harbor registry, dataset.toml, adapter
templates, result viewer, Hugging Face parity experiments, SkyRL, and GEPA into
Armory routing classifications.

The accepted evaluation-pipeline input is
[#185](https://github.com/nisavid/agent-armory/issues/185) and the reusable
[External Tool Evaluation](../external-tool-evaluation.md) contract.

The accepted Reward Kit input is
[#188](https://github.com/nisavid/agent-armory/issues/188) and its durable
[Harbor Reward Kit Evaluation](../closeout/harbor-reward-kit-evaluation.md).
That ledger evaluates deterministic criteria, judge TOML, LLM judges, agent
judges, trajectory evaluation, isolation, scoring, output files, provider
routing, comparison behavior, open Harbor PRs/issues, and security risks for
Assertion Provider and Learned Oracle fit.

The accepted prototype input is
[#187](https://github.com/nisavid/agent-armory/issues/187) and its durable
[Harbor Agent Equipment A/B Prototype Results](../closeout/harbor-agent-equipment-ab-prototype-results.md).
That ledger records a bounded local Harbor A/B prototype using a deterministic
Issue Ops advisory workflow task, custom agent import paths, container runtime
`no-network`, verifier reward evidence, and collected report artifacts. It
supports only the claim that Harbor produced a discriminating prototype job:
baseline reward `0.5714`, equipped reward `1.0`, both with collected artifacts
and no Harbor trial exceptions.

The accepted ATIF and artifact input is
[#189](https://github.com/nisavid/agent-armory/issues/189) and its durable
[Harbor ATIF And Job Artifact Evaluation](../closeout/harbor-atif-job-artifacts-evaluation.md).
That ledger evaluates Harbor job `result.json`, trial `result.json`,
`trajectory.json`, artifact `manifest.json`, verifier outputs, viewer
affordances, ATIF-v1.7, best-effort artifact collection, and evidence
durability for Jig Runner result needs. It recommends using Harbor artifacts
as source material for [#164](https://github.com/nisavid/agent-armory/issues/164)
and Harbor viewer affordances as later UX evidence for
[#169](https://github.com/nisavid/agent-armory/issues/169), without replacing
Armory result statuses or implementing UI in #189.

The accepted driver-gate input is
[#190](https://github.com/nisavid/agent-armory/issues/190) and its durable
[Harbor Driver Gate](../closeout/harbor-driver-gate.md). That ledger applies
ADR 0022 and the Agent Test Jig driver rubric to Harbor's Docker, cloud
sandbox, network policy, sidecar, artifact, cleanup, credential,
reproducibility, portability, Codex compatibility, and maintenance surfaces.
It recommends deferring Harbor as the first Jig Driver and retaining Harbor as
a research reference plus supporting driver-component source material.

The accepted final-disposition input is
[#191](https://github.com/nisavid/agent-armory/issues/191) and its durable
[Harbor Final Disposition](../closeout/harbor-final-disposition.md). That
ledger, docs/closeout/harbor-final-disposition.md, completes the evaluation
with final disposition `research reference`,
retains Harbor as supporting source material, and records exact projection
routes for [#163](https://github.com/nisavid/agent-armory/issues/163),
[#164](https://github.com/nisavid/agent-armory/issues/164),
[#165](https://github.com/nisavid/agent-armory/issues/165),
[#166](https://github.com/nisavid/agent-armory/issues/166),
[#167](https://github.com/nisavid/agent-armory/issues/167),
[#169](https://github.com/nisavid/agent-armory/issues/169),
[#177](https://github.com/nisavid/agent-armory/issues/177),
[#183](https://github.com/nisavid/agent-armory/issues/183), and
[#191](https://github.com/nisavid/agent-armory/issues/191).

## Evidence Ledger

| evidence class | current durable status |
| --- | --- |
| source-backed claims | Present for Harbor vocabulary and concept mapping through #184 and the Harbor Jig Source Map; present for Harbor-linked neighbor tools and surfaces through #186 and the Harbor-Neighbor Tool Catalog; present for Reward Kit and judge criteria fit through #188 and the Harbor Reward Kit Evaluation; present for bounded prototype behavior through #187 and the Harbor Agent Equipment A/B Prototype Results; present for ATIF, job result, trial result, artifact manifest, verifier output, and viewer-affordance fit through #189 and the Harbor ATIF And Job Artifact Evaluation; present for driver-gate fit through #190 and the Harbor Driver Gate. |
| local observations | Limited to live repository and issue review during each child issue; not retained here as raw command output. |
| prototype results | Accepted for #187 only as bounded evidence that Harbor produced a discriminating local A/B job with reward and artifact evidence. The prototype does not establish general skill superiority, Harbor adoption, Jig Driver fit, structured result-contract fit, cloud sandbox behavior, registry behavior, provider behavior, or verifier hardening. |
| implementation inference | Reward Kit currently fits as concept source for deterministic Assertion Provider and Learned Oracle work, not a direct Armory result contract. Harbor ATIF and job artifacts fit as source material for #164 and #169, not as a direct Armory result contract. Harbor fits as a research reference and supporting source material, not the selected first Jig Driver. Other inferences must cite the source or prototype evidence that supports them. |
| unknowns | No final-disposition unknown remains. Future implementation issues still own their own driver, result, assertion, oracle, Harness Test Suite, review-surface, and lifecycle evidence decisions. |
| rejected claims | Reward Kit output files are rejected as the direct current Armory structured result contract; Harbor as the first Jig Driver is not accepted on current evidence; Harbor is not accepted as an adopted candidate, supporting component, Assertion Provider, Learned Oracle, Harness Test Suite evidence source, direct Armory result contract, or selected first Jig Driver. |

Child issues update this table with durable conclusions only. Raw logs,
scratch output, transient command output, and unreviewed source extracts remain
outside the record.

## Child Issue Outputs

| route | expected output | current state |
| --- | --- | --- |
| [#185](https://github.com/nisavid/agent-armory/issues/185) | Reusable external-tool evaluation pipeline and this Harbor record skeleton. | Complete; reusable contract accepted. |
| [#186](https://github.com/nisavid/agent-armory/issues/186) | Neighbor-tool comparison against Harbor-relevant axes. | Complete through the Harbor-Neighbor Tool Catalog. |
| [#187](https://github.com/nisavid/agent-armory/issues/187) | Harbor Agent Equipment A/B test prototype results. | Complete through the Harbor Agent Equipment A/B Prototype Results; bounded prototype evidence accepted. |
| [#188](https://github.com/nisavid/agent-armory/issues/188) | Reward Kit and judge criteria fit for Assertion Provider and Learned Oracle questions. | Complete; borrow concepts and defer wrapping for both roles. |
| [#189](https://github.com/nisavid/agent-armory/issues/189) | ATIF trajectory and artifact contract evidence for Jig Runner results. | Complete; use Harbor outputs as source material for #164 and viewer affordances as later UX evidence for #169, without replacing Armory result statuses. |
| [#190](https://github.com/nisavid/agent-armory/issues/190) | Harbor driver gate evidence against ADR 0022 and Jig Driver requirements. | Complete; defer Harbor as the first Jig Driver and retain it as a research reference plus supporting driver-component source material. |
| [#191](https://github.com/nisavid/agent-armory/issues/191) | Final disposition, projection state, and closeout coherence. | Complete through the Harbor Final Disposition; final disposition is research reference. |

## Security Disclosure And Durability

Public-safe Harbor security boundaries include provider/auth surfaces, sandbox
network policy, verifier/reward tampering, artifact collection uncertainty,
judge provider cost boundaries, Reward Kit agent judge execution, verifier
output tampering, Docker credentials, artifact integrity, provider account
state, unsupported isolation claims, external observability integration risk,
local Docker/Podman compatibility, and the no-network container runtime
boundary observed by #187.

Do not commit or post credentials, private local paths, raw logs, raw
trajectories, transcripts, model outputs, provider account state, exploit
instructions, or sensitive external service usage details. If a child issue
discovers a sensitive concern, the record keeps a redacted public note and the
details route through a private operator handoff.

Durable evidence for this record is committed docs, issue bodies, PR bodies,
review summaries, and public-safe closeout notes. Portable review summaries may
name source URLs and curated conclusions. Instance-scoped scratch evidence
stays outside this record.

## Projection State

The final projection is to update existing issues and close the Harbor
evaluation parent after the #191 change set merges and live subissue state
still shows the child graph complete. The accepted final projection routes are
[#163](https://github.com/nisavid/agent-armory/issues/163),
[#164](https://github.com/nisavid/agent-armory/issues/164),
[#165](https://github.com/nisavid/agent-armory/issues/165),
[#166](https://github.com/nisavid/agent-armory/issues/166),
[#167](https://github.com/nisavid/agent-armory/issues/167),
[#169](https://github.com/nisavid/agent-armory/issues/169),
[#177](https://github.com/nisavid/agent-armory/issues/177),
[#183](https://github.com/nisavid/agent-armory/issues/183), and
[#191](https://github.com/nisavid/agent-armory/issues/191).

Harbor is a research reference and supporting source material. It is not the
selected first Jig Driver. Issue #163 should use Harbor as comparison evidence
when selecting the first Jig Driver. Issue #164 should borrow Harbor's
job-result, trial-result, trajectory, verifier-output, and artifact-manifest
separation without replacing Armory statuses. Issues #165 and #166 should
borrow Reward Kit concepts and defer wrapping. Issue #169 may use Harbor viewer
affordances as later UX evidence. Issues #167 and #177 receive no direct update
until structured Jig Runner or Harness Test Suite evidence exists.

No new issue, PRD, or ADR projection is accepted by this record because the
final disposition preserves ADR 0022 and avoids a hard-to-reverse architecture
change.

This record does not create new issues, propose a PRD, or propose an ADR.

## Final Disposition

Current External Tool Evaluation Disposition:
research reference.

Harbor remains supporting source material for driver comparison, result and
artifact design, Reward Kit-inspired assertion and oracle design pressure, and
later review-surface analysis. It is not an adopted candidate, supporting
component, selected first Jig Driver, direct Armory result contract, Assertion
Provider, Learned Oracle, or Harness Test Suite evidence source.

The evaluation is complete after #191 merges and projects the final closeout.
Any future Harbor-backed implementation must reopen the relevant downstream
issue's own evidence, security, validation, and review gates.
