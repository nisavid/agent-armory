# Agent Equipment Config Codex Plugin Security Closeout

Scope: repo marketplace entry, Codex plugin manifest, bundled MCP config,
plugin-local launcher, `PreToolUse` guard hook, routing skill, and validator
coverage for the Agent Equipment Config Codex plugin.

## Boundary

The plugin exposes the existing standalone Config MCP server to Codex. It does
not add a network endpoint, secret resolver, provider mutation path, or Config
runtime implementation. The plugin runs from the Codex plugin cache and binds
back to a live Armory checkout only when `AGENT_ARMORY_ROOT` or the process
working directory resolves to a checkout containing these markers:

- `tools/agent_equipment_config_mcp_server.py`
- `inventory/equipment.toml`
- `.agents/plugins/marketplace.json`

The MCP launcher changes directory to the resolved checkout before executing
`tools/agent_equipment_config_mcp_server.py` with the absolute path of the
current Python interpreter.

## Controls

- `.mcp.json` uses a direct local server map, `python3.14`, plugin-local
  launcher args, `env_vars = ["AGENT_ARMORY_ROOT"]`, default prompt approval,
  and prompt overrides for `config.apply` and `migrate.config_apply`.
- No static secrets, HTTP MCP endpoint, broad server environment pass-through,
  or alternate executable path is allowed by the validator.
- The launcher rejects lookalike roots without the Armory marketplace marker,
  uses an absolute interpreter path and an `AGENT_ARMORY_ROOT`-only server
  environment for the final `exec`, and fails closed with install guidance when
  no trusted checkout is found.
- The guard hook no-ops unrelated tools and denies Config local-write MCP calls
  unless the tool input includes `apply_authority = "operator"`.
- The validator statically restricts launcher and hook imports, functions,
  entrypoints, constants, decorators, command paths, MCP config, and hook shape
  before running bounded behavior probes.
- Codex hook trust and MCP approval prompts remain host policy surfaces.

## Review Disposition

The review loop found actionable validator gaps: launchers without `_argv`
assignment could pass static validation, reviewed functions could carry
decorators that run during import, stock inventory could omit the plugin
component paths while the plugin files still existed, and launcher failure
branches could pass with nonterminal return or misplaced module-entrypoint
shapes. The validator now requires the `_argv` assignment, rejects decorators on
reviewed launcher and guard functions before behavior probes import plugin code,
checks inventory component projection, accepts only terminal failure returns in
the reviewed launcher guards, and requires the module entrypoint to be final
after `launch()`.

A fresh isolated Codex prototype using `CODEX_HOME` under `/tmp` installed
`agent-equipment-config@agent-armory` from `.agents/plugins/marketplace.json`
and exposed the bundled MCP server from the cached plugin path. That confirms
the marketplace source path is resolved from the marketplace root, not the JSON
file's directory.

## Evidence

This committed closeout is the durable security evidence record for the Codex
plugin delivery. The Codex Security diff scan covered the executable plugin
boundary and found no reportable findings. Instance-scoped scan output stayed in
scratch storage; the durable conclusion is this document's scope, controls, and
findings disposition.

Validation commands completed for the security-relevant surface:

- `python3.14 -m unittest tests.test_agent_equipment_config_codex_plugin`
- `python3.14 -m unittest tests.test_validate_armory_integrity`
- `python3.14 -m unittest`
- `python3.14 tools/harness_capability_profiles.py validate --json`
- `python3.14 tools/validate_armory_integrity.py --final-closeout --json`
- `git diff --check`
