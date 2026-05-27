# Interface Decision Record: Issue Tracker Ops

Status: Equipment Candidate
Promotion state: implemented for bootstrap MVP; full delivery remains open

## Requirement

Issue Tracker Ops, or Issue Ops for short, needs procedural judgment, typed
external tracker operations, layered priority and selection policy, dry-run
safety, audit output, and future portability across issue trackers and agent
harnesses.

## Vision alignment

Issue Ops makes the Armory's reflection and self-onboarding loop durable. It
keeps follow-up creation, dependency mapping, repair, enrichment, and equipment
candidate routing issue-tracked while deterministic adapter behavior and future
layered config keep tracker mutations out of vague model preference.

## Decision

Use a tracker-neutral core module, a thin bootstrap script for GitHub Issues
operations, an Equipment Design Bundle for design and validation planning,
Agent Equipment Config for durable layered policy, an advisory workflow
executor skill and Agent Profile for review and orchestration judgment, and
future MCP/tools that expose the same typed contracts as the core and CLI
inspection surfaces.

## Chosen surface

- Skill: `skills/issue-ops-workflow-executor/SKILL.md` carries advisory issue
  review, repair, enrichment, assignment, selection, pickup, and orchestration
  judgment by consuming `describe-workflows` and `plan-workflow`.
- MCP/tool: deferred for publication; the tracker-neutral core and CLI
  inspection commands define the typed operation shape first.
- Hook: deferred mutation gate for approval and audit enforcement.
- Agent Profile: `agents/issue-ops-workflow-executor/profile.toml` defines the
  bounded read-only worker shape for advisory workflow preparation.
- Plugin: deferred portable bundle.
- Script: `tools/issue_tracker_core.py` for the tracker-neutral contract and
  `tools/issue_tracker_ops.py` for GitHub Issues-only bootstrap runtime
  operations plus read-only contract inspection.
- Config: Agent Equipment Config supplies explicit layer loading, effective
  Config evidence, and reusable consumer action decisions. Issue Ops owns the
  `issue_tracker_ops` fragment, plain handoff ingestion, and adapter semantics:
  dry-run is the default, live mutation still requires `--execute`, and
  live mutation requires usable Config authorization or a
  `--mutation-policy-ref`; config-aware live mutation requires the configured
  mode to be `execute` with a non-blocking consumer decision. The broader Issue
  Ops config profile and onboarding contract is defined in
  [Config profile and onboarding](config-profile-and-onboarding.md).
- Local docs: this Equipment Design Bundle records current design, security,
  validation, and closeout expectations.

## Rationale

The bootstrap gate requires working direct GitHub Issues operations and an
inspectable neutral contract. Standard-library Python is the narrowest reliable
surface available in the current repository because it can validate request
construction, enforce dry-run default behavior, use the operator's existing
`gh` authentication, expose stable JSON contract descriptions, and avoid
introducing a server or plugin before the tracker-neutral contract is stable.

Issue review and orchestration require model judgment, so they belong in the
workflow executor skill and bounded Agent Profile while the deterministic core
continues to own operation plans and write gates. Hard mutation policy belongs
in hooks, permissions, approvals, and typed config rather than skill prose.
Generic layering, governance, migration, and effective-config output belong in
Agent Equipment Config so Issue Ops does not depend on Repo Ops for its
instantiated policy. A future MCP/tool surface is appropriate once the adapter
contract can expose typed inputs and outputs without relying on CLI command
composition.

## Evidence category

- Documentation-supported: GitHub REST and `gh api` docs checked on 2026-05-26.
- Source-supported: adapter and unit tests in this repository.
- Implementation inference: the bootstrap script can become the reference
  behavior for a later MCP/tool adapter without becoming the final interface.

## Harness-specific projection

- Codex: use the script through local shell tools and GitHub MCP for issue
  orientation; mutation remains dry-run by default unless the active session
  explicitly executes it with Config authorization or a mutation policy
  reference, and explicit Config inputs can fail closed before tracker writes.
- Other harnesses: defer until the tracker-neutral core, Issue Ops plain config
  profile, and mutation gates have stable contracts.

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

- The runtime adapter remains GitHub-specific; the tracker-neutral core
  describes operations and plans but does not execute them directly.
- Dry-run output can expose issue body content in the terminal or logs.
- `gh` authentication and permissions are external to the script.
- GitHub API behavior may change; dependency and sub-issue features should be
  refreshed before promotion beyond the bootstrap MVP.
- The MVP does not yet implement runtime onboarding, semantic duplicate scoring,
  MCP parity, or deterministic selection and orchestration engines beyond the
  advisory workflow skill/profile boundary.
- The Config consumer proof covers adapter execute-mode gating; broader Issue
  Ops policy fields and onboarding behavior are specified but remain outside
  this bootstrap runtime surface.

## Maintenance notes

Review this decision when GitHub changes issue dependency or sub-issue APIs,
when the GitHub MCP connector exposes equivalent dependency operations, when
Issue Ops implements the config profile and onboarding contract, or when
repeated use shows the CLI contract is too narrow for real tracker
orchestration.
