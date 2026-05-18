# Validation Plan: Agent Equipment Config

Status: Equipment Blueprint
Promotion state: planned

This Equipment Design Bundle describes desired behavior and includes the first
standard-library runtime engine slice for effective-config, config-diff,
diagnostics, plain handoff promotion, authority checks, projection
classification, and reusable consumer action decisions. It does not implement Agent Equipment
beyond this runtime slice, publish assets, resolve secrets, mutate external
systems, or implement harness controls. Source mutation is limited to explicit
migration apply for eligible local TOML sources.

## Scope

This validation plan covers the v0 contract and current portable runtime slice.
The current bundle change validates repository shape, contract coverage, and the
standard-library engine behaviors covered by `tests.test_agent_equipment_config`.

## Current deterministic checks

- `python3.14 -m unittest tests.test_validate_armory_integrity.SpecValidationTests`
- `python3.14 -m unittest tests.test_agent_equipment_config`
- `python3.14 -m unittest tests.test_validate_armory_integrity`
- `python3.14 -m unittest`
- `python3.14 tools/validate_armory_integrity.py`
- `python3.14 tools/validate_armory_integrity.py --final-closeout`
- `git diff --check`

## Bundle validation

Armory Integrity Validation must require:

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

## Runtime cases

Runtime coverage tracks these current and follow-on cases:

- absent shared Config equipment with equipment-specific session-scoped fallback;
- partial config that keeps machine-shaped effective-config output while
  reporting `incomplete` with missing-required diagnostics;
- conflicting layers that report `conflicted`;
- blocked override diagnostics;
- schema conflict diagnostics;
- semantic validator diagnostics;
- read-time schema migration preview;
- explicit migration apply audit;
- committed durable config plus local-only override;
- checkout-local state;
- session override;
- explicit load-contract discovery proposal fields for source categories,
  caller responsibility, input surfaces, provenance requirements, and secret
  resolution boundaries;
- multi-equipment composition;
- secret reference resolution status without secret disclosure;
- config-diff output between two effective configs;
- enforcement projection classification as blocking or advisory;
- Issue Tracker Ops plain handoff ingestion and promotion.

Implemented by the v0 engine slice:

- TOML layer loading;
- schema fragment validation;
- effective-config output;
- config-diff output for values, secret-reference identity, status changes, and diagnostic changes;
- Config Safety Status classification;
- deprecation diagnostics and migration-preview output with audit-preview shape;
- migration-apply dry-run, write authority, source eligibility, refusal, and
  audit-record behavior;
- plain Issue Tracker Ops handoff fallback and promotion;
- consumer action decision helper for allowed, advisory, warning, blocking, and
  unsupported outcomes;
- missing-authority diagnostics for mutation-gated settings;
- enforcement projection classification as `blocking` or `advisory`;
- onboarding-plan output for missing shared Config, missing config data,
  interrupted partial config, resumed handoff completion, and restarted
  section revision;
- onboarding-plan discovery proposals that expose the explicit-load contract
  for caller-owned path discovery and schema-fragment registration;
- importable consumer integration output that preserves effective-config
  evidence and returns `allowed`, `advisory`, `warning`, `blocking`, and
  `unsupported` decisions;
- Issue Tracker Ops pressure scenario for blocked live mutation.

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

The runtime slice proves only the deterministic CLI behaviors covered by
`tests.test_agent_equipment_config`. It does not prove external enforcement,
provider secret resolution, migration behavior outside eligible local TOML
sources, or harness-specific control projection.
