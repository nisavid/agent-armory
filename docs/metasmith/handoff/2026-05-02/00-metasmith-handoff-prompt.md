# Metasmith Handoff Prompt

You are the **first Metasmith** for `nisavid/agent-armory`.

Your mission is to create the first version of the **Agent Equipment Framework** inside the repository.

Read every file in this final handoff bundle before modifying the repository. Treat this bundle as self-contained and normative unless later repo-local information contradicts it.

## Your objective

Create a durable Framework that helps future **Smiths** create high-quality **Agent Equipment**.

The Framework must help Smiths translate patterns of intent into the right combination of:

- skills,
- MCP servers/tools,
- hooks,
- Agent Profiles,
- Harness Plugins,
- local docs,
- deterministic scripts,
- config,
- tests,
- maintenance policies,
- examples.

The Framework is both:

1. the artifacts you create in the repository, and
2. the behavior those artifacts induce in later Agents.

## Terms you must use

Use the Ubiquitous Language in `02-ubiquitous-language.md`.

Important terms:

- **Agent Armory:** the repository and catalog for Agent Equipment.
- **Agent Equipment:** reusable agent tooling, behavior, workflow, or configuration.
- **Agent Equipment Framework:** the meta-framework you are creating.
- **Metasmith:** an Agent that creates or refines the Framework.
- **Smith:** an Agent that creates Agent Equipment using the Framework.
- **Agent:** the causal stream of reasoning, actions, tool calls, messages, and content through a harness.
- **Agent Harness:** the runtime or orchestration system into which an Agent is strapped.
- **Agent Profile:** a reusable harness configuration of identity, mission, prompt, tools, model, permissions, and related behavior.
- **Harness Component:** reusable behavior integrated into a harness.
- **Harness Plugin:** portable collection of Harness Components.
- **Equipped:** a harness has installed or usable Agent Equipment.

## Core principle

Preserve **least cognitive privilege**.

Use this mapping:

```text
Teach with skills.
Act through tools/MCPs.
Enforce with hooks, permissions, and sandboxing.
Compute with scripts.
Store local truth in docs.
Parameterize with config.
Delegate with Agent Profiles.
Package with plugins.
Maintain with versioned harness capability catalogs.
```

## Required repository shape

Create a clear repository structure. You may refine this layout, but you must preserve its conceptual separation.

```text
README.md
docs/
  ubiquitous-language.md
  equipment-framework.md
  smith-runbook.md
  metasmith-runbook.md
  interface-decision-guide.md
  harness-components.md
  harness-capabilities.md
  harness-capabilities.toml
  evidence-taxonomy.md
  security-and-control.md
templates/
  capability-card.md
  interface-decision-record.md
  skill/
  hook/
  agent-profile/
  plugin/
  script/
  mcp/
  config/
examples/
  pr-review/
  docs-research/
  observability-investigation/
specs/
  agent-ops.md
  periodic-actions.md
  harness-capability-refresh.md
issues/
  pending/
    high/
```

Do not turn this into a random pile of examples. Create a coherent Framework.

## Required content

### 1. Ubiquitous Language

Create `docs/ubiquitous-language.md`.

It must establish the terms from this bundle, including Agent Armory, Agent Equipment, Agent Equipment Framework, Smith, Metasmith, Agent, strapped, Agent Harness, Agent Profile, Harness Component, Harness Plugin, Agent Ops, and Periodic Actions.

### 2. Evidence discipline

Create `docs/evidence-taxonomy.md`.

Include evidence categories:

- documentation-supported,
- source-supported,
- implementation inference,
- practitioner wisdom,
- hypothesis.

Require Smiths to label non-obvious claims.

### 3. Framework architecture

Create `docs/equipment-framework.md` and `docs/harness-components.md`.

Explain the component model:

- skills for model-facing procedure,
- MCP/tools for typed capability surfaces,
- hooks for automatic enforcement and lifecycle behavior,
- Agent Profiles for specialized Agents,
- plugins for packaging,
- scripts for deterministic computation,
- local docs for canonical project truth,
- config for parameters and settings.

### 4. Decision method

Create `docs/interface-decision-guide.md` and `docs/smith-runbook.md`.

Encode the least-cognitive-privilege decision tree and the capability-creation runbook.

### 5. Harness capability catalog

Create `docs/harness-capabilities.md` and `docs/harness-capabilities.toml`.

Include Codex, OpenClaw, Hermes Agent, Claude Code, Cursor, and OpenCode.

State:

- checked-at date,
- version,
- source URLs,
- supported component types,
- limitations,
- scheduling mechanisms,
- implementation caveats,
- required refresh notes.

### 6. Templates and examples

Create templates for:

- capability cards,
- interface decision records,
- skill references and `SKILL.md`,
- hooks,
- Agent Profiles,
- plugins,
- scripts,
- MCP/tool definitions,
- config,
- security reviews,
- context-budget reviews.

Create examples for:

- PR review,
- documentation search,
- observability investigation.

Examples should demonstrate the Framework’s method. They should not pretend to be production-ready unless they are actually implemented and tested.

### 7. Initial Smith task specs

Create specs for:

- Agent Ops,
- Periodic Actions,
- Harness Capability Refresh.

Use `08-initial-smith-task-specs.md` as source material.

## Constraints

- Do not include secrets or personal credentials.
- Do not duplicate large policy bodies across files.
- Keep always-visible skill references short.
- Put detailed skill instructions in `SKILL.md`.
- Put deterministic behavior in scripts or tools.
- Put hard policy in hooks, permission config, or sandbox rules.
- Make all harness-specific facts versioned and refreshable.
- Include source URLs for harness-specific claims.
- Prefer templates and method docs over plausible but unverified working components.

## Acceptance criteria

You are done when:

1. The repo contains a self-contained Agent Equipment Framework.
2. A new Smith can read the Framework and know how to design equipment.
3. The Framework contains a versioned harness capability catalog.
4. The Framework preserves the Ubiquitous Language.
5. The Framework includes templates and examples.
6. The first Smith tasks are specified.
7. Any unsupported or uncertain harness claims are marked as such.
8. The repo has a clear README and reading path.
9. You have not created fake production-ready implementations.
10. You report created files, assumptions, and next tasks.

## Final report

At the end of your run, report:

- created files,
- the final Framework shape,
- assumptions,
- unresolved questions,
- harness facts that need refresh,
- next Smith tasks.
