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

Additional source inputs remain pending for neighbor tools, prototype behavior,
Reward Kit and judge semantics, trajectory/artifact contracts, driver gates,
and final projection.

## Evidence Ledger

| evidence class | current durable status |
| --- | --- |
| source-backed claims | Present for Harbor vocabulary and concept mapping through #184 and the Harbor Jig Source Map. |
| local observations | Limited to live repository and issue review during each child issue; not retained here as raw command output. |
| prototype results | Pending #187. No Harbor prototype result is accepted by this record yet. |
| implementation inference | Pending downstream work. Inferences must cite the source or prototype evidence that supports them. |
| unknowns | Neighbor-tool comparison, prototype fit, Reward Kit safety, ATIF/artifact contract fit, Jig Driver gate fit, and final projection remain unresolved. |
| rejected claims | No rejected Harbor claims have been promoted to this record yet. |

Child issues update this table with durable conclusions only. Raw logs,
scratch output, transient command output, and unreviewed source extracts remain
outside the record.

## Child Issue Outputs

| route | expected output | current state |
| --- | --- | --- |
| [#185](https://github.com/nisavid/agent-armory/issues/185) | Reusable external-tool evaluation pipeline and this Harbor record skeleton. | In progress. |
| [#186](https://github.com/nisavid/agent-armory/issues/186) | Neighbor-tool comparison against Harbor-relevant axes. | Pending. |
| [#187](https://github.com/nisavid/agent-armory/issues/187) | Harbor Agent Equipment A/B test prototype results. | Pending. |
| [#188](https://github.com/nisavid/agent-armory/issues/188) | Reward Kit and judge criteria fit for Assertion Provider and Learned Oracle questions. | Pending. |
| [#189](https://github.com/nisavid/agent-armory/issues/189) | ATIF trajectory and artifact contract evidence for Jig Runner results. | Pending. |
| [#190](https://github.com/nisavid/agent-armory/issues/190) | Harbor driver gate evidence against ADR 0022 and Jig Driver requirements. | Pending. |
| [#191](https://github.com/nisavid/agent-armory/issues/191) | Final disposition, projection state, and closeout coherence. | Pending. |

## Security Disclosure And Durability

Public-safe Harbor security boundaries include provider/auth surfaces, sandbox
network policy, verifier/reward tampering, artifact collection uncertainty,
judge provider cost boundaries, and external observability integration risk.

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

No new issue, PRD, or ADR projection is accepted by this record yet.

## Final Disposition

Current External Tool Evaluation Disposition:
unknown pending evidence.

Final disposition issue #191 will assign one of the fixed outcomes after the
child outputs are coherent: adopted candidate, supporting component, research
reference, deferred, rejected, or unknown pending evidence.
