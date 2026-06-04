# Harbor External Tool Evaluation

Status: External Tool Evaluation Record

Evaluation state: in progress

Final disposition: unknown pending evidence

## Scope

This record coordinates the Harbor evaluation for parent issue
[#183](https://github.com/nisavid/agent-armory/issues/183). It applies the
[External Tool Evaluation](../external-tool-evaluation.md) contract to Harbor
and accumulates durable child issue outputs until final disposition issue
[#191](https://github.com/nisavid/agent-armory/issues/191) closes the
evaluation.

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

Additional source input remains pending for final projection.

## Evidence Ledger

| evidence class | current durable status |
| --- | --- |
| source-backed claims | Present for Harbor vocabulary and concept mapping through #184 and the Harbor Jig Source Map; present for Harbor-linked neighbor tools and surfaces through #186 and the Harbor-Neighbor Tool Catalog; present for Reward Kit and judge criteria fit through #188 and the Harbor Reward Kit Evaluation; present for bounded prototype behavior through #187 and the Harbor Agent Equipment A/B Prototype Results; present for ATIF, job result, trial result, artifact manifest, verifier output, and viewer-affordance fit through #189 and the Harbor ATIF And Job Artifact Evaluation; present for driver-gate fit through #190 and the Harbor Driver Gate. |
| local observations | Limited to live repository and issue review during each child issue; not retained here as raw command output. |
| prototype results | Accepted for #187 only as bounded evidence that Harbor produced a discriminating local A/B job with reward and artifact evidence. The prototype does not establish general skill superiority, Harbor adoption, Jig Driver fit, structured result-contract fit, cloud sandbox behavior, registry behavior, provider behavior, or verifier hardening. |
| implementation inference | Reward Kit currently fits as concept source for deterministic Assertion Provider and Learned Oracle work, not a direct Armory result contract. Harbor ATIF and job artifacts fit as source material for #164 and #169, not as a direct Armory result contract. Harbor fits as a research reference and source of supporting driver-component ideas, not the first Jig Driver. Other inferences must cite the source or prototype evidence that supports them. |
| unknowns | Final projection remains unresolved. |
| rejected claims | Reward Kit output files are rejected as the direct current Armory structured result contract; Harbor as the first Jig Driver is not accepted on current evidence; final Harbor rejection or adoption remains unassigned. |

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
| [#191](https://github.com/nisavid/agent-armory/issues/191) | Final disposition, projection state, and closeout coherence. | Pending. |

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

The current projection is to update existing issues as child work closes. The
evaluation may create new issues when a finding is actionable, public-safe, and
not owned by #183 through #191. It may propose a PRD if Harbor evaluation
changes Armory requirements across multiple implementation stories. It may
propose an ADR if the evaluation resolves a hard-to-reverse tool, architecture,
driver, or evidence-contract tradeoff.

No new issue, PRD, or ADR projection is accepted by #190 or this record yet.

## Final Disposition

Current External Tool Evaluation Disposition:
unknown pending evidence.

Final disposition issue #191 will assign one of the fixed outcomes after the
child outputs are coherent. #187 no longer blocks on prototype evidence, #189
no longer blocks on ATIF/artifact evidence, and #190 no longer blocks on
driver-gate evidence. #191 remains open for final projection. If evidence
remains pending, #191 keeps the evaluation state in progress with unknown
pending evidence. If #191 marks the evaluation complete, it must use a finalized
disposition: adopted candidate, supporting component, research reference,
deferred, or rejected.
