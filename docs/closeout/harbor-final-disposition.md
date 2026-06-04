# Harbor Final Disposition

Status: Source Disposition Ledger

## Scope Boundary

Issue [#191](https://github.com/nisavid/agent-armory/issues/191) completes the
Harbor external-tool evaluation for parent
[#183](https://github.com/nisavid/agent-armory/issues/183). It consumes the
durable child ledgers:

- docs/closeout/harbor-jig-source-map.md
- docs/closeout/harbor-neighbor-tool-catalog.md
- docs/closeout/harbor-reward-kit-evaluation.md
- docs/closeout/harbor-agent-equipment-ab-prototype-results.md
- docs/closeout/harbor-atif-job-artifacts-evaluation.md
- docs/closeout/harbor-driver-gate.md

This ledger does not adopt Harbor, select a Jig Driver, revise ADR 0022,
implement a runner, implement Assertion Providers or Learned Oracles, add UI,
create a PRD, create an ADR, run Harbor again, or perform a broad
eval-platform survey.

## Disposition Decision

Final External Tool Evaluation Disposition: research reference.

Harbor remains supporting source material for Armory work. It is not an
adopted candidate, supporting component, selected first Jig Driver, Assertion
Provider, Learned Oracle, Harness Test Suite evidence source, or direct Armory
result contract.

The decision preserves the accepted driver gate. Harbor is useful evidence for
future design, comparison, and validation pressure, but current evidence does
not make Harbor responsible for an Armory runtime, schema, result, assertion,
oracle, UI, or lifecycle boundary.

## Evidence Basis

The source-map ledger maps Harbor concepts into current Armory vocabulary
without adopting Harbor terms as Armory vocabulary.

The neighbor-tool catalog records Harbor-linked sandbox providers, Reward Kit,
LiteLLM, ATIF, Opik fallback context, Harbor registry, dataset.toml, adapter
templates, result viewer, Hugging Face parity experiments, SkyRL, and GEPA as
source-backed routing aids, not integration approvals.

The #187 prototype remains bounded prototype evidence only. It shows Harbor can
produce one discriminating local A/B job with baseline reward and equipped
reward evidence, but it does not establish Harbor adoption, selected first Jig
Driver fit, cloud sandbox behavior, registry behavior, provider behavior,
verifier hardening, or a direct Armory result contract.

Reward Kit should inform #165 and #166 with the decision to borrow concepts and defer wrapping.
It provides useful deterministic criteria, judge TOML, LLM judges, agent
judges, trajectory evaluation, provider routing, scoring, output files, and
comparison behavior, but Reward Kit output files are not Armory typed
assertion results.

Harbor result and artifact surfaces should inform #164 and #169. Harbor
result.json, trajectory.json, verifier output, artifact manifest.json, and
viewer affordances are useful source material, but they do not replace Armory
statuses or the future review-surface decision.

The driver-gate ledger defers Harbor as the first Jig Driver. Harbor's Docker,
cloud sandbox, network policy, sidecar, artifact, cleanup, credential,
reproducibility, portability, Codex workflow compatibility, and maintenance
surfaces require Armory-native proof before they can become driver guarantees.

## Projection Matrix

| route | final projection | not accepted |
| --- | --- | --- |
| [#163](https://github.com/nisavid/agent-armory/issues/163) | Use Harbor as comparison evidence when selecting the first Jig Driver. Apply ADR 0022 and the driver rubric before writing driver code. | Selecting Harbor, a provider-backed driver, a container-first driver, or any hybrid driver from #191 alone. |
| [#164](https://github.com/nisavid/agent-armory/issues/164) | Borrow the separation between job result, trial result, trajectory, verifier output, and artifact manifest when shaping structured results. | Replacing Armory statuses with Harbor reward, exception, or artifact fields. |
| [#165](https://github.com/nisavid/agent-armory/issues/165) | Borrow deterministic Reward Kit criteria catalog, comparison behavior, and output-provenance cautions. | Wrapping Reward Kit or adopting reward files as typed assertion results. |
| [#166](https://github.com/nisavid/agent-armory/issues/166) | Borrow judge TOML ergonomics, per-criterion scoping, trajectory evaluation prompts, provider routing questions, calibration pressure, and error-boundary cautions. | Accepting external provider routing or Reward Kit judge output as the Learned Oracle contract. |
| [#167](https://github.com/nisavid/agent-armory/issues/167) | No direct update until Jig Runner and Harness Test Suite evidence exists. | Treating Harbor output as Harness Test Suite evidence source now. |
| [#169](https://github.com/nisavid/agent-armory/issues/169) | Use Harbor viewer affordances as later UX evidence after Armory result artifacts exist. | Implementing Harbor's viewer or accepting viewer screenshots as durable UI truth. |
| [#177](https://github.com/nisavid/agent-armory/issues/177) | No direct update until structured Jig Runner or Harness Test Suite evidence exists. | Mapping raw Harbor output into Harness Capability lifecycle evidence now. |
| [#183](https://github.com/nisavid/agent-armory/issues/183) | Close the parent Harbor evaluation after #191 merges if live subissue state remains complete. | Keeping the parent open for a broad survey or premature architecture change. |
| [#191](https://github.com/nisavid/agent-armory/issues/191) | Close #191 after the final ledger, Harbor evaluation record, validation, security closeout, and review evidence are merged and projected. | Treating #191 as another Harbor prototype or implementation story. |

## Non-Goals And Deferments

No broad eval-platform survey is accepted. Harbor-neighbor tools remain
Harbor-linked evidence only.

No PRD and no ADR are created because this decision avoids a hard-to-reverse
architecture change. It preserves ADR 0022 and keeps first Jig Driver selection
with #163.

No Harbor run, cloud sandbox run, Harbor registry operation, Opik integration,
model call, provider credential use, UI implementation, schema revision, public
API change, first Jig Driver selection, Assertion Provider implementation,
Learned Oracle implementation, or Harness Test Suite integration is introduced
by this ledger.

## Security Privacy And Durability

Public-safe security conclusions remain the curated conclusions in the child
ledgers. Credentials, raw logs, local paths, host-local paths, raw
trajectories, transcripts, model outputs, viewer screenshots, provider account
state, external service usage, raw GitHub API output, raw Firecrawl output, and
raw tool output remain scratch evidence.

Future Harbor-backed work must re-evaluate provider credentials, verifier and
reward tampering, network effects, sidecar behavior, artifact integrity,
cleanup guarantees, cloud provider trust, local path disclosure, and
unsupported isolation claims before using Harbor as more than research
reference evidence.

## Closeout Evidence

Triage result: live blockers #186, #187, #188, #189, and #190 were closed, and
#191 was updated to `depth:L3`, `kind:design`, `mode:agent-led-grill`, and
`dependency:unblocked` before implementation.

Grill-with-docs result: the operator accepted `research reference` as the final
disposition, with Harbor retained as supporting source material and explicitly
not selected as the first Jig Driver. No CONTEXT.md or ADR update was needed
because the decision uses existing Armory vocabulary and preserves ADR 0022.

Prototype result: no new prototype was run for #191. The #187 bounded
prototype ledger remains the accepted prototype input.

Impeccable result: non-applicable. #191 adds no UI or visual design surface.

TDD result: Armory Integrity Validation guards this ledger, the completed
Harbor External Tool Evaluation record, required downstream routes, required
disposition terms, source references, and host-local path rejection.

Security closeout: this change set records public-safe documentation and
validator coverage only. It introduces no Harbor execution, cloud sandbox
operation, provider call, credential handling, or new subprocess behavior.

Documentation closeout: this ledger and `docs/evaluations/harbor.md` carry the
durable documentation changes. Downstream issue comments carry concise
projection notes; #167 and #177 receive no direct body updates until
structured Jig Runner or Harness Test Suite evidence exists.

Ralph review closeout: Cross-Boundary Coherence and Story Quality Ralph Review
Cycle results belong in the PR body and final issue projection after the final
diff, validation, and security checks are complete.
