# Research Note: Cursor

Status: issue #44 research note

## Version Basis

Checked at: 2026-05-08T19:32:00-04:00.
Version basis: official Cursor changelog through the 2026-05-07 entry, plus first-party Cursor docs for rules, skills, MCP, hooks, subagents, plugins, Cloud Agent automations, and CLI use. The canonical profile is not changed in this story.

## Source Set

- [Cursor changelog](https://cursor.com/changelog)
- [Cursor changelog 2026-05-07](https://cursor.com/changelog/05-07-26)
- [Cursor rules](https://cursor.com/docs/rules)
- [Cursor skills](https://cursor.com/docs/skills)
- [Cursor MCP](https://cursor.com/docs/mcp)
- [Cursor hooks](https://cursor.com/docs/hooks)
- [Cursor subagents](https://cursor.com/docs/subagents)
- [Cursor plugins](https://cursor.com/docs/plugins)
- [Cursor Cloud Agent automations](https://cursor.com/docs/cloud-agent/automations)
- [Cursor CLI use](https://cursor.com/docs/cli/using)

## Surface Findings

- `instructions_context`: Source-backed fact. Cursor supports rules, AGENTS.md, skills, subagents, and plan-based execution surfaces.
- `skills`: Source-backed fact. Cursor treats Agent Skills as an open standard, loads project and user skill directories, and provides migration from rules and commands to skills.
- `mcp_tools`: Source-backed fact. Cursor MCP supports stdio, SSE, and Streamable HTTP transports plus tools, prompts, resources, roots, elicitation, and MCP Apps.
- `hooks_events`: Source-backed fact with schema pressure. Hooks are a documented surface, but the current research did not normalize Cursor hook event names against Codex or Claude Code.
- `plugins_bundles`: Source-backed fact. Plugins package rules, skills, agents, commands, MCP servers, and hooks, with marketplace and team marketplace surfaces.
- `agent_profiles_subagents`: Source-backed fact. Subagents have isolated context windows, foreground/background modes, resumability, built-in agents, and subagent trees.
- `memory_context_retrieval`: Needs more evidence. Subagents have separate context windows, but the checked sources do not define persistent shared memory.
- `config_settings`: Source-backed fact. Cursor exposes CLI and product settings, plus team marketplace/admin surfaces.
- `permissions_approvals_sandboxing`: Source-backed fact with schema pressure. MCP security guidance and admin model/provider allowlists exist, but the profile needs a uniform way to record plan, workspace, and team-admin constraints.
- `scheduling_automation`: Source-backed fact. Cloud Agent automations support schedule and event triggers; changelog evidence also includes scheduled vulnerability scanning.
- `commands_shortcuts`: Source-backed fact. Commands can be packaged in plugins, skills can be pinned as quick actions, and rules or commands can migrate to skills.
- `providers_connectors`: Source-backed fact. MCP and Cloud Agent integrations cover external tools, GitHub, Slack, Sentry, webhooks, and provider-level model controls.
- `runtime_modes`: Source-backed fact. Cursor spans IDE, CLI, Cloud Agent, automations, SDK agents, foreground/background subagents, and PR review workflows.
- `cross_harness_import_compatibility`: Needs more evidence. Skills are described as an open standard, but native import fidelity for another harness's equipment is not proven by the checked pages.
- `lifecycle_reload_update`: Needs more evidence. Cursor can toggle MCP servers and load local plugins, but lifecycle reload semantics need source-specific fields before canonical profile changes.

## Evidence Classification

This note distinguishes source-backed facts, local observations, implementation inferences, hypotheses, unsupported claims, unknowns, and not-applicable surfaces. Changelog entries and docs are source-backed; cross-harness compatibility remains a hypothesis until a source describes import fidelity.

## Cross-Harness Import And Compatibility

Cursor's Agent Skills compatibility is a pressure point because it may overlap with Codex and Claude Code skill conventions. The profile should distinguish "open-standard skill shape" from native plugin, command, or MCP import support.

## Memory-Like Surfaces

Subagent context isolation is source-backed. Persistent memory, retrieval freshness, write authority, and privacy boundaries remain unknown.

## Schema Pressure

Cursor motivates accepted schema pressure for open-standard compatibility notes, plugin component manifests, Cloud Agent automation runner details, admin/provider constraints, and command migration surfaces.

## Analysis Angle Notes

Cursor can be modeled through an IDE-local Capability Analysis Angle, a Cloud Agent automation angle, or a subagent parallelism angle. A future Capability State Graph should separate local editor state, cloud runner state, and background subagent state.

## Local Observations

No local Cursor desktop app, CLI, settings, Cloud Agent, plugin install, or marketplace state was inspected for this story.

## Major Uncertainty

Cursor's latest official state is changelog-based rather than a GitHub release tag. Exact local app version, plan gates, team marketplace policy, and automations availability remain environment-scoped.

## Scratch Artifact Disposition

Firecrawl extraction output was treated as instance-scoped scratch. Durable conclusions are the source URLs and curated surface findings above.
