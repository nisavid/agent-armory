# Validation Plan: Agent Equipment Config

Status: Equipment Blueprint
Promotion state: planned

This Forge Entry Bundle describes desired behavior only. It does not implement Agent Equipment, publish assets, or provide a runtime config engine.

## Scope

This validation plan covers the v0 contract and future implementation slices.
The current bundle change validates repository shape and contract coverage. Later
child issues add deterministic runtime validation as code exists.

## Current deterministic checks

- `python3.14 -m unittest tests.test_validate_forge_seed.SpecValidationTests`
- `python3.14 -m unittest tests.test_validate_forge_seed`
- `python3.14 -m unittest`
- `python3.14 tools/validate_forge_seed.py`
- `git diff --check`

## Bundle validation

The Forge Seed validator must require:

- `specs/agent-equipment-config/README.md`
- `specs/agent-equipment-config/capability-card.md`
- `specs/agent-equipment-config/interface-decision-record.md`
- `specs/agent-equipment-config/security-control-classification.md`
- `specs/agent-equipment-config/pressure-scenarios.md`
- `specs/agent-equipment-config/validation-plan.md`
- `specs/agent-equipment-config/closeout-evidence-plan.md`

The validator also checks visible v0 contract coverage for typed schemas,
schema fragments, layered config, Layer Precedence, Policy Authority,
effective-config, config-diff, semantic validators, Config Safety Status,
conflict diagnostics, migrations, secret references, session-scoped behavior,
plain equipment-specific config handoff, Issue Tracker Ops, policy, Codex,
OpenClaw, Hermes Agent, Claude Code, Cursor, and OpenCode.

## Future runtime cases

The first effective-config engine should validate:

- absent shared Config equipment with equipment-specific session-scoped fallback;
- partial config that stays schema-valid but reports `incomplete`;
- conflicting layers that report `conflicted`;
- blocked override diagnostics;
- schema conflict diagnostics;
- semantic validator diagnostics;
- read-time schema migration preview;
- explicit migration apply audit;
- committed durable config plus local-only override;
- checkout-local state;
- session override;
- multi-equipment composition;
- secret reference resolution status without secret disclosure;
- config-diff output between two effective configs;
- enforcement projection classification as blocking or advisory;
- Issue Tracker Ops plain handoff ingestion and promotion.

## Pressure validation

Before promotion beyond `planned`, test the Issue Tracker Ops pressure scenarios
under realistic task pressure. Evidence should show that an Agent can discover
the applicable policy, inspect effective-config output, avoid hidden preference,
and fail closed for live tracker mutation when Config Safety Status is not
`usable`.

## Security validation

Each implementation slice that adds executable parsing, migration, mutation,
secret resolution, hook behavior, tool definitions, network interaction, or
enforcement projection needs Codex Security review or a documented narrower
security action.

## Residual risk

The current bundle validates source shape and policy clarity. It does not prove
that a future engine computes merges correctly, enforces policy, resolves
secret references, or projects controls in any harness.
