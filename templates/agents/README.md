# Agent Profile Template

## Purpose

Use this template to define a bounded agent role with explicit mission, tools,
permissions, model preferences, and configuration placeholders.

The Framework calls this reusable configuration an Agent Profile. Harness and
plugin source paths commonly call the same component `agents`, so this template
uses `templates/agents/`.

## Required fields

- Identity.
- Mission.
- Allowed and denied tools.
- Permission mode.
- Model or inheritance policy.
- Configuration placeholders.
- Output contract, including the deliverable, return shape, and handoff
  expectations.

## Optional fields

- Nickname candidates.
- Output format.
- Review focus.
- Default docs to read.
- Escalation triggers.

## Common mistakes

- Granting broad tools because the role is convenient.
- Omitting denied tools when the role must stay read-only.
- Encoding stakeholder policy that belongs in `AGENTS.md`.
- Choosing model settings without stating whether they are required or inherited.

## Validation expectations

- The TOML parses.
- Required fields are present.
- Tools and permissions match the role's mission.
- The profile can be reviewed without reading unrelated project history.
