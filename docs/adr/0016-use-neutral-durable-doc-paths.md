# Use Neutral Durable Doc Paths

Durable committed project documents will live in neutral repository paths named for their role, not under the skill, plugin, tool, or workflow that happened to create or execute them. For example, implementation plans belong under `docs/plans/` unless the document is intrinsically about a specific planning skill.

## Considered Options

- Use neutral project paths for durable docs.
- Store docs under the workflow or skill path that produced them.
- Decide placement ad hoc for each generated document.

## Consequences

- Future agents can discover project artifacts by repository role instead of knowing which workflow created them.
- Durable docs can still name the skills, plugins, tools, or workflows that should execute them.
- Skill-, plugin-, tool-, and workflow-specific paths remain appropriate for docs that are intrinsically about that specific surface.
