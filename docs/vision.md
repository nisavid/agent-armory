# Armory Vision

Status: Forge Seed

The Agent Armory is being built to make a more coherent agent and operator
experience possible.

The intended experience starts with intent. An operator can express what they
want before every criterion, tool, risk, stakeholder constraint, or success
measure is known. In the target Armory experience, an underspecified but
realizable operator intent received by an Agent wielding only the Armory's
generic Head Gear is translated into a high-quality outcome.

That is the slop-solving claim. The input may be vibes; the output should be a
useful, well-shaped, evidence-backed result.

## Experience

An equipped Agent should not begin by merely generating a plausible answer. It
also should not always begin by doing the apparent task. It should begin by
making the intent usable.

Before selecting or inventing its initial equipment, the Agent asks the
operator enough questions to understand the shape, extent, and boundaries of
the solution space. The goal is not to exhaust every unknown before work starts.
The goal is to resolve enough ambiguity for the Agent to define an approach,
induce a plan, choose suitable standards, and know where the operator's
authority or values still matter.

Outfitting means selecting the right Agent Equipment, assembling it into a
purpose-built Loadout, assigning any accompanying Agents that need different
roles or authority, and identifying gaps before those gaps become quality
failures. If the needed equipment does not exist, the Agent starts the
engineering process by making or commissioning that equipment through the Forge.

The Agent then ingests the clarified intent, defines the approach, outfits the
work, induces the plan, and executes the solution. The result should feel
methodical without requiring the operator to micromanage method. The Agent
should make the task legible, respect the context's value system, use the tools
and boundaries already available, and surface operator decisions only where
operator authority is actually needed.

## Metacognitive loop

The workflow may have predefined stages, but the Agent's metacognitive
behavior should be self-initiated and self-directed.

Between stages, the Agent reflects on the previous stage, imagines the next
stage, asks the operator any new questions it has, predicts what capabilities
the next stage will need, and adjusts its Loadout accordingly. The same loop
also covers the underlying bookkeeping, durable knowledge retrieval, issue
routing, source lookup, config inspection, and evidence preservation that let an
Agent keep its own work coherent.

Equipment induces these behaviors through the Agent Harness. The operator
should not have to keep reminding the Agent to think critically, reflect,
anticipate, track context, prepare for the next phase, or keep itself aligned
with the active values and constraints.

Head Gear is the Armory's name for that generic cognition equipment: the
loadout that induces reflection, imagination, questioning, bookkeeping,
knowledge retrieval, capability prediction, and self-outfitting before the
Agent reaches for domain-specific equipment.

## Equipment

Skills are Agent Equipment, but the Armory's power comes from equipment that
goes beyond skills and from assemblies of equipment working in concert.

Agent Equipment includes skills, MCP/tools, hooks, workflows, Harness Plugins,
Agent Profiles, scripts, policy frameworks, local docs, config, typed data
contracts, validators, orchestration patterns, and other harness components an
Agent or agentic system can equip. A single item may teach judgment, expose a
typed operation, enforce a policy boundary, retain durable knowledge, validate
an invariant, or package several components into a portable bundle.

Coherent assemblies right-size the Agent's cognition to the task. They keep the
model focused on judgment, ambiguity, synthesis, and adaptation while giving
deterministic responsibilities to software surfaces that can perform them more
reliably and efficiently.

## Deterministic boundaries

The Armory treats probabilistic reasoning and deterministic software as
complementary parts of one harnessed experience.

Agents should do what they do best: infer intent, reason across context,
translate between domains, ask for the right missing decision, and adapt when
the situation changes. Equipment should take over where pattern matching is the
wrong reliability layer: deterministic parsing, schema validation, typechecking,
state inspection, policy evaluation, mutation gates, repeatable workflows, and
hard security boundaries.

Deterministically shaped operations should remain truly deterministic. Policy
that must be enforced should not live only in prose the model might forget.
Critical checks should run out of band. Durable knowledge should live where it
can be refreshed, cited, and handed off. Strongly typed data should typecheck
every time. Local choices, thresholds, autonomy levels, and environment-specific
parameters should be represented as config rather than hidden inside long
instructions.

## Harness lifecycle

The harness integrates equipment into the Agent's inference lifecycle.

That integration may happen through preloaded routing, on-demand skills,
MCP/tool schemas, hooks, approval gates, sandbox policy, Agent Profiles,
workflow controllers, config overlays, structured memory, validators, and
plugins. Each surface should carry the responsibility it can handle with the
least guesswork and the strongest available enforcement.

The Forge calls this least cognitive privilege. Put reasoning in the model only
when the model must actively reason. Put repeatability, policy, state,
serialization, and side effects into the harness surfaces that can make them
explicit, inspectable, and enforceable.

## Self-onboarding

The Armory's central feature is autonomous self-onboarding to purpose-built assemblies of harness components.

Given a task, an Agent should be able to clarify the operator's intent, discover
what equipment exists, decide what equipment fits, equip itself and any
companion Agents, adapt that Loadout to the harness and environment, and
continue with clear evidence about what it is relying on. Given a missing
capability, a Smith should be able to use the Forge to shape that capability
into equipment. Given a Forge limitation, a Forgewright should be able to
improve the Forge before equipment work continues.

The same methodology applies across use, procurement, and manufacturing:

- Wielders use Loadouts without needing to know every manufacturing detail.
- Outfitters assemble Loadouts from validated equipment and known harness facts.
- Smiths turn intent into equipment surfaces, validation, and promotion state.
- Forgewrights improve the Forge when the equipment-making process itself needs
  better tooling, policy, evidence, or structure.

Operators retain initiative and routing authority. Agents carry assigned work
forward until a stakeholder decision, unavailable access, or unknown policy
boundary requires operator input.

## Reflection

The Armory also expects agents and harnesses to learn from recent experience.

Reflection is the equipment-level counterpart to closeout. An Agent should
regularly inspect what happened, extract lessons, and act on them by improving
the harness surfaces that steer future work. Repeated friction can reveal a
missing skill, a weak hook, a brittle workflow, stale docs, an under-specified
config schema, an unsafe default, or a needed validator.

Self-alignment should therefore be an engineered loop, not only a prompt style.
The Agent reflects, identifies the harness adjustment that would make future
behavior more reliable, and routes that adjustment through the same Forge
discipline used for any other equipment.

Until generic Reflection equipment exists, manually invoked reflection should
still produce durable source material when it finds actionable work. Record the
finding in the issue tracker, route it to the relevant equipment story, and
preserve enough context for a future Smith to evaluate the induced equipment,
policy, validator, config, workflow, or documentation candidate.

## Lifecycle use

Use this vision as an input throughout the engineering lifecycle.

- Ideation asks whether an idea improves the Agent's ability to clarify intent,
  self-onboard, right-size cognition, respect stakeholder intent, or turn
  repeated friction into reusable equipment.
- Strategy asks which primitive equipment unlocks better future equipment, which
  assemblies belong together, and which work should be deferred until the right
  equipment exists.
- Architecture asks which responsibilities belong in probabilistic inference,
  deterministic software, durable docs, config, typed schemas, tools, hooks,
  plugins, Agent Profiles, or approval boundaries.
- Design asks how an Agent questions, discovers, equips, uses, adapts, hands
  off, and revises the equipment under realistic task pressure.
- Implementation keeps deterministic operations deterministic, state typed,
  policy enforceable, and model-facing context focused on judgment.
- Validation checks not only whether the component works, but whether the Agent
  asks useful questions, adjusts its Loadout, preserves evidence, and produces
  an experience that is reliable, explainable, policy-respecting, adaptable,
  and suitable for the intended Wielder or Outfitter.
- Maintenance asks what drift, repeated failures, stale assumptions, or awkward
  handoffs reveal about missing equipment or missing Forge support.

The Armory's hypothesis is that Head Gear solves the slop problem: it makes the
process productive, reliable, observable, controllable, accessible, and
enjoyable. The Armory succeeds when an Agent wielding generic Head Gear can move
from underspecified but realizable intent to high-quality outcome by clarifying
the solution space, outfitting the work, using deterministic support where it
belongs, and improving the equipment ecosystem when the work reveals a gap.
