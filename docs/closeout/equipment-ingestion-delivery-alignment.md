# Equipment Ingestion Delivery Alignment

Status: Alignment Record

## Scope Boundary

This record closes #157 by aligning #5 with the Published Equipment Delivery
System. It records the delivery-system policy boundary for future ingestion and
promotion work; it does not implement the #5 ingestion pipeline, create stock
records, create Equipment Shop Card files, create Equipment Inspection and Test
Plan files, or claim that any source intake candidate is stockable.

Issue #5 owns the broader equipment ingestion and promotion pipeline. #157
records the accepted delivery-system alignment and the routing of the now-closed
#84 and #85 source-intake findings into that later work.

## Source Evidence

- #147 defines the Published Equipment Delivery System in
  [docs/prd/published-equipment-delivery.md](../prd/published-equipment-delivery.md).
- [docs/equipment-delivery.md](../equipment-delivery.md) defines stock inventory,
  Equipment Shop Card, Equipment Inspection and Test Plan, delivery compliance,
  and closeout authority.
- [docs/equipment-promotion.md](../equipment-promotion.md) defines promotion
  path states and keeps promotion state separate from delivery compliance.
- #5 remains the live owner for the ingestion and promotion pipeline design.
- #84 contributes durable skill-eval methodology source intake evidence through
  [docs/closeout/skill-eval-methodology-source-intake.md](skill-eval-methodology-source-intake.md).
- #85 contributes durable plugin-creator source intake evidence through
  [docs/closeout/plugin-creator-source-intake.md](plugin-creator-source-intake.md).
- #157 records this alignment and does not supersede those source ledgers.

## Accepted Alignment

Source intake records provenance, eligibility, licensing, update-channel, and
compatibility evidence for candidate equipment. Source intake does not make
stock inventory claims, shop-card claims, delivery compliance claims, or
publication claims by itself.

Forge design decides the equipment shape before any stock inventory or
publication claim. The shape decision covers whether the result should become a
skill, MCP or tool surface, plugin, Agent Profile, hook, script, policy
framework, workflow, documentation surface, or another Agent Equipment form.

inventory/equipment.toml remains the canonical stock inventory authority for
stocked Published Agent Equipment. Human-facing inventories, storefront display,
storefronts, and Equipment Shop Card files are projections from that stock
authority plus the committed delivery evidence that supports it.

The Equipment Inspection and Test Plan is the per-equipment validation gate for
stockable releases or accepted vertical slices. Delivery compliance is the
delivery-system gate for stockable release claims. Promotion state is a separate
adoption and exposure state; it must not be used as a substitute for delivery
compliance.

## Skill And Plugin Routing

Issue #84 applies only to ingestion slices that consume skill-eval methodology,
package-validation, pressure-validation, trigger-selection evals, harness
adaptation, or skill-publication evidence. It is not a general ingestion rule for
all equipment shapes.

Issue #85 applies only to plugin-shaped ingestion slices or marketplace-like
presentation slices that need plugin manifest scaffolding, component surface
selection, asset metadata, policy/auth semantics, placeholder-debt handling, or
Codex plugin publication evidence. It is not a universal schema for all
equipment ingestion.

Future #5 work should use both ledgers as source-specific inputs when their
equipment slice needs them, then route the resulting policy through the Forge
design and delivery gates above.

## Follow-Up Projection

No new ingestion-specific follow-up issue is projected by #157. The accepted
alignment is specific enough for #5 to use during its grill and design work, but
it does not define an approved vertical-slice breakdown for new shop-card,
inventory, plugin, skill, or publication implementation issues.

If #5 later accepts narrower slices, project those with the issue tracker using
the accepted boundaries in this record:

- Source intake and provenance evidence before Forge shape selection.
- Forge shape selection before stock inventory or publication claims.
- Stock inventory, Equipment Shop Card, Equipment Inspection and Test Plan, and
  delivery compliance work as distinct delivery surfaces.
- Skill-eval and plugin-shaped source lessons only where the target slice
  actually depends on them.

## Dependency And Label Cleanup

The live dependency graph for #157 names #85, which is closed. #84 is durable
source evidence for this record but is not an active native blocker. The
`dependency:unblocked` labels on #5 and #157 are current.

The remaining closed dependency edges may stay as historical evidence unless the
tracker owner wants the graph pruned. #157 closeout should reconcile any stale
blocker prose by pointing to this record and the closed #84/#85 ledgers.

## Security Documentation And Review Closeout

This record adds no runtime API, network access, file mutation path, package
metadata, hook, MCP or tool definition, permission, secret-handling behavior, or
security policy. The validator check for this record reads one fixed
repository-relative Markdown path and rejects host-local paths in the durable
record text.

Documentation closeout reviewed the delivery PRD, equipment delivery guide,
promotion guide, issue tracker guidance, and source-intake closeout records. No
human-facing or agent-facing public workflow document needs a behavioral update
from #157 beyond this closeout record.

Ralph review scope for #157 is cross-boundary coherence across #5, #84, #85,
issue #147, this record, validator coverage, security closeout, documentation
closeout, and issue projection. Story quality review scope is the fit with the
Forge conveyor and Efficient Coherence doctrine: record stable boundaries here,
keep unresolved ingestion design in #5, and avoid broadening skill/plugin source
lessons beyond their evidence.
