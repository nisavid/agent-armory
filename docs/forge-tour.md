# Forge Tour

The Forge Tour is the plain-language introduction to the Forge.
It explains what the Forge is for, how its agent roles fit together, and where
to go next before asking you to read deeper technical details.

## The Armory and the Forge

The Agent Armory is a home for agent equipment: reusable tooling, behavior,
workflow, knowledge, and configuration that equips agents or agentic systems.

The Forge is the Armory's construction system. It helps agents design, build,
check, and care for equipment so the result is predictable, evidence-aware, and
reviewable before anyone relies on it.

The [Armory Vision](vision.md) describes the intended experience behind that
construction system: Agents should be able to clarify underspecified intent,
outfit themselves with the right equipment, use deterministic support where it
belongs, and improve the equipment ecosystem when a task reveals a gap.

The current Forge gives agents the shared vocabulary, templates, examples,
planned blueprints, harness facts, checks, and safeguards they need to start
manufacturing equipment.

## The agent roles

The Forge names agent roles directly:

- **Wielders** use loadouts to perform work.
- **Outfitters** select agent equipment from the Armory and assemble loadouts.
- **Smiths** create agent equipment with the Forge.
- **Forgewrights** create and refine the Forge.

Operators decide what should happen and when work should begin. Once a
direction is set, agents carry out the assigned work until they need an
operator decision or access they do not have.

## How equipment is made

The Forge starts with what someone needs the equipment to help an agent do, not
with a file type.

1. A smith describes what the equipment should help an agent do, who will use
   it, which harnesses it depends on, what risks or side effects it has, what it
   should produce, what evidence supports it, and what questions remain open.
2. The smith chooses the lowest reliable place for each responsibility: a skill,
   tool, hook, agent profile, harness plugin, script, local doc, or config.
3. The design becomes concrete harness pieces that can be reviewed and checked.
4. The equipment moves through clear readiness states: example, specified,
   planned, implemented, validated, and published.
5. Checks, safeguards, documentation, and review determine whether the equipment
   can move forward.

This process keeps examples, blueprints, candidates, and published agent
equipment from being treated as the same thing.

## How harnesses get outfitted

The Forge separates equipment manufacturing from future outfitting and use.
Examples, blueprints, and candidates remain construction material until they
reach the readiness state that makes them safe to select.

When equipment reaches the right readiness state, an outfitter will be able to
select equipment from the Armory and assemble a loadout for a role, task,
session, agent, or agentic system. A wielder will then use that loadout inside
an agent harness.

The Forge records harness capability facts because loadouts depend on what a
harness can actually support. The same loadout may need different pieces for
Codex, Claude Code, Cursor, Hermes Agent, OpenCode, OpenClaw, or another
harness.

## How the Forge learns from equipment work

The Forge also improves itself through reflection. When a smith sees repeated
friction, weak routing, stale facts, missing policy, or an absent tool, that
lesson should become source material for better equipment rather than a
chat-only takeaway.

Until generic Reflection equipment exists, agents should capture actionable
reflection findings in the issue tracker and route them to the relevant
equipment story. Future Reflection and cognition equipment will automate more
of that loop: inspecting recent work, extracting reusable lessons, and routing
the resulting equipment, policy, config, validator, or documentation candidates.

The Agent Armory also keeps written notes for larger future work, including
portable workflow equipment, side-thread hand-back, and ephemeral workflow
opportunity capture. These notes are not inventory items. They are source
material for future equipment.

## Where to go next

- [Documentation map](README.md): choose a path by goal.
- [Armory Vision](vision.md): understand the experience the Armory, Forge, and
  Agent Equipment are meant to create.
- [Forge Canon](agent-equipment-forge.md): the primary overview of the Forge.
- [Smith runbook](smith-runbook.md): give this to an agent making equipment.
- [Forgewright runbook](forgewright-runbook.md): give this to an agent improving
  the Forge itself.
- [Interface decision guide](interface-decision-guide.md): use when your agent
  needs to decide where a piece of equipment belongs.
- [Harness capabilities](harness-capabilities.md): harness facts with evidence.
- [Security and control](security-and-control.md): what equipment may do, what
  needs approval, and where side effects are controlled.
- [Equipment promotion](equipment-promotion.md): how examples and candidates
  move toward published agent equipment.

## Where this tour stops

This tour is only orientation. Use the linked docs when you want an agent to
make equipment, inspect harness facts, or evaluate whether a future item is
ready to trust.
