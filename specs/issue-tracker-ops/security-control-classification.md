# Security and Control Classification: Issue Tracker Ops

Status: Equipment Candidate
Promotion state: implemented for bootstrap MVP; full delivery remains open

## Scope

This classification covers the tracker-neutral core, bootstrap GitHub Issues
adapter, and Issue Tracker Ops Equipment Design Bundle for issue #11. It does
not certify runtime onboarding implementation, hooks, skills, Agent Profiles,
plugins, MCP publication, or GitHub Projects extension. The desired Issue Ops
config profile and onboarding control contract is specified in
[Config profile and onboarding](config-profile-and-onboarding.md).

## Operation classes

| Operation | Class | Bootstrap control |
| --- | --- | --- |
| Core or adapter description | Advisory | Read-only local JSON; no `gh` call. |
| Operation plan | Advisory | Read-only local JSON; no `gh` call. |
| Dry-run adapter operation | Advisory | No network call; JSON request preview. |
| Dependency list | Read | Requires `--execute`; uses `gh api` with read permission. |
| Label-axis audit | Read | Requires `--execute`; uses `gh api` with read permission and reports missing or conflicting baseline labels without mutation. |
| Issue create | Network write | Requires `--execute`; emits JSON audit output. |
| Issue update | Network write | Requires `--execute`; emits JSON audit output. |
| Issue comment | Network write and notification | Requires `--execute`; emits JSON audit output. |
| Dependency add/remove | Network write | Requires `--execute`; resolves issue number to REST `id` when needed and emits JSON audit output. |
| Config-aware mutation | Policy decision and adapter preflight | Uses explicit Config inputs only; `consumer_enforcement_projection` maps consumer decisions to allow or block behavior, and blocking or unsupported decisions fail closed before `gh` runs. |
| Fallback reconciliation | Read and optional local write | Reads tracker state under `--execute`; `--retire-record` updates only the explicitly supplied fallback record after projection is verified. |

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
- Tracker failure summaries to optional local fallback records.

## Controls

- Network operations default to dry-run.
- `--execute` is required for every bootstrap network operation.
- The script uses argument lists and JSON stdin for `gh api`; it does not invoke
  a shell.
- The API version header is explicit and overridable; the Accept header is
  explicit.
- The adapter emits JSON audit output for request shape, result, resolved IDs,
  and failure.
- Live mutation without Config input requires `--mutation-policy-ref`; Config
  input takes precedence and can still fail closed.
- Live mutation preflights block exact duplicate issue titles and comment
  bodies, skip exact no-op issue updates, and skip already-applied or
  already-absent dependency changes before the write call.
- Failed live mutations classify auth, permission, validation, conflict,
  rate-limit, secondary-rate-limit, outage, not-found, and unknown failures,
  and emit retry conditions and compensation guidance. The adapter does not
  auto-retry writes.
- The tracker-neutral core emits read-only JSON for operation ids, operation
  classes, side-effect classes, capability dispositions, adapter capabilities,
  audit requirements, and operation plans. These inspection commands do not
  invoke `gh`.
- When explicit Config inputs are supplied, mutation subcommands evaluate the
  Issue Ops Config fragment before side effects. Live mutation requires the
  configured mode to be `execute`, a consumer decision that is not `blocking`
  or `unsupported`, and a present, well-formed adapter preflight projection
  with `adapter_action = "allow"`. Missing or malformed projection evidence
  fails closed before `gh` runs.
- A valid adapter preflight projection records the effective Config Safety
  Status, diagnostic kinds, decision state, fallback, owner, and unsupported
  approval behavior in JSON audit output.
- Optional fallback records use `issue_tracker_ops.fallback_record.v1alpha1`
  and are written only when callers provide `--fallback-record-file`.
- Missing or uncertain auth, policy, adapter behavior, or tracker state fails
  closed for writes.

## Known runtime gaps

- Config consumption is limited to the Issue Ops fragment, explicit layers,
  plain handoff promotion, and adapter-owned GitHub API mutation preflight.
- The broader Issue Ops config profile and onboarding behavior are specified but
  not implemented in the bootstrap adapter.
- Duplicate detection is exact-match bootstrap behavior, not semantic issue
  similarity across PRD linkage, dependencies, Reflection Findings, or closed
  issue history beyond the configured issue scope.
- Idempotency keys are audit metadata; they do not create a durable server-side
  idempotency store.
- Compensation guidance is recorded for failed writes, but the adapter does not
  perform automatic rollback or repair mutations.
- No rate-limit backoff beyond surfacing `gh api` failure.
- No redaction layer for body text in dry-run output.
- No hook-enforced approval gate beyond explicit `--execute`.
- No Reflection Finding redaction or routing policy beyond current issue
  projection discipline.
- Core JSON output is additive and remains pre-publication until final Issue Ops
  validation and packaging.

## Bootstrap security decision

The bootstrap MVP is acceptable for issue #11 only under provisional policy:
agents may preview operations freely, but live tracker writes require explicit
session intent and must be summarized in closeout evidence. Broader publication
requires the full security and control requirements tracked in issue #11 or
child issues, including the profile and onboarding controls defined for issue
#13.
