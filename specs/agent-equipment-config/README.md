# Agent Equipment Config

Status: Equipment Blueprint
Promotion state: planned

This Forge Entry Bundle describes desired behavior only. It does not implement Agent Equipment, publish assets, or provide a runtime config engine.

Issue: [#23](https://github.com/nisavid/agent-armory/issues/23)

## Purpose

Agent Equipment Config is the shared configuration primitive for Agent
Equipment. It lets equipment declare typed schemas and namespaced schema
fragments, compose layered config, explain effective-config results, produce
config-diff output, and project enforceable policy without making Agent Ops,
Issue Tracker Ops, Periodic Actions, Harness Capability Refresh, or future
equipment own the generic config system.

Agent Equipment Config is progressive enhancement. Equipment that accepts
configuration must still support session-scoped behavior and a plain
equipment-specific config handoff when the shared Config equipment is absent.
When Config is present, that plain shape becomes a schema fragment and policy
layer inside the shared system.

## Bundle map

- [Capability card](capability-card.md)
- [Interface decision record](interface-decision-record.md)
- [Security and control classification](security-control-classification.md)
- [Pressure scenarios](pressure-scenarios.md)
- [Validation plan](validation-plan.md)
- [Closeout evidence plan](closeout-evidence-plan.md)

## V0 contract

The v0 contract centers on explainable effective-config behavior:

- Layer Precedence defines the canonical value merge order.
- Policy Authority defines who may mark settings non-overridable or
  mutation-gated.
- Human-authored config layers and plain equipment-specific config handoff
  records use TOML.
- Schema fragments, effective-config output, config-diff output, semantic
  validators, conflict diagnostics, audit records, and deterministic tool output
  use JSON-compatible objects.
- Config Safety Status values are `usable`, `incomplete`, `unsafe`, `stale`,
  `untrusted`, and `conflicted`.
- Secret references describe where secrets are resolved without storing secret
  values in config.
- Migrations may run at read time for preview and diagnostics; source rewrites
  require an explicit audited config mutation.

## Layer Precedence

The canonical layer order is:

1. equipment defaults
2. harness or adapter defaults
3. organization or tracker policy
4. repository policy
5. project or issue-set policy
6. user/operator local overrides
7. checkout-local state
8. session overrides

Later layers normally win by Layer Precedence, but Policy Authority can block a
later value from overriding a non-overridable or mutation-gated setting. Blocked
values remain visible in diagnostics instead of silently disappearing.

## Source categories

The v0 contract defines source categories and discovery duties rather than one
universal filename:

- committed durable config
- local-only operator config
- checkout-local state
- session override
- generated cache or state
- secret reference source

Every harness or equipment projection must state where it discovers each
category and whether that category is committed, local-only, session-scoped, or
generated.

## Harness projections

Every implementation slice must discuss projections for:

- Codex
- OpenClaw
- Hermes Agent
- Claude Code
- Cursor
- OpenCode

Each projection states where committed config is discovered, where local-only
config is discovered, how session overrides are provided, which settings can be
blocked or enforced, which settings are advisory only, how secret references are
handled, how schema fragments are registered, and how effective-config output is
exposed to Agents and humans.

## Non-goals

- Agent Equipment Config is not Agent Ops.
- Agent Equipment Config is not Issue Tracker Ops, Periodic Actions, Harness
  Capability Refresh, a scheduler, a harness catalog, or a secret store.
- Agent Equipment Config does not make unconfigured equipment safe for writes.
- Agent Equipment Config does not require every equipment invocation to have a
  durable config file.
- Agent Equipment Config does not make the v0 contract a final runtime schema.
