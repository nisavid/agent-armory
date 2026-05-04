# Include a Slim Forgewright Runbook

The Forge Seed will include `docs/forgewright-runbook.md` as a concise canonical workflow for maintaining the Agent Equipment Forge. The runbook will cover repeatable Forgewright duties without absorbing ADRs, PRDs, implementation plans, or review transcripts.

## Considered Options

- Include a slim Forgewright runbook as a canonical workflow surface.
- Keep Forgewright behavior only in ADRs, PRDs, and implementation plans.
- Put detailed Forgewright process directly into root `AGENTS.md`.

## Consequences

- Framework maintenance duties become discoverable without bloating always-loaded agent instructions.
- The runbook should point to source handoff preservation, decision projection, review-until-clean quality gates, harness fact refresh, and downstream Smith spec creation.
- Specific project execution details still belong in PRDs, plans, specs, and ADRs.
