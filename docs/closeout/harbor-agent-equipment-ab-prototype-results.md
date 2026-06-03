# Harbor Agent Equipment A/B Prototype Results

Status: Source Disposition Ledger

## Scope Boundary

Issue [#187](https://github.com/nisavid/agent-armory/issues/187) records a
bounded Harbor Agent Equipment A/B prototype for the Harbor external-tool
evaluation under parent [#183](https://github.com/nisavid/agent-armory/issues/183).
This ledger preserves only sanitized project evidence. It is not a Harbor
adoption decision, Armory structured result contract, public Armory API,
schema, PRD, ADR, Harbor registry decision, or proof that the equipped skill is
generally better.

The accepted durable claim is narrower: Harbor produced a discriminating local
A/B job with verifier reward evidence and collected report artifact evidence
for one deterministic task.

## Prototype Setup

Source scope used only Harbor Framework surfaces:

- [Harbor Getting Started](https://www.harborframework.com/docs/getting-started)
- [Harbor Tasks](https://www.harborframework.com/docs/tasks)
- [Harbor Agents](https://www.harborframework.com/docs/agents)
- [Harbor Evals](https://www.harborframework.com/docs/evals)
- [harbor-framework/harbor](https://github.com/harbor-framework/harbor)

The prototype installed Harbor with `uv tool install harbor` and observed
Harbor CLI version `0.13.0`. Plain-text evidence terms: uv tool install harbor,
0.13.0, schema_version, 1.3, no-network,
skills/issue-ops-workflow-executor/SKILL.md, artifact manifest.json, and status ok.
The local Harbor run used a Docker environment backed by the host's
Podman-compatible Docker and Compose surface. The scratch task used
`schema_version = "1.3"`, Linux container runtime, explicit timeouts, and
runtime `network_mode = "no-network"`. Image availability and container runtime
access were host prerequisites, not Armory adoption evidence.

The prototype task asked for an Issue Ops advisory workflow report. Both
variants used the same deterministic custom agent implementation through
custom agent import paths. The baseline variant ran without equipment input.
The equipped variant used the same logic with
`skills/issue-ops-workflow-executor/SKILL.md` as the only variable.

## Command Summary

Sanitized command coverage:

- `harbor --help`
- `harbor run --help`
- `harbor --version`
- `docker ps`
- `docker compose version`
- `podman ps`
- baseline `harbor run` with custom agent import path
- equipped `harbor run` with custom agent import path
- job `result.json` inspection
- trial `result.json` inspection
- verifier `reward.json` inspection
- artifact `manifest.json` inspection
- collected report artifact inspection
- trajectory and ATIF artifact search

The local Docker CLI resolved to a Podman-backed surface. The scratch runtime
needed a local Compose compatibility shim for Harbor's Docker Compose command
shape before the Harbor verifier could upload tests and complete both trials.
That shim is instance-scoped scratch evidence and is not committed.

## Result Summary

| variant | completed trials | errors | reward | required sections present | required sections missing | artifact manifest |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| baseline | 1 | 0 | 0.5714 | 3 | 4 | `status ok` for `/logs/artifacts` |
| equipped | 1 | 0 | 1.0 | 7 | 0 | `status ok` for `/logs/artifacts` |

Both trial result files recorded no exception. Both verifier reward files
included numeric `reward`, `score`, `report_exists`, `artifact_written`,
`required_section_fraction`, `required_sections_present`, and
`required_sections_missing` values. Both artifact manifest files reported
successful directory collection from `/logs/artifacts`, and both collected the
Issue Ops report artifact.

No trajectory or ATIF file was emitted by this deterministic custom-agent
prototype. That absence is an observation for [#189](https://github.com/nisavid/agent-armory/issues/189),
not a Harbor trajectory-contract conclusion.

## Evidence Classification

Durable project evidence:

- this sanitized closeout ledger
- the Harbor evaluation record update in `docs/evaluations/harbor.md`
- validator coverage for this ledger and the Harbor evaluation record

Instance-scoped scratch evidence:

- scratch task files
- raw jobs
- raw logs
- raw reward files
- raw artifact reports
- trial ids
- local absolute paths
- container runtime state
- trajectories, if any future run emits them
- transcripts
- model outputs
- provider credentials
- provider account state

Scratch evidence is summarized here by scope, disposition, and durable
conclusions. It is not committed and is not treated as project truth.

## Runtime Controls And Boundaries

The task runtime used a local container-backed Harbor Docker environment with
`network_mode = "no-network"`. The prototype used no provider credentials, no
LLM calls, no cloud sandboxes, no Harbor registry writes, and no model access.

Image pull or availability, Docker/Podman compatibility, and local container
runtime access are runtime prerequisites. They do not establish production Jig
Driver suitability, cloud sandbox behavior, registry compatibility, or
long-term operational support.

## Downstream Routing

[#187](https://github.com/nisavid/agent-armory/issues/187) accepts the bounded
prototype evidence recorded here.

[#189](https://github.com/nisavid/agent-armory/issues/189) owns trajectory and
artifact contract fit, including whether Harbor output should map to Armory
Jig Runner results or ATIF-adjacent result surfaces.

[#190](https://github.com/nisavid/agent-armory/issues/190) owns Harbor driver
gate evidence against ADR 0022 and Jig Driver requirements.

[#191](https://github.com/nisavid/agent-armory/issues/191) owns final Harbor
evaluation disposition for parent [#183](https://github.com/nisavid/agent-armory/issues/183).

## Deferments And Nonportable Claims

Do not infer any of these claims from this prototype:

- equipped Issue Ops equipment is generally better
- Harbor should be adopted
- Harbor is production-ready as an Armory Jig Driver
- Harbor reward files are an Armory structured result contract
- Harbor artifact handling satisfies the Armory result contract
- Harbor emits an acceptable trajectory or ATIF contract for Armory
- Harbor cloud sandbox, registry, provider routing, or model behavior is
  acceptable for Armory
- verifier hardening is sufficient against reward tampering

Those claims remain deferred to [#189](https://github.com/nisavid/agent-armory/issues/189),
[#190](https://github.com/nisavid/agent-armory/issues/190), and
[#191](https://github.com/nisavid/agent-armory/issues/191).

## Security Privacy And Durability

Public-safe security conclusions:

- no credentials were used
- no provider or model calls were used
- no cloud sandbox was used
- no Harbor registry write was used
- the task runtime used `no-network`
- raw logs, raw jobs, reward files, trajectories, transcripts, model outputs,
  provider account state, external service usage details, and host-local paths
  remain outside durable committed evidence

The prototype still exposed operational risks that downstream issues must not
ignore: local Docker/Podman compatibility, verifier reward-file trust,
artifact collection shape, and the absence of trajectory evidence in this
custom-agent run.

## Closeout Evidence

Closeout evidence includes Harbor CLI help and version probes, local container
runtime checks, baseline and equipped Harbor run results, job `result.json`
inspection, trial `result.json` inspection, verifier `reward.json` inspection,
artifact `manifest.json` inspection, collected report artifact inspection,
trajectory absence check, validator TDD, Armory integrity validation, security
review, Change Set Documentation Closeout, Cross-Boundary Coherence Ralph
Review, and Story Quality Ralph Review.
