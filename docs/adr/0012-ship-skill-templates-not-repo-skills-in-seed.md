# Ship Skill Templates, Not Repo Skills, in the Seed

The Framework Seed will include skill templates and runbook guidance, but it will not ship first-class repo-local skills. Real repo-local skills require a concrete recurring workflow and Pressure Scenario Validation before they become Published Agent Equipment.

## Considered Options

- Provide skill templates and guidance only.
- Ship one or more real repo-local skills in the seed.
- Defer all skill-related material.

## Consequences

- The seed can teach Smiths how to create skills without bypassing skill-writing discipline.
- Template paths such as `templates/skill/SKILL.md` and `templates/skill/README.md` are seed surfaces.
- A future `skills/` package should appear only after a Smith validates a real skill through the promotion path.
- The Smith runbook should define the expected Pressure Scenario Validation evidence before any repo-local skill is promoted.
