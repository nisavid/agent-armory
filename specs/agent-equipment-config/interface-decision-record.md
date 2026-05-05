# Interface Decision Record: Agent Equipment Config

Status: Equipment Blueprint
Promotion state: planned

This Forge Entry Bundle describes desired behavior only. It does not implement Agent Equipment, publish assets, or provide a runtime config engine.

## Requirement

Agent Equipment Config needs a shared configuration contract that equipment can
consume without depending on Agent Ops or any other higher-level equipment. The
first deliverable must make the v0 contract implementable and validate the
source shape before a deterministic engine is built.

## Vision alignment

The Armory vision expects deterministic state, serialization, policy, and
side-effect boundaries to live outside model memory. Config should make
equipment behavior adaptable without burying policy in long skills or hidden
agent preference.

## Decision

Use a contract-first Forge Entry Bundle and validator gate for v0.

The v0 contract defines typed schemas, namespaced schema fragments, Layer
Precedence, Policy Authority, Config Safety Status, secret references,
migrations, effective-config output, config-diff output, semantic validators,
conflict diagnostics, and decision/mutation audit boundaries. It does not build
the runtime engine in this change set.

Use TOML for human-authored config layers and plain equipment-specific config
handoff records. Use JSON-compatible objects for schemas, effective-config
output, config-diff output, diagnostics, audit records, and deterministic tool
output.

## Chosen surface

- Local docs: this Forge Entry Bundle owns the current v0 behavior.
- Validator: `tools/validate_forge_seed.py` recognizes the bundle and required
  v0 terms.
- Config: future implementation owns authored TOML layers and source category
  discovery.
- Scripts/tools: future deterministic commands compute effective config,
  config diff, validation, migration preview, and audit records.
- Hooks/permissions/approvals/sandboxes/tools: future enforcement projections.
- Skills: future Smith/Wielder procedure around designing, onboarding, and
  repairing config.
- Plugins and Agent Profiles: future packaging and specialized execution.

## Rationale

Config is lower-level equipment. If its shared machinery lives in Agent Ops,
Issue Tracker Ops and other primitives would inherit a dependency cycle. If
every equipment line invents its own config machinery, policy, safety status,
and audit shapes drift.

The bundle-first route lets the repo preserve the existing Blueprint material,
settle the v0 contract, and create executable child issues before writing a
generic engine. Updating the validator keeps the repository's deterministic gate
aligned with the new source shape.

## Alternatives rejected

- Build the runtime engine first: rejected because the current broad Blueprint
  leaves too many schema, merge, authority, safety, migration, and output-shape
  decisions unresolved.
- Leave the flat spec as canonical: rejected because the Smith Runbook now uses
  Forge Entry Bundles for real Equipment Candidates that need capability,
  interface, security, pressure, validation, and closeout artifacts.
- Use a generic toy example as the main scenario: rejected because Issue Tracker
  Ops already provides realistic policy pressure without owning Config.
- Choose one universal config filename now: rejected because v0 should define
  source categories and projection duties before freezing harness-specific
  discovery paths.

## Harness-specific projection

Every later implementation slice must explain how Codex, OpenClaw, Hermes
Agent, Claude Code, Cursor, and OpenCode discover committed config, local-only
operator config, checkout-local state, session overrides, generated state, and
secret reference sources. Each projection must distinguish blocking controls
from advisory fallback.

## Risks

- The v0 contract could become too broad to implement. Child issues should keep
  engine, consumer integration, onboarding, harness projection, and enforcement
  work separate.
- Output examples could look like a final runtime schema. This bundle labels
  them as contract examples until implementation validates them.
- Harness enforcement claims can drift. Harness projection slices must use the
  Harness Capability Catalog and current source-backed refresh evidence.

## Maintenance notes

Review this decision when the first effective-config engine lands, when Issue
Tracker Ops consumes Config directly, when a harness projection gets blocking
enforcement, or when repeated use shows that a Config Safety Status or conflict
diagnostic category is too coarse.
