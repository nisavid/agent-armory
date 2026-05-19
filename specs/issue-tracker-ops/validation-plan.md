# Validation Plan: Issue Tracker Ops

Status: Equipment Candidate
Promotion state: implemented for bootstrap MVP; full delivery remains open

## Bootstrap validation

Run deterministic checks:

```sh
python3.14 -m unittest tests.test_issue_tracker_ops
python3.14 -m unittest tests.test_agent_equipment_config
python3.14 tools/validate_armory_integrity.py
```

Run dry-run adapter smokes:

```sh
python3.14 tools/issue_tracker_ops.py create-issue --repo nisavid/agent-armory --title "Dry-run issue" --body "Dry-run body" --label ready-for-agent
python3.14 tools/issue_tracker_ops.py update-issue --repo nisavid/agent-armory --issue-number 11 --body "Dry-run update"
python3.14 tools/issue_tracker_ops.py comment --repo nisavid/agent-armory --issue-number 11 --body "Dry-run comment"
python3.14 tools/issue_tracker_ops.py audit-labels --repo nisavid/agent-armory
python3.14 tools/issue_tracker_ops.py add-blocked-by --repo nisavid/agent-armory --issue-number 10 --blocking-issue-number 11
python3.14 tools/issue_tracker_ops.py comment --repo nisavid/agent-armory --issue-number 11 --body "Config-aware dry-run comment" --config-layer templates/config/agent-equipment-config-example.toml
```

Run live validation only after dry-run output is inspected and the active session
allows tracker mutation:

- create or update child issues for the decomposed remaining work;
- comment on issue #11 with validation evidence;
- run a read-only label-axis audit and record the summary;
- add or verify a native dependency relation needed for the bootstrap gate.

Record live validation by issue number, URL, operation type, command shape, and
result summary. Do not record raw token, verbose HTTP logs, or private host
paths.

## Security validation

- Run Codex Security diff-focused review for the adapter and changed policy docs,
  or record why a narrower action is sufficient.
- Confirm the adapter uses `subprocess.run` with an argument list and JSON stdin.
- Confirm mutation commands require `--execute`.
- Confirm dry-run output records the operation without invoking `gh`.
- Confirm Config-aware mutation refuses blocking, unsupported, malformed, or
  missing projection decisions before invoking `gh`.

## Documentation validation

- Inspect affected agent-facing docs: `AGENTS.md`, `CONTEXT.md`,
  `docs/ubiquitous-language.md`, `docs/agent-equipment-forge.md`,
  `docs/smith-runbook.md`, and `docs/agents/issue-tracker.md`.
- Inspect affected human-facing docs: `README.md`, `docs/README.md`, and
  `docs/forge-tour.md`.
- Update stale or incomplete claims, or record unchanged rationale in closeout.

## Full-delivery validation

Full closure of issue #11 needs additional validation for onboarding, Issue Ops
config profile fields, configuration layering, policy conflicts, issue
selection, issue repair, fallback reconciliation, permission failure, rate
limiting, duplicate detection, subtask handling, and cross-issue orchestration.
