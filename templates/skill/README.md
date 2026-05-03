# Skill Template

## Purpose

Use this template when turning a repeated agent procedure into a reusable skill.
Skills should load for recognizable work and stay out of unrelated sessions.

## Required fields

- Frontmatter with `name` and a trigger-focused `description`.
- `Status: Template` while this file remains a template.
- Sections for use boundaries, preflight, procedure, output contract, failure
  handling, and safety or policy notes.
- Evidence that the skill's instructions are needed and testable.

## Optional fields

- Quick reference tables.
- Short examples that clarify ambiguous decisions.
- Links to heavy references, scripts, or fixtures when inline text would bloat
  the skill.

## Common mistakes

- Summarizing the procedure in the description instead of writing trigger
  conditions.
- Making the skill a one-off incident story.
- Burying policy that belongs in `AGENTS.md`.
- Keeping mechanical checks in prose when a validator would be clearer.

## Validation expectations

- The frontmatter is valid for the target harness.
- The description starts with "Use when" and names trigger conditions.
- Pressure scenarios demonstrate the skill changes future agent behavior.
- Any referenced scripts, docs, or fixtures exist.
