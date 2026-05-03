#!/usr/bin/env python3.14
from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    detail: str
    path: str


FENCE_START_RE = re.compile(r"(`{3,}|~{3,})")
BACKTICK_PATH_RE = re.compile(r"`([^`]+)`")
REFERENCE_DEFINITION_RE = re.compile(r"(?m)^[ \t]{0,3}\[([^\]\n]+)\]:[ \t]*(.+?)\s*$")


def strip_fenced_code_blocks(markdown: str) -> str:
    visible_lines: list[str] = []
    fence_char: str | None = None
    fence_length = 0
    for line in markdown.splitlines(keepends=True):
        stripped = line.lstrip(" ")
        indent = len(line) - len(stripped)
        if indent <= 3:
            if fence_char is not None:
                closing_fence = re.match(rf"{re.escape(fence_char)}{{{fence_length},}}\s*$", stripped)
                if closing_fence:
                    fence_char = None
                    fence_length = 0
                continue
            opening_fence = FENCE_START_RE.match(stripped)
            if opening_fence:
                marker = opening_fence.group(1)
                fence_char = marker[0]
                fence_length = len(marker)
                continue
        if fence_char is None:
            visible_lines.append(line)
    return "".join(visible_lines)


def strip_inline_code_spans(markdown: str) -> str:
    chars = list(markdown)
    index = 0
    while index < len(chars):
        if chars[index] != "`":
            index += 1
            continue
        fence_length = 1
        while index + fence_length < len(chars) and chars[index + fence_length] == "`":
            fence_length += 1
        marker = "`" * fence_length
        close_index = markdown.find(marker, index + fence_length)
        if close_index == -1:
            index += fence_length
            continue
        for position in range(index, close_index + fence_length):
            if chars[position] != "\n":
                chars[position] = " "
        index = close_index + fence_length
    return "".join(chars)


def strip_indented_code_blocks(markdown: str) -> str:
    visible_lines: list[str] = []
    for line in markdown.splitlines(keepends=True):
        if line.startswith(("    ", "\t")):
            visible_lines.append("\n" if line.endswith("\n") else "")
        else:
            visible_lines.append(line)
    return "".join(visible_lines)


def markdown_link_search_text(markdown: str) -> str:
    return strip_inline_code_spans(strip_indented_code_blocks(strip_fenced_code_blocks(markdown)))


def validate_required_paths(root: Path, paths: Iterable[str]) -> list[CheckResult]:
    results: list[CheckResult] = []
    for path in paths:
        exists = (root / path).exists()
        results.append(
            CheckResult(
                name=f"required_path:{path}",
                ok=exists,
                detail="exists" if exists else "missing",
                path=path,
            )
        )
    return results


def find_matching_label_close(markdown: str, open_index: int) -> int | None:
    depth = 0
    index = open_index
    while index < len(markdown):
        char = markdown[index]
        if char == "\\":
            index += 2
            continue
        if char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                return index
        index += 1
    return None


def find_matching_parenthesis_close(markdown: str, open_index: int) -> int | None:
    depth = 0
    index = open_index
    in_angle_destination = False
    while index < len(markdown):
        char = markdown[index]
        if char == "\\":
            index += 2
            continue
        if char == "<" and depth == 1:
            in_angle_destination = True
        elif char == ">" and in_angle_destination:
            in_angle_destination = False
        elif not in_angle_destination:
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    return index
        index += 1
    return None


def markdown_link_destination(raw_target: str) -> str:
    target = raw_target.strip()
    if not target:
        return ""
    if target.startswith("<"):
        close = target.find(">")
        target = target[1:close] if close != -1 else target[1:]
    else:
        target = target.split(maxsplit=1)[0]
    return target.split("#", 1)[0]


def local_markdown_target(target: str) -> bool:
    if not target:
        return False
    if target.startswith(("#", "//", "mailto:")):
        return False
    return not bool(urlparse(target).scheme)


def normalize_reference_label(label: str) -> str:
    return " ".join(label.strip().casefold().split())


def reference_definitions(markdown: str) -> dict[str, str]:
    definitions: dict[str, str] = {}
    for match in REFERENCE_DEFINITION_RE.finditer(markdown):
        raw_label = match.group(1).strip()
        if raw_label.startswith("^"):
            continue
        normalized_label = normalize_reference_label(raw_label)
        if normalized_label not in definitions:
            definitions[normalized_label] = markdown_link_destination(match.group(2))
    return definitions


def undefined_reference_labels(markdown: str) -> list[str]:
    searchable_markdown = markdown_link_search_text(markdown)
    definitions = reference_definitions(searchable_markdown)
    undefined: list[str] = []
    index = 0
    while index < len(searchable_markdown):
        char = searchable_markdown[index]
        if char == "\\":
            index += 2
            continue
        open_label = index + 1 if char == "!" and index + 1 < len(searchable_markdown) and searchable_markdown[index + 1] == "[" else index
        if searchable_markdown[open_label] != "[":
            index += 1
            continue
        close_label = find_matching_label_close(searchable_markdown, open_label)
        if close_label is None:
            index += 1
            continue
        open_reference = close_label + 1
        if open_reference >= len(searchable_markdown) or searchable_markdown[open_reference] != "[":
            index += 1
            continue
        close_reference = find_matching_label_close(searchable_markdown, open_reference)
        if close_reference is None:
            index += 1
            continue
        raw_label = searchable_markdown[open_reference + 1 : close_reference].strip()
        if not raw_label:
            raw_label = searchable_markdown[open_label + 1 : close_label].strip()
        if raw_label.startswith("^"):
            index = close_reference + 1
            continue
        if normalize_reference_label(raw_label) not in definitions:
            undefined.append(raw_label)
        index = close_reference + 1
    return unique_preserve_order(undefined)


def find_markdown_links(markdown: str) -> list[str]:
    searchable_markdown = markdown_link_search_text(markdown)
    links: list[str] = []
    for target in reference_definitions(searchable_markdown).values():
        if local_markdown_target(target):
            links.append(target)
    index = 0
    while index < len(searchable_markdown):
        char = searchable_markdown[index]
        if char == "\\":
            index += 2
            continue
        is_image = char == "!" and index + 1 < len(searchable_markdown) and searchable_markdown[index + 1] == "["
        if is_image:
            open_label = index + 1
        elif char == "[":
            open_label = index
        else:
            index += 1
            continue
        close_label = find_matching_label_close(searchable_markdown, open_label)
        if close_label is None:
            index += 1
            continue
        open_target = close_label + 1
        if open_target >= len(searchable_markdown) or searchable_markdown[open_target] != "(":
            index += 1
            continue
        close_target = find_matching_parenthesis_close(searchable_markdown, open_target)
        if close_target is None:
            index += 1
            continue
        target = markdown_link_destination(searchable_markdown[open_target + 1 : close_target])
        if local_markdown_target(target):
            links.append(target)
        index = close_target + 1 if is_image else index + 1
    return links


def load_toml(path: Path) -> dict:
    with path.open("rb") as handle:
        return tomllib.load(handle)


SOURCE_PROJECTION_PATH = "docs/metasmith/source-projection.md"
SOURCE_PROJECTION_FIELDS = [
    "requirement_id",
    "source_file",
    "source_anchor",
    "summary",
    "disposition",
    "target_path",
    "deferment_reason",
    "validation_status",
]

ACCEPTED_SOURCE_REQUIREMENTS = {
    "H001": {"source_file": "00-metasmith-handoff-prompt.md", "source_anchor": "Your objective"},
    "H002": {"source_file": "00-metasmith-handoff-prompt.md", "source_anchor": "Terms you must use"},
    "H003": {"source_file": "00-metasmith-handoff-prompt.md", "source_anchor": "Core principle"},
    "H004": {"source_file": "00-metasmith-handoff-prompt.md", "source_anchor": "Required repository shape"},
    "H005": {"source_file": "00-metasmith-handoff-prompt.md", "source_anchor": "1. Ubiquitous Language"},
    "H006": {"source_file": "00-metasmith-handoff-prompt.md", "source_anchor": "2. Evidence discipline"},
    "H007": {"source_file": "00-metasmith-handoff-prompt.md", "source_anchor": "3. Framework architecture"},
    "H008": {"source_file": "00-metasmith-handoff-prompt.md", "source_anchor": "4. Decision method"},
    "H009": {"source_file": "00-metasmith-handoff-prompt.md", "source_anchor": "5. Harness capability catalog"},
    "H010": {"source_file": "00-metasmith-handoff-prompt.md", "source_anchor": "6. Templates and examples"},
    "H011": {"source_file": "00-metasmith-handoff-prompt.md", "source_anchor": "7. Initial Smith task specs"},
    "H012": {"source_file": "00-metasmith-handoff-prompt.md", "source_anchor": "Acceptance criteria"},
    "H052": {"source_file": "00-metasmith-handoff-prompt.md", "source_anchor": "Constraints"},
    "H053": {"source_file": "00-metasmith-handoff-prompt.md", "source_anchor": "Final report"},
    "H013": {"source_file": "01-executive-brief.md", "source_anchor": "What the Framework must solve"},
    "H014": {"source_file": "01-executive-brief.md", "source_anchor": "Core decomposition"},
    "H015": {"source_file": "01-executive-brief.md", "source_anchor": "What the Metasmith should produce"},
    "H016": {"source_file": "02-ubiquitous-language.md", "source_anchor": "Agent Armory"},
    "H017": {"source_file": "02-ubiquitous-language.md", "source_anchor": "Relationship model"},
    "H018": {"source_file": "03-evidence-and-source-map.md", "source_anchor": "Evidence categories"},
    "H019": {"source_file": "03-evidence-and-source-map.md", "source_anchor": "Source hygiene rules"},
    "H020": {"source_file": "04-framework-architecture.md", "source_anchor": "Component responsibilities"},
    "H021": {"source_file": "04-framework-architecture.md", "source_anchor": "Context management architecture"},
    "H022": {"source_file": "04-framework-architecture.md", "source_anchor": "Security architecture"},
    "H023": {"source_file": "04-framework-architecture.md", "source_anchor": "Maintenance architecture"},
    "H024": {"source_file": "05-decision-method-and-runbook.md", "source_anchor": "Principle: least cognitive privilege"},
    "H025": {"source_file": "05-decision-method-and-runbook.md", "source_anchor": "Placement guide"},
    "H026": {"source_file": "05-decision-method-and-runbook.md", "source_anchor": "Decision tree"},
    "H027": {"source_file": "05-decision-method-and-runbook.md", "source_anchor": "Capability creation runbook"},
    "H028": {"source_file": "05-decision-method-and-runbook.md", "source_anchor": "Anti-patterns"},
    "H029": {"source_file": "06-harness-capability-catalog.md", "source_anchor": "Summary matrix"},
    "H030": {"source_file": "06-harness-capability-catalog.md", "source_anchor": "Periodic Actions projection order"},
    "H031": {"source_file": "06-harness-capability-catalog.md", "source_anchor": "Refresh requirement"},
    "H032": {"source_file": "07-equipment-templates-and-examples.md", "source_anchor": "Template: capability card"},
    "H033": {"source_file": "07-equipment-templates-and-examples.md", "source_anchor": "Template: interface decision record"},
    "H034": {"source_file": "07-equipment-templates-and-examples.md", "source_anchor": "Template: skill reference"},
    "H035": {"source_file": "07-equipment-templates-and-examples.md", "source_anchor": "Template: skill body"},
    "H036": {"source_file": "07-equipment-templates-and-examples.md", "source_anchor": "Template: hook"},
    "H037": {"source_file": "07-equipment-templates-and-examples.md", "source_anchor": "Template: Agent Profile"},
    "H038": {"source_file": "07-equipment-templates-and-examples.md", "source_anchor": "Template: Harness Plugin manifest"},
    "H039": {"source_file": "07-equipment-templates-and-examples.md", "source_anchor": "Template: deterministic script contract"},
    "H040": {"source_file": "07-equipment-templates-and-examples.md", "source_anchor": "Example: PR review"},
    "H041": {"source_file": "07-equipment-templates-and-examples.md", "source_anchor": "Template: MCP/tool definition notes"},
    "H042": {"source_file": "07-equipment-templates-and-examples.md", "source_anchor": "Template: config"},
    "H043": {"source_file": "07-equipment-templates-and-examples.md", "source_anchor": "Example: documentation search"},
    "H044": {"source_file": "07-equipment-templates-and-examples.md", "source_anchor": "Example: observability investigation"},
    "H045": {"source_file": "08-initial-smith-task-specs.md", "source_anchor": "Task 1: Agent Ops"},
    "H046": {"source_file": "08-initial-smith-task-specs.md", "source_anchor": "Task 2: Periodic Actions"},
    "H047": {"source_file": "08-initial-smith-task-specs.md", "source_anchor": "Task 3: Harness Capability Refresh"},
    "H048": {"source_file": "09-repository-seed-plan.md", "source_anchor": "Proposed initial structure"},
    "H049": {"source_file": "09-repository-seed-plan.md", "source_anchor": "README requirements"},
    "H050": {"source_file": "10-gap-resolution-and-design-notes.md", "source_anchor": "Key corrections"},
    "H051": {"source_file": "10-gap-resolution-and-design-notes.md", "source_anchor": "Remaining uncertainties"},
    "H054": {"source_file": "harness-capabilities.seed.toml", "source_anchor": "[harness.codex]"},
}

SOURCE_HANDOFF_DIR = "docs/metasmith/handoff/2026-05-02"
SOURCE_HANDOFF_MANIFEST = f"{SOURCE_HANDOFF_DIR}/manifest.json"
SOURCE_HANDOFF_PROVENANCE_NOTICE = f"{SOURCE_HANDOFF_DIR}/AGENTS.md"
REQUIRED_PRELOADED_ROUTES = [
    "docs/equipment-framework.md",
    "docs/smith-runbook.md",
    "docs/interface-decision-guide.md",
    "docs/harness-capabilities.md",
    "templates/",
    "specs/",
]
MARKDOWN_LINK_EXCLUDED_DIRS = [
    Path("docs/metasmith/handoff/2026-05-02"),
]


def parse_markdown_table(markdown: str) -> list[dict[str, str]]:
    rows = [line.strip() for line in markdown.splitlines() if line.strip().startswith("|")]
    if len(rows) < 2:
        return []
    headers = [cell.strip() for cell in rows[0].strip("|").split("|")]
    data_rows = rows[2:]
    parsed: list[dict[str, str]] = []
    for row in data_rows:
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        parsed.append(dict(zip(headers, cells, strict=False)))
    return parsed


def invalid_repo_relative_target(target: str) -> bool:
    parsed = urlparse(target)
    return bool(parsed.scheme) or target.startswith("/") or ".." in Path(target).parts


def repo_relative_path_status(root: Path, relative_path: str, expected_kind: str) -> tuple[bool, str, Path]:
    if invalid_repo_relative_target(relative_path):
        return False, "path invalid", root / relative_path
    candidate = root / relative_path
    current = root
    for part in Path(relative_path).parts:
        current = current / part
        if current.is_symlink():
            return False, "path contains symlink", candidate
    try:
        root_resolved = root.resolve(strict=True)
        candidate_resolved = candidate.resolve(strict=True)
    except OSError:
        return False, "missing", candidate
    try:
        candidate_resolved.relative_to(root_resolved)
    except ValueError:
        return False, "path escapes repository root", candidate
    if expected_kind == "file" and not candidate.is_file():
        return False, "not a file", candidate
    if expected_kind == "directory" and not candidate.is_dir():
        return False, "not a directory", candidate
    return True, "exists", candidate


def repo_surface_status(root: Path, relative_path: str, label: str) -> tuple[bool, str, Path]:
    ok, detail, path = repo_relative_path_status(root, relative_path, "any")
    if ok:
        return ok, detail, path
    if detail == "path contains symlink":
        return False, f"{label} path contains symlink", path
    return False, f"{label} {detail}", path


def route_target_status(root: Path, target: str) -> tuple[bool, str, Path]:
    expected_kind = "directory" if target.endswith("/") else "file"
    ok, detail, path = repo_relative_path_status(root, target, expected_kind)
    if ok:
        return ok, detail, path
    if detail == "path contains symlink":
        return False, "route target path contains symlink", path
    return False, f"route target {detail}", path


def markdown_section(markdown: str, heading: str) -> str | None:
    lines = markdown.splitlines()
    collected: list[str] = []
    in_section = False
    heading_level = len(heading) - len(heading.lstrip("#"))
    for line in lines:
        stripped = line.strip()
        if stripped == heading:
            in_section = True
            continue
        if in_section and stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            if level <= heading_level:
                break
        if in_section:
            collected.append(line)
    if not in_section:
        return None
    return "\n".join(collected)


def find_backticked_paths(markdown: str) -> list[str]:
    searchable_markdown = strip_fenced_code_blocks(markdown)
    paths: list[str] = []
    for match in BACKTICK_PATH_RE.finditer(searchable_markdown):
        target = match.group(1).strip()
        if not target or " " in target:
            continue
        if target.startswith(("-", "--")):
            continue
        if any(target.startswith(prefix) for prefix in ("http://", "https://", "mailto:", "#")):
            continue
        if "/" in target or target.endswith(".md"):
            paths.append(target)
    return paths


def unique_preserve_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def markdown_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*.md"):
        relative = path.relative_to(root)
        if any(relative == excluded or relative.is_relative_to(excluded) for excluded in MARKDOWN_LINK_EXCLUDED_DIRS):
            continue
        files.append(path)
    return sorted(files)


def markdown_link_target_status(root: Path, source_path: Path, target: str) -> bool:
    candidate = source_path.parent / target
    try:
        unresolved_relative = candidate.relative_to(root)
    except ValueError:
        return False
    current = root
    for part in unresolved_relative.parts:
        current = current / part
        if current.is_symlink():
            return False
    try:
        root_resolved = root.resolve(strict=True)
        candidate_resolved = candidate.resolve(strict=True)
    except OSError:
        return False
    try:
        candidate_resolved.relative_to(root_resolved)
    except ValueError:
        return False
    return candidate.exists()


def source_anchor_exists(path: Path, anchor: str) -> bool:
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("#") and stripped.lstrip("#").strip() == anchor:
            return True
        if stripped == anchor:
            return True
    return False


def handoff_root_status(root: Path) -> tuple[bool, str, Path]:
    ok, detail, path = repo_relative_path_status(root, SOURCE_HANDOFF_DIR, "directory")
    if ok:
        return ok, detail, path
    if detail == "path contains symlink":
        return False, "handoff directory path contains symlink", path
    if detail == "missing":
        return False, "handoff directory missing", path
    return False, f"handoff directory {detail}", path


def handoff_control_file_status(root: Path, relative_path: str, label: str) -> tuple[bool, str, Path]:
    ok, detail, path = repo_relative_path_status(root, relative_path, "file")
    if ok:
        return ok, detail, path
    if detail == "path contains symlink":
        return False, f"{label} path contains symlink", path
    if detail == "missing":
        return False, f"{label} missing", path
    return False, f"{label} {detail}", path


def handoff_file_status(root: Path, file_name: str) -> tuple[bool, str, Path]:
    root_ok, root_detail, handoff_root = handoff_root_status(root)
    candidate = handoff_root / file_name
    if not root_ok:
        return False, root_detail, candidate
    handoff_root_resolved = handoff_root.resolve(strict=True)
    current = handoff_root
    for part in Path(file_name).parts:
        current = current / part
        if current.is_symlink():
            return False, "manifest-listed file is a symlink", candidate
    try:
        candidate_resolved = candidate.resolve(strict=True)
    except OSError:
        return False, "manifest-listed file missing", candidate
    try:
        candidate_resolved.relative_to(handoff_root_resolved)
    except ValueError:
        return False, "manifest-listed file escapes handoff directory", candidate
    if not candidate.is_file():
        return False, "manifest-listed file missing", candidate
    return True, "exists", candidate


def validate_source_projection(root: Path) -> list[CheckResult]:
    register_ok, register_detail, path = repo_surface_status(root, SOURCE_PROJECTION_PATH, "register")
    if not register_ok:
        detail = "missing" if register_detail == "register missing" else register_detail
        return [CheckResult("source_projection:register", False, detail, SOURCE_PROJECTION_PATH)]
    rows = parse_markdown_table(path.read_text(encoding="utf-8"))
    results: list[CheckResult] = []
    if not rows:
        return [CheckResult("source_projection:rows", False, "no requirement rows", SOURCE_PROJECTION_PATH)]
    seen: dict[str, int] = {}
    for row in rows:
        requirement_id = row.get("requirement_id", "")
        seen[requirement_id] = seen.get(requirement_id, 0) + 1
        missing = [field for field in SOURCE_PROJECTION_FIELDS if field not in row]
        if missing:
            results.append(
                CheckResult(
                    name=f"source_projection:{requirement_id or 'unknown'}",
                    ok=False,
                    detail=f"missing fields: {', '.join(missing)}",
                    path=SOURCE_PROJECTION_PATH,
                )
            )
            continue
        expected = ACCEPTED_SOURCE_REQUIREMENTS.get(requirement_id)
        if expected:
            for field in ("source_file", "source_anchor"):
                if row[field] != expected[field]:
                    results.append(
                        CheckResult(
                            name=f"source_projection:{requirement_id}",
                            ok=False,
                            detail=f"{field} must be {expected[field]}",
                            path=SOURCE_PROJECTION_PATH,
                        )
                    )
            source_ok, source_detail, source_path = handoff_file_status(root, expected["source_file"])
            if not source_ok:
                detail = (
                    f"source_file missing: {expected['source_file']}"
                    if source_detail == "manifest-listed file missing"
                    else f"source_file invalid: {expected['source_file']} ({source_detail})"
                )
                results.append(
                    CheckResult(
                        name=f"source_projection:{requirement_id}",
                        ok=False,
                        detail=detail,
                        path=SOURCE_PROJECTION_PATH,
                    )
                )
            elif not source_anchor_exists(source_path, expected["source_anchor"]):
                results.append(
                    CheckResult(
                        name=f"source_projection:{requirement_id}",
                        ok=False,
                        detail=f"source_anchor not found in {expected['source_file']}",
                        path=SOURCE_PROJECTION_PATH,
                    )
                )
        disposition = row["disposition"]
        if disposition not in {"projected", "deferred"}:
            results.append(
                CheckResult(
                    name=f"source_projection:{requirement_id}",
                    ok=False,
                    detail="disposition must be projected or deferred",
                    path=SOURCE_PROJECTION_PATH,
                )
            )
        elif disposition == "projected":
            targets = [target.strip() for target in row["target_path"].split(",") if target.strip()]
            if not targets:
                results.append(
                    CheckResult(
                        name=f"source_projection:{requirement_id}",
                        ok=False,
                        detail="projected requirement missing target_path",
                        path=SOURCE_PROJECTION_PATH,
                    )
                )
            for target in targets:
                target_ok, target_detail, _ = repo_surface_status(root, target, "projected target")
                if not target_ok:
                    detail = (
                        "projected target missing"
                        if target_detail == "projected target missing"
                        else "projected target invalid"
                    )
                    results.append(
                        CheckResult(
                            name=f"source_projection:{requirement_id}:target:{target}",
                            ok=False,
                            detail=detail,
                            path=SOURCE_PROJECTION_PATH,
                        )
                    )
        elif disposition == "deferred":
            if not row["deferment_reason"]:
                results.append(
                    CheckResult(
                        name=f"source_projection:{requirement_id}",
                        ok=False,
                        detail="deferred requirement missing deferment_reason",
                        path=SOURCE_PROJECTION_PATH,
                    )
                )
            targets = [target.strip() for target in row["target_path"].split(",") if target.strip()]
            if not targets:
                results.append(
                    CheckResult(
                        name=f"source_projection:{requirement_id}",
                        ok=False,
                        detail="deferred requirement missing downstream target_path",
                        path=SOURCE_PROJECTION_PATH,
                    )
                )
            for target in targets:
                invalid = invalid_repo_relative_target(target)
                if invalid:
                    results.append(
                        CheckResult(
                            name=f"source_projection:{requirement_id}:target:{target}",
                            ok=False,
                            detail="deferred target invalid",
                            path=SOURCE_PROJECTION_PATH,
                        )
                    )
        if not any(result.name.startswith(f"source_projection:{requirement_id}") and not result.ok for result in results):
            results.append(
                CheckResult(
                    name=f"source_projection:{requirement_id}",
                    ok=True,
                    detail=disposition,
                    path=SOURCE_PROJECTION_PATH,
                )
            )
    expected_ids = set(ACCEPTED_SOURCE_REQUIREMENTS)
    seen_ids = {requirement_id for requirement_id in seen if requirement_id}
    missing_ids = sorted(expected_ids - seen_ids)
    extra_ids = sorted(seen_ids - expected_ids)
    duplicate_ids = sorted(requirement_id for requirement_id, count in seen.items() if count > 1)
    if missing_ids:
        results.append(
            CheckResult(
                name="source_projection:coverage",
                ok=False,
                detail=f"missing accepted requirements: {', '.join(missing_ids)}",
                path=SOURCE_PROJECTION_PATH,
            )
        )
    if extra_ids:
        results.append(
            CheckResult(
                name="source_projection:coverage",
                ok=False,
                detail=f"unknown requirement ids: {', '.join(extra_ids)}",
                path=SOURCE_PROJECTION_PATH,
            )
        )
    if duplicate_ids:
        results.append(
            CheckResult(
                name="source_projection:coverage",
                ok=False,
                detail=f"duplicate requirement ids: {', '.join(duplicate_ids)}",
                path=SOURCE_PROJECTION_PATH,
            )
        )
    return results


def validate_source_handoff_provenance(root: Path) -> list[CheckResult]:
    manifest_path = root / SOURCE_HANDOFF_MANIFEST
    notice_path = root / SOURCE_HANDOFF_PROVENANCE_NOTICE
    results = validate_required_paths(root, [SOURCE_HANDOFF_MANIFEST, SOURCE_HANDOFF_PROVENANCE_NOTICE])
    root_ok, root_detail, _ = handoff_root_status(root)
    if not root_ok:
        results.append(CheckResult("source_handoff:root", False, root_detail, SOURCE_HANDOFF_DIR))
        return results
    manifest_ok, manifest_detail, manifest_path = handoff_control_file_status(root, SOURCE_HANDOFF_MANIFEST, "manifest")
    if not manifest_ok:
        if manifest_detail != "manifest missing":
            results.append(CheckResult("source_handoff:manifest_path", False, manifest_detail, SOURCE_HANDOFF_MANIFEST))
        return results
    notice_ok, notice_detail, notice_path = handoff_control_file_status(
        root,
        SOURCE_HANDOFF_PROVENANCE_NOTICE,
        "provenance notice",
    )
    if not notice_ok and notice_detail != "provenance notice missing":
        results.append(
            CheckResult("source_handoff:provenance_notice_path", False, notice_detail, SOURCE_HANDOFF_PROVENANCE_NOTICE)
        )
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        results.append(
            CheckResult(
                name="source_handoff:manifest_json",
                ok=False,
                detail=f"manifest JSON invalid: {error.msg}",
                path=SOURCE_HANDOFF_MANIFEST,
            )
        )
        return results
    if not isinstance(manifest, dict):
        results.append(
            CheckResult(
                name="source_handoff:manifest_json",
                ok=False,
                detail="manifest JSON must be an object",
                path=SOURCE_HANDOFF_MANIFEST,
            )
        )
        return results
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        results.append(
            CheckResult(
                name="source_handoff:manifest_files",
                ok=False,
                detail="manifest files must be a non-empty list",
                path=SOURCE_HANDOFF_MANIFEST,
            )
        )
        return results
    manifest_files: set[str] = set()
    for file_name in files:
        if not isinstance(file_name, str) or not file_name.strip() or invalid_repo_relative_target(file_name):
            results.append(
                CheckResult(
                    name=f"source_handoff:file:{file_name}",
                    ok=False,
                    detail="manifest file path invalid",
                    path=SOURCE_HANDOFF_MANIFEST,
                )
            )
            continue
        manifest_files.add(file_name)
        path = f"{SOURCE_HANDOFF_DIR}/{file_name}"
        ok, detail, _ = handoff_file_status(root, file_name)
        results.append(
            CheckResult(
                name=f"source_handoff:file:{file_name}",
                ok=ok,
                detail=detail,
                path=path,
            )
        )
    expected_source_files = {metadata["source_file"] for metadata in ACCEPTED_SOURCE_REQUIREMENTS.values()}
    missing_source_files = sorted(expected_source_files - manifest_files)
    if missing_source_files:
        results.append(
            CheckResult(
                name="source_handoff:manifest_coverage",
                ok=False,
                detail=f"accepted source files missing from manifest: {', '.join(missing_source_files)}",
                path=SOURCE_HANDOFF_MANIFEST,
            )
        )
    if notice_ok:
        notice = notice_path.read_text(encoding="utf-8")
        expected_notice = "provenance, not current operating instructions."
        results.append(
            CheckResult(
                name="source_handoff:provenance_notice",
                ok=expected_notice in notice,
                detail="present" if expected_notice in notice else "missing archive instruction boundary",
                path=SOURCE_HANDOFF_PROVENANCE_NOTICE,
            )
        )
    return results


def validate_framework_routes(root: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    agents_path = root / "AGENTS.md"
    readme_path = root / "README.md"
    agents_markdown = agents_path.read_text(encoding="utf-8") if agents_path.exists() else ""
    readme_markdown = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

    agents_section = markdown_section(agents_markdown, "## Framework Path")
    readme_section = markdown_section(readme_markdown, "## Framework")

    if agents_section is None:
        results.append(CheckResult("framework_route:agent", False, "missing Preloaded Framework Path", "AGENTS.md"))
    if readme_section is None:
        results.append(CheckResult("framework_route:human", False, "missing Human Framework Entry", "README.md"))

    agents_targets: list[str] = []
    if agents_section is not None:
        agents_targets = unique_preserve_order([*find_markdown_links(agents_section), *find_backticked_paths(agents_section)])
        for required_route in REQUIRED_PRELOADED_ROUTES:
            if required_route not in agents_targets:
                results.append(
                    CheckResult(
                        f"framework_route:agent:{required_route}",
                        False,
                        "missing required preloaded route",
                        "AGENTS.md",
                    )
                )

    readme_targets: list[str] = []
    if readme_section is not None:
        readme_targets = find_markdown_links(readme_section)
        if "docs/equipment-framework.md" not in readme_targets:
            results.append(
                CheckResult(
                    "framework_route:human:docs/equipment-framework.md",
                    False,
                    "missing Human Framework Entry link",
                    "README.md",
                )
            )

    for target in unique_preserve_order([*agents_targets, *readme_targets]):
        ok, detail, _ = route_target_status(root, target)
        if not ok:
            source = "AGENTS.md" if target in agents_targets else "README.md"
            results.append(
                CheckResult(
                    f"framework_route:target:{target}",
                    False,
                    detail,
                    source,
                )
            )

    if not any(not result.ok for result in results):
        results.append(CheckResult("framework_route:agent", True, "present", "AGENTS.md"))
        results.append(CheckResult("framework_route:human", True, "present", "README.md"))
    return results


def validate_markdown_links(root: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    for path in markdown_files(root):
        source_relative = path.relative_to(root).as_posix()
        source_ok, source_detail, _ = repo_relative_path_status(root, source_relative, "file")
        if not source_ok:
            detail = (
                "markdown file path contains symlink"
                if source_detail == "path contains symlink"
                else f"markdown file {source_detail}"
            )
            results.append(CheckResult(f"markdown_file:{source_relative}", False, detail, source_relative))
            continue
        markdown = path.read_text(encoding="utf-8")
        for label in undefined_reference_labels(markdown):
            results.append(
                CheckResult(
                    f"markdown_reference:{source_relative}:{label}",
                    False,
                    "undefined reference",
                    source_relative,
                )
            )
        for link in find_markdown_links(markdown):
            ok = markdown_link_target_status(root, path, link)
            results.append(
                CheckResult(
                    f"markdown_link:{source_relative}:{link}",
                    ok,
                    "exists" if ok else "target missing",
                    source_relative,
                )
            )
    return results


def render_human(results: list[CheckResult]) -> str:
    lines: list[str] = []
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        lines.append(f"{status} {result.name} {result.path} - {result.detail}")
    failed = sum(1 for result in results if not result.ok)
    passed = len(results) - failed
    lines.append(f"{failed} failed, {passed} passed")
    return "\n".join(lines)


def render_json(results: list[CheckResult]) -> str:
    return json.dumps([asdict(result) for result in results], indent=2, sort_keys=True)


def run(root: Path) -> list[CheckResult]:
    required_paths = [
        "README.md",
        "AGENTS.md",
        "CONTEXT.md",
        "docs/prd/framework-seed.md",
        "docs/metasmith/source-projection.md",
        "docs/harness-capabilities.toml",
    ]
    return [
        *validate_required_paths(root, required_paths),
        *validate_source_handoff_provenance(root),
        *validate_source_projection(root),
        *validate_framework_routes(root),
        *validate_markdown_links(root),
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the Agent Armory Framework Seed.")
    parser.add_argument("--root", default=".", help="Repository root to validate.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args(argv)

    results = run(Path(args.root).resolve())
    output = render_json(results) if args.json else render_human(results)
    print(output)
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    sys.exit(main())
