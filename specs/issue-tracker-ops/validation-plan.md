# Validation Plan: Issue Tracker Ops

Status: Equipment Candidate
Promotion state: implemented for bootstrap MVP; full delivery remains open

## Bootstrap validation

Run deterministic checks:

```sh
python3.14 -m unittest tests.test_issue_tracker_ops
python3.14 -m unittest tests.test_agent_equipment_config
python3.14 -m unittest tests.test_validate_armory_integrity
python3.14 tools/validate_armory_integrity.py
```

Run dry-run adapter smokes:

```sh
python3.14 tools/issue_tracker_ops.py describe-core
python3.14 tools/issue_tracker_ops.py describe-adapter --adapter github-issues-baseline
python3.14 tools/issue_tracker_ops.py plan-operation --adapter github-issues-baseline --operation issue.create
python3.14 tools/issue_tracker_ops.py plan-operation --adapter github-issues-baseline --operation issue.read
python3.14 tools/issue_tracker_ops.py plan-operation --adapter github-issues-baseline --operation subissue.add
python3.14 tools/issue_tracker_ops.py read-issue --repo nisavid/agent-armory --issue-number 15
python3.14 tools/issue_tracker_ops.py list-issues --repo nisavid/agent-armory --issue-state open --label ready-for-agent --paginate
python3.14 tools/issue_tracker_ops.py create-issue --repo nisavid/agent-armory --title "Dry-run issue" --body "Dry-run body" --label ready-for-agent
python3.14 tools/issue_tracker_ops.py update-issue --repo nisavid/agent-armory --issue-number 11 --body "Dry-run update"
python3.14 tools/issue_tracker_ops.py comment --repo nisavid/agent-armory --issue-number 11 --body "Dry-run comment"
python3.14 tools/issue_tracker_ops.py audit-labels --repo nisavid/agent-armory
python3.14 tools/issue_tracker_ops.py add-blocked-by --repo nisavid/agent-armory --issue-number 10 --blocking-issue-number 11
python3.14 tools/issue_tracker_ops.py get-parent-issue --repo nisavid/agent-armory --issue-number 15
python3.14 tools/issue_tracker_ops.py list-sub-issues --repo nisavid/agent-armory --issue-number 11 --paginate
python3.14 tools/issue_tracker_ops.py add-sub-issue --repo nisavid/agent-armory --issue-number 11 --sub-issue-number 15
python3.14 tools/issue_tracker_ops.py remove-sub-issue --repo nisavid/agent-armory --issue-number 11 --sub-issue-number 15
python3.14 tools/issue_tracker_ops.py reprioritize-sub-issue --repo nisavid/agent-armory --issue-number 11 --sub-issue-number 15 --after-issue-number 14
python3.14 tools/issue_tracker_ops.py comment --repo nisavid/agent-armory --issue-number 11 --body "Config-aware dry-run comment" --config-layer templates/config/agent-equipment-config-example.toml
python3.14 tools/issue_tracker_ops.py reconcile-fallback --repo nisavid/agent-armory --fallback-record-file fallback-record.json
```

Run live validation only after dry-run output is inspected and the active session
allows tracker mutation:

- create or update child issues for the decomposed remaining work;
- comment on issue #11 with validation evidence;
- run a read-only label-axis audit and record the summary;
- add or verify a native dependency relation needed for the bootstrap gate.
- read selected issues, issue lists, parent relationships, and sub-issue lists
  with `--execute` before relying on tracker state.
- reconcile and retire a deliberately safe fallback fixture, if fallback
  validation is part of the change set.

Record live validation by issue number, URL, operation type, command shape, and
result summary. Do not record raw token, verbose HTTP logs, or private host
paths.

## Security validation

- Run Codex Security diff-focused review for the adapter and changed policy docs,
  or record why a narrower action is sufficient.
- Confirm the adapter uses `subprocess.run` with an argument list and JSON stdin.
- Confirm core and adapter description commands do not invoke `gh`.
- Confirm mutation commands require `--execute`.
- Confirm live mutation requires Config authorization or `--mutation-policy-ref`.
- Confirm dry-run output records the operation without invoking `gh`.
- Confirm Config-aware mutation refuses blocking, unsupported, malformed, or
  missing projection decisions before invoking `gh`.
- Confirm live mutation preflights duplicate-prone writes and idempotent no-op
  writes before invoking the write request.
- Confirm sub-issue writes resolve issue numbers to REST issue ids before
  writing, preview planned preflights in dry-run output, and reconcile fallback
  records through native sub-issue list reads.
- Confirm failed live mutation can produce an explicit fallback record with
  retry condition and compensation guidance when requested.

## Documentation validation

- Inspect affected agent-facing docs: `AGENTS.md`, `CONTEXT.md`,
  `docs/agent-equipment-forge.md`,
  `docs/smith-runbook.md`, and `docs/agents/issue-tracker.md`.
- Inspect affected human-facing docs: `README.md`, `docs/README.md`, and
  `docs/forge-tour.md`.
- Update stale or incomplete claims, or record unchanged rationale in closeout.

## Full-delivery validation

Full closure of issue #11 needs additional validation for onboarding, Issue Ops
config profile fields, configuration layering, policy conflicts, issue
selection, issue repair, fallback compatibility beyond bootstrap records,
permission failure, rate limiting, semantic duplicate detection, subtask
handling, and cross-issue orchestration.

Issue #13 validation specifically requires
[Config profile and onboarding](config-profile-and-onboarding.md), validator
coverage for that owner spec, bundle references from the other Issue Ops design
records, tracker drift correction for #13, and closeout evidence that #103,
#93/#99, #121, and #18 remain separate follow-ups.
