# Use Preloaded Framework Path as Agent Discovery Criterion

The Framework Seed measures agent discovery success by whether a Smith receives the canonical Framework path from preloaded root `AGENTS.md`, without scouting. The README remains human-facing and provides a concise Human Framework Entry that explains the Framework and links to the canonical starting path.

## Considered Options

- Use a preloaded Framework path from root `AGENTS.md` as the agent success criterion.
- Use a concise README Framework entry as the human success criterion.
- Use one scout pass from the README as the agent success criterion.
- Use a human-scaled time budget.
- Leave reading-path success unmeasured.

## Consequences

- Root `AGENTS.md` must route Smiths to canonical docs for understanding the Framework, creating equipment, checking harness facts, using templates, and finding downstream Smith specs.
- `README.md` explains the Framework for humans and links to the canonical starting path without exposing agent-only machinery.
- Seed Validation checks that both link paths exist.
- Review verifies that the agent path is available without scouting and that the human path stays README-appropriate.
