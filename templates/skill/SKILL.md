<!-- Replace this commented frontmatter before publishing:
---
name: example-skill
description: Use when a Smith is drafting a reusable agent skill from a template in the Agent Armory
---
-->

# Skill: <name>

Status: Template

## Use when

- The workflow recurs across sessions, repositories, or agents.
- A future agent needs non-obvious judgment, sequencing, or policy.
- The behavior cannot be expressed more clearly as a deterministic script,
  schema, or validator.

## Do not use when

- The guidance is project-local policy that belongs in `AGENTS.md` or repo docs.
- The task is a one-time narrative rather than reusable procedure.
- The behavior is standard tool syntax better served by official docs.

## Preflight

1. Identify the target harness and skill discovery rules.
2. Read the relevant repo policy and durable docs.
3. Confirm whether scripts, validators, or references should carry part of the
   behavior instead of inline prose.
4. Define one or more pressure scenarios that should fail without the skill.

## Procedure

1. Write trigger-focused frontmatter.
2. State use and non-use boundaries.
3. Keep the procedure ordered, concrete, and short enough to be followed under
   context pressure.
4. Move bulky examples, command catalogs, or API references into separate files.
5. Verify the pressure scenarios after the skill is written.

## Output contract

The skill produces a `SKILL.md` that the target harness can discover, parse, and
apply without loading unrelated project history.

## Failure handling

- If pressure scenarios still fail, revise the smallest ambiguous section.
- If the skill grows too large, split heavy material into references or scripts.
- If the workflow is not reusable, record the lesson in the narrower project
  doc instead.

## Safety and policy notes

- Do not hide approval, security, or stakeholder policy in a skill when it must
  be always loaded.
- Document side effects and escalation boundaries explicitly.
- Prefer current desired behavior over historical contrast unless the history is
  itself the subject.
