# Agent Equipment Config Integration Guide

Status: Published integration guide
Promotion state: published

Use this guide when a Smith adds Agent Equipment Config support to equipment,
when a Wielder supplies Config to existing equipment, or when an Outfitter maps
Config into a harness, plugin, hook, skill, CLI, or MCP surface.

Authoritative contracts live in the
[Agent Equipment Config PRD](../prd/agent-equipment-config.md), the
[runtime guide](agent-equipment-config.md), and the
[Equipment Blueprint](../../specs/agent-equipment-config/). This guide explains
how those contracts fit together during integration. It does not replace the
spec, and it does not define new Config operation surfaces.

## Integration contract

Agent Equipment Config has an explicit-load contract:

1. A caller discovers the relevant layer and handoff paths.
2. The caller registers the consuming equipment's schema fragment.
3. The caller chooses the requested behavior, such as `advisory` or
   `mutation`.
4. Config resolves effective values, diagnostics, provenance, safety status,
   migration previews, and enforcement projection.
5. The consuming equipment turns that evidence into a consumer action decision.

The runtime does not discover files, import equipment packages, resolve secret
values, mutate external systems, or enforce harness controls. Source writes are
limited to registered `migrate config apply` operations on eligible local TOML
sources. General proposal, patch, revision, and apply workflows belong to the
Config Authoring Surfaces follow-up bucket.

The product operation vocabulary is:

| User intent | Product operation | Current runtime basis |
| --- | --- | --- |
| Read, explain, and trace effective Config | `config resolve` | `effective-config` |
| Check readiness without dumping full output | `config validate` | effective-config validation and safety classification |
| Compare two effective outputs | `config diff` | `config-diff` |
| Plan first-run, resume, restart, or revise work | `onboard config` | `onboarding-plan` |
| Preview registered source migrations | `migrate config preview` | `migration-apply` without `--apply` |
| Apply registered source migrations | `migrate config apply` | `migration-apply --apply` |

The fluent CLI commands are the supported invocation surface. The runtime
command names remain available for implementation debugging and evidence
comparison.

MCP parity uses the same operation families with typed inputs and structured
outputs. Use MCP when the harness exposes these tools and an agent can operate
through typed arguments. Use the fluent CLI when MCP is unavailable, when a
human needs a copyable command, or when command output is the clearer review
artifact. See the [runtime guide's MCP parity section](agent-equipment-config.md#mcp-parity)
and the [MCP tools specification](../../specs/agent-equipment-config/mcp-tools.md)
for the authoritative MCP-to-CLI map.

## Smith path

Start with the equipment's plain session handoff. Keep that shape useful when
shared Config is absent, then register the same shape as a namespaced schema
fragment when shared Config is available.

A Config-aware equipment integration should:

- own its namespace, defaults, required fields, semantic validators, and
  registered migrations;
- pass layer paths and plain handoff paths explicitly;
- pass the requested behavior before evaluating effective Config;
- inspect `safety_status`, diagnostics, Policy Authority, secret references,
  migration previews, and `enforcement_projection`;
- produce a consumer action decision before mutation, external calls, hook
  execution, workflow changes, or durable publication;
- fail closed for mutation when the consumer decision is `blocking` or
  `unsupported`;
- keep generic layering, provenance, migration previews, and edit boundaries in
  Agent Equipment Config instead of reimplementing them locally.

Python consumers use the importable runtime when they need a direct decision:

```python
from pathlib import Path

from tools import agent_equipment_config

config = agent_equipment_config.evaluate_consumer_config(
    [Path("templates/config/agent-equipment-config-example.toml")],
    [agent_equipment_config.issue_tracker_ops_fragment()],
    equipment="issue_tracker_ops",
    requested_behavior="advisory",
    required_capabilities=[],
    supported_capabilities=["tracker_read", "tracker_write"],
)

decision = config["consumer_action_decision"]
if decision["state"] in {"blocking", "unsupported"}:
    raise RuntimeError(decision["reason"])
```

Use `consumer_action_decision` directly when the equipment already has
effective-config output and only needs to classify behavior against its
capability boundary.

## Wielder path

Choose Config sources by ownership and durability:

| Source | Use for | Portability |
| --- | --- | --- |
| committed durable config | project, repository, organization, or tracker policy | durable project truth |
| local-only operator config | machine-local choices and operator preferences | local only |
| checkout-local state | state tied to one checkout | local only |
| generated cache or state | generated evidence and cache state | generated, not source truth |
| secret reference source | pointers to secret providers or names | no secret values |
| session override | per-session choices and plain handoffs | session scoped |

Inspect effective Config before relying on it:

```bash
python3.14 tools/agent_equipment_config.py config resolve \
  --layer templates/config/agent-equipment-config-example.toml \
  --issue-tracker-ops \
  --requested-behavior advisory
```

Use validation output when a script or hook needs a lower-noise pass/fail
surface:

```bash
python3.14 tools/agent_equipment_config.py config validate \
  --layer templates/config/agent-equipment-config-example.toml \
  --issue-tracker-ops \
  --requested-behavior mutation
```

For the current Issue Tracker Ops consumer, pass Config to the adapter with
`--config-layer` or a plain handoff with `--config-plain-handoff`:

```bash
python3.14 tools/issue_tracker_ops.py comment \
  --repo OWNER/REPO \
  --issue-number 123 \
  --body "Config-aware dry-run comment" \
  --config-layer templates/config/agent-equipment-config-example.toml
```

The example layer keeps Issue Tracker Ops in `dry-run` mode. If a caller also
passes `--execute`, the adapter must refuse the write unless effective Config
supports live tracker mutation and the Issue Tracker Ops consumer decision is
non-blocking.

Use a plain handoff when shared Config is absent but the consuming equipment has
a narrow session shape:

```bash
python3.14 tools/issue_tracker_ops.py comment \
  --repo OWNER/REPO \
  --issue-number 123 \
  --body "Config-aware dry-run comment" \
  --config-plain-handoff templates/config/issue-tracker-ops-plain-handoff.toml
```

Plain handoffs are session overrides. They are useful for continuity and
diagnostics, but they are not durable project policy.

## Outfitter path

Outfitters decide where a harness or bundle discovers inputs and exposes Config
operations. Keep these responsibilities separate:

- Harness, plugin, hook, skill, or script code discovers candidate paths,
  chooses applicable sources, orders same-precedence inputs, and registers
  schema fragments.
- Agent Equipment Config resolves and validates the supplied inputs.
- Consuming equipment turns Config evidence into behavior-specific action
  decisions.
- Harness controls decide whether a decision becomes advisory evidence,
  approval friction, or a hard block.

Expose the fluent CLI operation names and MCP parity names from the PRD when
designing user-facing surfaces. Use runtime commands only for implementation
debug evidence. Do not turn a skill or prose guide into the product operation
surface.

When exposing MCP, wrap `tools.agent_equipment_config.mcp_tool_definitions()`
and `tools.agent_equipment_config.call_mcp_tool()` rather than hand-copying
the Config operation behavior. The current MCP layer classifies
`config.resolve`, `config.validate`, `config.diff`, `onboard.config`, and
`migrate.config_preview` as read-only. It classifies `migrate.config_apply` as
a local write that requires per-call `apply_authority = "operator"` for the MCP
tool, plus the migration apply contract's source category, trusted provenance,
projected safety, precondition, and audit gates. See
[`migrate.config_apply`](../../specs/agent-equipment-config/mcp-tools.md#migrateconfig_apply)
and [Migration apply](agent-equipment-config.md#migration-apply) for the full
contract.

Before publishing an integration surface, document:

- which layer categories the surface can discover;
- which categories are committed, local-only, generated, secret-reference, or
  session-scoped;
- which Config operation family the surface exposes;
- which schema fragments it can register;
- what side effects the consuming equipment may perform;
- how `blocking` and `unsupported` decisions are enforced or handed back;
- where audit evidence and refusal records appear.

## Integration checklist

- Link to the Config PRD, runtime guide, and Equipment Blueprint instead of
  restating unstable internal detail.
- Keep all source selection explicit; do not add hidden default discovery to
  the core runtime.
- Keep secret values out of Config and examples.
- Keep local-only paths out of durable examples.
- Demonstrate at least one dry-run path before live mutation.
- Treat `blocking` and `unsupported` as stop signals for mutation-capable
  behavior.
- Record validation, security, and documentation closeout evidence for every
  implementation slice that changes executable code, Config policy, operation
  surfaces, source writes, or harness enforcement.
