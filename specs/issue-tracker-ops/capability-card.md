# Capability Card: Issue Tracker Ops

Status: Equipment Candidate
Promotion state: implemented for bootstrap MVP; full delivery remains open

## Purpose

Record, review, repair, enrich, organize, assign, select, work, and orchestrate
issue-tracked follow-ups directly in an issue tracker without requiring
intermediate in-tree tracking state.

Issue Ops is accepted shorthand for Issue Tracker Ops.

## Vision alignment

Issue Ops supports the Armory vision by keeping follow-up capture,
dependencies, repair, enrichment, selection, orchestration, and Reflection
Findings in a durable tracker instead of scattered through chat or in-tree
fallback state. It lets agents route work systematically while deterministic
adapter operations, dry-run previews, audit output, and future config policy
keep tracker mutations explicit and governable.

## Users

- Human operator: wants durable issue-tracker artifacts instead of scattered
  follow-up notes.
- Root agent: needs a reliable issue lifecycle path during active repository
  work.
- Specialist agent: may inspect, repair, or operate bounded issue sets under a
  configured authority policy.
- External system: GitHub Issues is the required bootstrap tracker; other
  trackers are adapter targets after the core contract stabilizes.

## Target harnesses

- Codex: required bootstrap target through local repository tools, `gh`, and
  GitHub MCP reads/writes where available.
- Other harnesses: deferred until the tracker-neutral contract and GitHub
  adapter boundaries are stable.

## Risks

- Security: tracker mutations can alter public project state, create
  dependencies, notify subscribers, or expose private context.
- Privacy: issue bodies, comments, labels, and evidence links can disclose
  private repository, user, host, or session details.
- Reliability: duplicate issues, stale metadata, partial API failure, pagination
  gaps, or secondary rate limits can corrupt issue orchestration.
- Context budget: full issue-set orchestration can overload the model if raw
  issue bodies are copied into always-loaded instructions.
- Human workflow: unapproved tracker writes can override stakeholder ownership,
  status, priority, or delegation intent.

## External systems

- GitHub Issues REST API.
- Local `gh` CLI and its authenticated account.
- Local worktree files used as issue body, evidence, config, or validation
  inputs.

## Side effects

- Read-only: issue reads, dependency lists, dry-run previews, local validation.
- Network write: issue creation, issue updates, issue comments, dependency
  create/remove operations.
- External disclosure: issue bodies, comments, labels, links, and evidence sent
  to GitHub.
- Local write: committed Equipment Design Bundle and adapter implementation.

## Needed Harness Components

- Skills: issue review, repair, enrichment, issue selection, orchestration, and
  session pickup judgment.
- MCP/tools: tracker-neutral operations plus GitHub Issues adapter.
- Hooks: future mutation gates for policy enforcement and audit capture.
- Agent Profiles: future bounded issue reviewer or orchestrator profiles.
- Plugins: future portable Issue Tracker Ops bundle.
- Scripts: bootstrap GitHub Issues adapter and deterministic validation.
- Config: Agent Equipment Config for durable layered policy, plus an Issue
  Ops-specific plain config shape for session-scoped operation, handoff, and
  later ingestion when Agent Equipment Config is unavailable.
- Docs: this Equipment Design Bundle, user guidance, adapter boundaries, security
  rules, and validation evidence.

## Hard rules

- Direct tracker recording is the default when auth, tracker capability,
  stakeholder policy, and adapter safety allow it.
- Intermediate in-tree tracking state is fallback state, not the primary system
  of record.
- Mutation-capable modes default to dry-run or advisory behavior until policy and
  invocation explicitly allow writes.
- Hidden agent preferences must not become issue policy.
- Issue Ops must remain usable in session scope when Agent Equipment Config is
  unavailable.
- Issue Ops must know enough of its own config shape to serialize, hand off, and
  ingest plain Issue Ops config without Agent Equipment Config.
- Reflection Findings discovered during manual or ad hoc reflection must be
  routed to the narrowest relevant issue, with generic cognition-equipment
  findings linked to issue #25.
- Configured tracker priority and selection policy governs issue pick order;
  dependency relations determine feasibility unless the configured policy says
  they also change priority.
- Adapter capabilities must declare native, emulated, unsupported, or fallback
  behavior.
- Issue mutations must have an audit surface that names operation, target,
  policy mode, request shape, and result or failure.

## Deterministic checks

- `python3.14 -m unittest tests.test_issue_tracker_ops`
- `python3.14 tools/issue_tracker_ops.py <command> ...` dry-run smoke checks.
- `python3.14 tools/issue_tracker_ops.py audit-labels --repo nisavid/agent-armory --execute`
- `python3.14 tools/validate_armory_integrity.py`
- `python3.14 tools/validate_armory_integrity.py --final-closeout` before external
  projection or branch push.
- Codex Security diff scan or recorded narrower security action for executable
  code and tracker mutation behavior.

## Output contract

The bootstrap adapter emits JSON for every operation. Dry-run output records the
request that would be sent and the provisional policy. Execute output records
the request, result, resolved dependency IDs when applicable, and errors.

Full Equipment delivery will deepen the current Agent Equipment Config
adapter projection with the broader Issue Ops profile, onboarding,
tracker-neutral core contracts, richer repair/orchestration modes, fallback
reconciliation, and publication guidance.

## Failure modes

- Missing auth or permission: fail closed, report the failed GitHub call, and do
  not create fallback state unless the operator requests it.
- Missing tracker capability: fail closed and record unsupported or fallback
  disposition.
- API outage or secondary rate limit: fail closed, preserve operation intent in
  audit output, and require retry or tracked deferment.
- Duplicate-risk issue creation: default to dry-run; future duplicate detection
  belongs in the full tracker-neutral core.
- Uncertain policy: use read-only, advisory, or dry-run behavior.

## Evidence

- Documentation-supported: GitHub REST Issues, issue dependencies, sub-issues,
  and GitHub CLI `gh api` behavior checked on 2026-05-04.
- Source-supported: local adapter implementation and tests in this repository.
- Implementation inference: using `gh api --input -` keeps JSON payload handling
  deterministic and avoids shell interpolation.

## Open questions

- Which Issue Ops policy settings must exist in the first Issue Ops-specific
  plain config shape before Agent Equipment Config integration lands?
- Which child issues own GitHub Projects, duplicate detection, fallback
  reconciliation, and tracker-neutral adapters after the bootstrap MVP?
