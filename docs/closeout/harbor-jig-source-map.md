# Harbor Jig Source Map

Status: Source Disposition Ledger

## Scope Boundary

This ledger captures source-backed Harbor concepts for issue
[#184](https://github.com/nisavid/agent-armory/issues/184). It maps Harbor's
published evaluation vocabulary to current Armory Agent Test Jig and Harness
Capability lifecycle vocabulary so later Harbor issues can evaluate fit without
treating Harbor marketing language as accepted Armory architecture.

This ledger does not select Harbor as a Jig Driver, implement a Harbor
prototype, accept Reward Kit as an Assertion Provider or Learned Oracle, revise
ADR 0022, or change the Agent Test Jig design bundle. Those decisions belong
to downstream issues after their own evidence, security, validation, and review
gates.

## Portable Source Inventory

All sources were checked on 2026-06-01. Firecrawl extraction output was
instance-scoped scratch evidence. Durable project evidence is the source URL
set and the curated conclusions in this ledger.

| source_id | source identity | evidence class | retained use |
| --- | --- | --- | --- |
| HJ001 | [Harbor Core Concepts](https://www.harborframework.com/docs/core-concepts) | documentation-supported | Harbor definitions for task, dataset, agent, environment, trial, and job. |
| HJ002 | [Harbor Task Structure](https://www.harborframework.com/docs/tasks) | documentation-supported | Task format surfaces for environment, verifier, resources, setup/test scripts, and network policy. |
| HJ003 | [Harbor Datasets](https://www.harborframework.com/docs/datasets) | documentation-supported | Dataset collection, local dataset, published dataset, registry, and custom metrics context. |
| HJ004 | [Harbor Run Evals](https://www.harborframework.com/docs/run-jobs/run-evals) | documentation-supported | Job execution commands and job/trial result files, including `result.json`, `trajectory.json`, verifier output, and reward output. |
| HJ005 | [Harbor Results and Artifacts](https://www.harborframework.com/docs/run-jobs/results-and-artifacts) | documentation-supported | Artifact collection modes, `manifest.json`, best-effort collection, and provider-specific artifact handling. |
| HJ006 | [Harbor Reward Kit](https://www.harborframework.com/docs/rewardkit) | documentation-supported | Verifier and criteria model, reward JSON outputs, scoring aggregation, workspace access, trajectory access, and isolation notes. |
| HJ007 | [Harbor Judge Criteria](https://www.harborframework.com/docs/rewardkit/judge-criteria) | documentation-supported | LLM judge, agent judge, TOML criteria configuration, provider routing, file access, and cost/time boundaries. |
| HJ008 | [Harbor Cloud Sandboxes](https://www.harborframework.com/docs/run-jobs/cloud-sandboxes) | documentation-supported | Cloud sandbox provider model, provider list, network restrictions, and multi-container support limits. |
| HJ009 | [Harbor ATIF RFC](https://github.com/harbor-framework/harbor/blob/main/rfcs/0001-trajectory-format.md) | source-supported | ATIF trajectory purpose, JSON record shape, fields such as `schema_version`, `agent`, and `steps`, and open trajectory-format questions. |
| HJ010 | [Harbor repository agent instructions](https://github.com/harbor-framework/harbor/blob/main/AGENTS.md) | source-supported | Repository-level statement that Harbor evaluates and optimizes agents and language models, runs benchmark tasks, and uses ATIF trajectories. |
| HJ011 | [Opik Harbor integration](https://www.comet.com/docs/opik/integrations/harbor) | third-party fallback | Fallback evidence that Harbor integrations can expose trial traces, trajectory steps, tool calls, token usage, and costs through ATIF-derived observability. |

## Harbor-To-Armory Concept Map

| Harbor concept | Source-backed Harbor claim | Armory mapping | Fit boundary or uncertainty |
| --- | --- | --- | --- |
| task | A Harbor task is a single instruction, container environment, and test script used to evaluate agents and models. Source: HJ001, HJ002. | Partial overlap with **Jig Test Plan** scenario content because both name stimulus, environment, and expected verification behavior. | Harbor task format is not an Armory Jig Test Plan. It is source material for later schema comparison, not an accepted runner input. |
| dataset | A Harbor dataset is a collection of tasks for evaluation, local runs, registry runs, and custom metrics. Source: HJ001, HJ003. | Overlaps **Harness Test Suite** only at the grouped-case level. | Harbor dataset metrics are not yet Armory Harness Capability lifecycle evidence. Later work must decide whether metrics can support a **Study Report**. |
| agent | Harbor agents are programs that complete tasks, implemented through Harbor agent interfaces or installed-agent routes. Source: HJ001, HJ010. | Maps to the target under test or installed harness/equipment participant inside an **Agent Test Jig**. | Harbor's agent is not Armory's glossary **Agent** in full. Armory uses Agent for a causal reasoning/action stream mediated by a harness, so this row keeps the term scoped to Harbor. |
| environment | Harbor environments are container environments, typically Docker images, with a unified environment interface and cloud provider options. Source: HJ001, HJ002, HJ008. | Strong overlap with **Jig Driver** responsibilities for environment preparation, target exposure, process execution, observation, cleanup, and effect control. | Overlap does not prove Harbor is an acceptable first Jig Driver. ADR 0022 still defers driver selection. |
| verifier | Harbor task and Reward Kit verifier surfaces run checks and produce reward outputs. Source: HJ002, HJ006, HJ007. | Overlaps **Assertion Provider** when checks are deterministic and typed. Overlaps **Learned Oracle** only when judge criteria use LLM or agent judges. | Harbor verifier outputs need typed result, provenance, calibration, and tamper-resistance review before Armory can consume them as assertion results. |
| trial | A Harbor trial is an agent attempt at completing a task and produces reward/output files. Source: HJ001, HJ004. | Maps to a **Jig Runner** scenario attempt result and may contribute observations to a **Study Report**. | Harbor trial semantics are not identical to Armory result statuses such as `inconclusive`, `disagreement`, `oracle_error`, or `flaky`. |
| job | A Harbor job is a collection of trials and may span multiple datasets, agents, tasks, and models. Source: HJ001, HJ004. | Maps loosely to a **Harness Test Suite** run or a batch of Jig Runner scenario attempts. | Harbor job aggregation is not itself a **Jig Adequacy Report** or Harness Capability lifecycle decision. |
| Reward Kit | Reward Kit defines and runs verifiers with criteria, reward JSON outputs, reward-details JSON outputs, scoring weights, workspace access, trajectory access, and optional isolation. Source: HJ006. | Candidate input for later **Assertion Provider** and **Learned Oracle** evaluation in #188. | Reward Kit can modify workspaces through criteria unless isolated. It must be reviewed for verifier/reward tampering and result provenance before any adoption. |
| judge criteria | Harbor judge criteria can use LLM judges, agent judges, and per-criterion calls configured through TOML. Source: HJ007. | Candidate **Learned Oracle** input because judge criteria can perform inference-backed evaluation. | Agent judges may execute commands and access files, so they carry process, cost, provider, and auth boundaries that deterministic Assertion Providers do not. |
| ATIF trajectory | Harbor's ATIF RFC describes a JSON-based trajectory format for logging autonomous-agent interaction history, with fields such as `schema_version`, `agent`, and `steps`. Source: HJ009. | Potential evidence input for **Jig Runner** trajectory assertions, **Study Report** observations, and later artifact analysis in #189. | Exact required fields, compatibility, nested-agent semantics, and metric semantics need issue #189 evidence before Armory treats ATIF as a stable result contract. |
| artifacts | Harbor jobs and trials emit files such as job `result.json`, trial `result.json`, `trajectory.json`, verifier `reward.txt`, verifier stdout/stderr, recordings, and collected artifacts with `manifest.json`. Source: HJ004, HJ005. | Overlaps **Jig Runner** structured result artifacts and **Capability Profiling Protocol** artifact disposition. | Harbor artifact collection is best-effort, so missing artifacts cannot silently pass Armory evidence sufficiency checks. |
| scoring | Harbor and Reward Kit use reward outputs, reward JSON files, weighted criteria, custom metrics, and aggregated scores. Source: HJ003, HJ004, HJ006. | May inform **Study Report** confidence or suite summaries after normalization. | Scoring is not the same as an Armory assertion status. Weighting, calibration, and failure provenance remain open. |
| cloud sandbox | Harbor can scale containerized tasks across providers such as Daytona, Modal, E2B, Runloop, Tensorlake, Islo, CoreWeave Sandboxes, and W&B Sandboxes. Source: HJ008. | Candidate **Jig Driver** or supporting driver backend evidence for #190. | Provider capabilities differ. Daytona internet restrictions and limited multi-container support are known fit risks. |
| network policy | Harbor tasks include network policy configuration, and sandbox providers have provider-specific network behavior. Source: HJ002, HJ008. | Maps to **Jig Driver** effect controls and Capability Profiling Protocol effect gates. | Network policy must be proven per provider before Harbor evidence can satisfy Armory isolation or external-disclosure controls. |
| artifact handling | Harbor supports convention-directory and config-driven artifact collection, creates artifact manifests, and treats collection as best-effort. Source: HJ005. | Maps to **Jig Runner** artifact policy and **Capability Profiling Protocol** artifact disposition. | Best-effort collection means artifact absence may be infrastructure evidence, not task failure evidence. Later work must preserve this distinction. |
| verifier/reward tampering | Reward Kit criteria can interact with and potentially modify the workspace unless isolation is used. Source: HJ006, HJ007. | Security input for **Assertion Provider**, **Learned Oracle**, and **Jig Driver** evaluation. | Armory must separate verifier workspace writes from target behavior and must not accept reward output without tamper-boundary review. |
| auth/provider boundaries | Harbor judge/provider routes, agent judges, cloud sandbox providers, registry access, and third-party observability integrations all cross provider or auth boundaries. Source: HJ003, HJ007, HJ008, HJ011. | Security and control input for **Jig Driver**, **Learned Oracle**, and Harness Capability lifecycle evidence. | Third-party Opik facts are fallback only. Provider auth and cost boundaries need first-party or implementation evidence before adoption. |

## Risks And Open Issues

- Harbor task, dataset, job, and trial vocabulary overlaps Armory jig
  vocabulary but does not replace it. The safe current use is source mapping,
  not schema adoption. Sources: HJ001, HJ004.
- Network policy is provider-dependent. Daytona internet restrictions and
  multi-container limits need driver-gate evidence before Harbor can support
  an Armory Jig Driver claim. Sources: HJ002, HJ008.
- Artifact handling is best-effort. Later **Jig Runner** and **Study Report**
  consumers must distinguish task failure, verifier failure, sandbox failure,
  and artifact collection failure. Sources: HJ004, HJ005.
- ATIF trajectory is promising for trajectory assertions, but nested-agent
  semantics, metric semantics, and required-field stability remain open.
  Sources: HJ009, fallback HJ011.
- Reward Kit can provide deterministic and judge-based verifier evidence, but
  verifier/reward tampering, workspace mutation, isolation, judge calibration,
  and score weighting remain open. Sources: HJ006, HJ007.
- Auth/provider boundaries span Harbor Hub or registry access, cloud sandbox
  providers, LLM judge providers, agent judge execution, and observability
  integrations. Sources: HJ003, HJ007, HJ008, fallback HJ011.

## Downstream Routing

| route | accepted input from this ledger | not owned here |
| --- | --- | --- |
| [#183](https://github.com/nisavid/agent-armory/issues/183) | Parent Harbor evaluation can use this as the first source-backed vocabulary map. | Final Harbor disposition. |
| [#185](https://github.com/nisavid/agent-armory/issues/185) | External-tool evaluation pipeline should start from the source/uncertainty split in this ledger. | Pipeline architecture and human design decision. |
| [#186](https://github.com/nisavid/agent-armory/issues/186) | Neighbor-tool catalog can compare other tools against the same task, dataset, trial, job, verifier, artifact, and provider-boundary axes. | Catalog contents and non-Harbor research. |
| [#187](https://github.com/nisavid/agent-armory/issues/187) | Prototype work can use the mapped task, dataset, agent, trial, job, environment, verifier, artifact, and scoring surfaces as prototype inputs. | Running Harbor or building the A/B test. |
| [#188](https://github.com/nisavid/agent-armory/issues/188) | Reward Kit and judge criteria rows identify Assertion Provider and Learned Oracle questions. | Reward Kit adoption or implementation. |
| [#189](https://github.com/nisavid/agent-armory/issues/189) | ATIF trajectory and artifact rows identify Jig Runner result and artifact questions. | ATIF schema validation, artifact ingestion, or result contract changes. |
| [#190](https://github.com/nisavid/agent-armory/issues/190) | Environment, cloud sandbox, network policy, and provider-boundary rows feed the Jig Driver gate. | Driver selection or ADR 0022 revision. |
| [#191](https://github.com/nisavid/agent-armory/issues/191) | Final projection can cite this ledger as source-map evidence when deciding Harbor fit. | Final disposition, issue updates, or doc projection. |

## Deferments And Nonportable Claims

- No Harbor prototype, benchmark run, cloud sandbox job, registry operation,
  Reward Kit execution, Opik integration, or local Harbor install is accepted
  by this issue.
- Harbor docs and source are retained as evidence, not as Armory normative
  vocabulary. Existing Armory glossary terms remain sufficient for #184.
- The Opik integration source is third-party fallback evidence. It can inform
  questions about ATIF observability, tool calls, token usage, and cost
  aggregation, but it does not prove Harbor's first-party contract.
- Raw Firecrawl responses, scrape IDs, cache metadata, and extraction prompts
  are instance-scoped scratch evidence.
- No local paths, local environment state, provider credentials, benchmark
  outputs, or cloud account details are durable project evidence for this
  issue.

## Security Privacy And Durability

This change set records a documentation ledger and a structural Markdown
validator. It introduces no Harbor execution, subprocess invocation, cloud
sandbox operation, registry write, credential handling, LLM provider call,
Opik integration, local filesystem mutation outside the committed doc, or
external disclosure beyond normal source retrieval and issue/PR projection.

Durable project evidence for #184 is this ledger, the PR diff, validation
output, security closeout summary, documentation closeout summary, and issue
projection. Portable review summaries may name the source URLs and curated
conclusions above. Instance-scoped scratch includes Firecrawl output, search
results, scrape metadata, local command output, and local worktree state.

Privacy boundaries:

- Do not publish raw scrape output, local cache state, local paths, credentials,
  cloud provider account state, Harbor Hub auth state, or Opik project state.
- Do not treat collected Harbor artifacts or trajectories as project truth
  unless a downstream issue promotes sanitized fixtures or durable evidence.
- Keep source-backed claims tied to URLs and uncertainty notes because Harbor
  behavior, provider support, and docs can drift.

## Closeout Evidence

Triage result: issue #184 remained `enhancement`, `ready-for-agent`,
`kind:research`, `mode:afk-implementation`, and `dependency:unblocked` when
work began. Live dependency reads showed no blockers and showed #184 blocking
#185, #186, #187, #188, and #190.

Grill-with-docs result: no interactive grill was needed for #184. The source
evidence fits existing Armory vocabulary, and no new glossary term or ADR is
introduced by this ledger.

Prototype result: non-applicable for #184. Issue #187 owns the Harbor Agent
Equipment A/B test prototype.

Impeccable result: non-applicable for #184 because this is not a frontend or
product UI change.

TDD result: Armory Integrity Validation guards this ledger's path, status,
required sections, required Harbor and Armory coverage terms, downstream issue
routes, and host-local path rejection.

Security closeout: the change set adds a portable documentation ledger and
structural validation over one repository-relative Markdown path. The validator
uses existing path-status, Markdown-heading, link-search, route-token, and
host-local-path checks. It adds no new dynamic file selection, writes,
subprocess execution, network calls, secret handling, or untrusted path inputs.

Documentation closeout: this ledger is the committed documentation change for
issue #184. The repository documentation map remains reader-oriented and does
not list issue-specific closeout ledgers; downstream routing is captured here
and in issue projection.

Ralph review closeout: Cross-Boundary Coherence `Ralph Review Cycle 1` found
no findings. Story Quality `Ralph Review Cycle 1` found no findings after
checking validator locality, test robustness, security and privacy boundaries,
documentation fit, downstream routing, and Armory Vision alignment.
