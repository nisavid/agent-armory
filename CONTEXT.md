# Agent Armory

The Agent Armory defines a shared language for creating, cataloging, and maintaining reusable equipment for agents. This context keeps domain terms stable while the Forge is designed and refined.

## Language

Keep glossary terms in this section sorted alphabetically by term name.

**Advisory Mode**:
A mode where Agent Equipment provides non-authoritative guidance, diagnostics,
or plans without owning the behavior.
_Avoid_: Shadow Mode, Operational Continuity

**Agent**:
The causal stream of reasoning, actions, tool calls, messages, and content mediated by an Agent Harness.
_Avoid_: bot, model, profile when precision matters

**Agent Armory**:
A home for Agent Equipment.
_Avoid_: narrowing this term to one methodology, content model, directory structure, or toolchain

**Agent Engineering**:
The engineering of Agents, agentic systems, agent roles, and agent workflows.
_Avoid_: Agentic Engineering when the work is ordinary software engineering
performed by Agents

**Agent Equipment**:
Reusable tooling, behavior, workflow, knowledge, or configuration that equips an Agent or agentic system.
_Avoid_: asset, artifact, extension when used as the general term

**Agent Equipment Config**:
Agent Equipment for shared, layerable, composable, adaptable, and enforceable
configuration across Agent Equipment.
_Avoid_: treating it as a component of Repo Ops or any other higher-level
equipment

**Agent Equipment Forge**:
The Armory's method and supporting artifacts for designing, building, validating, and maintaining Agent Equipment.
_Avoid_: the Forge when the referent is unclear; Forge when the full name is needed for disambiguation

**Agent Harness**:
The runtime or orchestration system in which an Agent is strapped.
_Avoid_: client when the system provides agent orchestration

**Agent Meta-Engineering**:
Agent Engineering whose problem domain is engineering work: creating or
refining the Agents, agentic systems, roles, workflows, operating models, and
equipment that make Agentic Engineering more capable.
_Avoid_: Agentic Engineering, generic Agent Engineering outside the engineering
work domain

**Agent Ops**:
The generic term for operations work performed agentically.
_Avoid_: using Agent Ops as the name of the repository-operations equipment line

**Agent Profile**:
A reusable harness configuration for identity, mission, prompt, tools, model, permissions, and related behavior.
_Avoid_: Agent when referring to the reusable declaration

**Agent Test Jig**:
A controlled Capability Surface where an Agent Harness, Agent Equipment,
Loadout, or interaction can be installed, exercised, observed, and evaluated.
_Avoid_: Agent Harness, Harness Test Suite, Standard Clean-Room Profiling Jig
when the referent is not the harness runtime or the profiling-jig ideal

**Agent-Operated Repository**:
A repository where agents drive assigned execution after a human operator initiates or continues the work session.
_Avoid_: fully autonomous repository, human-absent governance

**Agentic Engineering**:
Software engineering performed agentically: code is written by AI Agents, and
the surrounding work is managed with methodical attention to how Agents
navigate tasks, fail, recover, use context, and benefit from equipment.
_Avoid_: vibe coding, Agent Engineering, Agent Meta-Engineering

**Agentic Engineering Operating Model Review**:
A structured review of the contracts and guidance under which Agents perform
engineering work, including authority, escalation, closeout gates, review
obligations, validation routing, issue and PR projection, evidence durability,
and how Agents discover, reference, and update those rules.
_Avoid_: Forge Domain Model Review, ad hoc process reminder

**Armory Equipment Core**:
The minimal Agent Equipment necessary for agents to autonomously operate Armory
functions outside the Forge. It may share equipment with the Forge Equipment
Core.
_Avoid_: Forge Equipment Core when the function is outside the Forge; Armory
Operating Contract when the surface is policy or process rather than equipment

**Armory Integrity Validation**:
The top-level live repository validation umbrella for checking current Armory
surfaces, contracts, evidence, routing, and publication-readiness invariants.
It may include Forge-scoped validation suites and other Armory-scoped suites.
_Avoid_: Seed Validation, equipment-specific behavior validation

**Armory Operating Contract**:
A durable rule surface that governs Agentic Engineering or repository
operations across the Agent Armory, rather than a specific Forge function or
Equipment Candidate.
_Avoid_: Forge Core when the rule applies across the Armory; Armory Equipment
Core when the surface is a process contract rather than Agent Equipment

**Assembly**:
A cohesive grouping of equipment designed to work together.
_Avoid_: unintegrated collection

**Assertion Provider**:
An Agent Test Jig component that evaluates an expected condition against
observed evidence and returns a structured assertion result.
_Avoid_: Learned Oracle when the provider is deterministic; test runner when
the provider only evaluates one condition

**Blueprint**:
A positive construction spec for something to be built.
_Avoid_: non-goal list when the desired construction can be stated directly

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

**Capability Profile**:
A notionally complete analysis and breakdown of a Capability Surface for a
stated scope, state, evidence basis, and intended use.
_Avoid_: summary, inventory, implementation plan

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

**Capability Surface**:
The capabilities, constraints, affordances, controls, state, and effects that
an entity, arrangement, environment, equipment item, harness, or potential
configuration can grant, alter, restrict, expose, or mediate. A Capability
Surface can describe an actual current state, past state, intended state,
potential state, realizable fixture, or hypothetical design.
_Avoid_: component list when the capability-bearing state is the point

**Change Set Documentation Closeout**:
The end-of-change documentation activity that inspects affected agent-facing and human-facing docs, updates stale or incomplete claims, and reviews the result with audience-appropriate doc-writing standards.
_Avoid_: README-only cleanup, indiscriminate doc churn, stale initial-state language

**Change Set Security Closeout**:
The end-of-change security activity that determines and performs the applicable security analyses, records findings and resolutions, and blocks merge-readiness on unresolved reportable risk.
_Avoid_: treating security review as optional cleanup, replacing analysis with a generic note

**Cognition Enhancement Equipment**:
Agent Equipment that shapes how an Agent reasons, reflects, remembers, routes
insight, right-sizes cognition, or improves its future harness behavior.
_Avoid_: prompt style when deterministic support, durable capture, policy, or
validation is the needed surface

**Config Edit Intent**:
A deliberate Agent Equipment Config source-change purpose such as propose,
patch, migrate, revise, or apply. The intent does not authorize a write by
itself.
_Avoid_: treating edit purpose as write authority

**Config Refusal State**:
The machine-visible reason a Config edit cannot write a source, such as
ineligible source category, missing authority, blocking safety status,
validation failure, secret-boundary violation, ownership-boundary violation,
or changed source precondition.
_Avoid_: treating every refusal as a validation failure

**Config Safety Status**:
The machine-visible Agent Equipment Config classification that states whether a
configuration is usable, incomplete, unsafe, stale, untrusted, or conflicted
for the requested behavior.
_Avoid_: treating schema validity alone as write safety

**Consumer Compatibility Entry**:
A reviewed record of an integration contract or output shape that new or
migrated equipment should preserve for existing consumers.
_Avoid_: Equipment Disposition, behavior ownership decision

**Cross-Boundary Coherence Ralph Review**:
A Review Until Clean gate that checks whether process outputs agree across PRD, specs, plans, implementation, validation, security, documentation, projection, and release or handoff surfaces.
_Avoid_: local-only consistency check

**Effective Harness Capability Profile**:
A Harness Capability Profile for an Effective Harness Capability Surface.
Effective Harness Profile is accepted shorthand when the harness context is
clear.
_Avoid_: Vanilla Harness Capability Profile, Agent Profile

**Effective Harness Capability Surface**:
The Harness Capability Surface for a harness in any specified state: current,
past, potential, realizable, or hypothetical. If the state is unspecified,
current state is assumed. Effective Harness Surface is accepted shorthand when
the harness context is clear.
_Avoid_: Vanilla Harness Capability Surface, base harness capability

**Effective Intent**:
The Intent actually imposed by ADRs, PRDs, specs, plans, acceptance criteria, review dispositions, and other declarative project surfaces; this is the direction the project would take if agents followed those declarations literally.
_Avoid_: assuming declarations always capture the operator's full purpose

**Efficient Coherence**:
The Agent Armory's guiding doctrine: honor the Underlying Intent, match the
rigor to the unresolved uncertainty, and minimize spend within that quality
boundary.
_Avoid_: treating economy as prior to intent alignment, or treating rigor as
ceremony rather than a response to unresolved uncertainty

**Equipment Blueprint**:
A Blueprint for Agent Equipment.
_Avoid_: downstream Smith spec when naming the current artifact shape

**Equipment Candidate**:
A proposed, specified, planned, or implemented equipment surface that has not yet been validated and published for use.
_Avoid_: Published Agent Equipment

**Equipment Capability Profile**:
A Capability Profile for an Equipment Capability Surface.
_Avoid_: capability card when the profile is about observed or analyzable
capabilities rather than intended equipment purpose

**Equipment Capability Surface**:
The Capability Surface of Agent Equipment, framed by the Agent capabilities the
equipment grants, alters, exposes, mediates, or restricts.
_Avoid_: implementation file list, installed package boundary

**Equipment Design Bundle**:
A neutral project-path bundle that gathers the design and validation-planning
artifacts for one Equipment Candidate, such as the capability card, interface
decision, security/control classification, pressure scenarios, validation plan,
closeout evidence plan, and related design records.
_Avoid_: Inventory, component implementation path, status dump

**Equipment Discovery Scope**:
A named boundary where Existing Equipment Onboarding searches for relevant
prior equipment.
_Avoid_: scanner implementation detail, implicit global search

**Equipment Disposition**:
A reviewed decision for how onboarding handles an Existing Equipment Surface or
Equipment Facet.
_Avoid_: installed state, inferred user intent, Source Material Disposition

**Equipment Evidence Entry**:
A structured evidence item that supports equipment dispositions, risk
acceptances, compatibility decisions, or derived coverage claims.
_Avoid_: free-form rationale, chat transcript, untraceable observation

**Equipment Facet**:
A separable behavior, policy, route, or integration within an Existing
Equipment Surface that can receive its own disposition.
_Avoid_: whole equipment item, source file

**Equipment Promotion Path**:
The lifecycle that moves an equipment idea from example or spec toward Published Agent Equipment.
_Avoid_: treating example, specified, planned, implemented, validated, and published as interchangeable states

**Equipment Review Record**:
A structured reviewed artifact that records equipment dispositions,
compatibility decisions, risk acceptances, unassessed areas, follow-up blockers,
and supporting evidence.
_Avoid_: active configuration, prose-only narrative, migration execution
artifact

**Existing Equipment Onboarding**:
The onboarding work that discovers Existing Equipment Surfaces, establishes
Onboarding Intent, and decides dispositions, compatibility, conflicts,
follow-ups, and activation limits before claiming coverage or replacement.
_Avoid_: automatic migration, source material extraction only

**Existing Equipment Surface**:
An equipment, component, or behavior-shaping surface present before an
onboarding workflow, whether or not it is currently used or intended to remain.
_Avoid_: installed equipment, retained equipment, legacy equipment when age or
intent is not established

**Follow-up Reminder Surface**:
A harness-dependent surface that brings unresolved follow-up candidates into
relevant agent sessions.
_Avoid_: capability report only, chat memory

**Foreign Policy Compatibility Surface**:
A kept Foreign Policy Surface that remains usable while its policy or behavior
is anchored in the Armory's preferred encoding. The compatibility mechanism may
be indirection, generation, adapter behavior, or a mixed strategy, depending on
what the foreign surface can faithfully support.
_Avoid_: Compatibility Surface when the point is specifically migrated foreign
policy; exposing mechanism-specific choices before the surface has been
classified

**Foreign Policy Surface**:
A non-Armory skill, doc, config file, hook, script, or integration that carries
policy or behavior an Armory equipment migration may discover, preserve,
ingest, discard, or leave untouched.
_Avoid_: legacy surface when the point is external origin rather than age;
treating a whole surface as indivisible when only some functions should migrate

**Forge Canon**:
The current conceptual framework and corresponding documentation that govern
Forge work.
_Avoid_: handoff docs, source notes

**Forge Conveyor**:
The preloaded agent-facing route from root `AGENTS.md` into the Forge Canon, without scouting.
_Avoid_: requiring repo-wide search, relying only on README discovery

**Forge Core**:
The materialized and enacted Forge processes, contracts, components, and
deterministic tools that implement the core features and functions of the
Forge.
_Avoid_: Forge Canon, Forge Equipment Core, Armory Operating Contract

**Forge Equipment Core**:
The minimal Agent Equipment necessary for agents to autonomously operate Forge
functions in a manner that fulfills Forge contracts.
_Avoid_: Forge Canon, Forge Core

**Forge Example**:
An annotated demonstration of the Forge's decision method using realistic but non-production equipment shapes.
_Avoid_: production package, installable equipment unless promoted through the full workflow

**Forge Integrity Validation**:
The Forge-scoped suite within Armory Integrity Validation that checks current
Forge Canon, Forge Core, Forge Equipment Core, Forge routes, Forge design
surfaces, and Forge closeout invariants.
_Avoid_: Armory-wide validation when the scope is only Forge; downstream
equipment behavior validation

**Forge Seed**:
The first coherent version of the Agent Equipment Forge, limited to canonical docs, decision method, evidence discipline, harness catalog, templates, examples, Smith task specs, and Seed Validation.
_Avoid_: Repo Ops implementation, Periodic Actions implementation

**Forge Tooling**:
Reusable fixtures, processes, validators, templates, and workflows supplied by the Forge.
_Avoid_: one-off Smith workaround

**Forge Tour**:
The Forge's exclusively human-facing documentation set, starting in this repo with `docs/forge-tour.md`.
_Avoid_: treating the root README link to the Tour as a special named surface; maintainer process dump; agent policy surface

**Forgewright**:
An Agent that creates or refines the Agent Equipment Forge.
_Avoid_: architect agent, Forge author

**Forgewright Hand-Back**:
The return note a Forgewright gives a Smith after resolving or deferring a Tooling Gap.
_Avoid_: chat-only conclusion, undocumented resume instruction

**Forgewright Runbook**:
A concise canonical workflow for Agents that maintain the Agent Equipment Forge.
_Avoid_: storing every project plan, review transcript, or implementation checklist there

**Fork Ops**:
A planned Repo Ops add-on for fork-specific operations, including upstream,
downstream, divergence, sync, publication, and selective-upstreaming behavior.
_Avoid_: treating it as a replacement for Repo Ops, treating current
non-Forge-built Fork Ops source material as published Armory equipment

**Harness Capability Catalog**:
The human-facing front door and collection boundary for Vanilla Harness
Capability Profiles, sources, limitations, and refresh requirements.
_Avoid_: source map, research notes

**Harness Capability Profile**:
A Capability Profile for a Harness Capability Surface.
_Avoid_: Agent Profile, Harness Plugin, equipment projection guidance

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

**Harness Capability Refresh**:
Future recurring Agent Equipment for invoking the Harness Capability Profile
Manager and keeping Vanilla Harness Capability Profiles current over time.
_Avoid_: one-time Harness Fact Refresh

**Harness Capability Surface**:
The Capability Surface of an Agent Harness in a stated state, including the
capabilities granted, altered, exposed, mediated, or restricted by the harness
and by the settings, equipment, plugins, profiles, tools, hooks, config, local
state, or other capabilities present in that state.
_Avoid_: Vanilla Harness Capability Surface when a non-default state is meant

**Harness Component**:
Reusable behavior integrated into an Agent Harness.
_Avoid_: plugin part unless the package boundary matters

**Harness Evidence Source Policy**:
The rule that Harness Capability Profile claims prefer first-party sources, use
third-party metadata only as labeled fallback, and record local CLI
observations separately.
_Avoid_: unlabeled source mixing, stale memory-backed harness claims

**Harness Fact Refresh**:
A source-backed update to Vanilla Harness Capability Profile claims when
harness versions or affordances may have changed.
_Avoid_: casual web lookup, stale handoff copy

**Harness Plugin**:
A portable collection of Harness Components.
_Avoid_: plugin when referring to an individual skill, hook, or profile

**Harness Test Suite**:
A set of Agent Test Jig plans used to validate Capability Surface claims for
one or more Agent Harnesses.
_Avoid_: Agent Test Jig, Capability Profiling Protocol, generic test suite

**Head Gear**:
The planned name for the Armory's generic Cognition Enhancement Equipment for
translating underspecified but realizable operator intent into high-quality
outcomes by inducing reflection, imagination, questioning, bookkeeping,
knowledge retrieval, capability prediction, and self-outfitting.
_Avoid_: domain-specific equipment, style-only prompting, one-off instruction
to think harder

**Initiative Authority**:
The human operator's reserved authority to choose project initiatives and start or continue work sessions.
_Avoid_: implementation authority, routine closeout authority

**Intent**:
A direction that an intent-capable actor, declaration, specification, tool, or workflow imposes or attempts to impose. Intent is usually goal-oriented, or at least directionally so.
_Avoid_: treating intent as only stakeholder purpose or only written specification

**Intent Alignment Check**:
A Story Quality check that compares Effective Intent with the refreshed model of Underlying Intent after Cross-Boundary Coherence has made Effective Intent legible. Refresh the model again if closeout evidence introduced new intent signals.
_Avoid_: silent reinterpretation, mind-reading, unexamined literalism

**Intent Model Refresh**:
The first Story Closeout gate, where the agent updates its evidence-backed model of Underlying Intent from current operator input, accepted decisions, review dispositions, handoffs, and observed corrections before running downstream closeout gates.
_Avoid_: validating against stale assumptions

**Inventory**:
An index or catalog of available, candidate, or planned equipment.
_Avoid_: treating every docs list as Inventory

**Issue Brief Status**:
The issue-tracker indication of whether the issue has the agent or human brief
needed for safe delegation.
_Avoid_: readiness state by itself; brief status supports readiness but does
not replace it

**Issue Category Role**:
The coarse triage classification that distinguishes `bug` from `enhancement`.
Every triaged issue should carry exactly one Issue Category Role.
_Avoid_: work kind, readiness state, priority, implementation surface

**Issue Dependency Disposition**:
The issue-tracker indication of how dependency state affects issue selection:
unblocked, blocked, unknown, or needing tracker-record repair.
_Avoid_: native dependency relation by itself; disposition records the current
selection effect of dependency knowledge

**Issue Engagement Mode**:
The next expected handling shape for an issue, such as AFK implementation,
agent-led grill, human decision, linked-context triage, or deep issue session.
_Avoid_: triage state, category, priority

**Issue Ops**:
Accepted shorthand for Issue Tracker Ops after the full name is clear in the
current context.
_Avoid_: using it as a separate equipment name

**Issue Projection**:
The post-review step that creates or updates a Published PRD Issue from a stable Repo Draft PRD.
_Avoid_: issue churn during draft review, untracked divergence

**Issue State Role**:
The mutually exclusive triage state that records whether an issue still needs
triage, needs specific outside information, is ready for an AFK agent, is ready
for human handling, or should not be actioned.
_Avoid_: dependency state, triage depth, priority, engagement mode, work kind

**Issue Tracker Baseline**:
The current GitHub Issues-only baseline for Issue Tracker Ops. Labels represent
custom predicates, and out-of-band policy imposes structure on those
predicates until richer tracker or GitHub Projects support is designed,
implemented, validated, and dogfooded.
_Avoid_: treating labels as the best long-term UX, or treating GitHub Projects
custom fields as already adopted policy

**Issue Tracker Ops**:
Agent Equipment for recording, reviewing, repairing, enriching, organizing,
assigning, working, and orchestrating issue-tracked follow-ups directly in an
issue tracker.
_Avoid_: Issue Projection when the work is broader than PRD publication;
in-tree tracking state when the issue tracker is available

**Issue Triage Record**:
A concise issue comment that records the evidence boundary, reasoning,
unresolved factors, applied or recommended labels, and next action behind a
triage outcome.
_Avoid_: labels as rationale, rewriting issue bodies for transient reasoning,
copying large private or instance-scoped evidence into public tracker comments

**Issue Work Kind**:
The orthogonal description of what kind of work an issue requires, such as
research, design, documentation, implementation, epic, cleanup, or Reflection
Finding.
_Avoid_: Issue Category Role, triage state

**Jig Adequacy Report**:
A Capability Profiling Protocol report for a clean-room profiling jig that
classifies controls as claimed, verified, unsupported, or unknown and records
how those controls affect selected rigor.
_Avoid_: assuming a clean-room jig is fully adequate without control evidence

**Jig Driver**:
The registered backend for an Agent Test Jig that owns environment lifecycle,
effect controls, execution, observation, capture, and teardown.
_Avoid_: Jig Runner, Agent Harness

**Jig Runner**:
The orchestrator that loads Agent Test Jig plans, selects a Jig Driver,
executes scenarios, invokes Assertion Providers, and emits structured results.
_Avoid_: Jig Driver, Assertion Provider

**Jig Test Plan**:
A machine-readable plan that tells a Jig Runner what target to exercise, which
driver constraints apply, which scenarios run, and which assertions evaluate
the observed result.
_Avoid_: Study Plan when the artifact is executable jig input rather than
Capability Profiling Protocol planning evidence

**Layer Precedence**:
The normal Agent Equipment Config merge order that decides which configuration
value would win when no policy lock blocks it.
_Avoid_: policy authority, when the point is the value merge order

**Learned Oracle**:
An inference-backed Assertion Provider whose structured result can be pass,
fail, inconclusive, disagreement, or oracle error.
_Avoid_: deterministic assertion, final arbiter, truth source

**Loadout**:
The selected equipment set for a role, task, session, Agent, or agentic system.
_Avoid_: Inventory, Assembly

**Manual Refresh Analysis Report**:
A normalized, noncanonical refresh artifact that compares a Manual Refresh
Scout Report with current Vanilla Harness Capability Profiles, prior evidence
basis, schema pressure, version deltas, similar claims, and Capability Claim
Triage.
_Avoid_: mutation plan, profile rewrite

**Manual Refresh Audit Summary**:
A refresh closeout artifact that records checked sources, planned and changed
profile files, claim dispositions, schema pressure, selected-rigor deviations,
scratch evidence disposition, apply result, validation results, and follow-up
disposition.
_Avoid_: raw transcript, hidden local cache

**Manual Refresh Scout Report**:
A normalized, noncanonical refresh artifact that records curated source
evidence, fallback evidence, local observations, selected study reports,
evidence notes, hypotheses, unknowns, effect classification, and scratch
disposition for one harness.
_Avoid_: canonical profile mutation, raw cache dump

**Manual Refresh Update Plan**:
A reviewable refresh artifact that records explicit canonical profile or schema
mutations, precondition hashes, planned content hashes, validation commands,
evidence promotions, and follow-up issue candidates.
_Avoid_: scout cache, implicit profile edit

**Onboarding Intent**:
The operator's session-level direction for equipment onboarding before
individual surfaces and facets receive detailed dispositions.
_Avoid_: installed state, per-facet disposition, inferred final decision

**Operational Continuity**:
A state where a capability can keep operating safely because target Agent
Equipment is active or a verified retained owner remains authoritative.
_Avoid_: Replacement Coverage, migration completion

**Operator**:
An intent-capable actor that initiates, routes, controls, or evaluates Agent
work. An Operator may be a human or an orchestrator-agent.
_Avoid_: assuming every Operator is human; use human operator or stakeholder
when human authority specifically matters

**Outfitter**:
An Agent that selects and assembles Agent Equipment from the Agent Armory into a Loadout for a role, task, session, Agent, or agentic system.
_Avoid_: Smith, Forgewright, Equipment creator

**Per-Harness Clean-Room Jig**:
The harness-specific clean-room profiling environment and Capability Surface
that records how closely one Agent Harness can approach the Standard
Clean-Room Profiling Jig and where it falls short.
_Avoid_: treating a harness-limited jig as the ideal baseline

**Periodic Actions**:
Future Agent Equipment for defining, installing, inspecting, and uninstalling recurring agent actions across harnesses.
_Avoid_: treating it as implemented by the Forge Seed

**Policy Authority**:
The right of a configuration layer to constrain later overrides or
lower-authority layers by marking a setting non-overridable or requiring a
mutation gate.
_Avoid_: layer precedence, when the point is who may constrain later overrides

**Pressure Scenario Validation**:
A skill-validation method that tests whether an Agent follows a proposed skill under realistic task pressure, including evidence of baseline failure or gap and post-skill compliance.
_Avoid_: informal read-through, author confidence

**Published Agent Equipment**:
Agent Equipment that has completed the promotion path and is intended to be equipped.
_Avoid_: example, draft, candidate

**Published PRD Issue**:
A GitHub issue that tracks an accepted PRD after repo-draft review.
_Avoid_: letting it drift from the Repo Draft PRD without an explicit projection note

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

**Replacement Coverage**:
A state where target Agent Equipment owns active behavior equivalent to a prior
Existing Equipment Surface or Equipment Facet for a declared scope.
_Avoid_: Operational Continuity, redirected retained-owner behavior

**Repo Draft PRD**:
A worktree-authored PRD used for review and refinement before projection into the issue tracker.
_Avoid_: treating the draft as the final issue-tracker record

**Repo Ops**:
Future Agent Equipment for operating repositories agentically. Repo Ops is
complete for repositories that are not forks and provides the extension base
for fork-specific operations.
_Avoid_: treating it as implemented by the Forge Seed, forcing fork-specific
behavior into non-fork repos

**Repository Threat Model**:
A repository-scoped security model that records assets, trust boundaries, attacker-controlled inputs, assumptions, invariants, and high-impact failure modes for future scans.
_Avoid_: target-specific finding list, one-off scan report

**Review Until Clean**:
A repeated review-and-revision loop that stops only when the latest review cycle has no findings.
_Avoid_: assuming any named external review skill is repo policy unless the operator invokes it or repo policy names it

**Seed Surface**:
A file or directory implemented during the Forge Seed because it had a clear
seed role.
_Avoid_: placeholder directories without seed responsibilities

**Seed Validation**:
Historical runnable checks that verified the Forge Seed's own repository shape,
documentation links, provenance, accepted-handoff projection or explicit
deferment, and structured catalog fields.
_Avoid_: Armory Integrity Validation, Forge Integrity Validation, harness integration validation, production equipment validation

**Seed Validation Tool**:
A historical standard-library Python script shape for completed Forge Seed
checks. Current live checks run through Armory Integrity Validation tooling.
_Avoid_: package-manager-dependent validator, harness-specific validator

**Shadow Mode**:
A mode where target Agent Equipment runs beside a retained authoritative owner
for comparison or confidence-building.
_Avoid_: Replacement Coverage, Advisory Mode

**Skill Template**:
A seed artifact that shows how Smiths should shape future skills without itself being equipped as a skill.
_Avoid_: repo-local skill, production skill

**Smith**:
An Agent that creates Agent Equipment using the Agent Equipment Forge.
_Avoid_: implementer when the role includes equipment design

**Smith-to-Forgewright Handoff**:
The context package a Smith gives to a Forgewright for Tooling Request.
_Avoid_: vague note, unstructured context dump

**Source Disposition Ledger**:
A durable, self-contained closeout surface that records source-handoff coverage, retained claim summaries, operator dispositions, and source-retirement evidence after raw source handoff materials are retired.
_Avoid_: raw source archive, implicit coverage, unverifiable handoff completeness

**Source Handoff**:
Preserved upstream material accepted as provenance for Forge design, not the live Forge surface.
_Avoid_: canonical docs, final docs

**Standard Clean-Room Profiling Jig**:
The ideal preferred baseline study environment and Capability Surface for
official Vanilla Harness Capability Profiles, designed to maximize control over
harness state, equipment, configuration, isolation, reproducibility, permitted
effects, and evidence quality within the limits of each harness.
_Avoid_: assuming every harness can expose the same controls

**Story Closeout**:
The story-level activity that assembles validation, security, documentation, review, projection, and handoff evidence before a story is treated as complete.
_Avoid_: treating one clean subprocess as proof that the whole story is complete

**Story Quality Ralph Review**:
A Review Until Clean gate that checks holistic quality after coherence is established, including DX, UX, architecture, robustness, strategic alignment, and lessons from prior development or operations failures.
_Avoid_: style-only review, generic correctness pass

**Strapped**:
Mediated by an Agent Harness.
_Avoid_: installed, configured, running when the harness relationship is the point

**Study Plan**:
A pre-execution Capability Profiling Protocol artifact that records the study
target, Capability State Graph, Capability Analysis Angles, rigor controls,
permitted effects, approvals, observation points, and sufficiency criteria.
_Avoid_: study report, profile mutation plan

**Study Report**:
A post-execution Capability Profiling Protocol artifact that records observed
results, claim confidence, test sufficiency, limitations, failed controls,
artifact disposition, and profile impact.
_Avoid_: raw transcript, unreviewed scratch output

**Study Target Declaration**:
The machine-readable declaration of the Capability Surface target, scope,
state or Capability State Graph, claims under study, required evidence,
available controls, operator preferences, permitted effects, and selected
rigor for a Capability Profiling Protocol study.
_Avoid_: study result, profile claim

**Target Structure**:
A planned repository shape used to reason about Forge surfaces before all of those surfaces exist.
_Avoid_: treating the target as an unconditional directory mandate

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

**Triage Depth**:
The evidence boundary that supports the current issue-triage recommendation,
from semantic hygiene through deep issue-session analysis.
_Avoid_: readiness state, work kind, priority

**Unassessed Equipment Area**:
A discovery scope, equipment group, or capability overlap not scanned or
classified enough to support activation, continuity, or coverage claims.
_Avoid_: warning-only note, scan success, hidden risk acceptance

**Underlying Intent**:
The stakeholder's actual current Intent: the direction they would want the project to move if a mismatch were brought to their attention. An agent does not directly know a stakeholder's or other intent-capable actor's Underlying Intent; it maintains an evidence-backed model that can be tested through questions, experiments, and observed corrections.
_Avoid_: confusing the agent's model of intent with the intent itself

**User Follow-up Registry**:
A user-scoped durable home for user-specific follow-up candidates across Agent
Equipment.
_Avoid_: team issue tracker, repo issue tracker, equipment-specific follow-up
store

**Vanilla Harness Capability Profile**:
A Harness Capability Profile for a Vanilla Harness Capability Surface. Vanilla
Harness Profile is accepted shorthand when the harness context is clear.
_Avoid_: Agent Profile, Effective Harness Capability Profile

**Vanilla Harness Capability Surface**:
The Harness Capability Surface for a harness immediately after installation and
onboarding, with default settings and default equipment. Vanilla Harness
Surface is accepted shorthand when the harness context is clear.
_Avoid_: Effective Harness Capability Surface, configured local harness state

**Wielder**:
An Agent outfitted with a Loadout and actively using that Agent Equipment to perform work.
_Avoid_: Outfitter, Loadout, Agent Profile

## Relationships

- The **Agent Armory** contains **Agent Equipment** and the **Agent Equipment Forge**.
- **Agentic Engineering** is software engineering performed agentically, while
  **Agent Engineering** is the engineering of Agents and agentic systems.
- **Agent Meta-Engineering** is Agent Engineering focused on engineering work;
  it can produce the Agents, workflows, operating models, and **Agent
  Equipment** that improve **Agentic Engineering**.
- The **Agent Equipment Forge** is created by **Forgewrights** and used by **Smiths**.
- **Smiths** create **Agent Equipment** for one or more **Agent Harnesses**.
- An **Equipment Design Bundle** gathers the early design and
  validation-planning surfaces for one **Equipment Candidate** before the
  interface decision projects implemented components into their chosen paths.
- **Outfitters** select **Agent Equipment** from the Armory and assemble
  **Loadouts**.
- **Wielders** use **Loadouts** to perform work.
- **Equipment Candidates** may become **Published Agent Equipment** after validation and publication.
- **Existing Equipment Onboarding** evaluates **Existing Equipment Surfaces**
  through named **Equipment Discovery Scopes** before making activation,
  continuity, or coverage claims.
- An **Existing Equipment Surface** can contain multiple **Equipment Facets**;
  **Equipment Dispositions** attach to the surface or facet that actually owns
  the behavior being reviewed.
- An **Equipment Review Record** stores **Equipment Evidence Entries**,
  **Equipment Dispositions**, **Consumer Compatibility Entries**, unassessed
  areas, risk acceptances, and follow-up blocker relationships.
- **Replacement Coverage** requires target **Agent Equipment** to own the
  active behavior; **Operational Continuity** can also come from a verified
  retained owner.
- **Shadow Mode** and **Advisory Mode** can support migration confidence, but
  neither establishes **Replacement Coverage** by itself.
- Team-wide follow-ups belong in the issue tracker when available; user-specific
  follow-ups belong in a **User Follow-up Registry** and may surface through a
  **Follow-up Reminder Surface**.
- An **Agent** is **Strapped** when its reasoning and actions are mediated by an **Agent Harness**.
- **Operators** initiate, route, control, or evaluate **Agent** work; human
  authority should be named explicitly when the distinction matters.
- A **Harness Plugin** packages one or more **Harness Components**.
- An **Agent Profile** configures a reusable kind of **Agent** but is not the running **Agent**.
- An **Agent Test Jig** uses a **Jig Runner** and **Jig Driver** to execute a
  **Jig Test Plan**; a **Harness Test Suite** groups plans for Harness
  Capability claims.
- **Assertion Providers** evaluate observed evidence. **Learned Oracles** are
  inference-backed Assertion Providers and do not replace deterministic
  assertions when deterministic checks can decide the condition.
- A **Source Handoff** can inform **Forge Canon**, but it is not itself the live Forge surface.
- The **Forge Seed** specifies future **Agent Equipment** but does not implement that downstream equipment.
- **Seed Validation** checks the completed **Forge Seed**; live repository
  integrity belongs to **Armory Integrity Validation** and Forge-scoped live
  integrity belongs to **Forge Integrity Validation**.
- The **Harness Capability Catalog** is a **Forge Canon** front door backed by
  validated **Vanilla Harness Capability Profiles** and maintained through the
  **Harness Capability Profile Manager**.
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
- Manual refresh moves through **Manual Refresh Scout Report**, **Manual
  Refresh Analysis Report**, **Manual Refresh Update Plan**, explicit apply,
  and **Manual Refresh Audit Summary** artifacts so deterministic Manager Core
  operations stay separate from agent-guided judgment.
- The **Capability Profiling Protocol** produces **Study Plans** before
  execution and **Study Reports** after execution; **Jig Adequacy Reports** use
  the same protocol vocabulary because clean-room jigs are **Capability
  Surfaces**.
- A **Forge Example** demonstrates how a **Smith** applies the **Agent Equipment Forge** but is not automatically **Agent Equipment**.
- **Repo Ops**, **Periodic Actions**, and **Harness Capability Refresh** are downstream **Agent Equipment** specified by the **Forge Seed**.
- **Fork Ops** is planned as a **Repo Ops** add-on after Repo Ops and its
  prerequisites are ready for intake.
- Portable Agentic Engineering workflow equipment is downstream of repo-local
  **Armory Operating Contracts** until the rules are coherent and
  pressure-tested enough to package.
- In an **Agent-Operated Repository**, **Initiative Authority** stays with the human operator while agents drive assigned execution.
- A **Repo Draft PRD** can become the source for a **Published PRD Issue** after review.
- A **Published PRD Issue** is the tracking surface; material repo-draft changes need explicit issue re-projection.
- **Issue Projection** happens after repo-draft review; closeout records either the issue update or the reason projection remains pending.
- **Reflection Findings** are source material for future **Cognition Enhancement Equipment** and may also induce **Tooling Requests**, **Equipment Candidates**, or issue-tracked work in narrower equipment stories.
- **Head Gear** is the planned generic **Cognition Enhancement Equipment** line;
  it is intended to prepare the Agent to clarify, equip, execute, and reflect
  before domain-specific equipment takes over.
- **Efficient Coherence** guides Armory strategy: preserve **Underlying Intent**
  and quality first, choose rigor according to unresolved uncertainty, then
  minimize spend within that quality boundary.
- A **Forgewright Runbook** guides Forge maintenance without replacing ADRs, PRDs, implementation plans, or Smith runbooks.
- A **Target Structure** can guide a PRD, but the **Forge Seed** creates only **Seed Surfaces**.
- Historical **Seed Validation** used a standard-library tool without
  runtime dependencies. Current live validation tooling belongs under **Armory
  Integrity Validation** and its scoped validation suites.
- **Armory Operating Contracts** state cross-Armory operating rules in readable
  form; deterministic validators enforce selected machine-checkable slices of
  those rules.
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
- **Story Closeout** is an **Armory Operating Contract** because it governs
  cohesive change sets across the Armory rather than a specific Forge function.
- **Intent Model Refresh** is the first **Story Closeout** gate so every downstream closeout check uses the current model of **Underlying Intent**.
- **Cross-Boundary Coherence Ralph Review** precedes **Story Quality Ralph Review** because quality review depends on coherent process evidence.
- A **Story Quality Ralph Review** includes an **Intent Alignment Check** that compares **Effective Intent** with the refreshed model of **Underlying Intent** before final Story Closeout.
- A **Tooling Request** turns an unsatisfied Forge Tooling need into a task dependency, moves Tooling Work to a **Forgewright**, and returns a **Forgewright Hand-Back** that lets the **Smith** resume safely.

## Precision rules

- Use **Agent** for the running causal stream, not for a reusable harness
  declaration.
- Use **Agent Profile** for a reusable identity, mission, tool, permission, or
  model configuration. Use `agents/` for source paths when following
  harness/plugin convention.
- Use **Agent Harness** for the runtime or orchestration system that mediates
  the Agent.
- Use **Vanilla Harness Capability Profile** for the default post-installation
  and onboarding harness profile. Use **Effective Harness Capability Profile**
  for a current, potential, realizable, hypothetical, or otherwise specified
  configured harness state.
- Use **Agent Equipment** for reusable capability; use **Equipment Candidate**
  until validation and publication are complete.
- Use **Equipment Design Bundle** for early design and validation-planning
  records, not for an Inventory or implemented component path.
- Use **Published Agent Equipment** only after the promotion path reaches
  `published`.
- Use **Outfitter** for equipment selection and Loadout assembly, not for
  Equipment creation.
- Use **Wielder** for the equipped Agent using a Loadout, not for the Loadout
  itself.
- Use **Source Handoff** for source material before disposition and **Source
  Disposition Ledger** for durable coverage after raw source retirement.
- Use **Forge Canon** for current guidance.
- Use **Forge Seed** for the first Forge pass; name downstream equipment
  separately.
- Use **Harness Fact Refresh** for source-backed profile updates and **Harness
  Capability Refresh** for the downstream recurring equipment that invokes the
  profile manager over time.
- Use **Manual Refresh Scout Report**, **Manual Refresh Analysis Report**,
  **Manual Refresh Update Plan**, and **Manual Refresh Audit Summary** for the
  staged manual workflow artifacts; use **Harness Capability Refresh** for the
  deferred recurring equipment.
- Use **Study Plan** for intended protocol shape before execution and **Study
  Report** for observed outcomes after execution.
- Use **Jig Adequacy Report** when the target under study is the control
  adequacy of a clean-room profiling jig.
- Use **Agent Test Jig** for the controlled test mechanism, **Jig Runner** for
  orchestration, **Jig Driver** for the environment backend, and **Harness Test
  Suite** for a grouped set of jig plans validating Harness Capability claims.
- Use **Issue Tracker Ops** for broad issue lifecycle equipment; use **Issue
  Projection** only for post-review PRD publication into the issue tracker.
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
- Use **Efficient Coherence** for quality-bound efficiency: preserve
  Underlying Intent, match rigor to unresolved uncertainty, and minimize spend
  only inside that quality boundary.

## Example dialogue

> **Smith:** "Should this repeated repo maintenance behavior become one skill?"
> **Forgewright:** "Put the active judgment and procedure in a skill. Keep deterministic checks in scripts, hard policy in hooks, and durable project truth in Forge Canon. Preserve the Source Handoff as provenance, but project the decision into the Forge surface Smiths will actually use."

## Flagged ambiguities

- "Agentic Engineering" can mean software engineering performed by Agents or
  engineering work done on Agents. Resolution: use **Agentic Engineering** for
  software engineering performed agentically, **Agent Engineering** for
  engineering Agents and agentic systems, and **Agent Meta-Engineering** for
  engineering the agentic systems that perform or improve engineering work.
- "Agent" can mean the running causal stream or a reusable harness declaration. Resolution: use **Agent** for the running stream and **Agent Profile** for the reusable declaration.
- "Handoff docs" can mean accepted source material or current project docs. Resolution: use **Source Handoff** for provenance and **Forge Canon** for the live Forge surface.
- "Tooling Work" can mean seeding the **Agent Equipment Forge** or implementing downstream equipment. Resolution: use **Forge Seed** for the first pass and name downstream equipment, such as Repo Ops or Periodic Actions, separately.
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
- "Existing equipment" can mean prior surfaces, currently used equipment,
  retained authority, or foreign policy material. Resolution: use **Existing
  Equipment Surface** for prior equipment presence, **Equipment Disposition**
  for the reviewed decision, **Operational Continuity** for safe ongoing
  operation, **Replacement Coverage** for target-equipment ownership, and
  **Foreign Policy Surface** only when the prior surface is external to the
  Armory's preferred equipment model.
- "PRD tracking" can mean worktree drafting or issue-tracker publication. Resolution: use **Repo Draft PRD** for reviewable drafts, **Published PRD Issue** for tracking, and re-project material draft changes into the issue.
- "Issue projection" can mean publication timing or synchronization mechanics. Resolution: use **Issue Projection** for post-review publication and closeout synchronization.
- "Reflection" can mean private thinking, a closeout habit, a durable finding, or future equipment. Resolution: use **Reflection Finding** when the output should be tracked, and **Cognition Enhancement Equipment** when the capability itself is being engineered.
- "Forgewright guidance" can mean durable workflow or a specific plan. Resolution: use the **Forgewright Runbook** for repeatable maintenance duties and keep project-specific steps in PRDs, plans, and ADRs.
- "Review until clean" can mean a general quality gate or a named imported skill. Resolution: use **Review Until Clean** for the repo concept and invoke named review skills only when requested or adopted by repo policy.
- "Repository structure" can mean an intended architecture or files to create now. Resolution: use **Target Structure** for the PRD-level architecture and **Seed Surface** for files created in the Forge Seed.
- "Validation tooling" can mean live integrity checks, historical seed checks,
  or harness behavior tests. Resolution: use live **Armory Integrity
  Validation** and **Forge Integrity Validation** tooling for current integrity
  checks, reserve **Seed Validation** for historical seed scope, and leave
  harness behavior tests to downstream equipment.
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
