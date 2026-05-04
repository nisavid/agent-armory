# Forge Seed Security Closeout

Status: Completed Security Closeout

## Scan scope

Codex Security scanned the merge-base-to-working-tree Forge Seed diff from the
`main` merge base `dbf41ace42ff4759a6d680ab963d7498996ddb6f` to the Seed
publication worktree that will be published from branch `forge-seed`, including
committed branch changes, staged diff, unstaged worktree edits, and untracked
intended files present in the scan instance.

The scan covered:

- active agent instructions and vocabulary,
- Forge Canon, Blueprints, templates, examples, and source-disposition evidence,
- the repository threat model,
- security and documentation closeout surfaces,
- Story Closeout, projection draft, and workflow closeout addendum surfaces,
- local Python validation tooling and tests,
- non-runtime hook, MCP/tool, plugin, script, config, and Agent Profile
  templates.

The human-facing documentation spine refresh touched `README.md`,
`docs/forge-tour.md`, `docs/README.md`, `CONTEXT.md`,
`docs/ubiquitous-language.md`, `docs/prd/forge-seed.md`,
`docs/security/threat-model.md`, `templates/skill/SKILL.md`, this closeout
surface, `docs/closeout/forge-seed-documentation.md`, and projection evidence.
The final public README presentation refresh also added
`docs/assets/agent-armory-hero.png` and a README image reference.
It did not add or materially change runtime-integrated execution surfaces such
as hooks, MCP/tool definitions, permissions, secrets handling,
network/file/process side effects, package metadata, security policy, or
Published Agent Equipment. This change set did include local validation tooling
and tests, which were included in scan scope and re-validation.
`docs/security-and-control.md` and `docs/security/threat-model.md` remain
current for the refreshed public docs path.

## Commands

- `python3.14 -m unittest tests.test_validate_forge_seed.SecurityCloseoutValidationTests`
- `python3.14 -m unittest tests/test_validate_forge_seed.py`
- `python3.14 tools/validate_forge_seed.py`
- `python3.14 tools/validate_forge_seed.py --json`
- `git diff --check`
- Targeted Codex Security discovery searches for dangerous sinks, secret-like
  terms, promotion-state claims, installability claims, and external path or
  URL surfaces.
- Codex Security phase sequence: threat modeling, finding discovery,
  validation, attack-path analysis, final report.

Validation and attack-path analysis were not separately run because finding
discovery produced no technically plausible candidates. That follows the Codex
Security diff-scan workflow.

## Scan artifact disposition

Codex Security generated an instance-scoped scan bundle outside the repository
during this review. The raw bundle is ephemeral scratch evidence, not a tracked
project artifact, not portable review evidence, and not a standing source of
project truth.

Artifact durability classification: instance-scoped scratch evidence. Durable
security evidence is this closeout summary, the repository threat model, and the
validation results recorded below.

The transient scan bundle contained:

- `artifacts/threat_model.md`,
- `artifacts/runtime_inventory.md`,
- `artifacts/finding_discovery_report.md`,
- captured git diff, worktree diff, staged diff, and untracked-file evidence,
- targeted discovery search outputs.

## Report disposition

The final Codex Security report was scoped to this review instance: the
Forge Seed diff, the working tree at review time, and the scan commands
listed above. Its durable conclusions are summarized in this closeout. The raw
report is not committed and should not be cited as reusable project doctrine.

## Findings disposition

No reportable findings.

The human-facing documentation spine refresh produced no reportable security
finding and no deferred security risk.

Suppressed findings: none.

Finding discovery promoted no technically plausible candidate to validation.
Search hits were traced to test fixtures, validator deny-list strings,
standard-library read-only parsing, explicit security guidance, non-installable
example boundaries, or documentation source URLs that Seed runtime code does
not fetch.

## Hardening changes

No finding-driven hardening changes were required.

Preventive hardening added during the Forge Seed closeout includes:

- a durable Repository Threat Model at `docs/security/threat-model.md`,
- a required change-set security closeout artifact at this path,
- validator coverage for threat model and security closeout requirements,
- Story Closeout ordering and rerun rules for security-dependent changes,
- strict final-closeout validation for unresolved story-review evidence and
  host-local scan paths in external projection drafts,
- TDD coverage for missing closeout paths, required sections, completed status,
  and closeout evidence.

## Re-validation status

Re-validation passed after this closeout file was populated.

- `python3.14 -m unittest tests/test_validate_forge_seed.py`: passed.
- `python3.14 tools/validate_forge_seed.py`: passed.
- `python3.14 tools/validate_forge_seed.py --json`: passed.
- `git diff --check`: passed.

## Deferred-risk tracking

Deferred risks: none.

No reportable security finding was deferred. Future change sets that introduce
or materially change executable code, hooks, MCP/tool definitions, permissions,
secrets handling, network/file/process side effects, package metadata, security
policy, or Published Agent Equipment require their own applicable security
analysis and closeout.
