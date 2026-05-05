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

### Add native dependency relation

An agent must record that one issue is blocked by another. The adapter must
support GitHub's native dependency relation and resolve a human issue number to
the REST `issue_id` required by the dependency API.

Expected evidence:

- dry-run JSON shows read-then-write steps for issue-number input;
- execute JSON records the resolved blocking issue id and API result.

## Full-delivery scenarios

- Missing config starts interruptible onboarding and leaves mutation modes
  advisory or read-only until policy enables writes.
- Issue review recommends repairs without writing when policy is uncertain.
- Duplicate-prone issue creation detects existing candidates and asks for a
  disposition.
- Fallback state records owner, retry condition, intended tracker target, and
  reconciliation requirements when direct tracker recording is blocked.
- Issue selection distinguishes backlog placement, selected-for-development or
  to-do status, explicit priority, readiness labels, dependencies, and
  stakeholder overrides before recommending the next card.
- Cross-issue orchestration manages priority, readiness, delegation, subtasks,
  dependencies, and parent relationships under configured policy.
