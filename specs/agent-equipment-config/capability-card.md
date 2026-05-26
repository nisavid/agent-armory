# Capability Card: Agent Equipment Config

Status: Equipment Blueprint
Promotion state: planned

This Equipment Design Bundle describes desired behavior and includes the first
standard-library runtime engine slice for fluent CLI operations,
effective-config, config-diff, diagnostics, plain handoff promotion, authority
checks, and projection classification, plus onboarding output for first-run and
re-onboarding flows, explicit migration apply for eligible local TOML sources,
authoring proposal, plan-generation, reviewed plan-artifact apply behavior, and
MCP parity tool definitions for the same safe operation families.
It does not implement Agent Equipment beyond this runtime slice. It does not
publish assets, resolve secrets, mutate external systems, or
implement harness controls.

## Purpose

Provide shared, layerable, composable, adaptable, and enforceable configuration
across Agent Equipment.

Config lets equipment lines declare typed schemas, register namespaced schema
fragments, merge layered config, explain effective-config and config-diff
results, and surface policy decisions without hard-coding generic configuration
machinery into higher-level equipment.

## Vision alignment

Agent Equipment Config supports least cognitive privilege by moving durable
policy, local choices, schema validation, merge behavior, conflict diagnostics,
secret references, migrations, and safety status into typed data and
deterministic checks instead of hidden model preference.

It helps Outfitters assemble Loadouts that can adapt to organization,
repository, checkout, issue-set, session, harness, and operator policy without
copying all of that variation into prompt text.

## Users

- Smith: defines an equipment-specific config shape without inventing a new
  config system.
- Outfitter: combines equipment into a Loadout and needs explainable effective
  policy across the selected items.
- Wielder: uses configured equipment and needs safe behavior when config is
  missing, partial, stale, untrusted, or conflicted.
- Repository owner or operator: supplies policy, local choices, and authority
  boundaries.
- Harness projection author: maps Config categories to Codex, OpenClaw, Hermes
  Agent, Claude Code, Cursor, OpenCode, and future harnesses.

## Target harnesses

The v0 contract must be projectable to Codex, OpenClaw, Hermes Agent, Claude
Code, Cursor, and OpenCode. The first pressure scenario uses Issue Tracker Ops
because tracker writes, priority selection, dependency feasibility, dry-run or
execute behavior, external disclosure, and partial onboarding exercise the
policy model without making Config depend on Issue Tracker Ops.

## Needed surfaces

- Docs: this Equipment Design Bundle and future usage docs.
- Config: TOML authored layers and plain equipment-specific config handoff
  records.
- Scripts/tools: the portable fluent CLI slice for resolve, validate, diff,
  authoring proposal, patch-plan generation, create-layer plan generation,
  reviewed plan apply, onboarding, migration preview, and migration apply, plus
  implementation commands and deliberate edit-boundary reference.
- MCP/tools: typed parity tools for `config.resolve`, `config.validate`,
  `config.diff`, `config.propose`, `config.patch`, `config.create_layer`,
  `config.apply`, `onboard.config`, `migrate.config_preview`, and
  `migrate.config_apply`.
- Hooks, permissions, approvals, sandboxes, or tool gates: future enforcement
  projections for mutation-capable behavior.
- Skills: future Smith and Wielder judgment around design, onboarding, and
  remediation.
- Agent Profiles and plugins: future packaging and specialized operating roles.

## Hard rules

- Agent Equipment Config remains independent equipment.
- Equipment-specific config shapes remain usable in session scope when Config is
  absent.
- Shared Config consumes equipment-specific plain shapes as schema fragments
  when Config is present.
- Schema fragments are namespaced to avoid collisions.
- TOML is the v0 human-authored format; JSON-compatible objects are the v0
  machine contract format.
- Config Safety Status is machine-visible.
- Mutation-capable behavior fails closed unless the effective configuration is
  `usable`.
- Secret references may appear in config; secret values must not. Direct secret
  values produce unsafe, redacted output.
- Read-time migrations may explain stale config; source rewrites require an
  explicit audited mutation.
- Deliberate config source writes require explicit edit intent, eligible source
  category, trusted provenance, applicable authority, reviewable diff, final
  source precondition check, and audit evidence.

## Output contract

Deterministic surfaces emit JSON-compatible objects for:

- schema registration results,
- effective-config output with value provenance,
- config-diff output,
- conflict diagnostics,
- semantic validator diagnostics,
- migration previews,
- migration-apply decisions, refusals, mutations, and audit records,
- authoring apply decisions, refusals, mutations, and audit records,
- MCP tool metadata and structured tool-call results,
- edit intent and refusal evidence for deliberate source changes,
- secret reference resolution status,
- secret boundary violation diagnostics,
- onboarding status and partial config handoff plans,
- consumer action decision evidence,
- policy decision audit records.

## Failure modes

- Missing shared Config equipment: equipment falls back to explicit
  session-scoped behavior and plain equipment-specific config handoff.
- Partial config: output is schema-valid but has Config Safety Status
  `incomplete`.
- Unsafe policy: output is `unsafe` and mutation-capable behavior fails closed.
- Stale schema version: read-time migrations may preview results, but
  mutation-capable behavior remains `stale` until policy accepts or applies the
  migration.
- Untrusted source: output is `untrusted` for behavior that requires accepted
  provenance.
- Conflict: output is `conflicted` until blocked override, same-precedence
  collision, or schema conflict is resolved.
- Semantic conflict or missing authority: output is `unsafe` until the
  behavior policy or authority gap is resolved.
- Unsupported required capability: mutation-capable behavior fails closed, and
  the consuming equipment may continue only through an explicit advisory or
  plain-handoff fallback.

## Evidence

- Source-supported: this repository's Config template, Repo Ops spec, Issue
  Tracker Ops bundle, Forge runbooks, security guidance, and validator.
- Implementation inference: TOML matches existing human-authored config
  examples; JSON-compatible output matches deterministic tool and agent
  consumption needs.

## Open questions

- Which harness projection should gain blocking enforcement before advisory
  fallback documentation?
- Which child issue owns the first onboarding and re-onboarding flow?
