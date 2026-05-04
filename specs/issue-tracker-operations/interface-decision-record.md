# Interface Decision Record: Issue Tracker Operations

Status: Equipment Candidate
Promotion state: implemented for bootstrap MVP; full delivery remains open

## Requirement

Issue Tracker Operations needs procedural judgment, typed external tracker
operations, layered policy, dry-run safety, audit output, and future portability
across issue trackers and agent harnesses.

## Decision

Use a thin bootstrap script for GitHub Issues operations, a Forge Entry Bundle
for design and validation planning, future config for durable policy, future
skills for review and orchestration judgment, and future MCP/tools for the
tracker-neutral contract once the MVP proves the operation shape.

## Chosen surface

- Skill: deferred; will carry issue review, repair, enrichment, and orchestration
  judgment.
- MCP/tool: deferred for the tracker-neutral contract; the bootstrap adapter
  defines the operation shape first.
- Hook: deferred mutation gate for approval and audit enforcement.
- Agent Profile: deferred issue reviewer or orchestrator profile.
- Plugin: deferred portable bundle.
- Script: `tools/issue_tracker_ops.py` for the GitHub Issues-only bootstrap MVP.
- Config: deferred layered policy; bootstrap uses provisional CLI policy with
  dry-run default and `--execute` for mutation.
- Local docs: this Forge Entry Bundle records current design, security,
  validation, and closeout expectations.

## Rationale

The bootstrap gate requires working direct GitHub Issues operations now. A
standard-library script is the narrowest reliable surface available in the
current repository because it can validate request construction, enforce dry-run
default behavior, use the operator's existing `gh` authentication, and avoid
introducing a server or plugin before the tracker-neutral contract is stable.

Issue review and orchestration require model judgment, so they belong in skills
after the operation contract exists. Hard mutation policy belongs in hooks,
permissions, approvals, and typed config rather than skill prose. A future
MCP/tool surface is appropriate once the adapter contract can expose typed inputs
and outputs without relying on CLI command composition.

## Evidence category

- Documentation-supported: GitHub REST and `gh api` docs checked on 2026-05-04.
- Source-supported: adapter and unit tests in this repository.
- Implementation inference: the bootstrap script can become the reference
  behavior for a later MCP/tool adapter without becoming the final interface.

## Harness-specific projection

- Codex: use the script through local shell tools and GitHub MCP for issue
  orientation; mutation remains dry-run by default unless the active session
  explicitly executes it.
- Other harnesses: defer until the tracker-neutral core, config model, and
  mutation gates have stable contracts.

## Alternatives rejected

- Spec-only handoff: rejected because issue #11 requires a working GitHub
  Issues-only MVP or explicit stakeholder deferment before #10 can resume.
- GitHub MCP only: rejected because the current connector does not expose every
  required dependency operation and cannot serve as portable Equipment by itself.
- One large skill: rejected because it would mix procedural judgment,
  external mutations, policy, deterministic validation, and adapter behavior.
- Full plugin first: rejected because installation and bundle boundaries are not
  the blocker for the bootstrap gate.
- In-tree pending issue files as the primary record: rejected because direct
  tracker recording is the default and in-tree state is only fallback.

## Risks

- The script is GitHub-specific and not yet a tracker-neutral core.
- Dry-run output can expose issue body content in the terminal or logs.
- `gh` authentication and permissions are external to the script.
- GitHub API behavior may change; dependency and sub-issue features should be
  refreshed before promotion beyond the bootstrap MVP.
- The MVP does not yet implement onboarding, layered policy, duplicate
  detection, fallback reconciliation, or issue-set orchestration.

## Maintenance notes

Review this decision when GitHub changes issue dependency or sub-issue APIs,
when the GitHub MCP connector exposes equivalent dependency operations, when
Issue Tracker Operations gains a schema-backed config model, or when repeated
use shows the CLI contract is too narrow for real tracker orchestration.
