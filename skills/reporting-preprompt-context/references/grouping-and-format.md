## Grouping Rules

Use `location` as the primary report section for both skills and MCPs, then break each location down by `group`. The goal is a compact report that preserves the most useful structure without flattening everything into one mixed table.

## Contents

- [Token Counting Discipline](#token-counting-discipline)
- [Skills](#skills)
- [MCPs](#mcps)
- [High-Level Breakdown](#high-level-breakdown)
- [Rules](#rules)
- [Presentation Rules](#presentation-rules)
- [Visual Format](#visual-format)
- [Caveat Line](#caveat-line)

## Token Counting Discipline

- Use a real tokenizer first, ideally `o200k_base` or another close match to the latest GPT-family tokenizer
- Only fall back to a proxy such as `utf8_bytes / 4` after an actual attempt to get `tiktoken` working has failed
- Use one tokenizer for the whole report
- Treat hidden prompt layers as `excluded` unless their exact text is visible
- Treat visible or exactly reconstructed prompt text as `measured` or `reconstructed`

## Skills

### Location

- `repo_local`: entry path is under the workspace-managed skill roots, including `.agents/skills/` and any verified symlinked discovery roots such as `.claude/skills/`
- `home`: entry path is under the user's home-level `.agents/skills/`
- `cursor`: entry path is under `.cursor/skills-cursor/`
- `plugin`: entry path is under `.cursor/plugins/cache/.../skills/`
- `others`: fallback only if the path does not fit the known buckets

### Group

- For `plugin` entries, use the containing plugin family from the path segment after `cursor-public/`
  - Example: `.../cursor-public/prisma/...` -> `prisma`
  - Example: `.../cursor-public/superpowers/...` -> `superpowers`
- If `cursor-public/` is not present, use the first meaningful segment under the plugin cache root
- If the cache layout is unfamiliar, fall back to `others` rather than guessing
- For `repo_local` and `home` entries, infer a semantic family from the first hyphen-delimited prefix only when at least two entries in the current catalog share that prefix
  - Common examples: `developing`, `understanding`, `vercel`, `firecrawl`, `gemini`, `using`, `writing`, `agent`, `create`, `hindsight`
- If the prefix appears only once or does not form a useful family, use `others`
- For `cursor` entries, default the group to `cursor`

### Duplicate Names

- Count duplicate names as separate entries when they appear multiple times in the injected catalog
- Group them by their actual source entry, not by deduplicated skill name
- If you reconstruct from a manifest spec instead of verbatim prompt text, repeat identical entries explicitly so multiplicity is preserved
- Keep current-session manifest specs in short-lived temp files; use [manifest-spec.example.json](manifest-spec.example.json) only as a synthetic shape reference
- If multiple catalog entries share the same skill identity, count every discovered entry and report a duplicate-skill summary instead of collapsing the entries

## MCPs

### Location

- `core`: server name does not start with `plugin-`
- `plugin`: server name starts with `plugin-`
- `others`: fallback only if the server name does not fit the known patterns

### Group

- For `plugin` servers, derive the group from the server name after `plugin-`
  - Use the longest stable family prefix that is shared by sibling servers in the current server list
  - `plugin-prisma-Prisma-Local` and `plugin-prisma-Prisma-Remote` -> `prisma`
  - `plugin-deploy-on-aws-awspricing`, `plugin-deploy-on-aws-awsiac`, and `plugin-deploy-on-aws-awsknowledge` -> `deploy-on-aws`
  - `plugin-context7-plugin-context7` -> `context7`
- If there are no sibling servers with the same family, use the first segment after `plugin-`, case-insensitively
- If no shared family prefix is obvious, use the first segment after `plugin-`
- If that is still ambiguous, fall back to `others`
- For `core` servers, prefer a small semantic label when obvious
  - `cursor-ide-browser` -> `browser`
- Otherwise use `others`
- If you reconstruct from a manifest spec instead of verbatim prompt text, repeat identical server entries explicitly so multiplicity is preserved

## High-Level Breakdown

Prefer non-overlapping buckets so the dashboard adds up cleanly:

- `rules_catalog` when visible injected rule entries are present
- `system` when visible
- `workspace_context_other`, excluding anything already counted in `rules_catalog`
  - Typical examples: session-level metadata such as `agent_transcripts` or similar non-rule pre-prompt blocks
- `skills_catalog`
- `mcp_catalog`
- `current_turn_overhead` when there are injected reminders, attachments, or similar per-turn additions
  - Typical examples: `git_status`, `open_and_recently_viewed_files`, and command wrappers attached to the current turn
- `known_total`
- `excluded_hidden_parts`

If you cannot split a bucket cleanly, say so rather than implying exact partitioning.

## Rules

### Section

- `always_applied_workspace_rules`: count each visible `<always_applied_workspace_rule ...>` occurrence separately
- `agent_requestable_workspace_rules`: count each visible `<agent_requestable_workspace_rule ...>` occurrence separately
- `user_rules`: count each visible `<user_rule>` occurrence separately

### Group

- For path-backed rule entries, preserve noteworthy sources such as `AGENTS.md`, `CLAUDE.md`, and `.cursor/rules`
- If an exact rule entry appears multiple times in the visible prompt, count each prompted occurrence separately
- For non-path-backed user rules, use `user_rule`

## Presentation Rules

- Lead with a compact dashboard first
- Then show rules by section when present
- Then show `skills by location`
- Under each skills location, show `groups within <location>`
- Then show `MCPs by location`
- Under each MCP location, show `groups within <location>`
- If duplicate skills or MCPs exist, add a final `Duplicate entries (excess tokens)` section after MCPs
- Group duplicate rows by catalog first, such as `skills` and `mcps`
- Render duplicate rows with the same tree, bar, token, count, and suffix style as the other sections, using excess-token counts for the numeric token column
- Sort duplicate rows by excess token count descending
- Show up to 20 duplicate rows per catalog by default; this is enough to expose broad bloat without overwhelming the report
- For duplicate skills, include symbolic collection markers on each skill label and a priority-elided collection-root legend:
  - `[◆ ●]` means the same skill identity appeared through two distinct skill collection roots
  - `[◆×2]` means the same collection contributed two entries for that skill
  - Render the legend as a boxed two-column grid with the legend title inline in the top border, not a long unwrapped line
  - Size the legend to match the width of the already-rendered report sections when possible
  - Replace the home directory with `~`
  - Prefer full collection-root paths when they fit
  - If a collection root must be elided, preserve the root marker (`~/`, `/`, or `./`), first path component, last path component, top-level collection/plugin/agent name, and final collection/plugin/agent name before filling remaining space with initial path content
  - If there are more collection roots than available markers, add `+N collections` to avoid implying that the marker list is complete
- Sort locations by token count descending
- Sort groups by token count descending within each location
- Render every quantified row with a bar, including dashboard rows, section/location rows, and leaf rows
- For each location row, show:
  - token total
  - entry count when applicable
  - share of the full skills or MCP bucket
  - status: `measured`, `reconstructed`, or `excluded`
- For each nested group row, show:
  - token total
  - entry count when applicable
  - share of the parent location
  - status: inherit the parent status when all child rows share it; otherwise mark the location or group as `mixed`

## Visual Format

Prefer a monospace code block for the main tables, using a Unicode box-drawing header, `broot`-style tree connectors, and Unicode block bars. Use `scripts/render-prompt-context-report.py` when possible so the layout stays deterministic.

The renderer script is the source of truth for the exact output shape. Avoid maintaining hand-written render examples here; they drift easily.

For chat output, wrap the entire rendered report in one fenced `text` code block. The renderer emits unfenced plain text so it remains useful in terminals and pipelines; the chat-facing wrapper belongs in the assistant response.

```text
<rendered report>
```

Box guidelines:

- Size the box to the longest content line so the right edge stays aligned
- Use `╔═╗║╚╝` for the frame; they are widely supported and look polished without Nerd Fonts
- Keep labels aligned as `Label : value`
- Use 1 space of padding inside the box on both sides when possible
- Prefer 3 short metadata lines such as `Scope`, `Tokenizer`, and `Method`

Tree guidelines:

- Use tree connectors such as `├──`, `└──`, and `│` so hierarchy remains readable at a glance
- Keep bars section-relative so the largest top-level row in a section fills the scale
- For leaf rows, scale the bar against the parent row so the child breakdown reads truthfully
- Render a bar for every quantified row, not just parent rows
- Prefer full blocks plus fractional blocks: `█▉▊▋▌▍▎▏`
- Prefer `░` as the empty track character
- Keep the scale fixed within a section, usually 20 columns
- Keep the opening `[` of the bar column vertically aligned within a section
- Offset the bar column to the right of the tree with a small, consistent gap
- Keep labels short and stable
- Use exact token counts in the main table; add rounded `k` values only if they materially improve scanability
- Avoid Nerd Font glyphs, Braille patterns, or characters with uneven terminal support
- A good visual target is the polish level of TUIs such as `rich`/`textual` progress bars for fractional fills and `btop` for dense, readable meters

## Caveat Line

End with a short caveat block when needed:

- what scope was included
- what was excluded
- which hidden prompt parts were excluded from token totals
