# Security and Control Classification: Harness Capability Lifecycle Methodology

Status: Equipment Blueprint
Promotion state: specified

## Scope

This classification covers the issue #62 design package: candidate discovery,
evidence classification, cross-harness correlation, schema pressure,
deprecation/removal routing, issue projection, and future implementation
boundaries. It does not certify Manager Core implementation, schema migration,
profile mutation, automation, Jig Runner behavior, or local harness execution.

## Assets

- Vanilla Harness Capability Profiles and profile schema docs.
- Candidate records, Study Plans, Study Reports, schema pressure reports, and
  future lifecycle disposition artifacts.
- Local observations, raw source notes, profile diffs, logs, transcripts,
  screenshots, command output, and test artifacts.
- User home directories, workspaces, harness configs, tokens, secrets, model
  provider settings, and managed policy config.
- GitHub Issues, PR bodies, comments, review threads, and closeout summaries.
- Future Agent Test Jig outputs, Harness Test Suite results, and Jig Adequacy
  Reports.

## Trust boundaries

- First-party sources to agent-guided interpretation.
- Fallback or third-party sources to labeled evidence.
- Local observation to durable profile truth.
- Future Jig Runner output to lifecycle decisions.
- Schema pressure to profile schema mutation.
- Candidate disposition to GitHub issue projection.
- Scratch artifacts to public PR, issue, or committed docs.
- Config, sandbox, approval, permission, hook, MCP/tool, plugin, and
  automation claims to downstream equipment projection.

## Side effects

| Side effect | Classification | Control expectation |
| --- | --- | --- |
| Source scouting | Read-only or network read | Prefer first-party sources and record checked scope. |
| Local observation | Read-only, local write, or process execution | Use approved study or refresh plan and scratch disposition. |
| Profile mutation | Local write | Manager Core dry-run/apply gates and validation evidence. |
| Schema mutation | Local write | Schema pressure, migration plan, tests, and review. |
| Issue projection | External disclosure/write | Keep bodies scoped, public-safe, and evidence-classified. |
| Future jig execution | Process/network/local write | Jig Test Plan, driver policy, adequacy report, and approval. |
| Automation | Recurring external effect | Defer to Config and Periodic Actions gates. |

## Threats

- A source page or changelog is stale, ambiguous, or version-scoped, but the
  lifecycle promotes it as a timeless capability fact.
- A compatibility bridge is treated as native support, leading Smiths to place
  equipment into a harness surface that cannot actually enforce or activate
  it.
- A local observation leaks private paths, secrets, prompts, screenshots, or
  configured equipment into a public issue or committed doc.
- A future candidate artifact allows unreviewed profile mutation or schema
  migration based on prose rather than deterministic preconditions.
- Hook, MCP/tool, plugin, sandbox, approval, managed-policy, or automation
  claims omit authority and side-effect semantics, creating unsafe downstream
  equipment.
- A future Agent Test Jig result is accepted without driver adequacy,
  unsupported-control, fixture, or cleanup evidence.
- Issue projection hides a blocker by marking implementation work unblocked
  while it depends on Config, Periodic Actions, Manager Core, schema, or jig
  work.

## Controls

- Preserve evidence classes instead of converting all evidence into a single
  confidence label.
- Require first-party sources as the baseline and label fallback evidence.
- Keep local observations scoped by version, environment, and artifact
  disposition.
- Route schema changes through schema pressure, migration expectations,
  validation updates, and review.
- Keep lifecycle dispositions separate from profile claim statuses until schema
  work explicitly changes that contract.
- Record authority, side effects, applicability scope, and failure modes for
  hook, MCP/tool, plugin, permission, sandbox, approval, and automation claims.
- Treat future jig evidence as unavailable unless runner, driver, suite, and
  adequacy evidence exist.
- Classify scratch artifacts before committing or publishing summaries.
- Use Story Closeout security, documentation, Cross-Boundary Coherence Ralph
  Review, and Story Quality Ralph Review before merge-readiness.

## Mutation gates

The issue #62 design package is non-mutating beyond repository documentation
and GitHub issue projection.

Later implementation must require explicit gates for:

- candidate artifact write and promotion;
- profile dry-run, diff, apply, and audit;
- schema field addition, migration, and fixture updates;
- local observation or controlled study execution;
- future jig execution and result promotion;
- recurring refresh installation or automation.

Profile updates, issue writes, PR body updates, release notes, and handoffs are
projection actions owned by Codex, Issue Tracker Ops, Manager Core workflows,
or closeout. They are not hidden side effects of candidate discovery.

## Evidence durability

Durable project evidence may include accepted design docs, profile schema docs,
curated Study Reports, curated schema pressure reports, issue projection, PR
bodies, reviewed closeout summaries, and public-safe issue comments.

Instance-scoped scratch includes raw terminal transcripts, local absolute
paths, raw source caches, raw logs, raw model outputs, raw hook input payloads,
screenshots, audio, video, copied fixture directories, local harness configs,
temporary worktrees, and scan artifacts unless explicitly promoted with
durability and disclosure rationale.

## Current security closeout

The current change set is doc-only. No executable code, schema implementation,
hook, MCP/tool, Config, automation, package metadata, permission policy, or
local harness invocation is added.

Security review still applies because the methodology shapes future claims
about hooks, permissions, sandboxing, MCP/tools, plugins, automation, local
observations, and evidence publication. The required closeout is a
threat-model and security-policy review against this classification and the
repository threat model, plus a secrets/disclosure scan over the changed docs.

## Residual risk

The main residual risk is future overimplementation: an agent could implement
candidate artifacts, profile mutation, and automation in one broad slice before
the schema, security, and validation gates are stable. The issue projection and
TDD requirement are the controls that keep future work narrow.
