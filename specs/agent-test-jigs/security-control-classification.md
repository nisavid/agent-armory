# Security and Control Classification: Agent Test Jigs

Status: Equipment Blueprint
Promotion state: specified

## Scope

This classification covers the Agent Test Jig design package for issue #61:
Jig Test Plans, Jig Runner, Jig Drivers, Assertion Providers, Learned Oracles,
local inference service integration, result artifacts, and Codex disagreement
handoff. It does not certify a runner, driver, schema validator, inference
service, or harness test suite implementation.

## Assets

- Local repository files, worktrees, fixtures, caches, and generated results.
- User home directories, harness configuration, credentials, tokens, and local
  model service endpoints.
- Agent prompts, transcripts, tool traces, screenshots, audio, video, and raw
  model outputs.
- GitHub Issues, PR bodies, review comments, and other external projection
  surfaces.
- Harness Capability Profiles, Study Reports, Jig Adequacy Reports, and later
  durable capability evidence.

## Trust boundaries

- Agent-authored Jig Test Plans to deterministic runner validation.
- Runner to driver lifecycle and effect controls.
- Driver to host filesystem, processes, network, and harness state.
- Runner to local inference service.
- Learned Oracle outputs to Codex adjudication.
- Scratch evidence to durable docs, PRs, issues, or profile updates.
- Future config layers to driver selection, assertion thresholds, and provider
  endpoints.

## Side effects

| Side effect | Classification | Control expectation |
| --- | --- | --- |
| Fixture reads | Read-only | Root-relative path and symlink controls. |
| Fixture writes | Local write | Approved fixture root and cleanup evidence. |
| Harness execution | Process execution | Driver lifecycle contract and captured command metadata. |
| Network probing | External network access | Explicit allowed effect and network policy record. |
| Local inference calls | Process or network access | Host-side endpoint allowlist and structured request logs. |
| Result publication | External disclosure | Evidence durability classification before projection. |
| Profile mutation | Local write | Out of scope for #61; later profile manager gates apply. |

## Threats

- Prompt injection in fixture content steers an Agent or Learned Oracle into
  leaking secrets or trusting malicious evidence.
- A test plan references host-local paths, symlinks, caches, or credentials
  outside the fixture boundary.
- A driver claims isolation that it does not enforce.
- A mock service or harness process remains running after cleanup.
- A Learned Oracle produces a confident but wrong pass and hides disagreement.
- Raw logs or model transcripts are committed or posted to GitHub as durable
  truth without disclosure review.
- A future runner invokes network or process effects because a prose plan
  implied permission rather than requiring structured approval.

## Controls

- Driver-selection rubric before first implementation.
- Structured effect declarations and approval references for effectful runs.
- Root-relative fixture paths, symlink rejection, and explicit scratch
  disposition in later validators.
- Result statuses that distinguish `fail`, `inconclusive`, `disagreement`,
  `oracle_error`, `infra_error`, `fixture_error`, `sandbox_error`, `timeout`,
  and `flaky`.
- Weakest reliable oracle policy for assertions.
- Local inference service metadata for model, prompt, threshold, sampling,
  input hash, cache, timeout, evidence, and error behavior.
- Codex high-thinking adjudication for unresolved Learned Oracle disagreement.
- Change Set Security Closeout and Story Closeout before merge readiness.

## Mutation gates

The design package is non-mutating beyond repository documentation edits and
issue projection. Later executable work must fail closed for effectful behavior
unless the Jig Test Plan, driver policy, and operator approval all allow the
effect.

Profile updates, issue writes, PR body updates, release notes, and handoffs are
not runner side effects. They are separate projection actions owned by Codex,
Issue Tracker Ops, or closeout surfaces after evidence durability is classified.

## Evidence durability

Durable project evidence may include accepted design docs, ADRs, issue
projection, PR summaries, reviewed Study Reports, Jig Adequacy Reports, and
curated result summaries. Instance-scoped scratch includes raw runner output,
local paths, model transcripts, screenshots, videos, audio, copied fixture
directories, cache contents, and temporary worktrees unless explicitly promoted
with review.

## Residual risk

The largest residual risk is that later implementation treats this design as
stronger isolation than the selected driver can provide. The driver ADR gate
and result status model are the controls that keep that risk visible.
