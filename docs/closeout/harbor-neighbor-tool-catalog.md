# Harbor-Neighbor Tool Catalog

Status: Source Disposition Ledger

## Scope Boundary

This catalog records Harbor-linked neighbor tools and surfaces only. Broad
eval-platform survey work is out of scope. A tool or surface belongs here only
when Harbor docs, Harbor repository source, or a fallback integration source
links it to Harbor's evaluation, sandbox, reward, trajectory, dataset,
observability, or training/export surface.

This catalog is not a Harbor adoption decision, prototype result, Agent Test
Jig driver selection, Reward Kit acceptance, ATIF result contract, or final
external-tool evaluation disposition.

## Portable Source Inventory

| source | evidence quality | accepted use |
| --- | --- | --- |
| <https://www.harborframework.com/docs/run-jobs/cloud-sandboxes> | harbor-doc-supported | Harbor cloud sandbox provider list and multi-container support notes. |
| <https://www.harborframework.com/docs/core-concepts> | harbor-doc-supported | Harbor task, dataset, agent, environment, trial, job, and cloud-runtime vocabulary. |
| <https://www.harborframework.com/docs/run-jobs/results-and-artifacts> | harbor-doc-supported | Result tree, artifact collection, artifact visibility, and provider caveats. |
| <https://www.harborframework.com/docs/rewardkit> | harbor-doc-supported | Reward Kit as Harbor's reward and verifier surface. |
| <https://www.harborframework.com/docs/rewardkit/judge-criteria> | harbor-doc-supported | Judge criteria and LiteLLM provider routing context. |
| <https://www.harborframework.com/docs/tutorials/llm-as-a-judge> | harbor-doc-supported | LLM-as-judge cost, key, and reward configuration context. |
| <https://www.harborframework.com/docs/tasks> | harbor-doc-supported | Task verifier, reward.txt, reward.json, and network-policy context. |
| <https://github.com/harbor-framework/harbor/blob/main/rfcs/0001-trajectory-format.md> | harbor-source-supported | ATIF trajectory format, metrics, tool-call, and training/export motivation. |
| <https://www.harborframework.com/docs/datasets> | harbor-doc-supported | Harbor registry, local datasets, published datasets, and dataset structure. |
| <https://www.harborframework.com/docs/datasets/publishing> | harbor-doc-supported | dataset.toml, task pointers, registry publication, and dataset visibility. |
| <https://www.harborframework.com/docs/run-jobs/run-evals> | harbor-doc-supported | Registered benchmarks, Terminal-Bench, SWE-Bench Verified, result viewer, and benchmark results. |
| <https://www.harborframework.com/docs/datasets/adapters-human> | harbor-doc-supported | adapter templates, compatible agents, Hugging Face parity experiments, SkyRL, and GEPA context. |
| <https://www.comet.com/docs/opik/integrations/harbor> | third-party-fallback | Opik fallback context for Harbor traces, trial results, ATIF steps, tool calls, observations, token usage, and cost. |

Evidence quality values used by this catalog are `harbor-doc-supported`,
`harbor-source-supported`, `vendor-doc-supported`, and `third-party-fallback`.
The vendor-doc-supported value remains available for directly reviewed vendor
documentation in downstream Harbor-linked work, but no first-party Harbor claim
in this catalog rests on vendor documentation.

## Harbor-Neighbor Tool Catalog

| entry_id | tool_or_surface | Harbor linkage | source URL | role classification | evidence quality | likely Armory consumer | open uncertainty |
| --- | --- | --- | --- | --- | --- | --- | --- |
| HN001 | Daytona | Harbor documents Daytona as a supported cloud sandbox provider and names it as supporting multi-container environments. | <https://www.harborframework.com/docs/run-jobs/cloud-sandboxes> | Jig Driver substrate; sandbox provider | harbor-doc-supported | #190 | Provider account policy, internet restrictions, and reproducibility constraints remain driver-gate questions. |
| HN002 | Modal | Harbor documents Modal as a supported cloud sandbox provider and describes artifact collection across Docker, Daytona, Modal, E2B, and Tensorlake environments. | <https://www.harborframework.com/docs/run-jobs/cloud-sandboxes>; <https://www.harborframework.com/docs/run-jobs/results-and-artifacts> | Jig Driver substrate; sandbox provider | harbor-doc-supported | #190 | Current Harbor docs do not make Modal a multi-container provider; driver gates must treat that as unproven. |
| HN003 | E2B | Harbor documents E2B as a supported cloud sandbox provider and includes it in artifact-collection behavior. | <https://www.harborframework.com/docs/run-jobs/cloud-sandboxes>; <https://www.harborframework.com/docs/run-jobs/results-and-artifacts> | Jig Driver substrate; sandbox provider | harbor-doc-supported | #190 | Account, isolation, network, and artifact limits need downstream driver validation. |
| HN004 | Runloop | Harbor documents Runloop as a supported cloud sandbox provider. | <https://www.harborframework.com/docs/run-jobs/cloud-sandboxes> | Jig Driver substrate; sandbox provider | harbor-doc-supported | #190 | Artifact handling and multi-container behavior are not established by the reviewed Harbor pages. |
| HN005 | Tensorlake | Harbor documents Tensorlake as a supported cloud sandbox provider and includes it in artifact-collection behavior. | <https://www.harborframework.com/docs/run-jobs/cloud-sandboxes>; <https://www.harborframework.com/docs/run-jobs/results-and-artifacts> | Jig Driver substrate; sandbox provider | harbor-doc-supported | #190 | Provider-specific auth, runtime parity, and artifact durability require downstream checks. |
| HN006 | Islo | Harbor documents Islo as a supported cloud sandbox provider and names it as supporting multi-container environments. | <https://www.harborframework.com/docs/run-jobs/cloud-sandboxes> | Jig Driver substrate; sandbox provider | harbor-doc-supported | #190 | The reviewed evidence does not settle Armory suitability, account availability, or result portability. |
| HN007 | CoreWeave Sandboxes | Harbor documents CoreWeave Sandboxes as a supported cloud sandbox provider. | <https://www.harborframework.com/docs/run-jobs/cloud-sandboxes> | Jig Driver substrate; sandbox provider | harbor-doc-supported | #190 | Multi-container support and artifact behavior are not proven by the reviewed Harbor pages. |
| HN008 | W&B Sandboxes | Harbor documents W&B Sandboxes as a supported cloud sandbox provider. | <https://www.harborframework.com/docs/run-jobs/cloud-sandboxes> | Jig Driver substrate; sandbox provider | harbor-doc-supported | #190 | Workspace, observability, and account-policy implications remain downstream driver-gate questions. |
| HN009 | Reward Kit | Harbor routes reward functions, verifiers, LLM-as-judge workflows, reward.txt, and reward.json through Reward Kit and related task configuration. | <https://www.harborframework.com/docs/rewardkit>; <https://www.harborframework.com/docs/tasks>; <https://www.harborframework.com/docs/tutorials/llm-as-a-judge> | verifier/assertion layer; trajectory/result format | harbor-doc-supported | #188 | Safety, tamper resistance, calibration, and acceptance as an Armory Assertion Provider remain unresolved. |
| HN010 | LiteLLM provider routing | Harbor judge criteria docs use LiteLLM model strings and provider routing for judge configuration. | <https://www.harborframework.com/docs/rewardkit/judge-criteria> | Agent or harness configurator; tool provider; verifier/assertion layer | harbor-doc-supported | #188 | Provider auth, cost, routing stability, and model-policy behavior need Reward Kit review. |
| HN011 | ATIF | Harbor repository source defines ATIF as an agent trajectory interchange format for steps, tool calls, observations, metrics, and SFT/RL-oriented reuse. | <https://github.com/harbor-framework/harbor/blob/main/rfcs/0001-trajectory-format.md> | trajectory/result format; observability/evaluation instrumentation; training/export surface | harbor-source-supported | #189 | Armory has not accepted ATIF as the Jig Runner result contract or artifact schema. |
| HN012 | Opik | Comet's Opik integration documents Harbor trace capture, trial results, ATIF steps, tool calls, observations, token usage, and cost. | <https://www.comet.com/docs/opik/integrations/harbor> | observability/evaluation instrumentation; tool provider | third-party-fallback | #189; #191 | This is fallback context only and does not prove Harbor's first-party contract or Armory acceptance. |
| HN013 | Harbor registry | Harbor docs describe local datasets, published datasets, a Harbor registry, registered benchmarks, and benchmark results. | <https://www.harborframework.com/docs/datasets>; <https://www.harborframework.com/docs/datasets/publishing>; <https://www.harborframework.com/docs/run-jobs/run-evals> | benchmark registry; benchmark format | harbor-doc-supported | #187; #191 | Registry account, visibility, and publication policy are not adoption decisions. |
| HN014 | dataset.toml and adapter templates | Harbor docs describe dataset.toml metadata, task pointers, and adapter templates for dataset conversion. | <https://www.harborframework.com/docs/datasets/publishing>; <https://www.harborframework.com/docs/datasets/adapters-human> | benchmark format; Agent or harness configurator; tool provider | harbor-doc-supported | #187; #191 | Per-benchmark mapping and compatibility with Armory stock surfaces require prototype and final projection work. |
| HN015 | result viewer | Harbor run-eval docs and result docs describe a local result viewer, Harbor view, result tree, artifacts, logs, metadata, and benchmark results. | <https://www.harborframework.com/docs/run-jobs/run-evals>; <https://www.harborframework.com/docs/run-jobs/results-and-artifacts> | observability/evaluation instrumentation; trajectory/result format | harbor-doc-supported | #189; #191 | The viewer is not yet an accepted durable evidence format for Armory closeout. |
| HN016 | Hugging Face parity experiments | Harbor adapter docs mention Hugging Face parity experiments in the adapter and dataset context. | <https://www.harborframework.com/docs/datasets/adapters-human> | training/export surface; benchmark registry | harbor-doc-supported | #191 | Publication, dataset provenance, and account boundaries remain final-disposition questions. |
| HN017 | SkyRL and GEPA | Harbor docs mention SkyRL and GEPA in the adapter and optimization context. | <https://www.harborframework.com/docs/datasets/adapters-human>; <https://www.harborframework.com/docs> | training/export surface; tool provider | harbor-doc-supported | #191 | Reviewed docs name the surfaces but do not establish an Armory adoption or integration path. |

## Role Classification Summary

The catalog supports these role classifications:

- Jig Driver substrate: Daytona, Modal, E2B, Runloop, Tensorlake, Islo,
  CoreWeave Sandboxes, and W&B Sandboxes.
- sandbox provider: the same cloud sandbox provider set.
- benchmark format: Harbor registry, dataset.toml, adapter templates, and
  registered benchmark surfaces.
- benchmark registry: Harbor registry, published datasets, registered
  benchmarks, benchmark results, and Hugging Face parity experiments.
- Agent or harness configurator: LiteLLM provider routing, dataset.toml, and
  adapter templates.
- tool provider: LiteLLM, Opik, adapter templates, SkyRL, and GEPA.
- observability/evaluation instrumentation: ATIF, Opik, result viewer, and
  artifact/result surfaces.
- verifier/assertion layer: Reward Kit, judge criteria, and LiteLLM-backed
  judge routing.
- trajectory/result format: ATIF, Reward Kit outputs where they affect result
  interpretation, result viewer, and artifact/result surfaces.
- training/export surface: ATIF, Hugging Face parity experiments, SkyRL, and
  GEPA.

These classifications are routing aids for #187 through #191. They do not
approve a provider, benchmark, judge, observability backend, training surface,
or Harbor adoption.

## Open Uncertainties And Follow-Up Conditions

- #187 owns prototype fit. This catalog may tell the prototype which
  Harbor-linked surfaces exist, but it does not supply prototype evidence.
- #188 owns Reward Kit, judge criteria, verifier/assertion layer safety,
  LiteLLM provider routing, and learned-oracle fit.
- #189 owns ATIF, artifact, result viewer, trajectory/result format, and
  observability/evaluation instrumentation fit.
- #190 owns Jig Driver substrate and sandbox provider gates for cloud runtime
  selection.
- #191 owns final disposition, Harbor registry projection, benchmark registry
  implications, training/export surface treatment, and any downstream adoption,
  deferment, or rejection.

## Downstream Routing

- #183 receives this catalog as one Harbor child-output input.
- #186 is complete when this catalog, validator coverage, Harbor record update,
  security closeout, documentation closeout, and Ralph review evidence are
  merged.
- #187 should use this catalog only as source-backed prototype candidate input.
- #188 should use the Reward Kit, judge criteria, LiteLLM, reward.txt, and
  reward.json entries as source-backed review input.
- #189 should use the ATIF, Opik, result viewer, artifact, and trajectory/result
  format entries as source-backed review input.
- #190 should use the Daytona, Modal, E2B, Runloop, Tensorlake, Islo,
  CoreWeave Sandboxes, and W&B Sandboxes entries as driver-gate input.
- #191 should consume this catalog during final projection and must keep
  third-party-fallback evidence separate from first-party Harbor claims.

## Deferments And Nonportable Claims

- Prototype implementation is deferred to #187.
- Visual and UX design is not applicable because this issue changes only
  source-backed documentation and validator gates; no user-facing UI is added.
- Broad market survey work is out of scope; only Harbor-linked surfaces are
  cataloged.
- Provider account state, credentials, raw logs, screenshots, local scratch
  output, and local source-review work directories are nonportable and are not
  retained as project truth.
- Third-party-fallback evidence can clarify context but cannot prove Harbor's
  first-party contract.

## Security Privacy And Durability

Security closeout for this issue is narrowed to the changed surfaces:

- The catalog is committed portable documentation.
- The validator addition checks a fixed repo-relative path, required sections,
  required fields, required coverage terms, exact downstream routes, portable
  path hygiene, and broad-survey exclusion.
- The validator does not add subprocess execution, network access, dynamic file
  selection, credential handling, provider API calls, or untrusted path writes.
- Source-review evidence is summarized by URL and durable conclusion; raw
  scratch output is not committed and should not be treated as project truth.
- No credentials, private provider account details, raw traces, model outputs,
  or sensitive external service usage details are recorded here.

If downstream Harbor work records real provider usage, traces, artifacts, or
security findings, it must classify the evidence separately before publication.

## Closeout Evidence

- Triage result: #186 was open, ready-for-agent, dependency:unblocked, and its
  blockers #184 and #185 were closed before implementation. #191 remained a
  downstream blocked issue.
- Source review result: reviewed official Harbor docs, Harbor repository source
  for ATIF, and Opik integration docs as third-party-fallback context. The
  accepted durable evidence is the source URL inventory and catalog conclusions
  above.
- Grill result: no interactive grill was started because the source review did
  not expose a new durable glossary term, ADR-worthy tradeoff, or unresolved
  scope conflict outside the approved plan.
- Prototype result: non-applicable for #186 because #187 owns Harbor prototype
  work.
- Impeccable result: non-applicable because this issue has no visual or UX
  surface.
- TDD result: validator coverage was added for path presence, ledger status,
  required sections, required fields, Harbor-linked coverage terms, downstream
  routes, portable paths, broad-survey exclusion, and final catalog presence.
- Security closeout: narrowed diff review found no new subprocess, network,
  credential, dynamic path, secret-handling, or external provider side effects.
- Documentation closeout: this catalog and `docs/evaluations/harbor.md` carry
  the durable documentation updates; README, AGENTS, and general operating
  docs were not changed because this is issue-specific Harbor evaluation
  evidence under existing external-tool evaluation routing.
- Ralph Review Cycle 1, Cross-Boundary Coherence: found that the Hugging Face
  parity row used vendor-doc-supported for a Harbor-doc source; fixed by using
  harbor-doc-supported and keeping vendor-doc-supported as an allowed value
  definition only.
- Ralph Review Cycle 1, Story Quality: found that the validator could accept
  catalog field names from non-header table cells; fixed by checking Markdown
  table headers and adding a regression test.
- Ralph Review Cycle 2, Cross-Boundary Coherence: clean after rerunning source
  routing, downstream issue routing, security closeout, documentation closeout,
  and validator evidence against the revised diff.
- Ralph Review Cycle 2, Story Quality: clean after rerunning the validator
  behavior, test coverage, maintainability, and durable-evidence review.
