# Forge Seed PRD

Status: Repo Draft PRD

## 1. Executive Summary

**Problem Statement**: The Agent Armory accepted a substantial Source Handoff for an Agent Equipment Forge. The Forge Seed must turn that source material into canonical, validated Forge surfaces that future Smiths can use without replaying the handoff. Without those surfaces and closeout gates, future equipment work can drift into unreviewed examples, stale harness claims, oversized skills, or unclear source-of-truth boundaries.

**Proposed Solution**: Create the Forge Seed: canonical docs, evidence discipline, harness capability catalog, decision method, templates, demonstrative examples, Equipment Blueprints, and Seed Validation. Preserve the Source Handoff as provenance, refresh canonical harness facts, and publish a reviewed PRD summary into GitHub Issues after the repo draft stabilizes.

**Success Criteria**:

- **Forge routing coverage**: Root `AGENTS.md` exposes the Forge Conveyor for Smiths, and `README.md` links readers to the Forge Tour; Seed Validation confirms all linked target paths exist.
- **Source disposition coverage**: 100% of accepted Source Handoff requirements are recorded in `docs/closeout/forge-seed-source-disposition.md`; the ledger records the source manifest, item-level coverage, challenge status, arbitration requirements, operator decisions, evidence targets, source-bearing checkpoint, and final source-retired stamp.
- **Validation pass rate**: `python3.14 -m unittest` and `python3.14 tools/validate_forge_seed.py` both exit 0 from the repository root.
- **Harness evidence completeness**: 100% of canonical Harness Capability Catalog claims include evidence category, source URL, checked-at date, checked version or version basis, and uncertainty note when evidence is incomplete or inconsistent.
- **Promotion-state coverage**: 100% of Forge Examples and Equipment Blueprints declare an Equipment Promotion Path state; every Forge Example traces from capability card to interface decision record to projected components.
- **Security closeout coverage**: The Forge Seed has a repository threat model, a Codex Security scan of the Seed change set, a durable security closeout summary, and recorded disposition for every reportable finding before the change set is treated as merge-ready.
- **Documentation closeout coverage**: Every agent-facing and human-facing doc plausibly affected by the Forge Seed is inspected and either updated or explicitly left unchanged with rationale; doc changes complete review-until-clean with audience-appropriate doc-writing guidance.
- **Story closeout review coverage**: Before closeout, the Forge Seed completes separate Cross-Boundary Coherence and Story Quality Ralph Reviews so scoped process outputs agree at system level and the story satisfies holistic quality criteria.
- **Tooling Request coverage**: The Smith and Forgewright runbooks define how a Smith records a newly discovered unsatisfied Tooling Gap as a dependency, preempts the current equipment task, selects a harness-appropriate Forgewright session path, and resumes from a Forgewright hand-back.

## 2. User Experience & Functionality

**User Personas**:

- **Forgewright**: An Agent that creates or refines the Agent Equipment Forge.
- **Smith**: An Agent that creates Agent Equipment using the Forge.
- **Human operator**: The stakeholder who chooses project initiatives, starts or continues work sessions, and arbitrates stakeholder decisions.
- **Maintainer**: A future human or Agent responsible for keeping canonical docs, harness facts, issue tracking, and validation healthy.

**User Stories**:

- As a Smith, I want the preloaded root agent doc to route me through the Forge Conveyor so that I can start without scouting.
- As a human reader, I want the README to explain the Forge and where to start so that I can understand the repo without reading agent-only policy.
- As a Smith, I want a decision guide for choosing skills, MCP/tools, hooks, Agent Profiles, plugins, scripts, docs, and config so that equipment uses the lowest reliable cognitive layer.
- As a Smith, I want templates and demonstrative examples so that I can create Equipment Candidates without confusing examples for Published Agent Equipment.
- As a Forgewright, I want preserved Source Handoff provenance and canonical projections so that I can audit origin decisions without treating old handoff prompts as current instructions.
- As a Forgewright, I want a refreshed Harness Capability Catalog so that Forge guidance does not start from stale harness facts.
- As a maintainer, I want Seed Validation so that required docs, links, provenance/disposition decisions, promotion states, and catalog fields are checked by a repeatable tool.
- As a human operator, I want GitHub Issues to remain the tracking surface after PRD review so that durable project work is visible in the issue tracker without creating draft churn.
- As a Smith, I want a built-in path for unsatisfied Tooling Gaps so that I can stop unsafe equipment work, hand the Tooling Gap to a Forgewright, and resume with a clear hand-back.

**Acceptance Criteria**:

- Root `AGENTS.md` gives Smiths the Forge Conveyor for understanding the Forge, creating equipment, checking harness facts, using templates, and finding Equipment Blueprints.
- `README.md` links human readers to the Forge Tour and canonical starting path without exposing agent-only machinery.
- `CONTEXT.md` defines the Forge Seed language used by canonical docs and specs.
- `docs/closeout/forge-seed-source-disposition.md` preserves the Source Handoff inventory and the disposition of accepted source requirements without keeping raw source prompts in the final tree.
- Seed Validation supports a source-bearing checkpoint mode before raw source retirement and a source-retired final mode after the disposition ledger is stamped.
- Forge Canon include, at minimum, a Forge overview, Smith runbook, Forgewright runbook, interface decision guide, harness component guide, evidence taxonomy, harness capability catalog, equipment promotion guidance, and security/control guidance.
- The Smith runbook defines Tooling Request, including trigger conditions, dependency recording, session path selection, handoff contents, and hand-back expectations for current-session, subagent-session, peer-agent-session, forked-session, and new-session Forgewright work.
- The Forgewright runbook defines Tooling Gap intake, including handoff preservation, requirement refinement, canonical-surface updates, validation/review expectations, dependency updates, deferment handling, and Smith resume guidance.
- `docs/story-closeout.md` defines Story Closeout gate order, subordinate change-set closeout gates, review sequencing, interdependency rerun rules, recursion boundaries, and completion criteria.
- Seed templates cover capability cards, interface decision records, skill templates, hooks, Agent Profiles, plugins, scripts, MCP/tool definitions, config, security reviews, and context-budget reviews.
- Forge Examples demonstrate PR review, documentation research, and observability investigation as annotated examples with promotion state `example`; each example traces from capability card to interface decision record to projected components.
- Equipment Blueprints exist for Agent Ops, Periodic Actions, and Harness Capability Refresh with promotion state `specified`; each Blueprint projects the substantive requirements captured in the Source Disposition Ledger, including required harness projections, management behavior, storage expectations, tracked fields, and change-response rules where applicable.
- Seed Validation provides human-readable output by default and machine-readable output with `--json`.
- `docs/security/threat-model.md` records an initial Repository Threat Model for the Agent Armory before the Forge Seed is considered merge-ready.
- `docs/security/forge-seed-closeout.md` records the Seed security closeout scope, commands, scan artifact disposition, report disposition, findings, fixes, suppressions, deferments, and re-validation status.
- `docs/closeout/forge-seed-documentation.md` records affected docs inspected, docs changed, docs left unchanged with rationale, stale-language cleanup results, doc review cycles, and residual documentation risk.
- The Forge Seed closeout follows the Codex Security phase sequence against the Seed change set. Threat modeling and finding discovery always run; validation and attack-path analysis run when discovery promotes technically plausible candidates or another security workflow rule requires them. When validation or attack-path analysis is not applicable, the security closeout records the reason. Reportable findings are fixed, suppressed with evidence, or explicitly deferred with stakeholder approval and a tracking issue.
- Forge Seed closeout includes a Change Set Documentation Closeout. At minimum, inspect `README.md`, `AGENTS.md`, `CONTEXT.md`, Forge Canon, specs, templates, examples, issue-tracker docs, security docs, closeout docs, ADRs, PRDs, and plan docs for stale initial-state language, inaccurate claims, missing established precedents, misplaced maintainer policy, and appropriate deliverable mentions.
- Documentation closeout removes or revises early language that says nothing is established or everything is up in the air when the Forge Seed has established a precedent, while preserving explicit uncertainty for unresolved ambiguities.
- Forge Seed closeout follows `docs/story-closeout.md`: security and documentation closeout finish before projection drafts; projection drafts are checked during Cross-Boundary Coherence review; Cross-Boundary Coherence review finishes before Story Quality review; final validation, including strict final-closeout validation, confirms the evidence; issue, PR, release, and handoff publication follows clean final story evidence.
- Forge Seed closeout includes a Cross-Boundary Coherence Ralph Review that verifies PRD, specs, plan, implementation, validation, security, docs, issue or PR projection, and release or handoff surfaces agree on current behavior and evidence.
- Forge Seed closeout includes a Story Quality Ralph Review that verifies DX, UX, code quality, clean architecture, robustness against unspecified interactions, user personas, and attack paths, mitigations for pathological dev/ops cycles, and alignment with a coherent strategic vision.
- Issue Projection happens only after the Repo Draft PRD has completed review-until-clean; closeout creates or updates the Published PRD Issue or records why projection remains pending.

**Non-Goals**:

- Do not implement Agent Ops, Periodic Actions, or Harness Capability Refresh as working Agent Equipment in the Forge Seed.
- Do not ship first-class repo-local skills in the Forge Seed.
- Do not create production-looking stubs that imply examples are installable or validated.
- Do not use third-party package managers or non-standard-library dependencies for Seed Validation.
- Do not treat the preserved Source Handoff as the live Forge surface.
- Do not rely on unrefreshed harness facts for the canonical Harness Capability Catalog.

## 3. AI System Requirements

**Tool Requirements**:

- Local repository tools: `git`, `rg`, `python3.14`, and the Python 3.14 standard library.
- Web research tools: Firecrawl or equivalent web source retrieval for harness fact refresh.
- Documentation lookup tools: Context7 for library, framework, SDK, API, CLI, or cloud-service documentation questions that arise during implementation.
- Issue-tracker tools: GitHub MCP or `gh` CLI for Issue Projection after PRD review.
- Review tools: review-until-clean cycles using reviewer Agents for PRDs, plans, docs, and cohesive implementation sets.
- Security tools: Codex Security workflows for repository threat modeling, Seed change-set scan phases, attack-path analysis, final security reporting, and hardening follow-up.

**Evaluation Strategy**:

- Use Seed Validation to check repository shape, canonical links, source disposition, source-retirement stamp, promotion-state labels, and harness catalog required fields.
- Use review-until-clean cycles for PRD, plan, canonical docs, and implementation sets.
- Use live source refresh for canonical harness facts before publishing `docs/harness-capabilities.md` and `docs/harness-capabilities.toml`.
- Use preloaded-path review to confirm that root `AGENTS.md` routes Smiths to the correct Forge surfaces without scouting.
- Use README-path review to confirm that the human-facing README explains the Forge and links to the canonical starting path.
- Use TDD for the Seed Validation Tool: write failing `unittest` tests before implementation, verify red, implement, verify green, and refactor while green.
- Use Codex Security at Seed closeout to create or update the repository threat model, scan the Seed change set, validate plausible findings, analyze attack paths when candidates require it, and drive hardening fixes before merge-readiness.
- Use Change Set Documentation Closeout at Seed closeout to inspect affected agent-facing and human-facing docs, apply the appropriate doc-honing standards, and Ralph-review doc changes with guidance from `honing-agent-facing-docs`, `honing-human-facing-docs`, `writing-skills`, `documentation-writer`, and `writing-clearly-and-concisely` as applicable.
- Use `docs/story-closeout.md` to order closeout gates and rerun affected upstream gates when security, documentation, validation, PRD/spec/plan scope, or issue/PR projection changes during review.
- Use a Cross-Boundary Coherence Ralph Review near story closeout to verify scoped process outputs cohere across their boundaries.
- Use a Story Quality Ralph Review near story closeout to verify holistic DX, UX, code quality, architecture, robustness, strategic alignment, and lessons from prior pathological development or operations cycles.

## 4. Technical Specifications

**Architecture Overview**:

The Forge Seed is a documentation- and validation-first system. It preserves the Source Handoff as provenance, projects accepted decisions into canonical docs and templates, refreshes volatile harness facts into a canonical catalog, and validates the resulting structure with a standard-library Python tool.

The seed separates durable surfaces by role:

- `README.md`: human-facing orientation that links to the Forge Tour.
- `AGENTS.md`: always-loaded agent law and concise repo operating policy.
- `CONTEXT.md`: project vocabulary and resolved ambiguities.
- `docs/adr/`: short decision records for architecture and policy choices.
- `docs/plans/`: neutral project implementation plans, regardless of which workflow skill executes them.
- `docs/prd/forge-seed.md`: Repo Draft PRD.
- `docs/security/threat-model.md`: persistent Repository Threat Model for security closeout and future scans.
- `docs/security/forge-seed-closeout.md`: durable review summary for the Forge Seed security closeout.
- `docs/closeout/forge-seed-documentation.md`: durable review summary for Forge Seed documentation closeout.
- `docs/closeout/forge-seed-projection-drafts.md`: reviewable issue, PR, release, and handoff projection drafts for Story Closeout before external publication.
- `docs/story-closeout.md`: canonical Story Closeout process for gate order, review sequencing, rerun rules, and completion criteria.
- `docs/closeout/forge-seed-source-disposition.md`: Source Disposition Ledger and source-retirement stamp.
- `docs/*.md`: Forge Canon.
- `docs/harness-capabilities.md` and `docs/harness-capabilities.toml`: refreshed Harness Capability Catalog.
- `templates/`: copyable templates for Smith-created Equipment Candidates.
- `examples/`: annotated Forge Examples.
- `specs/`: Equipment Blueprints.
- `tools/validate_forge_seed.py`: Seed Validation Tool.
- `tests/test_validate_forge_seed.py`: standard-library tests.

The target seed structure is:

```text
README.md
AGENTS.md
CONTEXT.md
docs/
  adr/
  closeout/
    forge-seed-documentation.md
    forge-seed-projection-drafts.md
    forge-seed-source-disposition.md
    forge-seed-workflow-lessons.md
  follow-ups/
    portable-agentic-engineering-workflow-equipment.md
    side-thread-hand-back-workflow.md
    ephemeral-workflow-opportunity-capture.md
  plans/
    2026-05-03-forge-seed.md
  prd/
    forge-seed.md
  security/
    threat-model.md
    forge-seed-closeout.md
  ubiquitous-language.md
  agent-equipment-forge.md
  smith-runbook.md
  forgewright-runbook.md
  interface-decision-guide.md
  harness-components.md
  harness-capabilities.md
  harness-capabilities.toml
  evidence-taxonomy.md
  security-and-control.md
  equipment-promotion.md
  story-closeout.md
templates/
  capability-card.md
  interface-decision-record.md
  skill/
    README.md
    SKILL.md
  hook/
    README.md
    hook.ts
  agents/
    README.md
    profile.toml
  plugin/
    README.md
    manifest.toml
  script/
    README.md
    validate-example.py
  mcp/
    README.md
    tool-spec.md
  config/
    README.md
    example.toml
  security-review.md
  context-budget-review.md
examples/
  pr-review/
  docs-research/
  observability-investigation/
specs/
  agent-ops.md
  periodic-actions.md
  harness-capability-refresh.md
tools/
  validate_forge_seed.py
tests/
  test_validate_forge_seed.py
```

**Integration Points**:

- **GitHub Issues**: Published PRD Issue and future issue tracking after repo-draft review.
- **Firecrawl or web retrieval**: source-backed harness fact refresh.
- **Context7**: current documentation for any library, API, SDK, CLI, or cloud-service implementation questions.
- **Python 3.14**: Seed Validation runtime and `unittest` test runner.
- **Git**: branch, commit, review, and closeout flow in the persistent worktree.
- **Codex Security**: repository threat model, change-set scan, validation, attack-path analysis, and final report/hardening workflow. Transient scan bundles are instance-scoped scratch evidence; merge-readiness evidence must be summarized in the change-set closeout with artifact and report disposition.

**Security & Privacy**:

- The Forge Seed must not include secrets, personal credentials, private cache paths, or host-specific credential references.
- Harness-specific claims must separate source-backed facts, local CLI observations, third-party fallback metadata, and uncertainty notes.
- Hard policy should be documented as a future hook, permission, sandbox, or approval concern rather than hidden inside examples.
- Example MCP/tool definitions must classify read/write behavior, side effects, auth source, approval requirements, and failure modes.
- The preserved Source Handoff is provenance and must not override current root `AGENTS.md`, `CONTEXT.md`, ADRs, canonical docs, specs, templates, examples, or validation scripts.
- The Forge Seed must complete a Change Set Security Closeout before merge-readiness. Reportable findings block closeout until fixed or explicitly deferred with stakeholder approval, risk rationale, and tracking. Hardening changes require the applicable Codex Security phases and final report to be rerun or updated before closeout.

## 5. Risks & Roadmap

**Phased Rollout**:

- **MVP: Forge Seed**: Preserve Source Handoff, write canonical docs, refresh harness catalog, create templates/examples/specs, implement Seed Validation, complete review-until-clean cycles, complete Change Set Security Closeout, complete Change Set Documentation Closeout, and perform Issue Projection or record projection pending.
- **v1.1: Downstream equipment planning**: Convert Agent Ops, Periodic Actions, and Harness Capability Refresh specs into implementation plans with TDD and SDD task decomposition.
- **v2.0: Published Agent Equipment**: Promote validated equipment through the Equipment Promotion Path and publish installable or equippable surfaces only after equipment-specific validation.

**Technical Risks**:

- **Harness drift**: Harness facts can change quickly. Mitigation: refresh canonical catalog from first-party sources and label evidence, checked-at dates, version basis, and uncertainty.
- **Source-of-truth drift**: Repo Draft PRDs and Published PRD Issues can diverge. Mitigation: require Issue Projection or explicit pending notes after material PRD changes.
- **Example confusion**: Demonstrative examples can be mistaken for production equipment. Mitigation: require promotion-state labels and explicit non-production status.
- **Validation overreach**: Seed Validation can drift into downstream equipment validation. Mitigation: limit it to seed integrity and promotion labels; require equipment-specific validators later.
- **Python availability**: Python 3.14 may not be the default interpreter everywhere. Mitigation: make Python 3.14 a declared constraint and verify availability before implementation closeout.
- **Skill discipline bypass**: Repo-local skills could appear without pressure-scenario validation. Mitigation: ship Skill Templates only in the seed and require Pressure Scenario Validation for future skills.
- **Security analysis drift**: Security requirements can become a generic checklist instead of a repo-specific gate. Mitigation: maintain a Repository Threat Model and require applicable Codex Security analysis at each change-set closeout.
- **Documentation drift**: Early repo docs can keep saying the shape is unsettled after the Seed establishes real precedents. Mitigation: require Change Set Documentation Closeout and doc-review guidance for every affected audience.
