# Validation Plan: Agent Equipment Config

Status: Equipment Blueprint
Promotion state: planned

This Equipment Design Bundle describes desired behavior and includes the first
standard-library runtime engine slice for fluent Config CLI operations,
effective-config, config-diff, diagnostics, plain handoff promotion, authority
checks, projection classification, reusable consumer action decisions,
read-only authoring proposal and plan-generation surfaces, and MCP parity tool
definitions plus the standalone stdio MCP server wrapper. It does not implement Agent Equipment beyond this runtime slice,
publish assets, resolve secrets, mutate external systems, implement harness
controls, or expose general edit surfaces beyond reviewed plan artifacts.
Source mutation is limited to explicit migration apply and reviewed
plan-artifact apply for eligible local TOML sources.

## Scope

This validation plan covers the v0 contract and current portable runtime slice.
The current bundle change validates repository shape, contract coverage, and the
standard-library engine behaviors covered by `tests.test_agent_equipment_config`.
The standalone MCP server wrapper is covered by
`tests.test_agent_equipment_config_mcp_server`.
It also treats `docs/prd/agent-equipment-config.md` as the product source for
required CLI/MCP operation-surface parity.

## Current deterministic checks

- `python3.14 -m unittest tests.test_validate_armory_integrity.SpecValidationTests`
- `python3.14 -m unittest tests.test_agent_equipment_config`
- `python3.14 -m unittest tests.test_agent_equipment_config_mcp_server`
- `python3.14 -m unittest tests.test_validate_armory_integrity`
- `python3.14 -m unittest`
- `python3.14 tools/validate_armory_integrity.py`
- `python3.14 tools/validate_armory_integrity.py --final-closeout`
- `git diff --check`

## Bundle validation

Armory Integrity Validation must require:

- `docs/prd/agent-equipment-config.md`
- `specs/agent-equipment-config/README.md`
- `specs/agent-equipment-config/capability-card.md`
- `specs/agent-equipment-config/interface-decision-record.md`
- `specs/agent-equipment-config/security-control-classification.md`
- `specs/agent-equipment-config/mcp-tools.md`
- `specs/agent-equipment-config/edit-boundaries.md`
- `specs/agent-equipment-config/authoring-plan-apply-model.md`
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
- deliberate edit intents and refusal states;
- target-agnostic `config propose` output and read-only authoring plan
  artifacts for `patch-layer` and `create-layer`, including precondition
  fingerprint, virtual post-change effective Config, durability
  classification, rollback stance, authority evidence, refusal codes, and
  secret-boundary refusals;
- `config apply` behavior for reviewed `patch-layer` and `create-layer`
  artifacts from file or stdin, including schema enforcement, source
  preconditions, authority, source category/trust/ownership, virtual
  post-change validation, semantic safety, secret-boundary refusals,
  all-or-nothing refusal, atomic local writes, and mutation audit evidence;
- allowed current edit path for eligible migration apply;
- refused current edit path for read-only, generated, untrusted, unsafe, or
  authority-blocked sources;
- committed durable config plus local-only override;
- checkout-local state;
- session override;
- explicit load-contract discovery proposal fields for source categories,
  caller responsibility, input surfaces, provenance requirements, and secret
  resolution boundaries;
- multi-equipment composition;
- secret reference resolution status without secret disclosure;
- blocked direct secret values and secret-reference tables with embedded value
  payloads;
- config-diff output between two effective configs;
- enforcement projection classification as blocking or advisory;
- Issue Tracker Ops plain handoff ingestion and promotion.

## Operation-surface validation

Before #23 closes, validation must cover the PRD's MVP operation map:

- `config resolve` maps to effective-config behavior and full provenance,
  diagnostics, safety, and enforcement evidence.
- `config validate` maps to lower-noise diagnostics, safety status, authority
  readiness, fragment readiness, and pass/fail status.
- `config diff` maps to config-diff behavior.
- `onboard config` maps to onboarding output behavior.
- `migrate config preview` and `migrate config apply` map to migration-apply
  preview and authorized write behavior.
- MCP tools mirror those safe operation families with typed inputs and outputs.
- `python3.14 tools/agent_equipment_config_mcp_server.py` exposes the current
  stdio MCP server for harnesses that can launch it, while the CLI remains the
  fallback evidence surface.

Implemented by the v0 engine slice:

- TOML layer loading;
- schema fragment validation;
- fluent CLI operations for resolve, validate, diff, onboarding, migration
  preview, and migration apply;
- fluent CLI authoring operations for `config propose`, `config patch`, and
  `create-layer` read-only proposal and plan-generation output;
- effective-config output;
- config-diff output for values, secret-reference identity, status changes, and diagnostic changes;
- lower-noise config validation output with authority readiness, fragment
  readiness, diagnostics, pass/fail status, and scriptable exit status;
- Config Safety Status classification;
- deprecation diagnostics and migration-preview output with audit-preview shape;
- migration-apply dry-run, write authority, source eligibility, refusal, and
  audit-record behavior;
- migration-apply allowed path for eligible TOML sources with operator or
  configured authority;
- migration-apply refused path for generated, checkout-local, session,
  secret-reference, untrusted, unsafe, incomplete, stale-without-migration,
  missing-authority, and changed-source cases;
- MCP tool definitions for every MVP operation with input schemas, output
  schemas, annotations, read/write classification, auth source, side effects,
  approval requirements, mutation gates, and failure modes;
- MCP tool-call dispatch for successful read-only resolution, config diff,
  onboarding, blocking validation, migration preview, refused apply, and
  allowed apply;
- MCP authoring parity for `config.propose`, `config.patch`,
  `config.create_layer`, and `config.apply`, including typed schemas,
  dispatch, read/write classification, side effects, auth source, approval
  requirements, failure modes, reviewed plan artifacts, precondition
  fingerprints, virtual post-change effective Config, refusal codes,
  all-or-nothing apply, durability classification, project-truth status,
  rollback stance, and secret/provider/source-category refusals;
- plain Issue Tracker Ops handoff fallback and promotion;
- consumer action decision helper for allowed, advisory, warning, blocking, and
  unsupported outcomes;
- missing-authority diagnostics for mutation-gated settings;
- enforcement projection classification as `blocking` or `advisory`;
- onboarding output for missing shared Config, missing config data,
  interrupted partial config, resumed handoff completion, and restarted
  section revision;
- onboarding discovery proposals that expose the explicit-load contract
  for caller-owned path discovery and schema-fragment registration;
- importable consumer integration output that preserves effective-config
  evidence and returns `allowed`, `advisory`, `warning`, `blocking`, and
  `unsupported` decisions;
- Issue Tracker Ops adapter projection for GitHub API mutation preflight,
  including allowed usable output and blocked incomplete, unsafe, conflicted,
  stale, untrusted, and missing-authority output;
- Issue Tracker Ops pressure scenario for blocked live mutation.

## Pressure validation

Before promotion beyond `planned`, test the Issue Tracker Ops pressure scenarios
under realistic task pressure. Evidence should show that an Agent can discover
the applicable policy, inspect effective-config output, avoid hidden preference,
and fail closed for live tracker mutation when Config Safety Status is not
`usable`.

## Security validation

Each implementation slice that adds executable parsing, migration, mutation,
secret resolution, hook behavior, tool definitions, network interaction,
reviewed plan apply, general source patching, revision writes, or enforcement
projection needs Codex Security review or a documented narrower security action.

## Residual risk

The runtime slice proves only the deterministic CLI behaviors covered by
`tests.test_agent_equipment_config`. It does not prove external enforcement,
provider secret resolution, migration behavior outside eligible local TOML
sources, or harness-specific control projection.
