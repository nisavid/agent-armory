# Capability Card: Documentation Research

Status: Forge Example
Promotion state: example

This Forge Example is not Published Agent Equipment and is not installable.
Trace: capability card -> [interface decision record](interface-decision-record.md) -> projected components.

## Purpose

Retrieve current library, SDK, API, CLI, or cloud-service documentation before an agent answers or implements behavior that may have changed.

## Users

- Human operator: wants answers and implementation choices grounded in current primary docs.
- Root agent: needs a trigger for when memory is not enough.
- Specialist agent: researches a bounded dependency question.
- External system: documentation provider, package registry, or source repository.

## Target harnesses

- Codex: primary example target through Context7, Firecrawl, web search, or local dependency inspection.
- Other harnesses: deferred until available documentation-retrieval tools and citation expectations are mapped.

## Risks

- Security: docs lookup may disclose private dependency names, internal package versions, or proprietary stack details.
- Privacy: search queries can leak user intent or private project context.
- Reliability: stale, unofficial, or version-mismatched docs can produce wrong implementation guidance.
- Context budget: large docs pages can crowd out local requirements.
- Human workflow: over-citing docs can obscure the decision the user needs.

## External systems

- Documentation APIs or MCPs.
- Public web search and web pages.
- Package registries and release notes.
- Local dependency manifests and lockfiles.

## Side effects

Default side effect classification: external disclosure when a query leaves the local machine; read-only when using local docs or local dependency metadata.

Network access and query disclosure require the harness and operator policy to allow them.

## Needed Harness Components

- Skills: documentation-research trigger and source-selection procedure.
- MCP/tools: documentation lookup, web search, scrape, and package-version readers.
- Hooks: warn or block answers that cite uncategorized docs for version-sensitive claims.
- Agent Profiles: docs researcher with read-only web and local file access.
- Plugins: deferred bundle for cross-harness docs research.
- Scripts: dependency/version inspector.
- Config: preferred doc providers, query disclosure policy, source priority.
- Docs: local dependency policy and evidence taxonomy.

## Hard rules

- Prefer primary docs or source repositories.
- Match the relevant version when the project pins one.
- Record evidence category and source basis.
- Do not claim current behavior from memory when a current docs tool is available and applicable.
- Avoid sending private code, secrets, or broad internal context in docs queries.

## Deterministic checks

- Local dependency version extraction.
- Citation presence check for version-sensitive claims.
- Source URL and evidence category validation.
- Secret scan over generated query strings when private context is included.

## Output contract

A documentation research note with:

- exact question researched;
- sources consulted and evidence category;
- applicable version or version uncertainty;
- answer or implementation implication;
- unresolved gaps.

## Failure modes

- Docs provider unavailable: use another primary source or mark the claim as unresolved.
- Version cannot be determined: state the uncertainty and avoid version-specific certainty.
- Query would disclose sensitive context: ask for approval or rewrite to a generic query.
- Conflicting sources: prefer source or current official docs and record the conflict.

## Evidence

Evidence category: implementation inference for the equipment shape. Individual documentation answers would need documentation-supported or source-supported evidence.

## Open questions

- Which documentation providers should each harness prefer?
- What level of private project context may be included in external docs queries?
