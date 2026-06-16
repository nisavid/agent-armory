# Equipment Inspection and Test Plan: Agent Equipment Config

Status: Equipment Inspection and Test Plan

## Scope

This ITP covers the Agent Equipment Config delivery retrofit for #152 and the
Codex gear-up validation for #156. The stocked slice is the published Config
runtime, its current MCP parity surface, and the repo-owned Codex plugin
bundle.

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
  `delivery_compliance = "passed"`.
- The stock record links this ITP, the shop card, and the closeout record.
- Required components have inspectable repository paths.
- Optional components have inspectable repository paths.
- The Codex gear-up validation component is required and links this ITP plus
  the closeout record as inspectable evidence.
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
- Repo-local CLI fallback validation passes through
  `tools/agent_equipment_config.py config validate`.
- Repo-local stdio MCP validation reaches initialize, `tools/list`, and a
  read-only Config tool call through the standalone server.
- Real local Codex install dogfood is not run unless the operator grants
  explicit approval for local Codex mutation.
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

- Run Config runtime and MCP parity smoke checks:

  ```bash
  python3.14 tools/agent_equipment_config.py config validate \
    --layer templates/config/agent-equipment-config-example.toml \
    --issue-tracker-ops \
    --requested-behavior advisory
  python3.14 -m unittest \
    tests.test_agent_equipment_config_mcp_server.AgentEquipmentConfigMcpServerTests.test_server_initializes_and_lists_config_tools \
    tests.test_agent_equipment_config_mcp_server.AgentEquipmentConfigMcpServerTests.test_server_calls_read_only_config_tool
  ```

The Codex plugin launcher delegates to the existing standalone MCP server.

## Validation Evidence

- `python3.14 -m unittest tests.test_validate_armory_integrity.PublishedEquipmentDeliveryValidationTests`:
  passed with 40 tests.
- `python3.14 -m unittest tests.test_agent_equipment_config_codex_plugin`:
  passed with 48 tests.
- `python3.14 -m unittest tests.test_agent_equipment_config_mcp_server`:
  passed with 13 tests.
- `python3.14 tools/agent_equipment_config.py config validate --layer templates/config/agent-equipment-config-example.toml --issue-tracker-ops --requested-behavior advisory`:
  passed with `passed: true`, `safety_status: usable`, ready authority, ready
  `issue_tracker_ops` fragment, and advisory enforcement projection.
- `python3.14 -m unittest tests.test_agent_equipment_config_mcp_server.AgentEquipmentConfigMcpServerTests.test_server_initializes_and_lists_config_tools tests.test_agent_equipment_config_mcp_server.AgentEquipmentConfigMcpServerTests.test_server_calls_read_only_config_tool`:
  passed with 2 tests.
- `python3.14 -m unittest tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_published_config_example_loads_as_repository_policy tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_cli_config_validate_outputs_lower_noise_report_and_exit_status`:
  passed with 2 tests.
- `python3.14 -m unittest tests.test_validate_armory_integrity`: passed with
  440 tests.
- `python3.14 -m unittest`: passed with 850 tests.
- `python3.14 tools/validate_armory_integrity.py`: passed with 0 failed and
  451 passed.
- `python3.14 tools/validate_armory_integrity.py --final-closeout`: passed
  with 0 failed and 452 passed.
- `git diff --check`: passed.
- Real local Codex install dogfood: not run. No explicit operator approval was
  granted for local Codex installation or plugin enablement in this
  implementation session.
- Codex Security diff scan: completed for the local patch across the validator,
  stock TOML, tests, ITP, closeout, shop card, and inventory projection with no
  plausible security candidates.

## Residual Limits

- The repo-local path proves the stock record, shop card, plugin source, MCP
  server, routing skill, CLI fallback, and ITP evidence are internally
  consistent.
- Local Codex installation, marketplace install UI behavior, and operator
  machine plugin enablement remain outside this validation because they require
  explicit approval before mutating the operator's Codex environment.

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

Completion status: complete

Delivery compliance: passed
