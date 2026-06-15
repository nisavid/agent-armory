# Equipment Inspection and Test Plan: Agent Equipment Config

Status: Equipment Inspection and Test Plan

## Scope

This ITP covers the Agent Equipment Config delivery retrofit for #152. The
stocked slice is the historical published runtime slice from #23 and #135,
represented under the Published Equipment Delivery standard with delivery
compliance pending until Codex gear-up validation passes.

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

## Inspection Checklist

- The stock record uses schema `agent-armory.equipment-stock.v1`.
- The stock record keeps `promotion_state = "published"` and
  `delivery_compliance = "pending"`.
- The stock record links this ITP, the shop card, and the closeout record.
- Required components have inspectable repository paths.
- Optional components have inspectable repository paths.
- Planned components explain why they are not stocked.
- Unavailable components explain why they are outside the stocked slice.
- README and docs routes point to the shop card or stock inventory without
  replacing `inventory/equipment.toml` as the stock authority.
- The closeout record explains why #23 and #135 remain closed and why #152 is
  delivery retrofit debt.

## Test Plan

- Run the published-equipment delivery regression tests:

  ```bash
  python3.14 -m unittest tests.test_validate_armory_integrity.PublishedEquipmentDeliveryValidationTests
  ```

- Run Armory integrity validation:

  ```bash
  python3.14 tools/validate_armory_integrity.py
  ```

- Run final closeout validation before treating the story as merge-ready:

  ```bash
  python3.14 tools/validate_armory_integrity.py --final-closeout
  ```

- Run Config runtime and MCP parity tests when runtime behavior changes. This
  retrofit does not change runtime behavior.

## Evidence Requirements

- Test output for the published-equipment delivery regression test class.
- Armory integrity validation output.
- Final closeout validation output.
- Security review result for the changed docs, TOML, and test surfaces.
- Documentation review result covering human-facing and agent-facing routing.
- Ralph Review Until Clean cycles for Cross-Boundary Coherence and Story
  Quality.

## Completion Decision

Completion status: pending

Delivery compliance: pending
