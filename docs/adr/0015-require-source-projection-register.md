# Require Source Projection Register

The Framework Seed will include `docs/metasmith/source-projection.md` as the auditable map from accepted Source Handoff requirements to canonical Framework Seed surfaces or explicit deferments. This register makes handoff coverage mechanically checkable instead of relying on reviewer memory of the preserved handoff bundle.

## Considered Options

- Add a Source Projection Register and validate it.
- Rely on PRD prose and review to ensure handoff coverage.
- Treat the preserved Source Handoff as the coverage record.

## Consequences

- Seed Validation can check for the register and required projection fields: `requirement_id`, `source_file`, `source_anchor`, `summary`, `disposition`, `target_path`, `deferment_reason`, and `validation_status`.
- Seed Validation can confirm accepted requirement ids, handoff manifest coverage, source file/anchor references, projected target paths, and deferred downstream target path syntax rather than trusting table prose.
- Metasmiths can audit where accepted handoff requirements landed.
- Deferred requirements must carry both a reason and a downstream target path, not just disappear from canonical docs.
