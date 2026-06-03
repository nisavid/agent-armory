# Harbor Reward Kit Evaluation

Status: Source Disposition Ledger

## Scope Boundary

This ledger evaluates Harbor Reward Kit and judge criteria for issue
[#188](https://github.com/nisavid/agent-armory/issues/188). It asks whether
Reward Kit should be wrapped, conceptually borrowed, deferred, or rejected for
current Armory **Assertion Provider** and **Learned Oracle** work.

This ledger does not implement deterministic Assertion Providers, Learned
Oracles, a Jig Runner, a Jig Driver, Harbor execution, Harbor prototype
results, or final Harbor disposition. Issue
[#191](https://github.com/nisavid/agent-armory/issues/191) owns final Harbor
projection after all child evidence is coherent.

## Portable Source Inventory

Sources were checked on 2026-06-03. Firecrawl extraction output, GitHub CLI
JSON, and raw command output are instance-scoped scratch evidence. Durable
project evidence is the source URL set and curated conclusions below.

| source_id | source identity | evidence class | retained use |
| --- | --- | --- | --- |
| HRK001 | [Reward Kit](https://www.harborframework.com/docs/rewardkit) | documentation-supported | Reward Kit purpose, programmatic criteria, judge TOML, scoring, isolation, output files, comparison behavior, CLI defaults, and provider routing. |
| HRK002 | [Judge Criteria](https://www.harborframework.com/docs/rewardkit/judge-criteria) | documentation-supported | LLM judges, agent judges, individual mode, TOML fields, score normalization, trajectory evaluation, and prompt-template behavior. |
| HRK003 | [Harbor source](https://github.com/harbor-framework/harbor) | source-supported | Reward Kit implementation and tests under `packages/rewardkit/`, including models, runner, reward aggregation, judge execution, and unit tests. |
| HRK004 | [Reward Kit example](https://github.com/harbor-framework/harbor/tree/main/examples/tasks/reward-kit-example) | source-supported | Harbor task integration shape for verifier files and reward output convention. |
| HRK005 | [Harbor open pull requests](https://github.com/harbor-framework/harbor/pulls?q=is%3Apr+is%3Aopen+rewardkit) | live repository observation | Current Reward Kit change pressure, including judge timeout handling, schema-key stability, individual mode, scoring, auth, and model override work. |
| HRK006 | [Harbor open issues](https://github.com/harbor-framework/harbor/issues?q=is%3Aissue+is%3Aopen+rewardkit) | live repository observation | Current Reward Kit risks, including auth bugs, agent judge mode behavior, timeout behavior, scoring ambiguity, and judge schema failure. |
| HRK007 | [Harbor verifier tampering issue](https://github.com/harbor-framework/harbor/issues/1779) | live repository observation | Public-safe security risk that malicious agent code can touch verifier reward output under at least one verifier execution shape. |

## Reward Kit Fit Matrix

| Armory role | Reward Kit evidence | Fit classification | Rationale |
| --- | --- | --- | --- |
| Deterministic Assertion Provider | Reward Kit supports programmatic deterministic criteria for files, commands, JSON, CSV, HTTP, images, trajectories, and custom Python checks. Source: HRK001, HRK003. | Borrow concepts; defer wrapping. | Deterministic criteria overlap useful Assertion Provider shapes, but Reward Kit returns numeric reward scores and `reward-details.json`, not the Armory structured assertion result statuses. The current safe path is to borrow the criterion catalog, directory ergonomics, weighted aggregation caution, and verifier comparison behavior while #165 defines Armory-native typed results. |
| Learned Oracle | Reward Kit judge TOML supports LLM judges, agent judges, individual mode, score normalization, `atif-trajectory`, prompt templates, and provider routing. Source: HRK001, HRK002, HRK003. | Borrow concepts; defer wrapping. | Judge criteria are a useful Learned Oracle reference, but they rely on LiteLLM/provider credentials or agent CLI execution, normalize outputs to numeric scores, and do not preserve Armory disagreement, `oracle_error`, calibration profile, or Codex adjudication semantics by default. Issue #166 should borrow the TOML ergonomics and per-criterion evidence scoping only after its local inference contract is explicit. |
| Shared assertion result contract | Reward Kit writes `reward.json` and `reward-details.json`; the runner groups reward scores and details by reward name. Source: HRK001, HRK003. | Reject as direct contract for current Armory result status. | Output files are useful evidence artifacts, but scores are not equivalent to Armory statuses such as pass, fail, inconclusive, disagreement, `oracle_error`, timeout, or flaky. |
| Provider routing | Reward Kit lets operators override judge providers through CLI flags or environment variables and uses LiteLLM for LLM judges. Source: HRK001, HRK002, HRK003. | Borrow with stricter controls. | Provider routing is useful for avoiding rubric lock-in, but Armory needs explicit local endpoint allowlists, model/prompt/version metadata, cost boundaries, credential handling, and raw evidence disposition before Learned Oracles can consume it. |
| Comparison behavior | Reward Kit can run multiple verifier directories and write namespaced reward keys for side-by-side comparison. Source: HRK001, HRK003. | Borrow concepts. | Verifier comparison is useful for evaluating assertion designs, but comparison output should remain methodology input until Armory result schemas and Study Report evidence rules decide how to preserve it. |

Recommended current disposition for #188:

- deterministic Assertion Providers: borrow concepts; defer wrapping.
- Learned Oracles: borrow concepts; defer wrapping.
- direct adoption of Reward Kit output files as Armory structured result
  contract: reject for current work.

## Open Harbor PRs Issues And Security Risks

Live open Harbor PRs/issues checked on 2026-06-03 show Reward Kit is still
moving across behavior that matters to Armory. Open pull requests include:

- [harbor-framework/harbor#1784](https://github.com/harbor-framework/harbor/pull/1784):
  stable rubric id for judge criteria.
- [harbor-framework/harbor#1785](https://github.com/harbor-framework/harbor/pull/1785):
  negative-verifier polarity for judge criteria.
- [harbor-framework/harbor#1787](https://github.com/harbor-framework/harbor/pull/1787):
  must-have importance and required-pass aggregation.
- [harbor-framework/harbor#1788](https://github.com/harbor-framework/harbor/pull/1788):
  schema-key decoupling from criterion names.
- [harbor-framework/harbor#1791](https://github.com/harbor-framework/harbor/pull/1791):
  judge timeout recording instead of whole-run crash.
- [harbor-framework/harbor#1793](https://github.com/harbor-framework/harbor/pull/1793):
  agent judge `mode = "individual"` handling.
- [harbor-framework/harbor#1770](https://github.com/harbor-framework/harbor/pull/1770)
  and [#1778](https://github.com/harbor-framework/harbor/pull/1778): judge auth
  and model override behavior.

Live open issues checked on 2026-06-03 show adoption risks:

- [harbor-framework/harbor#1771](https://github.com/harbor-framework/harbor/issues/1771):
  Claude subscription auth bugs can block grading.
- [harbor-framework/harbor#1792](https://github.com/harbor-framework/harbor/issues/1792):
  agent judges may ignore individual mode.
- [harbor-framework/harbor#1790](https://github.com/harbor-framework/harbor/issues/1790):
  judge timeouts can abort verifier runs and omit reward files.
- [harbor-framework/harbor#1786](https://github.com/harbor-framework/harbor/issues/1786):
  long criterion names can break judge schema handling.
- [harbor-framework/harbor#1726](https://github.com/harbor-framework/harbor/issues/1726):
  programmatic scoring aggregation remains a user-visible question.

Security risks relevant to Armory:

- verifier/reward tampering: [#1779](https://github.com/harbor-framework/harbor/issues/1779)
  reports a reward output boundary concern under a verifier execution shape.
- agent judges can run commands and inspect files; this makes them process,
  filesystem, credential, and external disclosure surfaces, not just passive
  rubric evaluators.
- LLM judges route provider credentials and model calls through environment and
  LiteLLM behavior. Armory Learned Oracles need explicit provider/account,
  cost, endpoint, raw evidence, transcript, and model output controls.
- isolation is promising but not enough by itself for Armory adoption because
  the selected driver, verifier workspace, artifact collection, and output
  provenance boundaries still need independent validation.

## Downstream Routing

| route | accepted input from this ledger | not owned here |
| --- | --- | --- |
| [#188](https://github.com/nisavid/agent-armory/issues/188) | Reward Kit fit evidence and closeout for deterministic Assertion Provider and Learned Oracle questions. | Final Harbor disposition. |
| [#165](https://github.com/nisavid/agent-armory/issues/165) | Borrow the deterministic criteria catalog, explicit comparison behavior, and output provenance cautions while designing Armory-native structured assertion results. | Implementing providers or adopting Reward Kit output files. |
| [#166](https://github.com/nisavid/agent-armory/issues/166) | Borrow judge TOML ergonomics, individual criteria scoping, trajectory evaluation prompts, and provider routing questions as design pressure. | Implementing local inference adapters or accepting external provider routing. |
| [#191](https://github.com/nisavid/agent-armory/issues/191) | Use this ledger as the Reward Kit child evidence when projecting final Harbor disposition. | Creating PRDs, ADRs, or final issue projection before remaining child evidence exists. |

## Deferments And Nonportable Claims

- No Harbor execution, Reward Kit execution, Docker run, cloud provider run,
  Harbor install, provider credential use, or local model call is accepted by
  #188.
- No `reward.json`, `reward-details.json`, trajectory, transcript, local log,
  local path, model output, provider account state, or raw scrape output is
  durable project truth for this issue.
- Reward Kit source and docs are retained as evidence, not Armory vocabulary.
  Existing glossary terms **Assertion Provider** and **Learned Oracle** remain
  sufficient.
- No PRD or ADR is created by this issue because the recommendation does not
  change a hard-to-reverse Armory architecture decision.

## Security Privacy And Durability

This change set records a documentation ledger and structural Markdown
validator coverage. It introduces no Harbor execution, subprocess invocation,
cloud sandbox operation, registry write, credential handling, LLM provider
call, local filesystem mutation outside committed docs/tests/validator files,
or external disclosure beyond normal public source retrieval and issue/PR
projection.

Privacy boundaries:

- Do not commit or post raw logs, local paths, credentials, trajectories,
  transcripts, model outputs, provider account state, external service usage,
  raw Firecrawl output, or raw GitHub API output.
- Keep source-backed claims tied to URLs and dates because Harbor docs,
  Reward Kit behavior, and open PRs/issues can drift.
- Treat live open PRs/issues as local observations until #191 rechecks the
  graph for final projection.

## Closeout Evidence

Triage result: issue #188 remained `enhancement`, `ready-for-agent`,
`kind:research`, `mode:afk-implementation`, and `dependency:unblocked` when
work began. Live dependency reads showed #184 and #185 closed as blockers and
#188 blocking #191. Label audit findings were unrelated to #188.

Grill-with-docs result: no interactive grill was needed for #188. The source
evidence fits existing Armory vocabulary, and no new glossary term, PRD, or
ADR is introduced by this ledger.

Prototype result: non-applicable for #188. Issue #187 owns Harbor execution
prototype work.

Impeccable result: non-applicable for #188 because this is not a frontend or
product UI change.

TDD result: Armory Integrity Validation guards this ledger's path, status,
required sections, required coverage terms, required source URLs, downstream
issue routes, and host-local path rejection.

Security closeout: the change set adds a portable documentation ledger and
structural validation over one repository-relative Markdown path. The validator
uses existing path-status, Markdown-heading, link-search, route-token, and
host-local-path checks. It adds no new dynamic file selection, writes,
subprocess execution, network calls, secret handling, or untrusted path inputs.

Documentation closeout: this ledger and the Harbor External Tool Evaluation
record are the committed documentation changes for issue #188. The repository
documentation map already points readers to the reusable External Tool
Evaluation contract and does not need issue-specific closeout ledger links.

Ralph review closeout: Cross-Boundary Coherence and Story Quality Ralph
Review Cycle results belong in the PR body and final issue projection after
the final diff, validation, and security checks are complete.
