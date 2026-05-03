# Agent Armory

Agent Armory defines a shared language for creating, cataloging, and maintaining reusable equipment for agents. This context keeps domain terms stable while the framework is designed and refined.

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

**Published Agent Equipment**:
Agent Equipment that has completed the promotion path and is intended to be equipped.
_Avoid_: example, draft, candidate

**Agent Equipment Framework**:
The Armory's method and supporting artifacts for helping Smiths create Agent Equipment.
_Avoid_: the framework when the referent is unclear

**Metasmith**:
An Agent that creates or refines the Agent Equipment Framework.
_Avoid_: architect agent, framework author

**Smith**:
An Agent that creates Agent Equipment using the Agent Equipment Framework.
_Avoid_: implementer when the role includes equipment design

**Agent**:
The causal stream of reasoning, actions, tool calls, messages, and content mediated by an Agent Harness.
_Avoid_: bot, model, profile when precision matters

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
Preserved upstream material accepted as provenance for framework design, not the live framework surface.
_Avoid_: canonical docs, final docs

**Canonical Framework Docs**:
The current live documentation, templates, examples, and specs that Smiths use as the Framework.
_Avoid_: handoff docs, source notes

**Framework Seed**:
The first coherent version of the Agent Equipment Framework, limited to canonical docs, decision method, evidence discipline, harness catalog, templates, examples, Smith task specs, and Seed Validation.
_Avoid_: Agent Ops implementation, Periodic Actions implementation

**Seed Validation**:
Minimal runnable checks that verify the Framework Seed's own repository shape, documentation links, provenance, accepted-handoff projection or explicit deferment, and structured catalog fields.
_Avoid_: harness integration validation, production equipment validation

**Harness Capability Catalog**:
The canonical versioned record of Agent Harness affordances, limitations, sources, and refresh requirements.
_Avoid_: source map, research notes

**Harness Fact Refresh**:
A source-backed update to the Harness Capability Catalog when harness versions or affordances may have changed.
_Avoid_: casual web lookup, stale handoff copy

**Framework Example**:
An annotated demonstration of the Framework's decision method using realistic but non-production equipment shapes.
_Avoid_: production package, installable equipment unless promoted through the full workflow

**Agent Ops**:
Future Agent Equipment for operating repositories agentically.
_Avoid_: treating it as implemented by the Framework Seed

**Agent-Operated Repository**:
A repository where agents drive assigned execution after a human operator initiates or continues the work session.
_Avoid_: fully autonomous repository, human-absent governance

**Initiative Authority**:
The human operator's reserved authority to choose project initiatives and start or continue work sessions.
_Avoid_: implementation authority, routine closeout authority

**Periodic Actions**:
Future Agent Equipment for defining, installing, inspecting, and uninstalling recurring agent actions across harnesses.
_Avoid_: treating it as implemented by the Framework Seed

**Harness Capability Refresh**:
Future Agent Equipment for maintaining the Harness Capability Catalog over time.
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

**Review Until Clean**:
A repeated review-and-revision loop that stops only when the latest review cycle has no findings.
_Avoid_: assuming any named external review skill is repo policy unless the operator invokes it or repo policy names it

**Metasmith Runbook**:
A concise canonical workflow for Agents that maintain the Agent Equipment Framework.
_Avoid_: storing every project plan, review transcript, or implementation checklist there

**Target Structure**:
A planned repository shape used to reason about Framework surfaces before all of those surfaces exist.
_Avoid_: treating the target as an unconditional directory mandate

**Seed Surface**:
A file or directory implemented during the Framework Seed because it has a clear current role.
_Avoid_: placeholder directories without seed responsibilities

**Seed Validation Tool**:
A standard-library Python script that runs Seed Validation and reports results for humans or agents.
_Avoid_: package-manager-dependent validator, harness-specific validator

**Harness Evidence Source Policy**:
The rule that Harness Capability Catalog claims prefer first-party sources, use third-party metadata only as labeled fallback, and record local CLI observations separately.
_Avoid_: unlabeled source mixing, stale memory-backed harness claims

**Equipment Promotion Path**:
The lifecycle that moves an equipment idea from example or spec toward published Agent Equipment.
_Avoid_: treating example, specified, planned, implemented, validated, and published as interchangeable states

**Pressure Scenario Validation**:
A skill-validation method that tests whether an Agent follows a proposed skill under realistic task pressure, including evidence of baseline failure or gap and post-skill compliance.
_Avoid_: informal read-through, author confidence

**Skill Template**:
A seed artifact that shows how Smiths should shape future skills without itself being equipped as a skill.
_Avoid_: repo-local skill, production skill

**Preloaded Framework Path**:
The canonical Framework routing that a Smith receives from preloaded root `AGENTS.md`, without scouting.
_Avoid_: requiring repo-wide search, relying only on README discovery

**Human Framework Entry**:
A concise README entry point that explains the Framework and links humans to the canonical starting path without exposing agent-only machinery.
_Avoid_: maintainer process dump, agent policy surface

**Source Projection Register**:
A canonical map that records each accepted Source Handoff requirement and where it was projected or why it was deferred.
_Avoid_: implicit coverage, unverifiable handoff completeness

## Relationships

- The **Agent Armory** contains **Agent Equipment** and the **Agent Equipment Framework**.
- The **Agent Equipment Framework** is created by **Metasmiths** and used by **Smiths**.
- **Smiths** create **Agent Equipment** for one or more **Agent Harnesses**.
- **Equipment Candidates** may become **Published Agent Equipment** after validation and publication.
- An **Agent** is **Strapped** when its reasoning and actions are mediated by an **Agent Harness**.
- A **Harness Plugin** packages one or more **Harness Components**.
- An **Agent Profile** configures a reusable kind of **Agent** but is not the running **Agent**.
- A **Source Handoff** can inform **Canonical Framework Docs**, but it is not itself the live Framework surface.
- The **Framework Seed** specifies future **Agent Equipment** but does not implement that downstream equipment.
- **Seed Validation** checks the **Framework Seed**; downstream equipment needs its own validation.
- The **Harness Capability Catalog** is a **Canonical Framework Docs** surface informed by the **Source Handoff** and by **Harness Fact Refresh**.
- A **Framework Example** demonstrates how a **Smith** applies the **Agent Equipment Framework** but is not automatically **Agent Equipment**.
- **Agent Ops**, **Periodic Actions**, and **Harness Capability Refresh** are downstream **Agent Equipment** specified by the **Framework Seed**.
- In an **Agent-Operated Repository**, **Initiative Authority** stays with the human operator while agents drive assigned execution.
- A **Repo Draft PRD** can become the source for a **Published PRD Issue** after review.
- A **Published PRD Issue** is the tracking surface; material repo-draft changes need explicit issue re-projection.
- **Issue Projection** happens after repo-draft review; closeout records either the issue update or the reason projection remains pending.
- A **Metasmith Runbook** guides Framework maintenance without replacing ADRs, PRDs, implementation plans, or Smith runbooks.
- A **Target Structure** can guide a PRD, but the **Framework Seed** creates only **Seed Surfaces**.
- A **Seed Validation Tool** implements **Seed Validation** without adding runtime dependencies.
- A **Harness Fact Refresh** follows the **Harness Evidence Source Policy** before updating the **Harness Capability Catalog**.
- The **Equipment Promotion Path** distinguishes **Framework Examples**, **Equipment Candidates**, validation, and **Published Agent Equipment**.
- **Seed Validation** may check promotion-state labels for seed surfaces, but downstream equipment behavior needs equipment-specific validation.
- A **Skill Template** can guide future skill creation but is not **Published Agent Equipment**.
- A repo-local skill needs **Pressure Scenario Validation** before promotion to **Published Agent Equipment**.
- The **Framework Seed** should expose a **Preloaded Framework Path** for Smiths and a **Human Framework Entry** for readers.
- **Seed Validation** checks the **Source Projection Register** so accepted Source Handoff requirements are auditable.

## Example dialogue

> **Smith:** "Should this repeated repo maintenance behavior become one skill?"
> **Metasmith:** "Put the active judgment and procedure in a skill. Keep deterministic checks in scripts, hard policy in hooks, and durable project truth in Canonical Framework Docs. Preserve the Source Handoff as provenance, but project the decision into the Framework surface Smiths will actually use."

## Flagged ambiguities

- "Agent" can mean the running causal stream or a reusable harness declaration. Resolution: use **Agent** for the running stream and **Agent Profile** for the reusable declaration.
- "Handoff docs" can mean accepted source material or current project docs. Resolution: use **Source Handoff** for provenance and **Canonical Framework Docs** for the live Framework surface.
- "Framework work" can mean seeding the **Agent Equipment Framework** or implementing downstream equipment. Resolution: use **Framework Seed** for the first pass and name downstream equipment, such as Agent Ops or Periodic Actions, separately.
- "Agent-operated" can mean guided autonomous execution or unsupervised initiative selection. Resolution: **Initiative Authority** remains human, while agents drive assigned work inside active sessions.
- "Validation" can mean checking repository/framework integrity or proving harness-specific behavior. Resolution: use **Seed Validation** for the first kind and name the harness or equipment validation separately.
- "Catalog refresh" can mean a one-time seed update or the downstream recurring equipment. Resolution: use **Harness Fact Refresh** for source-backed catalog updates and **Harness Capability Refresh** for the downstream Smith task.
- "Example" can mean a teaching artifact or an installable package. Resolution: use **Framework Example** for annotated demonstrations and reserve **Agent Equipment** for promoted, validated equipment.
- "Agent Equipment" can mean the broad category or a ready-to-equip surface. Resolution: use **Equipment Candidate** before validation/publication and **Published Agent Equipment** for ready-to-equip surfaces.
- "PRD tracking" can mean worktree drafting or issue-tracker publication. Resolution: use **Repo Draft PRD** for reviewable drafts, **Published PRD Issue** for tracking, and re-project material draft changes into the issue.
- "Issue projection" can mean publication timing or synchronization mechanics. Resolution: use **Issue Projection** for post-review publication and closeout synchronization.
- "Metasmith guidance" can mean durable workflow or a specific plan. Resolution: use the **Metasmith Runbook** for repeatable maintenance duties and keep project-specific steps in PRDs, plans, and ADRs.
- "Review until clean" can mean a general quality gate or a named imported skill. Resolution: use **Review Until Clean** for the repo concept and invoke named review skills only when requested or adopted by repo policy.
- "Repository structure" can mean an intended architecture or files to create now. Resolution: use **Target Structure** for the PRD-level architecture and **Seed Surface** for files created in the Framework Seed.
- "Validation tooling" can mean seed integrity checks or harness behavior tests. Resolution: use the **Seed Validation Tool** for repo/framework integrity and leave harness behavior tests to downstream equipment.
- "Harness evidence" can mean docs, release notes, source, third-party package metadata, or local CLI output. Resolution: follow the **Harness Evidence Source Policy** and label each evidence category.
- "Equipment status" can mean a teaching example, an accepted spec, a plan, implementation, validation result, or published equipment. Resolution: use the **Equipment Promotion Path** states.
- "Skill surface" can mean a template for Smiths or a real equipped skill. Resolution: use **Skill Template** for seed guidance and create repo-local skills only after **Pressure Scenario Validation**.
- "Framework discovery" can mean preloaded agent routing or human README discovery. Resolution: use **Preloaded Framework Path** for Smiths and **Human Framework Entry** for human readers.
- "Handoff coverage" can mean informal confidence or auditable projection. Resolution: use a **Source Projection Register** for accepted requirements and deferments.
