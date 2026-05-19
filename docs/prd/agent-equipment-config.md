# Agent Equipment Config PRD

Status: Repo Draft PRD

## 1. Executive Summary

**Problem Statement**: Agent Equipment needs shared configuration for policy,
defaults, local choices, authority, safety status, migrations, and audit
evidence. Without a common Config primitive, each equipment line invents its own
policy surface or depends on a higher-level equipment line that should be a
consumer, not the owner.

**Proposed Solution**: Build Agent Equipment Config as independent Agent
Equipment with a deterministic runtime, typed schema fragments, explicit load
contracts, fluent CLI operations, MCP parity for agent fluency, and documented
edit boundaries. The fluent CLI wraps the runtime implementation, while the
implementation command names remain available for debugging and evidence
comparison.

**Success Criteria**:

- Equipment can load, validate, explain, compare, onboard, and migrate
  configuration through stable CLI operations.
- Agents can perform the same safe operation families through MCP tools with
  typed inputs and outputs instead of manual parsing or ad hoc script glue.
- Mutation-capable behavior fails closed unless effective Config is usable,
  required authority is present, and the chosen surface owns the write.
- Smiths and Wielders can discover the right Config operation without reading
  the implementation code or reconstructing issue history.
- Deferred authoring and general edit capabilities are tracked in a named
  follow-up epic without blocking the MVP unless a child is explicitly promoted.

## 2. User Experience And Functionality

**User Personas**:

- **Smith**: an Agent creating Config-aware Agent Equipment.
- **Wielder**: an operator or Agent supplying project, local, checkout, or
  session configuration to equipment.
- **Outfitter**: an Agent choosing how Config should appear in a harness,
  plugin, hook, skill, CLI, or MCP surface.
- **Config-aware equipment**: equipment that consumes effective Config before
  advisory behavior, mutation, external calls, hook execution, workflow changes,
  or durable publication.
- **Human maintainer**: a person who reviews Config changes, debugs unexpected
  policy outcomes, and keeps the product and spec surfaces aligned.

**User Stories**:

- As a Smith, I want a shared Config primitive so that my equipment can declare
  a plain handoff shape first and later consume typed shared policy without
  owning the generic config system.
- As a Wielder, I want a universal CLI so that I can discover, copy, paste,
  debug, and script Config operations without a harness-specific tool.
- As an Agent, I want MCP tools for Config so that I can skip CLI discovery and
  operate through structured, typed calls when the harness exposes them.
- As Config-aware equipment, I want deterministic effective-config and
  validation evidence so that I can fail closed for unsafe mutation-capable
  behavior.
- As a maintainer, I want migration and audit evidence attached to the write
  operation so that source changes are reviewable and explainable.

**Acceptance Criteria**:

- The product surface names these MVP CLI operation families:
  `config resolve`, `config validate`, `config diff`, `onboard config`,
  `migrate config preview`, and `migrate config apply`.
- MCP parity is required before #23 closes. MCP v1 mirrors the safe CLI/runtime
  slice through `config.resolve`, `config.validate`, `config.diff`,
  `onboard.config`, `migrate.config_preview`, and
  `migrate.config_apply`.
- `config resolve` is the full read, explain, and trace surface. It returns
  effective values, provenance, diagnostics, safety status, enforcement
  projection, and related evidence.
- `config validate` is a lower-noise pass/fail surface. It reports diagnostics,
  safety status, authority readiness, fragment readiness, and suitable exit
  status without dumping the full effective config unless an option requests it.
  It validates mutation readiness by default while allowing explicit advisory
  checks.
- `config diff` compares effective Config outputs.
- `onboard config` owns onboarding, resume, restart, and revise-planning output.
  It does not write source config in the MVP.
- `migrate config preview` and `migrate config apply` own registered migration
  dry-runs, authorized migration writes, refusal records, and mutation audit
  evidence for eligible local TOML sources.
- `audit` remains attached to mutation-capable operations. The MVP does not
  introduce a standalone `config audit` operation.
- Skills and docs route agents to CLI and MCP usage. They are not substitutes
  for the agent-facing operation surfaces.
- Ad hoc scripts may support implementation, tests, or maintenance, but they
  are not the public Config operation surface.
- General non-migration `config propose`, `config patch`, and `config apply`
  authoring surfaces are deferred into the **Config Authoring Surfaces** epic
  bucket.

**Non-Goals**:

- Do not make Agent Equipment Config a component of Agent Ops, Issue Tracker
  Ops, Periodic Actions, Harness Capability Profiles, or Repo Ops.
- Do not require every equipment invocation to have shared Config present.
- Do not resolve secret values or mutate secret providers.
- Do not mutate external systems through the core Config runtime.
- Do not expose general source patching or revision writes in the MVP.
- Do not treat manual-parsing skills or one-off scripts as equivalent to a
  fluent CLI or typed MCP surface.

## 3. AI System Requirements

**Tool Requirements**:

- A deterministic Python runtime remains the implementation and debug path:
  `tools/agent_equipment_config.py` and importable functions in
  `tools.agent_equipment_config`.
- The MVP CLI must provide the fluent operation vocabulary while preserving the
  current runtime's JSON-compatible output contracts.
- MCP tools must expose typed input and output contracts that map clearly to
  the fluent CLI operations.
- GitHub Issues must carry blocker and follow-up issues for MVP CLI fluency,
  MCP parity, integration guides, and the Config Authoring Surfaces bucket.
- Armory Integrity Validation must keep the Config PRD and Config bundle paths
  visible as required repository surfaces.

**Evaluation Strategy**:

- Validate deterministic runtime behavior with
  `python3.14 -m unittest tests.test_agent_equipment_config`.
- Validate repository shape, links, and required Config surfaces with
  `python3.14 tools/validate_armory_integrity.py --final-closeout`.
- Check CLI and MCP parity by mapping every MVP CLI operation to one MCP tool
  and one underlying runtime behavior.
- Check `config validate` with both passing and blocking Config examples,
  including usable, incomplete, unsafe, stale, untrusted, conflicted, missing
  authority, and unsupported capability outcomes.
- Review MCP tool definitions for side-effect classification, auth source,
  failure modes, and mutation gates before treating them as merge-ready.
- Use Issue Tracker Ops pressure scenarios to confirm consuming equipment can
  fail closed for live mutation when Config evidence is blocking.

## 4. Technical Specifications

**Architecture Overview**:

Agent Equipment Config separates product surfaces from implementation contracts:

- The PRD states product requirements, user-facing operation vocabulary, MVP
  blockers, and deferred epic buckets.
- The Equipment Design Bundle under `specs/agent-equipment-config/` states
  exact runtime contracts, source ownership, security/control classification,
  pressure scenarios, validation, and closeout evidence.
- The runtime script and importable Python module implement deterministic
  effective-config, config-diff, onboarding-plan, migration-apply, diagnostics,
  consumer action decisions, and audit output.
- The CLI is the universal surface for agents and technically inclined humans:
  discoverable, self-onboardable, debuggable, scriptable, stable, low-noise,
  and copy/paste-friendly.
- MCP is the agent-fluency surface: typed, structured, and shaped so an agent
  can go directly to the right operation without manual command discovery.

**MVP Operation Map**:

| Product operation | Current implementation basis | Required output shape |
| --- | --- | --- |
| `config resolve` | `effective-config` | Full effective Config, provenance, diagnostics, safety status, enforcement projection, migration previews, and promoted handoff evidence. |
| `config validate` | Effective-config validation and safety classification | Lower-noise diagnostics, safety status, authority readiness, fragment readiness, and pass/fail status. |
| `config diff` | `config-diff` | Differences between effective Config outputs, including values, secret-reference identity, diagnostics, and status changes. |
| `onboard config` | `onboarding-plan` | Missing, partial, interrupted, resumed, restarted, and revise-planning output. |
| `migrate config preview` | `migration-apply` without apply | Dry-run migration plan, exact changes, refusals, audit preview, and no source write. |
| `migrate config apply` | `migration-apply --apply` | Authorized registered migration writes for eligible TOML sources, refusal handling, source precondition checks, and mutation audit records. |

**MCP Parity Map**:

| CLI operation | MCP tool |
| --- | --- |
| `config resolve` | `config.resolve` |
| `config validate` | `config.validate` |
| `config diff` | `config.diff` |
| `onboard config` | `onboard.config` |
| `migrate config preview` | `migrate.config_preview` |
| `migrate config apply` | `migrate.config_apply` |

MCP v1 stays constrained to parity with the current safe CLI/runtime slice.
General edit planning, patching, and applying belong to later MCP revisions
after their CLI and source-write contracts are specified.

**Integration Points**:

- Config-aware equipment registers schema fragments and consumes effective
  Config or validation output before deciding whether advisory or mutation
  behavior may continue.
- Harness adapters, hooks, skills, plugins, and repository tools discover layer
  paths and schema fragments, then call the CLI or MCP surface. The core runtime
  does not discover files by itself.
- Issue Tracker Ops remains the first concrete pressure consumer for policy,
  authority, advisory fallback, and fail-closed tracker mutation behavior.
- Integration guides explain how Smiths and Wielders use the CLI/MCP surfaces
  after the MVP operation split is implemented.

**Security And Privacy**:

- Config stores secret references, not secret values.
- Provider-specific secret resolution belongs to harnesses, tools, or adapters,
  not to the core Config merge engine.
- Direct secret values are unsafe Config input and must be redacted from
  published output.
- Mutation-capable behavior requires usable effective Config, applicable
  authority, supported capability, validation success, and a surface that owns
  the requested write.
- Migration apply writes only eligible local TOML sources under explicit
  authority and source precondition checks.
- MCP mutation-capable tools must classify side effects, auth source, approval
  requirements, failure modes, and audit evidence before publication.
- Local-only and session-scoped evidence must not be promoted to durable project
  truth without a separate eligible target and authority.

## 5. Risks And Roadmap

**Phased Rollout**:

- **MVP**: Maintain the current runtime slice and fluent CLI operation
  vocabulary; add MCP parity for the safe runtime slice; publish integration
  guides; preserve edit-boundary constraints.
- **v1.1**: Prove consumption through Issue Tracker Ops or another concrete
  consuming equipment line; refine validation and onboarding examples from real
  use.
- **v2.0**: Promote Config Authoring Surfaces for general proposal, patch,
  source-target selection, general apply, richer audit/query behavior, and MCP
  revisions for those capabilities.

**Blocker Map**:

- #23 remains blocked until the MVP CLI fluency (#91), MCP parity (#92), and
  integration guide (#78) surfaces are complete.
- #78 owns the integration-guide slice for the MVP operation surface. #91, #92,
  and #93 track CLI fluency, MCP parity, and deferred authoring follow-up work.
- **Config Authoring Surfaces** is a non-blocking follow-up epic bucket unless
  a child issue is explicitly promoted into MVP scope. #93 owns that bucket.

**Technical Risks**:

- CLI and MCP may drift if they are implemented as separate products. Mitigate
  by treating CLI/MCP parity as an explicit acceptance criterion.
- MCP can hide useful debugging context if it skips too much discovery. Mitigate
  by preserving clear links from each MCP tool to the corresponding CLI command
  and runtime evidence.
- `config validate` can become noisy if it returns the full effective config by
  default. Mitigate with a lower-noise contract and an explicit full-output
  option when needed.
- Deferred authoring work can leak into MVP. Mitigate by routing forward-looking
  work into the Config Authoring Surfaces bucket and keeping current source
  writes limited to migration apply.
