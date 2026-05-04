# Evidence Taxonomy

Status: Forge Seed

Smiths and Forgewrights label evidence so plausible guidance does not become an unlabeled fact. Use the strongest available category and record uncertainty when evidence is incomplete, inconsistent, or volatile.

## documentation-supported

A documentation-supported claim is backed by official documentation, first-party release notes, or first-party changelogs.

Use this category for public behavior that the harness provider documents. Record source URL, checked date, version basis, and any preview, beta, or deprecation warning.

## source-supported

A source-supported claim is backed by first-party source code, schema definitions, manifests, tests, or repository files.

Use this category when docs are absent or incomplete but the implementation source is available. Record the repository, commit, tag, file path, checked date, and inference boundary.

## implementation inference

An implementation inference is a claim reasoned from documented or source-supported behavior but not explicitly stated as a provider rule.

Use this category for design implications, compatibility expectations, or behavior likely to follow from inspected code. State the inference and what would falsify it.

## practitioner wisdom

Practitioner wisdom is a pattern supported by experience rather than a specific source.

Use it sparingly for maintainability or ergonomics guidance, such as preferring narrow tools over broad mutation surfaces. Do not use practitioner wisdom to justify security, compatibility, or harness capability claims.

## hypothesis

A hypothesis is a plausible but unverified claim.

Use it for questions to test, not as guidance to follow. Convert important hypotheses into Harness Fact Refresh tasks, pressure scenarios, experiments, or downstream specs.

## artifact durability

Before committing, publishing, or projecting closeout evidence, classify each
evidence artifact by durability:

- Durable project evidence belongs in committed docs, issue bodies, PR bodies,
  release notes, or handoff records when it remains accurate beyond the review
  instance.
- Portable review evidence can be summarized or attached to an external review
  surface when another reviewer can evaluate it without access to the original
  host, worktree, or scratch directory.
- Instance-scoped scratch evidence includes raw tool logs, local scan bundles,
  temporary reports, host-local paths, screenshots, copied diffs, and work
  directories whose accuracy is limited to one review run.

Do not commit or externally project raw instance-scoped scratch evidence as
project truth. Summarize the scope, commands, artifact disposition, findings,
fixes, suppressions, deferred risks, and durable conclusions in the appropriate
closeout surface. If a scratch artifact later becomes durable project material,
move it to a neutral project path and update its scope, review status, and
staleness boundaries.

## source hygiene

Follow these hygiene rules for Framework claims:

- prefer first-party docs, releases, source, schemas, and tests;
- label third-party metadata as fallback;
- keep local CLI observations separate from source-backed facts;
- record checked date and version basis for harness claims;
- record uncertainty when sources disagree or are stale;
- preserve Source Handoff provenance without treating it as the current canonical surface;
- classify evidence artifacts by durability before committing, publishing, or projecting them;
- refresh volatile claims before they drive implementation, validation, or publication.
