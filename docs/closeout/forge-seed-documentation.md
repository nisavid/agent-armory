# Forge Seed Documentation Closeout

Status: Completed Closeout

This closeout records the documentation sweep for the Forge Seed after
security closeout and before Issue Projection. It distinguishes live Forge
surfaces from archived provenance and leaves post-Seed follow-ups deferred.

## Scope of inspected docs

Inspected live agent-facing and human-facing surfaces:

- `README.md`
- `AGENTS.md`
- `CONTEXT.md`
- `docs/agents/*.md`
- Forge Canon under `docs/*.md`
- `docs/prd/forge-seed.md`
- `docs/adr/*.md`
- `docs/plans/2026-05-03-forge-seed.md`
- `docs/metasmith/source-projection.md`
- `docs/security/*.md`
- `docs/closeout/*.md`
- `specs/*.md`
- `templates/**/*.md`
- `examples/**/*.md`

Also inspected archived Source Handoff material under `docs/metasmith/handoff/` for stale-language search results. Those files remain provenance and were not edited as live documentation.

## Docs changed

- `docs/security/threat-model.md`: added the persistent Repository Threat Model with assets, trust boundaries, attacker-controlled inputs, invariants, assumptions, and high-impact failure modes.
- `docs/security/forge-seed-closeout.md`: added the Forge Seed security closeout with scan scope, artifact durability classification, artifact and report disposition, findings disposition, hardening notes, re-validation status, and deferred-risk tracking.
- `docs/story-closeout.md`: added the canonical Story Closeout process with gate order, interdependency rules, review gates, Intent Model Refresh, Intent Alignment Check, recursion boundaries, and completion criteria.
- `docs/closeout/forge-seed-projection-drafts.md`: added reviewable issue, PR, release, and handoff projection drafts for Story Closeout before external publication, using committed security closeout paths for portable external evidence.
- `docs/metasmith/handoff/2026-05-03-agentic-engineering-workflow-equipment.md`: linked the Seed Closeout Addendum and clarified that the addendum is current captured source material for the future Portable Agentic Engineering Workflow Equipment story, not a placeholder for later first capture.
- `docs/metasmith/handoff/2026-05-03-agentic-engineering-workflow-seed-closeout-addendum.md`: captured workflow lessons from Seed closeout about subagent review availability, closeout-gate ordering, recursive refresh, evidence freshness, process validation, and plan-state hygiene.
- `docs/security-and-control.md`: linked the Repository Threat Model from the canonical security/control surface.
- `AGENTS.md`: added zero-scout pointers from the Forge Conveyor to Tooling Request and Story Closeout, plus story-closeout requirements for Cross-Boundary Coherence and Story Quality Ralph Reviews.
- `CONTEXT.md`: added Tooling Request, Smith-to-Forgewright Handoff, Forgewright Hand-Back, Story Closeout, Cross-Boundary Coherence Ralph Review, Story Quality Ralph Review, Intent, Effective Intent, Underlying Intent, Intent Model Refresh, and Intent Alignment Check language.
- `docs/prd/forge-seed.md`: added Tooling Request success criteria, user story, acceptance criteria, story-closeout review criteria, and the Story Closeout process surface.
- `docs/smith-runbook.md`: added the Smith-facing Tooling Request trigger, dependency-recording rule, session-path selection, handoff contents, hand-back expectation, Story Closeout route, and story-closeout review gates.
- `docs/forgewright-runbook.md`: added Forgewright intake and hand-back responsibilities for Smith-discovered Tooling Gaps and linked Story Closeout from Forge change-set closeout.
- `templates/agents/README.md` and `templates/agents/profile.toml`: tightened remaining Agent Profile terminology after review.
- `docs/metasmith/source-projection.md`: updated completed Forge Seed projections from `planned` to `validated` where their target surfaces now exist and the Seed Validation Tool checks them or the closeout records their status.
- `docs/closeout/forge-seed-documentation.md`: added this documentation closeout summary.
- `docs/plans/2026-05-03-forge-seed.md`: tracked Task 9 work as it landed, repaired historical completed-step checkboxes, preserved the deferred post-Seed follow-up boundaries, and expanded the deferred Post-Seed Skill Migration capture with ingestion-pipeline design requirements.
- `tools/validate_forge_seed.py` and `tests/test_validate_forge_seed.py`: added validation for the Repository Threat Model, this documentation closeout summary, the security closeout summary, projection drafts, Source Projection Register status semantics, the Smith-to-Forgewright escalation path, the Story Closeout process, the story-closeout review gates, and strict final-closeout evidence before branch push or external projection.

## Docs unchanged with rationale

- `README.md`: already provides a concise Forge Tour and does not expose maintainer-only machinery.
- `docs/agents/*.md`: issue tracker, triage labels, and domain-doc guidance were not changed by the Forge Seed deliverables.
- Forge Canon not listed under "Docs changed" already describe the current seed surfaces, promotion boundaries, Forge Examples, downstream specs, and remaining uncertainties without saying that no Forge exists.
- `docs/adr/*.md`: ADRs are historical decision records; their future-tense decision language is appropriate to their decision context.
- `specs/*.md`: Task 8 review updated the specs to preserve source requirements and non-implementation boundaries.
- Remaining `templates/**/*.md` and template payloads: placeholder strings are intentional template fields, not stale project placeholders.
- `examples/**/*.md`: examples already state Forge Example status, promotion state `example`, trace links, and non-installable boundaries.
- Archived Source Handoff docs: preserved unchanged as provenance under their local handoff policy.

## Stale-language cleanup result

Searches for stale initial-state and placeholder language found no live docs claiming that the repository has no established Forge shape or that all decisions remain open.

Reviewed matches were resolved as:

- active status terms in the Equipment Promotion Path, Source Projection Register, and plan fixtures;
- intentional template placeholders under `templates/`;
- ADR decision context;
- PRD acceptance criteria describing the closeout requirement itself;
- archived handoff or side-thread source material that is explicitly not live Forge Canon.

The Source Projection Register now reflects established Forge Seed precedents by marking landed source requirements as `validated` and leaving only Issue Projection-dependent items planned.

## Established precedents added or updated

- The Forge Seed now has a persistent Repository Threat Model in `docs/security/threat-model.md`.
- The Forge Seed has canonical docs, refreshed harness catalog, templates, Forge Examples, downstream Smith specs, and Seed Validation.
- Root `AGENTS.md` is the zero-scout Forge Conveyor for Smiths.
- `README.md` is the Forge Tour, not an agent policy surface.
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
- Portable Agentic Engineering Workflow Equipment reflections are captured now in handoff and addendum surfaces. The capture window remains open through final validation, closeout reviews, issue projection, branch push, PR creation, PR review orchestration, merge, merge cleanup, external surface reconciliation, and final hand-back. A branch-push pause does not close the capture. Full Seed completion requires a merged Seed. An explicit hold or cancellation continues capture through an unmerged-state hand-back and should record the unmerged state directly. The post-Seed story is responsible for ingestion, challenge, and engineering, not for first capture.

## Review cycles and latest clean review

Task-level documentation review has been performed after each cohesive Forge Seed change set. The latest clean review for Task 8 was Ralph Review Cycle 42, covering docs/spec/source-projection/plan changes and validator/security behavior.

Ralph Review Cycle 43 reviewed the Task 9 documentation closeout and found issues in closeout status, closeout evidence validation, Source Projection Register status validation, the threat model's policy/design asset boundary, and Agent Profile terminology in the `templates/agents/` template. Those findings are addressed in the current change set.

Ralph Review Cycle 44 reviewed the Cycle 43 fixes and found issues in latest-clean-review field validation, stale `planned` source-projection rows, plan/checklist status, and closeout accounting for Agent Profile template edits. Those findings are addressed in the current change set.

Ralph Review Cycle 45 reviewed the Cycle 44 fixes and Smith-to-Forgewright escalation path. One reviewer found stale PRD initial-state language, an overbroad unchanged-docs rationale, and a plan expected-result contradiction; another reviewer found no issues. The findings are addressed in the current change set.

Ralph Review Cycles 47 through 50 reviewed security closeout, documentation closeout, and the Story Closeout process itself. They found issues in stale scan evidence, validation counts, closeout gate ordering, projection timing, rerun rules, closeout status consistency, and brittle process validation. Those findings are addressed in the current change set.

Ralph Review Cycle 51 reviewed the refreshed Step 6 closeout and found plan-state, documentation-closeout evidence, and projection-draft validation issues. Those findings are addressed in the current change set.

Ralph Review Cycle 52 reviewed the Cycle 51 fixes and found no remaining Step 6b closeout-process issues.

Ralph Review Cycle 58 reviewed the documentation closeout updates after Cycle 57 Story Quality findings. It found that the projection draft omitted the required portable report-disposition evidence. That finding is addressed in the current change set.

Ralph Review Cycle 59 reviewed the Cycle 58 fix and found no remaining documentation closeout or projection-draft contract issues.

Ralph Review Cycle 60 reviewed the Intent Alignment Check wording, prior closeout-review fixes, projection-draft target coverage, plan cross-references, and projection-draft evidence placeholders. It found no remaining documentation closeout issues.

Ralph Review Cycle 66 reviewed the refreshed intent model, Intent Alignment Check, `intent-capable` terminology, generalized artifact-durability policy, security closeout, and validator coverage. It found a stale security validation count. That finding is addressed in the current change set.

Ralph Review Cycle 67 reviewed the Cycle 66 fix and found stale path-shaped scan artifact contract wording in review history. That finding is addressed in the current change set.

Ralph Review Cycle 68 reviewed the current report-disposition language, generalized artifact-durability guardrail, intent terminology, gate ordering, security closeout evidence, validation evidence, and intentionally pending story-review placeholders. It found no remaining documentation closeout issues.

Latest clean documentation closeout review: Ralph Review Cycle 68.

## Residual documentation risk

- Issue Projection is still pending; external issue state may lag this repo draft until the projection step lands.
- The Source Handoff and side-thread handoff files intentionally retain source-era wording; future agents must continue treating those files as provenance, not live instruction.
- Further security or documentation edits before PR creation may require a narrow refresh of this closeout summary and its review evidence.
