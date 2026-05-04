# Security and Control Classification: Issue Tracker Operations

Status: Equipment Candidate
Promotion state: implemented for bootstrap MVP; full delivery remains open

## Scope

This classification covers the bootstrap GitHub Issues adapter and the Forge
Entry Bundle for issue #11. It does not certify the future tracker-neutral core,
onboarding flow, hooks, skills, Agent Profiles, plugins, or GitHub Projects
extension.

## Operation classes

| Operation | Class | Bootstrap control |
| --- | --- | --- |
| Dry-run create/update/comment/dependency operation | Advisory | No network call; JSON request preview. |
| Dependency list | Read | Requires `--execute`; uses `gh api` with read permission. |
| Issue create | Network write | Requires `--execute`; emits JSON audit output. |
| Issue update | Network write | Requires `--execute`; emits JSON audit output. |
| Issue comment | Network write and notification | Requires `--execute`; emits JSON audit output. |
| Dependency add/remove | Network write | Requires `--execute`; resolves issue number to REST `id` when needed and emits JSON audit output. |

## Assets

- GitHub repository issues, comments, labels, dependency relations, and future
  sub-issue relationships.
- Local `gh` authentication state and token.
- Issue bodies, comments, file references, source links, and validation evidence.
- Stakeholder priority, assignment, readiness, and delegation decisions.

## Trust boundaries

- Agent reasoning to local CLI invocation.
- Local script to `gh` authenticated transport.
- Local worktree or body files to external GitHub issue content.
- Dry-run terminal output to logs, chat summaries, and review evidence.
- Repository policy to future organization, project, user, and session overrides.

## Controls

- Network operations default to dry-run.
- `--execute` is required for every bootstrap network operation.
- The script uses argument lists and JSON stdin for `gh api`; it does not invoke
  a shell.
- The API version and Accept headers are explicit and overridable.
- The adapter emits JSON audit output for request shape, result, resolved IDs,
  and failure.
- Missing or uncertain auth, policy, adapter behavior, or tracker state fails
  closed for writes.

## Known gaps

- No schema-backed layered configuration yet.
- No duplicate detection or idempotency key behavior yet.
- No rollback or compensation beyond recording the failed or successful
  operation.
- No fallback reconciliation state yet.
- No rate-limit backoff beyond surfacing `gh api` failure.
- No redaction layer for body text in dry-run output.
- No hook-enforced approval gate beyond explicit `--execute`.

## Bootstrap security decision

The bootstrap MVP is acceptable for issue #11 only under provisional policy:
agents may preview operations freely, but live tracker writes require explicit
session intent and must be summarized in closeout evidence. Broader publication
requires the full security and control requirements tracked in issue #11 or
child issues.
