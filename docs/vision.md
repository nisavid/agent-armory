# Armory Vision

Status: Forge Seed

## Experience

The Agent Armory is being built to make a more coherent agent and operator
experience possible.

The intended experience starts with intent. An operator can express what they
want before every criterion, tool, risk, stakeholder constraint, or success
measure is known. The Armory's hypothesis is that the right generic equipment
can let an Agent translate underspecified but realizable intent into a
high-quality outcome.

That is not a better-prompting claim. It is an equipment claim.

## Equipment

The Armory is not a catalog of disconnected skills. Skills matter, but they are
only one kind of Agent Equipment.

Agent Equipment includes skills, MCP/tools, hooks, workflows, Harness Plugins,
Agent Profiles, scripts, policy frameworks, local docs, config, typed data
contracts, validators, orchestration patterns, and other harness components an
Agent or agentic system can equip. A single item may teach judgment, expose a
typed operation, enforce a policy boundary, retain durable knowledge, validate
an invariant, or package several components into a portable bundle.

The goal is coherence. Equipment should right-size the Agent's cognition to the
task. It should keep the model focused on judgment, ambiguity, synthesis, and
adaptation while giving deterministic responsibilities to software surfaces
that can perform them more reliably and efficiently.

That is the first departure from the common "bundle of skills" pattern. A
useful Armory item is not just another instruction file. It is part of a
harnessed system that can teach, constrain, inspect, validate, remember, route,
configure, and act.

## Harness lifecycle

Equipment becomes more powerful when it assembles into coherent loadouts and
plugins.

An Assembly is a group of equipment designed to work together. A Harness Plugin
is a portable package boundary that can carry skills, hooks, MCP/tool
definitions, Agent Profiles, scripts, docs, services, commands, and config
defaults into a harness.

The framework-style vision is that an equipped harness automatically steers and
enriches the Agent. The operator should not need a special incantation for the
Agent to ask better questions, respect policy, find durable knowledge, run
deterministic checks, or prepare for the next stage. The harness should make
those behaviors available through the Agent's normal inference lifecycle.

That lifecycle integration may happen through preloaded routing, on-demand
skills, MCP/tool schemas, hooks, approval gates, sandbox policy, Agent Profiles,
workflow controllers, config overlays, structured memory, validators, and
plugins. Each surface should carry the responsibility it can handle with the
least guesswork and the strongest available enforcement.

The Forge calls this least cognitive privilege. Put reasoning in the model only
when the model must actively reason. Put repeatability, policy, state,
serialization, and side effects into the harness surfaces that can make them
explicit, inspectable, and enforceable.

## Self-outfitting

An equipped Agent should not begin by merely generating a plausible answer. It
also should not always begin by doing the apparent task. It should begin by
making the intent usable.

Before selecting or inventing its initial equipment, the Agent asks the
operator enough questions to understand the shape, extent, and boundaries of
the solution space. The goal is not to exhaust every unknown before work starts.
The goal is to resolve enough ambiguity for the Agent to define an approach,
induce a plan, choose suitable standards, and know where the operator's
authority or values still matter.

The Agent then ingests the clarified intent, defines the approach, outfits the
work, induces the plan, and executes the solution. Outfitting means selecting
the right Agent Equipment, assembling it into a purpose-built Loadout, assigning
any accompanying Agents that need different roles or authority, and identifying
gaps before those gaps become quality failures.

Between stages, the Agent reflects on the previous stage, imagines the next
stage, asks the operator any new questions it has, predicts what capabilities
the next stage will need, and adjusts its Loadout accordingly. The same loop
also covers the underlying bookkeeping, durable knowledge retrieval, issue
routing, source lookup, config inspection, and evidence preservation that let an
Agent keep its own work coherent.

The result should feel methodical without requiring the operator to micromanage
method. The Agent should make the task legible, respect the context's value
system, use the tools and boundaries already available, and surface operator
decisions only where operator authority is actually needed.

## Self-onboarding

Self-outfitting depends on self-onboarding.

Given a task, an Agent should be able to discover what equipment exists, decide
what equipment fits, equip itself and any companion Agents, adapt that Loadout
to the harness and environment, and continue with clear evidence about what it
is relying on.

Given a missing capability, a Smith should be able to use the Forge to shape
that capability into equipment. Given a Forge limitation, a Forgewright should
be able to improve the Forge before equipment work continues.

The killer feature is autonomous self-onboarding to purpose-built assemblies of harness components.

The same methodology applies across use, procurement, and manufacturing:

- Wielders use Loadouts without needing to know every manufacturing detail.
- Outfitters assemble Loadouts from validated equipment and known harness facts.
- Smiths turn intent into equipment surfaces, validation, and promotion state.
- Forgewrights improve the Forge when the equipment-making process itself needs
  better tooling, policy, evidence, or structure.

Operators retain initiative and routing authority. Agents carry assigned work
forward until a stakeholder decision, unavailable access, or unknown policy
boundary requires operator input.

## Primitive Operations Equipment

The Armory's higher-level experience depends on lower-level equipment.

Agent Equipment Config is the shared configuration primitive. It should let
equipment declare typed schema fragments, compose layered policy, report
effective configuration, and project enforceable controls without making any
higher-level equipment own the generic config system. Equipment-specific config
should still work in session scope when shared config equipment is not present.

Issue Tracker Ops, or Issue Ops, makes follow-up durable. It gives Agents a way
to create, repair, enrich, organize, select, work, and orchestrate issue-tracked
work directly in an issue tracker. Reflection Findings, equipment candidates,
dependencies, and handoffs need this kind of durable routing so they do not
remain chat-only insight.

Agent Ops builds on lower-level equipment rather than owning it. It gives
repositories a framework for agentic operations: runbook discovery, autonomy
policy, owner and operator boundaries, extension points, publication rules, and
repo-specific operational behavior.

Periodic Actions and Harness Capability Refresh add time and drift awareness.
Recurring work needs local approval and auditable state. Harness facts need
source-backed refresh because equipment can only be reliable when the Armory
knows what each harness can actually enforce.

These primitives make later equipment adaptable. They let behavior vary by
organization, repository, checkout, session, issue set, harness, and operator
policy without hiding that variation in long prompts.

## Metacognitive loop

The higher-level cognition story connects the earlier primitives into a
self-directed loop.

Although a workflow's stages may be predefined, the Agent's metacognitive
behaviors should be self-initiated and self-directed. Reflection, imagination,
questioning, outfitting, bookkeeping, knowledge retrieval, capability
prediction, and policy inspection should happen because the harness equips the
Agent to do them, not because the operator remembers to ask for each behavior
by name.

That loop is what lets the Agent move stage by stage. It reflects on what just
happened, imagines what comes next, asks for missing operator decisions,
predicts the capabilities it will need, adjusts its Loadout, and then continues
with better evidence and boundaries.

## Head Gear

Head Gear is the planned name for the Armory's generic Cognition Enhancement
Equipment.

Its ambition is the universal deslopifier: generic equipment that helps an
Agent turn underspecified but realizable operator intent, even when it starts
as vibes, into a bounded, evidence-backed outcome. Head Gear is not merely a
prompt style. It is the loadout that should induce reflection, imagination,
questioning, bookkeeping, knowledge retrieval, capability prediction, and
self-outfitting before the Agent reaches for domain-specific equipment.

Head Gear builds on the earlier equipment lines. It needs Agent Equipment
Config for policy and adaptation, Issue Ops for durable routing of findings and
follow-up, Agent Ops for repository-operational context, Harness Capability
Refresh for current harness facts, and the Forge for manufacturing any missing
capability it discovers.

The Armory's hypothesis is that this stack can solve the slop problem by making
agent work productive, reliable, observable, controllable, accessible, and
enjoyable.

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

## Reflection

The Armory expects agents and harnesses to learn from recent experience.

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

The Armory succeeds when this layered equipment system can move an Agent from
underspecified but realizable intent to high-quality outcome by clarifying the
solution space, outfitting the work, using deterministic support where it
belongs, and improving the equipment ecosystem when the work reveals a gap.
