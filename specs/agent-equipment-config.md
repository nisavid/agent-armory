# Agent Equipment Config Spec

Status: Equipment Blueprint
Promotion state: specified

This spec describes desired behavior for future Agent Equipment. It does not implement Agent Equipment, publish installable assets, or establish a final config schema.

## Purpose

Agent Equipment Config provides a shared configuration primitive for Agent
Equipment. It lets equipment declare typed schema fragments, compose layered
policy, report effective configuration, and project enforceable controls without
making any higher-level equipment own the generic config system.

Agent Equipment Config is independent equipment. Agent Ops, Issue Tracker Ops
or Issue Ops, Periodic Actions, Harness Capability Refresh, Reflection and
cognition equipment, and future equipment may consume it, but they must not be
prerequisites for it.

## User stories

### Equipment declares configuration

As a Smith, I can define the configuration shape an equipment line needs without
inventing a new config system for that equipment.

Each equipment line can provide:

- a namespace,
- a typed schema fragment,
- defaults,
- migration behavior,
- validation behavior,
- safety status for partial or missing config,
- enforcement projections.

### Layers compose predictably

As an Outfitter or Wielder, I can combine equipment defaults, harness defaults,
organization policy, repository policy, project or issue-set policy, local
operator choices, checkout-local state, and session overrides without hidden
precedence.

The effective configuration explains which layer supplied each value, which
rules could not be overridden, and which conflicts remain unresolved.

### Policy can be enforced

As a repository owner, I can mark selected settings as enforceable policy. The
equipped harness uses the strongest available projection for each rule: hook,
permission, sandbox, approval, tool gate, or advisory model-facing guidance.

### Equipment still works without shared config

As a Wielder, I can use equipment in a session even when Agent Equipment Config
is not installed.

An equipment line that accepts config must know enough of its own config shape
to:

- run with full session-scoped behavior under explicit session policy;
- serialize a plain equipment-specific config handoff;
- ingest that plain config handoff later;
- identify missing, partial, stale, or unsafe config;
- separate configured policy from hidden agent preference;
- fail closed for unsafe mutation-capable behavior when policy is incomplete.

When Agent Equipment Config is present, that plain equipment-specific shape
becomes a schema fragment in the shared config system.

## Acceptance criteria

- Agent Equipment Config supports typed schemas, validation, versioning, and
  migration behavior.
- Equipment schema fragments are namespaced and can be composed without key
  collisions.
- Layered config covers equipment defaults, harness or adapter defaults,
  organization/tracker policy, repository policy, project or issue-set policy,
  user/operator local overrides, checkout-local state, and session overrides.
- Governance rules define which layers may mark settings non-overridable by
  lower-authority layers.
- Effective-config output explains value sources, overrides, conflicts,
  assumptions, incomplete sections, confidence, and safety status.
- Config-diff output shows how two effective configs differ.
- Partial config remains schema-valid but machine-visible as incomplete or
  unsafe when needed.
- Secret handling stores references to secrets, not secrets.
- Mutation-capable settings can project to hooks, permissions, approvals,
  sandboxes, tools, or advisory guidance according to harness capability.
- Audit records capture policy decisions and config mutations.
- Plain equipment-specific config handoffs can be validated and promoted into
  Agent Equipment Config when the shared equipment is available.

## Harness projections

Every implementation must define projections for:

- Codex,
- OpenClaw,
- Hermes Agent,
- Claude Code,
- Cursor,
- OpenCode.

Each projection must describe:

- where committed config is discovered,
- where local-only config is discovered,
- how session overrides are provided,
- which settings can be blocked or enforced,
- which settings are advisory only,
- how secrets are referenced,
- how schema fragments are registered,
- how effective-config output is exposed to Agents and humans.

## Non-goals

- Agent Equipment Config is not Agent Ops.
- Agent Equipment Config is not an issue tracker, scheduler, harness catalog, or
  secret store.
- Agent Equipment Config does not make unconfigured equipment safe for writes.
- Agent Equipment Config does not require every equipment invocation to have a
  durable config file.
- Agent Equipment Config does not treat this Blueprint as a final schema
  contract.

## Open questions

- What source path should be canonical for committed equipment config?
- What source path should be canonical for local-only operator config?
- Which serialization formats belong in the first implementation?
- How should schema fragments identify upstream equipment versions?
- Which harnesses can enforce non-overridable settings directly, and which need
  advisory fallback?
