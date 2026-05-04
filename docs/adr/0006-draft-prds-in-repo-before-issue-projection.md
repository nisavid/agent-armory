# Draft PRDs in Repo Before Issue Projection

Forge Seed PRDs will be drafted in the worktree before they are projected into GitHub Issues. The repo draft gives agents and reviewers a durable artifact for review-until-clean cycles, while the issue tracker remains the tracking surface once the PRD is stable enough to summarize.

## Considered Options

- Draft PRDs in the repo, then project stable summaries into GitHub Issues.
- Draft PRDs only in GitHub Issues.
- Keep PRDs only in repo docs and ignore the issue-tracker policy.

## Consequences

- The Forge Seed can use worktree-based review, diff, and validation workflows before issue publication.
- The implementation plan should include explicit Issue Projection after the repo PRD is reviewed and stable.
- After projection, the GitHub issue is the tracking surface. Material repo-draft PRD changes must include an explicit issue update or a note that issue projection is pending.
- Forge Seed closeout must either create or update the Published PRD Issue, or record why Issue Projection remains pending.
- Imported skill instructions are treated as workflow inputs, not automatically as repo policy.
