# Harness Components

Status: Forge Seed

Harness Components are reusable behavior integrated into an Agent Harness. Smiths choose components by required behavior, evidence, context cost, control needs, and target harness support.

## Skills

Skills are model-facing procedural packages. Use them for judgment, sequencing, examples, fallback behavior, source-quality discipline, and output contracts.

Keep skills thin. Move deterministic logic to scripts, project truth to local docs, hard policy to hooks or permissions, and large reference material behind on-demand paths.

Use `templates/skill/` for future skill drafts. The seed template is not itself
Published Agent Equipment.

## MCP/tools

MCP/tools expose typed local or external capabilities. Use them for live state, structured operations, reusable service interfaces, auth centralization, pagination, and cross-client reuse.

Every mutation-capable MCP/tool needs side-effect classification, auth source, approval requirements, failure modes, and an appropriate mutation gate.

Use `templates/mcp/tool-spec.md` before implementing or publishing a tool
definition.

## hooks

Hooks run around harness lifecycle events. Use them to block, require approval, redact, log, annotate, route, validate, or inject small context.

Hooks should be narrow, explain their decisions, and fail in a mode appropriate to risk. Do not hide long workflows or broad reasoning inside hooks.

Use `templates/hook/` to keep side effects, approval behavior, failure handling,
and the exported hook contract visible before implementation.

## Agent Profiles

Agent Profiles define reusable specialized Agent configurations.

Many harness and plugin file layouts call these configurations `agents`; the
Forge prose term remains Agent Profile.

Use an Agent Profile when the task needs distinct identity, authority, model/runtime preference, tool access, permissions, autonomy, context, skills, or output contract. Avoid profile proliferation for small prompt variations.

Use `templates/agents/` to make mission, tools, permissions, model
preferences, and config explicit.

## Harness Plugins

Harness Plugins package Harness Components for installation, update, versioning, sharing, or distribution.

A plugin may include skills, hooks, MCP/tool definitions, Agent Profiles, scripts, docs, services, commands, and config defaults. The plugin boundary should communicate a coherent capability, not merely collect unrelated files.

Use `templates/plugin/manifest.toml` to state components, version, and permissions
at the plugin boundary.

## scripts

Scripts perform deterministic work: parsing, validation, changed-file mapping, source inspection, formatting, report generation, or safe explicit side effects.

Agent-facing scripts should provide help text, stable human or JSON output, clear exit codes, safe defaults, explicit destructive flags, and tests or fixtures where practical.

Use `templates/script/` for deterministic script contracts and a minimal Python
validator example.

## local docs

Local docs store canonical project truth: policy, architecture, runbooks, evidence, maintenance rules, source-disposition/provenance records, and troubleshooting guidance.

Use docs when humans and Agents need the same current rule. Link or route to docs from skills rather than duplicating the full guidance.

## config

Config stores durable parameters and local choices: thresholds, timeouts,
allowlists, autonomy levels, enabled tools, hook modes, model selections,
scheduling periods, and install preferences.

Config should use typed values and human-friendly names. Store secret
references, not secrets.

Agent Equipment Config is the planned shared equipment for robust, layerable,
composable, adaptable, and enforceable config. Equipment-specific config should
still have a plain session-scoped shape so the equipment can run, hand off, and
later ingest config when shared config equipment is unavailable.

Use `templates/config/` to capture ownership, autonomy, enabled state, review,
and approval boundaries.
