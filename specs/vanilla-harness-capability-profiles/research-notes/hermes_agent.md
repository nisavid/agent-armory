# Research Note: Hermes Agent

Status: issue #44 research note

## Version Basis

Checked at: 2026-05-08T19:32:00-04:00.
Version basis: GitHub latest release `v2026.5.7`, named Hermes Agent v0.13.0, published 2026-05-07, plus tag-pinned first-party docs currently carried by the migrated profile. The canonical profile is not changed in this story.

## Source Set

- [Hermes Agent release `v2026.5.7`](https://github.com/NousResearch/hermes-agent/releases/tag/v2026.5.7)
- [Hermes Agent documentation index](https://hermes-agent.nousresearch.com/docs/llms.txt)
- [Hermes skills docs at migrated tag](https://github.com/NousResearch/hermes-agent/blob/v2026.4.30/website/docs/user-guide/features/skills.md)
- [Hermes MCP docs at migrated tag](https://github.com/NousResearch/hermes-agent/blob/v2026.4.30/website/docs/user-guide/features/mcp.md)
- [Hermes hooks docs at migrated tag](https://github.com/NousResearch/hermes-agent/blob/v2026.4.30/website/docs/user-guide/features/hooks.md)
- [Hermes plugins docs at migrated tag](https://github.com/NousResearch/hermes-agent/blob/v2026.4.30/website/docs/user-guide/features/plugins.md)
- [Hermes profiles docs at migrated tag](https://github.com/NousResearch/hermes-agent/blob/v2026.4.30/website/docs/user-guide/profiles.md)
- [Hermes delegation docs at migrated tag](https://github.com/NousResearch/hermes-agent/blob/v2026.4.30/website/docs/user-guide/features/delegation.md)
- [Hermes cron docs at migrated tag](https://github.com/NousResearch/hermes-agent/blob/v2026.4.30/website/docs/user-guide/features/cron.md)

## Surface Findings

- `instructions_context`: Needs more evidence. The migrated source set proves skills and delegation, and the release adds `/goal`, but the profile needs explicit instruction load paths before enrichment.
- `skills`: Source-backed fact. The migrated docs identify AgentSkills-compatible skills, managed skills, external skill directories, and Skills Hub installation.
- `mcp_tools`: Source-backed fact. Migrated docs identify MCP servers, MCP client toolsets, and a Hermes MCP server; the current release adds SSE transport, OAuth forwarding, retries, media tags, and keepalive behavior.
- `hooks_events`: Source-backed fact. Migrated docs identify gateway, plugin, and shell hooks; the release adds platform-plugin hooks and transform-output hooks.
- `plugins_bundles`: Source-backed fact. Migrated docs identify opt-in plugins; the release adds provider plugins, platform plugins, memory provider plugins, and dashboard plugin management.
- `agent_profiles_subagents`: Source-backed fact. Migrated docs identify profiles, subagents, and delegation; the release adds durable multi-agent Kanban boards and worker lifecycle controls.
- `memory_context_retrieval`: Source-backed fact with schema pressure. The current release adds `/goal`, checkpoints v2, session durability, and `X-Hermes-Session-Key` for long-term memory scoping.
- `config_settings`: Source-backed fact. Profiles and gateway configuration are source-backed; current release notes add allowlists, provider plugins, shared OAuth token stores, and config safety fixes.
- `permissions_approvals_sandboxing`: Source-backed fact. Release notes include redaction defaults, allowlists, stranger rejection, prompt-injection scanning, and credential TOCTOU fixes.
- `scheduling_automation`: Source-backed fact. Migrated docs identify cron, gateway cron ticker, curator scheduling, and background processes; current release adds `no_agent` cron mode and Kanban heartbeats.
- `commands_shortcuts`: Source-backed fact. Release notes and docs identify slash commands such as `/goal`, `/kanban`, `/model`, `/steer`, `/queue`, and curator subcommands.
- `providers_connectors`: Source-backed fact. Current release adds provider plugins, Google Chat, API server memory keys, xAI Custom Voices, SearXNG, OpenRouter cache control, and model provider changes.
- `runtime_modes`: Source-backed fact. Hermes spans TUI, gateway, dashboard, API server, Docker, ACP adapter, messaging platforms, and cron jobs.
- `cross_harness_import_compatibility`: Unknown. The profile names AgentSkills-compatible skills, but the checked sources do not prove native import fidelity for Codex, Claude Code, Cursor, OpenCode, or OpenClaw bundles.
- `lifecycle_reload_update`: Source-backed fact. Current release notes include auto-resume after restart, source-file reloads, `/update` restart handling, skill cache rescans, and restart-safe gateway behavior.

## Evidence Classification

This note distinguishes source-backed facts, local observations, implementation inferences, hypotheses, unsupported claims, unknowns, and not-applicable surfaces. Current-release facts are source-backed to the GitHub release; tag-pinned docs are source-backed to the migrated profile's version basis.

## Cross-Harness Import And Compatibility

Hermes applies AgentSkills-compatible language, but import fidelity is not established. A future profile should record imported convention, activation, surviving components, disable behavior, and limits instead of flattening compatibility into native skills support.

## Memory-Like Surfaces

Hermes is the strongest pressure case for memory-like profile structure. `/goal`, checkpoints v2, session durability, memory provider plugins, context provider plugins, and `X-Hermes-Session-Key` need fields for persistence scope, retrieval trigger, write authority, freshness, privacy, and API stability.

## Schema Pressure

Hermes motivates accepted schema pressure for version observations, memory-like structures, scheduler runner details, plugin/provider component types, security-control annotations, and lifecycle reload/update records.

## Analysis Angle Notes

Hermes can be modeled through a gateway Capability Analysis Angle, a cron/curator angle, a Kanban multi-agent angle, or a memory/checkpoint angle. A future Capability State Graph should prevent those surfaces from collapsing into one broad "automation" claim.

## Local Observations

No local Hermes binary, gateway, profile directory, plugin state, cron table, or dashboard state was inspected for this story.

## Major Uncertainty

The migrated profile is pinned to `v2026.4.30`; current release evidence is `v2026.5.7`. This creates significant migration pressure for issue #45 without authorizing profile mutation in issue #44.

## Scratch Artifact Disposition

GitHub release API output was treated as instance-scoped scratch. Durable conclusions are the source URLs and curated surface findings above.
