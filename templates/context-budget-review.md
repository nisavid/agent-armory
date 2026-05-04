# Context Budget Review

Status: Template

## Scope

Name the change set, capability, or document group being reviewed.

## Always-loaded context

List content that enters the root agent context before scouting, including
`AGENTS.md` routes and short policy pointers.

## On-demand context

List files, skills, references, scripts, and catalogs that should load only when
the task calls for them.

## Budget risks

Identify duplication, long rationale, scoutable facts, inventories, command
catalogs, examples, and stale history that may consume context without improving
decisions.

## Relocation decisions

State what stayed always loaded, what moved behind a route, what became
deterministic validation, and what was removed as obsolete or scoutable.

## Verification

Confirm that a future agent can find the needed route in zero scout passes when
that is required, and that bulky details are reachable without being preloaded.
