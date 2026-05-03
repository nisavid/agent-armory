#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
import textwrap
from pathlib import Path, PurePosixPath
from typing import Any


BAR_WIDTH = 20
FULL_BLOCK = "█"
EMPTY_BLOCK = "░"
FRACTIONAL_BLOCKS = ("", "▏", "▎", "▍", "▌", "▋", "▊", "▉")
DEFAULT_SCOPE = "pre-prompt scaffolding; prior chat turns excluded"
DUPLICATE_MARKER_FAMILIES = (
    ("◆", "◇", "◈"),
    ("●", "○", "◉", "◌", "◍", "◎"),
    ("■", "□"),
    ("▲", "△"),
    ("▼", "▽"),
    ("◀", "◁"),
    ("▶", "▷"),
    ("★", "☆"),
    ("✦", "✧"),
    ("✚", "✖"),
    ("✶", "✷", "✸", "✹", "✺", "✻"),
)
DUPLICATE_MARKERS = tuple(
    family[variant_index]
    for variant_index in range(max(len(family) for family in DUPLICATE_MARKER_FAMILIES))
    for family in DUPLICATE_MARKER_FAMILIES
    if variant_index < len(family)
)
MAX_DUPLICATE_ROWS = 20
MIN_LEGEND_LABEL_WIDTH = 32
ELLIPSIS = "…"
HOME_PATH = str(Path.home())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render a prompt-context report from JSON"
    )
    parser.add_argument("--json-file")
    parser.add_argument("--scope-text", default=DEFAULT_SCOPE)
    return parser.parse_args()


def load_payload(json_file: str | None) -> dict[str, Any]:
    if json_file:
        return json.loads(Path(json_file).read_text(encoding="utf-8"))
    return json.loads(sys.stdin.read())


def human_tokenizer_label(payload: dict[str, Any]) -> str:
    token_method = str(payload.get("token_method", "unknown"))
    approximate = bool(payload.get("approximate"))

    if token_method == "o200k_base":
        label = "o200k_base (tiktoken)"
    elif token_method == "utf8_bytes_div_4_proxy":
        label = "utf8_bytes / 4 proxy"
    else:
        label = token_method

    if approximate:
        label += " approximate"
    return label


def derive_method_label(payload: dict[str, Any]) -> str:
    sources = {
        str(section.get("source"))
        for key in ("rules", "skills", "mcps")
        if isinstance(payload.get(key), dict)
        for section in [payload[key]]
        if section.get("source") is not None
    }

    if len(sources) != 1:
        if sources and sources.issubset({"prompt_text", "manifest_spec"}):
            return "prompt-derived mixed mode"
        return "mixed-source mode"

    source = next(iter(sources))
    if source == "prompt_text":
        return "prompt-text mode"
    if source == "manifest_spec":
        return "manifest-spec mode"
    if source == "filesystem":
        return "filesystem fallback mode"
    return source.replace("_", "-")


def render_header(scope_text: str, payload: dict[str, Any]) -> str:
    lines = [
        f"Scope     : {scope_text}",
        f"Tokenizer : {human_tokenizer_label(payload)}",
        f"Method    : {derive_method_label(payload)}",
    ]
    inner_width = max(len("PRE-PROMPT CONTEXT REPORT"), *(len(line) for line in lines))
    title = "PRE-PROMPT CONTEXT REPORT"
    title_with_padding = f" {title} "
    left_fill = (inner_width - len(title_with_padding)) // 2
    right_fill = inner_width - len(title_with_padding) - left_fill

    rendered_lines = [
        f"╔{'═' * max(left_fill + 1, 1)}{title_with_padding}{'═' * max(right_fill + 1, 1)}╗",
        *[f"║ {line.ljust(inner_width)} ║" for line in lines],
        f"╚{'═' * (inner_width + 2)}╝",
    ]
    return "\n".join(rendered_lines)


def render_bar(ratio: float, width: int = BAR_WIDTH) -> str:
    bounded_ratio = max(0.0, min(1.0, ratio))
    total_units = bounded_ratio * width
    full_units = int(total_units)
    remainder = total_units - full_units
    fractional_index = int(round(remainder * 8))

    if fractional_index == 8:
        full_units += 1
        fractional_index = 0

    full_units = min(full_units, width)
    fractional = FRACTIONAL_BLOCKS[fractional_index]
    empty_units = width - full_units - (1 if fractional else 0)
    return (FULL_BLOCK * full_units) + fractional + (EMPTY_BLOCK * max(empty_units, 0))


def source_status(source: str) -> str:
    if source == "prompt_text":
        return "measured"
    return "reconstructed"


def pluralize(count: int, singular: str, plural: str | None = None) -> str:
    if count == 1:
        return singular
    return plural or f"{singular}s"


def skill_name_from_target(target: str) -> str:
    path = PurePosixPath(target)
    if path.name == "SKILL.md":
        return path.parent.name
    return path.name or target


def skill_collection_root(skill_path: str) -> str:
    path = PurePosixPath(skill_path)
    if path.name == "SKILL.md":
        return str(path.parent.parent)
    return str(path.parent)


def normalize_home_path(path: str) -> str:
    if path == HOME_PATH:
        return "~"
    if path.startswith(f"{HOME_PATH}/"):
        return "~/" + path[len(HOME_PATH) + 1 :]
    return path


def path_prefix_and_parts(path: str) -> tuple[str, list[str]]:
    if path.startswith("~/"):
        return "~/", path[2:].split("/")
    if path.startswith("./"):
        return "./", path[2:].split("/")
    if path.startswith("/"):
        return "/", path[1:].split("/")
    return "", path.split("/")


def join_path_parts(prefix: str, parts: list[str]) -> str:
    return prefix + "/".join(part for part in parts if part)


def top_collection_part_count(parts: list[str]) -> int:
    for marker in ("cursor-public", "claude-plugins-official"):
        if marker in parts:
            marker_index = parts.index(marker)
            return min(len(parts), marker_index + 2)

    if "plugins" in parts and "cache" in parts:
        cache_index = parts.index("cache")
        return min(len(parts), cache_index + 2)

    for marker in (".agents", ".claude", ".cursor", ".codex"):
        if marker in parts:
            marker_index = parts.index(marker)
            return min(len(parts), marker_index + 2)

    return min(len(parts), 1)


def final_collection_part_count(parts: list[str]) -> int:
    if len(parts) >= 2 and parts[-1] in {"skills", "skills-cursor"}:
        return 2
    return min(len(parts), 1)


def compose_elided_path(
    prefix: str, parts: list[str], initial_count: int, final_count: int
) -> str:
    if initial_count + final_count >= len(parts):
        return join_path_parts(prefix, parts)
    return (
        join_path_parts(prefix, parts[:initial_count])
        + f"/{ELLIPSIS}/"
        + "/".join(parts[-final_count:])
    )


def middle_elide_text(text: str, width: int) -> str:
    if len(text) <= width:
        return text
    if width <= len(ELLIPSIS):
        return ELLIPSIS[:width]

    left_width = max(1, (width - len(ELLIPSIS)) // 2)
    right_width = max(1, width - len(ELLIPSIS) - left_width)
    return text[:left_width] + ELLIPSIS + text[-right_width:]


def priority_elide_path(path: str, width: int) -> str:
    path = normalize_home_path(path)
    if len(path) <= width:
        return path

    prefix, raw_parts = path_prefix_and_parts(path)
    parts = [part for part in raw_parts if part]
    if not parts:
        return middle_elide_text(path, width)

    initial_count = 1
    final_count = 1
    top_count = top_collection_part_count(parts)
    final_target_count = final_collection_part_count(parts)

    def fits(candidate_initial_count: int, candidate_final_count: int) -> bool:
        return (
            len(
                compose_elided_path(
                    prefix, parts, candidate_initial_count, candidate_final_count
                )
            )
            <= width
        )

    if not fits(initial_count, final_count):
        minimal = compose_elided_path(prefix, parts, initial_count, final_count)
        return middle_elide_text(minimal, width)

    if top_count > initial_count and fits(top_count, final_count):
        initial_count = top_count

    if final_target_count > final_count and fits(initial_count, final_target_count):
        final_count = final_target_count

    while initial_count + final_count < len(parts) and fits(
        initial_count + 1, final_count
    ):
        initial_count += 1

    return compose_elided_path(prefix, parts, initial_count, final_count)


def priority_path_labels(paths: list[str], width: int) -> dict[str, str]:
    return {path: priority_elide_path(path, width) for path in paths}


def duplicate_marker_text(
    path_counts: list[dict[str, Any]], marker_by_collection: dict[str, str]
) -> str:
    markers: list[str] = []
    collection_counts: dict[str, int] = {}
    for path_count in path_counts:
        path = str(path_count["path"])
        collection = skill_collection_root(path)
        collection_counts[collection] = collection_counts.get(collection, 0) + int(
            path_count.get("count", 1)
        )

    omitted_collection_count = 0
    for collection, count in collection_counts.items():
        marker = marker_by_collection.get(collection)
        if marker is None:
            omitted_collection_count += 1
            continue
        markers.append(f"{marker}×{count}" if count > 1 else marker)
    if omitted_collection_count:
        markers.append(f"+{omitted_collection_count} collections")
    return " ".join(markers)


def collect_duplicate_skill_rows(
    section: dict[str, Any], marker_by_collection: dict[str, str]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for skill in section.get("duplicate_targets", []):
        skill_name = str(
            skill.get("skill") or skill_name_from_target(str(skill.get("target", "")))
        )
        marker_text = duplicate_marker_text(
            list(skill.get("path_counts", [])), marker_by_collection
        )
        if marker_text:
            skill_name = f"{skill_name} [{marker_text}]"
        rows.append(
            {
                "label": skill_name,
                "tokens": int(skill["excess_tokens"]),
                "count": int(skill["count"]),
                "excess_count": int(skill.get("excess_count", int(skill["count"]) - 1)),
            }
        )
    return rows


def collect_duplicate_mcp_rows(section: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "label": str(server["name"]),
            "tokens": int(server["excess_tokens"]),
            "count": int(server["count"]),
            "excess_count": int(server.get("excess_count", int(server["count"]) - 1)),
        }
        for server in section.get("duplicate_servers", [])
    ]


def format_duplicate_suffix(row: dict[str, Any]) -> str:
    count = int(row["count"])
    excess_count = int(row["excess_count"])
    return (
        f"{count} {pluralize(count, 'entry', 'entries')}  "
        f"{excess_count} excess {pluralize(excess_count, 'entry', 'entries')}"
    )


def render_boxed_marker_legend(
    marker_by_collection: dict[str, str], target_width: int | None
) -> str:
    if not marker_by_collection:
        return ""

    marker_width = max(len(marker) for marker in marker_by_collection.values())
    label_width = max(
        MIN_LEGEND_LABEL_WIDTH,
        (target_width - marker_width - 7) if target_width is not None else 0,
    )
    compact_labels = priority_path_labels(
        list(marker_by_collection.keys()), label_width
    )
    inner_width = marker_width + label_width + 5
    title_with_padding = " DUPLICATE MARKER LEGEND "
    left_fill = max((inner_width - len(title_with_padding)) // 2, 0)
    right_fill = max(inner_width - len(title_with_padding) - left_fill, 0)
    if len(title_with_padding) > inner_width:
        top = f"╔{title_with_padding[:inner_width]}╗"
    else:
        top = f"╔{'═' * left_fill}{title_with_padding}{'═' * right_fill}╗"
    bottom = f"╚{'═' * inner_width}╝"

    lines = [top]
    for collection, marker in marker_by_collection.items():
        wrapped_label = textwrap.wrap(
            compact_labels[collection],
            width=label_width,
            break_long_words=True,
            break_on_hyphens=False,
        ) or [""]
        for index, label_part in enumerate(wrapped_label):
            marker_cell = marker if index == 0 else ""
            lines.append(
                f"║ {marker_cell.ljust(marker_width)} │ {label_part.ljust(label_width)} ║"
            )
    lines.append(bottom)
    return "\n".join(lines)


def render_duplicate_entries(
    payload: dict[str, Any], target_width: int | None = None
) -> str:
    skills = payload.get("skills")
    mcps = payload.get("mcps")
    if not isinstance(skills, dict) and not isinstance(mcps, dict):
        return ""

    displayed_skill_collections: list[str] = []
    if isinstance(skills, dict):
        for skill in skills.get("duplicate_targets", [])[:MAX_DUPLICATE_ROWS]:
            for path_count in skill.get("path_counts", []):
                displayed_skill_collections.append(
                    skill_collection_root(str(path_count["path"]))
                )
    displayed_skill_collections = list(dict.fromkeys(displayed_skill_collections))
    marker_by_collection = {
        collection: DUPLICATE_MARKERS[index]
        for index, collection in enumerate(
            displayed_skill_collections[: len(DUPLICATE_MARKERS)]
        )
    }

    parent_rows: list[dict[str, Any]] = []
    if isinstance(skills, dict) and int(skills.get("duplicate_target_count", 0)):
        skill_rows = collect_duplicate_skill_rows(skills, marker_by_collection)[
            :MAX_DUPLICATE_ROWS
        ]
        parent_rows.append(
            {
                "label": "skills",
                "tokens": int(skills["duplicate_target_excess_tokens"]),
                "count": int(skills["duplicate_target_entry_count"]),
                "excess_count": int(skills["duplicate_target_excess_count"]),
                "children": skill_rows,
            }
        )

    if isinstance(mcps, dict) and int(mcps.get("duplicate_server_count", 0)):
        mcp_rows = collect_duplicate_mcp_rows(mcps)[:MAX_DUPLICATE_ROWS]
        parent_rows.append(
            {
                "label": "mcps",
                "tokens": int(mcps["duplicate_server_excess_tokens"]),
                "count": int(mcps["duplicate_server_entry_count"]),
                "excess_count": int(mcps["duplicate_server_excess_count"]),
                "children": mcp_rows,
            }
        )

    if not parent_rows:
        return ""

    rendered_rows: list[dict[str, str | int | float]] = []
    max_parent_tokens = max(int(row["tokens"]) for row in parent_rows)
    for parent_index, row in enumerate(parent_rows):
        parent_is_last = parent_index == len(parent_rows) - 1
        rendered_rows.append(
            {
                "label": f"{tree_row_prefix(parent_is_last)}{row['label']}",
                "tokens": int(row["tokens"]),
                "ratio": int(row["tokens"]) / max_parent_tokens
                if max_parent_tokens
                else 0.0,
                "suffix": format_duplicate_suffix(row),
            }
        )
        children = list(row.get("children", []))
        max_child_tokens = max((int(child["tokens"]) for child in children), default=0)
        for child_index, child in enumerate(children):
            child_is_last = child_index == len(children) - 1
            rendered_rows.append(
                {
                    "label": f"{tree_child_prefix(parent_is_last)}{tree_row_prefix(child_is_last)}{child['label']}",
                    "tokens": int(child["tokens"]),
                    "ratio": int(child["tokens"]) / max_child_tokens
                    if max_child_tokens
                    else 0.0,
                    "suffix": format_duplicate_suffix(child),
                }
            )

    label_width = max(len(str(row["label"])) for row in rendered_rows)
    token_width = max(len(str(row["tokens"])) for row in rendered_rows)
    lines = ["Duplicate entries (excess tokens)"]
    for row in rendered_rows:
        lines.append(
            f"{str(row['label']).ljust(label_width)}  "
            f"{str(row['tokens']).rjust(token_width)}  "
            f"[{render_bar(float(row['ratio']))}]  "
            f"{row['suffix']}"
        )

    legend = render_boxed_marker_legend(marker_by_collection, target_width)
    if legend:
        lines.extend(["", legend])
    return "\n".join(lines)


def tree_row_prefix(is_last: bool) -> str:
    return "└── " if is_last else "├── "


def tree_child_prefix(parent_is_last: bool) -> str:
    return "   " if parent_is_last else "│  "


def render_tree_section(
    title: str,
    rows: list[dict[str, Any]],
    *,
    status: str | None = None,
    show_counts: bool = True,
) -> str:
    if not rows:
        return ""

    rendered_rows: list[dict[str, str | int | float]] = []
    max_parent_tokens = max(int(row["tokens"]) for row in rows)

    for parent_index, row in enumerate(rows):
        parent_is_last = parent_index == len(rows) - 1
        parent_label = f"{tree_row_prefix(parent_is_last)}{row['label']}"
        parent_suffix = ""
        if show_counts:
            parent_suffix = f"{int(row['count'])} entries  {status}"
        rendered_rows.append(
            {
                "label": parent_label,
                "tokens": int(row["tokens"]),
                "ratio": int(row["tokens"]) / max_parent_tokens
                if max_parent_tokens
                else 0.0,
                "suffix": parent_suffix,
            }
        )

        children = list(row.get("children", []))
        max_child_tokens = max((int(child["tokens"]) for child in children), default=0)
        for child_index, child in enumerate(children):
            child_is_last = child_index == len(children) - 1
            child_label = f"{tree_child_prefix(parent_is_last)}{tree_row_prefix(child_is_last)}{child['label']}"
            child_suffix = ""
            if show_counts:
                parent_tokens = int(row["tokens"])
                child_share = (
                    (int(child["tokens"]) / parent_tokens * 100)
                    if parent_tokens
                    else 0.0
                )
                child_suffix = f"{int(child['count'])} entries  {child_share:5.1f}%"
            rendered_rows.append(
                {
                    "label": child_label,
                    "tokens": int(child["tokens"]),
                    "ratio": int(child["tokens"]) / max_child_tokens
                    if max_child_tokens
                    else 0.0,
                    "suffix": child_suffix,
                }
            )

    label_width = max(len(str(row["label"])) for row in rendered_rows)
    token_width = max(len(str(row["tokens"])) for row in rendered_rows)

    lines = [title]
    for row in rendered_rows:
        line = (
            f"{str(row['label']).ljust(label_width)}  "
            f"{str(row['tokens']).rjust(token_width)}  "
            f"[{render_bar(float(row['ratio']))}]"
        )
        if row["suffix"]:
            line += f"  {row['suffix']}"
        lines.append(line)

    return "\n".join(lines)


def render_high_level(payload: dict[str, Any]) -> str:
    known_total = payload.get("known_total")
    if not isinstance(known_total, dict):
        return ""

    components = known_total.get("components", {})
    if not isinstance(components, dict):
        return ""

    ordered_keys = [
        "rules_catalog",
        "system",
        "workspace_context_other",
        "skills_catalog",
        "mcp_catalog",
        "current_turn_overhead",
    ]
    rows = [
        {"label": key, "tokens": int(components[key]), "count": 0, "children": []}
        for key in ordered_keys
        if key in components
    ]
    rows.append(
        {
            "label": "known_total",
            "tokens": int(known_total["tokens"]),
            "count": 0,
            "children": [],
        }
    )

    section = render_tree_section("High-level", rows, status=None, show_counts=False)
    excluded = payload.get("excluded", [])
    if excluded:
        section += "\n" + "excluded: " + ", ".join(str(item) for item in excluded)
    return section


def render_rules(payload: dict[str, Any]) -> str:
    rules = payload.get("rules")
    if not isinstance(rules, dict):
        return ""

    rows = [
        {
            "label": str(section["section"]),
            "tokens": int(section["tokens"]),
            "count": int(section["count"]),
            "children": [
                {
                    "label": str(group["group"]),
                    "tokens": int(group["tokens"]),
                    "count": int(group["count"]),
                }
                for group in section.get("groups", [])
            ],
        }
        for section in rules.get("section_totals", [])
    ]
    return render_tree_section(
        "Rules by section", rows, status=source_status(str(rules.get("source")))
    )


def render_locations(payload: dict[str, Any], key: str, title: str) -> str:
    section = payload.get(key)
    if not isinstance(section, dict):
        return ""

    rows = [
        {
            "label": str(location["location"]),
            "tokens": int(location["tokens"]),
            "count": int(location["count"]),
            "children": [
                {
                    "label": str(group["group"]),
                    "tokens": int(group["tokens"]),
                    "count": int(group["count"]),
                }
                for group in location.get("groups", [])
            ],
        }
        for location in section.get("location_totals", [])
    ]
    return render_tree_section(
        title, rows, status=source_status(str(section.get("source")))
    )


def main() -> int:
    args = parse_args()
    payload = load_payload(args.json_file)

    leading_sections = [
        render_header(args.scope_text, payload),
        render_high_level(payload),
        render_rules(payload),
        render_locations(payload, "skills", "Skills by location"),
        render_locations(payload, "mcps", "MCPs by location"),
    ]
    target_width = max(
        (
            len(line)
            for section in leading_sections
            if section
            for line in section.splitlines()
        ),
        default=None,
    )
    sections = [
        *leading_sections,
        render_duplicate_entries(payload, target_width),
    ]
    rendered = "\n\n".join(section for section in sections if section)
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
