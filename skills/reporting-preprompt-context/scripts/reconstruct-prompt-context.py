#!/usr/bin/env python3

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypedDict


class CountGroup(TypedDict):
    tokens: int
    count: int


class McpLocationGroup(TypedDict):
    tokens: int
    count: int
    groups: defaultdict[str, CountGroup]


class RuleSectionSpec(TypedDict):
    section: str
    block_tag: str
    entry_pattern: re.Pattern[str]
    path_attribute: str | None


class DuplicatePathCount(TypedDict):
    path: str
    count: int


class DuplicateSkill(TypedDict):
    skill: str
    target: str
    duplicate_kind: str
    count: int
    unique_path_count: int
    resolved_target_count: int
    tokens: int
    excess_count: int
    excess_tokens: int
    paths: list[str]
    resolved_targets: list[str]
    path_counts: list[DuplicatePathCount]


class DuplicateMcpServer(TypedDict):
    name: str
    count: int
    tokens: int
    excess_count: int
    excess_tokens: int


def default_workspace_root() -> Path:
    script_path = Path(__file__).resolve()
    for candidate in [script_path.parent, *script_path.parents]:
        if (candidate / ".agents").exists() or (candidate / "AGENTS.md").exists():
            return candidate
    return script_path.parents[4]


@dataclass(frozen=True)
class Config:
    workspace_root: Path
    home_dir: Path


DEFAULT_WORKSPACE_ROOT = default_workspace_root()
DEFAULT_HOME_DIR = Path.home()

SKILL_WRAPPER_PREFIX = """<agent_skills>
When users ask you to perform tasks, check if any of the available skills below can help complete the task more effectively. Skills provide specialized capabilities and domain knowledge. To use a skill, read the skill file at the provided absolute path using the ReadFile tool, then follow the instructions within. When a skill is relevant, read and follow it IMMEDIATELY as your first action. NEVER just announce or mention a skill without actually reading and following it. Only use skills listed below.


<available_skills description="Skills the agent can use. Use the ReadFile tool with the provided absolute path to fetch full contents.">
"""

SKILL_WRAPPER_SUFFIX = """
</available_skills>
</agent_skills>"""

WORKSPACE_RULE_PREFIX_TEMPLATE = '<always_applied_workspace_rule name="{path}">'
WORKSPACE_RULE_SUFFIX = "</always_applied_workspace_rule>"

MCP_WRAPPER_SUFFIX = """</mcp_file_system_servers>
</mcp_file_system>"""

PLUGIN_CACHE_MARKERS = ("/.cursor/plugins/cache/", "/.claude/plugins/cache/")
REPO_LOCAL_SKILL_ROOT_MARKERS = (
    "/.agents/skills/",
    "/.claude/skills/",
    "/.codex/skills/",
)
HOME_LOCAL_SKILL_ROOT_MARKERS = (
    "/.agents/skills/",
    "/.claude/skills/",
    "/.codex/skills/",
)
LOCAL_SKILL_ROOT_CANDIDATES = (".agents/skills", ".claude/skills", ".codex/skills")
PLUGIN_SKILL_CONTAINER_MARKERS = {".claude", ".agents", ".codex"}
STATUS_DESCRIPTION_PATTERNS = (
    re.compile(r"\bauthenticated user\b", re.I),
    re.compile(r"\blogged in\b", re.I),
    re.compile(r"\bconnected account\b", re.I),
)


class TokenCounter:
    def __init__(self, allow_proxy: bool) -> None:
        self.method = "o200k_base"
        self.approximate = False
        self._encoder = None
        try:
            import tiktoken  # type: ignore[import-not-found]

            self._encoder = tiktoken.get_encoding("o200k_base")
        except Exception:
            if not allow_proxy:
                raise
            self.method = "utf8_bytes_div_4_proxy"
            self.approximate = True

    def count(self, text: str) -> int:
        if self._encoder is not None:
            return len(self._encoder.encode(text))
        return int(round(len(text.encode("utf-8")) / 4))


def parse_description(frontmatter_text: str) -> str | None:
    lines = frontmatter_text.splitlines()
    for index, line in enumerate(lines):
        if not line.startswith("description:"):
            continue

        raw_value = line.partition(":")[2].strip()
        if raw_value in {">", ">-", ">+", "|", "|-", "|+"}:
            block_lines: list[str] = []
            for continuation in lines[index + 1 :]:
                if continuation.startswith((" ", "\t")):
                    block_lines.append(continuation.strip())
                    continue
                if not continuation.strip():
                    block_lines.append("")
                    continue
                break

            if raw_value.startswith(">"):
                description = " ".join(part for part in block_lines if part)
            else:
                description = "\n".join(block_lines).strip()
        else:
            description = raw_value

        if (
            len(description) >= 2
            and description[0] == description[-1]
            and description[0] in {'"', "'"}
        ):
            description = description[1:-1]
        return description

    return None


def read_description(skill_path: Path) -> str:
    text = skill_path.read_text()
    frontmatter_match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if frontmatter_match:
        description = parse_description(frontmatter_match.group(1))
        if description is not None:
            return description

    for line in text.splitlines():
        stripped = line.strip()
        if stripped and stripped != "---":
            return stripped
    return ""


def skill_entry(skill_path: Path) -> str:
    return f'<agent_skill fullPath="{skill_path}">{read_description(skill_path)}</agent_skill>'


def workspace_rule_entry(rule_path: Path) -> str:
    return (
        WORKSPACE_RULE_PREFIX_TEMPLATE.format(path=rule_path)
        + rule_path.read_text()
        + WORKSPACE_RULE_SUFFIX
    )


def cursor_project_slug(config: Config) -> str:
    return config.workspace_root.as_posix().lstrip("/").replace("/", "-")


def live_mcp_root(config: Config) -> Path:
    return (
        config.home_dir / ".cursor" / "projects" / cursor_project_slug(config) / "mcps"
    )


def build_mcp_wrapper_prefix(mcp_root: Path) -> str:
    mcp_root_text = mcp_root.as_posix()
    return f"""<mcp_file_system>
You have access to MCP (Model Context Protocol) tools through the MCP FileSystem.

## MCP Tool Access

You have a `CallMcpTool` tool available that allows you to call any MCP tool from the enabled MCP servers. To use MCP tools effectively:

1. Discover Available Tools: Browse the MCP tool descriptors in the file system to understand what tools are available. Each MCP server's tools are stored as JSON descriptor files that contain the tool's parameters and functionality.
2. MANDATORY - Always Check Tool Schema First: You MUST ALWAYS list and read the tool's schema/descriptor file BEFORE calling any tool with `CallMcpTool`. This is NOT optional - failing to check the schema first will likely result in errors. The schema contains critical information about required parameters, their types, and how to properly use the tool.

The MCP tool descriptors live in the {mcp_root_text} folder. Each enabled MCP server has its own folder containing JSON descriptor files (for example, {mcp_root_text}/<server>/tools/tool-name.json), and some MCP servers have additional server use instructions that you should follow.

## MCP Resource Access

You also have access to MCP resources through the `ListMcpResources` and `FetchMcpResource` tools. MCP resources are read-only data provided by MCP servers. To discover and access resources:

1. Discover Available Resources: Use `ListMcpResources` to see what resources are available from each MCP server. Alternatively, you can browse the resource descriptor files in the file system at {mcp_root_text}/<server>/resources/resource-name.json.
2. Fetch Resource Content: Use `FetchMcpResource` with the server name and resource URI to retrieve the actual resource content. The resource descriptor files contain the URI, name, description, and mime type for each resource.
3. Authenticate MCP Servers When Needed: If you inspect a server's tools and it has an `mcp_auth` tool, you MUST call `mcp_auth` so the user can use that MCP server. Do not call `mcp_auth` in parallel. Authenticate only one server at a time.

Available MCP servers:

<mcp_file_system_servers>"""


def read_optional_text(path: Path) -> str | None:
    if not path.exists():
        return None
    text = path.read_text().strip()
    return text or None


def iter_status_description_lines(server_dir: Path) -> list[str]:
    tools_root = server_dir / "tools"
    if not tools_root.exists():
        return []

    descriptions: list[str] = []
    for tool_path in sorted(tools_root.glob("*.json")):
        try:
            payload = json.loads(tool_path.read_text())
        except Exception:
            continue
        description = payload.get("description")
        if not isinstance(description, str):
            continue
        first_line = description.strip().splitlines()[0]
        if any(pattern.search(first_line) for pattern in STATUS_DESCRIPTION_PATTERNS):
            descriptions.append(first_line)
    return descriptions


def build_server_use_instructions(server_dir: Path) -> str | None:
    instructions_parts: list[str] = []

    instructions = read_optional_text(server_dir / "INSTRUCTIONS.md")
    if instructions is not None:
        instructions_parts.append(instructions)

    for status_line in iter_status_description_lines(server_dir):
        if status_line not in instructions_parts:
            instructions_parts.append(status_line)

    if not instructions_parts:
        return None
    return "\n\n".join(instructions_parts)


def load_mcp_server_identifier(server_dir: Path) -> str:
    metadata_path = server_dir / "SERVER_METADATA.json"
    if not metadata_path.exists():
        raise RuntimeError(f"Missing MCP server metadata: {metadata_path}")

    metadata = json.loads(metadata_path.read_text())
    candidate = (
        metadata.get("serverIdentifier")
        or metadata.get("serverName")
        or server_dir.name
    )
    if not isinstance(candidate, str) or not candidate:
        raise RuntimeError(f"Invalid MCP server metadata: {metadata_path}")
    return candidate


def render_mcp_server_entry(server_dir: Path) -> str:
    server_name = load_mcp_server_identifier(server_dir)
    attribute_parts = [
        f'name="{html.escape(server_name, quote=True)}"',
        f'folderPath="{html.escape(server_dir.as_posix(), quote=True)}"',
    ]

    instructions = build_server_use_instructions(server_dir)
    if instructions is not None:
        attribute_parts.append(
            f'serverUseInstructions="{html.escape(instructions, quote=True)}"'
        )

    return (
        f"<mcp_file_system_server {' '.join(attribute_parts)}>"
        f"{html.escape(server_name)}"
        "</mcp_file_system_server>"
    )


def discover_mcp_server_directories(config: Config) -> list[Path]:
    mcp_root = live_mcp_root(config)
    if not mcp_root.exists():
        return []

    return sorted(
        path
        for path in mcp_root.iterdir()
        if path.is_dir() and (path / "SERVER_METADATA.json").exists()
    )


def canonical_skill_roots(base_dir: Path) -> list[Path]:
    roots: list[Path] = []
    for relative_root in LOCAL_SKILL_ROOT_CANDIDATES:
        skill_root = base_dir / relative_root
        if not skill_root.exists():
            continue
        roots.append(skill_root)
    return roots


def discover_skill_paths_in_root(skill_root: Path) -> list[Path]:
    if not skill_root.exists():
        return []
    return sorted(path for path in skill_root.glob("*/SKILL.md") if path.is_file())


def is_plugin_skill_path(skill_path: Path, plugin_cache_root: Path) -> bool:
    if skill_path.name != "SKILL.md":
        return False
    try:
        skill_path.relative_to(plugin_cache_root)
    except ValueError:
        return False

    if skill_path.parent.parent.name != "skills":
        return False

    container_name = skill_path.parent.parent.parent.name
    return (
        not container_name.startswith(".")
        or container_name in PLUGIN_SKILL_CONTAINER_MARKERS
    )


SKILL_ENTRY_PATTERN = re.compile(r"<agent_skill\b[^>]*>.*?</agent_skill>", re.S)
MCP_SERVER_ENTRY_PATTERN = re.compile(
    r"<mcp_file_system_server\b[^>]*>.*?</mcp_file_system_server>", re.S
)

RULE_SECTION_SPECS: list[RuleSectionSpec] = [
    {
        "section": "always_applied_workspace_rules",
        "block_tag": "always_applied_workspace_rules",
        "entry_pattern": re.compile(
            r"<always_applied_workspace_rule\b[^>]*>.*?</always_applied_workspace_rule>",
            re.S,
        ),
        "path_attribute": "name",
    },
    {
        "section": "agent_requestable_workspace_rules",
        "block_tag": "agent_requestable_workspace_rules",
        "entry_pattern": re.compile(
            r"<agent_requestable_workspace_rule\b[^>]*>.*?</agent_requestable_workspace_rule>",
            re.S,
        ),
        "path_attribute": "fullPath",
    },
    {
        "section": "user_rules",
        "block_tag": "user_rules",
        "entry_pattern": re.compile(r"<user_rule>.*?</user_rule>", re.S),
        "path_attribute": None,
    },
]

RULE_SECTION_OPEN_TAGS = {
    "always_applied_workspace_rules": (
        '<always_applied_workspace_rules description="These are workspace-level rules that the agent must always follow.">'
    ),
    "agent_requestable_workspace_rules": (
        '<agent_requestable_workspace_rules description="These are workspace-level rules that the agent should follow. Use the ReadFile tool with the provided absolute path to fetch full contents.">'
    ),
    "user_rules": '<user_rules description="These are rules set by the user that you should follow if appropriate.">',
}

RULE_SECTION_CLOSE_TAGS = {
    "always_applied_workspace_rules": "</always_applied_workspace_rules>",
    "agent_requestable_workspace_rules": "</agent_requestable_workspace_rules>",
    "user_rules": "</user_rules>",
}


def find_tag_blocks(text: str, tag_name: str) -> list[str]:
    return [
        match.group(0)
        for match in re.finditer(rf"<{tag_name}\b[^>]*>.*?</{tag_name}>", text, re.S)
    ]


def extract_attribute(tag_text: str, attribute_name: str) -> str | None:
    match = re.search(rf"{attribute_name}=([\"'])(.*?)\1", tag_text)
    if match:
        return match.group(2)
    return None


def require_attribute(tag_text: str, attribute_name: str, catalog_name: str) -> str:
    value = extract_attribute(tag_text, attribute_name)
    if value is None:
        snippet = " ".join(tag_text.split())[:160]
        raise ValueError(
            f"Malformed {catalog_name} catalog entry: missing `{attribute_name}` attribute in {snippet!r}"
        )
    return value


def summarize_occurrences(keys: list[str]) -> dict[str, int]:
    occurrence_count = len(keys)
    unique_key_count = len(set(keys))
    return {
        "entry_occurrence_count": occurrence_count,
        "unique_key_count": unique_key_count,
        "duplicate_occurrence_excess": occurrence_count - unique_key_count,
    }


def resolved_skill_target(skill_path: str) -> str:
    return str(Path(skill_path).expanduser().resolve())


def skill_identity(skill_path: str) -> str:
    return Path(skill_path).parent.name


def summarize_duplicate_skills(
    skill_entries: list[dict[str, str]], token_counter: TokenCounter
) -> dict[str, object]:
    entries_by_skill: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for entry in skill_entries:
        entries_by_skill[skill_identity(entry["path"])].append(entry)

    duplicate_skills: list[DuplicateSkill] = []
    for skill_name, skill_entries_for_name in entries_by_skill.items():
        if len(skill_entries_for_name) < 2:
            continue

        entry_tokens = [
            token_counter.count(entry["text"]) for entry in skill_entries_for_name
        ]
        paths = [entry["path"] for entry in skill_entries_for_name]
        path_counts = Counter(paths)
        resolved_targets = sorted({resolved_skill_target(path) for path in paths})
        duplicate_skills.append(
            {
                "skill": skill_name,
                "target": resolved_targets[0]
                if len(resolved_targets) == 1
                else skill_name,
                "duplicate_kind": "same_target"
                if len(resolved_targets) == 1
                else "same_name",
                "count": len(skill_entries_for_name),
                "unique_path_count": len(set(paths)),
                "resolved_target_count": len(resolved_targets),
                "tokens": sum(entry_tokens),
                "excess_count": len(skill_entries_for_name) - 1,
                "excess_tokens": sum(entry_tokens) - max(entry_tokens),
                "paths": sorted(set(paths)),
                "resolved_targets": resolved_targets,
                "path_counts": [
                    {"path": path, "count": count}
                    for path, count in sorted(path_counts.items())
                ],
            }
        )

    duplicate_skills.sort(
        key=lambda item: (-int(item["excess_tokens"]), str(item["target"]))
    )
    duplicate_entry_count = sum(int(item["count"]) for item in duplicate_skills)
    duplicate_excess_count = sum(int(item["excess_count"]) for item in duplicate_skills)
    duplicate_tokens = sum(int(item["tokens"]) for item in duplicate_skills)
    duplicate_excess_tokens = sum(
        int(item["excess_tokens"]) for item in duplicate_skills
    )
    return {
        "duplicate_target_count": len(duplicate_skills),
        "duplicate_target_entry_count": duplicate_entry_count,
        "duplicate_target_excess_count": duplicate_excess_count,
        "duplicate_target_tokens": duplicate_tokens,
        "duplicate_target_excess_tokens": duplicate_excess_tokens,
        "duplicate_targets": duplicate_skills,
    }


def summarize_duplicate_mcp_servers(
    mcp_entries: list[dict[str, str]], token_counter: TokenCounter
) -> dict[str, object]:
    entries_by_name: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for entry in mcp_entries:
        entries_by_name[entry["name"]].append(entry)

    duplicate_servers: list[DuplicateMcpServer] = []
    for server_name, server_entries in entries_by_name.items():
        if len(server_entries) < 2:
            continue

        entry_tokens = [token_counter.count(entry["text"]) for entry in server_entries]
        duplicate_servers.append(
            {
                "name": server_name,
                "count": len(server_entries),
                "tokens": sum(entry_tokens),
                "excess_count": len(server_entries) - 1,
                "excess_tokens": sum(entry_tokens) - max(entry_tokens),
            }
        )

    duplicate_servers.sort(
        key=lambda item: (-int(item["excess_tokens"]), str(item["name"]))
    )
    duplicate_entry_count = sum(int(item["count"]) for item in duplicate_servers)
    duplicate_excess_count = sum(
        int(item["excess_count"]) for item in duplicate_servers
    )
    duplicate_tokens = sum(int(item["tokens"]) for item in duplicate_servers)
    duplicate_excess_tokens = sum(
        int(item["excess_tokens"]) for item in duplicate_servers
    )
    return {
        "duplicate_server_count": len(duplicate_servers),
        "duplicate_server_entry_count": duplicate_entry_count,
        "duplicate_server_excess_count": duplicate_excess_count,
        "duplicate_server_tokens": duplicate_tokens,
        "duplicate_server_excess_tokens": duplicate_excess_tokens,
        "duplicate_servers": duplicate_servers,
    }


def count_catalog_from_blocks(
    text: str,
    block_tag: str,
    entry_pattern: re.Pattern[str],
    token_counter: TokenCounter,
) -> tuple[list[str], int]:
    blocks = find_tag_blocks(text, block_tag)
    if not blocks:
        return [match.group(0) for match in entry_pattern.finditer(text)], 0

    entries: list[str] = []
    wrapper_tokens = 0
    for block in blocks:
        block_entries = [match.group(0) for match in entry_pattern.finditer(block)]
        entry_tokens = sum(token_counter.count(entry) for entry in block_entries)
        wrapper_tokens += token_counter.count(block) - entry_tokens
        entries.extend(block_entries)

    return entries, wrapper_tokens


def classify_skill_location(skill_path: str, config: Config) -> str:
    if any(marker in skill_path for marker in PLUGIN_CACHE_MARKERS):
        return "plugin"

    if skill_path.startswith(str(config.home_dir / ".cursor" / "skills-cursor" / "")):
        return "cursor"

    if skill_path.startswith(str(config.workspace_root)):
        if any(marker in skill_path for marker in REPO_LOCAL_SKILL_ROOT_MARKERS):
            return "repo_local"

    if skill_path.startswith(str(config.home_dir)):
        if any(marker in skill_path for marker in HOME_LOCAL_SKILL_ROOT_MARKERS):
            return "home"

    return "others"


def plugin_skill_group_from_path(skill_path: str) -> str:
    cursor_public_match = re.search(r"/cursor-public/([^/]+)/", skill_path)
    if cursor_public_match:
        return cursor_public_match.group(1)

    for marker in PLUGIN_CACHE_MARKERS:
        if marker not in skill_path:
            continue
        suffix = skill_path.split(marker, 1)[1]
        first_segment = suffix.split("/", 1)[0]
        if first_segment:
            return first_segment

    return "others"


def group_semantic_skill_entries(
    skill_entries: list[dict[str, str]], location: str, token_counter: TokenCounter
) -> dict:
    prefix_counts: defaultdict[str, int] = defaultdict(int)
    for entry in skill_entries:
        skill_name = Path(entry["path"]).parent.name
        if "-" in skill_name:
            prefix_counts[skill_name.split("-", 1)[0]] += 1

    location_total = 0
    location_count = 0
    groups: defaultdict[str, dict[str, int]] = defaultdict(
        lambda: {"tokens": 0, "count": 0}
    )

    for entry in skill_entries:
        skill_name = Path(entry["path"]).parent.name
        if location == "cursor":
            group = "cursor"
        elif location == "plugin":
            group = plugin_skill_group_from_path(entry["path"])
        elif "-" in skill_name:
            prefix = skill_name.split("-", 1)[0]
            group = prefix if prefix_counts[prefix] >= 2 else "others"
        else:
            group = "others"

        tokens = token_counter.count(entry["text"])
        location_total += tokens
        location_count += 1
        groups[group]["tokens"] += tokens
        groups[group]["count"] += 1

    sorted_groups = [
        {"group": group, **payload}
        for group, payload in sorted(
            groups.items(), key=lambda item: (-item[1]["tokens"], item[0])
        )
    ]

    return {
        "location": location,
        "tokens": location_total,
        "count": location_count,
        "groups": sorted_groups,
    }


def build_skills_from_entry_texts(
    entries: list[str],
    wrapper_tokens: int,
    token_counter: TokenCounter,
    source: str,
    multiplicity_model: str,
    config: Config,
) -> dict:
    skill_entries = []
    for entry_text in entries:
        skill_path = require_attribute(entry_text, "fullPath", "skills")
        skill_entries.append({"path": skill_path, "text": entry_text})

    entries_by_location: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for entry in skill_entries:
        entries_by_location[classify_skill_location(entry["path"], config)].append(
            entry
        )

    location_totals = [
        group_semantic_skill_entries(location_entries, location, token_counter)
        for location, location_entries in entries_by_location.items()
    ]
    location_totals.sort(key=lambda item: (-item["tokens"], item["location"]))

    entry_total = sum(item["tokens"] for item in location_totals)
    multiplicity_summary = summarize_occurrences(
        [entry["path"] for entry in skill_entries]
    )
    duplicate_skill_summary = summarize_duplicate_skills(skill_entries, token_counter)
    return {
        "source": source,
        "multiplicity_model": multiplicity_model,
        "catalog_total_tokens": entry_total + wrapper_tokens,
        "entry_total_tokens": entry_total,
        "wrapper_tokens": wrapper_tokens,
        **multiplicity_summary,
        **duplicate_skill_summary,
        "location_totals": location_totals,
    }


def build_skills_from_prompt_text(
    prompt_text: str, token_counter: TokenCounter, config: Config
) -> dict:
    entries, wrapper_tokens = count_catalog_from_blocks(
        prompt_text,
        "agent_skills",
        SKILL_ENTRY_PATTERN,
        token_counter,
    )

    return build_skills_from_entry_texts(
        entries,
        wrapper_tokens,
        token_counter,
        source="prompt_text",
        multiplicity_model="prompt_occurrences",
        config=config,
    )


def longest_shared_plugin_prefix(
    server_names: list[str], target_name: str
) -> str | None:
    target_segments = target_name.split("-")[1:]
    if not target_segments:
        return None

    sibling_names = [name for name in server_names if name != target_name]
    for prefix_length in range(len(target_segments), 0, -1):
        prefix = target_segments[:prefix_length]
        if any(
            other.split("-")[1:][:prefix_length] == prefix for other in sibling_names
        ):
            return "-".join(collapse_adjacent_repeated_segments(prefix)).lower()
    return None


def collapse_adjacent_repeated_segments(segments: list[str]) -> list[str]:
    collapsed_segments: list[str] = []
    for segment in segments:
        if collapsed_segments and collapsed_segments[-1].lower() == segment.lower():
            continue
        collapsed_segments.append(segment)
    return collapsed_segments


def classify_mcp_group(
    server_name: str, plugin_server_names: list[str]
) -> tuple[str, str]:
    if not server_name.startswith("plugin-"):
        if server_name == "cursor-ide-browser":
            return "core", "browser"
        return "core", "others"

    shared_prefix = longest_shared_plugin_prefix(plugin_server_names, server_name)
    if shared_prefix:
        return "plugin", shared_prefix

    suffix = server_name[len("plugin-") :]
    first_segment = suffix.split("-", 1)[0]
    return "plugin", first_segment.lower() if first_segment else "others"


def build_mcps_from_entry_texts(
    entries: list[str],
    wrapper_tokens: int,
    token_counter: TokenCounter,
    source: str,
    multiplicity_model: str,
) -> dict:
    parsed_entries: list[dict[str, str]] = []
    for entry_text in entries:
        server_name = require_attribute(entry_text, "name", "MCP")
        parsed_entries.append({"name": server_name, "text": entry_text})

    plugin_server_names = [
        entry["name"] for entry in parsed_entries if entry["name"].startswith("plugin-")
    ]

    def empty_count_group() -> CountGroup:
        return {"tokens": 0, "count": 0}

    location_groups: defaultdict[str, McpLocationGroup] = defaultdict(
        lambda: {
            "tokens": 0,
            "count": 0,
            "groups": defaultdict(empty_count_group),
        }
    )

    entry_total = 0
    for entry in parsed_entries:
        location, group = classify_mcp_group(entry["name"], plugin_server_names)
        tokens = token_counter.count(entry["text"])
        entry_total += tokens
        location_groups[location]["tokens"] += tokens
        location_groups[location]["count"] += 1
        location_groups[location]["groups"][group]["tokens"] += tokens
        location_groups[location]["groups"][group]["count"] += 1

    location_totals: list[dict[str, Any]] = []
    for location, payload in location_groups.items():
        groups = [
            {"group": group, **group_payload}
            for group, group_payload in sorted(
                payload["groups"].items(),
                key=lambda item: (-item[1]["tokens"], item[0]),
            )
        ]
        location_totals.append(
            {
                "location": location,
                "tokens": payload["tokens"],
                "count": payload["count"],
                "groups": groups,
            }
        )
    location_totals.sort(key=lambda item: (-item["tokens"], item["location"]))

    multiplicity_summary = summarize_occurrences(
        [entry["name"] for entry in parsed_entries]
    )
    duplicate_server_summary = summarize_duplicate_mcp_servers(
        parsed_entries, token_counter
    )
    return {
        "source": source,
        "multiplicity_model": multiplicity_model,
        "catalog_total_tokens": entry_total + wrapper_tokens,
        "entry_total_tokens": entry_total,
        "wrapper_tokens": wrapper_tokens,
        **multiplicity_summary,
        **duplicate_server_summary,
        "location_totals": location_totals,
    }


def build_mcps_from_prompt_text(prompt_text: str, token_counter: TokenCounter) -> dict:
    entries, wrapper_tokens = count_catalog_from_blocks(
        prompt_text,
        "mcp_file_system",
        MCP_SERVER_ENTRY_PATTERN,
        token_counter,
    )

    return build_mcps_from_entry_texts(
        entries,
        wrapper_tokens,
        token_counter,
        source="prompt_text",
        multiplicity_model="prompt_occurrences",
    )


def classify_rule_group(
    section: str, entry_text: str, path_attribute: str | None
) -> str:
    if path_attribute is None:
        return "user_rule"

    rule_path = extract_attribute(entry_text, path_attribute)
    if rule_path is None:
        return "others"
    if rule_path.endswith("/AGENTS.md"):
        return "AGENTS.md"
    if rule_path.endswith("/CLAUDE.md"):
        return "CLAUDE.md"
    if "/.cursor/rules/" in rule_path:
        return ".cursor/rules"
    return Path(rule_path).name or "others"


def build_rules_from_prompt_text(prompt_text: str, token_counter: TokenCounter) -> dict:
    section_totals: list[dict[str, Any]] = []
    entry_total = 0
    wrapper_tokens = 0

    for spec in RULE_SECTION_SPECS:
        entries, section_wrapper_tokens = count_catalog_from_blocks(
            prompt_text,
            str(spec["block_tag"]),
            spec["entry_pattern"],
            token_counter,
        )
        wrapper_tokens += section_wrapper_tokens
        if not entries and section_wrapper_tokens == 0:
            continue

        groups: defaultdict[str, dict[str, int]] = defaultdict(
            lambda: {"tokens": 0, "count": 0}
        )
        section_entry_total = 0
        for entry_text in entries:
            group = classify_rule_group(
                spec["section"], entry_text, spec["path_attribute"]
            )
            tokens = token_counter.count(entry_text)
            section_entry_total += tokens
            groups[group]["tokens"] += tokens
            groups[group]["count"] += 1

        entry_total += section_entry_total
        section_totals.append(
            {
                "section": str(spec["section"]),
                "tokens": section_entry_total,
                "count": len(entries),
                "groups": [
                    {"group": group, **payload}
                    for group, payload in sorted(
                        groups.items(), key=lambda item: (-item[1]["tokens"], item[0])
                    )
                ],
            }
        )

    section_totals.sort(key=lambda item: (-item["tokens"], item["section"]))
    return {
        "source": "prompt_text",
        "catalog_total_tokens": entry_total + wrapper_tokens,
        "entry_total_tokens": entry_total,
        "wrapper_tokens": wrapper_tokens,
        "section_totals": section_totals,
    }


def normalize_manifest_path(
    spec_entry: object, *, field_names: tuple[str, ...]
) -> Path:
    if isinstance(spec_entry, str):
        return Path(spec_entry)
    if isinstance(spec_entry, dict):
        for field_name in field_names:
            raw_value = spec_entry.get(field_name)
            if isinstance(raw_value, str):
                return Path(raw_value)
    raise ValueError(f"Manifest entry must provide one of {field_names}")


def normalize_manifest_text(spec_entry: object, *, field_names: tuple[str, ...]) -> str:
    if isinstance(spec_entry, str):
        return spec_entry
    if isinstance(spec_entry, dict):
        for field_name in field_names:
            raw_value = spec_entry.get(field_name)
            if isinstance(raw_value, str):
                return raw_value
    raise ValueError(f"Manifest entry must provide one of {field_names}")


def lookup_mcp_entry_text(server_name: str, config: Config) -> str:
    for server_dir in discover_mcp_server_directories(config):
        if load_mcp_server_identifier(server_dir) == server_name:
            return render_mcp_server_entry(server_dir)
    raise ValueError(f"Unknown MCP server name in manifest spec: {server_name}")


def build_rules_prompt_text_from_manifest_spec(manifest_spec: dict) -> str:
    rules_spec = manifest_spec.get("rules")
    if not isinstance(rules_spec, dict):
        return ""

    sections: list[str] = []
    always_applied_entries = rules_spec.get("always_applied_workspace_rules", [])
    if always_applied_entries:
        section_lines = [RULE_SECTION_OPEN_TAGS["always_applied_workspace_rules"]]
        for spec_entry in always_applied_entries:
            rule_path = normalize_manifest_path(
                spec_entry, field_names=("path", "fullPath", "name")
            )
            section_lines.append(workspace_rule_entry(rule_path))
        section_lines.append(RULE_SECTION_CLOSE_TAGS["always_applied_workspace_rules"])
        sections.append("\n".join(section_lines))

    requestable_entries = rules_spec.get("agent_requestable_workspace_rules", [])
    if requestable_entries:
        section_lines = [RULE_SECTION_OPEN_TAGS["agent_requestable_workspace_rules"]]
        for spec_entry in requestable_entries:
            if isinstance(spec_entry, dict):
                rule_path = normalize_manifest_path(
                    spec_entry, field_names=("path", "fullPath", "name")
                )
                description = normalize_manifest_text(
                    spec_entry, field_names=("description", "text")
                )
            else:
                raise ValueError(
                    "Requestable rule manifest entries must be objects with path and description fields"
                )
            section_lines.append(
                f'<agent_requestable_workspace_rule fullPath="{rule_path}">{description}</agent_requestable_workspace_rule>'
            )
        section_lines.append(
            RULE_SECTION_CLOSE_TAGS["agent_requestable_workspace_rules"]
        )
        sections.append("\n".join(section_lines))

    user_rule_entries = rules_spec.get("user_rules", [])
    if user_rule_entries:
        section_lines = [RULE_SECTION_OPEN_TAGS["user_rules"]]
        for spec_entry in user_rule_entries:
            if not isinstance(spec_entry, str):
                raise ValueError("User rule manifest entries must be strings")
            rule_text = spec_entry
            section_lines.append(f"<user_rule>{rule_text}</user_rule>")
        section_lines.append(RULE_SECTION_CLOSE_TAGS["user_rules"])
        sections.append("\n".join(section_lines))

    return "\n\n".join(sections)


def build_skills_from_manifest_spec(
    manifest_spec: dict, token_counter: TokenCounter, config: Config
) -> dict:
    skills_spec = manifest_spec.get("skills", [])
    entries = [
        skill_entry(
            normalize_manifest_path(spec_entry, field_names=("path", "fullPath"))
        )
        for spec_entry in skills_spec
    ]
    if not entries:
        return build_skills_from_entry_texts(
            [],
            0,
            token_counter,
            source="manifest_spec",
            multiplicity_model="explicit_occurrence_spec",
            config=config,
        )

    wrapper_tokens = token_counter.count(SKILL_WRAPPER_PREFIX) + token_counter.count(
        SKILL_WRAPPER_SUFFIX
    )
    return build_skills_from_entry_texts(
        entries,
        wrapper_tokens,
        token_counter,
        source="manifest_spec",
        multiplicity_model="explicit_occurrence_spec",
        config=config,
    )


def build_mcps_from_manifest_spec(
    manifest_spec: dict, token_counter: TokenCounter, config: Config
) -> dict:
    mcp_spec = manifest_spec.get("mcps", [])
    entries: list[str] = []
    for spec_entry in mcp_spec:
        if isinstance(spec_entry, str):
            entries.append(lookup_mcp_entry_text(spec_entry, config))
            continue
        if isinstance(spec_entry, dict):
            if isinstance(spec_entry.get("entry_text"), str):
                entries.append(str(spec_entry["entry_text"]))
                continue
            if isinstance(spec_entry.get("name"), str):
                entries.append(lookup_mcp_entry_text(str(spec_entry["name"]), config))
                continue
        raise ValueError("MCP manifest entries must provide `name` or `entry_text`")

    if not entries:
        return build_mcps_from_entry_texts(
            [],
            0,
            token_counter,
            source="manifest_spec",
            multiplicity_model="explicit_occurrence_spec",
        )

    wrapper_tokens = token_counter.count(
        build_mcp_wrapper_prefix(live_mcp_root(config))
    ) + token_counter.count(MCP_WRAPPER_SUFFIX)
    return build_mcps_from_entry_texts(
        entries,
        wrapper_tokens,
        token_counter,
        source="manifest_spec",
        multiplicity_model="explicit_occurrence_spec",
    )


def build_rules_from_manifest_spec(
    manifest_spec: dict, token_counter: TokenCounter
) -> dict:
    prompt_text = build_rules_prompt_text_from_manifest_spec(manifest_spec)
    rules = build_rules_from_prompt_text(prompt_text, token_counter)
    rules["source"] = "manifest_spec"
    return rules


def derive_agents_md_from_rules(rules: dict) -> dict | None:
    for section in rules.get("section_totals", []):
        for group in section.get("groups", []):
            if group["group"] == "AGENTS.md":
                return {
                    "tokens": group["tokens"],
                    "count": group["count"],
                    "status": "measured",
                }
    return None


def discover_plugin_skill_paths(config: Config) -> list[Path]:
    skill_paths: list[Path] = []
    for plugin_cache_root in [
        config.home_dir / ".cursor" / "plugins" / "cache",
        config.home_dir / ".claude" / "plugins" / "cache",
    ]:
        if not plugin_cache_root.exists():
            continue
        skill_paths.extend(
            path
            for path in plugin_cache_root.rglob("SKILL.md")
            if is_plugin_skill_path(path, plugin_cache_root)
        )
    return sorted(skill_paths)


def build_skills(token_counter: TokenCounter, config: Config) -> dict:
    repo_skill_paths = [
        skill_path
        for skill_root in canonical_skill_roots(config.workspace_root)
        for skill_path in discover_skill_paths_in_root(skill_root)
    ]
    home_skill_paths = [
        skill_path
        for skill_root in canonical_skill_roots(config.home_dir)
        for skill_path in discover_skill_paths_in_root(skill_root)
    ]
    cursor_skill_paths = discover_skill_paths_in_root(
        config.home_dir / ".cursor" / "skills-cursor"
    )
    plugin_skill_paths = discover_plugin_skill_paths(config)

    entries = [
        skill_entry(skill_path)
        for skill_path in repo_skill_paths
        + home_skill_paths
        + cursor_skill_paths
        + plugin_skill_paths
    ]
    wrapper_tokens = token_counter.count(SKILL_WRAPPER_PREFIX) + token_counter.count(
        SKILL_WRAPPER_SUFFIX
    )
    return build_skills_from_entry_texts(
        entries,
        wrapper_tokens,
        token_counter,
        source="filesystem",
        multiplicity_model="unique_manifest_entries_only",
        config=config,
    )


def build_mcps(token_counter: TokenCounter, config: Config) -> dict:
    entries = [
        render_mcp_server_entry(server_dir)
        for server_dir in discover_mcp_server_directories(config)
    ]
    wrapper_tokens = token_counter.count(
        build_mcp_wrapper_prefix(live_mcp_root(config))
    ) + token_counter.count(MCP_WRAPPER_SUFFIX)
    return build_mcps_from_entry_texts(
        entries,
        wrapper_tokens,
        token_counter,
        source="filesystem",
        multiplicity_model="unique_manifest_entries_only",
    )


def build_agents_md(token_counter: TokenCounter, config: Config) -> dict | None:
    agents_path = config.workspace_root / "AGENTS.md"
    if not agents_path.exists():
        return None

    return {
        "path": str(agents_path),
        "tokens": token_counter.count(workspace_rule_entry(agents_path)),
        "status": "reconstructed",
    }


def build_rules_from_filesystem(token_counter: TokenCounter, config: Config) -> dict:
    rule_paths: list[Path] = []
    for candidate in [
        config.workspace_root / "AGENTS.md",
        config.workspace_root / "CLAUDE.md",
    ]:
        if candidate.exists():
            rule_paths.append(candidate)

    cursor_rules_root = config.workspace_root / ".cursor" / "rules"
    if cursor_rules_root.exists():
        rule_paths.extend(
            path for path in cursor_rules_root.rglob("*") if path.is_file()
        )

    section_tokens = 0
    groups: defaultdict[str, dict[str, int]] = defaultdict(
        lambda: {"tokens": 0, "count": 0}
    )
    for rule_path in rule_paths:
        entry_text = workspace_rule_entry(rule_path)
        tokens = token_counter.count(entry_text)
        section_tokens += tokens
        group = classify_rule_group(
            "always_applied_workspace_rules", entry_text, "name"
        )
        groups[group]["tokens"] += tokens
        groups[group]["count"] += 1

    section_totals = []
    if rule_paths:
        section_totals.append(
            {
                "section": "always_applied_workspace_rules",
                "tokens": section_tokens,
                "count": len(rule_paths),
                "groups": [
                    {"group": group, **payload}
                    for group, payload in sorted(
                        groups.items(), key=lambda item: (-item[1]["tokens"], item[0])
                    )
                ],
            }
        )

    return {
        "source": "filesystem",
        "catalog_total_tokens": section_tokens,
        "entry_total_tokens": section_tokens,
        "wrapper_tokens": 0,
        "section_totals": section_totals,
    }


def add_known_total(
    result: dict,
    system_visible: int | None,
    workspace_context_other: int | None,
    current_turn_overhead: int | None,
) -> None:
    known_components = {
        "rules_catalog": result["rules"]["catalog_total_tokens"]
        if result.get("rules")
        else None,
        "skills_catalog": result["skills"]["catalog_total_tokens"],
        "mcp_catalog": result["mcps"]["catalog_total_tokens"],
    }
    known_components = {
        key: value for key, value in known_components.items() if value is not None
    }
    if system_visible is not None:
        known_components["system"] = system_visible
    if workspace_context_other is not None:
        known_components["workspace_context_other"] = workspace_context_other
    if current_turn_overhead is not None:
        known_components["current_turn_overhead"] = current_turn_overhead

    known_total = sum(known_components.values())
    result["known_total"] = {
        "components": known_components,
        "tokens": known_total,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Measure prompt-context rules, skill catalogs, and MCP catalogs."
    )
    parser.add_argument("--workspace-root", default=str(DEFAULT_WORKSPACE_ROOT))
    parser.add_argument("--home-dir", default=str(DEFAULT_HOME_DIR))
    parser.add_argument("--prompt-text-file")
    parser.add_argument("--prompt-text-stdin", action="store_true")
    parser.add_argument("--manifest-spec-file")
    parser.add_argument("--allow-filesystem-fallback", action="store_true")
    parser.add_argument("--system-visible", type=int)
    parser.add_argument("--workspace-context-other", type=int)
    parser.add_argument("--current-turn-overhead", type=int)
    parser.add_argument("--allow-proxy", action="store_true")
    parser.add_argument("--proxy-after-tiktoken-failure", action="store_true")
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = Config(
        workspace_root=Path(args.workspace_root).resolve(),
        home_dir=Path(args.home_dir).resolve(),
    )

    if args.allow_proxy and not args.proxy_after_tiktoken_failure:
        print(
            json.dumps(
                {
                    "error": "proxy_acknowledgement_required",
                    "message": (
                        "Refusing eager proxy mode. First run without `--allow-proxy` so a missing "
                        "`tiktoken` surfaces as `tiktoken_unavailable`. Only then rerun with both "
                        "`--allow-proxy` and `--proxy-after-tiktoken-failure` if you explicitly want "
                        "the approximate fallback."
                    ),
                },
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1

    prompt_source_count = (
        int(bool(args.prompt_text_file))
        + int(bool(args.prompt_text_stdin))
        + int(bool(args.manifest_spec_file))
    )
    if prompt_source_count > 1:
        print(
            json.dumps(
                {
                    "error": "multiple_prompt_snapshot_sources",
                    "message": (
                        "Pass only one of `--prompt-text-file`, `--prompt-text-stdin`, or "
                        "`--manifest-spec-file`."
                    ),
                },
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1

    if (
        not args.prompt_text_file
        and not args.prompt_text_stdin
        and not args.manifest_spec_file
        and not args.allow_filesystem_fallback
    ):
        print(
            json.dumps(
                {
                    "error": "prompt_snapshot_required",
                    "message": (
                        "Refusing to silently reconstruct from filesystem manifests. "
                        "Pass `--prompt-text-file`, `--prompt-text-stdin`, or `--manifest-spec-file` "
                        "for repeat-preserving prompt-based counting, or pass `--allow-filesystem-fallback` "
                        "if you explicitly want an approximate filesystem reconstruction."
                    ),
                },
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1

    try:
        token_counter = TokenCounter(args.allow_proxy)
    except Exception as error:
        print(
            json.dumps(
                {
                    "error": "tiktoken_unavailable",
                    "message": (
                        "Install `tiktoken` in a temporary environment, or if you explicitly want the "
                        "approximate fallback after this failure, rerun with both `--allow-proxy` and "
                        "`--proxy-after-tiktoken-failure`."
                    ),
                    "details": str(error),
                },
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1

    try:
        manifest_spec: dict | None = None
        if args.manifest_spec_file:
            manifest_spec = json.loads(Path(args.manifest_spec_file).read_text())

        system_visible = args.system_visible
        workspace_context_other = args.workspace_context_other
        current_turn_overhead = args.current_turn_overhead
        if manifest_spec is not None:
            if system_visible is None and isinstance(
                manifest_spec.get("system_visible"), int
            ):
                system_visible = int(manifest_spec["system_visible"])
            if workspace_context_other is None and isinstance(
                manifest_spec.get("workspace_context_other"), int
            ):
                workspace_context_other = int(manifest_spec["workspace_context_other"])
            if current_turn_overhead is None and isinstance(
                manifest_spec.get("current_turn_overhead"), int
            ):
                current_turn_overhead = int(manifest_spec["current_turn_overhead"])

        if args.prompt_text_file or args.prompt_text_stdin:
            if args.prompt_text_file:
                prompt_text = Path(args.prompt_text_file).read_text()
            else:
                prompt_text = sys.stdin.read()
            rules = build_rules_from_prompt_text(prompt_text, token_counter)
            skills = build_skills_from_prompt_text(prompt_text, token_counter, config)
            mcps = build_mcps_from_prompt_text(prompt_text, token_counter)
            agents_md = derive_agents_md_from_rules(rules)
        elif manifest_spec is not None:
            rules = build_rules_from_manifest_spec(manifest_spec, token_counter)
            skills = build_skills_from_manifest_spec(
                manifest_spec, token_counter, config
            )
            mcps = build_mcps_from_manifest_spec(manifest_spec, token_counter, config)
            agents_md = derive_agents_md_from_rules(rules)
        else:
            rules = build_rules_from_filesystem(token_counter, config)
            skills = build_skills(token_counter, config)
            mcps = build_mcps(token_counter, config)
            agents_md = derive_agents_md_from_rules(rules) or build_agents_md(
                token_counter, config
            )
    except Exception as error:
        print(
            json.dumps(
                {
                    "error": "prompt_context_reconstruction_failed",
                    "message": str(error),
                },
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1

    result = {
        "token_method": token_counter.method,
        "approximate": token_counter.approximate,
        "rules": rules,
        "agents_md": agents_md,
        "skills": skills,
        "mcps": mcps,
        "excluded": [
            "hidden_system_layers",
            "hidden_developer_layers",
            "opaque_transport_or_wrapper_overhead",
        ],
    }
    add_known_total(
        result,
        system_visible,
        workspace_context_other,
        current_turn_overhead,
    )

    if args.pretty:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
