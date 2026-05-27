# Skill-Eval Methodology Source Intake

Status: Source Disposition Ledger

## Scope Boundary

This ledger captures reusable skill-eval methodology from the skill-creator
source family and the harness-adaptation source family. It is source-disposition
evidence for issue #84. It does not define a final Forge eval DSL, runner,
schema, review UI, packaging workflow, or harness capability lifecycle.

Accepted claims in this ledger are design input for downstream Armory issues.
They are not direct proof that a harness supports a specific trigger signal,
timing field, token field, browser surface, isolated agent run, or packaging
contract. Harness-specific facts still need the Harness Capability Profile and
validation routes owned by the relevant downstream work.

## Portable Source Inventory

| source_id | source identity | source family | retained use |
| --- | --- | --- | --- |
| SE001 | `skill-creator/SKILL.md` | skill creation and evaluation workflow | Behavioral eval loop, baseline comparison, grading, benchmarking, human review, description optimization, and packaging workflow patterns. |
| SE002 | `skill-creator/references/schemas.md` | skill creation and evaluation workflow | Portable schema field names for eval, grading, timing, benchmark, comparator, analyzer, and feedback artifacts. |
| SE003 | `skill-creator/agents/grader.md` | skill creation and evaluation workflow | Grading discipline, burden of proof, expectation evidence, execution metrics, timing, claim capture, and eval-feedback capture. |
| SE004 | `skill-creator/agents/analyzer.md` | skill creation and evaluation workflow | Benchmark analysis patterns: non-discriminating checks, variance, hidden regressions, qualitative differences, and tradeoff review. |
| SE005 | `skill-creator/scripts/package_skill.py` and `skill-creator/scripts/quick_validate.py` | skill creation and evaluation workflow | Packaging exclusion and skill metadata validation constraints for later ingestion and promotion work. |
| SE006 | `adapting-skill-creator-to-harnesses/SKILL.md` | harness adaptation | Harness capability questions, current-harness substitution rules, trigger eval boundaries, unsupported-harness behavior, and static viewer fallback. |
| SE007 | `adapting-skill-creator-to-harnesses/scripts/prepare_behavior_evals.py` | harness adaptation | Behavior-eval workspace scaffolding and preservation of with-skill and baseline prompt parity. |
| SE008 | `adapting-skill-creator-to-harnesses/scripts/trigger_eval_core.py` | harness adaptation | Shared trigger eval case loading, temporary probe skill construction, sentinel detection, body-load diagnostics, and summary rendering. |
| SE009 | `adapting-skill-creator-to-harnesses/scripts/codex_trigger_eval.py`, `acpx_trigger_eval.py`, `claude_trigger_eval.py`, and `cursor_trigger_eval.py` | harness adaptation | Harness-specific runner contracts and explicit weaker-signal reporting when no native skill invocation event exists. |
| SE010 | `skill-creator/scripts/improve_description.py` and `skill-creator/scripts/run_loop.py` | skill creation and evaluation workflow | Description-improvement loop, trigger-case feedback, held-out testing, and benchmark-driven iteration. |
| SE011 | `skill-creator/eval-viewer/generate_review.py` and `skill-creator/eval-viewer/viewer.html` | skill creation and evaluation workflow | Review artifact generation, static viewer fallback, qualitative output review, benchmark display, and feedback capture. |

## Reusable Techniques

| technique | retained method | evidence class | limits and side effects |
| --- | --- | --- | --- |
| behavioral evals | Keep eval definitions, run metadata, with-skill outputs, baseline outputs, grading, benchmark aggregation, and review artifacts as separate surfaces. Compare runs only when prompts and fixtures are otherwise identical. | Source-supported methodology from SE001 and SE007. | Requires an isolated or equivalent baseline runner. If isolation is absent, retain qualitative with-skill checks and state that baseline benchmarking is unavailable. |
| trigger-selection evals | Use should-trigger and should-not-trigger cases against a temporary probe skill whose body contains only a unique sentinel. Count positives only when the harness provides the strongest available body-load or skill-selection signal and emits the sentinel. Count negatives only when the sentinel is absent and the documented tool boundary is respected. | Source-supported methodology from SE006, SE008, and SE009. | Trigger evidence is harness-specific. Claude, Codex, ACPX, and Cursor signals are not interchangeable. Weaker surrogate signals must be named in summaries. |
| harness adaptation | Start by recording whether the current harness can spawn isolated agents, inherit model settings, expose timing or token metadata, present files or browser views, and test real skill-trigger behavior. | Source-supported methodology from SE006 and implementation inference from SE009. | Missing harness capabilities are reported as limits, not filled with fabricated metrics or cross-harness proxy results. |
| description optimization | Evaluate trigger descriptions against mixed positive and near-miss negative queries, split train and held-out test cases, generalize from failures, and keep rewritten descriptions comfortably below the skill metadata limit. | Source-supported methodology from SE001 and SE010. | Optimization is authoritative only when both detector and optimizer target an accepted current-harness route. Cross-harness optimization is optional analysis, not validation. |
| benchmarking | Aggregate expectation pass rate, timing, tokens, errors, deltas, means, and variance across configurations, then analyze whether aggregate wins hide flaky or non-discriminating evals. | Source-supported methodology from SE001, SE002, and SE004. | Timing and token fields are retained only when the harness exposes them. Missing metrics are limitations, not zero values. |
| human review | Put qualitative outputs and benchmark summaries in front of a reviewer before revising the skill. Treat feedback as a first-class input alongside quantitative results. | Source-supported methodology from SE001 and SE002. | Human judgment remains necessary for subjective skills and for claims that cannot be reduced to deterministic assertions. |
| grading | Grade expectations with fields that state the assertion text, pass/fail status, and evidence. Use scripts for objectively checkable assertions where practical, and keep grader feedback about eval quality. | Source-supported methodology from SE001, SE002, and SE003. | Passing grades do not prove trigger selection, packaging safety, or harness portability unless those properties were directly evaluated. |
| packaging | Validate skill metadata before packaging, exclude eval workspaces from distributable packages, and present packaged artifacts only through an accepted harness affordance. | Source-supported methodology from SE001 and SE005. | Packaging claims are skill-package claims, not ingestion, promotion, or registry policy. Those belong to #5, #155, #157, and later Forge work. |
| viewer/review workflow | Prefer the existing review viewer or a static equivalent over custom review UI. Keep reviewer focus on outputs, grades, benchmark deltas, feedback capture, and the current decision. | Source-supported methodology from SE001, SE006, SE007, and SE011, plus product-interface design review. | This issue does not implement UI. Later UI work should reduce cognitive load with task-first grouping, familiar tabs or sections, and no decorative component vocabulary. |

## Downstream Routing

| route | accepted input from this ledger | not owned here |
| --- | --- | --- |
| #61 | Agent Test Jigs and Harness Testing System should inherit the distinction between behavioral evals, trigger-selection evals, grading, benchmark aggregation, human review, fixture failures, harness failures, oracle disagreement, and unsupported capability states. | Final jig runner architecture, result schema, assertion provider contracts, and learned-oracle policy. |
| #62 | Harness Capability lifecycle methodology should require capability checks before claims about isolated agents, trigger signals, timing, tokens, file presentation, browser/viewer support, and packaging presentation. | Lifecycle stage definitions and promotion criteria. |
| #67 | Manager Core and Forge workflows should project only accepted harness facts and should preserve uncertainty, side effects, privacy, and durability limits when consuming skill-eval evidence. | Manager Core workflow implementation or Forge workflow rewrites. |
| #5 | Equipment ingestion and promotion should treat skill eval outputs, package validation, review feedback, and source inventories as evidence inputs, not as automatic promotion decisions. | The full ingestion and promotion pipeline design. |
| #155 | Agent Equipment Config routing skill should receive the lesson that evaluation and packaging routes depend on declared harness capabilities and configured side-effect policy. | The published skill content and executable routing behavior. |
| #157 | Delivery-system alignment should use this source intake and #85 together for only the delivery slices that consume skill or plugin source-intake lessons. | The aligned delivery-system design and dependency cleanup beyond #84. |
| later Forge work | Later Forge work can decide whether these techniques become templates, examples, specs, validation scripts, or equipment-specific closeout gates. | Any final canonical eval DSL, reusable runner framework, or UI surface. |

## Deferments And Nonportable Claims

- Runner internals in SE008 and SE009 are retained as methodology examples, not
  as canonical Armory runner architecture.
- Per-harness trigger contracts are retained with their evidence limits. A
  positive trigger-selection eval in one harness is not evidence for another
  harness.
- Raw eval workspaces, local execution logs, and temporary probe artifacts are
  instance-scoped scratch. They are summarized by durable conclusions and are
  not committed as project truth.
- Timing and token metadata are optional harness facts. When absent, downstream
  consumers record the gap instead of substituting zeros or estimates.
- Description optimization remains separate from behavior validation. A better
  trigger description does not prove task quality.
- Viewer/review workflow lessons are information-architecture input only. No
  custom review UI is accepted by this issue.

## Security, Privacy, And Durability

The accepted source material contains local execution patterns, temporary
workspace creation, command invocation, probe skills, package output, review
artifacts, and benchmark metadata. Downstream executable work must model those
as file, process, network, and disclosure boundaries before treating them as
automation.

Durable project evidence for #84 consists of this ledger, the PR diff,
deterministic validation output, security closeout, documentation closeout, and
issue projection. Portable review summaries may name the source identities
above and the conclusions retained here. Instance-scoped scratch includes raw
runner stdout, local workspaces, temporary skill bodies, copied source paths,
generated reports, browser sessions, and local packaging output.

Privacy boundaries:

- Do not preserve user workstation paths, raw home-directory layout, auth
  state, command environment, model transcript payloads, or local package
  artifacts in durable project docs.
- Do not publish probe-skill bodies beyond the sentinel methodology unless a
  later issue accepts a sanitized fixture format.
- Do not treat human review feedback as publishable unless the feedback is
  intentionally supplied for project record.

## Closeout Evidence

Grill-with-docs result: existing Armory vocabulary is sufficient. The correct
durable surface is this Source Disposition Ledger under `docs/closeout/`.
No new glossary term or ADR is needed for #84.

Impeccable review-method pass: the accepted viewer/review workflow lesson is
task-first review structure, not frontend implementation. Future review UI
should keep outputs, grades, benchmark deltas, and reviewer feedback visible
without asking the reviewer to remember facts across screens.

TDD result: Armory Integrity Validation owns a structural guard for this ledger:
status, required sections, required technique coverage, downstream issue routes,
and host-local path rejection.

Security closeout: the change-set scan found no reportable candidates. The new
validator code reads one constant repository-relative Markdown path through the
existing required-path guard, does not introduce writes, subprocess execution,
network calls, secret handling, or untrusted path inputs, and the ledger
preserves only portable source identities.

Documentation closeout: this ledger is the only committed doc change needed for
#84. The repository documentation map remains reader-oriented and does not list
issue-specific closeout ledgers; the repository threat model already covers the
validator and durable-evidence boundaries exercised by this change.

Ralph review closeout: documentation closeout, Cross-Boundary Coherence, and
Story Quality review cycles are clean after the source-inventory precision fix.
