# Harbor Agent Equipment A/B Prototype

Status: Prototype Evidence Record

## Scope Boundary

This record closes the issue
[#187](https://github.com/nisavid/agent-armory/issues/187) prototype slice for
parent issue [#183](https://github.com/nisavid/agent-armory/issues/183). It
asks whether Harbor can compare a baseline variant against an Agent Equipment
enabled variant and retain enough result evidence for later Armory evaluation.

This record does not adopt Harbor, select Harbor as a Jig Driver, revise
[ADR 0022](../adr/0022-defer-agent-test-jig-driver-selection.md), change the
Agent Test Jig design bundle, update PRDs, or claim stocked Published Agent
Equipment. The current stock inventory has no stocked equipment, so the
prototype uses the implemented candidate
[`Issue Ops Workflow Executor`](../../skills/issue-ops-workflow-executor/SKILL.md)
as the small Agent Equipment item under test.

## Prototype Question

Can Harbor run or hand off a bounded comparison where the baseline variant
receives only an Issue Ops advisory task and the equipment-enabled variant
receives the same task plus the Issue Ops Workflow Executor instructions?

Useful evidence for #187 is limited to Harbor's ability to represent the
comparison, emit reward output, retain trajectory and artifacts, and expose
repeatability limits. It is not evidence that the equipment item improves
agents, that Harbor should become a Jig Driver, or that ADR 0022 should change.

## Source Inputs

Source review reused the accepted
[Harbor Jig Source Map](harbor-jig-source-map.md) and
[External Tool Evaluation](../external-tool-evaluation.md) contract.

Primary Harbor inputs:

| source | retained use |
| --- | --- |
| [Harbor run evals](https://www.harborframework.com/docs/run-jobs/run-evals) | Command shape for `harbor run`, job grouping, trial output, verifier output, `reward.txt`, and viewer comparison. |
| [Harbor task structure](https://www.harborframework.com/docs/tasks) | Task layout, instruction file, verifier behavior, `network_mode = "no-network"`, and required reward file output. |
| [Harbor results and artifacts](https://www.harborframework.com/docs/run-jobs/results-and-artifacts) | Artifact capture through configured artifacts and artifact manifests, with best-effort collection limits. |
| [Harbor agents](https://www.harborframework.com/docs/agents) | Custom agent import path support for deterministic baseline and equipped agents. |
| [Reward Kit](https://www.harborframework.com/docs/rewardkit) | Reward JSON and reward-details JSON concepts for verifier output and scoring detail. |
| [ATIF RFC](https://raw.githubusercontent.com/harbor-framework/harbor/main/rfcs/0001-trajectory-format.md) | ATIF trajectory context for later #189 trajectory and result-contract review. |

Live issue review for #187 found labels `enhancement`, `ready-for-agent`,
`brief:present`, and `dependency:unblocked`. Native blockers #184 and #185
were closed, and #187 was still blocking #189, #190, and #191 when work began.

## Fixture Design

The planned throwaway prototype is a Harbor task stored under a temporary
scratch directory outside the repository. It is intentionally not committed.

Fixture layout:

| fixture part | planned content |
| --- | --- |
| Harbor task | `instruction.md` asks for a short Issue Ops advisory report for an already-triaged issue. `task.toml` uses a deterministic local environment and no network. |
| dataset | A single-task local dataset is enough because the goal is Harbor comparison mechanics, not benchmark confidence. |
| baseline variant | A custom agent reads only the Harbor task instruction and emits the advisory report artifact. |
| equipment-enabled variant | A custom agent reads the same task plus `skills/issue-ops-workflow-executor/SKILL.md`, then emits the advisory report artifact. |
| verifier result | A deterministic verifier reads the report artifact, checks required sections and evidence-boundary language, and writes reward output. |
| artifacts | Expected artifacts include each report, artifact manifest data, job result, trial result, verifier result, optional `reward.json`, `reward.txt`, stdout/stderr, and any emitted trajectory. |

The fixture should make the two variants deterministic so Harbor mechanics are
observable without provider credentials or model variance. A real model-backed
trial would be later evidence, not this #187 minimum.

## Execution Feasibility

Prototype execution was not safe in the active environment:

- `harbor` was not available on `PATH`.
- The Docker CLI resolved through Podman, but Podman could not initialize its
  user runtime directory because the current sandbox exposed it as read-only.
- No provider credentials, Harbor Hub state, model account, cloud sandbox, or
  external service usage was needed or inspected.

That puts #187 on the issue's accepted no-run handoff path. The blocked
control is local Harbor plus a working container runtime, not prototype design.

## Result Or Handoff

No Harbor job result is accepted by this record. The durable result is a
precise no-run handoff.

Recommended command shape after Harbor and a safe container runtime are
available:

```bash
export SCRATCH_ROOT="<temporary scratch directory outside the repository>"
export PYTHONPATH="$SCRATCH_ROOT:$PYTHONPATH"
cd "$SCRATCH_ROOT"

harbor run \
  -p "datasets/issue-ops-advisory-ab" \
  --agent-import-path "harbor_ab_agents:BaselineIssueOpsAgent"

harbor run \
  -p "datasets/issue-ops-advisory-ab" \
  --agent-import-path "harbor_ab_agents:EquippedIssueOpsAgent"

harbor view jobs
```

If the installed Harbor version requires a model argument even for a
deterministic custom agent, set the model to the local no-provider setting
recommended by that Harbor release and record the exact flag in the return
summary. Do not introduce provider credentials for the first rerun.

Expected job and trial artifacts:

- Job-level `config.json` and `result.json` for each variant.
- Trial-level `config.json`, `result.json`, verifier output, reward output,
  and stdout/stderr for each variant.
- Agent-side report artifact for each variant.
- ATIF trajectory if the custom agent path emits or Harbor captures one.
- Artifact manifest data showing collected, missing, or failed artifacts.
- Viewer comparison evidence showing whether Harbor can compare the two jobs.

Return contract for a later operator or agent run:

1. Report Harbor version, container runtime version, and whether network was
   disabled for the Harbor task.
2. Summarize reward output for baseline variant and equipment-enabled variant.
3. List the durable artifact names, missing artifacts, and collection status.
4. State whether a trajectory was produced and whether it is ATIF-shaped.
5. State repeatability limits, including deterministic fixture limits,
   container/runtime variance, and any model/provider boundary if used.
6. Confirm local scratch disposition and do not commit raw logs, trajectories,
   transcripts, model outputs, provider/account state, or local paths.

## Evidence Ledger

| evidence class | #187 status |
| --- | --- |
| source-backed claims | Harbor docs support the task, dataset, custom agent, verifier, job, trial, reward output, artifacts, and trajectory surfaces listed here. |
| local observations | Harbor CLI was unavailable and the Docker-compatible runtime was blocked by sandboxed Podman state. These observations can drift and are retained only as a public-safe closeout summary. |
| prototype results | No executed Harbor prototype result is accepted. The accepted #187 prototype result is the no-run handoff and fixture design above. |
| implementation inference | A deterministic custom agent pair is sufficient to test Harbor comparison mechanics, but not sufficient to measure agent quality. |
| unknowns | Harbor version-specific custom agent flags, exact artifact manifest shape, viewer comparison behavior, and ATIF trajectory capture remain unresolved until the no-run handoff is executed. |
| rejected claims | This record rejects claims that Harbor is selected as a Jig Driver, that ADR 0022 changed, or that the Issue Ops Workflow Executor is stocked Published Agent Equipment. |

## Security Privacy And Durability

The change set adds a documentation record, an evaluation-record projection,
validator coverage, and unit tests. It does not add Harbor execution code,
subprocess execution paths, dynamic network access, credential reads, provider
calls, Docker invocation, registry writes, cloud sandbox execution, or external
service usage.

Security and privacy boundaries:

- Credentials are out of scope for the first rerun.
- Docker/provider boundaries stay explicit because container execution is the
  blocked control.
- Raw logs, raw trajectories, transcripts, model outputs, provider account
  state, and local paths are instance-scoped scratch evidence.
- Durable project evidence is limited to this record, the Harbor evaluation
  record update, the validator/test diff, PR body, issue closeout, and portable
  review summaries.
- A later run may summarize trajectory and artifacts, but raw artifacts should
  stay out of the repository unless a downstream issue promotes a sanitized
  fixture.

Codex Security closeout for this change set used a scoped diff review rather
than a full scan artifact bundle because the only executable change is a
structural Markdown validator over one fixed repository-relative path. The
validator uses existing file-status, heading, link-search, downstream route,
and host-local-path helpers. It adds no new untrusted path input, subprocess,
network, secret, or write behavior.

## Downstream Routing

| route | #187 output |
| --- | --- |
| [#183](https://github.com/nisavid/agent-armory/issues/183) | Parent Harbor evaluation may cite this as bounded no-run prototype evidence, not a Harbor adoption decision. |
| [#187](https://github.com/nisavid/agent-armory/issues/187) | This record is the durable closeout evidence and return contract for the issue. |
| [#189](https://github.com/nisavid/agent-armory/issues/189) | Later ATIF and artifact review can use the expected trajectory and artifacts list as handoff input, but must wait for real job evidence before accepting Harbor result contracts. |
| [#190](https://github.com/nisavid/agent-armory/issues/190) | Driver gate work can use the blocked container/runtime control and no-run result as environment evidence, without treating Harbor as a Jig Driver. |
| [#191](https://github.com/nisavid/agent-armory/issues/191) | Final Harbor projection should keep final disposition as unknown pending evidence until downstream evidence is stronger. |

No update is made to #183, #190, #191, PRDs, ADRs, or stock inventory by this
record.

## Closeout Evidence

Triage result: no further triage was needed for #187. Labels were
`enhancement`, `ready-for-agent`, `brief:present`, and `dependency:unblocked`;
native blockers #184 and #185 were closed; #187 blocked #189, #190, and #191.

Grill-with-docs result: the only unresolved decision was whether #187 may close
with a precise no-run handoff if Harbor or Docker cannot run safely. The issue
acceptance criteria already allow that path, so the answer is yes.

Prototype result: Harbor execution was unavailable. The no-run handoff above
records the planned Harbor task, dataset, baseline variant,
equipment-enabled variant, custom agent approach, verifier result, reward
output, trajectory and artifacts expectations, blocked control, expected job
result and trial result artifacts, repeatability limits, environment controls,
credentials boundary, Docker/provider boundaries, and local scratch disposition.

Impeccable result: non-applicable. #187 has no UI, frontend, report viewer, or
product surface change.

TDD result: Armory Integrity Validation now guards this record's path, status,
required sections, required evidence terms, downstream routes, and host-local
path rejection.

Security closeout: scoped Codex Security review is recorded in
`Security Privacy And Durability` because the executable diff only adds
fixed-path Markdown validation and tests.

Documentation closeout: affected docs are this closeout record and the Harbor
External Tool Evaluation Record. README, AGENTS, PRDs, ADRs, and inventory do
not need changes because #187 creates no public feature, policy change,
architecture decision, or stocked equipment claim.

Ralph review closeout: Cross-Boundary Coherence Ralph Review Cycle 1 found and
fixed projection wording for #185 and the remaining Harbor unknowns. Cross-Boundary
Coherence Ralph Review Cycle 2 found no findings. Story Quality Ralph Review
Cycle 1 found no findings after checking DX, validator locality, evidence
durability, security boundaries, command handoff shape, and alignment with
`docs/vision.md`.
