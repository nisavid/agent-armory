# Issue Tracker Ops

Status: Equipment Candidate
Promotion state: implemented for bootstrap MVP; full delivery remains open

This Forge Entry Bundle records the bootstrap design for Issue Tracker Ops
Equipment tracked by GitHub issue #11.

## Bundle contents

- [Capability card](capability-card.md)
- [Interface decision record](interface-decision-record.md)
- [Security and control classification](security-control-classification.md)
- [Pressure scenarios](pressure-scenarios.md)
- [Validation plan](validation-plan.md)
- [Closeout evidence plan](closeout-evidence-plan.md)

## Bootstrap surface

The bootstrap MVP is the GitHub Issues adapter at
`tools/issue_tracker_ops.py`. It uses the local `gh` CLI as the authenticated
transport and defaults write modes to dry-run output unless `--execute` is
provided.

The bootstrap scope covers direct issue create, issue update, issue comment, and
issue dependency operations for GitHub Issues without Projects. Full Issue
Tracker Ops delivery remains tracked in issue #11 and child issues.
