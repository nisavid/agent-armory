# Published Equipment Delivery

Status: Forge Canon

Published Equipment Delivery defines the minimum stock standard for equipment
that appears as available Armory stock. It keeps public delivery claims
separate from Smith-facing design evidence and from historical promotion state.

## Purpose

A stockable equipment release or slice is ready for delivery only when its
canonical stock record, shop card, advertised component manifest, inspection
and test plan, and delivery status can be inspected together. The standard
prevents a published claim from implying that planned, unavailable, or
uninspectable components are ready to equip.

This standard does not stock Agent Equipment Config by itself. The first real
Config stock record belongs to the delivery retrofit issue that consumes this
standard.

## Authority

`inventory/equipment.toml` is the canonical stock inventory authority. Human
storefronts, README copy, docs maps, issue comments, and shop cards may display
stock information, but they do not replace the inventory record.

Each stock record links to an Equipment Epic Closeout Record under
`docs/closeout/`. That closeout record is the durable authority for the story
completion decision behind a stockable delivery claim. Issue comments, PR
bodies, release summaries, and handoff notes may project or summarize it, but
they do not replace it.

The inventory file uses schema version `agent-armory.equipment-stock.v1`. It
may use `equipment = []` while the standard exists and before a stockable slice
is recorded.

## Equipment Shop Cards

An Equipment Shop Card is a Wielder and Outfitter-facing catalog artifact. It
answers whether the equipment fits the task, what is actually stocked, what
delivery status is claimed, how to gear up, which components are required or
not ready, what evidence exists, and what support or lifecycle expectations
apply.

Capability Cards remain Smith-facing design records. A shop card can link to a
Capability Card or Equipment Design Bundle for deeper evidence, but it does not
become the design authority.

Shop cards live under `docs/equipment/shop-cards/`. Stock records must link to
Markdown shop cards in that directory.

## Equipment Inspection and Test Plans

An Equipment Inspection and Test Plan is the delivery gate for one stockable
equipment release or slice. It names the subject under inspection, checklist,
test plan, required evidence, and completion decision.

Inspection and Test Plans live under
`docs/equipment/inspection-test-plans/`. Stock records must link to Markdown
plans in that directory.

## Equipment Epic Closeout Records

An Equipment Epic Closeout Record is the story-level delivery decision for one
stockable equipment release or slice. It ties the stock record, shop card,
inspection and test plan, advertised gear-up surfaces, Issue Ops projection,
validation evidence, Ralph Review Until Clean evidence, and completion decision
into one inspectable repo artifact.

Closeout records live under `docs/closeout/`. Stock records must link to
Markdown closeout records in that directory.

## Stock Inventory Records

Each `[[equipment]]` record describes one stockable equipment release or slice:

- `id`: stable inventory identifier.
- `name`: human-readable stock name.
- `summary`: short Wielder and Outfitter-facing description.
- `promotion_state`: historical Equipment Promotion Path state.
- `delivery_compliance`: current delivery status under this standard.
- `shop_card`: repo-relative Markdown path under `docs/equipment/shop-cards/`.
- `inspection_test_plan`: repo-relative Markdown path under
  `docs/equipment/inspection-test-plans/`.
- `closeout_record`: repo-relative Markdown path under `docs/closeout/`.
- `notes`: optional status context.

Promotion state and delivery compliance are separate. Historical `published`
claims remain promotion records; delivery compliance records whether the
current delivery standard has passed.

## Component Manifests

Each equipment record may list `[[equipment.components]]` entries:

- `name`: component label shown to Wielders and Outfitters.
- `kind`: component type, such as `cli`, `mcp`, `docs`, `config`, `plugin`,
  `skill`, `validation`, or `provider`.
- `status`: one of `required`, `optional`, `planned`, or `unavailable`.
- `paths`: repo-relative paths that make the component inspectable.
- `notes`: required for `planned` and `unavailable` components.

Required advertised components must list at least one inspectable repo path.
Any listed component path must exist in the repository and must not use an
absolute path, `..`, a URL scheme, a symlink escape, or any other root escape.

## Delivery Compliance

Delivery compliance statuses are:

- `not_evaluated`: the stock record exists, but delivery evidence has not been
  checked against the current standard.
- `pending`: delivery work is underway or waiting on later slices.
- `passed`: the release or slice satisfies the current delivery standard.
- `blocked`: a known missing, unsafe, or unapproved condition prevents delivery.

`passed` requires:

- `promotion_state = "published"`;
- a completed linked Equipment Inspection and Test Plan whose completion
  decision records the exact strings `Completion status: complete` and
  `Delivery compliance: passed`;
- a completed linked Equipment Epic Closeout Record whose completion decision
  records the exact strings `Completion status: complete` and
  `Delivery compliance: passed`.

Published equipment may still have `not_evaluated`, `pending`, or `blocked`
delivery compliance when historical publication predates this delivery standard
or later evidence has not passed.

## Validation

Armory Integrity Validation checks the inventory schema version, record fields,
delivery-compliance vocabulary, promotion and delivery consistency, shop-card,
inspection-test-plan, and closeout-record path boundaries, shop-card, ITP, and
closeout-record sections, passed-delivery completion evidence, component
statuses, required component paths, planned and unavailable component notes,
and repo-relative path safety.

The validator does not infer stock from README copy, docs lists, templates,
issue labels, or Capability Cards. Stock authority starts at
`inventory/equipment.toml`.
