# Issue Tracker

Issues and PRDs for this repo live in GitHub Issues for `nisavid/agent-armory`.

Use `tools/issue_tracker_ops.py` for Issue Tracker Ops, or Issue Ops,
bootstrap modes
that create, update, comment on, add dependency relations, remove dependency
relations, and list dependency relations for GitHub Issues.

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

## Follow-Up Captures

`docs/follow-ups/*.md` files are governed local captures for deferred work that
has not yet been projected into GitHub Issues.

Each follow-up capture should include:

- `Status: Follow-Up Capture`
- a `## Purpose` section,
- a `## Captured Requirements` section,
- a `## GitHub Issue Projection` section that explains why the GitHub issue is
  not created or updated yet.

Keep these captures narrow. They are not a general Inventory; they are the local
governing surface until Issue Projection validates the corresponding GitHub
issue.
