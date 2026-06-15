# Equipment Inspection and Test Plan: Agent Equipment Config

Status: Equipment Inspection and Test Plan

## Scope

This ITP covers the Agent Equipment Config delivery retrofit for #152. The
stocked slice is the published Config runtime, its current MCP parity surface,
and the repo-owned Codex plugin bundle. Delivery compliance remains pending
until Codex gear-up validation passes.

## Subject Under Inspection

- Stock record: [`inventory/equipment.toml`](../../../inventory/equipment.toml)
  entry `agent-equipment-config`.
- Shop card:
  [`docs/equipment/shop-cards/agent-equipment-config.md`](../shop-cards/agent-equipment-config.md).
- Closeout record:
  [`docs/closeout/agent-equipment-config-delivery-retrofit.md`](../../closeout/agent-equipment-config-delivery-retrofit.md).
- Runtime guide:
  [`docs/equipment/agent-equipment-config.md`](../agent-equipment-config.md).
- Integration guide:
  [`docs/equipment/agent-equipment-config-integration.md`](../agent-equipment-config-integration.md).
- Runtime source:
  [`tools/agent_equipment_config.py`](../../../tools/agent_equipment_config.py).
- MCP wrapper:
  [`tools/agent_equipment_config_mcp_server.py`](../../../tools/agent_equipment_config_mcp_server.py).
- Codex plugin:
  [`plugins/agent-equipment-config/`](../../../plugins/agent-equipment-config/).
- Repo marketplace:
  [`.agents/plugins/marketplace.json`](../../../.agents/plugins/marketplace.json).

## Inspection Checklist

- The stock record uses schema `agent-armory.equipment-stock.v1`.
- The stock record keeps `promotion_state = "published"` and
  `delivery_compliance = "pending"`.
- The stock record links this ITP, the shop card, and the closeout record.
- Required components have inspectable repository paths.
- Optional components have inspectable repository paths.
- Planned components explain why they are not stocked.
- Unavailable components explain why they are outside the stocked slice.
- The Codex plugin manifest points to bundled skills, MCP config, and hooks
  with plugin-root-confined paths.
- The bundled MCP config uses the local launcher, passes through only
  `AGENT_ARMORY_ROOT`, and keeps prompt approval for local-write tools.
- The plugin-local launcher finds the standalone repo server only from
  `AGENT_ARMORY_ROOT`, changes directory to the resolved checkout root, and
  fails closed otherwise.
- The `PreToolUse` guard hook ignores unrelated tools and denies Config
  local-write MCP calls missing `apply_authority = "operator"`.
- The routing skill is thin and links to the runtime guide, integration guide,
  and MCP tool spec instead of duplicating their contracts.
- README and docs routes point to the shop card or stock inventory without
  replacing `inventory/equipment.toml` as the stock authority.
- The closeout record explains why #23 and #135 remain closed and why #152 is
  delivery retrofit debt.

## Test Plan

- Run the published-equipment delivery regression tests:

  ```bash
  python3.14 -m unittest tests.test_validate_armory_integrity.PublishedEquipmentDeliveryValidationTests
  ```

- Run the Codex plugin contract, launcher, hook, and routing skill tests:

  ```bash
  python3.14 -m unittest tests.test_agent_equipment_config_codex_plugin
  ```

- Run Armory integrity validation:

  ```bash
  python3.14 tools/validate_armory_integrity.py
  ```

- Run final closeout validation before treating the story as merge-ready:

  ```bash
  python3.14 tools/validate_armory_integrity.py --final-closeout
  ```

- Run Config runtime and MCP parity tests when runtime behavior changes. The
  Codex plugin launcher delegates to the existing standalone MCP server.

## Evidence Requirements

- Test output for the published-equipment delivery regression test class.
- Test output for the Codex plugin contract test module.
- Armory integrity validation output.
- Final closeout validation output.
- Security review result for the changed docs, TOML, and test surfaces.
- Documentation review result covering human-facing and agent-facing routing.
- Ralph Review Until Clean cycles for Cross-Boundary Coherence and Story
  Quality.

## Completion Decision

Completion status: pending

Delivery compliance: pending
