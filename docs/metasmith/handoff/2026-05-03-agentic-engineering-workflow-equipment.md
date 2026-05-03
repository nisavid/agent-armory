# Agentic Engineering Workflow Equipment Handoff

Status: Handoff

This handoff captures side-conversation reflection on the engineering workflow
used during the Framework Seed. It is not canonical Framework doctrine. A future
post-Seed task should ingest this document, challenge it against the then-current
repo docs, and turn the useful parts into properly engineered Agent Equipment.

## Source Context

The Framework Seed work has treated Agent Armory as an agent-operated,
operator-directed repository. The operator owns project initiatives, session
continuation, arbitration, and stakeholder policy. Once work is underway, agents
are expected to drive discovery, planning, implementation, validation, review,
documentation closeout, security closeout, and handoff until they hit a genuine
stakeholder boundary or unavailable control surface.

The workflow has also treated handoff material as provenance, not live doctrine.
Accepted requirements are projected into repo-native docs, plans, validators, and
source registers. Preserved handoff docs remain auditable source context.

## Relationship To Existing Post-Seed Follow-Ups

This handoff should be processed after, or in coordination with, the Post-Seed
Skill Migration and Side-Thread Hand-Back Workflow tasks already listed in the
Framework Seed plan.

If those tasks have already landed, ingest their outputs as source material
before designing portable workflow equipment. Do not bypass or duplicate their
decisions without recording why. In particular:

- migrated repo-local skills may provide source examples, anti-examples,
  provenance constraints, and global-installation assumptions;
- the side-thread hand-back workflow may provide source language for
  side-conversation boundaries, provenance, and integration responsibility;
- any progressive-disclosure routing added by those tasks should become evidence
  for the minimal always-loaded instruction set.

The portable workflow task should distinguish three categories:

- Agent Armory internal operating practice,
- portable workflow equipment suitable for other repos,
- adapter-specific projections for a harness, issue tracker, review tool, or
  security tool.

## Extracted Workflow Principles

### Agent Ops Model

- The human operator initiates project initiatives and work sessions.
- Agents autonomously execute within established policy once work is underway.
- Agents escalate only when stakeholder policy is unknown, authority is missing,
  or an action has no available autonomous control surface.
- Agents should fix forward and preserve audit trails unless explicitly told to
  perform destructive history or state changes.

### Docs-As-Source Model

- Handoff docs are source provenance.
- PRDs, plans, canonical docs, validators, ADRs, issue projections, and closeout
  notes are repo-native working surfaces.
- Each accepted upstream requirement needs a disposition, target path, and
  validation status.
- Once a precedent is established, live docs should state the current rule rather
  than preserving "everything is still open" language.

### Development Method

- Start with requirements and vocabulary before broad implementation.
- Write failing tests or deterministic checks before changing behavior.
- Implement the narrowest durable source shape that satisfies the desired
  behavior.
- Run targeted tests, full tests, and broader validators.
- Treat documentation, security, source projection, and review outcomes as part
  of the implementation, not follow-up polish.

### Review Method

- Use labeled Ralph review cycles when work is broad, security-sensitive,
  architecture-affecting, or explicitly requested.
- Review by concern: validator/security, docs/templates, source projection,
  planning consistency, and any domain-specific risks.
- Fix every valid finding, verify the fix, and start another labeled cycle.
- Stop only when the latest review cycle is clean.

### Security Method

- Treat security as a change-set closeout gate.
- Use threat modeling, diff-focused discovery, validation, hardening, and final
  reporting where applicable.
- Run local secret-pattern scans for changed surfaces.
- Prefer fail-closed defaults, explicit approval gates, least privilege, scoped
  authority, and documented residual risk.

### Documentation Closeout Method

- At the end of every cohesive change set, inspect affected human-facing and
  agent-facing docs for gaps, stale claims, and misplaced guidance.
- Keep always-loaded agent docs short and law-like.
- Put deferred work in plans or backlog surfaces, not in PRD success criteria or
  canonical docs before the work is actively designed.
- Preserve useful facts before deleting or relocating them.

### Side-Conversation Method

- Side conversations should default to non-mutating inspection and advice.
- Narrow side-thread edits are acceptable only when explicitly requested.
- A side-thread hand-back should record provenance, operator intent, files
  touched, review and validation implications, and commit guidance.
- The main worker remains responsible for integration, validation, review, and
  commit or PR handling.

## Reflection On The Reflection

The first reflection identified the workflow, but it also exposed a second-order
requirement: this discipline should not depend on a future agent reading a long
chat transcript or guessing the operator's expectations from memory. The
workflow needs to become repo equipment with progressive disclosure.

The reflection also showed that the method should not be copied as a maximal
ritual. Its portable form needs a right-sizing rule: apply the same discipline,
but scale the ceremony to the risk, blast radius, reversibility, stakeholder
impact, and uncertainty of the work.

The reflection is therefore a seed artifact, not the design. A future task needs
to challenge it against actual repo language, resolve terminology, define
minimum viable equipment, and decide which parts belong in always-loaded docs,
triggered skills, templates, validators, checklists, or examples.

## Prompt-Reduction Goal

After the future task is complete, an operator should be able to start a new
agent with a minimal prompt such as:

> Continue the next agent-operated engineering task in this repo.

Given the repo's instructions and equipment, that should reliably project to the
same outcomes:

- discover current state and active plan,
- identify task scope and stakeholder boundaries,
- use requirements-first planning when needed,
- use TDD or deterministic validation for behavior and docs,
- update affected docs as part of the change,
- run applicable security closeout,
- review with the right strength,
- preserve source projection and audit trails,
- produce a clear handoff or closeout.

## Validation Ideas

The future task should prove the prompt-reduction goal with pressure scenarios,
not only by prose review.

Candidate pressure scenarios:

- a small docs-only correction that should use a lightweight path;
- a medium feature or template change that should use requirements, tests, docs
  closeout, and review;
- a security-sensitive hook, MCP/tool, script, or permission change that should
  trigger security closeout;
- a side conversation that should inspect or narrowly edit without taking over
  the main change set;
- an unavailable issue tracker, review tool, network, or permission surface that
  should produce a clear escalation or repo-file fallback;
- a repo that lacks user-global skills and must still recover the workflow from
  repo-local equipment.

Expected validation evidence:

- an agent can find the workflow route from always-loaded docs with minimal
  scouting;
- the selected ceremony scales with risk and reversibility;
- affected human-facing and agent-facing docs are checked at closeout;
- security closeout is run or explicitly scoped down with a reason;
- review strength matches the change shape;
- handoff, source projection, or issue/PR projection is durable enough for a
  later agent to resume.

## Candidate Equipment

### Always-Loaded Agent Policy

A short `AGENTS.md` block should encode only the durable law:

- agent-operated autonomy boundary,
- stakeholder escalation boundary,
- route to workflow equipment,
- review/security/doc closeout gates,
- source-projection expectation when working from handoffs.

### Triggered Workflow Skills

The repo may need portable, repo-local skills for recognizable work shapes:

- agent-operated change set execution,
- handoff ingestion and source projection,
- requirements-to-plan workflow,
- TDD plus deterministic doc validation,
- change-set closeout,
- Ralph review orchestration,
- security closeout routing,
- side-thread hand-back.

These skills should be written so they can be copied into another repo without
requiring Agent Armory terminology except where the receiving repo opts into it.

### Templates

Portable templates could include:

- handoff ingestion report,
- source projection register,
- PRD,
- implementation plan,
- review cycle log,
- security closeout report,
- documentation closeout checklist,
- side-thread hand-back note,
- ADR,
- issue projection note.

### Validators And Scripts

Portable validators should check repo-local invariants without assuming a
specific language stack:

- required docs and sections,
- source-projection completeness,
- stale-path and stale-term scans,
- secret-pattern scans,
- review/security/doc closeout evidence,
- generated issue or PR body shape,
- task-specific acceptance checks.

### Examples

Examples should demonstrate right-sized use:

- a small docs-only change,
- a medium feature or template change,
- a security-sensitive hook or tool change,
- a side-thread hand-back,
- a full PR closeout.

## Portability Requirements

The equipment should be robust across repos with different languages, domains,
and workflows.

- Do not assume Python, GitHub, Codex, a specific CI system, or a specific issue
  tracker unless the receiving repo selects that adapter.
- Separate universal workflow concepts from harness-specific projections.
- Keep domain vocabulary in the receiving repo's `CONTEXT.md` or equivalent.
- Make optional adapters explicit: GitHub Issues, PRs, local validators, MCPs,
  security scanners, documentation linters, or package managers.
- Provide graceful fallback paths when a control surface is unavailable.
- Prefer deterministic checks for durable invariants and human review for
  judgment-heavy decisions.

## Adaptability Requirements

The equipment should apply to software engineering, operations, documentation,
packaging, security, research, and maintenance work.

- Classify work by risk and reversibility before selecting ceremony.
- Make the smallest reliable workflow the default for low-risk work.
- Require stronger planning, TDD, security, and review for broader or
  authority-bearing work.
- Let repos add domain-specific stages without changing the universal core.

## Human Usability Requirements

Humans should be able to adopt the workflow without becoming agent-framework
experts.

- Provide a short orientation document.
- Provide copyable minimal prompts.
- Provide a checklist-style quick path.
- Keep rationale behind progressive disclosure.
- Make the handoff and closeout artifacts readable without model-specific
  jargon.

## Agent Usability Requirements

Agents should be able to recover the workflow from repo files alone.

- Put only pre-scouting law in always-loaded docs.
- Put task-shaped procedures behind triggered skills or routed docs.
- Keep handoff ingestion and current-state discovery deterministic.
- Make every workflow stage produce or update a durable artifact.
- Include failure modes and escalation return contracts.

## Open Design Questions For The Future Grill Loop

1. What is the canonical name for this capability: Agentic Engineering Workflow,
   Agent Ops Workflow, Change-Set Operating System, or another term?
2. Is the portable unit a plugin, a skill bundle, a template pack, a validator
   suite, a repo bootstrap, or a layered combination?
3. Which parts are universal enough to ship as publishable equipment, and which
   parts should remain Agent Armory internal workflow?
4. How much ceremony should each risk tier require?
5. What is the minimal always-loaded instruction set that still reliably routes
   agents into the workflow?
6. How should this integrate with user-global skills without depending on them?
7. What should be validated mechanically, and what should remain review
   judgment?
8. What adapters are needed for GitHub Issues, PRs, local-only repos, CI,
   security tools, and non-Git workflows?

## Proposed Post-Seed Task

Begin by ingesting this handoff and the then-current Framework Seed docs. Run a
`grill-with-docs` loop before drafting requirements. The loop should challenge
terminology, scope, portability, ceremony, and placement against `CONTEXT.md`,
Framework docs, existing templates, and Agent Ops policy.

After the grill loop, produce a PRD, specification or implementation plan,
tests/validators, templates, docs, examples, security review, and Ralph-reviewed
closeout appropriate to the final scope.
