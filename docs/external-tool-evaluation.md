# External Tool Evaluation

Status: Armory Operating Contract

## Purpose

External-tool evaluation is the Armory process for judging outside tools,
frameworks, harnesses, services, datasets, and adjacent projects before their
claims influence Agent Equipment architecture, issue projection, documentation,
security posture, or adoption decisions.

The process creates an **External Tool Evaluation Record** when the evaluation
can affect Armory architecture, issue projection, docs, security posture, or
final disposition. A small one-off source check may mark the record not
applicable in the relevant issue or PR, with a rationale.

An External Tool Evaluation Record declares its evaluation state as in progress
or complete, and its final disposition as one of the fixed External Tool
Evaluation Disposition values.

`unknown pending evidence` is the disposition for an in-progress evaluation.
A complete evaluation must use a finalized disposition: adopted candidate,
supporting component, research reference, deferred, or rejected.

The process is reusable across external tools. Harbor is the first application,
not a special-case rule source.

## Pipeline Stages

Use these stages for each external-tool evaluation. A stage may be marked not
applicable when the record states why the stage does not affect the evaluation.

| stage | required output |
| --- | --- |
| intake scope | Name the tool, intended Armory question, affected issues, expected outputs, and non-goals. |
| source review | Collect first-party docs, source, schemas, examples, and release notes before accepting claims. |
| live repository and issue review | Check current Armory docs, issue graph, labels, blockers, and prior ledgers that already answer part of the question. |
| evidence classification | Classify each durable claim before using it. |
| Armory role mapping | Translate the external tool's vocabulary into current Armory terms without adopting foreign terms as Armory vocabulary. |
| bounded prototype decision | Decide whether prototype results are needed, and keep prototype scope separate from source-backed conclusions. |
| security and disclosure review | Classify credentials, local paths, raw logs, trajectories, transcripts, model outputs, external service usage, and provider/account state before publication. |
| documentation closeout | Run Change Set Documentation Closeout on every affected human-facing and agent-facing doc. |
| issue projection | Decide whether to update existing issues, create new issues, propose a PRD, propose an ADR, or defer projection. |
| final disposition | Assign a finalized External Tool Evaluation Disposition value after the evidence is sufficient. |

## Evidence Classification

Each External Tool Evaluation Record distinguishes these evidence classes:

- source-backed claims: claims supported by first-party source code, schemas,
  tests, manifests, or committed repository instructions.
- local observations: results from local commands, repo checks, or live issue
  reads that are useful for one evaluation run but can drift.
- prototype results: bounded experimental outcomes, including fixture behavior,
  failure modes, and measured tradeoffs.
- implementation inference: conclusions reasoned from documented or
  source-backed behavior but not directly stated by the tool provider.
- unknowns: unresolved facts, missing sources, stale claims, or questions that
  must block or limit projection.
- rejected claims: claims that sources, prototype results, or Armory constraints
  rule out for the current evaluation.

Use [Evidence Taxonomy](evidence-taxonomy.md) for the broader source and
durability vocabulary. Keep raw scratch output out of durable records unless it
has been promoted to portable project evidence.

## Projection Rules

An external-tool evaluation may project work only after the affected record
classifies the evidence basis and disclosure boundary.

Use existing issues when the finding belongs to an active issue's acceptance
criteria, dependency state, or closeout evidence. Create new issues when the
finding is actionable, separable, and not already owned. Propose a PRD when the
finding changes product or system requirements across multiple implementation
stories. Propose an ADR when the decision is hard to reverse, surprising without
context, and the result of a real tradeoff.

Child issues may update their own section of the External Tool Evaluation
Record as they close. The final-disposition issue owns the final coherence pass,
final projection state, and final disposition. A parent issue may cite the
record, but the record remains the durable evidence surface.

## Security Disclosure And Durability

Security concerns discovered during evaluation are classified immediately.
Public issue projection depends on disclosure safety and actionability.

The public record may include public-safe risk categories, effect boundaries,
uncertainty, and redacted conclusions. Do not commit or post credentials,
private local paths, raw logs, raw trajectories, transcripts, model outputs,
provider account state, exploit instructions, or sensitive external service
usage details.

If a concern is actionable and public-safe, update existing issues or create new
issues. If a concern is sensitive, record a redacted public note and route the
details through a private operator handoff. If a concern is not actionable yet,
record it as an unknown with a follow-up condition.

Change Set Security Closeout applies to evaluation changes that affect
security policy, executable validation, tool selection, provider boundaries,
credentials, side effects, or disclosure rules.

## Harbor-First Application

Harbor evaluation uses this contract as the general process for parent issue
[#183](https://github.com/nisavid/agent-armory/issues/183) and child issues
[#184](https://github.com/nisavid/agent-armory/issues/184),
[#185](https://github.com/nisavid/agent-armory/issues/185),
[#186](https://github.com/nisavid/agent-armory/issues/186),
[#187](https://github.com/nisavid/agent-armory/issues/187),
[#188](https://github.com/nisavid/agent-armory/issues/188),
[#189](https://github.com/nisavid/agent-armory/issues/189),
[#190](https://github.com/nisavid/agent-armory/issues/190), and
[#191](https://github.com/nisavid/agent-armory/issues/191).

The Harbor External Tool Evaluation Record lives at
[docs/evaluations/harbor.md](evaluations/harbor.md). It imports the completed
source-map result from
[Harbor Jig Source Map](closeout/harbor-jig-source-map.md), keeps later child
issue outputs pending until those issues close, and starts with final
disposition set to unknown pending evidence while the evaluation remains in
progress.

## Closeout

Before an external-tool evaluation issue is merge-ready, perform the applicable
checks in this order:

1. Verify live issue labels, blockers, dependencies, and parent/child routing.
2. Confirm the External Tool Evaluation Record exists or records a
   not-applicable rationale.
3. Run the validation checks that cover the reusable contract and any required
   evaluation record shape.
4. Run Change Set Security Closeout.
5. Run Change Set Documentation Closeout.
6. Run Cross-Boundary Coherence Ralph Review.
7. Run Story Quality Ralph Review.
8. Record issue and PR projection, including any deferred risks or follow-up
   conditions.

Do not mark an External Tool Evaluation Record complete until the record has
enough evidence to support one finalized External Tool Evaluation Disposition
value: adopted candidate, supporting component, research reference, deferred,
or rejected.
