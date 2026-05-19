# Issue Tracker Ops PRD

Status: Repo Draft PRD

Published PRD Issue: #107

## Problem Statement

Agent Armory needs Issue Tracker Ops to be usable as full Agent Equipment, not
only as a GitHub Issues bootstrap script. Agents and operators need a durable,
configurable, context-sensitive way to record, review, repair, enrich,
organize, select, work, and orchestrate issue-tracked follow-ups directly in an
issue tracker.

The current bootstrap adapter proves useful GitHub issue mutations and label
audits, but full delivery needs a stable product contract that covers
tracker-neutral behavior, GitHub Issues runtime support, local fallback
records, onboarding, policy migration, compatibility with existing issue
skills, CLI/MCP parity, mutation safety, duplicate detection, issue selection,
and judgment-heavy workflows.

## Solution

Deliver Issue Tracker Ops as an Agent Equipment product with:

- a tracker-neutral core contract;
- a complete GitHub Issues baseline adapter;
- a local-markdown fallback and compatibility path;
- migration-compatible advisory stubs for GitLab and freeform "other" trackers;
- Issue Ops Config backed by Agent Equipment Config;
- a smooth onboarding and migration flow that auto-discovers repo-local and
  user-global Issue Ops policy surfaces;
- pre-built migration recipes for Matt Pocock's AI Skills for Real Engineers;
- sufficient expressiveness to capture Agent Armory's current Issue Ops policy;
- deterministic CLI and MCP parity for operations, plans, gates, audits, and
  adapter calls;
- agent-facing skills or profiles for judgment-heavy workflows that prepare
  deterministic operation plans rather than bypassing them.

GitHub Projects custom fields are a follow-up adapter extension, not an MVP
blocker. Non-GitHub live mutation adapters are follow-up work unless promoted
by later product decision.

## User Stories

1. As an Operator, I want Issue Ops to inspect the current repository and issue
   tracker before acting, so that agents do not invent hidden policy.
2. As an Operator, I want onboarding to explain each decision progressively, so
   that I understand what policy is being codified.
3. As an Operator, I want onboarding to auto-discover repo-local and
   user-global Issue Ops surfaces, so that existing skills, docs, configs,
   hooks, scripts, and integrations are not missed.
4. As an Operator, I want each discovered Foreign Policy Surface listed with an
   explicit migration fate, so that I can keep, ingest, discard, ignore, defer,
   or split policy deliberately.
5. As an Operator, I want `keep & establish compat` to hide implementation
   mechanism details until classification, so that compatibility can use
   indirection, generation, adapter behavior, or a mixed strategy as
   appropriate.
6. As an Operator, I want migration to start with a dry-run plan, so that no
   policy or integration changes happen silently.
7. As an Operator, I want approved migration apply to show exact diffs,
   authority, audit records, and rollback guidance, so that policy migration is
   safe and reviewable.
8. As an Operator, I want user-global skill edits or removals to require
   explicit approval, so that onboarding cannot unexpectedly rewrite my global
   tools.
9. As a Smith, I want Issue Ops to include a pre-built, pre-validated migration
   recipe for Matt Pocock's skills, so that repos using those skills have a
   reliable upgrade path.
10. As a Smith, I want the Matt Pocock recipe to preserve setup, triage, PRD
    publication, issue slicing, agent briefs, out-of-scope memory, GitHub,
    GitLab, local markdown, and freeform tracker policy expressiveness, so that
    migration does not flatten useful behavior.
11. As a Smith, I want Issue Ops to represent Agent Armory's current label axes,
    dependency disposition, triage records, brief status, engagement modes, and
    Reflection Finding routing, so that Agent Armory can dogfood the equipment.
12. As an Agent, I want a tracker-neutral operation model, so that adapter
    behavior is not hard-coded to one tracker.
13. As an Agent, I want each adapter capability to declare native, emulated,
    unsupported, or fallback behavior, so that I can choose safe operations.
14. As an Agent, I want a full GitHub Issues runtime adapter, so that MVP use
    works against the repo's current active tracker.
15. As an Agent, I want local markdown to be available as a fallback and
    compatibility adapter, so that tracker outages, missing auth, and existing
    local workflows can be reconciled.
16. As an Agent, I want GitLab and other tracker policies to be ingestible even
    before live mutation adapters exist, so that migration can preserve intent.
17. As an Agent, I want deterministic CLI and MCP operations to share the same
    typed contracts, so that tool and command use stay equivalent.
18. As an Agent, I want Config-backed policy with scoped applicability
    predicates, so that repo, project, issue-set, role, phase, operation, and
    stakeholder differences are represented declaratively.
19. As an Agent, I want policy precedence, conflicts, defaults, and unresolved
    judgment explained, so that I can avoid converting uncertainty into hidden
    preference.
20. As an Agent, I want predefinable factors such as dependency relations to
    ship with robust defaults, so that routine issue graph behavior is
    reliable.
21. As an Operator, I want judgment-sensitive factors such as assignee choice
    and priority weighing to ask for guidance until policy is codified, so that
    stakeholder intent remains explicit.
22. As an Agent, I want issue review and repair workflows to produce plans
    before mutation, so that issue quality can improve without unsafe writes.
23. As an Agent, I want PRD publication and issue slicing workflows to preserve
    project vocabulary and durable requirements, so that generated tracker work
    remains actionable over time.
24. As an Agent, I want agent briefs to be durable behavioral contracts, so
    that AFK work can start without relying on stale file paths or line numbers.
25. As an Agent, I want duplicate detection before creating or closing issues,
    so that the tracker does not accumulate avoidable duplicates.
26. As an Agent, I want duplicate detection to consider open and closed issues,
    semantic title/body similarity, dependencies, sub-issues, PRD linkage,
    Reflection Finding routing, and out-of-scope records, so that related work
    is handled with appropriate context.
27. As an Agent, I want issue selection to explain priority, readiness,
    dependency disposition, brief status, work kind, engagement mode,
    stakeholder overrides, and tracker-native state, so that next-work choices
    are inspectable.
28. As an Agent, I want fallback records to include owner, retry condition,
    intended tracker target, and reconciliation requirements, so that temporary
    fallback state does not become a parallel tracker.
29. As an Agent, I want every write-capable operation to support dry-run,
    approval gates, audit output, idempotency or duplicate detection, and
    compensation guidance, so that tracker mutations are controlled.
30. As a Wielder, I want docs and validation to state what is implemented,
    advisory, fallback, or follow-up, so that I know which Issue Ops capability
    can be trusted in the current promotion state.

## Implementation Decisions

- Product boundary: Issue Ops MVP is a complete GitHub Issues baseline, not a
  partial bootstrap. It includes tracker-neutral contracts, GitHub Issues
  runtime operations, local fallback/compatibility, Config-backed onboarding and
  migration, CLI/MCP parity, safety controls, duplicate detection, issue
  selection, and judgment-heavy workflow support.
- Deferred adapter boundary: GitHub Projects custom fields, full GitLab live
  mutation, and non-GitHub tracker live mutation are follow-up adapter work.
  Their policy shapes must remain ingestible and explainable in MVP.
- Core/adapters: the tracker-neutral core defines operation types, capability
  matrix entries, side-effect classifications, plan shapes, audit records, and
  validation. Adapters map those contracts to tracker-specific behavior.
- GitHub adapter: the MVP adapter covers issue create/read/update/close,
  comments, labels, assignees, dependencies, and sub-issues where available.
  Projects support is represented as unavailable or fallback capability
  evidence until the follow-up adapter lands.
- Local markdown adapter: the MVP includes local markdown as a fallback and
  compatibility path with reconciliation back to the active tracker.
- Config model: Issue Ops contributes a schema fragment to Agent Equipment
  Config and supports scoped policies with applicability predicates for repo,
  tracker, project, issue set, stakeholder, role, work phase, operation, work
  kind, side-effect class, adapter capability, and session intent.
- Onboarding: missing or incomplete policy starts a smooth onboarding flow
  similar to Agent Equipment Config. Onboarding discovers, classifies, explains,
  interviews, saves partial config safely, resumes, restarts, and re-onboards.
- Migration: onboarding auto-discovers repo-local and user-global Issue Ops
  surfaces. Operators choose fates including keep and establish compatibility,
  remove and ingest policy, remove and discard policy, ignore, defer for
  review, and split. Apply is dry-run-first and explicitly approved.
- Compatibility: compatibility is an operator-facing fate, not a mechanism.
  The implementation classifies whether indirection, generation, adapter
  behavior, or mixed compatibility can faithfully preserve a Foreign Policy
  Surface.
- Matt Pocock migration: MVP ships a pre-built, pre-validated migration recipe
  for `mattpocock/skills`, including setup policy, tracker templates, triage,
  PRD publication, issue slicing, agent briefs, and out-of-scope rejection
  memory.
- Agent Armory expressiveness: MVP Config must represent the current Agent
  Armory Issue Ops baseline, including label axes, depth, work kind, engagement
  mode, brief status, dependency disposition, triage records, Reflection
  Findings, fallback capture, and audit-label behavior.
- Judgment split: deterministic core owns contracts, planning, validation,
  dry-run/write gates, audit, and tracker mutation. Skills or Agent Profiles
  own context reading, recommendations, interviews, drafting, and other
  judgment-heavy workflows.
- Workflow modes: triage, PRD publication, issue slicing, agent brief creation,
  issue review, issue repair, enrichment, duplicate detection, issue selection,
  session pickup, and orchestration are named workflow modes with typed
  inputs/outputs and policy-backed templates.
- CLI/MCP parity: every deterministic operation has a fluent CLI command and
  MCP tool with the same typed contract. Judgment-heavy modes expose prepare or
  plan surfaces whose writes still go through deterministic operation plans and
  gates.
- Safety: write-capable behavior requires dry-run output, explicit authority,
  policy evidence, audit records, duplicate/idempotency checks, fallback or
  compensation guidance, rate-limit handling, and partial-failure handling.

## Testing Decisions

- Test externally visible behavior and machine-readable contracts rather than
  internal helper structure.
- Cover tracker-neutral operation planning with deterministic fixtures for each
  operation class and capability disposition.
- Cover GitHub adapter request construction, dry-run behavior, execute
  behavior, response summaries, auth/permission failures, pagination,
  retryable failures, rate limits, duplicate detection, and
  dependency/sub-issue behavior.
- Cover local markdown fallback creation, reconciliation, retirement, and
  projection verification.
- Cover Config resolution, policy precedence, applicability predicates,
  conflicts, missing policy, partial onboarding state, migration plans, approved
  migration apply, refused user-global mutation, and compatibility decisions.
- Cover the Matt Pocock migration recipe against fixture copies of setup,
  triage, PRD, issue slicing, agent brief, out-of-scope, GitHub, GitLab, local
  markdown, and other-tracker policy shapes.
- Cover Agent Armory policy expressiveness with fixtures for the current label
  axes, triage records, dependency disposition, Reflection Finding routing, and
  audit-label expectations.
- Cover CLI/MCP parity by comparing operation metadata, input schemas, output
  shapes, side-effect classifications, and representative tool-call results.
- Cover judgment-heavy workflow boundaries by verifying that prepare/plan
  outputs do not mutate trackers and that final writes flow through
  deterministic operation plans.

## Out of Scope

- GitHub Projects custom-field runtime support for MVP.
- Full GitLab live mutation support for MVP.
- Live mutation adapters for Jira, Linear, or other non-GitHub trackers.
- Replacing human/operator judgment for assignee choice, priority weighing, or
  stakeholder-sensitive routing before policy is explicitly codified.
- Treating migrated foreign policy surfaces as authoritative parallel policy
  sources after compatibility or ingestion is established.
- Implementing unrelated Agent Armory product doctrine work; that is tracked
  separately by #106.

## Further Notes

- This PRD is the stable requirements surface produced by #105 for #11 and #13.
- #103 remains the tracked Issue Ops policy-doc migration work and should align
  with the generic policy migration rule in #104.
- Existing child issues #14 through #18 remain useful implementation buckets,
  but their exact scope should be checked against this PRD before closeout.
