---
name: reporting-preprompt-context
description: Use when reporting pre-prompt token occupancy, default-context size, skill catalog size, MCP catalog size, or generating a compact prompt-context report for the current session or via `/prompt-context-report`.
---

# Reporting Pre-Prompt Context

## Overview

Default to the current session's pre-prompt scaffolding that can be reported: visible prompt-injected workspace/user context before the current request, with hidden `system` and `developer` layers named as exclusions unless their exact text is available.

Unless the user explicitly asks for full conversation-history accounting, **exclude ordinary prior chat turns** and focus on the default prompt payload.

Count prompt manifests, not on-demand file contents:

- `rules_catalog`: count the injected rule entries that are actually present, including prompt-listed `AGENTS.md`, `CLAUDE.md`, `.cursor/rules`, requestable rules, and user rules when visible
- skills: count the injected `<agent_skill ...>` catalog entries, not full `SKILL.md` bodies
- MCPs: count the injected MCP server metadata block, not tool or resource descriptor JSON files

## When to Use

- User asks about prompt tokens, pre-prompt tokens, or default-context occupancy
- User wants a reproducible prompt-context report at any point in a session
- User asks how much of the context window is consumed by skills or MCPs
- User invokes `/prompt-context-report`

Do not use this skill for whole-repository token audits, file-by-file codebase sizing, or arbitrary document token counts.

## Quick Reference

| Topic          | Default                                                                                                                                 |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| Scope          | Current session pre-prompt scaffolding                                                                                                  |
| Tokenizer      | Use a real tokenizer first, ideally `o200k_base`; use a proxy only after tokenizer setup fails                                          |
| Hidden parts   | Exclude what you cannot measure; label those exclusions clearly                                                                         |
| Model          | Prefer the latest `Gemini Pro`; otherwise ask whether to continue, using `AskQuestion` when available and plain chat otherwise          |
| Rules          | Count visible injected rule entries, not just canonical `AGENTS.md`                                                                     |
| Skills         | Count manifest entries only                                                                                                             |
| MCPs           | Count MCP prompt metadata only                                                                                                          |
| Duplicates     | Count every repeated entry in totals; report duplicate skill identities by skill directory name                                           |
| Grouping       | Report by `location`, with per-location `group` breakdown                                                                               |
| Output         | Use the renderer script when possible; when posting in chat, wrap the full report in a fenced `text` code block                        |
| Fallback       | Fail loudly without a prompt snapshot unless the user explicitly approves approximate fallback                                          |
| Reconstruction | If chat text is not directly tool-readable, jump straight to repeat-preserving manifest-spec mode                                       |

Read [references/grouping-and-format.md](references/grouping-and-format.md) before presenting the report.
Read [references/working-method.md](references/working-method.md) before counting tokens.
Prefer [scripts/run-prompt-context-report.py](scripts/run-prompt-context-report.py) as the default entrypoint. It bootstraps or reuses a `tiktoken`-capable Python environment, calls [scripts/reconstruct-prompt-context.py](scripts/reconstruct-prompt-context.py) with prompt-derived inputs, and renders the final chat report through [scripts/render-prompt-context-report.py](scripts/render-prompt-context-report.py).

Do not silently fall back to filesystem reconstruction for `/prompt-context-report`. If you do not have a prompt snapshot, stop and say so unless the user explicitly wants approximate fallback mode.

Passing visible prompt text to the helper through stdin or a short-lived temp file is acceptable and does not count as writing a saved snapshot artifact.

If you cannot conveniently pass the exact prompt text but you can enumerate the visible rule, skill, and MCP entries in order, use the helper's manifest-spec mode immediately. That mode can preserve multiplicity, but only if you repeat entries exactly as many times as they appear in the visible prompt. Use [references/manifest-spec.example.json](references/manifest-spec.example.json) as a shape reference only; do not save current-session prompt manifests in the skill directory.

## Implementation

1. Define the scope first

   - Default to the current session's pre-prompt payload
   - Exclude normal prior conversation turns unless the user explicitly asks for them
   - State the scope in one line near the top of the report

2. Prefer the best available model via explicit user choice

   - The latest `Gemini Pro` is the preferred model for faithful recall, accurate counting, and polished rendering
   - If the current model is not the latest `Gemini Pro`, or you cannot confirm that it is, ask the user before counting work using the available interaction mechanism
   - Use `AskQuestion` when the client provides it; otherwise ask in plain chat
   - Keep the prompt succinct and user-friendly
   - Put the recommendation text inside the question prompt itself, not in a separate assistant paragraph above the question UI or plain-chat question
   - Briefly explain there that the latest `Gemini Pro` is preferred for this task, and that GPT, Opus, Sonnet, and Composer are generally the next best options if the user wants to switch
   - Keep the question text in second person; do not rewrite that final clause into first person
   - Prefer a direct prompt such as: `The latest Gemini Pro tends to be the most reliable model for this report. GPT, Opus, Sonnet, and Composer are usually the next best options if you want to switch. Would you like to continue with the current model, or cancel so you can switch?`
   - Within a family, prefer medium-or-higher thinking or reasoning variants when configurable
   - Offer exactly two choices:
     - continue with the current model
     - cancel so you can switch models
   - If the user cancels, stop immediately
   - If the current model is already the latest `Gemini Pro`, continue without prompting

3. Keep the counting method consistent

   - Use a real tokenizer first, ideally `o200k_base` or another close match to the latest GPT-family tokenizer
   - Prefer `scripts/run-prompt-context-report.py` so tokenizer environment setup is handled deterministically instead of improvised by the model
   - Let the wrapper script reuse a working interpreter or bootstrap a temporary tokenizer environment before any proxy fallback is considered
   - Only if wrapper-level tokenizer bootstrap truly fails should the wrapper allow the approximate proxy path
   - Only if a real tokenizer still cannot be made to work should you say so and use one consistent proxy across the full report
   - Do not mix tokenizers inside one report

   - Follow the fast-path method from the working-method reference instead of improvising around transcripts or prompt discovery
   - If the prompt text is visible in the current conversation context and already easy to materialize, pass it to the helper via stdin or a short-lived temp file
   - If the chat text is not directly tool-readable or would take extra turns to materialize, jump straight to manifest-spec mode instead of forcing a snapshot-file workflow
   - If you must reconstruct from visible entry lists instead of verbatim prompt text, use the helper's manifest-spec mode and preserve repeated occurrences in order
   - Run the wrapper script first so tokenizer setup, reconstruction, and rendering are derived deterministically
   - Use the raw helper or renderer directly only for advanced/manual debugging

4. Separate measured, reconstructed, and excluded sections

   - `measured`: directly visible or exactly reconstructed prompt text
   - `reconstructed`: rebuilt from stable local files and prompt structure
   - `excluded`: hidden `system` / `developer` layers or anything not directly inspectable

5. Build the high-level breakdown first

   - Prefer non-overlapping buckets such as:
     - `rules_catalog` when visible injected rule entries are present
     - `system` when visible
     - `workspace_context_other` excluding anything already counted in `rules_catalog`
     - `skills_catalog`
     - `mcp_catalog`
     - `current_turn_overhead` when the session has extra injected reminders or attachments
   - Make the labels clear enough that the user can tell what is and is not double-counted
   - Treat the helper script's prompt-snapshot totals as the source of truth for `rules_catalog`, `skills_catalog`, and `mcp_catalog`
   - Do not invent a `developer` bucket or any other opaque remainder
   - Report a measurable subtotal and then list excluded hidden prompt parts explicitly
   - If the helper refuses to run because no prompt snapshot was provided, surface that as the blocker instead of bypassing it with fallback mode
   - Treat session-level metadata such as `agent_transcripts` as `workspace_context_other` when counted; reserve `current_turn_overhead` for per-turn injected blocks such as `git_status`, `open_and_recently_viewed_files`, or command wrappers

6. Reconstruct the skills catalog correctly

   - Count each prompted entry as:
     - `<agent_skill fullPath="...">description</agent_skill>`
   - Use the injected catalog, not the full contents of every `SKILL.md`

   - If the injected catalog is not fully visible, rebuild the entry text from stable local files and label the result `reconstructed`
   - If the same skill name appears multiple times from different sources, count each catalog entry separately
   - If the same exact skill entry appears multiple times in the visible prompt, count each prompted occurrence separately
   - If the same skill identity appears through multiple paths or repeated entries, still count every entry's token occupancy and surface the duplicate skill summary
   - Count skill catalog wrapper prose and wrapper tags only at the catalog-total level unless the user explicitly asks for wrapper-inclusive subgroup numbers
   - Group using the `location` and nested `group` rules from the reference file

7. Reconstruct the MCP catalog correctly

   - Count only the MCP prompt block: wrapper prose, server entries, and wrapper tags
   - If the live MCP block is not fully visible, rebuild the current server metadata block from the prompt-visible structure and local server list, then label it `reconstructed`

   - If the same exact MCP server entry appears multiple times in the visible prompt, count each prompted occurrence separately
   - In manifest-spec mode, prefer exact MCP `entry_text` when you already have it; use `name` only when locally discovered metadata is sufficient
   - Count MCP wrapper prose and wrapper tags only at the catalog-total level unless the user explicitly asks for wrapper-inclusive subgroup numbers
   - Do not count descriptor JSON files under `mcps/<server>/tools` or `mcps/<server>/resources`
   - Group servers using the `location` and nested `group` rules from the reference file

8. Present the report compactly

   - Lead with a high-level dashboard
   - Start with a decorated Unicode header sized to the content, using box-drawing characters such as `╔═╗║╚╝`
   - Use tree connectors such as `├──`, `└──`, and `│` so parent-child structure stays obvious
   - Render every quantified row, including leaf rows, with an accurate progress bar
   - Keep the bar column vertically aligned within each section and offset to the right of the tree for breathing room
   - Then show skills by `location`, with each location followed by its `group` breakdown
   - Then show MCPs by `location`, with each location followed by its `group` breakdown
   - If duplicate skills or MCPs exist, show a final `Duplicate entries (excess tokens)` breakdown with the same tree, bar, token, count, and share style as the other breakdowns
   - For duplicate skills, include marker labels such as `[◆ ●]` or `[◆×2]`, where each marker denotes a skill collection root, then define the markers in a report-width boxed collection legend that uses `~` for the home directory
   - When presenting the rendered report in chat, wrap the entire report in one fenced `text` code block so box drawing, tree connectors, bars, and spacing survive Markdown rendering
   - Use this chat wrapper shape:
     ```text
     <rendered report>
     ```
   - Sort locations by token count descending, then sort groups by token count descending within each location
   - Prefer the renderer script so layout details stay deterministic across models
   - Keep prose short and put caveats after the numbers, not before them
   - Stop after the fenced report; do not append reflective process notes or planning chatter unless the user asked for them

9. State exclusions explicitly
   - full skill bodies are excluded from catalog counts
   - MCP descriptor files and fetched resources are excluded

   - visible injected rule entries belong in `rules_catalog`; do not hide them inside `workspace_context_other`
   - if you excluded prior chat history, say so

## Validation

Run `python3 -m unittest discover -s "skills/reporting-preprompt-context/tests"` after changing the skill or its scripts.

The focused tests are [tests/test_reconstruct_prompt_context.py](tests/test_reconstruct_prompt_context.py), [tests/test_render_prompt_context_report.py](tests/test_render_prompt_context_report.py), and [tests/test_run_prompt_context_report.py](tests/test_run_prompt_context_report.py).

For docs or command changes, also run `git diff --check` and use `ReadLints` on changed Markdown, JSON, and Python files when available.

## Common Mistakes

- Counting only canonical `AGENTS.md` while ignoring other visible injected rule entries such as `CLAUDE.md` or `.cursor/rules`
- Counting full `SKILL.md` contents instead of the injected skill manifest entries
- Counting MCP tool or resource descriptor files instead of the MCP prompt block
- Guessing the opaque prompt layer with a convenient round number such as `20k` or `30k`
- Scanning the full plugin cache or a hard-coded plugin allowlist instead of the visible manifest set
- Folding `skills_catalog` and `mcp_catalog` into a larger workspace bucket without saying so
- Presenting hidden prompt parts as measured when they are actually excluded
- Using a visually noisy changelog instead of a compact dashboard
- Defaulting to `utf8_bytes / 4` for convenience without first trying to get a real tokenizer working
- Silently using filesystem reconstruction when prompt-snapshot mode was requested
- Claiming the prompt snapshot is unavailable just because tools cannot read conversation text directly, without either bridging readily available text through stdin/temp input or switching straight to manifest-spec mode
- Reconstructing visible catalogs from unique root globs or deduplicated path sets when duplicate prompt entries may exist
- Saving current-session prompt manifests as skill fixtures instead of using a short-lived temp file or a synthetic example
- Deduplicating symlinked, hardlinked, copied, or otherwise repeated skill entries instead of counting their full prompt occupancy and reporting duplicate skills
- Mixing tokenizers or counting methods inside one report
- Omitting the fenced `text` code block around the rendered report in chat, which can collapse the fixed-width layout
