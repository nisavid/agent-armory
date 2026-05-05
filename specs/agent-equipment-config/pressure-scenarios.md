# Pressure Scenarios: Agent Equipment Config

Status: Equipment Blueprint
Promotion state: planned

This Forge Entry Bundle describes desired behavior and includes the first
standard-library runtime engine slice for effective-config, config-diff,
diagnostics, plain handoff promotion, authority checks, and projection
classification, plus onboarding-plan and migration-apply output. It does not implement Agent Equipment beyond this runtime slice, publish assets, resolve
secrets, mutate external systems, or implement harness controls.

## Primary scenario: Issue Tracker Ops

Issue Tracker Ops is the primary pressure scenario for v0 because it needs real
policy without owning the generic config system.

Scenario:

An Agent is using Issue Tracker Ops to choose and mutate GitHub issues. The
repository policy allows dry-run previews by default. Organization policy marks
external disclosure and live tracker writes as mutation-gated. The operator adds
a session override requesting `execute`. A project or issue-set policy changes
priority selection. A local-only operator layer names the preferred tracker
account. The GitHub token is represented by a secret reference.

Expected Config behavior:

- Layer Precedence explains which value would normally win.
- Policy Authority blocks the session override from enabling live writes unless
  the required approval rule is usable.
- The effective-config output shows the dry-run value, the blocked execute
  override, and the policy source that blocked it.
- The Config Safety Status is `usable` for advisory dry-run behavior and
  `unsafe` or `conflicted` for live mutation until authority is resolved.
- The secret reference status is reported without exposing the token value.
- Issue Tracker Ops remains able to serialize a plain equipment-specific config
  handoff if shared Config is absent.

Runtime coverage: `tests.test_agent_equipment_config` covers the blocked
session override path and missing-authority path for Issue Tracker Ops
mutation. The broader pressure scenario still needs harness-specific
enforcement implementation before promotion beyond `planned`.

## Partial onboarding

Scenario:

An onboarding flow discovers a repository and tracker, but the operator stops
before setting mutation authority or external disclosure policy.

Expected Config behavior:

- The partial TOML remains parseable and schema-valid.
- Effective-config output reports `incomplete`.
- Read-only and advisory behavior may continue.
- Mutation-capable behavior fails closed.
- Resume output shows which choices remain unresolved.

## Stale schema

Scenario:

Issue Tracker Ops publishes schema fragment version `2`, but a repository has a
version `1` TOML layer. The migration can translate the old key names for
preview, but applying the rewrite would change committed config.

Expected Config behavior:

- Read-time migration can show a preview effective-config.
- The original source remains unchanged.
- Mutation-capable behavior reports `stale` until policy accepts the migration
  or an explicit audited mutation rewrites the source.
- The audit record for a later apply action names the source layer, migration,
  and result.

## Same-precedence collision

Scenario:

Two repository policy files in the same layer define incompatible values for an
Issue Tracker Ops priority rule.

Expected Config behavior:

- Config emits a same-precedence collision diagnostic.
- No silent tie-breaker chooses a winner.
- Mutation-capable behavior is `conflicted`.
- Advisory output may include safe values not affected by the collision.

## Untrusted local override

Scenario:

A checkout-local state file requests a weaker approval rule, but the harness
cannot verify its provenance.

Expected Config behavior:

- The layer is visible in provenance.
- The requested behavior receives `untrusted`.
- The weaker approval rule cannot authorize mutation-capable behavior.

## Neutral schema fragment

Scenario:

A toy equipment fragment defines a harmless display preference with a default
and a local override.

Expected Config behavior:

- Namespacing prevents collision with Issue Tracker Ops keys.
- The default is visible as equipment defaults.
- The local override wins by Layer Precedence when no Policy Authority marker
  blocks it.
- The example remains illustrative and does not become a final runtime schema.
