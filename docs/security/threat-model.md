# Agent Armory Repository Threat Model

Status: Repository Threat Model

This threat model covers the Agent Armory repository, not one task or one diff.
It is the durable baseline for Forge Seed security closeout and future
change-set scans.

## Overview

Agent Armory is a repository for Agent Equipment and the Agent Equipment
Forge. The Forge Seed currently contains documentation, source
projection records, templates, examples, specs, a harness capability catalog,
and standard-library validation tooling. It does not expose a network service,
authentication boundary, tenant boundary, remote request path, installed hook,
installed MCP server, or published skill.

The primary security concern in the Seed is integrity of guidance and
validation. Future Smiths and Forgewrights may use these files to decide what
equipment to build, promote, install, publish, or grant authority. A misleading
Forge surface can therefore become a downstream execution, credential,
filesystem, network, scheduling, or repository-control risk when future
equipment is promoted.

## Threat Model, Trust Boundaries, and Assumptions

### Assets

- Active repository policy in `AGENTS.md` and project vocabulary in
  `CONTEXT.md`.
- Forge design, validation, and teaching surfaces in ADRs, canonical
  Forge Canon, Blueprints, templates, examples, and validators.
- Forge Seed requirements, source-disposition records, PRD content, plan
  content, and closeout evidence.
- Preserved Source Handoff files, which are provenance rather than active
  instructions.
- Validation tooling that future agents use to decide whether Forge surfaces
  are complete.
- Future Agent Equipment surfaces, including skills, MCP/tool definitions,
  hooks, scripts, config, Agent Profiles, and plugin manifests.
- Security and documentation closeout records that carry merge-readiness claims
  into PRs, issues, and future work.

### Trust boundaries

- Human operator to agent: the operator initiates project initiatives and work
  sessions; agents execute within repo policy, tool permissions, and review
  gates.
- Active repo policy to archived provenance: current root instructions and
  canonical docs supersede archived handoff prompts and session notes.
- Documentation to executable equipment: specs, templates, and examples may
  influence future code, hooks, MCPs, scripts, or plugins, but are not
  themselves installable equipment.
- Local validation tooling to filesystem: `tools/validate_forge_seed.py`
  reads repo files and reports validation status for the operator or agent.
- Repo content to external control surfaces: issue projection, PR bodies, and
  review comments can publish project status and security claims outside the
  repository.
- Future equipment to host or network resources: promoted equipment may receive
  permissions, credentials, filesystem access, process execution, scheduling,
  or network access.

### Assumptions

- The current Forge Seed has no network service, authentication boundary,
  tenant boundary, or remote request path.
- The Seed Validation Tool is a local standard-library Python tool that reads
  repository files and writes only process output.
- Agents and humans run validation from a trusted checkout, while still
  reviewing branch content as potentially adversarial.
- Transient Codex Security scan bundles may live outside the repository, but
  durable merge-readiness evidence is summarized in committed closeout docs or
  external PR/issue surfaces.
- Future Agent Equipment can become security-sensitive when it introduces
  execution, hooks, MCP/tools, permissions, credentials, scheduling, external
  disclosure, or mutation authority.

### Invariants

- Archived handoff content remains provenance and does not become active
  instruction unless projected into a live Forge surface.
- Examples and specs must not claim to be installable, loadable,
  production-ready, published, or validated Agent Equipment.
- Harness-specific claims stay source-backed with checked dates, version basis,
  evidence category, and uncertainty.
- Mutation-capable equipment must classify side effects, permissions, secrets,
  approval requirements, rollback or cleanup behavior, and failure modes before
  promotion.
- Local-only operator choices, including machine-specific automation
  installation choices, must not be committed by default.
- Validation tooling must not follow symlink escapes, absolute paths, `..`
  paths, URL-scheme paths, or repository-root escapes for required repo
  surfaces.
- Reportable security findings block merge-readiness until fixed, suppressed
  with evidence, or explicitly deferred by the stakeholder with risk rationale
  and tracking.

## Attack Surface, Mitigations, and Attacker Stories

### Attacker-controlled inputs

Current Forge Seed inputs are primarily repository files in the checked-out
worktree. A malicious branch, compromised dependency source, or misleading
handoff note can attempt to alter:

- Markdown and TOML files parsed by the Seed Validation Tool.
- Source projection rows, plan status, PRD criteria, ADRs, specs, templates,
  and examples.
- Links and path strings that future agents may follow.
- Claimed promotion states such as example, specified, validated, or published.
- Closeout evidence, security scan summaries, issue projection text, and review
  dispositions.

Future equipment can add attacker-controlled inputs from harness events,
MCP/tool arguments, hook payloads, scripts, config files, external APIs, issue
or PR comments, repository metadata, local filesystem state, and scheduled
actions.

### Existing mitigations

- Root `AGENTS.md` routes agents through current live Forge surfaces and
  treats archived handoff material as provenance.
- `docs/closeout/forge-seed-source-disposition.md` maps accepted Source
  Handoff requirements to live target paths, operator dispositions, checkpoint
  evidence, and source-retirement status.
- `tools/validate_forge_seed.py` checks required paths, source disposition,
  source retirement, markdown links, promotion-state boundaries, harness
  catalog fields, and closeout surfaces.
- The validator rejects symlinked required paths and repository-root escapes for
  required live surfaces.
- Templates and examples explicitly carry non-installable, non-production seed
  boundaries.
- Change-set policy requires security closeout, documentation closeout, and
  review before merge-readiness.

### Attacker stories

- A contributor edits an archived handoff file or example so a future agent
  treats stale or adversarial guidance as active policy.
- A branch changes validation logic so incomplete source disposition or missing
  closeout evidence appears complete.
- A template normalizes broad permissions or missing rollback guidance, making a
  future Smith more likely to create overpowered equipment.
- An issue or PR projection reports stale security status, causing reviewers to
  merge a change set with unresolved risk.

### Out-of-scope attacker stories

- Remote exploitation of a live service is out of scope for the current Seed
  because the repository does not expose a service or request path.
- Cross-tenant data access is out of scope for the current Seed because the
  repository has no tenant model or data plane.
- Dependency exploitation through package installation is low relevance for the
  current Seed because validation uses the Python standard library and Seed
  artifacts are docs/templates/examples, not installable runtime packages.

### High-impact failure modes

- Active policy is hidden in archived provenance, examples, or bulky docs that
  future agents do not reliably load.
- A spec, template, or example is mistaken for installed, validated, or
  production-ready equipment.
- A validator gap marks incomplete, stale, or misleading Forge surfaces as
  ready.
- A hook, MCP/tool definition, script, Agent Profile, or plugin template omits
  side-effect, permission, approval, secret, or rollback boundaries.
- A future equipment bundle grants broad filesystem, process, network, issue,
  PR, repository, or credential authority without matching controls.
- Security closeout suppresses, loses, or misstates findings without durable
  evidence and stakeholder-approved tracking.
- Issue or PR projection publishes stale SHA, stale validation status, or
  incomplete security/documentation closeout claims.

## Severity Calibration (Critical, High, Medium, Low)

Critical findings are unlikely in the current Seed unless a change introduces
actual executable equipment, credential handling, repository mutation, network
service exposure, or a validation bypass that would predictably authorize those
capabilities downstream.

High severity applies to changes that let future agents or reviewers treat
unsafe equipment as published, validated, or approved for broad authority.
Examples include a validator bypass for promotion-state labels, a template that
requires overbroad filesystem or credential access without controls, or a
closeout record that falsely suppresses a reportable security finding.

Medium severity applies to misleading or incomplete guidance that can plausibly
lead to unsafe equipment but still requires a later Smith, reviewer, or operator
decision before privileged execution occurs. Examples include unclear rollback
expectations, weak side-effect classification, stale harness capability facts,
or broken links from canonical security docs to the threat model.

Low severity applies to clarity, consistency, or provenance issues that are
unlikely to change security-sensitive behavior by themselves. Examples include a
minor wording mismatch in non-normative prose, a redundant reference, or a
non-blocking documentation gap that does not affect promotion, authority, or
validation.
