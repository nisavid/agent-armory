# Metasmith Runbook

Status: Framework Seed

This runbook is the canonical workflow for Agents that maintain the Agent Equipment Framework. Keep project-specific task checklists in PRDs, plans, ADRs, issues, and closeout records.

## Source handoff preservation

Preserve Source Handoffs as provenance. Do not turn archived prompts or handoff notes into current instructions.

For accepted source material:

- keep the source file available under the handoff path;
- record the requirement in the Source Projection Register;
- project the live rule into canonical docs, templates, examples, specs, validation, or ADRs;
- defer only with a reason and a downstream target.

## decision projection

Project durable decisions into the narrowest live surface that future Smiths or Metasmiths will read at the right time.

- Vocabulary belongs in `CONTEXT.md` and this Framework language surface.
- Current Smith procedure belongs in canonical Framework docs and templates.
- Architecture or policy choices that need rationale belong in ADRs.
- Repeatable checks belong in validation tools or tests.
- Bulky provenance stays in the Source Handoff.

Keep the current rule direct. Use historical contrast only when the history is the subject.

## Review Until Clean

Use Review Until Clean for Framework changes that establish or alter durable guidance.

A review cycle is clean when the latest reviewer pass has no findings that require changes. If review tooling is unavailable, record the attempted path, the unavailable control surface, and the residual risk before asking for human direction.

## Harness Fact Refresh

Refresh harness facts before relying on moving harness capabilities.

Use first-party docs, releases, source, or schemas where available. Label third-party metadata as fallback, and keep local CLI observations separate from source-backed facts. Record checked date, version basis, source URL, uncertainty, and the affected Framework surfaces.

## Change set closeout

Near the end of each cohesive Framework change set, inspect every agent-facing and human-facing doc the change could plausibly affect. Update stale claims, gaps, inaccurate initial-state language, and appropriate deliverable mentions. If no doc edits are needed, record the rationale in the closeout.

Run the security analyses applicable to the change-set scope before merge-readiness. Resolve reportable findings, or record stakeholder-approved deferment with risk rationale and tracking.

Ralph-review doc closeout changes with the relevant doc-writing guidance for the affected audience.

## Issue Projection

Repo Draft PRDs are review surfaces. Published PRD Issues are tracking surfaces.

After a Repo Draft PRD stabilizes and review is clean, create or update the corresponding Published PRD Issue. If projection remains pending, record why, what issue action is needed, and what repo artifact is the current source of truth.

## downstream Smith specs

Downstream Smith specs describe future Agent Equipment without implementing it in the Framework Seed.

Each spec names its promotion state, target harness assumptions, required Framework inputs, expected surfaces, validation needs, security boundaries, and open questions. When Metasmith decisions change the Framework, inspect downstream specs for drift and update or explicitly leave them unchanged with rationale.
