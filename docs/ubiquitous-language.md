# Ubiquitous Language

Status: Forge Seed

This document is the canonical vocabulary surface for Smiths and Forgewrights. Use `CONTEXT.md` as the project-wide vocabulary register; use this document when applying that language inside the Agent Equipment Forge.

## Language

**Agent Armory** is the home for Agent Equipment and the Agent Equipment Forge.

**Agent Equipment** is reusable tooling, behavior, workflow, knowledge, or configuration that equips an Agent or agentic system.

**Equipment Candidate** is proposed, specified, planned, or implemented equipment that has not completed validation and publication.

**Forge Entry Bundle** gathers the early design and validation-planning artifacts for one Equipment Candidate before implementation surfaces are projected into component paths.

**Published Agent Equipment** is Agent Equipment that has completed the Equipment Promotion Path and is intended to be equipped.

**Agent Equipment Forge** is the Armory method and supporting artifacts for designing, building, validating, and maintaining Agent Equipment.

**Forgewright** is an Agent that creates or refines the Agent Equipment Forge.

**Smith** is an Agent that creates Agent Equipment using the Agent Equipment Forge.

**Agent** is the causal stream of reasoning, actions, tool calls, messages, and content mediated by an Agent Harness.

**Operator** is an intent-capable actor that initiates, routes, controls, or
evaluates Agent work. An Operator may be a human or an orchestrator-agent.

**Agent Harness** is the runtime or orchestration system in which an Agent is strapped.

**Strapped** means mediated by an Agent Harness.

**Agent Profile** is a reusable harness configuration for identity, mission, prompt, tools, model, permissions, and related behavior.

Many harnesses and Harness Plugin file paths call Agent Profiles `agents`.
Use Agent Profile in prose when the subject is the reusable configuration, and
use `agents/` for source paths that follow harness/plugin convention.

**Harness Component** is reusable behavior integrated into an Agent Harness.

**Harness Plugin** is a portable collection of Harness Components.

**Source Handoff** is preserved upstream material accepted as provenance for Forge design, not the live Forge surface.

**Forge Canon** is the current durable doctrine and canonical surfaces that govern Forge work.

**Forge Seed** is the first coherent version of the Agent Equipment Forge.

**Seed Validation** checks the Forge Seed's repository shape, links, source disposition, promotion-state labels, and catalog metadata.

**Harness Capability Catalog** is the canonical versioned record of Agent Harness affordances, limitations, sources, and refresh requirements.

**Harness Fact Refresh** is a source-backed update to the Harness Capability Catalog.

**Forge Example** is an annotated demonstration of the Forge's decision method using realistic but non-production equipment shapes.

**Equipment Promotion Path** is the lifecycle that moves an equipment idea from example or spec toward Published Agent Equipment.

**Issue Tracker Ops** is Agent Equipment for issue-tracked follow-ups
that should be created, reviewed, repaired, enriched, organized, assigned,
worked, and orchestrated directly in an issue tracker.

**Issue Ops** is accepted shorthand for Issue Tracker Ops.

**Agent Equipment Config** is Agent Equipment for shared, layerable,
composable, adaptable, and enforceable configuration across Agent Equipment.

**Layer Precedence** is the Agent Equipment Config merge order that decides
which configuration value would win when no policy lock blocks it.

**Policy Authority** is the right of a configuration layer to constrain
lower-precedence layers by marking a setting non-overridable or requiring a
mutation gate.

**Config Safety Status** is the machine-visible Agent Equipment Config
classification that states whether a configuration is usable, incomplete,
unsafe, stale, untrusted, or conflicted for the requested behavior.

**Cognition Enhancement Equipment** is Agent Equipment that shapes how an Agent
reasons, reflects, remembers, routes insight, right-sizes cognition, or
improves its future harness behavior.

**Head Gear** is the planned name for the Armory's generic Cognition
Enhancement Equipment for translating underspecified but realizable operator
intent into high-quality outcomes by inducing reflection, imagination,
questioning, bookkeeping, knowledge retrieval, capability prediction, and
self-outfitting.

**Reflection** is Agent activity that inspects recent experience, extracts
reusable lessons, and routes durable follow-up into equipment, issues, config,
docs, validators, workflows, policy, or Forge Tooling.

**Reflection Finding** is an issue-tracked or otherwise durable output of
Reflection that captures observed friction, failure, pattern, or insight and an
induced candidate for future work.

**Forge Conveyor** is the preloaded agent-facing route from root `AGENTS.md` into the Forge Canon, without scouting.

**Forge Tour** is the Forge's exclusively human-facing documentation set. In this repo, `docs/forge-tour.md` is the Forge README and initial Tour entry.

**Blueprint** is a positive construction spec for something to be built.

**Equipment Blueprint** is a Blueprint for Agent Equipment.

**Inventory** is an index or catalog of available, candidate, or planned equipment.

**Outfitter** is an Agent that selects and assembles Agent Equipment from the Agent Armory into a Loadout for a role, task, session, Agent, or agentic system.

**Loadout** is the selected equipment set for a role, task, session, Agent, or agentic system.

**Wielder** is an Agent outfitted with a Loadout and actively using that Agent Equipment to perform work.

**Assembly** is a cohesive grouping of equipment designed to work together.

**Forge Tooling** is reusable fixtures, processes, validators, templates, and workflows supplied by the Forge.

**Tooling Gap** is a missing or inadequate Forge provision that blocks or materially weakens Smith work.

**Tooling Request** is the structured escalation of a Tooling Gap to a Forgewright.

**Tooling Work** is Forgewright work that adds or refines Forge Tooling.

**Source Disposition Ledger** is the durable closeout surface that records source-handoff coverage, retained claim summaries, operator dispositions, and source-retirement evidence after raw source handoff materials are retired.

## Relationships

- The Agent Armory contains Agent Equipment and the Agent Equipment Forge.
- The Agent Equipment Forge is created by Forgewrights and used by Smiths.
- Smiths create Agent Equipment for one or more Agent Harnesses.
- A Forge Entry Bundle keeps one Equipment Candidate's capability card,
  interface decision, security/control classification, pressure scenarios,
  validation plan, closeout evidence plan, and related design records together
  in a neutral project path.
- Outfitters select Agent Equipment from the Armory and assemble Loadouts.
- Wielders use Loadouts to perform work.
- Equipment Candidates may become Published Agent Equipment after validation and publication.
- An Agent is strapped when its reasoning and actions are mediated by an Agent Harness.
- Operators initiate, route, control, or evaluate Agent work; human authority
  should be named explicitly when the distinction matters.
- A Harness Plugin packages one or more Harness Components.
- An Agent Profile configures a reusable kind of Agent but is not the running Agent.
- A Source Handoff can inform Forge Canon, but it is not itself the live Forge surface.
- Forge Examples teach the decision method; they are not automatically Agent Equipment.
- Seed Validation checks Forge Seed integrity; downstream equipment needs equipment-specific validation.
- The Forge Conveyor routes Smiths from preloaded agent instructions into the Forge Canon.
- The Forge Tour routes human readers into the Forge without exposing agent-only machinery first.
- Reflection Findings are source material for future Cognition Enhancement
  Equipment and may also induce Tooling Requests, Equipment Candidates, or
  issue-tracked work in narrower equipment stories.
- Head Gear is the planned generic Cognition Enhancement Equipment line; it is
  intended to prepare the Agent to clarify, equip, execute, and reflect before
  domain-specific equipment takes over.
- A Tooling Request moves a Tooling Gap into Tooling Work for a Forgewright.
- The Source Disposition Ledger replaces raw source-handoff preservation after source retirement.

## Precision rules

- Use **Agent** for the running causal stream, not for a reusable harness declaration.
- Use **Agent Profile** for a reusable identity, mission, tool, permission, or model configuration. Use `agents/` for source paths when following harness/plugin convention.
- Use **Agent Harness** for the runtime or orchestration system that mediates the Agent.
- Use **Agent Equipment** for reusable capability; use **Equipment Candidate** until validation and publication are complete.
- Use **Forge Entry Bundle** for early design and validation-planning records,
  not for an Inventory or implemented component path.
- Use **Published Agent Equipment** only after the promotion path reaches `published`.
- Use **Outfitter** for equipment selection and Loadout assembly, not for Equipment creation.
- Use **Wielder** for the equipped Agent using a Loadout, not for the Loadout itself.
- Use **Source Handoff** for source material before disposition and **Source Disposition Ledger** for durable coverage after raw source retirement.
- Use **Forge Canon** for current guidance.
- Use **Forge Seed** for this first Forge pass; name downstream equipment separately.
- Use **Harness Fact Refresh** for catalog updates and **Harness Capability Refresh** for the downstream equipment that maintains the catalog over time.
- Use **Issue Tracker Ops** for broad issue lifecycle equipment; use
  **Issue Projection** only for post-review PRD publication into the issue
  tracker.
- Use **Issue Ops** as shorthand only after the full Issue Tracker Ops name is
  clear in the current context.
- Use **Agent Equipment Config** for the shared equipment config primitive; use
  equipment-specific config for one equipment line's schema fragment or plain
  handoff shape.
- Use **Layer Precedence** for merge order, **Policy Authority** for who may
  constrain later overrides, and **Config Safety Status** for machine-visible
  safety classification.
- Use **Reflection Finding** for durable reflection output, not for private
  reasoning or final equipment design.
