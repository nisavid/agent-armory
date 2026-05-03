# Interface Decision Record: Documentation Research

Status: Framework Example
Promotion state: example

This Framework Example is not Published Agent Equipment and is not installable.
Trace: [capability card](capability-card.md) -> interface decision record -> [projected components](projected-components.md).

## Requirement

The documentation research capability needs a trigger for version-sensitive questions, deterministic local version discovery, read-only external retrieval tools, evidence labeling, and disclosure gates for private context.

## Decision

Use a skill for the trigger and research procedure, MCP/tools for live docs retrieval, scripts for local version inspection, local docs for source policy, config for provider and disclosure preferences, and hooks for citation or disclosure enforcement where the harness supports them.

## Chosen surface

- Skill: decide when docs lookup is required and how to summarize findings.
- MCP/tool: Context7, Firecrawl, web search, package registry, or source lookup.
- Hook: warn or block uncited version-sensitive claims when enforceable.
- Agent Profile: read-only docs researcher with restricted external access.
- Plugin: deferred bundle after provider contracts are validated.
- Script: dependency and tool-version inspector.
- Config: preferred providers, source order, allowed query detail.
- Local docs: evidence taxonomy and project dependency policy.

## Rationale

The need for current documentation is situational, so a skill is appropriate for trigger judgment. Retrieval belongs in tools because it exposes live external state. Version extraction is deterministic and should be scripted. Disclosure control cannot rely on reminder text alone when private project details may leave the machine.

## Evidence category

Implementation inference. The example reflects the Framework method and current project policy but does not validate any provider integration.

## Harness-specific projection

- Codex: use Context7 for library and API docs when applicable; use Firecrawl or web search for broader web research; inspect local files for dependency versions.
- Claude Code: project to available docs tools and local commands after a Smith confirms provider behavior.
- Cursor: start with local docs and package files; defer external provider details.
- Hermes Agent, OpenCode, OpenClaw: defer until source-retrieval and citation surfaces are documented.

## Alternatives rejected

- Always-loaded docs catalog: rejected because current docs and dependency versions drift.
- General web search only: rejected because primary library docs and version-specific APIs need stronger evidence.
- Skill-only reminder: rejected because external retrieval, source parsing, and disclosure control need supporting surfaces.

## Risks

- External disclosure through search terms or copied error logs.
- False precision from docs for the wrong major version.
- Source overload when long docs are pasted into the main context.
- Fragile provider assumptions if a docs MCP changes schema or coverage.

## Maintenance notes

Review this decision when docs providers change, when the project adds private dependencies, when source-citation policy changes, or when repeated answers show stale or mismatched documentation.
