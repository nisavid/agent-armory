# Interface Decision Record: PR Review

Status: Framework Example
Promotion state: example

This Framework Example is not Published Agent Equipment and is not installable.
Trace: [capability card](capability-card.md) -> interface decision record -> [projected components](projected-components.md).

## Requirement

The PR review capability needs procedural judgment, repository-local policy, deterministic changed-file support, optional forge reads, and tightly gated write actions.

## Decision

Use a skill for review judgment, scripts for deterministic file and test selection, local docs for policy, a read-only Agent Profile for specialist review, and gated tools or hooks for any forge mutation.

## Chosen surface

- Skill: review procedure, finding priorities, output contract.
- MCP/tool: forge read APIs and optional approved review-comment write APIs.
- Hook: mutation gate for comments, review submission, thread resolution, or merge actions.
- Agent Profile: read-only reviewer identity with bounded tools.
- Plugin: deferred portable bundle.
- Script: changed-file and test-target helpers.
- Config: repo-specific mutation authority and severity policy.
- Local docs: source of truth for repo review policy.

## Rationale

The review itself requires model judgment, so the procedure belongs in a skill. The model should not hand-select test targets when a deterministic script can do it. Comments, review submissions, labels, and merges are user-visible mutations, so they need hooks, permissions, or approvals instead of skill prose.

## Evidence category

Implementation inference. The example applies the Framework decision tree to a common workflow without asserting that these exact components work in any harness.

## Harness-specific projection

- Codex: use a read-only review subagent, local git inspection, and GitHub MCP or `gh` reads when available.
- Claude Code: project to a skill plus repository tools after the Smith confirms tool and permission semantics.
- Cursor: project to local docs and scripts first; defer forge write behavior until the harness surface is confirmed.
- Hermes Agent, OpenCode, OpenClaw: keep as deferred targets until harness-specific review and tool contracts are documented.

## Alternatives rejected

- Single large skill: rejected because it would mix policy, deterministic routing, mutable operations, and procedural judgment.
- Hook-only review: rejected because hooks can enforce gates but cannot perform rich review judgment.
- Forge bot only: rejected because repo-local policy and local tests remain central to the review.

## Risks

- External disclosure if private diffs are sent to an external reviewer.
- Stale PR metadata if the branch changes during review.
- Context overrun if all repo policy is duplicated into the skill.
- Operator confusion if example components look publishable.

## Maintenance notes

Review this decision when a harness adds new review APIs, when the repo changes mutation authority, when CI or test routing changes, or when repeated review findings show the output contract is too vague.
