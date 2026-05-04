# Limit First Pass to the Forge Seed

The first PRD and implementation plan will cover the Forge Seed: canonical docs, decision method, evidence discipline, harness catalog, templates, examples, initial Smith task specs, and Seed Validation. Agent Ops, Periodic Actions, and Harness Capability Refresh remain downstream Smith specs until the Framework can guide their design and validation.

## Considered Options

- Build only the Forge Seed and specify downstream equipment.
- Build the Forge Seed plus first implementations of Agent Ops and Periodic Actions.
- Skip the Forge Seed and start directly with equipment implementations.

## Consequences

- The first pass stays reviewable and can establish quality gates before equipment work starts.
- Downstream Smith specs can inherit the Framework's decision method instead of being designed ad hoc.
- Acceptance criteria must distinguish specified future work from implemented equipment.
