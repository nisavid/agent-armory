# Closeout Evidence Plan: Issue Tracker Ops

Status: Equipment Candidate
Promotion state: implemented for bootstrap MVP; full delivery remains open

## Durable project evidence

Commit durable evidence in neutral project paths when it remains accurate beyond
this review instance:

- Forge Entry Bundle records under `specs/issue-tracker-ops/`.
- Adapter source and tests under `tools/` and `tests/`.
- Updated Forge Canon or vocabulary surfaces.
- Security and documentation closeout summaries when they describe durable
  project state.

## Portable review evidence

Project portable summaries to issue #11, the PR body, and final handoff:

- exact validation commands and pass/fail status;
- live issue operations performed by the adapter;
- child issues created for remaining work;
- dependency relation changes or verification;
- security review scope, findings, fixes, suppressions, and residual risks;
- documentation closeout scope and unchanged rationale.

## Instance-scoped scratch evidence

Do not commit or externally project raw scratch material as project truth:

- raw `gh --verbose` output;
- local token, auth, or keyring details;
- copied terminal logs with host paths;
- temporary dry-run bodies containing private context;
- unreviewed security scan work directories.

Summarize scratch evidence by operation, scope, disposition, and durable
conclusion.

## Bootstrap closeout checklist

- Forge capability card or equivalent Tooling Gap capture exists.
- Interface decision is recorded.
- Security/control classification is recorded.
- Remaining work is decomposed into child issues or explicitly linked
  follow-ups.
- GitHub Issues-only MVP is delivered and validated.
- MVP covers direct issue create, update, comment, and dependency operations
  under provisional policy.
- Validation evidence is recorded.

## Full-delivery closeout

Issue #11 remains open until the tracker-neutral core, full GitHub adapter,
Projects extension or child issue, configuration/onboarding model, issue repair
and orchestration modes, security controls, fallback reconciliation, docs, and
full validation matrix are complete.
