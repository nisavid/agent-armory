# Agent Equipment Forge

Status: Forge Seed

The Agent Equipment Forge helps Smiths design reusable Agent Equipment without overloading model context, hiding hard policy in prose, or treating harness-specific guesses as facts.

## Purpose

The Forge answers four questions for each equipment idea:

- What capability is the equipment meant to provide?
- Which harness surfaces should carry each part of that capability?
- What evidence supports the harness and security claims?
- What validation is required before the equipment can be promoted?

The Forge Seed supplies the first canonical docs, templates, examples, specs,
and validation checks. It does not implement downstream equipment such as Agent
Equipment Config, Agent Ops, Periodic Actions, or Harness Capability Refresh.

## Vision alignment

Use the [Armory Vision](vision.md) as the experience north star for Forge work.
Equipment should help Agents outfit work before execution, right-size model
cognition, clarify underspecified intent, keep deterministic operations in
deterministic surfaces, enforce policy through reliable boundaries, preserve
durable knowledge, and improve the equipment ecosystem when repeated friction
reveals a gap.

## Least cognitive privilege

Put only reasoning the model must actively apply into model-facing context.

Use lower-overhead, more reliable surfaces for everything else:

- enforce hard invariants with hooks, permissions, sandboxes, or approval gates;
- compute deterministic results with scripts or tools;
- expose external live state through MCP/tools;
- store project truth in local docs;
- parameterize durable choices with config;
- teach judgment with skills;
- delegate specialized work with Agent Profiles;
- package coherent bundles with Harness Plugins.

## Component model

A complete equipment design starts with a capability card, then projects requirements into one or more Harness Components and supporting artifacts. When a real Equipment Candidate requires committed entry artifacts before implementation, keep those records in one Forge Entry Bundle under a neutral project path.

Primary component types:

- **Skills** teach task judgment, sequencing, fallback behavior, and output contracts.
- **MCP/tools** expose typed local or external operations.
- **Hooks** enforce, observe, inject, rewrite, block, route, or record around harness lifecycle events.
- **Agent Profiles** define specialized worker identity, authority, context, model, tools, and permissions. Harness and plugin paths often call these `agents`.
- **Harness Plugins** package components for installation, versioning, sharing, and reuse.
- **Scripts** perform deterministic parsing, validation, inspection, formatting, or safe explicit side effects.
- **Local docs** store canonical project truth that humans or Agents need to read.
- **Config** stores typed parameters, thresholds, allowlists, autonomy levels,
  and local choices. Agent Equipment Config is the planned shared equipment for
  layerable, composable, enforceable equipment config.

## Context management

Always-visible context stays small. Smiths route bulky or task-specific material behind the surface that loads when needed.

Use concise root routing, narrow skill descriptions, on-demand docs, deterministic helper scripts, structured tool responses, and scoped Agent Profiles. Avoid giant always-on instructions, duplicated policy, verbose tool descriptions, hidden prompt injection, and skills that contain complete project histories.

## Security

Security design is part of the equipment interface decision, not a final polish step.

Smiths classify read/write behavior, side effects, secrets, approval requirements, failure modes, and mutation gates before implementation. Mutation-capable MCP/tools require permissions, hooks, approvals, or sandboxing appropriate to their blast radius. Examples and templates must not imply production safety before equipment-specific validation.

## Maintenance

Harness facts are volatile. Canonical guidance records evidence category, source, checked date, version basis, and uncertainty where the source is incomplete or inconsistent.

Forgewrights keep source handoffs as provenance, project accepted decisions
into canonical surfaces, refresh harness facts before relying on moving
affordances, and update downstream specs when Forge decisions change.
Reflection Findings are maintenance evidence: route them through the issue
tracker, Tooling Request, or the relevant Equipment Candidate instead of leaving
reusable lessons in chat.
