# Agentic Engineering Operating Model Review

Status: Completed Review

Issue: [#47](https://github.com/nisavid/agent-armory/issues/47)

## Purpose

This review classifies the operating model under which Agents perform
engineering work in the Agent Armory. It inventories process surfaces,
authority boundaries, evidence rules, mutation gates, review loops, escalation
paths, closeout expectations, update mechanisms, and discovery routes so future
Agents can find, use, and revise those rules reliably.

## Vocabulary Boundary

Agentic Engineering is software engineering performed agentically: code is
written by AI Agents, and the surrounding work is managed with methodical
attention to how Agents navigate tasks, fail, recover, use context, and benefit
from equipment.

Agent Engineering is the engineering of Agents, agentic systems, agent roles,
and agent workflows.

Agent Meta-Engineering is Agent Engineering whose problem domain is engineering
work: creating or refining the Agents, agentic systems, roles, workflows,
operating models, and equipment that make Agentic Engineering more capable.

This story is Agent Meta-Engineering in service of Agentic Engineering. The
review does not redefine the Armory as the whole of Agentic Engineering, and it
does not treat Harness Capability Profile work as the owner of this operating
model.

## Foundational Premise

Agentic Engineering needs both imaginative commitment and rigorous checking.
The operating model should let Agents pursue ambitious automation goals while
forcing claims, changes, and publication decisions through evidence, validation,
review, and explicit control boundaries.

This review may preserve that premise where it clarifies operating-model
decisions. It is not yet a manifesto and does not create a separate manifesto
surface unless the review finds a concrete need for one.

## Dependency Context

Issue #47 is cross-cutting operating-model work. The Harness Capability
Profiles epic and the manual refresh manager may use this review as dependency
context, especially for authority, escalation, evidence durability, mutation,
audit, and closeout rules. Their dependency does not make this review part of
the Harness Capability Profiles epic or limit this review's scope to that
epic's needs.

## Crystallized Decisions

- Story Closeout is an Armory Operating Contract, not Forge Core. It governs all
  cohesive Armory change sets through validation, evidence, security,
  documentation, issue and PR projection, intent refresh, and review gates.
- Smith and Forgewright runbooks remain Forge Core because they govern Forge
  roles and Forge work, even when their outputs support broader Agentic
  Engineering goals.
- Root `AGENTS.md` is the repo-local agent policy entrypoint. Detailed
  cross-Armory operating-model rules belong in named Armory Operating Contract
  docs, with `AGENTS.md` routing Agents to them instead of duplicating them.
- Deterministic validators enforce selected machine-checkable slices of the
  operating model. They are not the canonical source of the policy they enforce;
  readable policy and process contracts state the rule first.
- Portable Agentic Engineering workflow equipment is downstream of the
  repo-local operating model. This review may identify equipment candidates and
  follow-ups, but current operating-model rules stay in Armory Operating
  Contracts until they are coherent and pressure-tested enough to package.
- The operating-model inventory is surface-first. Specific clauses are called
  out when they create contradictions, hidden dependencies, stale terminology,
  missing discovery paths, or certification risks.
- This review's Harness Capability Profile refresh certification scope is
  limited to operating-model adequacy. It does not judge detailed manual refresh
  behavior, CLI shape, schema updates, or profile workflow criteria owned by
  issue #48 and its Equipment Design Bundle.
- Issue #48 is no longer blocked at the operating-model layer. The native issue
  blockers and implementation acceptance criteria for #48 remain intact.

## Review Method

Inventory durable operating-model surfaces first, then drill into specific
clauses only where the surface-level classification is not enough. Each surface
is classified by ownership, durability, audience, enforcement, update
mechanism, and surface type. Clause-level findings are reserved for conflicts,
gaps, stale terms, overbroad guidance, hidden operator-memory dependencies,
missing discovery paths, and certification risks.

## Surface Inventory

| Surface | Type | Ownership | Durability | Audience | Enforcement and update mechanism |
| --- | --- | --- | --- | --- | --- |
| `AGENTS.md` | Agent policy entrypoint | Armory repository policy | Durable repo-local entrypoint | Agents before and during scouting | Updated by PR when pre-scout routing or authority changes; points to detailed contracts instead of duplicating them |
| `docs/story-closeout.md` | Armory Operating Contract | Armory operating model | Durable cross-Armory process contract | Agents closing stories or judging merge-readiness | Enforced in selected slices by Armory Integrity Validation and review gates; updated when closeout gates or interdependency rules change |
| `docs/vision.md` | Armory Canon | Project vision and experience direction | Durable north-star guidance | Humans, Smiths, Forgewrights, and review agents | Checked through Story Quality alignment and doc closeout; updated only when accepted vision changes need durable projection |
| `docs/agent-equipment-forge.md` and Forge Canon docs | Forge Canon | Forgewrights | Durable conceptual and decision framework for Forge work | Smiths and Forgewrights | Checked by integrity validation, Forge review, and doc closeout; updated when accepted Forge decisions change |
| `docs/smith-runbook.md` | Forge Core workflow | Forgewrights | Durable Smith process contract | Smiths creating Agent Equipment | Updated through Forge maintenance; references templates, specs, validation, and Story Closeout |
| `docs/forgewright-runbook.md` | Forge Core workflow | Forgewrights | Durable Forge-maintenance process contract | Forgewrights | Updated through Forge maintenance; projects decisions into narrow live surfaces and hands work back to Smiths |
| `CONTEXT.md` and `docs/ubiquitous-language.md` | Vocabulary surfaces | Armory and Forge language owners | Durable domain language | Agents and humans interpreting project terms | Updated when terminology decisions crystallize; integrity validation checks canonical vocabulary surfaces |
| `docs/agents/*.md` | Agent-facing domain docs | Domain owners such as Issue Tracker Ops | Durable operational guidance | Agents working in a specific operational domain | Updated when domain operations change; some domains have supporting tools |
| `tools/validate_armory_integrity.py` | Deterministic validation | Armory validation tooling | Executable enforcement surface | Agents, CI-like local checks, and reviewers | Enforces machine-checkable slices of readable contracts; updated when an invariant becomes or ceases to be machine-checkable |
| `tools/issue_tracker_ops.py` | Bootstrap adapter tooling | Issue Tracker Ops | Executable issue-tracker surface | Agents performing supported GitHub issue operations | Defaults to dry-run; updated when Issue Tracker Ops needs new supported operations |
| `docs/security/threat-model.md` | Repository Threat Model | Security closeout | Durable security model | Agents and reviewers assessing change-set security | Used by Change Set Security Closeout; updated when trust boundaries or security assumptions change |
| `specs/*` and `specs/*/` bundles | Equipment Blueprint or Equipment Candidate surfaces | Owning Equipment Candidate | Durable design and validation planning | Smiths, Forgewrights, and implementation agents | Updated through the owning issue or story; validation plans and deterministic tools enforce implemented slices |
| `docs/follow-ups/*.md` | Follow-Up Capture | Deferred issue-projection owner | Durable local capture until projected or retired | Forgewrights and agents scouting deferred work | Governed by `docs/agents/issue-tracker.md`; updated, projected, consolidated, or retired by follow-up issue work |
| GitHub Issues and PRs | Published PRD Issue, tracker, and projection surfaces | Issue Tracker Ops and story owners | Durable external tracking and publication surface | Operators, agents, reviewers, and downstream stories | Updated through Issue Tracker Ops or `gh`; projections must match current repo evidence |

## Operating-Model Certification For #48

Issue #48 can proceed once its native blockers and implementation criteria are
otherwise satisfied. The operating-model layer provides sufficient rules for
manual Harness Capability Profile refresh work:

- Authority and escalation are covered by root `AGENTS.md`, which keeps
  initiative authority with the human operator while directing Agents to drive
  assigned execution and escalate unknown stakeholder policy or unavailable
  controls.
- Evidence durability is covered by `docs/evidence-taxonomy.md`,
  `docs/story-closeout.md`, and the Vanilla Harness Capability Profiles
  closeout evidence plan. Raw scout output, fetched pages, transcripts, fixture
  logs, and temporary local observations remain scratch by default; durable
  project evidence is promoted explicitly through curated notes, selected study
  reports, audit summaries, profile claims, or reviewable summaries.
- Mutation gates are covered by `docs/security-and-control.md`, the repository
  threat model, and the Vanilla Harness Capability Profiles security/control
  classification. Manual refresh commands default to non-mutating staged
  behavior, and canonical profile writes require explicit apply behavior.
- Audit expectations are covered by the Vanilla Harness Capability Profiles
  manual refresh workflow and closeout evidence plan, which require audit
  output for sources, changed claims, unresolved uncertainty, security-control
  decisions, scratch disposition, validation results, and curated durable
  evidence.
- Closeout is covered by `docs/story-closeout.md`, including security closeout,
  documentation closeout, Cross-Boundary Coherence Ralph Review, Story Quality
  Ralph Review, final validation, evidence durability classification, and issue
  or PR projection from current repo evidence.

This certification does not replace #48's detailed design ownership. The manual
refresh command shape, profile schema updates, test plan, and workflow behavior
remain owned by #48 and the Vanilla Harness Capability Profiles Equipment
Design Bundle.

## Findings

### Resolved Classification Findings

- Story Closeout was classified as Forge Core even though it governs all
  cohesive Armory change sets. It is now classified as an Armory Operating
  Contract, and the validator enforces that status.
- `AGENTS.md` carried cross-Armory operating rules without naming the boundary
  between root policy entrypoint and detailed operating contracts. It now
  routes Agents to Armory Operating Contracts and keeps detailed rules in named
  project docs.
- Agentic Engineering, Agent Engineering, and Agent Meta-Engineering were not
  distinguished in durable vocabulary. The vocabulary now defines Agentic
  Engineering as software engineering performed agentically, Agent Engineering
  as engineering Agents and agentic systems, and Agent Meta-Engineering as
  Agent Engineering whose problem domain is engineering work.
- Deterministic validation could be mistaken for the source of policy because
  it enforces canonical statuses and integrity rules. The review now records
  that validators enforce selected machine-checkable slices of readable policy
  and process contracts.
- Portable Agentic Engineering workflow equipment could be mistaken for the
  current home of operating-model rules. The review now records it as
  downstream equipment that may later package coherent, pressure-tested rules.

### Remaining Gaps And Risks

- The repo has one named Armory Operating Contract. If more cross-Armory
  operating contracts appear, the project may need an index or stronger
  discovery route. For now, `AGENTS.md` and `docs/story-closeout.md` are enough.
- Some accepted operating-model rules are enforced only by review discipline.
  That is appropriate for judgment-heavy gates such as Intent Model Refresh and
  Story Quality Ralph Review, but future repeated failures should induce
  validators, templates, or Agent Equipment.
- The review certifies #48 only at the operating-model layer. #48 still needs
  its native blockers, implementation design, tests, security closeout, and
  documentation closeout before its own story can close.

## Recommendations

- Keep Story Closeout as the first Armory Operating Contract and keep its
  status enforced by Armory Integrity Validation.
- Keep root `AGENTS.md` as the repo-local agent policy entrypoint. Add detailed
  cross-Armory rules to named Armory Operating Contract docs when the rules
  outgrow entrypoint routing.
- Add deterministic validation only for rules that are stable and
  machine-checkable. Keep judgment-heavy obligations in readable contracts,
  review gates, and future Agent Equipment candidates.
- Treat portable Agentic Engineering workflow equipment as a downstream
  packaging and automation candidate, not as the source of current repo-local
  operating policy.
- Project this review's #48 certification into issue closeout or the relevant
  tracker surface so future Harness Capability Profile work can see that the
  operating-model checkpoint has passed without mistaking #47 for a Harness
  implementation story.

## Validation And Security Notes

The implemented changes are documentation and one validator status expectation.
The validator change does not add parsing, IO, network access, mutation,
authorization, or external side effects; it only updates the expected status for
`docs/story-closeout.md`.

Security closeout is therefore diff-scoped. No new secrets, permissions,
network operations, mutation paths, or external authority surfaces are
introduced. The security-relevant effect is positive: Story Closeout is now
classified as a cross-Armory operating contract, and the review preserves the
existing mutation-gate, evidence-durability, audit, and closeout controls for
future manual Harness Capability Profile refresh work.

GitHub repository metadata reports secret scanning and secret scanning push
protection as enabled. The GitHub secret scanning alerts API returned no open
or resolved alerts, and the local secret-pattern scan over changed files
returned no matches.

Validation performed during the review:

- `python3.14 tools/validate_armory_integrity.py --json`
- `python3.14 tools/harness_capability_profiles.py validate --json`
- `python3.14 -m unittest`
- `git diff --check`
- `rg -n --pcre2 "(AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9_]{36,}|sk-[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)" ...`
- `python3.14 tools/validate_armory_integrity.py --final-closeout`
