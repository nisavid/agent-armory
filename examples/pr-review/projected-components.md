# Projected Components: PR Review

Status: Forge Example
Promotion state: example

This Forge Example is not Published Agent Equipment and is not installable.
Trace: [capability card](capability-card.md) -> [interface decision record](interface-decision-record.md) -> projected components.

## Components

| Surface | Example projection | Promotion note |
| --- | --- | --- |
| Local docs | `docs/engineering/pr-review.md` | Canonical repo review policy. |
| Skill | `pr-review` | Thin procedure that points to docs and scripts. |
| Script | `scripts/changed-files --json` | Deterministic input for scope and test selection. |
| Script | `scripts/test-targets --changed-files changed-files.json --json` | Deterministic candidate checks. |
| Agent Profile | `agents/pr-reviewer.toml` | Read-only review worker profile. |
| Hook | `hooks/review-mutation-gate` | Blocks comments, thread resolution, review submission, and merge changes without authority. |
| MCP/tool | Forge PR metadata reader | Read-only PR metadata and check status. |
| Config | `config/pr-review.toml` | Severity vocabulary, mutation policy, and disclosure gates. |
| Plugin | `agent-armory-pr-review` | Deferred bundle after validation. |

## Minimal Smith Path

1. Confirm the capability in the [capability card](capability-card.md).
2. Keep this [interface decision record](interface-decision-record.md) aligned with any changed surface.
3. Implement read-only docs, scripts, and skill surfaces before any mutation-capable tool.
4. Add gates before review comments, status updates, thread changes, or merge operations.
5. Run pressure validation on a real PR or synthetic diff before any publication step.

## Non-Published Boundary

This example names plausible files and commands, but it does not ship those files. A Smith must create, test, review, security-scan, and validate them before the capability can leave `example` state.
