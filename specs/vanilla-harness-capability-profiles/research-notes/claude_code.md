# Research Note: Claude Code

Status: issue #44 research note

## Version Basis

Checked at: 2026-05-08T19:32:00-04:00.
Version basis: GitHub latest release `v2.1.136` published 2026-05-08, plus first-party Claude Code docs for integration surfaces. The canonical profile is not changed in this story.

## Source Set

- [Claude Code release `v2.1.136`](https://github.com/anthropics/claude-code/releases/tag/v2.1.136)
- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [Claude Code MCP](https://code.claude.com/docs/en/mcp)
- [Claude Code hooks](https://code.claude.com/docs/en/hooks)
- [Claude Code subagents](https://code.claude.com/docs/en/sub-agents)
- [Claude Code plugins reference](https://code.claude.com/docs/en/plugins-reference)
- [Claude Code settings](https://code.claude.com/docs/en/settings)
- [Claude Code routines](https://code.claude.com/docs/en/routines)
- [Claude Code desktop scheduled tasks](https://code.claude.com/docs/en/desktop-scheduled-tasks)
- [Claude Code scheduled tasks](https://code.claude.com/docs/en/scheduled-tasks)

## Surface Findings

- `instructions_context`: Source-backed fact. Skills, subagents, routines, and scheduled tasks carry prompts and instructions. Skill dynamic context also runs shell commands before skill content is sent.
- `skills`: Source-backed fact. Skills live at enterprise, personal, project, and plugin scopes, can include structured frontmatter, and can run in a subagent with `context: fork`.
- `mcp_tools`: Source-backed fact. MCP supports remote HTTP, remote SSE, local stdio, dynamic tool updates, push-message channels, OAuth, resources, and managed configuration.
- `hooks_events`: Source-backed fact. Plugin and settings docs identify hook surfaces and allow controls.
- `plugins_bundles`: Source-backed fact. Plugins can package skills, agents, hooks, MCP servers, LSP servers, monitors, themes, and manifest metadata.
- `agent_profiles_subagents`: Source-backed fact. Subagents are a supported surface and plugin agents can be invoked automatically when appropriate.
- `memory_context_retrieval`: Unknown. Routines and scheduled tasks can reuse prompt/config state, and MCP resources can be referenced, but the checked pages do not define a stable memory API.
- `config_settings`: Source-backed fact. Settings use managed, user, project, local, and command-line precedence scopes.
- `permissions_approvals_sandboxing`: Source-backed fact. Settings include permission rules, sandbox settings, hook allow controls, and per-task permission modes.
- `scheduling_automation`: Source-backed fact. Routines support scheduled, API, and GitHub triggers; desktop scheduled tasks run locally while the app is open; session-scoped scheduled tasks are separate.
- `commands_shortcuts`: Source-backed fact with schema pressure. Skills and plugins create slash-command surfaces, and routines can be managed from `/schedule`; profile enrichment needs a command taxonomy rather than a boolean.
- `providers_connectors`: Source-backed fact. Routines can use connected MCP connectors; MCP can connect to external tools and data sources.
- `runtime_modes`: Source-backed fact. Claude Code spans CLI sessions, Desktop scheduled tasks, cloud routines, plugin monitors, and remote MCP connections.
- `cross_harness_import_compatibility`: Unknown. Claude Code supports plugins and skills but the checked source set does not prove native import of other harness conventions.
- `lifecycle_reload_update`: Source-backed fact. Skills have live change detection, and MCP supports `list_changed` notifications for tools, prompts, and resources.

## Evidence Classification

This note distinguishes source-backed facts, local observations, implementation inferences, hypotheses, unsupported claims, unknowns, and not-applicable surfaces. Release and docs facts are source-backed; mapping them to profile shape is implementation inference.

## Cross-Harness Import And Compatibility

No checked first-party Claude Code source proves native import of Codex, Cursor, OpenCode, Hermes, or OpenClaw equipment. Skills may share conventions with other Agent Skills adopters, but profile enrichment should represent that as compatibility evidence only when a source names the bridge.

## Memory-Like Surfaces

The checked pages show prompt/config persistence and external resources, not a stable shared memory API. Memory-like claims need fields for retrieval timing, mutability, freshness, write authority, and privacy before profile enrichment.

## Schema Pressure

Claude Code motivates accepted schema pressure for scoped configuration precedence, lifecycle reload behavior, automation trigger classes, command surfaces, plugin component manifests, and memory-like unknowns.

## Analysis Angle Notes

Scheduled behavior can be modeled by a cloud-routine Capability Analysis Angle, a desktop scheduled-task angle, and a session task angle. A future Capability State Graph should distinguish runner locus, machine-awake dependency, trigger authority, and permission mode.

## Local Observations

No local Claude Code binary, Desktop app, plugin state, MCP configuration, or routine state was inspected for this story.

## Major Uncertainty

The migrated profile records `2.1.126`; current release evidence is `2.1.136`. The exact installed binary and enterprise-managed settings remain environment-scoped.

## Scratch Artifact Disposition

GitHub release API output and Firecrawl extraction output were treated as instance-scoped scratch. Durable conclusions are the source URLs and curated surface findings above.
