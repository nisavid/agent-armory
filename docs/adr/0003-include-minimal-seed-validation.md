# Include Minimal Seed Validation

The Forge Seed will include minimal runnable validation for its own repository shape, documentation links, preserved handoff provenance, accepted-handoff projection or explicit deferment, and structured harness catalog fields. It will not include harness-specific behavior validators until downstream Smiths implement concrete equipment.

## Considered Options

- Include minimal Seed Validation now.
- Specify validation expectations only in prose.
- Build harness-specific validators during the Forge Seed.

## Consequences

- The first pass has testable substance without creating fake production equipment.
- The implementation plan can use TDD for validation behavior.
- Harness-specific validation remains scoped to later Smith specs and must not be implied by seed checks.
