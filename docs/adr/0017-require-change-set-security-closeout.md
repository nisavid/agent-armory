# Require Change Set Security Closeout

Every change set must complete the security analyses applicable to its scope before merge-readiness. The Forge Seed must create or update a persistent Repository Threat Model, run Codex Security's scan phases against the Seed change set, resolve or explicitly disposition reportable findings, and record closeout evidence.

## Considered Options

- Require applicable security closeout for every change set.
- Run security analysis only for obviously security-sensitive code.
- Defer security modeling until after the Forge Seed.

## Consequences

- Security review becomes a normal closeout gate rather than an optional final note.
- Diff-sized changes can use scoped analysis, while repository-shaping changes can require a fuller Codex Security pass.
- Reportable findings block merge-readiness unless fixed or explicitly deferred with stakeholder approval, risk rationale, and tracking.
- Transient scan bundles can remain in tool artifact directories, but the change set must summarize the commands, artifacts, findings, and dispositions needed for review.
