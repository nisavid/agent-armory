# Forge Seed Projection Drafts

Status: Review Draft

Projection state: PR published; issue projection pending.

These drafts are review surfaces for Story Closeout. The pull request surface
has been published as <https://github.com/nisavid/agent-armory/pull/1>. The
Published PRD Issue remains pending.

External projection happens only after final validation, clean Cross-Boundary
Coherence review, clean Story Quality review, final commit, and branch push. If
the session pauses before Publishing the PRD Issue, this reviewed draft remains
the source of truth for that issue until work resumes.

## Published PRD Issue Draft

Intended action: create the Published PRD Issue for `docs/prd/forge-seed.md`
in `nisavid/agent-armory` during Issue Projection.

Projected commit SHA: `TO_CAPTURE_IMMEDIATELY_BEFORE_ISSUE_PUBLICATION`

Draft body:

```markdown
# Forge Seed PRD

Status: Implemented on branch `forge-seed`; PR published; pending issue publication.

Repo draft: `docs/prd/forge-seed.md`

## Success Criteria

- The Forge Seed preserves the Source Handoff as provenance and projects
  accepted requirements into repo-native docs, templates, examples, specs,
  validators, and closeout evidence.
- Root `AGENTS.md` gives Smiths the zero-scout Forge Conveyor, including
  Tooling Request and Story Closeout routing.
- Root `README.md` presents the under-construction state of the Armory, links
  readers to the Forge Tour and docs map, keeps Wielders, Outfitters, Smiths,
  and Forgewrights as agent roles, and avoids agent-only policy detail.
- `docs/README.md` routes human readers by goal and Diataxis type.
- Forge Canon describe equipment vocabulary, runbooks, harness
  capabilities, evidence, security/control boundaries, promotion policy, and
  Story Closeout.
- Templates, examples, and Equipment Blueprints exist without implying
  installability, publication, or production readiness.
- Seed Validation and tests check required files, source disposition and
  retirement status, markdown links, templates, examples, specs, Story
  Closeout, security closeout, and documentation closeout.

## Implementation Summary

The Forge Seed adds:

- `docs/closeout/forge-seed-source-disposition.md` for source manifest,
  requirement disposition, checkpoint evidence, and source-retirement stamp;
- Forge Canon under `docs/`;
- a refreshed human-facing docs spine with `README.md`, `docs/forge-tour.md`,
  and `docs/README.md`;
- ADRs for Seed architectural decisions;
- templates for skills, hooks, MCP tools, plugins, scripts, configs, security
  review, Agent Profiles, and interface decisions;
- Forge Examples under `examples/`;
- Equipment Blueprints under `specs/`;
- Tooling Request from Smith to Forgewright;
- Story Closeout, security closeout, documentation closeout, and projection
  draft surfaces;
- `tools/validate_forge_seed.py` and its test suite.

## Validation

- `python3.14 -m unittest tests/test_validate_forge_seed.py`: passed.
- `python3.14 tools/validate_forge_seed.py`: passed.
- `python3.14 tools/validate_forge_seed.py --json`: passed.
- `python3.14 tools/validate_forge_seed.py --final-closeout`: passed.
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
Forge Canon, PRD, ADRs, plan, source-disposition evidence, security docs,
closeout docs, specs, templates, examples, and archived handoff material reached
by stale-language searches.

Material updates include the refreshed public docs spine, Repository Threat
Model, security closeout, Story Closeout, Tooling Request, Source Disposition
Ledger status semantics, Agent Profile terminology alignment, and captured
post-Seed Portable Workflow reflections.

Documentation closeout review: Ralph Review Cycle 87.

## Story Closeout Reviews

Source-retirement and projection consistency review: Ralph Review Cycle 74.

Cross-Boundary Coherence review: Ralph Review Cycle 80.

Story Quality review: Ralph Review Cycle 87.

## Commit

Current commit SHA: `TO_CAPTURE_IMMEDIATELY_BEFORE_ISSUE_PUBLICATION`

The repo draft remains the detailed review artifact. This issue is the tracking
surface for the PRD.
```

## Published Pull Request

Published PR: <https://github.com/nisavid/agent-armory/pull/1>

PR title:

```text
feat(forge): implement forge seed
```

Published PR body:

```markdown
## Summary

- Preserve and project the Source Handoff into Forge Canon,
  templates, examples, specs, validators, and closeout evidence.
- Refresh the public docs spine with an under-construction README, generated
  README hero image, expanded Forge Tour, and human-facing docs map.
- Add Tooling Request, Story Closeout, security closeout,
  documentation closeout, workflow reflection capture, and projection draft
  surfaces.
- Add deterministic Seed Validation coverage and TDD tests for the seeded
  Forge shape.

## Validation

- `python3.14 -m unittest tests/test_validate_forge_seed.py`
- `python3.14 tools/validate_forge_seed.py`
- `python3.14 tools/validate_forge_seed.py --source-retired-pre-stamp`
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

- Documentation closeout: Ralph Review Cycle 87.
- Source-retirement and projection consistency: Ralph Review Cycle 74.
- Cross-Boundary Coherence: Ralph Review Cycle 80.
- Story Quality: Ralph Review Cycle 87.
```

## Release Draft

No release publication is planned for the Forge Seed. The Seed is a branch
and PR change set, not a versioned release.

## Handoff Draft

No separate handoff publication is required during PR review. The durable
handoff surfaces are:

- this projection draft,
- `docs/plans/2026-05-03-forge-seed.md`,
- `docs/closeout/forge-seed-documentation.md`,
- `docs/security/forge-seed-closeout.md`,
- `docs/follow-ups/portable-agentic-engineering-workflow-equipment.md`,
- `docs/closeout/forge-seed-workflow-lessons.md`,
- `docs/closeout/forge-seed-engineering-workflow-generalization.md`.

Any in-chat pause during PR review should report the pushed branch, PR URL,
validation state, whether the Published PRD Issue has been created or remains a
reviewed draft, and that the Seed Closeout Addendum remains open through PR
review orchestration, merge, merge cleanup, external surface reconciliation, and
final hand-back.

If issue projection, branch push, PR creation, PR review orchestration, merge,
merge cleanup, external surface reconciliation, or final hand-back exposes
additional workflow lessons, append them to the Seed Closeout Addendum before
treating the Forge Seed as fully closed. If the operator explicitly holds or
cancels the Seed instead of merging it, continue capture through the hold or
cancellation hand-back and record the unmerged state.
