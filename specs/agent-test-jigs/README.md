# Agent Test Jigs and Harness Testing System

Status: Equipment Blueprint
Promotion state: specified

This Equipment Design Bundle records the accepted design package for issue
[#61](https://github.com/nisavid/agent-armory/issues/61). It specifies Agent
Test Jigs, the Harness Testing System shape, and the first driver gate without
implementing a runner, driver, schema validator, assertion provider, local
inference adapter, or harness test suite.

The AI assertion layers source handoff is retained as design guidance for
assertion families, model allocation, calibration, and disagreement handling.
It is not a final API contract and should not be copied wholesale into runner
implementation.

## Bundle map

- [Capability card](capability-card.md)
- [Interface decision record](interface-decision-record.md)
- [Security and control classification](security-control-classification.md)
- [Pressure scenarios](pressure-scenarios.md)
- [Validation plan](validation-plan.md)
- [Closeout evidence plan](closeout-evidence-plan.md)
- [Driver ADR](../../docs/adr/0022-defer-agent-test-jig-driver-selection.md)

## Purpose

Agent Test Jigs give Smiths and future harness lifecycle work a controlled way
to exercise Agent Harnesses, Agent Equipment, Loadouts, and interactions before
the Armory relies on their Capability Surface claims in larger workflows.

The design package keeps a strict boundary between:

- the controlled environment and lifecycle backend, the **Jig Driver**;
- the orchestration layer that loads plans and emits results, the **Jig
  Runner**;
- grouped validation for Harness Capability claims, the **Harness Test Suite**;
- deterministic and learned condition evaluation, the **Assertion Provider**;
- inference-backed assertions, the **Learned Oracle**.

Do not use `harness` for the jig itself. An Agent Harness is the runtime or
orchestration system being strapped; an Agent Test Jig is the controlled place
or mechanism where that runtime, equipment, Loadout, or interaction is tested.

## Accepted scope

This issue specifies the design package and creates implementation follow-up
work. It does not ship executable jig behavior.

Accepted in this package:

- glossary updates for the new jig terms;
- architecture and interface boundaries for runner, driver, assertions,
  inference service, results, and Codex handoff;
- a driver-selection rubric applied to the first candidate set;
- an ADR that defers first driver selection until the implementation gate;
- pressure scenarios and validation expectations for the later executable
  work.

Deferred to follow-up issues:

- TOML schema validator and example fixture corpus;
- a standard-library Jig Runner CLI;
- first Jig Driver implementation;
- deterministic assertion library;
- local inference service adapter and Learned Oracle providers;
- Harness Test Suite integration for Harness Capability lifecycle work;
- any review UI, static report viewer, browser workflow, or frontend surface.

## Architecture

### Jig Test Plan

A Jig Test Plan is the machine-readable input to a Jig Runner. The preferred
direction is a declarative TOML behavioral spec because the Armory already uses
TOML for human-authored structured equipment surfaces and because the
`arch-strix-halo-pkgs` inference scenario catalog shows a compact local example
of scenario-shaped TOML.

The plan shape should stay close to behavior:

- target: the harness, equipment, Loadout, interaction, or Capability Surface
  under test;
- driver constraints: isolation, permitted effects, network policy, fixture
  paths, process controls, cleanup expectations, and observation needs;
- scenario: setup, stimulus, expected state transition, captured outputs, and
  timeout or budget constraints;
- assertions: deterministic checks first, Learned Oracle checks only when the
  weaker reliable oracle cannot decide;
- artifact policy: which logs, traces, snapshots, model outputs, and reports
  remain scratch and which may become durable evidence.

Inline snippets may be useful for tiny fixtures, but referenced scripts are the
normal path when code is intrinsic to the test case. The spec language should
not turn into a general imperative workflow language.

### Jig Runner

The Jig Runner owns orchestration, not environment mechanics or judgment. It:

- loads and validates Jig Test Plans;
- resolves target and fixture references relative to the repository or an
  approved fixture root;
- selects a Jig Driver through explicit selection or policy;
- executes scenarios through the driver lifecycle interface;
- invokes Assertion Providers;
- writes structured result output for Codex and later equipment;
- preserves failure provenance without treating prose summaries as the contract.

The runner must not silently downgrade missing controls. Unsupported or unknown
driver controls remain visible in structured output and affect selected rigor.

### Jig Driver

A Jig Driver is a registered backend. The first implementation contract should
cover:

- prepare environment;
- install, mount, or expose target material;
- configure harness and equipment state;
- execute scenario operations;
- observe stdout, stderr, exit codes, logs, traces, artifacts, state snapshots,
  resource usage, and attempted external effects;
- restrict filesystem, network, process, and external disclosure effects;
- clean up and report cleanup failures.

Driver selection is deferred by
[ADR 0022](../../docs/adr/0022-defer-agent-test-jig-driver-selection.md). The
rubric below is the accepted gate for selecting the first driver.

### Assertion Providers

Assertion Providers return typed results. A bare boolean is insufficient.

Deterministic providers cover exact, normalized, contains, excludes, regex,
edit distance, JSON or schema shape, numeric tolerance, temporal tolerance,
state delta, tool-call presence and arguments, trajectory, safety or policy,
and performance or budget checks.

Learned Oracles are inference-backed Assertion Providers. They must be
structured, versioned, calibrated, auditable, and allowed to return
`inconclusive`, `disagreement`, or `oracle_error`. The runner must prefer the
weakest reliable oracle and must not use LLM or VLM judges when deterministic
or specialized checks can decide the condition.

Initial model-allocation guidance:

- use `zembed-1` for semantic similarity, candidate lookup, clustering, and
  recall-oriented prefiltering, not as a final correctness oracle;
- use `zerank-2` for criterion satisfaction, retrieval relevance, and stronger
  candidate scoring when the condition can be phrased as query plus document;
- use `cross-encoder/nli-deberta-v3-large` for short atomic entailment,
  contradiction, neutral, and mutual-entailment checks;
- use Qwen3.6 35B A3B as the primary local text reasoner for complex rubrics,
  long traces, causal or temporal reasoning, tool-use reasoning, claim
  decomposition, and adjudicating ambiguous specialized outputs;
- use Gemma 4 primarily for multimodal extraction into structured evidence,
  then apply deterministic checks or Qwen reasoning over that extracted
  evidence;
- use Qwen3.5 as a cheaper baseline, fallback, or challenger judge when
  independence from the system under test is useful.

Thresholds must be calibrated per model, model version, runtime, prompt or
rubric version, assertion type, domain, language, answer length, scenario type,
modality, and desired error profile. One global semantic, reranker, or judge
threshold is not an accepted design.

### Local inference service

Learned Oracles call a host-side local inference service rather than embedding
model-specific behavior in the runner. The service boundary should expose
strict request and response schemas for:

- `POST /embed`
- `POST /semantic-similarity`
- `POST /rerank`
- `POST /nli`
- `POST /judge/text`
- `POST /extract/image`
- `POST /extract/audio`
- `POST /extract/video`
- `POST /judge/multimodal`

Requests and responses record model names, model versions, prompt versions,
threshold or calibration profiles, sampling parameters, normalized input
hashes, raw or redacted evidence disposition, runtime version, cache behavior,
timeout behavior, and structured errors.

### Structured result contract

Result statuses are first-class values:

- `pass`
- `fail`
- `inconclusive`
- `disagreement`
- `oracle_error`
- `infra_error`
- `fixture_error`
- `sandbox_error`
- `timeout`
- `flaky`

Each result records scenario identity, selected jig and driver, environment,
target, steps, captured outputs, assertions, attempted external effects,
resource usage, model or prompt metadata where applicable, and recommended
durable repo updates. Prose summaries may be emitted for humans, but
machine-readable structured output is the contract.

### Codex disagreement handoff

The runner does not arbitrate unresolved Learned Oracle disagreements. It
returns disagreement records to Codex with the scenario, rubric, expected value,
actual output, trace, evidence, and all oracle outputs. Codex then delegates to
a fresh latest-GPT high-thinking subagent and records adjudication without
hiding the original disagreement evidence.

## Driver gate

The first implementation issue must apply this rubric before selecting a
driver:

| Criterion | What to examine |
| --- | --- |
| Safety | Whether the driver prevents unintended writes, disclosures, and host-state changes. |
| Isolation from host state | Home, repo, config, credentials, caches, processes, and network separation. |
| Reproducibility | Version pinning, fixture control, deterministic setup, and cleanup repeatability. |
| Simplicity | How much code and operator setup is needed for a useful first slice. |
| Local iteration speed | Whether Smiths can run a small scenario quickly during design and repair. |
| Observability | Captured stdout, stderr, logs, traces, state snapshots, effects, and resource use. |
| Effect controls | Filesystem, network, process, external disclosure, and cleanup controls. |
| Fixture and mock support | How fixtures, mock services, fake homes, and test data are mounted or started. |
| Cleanup reliability | Whether partial failures leave visible residue and recoverable state. |
| Portability | Fit across Codex, OpenClaw, Hermes Agent, local shells, and later CI. |
| Codex workflow compatibility | Whether Codex can invoke it, parse results, and route follow-up safely. |
| Maintenance cost | Ongoing burden of dependencies, privileged setup, and platform assumptions. |

Initial candidate dispositions:

| Candidate | Strengths | Limits | Gate disposition |
| --- | --- | --- | --- |
| OpenClaw approach | Source-backed harness with cron, heartbeat, hooks, background services, and plugin surfaces worth studying. | It is itself a harness, not automatically the Armory's generic driver backend. | Research reference before copying any driver model. |
| Hermes Agent approach | Source-backed harness with cron, gateway, plugin hooks, and worker flows worth comparing. | Harness-specific lifecycle and gateway assumptions may not fit Codex-mediated local runs. | Research reference before copying any driver model. |
| Codex sandbox/local execution | Current working harness, approvals, worktrees, and local tooling already available. | Sandbox semantics vary by session, and Codex should not be both unexamined investigator and hidden target. | Likely first consumer path, not sufficient as an unreviewed driver choice. |
| Containers | Strong filesystem and process isolation with familiar cleanup boundaries. | Setup, privilege, GPU/inference access, and nested harness behavior may be heavy. | Candidate for high-rigor driver. |
| Process sandbox | Fast local execution and low implementation cost. | Weak isolation unless paired with explicit filesystem, network, and credential controls. | Candidate for first thin driver only if limits are explicit. |
| Temporary worktrees | Excellent repo-state isolation and diff review. | Does not isolate home, network, credentials, or external processes by itself. | Supporting control, not a complete driver. |
| Ephemeral directories | Simple fixture and output isolation. | Does not isolate global state or process effects by itself. | Supporting control, not a complete driver. |
| Mock service processes | Good for API, MCP, or network boundary tests. | Requires lifecycle supervision and port/network controls. | Supporting driver component. |
| Network policy restrictions | Essential for disclosure and external-effect claims. | Platform-specific and insufficient without process and filesystem boundaries. | Required control axis for effectful drivers. |
| Hybrid local driver | Can combine temp dirs, worktrees, mock services, process controls, and optional network policy. | Needs careful contract to avoid pretending it is stronger than its parts. | Strong first implementation candidate after the gate. |

## Developer UX direction

The spec language and reports are product-style tool surfaces. Because this
repo does not define `PRODUCT.md` or `DESIGN.md`, #61 adopts the existing
Armory docs as the source of product intent and keeps visual work out of scope.

Design rules for later UI, report, or review surfaces:

- keep the primary reviewer task visible first;
- group decisions into no more than four visible choices per decision point;
- use domain terms from `CONTEXT.md` consistently;
- prefer familiar tabs, sections, tables, and summaries over invented
  affordances;
- use specific action labels and error messages;
- keep raw logs behind explicit disclosure rather than making them the default
  review surface.

## Downstream routing

Follow-up issues are listed in dependency order where practical. Native issue
dependencies remain authoritative for blocked work:

- [#162](https://github.com/nisavid/agent-armory/issues/162): Jig Test Plan
  TOML schema and example fixtures;
- [#163](https://github.com/nisavid/agent-armory/issues/163): first Jig Driver
  implementation selected by the gate;
- [#165](https://github.com/nisavid/agent-armory/issues/165): deterministic
  Assertion Provider library;
- [#164](https://github.com/nisavid/agent-armory/issues/164): Jig Runner CLI
  and structured result output;
- [#166](https://github.com/nisavid/agent-armory/issues/166): local inference
  service adapter and Learned Oracle providers;
- [#167](https://github.com/nisavid/agent-armory/issues/167): Harness Test
  Suite integration for Harness Capability lifecycle work;
- [#168](https://github.com/nisavid/agent-armory/issues/168): Codex
  disagreement adjudication workflow;
- [#169](https://github.com/nisavid/agent-armory/issues/169): optional review
  report or static viewer only after result artifacts exist.

Issue #62 should consume this bundle before making claims about local
validation, capability testing, Learned Oracle providers, Harness Test Suites,
or driver-backed execution.
