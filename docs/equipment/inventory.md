# Stocked Equipment Inventory

This page is the human-facing view of current Armory stock. It is a checked
projection of the canonical inventory, not a separate source of stock truth.

## Stock Authority

The canonical stock authority is
[`inventory/equipment.toml`](../../inventory/equipment.toml). The stock
inventory uses schema `agent-armory.equipment-stock.v1`.

## Stock Records

No stocked equipment is recorded in `inventory/equipment.toml` yet.

## Shop Cards

Equipment Shop Cards will live in the
[shop-card index](shop-cards/README.md). Future stock records will reference
cards from `inventory/equipment.toml`.

## Inspection and Test Plans

Equipment Inspection and Test Plans will live in the
[ITP index](inspection-test-plans/README.md). Future stock records will
reference ITPs from `inventory/equipment.toml`.

## Gear-Up Paths

[Agent Equipment Config](agent-equipment-config.md) is available now as a
published runtime documentation surface, and the
[Config integration guide](agent-equipment-config-integration.md) shows how
Smiths, Wielders, and Outfitters connect that runtime to equipment and harness
surfaces.

Config does not have a stocked inventory record or shop card yet. Issue #152
owns the Config stock record and shop-card retrofit.
