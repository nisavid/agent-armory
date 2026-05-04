# Refresh Canonical Harness Catalog in the Seed

The handoff's 2026-05-02 harness facts remain preserved as source provenance, but the Forge Seed will refresh the canonical Harness Capability Catalog before publishing it. Harness capabilities are volatile, and the canonical catalog should not knowingly start stale when source refresh is available.

## Considered Options

- Preserve the handoff snapshot only and defer all refresh work.
- Refresh the canonical catalog during the Forge Seed and preserve the handoff snapshot as provenance.
- Build the full recurring Harness Capability Refresh equipment during the Forge Seed.

## Consequences

- The canonical catalog needs source-backed refresh evidence during the seed pass.
- The downstream Harness Capability Refresh spec remains responsible for ongoing maintenance automation.
- Seed docs must distinguish preserved handoff facts from refreshed canonical facts.
