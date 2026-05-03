# Capability Card: PR Review

Status: Framework Example
Promotion state: example

This Framework Example is not Published Agent Equipment and is not installable.
Trace: capability card -> [interface decision record](interface-decision-record.md) -> projected components.

## Purpose

Review pull requests, local diffs, and branches for defects, regressions, security risk, missing tests, and repo convention drift.

## Users

- Human operator: wants risk-focused findings before merge or handoff.
- Root agent: needs a repeatable review path after a cohesive change set.
- Specialist agent: reviews a bounded diff with read-only context and a strict output contract.
- External system: may provide pull request metadata, changed files, checks, and comments.

## Target harnesses

- Codex: primary example target because it already supports repo inspection and review-oriented subagents.
- Claude Code, Cursor, Hermes Agent, OpenCode, OpenClaw: deferred until a Smith maps each harness's review, tool, and permission surfaces.

## Risks

- Security: review may expose private code or PR context to external systems.
- Privacy: PR metadata can include personal data, credentials in diffs, or private repository names.
- Reliability: false confidence if the reviewer sees only a partial diff or stale CI state.
- Context budget: broad repositories can overload always-loaded instructions.
- Human workflow: unsolicited comments or status changes can disrupt review ownership.

## External systems

- Local git worktree and commit graph.
- GitHub, GitLab, or another forge when PR metadata is needed.
- Local test runner, linter, or deterministic changed-file scripts if present.

## Side effects

Default side effect classification: read-only.

Potential side effects that require explicit gates before promotion:

- external disclosure when sending diffs or private metadata to external review services;
- local write when recording review evidence;
- network write when posting comments or changing PR state.

## Needed Harness Components

- Skills: PR review procedure and finding format.
- MCP/tools: forge metadata reader, optional review-comment writer behind approval.
- Hooks: block posting or merge-state mutation without approval.
- Agent Profiles: read-only reviewer profile with focused repository and forge access.
- Plugins: optional portable review bundle after validation.
- Scripts: changed-file classifier and test-target selector.
- Config: repository review policy, severity labels, allowed mutation targets.
- Docs: repo `AGENTS.md`, module policies, review closeout rules, and this example set.

## Hard rules

- Findings come first and include file and line references when available.
- Do not post comments, resolve threads, update labels, or merge without the active authority policy.
- Treat missing tests and unavailable CI as residual risk, not as clean evidence.
- Keep summary secondary to concrete review findings.

## Deterministic checks

- Changed-file enumeration.
- Targeted test selection.
- Markdown link validation for review documentation.
- Secret scan over diff snippets before external disclosure.

## Output contract

A review report with:

- blocking findings ordered by severity;
- non-blocking risks or test gaps;
- checks and evidence inspected;
- unresolved assumptions.

## Failure modes

- Missing PR metadata: continue with local diff and record the missing source.
- Unavailable test runner: report residual risk and do not infer pass.
- Potential secret in diff: fail closed before external disclosure.
- Mutation request without approval: stop at a proposed comment or action summary.

## Evidence

Evidence category: implementation inference for this example shape. A Smith must replace this with source-supported or documentation-supported harness facts before promotion.

## Open questions

- Which forge operations should be read-only by default for each target harness?
- Which review-comment mutations are operator-approved versus repo-policy-approved?
