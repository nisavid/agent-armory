# Research Note: OpenCode

Status: issue #44 research note

## Version Basis

Checked at: 2026-05-08T19:32:00-04:00.
Version basis: GitHub latest release `v1.14.41` published 2026-05-07, plus first-party OpenCode docs for integration surfaces. The canonical profile is not changed in this story.

## Source Set

- [OpenCode release `v1.14.41`](https://github.com/anomalyco/opencode/releases/tag/v1.14.41)
- [OpenCode docs index](https://opencode.ai/docs/)
- [OpenCode CLI docs](https://opencode.ai/docs/cli/)
- [OpenCode skills](https://opencode.ai/docs/skills/)
- [OpenCode plugins](https://opencode.ai/docs/plugins/)
- [OpenCode agents](https://opencode.ai/docs/agents/)
- [OpenCode config](https://opencode.ai/docs/config/)
- [OpenCode MCP servers](https://opencode.ai/docs/mcp-servers/)
- [OpenCode permissions](https://opencode.ai/docs/permissions/)
- [OpenCode commands](https://opencode.ai/docs/commands/)
- [OpenCode GitHub integration](https://opencode.ai/docs/github/)

## Surface Findings

- `instructions_context`: Source-backed fact. Skills, agents, command templates, and instruction files all carry authored instruction material.
- `skills`: Source-backed fact. Skills are documented first-party components.
- `mcp_tools`: Source-backed fact. OpenCode documents MCP server integration.
- `hooks_events`: Source-backed fact. Plugin docs identify plugin hooks; the exact event vocabulary needs separate normalization.
- `plugins_bundles`: Source-backed fact. Plugins are first-party extension components and can define tools and hooks.
- `agent_profiles_subagents`: Source-backed fact. OpenCode documents primary agents and subagents.
- `memory_context_retrieval`: Needs more evidence. The migrated profile mentions snapshots and context pressure, but the checked source set does not establish a stable memory API.
- `config_settings`: Source-backed fact. OpenCode documents configuration.
- `permissions_approvals_sandboxing`: Source-backed fact. Permissions are documented and default posture can be broad unless configured.
- `scheduling_automation`: Source-backed fact with limitation. GitHub Action integration can be scheduled externally; no verified native durable scheduler was found.
- `commands_shortcuts`: Source-backed fact. Commands can be defined in markdown files or config.
- `providers_connectors`: Source-backed fact. Docs and release notes identify custom providers, GitHub integration, and provider setup surfaces.
- `runtime_modes`: Source-backed fact. OpenCode supports terminal/TUI, desktop, IDE extension, server, noninteractive run, GitHub Action integration, and ACP server modes.
- `cross_harness_import_compatibility`: Unknown. The checked sources do not prove native import of other harness conventions.
- `lifecycle_reload_update`: Needs more evidence. Release notes mention session warp and utility-process changes; config/plugin reload behavior needs a sourced lifecycle model.

## Evidence Classification

This note distinguishes source-backed facts, local observations, implementation inferences, hypotheses, unsupported claims, unknowns, and not-applicable surfaces. Release and docs facts are source-backed; external scheduling is a constrained source-backed fact, not native scheduler support.

## Cross-Harness Import And Compatibility

OpenCode's GitHub integration and ACP surface are connectors, not evidence of native import for Codex, Claude Code, Cursor, Hermes, or OpenClaw bundles. Compatibility should remain unknown until a first-party source names a bridge.

## Memory-Like Surfaces

Snapshots and context pressure are memory-like signals, but the checked source set does not prove persistence scope, retrieval trigger, write authority, freshness, privacy, or stable API shape.

## Schema Pressure

OpenCode motivates accepted schema pressure for native-versus-external scheduling, permission posture, runtime modes, command templates, plugin hook event taxonomy, and provider connector fields.

## Analysis Angle Notes

OpenCode can be modeled through a local TUI Capability Analysis Angle, a desktop/server angle, or a GitHub Action angle. A future Capability State Graph should keep native scheduler absence distinct from external runner support.

## Local Observations

No local OpenCode binary, desktop process, config, plugin directory, or GitHub workflow was inspected for this story.

## Major Uncertainty

The migrated profile records `1.14.33`; current release evidence is `1.14.41`. The exact installed local version and plugin lifecycle behavior remain environment-scoped.

## Scratch Artifact Disposition

GitHub release API output and Firecrawl extraction output were treated as instance-scoped scratch. Durable conclusions are the source URLs and curated surface findings above.
