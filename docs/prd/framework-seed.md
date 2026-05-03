# Framework Seed PRD

Status: Repo Draft PRD

## 1. Executive Summary

**Problem Statement**: Agent Armory has accepted a substantial Source Handoff for an Agent Equipment Framework, but the repository does not yet expose a canonical, validated Framework surface that future Smiths can use without replaying the handoff. Without a seed Framework, future equipment work can drift into unreviewed examples, stale harness claims, oversized skills, or unclear source-of-truth boundaries.

**Proposed Solution**: Create the Framework Seed: canonical docs, evidence discipline, harness capability catalog, decision method, templates, demonstrative examples, downstream Smith specs, and Seed Validation. Preserve the Source Handoff as provenance, refresh canonical harness facts, and publish a reviewed PRD summary into GitHub Issues after the repo draft stabilizes.

**Success Criteria**:

- **Framework routing coverage**: Root `AGENTS.md` exposes the Smith Framework path, and `README.md` exposes the Human Framework Entry; Seed Validation confirms all linked target paths exist.
- **Source projection coverage**: 100% of accepted Source Handoff requirements are recorded in `docs/metasmith/source-projection.md` with disposition `projected` or `deferred`; every accepted source file is listed in the handoff manifest; every projected target path exists; and every deferred requirement has both a reason and a downstream target path.
- **Validation pass rate**: `python3.14 -m unittest` and `python3.14 tools/validate_framework_seed.py` both exit 0 from the repository root.
- **Harness evidence completeness**: 100% of canonical Harness Capability Catalog claims include evidence category, source URL, checked-at date, checked version or version basis, and uncertainty note when evidence is incomplete or inconsistent.
- **Promotion-state coverage**: 100% of Framework Examples and downstream Smith specs declare an Equipment Promotion Path state; every Framework Example traces from capability card to interface decision record to projected components.
- **Security closeout coverage**: The Framework Seed has a repository threat model, a Codex Security scan of the Seed change set, a durable security closeout summary, and recorded disposition for every reportable finding before the change set is treated as merge-ready.
- **Documentation closeout coverage**: Every agent-facing and human-facing doc plausibly affected by the Framework Seed is inspected and either updated or explicitly left unchanged with rationale; doc changes complete review-until-clean with audience-appropriate doc-writing guidance.

## 2. User Experience & Functionality

**User Personas**:

- **Metasmith**: An Agent that creates or refines the Agent Equipment Framework.
- **Smith**: An Agent that creates Agent Equipment using the Framework.
- **Human operator**: The stakeholder who chooses project initiatives, starts or continues work sessions, and arbitrates stakeholder decisions.
- **Maintainer**: A future human or Agent responsible for keeping canonical docs, harness facts, issue tracking, and validation healthy.

**User Stories**:

- As a Smith, I want the preloaded root agent doc to route me to the canonical Framework path so that I can start without scouting.
- As a human reader, I want the README to explain the Framework and where to start so that I can understand the repo without reading agent-only policy.
- As a Smith, I want a decision guide for choosing skills, MCP/tools, hooks, Agent Profiles, plugins, scripts, docs, and config so that equipment uses the lowest reliable cognitive layer.
- As a Smith, I want templates and demonstrative examples so that I can create Equipment Candidates without confusing examples for Published Agent Equipment.
- As a Metasmith, I want preserved Source Handoff provenance and canonical projections so that I can audit origin decisions without treating old handoff prompts as current instructions.
- As a Metasmith, I want a refreshed Harness Capability Catalog so that framework guidance does not start from stale harness facts.
- As a maintainer, I want Seed Validation so that required docs, links, provenance, projection decisions, promotion states, and catalog fields are checked by a repeatable tool.
- As a human operator, I want GitHub Issues to remain the tracking surface after PRD review so that durable project work is visible in the issue tracker without creating draft churn.

**Acceptance Criteria**:

- Root `AGENTS.md` gives Smiths the canonical Framework path for understanding the Framework, creating equipment, checking harness facts, using templates, and finding downstream Smith specs.
- `README.md` gives humans a concise Framework entry point and links to the canonical starting path without exposing agent-only machinery.
- `CONTEXT.md` defines the Framework Seed language used by canonical docs and specs.
- `docs/metasmith/handoff/2026-05-02/` preserves the manifest-listed Source Handoff and contains a local provenance wrapper that prevents archived prompts from becoming current instructions.
- `docs/metasmith/source-projection.md` records accepted Source Handoff requirements with `requirement_id`, `source_file`, `source_anchor`, `summary`, `disposition`, `target_path`, `deferment_reason`, and `validation_status`; Seed Validation checks accepted requirement ids, handoff manifest coverage, source references, projected target paths, and deferred downstream target path syntax.
- Canonical Framework docs include, at minimum, a Framework overview, Smith runbook, Metasmith runbook, interface decision guide, harness component guide, evidence taxonomy, harness capability catalog, equipment promotion guidance, and security/control guidance.
- Seed templates cover capability cards, interface decision records, skill templates, hooks, Agent Profiles, plugins, scripts, MCP/tool definitions, config, security reviews, and context-budget reviews.
- Framework Examples demonstrate PR review, documentation research, and observability investigation as annotated examples with promotion state `example`; each example traces from capability card to interface decision record to projected components.
- Downstream specs exist for Agent Ops, Periodic Actions, and Harness Capability Refresh with promotion state `specified`; each spec projects the substantive requirements from `docs/metasmith/handoff/2026-05-02/08-initial-smith-task-specs.md`, including required harness projections, management behavior, storage expectations, tracked fields, and change-response rules where applicable.
- Seed Validation provides human-readable output by default and machine-readable output with `--json`.
- `docs/security/threat-model.md` records an initial Repository Threat Model for Agent Armory before the Framework Seed is considered merge-ready.
- `docs/security/framework-seed-closeout.md` records the Seed security closeout scope, commands, scan artifact directory, final report path, findings, fixes, suppressions, deferments, and re-validation status.
- `docs/closeout/framework-seed-documentation.md` records affected docs inspected, docs changed, docs left unchanged with rationale, stale-language cleanup results, doc review cycles, and residual documentation risk.
- The Framework Seed closeout runs Codex Security's threat modeling, finding discovery, validation, attack-path analysis, and final reporting phases against the Seed change set; reportable findings are fixed, suppressed with evidence, or explicitly deferred with stakeholder approval and a tracking issue.
- Framework Seed closeout includes a Change Set Documentation Closeout. At minimum, inspect `README.md`, `AGENTS.md`, `CONTEXT.md`, canonical Framework docs, specs, templates, examples, issue-tracker docs, security docs, closeout docs, ADRs, PRDs, and plan docs for stale initial-state language, inaccurate claims, missing established precedents, misplaced maintainer policy, and appropriate deliverable mentions.
- Documentation closeout removes or revises early language that says nothing is established or everything is up in the air when the Framework Seed has established a precedent, while preserving explicit uncertainty for unresolved ambiguities.
- Issue Projection happens only after the Repo Draft PRD has completed review-until-clean; closeout creates or updates the Published PRD Issue or records why projection remains pending.

**Non-Goals**:

- Do not implement Agent Ops, Periodic Actions, or Harness Capability Refresh as working Agent Equipment in the Framework Seed.
- Do not ship first-class repo-local skills in the Framework Seed.
- Do not create production-looking stubs that imply examples are installable or validated.
- Do not use third-party package managers or non-standard-library dependencies for Seed Validation.
- Do not treat the preserved Source Handoff as the live Framework surface.
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

- Use Seed Validation to check repository shape, canonical links, Source Handoff provenance, the Source Projection Register, promotion-state labels, and harness catalog required fields.
- Use review-until-clean cycles for PRD, plan, canonical docs, and implementation sets.
- Use live source refresh for canonical harness facts before publishing `docs/harness-capabilities.md` and `docs/harness-capabilities.toml`.
- Use preloaded-path review to confirm that root `AGENTS.md` routes Smiths to the correct Framework surfaces without scouting.
- Use README-path review to confirm that the human-facing README explains the Framework and links to the canonical starting path.
- Use TDD for the Seed Validation Tool: write failing `unittest` tests before implementation, verify red, implement, verify green, and refactor while green.
- Use Codex Security at Seed closeout to create or update the repository threat model, scan the Seed change set, validate plausible findings, analyze attack paths, and drive hardening fixes before merge-readiness.
- Use Change Set Documentation Closeout at Seed closeout to inspect affected agent-facing and human-facing docs, apply the appropriate doc-honing standards, and Ralph-review doc changes with guidance from `honing-agent-facing-docs`, `honing-human-facing-docs`, `writing-skills`, `documentation-writer`, and `writing-clearly-and-concisely` as applicable.

## 4. Technical Specifications

**Architecture Overview**:

The Framework Seed is a documentation- and validation-first system. It preserves the Source Handoff as provenance, projects accepted decisions into canonical docs and templates, refreshes volatile harness facts into a canonical catalog, and validates the resulting structure with a standard-library Python tool.

The seed separates durable surfaces by role:

- `README.md`: human-facing orientation with a Human Framework Entry.
- `AGENTS.md`: always-loaded agent law and concise repo operating policy.
- `CONTEXT.md`: project vocabulary and resolved ambiguities.
- `docs/adr/`: short decision records for architecture and policy choices.
- `docs/plans/`: neutral project implementation plans, regardless of which workflow skill executes them.
- `docs/prd/framework-seed.md`: Repo Draft PRD.
- `docs/security/threat-model.md`: persistent Repository Threat Model for security closeout and future scans.
- `docs/security/framework-seed-closeout.md`: durable review summary for the Framework Seed security closeout.
- `docs/closeout/framework-seed-documentation.md`: durable review summary for Framework Seed documentation closeout.
- `docs/metasmith/source-projection.md`: Source Projection Register.
- `docs/metasmith/handoff/2026-05-02/`: preserved Source Handoff provenance.
- `docs/*.md`: canonical Framework docs.
- `docs/harness-capabilities.md` and `docs/harness-capabilities.toml`: refreshed Harness Capability Catalog.
- `templates/`: copyable templates for Smith-created Equipment Candidates.
- `examples/`: annotated Framework Examples.
- `specs/`: downstream Smith specs.
- `tools/validate_framework_seed.py`: Seed Validation Tool.
- `tests/test_validate_framework_seed.py`: standard-library tests.

The target seed structure is:

```text
README.md
AGENTS.md
CONTEXT.md
docs/
  adr/
  closeout/
    framework-seed-documentation.md
  plans/
    2026-05-03-framework-seed.md
  prd/
    framework-seed.md
  security/
    threat-model.md
    framework-seed-closeout.md
  metasmith/
    source-projection.md
    handoff/2026-05-02/
  ubiquitous-language.md
  equipment-framework.md
  smith-runbook.md
  metasmith-runbook.md
  interface-decision-guide.md
  harness-components.md
  harness-capabilities.md
  harness-capabilities.toml
  evidence-taxonomy.md
  security-and-control.md
  equipment-promotion.md
templates/
  capability-card.md
  interface-decision-record.md
  skill/
    README.md
    SKILL.md
  hook/
    README.md
    hook.ts
  agent-profile/
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
  validate_framework_seed.py
tests/
  test_validate_framework_seed.py
```

**Integration Points**:

- **GitHub Issues**: Published PRD Issue and future issue tracking after repo-draft review.
- **Firecrawl or web retrieval**: source-backed harness fact refresh.
- **Context7**: current documentation for any library, API, SDK, CLI, or cloud-service implementation questions.
- **Python 3.14**: Seed Validation runtime and `unittest` test runner.
- **Git**: branch, commit, review, and closeout flow in the persistent worktree.
- **Codex Security**: repository threat model, change-set scan, validation, attack-path analysis, and final report/hardening workflow. Transient scan bundles may live under the tool's scan artifact directory, but merge-readiness evidence must be summarized in the change-set closeout.

**Security & Privacy**:

- The Framework Seed must not include secrets, personal credentials, private cache paths, or host-specific credential references.
- Harness-specific claims must separate source-backed facts, local CLI observations, third-party fallback metadata, and uncertainty notes.
- Hard policy should be documented as a future hook, permission, sandbox, or approval concern rather than hidden inside examples.
- Example MCP/tool definitions must classify read/write behavior, side effects, auth source, approval requirements, and failure modes.
- The preserved Source Handoff is provenance and must not override current root `AGENTS.md`, `CONTEXT.md`, ADRs, canonical docs, specs, templates, examples, or validation scripts.
- The Framework Seed must complete a Change Set Security Closeout before merge-readiness. Reportable findings block closeout until fixed or explicitly deferred with stakeholder approval, risk rationale, and tracking. Hardening changes require the applicable Codex Security phases and final report to be rerun or updated before closeout.

## 5. Risks & Roadmap

**Phased Rollout**:

- **MVP: Framework Seed**: Preserve Source Handoff, write canonical docs, refresh harness catalog, create templates/examples/specs, implement Seed Validation, complete review-until-clean cycles, complete Change Set Security Closeout, complete Change Set Documentation Closeout, and perform Issue Projection or record projection pending.
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
