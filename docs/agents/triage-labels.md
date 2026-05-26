# Triage Labels

Preferred policy authority: `config/agent-equipment.toml`.

This document is a compatibility layer for active triage skills and human
readers. Use the Config layer for the machine-readable label axes,
cardinalities, role mappings, dependency-disposition policy, and audit
expectations. Use this document for readable role meanings and triage-record
guidance over that Config authority. If these surfaces conflict, the Config
layer is authoritative.

The engineering skills use two issue category roles and five canonical triage
state roles.

These roles are represented as GitHub labels in the current GitHub Issues
baseline. Labels are the baseline because Issue Tracker Ops must support common
GitHub Issues workflows before it can coherently build and dogfood richer
GitHub Projects custom-field behavior. Labels are not assumed to be the best
long-term UX.

## Representation Boundary

Use GitHub built-in issue fields for native issue facts: open or closed state,
assignees, milestones, title, body, comments, and native dependency relations.
Use labels only for custom predicates that GitHub Issues does not otherwise
represent in the baseline. Use comments for rationale, evidence, questions,
briefs, and decision records.

Do not treat GitHub Projects custom fields as adopted Issue Tracker Ops policy
yet. They remain a future adapter surface after the GitHub Issues label baseline
is specified, implemented, validated, and dogfooded.

## Category Roles

Each triaged issue should carry exactly one category role.

| Role | Label | Meaning |
| --- | --- | --- |
| `bug` | `bug` | Broken or regressed behavior needs repair |
| `enhancement` | `enhancement` | New, changed, or improved behavior is requested |

Keep category roles intentionally coarse. Research, design, documentation,
implementation, epic, cleanup, and Reflection Finding are work kinds, not
category replacements. If one issue mixes bug repair and enhancement work,
split it when practical, or choose the dominant immediate correction and note
the follow-up.

## State Roles

| Role | Label | Meaning |
| --- | --- | --- |
| `needs-triage` | `needs-triage` | No stable next handling decision exists yet, or the next decision depends on unresolved context that is not specifically waiting on a reporter |
| `needs-info` | `needs-info` | Waiting on a specific answer, artifact, confirmation, or decision from a reporter or operator |
| `ready-for-agent` | `ready-for-agent` | An AFK agent can act from the issue or brief without first resolving material ambiguity |
| `ready-for-human` | `ready-for-human` | Human judgment, external authority, manual access, or subjective product/design decision is needed before implementation can proceed |
| `wontfix` | `wontfix` | The work should not be actioned under current project intent |

Keep state roles mutually exclusive. Do not make them carry dependency state,
triage depth, priority, engagement mode, or work kind. Track those axes
separately.

## Baseline Dogfooding Axes

The GitHub Issues baseline also uses labels for the following custom axes. This
is intentional dogfooding of the minimum Issue Tracker Ops surface. These axes
may later move to GitHub Projects custom fields or another tracker adapter once
that richer workflow is specified, implemented, validated, and battle-tested.

### Triage Depth

Triage depth records the evidence boundary that supports the current triage
recommendation. An issue should carry at most one triage-depth label, updated
to the deepest level reached.

| Role | Label | Meaning |
| --- | --- | --- |
| `L0` | `depth:L0` | Semantic hygiene only; no reflective issue analysis |
| `L1` | `depth:L1` | Issue body and comments were critically read |
| `L2` | `depth:L2` | First-order linked issues, docs, PRs, or references were checked |
| `L3` | `depth:L3` | Deep issue session with repo scouting, reproduction or design facilitation, and review as needed |

### Work Kind

Work kind records the primary kind of work the issue requires. Prefer one
primary work-kind label. Use multiple only when a deliberate mixed-work issue
is better than splitting.

| Role | Label | Meaning |
| --- | --- | --- |
| `research` | `kind:research` | Evidence gathering, source scouting, comparison, or investigation |
| `design` | `kind:design` | Product, workflow, architecture, policy, or equipment design |
| `documentation` | `kind:documentation` | Human-facing or agent-facing documentation work |
| `implementation` | `kind:implementation` | Code, script, tool, config, validator, or executable behavior work |
| `epic` | `kind:epic` | Parent, umbrella, or orchestration issue for related work |
| `cleanup` | `kind:cleanup` | Retiring, reorganizing, reconciling, or simplifying existing material |
| `reflection-finding` | `kind:reflection-finding` | Durable routing for a Reflection Finding or cognition/workflow lesson |

### Engagement Mode

Engagement mode records the next expected handling shape. An issue should carry
at most one engagement-mode label.

| Role | Label | Meaning |
| --- | --- | --- |
| `afk-implementation` | `mode:afk-implementation` | An AFK agent can execute the next work without live operator interaction |
| `agent-led-grill` | `mode:agent-led-grill` | The next useful step is an agent-led grill, interview, or design facilitation |
| `human-decision` | `mode:human-decision` | The next useful step depends on human judgment, authority, preference, or access |
| `linked-context-triage` | `mode:linked-context-triage` | The next useful step is reading linked issues, docs, PRs, dependencies, or source references |
| `deep-session` | `mode:deep-session` | The issue should be handled in a focused one-issue session |

### Brief Status

Brief status records whether the issue has the handoff needed for delegation.
Use at most one brief-status label when brief state matters.

| Role | Label | Meaning |
| --- | --- | --- |
| `not-needed` | `brief:not-needed` | No agent or human brief is needed for the next action |
| `needed` | `brief:needed` | A brief must be written before the issue can be delegated safely |
| `present` | `brief:present` | A current brief exists and can guide the next handler |
| `stale` | `brief:stale` | A brief exists but must be refreshed before use |

### Dependency Disposition

Dependency disposition records how dependency state affects issue selection.
Use at most one dependency-disposition label when dependency state has been
checked.

| Role | Label | Meaning |
| --- | --- | --- |
| `unblocked` | `dependency:unblocked` | No active blocker is known |
| `blocked` | `dependency:blocked` | One or more blockers currently prevent useful execution |
| `unknown` | `dependency:unknown` | Dependency state needs checking before selection |
| `needs-recording` | `dependency:needs-recording` | A dependency is known but the tracker relation or issue record is incomplete |

## Triage Records

Labels carry the current machine-checkable predicates. Triage comments carry
the reasoning that made those predicates safe to apply.

Every triage record comment must start with:

```markdown
> *This was generated by AI during triage.*
```

Use a triage record when an issue's current labels, readiness, unresolved
factors, or delegation path would not be obvious from the issue body alone. A
triage record should name the triage depth reached, the recommended category
and state, any work-kind or handling-mode labels that matter, the evidence
boundary checked, unresolved factors, and the next action or return contract.

Keep records concise. Do not copy large issue bodies, chat transcripts, logs,
or linked documents into the comment. Link or summarize the evidence boundary
instead, and preserve private or instance-scoped material outside public tracker
content.

Template:

```markdown
> *This was generated by AI during triage.*

## Triage Record

**Outcome:** `enhancement` / `ready-for-agent`
**Depth:** `depth:L1`
**Work kind:** `kind:documentation`
**Engagement mode:** `mode:afk-implementation`
**Brief status:** `brief:not-needed`
**Dependency disposition:** `dependency:unblocked`

**Evidence boundary:** issue body and comments.

**Reasoning:** short rationale for the outcome.

**Unresolved factors:** none, or a specific list.

**Next action:** concrete next step and owner shape.
```

## Baseline Audit

Run the label-axis audit before bulk dogfooding or when label drift is
suspected:

```sh
python3.14 tools/issue_tracker_ops.py audit-labels --repo nisavid/agent-armory --config-layer config/agent-equipment.toml
python3.14 tools/issue_tracker_ops.py audit-labels --repo nisavid/agent-armory --config-layer config/agent-equipment.toml --execute
```

The first command previews the read and axis policy. The second performs the
read-only GitHub query and reports missing or conflicting category, state,
depth, engagement-mode, brief-status, and dependency-disposition labels. It
also warns when multiple work-kind labels are present.
