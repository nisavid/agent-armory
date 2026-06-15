# Stocked Equipment Inventory

This page is the human-facing view of current Armory stock. It is a checked
projection of the canonical inventory, not a separate source of stock truth.

## Stock Authority

The canonical stock authority is
[`inventory/equipment.toml`](../../inventory/equipment.toml). The stock
inventory uses schema `agent-armory.equipment-stock.v1`.

## Stock Records

- `agent-equipment-config` - Agent Equipment Config - `pending` -
  [shop card](shop-cards/agent-equipment-config.md) -
  [ITP](inspection-test-plans/agent-equipment-config.md)

## Shop Cards

Equipment Shop Cards live in the [shop-card index](shop-cards/README.md).
Stock records reference cards from `inventory/equipment.toml`.

## Inspection and Test Plans

Equipment Inspection and Test Plans live in the
[ITP index](inspection-test-plans/README.md). Stock records reference ITPs from
`inventory/equipment.toml`.

## Gear-Up Paths

[Agent Equipment Config](agent-equipment-config.md) is available now as a
published runtime and Codex plugin surface, and the
[Config integration guide](agent-equipment-config-integration.md) shows how
Smiths, Wielders, and Outfitters connect that runtime to equipment and harness
surfaces.

Config now has a stocked inventory record and
[shop card](shop-cards/agent-equipment-config.md). Its delivery compliance is
pending until Codex gear-up validation passes.
