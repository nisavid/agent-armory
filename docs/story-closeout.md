# Story Closeout

Status: Forge Seed

## Purpose

Story Closeout is the story-level gate; Change Set Security Closeout and Change Set Documentation Closeout are subordinate gates.

Use this process when deciding whether a story is complete, merge-ready, or ready to hand back. It keeps process-specific checks from passing in isolation while their combined evidence still conflicts.

## Gate order

Run closeout gates in this order:

1. Refresh the Intent Model before downstream closeout gates.
2. Confirm the implementation, specs, plans, and deterministic validation reflect the same scope.
3. Complete Change Set Security Closeout for the current change set.
4. Complete Change Set Documentation Closeout for affected human-facing and agent-facing docs.
5. Prepare projection drafts for issues, PR bodies, handoff notes, and release summaries from the current story evidence, or record the explicit pending-projection rationale.
6. Run Cross-Boundary Coherence before Story Quality because quality review depends on coherent process evidence.
7. Run Story Quality Ralph Review after coherence findings are fixed or soundly rejected.
8. Run final validation and publication-readiness checks required by the active plan or repository policy. For the Forge Seed, `python3.14 tools/validate_forge_seed.py --final-closeout` is the branch-push and external-projection readiness check.
9. Push or otherwise publish the branch only when the active plan, operator direction, or issue-projection surface needs a pushed commit before PR creation. A stated human pause point may occur here.
10. Publish or update issue, PR, release, and handoff surfaces from the clean final story evidence.
11. Perform publication actions that remain in scope, respecting repository policy and stated human pause points.

Do not use issue projection, a PR body, or a final chat summary to make stale committed docs look current. Update the repo surface first when the evidence belongs in the repo.

Before committing or externally projecting closeout evidence, classify evidence artifacts by durability. Durable project evidence and portable review summaries may be committed or projected. Instance-scoped scratch artifacts, including raw tool reports, local scan bundles, copied diffs, host-local paths, screenshots, or work directories, should be summarized by scope, disposition, and durable conclusions instead of treated as project truth.

## Interdependency rules

Rerun the gate that owns any surface changed by a review fix.

- Security changes rerun or update Change Set Security Closeout when the change touches trust boundaries, executable code, hooks, MCP/tool definitions, permissions, secrets handling, network/file/process side effects, package metadata, or security policy.
- Documentation changes rerun or update Change Set Documentation Closeout when they change agent-facing policy, human-facing orientation, Forge Canon, examples, templates, specs, closeout claims, or issue/PR projection text that is derived from repo docs.
- Validation changes rerun deterministic tests and Seed Validation. Treat validator logic as security-relevant when it gates merge-readiness evidence or suppresses risks.
- PRD, Blueprint, or plan changes rerun source-disposition/provenance checks, acceptance-criteria checks, and Cross-Boundary Coherence review for the affected scope.
- Issue or PR projection draft changes rerun the checks that prove the draft matches the current repo source of truth before external publication.
- Final validation or publication-readiness changes rerun projection for any issue, PR, release, or handoff surface that carries the changed evidence.
- Published issue, PR, release, or handoff corrections rerun a projection consistency check and a narrow Cross-Boundary Coherence review for the corrected surface.
- New operator input, accepted decision changes, review dispositions, handoff updates, or observed corrections that may change Underlying Intent rerun Intent Model Refresh before the next closeout gate.
- Evidence-artifact durability changes rerun the closeout gate that owns the artifact and any projection surface that carries its claims.

If a revision changes security, documentation, validation, PRD/spec/plan scope, or issue/PR projection, rerun the affected upstream gate before the next closeout review.

## Review gates

Cross-Boundary Coherence Ralph Review checks whether the story's process outputs agree across PRD, Blueprints, plans, implementation, deterministic validation, security closeout, documentation closeout, source-disposition/provenance evidence, existing or draft issue/PR projection, and release or handoff surfaces.

Story Quality Ralph Review checks whether the story meets broader quality expectations after coherence is established: DX, UX, code quality, clean architecture, cohesive module boundaries, robustness against unspecified situations, interactions, user personas and attack paths, lessons from pathological dev/ops cycles, and alignment with a coherent strategic vision.

Intent Model Refresh is the first closeout gate. Update the agent's model of Underlying Intent by reviewing recent operator input, accepted ADR/PRD/spec/plan changes, review dispositions, handoff notes, and observed corrections relevant to the story before running downstream closeout gates.

Story Quality also runs an Intent Alignment Check. Compare Effective Intent, meaning the Intent actually imposed by ADRs, PRDs, specs, plans, acceptance criteria, review dispositions, and other declarations, with the refreshed model of Underlying Intent after Cross-Boundary Coherence has made Effective Intent legible. Refresh the model again if closeout evidence introduced new intent signals. Underlying Intent is the stakeholder's actual current Intent: the direction they would want the project to move if a mismatch were brought to their attention. An agent does not directly know a stakeholder's or other intent-capable actor's Underlying Intent; it maintains an evidence-backed model that can be tested through questions, experiments, and observed corrections. Treat these as contraindications for alignment: comments in chat or docs that suggest contrary intent; concrete contradictions; documented revisions or changed priorities; wording that plausibly substitutes a false equivalent for the underlying intent; and documented shifts in direction, strategy, vision, or mental model away from the codified intent. Hypotheses about emotion, belief state, attention, engagement, discipline, or other internal disposition can explain why a mismatch might exist, but they are not evidence by themselves and must not justify unilateral realignment. When observable evidence shows misalignment beyond reasonable doubt, realign the affected declarations and reproject downstream implications. When the model remains uncertain, the case depends on internal-state inference, or the evidence otherwise creates a non-dismissible likelihood of misalignment without certainty, raise a concise question to the operator, using an interactive question tool when available.

Both reviews use Review Until Clean semantics. A finding remains open until fixed, verified, or rejected for a stated technical reason. The latest cycle must have no findings.

## Recursion and bookkeeping

Closeout is recursive only when a substantive change affects an upstream gate. A security fix reopens security closeout; a doc correction reopens documentation closeout; a validator change reopens deterministic validation; a PRD or spec correction reopens the relevant acceptance and projection checks.

Recording the latest clean review result is bookkeeping and does not reopen the full review loop unless it changes substantive claims.

Avoid impossible self-reference. A committed file cannot require the SHA of the commit that contains it. Put post-commit SHA evidence in the PR body, issue update, release note, final response, or a later committed follow-up when that evidence must become durable.

## Completion criteria

A story is ready to close when:

- deterministic validation for the story's scope passes or has an explicit unavailable-control note;
- Change Set Security Closeout is current for the final diff or records why narrower action is sufficient;
- Change Set Documentation Closeout is current for affected docs and records unchanged rationale where no edits were needed;
- Cross-Boundary Coherence Ralph Review and Story Quality Ralph Review both have latest clean cycles;
- issue, PR, release, and handoff drafts or published surfaces are projected from the same current repo facts;
- closeout evidence artifacts are classified by durability, and instance-scoped scratch artifacts are summarized rather than committed or externally projected as project truth;
- deferred risks, unavailable controls, or stakeholder decisions have tracking and owner-visible rationale;
- final publication actions respect repository policy and the human operator's stated pause points.
