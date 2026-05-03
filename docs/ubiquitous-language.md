# Ubiquitous Language

Status: Framework Seed

This document is the canonical vocabulary surface for Smiths and Metasmiths. Use `CONTEXT.md` as the project-wide vocabulary register; use this document when applying that language inside the Agent Equipment Framework.

## Language

**Agent Armory** is the home for Agent Equipment and the Agent Equipment Framework.

**Agent Equipment** is reusable tooling, behavior, workflow, knowledge, or configuration that equips an Agent or agentic system.

**Equipment Candidate** is proposed, specified, planned, or implemented equipment that has not completed validation and publication.

**Published Agent Equipment** is Agent Equipment that has completed the Equipment Promotion Path and is intended to be equipped.

**Agent Equipment Framework** is the Armory method and supporting artifacts that help Smiths create Agent Equipment.

**Metasmith** is an Agent that creates or refines the Agent Equipment Framework.

**Smith** is an Agent that creates Agent Equipment using the Agent Equipment Framework.

**Agent** is the causal stream of reasoning, actions, tool calls, messages, and content mediated by an Agent Harness.

**Agent Harness** is the runtime or orchestration system in which an Agent is strapped.

**Strapped** means mediated by an Agent Harness.

**Agent Profile** is a reusable harness configuration for identity, mission, prompt, tools, model, permissions, and related behavior.

**Harness Component** is reusable behavior integrated into an Agent Harness.

**Harness Plugin** is a portable collection of Harness Components.

**Source Handoff** is preserved upstream material accepted as provenance for Framework design, not the live Framework surface.

**Canonical Framework Docs** are the current live documentation, templates, examples, and specs that Smiths use as the Framework.

**Framework Seed** is the first coherent version of the Agent Equipment Framework.

**Seed Validation** checks the Framework Seed's repository shape, links, source projection, promotion-state labels, and catalog metadata.

**Harness Capability Catalog** is the canonical versioned record of Agent Harness affordances, limitations, sources, and refresh requirements.

**Harness Fact Refresh** is a source-backed update to the Harness Capability Catalog.

**Framework Example** is an annotated demonstration of the Framework's decision method using realistic but non-production equipment shapes.

**Equipment Promotion Path** is the lifecycle that moves an equipment idea from example or spec toward Published Agent Equipment.

## Relationships

- The Agent Armory contains Agent Equipment and the Agent Equipment Framework.
- The Agent Equipment Framework is created by Metasmiths and used by Smiths.
- Smiths create Agent Equipment for one or more Agent Harnesses.
- Equipment Candidates may become Published Agent Equipment after validation and publication.
- An Agent is strapped when its reasoning and actions are mediated by an Agent Harness.
- A Harness Plugin packages one or more Harness Components.
- An Agent Profile configures a reusable kind of Agent but is not the running Agent.
- A Source Handoff can inform Canonical Framework Docs, but it is not itself the live Framework surface.
- Framework Examples teach the decision method; they are not automatically Agent Equipment.
- Seed Validation checks Framework Seed integrity; downstream equipment needs equipment-specific validation.

## Precision rules

- Use **Agent** for the running causal stream, not for a reusable harness declaration.
- Use **Agent Profile** for a reusable identity, mission, tool, permission, or model configuration.
- Use **Agent Harness** for the runtime or orchestration system that mediates the Agent.
- Use **Agent Equipment** for reusable capability; use **Equipment Candidate** until validation and publication are complete.
- Use **Published Agent Equipment** only after the promotion path reaches `published`.
- Use **Source Handoff** for preserved provenance and **Canonical Framework Docs** for current guidance.
- Use **Framework Seed** for this first framework pass; name downstream equipment separately.
- Use **Harness Fact Refresh** for catalog updates and **Harness Capability Refresh** for the downstream equipment that maintains the catalog over time.
