# Forgewright Runbook

Status: Forge Seed

This runbook is the canonical workflow for Agents that maintain the Agent Equipment Forge. Keep project-specific task checklists in PRDs, plans, ADRs, issues, and closeout records.

## Source handoff preservation

Preserve Source Handoffs as provenance. Do not turn archived prompts or handoff notes into current instructions.

For accepted source material:

- keep durable provenance through the Source Disposition Ledger or an explicitly
  scoped source-bearing checkpoint;
- record accepted requirements, deferments, challenge status, operator
  arbitration, and evidence targets in the Source Disposition Ledger;
- project the live rule into canonical docs, templates, examples, specs, validation, or ADRs;
- defer only with a reason and a downstream target.

## decision projection

Project durable decisions into the narrowest live surface that future Smiths or Forgewrights will read at the right time.

- Vocabulary belongs in `CONTEXT.md` and this Forge language surface.
- Current Smith procedure belongs in Forge Canon and templates.
- Architecture or policy choices that need rationale belong in ADRs.
- Repeatable checks belong in validation tools or tests.
- Bulky provenance stays in the Source Handoff.

Keep the current rule direct. Use historical contrast only when the history is the subject.

## Review Until Clean

Use Review Until Clean for Forge changes that establish or alter durable guidance.

A review cycle is clean when the latest reviewer pass has no findings that require changes. If review tooling is unavailable, record the attempted path, the unavailable control surface, and the residual risk before asking for human direction.

## Harness Fact Refresh

Refresh harness facts before relying on moving harness capabilities.

Use first-party docs, releases, source, or schemas where available. Label third-party metadata as fallback, and keep local CLI observations separate from source-backed facts. Record checked date, version basis, source URL, uncertainty, and the affected Forge surfaces.

## Change set closeout

Use `docs/story-closeout.md` for story-level closeout order, interdependency rules, and review sequencing.

Near the end of each cohesive Forge change set, inspect every agent-facing and human-facing doc the change could plausibly affect. Update stale claims, gaps, inaccurate initial-state language, and appropriate deliverable mentions. If no doc edits are needed, record the rationale in the closeout.

Run the security analyses applicable to the change-set scope before merge-readiness. Resolve reportable findings, or record stakeholder-approved deferment with risk rationale and tracking.

Ralph-review doc closeout changes with the relevant doc-writing guidance for the affected audience.

## Issue Projection

Repo Draft PRDs are review surfaces. Published PRD Issues are tracking surfaces.

After a Repo Draft PRD stabilizes and review is clean, create or update the corresponding Published PRD Issue. If projection remains pending, record why, what issue action is needed, and what repo artifact is the current source of truth.

## Equipment Blueprints

Equipment Blueprints describe future Agent Equipment without implementing it in the Forge Seed.

Each Blueprint names its promotion state, target harness assumptions, required Forge inputs, expected surfaces, validation needs, security boundaries, and open questions. When Forgewright decisions change the Forge, inspect Equipment Blueprints for drift and update or explicitly leave them unchanged with rationale.

## Tooling Gap intake

A Forgewright intake from a Smith starts by preserving the Smith handoff, refining the Tooling Gap, updating canonical surfaces and validation, and returning a hand-back note.

Treat the Smith handoff as active task context, not as durable doctrine. Project only accepted Forge decisions into the narrowest live surface. If the requirement is not accepted, record the deferment reason, tracking surface, and Smith resume guidance.

Before editing, identify:

- the blocked Smith task and tracking surface;
- the unsatisfied Tooling Gap;
- the dependency impact on the current equipment work;
- the selected session path: current session, subagent session, peer agent session, forked session, or new session;
- harness and operator constraints that affect the Forgewright path;
- the expected hand-back format.

After resolving or deferring the requirement, update affected Forge Canon, validation, source-disposition or provenance evidence, PRD/Blueprint/issue surfaces, and closeout evidence as applicable. The hand-back note names files changed, validation and review results, dependency updates, remaining risks, and the context the Smith needs to resume.
