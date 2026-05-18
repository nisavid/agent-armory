# Interface Decision Record: Agent Equipment Config

Status: Equipment Blueprint
Promotion state: planned

This Equipment Design Bundle describes desired behavior and includes the first
standard-library runtime engine slice for effective-config, config-diff,
diagnostics, plain handoff promotion, authority checks, and projection
classification, plus onboarding-plan and migration-apply output. It does not implement Agent Equipment beyond this runtime slice, publish assets, resolve
secrets, mutate external systems, or implement harness controls.

## Requirement

Agent Equipment Config needs a shared configuration contract that equipment can
consume without depending on Agent Ops or any other higher-level equipment. The
current deliverable keeps the v0 contract source-aligned and provides the first
portable deterministic engine slice for the covered config behaviors.

## Vision alignment

The Armory vision expects deterministic state, serialization, policy, and
side-effect boundaries to live outside model memory. Config should make
equipment behavior adaptable without burying policy in long skills or hidden
agent preference.

## Decision

Use an Equipment Design Bundle, validator gate, and portable standard-library Python
runtime slice for v0.

The v0 contract defines typed schemas, namespaced schema fragments, explicit
load duties, Layer Precedence, Policy Authority, Config Safety Status, secret
references, migrations, effective-config output, config-diff output, semantic
validators, conflict diagnostics, and decision/mutation audit boundaries. The
implemented runtime slice computes deterministic effective-config and
config-diff output, diagnostics, plain handoff promotion, authority checks,
onboarding-plan load-contract proposals, and projection classification;
harness adapters, arbitrary CLI fragment registration, and blocking enforcement
remain separate work.

The consumption contract keeps the final action decision with the consuming
equipment. Shared Config output supplies evidence; the consumer maps that
evidence to `allowed`, `advisory`, `warning`, `blocking`, or `unsupported`
before mutation, external calls, hook execution, workflow changes, or durable
publication. Mutation-capable behavior fails closed unless effective Config is
`usable`, required authority and semantic validators pass, and the required
capability is supported.

Use TOML for human-authored config layers and plain equipment-specific config
handoff records. Use JSON-compatible objects for schemas, effective-config
output, config-diff output, diagnostics, audit records, and deterministic tool
output.

## Chosen surface

- Local docs: this Equipment Design Bundle owns the current v0 behavior and runtime
  slice boundary.
- Validator: `tools/validate_armory_integrity.py` recognizes the bundle and required
  v0 terms.
- Config: authored TOML layers and source category discovery are input to the
  portable runtime slice.
- Scripts/tools: `tools/agent_equipment_config.py` computes effective config,
  config diff, validation diagnostics, migration previews, and projection
  classification for the v0 slice.
- Load contract: callers discover paths, select sources, order same-precedence
  inputs, register schema fragments, and pass explicit layer or handoff paths
  into the runtime; the runtime preserves layer, source category, source path,
  and trust provenance in output.
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
settle the v0 contract, and land a narrow portable engine before consumer and
harness integration. Updating the validator keeps the repository's deterministic
gate aligned with the current source and runtime shape.

## Alternatives rejected

- Build all runtime, consumer, onboarding, and harness enforcement behavior at
  once: rejected because those surfaces have different security and validation
  boundaries.
- Leave the flat spec as canonical: rejected because the Smith Runbook now uses
  Equipment Design Bundles for real Equipment Candidates that need capability,
  interface, security, pressure, validation, and closeout artifacts.
- Use a generic toy example as the main scenario: rejected because Issue Tracker
  Ops already provides realistic policy pressure without owning Config.
- Choose one universal config filename now: rejected because v0 should define
  source categories and projection duties before freezing harness-specific
  discovery paths.

## Load and harness-specific projection

Every later implementation slice must explain how Codex, OpenClaw, Hermes
Agent, Claude Code, Cursor, and OpenCode discover committed config, local-only
operator config, checkout-local state, session overrides, generated state, and
secret reference sources before invoking the runtime. Each projection must
distinguish path discovery, schema-fragment registration, provenance handling,
blocking controls, and advisory fallback.

## Risks

- The v0 contract could become too broad to implement. Child issues should keep
  engine, consumer integration, onboarding, harness projection, and enforcement
  work separate.
- Output examples could look like a final runtime schema. This bundle names the
  implemented portable slice and keeps consumer and harness-specific output
  commitments separate.
- Harness enforcement claims can drift. Harness projection slices must use
  Vanilla Harness Capability Profiles and current source-backed evidence.

## Maintenance notes

Review this decision when Issue Tracker Ops consumes Config directly, when a
harness projection gets blocking enforcement, or when repeated use shows that a
Config Safety Status or conflict diagnostic category is too coarse.
