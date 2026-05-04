# Define Equipment Promotion Path

The Forge Seed will define an Equipment Promotion Path so examples, Equipment Candidates, validated equipment, and Published Agent Equipment are visibly distinct. The path will use the states `example`, `specified`, `planned`, `implemented`, `validated`, and `published`.

## Considered Options

- Define explicit promotion states in the Forge Seed.
- Let each Smith invent status language for its equipment.
- Treat examples and specs as informal until implementation starts.

## Consequences

- Forge Examples can remain useful without implying production readiness.
- Smith specs can name their current state before implementation begins.
- Seed Validation can check that seed examples, specs, and other seed surfaces label their promotion state clearly.
- Equipment-specific validators, not Seed Validation, are responsible for proving downstream Published Agent Equipment behavior.
