# Draft PRDs in Repo Before Issue Projection

Framework Seed PRDs will be drafted in the worktree before they are projected into GitHub Issues. The repo draft gives agents and reviewers a durable artifact for review-until-clean cycles, while the issue tracker remains the tracking surface once the PRD is stable enough to summarize.

## Considered Options

- Draft PRDs in the repo, then project stable summaries into GitHub Issues.
- Draft PRDs only in GitHub Issues.
- Keep PRDs only in repo docs and ignore the issue-tracker policy.

## Consequences

- The Framework Seed can use worktree-based review, diff, and validation workflows before issue publication.
- The implementation plan should include an explicit issue-tracker projection step after the PRD is reviewed.
- After projection, the GitHub issue is the tracking surface. Material repo-draft PRD changes must include an explicit issue update or a note that issue projection is pending.
- Imported skill instructions are treated as workflow inputs, not automatically as repo policy.
