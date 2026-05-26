# Pressure Scenarios: Issue Tracker Ops

Status: Equipment Candidate
Promotion state: implemented for bootstrap MVP; full delivery remains open

## Bootstrap scenarios

### Create follow-up under task pressure

An agent discovers a follow-up while closing a story and needs to record it in
GitHub Issues without adding a committed `docs/follow-ups/` file. The adapter
must produce a dry-run create preview by default and execute only when the
operator or active policy allows mutation.

Expected evidence:

- dry-run JSON shows title, body, labels, and target repository;
- execute JSON records the created issue response when live mutation is used.

### Update existing issue with validation evidence

An agent validates a bootstrap gate and needs to update an issue body or status.
The adapter must PATCH the target issue only under `--execute` and must reject an
empty update.

Expected evidence:

- dry-run JSON shows the exact PATCH body;
- tests cover empty-update rejection or equivalent validation.

### Comment with closeout evidence

An agent needs to add a concise validation note to a tracker issue. The adapter
must post a comment only under `--execute`; dry-run output must be inspectable
before notification side effects occur.

Expected evidence:

- unit test proves comment execution sends JSON stdin to `gh api`;
- live validation records the issue comment URL or response summary.

### Audit label-axis drift

An agent needs to dogfood the GitHub Issues label baseline before richer tracker
fields exist. The adapter must read issues, skip pull requests, and report
missing or conflicting baseline-axis labels without mutating tracker state.

Expected evidence:

- dry-run JSON shows the paginated GitHub read and the axis policy;
- execute JSON reports checked issues, issues with findings, error count, and
  warning count;
- unit tests cover category or state gaps, conflicting exclusive axes, and
  multiple primary work-kind warnings.

### Add native dependency relation

An agent must record that one issue is blocked by another. The adapter must
support GitHub's native dependency relation and resolve a human issue number to
the REST `issue_id` required by the dependency API.

Expected evidence:

- dry-run JSON shows read-then-write steps for issue-number input;
- execute JSON records the resolved blocking issue id and API result.

### Avoid duplicate and idempotent tracker writes

An agent repeats a closeout action after interruption. The adapter must check
tracker state under live `--execute`, block exact duplicate issue titles and
comment bodies by default, and return `idempotent_skip` for exact no-op updates
or dependency changes.

Expected evidence:

- mutation dry-run JSON shows planned safety preflight reads without calling
  `gh`;
- execute JSON records duplicate decisions or idempotent skips before a write;
- duplicate override requires an explicit reason.

### Reconcile fallback after tracker failure

A live tracker mutation fails after dry-run inspection and the caller explicitly
requests a fallback record. The adapter must write a local fallback record with
owner, retry condition, intended tracker target, reconciliation requirements,
and compensation guidance. Later reconciliation must inspect tracker state
before retry or retirement.

Expected evidence:

- failure JSON includes a failure class, retry condition, compensation guidance,
  and fallback record path when requested;
- `reconcile-fallback` reports whether the intended projection is present;
- `--retire-record` changes only the supplied fallback record after projection
  is verified.

## Full-delivery scenarios

- Missing config starts interruptible onboarding, as specified in
  [Config profile and onboarding](config-profile-and-onboarding.md), and leaves
  mutation modes advisory or read-only until policy enables writes.
- A plain handoff carries session-scoped Issue Ops policy when shared Config is
  absent, then promotes as a session override when Agent Equipment Config is
  equipped.
- Onboarding discovers repo-local and user-global Foreign Policy Surface
  inputs, records migration fates, and refuses user-global mutation without
  explicit approval.
- Compatibility classification decides whether a kept foreign policy surface is
  preserved through indirection, generation, adapter behavior, or a mixed
  strategy.
- Conflict reporting separates Config conflicts, Issue Ops semantic conflicts,
  adapter capability conflicts, and unresolved judgment.
- CLI and MCP parity expose the same typed contracts for onboarding, migration
  preview, migration apply, compatibility classification, and tracker operation
  plans.
- Issue review recommends repairs without writing when policy is uncertain.
- Semantic duplicate detection considers related issues, dependencies, PRD
  linkage, Reflection Findings, and out-of-scope records before asking for a
  disposition.
- Fallback compatibility supports richer local markdown workflows without
  turning fallback state into a parallel tracker.
- Issue selection distinguishes backlog placement, selected-for-development or
  to-do status, explicit priority, readiness labels, dependencies, and
  stakeholder overrides before recommending the next card.
- Cross-issue orchestration manages priority, readiness, delegation, subtasks,
  dependencies, and parent relationships under configured policy.
