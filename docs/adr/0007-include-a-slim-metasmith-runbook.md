# Include a Slim Metasmith Runbook

The Framework Seed will include `docs/metasmith-runbook.md` as a concise canonical workflow for maintaining the Agent Equipment Framework. The runbook will cover repeatable Metasmith duties without absorbing ADRs, PRDs, implementation plans, or review transcripts.

## Considered Options

- Include a slim Metasmith runbook as a canonical workflow surface.
- Keep Metasmith behavior only in ADRs, PRDs, and implementation plans.
- Put detailed Metasmith process directly into root `AGENTS.md`.

## Consequences

- Framework maintenance duties become discoverable without bloating always-loaded agent instructions.
- The runbook should point to source handoff preservation, decision projection, review-until-clean quality gates, harness fact refresh, and downstream Smith spec creation.
- Specific project execution details still belong in PRDs, plans, specs, and ADRs.
