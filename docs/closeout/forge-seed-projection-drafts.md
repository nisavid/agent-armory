# Forge Seed Projection Drafts

Status: Review Draft

These drafts are review surfaces for Story Closeout. They are not published
issue, PR, release, or handoff surfaces.

External projection happens only after final validation, clean Cross-Boundary
Coherence review, clean Story Quality review, final commit, and branch push.
The operator-requested pause point happens after branch push and before PR
creation. If the session pauses before Publishing the PRD Issue, this reviewed
draft remains the source of truth until work resumes.

## Published PRD Issue Draft

Intended action: create the Published PRD Issue for `docs/prd/forge-seed.md`
in `nisavid/agent-armory` during Issue Projection.

Projected commit SHA: `TO_CAPTURE_IMMEDIATELY_BEFORE_ISSUE_PUBLICATION`

Draft body:

```markdown
# Forge Seed PRD

Status: Implemented in branch `forge-seed`; pending PR publication.

Repo draft: `docs/prd/forge-seed.md`

## Success Criteria

- The Forge Seed preserves the Source Handoff as provenance and projects
  accepted requirements into repo-native docs, templates, examples, specs,
  validators, and closeout evidence.
- Root `AGENTS.md` gives Smiths the zero-scout Forge Conveyor, including
  Tooling Request and Story Closeout routing.
- Root `README.md` remains the Forge Tour and avoids agent-only
  policy detail.
- Forge Canon describe equipment vocabulary, runbooks, harness
  capabilities, evidence, security/control boundaries, promotion policy, and
  Story Closeout.
- Templates, examples, and downstream Smith specs exist without implying
  installability, publication, or production readiness.
- Seed Validation and tests check required files, Source Projection Register
  semantics, markdown links, templates, examples, specs, Story Closeout,
  security closeout, and documentation closeout.

## Implementation Summary

The Forge Seed adds:

- preserved Source Handoff material under `docs/metasmith/handoff/2026-05-02/`;
- `docs/metasmith/source-projection.md` for requirement disposition and
  validation status;
- Forge Canon under `docs/`;
- ADRs for Seed architectural decisions;
- templates for skills, hooks, MCP tools, plugins, scripts, configs, security
  review, Agent Profiles, and interface decisions;
- Forge Examples under `examples/`;
- downstream Smith specs under `specs/`;
- Tooling Request from Smith to Forgewright;
- Story Closeout, security closeout, documentation closeout, and projection
  draft surfaces;
- `tools/validate_forge_seed.py` and its test suite.

## Validation

- `python3.14 -m unittest tests/test_validate_forge_seed.py`: 264 tests
  passed.
- `python3.14 tools/validate_forge_seed.py`: 0 failed, 174 passed.
- `python3.14 tools/validate_forge_seed.py --json`: 174 passing result
  objects.
- `python3.14 tools/validate_forge_seed.py --final-closeout`: 0 failed,
  175 passed.
- `git diff --check`: passed.

## Security Closeout

- Threat model: `docs/security/threat-model.md`
- Security closeout: `docs/security/forge-seed-closeout.md`
- Report disposition: recorded in `docs/security/forge-seed-closeout.md`;
  transient host-local scan paths are intentionally not republished in external
  projection surfaces.
- Findings disposition: no reportable findings.
- Deferred risks: none.

## Documentation Closeout

Documentation closeout inspected live agent-facing and human-facing surfaces,
Forge Canon, PRD, ADRs, plan, source projection, security docs,
closeout docs, specs, templates, examples, and archived handoff material reached
by stale-language searches.

Material updates include the Repository Threat Model, security closeout, Story
Closeout, Tooling Request, Source Projection Register status
semantics, Agent Profile terminology alignment, and captured post-Seed Portable
Workflow reflections.

Documentation closeout review: Ralph Review Cycle 68.

Ralph Review Cycle 58 found that the projection draft omitted the portable
report-disposition evidence required by the plan. Ralph Review Cycle 59
verified that fix. Ralph Review Cycle 60 verified the Intent Alignment Check wording,
projection-draft target coverage, plan cross-references, and story-review
evidence placeholders, and found no remaining documentation closeout issues.
Ralph Review Cycle 66 found a stale security validation count, and Ralph Review
Cycle 67 found stale path-shaped scan artifact contract wording in review
history. Those findings were fixed. Ralph Review Cycle 68 verified the current
report-disposition language, artifact-durability guardrail, intent terminology,
gate ordering, security closeout evidence, validation evidence, and intentionally
pending story-review placeholders, and found no remaining documentation
closeout issues.

## Story Closeout Reviews

Cross-Boundary Coherence review: Ralph Review Cycle 71. Cycle 69 found the
Forge Seed coherent across PRD, plan, canonical docs, validation, security,
documentation closeout, projection drafts, deferred follow-ups, and the
branch-push pause. Cycle 71 reran the affected boundary after the final staging
plan was fixed to include `.gitignore`; it found no remaining coherence issues.

Story Quality review: Ralph Review Cycle 72. Cycle 70 found that the final
staging plan omitted `.gitignore`; that finding was fixed and narrow
Cross-Boundary Cycle 71 verified the fix. Cycle 72 refreshed the Intent Model,
ran the Intent Alignment Check, reviewed DX, UX, architecture, maintainability,
security robustness, pathological-cycle mitigations, and strategic alignment,
and found no remaining Story Quality issues.

## Commit

Current commit SHA: `TO_CAPTURE_IMMEDIATELY_BEFORE_ISSUE_PUBLICATION`

The repo draft remains the detailed review artifact. This issue is the tracking
surface for the PRD.
```

## Pull Request Draft

PR creation is intentionally paused after branch push in this session. The
operator has a side quest to perform at that point.

Draft PR title:

```text
feat(forge): implement forge seed
```

Draft PR body:

```markdown
## Summary

- Preserve and project the Source Handoff into Forge Canon,
  templates, examples, specs, validators, and closeout evidence.
- Add Tooling Request, Story Closeout, security closeout,
  documentation closeout, and projection draft surfaces.
- Add deterministic Seed Validation coverage and TDD tests for the seeded
  Forge shape.

## Validation

- `python3.14 -m unittest tests/test_validate_forge_seed.py`
- `python3.14 tools/validate_forge_seed.py`
- `python3.14 tools/validate_forge_seed.py --json`
- `python3.14 tools/validate_forge_seed.py --final-closeout`
- `git diff --check`

## Security

- Threat model: `docs/security/threat-model.md`
- Security closeout: `docs/security/forge-seed-closeout.md`
- Report disposition: recorded in `docs/security/forge-seed-closeout.md`;
  transient host-local scan paths are intentionally not republished in external
  projection surfaces.
- Findings: no reportable findings.
- Deferred risks: none.

## Reviews

- Documentation closeout: Ralph Review Cycle 68.
- Cross-Boundary Coherence: Ralph Review Cycle 71.
- Story Quality: Ralph Review Cycle 72.
```

## Release Draft

No release publication is planned for the Forge Seed. The Seed is a branch
and PR change set, not a versioned release.

## Handoff Draft

No separate handoff publication is required before PR creation. The durable
handoff surfaces are:

- this projection draft,
- `docs/plans/2026-05-03-forge-seed.md`,
- `docs/closeout/forge-seed-documentation.md`,
- `docs/security/forge-seed-closeout.md`,
- `docs/metasmith/handoff/2026-05-03-agentic-engineering-workflow-equipment.md`,
- `docs/metasmith/handoff/2026-05-03-agentic-engineering-workflow-seed-closeout-addendum.md`.

The in-chat pause after branch push should report the pushed branch, validation
state, whether the Published PRD Issue has been created or remains a reviewed
draft, and that PR creation is intentionally paused for the operator's side
quest. It should also state that the Seed Closeout Addendum remains open through
PR creation, PR review orchestration, merge, merge cleanup, external surface
reconciliation, and final hand-back.

If issue projection, branch push, PR creation, PR review orchestration, merge,
merge cleanup, external surface reconciliation, or final hand-back exposes
additional workflow lessons, append them to the Seed Closeout Addendum before
treating the Forge Seed as fully closed. If the operator explicitly holds or
cancels the Seed instead of merging it, continue capture through the hold or
cancellation hand-back and record the unmerged state.
