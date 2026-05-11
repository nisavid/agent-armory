# Harness Capability Profiles Epic Closeout

Status: Closeout Evidence

## Scope

This closeout covers issue #49 for the Harness Capability Profiles epic, issue #4.
The pre-Config scope is the manual, source-backed capability-profile system:
Armory and Forge validation boundaries, per-harness profile migration,
schema-pressure research, six refreshed Vanilla Harness Capability Profiles,
the Capability Profiling Protocol, and manual profile refresh workflow.

Recurring refresh integration remains deferred until Agent Equipment Config and
Periodic Actions provide the required configuration and scheduled-action
surfaces.

## Delivered Surface

- PR #51 renamed live validation to Armory Integrity Validation and Forge
  Integrity Validation.
- PR #52 migrated the retired aggregate catalog into six validated per-harness
  Vanilla Harness Capability Profiles and Manager Core validation.
- PR #53 added durable research notes and schema-pressure validation.
- PR #55 refreshed all six profiles against current source-backed evidence.
- PR #57 defined the Capability Profiling Protocol and validated protocol
  artifacts.
- PR #54 certified the operating-model layer needed by manual refresh.
- PR #58 added staged manual refresh commands, mutation gates, audit behavior,
  and review workflow documentation.

The structured source of truth is `docs/harness-capabilities/vanilla/`. The
human-facing front door is `docs/harness-capabilities.md`.

## Downstream State

Agent Equipment Config can resume against current Vanilla Harness Capability
Profiles after this closeout lands and issue #4 is closed. Config enforcement
projection work may consume the descriptive profile surface, but profiles do
not prescribe downstream Equipment decisions.

Periodic refresh remains future work. Harness Capability Refresh should invoke
the Manager Core's staged scout, analyze, plan, diff, apply, and audit flow when
Agent Equipment Config and Periodic Actions provide the required configuration,
authority, and scheduled-action surfaces.

## Residual Unknowns

Profile files intentionally preserve unsupported, unknown, not-applicable, and
environment-scoped claims where current evidence is incomplete. Those unknowns
are accepted as non-blocking for returning to Agent Equipment Config because
the profiles expose them directly and the Manager Core validates the structure.

Effective Harness Capability Profile tooling remains deferred until downstream
equipment needs to compose vanilla profiles with installed equipment, local
config, and local observations. Memory-system evaluation remains routed to
future Reflection and cognition work unless a narrower Config or harness issue
selects it first. Issue #59 tracks the Codex memory-write authority unknown
surfaced by the manual refresh smoke audit.

## Security Closeout

This issue #49 change set updates closeout documentation and projection state.
It adds no executable code, hooks, MCP/tool definitions, permissions, secrets
handling, network access, filesystem mutation path, package metadata, or new
security policy.

The executable and mutation-capable Harness Capability Profile Manager surfaces
were reviewed and hardened in PRs #52, #53, #55, #57, and #58. No surviving
reportable security findings are recorded for the pre-Config epic scope.

A targeted secret-pattern scan of the reconciliation files found only generic
policy references to secrets and authorization, not credential-shaped literals.

## Documentation Closeout

The reconciliation inspected active human-facing and agent-facing docs that
could carry stale aggregate-catalog, Seed-era validation, manual-refresh, or
downstream Config claims. This closeout updates the active bundle, refresh
spec, documentation map, README, Forgewright runbook, and interface decision
record. Historical Forge Seed records remain historically accurate.

Agent Equipment Config specs need no committed change in this closeout: the
current Config bundle already names Vanilla Harness Capability Profiles as
descriptive source-backed evidence and does not claim that Config owns recurring
refresh.

## Validation Summary

Baseline validation after syncing main passed:

- `env PYTHONPYCACHEPREFIX=/tmp/agent-armory-pycache-baseline python3.14 -m unittest`
- `env PYTHONPYCACHEPREFIX=/tmp/agent-armory-pycache-baseline-hcp python3.14 tools/harness_capability_profiles.py validate --json`
- `env PYTHONPYCACHEPREFIX=/tmp/agent-armory-pycache-baseline-integrity python3.14 tools/validate_armory_integrity.py --final-closeout --json`
- `git diff --check`

Manual refresh smoke validation passed against the example Codex refresh input:

- `env PYTHONPYCACHEPREFIX=/tmp/agent-armory-pycache-smoke python3.14 tools/harness_capability_profiles.py scout --input examples/harness-capability-refresh/codex-scout-input.json --write-output codex-security-scans/issue49/scout.json --json`
- `env PYTHONPYCACHEPREFIX=/tmp/agent-armory-pycache-smoke python3.14 tools/harness_capability_profiles.py analyze --scout-report codex-security-scans/issue49/scout.json --write-output codex-security-scans/issue49/analysis.json --json`
- `env PYTHONPYCACHEPREFIX=/tmp/agent-armory-pycache-smoke python3.14 tools/harness_capability_profiles.py plan --analysis-report codex-security-scans/issue49/analysis.json --write-output codex-security-scans/issue49/plan.json --json`
- `env PYTHONPYCACHEPREFIX=/tmp/agent-armory-pycache-smoke python3.14 tools/harness_capability_profiles.py diff --plan codex-security-scans/issue49/plan.json --json`
- `env PYTHONPYCACHEPREFIX=/tmp/agent-armory-pycache-smoke python3.14 tools/harness_capability_profiles.py audit --scout-report codex-security-scans/issue49/scout.json --analysis-report codex-security-scans/issue49/analysis.json --plan codex-security-scans/issue49/plan.json --write-output codex-security-scans/issue49/audit.json --json`

The smoke run produced no canonical profile mutations and routed the
`unknown-codex-memory-write-authority` candidate to issue #59. Scratch JSON
outputs stayed under the ignored `codex-security-scans/issue49/` work area.

Final validation for this closeout passed:

- `env PYTHONPYCACHEPREFIX=/tmp/agent-armory-pycache-final2 python3.14 -m unittest`
- `env PYTHONPYCACHEPREFIX=/tmp/agent-armory-pycache-final2-hcp python3.14 tools/harness_capability_profiles.py validate --json`
- `env PYTHONPYCACHEPREFIX=/tmp/agent-armory-pycache-final2-integrity python3.14 tools/validate_armory_integrity.py --final-closeout --json`
- `git diff --check`
- stale-surface search for obsolete aggregate-catalog, old manual-refresh blocker, and live Seed Validation wording

## Ralph Reviews

Cross-Boundary Coherence Ralph Review cycle 1 found three actionable gaps:
downstream docs still framed manual refresh as blocking Config, issue #49's
closeout evidence needed a durable home, and the manual-refresh smoke candidate
needed issue routing. This change set resolves those gaps by updating active
docs/specs, adding this closeout evidence, and opening issue #59. Cycle 2 is
clean.

Story Quality Ralph Review cycle 1 found one validation-quality issue: the
recurring-refresh spec edit broke the repository's required non-implementation
boundary phrase. The wording is restored while preserving the current
manual-refresh and periodic-refresh distinction. Cycle 2 is clean.

The resulting operator and agent experience is coherent: Config can resume
without mixed aggregate/profile state, profile unknowns stay visible, recurring
refresh stays explicitly deferred, and active issue, doc, profile, schema, and
workflow surfaces do not treat Seed Validation or the retired aggregate catalog
as the live boundary.
