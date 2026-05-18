# Agent Equipment Config

Status: Equipment Blueprint
Promotion state: planned

This Equipment Design Bundle describes desired behavior and includes the first
standard-library runtime engine slice for effective-config, config-diff,
diagnostics, plain handoff promotion, authority checks, projection
classification, onboarding-plan output, explicit migration apply, and the
published runtime guide. It does not resolve secrets, mutate external systems,
or implement harness controls. The Blueprint itself does not implement Agent Equipment.
The runtime guide names the currently published slice.

Issue: [#23](https://github.com/nisavid/agent-armory/issues/23)

## Purpose

Agent Equipment Config is the shared configuration primitive for Agent
Equipment. It lets equipment declare typed schemas and namespaced schema
fragments, compose layered config, explain effective-config results, produce
config-diff output, and project enforceable policy without making Agent Ops,
Issue Tracker Ops, Periodic Actions, Harness Capability Profiles, recurring
Harness Capability Refresh, or future equipment own the generic config system.

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

## Runtime slice

The first runtime slice provides a standard-library Python effective-config
engine for deterministic validation and pressure coverage. It previews source
migrations, classifies enforcement projections, and emits onboarding-plan
output for missing, partial, interrupted, resumed, and restarted configuration
flows. It also applies registered source migrations to eligible TOML sources
after dry-run review and an explicit authority gate. It does not resolve
secrets, mutate external systems, or implement harness controls.

Published usage guidance lives in
[docs/equipment/agent-equipment-config.md](../../docs/equipment/agent-equipment-config.md).

### Load contract

The runtime uses explicit caller-supplied inputs. It does not discover default
paths, import schema fragments from equipment packages, scan hook or plugin
directories, resolve secret values, or decide harness enforcement.

Scripts, hooks, harness adapters, repository equipment, and operators own these
load duties:

- discover candidate config paths through their own harness or repository
  conventions;
- select which sources apply to the requested behavior;
- pass authored TOML layers through `--layer` or Python `layer_paths`;
- pass plain session handoffs through `--plain-handoff` or
  `plain_handoff_paths`;
- order same-precedence sources deliberately;
- register schema fragments before validation;
- preserve and consume the provenance, diagnostics, discovery proposals,
  migration previews, refusals, and audit records emitted by the runtime.

Authored TOML layers declare `agent_equipment_config.layer.name`,
`agent_equipment_config.layer.category`, and optional
`agent_equipment_config.layer.trusted`. Layer `name` maps to Layer Precedence.
Layer `category` must be one of the source categories below. `trusted = false`
keeps the source visible for diagnostics without letting it authorize mutation.

Schema fragments are caller-registered. Python callers pass `SchemaFragment`
objects to the runtime functions. CLI callers use explicit fragment flags. The
current CLI exposes the bundled `--issue-tracker-ops` fragment; arbitrary CLI
schema-fragment registration belongs to a later integration surface.

### Consumption contract

Consuming equipment derives its own consumer action decision from effective
Config output. Shared Config does not know every equipment action; it provides
machine-visible evidence that a consumer evaluates against its own side-effect
boundary.

The consumer must:

- register the equipment schema fragment before validation;
- keep defaults, required fields, migrations, semantic validators, and
  equipment-specific policy gates in that fragment;
- pass the requested behavior, such as advisory or mutation, into the Config
  runtime;
- inspect `safety_status`, diagnostics, provenance, policy authority evidence,
  secret reference metadata, migration previews, and
  `enforcement_projection`;
- emit a consumer action decision before mutation, external calls, hook
  execution, workflow changes, or durable publication.

Consumer action decision states:

| State | Required meaning |
| --- | --- |
| `allowed` | The requested behavior may run because effective Config is `usable`, consumer semantic validators pass, and the required capability is supported. |
| `advisory` | Read-only, dry-run, explanation, or model-facing guidance may continue, but no side effect is authorized. |
| `warning` | The requested behavior may run with visible non-blocking diagnostics, such as deprecation or migration-preview evidence. |
| `blocking` | The requested behavior must not run because Config is missing, incomplete, unsafe, stale, untrusted, conflicted, missing required Policy Authority, or otherwise classified as blocking for the behavior. |
| `unsupported` | The required capability cannot be applied by the consumer or harness; mutation-capable behavior fails closed and only an explicit safe fallback may continue. |

The runtime's `enforcement_projection` is evidence for this decision. It is not
the reusable consumer integration surface. That surface belongs to a separate
implementation slice.

Progressive fallback is required. A consumer uses a plain
equipment-specific session handoff when shared Config is absent. When effective
Config exists but cannot authorize the requested behavior, the consumer may
continue only with a narrower explicit behavior such as dry-run, read-only
explanation, advisory guidance, or no action. A fallback must not silently turn
an unsupported or blocking mutation into a write.

Example consumer-owned decision shape for Issue Tracker Ops:

```json
{
  "equipment": "issue_tracker_ops",
  "requested_behavior": "mutation",
  "state": "blocking",
  "source": "effective_config.enforcement_projection",
  "reason": "missing usable Policy Authority for live tracker writes",
  "fallback": "advisory dry-run"
}
```

### Runtime-slice harness projections

The runtime slice exposes one portable CLI. Each harness projection invokes the
CLI with the layer paths it can discover, receives effective-config,
config-diff, or migration-apply JSON, and treats `blocking` classifications as decision evidence
until a later harness adapter implements blocking controls.

| Harness | Discovery and exposure for this slice | Blocking and advisory boundary |
| --- | --- | --- |
| Codex | A Codex agent, hook, automation, or external `codex exec` wrapper supplies repository-committed TOML, local-only TOML, checkout-local state, generated state, `--plain-handoff` session TOML, and schema fragments through the Python module. Effective-config and config-diff JSON are printed to stdout or captured by the invoking agent surface. Secret references stay unresolved metadata. | The engine classifies mutation-unsafe output as `blocking`, but Codex enforcement remains advisory unless a future hook, permission profile, or automation wrapper consumes the JSON and blocks the action. |
| OpenClaw | An OpenClaw command, hook, cron job, heartbeat turn, or plugin background service supplies the same layer categories and schema fragments to the portable CLI. Effective-config and config-diff JSON are exposed through the invoking command or plugin surface. Secret references stay unresolved metadata. | The engine classifies blocking conditions deterministically; actual OpenClaw hook, webhook, cron, or plugin blocking remains a future adapter concern. |
| Hermes Agent | A Hermes Agent gateway hook, plugin hook, cron job, curator job, terminal process, or profile-driven command invokes the CLI with committed, local-only, checkout-local, generated, session, and secret-reference inputs. Effective-config and config-diff JSON are returned to the invoking agent surface. | Blocking classifications are decision evidence only until a Hermes-specific gateway, plugin, toolset, or profile adapter enforces them. |
| Claude Code | A Claude Code hook, Routine, scheduled task, or command invokes the CLI with the available layer paths and schema fragments. Effective-config and config-diff JSON are visible in the command output or captured task context. Secret references remain typed pointers. | Blocking classifications guide the agent or hook consumer; no Claude Code hook or settings enforcement is implemented in this slice. |
| Cursor | Cursor rules, hooks, Cloud Agent Automations, SDK agents, or CLI configuration can invoke the CLI with the discovered layer paths and schema fragments. Effective-config and config-diff JSON are exposed through the caller. Secret references remain unresolved metadata. | Blocking classifications are advisory until a Cursor hook, automation, SDK agent, or policy surface consumes the JSON and prevents the action. |
| OpenCode | An OpenCode command template, plugin hook, GitHub Action, external scheduler, or `opencode run` wrapper invokes the CLI with committed, local-only, checkout-local, generated, session, and secret-reference inputs. Effective-config and config-diff JSON are returned to the invoking surface. | Blocking classifications are not enforced by OpenCode in this slice; a future plugin hook, permission, or wrapper may turn them into blocking controls. |

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
Later or lower-authority layers cannot mint authority for an earlier Policy
Authority gate.

## Source categories

The v0 contract defines source categories and discovery duties rather than one
universal filename:

| Source category | Input surface | Core discovery | Mutation apply |
| --- | --- | --- | --- |
| `committed durable config` | `--layer` or `layer_paths` | None | Eligible after authority gates |
| `local-only operator config` | `--layer` or `layer_paths` | None | Eligible after authority gates |
| `checkout-local state` | `--layer` or `layer_paths` | None | Read-only |
| `generated cache or state` | `--layer` or `layer_paths` | None | Read-only |
| `secret reference source` | `--layer` or `layer_paths` | None | Read-only; unresolved secret metadata only |
| `session override` | `--layer`, `--plain-handoff`, `layer_paths`, or `plain_handoff_paths` | None | Read-only |

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
