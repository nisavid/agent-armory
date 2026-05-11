# Forge Seed Documentation Closeout

Status: Completed Closeout

This closeout records the documentation sweep for the Forge Seed after
security closeout and before Issue Projection. It distinguishes live Forge
surfaces from archived provenance. It originally left post-Seed follow-ups
deferred; the post-projection update below records their later issue projection
and local-capture retirement.

## Scope of inspected docs

Inspected live agent-facing and human-facing surfaces:

- `README.md`
- `docs/README.md`
- `AGENTS.md`
- `CONTEXT.md`
- `docs/agents/*.md`
- Forge Canon under `docs/*.md`
- `docs/prd/forge-seed.md`
- `docs/adr/*.md`
- `docs/plans/2026-05-03-forge-seed.md`
- `docs/closeout/forge-seed-source-disposition.md`
- `docs/security/*.md`
- `docs/closeout/*.md`
- `specs/*.md`
- `templates/**/*.md`
- `examples/**/*.md`

Also inspected the raw Source Handoff before source retirement. The final tree preserves provenance through the Source Disposition Ledger rather than raw handoff prompts.

## Docs changed

- `README.md`: replaced the minimal landing page with an under-construction
  public orientation, current Forge Seed value, agent role model, reader paths,
  differentiators, and grounded roadmap links.
- `README.md` and `docs/assets/agent-armory-hero.webp`: added the public hero
  image while preserving the under-construction notice as the first substantive
  README content.
- `docs/forge-tour.md`: expanded the human-facing Forge introduction with the
  Armory/the Forge distinction, Wielder/Outfitter/Smith/Forgewright role
  model, agent-operated repo model, equipment lifecycle, future outfitting
  path, and reflection-driven Forge improvement loop.
- `docs/README.md`: added the human-facing documentation map organized by
  reader intent and Diataxis type.
- `CONTEXT.md`, `docs/ubiquitous-language.md`, `docs/prd/forge-seed.md`,
  `docs/security/threat-model.md`, and `templates/skill/SKILL.md`: aligned
  current prose with the definite-article form for the Armory while preserving
  role terminology.
- `docs/security/forge-seed-closeout.md`: recorded a narrow security
  applicability refresh for the human-facing documentation spine change.
- `docs/closeout/forge-seed-projection-drafts.md`: updated issue and PR draft
  text so external projection reflects the refreshed public docs spine.
- `tools/validate_forge_seed.py` and `tests/test_validate_forge_seed.py`:
  aligned the human README route check with the full `Agent Equipment Forge`
  section heading.
- `docs/security/threat-model.md`: added the persistent Repository Threat Model with assets, trust boundaries, attacker-controlled inputs, invariants, assumptions, and high-impact failure modes.
- `docs/security/forge-seed-closeout.md`: added the Forge Seed security closeout with scan scope, artifact durability classification, artifact and report disposition, findings disposition, hardening notes, re-validation status, and deferred-risk tracking.
- `docs/story-closeout.md`: added the canonical Story Closeout process with gate order, interdependency rules, review gates, Intent Model Refresh, Intent Alignment Check, recursion boundaries, and completion criteria.
- `docs/closeout/forge-seed-projection-drafts.md`: added reviewable issue, PR, release, and handoff projection drafts for Story Closeout before external publication, using committed security closeout paths for portable external evidence.
- `docs/follow-ups/portable-agentic-engineering-workflow-equipment.md`:
  captured the future Portable Agentic Engineering Workflow Equipment story in
  a neutral follow-up path before issue projection.
- `docs/closeout/forge-seed-workflow-lessons.md`: captured workflow lessons from Seed closeout about subagent review availability, closeout-gate ordering, recursive refresh, evidence freshness, process validation, and plan-state hygiene.
- `docs/closeout/forge-seed-engineering-workflow-generalization.md`: captured
  generalizable workflow patterns, antipatterns, and portable equipment design
  inputs for the post-Seed engineering workflow story.
- `docs/security-and-control.md`: linked the Repository Threat Model from the canonical security/control surface.
- `AGENTS.md`: added zero-scout pointers from the Forge Conveyor to Tooling Request and Story Closeout, plus story-closeout requirements for Cross-Boundary Coherence and Story Quality Ralph Reviews.
- `CONTEXT.md`: added Tooling Request, Smith-to-Forgewright Handoff, Forgewright Hand-Back, Story Closeout, Cross-Boundary Coherence Ralph Review, Story Quality Ralph Review, Intent, Effective Intent, Underlying Intent, Intent Model Refresh, and Intent Alignment Check language.
- `docs/prd/forge-seed.md`: added Tooling Request success criteria, user story, acceptance criteria, story-closeout review criteria, and the Story Closeout process surface.
- `docs/smith-runbook.md`: added the Smith-facing Tooling Request trigger, dependency-recording rule, session-path selection, handoff contents, hand-back expectation, Story Closeout route, and story-closeout review gates.
- `docs/forgewright-runbook.md`: added Forgewright intake and hand-back responsibilities for Smith-discovered Tooling Gaps and linked Story Closeout from Forge change-set closeout.
- `templates/agents/README.md` and `templates/agents/profile.toml`: tightened remaining Agent Profile terminology after review.
- `docs/closeout/forge-seed-source-disposition.md`: records the Source Disposition Ledger, source-bearing checkpoint, and final source-retirement stamp.
- `docs/closeout/forge-seed-source-disposition.md`: restamped the final
  source-retirement tree digest after adding the README hero asset.
- `docs/closeout/forge-seed-documentation.md`: added this documentation closeout summary.
- `docs/plans/2026-05-03-forge-seed.md`: tracked Task 9 work as it landed, repaired historical completed-step checkboxes, preserved the deferred post-Seed follow-up boundaries, and expanded the deferred Post-Seed Skill Migration capture with ingestion-pipeline design requirements.
- `tools/validate_forge_seed.py` and `tests/test_validate_forge_seed.py`: added validation for the Repository Threat Model, this documentation closeout summary, the security closeout summary, projection drafts, Source Disposition Ledger semantics, the Smith-to-Forgewright escalation path, the Story Closeout process, the story-closeout review gates, and strict final-closeout evidence before branch push or external projection.

## Docs unchanged with rationale

- `docs/agents/*.md`: issue tracker, triage labels, and domain-doc guidance were not changed by the Forge Seed deliverables.
- `docs/security-and-control.md`: inspected for the refreshed public
  security/control route; the docs-only change did not alter controls or
  security policy.
- Forge Canon not listed under "Docs changed" already describe the current seed surfaces, promotion boundaries, Forge Examples, downstream specs, and remaining uncertainties without saying that no Forge exists.
- `docs/adr/*.md`: ADRs are historical decision records; their future-tense decision language is appropriate to their decision context.
- `specs/*.md`: Task 8 review updated the specs to preserve source requirements and non-implementation boundaries.
- Remaining `templates/**/*.md` and template payloads: placeholder strings are intentional template fields, not stale project placeholders.
- `examples/**/*.md`: examples already state Forge Example status, promotion state `example`, trace links, and non-installable boundaries.
- Source Handoff docs: retired from the final tree after disposition was captured in `docs/closeout/forge-seed-source-disposition.md`.

## Post-projection update

The projected follow-up captures now live in GitHub Issues. The retired local
capture disposition is recorded in
`docs/closeout/forge-seed-follow-up-projection.md`, and the Source Disposition
Ledger points to that durable closeout evidence.

## Stale-language cleanup result

Searches for stale initial-state and placeholder language found no live docs claiming that the repository has no established Forge shape or that all decisions remain open.

Reviewed matches were resolved as:

- intentional under-construction language in the README and docs map, which now
  describes the current Forge Seed state without implying a populated
  inventory;
- active status terms in the Equipment Promotion Path, Source Disposition Ledger, and plan fixtures;
- intentional template placeholders under `templates/`;
- ADR decision context;
- PRD acceptance criteria describing the closeout requirement itself;
- archived handoff or side-thread source material that is explicitly not live Forge Canon.

The Source Disposition Ledger reflects established Forge Seed precedents, source coverage, operator arbitration, source-bearing checkpoint evidence, and final source-retirement requirements.

The refreshed public docs describe Wielders, Outfitters, Smiths, and
Forgewrights as agent roles. Human readers are described as people acting through
their agents without carrying internal operator-naming rules into the
human-facing orientation.

Current prose refers to the Armory as `the Armory` or `the Agent Armory`.
Source-disposition rows that retain source-era wording remain provenance, not
live reader guidance.

## Established precedents added or updated

- The Forge Seed now has a persistent Repository Threat Model in `docs/security/threat-model.md`.
- The Forge Seed has canonical docs, refreshed harness catalog, templates, Forge Examples, Equipment Blueprints, and Seed Validation.
- Root `AGENTS.md` is the zero-scout Forge Conveyor for Smiths.
- `README.md` is the public landing page. It now states that the Armory is
  under construction, the Forge has just come online, first equipment is being
  prepared, and the inventory is not yet populated.
- After operator feedback, `README.md` was reframed around prospective users
  who value strong agent-operator experience before introducing deeper Forge
  method.
- `docs/README.md` is the human-facing documentation map, while `docs/forge-tour.md`
  remains the human-facing Forge orientation.
- Wielders, Outfitters, Smiths, and Forgewrights are agent roles. Human-facing
  docs may assume a human reader without explaining internal operator naming.
- Current reader-facing prose uses the definite article for the Armory: `the
  Armory` or `the Agent Armory`.
- Durable committed docs use neutral project paths unless intrinsically tied to a specific skill, plugin, tool, or workflow.
- Agent Profiles are described in prose while source paths use the harness/plugin term `agents`.
- Smiths have a zero-inquiry Tooling Request path for recording a discovered Tooling Gap, preempting unsafe equipment work, selecting a harness-appropriate Forgewright session path, and resuming from a Forgewright hand-back.
- Agent Ops, Periodic Actions, and Harness Capability Refresh are specified downstream equipment, not implemented Seed equipment.
- Forge Examples and specs must not imply installability, loadability, production readiness, or publication.
- Security and documentation closeout are required change-set gates before merge-readiness.
- Story Closeout is the story-level gate. Change Set Security Closeout and Change Set Documentation Closeout are subordinate gates.
- Story closeout requires separate Cross-Boundary Coherence and Story Quality Ralph Reviews before a story is treated as complete.
- Cross-Boundary Coherence Ralph Review precedes Story Quality Ralph Review because quality review depends on coherent process evidence.
- Intent Model Refresh is the first Story Closeout gate. Story Quality Ralph Review later includes an Intent Alignment Check that compares declaration-imposed Effective Intent with the refreshed model of Underlying Intent after Cross-Boundary Coherence has made Effective Intent legible, permits unilateral declaration realignment only when observable evidence shows misalignment beyond reasonable doubt, and escalates non-dismissible uncertainty to the operator.
- Projection drafts are prepared before story-level review; external issue or PR publication happens after final validation and policy gates.
- Strict final-closeout validation rejects unresolved story-review placeholders and host-local or scratch artifact paths in external projection drafts before branch push or external projection.
- Closeout evidence artifacts are classified by durability before commit or external projection. Instance-scoped scratch evidence, including Codex Security scan bundles, is not tracked as project truth; durable conclusions belong in committed closeout summaries or portable review surfaces.
- Post-Seed Skill Migration must begin with a dedicated generic ingestion-pipeline engineering story before importing the operator's equipment. That story should start with `grill-with-docs`, inspect candidate and existing equipment holistically, treat source materials as evidence about intended capability rather than authority over the user's current Underlying Intent or final form, support configurable ingestion policy choices, and handle upstream-maintained materials with explicit provenance, licensing, update-channel, and adaptation strategies.
- Portable Agentic Engineering Workflow Equipment reflections are captured now in handoff and addendum surfaces, including the linked Engineering Workflow Generalization Addendum. The capture window remains open through final validation, closeout reviews, issue projection, branch push, PR creation, PR review orchestration, merge, merge cleanup, external surface reconciliation, and final hand-back. A branch-push pause does not close the capture. Full Seed completion requires a merged Seed. An explicit hold or cancellation continues capture through an unmerged-state hand-back and should record the unmerged state directly. The post-Seed story is responsible for ingestion, challenge, and engineering, not for first capture.

## Review status

- Documentation closeout: Ralph Review Cycle 87.
- Cross-Boundary Coherence: Ralph Review Cycle 80.
- Story Quality: Ralph Review Cycle 87.

## Residual documentation risk

- Follow-up issue projection is complete for the Seed-era follow-up captures.
  The Published PRD Issue draft remains in
  `docs/closeout/forge-seed-projection-drafts.md` unless a later story
  publishes or retires it.
- Source-disposition and workflow-lesson records intentionally retain normalized references to source-era wording; future agents must continue treating those references as provenance, not live instruction.
- Further security or documentation edits during PR review may require a narrow refresh of this closeout summary and its review evidence.
