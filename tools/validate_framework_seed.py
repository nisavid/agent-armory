#!/usr/bin/env python3.14
from __future__ import annotations

import argparse
import ast
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
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
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


def strip_html_comments(markdown: str) -> str:
    return HTML_COMMENT_RE.sub(lambda match: "\n" * match.group(0).count("\n"), markdown)


def markdown_visible_text(markdown: str) -> str:
    return strip_html_comments(strip_indented_code_blocks(strip_fenced_code_blocks(markdown)))


def markdown_link_search_text(markdown: str) -> str:
    return strip_inline_code_spans(markdown_visible_text(markdown))


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
CANONICAL_DOC_REQUIRED_SECTIONS = {
    "docs/ubiquitous-language.md": ["Language", "Relationships", "Precision rules"],
    "docs/equipment-framework.md": [
        "Purpose",
        "Least cognitive privilege",
        "Component model",
        "Context management",
        "Security",
        "Maintenance",
    ],
    "docs/smith-runbook.md": [
        "Capability card",
        "Interface decision record",
        "Docs/config/scripts/hooks/skills/agents/plugins",
        "Pressure Scenario Validation",
        "Equipment Promotion Path",
        "Closeout",
    ],
    "docs/metasmith-runbook.md": [
        "Source handoff preservation",
        "decision projection",
        "Review Until Clean",
        "Harness Fact Refresh",
        "Change set closeout",
        "Issue Projection",
        "downstream Smith specs",
    ],
    "docs/interface-decision-guide.md": ["Decision tree", "placement guide"],
    "docs/harness-components.md": [
        "Skills",
        "MCP/tools",
        "hooks",
        "Agent Profiles",
        "Harness Plugins",
        "scripts",
        "local docs",
        "config",
    ],
    "docs/harness-capabilities.md": [
        "Catalog policy",
        "Refresh summary",
        "Harness matrix",
        "Harness notes",
        "Periodic Actions projection order",
        "Refresh requirement",
    ],
    "docs/evidence-taxonomy.md": [
        "documentation-supported",
        "source-supported",
        "implementation inference",
        "practitioner wisdom",
        "hypothesis",
        "source hygiene",
    ],
    "docs/security-and-control.md": [
        "least privilege",
        "mutation gates",
        "secrets",
        "hooks",
        "MCP/tool side effects",
        "examples caveat",
    ],
    "docs/equipment-promotion.md": [
        "example",
        "specified",
        "planned",
        "implemented",
        "validated",
        "published",
        "entry/exit criteria",
    ],
}
CANONICAL_DOC_REQUIRED_TEXT = {
    "docs/smith-runbook.md": [
        "docs, config, scripts, hooks, skills, Agent Profiles, plugins, and templates are discoverable from the Framework path",
    ],
}
HARNESS_CATALOG_MARKDOWN_PATH = "docs/harness-capabilities.md"
HARNESS_CATALOG_PATH = "docs/harness-capabilities.toml"
REQUIRED_HARNESSES = [
    "codex",
    "claude_code",
    "cursor",
    "hermes_agent",
    "opencode",
    "openclaw",
]
ALLOWED_SOURCE_KINDS = {"first_party", "third_party_fallback"}
ALLOWED_EVIDENCE_CATEGORIES = {
    "documentation-supported",
    "source-supported",
    "implementation inference",
    "practitioner wisdom",
    "hypothesis",
}
HARNESS_REQUIRED_FIELDS = [
    "display_name",
    "evidence",
    "uncertainty",
    "summary_scheduling",
    "scheduling",
    "limitations",
    "refresh_notes",
    "local_observations",
]
TEMPLATE_REQUIRED_PATHS = [
    "templates/capability-card.md",
    "templates/interface-decision-record.md",
    "templates/skill/README.md",
    "templates/skill/SKILL.md",
    "templates/hook/README.md",
    "templates/hook/hook.ts",
    "templates/agents/README.md",
    "templates/agents/profile.toml",
    "templates/plugin/README.md",
    "templates/plugin/manifest.toml",
    "templates/script/README.md",
    "templates/script/validate-example.py",
    "templates/mcp/README.md",
    "templates/mcp/tool-spec.md",
    "templates/config/README.md",
    "templates/config/example.toml",
    "templates/security-review.md",
    "templates/context-budget-review.md",
]
ROOT_TEMPLATE_FILES = [
    "templates/capability-card.md",
    "templates/interface-decision-record.md",
    "templates/security-review.md",
    "templates/context-budget-review.md",
]
ROOT_TEMPLATE_REQUIRED_SECTIONS = {
    "templates/capability-card.md": [
        "Purpose",
        "Users",
        "Target harnesses",
        "Risks",
        "External systems",
        "Side effects",
        "Needed Harness Components",
        "Hard rules",
        "Deterministic checks",
        "Output contract",
        "Failure modes",
        "Evidence",
        "Open questions",
    ],
    "templates/interface-decision-record.md": [
        "Requirement",
        "Decision",
        "Chosen surface",
        "Rationale",
        "Evidence category",
        "Harness-specific projection",
        "Alternatives rejected",
        "Risks",
        "Maintenance notes",
    ],
    "templates/security-review.md": [
        "Scope",
        "Assets",
        "Trust boundaries",
        "Side effects",
        "Threats",
        "Controls",
        "Findings",
        "Residual risk",
    ],
    "templates/context-budget-review.md": [
        "Scope",
        "Always-loaded context",
        "On-demand context",
        "Budget risks",
        "Relocation decisions",
        "Verification",
    ],
}
TEMPLATE_READMES = [
    "templates/skill/README.md",
    "templates/hook/README.md",
    "templates/agents/README.md",
    "templates/plugin/README.md",
    "templates/script/README.md",
    "templates/mcp/README.md",
    "templates/config/README.md",
]
TEMPLATE_README_SECTIONS = [
    "Purpose",
    "Required fields",
    "Optional fields",
    "Common mistakes",
    "Validation expectations",
]
SKILL_TEMPLATE_PATH = "templates/skill/SKILL.md"
SKILL_TEMPLATE_SECTIONS = [
    "Use when",
    "Do not use when",
    "Preflight",
    "Procedure",
    "Output contract",
    "Failure handling",
    "Safety and policy notes",
]
HOOK_TEMPLATE_PATH = "templates/hook/hook.ts"
HOOK_REQUIRED_CONTRACT_FIELDS = {
    "side-effect classification": "sideEffectClassification",
    "approval behavior": "approvalBehavior",
    "failure handling": "failureHandling",
}
HOOK_REQUIRED_CONTRACT_VALUES = {
    "sideEffectClassification": "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
    "approvalBehavior": "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
    "failureHandling": "fail closed for unsafe mutations",
}
CANONICAL_APPROVAL_REQUIRED_FOR = {
    "external disclosure",
    "local write",
    "network write",
    "process execution",
    "privileged operation",
    "irreversible mutation",
}
AGENT_PROFILE_TEMPLATE_PATH = "templates/agents/profile.toml"
AGENT_PROFILE_REQUIRED_FIELDS = {
    "identity": ("identity",),
    "mission": ("identity", "mission"),
    "tools": ("tools",),
    "tools_allow": ("tools", "allow"),
    "tools_deny": ("tools", "deny"),
    "permissions": ("permissions",),
    "permission_mode": ("permissions", "mode"),
    "model": ("model",),
    "config": ("config",),
    "output": ("output",),
    "output_contract": ("output", "contract"),
}
PLUGIN_MANIFEST_TEMPLATE_PATH = "templates/plugin/manifest.toml"
PLUGIN_MANIFEST_REQUIRED_FIELDS = {
    "name": ("name",),
    "version": ("version",),
    "components": ("components",),
    "ownership": ("ownership",),
    "source": ("ownership", "source"),
    "permissions": ("permissions",),
    "approval_required_for": ("permissions", "approval_required_for"),
}
SCRIPT_TEMPLATE_PATH = "templates/script/validate-example.py"
MCP_TOOL_SPEC_PATH = "templates/mcp/tool-spec.md"
MCP_TOOL_REQUIRED_SECTIONS = [
    "Purpose",
    "Read/write classification",
    "Input schema",
    "Output schema",
    "Auth source",
    "Side effects",
    "Approval requirements",
    "Rate limits",
    "Pagination",
    "Rollback and cleanup",
    "Failure modes",
]
CONFIG_TEMPLATE_PATH = "templates/config/example.toml"
CONFIG_REQUIRED_FIELDS = {
    "ownership": ("ownership",),
    "autonomy": ("autonomy",),
    "enabled": ("enabled",),
    "enabled_default": ("enabled", "default"),
    "review": ("review",),
    "approval": ("approval",),
}
TOML_REQUIRED_TABLES = {
    AGENT_PROFILE_TEMPLATE_PATH: {
        "identity": ("identity",),
        "tools": ("tools",),
        "permissions": ("permissions",),
        "model": ("model",),
        "config": ("config",),
        "output": ("output",),
    },
    PLUGIN_MANIFEST_TEMPLATE_PATH: {
        "components": ("components",),
        "ownership": ("ownership",),
        "permissions": ("permissions",),
    },
    CONFIG_TEMPLATE_PATH: {
        "ownership": ("ownership",),
        "autonomy": ("autonomy",),
        "enabled": ("enabled",),
        "review": ("review",),
        "approval": ("approval",),
    },
}
EXTERNAL_DISCLOSURE_TEMPLATES = [
    "templates/capability-card.md",
    "templates/security-review.md",
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


def harness_matrix_rows(markdown: str) -> dict[str, dict[str, str]]:
    section = markdown_section(markdown, "## Harness matrix")
    if section is None:
        return {}
    rows = {}
    for row in parse_markdown_table(section):
        harness = row.get("Harness", "")
        if harness:
            rows[harness] = row
    return rows


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


def markdown_heading_texts(markdown: str) -> set[str]:
    headings: set[str] = set()
    for line in markdown_visible_text(markdown).splitlines():
        stripped = line.strip()
        if not stripped.startswith("#"):
            continue
        text = stripped.lstrip("#").strip()
        if text:
            headings.add(normalize_reference_label(text))
    return headings


def has_framework_seed_status(markdown: str) -> bool:
    visible_markdown = markdown_visible_text(markdown)
    nonblank_lines = [line.strip() for line in visible_markdown.splitlines() if line.strip()]
    return "Status: Framework Seed" in nonblank_lines[:8]


def has_template_status(markdown: str) -> bool:
    visible_markdown = markdown_visible_text(markdown)
    nonblank_lines = [line.strip() for line in visible_markdown.splitlines() if line.strip()]
    return "Status: Template" in nonblank_lines[:8]


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


def validate_canonical_docs(root: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    for relative_path, required_sections in CANONICAL_DOC_REQUIRED_SECTIONS.items():
        ok, detail, path = repo_relative_path_status(root, relative_path, "file")
        if not ok:
            if detail == "path contains symlink":
                detail = "canonical doc path contains symlink"
            results.append(CheckResult(f"canonical_doc:{relative_path}", False, detail, relative_path))
            continue
        markdown = path.read_text(encoding="utf-8")
        if not has_framework_seed_status(markdown):
            results.append(
                CheckResult(
                    f"canonical_doc:status:{relative_path}",
                    False,
                    "missing Status: Framework Seed",
                    relative_path,
                )
            )
        headings = markdown_heading_texts(markdown)
        for required_section in required_sections:
            if normalize_reference_label(required_section) not in headings:
                results.append(
                    CheckResult(
                        f"canonical_doc:section:{relative_path}:{required_section}",
                        False,
                        f"missing section: {required_section}",
                        relative_path,
                    )
                )
        searchable_markdown = markdown_link_search_text(markdown).casefold()
        for required_text in CANONICAL_DOC_REQUIRED_TEXT.get(relative_path, []):
            if required_text.casefold() not in searchable_markdown:
                results.append(
                    CheckResult(
                        f"canonical_doc:text:{relative_path}:{required_text}",
                        False,
                        f"missing text: {required_text}",
                        relative_path,
                    )
                )
        if not any(result.name.startswith(f"canonical_doc:") and result.path == relative_path and not result.ok for result in results):
            results.append(CheckResult(f"canonical_doc:{relative_path}", True, "present", relative_path))
    return results


def non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def non_empty_string_list(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(non_empty_string(item) for item in value)


def string_list(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def validate_harness_catalog(root: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    ok, detail, path = repo_relative_path_status(root, HARNESS_CATALOG_PATH, "file")
    if not ok:
        if detail == "path contains symlink":
            detail = "harness catalog path contains symlink"
        return [CheckResult("harness_catalog:catalog", False, detail, HARNESS_CATALOG_PATH)]
    try:
        catalog = load_toml(path)
    except tomllib.TOMLDecodeError as error:
        return [CheckResult("harness_catalog:toml", False, f"TOML invalid: {error.msg}", HARNESS_CATALOG_PATH)]

    if not non_empty_string(catalog.get("checked_at")):
        results.append(CheckResult("harness_catalog:checked_at", False, "missing checked_at", HARNESS_CATALOG_PATH))

    harnesses = catalog.get("harness")
    if not isinstance(harnesses, dict):
        results.append(CheckResult("harness_catalog:coverage", False, "missing harness table", HARNESS_CATALOG_PATH))
        return results

    required_ids = set(REQUIRED_HARNESSES)
    observed_ids = {harness_id for harness_id in harnesses if isinstance(harness_id, str)}
    missing_ids = [harness_id for harness_id in REQUIRED_HARNESSES if harness_id not in observed_ids]
    unknown_ids = sorted(observed_ids - required_ids)
    if missing_ids:
        results.append(
            CheckResult(
                "harness_catalog:coverage",
                False,
                f"missing required harnesses: {', '.join(missing_ids)}",
                HARNESS_CATALOG_PATH,
            )
        )
    if unknown_ids:
        results.append(
            CheckResult(
                "harness_catalog:coverage",
                False,
                f"unknown harness ids: {', '.join(unknown_ids)}",
                HARNESS_CATALOG_PATH,
            )
        )

    for harness_id in REQUIRED_HARNESSES:
        entry = harnesses.get(harness_id)
        if not isinstance(entry, dict):
            continue
        for field in HARNESS_REQUIRED_FIELDS:
            if field not in entry:
                results.append(
                    CheckResult(
                        f"harness_catalog:{harness_id}:{field}",
                        False,
                        f"missing {field}",
                        HARNESS_CATALOG_PATH,
                    )
                )
        for field in [
            "display_name",
            "evidence",
            "uncertainty",
            "summary_scheduling",
            "scheduling",
            "limitations",
            "refresh_notes",
        ]:
            if field in entry and not non_empty_string(entry[field]):
                results.append(
                    CheckResult(
                        f"harness_catalog:{harness_id}:{field}",
                        False,
                        f"{field} must be non-empty",
                        HARNESS_CATALOG_PATH,
                    )
                )
        local_observations = entry.get("local_observations")
        if "local_observations" in entry and not string_list(local_observations):
            results.append(
                CheckResult(
                    f"harness_catalog:{harness_id}:local_observations",
                    False,
                    "local_observations must be a list of strings",
                    HARNESS_CATALOG_PATH,
                )
            )
        sources = entry.get("sources")
        if not isinstance(sources, list) or not sources:
            results.append(
                CheckResult(
                    f"harness_catalog:{harness_id}:sources",
                    False,
                    "sources must be non-empty",
                    HARNESS_CATALOG_PATH,
                )
            )
        else:
            for index, source in enumerate(sources):
                if not isinstance(source, dict):
                    results.append(
                        CheckResult(
                            f"harness_catalog:{harness_id}:sources:{index}",
                            False,
                            "source must be a table",
                            HARNESS_CATALOG_PATH,
                        )
                    )
                    continue
                for field in ["url", "kind", "claim_scope"]:
                    if not non_empty_string(source.get(field)):
                        results.append(
                            CheckResult(
                                f"harness_catalog:{harness_id}:sources:{index}:{field}",
                                False,
                                f"missing source {field}",
                                HARNESS_CATALOG_PATH,
                            )
                        )
                url = source.get("url")
                if non_empty_string(url):
                    parsed_url = urlparse(url)
                    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
                        results.append(
                            CheckResult(
                                f"harness_catalog:{harness_id}:sources:{index}:url",
                                False,
                                "source url must be http or https with a host",
                                HARNESS_CATALOG_PATH,
                            )
                        )
                kind = source.get("kind")
                if non_empty_string(kind) and kind not in ALLOWED_SOURCE_KINDS:
                    results.append(
                        CheckResult(
                            f"harness_catalog:{harness_id}:sources:{index}:kind",
                            False,
                            "source kind must be first_party or third_party_fallback",
                            HARNESS_CATALOG_PATH,
                        )
                    )
        evidence = entry.get("evidence")
        if non_empty_string(evidence) and evidence not in ALLOWED_EVIDENCE_CATEGORIES:
            results.append(
                CheckResult(
                    f"harness_catalog:{harness_id}:evidence",
                    False,
                    "invalid evidence category",
                    HARNESS_CATALOG_PATH,
                )
            )
        if not non_empty_string(entry.get("checked_version")) and not non_empty_string(entry.get("version_basis")):
            results.append(
                CheckResult(
                    f"harness_catalog:{harness_id}:version",
                    False,
                    "missing checked_version or version_basis",
                    HARNESS_CATALOG_PATH,
                )
            )
        components = entry.get("components")
        if not non_empty_string_list(components):
            results.append(
                CheckResult(
                    f"harness_catalog:{harness_id}:components",
                    False,
                    "components must be non-empty",
                    HARNESS_CATALOG_PATH,
                )
            )
        if not any(result.name.startswith(f"harness_catalog:{harness_id}:") and not result.ok for result in results):
            results.append(CheckResult(f"harness_catalog:{harness_id}", True, "present", HARNESS_CATALOG_PATH))

    markdown_ok, markdown_detail, markdown_path = repo_relative_path_status(root, HARNESS_CATALOG_MARKDOWN_PATH, "file")
    if not markdown_ok:
        if markdown_detail == "path contains symlink":
            markdown_detail = "harness catalog markdown path contains symlink"
        results.append(CheckResult("harness_catalog_markdown:catalog", False, markdown_detail, HARNESS_CATALOG_MARKDOWN_PATH))
        return results

    markdown = markdown_path.read_text(encoding="utf-8")
    matrix_rows = harness_matrix_rows(markdown)
    for harness_id in REQUIRED_HARNESSES:
        entry = harnesses.get(harness_id)
        if not isinstance(entry, dict):
            continue
        display_name = entry.get("display_name")
        if not non_empty_string(display_name):
            continue
        row = matrix_rows.get(display_name)
        if row is None:
            results.append(
                CheckResult(
                    f"harness_catalog_markdown:{harness_id}:display_name",
                    False,
                    f"markdown missing matrix row: {display_name}",
                    HARNESS_CATALOG_MARKDOWN_PATH,
                )
            )
            continue
        expected_cells = {
            "checked_version": ("Checked version", entry.get("checked_version")),
            "evidence": ("Evidence", entry.get("evidence")),
            "summary_scheduling": ("Scheduling posture", entry.get("summary_scheduling")),
        }
        for field, (column, expected_value) in expected_cells.items():
            if non_empty_string(expected_value) and row.get(column) != expected_value:
                results.append(
                    CheckResult(
                        f"harness_catalog_markdown:{harness_id}:{field}",
                        False,
                        f"markdown matrix {column} mismatch: expected {expected_value}",
                        HARNESS_CATALOG_MARKDOWN_PATH,
                    )
                )
    return results


def template_file_text(root: Path, relative_path: str) -> tuple[str | None, CheckResult | None]:
    ok, detail, path = repo_relative_path_status(root, relative_path, "file")
    if not ok:
        if detail == "path contains symlink":
            detail = "template path contains symlink"
        return None, CheckResult(f"template:path:{relative_path}", False, detail, relative_path)
    return path.read_text(encoding="utf-8"), None


def validate_markdown_section_set(root: Path, relative_path: str, required_sections: Iterable[str]) -> list[CheckResult]:
    markdown, missing_result = template_file_text(root, relative_path)
    if missing_result is not None:
        return [missing_result]
    assert markdown is not None
    headings = markdown_heading_texts(markdown)
    results: list[CheckResult] = []
    for required_section in required_sections:
        if normalize_reference_label(required_section) not in headings:
            results.append(
                CheckResult(
                    f"template:section:{relative_path}:{required_section}",
                    False,
                    f"missing section: {required_section}",
                    relative_path,
                )
            )
    return results


def validate_required_template_text(
    root: Path,
    relative_path: str,
    required_label: str,
    required_text: str,
) -> list[CheckResult]:
    text, missing_result = template_file_text(root, relative_path)
    if missing_result is not None:
        return [missing_result]
    assert text is not None
    visible_text = markdown_visible_text(text)
    if required_text.casefold() not in visible_text.casefold():
        return [
            CheckResult(
                f"template:text:{relative_path}:{required_label}",
                False,
                f"missing {required_label}",
                relative_path,
            )
        ]
    return []


def validate_required_template_preamble_text(
    root: Path,
    relative_path: str,
    required_label: str,
    required_text: str,
) -> list[CheckResult]:
    text, missing_result = template_file_text(root, relative_path)
    if missing_result is not None:
        return [missing_result]
    assert text is not None
    visible_text = markdown_visible_text(text)
    first_section = re.search(r"(?m)^##\s+", visible_text)
    preamble = visible_text[: first_section.start()] if first_section else visible_text
    if required_text.casefold() not in preamble.casefold():
        return [
            CheckResult(
                f"template:text:{relative_path}:{required_label}",
                False,
                f"missing {required_label}",
                relative_path,
            )
        ]
    return []


def validate_required_template_section_text(
    root: Path,
    relative_path: str,
    section_heading: str,
    required_label: str,
    required_text: str,
) -> list[CheckResult]:
    text, missing_result = template_file_text(root, relative_path)
    if missing_result is not None:
        return [missing_result]
    assert text is not None
    visible_text = markdown_visible_text(text)
    section = markdown_section(visible_text, section_heading)
    section_text = markdown_visible_text(section or "")
    if section is None or required_text.casefold() not in section_text.casefold():
        return [
            CheckResult(
                f"template:text:{relative_path}:{required_label}",
                False,
                f"missing {required_label}",
                relative_path,
            )
        ]
    return []


def toml_path_exists(data: object, path: tuple[str, ...]) -> bool:
    current = data
    for part in path:
        if not isinstance(current, dict) or part not in current:
            return False
        current = current[part]
    return True


def toml_path_value(data: object, path: tuple[str, ...]) -> tuple[bool, object | None]:
    current = data
    for part in path:
        if not isinstance(current, dict) or part not in current:
            return False, None
        current = current[part]
    return True, current


def string_list_exactly_matches(value: object, expected: set[str]) -> bool:
    return (
        isinstance(value, list)
        and all(isinstance(item, str) for item in value)
        and len(value) == len(expected)
        and set(value) == expected
    )


def validate_toml_template_fields(
    root: Path,
    relative_path: str,
    required_fields: dict[str, tuple[str, ...]],
) -> list[CheckResult]:
    ok, detail, path = repo_relative_path_status(root, relative_path, "file")
    if not ok:
        if detail == "path contains symlink":
            detail = "template path contains symlink"
        return [CheckResult(f"template:path:{relative_path}", False, detail, relative_path)]
    try:
        data = load_toml(path)
    except tomllib.TOMLDecodeError as error:
        return [CheckResult(f"template:toml:{relative_path}", False, f"TOML invalid: {error.msg}", relative_path)]
    results: list[CheckResult] = []
    for field, path_parts in required_fields.items():
        if not toml_path_exists(data, path_parts):
            results.append(
                CheckResult(
                    f"template:toml:{relative_path}:{field}",
                    False,
                    f"missing {field}",
                    relative_path,
                )
            )
    for field, path_parts in TOML_REQUIRED_TABLES.get(relative_path, {}).items():
        exists, value = toml_path_value(data, path_parts)
        if exists and not isinstance(value, dict):
            results.append(
                CheckResult(
                    f"template:toml:{relative_path}:{field}",
                    False,
                    f"{field} must be a table",
                    relative_path,
                )
            )
    if relative_path == CONFIG_TEMPLATE_PATH:
        autonomy = data.get("autonomy")
        may_continue = autonomy.get("agent_may_continue_sessions") if isinstance(autonomy, dict) else None
        if may_continue is not False:
            results.append(
                CheckResult(
                    f"template:toml:{relative_path}:agent_may_continue_sessions",
                    False,
                    "agent_may_continue_sessions must be false",
                    relative_path,
                )
            )
        may_initiate = (
            autonomy.get("agent_may_initiate_project_initiatives") if isinstance(autonomy, dict) else None
        )
        if may_initiate is not False:
            results.append(
                CheckResult(
                    f"template:toml:{relative_path}:agent_may_initiate_project_initiatives",
                    False,
                    "agent_may_initiate_project_initiatives must be false",
                    relative_path,
                )
            )
        enabled = data.get("enabled")
        enabled_default = enabled.get("default") if isinstance(enabled, dict) else None
        if enabled_default is not False:
            results.append(
                CheckResult(
                    f"template:toml:{relative_path}:enabled.default",
                    False,
                    "enabled.default must be false",
                    relative_path,
                )
            )
        review = data.get("review")
        for flag in (
            "required_before_publish",
            "review_until_clean",
            "doc_closeout_required",
            "security_closeout_required",
        ):
            value = review.get(flag) if isinstance(review, dict) else None
            if value is not True:
                results.append(
                    CheckResult(
                        f"template:toml:{relative_path}:{flag}",
                        False,
                        f"review.{flag} must be true",
                        relative_path,
                    )
                )
        approval = data.get("approval")
        required_for = approval.get("required_for") if isinstance(approval, dict) else None
        if not string_list_exactly_matches(required_for, CANONICAL_APPROVAL_REQUIRED_FOR):
            results.append(
                CheckResult(
                    f"template:toml:{relative_path}:approval coverage",
                    False,
                    "approval.required_for must cover mutation side-effect labels",
                    relative_path,
                )
            )
    if relative_path in {AGENT_PROFILE_TEMPLATE_PATH, PLUGIN_MANIFEST_TEMPLATE_PATH}:
        permissions = data.get("permissions")
        approval_required_for = permissions.get("approval_required_for") if isinstance(permissions, dict) else None
        if not isinstance(approval_required_for, list) or not all(
            isinstance(item, str) and item in CANONICAL_APPROVAL_REQUIRED_FOR
            for item in approval_required_for
        ):
            results.append(
                CheckResult(
                    f"template:toml:{relative_path}:approval vocabulary",
                    False,
                    "approval_required_for must use canonical side-effect labels",
                    relative_path,
                )
            )
        if not string_list_exactly_matches(approval_required_for, CANONICAL_APPROVAL_REQUIRED_FOR):
            results.append(
                CheckResult(
                    f"template:toml:{relative_path}:approval coverage",
                    False,
                    "approval_required_for must cover mutation side-effect labels",
                    relative_path,
                )
            )
    if relative_path == AGENT_PROFILE_TEMPLATE_PATH:
        mode_exists, mode = toml_path_value(data, ("permissions", "mode"))
        if mode_exists and mode != "read-only":
            results.append(
                CheckResult(
                    f"template:toml:{relative_path}:permission_mode",
                    False,
                    "permissions.mode must be read-only",
                    relative_path,
                )
            )
        tools = data.get("tools")
        for field in ("allow", "deny"):
            value = tools.get(field) if isinstance(tools, dict) else None
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                results.append(
                    CheckResult(
                        f"template:toml:{relative_path}:tools_{field}",
                        False,
                        f"tools_{field} must be a list of strings",
                        relative_path,
                    )
                )
    if relative_path == PLUGIN_MANIFEST_TEMPLATE_PATH:
        permissions = data.get("permissions")
        approval_required_for = permissions.get("approval_required_for") if isinstance(permissions, dict) else None
        has_external_disclosure = (
            isinstance(approval_required_for, list)
            and any(
                isinstance(item, str) and item.casefold() == "external disclosure"
                for item in approval_required_for
            )
        )
        if not has_external_disclosure:
            results.append(
                CheckResult(
                    f"template:toml:{relative_path}:external disclosure approval",
                    False,
                    "approval_required_for must include external disclosure",
                    relative_path,
                )
            )
        ownership = data.get("ownership")
        source = ownership.get("source") if isinstance(ownership, dict) else None
        if not isinstance(source, str) or not source.strip():
            results.append(
                CheckResult(
                    f"template:toml:{relative_path}:source",
                    False,
                    "source must be a non-empty string",
                    relative_path,
                )
            )
    return results


def validate_root_templates(root: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    for relative_path in ROOT_TEMPLATE_FILES:
        markdown, missing_result = template_file_text(root, relative_path)
        if missing_result is not None:
            results.append(missing_result)
            continue
        assert markdown is not None
        if not has_template_status(markdown):
            results.append(
                CheckResult(
                    f"template:status:{relative_path}",
                    False,
                    "missing Status: Template",
                    relative_path,
                )
            )
        results.extend(validate_markdown_section_set(root, relative_path, ROOT_TEMPLATE_REQUIRED_SECTIONS[relative_path]))
    return results


def validate_skill_template(root: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    markdown, missing_result = template_file_text(root, SKILL_TEMPLATE_PATH)
    if missing_result is not None:
        return [missing_result]
    assert markdown is not None
    if re.match(r"\s*---\s*\n", markdown):
        results.append(
            CheckResult(
                f"template:skill:{SKILL_TEMPLATE_PATH}:live frontmatter",
                False,
                "live frontmatter is not allowed in template",
                SKILL_TEMPLATE_PATH,
            )
        )
    if not has_template_status(markdown):
        results.append(
            CheckResult(
                f"template:status:{SKILL_TEMPLATE_PATH}",
                False,
                "missing Status: Template",
                SKILL_TEMPLATE_PATH,
            )
        )
    results.extend(validate_markdown_section_set(root, SKILL_TEMPLATE_PATH, SKILL_TEMPLATE_SECTIONS))
    return results


def mask_span_preserving_lines(characters: list[str], start: int, end: int) -> None:
    for position in range(start, min(end, len(characters))):
        if characters[position] != "\n":
            characters[position] = " "


def previous_typescript_token(source: str, index: int) -> str | None:
    cursor = index - 1
    while cursor >= 0 and source[cursor].isspace():
        cursor -= 1
    if cursor < 0:
        return None
    if source[cursor].isidentifier() or source[cursor] in {"_", "$"}:
        end = cursor + 1
        while cursor >= 0 and (source[cursor].isidentifier() or source[cursor].isdigit() or source[cursor] in {"_", "$"}):
            cursor -= 1
        return source[cursor + 1 : end]
    return source[cursor]


def previous_nonspace_index(source: str, index: int) -> int | None:
    cursor = index - 1
    while cursor >= 0 and source[cursor].isspace():
        cursor -= 1
    return cursor if cursor >= 0 else None


def slash_starts_typescript_regex(source: str, index: int) -> bool:
    previous_token = previous_typescript_token(source, index)
    if previous_token is None:
        return True
    if previous_token in {"return", "throw", "case", "delete", "void", "typeof", "yield", "await"}:
        return True
    previous_index = previous_nonspace_index(source, index)
    if previous_index is not None and source[previous_index] == ">" and previous_index > 0 and source[previous_index - 1] == "=":
        return True
    return previous_token in {"(", "{", "[", "=", ":", ",", ";", "!", "?", "&", "|", "+", "-", "*", "~", "^", "<"}


def typescript_regex_literal_end(source: str, start: int) -> int:
    index = start + 1
    escaped = False
    in_character_class = False
    while index < len(source):
        character = source[index]
        if character == "\n":
            return index
        if escaped:
            escaped = False
        elif character == "\\":
            escaped = True
        elif character == "[":
            in_character_class = True
        elif character == "]" and in_character_class:
            in_character_class = False
        elif character == "/" and not in_character_class:
            index += 1
            while index < len(source) and (source[index].isalpha() or source[index] in {"_", "$"}):
                index += 1
            return index
        index += 1
    return len(source)


def typescript_has_template_interpolation(source: str) -> bool:
    index = 0
    while index < len(source):
        character = source[index]
        next_character = source[index + 1] if index + 1 < len(source) else ""
        if character in {"'", '"'}:
            quote = character
            index += 1
            escaped = False
            while index < len(source):
                current = source[index]
                if escaped:
                    escaped = False
                elif current == "\\":
                    escaped = True
                elif current == quote:
                    index += 1
                    break
                index += 1
            continue
        if character == "/" and next_character == "/":
            index += 2
            while index < len(source) and source[index] != "\n":
                index += 1
            continue
        if character == "/" and next_character == "*":
            index += 2
            while index < len(source) - 1:
                if source[index] == "*" and source[index + 1] == "/":
                    index += 2
                    break
                index += 1
            continue
        if character == "`":
            index += 1
            escaped = False
            while index < len(source):
                current = source[index]
                next_current = source[index + 1] if index + 1 < len(source) else ""
                if escaped:
                    escaped = False
                elif current == "\\":
                    escaped = True
                elif current == "$" and next_current == "{":
                    return True
                elif current == "`":
                    index += 1
                    break
                index += 1
            continue
        index += 1
    return False


def typescript_structure_source(source: str) -> str:
    characters = list(source)
    index = 0
    while index < len(source):
        character = source[index]
        next_character = source[index + 1] if index + 1 < len(source) else ""
        if character in {"'", '"', "`"}:
            quote = character
            cursor = index + 1
            escaped = False
            while cursor < len(source):
                current = source[cursor]
                if escaped:
                    escaped = False
                elif current == "\\":
                    escaped = True
                elif current == quote:
                    cursor += 1
                    break
                cursor += 1
            mask_span_preserving_lines(characters, index, cursor)
            index = cursor
            continue
        if character == "/" and next_character == "/":
            cursor = index + 2
            while cursor < len(source) and source[cursor] != "\n":
                cursor += 1
            mask_span_preserving_lines(characters, index, cursor)
            index = cursor
            continue
        if character == "/" and next_character == "*":
            cursor = index + 2
            while cursor < len(source) - 1:
                if source[cursor] == "*" and source[cursor + 1] == "/":
                    cursor += 2
                    break
                cursor += 1
            mask_span_preserving_lines(characters, index, cursor)
            index = cursor
            continue
        if character == "/" and slash_starts_typescript_regex(source, index):
            cursor = typescript_regex_literal_end(source, index)
            if cursor > index + 1:
                mask_span_preserving_lines(characters, index, cursor)
                index = cursor
                continue
        index += 1
    return "".join(characters)


def balanced_typescript_span(structure_source: str, opening_index: int, open_character: str, close_character: str) -> int | None:
    depth = 1
    index = opening_index + 1
    while index < len(structure_source):
        character = structure_source[index]
        if character == open_character:
            depth += 1
        elif character == close_character:
            depth -= 1
            if depth == 0:
                return index
        index += 1
    return None


def previous_nonspace_character(source: str, index: int) -> str | None:
    cursor = index - 1
    while cursor >= 0 and source[cursor].isspace():
        cursor -= 1
    return source[cursor] if cursor >= 0 else None


def find_top_level_export_const_object(source: str, structure_source: str, object_name: str) -> str | None:
    pattern = re.compile(rf"export\s+const\s+{re.escape(object_name)}\s*=")
    index = 0
    depth = 0
    while index < len(structure_source):
        if depth == 0:
            match = pattern.match(structure_source, index)
            if match is not None:
                cursor = match.end()
                while cursor < len(structure_source) and structure_source[cursor].isspace():
                    cursor += 1
                if cursor >= len(structure_source) or structure_source[cursor] != "{":
                    return None
                close_index = balanced_typescript_span(structure_source, cursor, "{", "}")
                if close_index is None:
                    return None
                return source[cursor + 1 : close_index]
        character = structure_source[index]
        if character in "{[(":
            depth += 1
        elif character in "}])":
            depth = max(0, depth - 1)
        index += 1
    return None


def find_typescript_function_body_opening_brace(structure_source: str, start: int) -> int | None:
    index = start
    angle_depth = 0
    paren_depth = 0
    bracket_depth = 0
    brace_depth = 0
    while index < len(structure_source):
        character = structure_source[index]
        if character == "<":
            angle_depth += 1
        elif character == ">" and angle_depth > 0:
            angle_depth -= 1
        elif character == "(":
            paren_depth += 1
        elif character == ")" and paren_depth > 0:
            paren_depth -= 1
        elif character == "[":
            bracket_depth += 1
        elif character == "]" and bracket_depth > 0:
            bracket_depth -= 1
        elif character == "{":
            previous_character = previous_nonspace_character(structure_source, index)
            if (
                angle_depth == 0
                and paren_depth == 0
                and bracket_depth == 0
                and brace_depth == 0
                and previous_character not in {":", "<", "|", "&", ",", "=", "?"}
            ):
                return index
            brace_depth += 1
        elif character == "}" and brace_depth > 0:
            brace_depth -= 1
        elif character == ";" and angle_depth == 0 and paren_depth == 0 and bracket_depth == 0 and brace_depth == 0:
            return None
        index += 1
    return None


def typescript_exported_function_body(source: str, structure_source: str, function_name: str) -> str | None:
    pattern = re.compile(rf"export\s+(?:async\s+)?function\s+{re.escape(function_name)}\s*(?P<open>\()")
    index = 0
    depth = 0
    while index < len(structure_source):
        if depth == 0:
            match = pattern.match(structure_source, index)
            if match is not None:
                opening_paren = match.start("open")
                closing_paren = balanced_typescript_span(structure_source, opening_paren, "(", ")")
                if closing_paren is None:
                    return None
                opening_brace = find_typescript_function_body_opening_brace(structure_source, closing_paren + 1)
                if opening_brace is None:
                    return None
                closing_brace = balanced_typescript_span(structure_source, opening_brace, "{", "}")
                if closing_brace is None:
                    return None
                return source[opening_brace + 1 : closing_brace]
        character = structure_source[index]
        if character in "{[(":
            depth += 1
        elif character in "}])":
            depth = max(0, depth - 1)
        index += 1
    return None


def typescript_exported_function_parameters(source: str, structure_source: str, function_name: str) -> str | None:
    pattern = re.compile(rf"export\s+(?:async\s+)?function\s+{re.escape(function_name)}\s*(?P<open>\()")
    index = 0
    depth = 0
    while index < len(structure_source):
        if depth == 0:
            match = pattern.match(structure_source, index)
            if match is not None:
                opening_paren = match.start("open")
                closing_paren = balanced_typescript_span(structure_source, opening_paren, "(", ")")
                if closing_paren is None:
                    return None
                return source[opening_paren + 1 : closing_paren]
        character = structure_source[index]
        if character in "{[(":
            depth += 1
        elif character in "}])":
            depth = max(0, depth - 1)
        index += 1
    return None


def typescript_top_level_statement_end(structure_source: str, start: int) -> int | None:
    depth = 0
    index = start
    while index < len(structure_source):
        character = structure_source[index]
        if character in "{[(":
            depth += 1
        elif character in "}])":
            depth = max(0, depth - 1)
        elif character == ";" and depth == 0:
            return index + 1
        index += 1
    return None


def typescript_top_level_function_end(structure_source: str, function_name: str, start: int) -> int | None:
    pattern = re.compile(rf"export\s+(?:async\s+)?function\s+{re.escape(function_name)}\s*(?P<open>\()")
    match = pattern.match(structure_source, start)
    if match is None:
        return None
    opening_paren = match.start("open")
    closing_paren = balanced_typescript_span(structure_source, opening_paren, "(", ")")
    if closing_paren is None:
        return None
    opening_brace = find_typescript_function_body_opening_brace(structure_source, closing_paren + 1)
    if opening_brace is None:
        return None
    closing_brace = balanced_typescript_span(structure_source, opening_brace, "{", "}")
    if closing_brace is None:
        return None
    return closing_brace + 1


def hook_top_level_declarations_are_allowed(structure_source: str) -> bool:
    index = 0
    seen_contract = False
    seen_handle = False
    while True:
        index = skip_typescript_whitespace(structure_source, index)
        if index >= len(structure_source):
            return seen_contract and seen_handle
        if re.match(r"\bexport\s+const\s+hookContract\s*=", structure_source[index:]) is not None:
            if seen_contract:
                return False
            end = typescript_top_level_statement_end(structure_source, index)
            if end is None:
                return False
            seen_contract = True
            index = end
            continue
        if re.match(r"\bexport\s+type\s+[A-Za-z_$][A-Za-z0-9_$]*\s*=", structure_source[index:]) is not None:
            end = typescript_top_level_statement_end(structure_source, index)
            if end is None:
                return False
            index = end
            continue
        function_end = typescript_top_level_function_end(structure_source, "handle", index)
        if function_end is not None:
            if seen_handle:
                return False
            seen_handle = True
            index = function_end
            continue
        return False


def typescript_return_value_at(
    function_body: str,
    structure_body: str,
    return_start: int,
) -> tuple[str | None, int]:
    value_start = return_start + len("return")
    line_index = value_start
    while line_index < len(structure_body) and structure_body[line_index] in " \t\r":
        line_index += 1
    if line_index < len(structure_body) and structure_body[line_index] == "\n":
        return None, line_index + 1
    value_start = line_index
    if value_start < len(structure_body) and structure_body[value_start] == "{":
        close_index = balanced_typescript_span(structure_body, value_start, "{", "}")
        if close_index is None:
            return None, len(structure_body)
        statement_end = close_index + 1
        while statement_end < len(structure_body) and structure_body[statement_end] in " \t\r":
            statement_end += 1
        if statement_end >= len(structure_body):
            return function_body[value_start + 1 : close_index], statement_end
        if structure_body[statement_end] == ";":
            return function_body[value_start + 1 : close_index], statement_end + 1
        if structure_body[statement_end] == "\n":
            next_token = statement_end + 1
            while next_token < len(structure_body) and structure_body[next_token].isspace():
                next_token += 1
            if next_token >= len(structure_body) or structure_body[next_token] == "}":
                return function_body[value_start + 1 : close_index], next_token
        semicolon_index = structure_body.find(";", statement_end)
        next_index = semicolon_index + 1 if semicolon_index != -1 else len(structure_body)
        return None, next_index
    semicolon_index = structure_body.find(";", value_start)
    next_index = semicolon_index + 1 if semicolon_index != -1 else len(structure_body)
    return None, next_index


def typescript_return_values(function_body: str) -> list[str | None]:
    structure_body = typescript_structure_source(function_body)
    results: list[str | None] = []
    if re.search(r"\bfunction\b|=>", structure_body):
        results.append(None)
    index = 0
    while index < len(structure_body):
        return_match = re.search(r"\breturn\b", structure_body[index:])
        if return_match is None:
            break
        return_start = index + return_match.start()
        return_value, index = typescript_return_value_at(function_body, structure_body, return_start)
        results.append(return_value)
    return results


def typescript_top_level_return_values(function_body: str) -> list[str | None]:
    structure_body = typescript_structure_source(function_body)
    results: list[str | None] = []
    index = 0
    depth = 0
    while index < len(structure_body):
        if depth == 0 and re.match(r"\breturn\b", structure_body[index:]):
            return_value, index = typescript_return_value_at(function_body, structure_body, index)
            results.append(return_value)
            continue
        character = structure_body[index]
        if character in "{[(":
            depth += 1
        elif character in "}])":
            depth = max(0, depth - 1)
        index += 1
    return results


def split_typescript_top_level_object_fields(object_body: str) -> list[str]:
    fields: list[str] = []
    structure_body = typescript_structure_source(object_body)
    field_start = 0
    depth = 0
    index = 0
    while index < len(structure_body):
        character = structure_body[index]
        if character in "{[(":
            depth += 1
        elif character in "}])":
            depth = max(0, depth - 1)
        elif character == "," and depth == 0:
            fields.append(object_body[field_start:index].strip())
            field_start = index + 1
        index += 1
    tail = object_body[field_start:].strip()
    if tail:
        fields.append(tail)
    return fields


def parse_typescript_simple_data_field(field: str) -> tuple[str, str] | None:
    stripped_field = field.strip().rstrip(";").strip()
    if not stripped_field:
        return None
    if stripped_field.startswith(("...", "[", '"', "'")):
        return None
    if re.match(
        r"(?:async\s+)?\*?\s*(?:get\s+|set\s+)?[A-Za-z_$][A-Za-z0-9_$]*\s*\(",
        stripped_field,
        flags=re.DOTALL,
    ):
        return None
    field_match = re.fullmatch(
        r"(?P<name>[A-Za-z_$][A-Za-z0-9_$]*)\s*:\s*(?P<value>.+)",
        stripped_field,
        flags=re.DOTALL,
    )
    if field_match is None:
        return None
    return field_match.group("name"), field_match.group("value").strip()


def typescript_object_string_value(object_body: str, field_name: str) -> str | None:
    values: list[str] = []
    for field in split_typescript_top_level_object_fields(object_body):
        parsed_field = parse_typescript_simple_data_field(field)
        if parsed_field is None:
            return None
        name, value = parsed_field
        if name != field_name:
            continue
        string_match = re.fullmatch(r"(?P<quote>[\"'])(?P<value>[^\"']*)(?P=quote)", value, flags=re.DOTALL)
        if string_match is None:
            return None
        values.append(string_match.group("value"))
    if len(values) != 1:
        return None
    return values[0]


def typescript_object_has_literal_false(object_body: str, field_name: str) -> bool:
    allow_field_count = 0
    reason_field_count = 0
    for field in split_typescript_top_level_object_fields(object_body):
        parsed_field = parse_typescript_simple_data_field(field)
        if parsed_field is None:
            return False
        name, value = parsed_field
        if name != field_name:
            if name != "reason":
                return False
            reason_field_count += 1
            reason_match = re.fullmatch(r"(?P<quote>[\"'])(?P<value>[^\"']*)(?P=quote)", value, flags=re.DOTALL)
            if reason_field_count > 1 or reason_match is None or not reason_match.group("value").strip():
                return False
            continue
        allow_field_count += 1
        if allow_field_count > 1 or value != "false":
            return False
    return allow_field_count == 1 and reason_field_count == 1


def skip_typescript_whitespace(structure_source: str, index: int) -> int:
    while index < len(structure_source) and structure_source[index].isspace():
        index += 1
    return index


def consume_fail_closed_hook_return(function_body: str, structure_body: str, index: int) -> int | None:
    if re.match(r"\breturn\b", structure_body[index:]) is None:
        return None
    return_value, next_index = typescript_return_value_at(function_body, structure_body, index)
    if return_value is None or not typescript_object_has_literal_false(return_value, "allow"):
        return None
    return next_index


def typescript_condition_is_read_only(condition: str) -> bool:
    stripped = condition.strip()
    if not stripped:
        return False
    if any(character in stripped for character in "(){}[];,"):
        return False
    if re.search(r"\b(await|new|delete|yield|throw|import|function|class)\b", stripped):
        return False
    if "=>" in stripped or "++" in stripped or "--" in stripped:
        return False
    if re.search(r"(\+=|-=|\*=|/=|%=|&&=|\|\|=|\?\?=)", stripped):
        return False
    if re.search(r"(?<![=!<>])=(?![=>])", stripped):
        return False
    return re.fullmatch(r"[A-Za-z0-9_$.\s!&|=<>]*", stripped) is not None


def hook_parameters_are_simple(parameters: str) -> bool:
    structure_parameters = typescript_structure_source(parameters).strip()
    return re.fullmatch(r"event\s*:\s*HookEvent\s*\|\s*null\s*\|\s*undefined\s*", structure_parameters) is not None


def hook_body_has_malformed_event_guard(function_body: str) -> bool:
    structure_body = typescript_structure_source(function_body)
    index = skip_typescript_whitespace(structure_body, 0)
    if re.match(r"\bif\b", structure_body[index:]) is None:
        return False
    cursor = skip_typescript_whitespace(structure_body, index + len("if"))
    if cursor >= len(structure_body) or structure_body[cursor] != "(":
        return False
    condition_end = balanced_typescript_span(structure_body, cursor, "(", ")")
    if condition_end is None:
        return False
    condition = function_body[cursor + 1 : condition_end].strip()
    if re.fullmatch(r"!event\s*\|\|\s*!event\.kind", condition) is None:
        return False
    cursor = skip_typescript_whitespace(structure_body, condition_end + 1)
    if cursor >= len(structure_body) or structure_body[cursor] != "{":
        return False
    block_end = balanced_typescript_span(structure_body, cursor, "{", "}")
    if block_end is None:
        return False
    block_body = function_body[cursor + 1 : block_end]
    block_structure = typescript_structure_source(block_body)
    block_index = skip_typescript_whitespace(block_structure, 0)
    return_end = consume_fail_closed_hook_return(block_body, block_structure, block_index)
    if return_end is None:
        return False
    return skip_typescript_whitespace(block_structure, return_end) >= len(block_structure)


def hook_body_contains_only_fail_closed_decisions(function_body: str) -> bool:
    structure_body = typescript_structure_source(function_body)
    index = 0
    found_decision = False
    while True:
        index = skip_typescript_whitespace(structure_body, index)
        if index >= len(structure_body):
            return found_decision
        return_end = consume_fail_closed_hook_return(function_body, structure_body, index)
        if return_end is not None:
            found_decision = True
            index = return_end
            continue
        if re.match(r"\bif\b", structure_body[index:]) is None:
            return False
        cursor = skip_typescript_whitespace(structure_body, index + len("if"))
        if cursor >= len(structure_body) or structure_body[cursor] != "(":
            return False
        condition_end = balanced_typescript_span(structure_body, cursor, "(", ")")
        if condition_end is None:
            return False
        if not typescript_condition_is_read_only(function_body[cursor + 1 : condition_end]):
            return False
        cursor = skip_typescript_whitespace(structure_body, condition_end + 1)
        if cursor >= len(structure_body) or structure_body[cursor] != "{":
            return False
        block_end = balanced_typescript_span(structure_body, cursor, "{", "}")
        if block_end is None:
            return False
        block_body = function_body[cursor + 1 : block_end]
        if not hook_body_contains_only_fail_closed_decisions(block_body):
            return False
        found_decision = True
        index = block_end + 1
        after_block = skip_typescript_whitespace(structure_body, index)
        if re.match(r"\belse\b", structure_body[after_block:]):
            return False


def validate_hook_template(root: Path) -> list[CheckResult]:
    text, missing_result = template_file_text(root, HOOK_TEMPLATE_PATH)
    if missing_result is not None:
        return [missing_result]
    assert text is not None
    structure_text = typescript_structure_source(text)
    hook_contract_body = find_top_level_export_const_object(text, structure_text, "hookContract") or ""
    results: list[CheckResult] = []
    hook_contract_references = len(re.findall(r"\bhookContract\b", structure_text))
    if hook_contract_references > 1:
        results.append(
            CheckResult(
                f"template:hook:{HOOK_TEMPLATE_PATH}:hook contract mutation",
                False,
                "hookContract must not be referenced outside its exported declaration",
                HOOK_TEMPLATE_PATH,
            )
        )
    if typescript_has_template_interpolation(text):
        results.append(
            CheckResult(
                f"template:hook:{HOOK_TEMPLATE_PATH}:pre-decision side effects",
                False,
                "handler must contain only fail-closed decision returns",
                HOOK_TEMPLATE_PATH,
            )
        )
    if not hook_top_level_declarations_are_allowed(structure_text):
        results.append(
            CheckResult(
                f"template:hook:{HOOK_TEMPLATE_PATH}:pre-decision side effects",
                False,
                "handler must contain only fail-closed decision returns",
                HOOK_TEMPLATE_PATH,
            )
        )
    for phrase, field_name in HOOK_REQUIRED_CONTRACT_FIELDS.items():
        field_pattern = rf"(?m)^\s*{re.escape(field_name)}\s*:"
        if re.search(field_pattern, hook_contract_body) is None:
            results.append(
                CheckResult(
                    f"template:hook:{HOOK_TEMPLATE_PATH}:{phrase}",
                    False,
                    f"missing {phrase}",
                    HOOK_TEMPLATE_PATH,
                )
            )
    approval_behavior = typescript_object_string_value(hook_contract_body, "approvalBehavior")
    side_effect_classification = typescript_object_string_value(hook_contract_body, "sideEffectClassification")
    required_approval_behavior = HOOK_REQUIRED_CONTRACT_VALUES["approvalBehavior"]
    if approval_behavior != required_approval_behavior:
        results.append(
            CheckResult(
                f"template:hook:{HOOK_TEMPLATE_PATH}:approval behavior",
                False,
                "approval behavior must require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                HOOK_TEMPLATE_PATH,
            )
        )
    if side_effect_classification is None or "external disclosure" not in side_effect_classification.casefold():
        results.append(
            CheckResult(
                f"template:hook:{HOOK_TEMPLATE_PATH}:external disclosure classification",
                False,
                "side-effect classification must include external disclosure",
                HOOK_TEMPLATE_PATH,
            )
        )
    elif side_effect_classification != HOOK_REQUIRED_CONTRACT_VALUES["sideEffectClassification"]:
        results.append(
            CheckResult(
                f"template:hook:{HOOK_TEMPLATE_PATH}:side-effect classification vocabulary",
                False,
                "side-effect classification must use canonical labels",
                HOOK_TEMPLATE_PATH,
            )
        )
    if approval_behavior is None or "external disclosure" not in approval_behavior.casefold():
        results.append(
            CheckResult(
                f"template:hook:{HOOK_TEMPLATE_PATH}:external disclosure approval",
                False,
                "approval behavior must include external disclosure",
                HOOK_TEMPLATE_PATH,
            )
        )
    failure_handling = typescript_object_string_value(hook_contract_body, "failureHandling")
    if failure_handling != HOOK_REQUIRED_CONTRACT_VALUES["failureHandling"]:
        results.append(
            CheckResult(
                f"template:hook:{HOOK_TEMPLATE_PATH}:failure handling",
                False,
                "failure handling must fail closed",
                HOOK_TEMPLATE_PATH,
            )
        )
    function_parameters = typescript_exported_function_parameters(text, structure_text, "handle")
    function_body = typescript_exported_function_body(text, structure_text, "handle")
    if function_body is None or function_parameters is None:
        results.append(
            CheckResult(
                f"template:hook:{HOOK_TEMPLATE_PATH}:exported hook contract",
                False,
                "missing exported hook contract",
                HOOK_TEMPLATE_PATH,
            )
        )
    elif (
        not hook_parameters_are_simple(function_parameters)
        or not hook_body_has_malformed_event_guard(function_body)
        or not hook_body_contains_only_fail_closed_decisions(function_body)
    ):
        results.append(
            CheckResult(
                f"template:hook:{HOOK_TEMPLATE_PATH}:pre-decision side effects",
                False,
                "handler must contain only fail-closed decision returns",
                HOOK_TEMPLATE_PATH,
            )
        )
    return_values = typescript_return_values(function_body) if function_body is not None else []
    top_level_return_values = typescript_top_level_return_values(function_body) if function_body is not None else []
    has_fail_closed_return = bool(return_values) and all(
        return_value is not None and typescript_object_has_literal_false(return_value, "allow")
        for return_value in return_values
    ) and bool(top_level_return_values) and all(
        return_value is not None and typescript_object_has_literal_false(return_value, "allow")
        for return_value in top_level_return_values
    )
    if not has_fail_closed_return:
        results.append(
            CheckResult(
                f"template:hook:{HOOK_TEMPLATE_PATH}:default decision",
                False,
                "default decision must fail closed",
                HOOK_TEMPLATE_PATH,
            )
        )
    return results


def call_is_main(node: ast.AST) -> bool:
    return isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "main"


def sole_main_exit_argument(call: ast.Call) -> bool:
    return len(call.args) == 1 and not call.keywords and call_is_main(call.args[0])


def statement_invokes_main(statement: ast.stmt) -> bool:
    if isinstance(statement, ast.Raise) and statement.exc is not None:
        exc = statement.exc
        return (
            statement.cause is None
            and isinstance(exc, ast.Call)
            and isinstance(exc.func, ast.Name)
            and exc.func.id == "SystemExit"
            and sole_main_exit_argument(exc)
        )
    return False


def main_definition_is_plain(node: ast.FunctionDef) -> bool:
    arguments = node.args
    return (
        not node.decorator_list
        and not arguments.posonlyargs
        and not arguments.args
        and arguments.vararg is None
        and not arguments.kwonlyargs
        and not arguments.kw_defaults
        and arguments.kwarg is None
        and not arguments.defaults
        and isinstance(node.returns, ast.Name)
        and node.returns.id == "int"
    )


def script_function_definition_has_plain_signature(node: ast.FunctionDef) -> bool:
    arguments = node.args
    return (
        not node.decorator_list
        and not arguments.defaults
        and not arguments.kw_defaults
        and arguments.vararg is None
        and arguments.kwarg is None
    )


def dataclass_decorator_is_allowed(node: ast.expr) -> bool:
    if isinstance(node, ast.Name) and node.id == "dataclass":
        return True
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "dataclass"
        and not node.args
        and all(
            keyword.arg == "frozen" and isinstance(keyword.value, ast.Constant) and keyword.value.value is True
            for keyword in node.keywords
        )
    )


def script_class_definition_is_plain(node: ast.ClassDef) -> bool:
    return (
        not node.bases
        and not node.keywords
        and all(dataclass_decorator_is_allowed(decorator) for decorator in node.decorator_list)
        and all(
            (isinstance(statement, ast.AnnAssign) and statement.value is None)
            or isinstance(statement, ast.Pass)
            or (isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Constant) and isinstance(statement.value.value, str))
            for statement in node.body
        )
    )


ALLOWED_SCRIPT_CALL_NAMES = {"CheckResult", "SystemExit", "all", "asdict", "bool", "dataclass", "main", "print", "run"}
ALLOWED_SCRIPT_CALL_ATTRIBUTES = {"ArgumentParser", "add_argument", "dumps", "parse_args", "strip"}
ALLOWED_SCRIPT_IMPORT_ROOTS = {"__future__", "argparse", "dataclasses", "json"}
FORBIDDEN_SCRIPT_NAME_REFERENCES = {
    "__builtins__",
    "__import__",
    "compile",
    "eval",
    "exec",
    "getattr",
    "globals",
    "input",
    "locals",
    "open",
    "setattr",
    "vars",
}
RESERVED_SCRIPT_BINDING_NAMES = ALLOWED_SCRIPT_CALL_NAMES | {
    "argparse",
    "asdict",
    "dataclass",
    "json",
}
FORBIDDEN_SCRIPT_IMPORT_ROOTS = {
    "aiohttp",
    "ftplib",
    "http",
    "httpx",
    "imaplib",
    "os",
    "paramiko",
    "poplib",
    "requests",
    "shutil",
    "smtplib",
    "socket",
    "subprocess",
    "telnetlib",
    "urllib",
    "webbrowser",
}


def import_root(module_name: str) -> str:
    return module_name.split(".", 1)[0]


def script_has_forbidden_import(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if not node.names:
                return True
            for alias in node.names:
                if alias.asname is not None:
                    return True
                if alias.name not in {"argparse", "json"}:
                    return True
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            names = {alias.name for alias in node.names}
            if any(alias.asname is not None or alias.name == "*" for alias in node.names):
                return True
            if module == "__future__":
                if names != {"annotations"}:
                    return True
            elif module == "dataclasses":
                if not names or not names <= {"asdict", "dataclass"}:
                    return True
            else:
                return True
    return False


def script_has_forbidden_name_reference(tree: ast.AST) -> bool:
    return any(
        isinstance(node, ast.Name)
        and isinstance(node.ctx, ast.Load)
        and node.id in FORBIDDEN_SCRIPT_NAME_REFERENCES
        for node in ast.walk(tree)
    )


def script_target_names(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Name):
        return [node.id]
    if isinstance(node, (ast.Tuple, ast.List)):
        names: list[str] = []
        for element in node.elts:
            names.extend(script_target_names(element))
        return names
    return []


def script_has_reserved_rebinding(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        targets: list[ast.AST] = []
        if isinstance(node, ast.Assign):
            targets = list(node.targets)
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        elif isinstance(node, ast.AugAssign):
            targets = [node.target]
        elif isinstance(node, ast.NamedExpr):
            targets = [node.target]
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            targets = [node.target]
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name in RESERVED_SCRIPT_BINDING_NAMES and node.name not in {"main", "run"}:
                return True
        elif isinstance(node, ast.ClassDef):
            if node.name in RESERVED_SCRIPT_BINDING_NAMES and node.name != "CheckResult":
                return True
        for target in targets:
            if any(name in RESERVED_SCRIPT_BINDING_NAMES for name in script_target_names(target)):
                return True
    return False


def script_name(node: ast.AST, name: str) -> bool:
    return isinstance(node, ast.Name) and node.id == name


def script_attribute(node: ast.AST, owner: str, attribute: str) -> bool:
    return (
        isinstance(node, ast.Attribute)
        and node.attr == attribute
        and script_name(node.value, owner)
    )


def script_constant_string(node: ast.AST) -> bool:
    return isinstance(node, ast.Constant) and isinstance(node.value, str)


def script_keyword_value_is_literal(keyword: ast.keyword) -> bool:
    return isinstance(keyword.value, ast.Constant) and isinstance(keyword.value.value, (str, int, bool))


def script_keywords_match_literals(node: ast.Call, allowed_keywords: set[str]) -> bool:
    if any(keyword.arg is None or keyword.arg not in allowed_keywords for keyword in node.keywords):
        return False
    return all(script_keyword_value_is_literal(keyword) for keyword in node.keywords)


def script_comprehension_is_safe(generator: ast.comprehension) -> bool:
    return (
        not generator.is_async
        and len(script_target_names(generator.target)) == 1
        and script_target_names(generator.target)[0] == "result"
        and script_name(generator.iter, "results")
        and not generator.ifs
    )


def script_expression_is_safe(node: ast.AST) -> bool:
    if isinstance(node, ast.Constant):
        return True
    if isinstance(node, ast.Name):
        return node.id in {"args", "result", "results", "status", "subject"}
    if isinstance(node, ast.Attribute):
        return script_expression_is_safe(node.value)
    if isinstance(node, ast.Call):
        return script_call_is_allowed(node)
    if isinstance(node, ast.IfExp):
        return (
            script_expression_is_safe(node.test)
            and script_expression_is_safe(node.body)
            and script_expression_is_safe(node.orelse)
        )
    if isinstance(node, ast.List):
        return all(script_expression_is_safe(element) for element in node.elts)
    if isinstance(node, ast.ListComp):
        return (
            len(node.generators) == 1
            and script_comprehension_is_safe(node.generators[0])
            and script_expression_is_safe(node.elt)
        )
    if isinstance(node, ast.GeneratorExp):
        return (
            len(node.generators) == 1
            and script_comprehension_is_safe(node.generators[0])
            and script_expression_is_safe(node.elt)
        )
    if isinstance(node, ast.JoinedStr):
        return all(script_expression_is_safe(value) for value in node.values)
    if isinstance(node, ast.FormattedValue):
        return node.format_spec is None and script_expression_is_safe(node.value)
    return False


def script_add_argument_call_is_allowed(node: ast.Call) -> bool:
    if not (isinstance(node.func, ast.Attribute) and node.func.attr == "add_argument" and script_name(node.func.value, "parser")):
        return False
    if not node.args or not all(script_constant_string(argument) for argument in node.args):
        return False
    if any(keyword.arg is None or keyword.arg not in {"action", "help"} for keyword in node.keywords):
        return False
    for keyword in node.keywords:
        if keyword.arg == "help" and not script_constant_string(keyword.value):
            return False
        if keyword.arg == "action" and not (
            script_constant_string(keyword.value) and keyword.value.value == "store_true"
        ):
            return False
    return True


def script_call_is_allowed(node: ast.Call) -> bool:
    if any(keyword.arg is None for keyword in node.keywords):
        return False
    if any(keyword.arg == "type" for keyword in node.keywords):
        return False
    if isinstance(node.func, ast.Name):
        if node.func.id == "CheckResult":
            return (
                not node.args
                and {keyword.arg for keyword in node.keywords} == {"detail", "name", "ok"}
                and all(script_expression_is_safe(keyword.value) for keyword in node.keywords)
            )
        if node.func.id == "SystemExit":
            return sole_main_exit_argument(node)
        if node.func.id == "all":
            return len(node.args) == 1 and not node.keywords and script_expression_is_safe(node.args[0])
        if node.func.id == "asdict":
            return len(node.args) == 1 and not node.keywords and script_name(node.args[0], "result")
        if node.func.id == "bool":
            return len(node.args) == 1 and not node.keywords and script_expression_is_safe(node.args[0])
        if node.func.id == "dataclass":
            return dataclass_decorator_is_allowed(node)
        if node.func.id == "main":
            return not node.args and not node.keywords
        if node.func.id == "print":
            return len(node.args) == 1 and not node.keywords and script_expression_is_safe(node.args[0])
        if node.func.id == "run":
            return len(node.args) == 1 and not node.keywords and script_expression_is_safe(node.args[0])
        return False
    if isinstance(node.func, ast.Attribute):
        if script_attribute(node.func, "argparse", "ArgumentParser"):
            return not node.args and script_keywords_match_literals(node, {"description"})
        if node.func.attr == "add_argument":
            return script_add_argument_call_is_allowed(node)
        if isinstance(node.func.value, ast.Name) and node.func.value.id == "parser" and node.func.attr == "parse_args":
            return not node.args and not node.keywords
        if script_attribute(node.func, "json", "dumps"):
            return (
                len(node.args) == 1
                and script_expression_is_safe(node.args[0])
                and script_keywords_match_literals(node, {"indent", "sort_keys"})
            )
        if isinstance(node.func.value, ast.Name) and node.func.value.id == "subject" and node.func.attr == "strip":
            return not node.args and not node.keywords
        return False
    return False


def script_uses_only_allowed_calls(tree: ast.AST) -> bool:
    return (
        not script_has_forbidden_import(tree)
        and not script_has_forbidden_name_reference(tree)
        and not script_has_reserved_rebinding(tree)
    ) and all(
        script_call_is_allowed(node)
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
    )


def script_top_level_statement_is_allowed(statement: ast.stmt, guard: ast.If) -> bool:
    if statement is guard:
        return True
    if isinstance(statement, ast.Expr):
        return isinstance(statement.value, ast.Constant) and isinstance(statement.value.value, str)
    if isinstance(statement, (ast.Import, ast.ImportFrom)):
        return True
    if isinstance(statement, ast.ClassDef):
        return script_class_definition_is_plain(statement)
    if isinstance(statement, ast.FunctionDef):
        return script_function_definition_has_plain_signature(statement)
    return False


def script_has_cli_entry_point(tree: ast.AST) -> bool:
    if not script_uses_only_allowed_calls(tree):
        return False
    main_definitions = [
        (index, node)
        for index, node in enumerate(tree.body)
        if isinstance(node, ast.FunctionDef) and node.name == "main"
    ]
    if len(main_definitions) != 1:
        return False
    main_definition_index, main_definition = main_definitions[0]
    if not main_definition_is_plain(main_definition):
        return False
    matching_guards: list[tuple[int, ast.If]] = []
    for index, node in enumerate(tree.body):
        if not isinstance(node, ast.If):
            continue
        if not isinstance(node.test, ast.Compare):
            continue
        left = node.test.left
        comparators = node.test.comparators
        if not (isinstance(left, ast.Name) and left.id == "__name__"):
            continue
        if len(node.test.ops) != 1 or not isinstance(node.test.ops[0], ast.Eq):
            continue
        if len(comparators) != 1 or not (
            isinstance(comparators[0], ast.Constant) and comparators[0].value == "__main__"
        ):
            continue
        matching_guards.append((index, node))
    if len(matching_guards) != 1:
        return False
    guard_index, guard = matching_guards[0]
    if guard_index <= main_definition_index:
        return False
    if guard_index != main_definition_index + 1 or guard_index != len(tree.body) - 1:
        return False
    if not all(script_top_level_statement_is_allowed(statement, guard) for statement in tree.body):
        return False
    return not guard.orelse and len(guard.body) == 1 and statement_invokes_main(guard.body[0])


def validate_script_template(root: Path) -> list[CheckResult]:
    text, missing_result = template_file_text(root, SCRIPT_TEMPLATE_PATH)
    if missing_result is not None:
        return [missing_result]
    assert text is not None
    results: list[CheckResult] = []
    try:
        tree = ast.parse(text)
    except SyntaxError as error:
        results.append(
            CheckResult(
                f"template:script:{SCRIPT_TEMPLATE_PATH}:syntax",
                False,
                f"Python syntax invalid: {error.msg}",
                SCRIPT_TEMPLATE_PATH,
            )
        )
        tree = None
    if tree is None or not script_has_cli_entry_point(tree):
        results.append(
            CheckResult(
                f"template:script:{SCRIPT_TEMPLATE_PATH}:cli entry point",
                False,
                "missing CLI entry point",
                SCRIPT_TEMPLATE_PATH,
            )
        )
    lowercase_text = text.lower()
    if "deterministic exit-code contract" not in lowercase_text and "exit-code contract" not in lowercase_text:
        results.append(
            CheckResult(
                f"template:script:{SCRIPT_TEMPLATE_PATH}:exit-code contract",
                False,
                "missing deterministic exit-code contract",
                SCRIPT_TEMPLATE_PATH,
            )
        )
    return results


def validate_templates(root: Path) -> list[CheckResult]:
    results: list[CheckResult] = [
        *validate_root_templates(root),
        *validate_skill_template(root),
        *validate_hook_template(root),
        *validate_toml_template_fields(root, AGENT_PROFILE_TEMPLATE_PATH, AGENT_PROFILE_REQUIRED_FIELDS),
        *validate_toml_template_fields(root, PLUGIN_MANIFEST_TEMPLATE_PATH, PLUGIN_MANIFEST_REQUIRED_FIELDS),
        *validate_script_template(root),
        *validate_markdown_section_set(root, MCP_TOOL_SPEC_PATH, MCP_TOOL_REQUIRED_SECTIONS),
        *validate_toml_template_fields(root, CONFIG_TEMPLATE_PATH, CONFIG_REQUIRED_FIELDS),
    ]
    for readme_path in TEMPLATE_READMES:
        results.extend(validate_markdown_section_set(root, readme_path, TEMPLATE_README_SECTIONS))
    for template_path in EXTERNAL_DISCLOSURE_TEMPLATES:
        results.extend(
            validate_required_template_section_text(
                root,
                template_path,
                "## Side effects",
                "external disclosure",
                "external disclosure",
            )
        )
    results.extend(
        validate_required_template_preamble_text(
            root,
            "templates/capability-card.md",
            "promotion state",
            "Promotion state:",
        )
    )
    results.extend(
        validate_required_template_section_text(
            root,
            MCP_TOOL_SPEC_PATH,
            "## Read/write classification",
            "process execution",
            "process execution",
        )
    )
    if not any(result.name.startswith("template:") and not result.ok for result in results):
        results.append(CheckResult("template:templates", True, "present", "templates"))
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
        *CANONICAL_DOC_REQUIRED_SECTIONS,
        *TEMPLATE_REQUIRED_PATHS,
    ]
    return [
        *validate_required_paths(root, required_paths),
        *validate_source_handoff_provenance(root),
        *validate_source_projection(root),
        *validate_framework_routes(root),
        *validate_canonical_docs(root),
        *validate_harness_catalog(root),
        *validate_templates(root),
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
