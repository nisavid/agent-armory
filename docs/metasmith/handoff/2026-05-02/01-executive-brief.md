# Executive Brief

## Purpose

This handoff asks the first Metasmith to populate `nisavid/agent-armory` with the first version of the **Agent Equipment Framework**.

The Framework will guide future Smiths in creating Agent Equipment that is reliable, portable, maintainable, and aligned with each target harness’s actual affordances.

## What the Framework must solve

Agents need reusable equipment, but current harness ecosystems use overlapping terms and incompatible primitives. A method is needed for deciding when intent should become:

- a skill,
- an MCP/tool,
- a hook,
- an Agent Profile,
- a plugin,
- a local script,
- a config value,
- a repo-local doc,
- a workflow or runbook.

The Framework must make those decisions systematic.

## Key thesis

Use **least cognitive privilege**:

> Put only the reasoning that the model must actively apply into model-facing skills. Put everything else into references, docs, configs, scripts, hooks, tools, Agent Profiles, or plugins according to how deterministic, local, enforceable, volatile, and reusable it is.

## Core decomposition

```text
Skill:
  teaches judgment and procedure.

MCP/tool:
  exposes typed external or local operations.

Hook:
  enforces, observes, injects, rewrites, blocks, routes, or records at lifecycle seams.

Agent Profile:
  defines a specialized Agent identity, toolset, model, permissions, and mission.

Harness Plugin:
  packages components for installation and reuse.

Script:
  performs deterministic computation or validation.

Local doc:
  stores human-readable canonical project truth.

Config:
  stores durable parameters, settings, thresholds, and local choices.
```

## What the Metasmith should produce

The Metasmith should create:

- Ubiquitous Language docs.
- Evidence taxonomy and source map.
- Framework architecture docs.
- Decision guide and Smith runbook.
- Harness capability catalog.
- Templates for every key artifact type.
- Example capabilities.
- Initial Smith task specs.
- Maintenance policy for harness capability refresh.

## First Smith tasks

After the Framework is created, Smiths should be tasked with:

1. **Agent Ops:** a framework for agentic repo operations and durable repo-local settings.
2. **Periodic Actions:** reusable cross-harness equipment for periodic agent actions.
3. **Harness Capability Refresh:** Armory-local maintenance that tracks supported harness versions and capability changes.

## Harnesses covered

This handoff includes harness-specific analysis for:

- Codex,
- OpenClaw,
- Hermes Agent,
- Claude Code,
- Cursor,
- OpenCode.

Each harness entry is versioned and must be refreshed before depending on it in production equipment.

## Expected outcome

After this handoff is executed, `nisavid/agent-armory` should no longer be a blank slate. It should contain a coherent meta-framework that future agents can use to create reusable Agent Equipment without rediscovering these architectural decisions.
