# Agent Equipment Config

Status: Equipment Shop Card

## Fit

Use Agent Equipment Config when a Smith, Wielder, or Outfitter needs shared,
layered configuration for agent equipment without making each equipment line
rebuild policy loading, provenance, effective-config explanation, config diff,
or local Config source-write gates.

It fits local repository and session configuration work. It does not fit secret
value resolution, harness enforcement, external mutation, package discovery, or
plugin installation.

## What is stocked

The stocked slice is the published local Config runtime and its current
integration surfaces:

- CLI operations in
  [`tools/agent_equipment_config.py`](../../../tools/agent_equipment_config.py)
  for resolving, validating, diffing, onboarding, proposing, planning,
  applying reviewed Config changes, and previewing or applying registered
  migrations.
- MCP parity through the importable runtime and the standalone stdio server in
  [`tools/agent_equipment_config_mcp_server.py`](../../../tools/agent_equipment_config_mcp_server.py).
- Wielder, Smith, and Outfitter guidance in the
  [runtime guide](../agent-equipment-config.md) and
  [integration guide](../agent-equipment-config-integration.md).
- Example Config layers under [`templates/config/`](../../../templates/config/).

## Delivery status

Delivery compliance: pending.

The canonical stock record is
[`inventory/equipment.toml`](../../../inventory/equipment.toml). The linked
[Inspection and Test Plan](../inspection-test-plans/agent-equipment-config.md)
keeps delivery compliance pending until Codex gear-up validation passes.

## Gear-up paths

- Use the CLI when shell commands are the clearest evidence surface:

  ```bash
  python3.14 tools/agent_equipment_config.py config validate \
    --layer templates/config/agent-equipment-config-example.toml \
    --issue-tracker-ops \
    --requested-behavior advisory
  ```

- Use the stdio MCP server when the harness can launch a local MCP process:

  ```bash
  python3.14 tools/agent_equipment_config_mcp_server.py
  ```

- Use the [Config integration guide](../agent-equipment-config-integration.md)
  when adding Config awareness to equipment, harness adapters, hooks, scripts,
  plugins, or local workflows.

## Component manifest

- Required: Config CLI runtime,
  [`tools/agent_equipment_config.py`](../../../tools/agent_equipment_config.py).
- Required: stdio MCP server wrapper,
  [`tools/agent_equipment_config_mcp_server.py`](../../../tools/agent_equipment_config_mcp_server.py).
  MCP behavior is specified in
  [`specs/agent-equipment-config/mcp-tools.md`](../../../specs/agent-equipment-config/mcp-tools.md).
- Required: runtime and integration docs,
  [runtime guide](../agent-equipment-config.md),
  [integration guide](../agent-equipment-config-integration.md), and
  [Equipment Blueprint](../../../specs/agent-equipment-config/).
- Optional: example Config layers,
  [`templates/config/agent-equipment-config-example.toml`](../../../templates/config/agent-equipment-config-example.toml),
  [`templates/config/example.toml`](../../../templates/config/example.toml),
  and
  [`templates/config/issue-tracker-ops-plain-handoff.toml`](../../../templates/config/issue-tracker-ops-plain-handoff.toml).
- Planned: Codex plugin, tracked by #154.
- Planned: Config routing skill, tracked by #155.
- Planned: Codex gear-up validation, tracked by #156.
- Unavailable: secret value resolution. Config records secret references and
  leaves provider lookup, authentication, value lifetime, and private audit to
  the provider-owning surface.

## Inspection and evidence

- Delivery gate:
  [Agent Equipment Config Inspection and Test Plan](../inspection-test-plans/agent-equipment-config.md).
- Story closeout:
  [Agent Equipment Config Delivery Retrofit Closeout](../../closeout/agent-equipment-config-delivery-retrofit.md).
- Runtime evidence:
  [Validation Plan](../../../specs/agent-equipment-config/validation-plan.md)
  and
  [Closeout Evidence Plan](../../../specs/agent-equipment-config/closeout-evidence-plan.md).
- Security evidence:
  [Security and Control Classification](../../../specs/agent-equipment-config/security-control-classification.md)
  and the repository
  [threat model](../../security/threat-model.md).

## Support and lifecycle

The published runtime slice is supported as local repository equipment. Its
delivery compliance remains pending until Codex gear-up validation passes and
the linked ITP records that result.

Rollback is documentation-only for this retrofit: remove or revise the stock
record and its linked card, ITP, closeout, and storefront routes if a later
review finds the slice should not be stocked.
