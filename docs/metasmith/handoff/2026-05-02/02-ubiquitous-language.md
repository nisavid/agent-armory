# Ubiquitous Language

## Purpose

This document establishes the Ubiquitous Language for the Agent Armory.

Smiths and Metasmiths should use these terms consistently. Harness-specific terms should be mapped to these terms rather than replacing them.

## Agent Armory

The **Agent Armory** is the repository, catalog, and methodology for curated Agent Equipment.

In this handoff, the concrete Armory is `nisavid/agent-armory`.

## Agent Equipment

**Agent Equipment** includes any reusable tooling, behavior, knowledge package, workflow, or configuration that equips an Agent or an agentic harness.

Examples:

- skills,
- MCP servers or tools,
- hooks,
- Agent Profiles,
- harness plugins,
- deterministic scripts,
- repo-local policy docs,
- reusable configuration templates,
- workflow runbooks,
- periodic action definitions,
- swarms or multi-agent workflows.

A harness or orchestration system having equipment installed is said to be **equipped** with that equipment.

## Agent Equipment Framework

The **Agent Equipment Framework** is the framework the first Metasmith is being asked to create.

It comprises:

1. all artifacts the Metasmith produces, and
2. the behaviors those artifacts induce in agents that later use the Armory.

The Framework’s purpose is to guide, direct, shape, constrain, and improve how Smiths create Agent Equipment.

## Metasmith

A **Metasmith** is an Agent whose task is to create or refine the Agent Equipment Framework.

The agent receiving the initial handoff is the **first Metasmith**.

## Smith

A **Smith** is an Agent that creates Agent Equipment within the Agent Equipment Framework.

Smiths should use the Framework’s methods, templates, harness catalogs, and validation rules before creating or modifying equipment.

## Agent

Strictly speaking, an **Agent** is the causal stream of reasoning, actions, tool calls, messages, and content that manifests through one or more inference turns within an agentic harness.

Loosely and commonly, people may refer to the whole assembly as an Agent: the model, harness, tools, permissions, context, state, identity, and ongoing interaction.

The Framework should preserve this distinction when precision matters.

## Agent Harness

An **Agent Harness** is the runtime or orchestration system in which an Agent is strapped.

Examples:

- Codex,
- OpenClaw,
- Hermes Agent,
- Claude Code,
- Cursor,
- OpenCode.

## Strapped

An Agent is **strapped into** or **strapped with** a harness when its reasoning, actions, and content stream is being mediated by that harness.

Example:

> A Smith strapped into Claude Code can use Claude Code hooks, subagents, skills, MCP servers, and scheduled tasks.

## Agent Profile

Some harnesses use the word “agent” for a reusable declaration or configuration of identity, affordances, mission, prompt, tools, persona, model, permissions, and other specialization data.

In the Framework, call such a declaration an **Agent Profile**.

Examples:

- Claude Code subagents,
- Codex agent roles,
- OpenCode configured agents,
- Cursor custom modes or subagents,
- OpenClaw configured agents or agent runtime profiles.

This avoids confusing the profile with the running Agent.

## Harness Component

A **Harness Component** is a reusable behavior that integrates into an Agent Harness.

Common component types:

- MCPs,
- skills,
- hooks,
- Agent Profiles.

Some harness providers support additional component types, such as slash commands, scheduled tasks, routines, custom modes, context engines, toolsets, gateway hooks, cron jobs, desktop tasks, or services.

## Harness Plugin

A **Harness Plugin** is a portable collection of Harness Components.

A plugin may contain:

- tools,
- skills,
- hooks,
- Agent Profiles,
- services,
- configuration,
- commands,
- resources,
- docs.

Some harnesses use “plugin” narrowly, while others use it broadly. The Framework treats plugins as packaging and distribution units for components.

## Agent Ops

**Agent Ops** is a future item of Agent Equipment to be implemented by a Smith after the Framework is created.

Agent Ops provides an operations framework for repos that are operated agentically.

## Periodic Actions

**Periodic Actions** are a future item of Agent Equipment to be implemented by a Smith after the Framework is created.

Periodic Actions provide a cross-harness way to define, install, inspect, and uninstall repeated agent actions with configured periods.

## Relationship model

```text
Agent Armory
  contains Agent Equipment
  contains the Agent Equipment Framework

Agent Equipment Framework
  created by the first Metasmith
  used by Smiths
  guides creation of Agent Equipment

Harness Plugin
  packages Harness Components

Harness Component
  may be a skill, MCP, hook, Agent Profile, or other harness-supported unit

Agent Profile
  configures a kind of Agent but is not itself the running Agent

Agent
  is strapped into a Harness
  may be equipped with Agent Equipment
```

## Harness-specific term mapping

| Harness term | Framework term |
|---|---|
| Claude Code subagent | Agent Profile |
| Codex agent role | Agent Profile |
| OpenCode configured agent | Agent Profile |
| Cursor custom mode | Agent Profile-like component |
| OpenClaw configured agent | Agent Profile-like configuration |
| MCP server | Harness Component: MCP |
| Plugin-provided skill/hook/MCP/profile | Harness Components packaged by a Harness Plugin |

## Precision rule

When a document is about model behavior, say **Agent**.

When a document is about a reusable configuration, say **Agent Profile**.

When a document is about the host runtime or client, say **Agent Harness**.

When a document is about reusable capability, say **Agent Equipment**.

When a document is about the Armory’s meta-methodology, say **Agent Equipment Framework**.
