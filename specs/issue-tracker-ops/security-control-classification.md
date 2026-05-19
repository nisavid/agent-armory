# Security and Control Classification: Issue Tracker Ops

Status: Equipment Candidate
Promotion state: implemented for bootstrap MVP; full delivery remains open

## Scope

This classification covers the bootstrap GitHub Issues adapter and the Issue
Tracker Ops Equipment Design Bundle for issue #11. It does not certify the
future tracker-neutral core, onboarding flow, full Issue Ops config profile,
hooks, skills, Agent Profiles, plugins, or GitHub Projects extension.

## Operation classes

| Operation | Class | Bootstrap control |
| --- | --- | --- |
| Dry-run adapter operation | Advisory | No network call; JSON request preview. |
| Dependency list | Read | Requires `--execute`; uses `gh api` with read permission. |
| Label-axis audit | Read | Requires `--execute`; uses `gh api` with read permission and reports missing or conflicting baseline labels without mutation. |
| Issue create | Network write | Requires `--execute`; emits JSON audit output. |
| Issue update | Network write | Requires `--execute`; emits JSON audit output. |
| Issue comment | Network write and notification | Requires `--execute`; emits JSON audit output. |
| Dependency add/remove | Network write | Requires `--execute`; resolves issue number to REST `id` when needed and emits JSON audit output. |
| Config-aware mutation | Policy decision and adapter preflight | Uses explicit Config inputs only; `consumer_enforcement_projection` maps consumer decisions to allow or block behavior, and blocking or unsupported decisions fail closed before `gh` runs. |

## Assets

- GitHub repository issues, comments, labels, dependency relations, and future
  sub-issue relationships.
- Local `gh` authentication state and token.
- Issue bodies, comments, file references, source links, and validation evidence.
- Stakeholder priority, workflow status, board-column placement, assignment,
  readiness, selection, and delegation decisions.
- Reflection Findings, including session context, observed failures, workflow
  insights, and induced equipment candidates.

## Trust boundaries

- Agent reasoning to local CLI invocation.
- Local script to `gh` authenticated transport.
- Local worktree or body files to external GitHub issue content.
- Dry-run terminal output to logs, chat summaries, and review evidence.
- Repository policy to future organization, project, user, and session
  overrides.
- Issue Ops plain handoffs and Config layers to effective Config evidence and
  consumer action decisions.

## Controls

- Network operations default to dry-run.
- `--execute` is required for every bootstrap network operation.
- The script uses argument lists and JSON stdin for `gh api`; it does not invoke
  a shell.
- The API version header is explicit and overridable; the Accept header is
  explicit.
- The adapter emits JSON audit output for request shape, result, resolved IDs,
  and failure.
- When explicit Config inputs are supplied, mutation subcommands evaluate the
  Issue Ops Config fragment before side effects. Live mutation requires the
  configured mode to be `execute`, a consumer decision that is not `blocking`
  or `unsupported`, and an adapter preflight projection with
  `adapter_action = "allow"`.
- The adapter preflight records the effective Config Safety Status, diagnostic
  kinds, decision state, fallback, owner, and unsupported approval behavior in
  JSON audit output.
- Missing or uncertain auth, policy, adapter behavior, or tracker state fails
  closed for writes.

## Known gaps

- Config consumption is limited to the Issue Ops fragment, explicit layers,
  plain handoff promotion, and adapter-owned GitHub API mutation preflight.
- The broader Issue Ops config profile is not implemented yet.
- No duplicate detection or idempotency key behavior yet.
- No rollback or compensation beyond recording the failed or successful
  operation.
- No fallback reconciliation state yet.
- No rate-limit backoff beyond surfacing `gh api` failure.
- No redaction layer for body text in dry-run output.
- No hook-enforced approval gate beyond explicit `--execute`.
- No Reflection Finding redaction or routing policy beyond current issue
  projection discipline.

## Bootstrap security decision

The bootstrap MVP is acceptable for issue #11 only under provisional policy:
agents may preview operations freely, but live tracker writes require explicit
session intent and must be summarized in closeout evidence. Broader publication
requires the full security and control requirements tracked in issue #11 or
child issues.
