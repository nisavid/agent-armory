## Fast Path

Use this method first. It is optimized for the actual ambiguities that tend to slow the report down.

## Contents

- [Scope First](#scope-first)
- [Prompt Text Sources](#prompt-text-sources)
- [What Not To Do](#what-not-to-do)
- [Tokenizer Order](#tokenizer-order)
- [Wrapper Script](#wrapper-script)
- [Counting Order](#counting-order)
- [Skills Method](#skills-method)
- [MCP Method](#mcp-method)
- [Output Shape](#output-shape)

Before doing any counting work:

1. Prefer the latest `Gemini Pro` for faithful recall, accurate counting, and polished rendering
2. If the current model is not the latest `Gemini Pro`, or you cannot confirm that it is, ask the user before counting using the available interaction mechanism
3. Keep the prompt succinct and user-friendly
4. Put that recommendation text inside the question prompt itself when using a question tool, or in the plain-chat question when no question tool is available
5. Briefly explain there that the latest `Gemini Pro` is preferred for this task, and that GPT, Opus, Sonnet, and Composer are generally the next best options if the user wants to switch
6. Keep the question text in second person; do not rewrite that final clause into first person
7. A good prompt shape is: `The latest Gemini Pro tends to be the most reliable model for this report. GPT, Opus, Sonnet, and Composer are usually the next best options if you want to switch. Would you like to continue with the current model, or cancel so you can switch?`
8. Within a family, prefer medium-or-higher thinking or reasoning variants when configurable
9. Offer exactly two choices, using `AskQuestion` when available and plain chat otherwise:
   - continue with the current model
   - cancel so you can switch models
10. If the user cancels, stop immediately
11. If the current model is already the latest `Gemini Pro`, continue without prompting
12. Run [scripts/run-prompt-context-report.py](../scripts/run-prompt-context-report.py) with prompt-derived input for the current session
13. Let the wrapper reuse or bootstrap a `tiktoken` environment before considering proxy fallback
14. Use the wrapper's rendered output by default; use `--json-only` only when you need to inspect or post-process the helper payload
15. Use its `rules`, `skills`, `mcps`, and `known_total` output as the base of the report
16. Add the current run's visible or separately measured `system`, `workspace_context_other`, and `current_turn_overhead`
17. Report the measurable subtotal from those buckets
18. List hidden prompt parts as excluded instead of estimating them

## Scope First

1. Default to the current session's pre-prompt/default-context scaffolding only
2. Exclude ordinary prior chat turns unless the user explicitly asks for them
3. Treat hidden `system` and `developer` layers as excluded unless their exact text is already available in the live prompt

## Prompt Text Sources

Use sources in this order:

1. **Live prompt text already present in the current conversation context**
   - This is the primary source of truth for the current session
   - Use it for the current command text, user-injected context blocks, visible rules, visible skill catalog entries, and visible MCP server metadata
2. **Manifest spec built from the current visible prompt entries**
   - Use `--manifest-spec-file` when you can enumerate the visible rules, skills, and MCPs in order but do not want to materialize the full prompt text
   - If the chat text is not directly tool-readable, jump straight here instead of spending extra turns trying to create a full prompt snapshot
   - Repeat entries exactly as many times as they appear in the visible prompt; do not dedupe by path, family, or server name
   - This mode is only as good as the occurrence list you provide
3. **Prompt snapshot file built from the current visible prompt text**
   - Prefer this when the exact prompt text is already easy to materialize
   - The helper script's `--prompt-text-file` mode preserves multiplicity and excludes non-injected cached items
   - Passing the same prompt text through stdin is equally valid when that is easier than creating a short-lived temp file
4. **Stable local files that let you reconstruct known prompt manifests**
   - For skills, rebuild the same manifest unit the prompt uses: `<agent_skill fullPath="...">description</agent_skill>`
   - When reconstructing from local files, use the frontmatter `description` field for that manifest entry and label the result `reconstructed`
   - Use the visible MCP server list and local server names to rebuild the MCP block when needed
5. **Clearly labeled exclusions**
   - Exclude hidden layers or prompt text you cannot directly inspect from token totals
   - When you supply `workspace_context_other`, exclude any rule content already counted in the helper's `rules` bucket

## What Not To Do

- Do not spend time searching local agent transcripts hoping they contain the hidden pre-prompt
- Do not assume the transcript is a complete source of truth for `system`, `developer`, or workspace-injected blocks
- Do not count full `SKILL.md` bodies or MCP descriptor JSON files just because those files are easy to read
- Do not glob the entire plugin cache or rely on hard-coded plugin allowlists as a first pass
- Do not invent a round opaque bucket such as `20k` or `30k`
- Do not add a derived hidden-layer remainder just to force a grand total
- Do not burn turns trying to force a full snapshot-file workflow when manifest-spec mode already has enough visible information

Local transcripts can still be useful for confirming what the command text looked like in a prior run, but they are not the main counting source for the default pre-prompt.

For `/prompt-context-report`, missing prompt-snapshot input is a blocker by default. Do not silently continue with filesystem reconstruction unless the user explicitly approves approximate fallback mode.

If the visible prompt text is already in the current conversation context and easy to materialize, bridge it into the helper via stdin or a short-lived temp file. That is still prompt-snapshot mode, not fallback mode.

If the visible chat text is not directly tool-readable, prefer manifest-spec mode over spending extra turns trying to materialize a full snapshot file.

If you instead build a manifest spec from the visible entry list, preserve occurrence order and multiplicity explicitly. A deduplicated root-glob reconstruction is not an exact snapshot.

## Tokenizer Order

Try tokenizers in this order:

1. **Reuse an existing local tokenizer environment**
   - If a temporary Python virtualenv with `tiktoken` already exists, reuse it
2. **Create an ephemeral tokenizer environment**
   - Prefer a temporary virtualenv outside the repo, such as `/tmp/tokenvenv` on Unix-like systems
   - Install `tiktoken` there so you do not modify repo dependencies
3. **Use one consistent proxy**
   - If `tiktoken` is still unavailable, use one explicit fallback such as `utf8_bytes / 4`
   - Label the result clearly as approximate
   - Do not pass `--allow-proxy` on the first helper run
   - Only after the helper fails with `tiktoken_unavailable` should you rerun with both `--allow-proxy` and `--proxy-after-tiktoken-failure`

Treat steps 1 and 2 as required, not optional niceties. Do not jump straight to `utf8_bytes / 4` just because it is faster or easier.

Prefer `o200k_base` when using `tiktoken`. If that exact tokenizer is unavailable for some reason, use the closest practical tokenizer for the latest GPT-family models and stay consistent across the full report.

Do not burn time probing multiple package ecosystems in the repo if a temporary external tokenizer environment is available. A quick existing-venv check plus a quick temporary `tiktoken` install is the intended fast path.

## Wrapper Script

Preferred invocation:

```bash
cd "/absolute/path/to/repo"
python3 "skills/reporting-preprompt-context/scripts/run-prompt-context-report.py" \
  --prompt-text-file "/tmp/prompt-snapshot.txt"
```

Equivalent stdin-based invocation:

```bash
cd "/absolute/path/to/repo"
python3 - <<'PY' > "/tmp/prompt-snapshot.txt"
print("""<prompt text here>""")
PY
python3 "skills/reporting-preprompt-context/scripts/run-prompt-context-report.py" \
  --prompt-text-file "/tmp/prompt-snapshot.txt"
```

Repeat-preserving manifest-spec invocation:

```bash
cd "/absolute/path/to/repo"
python3 "skills/reporting-preprompt-context/scripts/run-prompt-context-report.py" \
  --manifest-spec-file "/tmp/prompt-manifest-spec.json"
```

Example manifest spec shape:

```json
{
  "rules": {
    "always_applied_workspace_rules": ["/absolute/path/to/AGENTS.md", "/absolute/path/to/AGENTS.md"],
    "agent_requestable_workspace_rules": [
      {
        "path": "/absolute/path/to/rule.mdc",
        "description": "Rule summary shown in the prompt catalog"
      }
    ],
    "user_rules": ["A visible user rule"]
  },
  "skills": ["/absolute/path/to/skill/SKILL.md", "/absolute/path/to/skill/SKILL.md"],
  "mcps": [
    {
      "entry_text": "<mcp_file_system_server name=\"cursor-ide-browser\" folderPath=\"/absolute/path/to/mcps/cursor-ide-browser\">cursor-ide-browser</mcp_file_system_server>"
    },
    { "name": "cursor-ide-browser" }
  ]
}
```

If the visible prompt repeats an entry twice, the manifest spec must repeat it twice too.

For a synthetic template, see [manifest-spec.example.json](manifest-spec.example.json). Do not keep current-session manifest snapshots in the skill directory; use short-lived temp files for live runs.

For MCPs, prefer `entry_text` when you already have the exact visible server entry text. Use `name` when locally discovered metadata is sufficient.

When you already know the current run's visible non-catalog buckets, pass them too:

```bash
cd "/absolute/path/to/repo"
python3 "skills/reporting-preprompt-context/scripts/run-prompt-context-report.py" \
  --prompt-text-file "/tmp/prompt-snapshot.txt" \
  --system-visible 139 \
  --workspace-context-other 2938 \
  --current-turn-overhead 607
```

Run those from the repo root, or replace the relative script path with an absolute one.

For advanced/manual debugging, the underlying helper and renderer scripts still exist. The wrapper is the preferred entrypoint because it reuses or bootstraps a `tiktoken`-capable Python environment before proxy fallback is considered.

What it gives you:

- a `rules` bucket for visible injected rule entries such as `AGENTS.md`, `CLAUDE.md`, `.cursor/rules`, requestable rules, and user rules when present
- exact or proxy-counted skill catalog totals
- exact or proxy-counted MCP catalog totals
- a measurable known-total subtotal for the current run
- an explicit `excluded` list for hidden prompt parts that are out of scope

When both `--prompt-text-file` and `--prompt-text-stdin` are omitted, the helper now refuses to proceed unless `--allow-filesystem-fallback` is passed explicitly. Treat that fallback mode as an approximation, not proof of live prompt presence.

If wrapper-level tokenizer bootstrap fails, the wrapper may use the approximate proxy path as a last resort. Prefer fixing the tokenizer environment when practical.

`--manifest-spec-file` is the preferred reconstruction path when you have an ordered list of visible entries but not a verbatim prompt snapshot. It can preserve multiplicity if and only if your spec repeats those entries.

## Counting Order

Use this order so the report converges quickly:

1. Run the helper script
2. Render its JSON through the renderer script when possible
3. High-level dashboard buckets
4. Rules by section and noteworthy group when useful
5. Skills by location
6. Skills by nested group within each location
7. MCPs by location
8. MCPs by nested group within each location
9. Exclusions and caveats

## Skills Method

1. Rebuild each skill catalog entry as:
   - `<agent_skill fullPath="...">description</agent_skill>`
2. Count those entry strings, not the full `SKILL.md` contents
3. If you are using manifest-spec mode, repeat identical skill paths when the visible prompt repeats them
4. Roll them up by location first
5. Within each location, roll them up by group
6. Add wrapper prose and tags only at the catalog-total level unless the user explicitly asks for wrapper-inclusive subgroup numbers
7. Count every repeated or aliased path's token occupancy, including symlinked, hardlinked, copied, or otherwise duplicated skill entries
8. Surface duplicate skill identities as bloat signals instead of deduplicating them away
9. For duplicate skills, show the largest duplicate skill identities with collection markers such as `[◆ ●]` for distinct skill roots or `[◆×2]` for repeated entries from one root
10. Prefer the helper script's output over a fresh ad hoc reconstruction when the script and current snapshot agree

## MCP Method

1. Count the MCP prompt wrapper prose once at the top-level MCP total
2. Count each injected server entry from the MCP server list
3. If you are using manifest-spec mode, repeat identical servers when the visible prompt repeats them
4. Prefer exact `entry_text` when you already have the visible server entry text; otherwise `name` can rebuild from live local metadata
5. Roll server entries up by location first
6. Within each location, roll them up by group
7. Exclude `mcps/<server>/tools/*.json`, `resources/*.json`, and fetched resource contents
8. Prefer the helper script's output over a fresh ad hoc reconstruction when the script and current snapshot agree

## Output Shape

The renderer script is the preferred way to achieve the final layout. Avoid maintaining literal output mockups here; they drift more easily than the implementation.

When posting the report in chat, wrap the renderer output in one fenced `text` code block:

```text
<rendered report>
```

Render it with these section-level invariants:

- header with `Scope`, `Tokenizer`, and `Method`
- `High-level`
- `Rules by section` when present
- `Skills by location`
- `MCPs by location`
- `Duplicate entries (excess tokens)` after MCPs when duplicate skills or MCPs exist
- explicit excluded hidden parts
- tree connectors to show hierarchy
- aligned bars for every quantified row

The location rows answer "where is the prompt budget going?" The nested group rows answer "what within that location is responsible?"

Stop after the fenced report. Do not append reflective process notes or planning chatter unless the user asked for them.
