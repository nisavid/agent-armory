# Research Note: OpenClaw

Status: issue #44 research note

## Version Basis

Checked at: 2026-05-08T19:32:00-04:00.
Version basis: GitHub latest release `v2026.5.7` published 2026-05-07, plus tag-pinned first-party docs currently carried by the migrated profile. The canonical profile is not changed in this story.

## Source Set

- [OpenClaw release `v2026.5.7`](https://github.com/openclaw/openclaw/releases/tag/v2026.5.7)
- [OpenClaw feature overview at migrated tag](https://github.com/openclaw/openclaw/blob/v2026.5.2/docs/concepts/features.md)
- [OpenClaw skills at migrated tag](https://github.com/openclaw/openclaw/blob/v2026.5.2/docs/tools/skills.md)
- [OpenClaw plugins at migrated tag](https://github.com/openclaw/openclaw/blob/v2026.5.2/docs/tools/plugin.md)
- [OpenClaw plugin manifest at migrated tag](https://github.com/openclaw/openclaw/blob/v2026.5.2/docs/plugins/manifest.md)
- [OpenClaw compatible bundles at migrated tag](https://github.com/openclaw/openclaw/blob/v2026.5.2/docs/plugins/bundles.md)
- [OpenClaw MCP at migrated tag](https://github.com/openclaw/openclaw/blob/v2026.5.2/docs/cli/mcp.md)
- [OpenClaw multi-agent docs at migrated tag](https://github.com/openclaw/openclaw/blob/v2026.5.2/docs/concepts/multi-agent.md)
- [OpenClaw cron jobs at migrated tag](https://github.com/openclaw/openclaw/blob/v2026.5.2/docs/automation/cron-jobs.md)
- [OpenClaw hooks at migrated tag](https://github.com/openclaw/openclaw/blob/v2026.5.2/docs/automation/hooks.md)

## Surface Findings

- `instructions_context`: Needs more evidence. Compatible bundles, skills, commands, and multi-agent configs carry instructions, but enrichment needs source-shaped load path fields.
- `skills`: Source-backed fact. OpenClaw supports skills, plugin-shipped skills, per-agent allowlists, and skill snapshot invalidation.
- `mcp_tools`: Source-backed fact. OpenClaw supports MCP client/server surfaces; current release notes include Codex OAuth route preservation and Tavily SecretRef resolution.
- `hooks_events`: Source-backed fact. OpenClaw supports hooks and webhooks, with release notes adding authorization gates around inline skill tool dispatch.
- `plugins_bundles`: Source-backed fact. OpenClaw supports native plugins, plugin manifests, plugin commands, managed plugin install/rollback/repair, and compatible bundle surfaces.
- `agent_profiles_subagents`: Source-backed fact. Multi-agent configs, per-agent skill allowlists, and subagent registry behavior are source-backed.
- `memory_context_retrieval`: Source-backed fact with schema pressure. Current release notes include Active Memory admin toggles and cached assembled context invalidation.
- `config_settings`: Source-backed fact. Config, channels, models, providers, plugin lifecycle, and runtime snapshots are source-backed surfaces.
- `permissions_approvals_sandboxing`: Source-backed fact. Current release notes mention Codex approval modes, admin-scope memory toggles, before-tool-call authorization hooks, owner enforcement, allowlists, and SecretRef handling.
- `scheduling_automation`: Source-backed fact. Cron, heartbeat turns, hooks, webhooks, background services, and cron status JSON are source-backed.
- `commands_shortcuts`: Source-backed fact. CLI commands, plugin commands, native command handlers, channels CLI, cron CLI, and model auth/list commands are source-backed.
- `providers_connectors`: Source-backed fact. Model providers, media providers, search providers, channels, Discord, Telegram, WhatsApp, Tavily, OpenAI, and Codex OAuth are source-backed connectors.
- `runtime_modes`: Source-backed fact. OpenClaw spans Gateway, CLI, multi-agent workspaces, channels, plugin background services, cron, and native desktop release artifacts.
- `cross_harness_import_compatibility`: Source-backed fact. The migrated docs name compatible Codex, Claude, and Cursor bundles; current release notes include Codex approval-route behavior. This must not be flattened into native support.
- `lifecycle_reload_update`: Source-backed fact. Current release notes include plugin install rollback/repair, skill snapshot invalidation, runtime config snapshots, channel hot-reload deferrals, and doctor repair behavior.

## Evidence Classification

This note distinguishes source-backed facts, local observations, implementation inferences, hypotheses, unsupported claims, unknowns, and not-applicable surfaces. Release and tag-pinned docs are source-backed; mapping compatible bundles into a cross-harness compatibility extension is implementation inference.

## Cross-Harness Import And Compatibility

OpenClaw is the clearest compatibility pressure case. The profile needs fields for imported convention, originating harness, surviving components, activation, disable behavior, precedence, fidelity limits, route/approval visibility, and source evidence.

## Memory-Like Surfaces

Active Memory and assembled context invalidation need first-class memory-like metadata. The profile should record persistence scope, admin scope, write authority, retrieval/freshness behavior, privacy controls, and whether memory is native, plugin-provided, or connector-backed.

## Schema Pressure

OpenClaw motivates accepted schema pressure for cross-harness import compatibility, memory-like surfaces, lifecycle/reload/update semantics, approval/sandbox detail, runtime config snapshots, and scheduler state fields.

## Analysis Angle Notes

OpenClaw can be modeled through a compatibility-bridge Capability Analysis Angle, a Gateway/runtime angle, a cron/heartbeat angle, or a memory/context angle. A future Capability State Graph should keep these separate because each has different evidence and mutation risks.

## Local Observations

No local OpenClaw gateway, config, channel, plugin, cron, or desktop state was inspected for this story.

## Major Uncertainty

The migrated profile records `v2026.5.2`; current release evidence is `v2026.5.7`. Release notes are rich enough to signal schema pressure, but tag-pinned docs for the newer release should be refreshed in the profile enrichment story.

## Scratch Artifact Disposition

GitHub release API output was treated as instance-scoped scratch. Durable conclusions are the source URLs and curated surface findings above.
