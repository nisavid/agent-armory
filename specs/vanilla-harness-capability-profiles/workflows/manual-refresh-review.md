# Manual Refresh Review Workflow

Status: Equipment Blueprint
Promotion state: specified

Use this workflow when a Smith manually refreshes Vanilla Harness Capability
Profiles through the Harness Capability Profile Manager Core.

## Inputs

- Supported harness id and refresh scope.
- Current profile file under `docs/harness-capabilities/vanilla/`.
- Curated scout input JSON.
- Selected Capability Profiling Protocol Study Reports, if any.
- Explicit profile or schema replacement candidates, if any.
- Security/control classification and operator approval references for any
  non-passive effect.

## Review Steps

1. Scout evidence into a Manual Refresh Scout Report.
   - Prefer first-party sources.
   - Label fallback sources, local observations, selected study reports,
     curated notes, hypotheses, and unknowns separately.
   - Record scratch evidence disposition.
   - Do not mutate canonical profile files.
2. Analyze claim impact.
   - Compare evidence with the current profile, prior evidence basis, schema
     pressure, version deltas, and similar claims in other harnesses.
   - Run Capability Claim Triage.
   - Keep stale, changed, hypothesis-backed, unsupported, and unknown claims
     visible.
3. Plan explicit mutations.
   - Prepare replacement profile or schema files through agent-guided judgment.
   - Use `plan` to validate replacements, record precondition hashes, planned
     content hashes, validation commands, evidence promotions, and follow-up
     candidates.
   - Treat the plan as review input, not as proof that the profile content is
     semantically correct.
4. Review diffs before apply.
   - Use `diff` to inspect every planned canonical file mutation.
   - Reject plans that hide raw scout caches or unrelated file edits.
5. Apply only with explicit approval.
   - Require `profile_mutation` approval and security/control references.
   - Refuse stale plans.
   - Write only planned canonical profile or schema content.
6. Audit the refresh.
   - Provide the apply result for mutation plans.
   - Provide the passing Manager Core validation result artifact from post-apply
     gates, plus any other passing closeout validation artifacts used as
     supporting evidence.
   - Record sources checked, profile files changed, claims added, changed,
     retired, unsupported, or left unknown, schema pressure, selected-rigor
     deviations, scratch disposition, validation results, and follow-up
     disposition.

Generated scout, analysis, plan, diff, apply, and audit outputs are JSON.
Manager Core `--write-output` paths must end in `.json` and must not point at
canonical profile or schema paths.

## Output Contract

The refresh closeout should name:

- scout, analysis, plan, diff, apply, and audit artifacts used;
- non-passive effects and their approval references;
- whether raw evidence stayed scratch or was promoted;
- exact canonical files changed;
- validation commands and results;
- follow-up issue candidates or accepted non-blocking unknowns.

Do not describe downstream Forge consumption behavior in refresh outputs. Keep
the outputs descriptive of harness integration surfaces and profile maintenance
evidence.
