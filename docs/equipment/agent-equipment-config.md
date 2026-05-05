# Agent Equipment Config

Status: Published runtime slice
Promotion state: published

Agent Equipment Config is the shared configuration primitive for Agent
Equipment. The published runtime slice provides a local, standard-library
Python engine for loading authored TOML layers, composing schema fragments,
explaining effective configuration, comparing config outputs, and preserving
plain equipment-specific handoffs. It also exposes onboarding-plan output for
first-run, interrupted, resumed, and restarted configuration flows.

Use this guide when a Smith is making Config-aware equipment or when a Wielder
needs to provide local or session configuration for equipment that already
declares a schema fragment.

## What to use

- Runtime: `tools/agent_equipment_config.py`
- Blueprint: `specs/agent-equipment-config/`
- Example layer: `templates/config/agent-equipment-config-example.toml`
- Generic config template: `templates/config/example.toml`

The runtime reads local files supplied by the caller and emits JSON to stdout.
It does not discover files by itself, resolve secret values, mutate source
config, mutate external systems, or enforce harness controls. Harnesses,
skills, hooks, scripts, or operators choose which layer paths to pass in and
what to do with the resulting classification.

## Smith path

When designing Config-aware equipment:

1. Define the equipment's plain session-scoped config shape first.
2. Register that shape as a namespaced schema fragment when shared Config is
   available.
3. Keep generic layering, Policy Authority, conflict diagnostics, migration
   previews, and effective-config explanation in Agent Equipment Config.
4. Keep equipment-specific behavior, defaults, and safety rules in the
   consuming equipment's schema fragment and semantic validators.
5. Keep provider secret resolution and harness blocking controls outside the
   core Config runtime unless a later projection slice explicitly owns them.

The schema fragment boundary prevents Agent Equipment Config from depending on
the equipment that consumes it.

## Wielder path

When supplying config:

- Put durable project policy in committed config.
- Put machine-local choices in local-only config.
- Put checkout-local state in checkout-local state.
- Put per-session choices in session overrides or a plain handoff.
- Use secret references instead of secret values.
- Treat `blocking` projection output as a stop signal until the relevant
  policy owner or harness adapter decides otherwise.

Mutation-capable behavior should proceed only when the effective Config Safety
Status is `usable` and the required Policy Authority is present for the
requested behavior.

## Example layer

`templates/config/agent-equipment-config-example.toml` is a minimal
repository-policy layer. It demonstrates:

- layer metadata;
- fragment version metadata;
- a usable repository policy authority;
- non-overridable policy gates;
- equipment-specific values under the consuming equipment namespace.

Run it through the current Issue Tracker Ops pressure fragment with:

```bash
python3 tools/agent_equipment_config.py effective-config \
  --layer templates/config/agent-equipment-config-example.toml \
  --issue-tracker-ops \
  --requested-behavior advisory
```

The output should be `usable` for advisory dry-run behavior. Mutation behavior
remains governed by the consuming equipment's semantic validators and the
selected harness projection.

## Onboarding and authoring

Use `onboarding-plan` when a Smith or Wielder needs machine-visible next steps
instead of hidden preference. The command reports:

- `onboarding_status` for missing shared Config, missing config data,
  interrupted partial output, resumed completion, restarted authoring,
  blocked config, or complete config;
- `partial_config` with schema-valid sections, missing required fields, and
  unsafe write modes blocked while policy is incomplete;
- `handoff_behavior` for plain session handoffs and mutation-capable behavior;
- `discovery_proposals` for committed durable config, local-only operator
  config, checkout-local state, generated cache or state, and session override
  categories supplied by the caller;
- `revision_plan` for re-onboarding selected sections while preserving
  unrelated policy.

Example:

```bash
python3 tools/agent_equipment_config.py onboarding-plan \
  --layer templates/config/agent-equipment-config-example.toml \
  --issue-tracker-ops \
  --requested-behavior mutation \
  --onboarding-state resume \
  --revise-section issue_tracker_ops
```

Smiths author the equipment namespace: schema fragments, defaults, semantic
validators, policy gates, and any equipment-specific safety rules. Wielders
supply local, checkout, or session values without weakening committed policy
authority. Re-onboarding should revise the selected section and preserve
unselected sections unless a policy owner deliberately changes them. Unknown
section names fail before emitting a plan.

## Review and maintenance

Update this guide when:

- a new Config runtime command becomes the supported entry point;
- an equipment line consumes Config directly;
- onboarding-plan status, handoff, discovery, or revision output changes;
- a harness projection turns advisory classification into blocking behavior;
- secret-reference handling changes;
- migration behavior begins writing source config.

Security closeout for Config publication must cover CLI output, diagnostics,
secret-reference redaction, local file reads, and any new write or enforcement
surface.
