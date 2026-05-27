---
name: issue-ops-workflow-executor
description: Use when executing Issue Ops advisory workflows for issue review, repair, enrichment, refactor, assignment, duplicate review, selection, session pickup, or issue-set orchestration.
---

# Issue Ops Workflow Executor

Status: Implemented candidate

## Use when

- An agent needs to execute an Issue Ops advisory workflow.
- The workflow is issue review, repair, enrichment, refactor, assignment,
  duplicate review, selection, session pickup, or issue-set orchestration.
- The task should produce recommendations or candidate operations without
  directly mutating the tracker.

## Do not use when

- The task is MCP parity for Issue Ops workflow planning.
- The task is semantic duplicate scoring or recommendation ranking.
- The operator has already accepted a deterministic Issue Ops write plan and
  only needs the write command executed through the adapter gates.

## Preflight

1. Read the active issue, parent issue, linked PRD, and relevant repo-local
   Issue Ops policy surfaces.
2. Run or consume `describe-workflows`.
3. Select exactly one workflow ID from the described workflow contract.
4. Run `plan-workflow --adapter github-issues-baseline --workflow <workflow-id>`.
5. Treat the workflow plan as the source of truth for required context, read
   operations, candidate_write_operations, output sections, policy factors,
   and adapter-mapped operation plans.

## Procedure

1. Gather the workflow's required context with read-only issue, dependency,
   parent, sub-issue, documentation, and repository inspection.
2. Emit the workflow's configured output sections using the names and intent
   from the workflow plan.
3. Separate evidence, recommendations, candidate writes, and unresolved
   judgment so an operator can accept, reject, or revise each recommendation.
4. List candidate writes only as deterministic Issue Ops operation plans or
   dry-run command shapes derived from the workflow's adapter-mapped operation
   plans.
5. For fallback or unsupported adapter capabilities, name the limitation and
   propose the configured fallback surface instead of inventing a tracker write.

## Output contract

Return a structured report that includes:

- workflow ID and adapter;
- evidence boundary and context sources inspected;
- every required output section from the workflow plan;
- candidate operations keyed by Issue Ops operation ID;
- dry-run command shapes for accepted writes when available;
- policy factors applied;
- unresolved judgment and operator questions.

## Safety

- Do not perform direct `gh` writes.
- Do not perform direct GitHub MCP writes.
- Do not perform tracker mutation outside Issue Ops dry-run/write gates.
- Do not convert unresolved stakeholder judgment into hidden default policy.
- Do not disclose private session, host, or user-global policy details unless
  the active policy allows external disclosure.
- Accepted writes still require deterministic Issue Ops operations, dry-run
  review, explicit execute authority, and mutation policy evidence.

## Failure handling

- If `describe-workflows` or `plan-workflow` is unavailable, stop and report the
  missing deterministic contract.
- If required context cannot be read, mark the affected output sections as
  blocked instead of guessing.
- If adapter capability is fallback or unsupported, keep the recommendation
  advisory and identify the follow-up operation or issue.
