# Treat Repo Structure as Target, Not Mandate

The Forge Seed PRD will define the target repository structure, but implementation will create only files and directories with clear seed responsibilities. The handoff's proposed tree is an architectural target, not an unconditional directory mandate.

## Considered Options

- Define the full target structure in the PRD and implement only seed surfaces.
- Create the full handoff tree immediately, including placeholder directories.
- Avoid defining the target structure until every surface is needed.

## Consequences

- The PRD can preserve the intended architecture without cluttering the repo with empty or speculative paths.
- Implementation tasks must justify each created path by its seed role.
- Future Smiths can add reserved surfaces when their equipment or docs need them.
