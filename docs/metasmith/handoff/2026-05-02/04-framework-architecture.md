# Agent Equipment Framework Architecture

## Purpose

The Agent Equipment Framework is the meta-architecture for creating reusable Agent Equipment inside the Agent Armory.

Its job is to help Smiths decide what to build, where to encode each part, how to package it, how to project it into harnesses, and how to maintain it.

## Architectural layers

```text
Agent Armory
  README and Framework docs
  Ubiquitous Language
  Evidence taxonomy
  Harness capability catalog
  Smith runbooks
  Templates
  Examples
  Specs
  Equipment packages

Agent Equipment
  Harness Components
    skills
    MCP/tools
    hooks
    Agent Profiles
    commands
    scheduled tasks
    rules
  Supporting artifacts
    scripts
    config
    local docs
    tests
    source maps
  Packaging
    Harness Plugins
    installation docs
    manifests
```

## Component responsibilities

### Skill

A skill is a model-facing procedural package. It teaches an Agent how to approach a task.

Use a skill for:

- judgment,
- task decomposition,
- sequencing,
- examples,
- fallbacks,
- output contracts,
- source-quality discipline.

Do not use a skill for:

- secrets,
- hard policy enforcement,
- long static docs,
- deterministic calculations,
- large generated state,
- duplicated project policy.

### MCP/tool

An MCP server or tool is a typed capability boundary.

Use MCP/tools for:

- external live state,
- structured operations,
- reusable service interfaces,
- typed inputs/outputs,
- auth centralization,
- pagination,
- rate-limit handling,
- cross-client reuse.

Do not rely on MCP alone for policy. Wrap mutation-capable tools with hooks, permissions, or approvals.

### Hook

A hook is middleware around lifecycle events.

Use hooks for:

- blocking dangerous actions,
- requiring approvals,
- redacting outputs,
- logging telemetry,
- enforcing settings,
- injecting small context,
- rewriting tool params,
- validating or annotating results.

Do not hide long workflows inside hooks.

### Agent Profile

An Agent Profile defines a specialized Agent configuration.

Use Agent Profiles when the worker’s identity, authority, context, model, or toolset materially changes.

Examples:

- `pr-reviewer`,
- `docs-researcher`,
- `latency-investigator`,
- `release-manager`,
- `security-auditor`.

### Harness Plugin

A Harness Plugin packages Harness Components.

Use plugins when equipment should be installed, updated, versioned, shared, or distributed as a coherent bundle.

A plugin may include:

- skills,
- MCPs/tools,
- hooks,
- Agent Profiles,
- scripts,
- config defaults,
- docs,
- services,
- commands.

### Script

A script performs deterministic work.

Use scripts for:

- parsing,
- validation,
- mapping changed files to modules,
- inspecting package versions,
- summarizing structured data,
- producing JSON outputs,
- performing safe, explicit side effects.

Scripts should provide `--help`, stable output, clear exit codes, and safe defaults.

### Local doc

A local doc stores canonical project truth.

Use local docs for:

- repo policy,
- module boundaries,
- ops runbooks,
- review rubrics,
- architecture decisions,
- release procedures.

Skills should reference local docs, not duplicate them.

### Config

Config stores durable parameters.

Use config for:

- thresholds,
- timeouts,
- allowlists,
- autonomy levels,
- model selections,
- hook enablement,
- tool enablement,
- secrets references,
- local install choices.

Config should use human-friendly names, typed values, and avoid long prose.

## The Framework itself

The Framework should contain:

- terminology,
- architecture,
- decision methods,
- templates,
- examples,
- harness projections,
- evidence rules,
- maintenance rules.

It should not merely contain finished equipment. It should teach Smiths how to create equipment well.

## Context management architecture

Always-visible context should be minimal.

Smiths should prefer:

- short skill references,
- on-demand `SKILL.md`,
- on-demand doc reads,
- deterministic helper scripts,
- narrow MCP tools,
- scoped Agent Profiles,
- hook-enforced policy.

Avoid:

- giant always-on rule files,
- verbose tool descriptions,
- bloated skill descriptions,
- hidden prompt injections,
- duplicated docs.

## Security architecture

Use defense in depth:

1. least cognitive privilege,
2. least tool privilege,
3. narrow MCP/tool scopes,
4. hook-enforced policy,
5. approval gates for mutations,
6. sandboxing where available,
7. secret redaction,
8. repo-local config,
9. explicit ownership and autonomy settings,
10. audit logs where feasible.

## Maintenance architecture

Harness facts are volatile.

The Armory must track:

- harness versions,
- checked-at timestamps,
- supported components,
- hook events,
- scheduling mechanisms,
- skill discovery rules,
- plugin packaging rules,
- MCP support,
- known limitations,
- source URLs.

When a depended-on capability changes, the Armory should create a high-priority issue or issue candidate.
