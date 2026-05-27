# Published Equipment Delivery System PRD

Status: Repo Draft PRD

Published PRD Issue: #147

## Problem Statement

Agent Armory can design and implement useful Agent Equipment before the
equipment is easy for Wielders and Outfitters to find, understand, equip,
inspect, and trust. Agent Equipment Config shows the gap: its runtime slice and
MCP parity are closed, but the Armory does not yet present a clear shop card,
stock inventory entry, Codex plugin, runnable MCP server, routing skill, or
standard publication inspection record.

The Forge already has Capability Cards, Equipment Design Bundles, promotion
states, validation plans, and Story Closeout. Those surfaces help Smiths build
equipment, but they do not yet form a complete delivery system for published
equipment. Published claims need stock records, Wielder and Outfitter
presentation, gear-up paths, component manifests, inspection criteria, and
equipment-epic closeout gates that block publication until the advertised
equipment can actually be equipped.

## Solution

Create a Published Equipment Delivery System for stockable equipment releases
and slices. The system adds:

- Wielder and Outfitter-facing Equipment Shop Cards;
- canonical structured inventory records;
- human-facing storefront display;
- standard Equipment Inspection and Test Plans;
- equipment-epic closeout templates and gates;
- a transition rule for historical published claims;
- a Config tracer retrofit that proves the delivery system on the current
  published Agent Equipment Config runtime slice.

Prior published claims remain historical promotion-state records. New stock
inventory records carry a separate delivery-compliance status until the new
Equipment Inspection and Test Plan passes.

The first gear-up bay is Codex. The Config tracer must provide a CLI fallback,
a standalone MCP server wrapper, a repo-owned Codex plugin, one thin routing
skill, a shop card, inventory entry, storefront presence, and onboarding path.
Full marketplace UI, all-harness package management, and broad migration of
existing skills or equipment are out of scope for this PRD.

## User Stories

1. As a Wielder, I want a short shop card for published equipment, so that I
   can tell what the equipment does and whether it fits my task.
2. As a Wielder, I want gear-up instructions that start from a concrete
   harness, so that I can equip the item without reading dense Smith-facing
   specs first.
3. As a Wielder, I want the shop card to name the CLI, MCP, plugin, skill, and
   docs surfaces that actually exist, so that I do not chase planned pieces.
4. As a Wielder, I want optional and future components labeled separately from
   required components, so that missing future work is not hidden inside a
   published claim.
5. As a Wielder, I want a fallback path when a preferred gear-up surface is
   unavailable, so that I can still use the equipment safely.
6. As a Wielder, I want onboarding instructions to explain first use, normal
   use, failure handling, and support expectations, so that I can rely on the
   equipment under task pressure.
7. As an Outfitter, I want a structured inventory record for each stockable
   equipment release or slice, so that I can assemble Loadouts from current
   stock instead of reading every spec.
8. As an Outfitter, I want inventory records to list required, optional,
   planned, and unavailable components, so that Loadout fit can be checked
   mechanically.
9. As an Outfitter, I want delivery-compliance status separate from historical
   promotion state, so that old publication claims can be retrofit without
   rewriting history.
10. As an Outfitter, I want inventory records to link shop cards, ITP evidence,
    security notes, support notes, and rollback/deprecation expectations, so
    that publication readiness is inspectable.
11. As an Operator, I want the README and documentation map to surface stocked
    equipment clearly, so that I can see what is usable now.
12. As an Operator, I want the current Agent Equipment Config runtime slice to
    become a complete stocked item, so that the first published Config claim
    has a concrete equipment delivery path.
13. As an Operator, I want real Codex gear-up for Config before claiming the
    Codex loadout is complete, so that plugin, skill, MCP, and CLI paths are
    not theoretical.
14. As an Operator, I want real local Codex installation dogfood to require
    explicit approval, so that the delivery validation does not mutate my local
    environment without consent.
15. As a Smith, I want Capability Cards to remain Smith-facing design records,
    so that public shop presentation does not dilute design evidence.
16. As a Smith, I want Equipment Shop Cards to be derived from current
    equipment truth, so that public presentation does not become a parallel
    authority.
17. As a Smith, I want an Equipment ITP template, so that publication work has
    a concrete gate before closeout.
18. As a Smith, I want ITP criteria to cover behavior, installation, gear-up,
    component manifests, docs, security, support, rollback, deprecation, and
    publication surfaces, so that validation is broader than unit tests.
19. As a Forgewright, I want Story Closeout to require the equipment-epic
    closeout template for published equipment, so that epics do not close
    before delivery surfaces exist.
20. As a Forgewright, I want validators to check stock records, shop-card links,
    required components, delivery-compliance status, ITP completion, and
    closeout gating, so that the rules stay enforceable.
21. As a Forgewright, I want Issue Ops projection to preserve dependency
    relationships among delivery slices, so that agents can work the sequence
    without rediscovering the graph.
22. As a Forgewright, I want #84 and #85 to block only the delivery-system
    slices that consume their skill and plugin source-intake lessons, so that
    the PRD and standards work can proceed in parallel.
23. As a reviewer, I want Ralph Review Until Clean on the PRD, standards,
    templates, executable surfaces, and closeout evidence, so that the delivery
    system does not encode ambiguous or contradictory rules.
24. As a security reviewer, I want new executable surfaces and plugin package
    boundaries to receive security closeout, so that Config delivery does not
    introduce unreviewed filesystem, MCP, secret, or plugin risks.
25. As a future equipment maintainer, I want the new delivery standard to align
    with the existing ingestion and promotion pipeline, so that imported
    equipment and newly forged equipment use compatible publication rules.

## Implementation Decisions

- Publication unit: a stockable equipment release or slice may be published
  independently from a whole equipment line.
- Transition rule: historical `published` claims are not reopened by default.
  New inventory records carry delivery-compliance status until the ITP passes.
- Shop Card boundary: Equipment Shop Cards are Wielder and Outfitter-facing
  catalog records. Capability Cards remain Smith-facing design records.
- Inventory authority: `inventory/equipment.toml` is the canonical stock
  record. Human-facing docs and README surfaces must be checked against it.
- Shop card placement: human-facing shop cards live under
  `docs/equipment/shop-cards/`.
- Component status: component manifests distinguish `required`, `optional`,
  `planned`, and `unavailable` components. Every advertised required component
  must exist and be inspectable.
- ITP boundary: Equipment Inspection and Test Plans are publication gates, not
  replacements for per-bundle validation plans.
- Closeout boundary: equipment-epic closeout uses a reusable template and blocks
  closeout unless the ITP and stock surfaces pass.
- Config tracer: Agent Equipment Config remains closed as #23 and #135. The new
  work creates delivery retrofit issues instead of reopening those issues.
- First gear-up bay: Codex is the first concrete gear-up target. Other harness
  projections may remain planned or unavailable until future slices.
- MCP boundary: the Config runtime gains a standalone MCP server wrapper around
  existing Config MCP definitions and dispatcher behavior.
- Plugin boundary: the Config Codex plugin is repo-owned source with manifest,
  build/install instructions, validation, and inventory linkage.
- Skill boundary: the first Config skill is one thin routing skill for Smith,
  Wielder, and Outfitter tasks. It points to MCP, CLI, shop card, and guides
  rather than duplicating heavy contracts.
- Install validation: repo-local build/schema/smoke checks are required. Real
  local Codex installation dogfood is opt-in during implementation.
- Related work: #106 is product-doctrine input, not a blocker. #5 is the
  existing ingestion and promotion pipeline alignment target, not a direct
  blocker for this PRD; the projected alignment slice owns that coordination.
  #84 blocks only skill-validation, packaging, or ingestion/promotion alignment
  work that consumes skill-evaluation lessons. #85 blocks only plugin-dependent
  or ingestion/promotion alignment work that consumes plugin-creation lessons.
  #157 intentionally depends on #84 and #85 for those source-intake lessons
  while #5 remains an alignment target rather than a blocker.
- Scope boundary: full marketplace UI, all-harness package management, and
  broad skill/equipment migration are out of scope for this PRD.

## Testing Decisions

- Tests should verify externally observable behavior through public validators,
  CLI commands, MCP calls, plugin package checks, and skill pressure validation.
- Validator coverage should check stock record schema, required links, required
  component existence, shop-card paths, promotion and delivery-compliance
  consistency, ITP completion, closeout gating, support notes, rollback or
  uninstall cleanup, deprecation expectations, and any publication-blocking
  local Codex dogfood cleanup requirement.
- The Config MCP server wrapper should be tested through public MCP tool-call
  behavior and should reuse existing Config runtime behavior rather than
  duplicating the dispatcher.
- The Config Codex plugin should have repo-local manifest, component-path,
  package, and smoke validation before any real local installation dogfood.
- The Config routing skill should be pressure-tested for correct routing under
  realistic Smith, Wielder, and Outfitter prompts.
- New executable or package surfaces require Change Set Security Closeout,
  Change Set Documentation Closeout, deterministic validation, and Ralph Review
  Until Clean before merge-readiness.

## Out of Scope

- Reopening #23 or #135.
- General marketplace UI or remote marketplace publication.
- All-harness packaging or install support.
- Broad migration of operator-global skills or externally maintained
  equipment.
- Replacing Existing Equipment Onboarding.
- Replacing Agent Test Jigs or future Harness Testing System work.
- Making Agent Equipment Config resolve secrets, mutate external systems, or
  enforce harness controls beyond its current product boundary.

## Further Notes

GitHub Issues now owns active tracking for this PRD. Issue #147 is the parent
epic and Published PRD Issue. Its projected child issues are:

- #148 for the shop card and structured inventory standard;
- #149 for storefront and README display;
- #150 for the standard Equipment ITP gate;
- #151 for equipment-epic closeout template and gate integration;
- #152 for Config shop card, inventory entry, and storefront retrofit;
- #153 for the Config standalone MCP server wrapper;
- #154 for the Config Codex plugin;
- #155 for the Config routing skill;
- #156 for Config Codex gear-up validation;
- #157 for aligning the #5 ingestion and promotion pipeline with the delivery
  system; #157 intentionally waits on #84 and #85 for source-intake alignment
  input while #5 remains related context, not a blocker.
