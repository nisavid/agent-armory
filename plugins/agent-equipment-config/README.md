# Agent Equipment Config Codex Plugin

This plugin equips Codex with the Agent Equipment Config routing skill, a
plugin-local MCP launcher, and a guard hook for Config local-write MCP tools.

## Install

The Armory repository exposes this plugin through
`.agents/plugins/marketplace.json` as the `agent-armory` repo marketplace. Codex
installs the source from `./plugins/agent-equipment-config` into its plugin
cache, so the plugin-local launcher uses the configured live Armory checkout at
runtime.

Do not copy secrets into plugin files. The MCP config passes through only
`AGENT_ARMORY_ROOT`. The plugin manifest uses `mcpServers` to point at
`.mcp.json`; the referenced MCP config uses Codex's documented direct MCP
server map.

## MCP Checkout Binding

The plugin MCP entry runs from the installed plugin root and launches
`./mcp/agent_equipment_config_launcher.py`. The launcher starts the standalone
server only when `AGENT_ARMORY_ROOT` points at a checkout, or when the process
cwd is inside a checkout, containing:

- `tools/agent_equipment_config_mcp_server.py`
- `inventory/equipment.toml`
- `.agents/plugins/marketplace.json`

If neither source contains those Armory markers, the launcher exits closed with
install guidance instead of starting an unexpected process.

After validation, the launcher changes directory to the live Armory checkout
before executing the standalone MCP server so relative Config paths resolve
against the repository, not the installed plugin cache.

## Hook Trust

`hooks/hooks.json` registers a `PreToolUse` command hook through
`python3.14 -P "${PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}/hooks/config_write_guard.py"`. The isolated
startup flag avoids plugin-cache import shadowing, and the quoted path is safe
for plugin cache paths containing whitespace. The hook ignores unrelated MCP
tools and denies Agent Equipment Config local-write MCP calls unless
`apply_authority = "operator"` is present in the tool input.

Codex hook trust and MCP approval prompts remain host policy surfaces. This
plugin asks Codex to prompt by default and specifically prompt for
`config.apply` and `migrate.config_apply`.

## Validate

Run these checks from the Armory checkout:

```bash
python3.14 -m unittest tests.test_agent_equipment_config_codex_plugin
python3.14 tools/validate_armory_integrity.py
```

Use the routing skill for Smith, Wielder, and Outfitter workflows; use
`docs/equipment/agent-equipment-config-integration.md` before changing adapter
behavior.
