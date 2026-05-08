# Agent Armory

The Agent Armory defines a shared language for creating, cataloging, and maintaining reusable equipment for agents. This context keeps domain terms stable while the Forge is designed and refined.

## Language

**Agent Armory**:
A home for Agent Equipment.
_Avoid_: narrowing this term to one methodology, content model, directory structure, or toolchain

**Agent Equipment**:
Reusable tooling, behavior, workflow, knowledge, or configuration that equips an Agent or agentic system.
_Avoid_: asset, artifact, extension when used as the general term

**Equipment Candidate**:
A proposed, specified, planned, or implemented equipment surface that has not yet been validated and published for use.
_Avoid_: Published Agent Equipment

**Equipment Design Bundle**:
A neutral project-path bundle that gathers the design and validation-planning
artifacts for one Equipment Candidate, such as the capability card, interface
decision, security/control classification, pressure scenarios, validation plan,
closeout evidence plan, and related design records.
_Avoid_: Inventory, component implementation path, status dump

**Published Agent Equipment**:
Agent Equipment that has completed the promotion path and is intended to be equipped.
_Avoid_: example, draft, candidate

**Agent Equipment Forge**:
The Armory's method and supporting artifacts for designing, building, validating, and maintaining Agent Equipment.
_Avoid_: the Forge when the referent is unclear; Forge when the full name is needed for disambiguation

**Forgewright**:
An Agent that creates or refines the Agent Equipment Forge.
_Avoid_: architect agent, Forge author

**Smith**:
An Agent that creates Agent Equipment using the Agent Equipment Forge.
_Avoid_: implementer when the role includes equipment design

**Agent**:
The causal stream of reasoning, actions, tool calls, messages, and content mediated by an Agent Harness.
_Avoid_: bot, model, profile when precision matters

**Operator**:
An intent-capable actor that initiates, routes, controls, or evaluates Agent
work. An Operator may be a human or an orchestrator-agent.
_Avoid_: assuming every Operator is human; use human operator or stakeholder
when human authority specifically matters

**Agent Harness**:
The runtime or orchestration system in which an Agent is strapped.
_Avoid_: client when the system provides agent orchestration

**Strapped**:
Mediated by an Agent Harness.
_Avoid_: installed, configured, running when the harness relationship is the point

**Agent Profile**:
A reusable harness configuration for identity, mission, prompt, tools, model, permissions, and related behavior.
_Avoid_: Agent when referring to the reusable declaration

**Harness Component**:
Reusable behavior integrated into an Agent Harness.
_Avoid_: plugin part unless the package boundary matters

**Harness Plugin**:
A portable collection of Harness Components.
_Avoid_: plugin when referring to an individual skill, hook, or profile

**Source Handoff**:
Preserved upstream material accepted as provenance for Forge design, not the live Forge surface.
_Avoid_: canonical docs, final docs

**Forge Canon**:
The current conceptual framework and corresponding documentation that govern
Forge work.
_Avoid_: handoff docs, source notes

**Forge Core**:
The materialized and enacted Forge processes, contracts, components, and
deterministic tools that implement the core features and functions of the
Forge.
_Avoid_: Forge Canon, Forge Equipment Core

**Forge Equipment Core**:
The minimal Agent Equipment necessary for agents to autonomously operate Forge
functions in a manner that fulfills Forge contracts.
_Avoid_: Forge Canon, Forge Core

**Armory Equipment Core**:
The minimal Agent Equipment necessary for agents to autonomously operate Armory
functions outside the Forge. It may share equipment with the Forge Equipment
Core.
_Avoid_: Forge Equipment Core when the function is outside the Forge

**Agentic Engineering Operating Model Review**:
A structured review of the contracts and guidance under which Agents perform
engineering work, including authority, escalation, closeout gates, review
obligations, validation routing, issue and PR projection, evidence durability,
and how Agents discover, reference, and update those rules.
_Avoid_: Forge Domain Model Review, ad hoc process reminder

**Armory Integrity Validation**:
The top-level live repository validation umbrella for checking current Armory
surfaces, contracts, evidence, routing, and publication-readiness invariants.
It may include Forge-scoped validation suites and other Armory-scoped suites.
_Avoid_: Seed Validation, equipment-specific behavior validation

**Forge Integrity Validation**:
The Forge-scoped suite within Armory Integrity Validation that checks current
Forge Canon, Forge Core, Forge Equipment Core, Forge routes, Forge design
surfaces, and Forge closeout invariants.
_Avoid_: Armory-wide validation when the scope is only Forge; downstream
equipment behavior validation

**Forge Seed**:
The first coherent version of the Agent Equipment Forge, limited to canonical docs, decision method, evidence discipline, harness catalog, templates, examples, Smith task specs, and Seed Validation.
_Avoid_: Agent Ops implementation, Periodic Actions implementation

**Seed Validation**:
Historical runnable checks that verified the Forge Seed's own repository shape,
documentation links, provenance, accepted-handoff projection or explicit
deferment, and structured catalog fields.
_Avoid_: Armory Integrity Validation, Forge Integrity Validation, harness integration validation, production equipment validation

**Harness Capability Catalog**:
The human-facing front door and collection boundary for Vanilla Harness
Capability Profiles, sources, limitations, and refresh requirements.
_Avoid_: source map, research notes

**Capability Surface**:
The capabilities, constraints, affordances, controls, state, and effects that
an entity, arrangement, environment, equipment item, harness, or potential
configuration can grant, alter, restrict, expose, or mediate. A Capability
Surface can describe an actual current state, past state, intended state,
potential state, realizable fixture, or hypothetical design.
_Avoid_: component list when the capability-bearing state is the point

**Capability Profile**:
A notionally complete analysis and breakdown of a Capability Surface for a
stated scope, state, evidence basis, and intended use.
_Avoid_: summary, inventory, implementation plan

**Equipment Capability Surface**:
The Capability Surface of Agent Equipment, framed by the Agent capabilities the
equipment grants, alters, exposes, mediates, or restricts.
_Avoid_: implementation file list, installed package boundary

**Equipment Capability Profile**:
A Capability Profile for an Equipment Capability Surface.
_Avoid_: capability card when the profile is about observed or analyzable
capabilities rather than intended equipment purpose

**Harness Capability Surface**:
The Capability Surface of an Agent Harness in a stated state, including the
capabilities granted, altered, exposed, mediated, or restricted by the harness
and by the settings, equipment, plugins, profiles, tools, hooks, config, local
state, or other capabilities present in that state.
_Avoid_: Vanilla Harness Capability Surface when a non-default state is meant

**Harness Capability Profile**:
A Capability Profile for a Harness Capability Surface.
_Avoid_: Agent Profile, Harness Plugin, equipment projection guidance

**Vanilla Harness Capability Surface**:
The Harness Capability Surface for a harness immediately after installation and
onboarding, with default settings and default equipment. Vanilla Harness
Surface is accepted shorthand when the harness context is clear.
_Avoid_: Effective Harness Capability Surface, configured local harness state

**Vanilla Harness Capability Profile**:
A Harness Capability Profile for a Vanilla Harness Capability Surface. Vanilla
Harness Profile is accepted shorthand when the harness context is clear.
_Avoid_: Agent Profile, Effective Harness Capability Profile

**Effective Harness Capability Surface**:
The Harness Capability Surface for a harness in any specified state: current,
past, potential, realizable, or hypothetical. If the state is unspecified,
current state is assumed. Effective Harness Surface is accepted shorthand when
the harness context is clear.
_Avoid_: Vanilla Harness Capability Surface, base harness capability

**Effective Harness Capability Profile**:
A Harness Capability Profile for an Effective Harness Capability Surface.
Effective Harness Profile is accepted shorthand when the harness context is
clear.
_Avoid_: Vanilla Harness Capability Profile, Agent Profile

**Harness Fact Refresh**:
A source-backed update to Vanilla Harness Capability Profile claims when
harness versions or affordances may have changed.
_Avoid_: casual web lookup, stale handoff copy

**Harness Capability Profile Manager**:
The system that maintains Harness Capability Profiles through deterministic
manager-core tooling, agent-guided workflows, and optional evidence adapters.
_Avoid_: recurring scheduler, Forge consumption guidance

**Harness Capability Profile Manager Core**:
The deterministic tool layer of the Harness Capability Profile Manager,
responsible for schema validation, structured IO, claim IDs, evidence-link
checks, summary generation, diffs, deterministic migration, dry-run and apply
mechanics, audit formatting, fixture checks, and machine-readable study plan or
report validation.
_Avoid_: agent-guided judgment, source interpretation, open-ended research

**Capability Profiling Protocol**:
A generic meta-protocol that generates a study protocol for a selected
Capability Surface target by considering target type, desired rigor, available
controls, permitted effects, operator preferences, evidence needs, and jig
constraints.
_Avoid_: fixed harness test plan, one-size-fits-all validation recipe

**Capability State Graph**:
A sequence or directed acyclic graph of capability-relevant states and
transitions spanning the harness, its state-bearing components, equipment, and
external states that influence or are influenced by the capability under study.
_Avoid_: vague behavior pattern, single target state when the capability
manifests across states

**Capability Analysis Angle**:
A way of modeling, probing, or judging a capability claim, including the chosen
Capability State Graph, observation points, controls, expected evidence, and
practical tradeoffs.
_Avoid_: treating the first plausible test model as the only valid model

**Capability Claim Triage**:
The process for deciding how much re-analysis a capability claim needs based on
prior evidence, version deltas, claim criticality, similar capabilities,
applicability scope changes, and current intended use.
_Avoid_: exhaustive re-proof of every claim, unexamined evidence reuse

**Standard Clean-Room Profiling Jig**:
The ideal preferred baseline study environment and Capability Surface for
official Vanilla Harness Capability Profiles, designed to maximize control over
harness state, equipment, configuration, isolation, reproducibility, permitted
effects, and evidence quality within the limits of each harness.
_Avoid_: assuming every harness can expose the same controls

**Per-Harness Clean-Room Jig**:
The harness-specific clean-room profiling environment and Capability Surface
that records how closely one Agent Harness can approach the Standard
Clean-Room Profiling Jig and where it falls short.
_Avoid_: treating a harness-limited jig as the ideal baseline

**Forge Example**:
An annotated demonstration of the Forge's decision method using realistic but non-production equipment shapes.
_Avoid_: production package, installable equipment unless promoted through the full workflow

**Agent Ops**:
Future Agent Equipment for operating repositories agentically.
_Avoid_: treating it as implemented by the Forge Seed

**Agent-Operated Repository**:
A repository where agents drive assigned execution after a human operator initiates or continues the work session.
_Avoid_: fully autonomous repository, human-absent governance

**Initiative Authority**:
The human operator's reserved authority to choose project initiatives and start or continue work sessions.
_Avoid_: implementation authority, routine closeout authority

**Periodic Actions**:
Future Agent Equipment for defining, installing, inspecting, and uninstalling recurring agent actions across harnesses.
_Avoid_: treating it as implemented by the Forge Seed

**Harness Capability Refresh**:
Future recurring Agent Equipment for invoking the Harness Capability Profile
Manager and keeping Vanilla Harness Capability Profiles current over time.
_Avoid_: one-time Harness Fact Refresh

**Repo Draft PRD**:
A worktree-authored PRD used for review and refinement before projection into the issue tracker.
_Avoid_: treating the draft as the final issue-tracker record

**Published PRD Issue**:
A GitHub issue that tracks an accepted PRD after repo-draft review.
_Avoid_: letting it drift from the Repo Draft PRD without an explicit projection note

**Issue Projection**:
The post-review step that creates or updates a Published PRD Issue from a stable Repo Draft PRD.
_Avoid_: issue churn during draft review, untracked divergence

**Issue Tracker Ops**:
Agent Equipment for recording, reviewing, repairing, enriching, organizing,
assigning, working, and orchestrating issue-tracked follow-ups directly in an
issue tracker.
_Avoid_: Issue Projection when the work is broader than PRD publication;
in-tree tracking state when the issue tracker is available

**Issue Ops**:
Accepted shorthand for Issue Tracker Ops after the full name is clear in the
current context.
_Avoid_: using it as a separate equipment name

**Agent Equipment Config**:
Agent Equipment for shared, layerable, composable, adaptable, and enforceable
configuration across Agent Equipment.
_Avoid_: treating it as a component of Agent Ops or any other higher-level
equipment

**Layer Precedence**:
The normal Agent Equipment Config merge order that decides which configuration
value would win when no policy lock blocks it.
_Avoid_: policy authority, when the point is the value merge order

**Policy Authority**:
The right of a configuration layer to constrain later overrides or
lower-authority layers by marking a setting non-overridable or requiring a
mutation gate.
_Avoid_: layer precedence, when the point is who may constrain later overrides

**Config Safety Status**:
The machine-visible Agent Equipment Config classification that states whether a
configuration is usable, incomplete, unsafe, stale, untrusted, or conflicted
for the requested behavior.
_Avoid_: treating schema validity alone as write safety

**Cognition Enhancement Equipment**:
Agent Equipment that shapes how an Agent reasons, reflects, remembers, routes
insight, right-sizes cognition, or improves its future harness behavior.
_Avoid_: prompt style when deterministic support, durable capture, policy, or
validation is the needed surface

**Head Gear**:
The planned name for the Armory's generic Cognition Enhancement Equipment for
translating underspecified but realizable operator intent into high-quality
outcomes by inducing reflection, imagination, questioning, bookkeeping,
knowledge retrieval, capability prediction, and self-outfitting.
_Avoid_: domain-specific equipment, style-only prompting, one-off instruction
to think harder

**Reflection**:
An Agent activity that inspects recent experience, extracts reusable lessons,
and routes durable follow-up into Agent Equipment, issue tracker records,
config, docs, validators, workflows, policy, or Forge Tooling.
_Avoid_: chat-only introspection when the finding should become durable

**Reflection Finding**:
An issue-tracked or otherwise durable output of Reflection that captures an
observed friction, failure, pattern, or insight and the induced equipment,
policy, validator, config, workflow, or documentation candidate.
_Avoid_: final equipment design, untracked note

**Review Until Clean**:
A repeated review-and-revision loop that stops only when the latest review cycle has no findings.
_Avoid_: assuming any named external review skill is repo policy unless the operator invokes it or repo policy names it

**Forgewright Runbook**:
A concise canonical workflow for Agents that maintain the Agent Equipment Forge.
_Avoid_: storing every project plan, review transcript, or implementation checklist there

**Target Structure**:
A planned repository shape used to reason about Forge surfaces before all of those surfaces exist.
_Avoid_: treating the target as an unconditional directory mandate

**Seed Surface**:
A file or directory implemented during the Forge Seed because it had a clear
seed role.
_Avoid_: placeholder directories without seed responsibilities

**Seed Validation Tool**:
A transitional standard-library Python script that currently runs seed-era live
checks and reports results for humans or agents.
_Avoid_: package-manager-dependent validator, harness-specific validator

**Harness Evidence Source Policy**:
The rule that Harness Capability Profile claims prefer first-party sources, use
third-party metadata only as labeled fallback, and record local CLI
observations separately.
_Avoid_: unlabeled source mixing, stale memory-backed harness claims

**Equipment Promotion Path**:
The lifecycle that moves an equipment idea from example or spec toward Published Agent Equipment.
_Avoid_: treating example, specified, planned, implemented, validated, and published as interchangeable states

**Pressure Scenario Validation**:
A skill-validation method that tests whether an Agent follows a proposed skill under realistic task pressure, including evidence of baseline failure or gap and post-skill compliance.
_Avoid_: informal read-through, author confidence

**Skill Template**:
A seed artifact that shows how Smiths should shape future skills without itself being equipped as a skill.
_Avoid_: repo-local skill, production skill

**Forge Conveyor**:
The preloaded agent-facing route from root `AGENTS.md` into the Forge Canon, without scouting.
_Avoid_: requiring repo-wide search, relying only on README discovery

**Forge Tour**:
The Forge's exclusively human-facing documentation set, starting in this repo with `docs/forge-tour.md`.
_Avoid_: treating the root README link to the Tour as a special named surface; maintainer process dump; agent policy surface

**Blueprint**:
A positive construction spec for something to be built.
_Avoid_: non-goal list when the desired construction can be stated directly

**Equipment Blueprint**:
A Blueprint for Agent Equipment.
_Avoid_: downstream Smith spec when naming the current artifact shape

**Inventory**:
An index or catalog of available, candidate, or planned equipment.
_Avoid_: treating every docs list as Inventory

**Outfitter**:
An Agent that selects and assembles Agent Equipment from the Agent Armory into a Loadout for a role, task, session, Agent, or agentic system.
_Avoid_: Smith, Forgewright, Equipment creator

**Loadout**:
The selected equipment set for a role, task, session, Agent, or agentic system.
_Avoid_: Inventory, Assembly

**Wielder**:
An Agent outfitted with a Loadout and actively using that Agent Equipment to perform work.
_Avoid_: Outfitter, Loadout, Agent Profile

**Assembly**:
A cohesive grouping of equipment designed to work together.
_Avoid_: unintegrated collection

**Forge Tooling**:
Reusable fixtures, processes, validators, templates, and workflows supplied by the Forge.
_Avoid_: one-off Smith workaround

**Tooling Gap**:
A missing or inadequate Forge provision that blocks or materially weakens Smith work.
_Avoid_: ordinary task bug, ad hoc preference

**Tooling Request**:
A Smith workflow for pausing an equipment task when an unsatisfied Tooling Gap
blocks or materially weakens the task, recording that dependency, and handing
the Tooling Work to a Forgewright before continuing.
_Avoid_: vague handoff, unsupported workaround, continuing with an underspecified Forge

**Tooling Work**:
Forgewright work that adds or refines Forge Tooling.
_Avoid_: Smith equipment work

**Source Disposition Ledger**:
A durable, self-contained closeout surface that records source-handoff coverage, retained claim summaries, operator dispositions, and source-retirement evidence after raw source handoff materials are retired.
_Avoid_: raw source archive, implicit coverage, unverifiable handoff completeness

**Change Set Security Closeout**:
The end-of-change security activity that determines and performs the applicable security analyses, records findings and resolutions, and blocks merge-readiness on unresolved reportable risk.
_Avoid_: treating security review as optional cleanup, replacing analysis with a generic note

**Repository Threat Model**:
A repository-scoped security model that records assets, trust boundaries, attacker-controlled inputs, assumptions, invariants, and high-impact failure modes for future scans.
_Avoid_: target-specific finding list, one-off scan report

**Change Set Documentation Closeout**:
The end-of-change documentation activity that inspects affected agent-facing and human-facing docs, updates stale or incomplete claims, and reviews the result with audience-appropriate doc-writing standards.
_Avoid_: README-only cleanup, indiscriminate doc churn, stale initial-state language

**Story Closeout**:
The story-level activity that assembles validation, security, documentation, review, projection, and handoff evidence before a story is treated as complete.
_Avoid_: treating one clean subprocess as proof that the whole story is complete

**Cross-Boundary Coherence Ralph Review**:
A Review Until Clean gate that checks whether process outputs agree across PRD, specs, plans, implementation, validation, security, documentation, projection, and release or handoff surfaces.
_Avoid_: local-only consistency check

**Story Quality Ralph Review**:
A Review Until Clean gate that checks holistic quality after coherence is established, including DX, UX, architecture, robustness, strategic alignment, and lessons from prior development or operations failures.
_Avoid_: style-only review, generic correctness pass

**Intent**:
A direction that an intent-capable actor, declaration, specification, tool, or workflow imposes or attempts to impose. Intent is usually goal-oriented, or at least directionally so.
_Avoid_: treating intent as only stakeholder purpose or only written specification

**Effective Intent**:
The Intent actually imposed by ADRs, PRDs, specs, plans, acceptance criteria, review dispositions, and other declarative project surfaces; this is the direction the project would take if agents followed those declarations literally.
_Avoid_: assuming declarations always capture the operator's full purpose

**Underlying Intent**:
The stakeholder's actual current Intent: the direction they would want the project to move if a mismatch were brought to their attention. An agent does not directly know a stakeholder's or other intent-capable actor's Underlying Intent; it maintains an evidence-backed model that can be tested through questions, experiments, and observed corrections.
_Avoid_: confusing the agent's model of intent with the intent itself

**Intent Model Refresh**:
The first Story Closeout gate, where the agent updates its evidence-backed model of Underlying Intent from current operator input, accepted decisions, review dispositions, handoffs, and observed corrections before running downstream closeout gates.
_Avoid_: validating against stale assumptions

**Intent Alignment Check**:
A Story Quality check that compares Effective Intent with the refreshed model of Underlying Intent after Cross-Boundary Coherence has made Effective Intent legible. Refresh the model again if closeout evidence introduced new intent signals.
_Avoid_: silent reinterpretation, mind-reading, unexamined literalism

**Smith-to-Forgewright Handoff**:
The context package a Smith gives to a Forgewright for Tooling Request.
_Avoid_: vague note, unstructured context dump

**Forgewright Hand-Back**:
The return note a Forgewright gives a Smith after resolving or deferring a Tooling Gap.
_Avoid_: chat-only conclusion, undocumented resume instruction

## Relationships

- The **Agent Armory** contains **Agent Equipment** and the **Agent Equipment Forge**.
- The **Agent Equipment Forge** is created by **Forgewrights** and used by **Smiths**.
- **Smiths** create **Agent Equipment** for one or more **Agent Harnesses**.
- An **Equipment Design Bundle** gathers the early design and
  validation-planning surfaces for one **Equipment Candidate** before the
  interface decision projects implemented components into their chosen paths.
- **Equipment Candidates** may become **Published Agent Equipment** after validation and publication.
- An **Agent** is **Strapped** when its reasoning and actions are mediated by an **Agent Harness**.
- A **Harness Plugin** packages one or more **Harness Components**.
- An **Agent Profile** configures a reusable kind of **Agent** but is not the running **Agent**.
- A **Source Handoff** can inform **Forge Canon**, but it is not itself the live Forge surface.
- The **Forge Seed** specifies future **Agent Equipment** but does not implement that downstream equipment.
- **Seed Validation** checks the completed **Forge Seed**; live repository
  integrity belongs to **Armory Integrity Validation** and Forge-scoped live
  integrity belongs to **Forge Integrity Validation**.
- The **Harness Capability Catalog** is a **Forge Canon** surface informed by
  the **Source Handoff** and by **Harness Fact Refresh**.
- A **Capability Profile** analyzes a **Capability Surface** for a stated
  scope, state, evidence basis, and intended use.
- A **Harness Capability Profile** analyzes a **Harness Capability Surface**.
- A **Vanilla Harness Capability Profile** is the per-harness structured entry
  inside the **Harness Capability Catalog**.
- An **Effective Harness Capability Surface** combines a base **Agent Harness**
  with the capabilities layered onto the specified harness state.
- The **Harness Capability Profile Manager** maintains **Harness Capability
  Profiles** as deterministic data and tooling, while **Harness Capability
  Refresh** is the future recurring **Agent Equipment** that can invoke it.
- A **Forge Example** demonstrates how a **Smith** applies the **Agent Equipment Forge** but is not automatically **Agent Equipment**.
- **Agent Ops**, **Periodic Actions**, and **Harness Capability Refresh** are downstream **Agent Equipment** specified by the **Forge Seed**.
- In an **Agent-Operated Repository**, **Initiative Authority** stays with the human operator while agents drive assigned execution.
- A **Repo Draft PRD** can become the source for a **Published PRD Issue** after review.
- A **Published PRD Issue** is the tracking surface; material repo-draft changes need explicit issue re-projection.
- **Issue Projection** happens after repo-draft review; closeout records either the issue update or the reason projection remains pending.
- **Reflection Findings** are source material for future **Cognition Enhancement Equipment** and may also induce **Tooling Requests**, **Equipment Candidates**, or issue-tracked work in narrower equipment stories.
- **Head Gear** is the planned generic **Cognition Enhancement Equipment** line;
  it is intended to prepare the Agent to clarify, equip, execute, and reflect
  before domain-specific equipment takes over.
- A **Forgewright Runbook** guides Forge maintenance without replacing ADRs, PRDs, implementation plans, or Smith runbooks.
- A **Target Structure** can guide a PRD, but the **Forge Seed** creates only **Seed Surfaces**.
- A **Seed Validation Tool** implements historical **Seed Validation** without
  adding runtime dependencies. Live validation tooling belongs under **Armory
  Integrity Validation** and its scoped validation suites.
- A **Harness Fact Refresh** follows the **Harness Evidence Source Policy**
  before updating Vanilla Harness Capability Profile claims.
- The **Equipment Promotion Path** distinguishes **Forge Examples**, **Equipment Candidates**, validation, and **Published Agent Equipment**.
- **Seed Validation** may check promotion-state labels for seed surfaces, but downstream equipment behavior needs equipment-specific validation.
- A **Skill Template** can guide future skill creation but is not **Published Agent Equipment**.
- A repo-local skill needs **Pressure Scenario Validation** before promotion to **Published Agent Equipment**.
- The **Forge Seed** exposes a **Forge Conveyor** for Smiths and a **Forge Tour** for readers.
- Live **Armory Integrity Validation** and **Forge Integrity Validation** may
  check the **Source Disposition Ledger** when accepted source material and
  retired raw source files remain active integrity evidence.
- A **Change Set Security Closeout** uses the **Repository Threat Model** when deciding which security analyses and fixes are required before merge-readiness.
- A **Change Set Documentation Closeout** updates affected **Forge Canon**, agent-facing policy, and human-facing orientation so established precedents and remaining ambiguities are represented accurately.
- **Story Closeout** depends on current change-set validation, **Change Set Security Closeout**, **Change Set Documentation Closeout**, **Cross-Boundary Coherence Ralph Review**, and **Story Quality Ralph Review**.
- **Intent Model Refresh** is the first **Story Closeout** gate so every downstream closeout check uses the current model of **Underlying Intent**.
- **Cross-Boundary Coherence Ralph Review** precedes **Story Quality Ralph Review** because quality review depends on coherent process evidence.
- A **Story Quality Ralph Review** includes an **Intent Alignment Check** that compares **Effective Intent** with the refreshed model of **Underlying Intent** before final Story Closeout.
- A **Tooling Request** turns an unsatisfied Forge Tooling need into a task dependency, moves Tooling Work to a **Forgewright**, and returns a **Forgewright Hand-Back** that lets the **Smith** resume safely.

## Example dialogue

> **Smith:** "Should this repeated repo maintenance behavior become one skill?"
> **Forgewright:** "Put the active judgment and procedure in a skill. Keep deterministic checks in scripts, hard policy in hooks, and durable project truth in Forge Canon. Preserve the Source Handoff as provenance, but project the decision into the Forge surface Smiths will actually use."

## Flagged ambiguities

- "Agent" can mean the running causal stream or a reusable harness declaration. Resolution: use **Agent** for the running stream and **Agent Profile** for the reusable declaration.
- "Handoff docs" can mean accepted source material or current project docs. Resolution: use **Source Handoff** for provenance and **Forge Canon** for the live Forge surface.
- "Tooling Work" can mean seeding the **Agent Equipment Forge** or implementing downstream equipment. Resolution: use **Forge Seed** for the first pass and name downstream equipment, such as Agent Ops or Periodic Actions, separately.
- "Agent-operated" can mean guided autonomous execution or unsupervised initiative selection. Resolution: **Initiative Authority** remains human, while agents drive assigned work inside active sessions.
- "Validation" can mean checking live repository or Forge integrity, proving
  historical seed migration, or proving harness-specific behavior. Resolution:
  use **Armory Integrity Validation** for live repository integrity, **Forge
  Integrity Validation** for Forge-scoped live integrity, **Seed Validation**
  for completed seed-migration scope, and named harness or equipment validation
  for behavior-specific proof.
- "Catalog refresh" can mean a one-time evidence update or downstream
  recurring equipment. Resolution: use **Harness Fact Refresh** for
  source-backed profile updates and **Harness Capability Refresh** for the
  downstream recurring equipment.
- "Example" can mean a teaching artifact or an installable package. Resolution: use **Forge Example** for annotated demonstrations and reserve **Agent Equipment** for promoted, validated equipment.
- "Agent Equipment" can mean the broad category or a ready-to-equip surface. Resolution: use **Equipment Candidate** before validation/publication and **Published Agent Equipment** for ready-to-equip surfaces.
- "PRD tracking" can mean worktree drafting or issue-tracker publication. Resolution: use **Repo Draft PRD** for reviewable drafts, **Published PRD Issue** for tracking, and re-project material draft changes into the issue.
- "Issue projection" can mean publication timing or synchronization mechanics. Resolution: use **Issue Projection** for post-review publication and closeout synchronization.
- "Reflection" can mean private thinking, a closeout habit, a durable finding, or future equipment. Resolution: use **Reflection Finding** when the output should be tracked, and **Cognition Enhancement Equipment** when the capability itself is being engineered.
- "Forgewright guidance" can mean durable workflow or a specific plan. Resolution: use the **Forgewright Runbook** for repeatable maintenance duties and keep project-specific steps in PRDs, plans, and ADRs.
- "Review until clean" can mean a general quality gate or a named imported skill. Resolution: use **Review Until Clean** for the repo concept and invoke named review skills only when requested or adopted by repo policy.
- "Repository structure" can mean an intended architecture or files to create now. Resolution: use **Target Structure** for the PRD-level architecture and **Seed Surface** for files created in the Forge Seed.
- "Validation tooling" can mean live integrity checks, historical seed checks,
  or harness behavior tests. Resolution: use live **Armory Integrity
  Validation** and **Forge Integrity Validation** tooling for current integrity
  checks, preserve **Seed Validation Tool** for historical seed scope while it
  remains relevant, and leave harness behavior tests to downstream equipment.
- "Harness evidence" can mean docs, release notes, source, third-party package metadata, or local CLI output. Resolution: follow the **Harness Evidence Source Policy** and label each evidence category.
- "Equipment status" can mean a teaching example, an accepted spec, a plan, implementation, validation result, or published equipment. Resolution: use the **Equipment Promotion Path** states.
- "Skill surface" can mean a template for Smiths or a real equipped skill. Resolution: use **Skill Template** for seed guidance and create repo-local skills only after **Pressure Scenario Validation**.
- "Security review" can mean a repository threat model, a diff-focused scan, a repository-wide scan, a secret scan, or a hardening task. Resolution: use **Change Set Security Closeout** for the merge-readiness gate and name the specific analysis performed.
- "Doc closeout" can mean updating one touched file or reassessing every affected doc audience. Resolution: use **Change Set Documentation Closeout** for the affected-doc sweep and review gate.
- "Closeout" can mean story completion, subordinate security or documentation gates, or publication cleanup. Resolution: use **Story Closeout** for the story-level gate and name subordinate gates explicitly.
- "Coherence review" can mean local module consistency or cross-process consistency. Resolution: use **Cross-Boundary Coherence Ralph Review** for the story-closeout gate that checks PRD, specs, plan, implementation, validation, security, docs, issue/PR projection, and release or handoff surfaces together.
- "Quality review" can mean style, correctness, architecture, UX, DX, or strategic fit. Resolution: use **Story Quality Ralph Review** for the story-closeout gate that checks holistic quality criteria after scoped process-specific reviews have done their work.
- "Intent" can mean a direction imposed by an intent-capable actor, the stakeholder's current intent, the project's declaration-imposed direction, or the agent's uncertain model of stakeholder intent. Resolution: use **Intent** for the general direction, **Underlying Intent** for actual current stakeholder intent, **Effective Intent** for the direction imposed by declarations, **Intent Model Refresh** for the first Story Closeout gate that updates the agent's evidence-backed model, and **Intent Alignment Check** for the Story Quality gate that compares Effective Intent against that refreshed model.
- "Forge discovery" can mean preloaded agent routing or human README discovery. Resolution: use **Forge Conveyor** for Smiths and **Forge Tour** for human readers.
- "Handoff coverage" can mean informal confidence or auditable projection. Resolution: use the **Source Disposition Ledger** for accepted requirements, deferments, challenge status, operator decisions, evidence targets, and source-retirement evidence.
