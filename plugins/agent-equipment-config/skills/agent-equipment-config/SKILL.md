---
name: agent-equipment-config
description: Use when Smith, Wielder, or Outfitter work involves Agent Equipment Config policy layers, effective-config explanation, migration preview, or reviewed local Config writes.
---

# Agent Equipment Config

Use this skill when work involves Agent Equipment Config policy layers,
effective-config explanation, config diff, onboarding, migration preview, or
reviewed local Config writes.

## Route

1. Read `docs/equipment/agent-equipment-config.md` for runtime behavior,
   boundaries, and CLI commands.
2. Read `docs/equipment/agent-equipment-config-integration.md` before wiring
   Config into a harness, plugin, hook, skill, script, or MCP workflow.
3. Read `specs/agent-equipment-config/mcp-tools.md` before using or changing
   MCP tool contracts.
4. Use the `agent-equipment-config` MCP server when Codex has launched it; use
   `python3.14 tools/agent_equipment_config.py` as the CLI fallback.

## Local Writes

Prefer read-only inspect, validate, explain, diff, and migration-preview
operations while shaping the work.

Use `config.apply` or `migrate.config_apply` only when a reviewed plan is ready
and the call includes `apply_authority = "operator"`. The bundled Codex
`PreToolUse` hook denies those local-write MCP calls when that authority is
missing.

## Boundaries

Agent Equipment Config records secret references but does not resolve secret
values. Harnesses, plugins, hooks, scripts, and operators own discovery,
provider lookup, network calls, and broader enforcement outside the Config
runtime.
