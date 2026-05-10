# Ubiquitous Language

Status: Forge Canon

This document is the canonical vocabulary surface for Smiths and Forgewrights. Use `CONTEXT.md` as the project-wide vocabulary register; use this document when applying that language inside the Agent Equipment Forge.

## Language

**Agent Armory** is the home for Agent Equipment and the Agent Equipment Forge.

**Agent Equipment** is reusable tooling, behavior, workflow, knowledge, or configuration that equips an Agent or agentic system.

**Agentic Engineering** is software engineering performed agentically: code is
written by AI Agents, and the surrounding work is managed with methodical
attention to how Agents navigate tasks, fail, recover, use context, and benefit
from equipment.

**Agent Engineering** is the engineering of Agents, agentic systems, agent
roles, and agent workflows.

**Agent Meta-Engineering** is Agent Engineering whose problem domain is
engineering work: creating or refining the Agents, agentic systems, roles,
workflows, operating models, and equipment that make Agentic Engineering more
capable.

**Equipment Candidate** is proposed, specified, planned, or implemented equipment that has not completed validation and publication.

**Equipment Design Bundle** gathers the early design and validation-planning
artifacts for one Equipment Candidate before implementation surfaces are
projected into component paths.

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

**Forge Canon** is the current conceptual framework and corresponding
documentation that govern Forge work.

**Forge Core** is the materialized and enacted Forge processes, contracts,
components, and deterministic tools that implement the core features and
functions of the Forge.

**Forge Equipment Core** is the minimal Agent Equipment necessary for agents to
autonomously operate Forge functions in a manner that fulfills Forge contracts.

**Armory Operating Contract** is a durable rule surface that governs Agentic
Engineering or repository operations across the Agent Armory, rather than a
specific Forge function or Equipment Candidate.

**Armory Equipment Core** is the minimal Agent Equipment necessary for agents
to autonomously operate Armory functions outside the Forge. It may share
equipment with the Forge Equipment Core.

**Agentic Engineering Operating Model Review** is a structured review of the
contracts and guidance under which Agents perform engineering work, including
authority, escalation, closeout gates, review obligations, validation routing,
issue and PR projection, evidence durability, and rule discovery or update
paths.

**Armory Integrity Validation** is the top-level live repository validation
umbrella for checking current Armory surfaces, contracts, evidence, routing,
and publication-readiness invariants.

**Forge Integrity Validation** is the Forge-scoped suite within Armory
Integrity Validation that checks current Forge Canon, Forge Core, Forge
Equipment Core, Forge routes, Forge design surfaces, and Forge closeout
invariants.

**Forge Seed** is the first coherent version of the Agent Equipment Forge.

**Seed Validation** is historical validation of the completed Forge Seed's
repository shape, links, source disposition, promotion-state labels, and
catalog metadata.

**Harness Capability Catalog** is the human-facing front door and collection
boundary for Vanilla Harness Capability Profiles, sources, limitations, and
refresh requirements.

**Capability Surface** is the capabilities, constraints, affordances, controls,
state, and effects that an entity, arrangement, environment, equipment item,
harness, or potential configuration can grant, alter, restrict, expose, or
mediate. A Capability Surface may describe an actual current state, past state,
intended state, potential state, realizable fixture, or hypothetical design.

**Capability Profile** is a notionally complete analysis and breakdown of a
Capability Surface for a stated scope, state, evidence basis, and intended use.

**Equipment Capability Surface** is the Capability Surface of Agent Equipment,
framed by the Agent capabilities the equipment grants, alters, exposes,
mediates, or restricts.

**Equipment Capability Profile** is a Capability Profile for an Equipment
Capability Surface.

**Harness Capability Surface** is the Capability Surface of an Agent Harness in
a stated state, including the capabilities granted, altered, exposed, mediated,
or restricted by the harness and by the settings, equipment, plugins, profiles,
tools, hooks, config, local state, or other capabilities present in that state.

**Harness Capability Profile** is a Capability Profile for a Harness Capability
Surface.

**Vanilla Harness Capability Surface** is the Harness Capability Surface for a
harness immediately after installation and onboarding, with default settings
and default equipment. Vanilla Harness Surface is accepted shorthand when the
harness context is clear.

**Vanilla Harness Capability Profile** is a Harness Capability Profile for a
Vanilla Harness Capability Surface. Vanilla Harness Profile is accepted
shorthand when the harness context is clear.

**Effective Harness Capability Surface** is the Harness Capability Surface for
a harness in any specified state: current, past, potential, realizable, or
hypothetical. If the state is unspecified, current state is assumed. Effective
Harness Surface is accepted shorthand when the harness context is clear.

**Effective Harness Capability Profile** is a Harness Capability Profile for an
Effective Harness Capability Surface. Effective Harness Profile is accepted
shorthand when the harness context is clear.

**Harness Fact Refresh** is a source-backed update to Vanilla Harness
Capability Profile claims.

**Harness Capability Profile Manager** is the system that maintains Harness
Capability Profiles through deterministic manager-core tooling, agent-guided
workflows, and optional evidence adapters.

**Harness Capability Profile Manager Core** is the deterministic tool layer of
the Harness Capability Profile Manager, responsible for schema validation,
structured IO, claim IDs, evidence-link checks, summary generation, diffs,
deterministic migration, dry-run and apply mechanics, audit formatting, fixture
checks, and machine-readable study plan or report validation.

**Capability Profiling Protocol** is a generic meta-protocol that generates a
study protocol for a selected Capability Surface target by considering target
type, desired rigor, available controls, permitted effects, operator
preferences, evidence needs, and jig constraints.

**Capability State Graph** is a sequence or directed acyclic graph of
capability-relevant states and transitions spanning the harness, its
state-bearing components, equipment, and external states that influence or are
influenced by the capability under study.

**Capability Analysis Angle** is a way of modeling, probing, or judging a
capability claim, including the chosen Capability State Graph, observation
points, controls, expected evidence, and practical tradeoffs.

**Capability Claim Triage** is the process for deciding how much re-analysis a
capability claim needs based on prior evidence, version deltas, claim
criticality, similar capabilities, applicability scope changes, and current
intended use.

**Standard Clean-Room Profiling Jig** is the ideal preferred baseline study
environment and Capability Surface for official Vanilla Harness Capability Profiles, designed to
maximize control over harness state, equipment, configuration, isolation,
reproducibility, permitted effects, and evidence quality within the limits of
each harness.

**Per-Harness Clean-Room Jig** is the harness-specific clean-room profiling
environment and Capability Surface that records how closely one Agent Harness can approach the
Standard Clean-Room Profiling Jig and where it falls short.

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
later overrides or lower-authority layers by marking a setting
non-overridable or requiring a mutation gate.

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
- Agentic Engineering is software engineering performed agentically, while
  Agent Engineering is the engineering of Agents and agentic systems.
- Agent Meta-Engineering is Agent Engineering focused on engineering work; it
  can produce the Agents, workflows, operating models, and Agent Equipment that
  improve Agentic Engineering.
- The Agent Equipment Forge is created by Forgewrights and used by Smiths.
- Smiths create Agent Equipment for one or more Agent Harnesses.
- An Equipment Design Bundle keeps one Equipment Candidate's capability card,
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
- A Capability Profile analyzes a Capability Surface for a stated scope, state,
  evidence basis, and intended use.
- A Harness Capability Profile analyzes a Harness Capability Surface.
- A Vanilla Harness Capability Profile is the per-harness entry inside the
  Harness Capability Catalog.
- An Effective Harness Capability Surface combines a base Agent Harness with
  the capabilities layered onto the specified harness state.
- The Harness Capability Profile Manager maintains Harness Capability Profiles
  through deterministic manager-core tooling, agent-guided workflows, and
  optional evidence adapters; Harness Capability Refresh is future recurring
  Agent Equipment that can invoke it.
- An Agent Profile configures a reusable kind of Agent but is not the running Agent.
- A Source Handoff can inform Forge Canon, but it is not itself the live Forge surface.
- Forge Examples teach the decision method; they are not automatically Agent Equipment.
- Seed Validation checks completed Forge Seed integrity; live repository
  integrity belongs to Armory Integrity Validation and Forge-scoped live
  integrity belongs to Forge Integrity Validation.
- Armory Operating Contracts state cross-Armory operating rules in readable
  form; deterministic validators enforce selected machine-checkable slices of
  those rules.
- Story Closeout is an Armory Operating Contract because it governs cohesive
  change sets across the Armory rather than a specific Forge function.
- The Forge Conveyor routes Smiths from preloaded agent instructions into the Forge Canon.
- The Forge Tour routes human readers into the Forge without exposing agent-only machinery first.
- Reflection Findings are source material for future Cognition Enhancement
  Equipment and may also induce Tooling Requests, Equipment Candidates, or
  issue-tracked work in narrower equipment stories.
- Portable Agentic Engineering workflow equipment is downstream of repo-local
  Armory Operating Contracts until the rules are coherent and pressure-tested
  enough to package.
- Head Gear is the planned generic Cognition Enhancement Equipment line; it is
  intended to prepare the Agent to clarify, equip, execute, and reflect before
  domain-specific equipment takes over.
- A Tooling Request moves a Tooling Gap into Tooling Work for a Forgewright.
- The Source Disposition Ledger replaces raw source-handoff preservation after source retirement.

## Precision rules

- Use **Agent** for the running causal stream, not for a reusable harness declaration.
- Use **Agent Profile** for a reusable identity, mission, tool, permission, or model configuration. Use `agents/` for source paths when following harness/plugin convention.
- Use **Agent Harness** for the runtime or orchestration system that mediates the Agent.
- Use **Vanilla Harness Capability Profile** for the default post-installation
  and onboarding harness profile. Use **Effective Harness Capability Profile**
  for a current, potential, realizable, hypothetical, or otherwise specified
  configured harness state.
- Use **Agent Equipment** for reusable capability; use **Equipment Candidate** until validation and publication are complete.
- Use **Equipment Design Bundle** for early design and validation-planning records,
  not for an Inventory or implemented component path.
- Use **Published Agent Equipment** only after the promotion path reaches `published`.
- Use **Outfitter** for equipment selection and Loadout assembly, not for Equipment creation.
- Use **Wielder** for the equipped Agent using a Loadout, not for the Loadout itself.
- Use **Source Handoff** for source material before disposition and **Source Disposition Ledger** for durable coverage after raw source retirement.
- Use **Forge Canon** for current guidance.
- Use **Forge Seed** for this first Forge pass; name downstream equipment separately.
- Use **Harness Fact Refresh** for source-backed profile updates and **Harness
  Capability Refresh** for the downstream recurring equipment that invokes the
  profile manager over time.
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
