# Smith Runbook

Status: Forge Seed

This runbook is the canonical workflow for Smiths creating Agent Equipment with the Forge Seed.

## Capability card

Write the capability card before choosing an interface. Start from
`templates/capability-card.md` when creating a new equipment candidate.

Capture:

- name and purpose;
- intended users and target harnesses;
- risks, external systems, and side effects;
- needed docs, config, scripts, hooks, skills, MCP/tools, Agent Profiles, and plugins;
- hard rules and deterministic checks;
- output contract and failure modes;
- evidence category and open questions.

The card keeps the capability independent from any first implementation shape.

## Interface decision record

Create an interface decision record after the capability card. Start from
`templates/interface-decision-record.md` and keep it aligned with the capability
card as the design changes.

For each requirement, decide the narrowest reliable surface:

- skill for judgment;
- MCP/tool for typed operations or live state;
- hook for lifecycle enforcement or observation;
- Agent Profile for specialized identity, authority, context, model, or tools;
- Harness Plugin for installation and distribution;
- script for deterministic work;
- local docs for canonical project truth;
- config for durable parameters and local choices.

Record rejected alternatives, evidence category, harness-specific projection, risks, and maintenance notes.

## Docs/config/scripts/hooks/skills/agents/plugins

Build from lower-overhead surfaces upward.

1. Put shared project truth in local docs.
2. Put thresholds, modes, allowlists, and local choices in config.
3. Put deterministic parsing, validation, and formatting in scripts.
4. Put hard policy and lifecycle checks in hooks, permissions, sandboxes, or approvals.
5. Put procedural judgment in skills.
6. Put specialized worker shape in Agent Profiles.
7. Put portable bundles in Harness Plugins.

Do not duplicate the same rule across every surface. Keep one canonical source and point or enforce from the others.

Use the component templates under `templates/` when a capability needs a skill,
hook, Agent Profile, plugin, script, MCP/tool definition, config file, security
review, or context-budget review.

## Pressure Scenario Validation

Use Pressure Scenario Validation before promoting a skill or skill-shaped workflow.

A useful validation records:

- the realistic task pressure that should trigger the skill;
- baseline failure, friction, or ambiguity without the skill;
- the expected loaded instructions or routing path;
- the Agent behavior after the skill is available;
- evidence that the skill was followed under task pressure;
- gaps, false triggers, and follow-up changes.

Pressure validation is not a read-through. It tests whether an Agent actually uses the equipment when the task is busy.

## Equipment Promotion Path

Assign and maintain a promotion state for every Forge Example, spec, and Equipment Candidate.

Use `example` for teaching artifacts, `specified` for accepted behavior without an implementation plan, `planned` for implementation-ready work, `implemented` for built equipment, `validated` for equipment with passing evidence, and `published` for equipment intended to be equipped.

Do not present an example, spec, or unvalidated implementation as Published Agent Equipment.

## Tooling Request

When a Smith finds an unsatisfied Tooling Gap that blocks or materially weakens the current equipment task, treat the Tooling Work as a dependency and escalate to a Forgewright before continuing.

Use this path without asking whether the capability exists. Ask only when the harness or stakeholder policy leaves a concrete choice unresolved.

1. State the blocking requirement in the current task, issue, project, or local plan. If the Smith cannot update the tracking surface, put the dependency in the handoff and make tracking part of the Forgewright request.
2. Preserve a Smith resume note before switching context. Include the current objective, completed work, open files, validation state, pending decisions, and the exact condition for resuming.
3. Choose the least disruptive Forgewright path supported by the harness and operator policy: current session, subagent session, peer agent session, forked session, or new session.
4. Hand off only the context needed for Tooling Work, plus source links for anything the Forgewright must verify.
5. Stop Smith implementation until the Forgewright returns a hand-back, explicitly defers the requirement with tracking, or the operator chooses a different path.

Session path selection:

| Path | Use when | Smith duty |
| --- | --- | --- |
| Current session | The harness supports role switching and context retention, and the operator allows the same session to become Forgewright temporarily. | Record a resume note, switch to Forgewright, then use the Forgewright hand-back to restore Smith state before implementation resumes. |
| Subagent session | The harness can start a bounded subordinate Agent with a clear task and return contract. | Provide a self-contained handoff because subagents usually start with little or no parent context. |
| Peer agent session | The harness can hand work to another Agent with comparable authority or workspace access. | Provide the same handoff as for a subagent, plus coordination rules for shared files and review ownership. |
| Forked session | The harness can fork the current conversation or workspace context. | Output a copyable handoff prompt, state how to fork, and define the hand-back note the user should return. |
| New session | Forking is unavailable or inappropriate. | Output a standalone handoff prompt with repo path, branch, current SHA when available, relevant files, and the requested Forgewright deliverable. |

The handoff must include the blocked task, unsatisfied Tooling Gap, dependency impact, evidence checked, requested Forgewright deliverable, selected session path, and hand-back expectation.

The hand-back expectation should require:

- Forge decision or deferment;
- files changed or issue/project tracking updated;
- validation and review results;
- remaining risks or open questions;
- exact resume instructions for the Smith;
- whether the Smith must rerun security, documentation, validation, or review closeout before continuing.

## Closeout

Follow `docs/story-closeout.md` for closeout gate order, interdependencies, review sequencing, and rerun rules.

Before closeout, verify:

- the capability card and interface decision record agree;
- deterministic checks run or have an explicit unavailable-control note;
- security and control requirements are represented in the right surfaces;
- harness claims name their evidence and refresh basis;
- affected agent-facing and human-facing docs are inspected and updated, or unchanged rationale is recorded;
- applicable security closeout evidence is recorded;
- docs, config, scripts, hooks, skills, MCP/tools, Agent Profiles, plugins, and templates are discoverable from the Forge Conveyor;
- promotion state and next validation step are recorded.

Run a Cross-Boundary Coherence Ralph Review before story closeout.
This review checks whether behavior and evidence agree across PRD, specs, plan,
implementation, validation, security, documentation, issue or PR projection, and
release or handoff surfaces.

Run a Story Quality Ralph Review before story closeout.
This review checks general and specific DX, UX, code quality, clean
architecture, robustness against unspecified interactions, user personas, and
attack paths, mitigations for pathological dev/ops cycles, and alignment with a
coherent strategic vision.

If a stakeholder decision or unavailable control surface blocks the work, escalate with the needed result or artifact stated clearly.
