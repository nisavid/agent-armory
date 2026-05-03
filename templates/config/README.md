# Config Template

## Purpose

Use this template for configuration that controls equipment enablement,
ownership, autonomy, review, and approval boundaries.

## Required fields

- Ownership.
- Autonomy.
- Enabled state.
- Review policy.
- Approval policy.

## Optional fields

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
- Disabled-by-default examples stay disabled unless the doc states otherwise.
- Review and approval settings match the capability card.
- Harness-specific overrides do not weaken global policy silently.
