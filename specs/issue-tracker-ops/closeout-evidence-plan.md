# Closeout Evidence Plan: Issue Tracker Ops

Status: Equipment Candidate
Promotion state: implemented for bootstrap MVP; full delivery remains open

## Durable project evidence

Commit durable evidence in neutral project paths when it remains accurate beyond
this review instance:

- Equipment Design Bundle records under `specs/issue-tracker-ops/`.
- Adapter source and tests under `tools/` and `tests/`.
- Updated Forge Canon or vocabulary surfaces.
- Security and documentation closeout summaries when they describe durable
  project state.

## Portable review evidence

Project portable summaries to issue #11, the PR body, and final handoff:

- exact validation commands and pass/fail status;
- live issue operations performed by the adapter;
- child issues created for remaining work;
- dependency relation changes or verification;
- security review scope, findings, fixes, suppressions, and residual risks;
- documentation closeout scope and unchanged rationale.

## Instance-scoped scratch evidence

Do not commit or externally project raw scratch material as project truth:

- raw `gh --verbose` output;
- local token, auth, or keyring details;
- copied terminal logs with host paths;
- temporary dry-run bodies containing private context;
- unreviewed security scan work directories.

Summarize scratch evidence by operation, scope, disposition, and durable
conclusion.

## Bootstrap closeout checklist

- Forge capability card or equivalent Tooling Gap capture exists.
- Interface decision is recorded.
- Security/control classification is recorded.
- Remaining work is decomposed into child issues or explicitly linked
  follow-ups.
- GitHub Issues-only MVP is delivered and validated.
- MVP covers direct issue read, list, create, update, close or reopen through
  update state, comment, dependency, and supported native parent/sub-issue
  operations under provisional policy.
- Validation evidence is recorded.

## Config profile and onboarding closeout

Issue #13 closes when the progressive config profile and onboarding contract is
durable, validated, projected, reviewed, and merged. The closeout evidence
must include:

- the owner spec at
  [Config profile and onboarding](config-profile-and-onboarding.md);
- bundle references that route readers from the capability card, interface
  decision, security/control classification, pressure scenarios, validation
  plan, and closeout plan to that owner spec;
- validator evidence for required owner-spec presence and section coverage;
- security and documentation closeout scope;
- Ralph Review cycles until clean, including Cross-Boundary Coherence and
  Story Quality checks;
- tracker drift correction that records #23 as closed, #107 as the PRD
  reference, #103 as policy-doc migration, #93/#99 as Config authoring
  mechanics, #121 as onboarding follow-up projection, and #18 as final
  validation/publication.

## Full-delivery closeout

Issue #11 remains open after the tracker-neutral core inspection surface until
the full GitHub adapter, Projects extension or child issue, runtime
implementation of the Issue Ops plain config profile, Agent Equipment Config
integration, onboarding model, issue repair and orchestration modes, security
controls, fallback compatibility beyond bootstrap records, docs, and full
validation matrix are complete.
