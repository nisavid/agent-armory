# Issue Tracker

Issues and PRDs for this repo live in GitHub Issues for `nisavid/agent-armory`.

Use `tools/issue_tracker_ops.py` for Issue Tracker Ops (Issue Ops) bootstrap
modes that create, update, comment on, add dependency relations, remove
dependency relations, and list dependency relations for GitHub Issues.

Bootstrap adapter subcommands:

- `create-issue`
- `update-issue`
- `comment`
- `add-blocked-by`
- `remove-blocked-by`
- `list-blocked-by`
- `list-blocking`

The adapter defaults network operations to dry-run output; pass `--execute`
only when the active session allows the GitHub tracker operation.

Use the `gh` CLI directly when a needed GitHub Issues operation is outside the
bootstrap adapter's current modes, or when a skill needs a read-only query that
is simpler through `gh`.

## Reflection Findings

A Reflection Finding is durable output from manual or ad hoc reflection that
may inform future equipment, Forge policy, validation, config, workflow, or
documentation.

Before external projection, classify privacy and disclosure limits for the
reflected content. Redact session context, speculative priorities, or
operator-sensitive material that should not become durable issue-tracker
content.

Create or update a GitHub issue when a reflection produces an actionable,
publishable candidate. Route the finding to the narrowest owner issue when one
is clear. When the finding informs generic Reflection or cognition equipment,
link it to [#25](https://github.com/nisavid/agent-armory/issues/25).

Capture:

- session or work context;
- observed friction, failure, repeated pattern, or insight;
- induced equipment, policy, validator, config, workflow, or documentation
  candidate;
- routing target, parent issue, dependency, or deferment reason;
- evidence or source surface to scout later;
- confidence, urgency, and readiness;
- privacy or disclosure limits before external projection.

## Follow-Up Capture Fallback

GitHub Issues are the preferred active tracker for follow-up work. Use a local
follow-up capture only when a durable repo note is needed before issue
projection is available or appropriate.

Each follow-up capture should include:

- `Status: Follow-Up Capture`
- a `## Purpose` section,
- a `## Captured Requirements` section,
- a `## GitHub Issue Projection` section that explains why the GitHub issue is
  not created or updated yet.

Keep these captures narrow. They are not a general inventory, and they must not
remain as parallel trackers after projection. Once GitHub Issues carry the
active work, retire or consolidate the local capture and leave only durable
closeout or source-disposition evidence.
