# Research Note: Codex

Status: issue #44 research note

## Version Basis

Checked at: 2026-05-08T19:32:00-04:00.
Version basis: GitHub latest release `rust-v0.130.0` published 2026-05-08, plus first-party OpenAI Codex docs for integration surfaces. The canonical profile is not changed in this story.

## Source Set

- [Codex release `rust-v0.130.0`](https://github.com/openai/codex/releases/tag/rust-v0.130.0)
- [Codex skills](https://developers.openai.com/codex/skills)
- [Codex plugins](https://developers.openai.com/codex/plugins)
- [Codex hooks](https://developers.openai.com/codex/hooks)
- [Codex subagents](https://developers.openai.com/codex/subagents)
- [Codex automations](https://developers.openai.com/codex/app/automations)
- [Codex noninteractive mode](https://developers.openai.com/codex/noninteractive)
- [Codex config reference](https://developers.openai.com/codex/config-reference)

## Surface Findings

- `instructions_context`: Source-backed fact. Skills, plugins, subagents, automations, and noninteractive runs all carry instruction or prompt material. The current first-slice profile treats this family as unknown because migrated evidence was not shaped to separate instruction load paths from component presence.
- `skills`: Source-backed fact. Skills are reusable instructions and can be explicitly or implicitly activated.
- `mcp_tools`: Source-backed fact with schema pressure. Plugin docs describe MCP servers as bundled plugin components, and release notes mention built-in MCP runtime work. The current profile lacks a dedicated claim because the migrated evidence keywording did not map plugin-bundled MCP to the MCP family.
- `hooks_events`: Source-backed fact. Hooks are event-triggered scripts in the agentic loop, including permission and tool-use events.
- `plugins_bundles`: Source-backed fact. Plugins are installable bundles that can contain skills, apps, MCP servers, hooks, and sharing metadata.
- `agent_profiles_subagents`: Source-backed fact. Codex has built-in and custom subagent/profile-like definitions with sandbox inheritance.
- `memory_context_retrieval`: Needs more evidence. Source extraction found memory-like references and automations can preserve thread context, but the source set did not establish a stable shared memory API for profile claims.
- `config_settings`: Source-backed fact. Codex has config-file surfaces for agent, sandbox, approval, hooks, and provider settings.
- `permissions_approvals_sandboxing`: Source-backed fact. Noninteractive mode, automations, hooks, and subagents are constrained by sandbox and approval settings.
- `scheduling_automation`: Source-backed fact. App automations support recurring schedules, and `codex exec` supports external scheduling through CI or cron.
- `commands_shortcuts`: Needs more evidence. CLI and app commands exist, but the canonical surface needs a sourced command taxonomy before profile enrichment.
- `providers_connectors`: Source-backed fact. GitHub Actions and app integrations are connector surfaces; release notes also add Bedrock auth support.
- `runtime_modes`: Source-backed fact. Codex exposes interactive app/CLI use, noninteractive `codex exec`, app-server, remote-control, and GitHub Action modes.
- `cross_harness_import_compatibility`: Unknown. Skills and plugins are reusable inside Codex installations, but the checked source set does not prove native import of another harness's bundle convention.
- `lifecycle_reload_update`: Source-backed fact with schema pressure. Release notes say live app-server threads pick up config changes without restart; skills and plugins have reload/update behavior that should be recorded per component, not as one flat claim.

## Evidence Classification

This note distinguishes source-backed facts, local observations, implementation inferences, hypotheses, unsupported claims, unknowns, and not-applicable surfaces. Source-backed facts are tied to first-party URLs. Implementation inferences are limited to mapping those facts onto the current surface-family rubric.

## Cross-Harness Import And Compatibility

No first-party source in this check proves native Codex import of Claude Code, Cursor, OpenCode, Hermes, or OpenClaw equipment. The profile schema needs a compatibility field that can represent "no proven bridge" separately from "unknown because not checked" and separately from same-harness reuse of plugins or skills.

## Memory-Like Surfaces

Codex has context-preserving automations and memory-like claims in docs, but the source set did not establish a uniform memory API, write authority, freshness contract, or privacy boundary. Treat this as a first-class memory-like surface with `needs more evidence` disposition.

## Schema Pressure

Codex motivates accepted schema pressure for evidence classification, component reload behavior, MCP/tool nested details, automation runner details, version-observation records, and memory-like surface metadata. It also motivates rejected pressure against adding downstream Smith guidance to profiles.

## Analysis Angle Notes

Two Capability Analysis Angles could model Codex automation: a scheduling angle centered on app automations and a runtime-mode angle centered on `codex exec`. A future Capability State Graph should keep both until the profile can express trigger, runner, sandbox, and output surfaces separately.

## Local Observations

No local Codex binary, Codex app state, plugin install, automation state, or app-server state was inspected for this story.

## Major Uncertainty

The current profile predates `rust-v0.130.0`; this story records drift pressure but does not mutate the canonical profile. Memory-like behavior and cross-harness import remain unresolved.

## Scratch Artifact Disposition

GitHub release API output and Firecrawl extraction output were treated as instance-scoped scratch. Durable conclusions are the source URLs and the curated surface findings above.
