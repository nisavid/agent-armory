# Config Template

## Purpose

Use this template for configuration that controls equipment enablement,
ownership, autonomy, review, and approval boundaries.

Use `example.toml` for the generic equipment config shape described below.

Use `agent-equipment-config-example.toml` for a loadable Agent Equipment Config
layer that exercises the v0 runtime.

Use `issue-tracker-ops-plain-handoff.toml` when a Smith or Wielder needs a
session-scoped Issue Tracker Ops handoff to pass with
`--config-plain-handoff`.

## Required fields

For `example.toml`:

- Ownership.
- Autonomy.
- Enabled state.
- Review policy.
- Approval policy.

## Optional fields

For `example.toml`:

- Harness-specific overrides.
- Environment selection.
- Default paths.
- Logging or audit settings.
- Migration notes.

## Common mistakes

- Treating config as consent for risky actions without an approval rule.
- Leaving ownership implicit.
- Enabling a capability by default before validation.
- Mixing local workstation paths into portable examples.

## Validation expectations

- The TOML parses.
- The Agent Equipment Config example resolves and validates through
  `tools/agent_equipment_config.py config resolve` and
  `tools/agent_equipment_config.py config validate`.
- Disabled-by-default examples stay disabled unless the doc states otherwise.
- Review and approval settings match the capability card.
- Harness-specific overrides do not weaken global policy silently.
