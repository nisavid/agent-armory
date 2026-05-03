# Smith Runbook

Status: Framework Seed

This runbook is the canonical workflow for Smiths creating Agent Equipment with the Framework Seed.

## Capability card

Write the capability card before choosing an interface.

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

Create an interface decision record after the capability card.

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

## Docs/config/scripts/hooks/skills/profiles/plugins

Build from lower-overhead surfaces upward.

1. Put shared project truth in local docs.
2. Put thresholds, modes, allowlists, and local choices in config.
3. Put deterministic parsing, validation, and formatting in scripts.
4. Put hard policy and lifecycle checks in hooks, permissions, sandboxes, or approvals.
5. Put procedural judgment in skills.
6. Put specialized worker shape in Agent Profiles.
7. Put portable bundles in Harness Plugins.

Do not duplicate the same rule across every surface. Keep one canonical source and point or enforce from the others.

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

Assign and maintain a promotion state for every Framework Example, spec, and Equipment Candidate.

Use `example` for teaching artifacts, `specified` for accepted behavior without an implementation plan, `planned` for implementation-ready work, `implemented` for built equipment, `validated` for equipment with passing evidence, and `published` for equipment intended to be equipped.

Do not present an example, spec, or unvalidated implementation as Published Agent Equipment.

## Closeout

Before closeout, verify:

- the capability card and interface decision record agree;
- deterministic checks run or have an explicit unavailable-control note;
- security and control requirements are represented in the right surfaces;
- harness claims name their evidence and refresh basis;
- docs, config, scripts, hooks, skills, profiles, plugins, and templates are discoverable from the Framework path;
- promotion state and next validation step are recorded.

If a stakeholder decision or unavailable control surface blocks the work, escalate with the needed result or artifact stated clearly.
