# MCP Tools: Agent Equipment Config

Status: Equipment Blueprint
Promotion state: planned

Agent Equipment Config exposes MCP parity for the safe CLI/runtime slice through
typed tool definitions and structured tool-call results. The importable runtime
source is `tools.agent_equipment_config.mcp_tool_definitions()` for tool
metadata and `tools.agent_equipment_config.call_mcp_tool()` for direct tool
dispatch. A harness-specific MCP server can wrap those functions without
redefining Config behavior.

This spec describes desired behavior and the current runtime boundary. It does not implement Agent Equipment.

## Tool definition contract

Each Config MCP tool definition includes:

- `name`, `title`, `description`, `inputSchema`, and `outputSchema`;
- MCP `annotations` for read-only, destructive, idempotent, and open-world
  hints;
- `x-agent-armory` metadata for CLI parity, read/write classification, auth
  source, side effects, approval requirements, mutation gate, and failure
  modes.

Tool-call results return an MCP-style object with text `content` and
`structuredContent`. The structured content contains the tool name, paired CLI
operation, read/write classification, and the redacted runtime result.
The direct dispatcher rejects arguments outside the published input schema and
requires every schema-required argument before invoking runtime behavior.

## Operation map

| CLI operation | MCP tool | Read/write classification |
| --- | --- | --- |
| `config resolve` | `config.resolve` | read-only |
| `config validate` | `config.validate` | read-only |
| `config diff` | `config.diff` | read-only |
| `onboard config` | `onboard.config` | read-only |
| `migrate config preview` | `migrate.config_preview` | read-only |
| `migrate config apply` | `migrate.config_apply` | local write |

All tools are closed-world local Config operations. They do not call networks,
resolve secret values, mutate external systems, or discover config paths.

## Shared inputs

Read operations that load Config accept:

- `layer_paths`: explicit authored TOML layer paths;
- `plain_handoff_paths`: explicit plain handoff TOML paths promoted as session
  overrides;
- `fragments`: schema fragments to register before validation;
- `requested_behavior`: `advisory` or `mutation`.

The current fragment registry exposes `issue_tracker_ops`. Arbitrary fragment
registration belongs to a later integration surface.

`config.diff` accepts typed `before` and `after` JSON objects rather than file
paths. The CLI fallback remains `config diff --before <file> --after <file>`
for command-line evidence comparison.

## Tool specs

### `config.resolve`

Purpose: resolve effective Config with values, provenance, diagnostics, safety
status, migration previews, plain-handoff promotion evidence, and enforcement
projection.

Classification: read-only. Auth source: none. Side effects: none. Approval
requirements: none.

Failure modes: input validation failure, config parse failure, schema conflict,
policy diagnostic.

### `config.validate`

Purpose: return lower-noise readiness evidence without full effective Config by
default. The report includes pass/fail status, Config Safety Status, authority
readiness, fragment readiness, diagnostics, and enforcement projection.

Classification: read-only. Auth source: none. Side effects: none. Approval
requirements: none.

Failure modes: input validation failure, config parse failure, blocking
validation, policy diagnostic.

### `config.diff`

Purpose: compare two effective Config objects and report value,
secret-reference identity, diagnostic, and safety-status changes.

Classification: read-only. Auth source: none. Side effects: none. Approval
requirements: none.

Failure modes: input validation failure, malformed effective Config input.

### `onboard.config`

Purpose: produce first-run, resume, restart, or revise planning output for
Config onboarding.

Classification: read-only. Auth source: none. Side effects: none. Approval
requirements: none.

Failure modes: input validation failure, config parse failure, unknown revise
section, policy diagnostic.

### `migrate.config_preview`

Purpose: preview registered migrations, refusals, projected effective Config,
and audit records without rewriting sources.

Classification: read-only. Auth source: none. Side effects: none. Approval
requirements: none.

Failure modes: input validation failure, config parse failure, migration
refusal, policy diagnostic.

### `migrate.config_apply`

Purpose: apply registered migrations to eligible local TOML sources and return
applications, refusals, write failures, projected effective Config, and audit
records.

Classification: local write. Auth source: explicit apply authority. Side
effects: eligible local TOML source rewrite. Approval requirements: explicit
apply authority.

Mutation gate: eligible source category, trusted provenance, usable projected
Config, explicit apply authority, and final source precondition check.

Failure modes: input validation failure, config parse failure, missing
migration apply authority, ineligible source refusal, source precondition
failure, partial local write failure.

Rollback: restore the source file from version control or the recorded diff.

## Fallback path

Agents should prefer MCP when a harness exposes these tools because the input
and output contracts are typed. Agents should fall back to the paired fluent CLI
operation when MCP is unavailable, when a human needs copyable commands, or
when command-line evidence comparison is clearer for review.
