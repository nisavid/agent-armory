#!/usr/bin/env python3.14
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import re
import sys
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

try:
    from tools import harness_capability_profiles
except ModuleNotFoundError:
    spec = importlib.util.spec_from_file_location(
        "harness_capability_profiles",
        Path(__file__).with_name("harness_capability_profiles.py"),
    )
    if spec is None or spec.loader is None:
        raise
    harness_capability_profiles = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = harness_capability_profiles
    spec.loader.exec_module(harness_capability_profiles)

try:
    from tools import agent_equipment_config
except ModuleNotFoundError:
    spec = importlib.util.spec_from_file_location(
        "agent_equipment_config",
        Path(__file__).with_name("agent_equipment_config.py"),
    )
    if spec is None or spec.loader is None:
        raise
    agent_equipment_config = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = agent_equipment_config
    spec.loader.exec_module(agent_equipment_config)

try:
    from tools import issue_tracker_core
except ModuleNotFoundError:
    spec = importlib.util.spec_from_file_location(
        "issue_tracker_core",
        Path(__file__).with_name("issue_tracker_core.py"),
    )
    if spec is None or spec.loader is None:
        raise
    issue_tracker_core = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = issue_tracker_core
    spec.loader.exec_module(issue_tracker_core)


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    detail: str
    path: str


VALIDATION_SCHEMA = "armory_integrity.validation_result.v1"
VALIDATION_NAME = "Armory Integrity Validation"
FORGE_VALIDATION_NAME = "Forge Integrity Validation"


VALIDATION_INVENTORY = [
    {
        "check": "required_paths",
        "boundary": "armory_integrity",
        "relationship": "Top-level repository integrity preflight for required live and durable evidence surfaces.",
    },
    {
        "check": "python_runtime",
        "boundary": "armory_integrity",
        "relationship": "Top-level repository integrity check for the declared deterministic runtime and live references.",
    },
    {
        "check": "forge_routes",
        "boundary": "forge_integrity",
        "relationship": "Forge-scoped live integrity check for Smith and reader routing.",
    },
    {
        "check": "canonical_docs",
        "boundary": "forge_integrity",
        "relationship": "Forge-scoped live integrity check for Forge Canon and Forge Core documentation shape.",
    },
    {
        "check": "threat_model",
        "boundary": "armory_integrity",
        "relationship": "Top-level repository integrity check for durable security-model presence and routing.",
    },
    {
        "check": "documentation_closeout",
        "boundary": "armory_integrity",
        "relationship": "Top-level repository integrity check for durable documentation closeout evidence.",
    },
    {
        "check": "security_closeout",
        "boundary": "armory_integrity",
        "relationship": "Top-level repository integrity check for durable security closeout evidence.",
    },
    {
        "check": "projection_drafts",
        "boundary": "armory_integrity",
        "relationship": "Top-level repository integrity check for issue, PR, release, and handoff projection evidence.",
    },
    {
        "check": "harness_catalog",
        "boundary": "forge_integrity",
        "relationship": "Forge-scoped live integrity; detailed Vanilla Harness Capability Profile behavior belongs to the Manager Core validator.",
    },
    {
        "check": "templates",
        "boundary": "equipment_candidate_shape",
        "relationship": "Equipment-candidate shape validation for Forge templates, not equipment-specific behavior validation.",
    },
    {
        "check": "published_equipment_delivery",
        "boundary": "armory_integrity",
        "relationship": "Top-level stock inventory and Equipment Shop Card standard validation for published equipment delivery claims.",
    },
    {
        "check": "published_equipment_inventory_view",
        "boundary": "armory_integrity",
        "relationship": "Top-level validation that the human-facing Markdown inventory remains a checked projection of the canonical stock inventory.",
    },
    {
        "check": "examples",
        "boundary": "equipment_candidate_shape",
        "relationship": "Equipment-candidate shape validation for Forge examples, not equipment-specific behavior validation.",
    },
    {
        "check": "specs",
        "boundary": "equipment_candidate_shape",
        "relationship": "Equipment-candidate shape validation for Equipment Blueprints and bundles, not equipment-specific behavior validation.",
    },
    {
        "check": "issue_ops_workflow_executor",
        "boundary": "equipment_candidate_shape",
        "relationship": "Equipment-candidate shape validation for the Issue Ops advisory workflow skill and Agent Profile.",
    },
    {
        "check": "issue_ops_policy_config",
        "boundary": "armory_integrity",
        "relationship": "Top-level repository integrity check for the committed Issue Ops policy authority and compatibility docs.",
    },
    {
        "check": "markdown_links",
        "boundary": "armory_integrity",
        "relationship": "Top-level repository integrity check for internal documentation link targets.",
    },
    {
        "check": "source_disposition",
        "boundary": "armory_integrity",
        "relationship": "Top-level repository integrity check for the durable source-disposition ledger retained after source retirement.",
    },
    {
        "check": "harbor_jig_source_map",
        "boundary": "armory_integrity",
        "relationship": "Top-level repository integrity check for the durable Harbor-to-Armory jig source-map ledger.",
    },
    {
        "check": "harbor_neighbor_tool_catalog",
        "boundary": "armory_integrity",
        "relationship": "Top-level repository integrity check for the durable Harbor-neighbor tool catalog ledger.",
    },
    {
        "check": "external_tool_evaluation",
        "boundary": "armory_integrity",
        "relationship": "Top-level repository integrity check for the reusable external-tool evaluation operating contract.",
    },
    {
        "check": "harbor_external_tool_evaluation_record",
        "boundary": "armory_integrity",
        "relationship": "Top-level repository integrity check for the Harbor External Tool Evaluation Record skeleton.",
    },
    {
        "check": "skill_eval_methodology_source_intake",
        "boundary": "armory_integrity",
        "relationship": "Top-level repository integrity check for the durable skill-eval methodology source-intake ledger.",
    },
    {
        "check": "plugin_creator_source_intake",
        "boundary": "armory_integrity",
        "relationship": "Top-level repository integrity check for the durable plugin-creator source-intake ledger.",
    },
    {
        "check": "source_retired_tree",
        "boundary": "historical_seed_migration",
        "relationship": "Historical Seed migration guard that prevents retired raw source trees from returning to the live repository.",
    },
    {
        "check": "final_source_retired_stamp",
        "boundary": "historical_seed_migration",
        "relationship": "Historical Seed migration guard for the durable final source-retirement stamp.",
    },
]


def validation_inventory() -> list[dict[str, str]]:
    return [dict(item) for item in VALIDATION_INVENTORY]


FENCE_START_RE = re.compile(r"(`{3,}|~{3,})")
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
BACKTICK_PATH_RE = re.compile(r"`([^`]+)`")
REFERENCE_DEFINITION_RE = re.compile(r"(?m)^[ \t]{0,3}\[([^\]\n]+)\]:[ \t]*(.+?)\s*$")
PYTHON_RUNTIME_REFERENCE_RE = re.compile(r"\b(?:python|Python)\s*(\d+\.\d+)\b")
HOST_LOCAL_PATH_RE = re.compile(
    r"(?<![\w.-])(?:"
    r"~[/\\]"
    r"|/(?:home|Users|tmp|var/tmp)/"
    r"|[A-Za-z]:[\\/](?:Users|Windows|Temp|Documents)(?:[\\/]|$)"
    r")"
)


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


def markdown_frontmatter(markdown: str) -> dict[str, str]:
    lines = markdown.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    fields: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fields
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"').strip("'")
    # No closing "---" found: treat the block as malformed frontmatter.
    return {}


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
SOURCE_PROJECTION_VALIDATION_STATUSES = {"planned", "validated"}
SOURCE_PROJECTION_PLANNED_REQUIREMENTS = {"H012", "H053"}
SOURCE_DISPOSITION_PATH = "docs/closeout/forge-seed-source-disposition.md"
HARBOR_JIG_SOURCE_MAP_PATH = "docs/closeout/harbor-jig-source-map.md"
HARBOR_NEIGHBOR_TOOL_CATALOG_PATH = "docs/closeout/harbor-neighbor-tool-catalog.md"
EXTERNAL_TOOL_EVALUATION_PATH = "docs/external-tool-evaluation.md"
HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH = "docs/evaluations/harbor.md"
SKILL_EVAL_METHODOLOGY_SOURCE_INTAKE_PATH = "docs/closeout/skill-eval-methodology-source-intake.md"
PLUGIN_CREATOR_SOURCE_INTAKE_PATH = "docs/closeout/plugin-creator-source-intake.md"
HARBOR_JIG_SOURCE_MAP_REQUIRED_SECTIONS = [
    "Scope Boundary",
    "Portable Source Inventory",
    "Harbor-To-Armory Concept Map",
    "Risks And Open Issues",
    "Downstream Routing",
    "Deferments And Nonportable Claims",
    "Security Privacy And Durability",
    "Closeout Evidence",
]
HARBOR_JIG_SOURCE_MAP_COVERAGE_TERMS = [
    "task",
    "dataset",
    "agent",
    "trial",
    "job",
    "environment",
    "verifier",
    "Reward Kit",
    "ATIF trajectory",
    "artifacts",
    "scoring",
    "cloud sandbox",
    "network policy",
    "artifact handling",
    "verifier/reward tampering",
    "auth/provider boundaries",
    "Agent Test Jig",
    "Jig Test Plan",
    "Jig Driver",
    "Jig Runner",
    "Assertion Provider",
    "Learned Oracle",
    "Harness Test Suite",
    "Capability Profiling Protocol",
    "Study Report",
    "Jig Adequacy Report",
]
HARBOR_JIG_SOURCE_MAP_DOWNSTREAM_ROUTES = [
    "#183",
    "#185",
    "#186",
    "#187",
    "#188",
    "#189",
    "#190",
    "#191",
]
HARBOR_NEIGHBOR_TOOL_CATALOG_REQUIRED_SECTIONS = [
    "Scope Boundary",
    "Portable Source Inventory",
    "Harbor-Neighbor Tool Catalog",
    "Role Classification Summary",
    "Open Uncertainties And Follow-Up Conditions",
    "Downstream Routing",
    "Deferments And Nonportable Claims",
    "Security Privacy And Durability",
    "Closeout Evidence",
]
HARBOR_NEIGHBOR_TOOL_CATALOG_FIELDS = [
    "entry_id",
    "tool_or_surface",
    "Harbor linkage",
    "source URL",
    "role classification",
    "evidence quality",
    "likely Armory consumer",
    "open uncertainty",
]
HARBOR_NEIGHBOR_TOOL_CATALOG_COVERAGE_TERMS = [
    "Daytona",
    "Modal",
    "E2B",
    "Runloop",
    "Tensorlake",
    "Islo",
    "CoreWeave Sandboxes",
    "W&B Sandboxes",
    "Reward Kit",
    "LiteLLM",
    "ATIF",
    "Opik",
    "Harbor registry",
    "dataset.toml",
    "adapter templates",
    "result viewer",
    "Hugging Face parity experiments",
    "SkyRL",
    "GEPA",
    "Jig Driver substrate",
    "sandbox provider",
    "benchmark format",
    "benchmark registry",
    "Agent or harness configurator",
    "tool provider",
    "observability/evaluation instrumentation",
    "verifier/assertion layer",
    "trajectory/result format",
    "training/export surface",
    "harbor-doc-supported",
    "harbor-source-supported",
    "vendor-doc-supported",
    "third-party-fallback",
]
HARBOR_NEIGHBOR_TOOL_CATALOG_ROUTES = [
    "#183",
    "#186",
    "#187",
    "#188",
    "#189",
    "#190",
    "#191",
]
EXTERNAL_TOOL_EVALUATION_REQUIRED_SECTIONS = [
    "Purpose",
    "Pipeline Stages",
    "Evidence Classification",
    "Projection Rules",
    "Security Disclosure And Durability",
    "Harbor-First Application",
    "Closeout",
]
EXTERNAL_TOOL_EVALUATION_COVERAGE_TERMS = [
    "intake scope",
    "source review",
    "live repository and issue review",
    "evidence classification",
    "Armory role mapping",
    "bounded prototype decision",
    "security and disclosure review",
    "documentation closeout",
    "issue projection",
    "final disposition",
    "source-backed claims",
    "local observations",
    "prototype results",
    "implementation inference",
    "unknowns",
    "rejected claims",
    "update existing issues",
    "create new issues",
    "propose a PRD",
    "propose an ADR",
    "credentials",
    "local paths",
    "raw logs",
    "trajectories",
    "transcripts",
    "model outputs",
    "external service usage",
    "Change Set Security Closeout",
    "Change Set Documentation Closeout",
]
EXTERNAL_TOOL_EVALUATION_ROUTES = ["#184", "#185"]
HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_REQUIRED_SECTIONS = [
    "Scope",
    "Source Inputs",
    "Evidence Ledger",
    "Child Issue Outputs",
    "Security Disclosure And Durability",
    "Projection State",
    "Final Disposition",
]
HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_COVERAGE_TERMS = [
    "source-backed claims",
    "local observations",
    "prototype results",
    "implementation inference",
    "unknowns",
    "rejected claims",
    "update existing issues",
    "create new issues",
    "propose a PRD",
    "propose an ADR",
    "credentials",
    "local paths",
    "raw logs",
    "trajectories",
    "transcripts",
    "model outputs",
    "external service usage",
]
HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_ROUTES = [
    "#183",
    "#184",
    "#185",
    "#186",
    "#187",
    "#188",
    "#189",
    "#190",
    "#191",
]
HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_STATES = {"in progress", "complete"}
EXTERNAL_TOOL_EVALUATION_DISPOSITIONS = {
    "adopted candidate",
    "supporting component",
    "research reference",
    "deferred",
    "rejected",
    "unknown pending evidence",
}
FINALIZED_EXTERNAL_TOOL_EVALUATION_DISPOSITIONS = EXTERNAL_TOOL_EVALUATION_DISPOSITIONS - {"unknown pending evidence"}
PLUGIN_CREATOR_SOURCE_INTAKE_REQUIRED_SECTIONS = [
    "Scope Boundary",
    "Portable Source Inventory",
    "Reusable Techniques",
    "UX And Marketplace Metadata",
    "Downstream Routing",
    "Deferments And Nonportable Claims",
    "Security, Privacy, And Durability",
    "Closeout Evidence",
]
PLUGIN_CREATOR_SOURCE_INTAKE_COVERAGE_TERMS = [
    "manifest scaffolding",
    "name normalization",
    "marketplace projection",
    "cachebuster reinstall flow",
    "schema validation",
    "component surface selection",
    "placeholder debt",
    "policy/auth semantics",
    "asset metadata",
]
PLUGIN_CREATOR_SOURCE_INTAKE_DOWNSTREAM_ROUTES = ["#5", "#154", "#157"]
SKILL_EVAL_METHODOLOGY_SOURCE_INTAKE_REQUIRED_SECTIONS = [
    "Scope Boundary",
    "Portable Source Inventory",
    "Reusable Techniques",
    "Downstream Routing",
    "Deferments And Nonportable Claims",
    "Security, Privacy, And Durability",
    "Closeout Evidence",
]
SKILL_EVAL_METHODOLOGY_SOURCE_INTAKE_COVERAGE_TERMS = [
    "behavioral evals",
    "trigger-selection evals",
    "harness adaptation",
    "description optimization",
    "benchmarking",
    "human review",
    "grading",
    "packaging",
    "viewer/review workflow",
]
SKILL_EVAL_METHODOLOGY_SOURCE_INTAKE_DOWNSTREAM_ROUTES = [
    "#61",
    "#62",
    "#67",
    "#5",
    "#155",
    "#157",
    "later Forge work",
]
SOURCE_DISPOSITION_MANIFEST_FIELDS = [
    "source_id",
    "source_kind",
    "original_path",
    "git_blob_id",
    "sha256",
    "normalized_payload_digest",
    "durable_payload",
]
SOURCE_DISPOSITION_ITEM_FIELDS = [
    "item_id",
    "source_id",
    "coverage_status",
    "challenge_status",
    "challenge_operator_confirmation_required",
    "arbitration_required",
    "disposition",
    "operator_decision",
    "evidence_target",
    "normalized_claim_summary",
]
SOURCE_DISPOSITION_COVERAGE_STATUSES = {
    "adequately_captured",
    "partially_captured",
    "missing",
    "obsolete",
    "intentionally_deferred",
}
SOURCE_DISPOSITION_CHALLENGE_STATUSES = {"unchallenged", "resolved"}
SOURCE_DISPOSITION_MATRIX = {
    "adequately_captured": {"kept_current", "integrated"},
    "partially_captured": {"integrated", "deferred"},
    "missing": {"integrated", "deferred", "rejected"},
    "obsolete": {"obsolete"},
    "intentionally_deferred": {"deferred"},
}
SOURCE_BEARING_STAMP_FIELDS = [
    "source_bearing_snapshot_tree_id",
    "source_bearing_stamp_id",
    "source_manifest_digest",
    "source_disposition_digest",
    "source_bearing_result",
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
SOURCE_DISPOSITION_FINAL_REQUIRED_ITEM_IDS = set(ACCEPTED_SOURCE_REQUIREMENTS) | {"F001", "F002", "F003", "F004"}
HEX40_RE = re.compile(r"^[0-9a-f]{40}$")
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")

SOURCE_HANDOFF_DIR = "docs/metasmith/handoff/2026-05-02"
SOURCE_HANDOFF_MANIFEST = f"{SOURCE_HANDOFF_DIR}/manifest.json"
SOURCE_HANDOFF_PROVENANCE_NOTICE = f"{SOURCE_HANDOFF_DIR}/AGENTS.md"
PYTHON_VERSION_DECLARATION_PATH = ".python-version"
REQUIRED_PRELOADED_ROUTES = [
    "docs/vision.md",
    "docs/agent-equipment-forge.md",
    "docs/smith-runbook.md",
    "docs/story-closeout.md",
    "docs/interface-decision-guide.md",
    "docs/harness-capabilities.md",
    "templates/",
    "examples/",
    "specs/",
]
CONTEXT_REQUIRED_SECTIONS = ["Language", "Relationships", "Precision rules", "Flagged ambiguities"]
CANONICAL_DOC_REQUIRED_SECTIONS = {
    "docs/vision.md": [
        "Experience",
        "Equipment",
        "Deterministic boundaries",
        "Harness lifecycle",
        "Self-onboarding",
        "Metacognitive loop",
        "Reflection",
        "Lifecycle use",
    ],
    "docs/agent-equipment-forge.md": [
        "Purpose",
        "Vision alignment",
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
        "Tooling Request",
        "Closeout",
    ],
    "docs/forgewright-runbook.md": [
        "Source handoff preservation",
        "decision projection",
        "Review Until Clean",
        "Harness Fact Refresh",
        "Change set closeout",
        "Issue Projection",
        "Equipment Blueprints",
        "Tooling Gap intake",
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
        "artifact durability",
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
    "docs/equipment-delivery.md": [
        "Purpose",
        "Authority",
        "Equipment Shop Cards",
        "Stock Inventory Records",
        "Component Manifests",
        "Delivery Compliance",
        "Validation",
    ],
    "docs/story-closeout.md": [
        "Purpose",
        "Gate order",
        "Interdependency rules",
        "Review gates",
        "Recursion and bookkeeping",
        "Completion criteria",
    ],
}
CANONICAL_DOC_REQUIRED_TEXT = {
    "docs/vision.md": [
        "autonomous self-onboarding to purpose-built assemblies of harness components",
        "Use this vision as an input throughout the engineering lifecycle.",
    ],
    "docs/smith-runbook.md": [
        "When a Smith finds an unsatisfied Tooling Gap that blocks or materially weakens the current equipment task, treat the Tooling Work as a dependency and escalate to a Forgewright before continuing.",
        "Choose the least disruptive Forgewright path supported by the harness and operator policy: current session, subagent session, peer agent session, forked session, or new session.",
        "The handoff must include the blocked task, unsatisfied Tooling Gap, dependency impact, evidence checked, requested Forgewright deliverable, selected session path, and hand-back expectation.",
        "docs, config, scripts, hooks, skills, MCP/tools, Agent Profiles, plugins, and templates are discoverable from the Forge Conveyor",
        "Run a Cross-Boundary Coherence Ralph Review before story closeout.",
        "Run a Story Quality Ralph Review before story closeout.",
    ],
    "docs/forgewright-runbook.md": [
        "A Forgewright intake from a Smith starts by preserving the Smith handoff, refining the Tooling Gap, updating canonical surfaces and validation, and returning a hand-back note.",
        "The hand-back note names files changed, validation and review results, dependency updates, remaining risks, and the context the Smith needs to resume.",
    ],
    "docs/story-closeout.md": [
        "Story Closeout is the story-level gate; Change Set Security Closeout and Change Set Documentation Closeout are subordinate gates.",
        "Refresh the Intent Model before downstream closeout gates.",
        "Before committing or externally projecting closeout evidence, classify evidence artifacts by durability.",
        "Durable project evidence and portable review summaries may be committed or projected.",
        "Instance-scoped scratch artifacts, including raw tool reports, local scan bundles, copied diffs, host-local paths, screenshots, or work directories, should be summarized by scope, disposition, and durable conclusions instead of treated as project truth.",
        "Classify privacy and disclosure limits for actionable Reflection Findings",
        "Run Cross-Boundary Coherence before Story Quality because quality review depends on coherent process evidence.",
        "Intent Model Refresh is the first closeout gate.",
        "Update the agent's model of Underlying Intent by reviewing recent operator input, accepted ADR/PRD/spec/plan changes, review dispositions, handoff notes, and observed corrections relevant to the story before running downstream closeout gates.",
        "Story Quality also runs an Intent Alignment Check.",
        "Compare Effective Intent, meaning the Intent actually imposed by ADRs, PRDs, specs, plans, acceptance criteria, review dispositions, and other declarations, with the refreshed model of Underlying Intent after Cross-Boundary Coherence has made Effective Intent legible.",
        "Refresh the model again if closeout evidence introduced new intent signals.",
        "An agent does not directly know a stakeholder's or other intent-capable actor's Underlying Intent; it maintains an evidence-backed model that can be tested through questions, experiments, and observed corrections.",
        "Hypotheses about emotion, belief state, attention, engagement, discipline, or other internal disposition can explain why a mismatch might exist, but they are not evidence by themselves and must not justify unilateral realignment.",
        "When observable evidence shows misalignment beyond reasonable doubt, realign the affected declarations and reproject downstream implications.",
        "When the model remains uncertain, the case depends on internal-state inference, or the evidence otherwise creates a non-dismissible likelihood of misalignment without certainty, raise a concise question to the operator, using an interactive question tool when available.",
        "If a revision changes security, documentation, validation, PRD/spec/plan scope, or issue/PR projection, rerun the affected upstream gate before the next closeout review.",
        "Evidence-artifact durability changes rerun the closeout gate that owns the artifact and any projection surface that carries its claims.",
        "after privacy and disclosure limits are classified",
        "Recording the latest clean review result is bookkeeping and does not reopen the full review loop unless it changes substantive claims.",
        "Published issue, PR, release, or handoff corrections rerun a projection consistency check and a narrow Cross-Boundary Coherence review for the corrected surface.",
        "closeout evidence artifacts are classified by durability",
        "instance-scoped scratch artifacts are summarized rather than committed or externally projected as project truth",
    ],
}
STORY_CLOSEOUT_PATH = "docs/story-closeout.md"
STORY_CLOSEOUT_GATE_ORDER_TOKENS = [
    "refresh the intent model",
    "confirm the implementation",
    "complete change set security closeout",
    "complete change set documentation closeout",
    "prepare projection drafts",
    "classify privacy and disclosure limits",
    "run cross-boundary coherence",
    "run story quality ralph review",
    "run final validation",
    "push or otherwise publish the branch",
    "publish or update issue",
    "perform publication actions",
]
THREAT_MODEL_PATH = "docs/security/threat-model.md"
THREAT_MODEL_REFERENCE_PATHS = ["docs/security-and-control.md"]
THREAT_MODEL_REQUIRED_SECTIONS = [
    "Assets",
    "Trust boundaries",
    "Attacker-controlled inputs",
    "Invariants",
    "Assumptions",
    "High-impact failure modes",
]
DOCUMENTATION_CLOSEOUT_PATH = "docs/closeout/forge-seed-documentation.md"
DOCUMENTATION_CLOSEOUT_REQUIRED_SECTIONS = [
    "Scope of inspected docs",
    "Docs changed",
    "Docs unchanged with rationale",
    "Stale-language cleanup result",
    "Established precedents added or updated",
    "Review status",
    "Residual documentation risk",
]
DOCUMENTATION_CLOSEOUT_REQUIRED_EVIDENCE = [
    "README.md",
    "AGENTS.md",
    "CONTEXT.md",
    EXTERNAL_TOOL_EVALUATION_PATH,
    HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH,
    "docs/agents/*.md",
    "Forge Canon",
    "docs/prd/forge-seed.md",
    "docs/adr/*.md",
    "docs/plans/2026-05-03-forge-seed.md",
    "docs/security/*.md",
    "docs/closeout/*.md",
    "docs/closeout/forge-seed-source-disposition.md",
    "specs/*.md",
    "templates/**/*.md",
    "examples/**/*.md",
    "branch-push pause does not close the capture",
    "Full Seed completion requires a merged Seed",
    "An explicit hold or cancellation continues",
    "unmerged-state hand-back",
    "record the unmerged state directly",
    "Cross-Boundary Coherence",
    "Story Quality",
    "Ralph Review Cycle",
]
DOCUMENTATION_CLOSEOUT_FORBIDDEN_INCOMPLETE_TEXT = [
    "still requires",
    "record that review result here after it completes",
]
SECURITY_CLOSEOUT_PATH = "docs/security/forge-seed-closeout.md"
SECURITY_CLOSEOUT_REQUIRED_SECTIONS = [
    "Scan scope",
    "Commands",
    "Scan artifact disposition",
    "Report disposition",
    "Findings disposition",
    "Hardening changes",
    "Re-validation status",
    "Deferred-risk tracking",
]
SECURITY_CLOSEOUT_REQUIRED_EVIDENCE = [
    "ephemeral scratch evidence",
    "not a tracked project artifact",
    "not portable review evidence",
    "not a standing source of project truth",
    "Artifact durability classification: instance-scoped scratch evidence.",
    "Durable security evidence is this closeout summary",
    "The raw report is not committed and should not be cited as reusable project doctrine.",
    "Codex Security phase sequence",
    "python3.14 -m unittest tests.test_validate_armory_integrity",
    "python3.14 tools/validate_armory_integrity.py",
    "No reportable findings",
    "Suppressed findings",
    "Re-validation passed",
    "Deferred risks",
]
SECURITY_CLOSEOUT_SKIPPED_PHASE_DISPOSITION = (
    "Validation and attack-path analysis were not separately run because finding discovery produced no technically plausible candidates"
)
SECURITY_CLOSEOUT_COMPLETED_PHASE_EVIDENCE = [
    "Validation phase completed",
    "Attack-path analysis completed",
]
PLAN_PATH = "docs/plans/2026-05-03-forge-seed.md"
STORY_REVIEW_STEP_LABEL = "Step 7: Ralph-review closeout coherence and quality"
PROJECTION_DRAFTS_PATH = "docs/closeout/forge-seed-projection-drafts.md"
PROJECTION_DRAFTS_REQUIRED_SECTIONS = [
    "Published PRD Issue Draft",
    "Published Pull Request",
    "Release Draft",
    "Handoff Draft",
]
PROJECTION_DRAFTS_REQUIRED_EVIDENCE = [
    "Projected commit SHA",
    "TO_CAPTURE_IMMEDIATELY_BEFORE_ISSUE_PUBLICATION",
    "Report disposition: recorded in `docs/security/forge-seed-closeout.md`",
    "Published PR: <https://github.com/nisavid/agent-armory/pull/1>",
    "Seed Closeout Addendum remains open through PR review orchestration, merge, merge cleanup, external surface reconciliation, and final hand-back",
    "No release publication is planned",
    "No separate handoff publication is required",
]
PROJECTION_DRAFTS_FORBIDDEN_UNRESOLVED_TEXT = [
    "TO_FILL_AFTER_FINAL_CLEAN_DOCUMENTATION_CLOSEOUT_REVIEW",
]
PROJECTION_DRAFTS_PENDING_STORY_REVIEW_PLACEHOLDER = "TO_FILL_AFTER_CLEAN_REVIEW"
PROJECTION_DRAFTS_SCRATCH_ARTIFACT_MARKERS = [
    "/tmp/",
    "/var/tmp/",
    "/home/",
    "file:///tmp/",
    "file:///var/tmp/",
    "codex-security-scans/",
]
FINAL_CLOSEOUT_EXACT_VALIDATION_COUNT_RE = re.compile(
    r"\b\d+\s+(?:tests?\s+)?passed\b|\b\d+\s+passing result objects\b",
    re.IGNORECASE,
)
STORY_REVIEW_LINE_RE = re.compile(
    r"(?im)^(?:-\s*)?(cross-boundary coherence|story quality)(?: review)?:\s*`?(Ralph Review Cycle \d+)`?\.?\s*$"
)
REQUIRED_HARNESSES = [
    "codex",
    "claude_code",
    "cursor",
    "hermes_agent",
    "opencode",
    "openclaw",
]
TEMPLATE_REQUIRED_PATHS = [
    "templates/capability-card.md",
    "templates/equipment-shop-card.md",
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
    "templates/equipment-stock-record.toml",
]
EXAMPLE_DIRECTORIES = [
    "examples/pr-review",
    "examples/docs-research",
    "examples/observability-investigation",
]
EXAMPLE_FILES = [
    "capability-card.md",
    "interface-decision-record.md",
    "projected-components.md",
]
EXAMPLE_REQUIRED_PATHS = [
    f"{example_directory}/{example_file}"
    for example_directory in EXAMPLE_DIRECTORIES
    for example_file in EXAMPLE_FILES
]
CONFIG_BUNDLE_PATH = "specs/agent-equipment-config"
CONFIG_PRD_PATH = "docs/prd/agent-equipment-config.md"
ISSUE_TRACKER_OPS_PRD_PATH = "docs/prd/issue-tracker-ops.md"
ISSUE_TRACKER_OPS_CONFIG_PROFILE_PATH = "specs/issue-tracker-ops/config-profile-and-onboarding.md"
ISSUE_TRACKER_OPS_POLICY_CONFIG_PATH = "config/agent-equipment.toml"
ISSUE_TRACKER_OPS_COMPATIBILITY_DOCS = [
    "docs/agents/issue-tracker.md",
    "docs/agents/triage-labels.md",
]
ISSUE_OPS_WORKFLOW_EXECUTOR_SKILL_PATH = "skills/issue-ops-workflow-executor/SKILL.md"
ISSUE_OPS_WORKFLOW_EXECUTOR_PROFILE_PATH = "agents/issue-ops-workflow-executor/profile.toml"
ISSUE_OPS_WORKFLOW_EXECUTOR_REQUIRED_SKILL_TEXT = [
    "describe-workflows",
    "plan-workflow --adapter github-issues-baseline --workflow <workflow-id>",
    "required context",
    "output sections",
    "candidate writes",
    "deterministic Issue Ops operation plans",
    "dry-run command shapes",
    "direct `gh` writes",
    "direct GitHub MCP writes",
    "Issue Ops dry-run/write gates",
]
ISSUE_OPS_WORKFLOW_EXECUTOR_ALLOWED_TOOLS = [
    "describe-workflows",
    "plan-workflow",
    "read/context gathering",
]
ISSUE_OPS_WORKFLOW_EXECUTOR_REQUIRED_DENIES = [
    "direct tracker mutation",
    "direct gh writes",
    "direct GitHub MCP writes",
    "user-global policy mutation",
    "external disclosure without approval",
]
ISSUE_OPS_WORKFLOW_EXECUTOR_REQUIRED_APPROVALS = [
    "external disclosure",
    "network write",
    "tracker mutation",
    "user-global policy mutation",
]
PUBLISHED_EQUIPMENT_DELIVERY_DOC_PATH = "docs/equipment-delivery.md"
PUBLISHED_EQUIPMENT_INVENTORY_PATH = "inventory/equipment.toml"
PUBLISHED_EQUIPMENT_INVENTORY_VIEW_PATH = "docs/equipment/inventory.md"
PUBLISHED_EQUIPMENT_SHOP_CARD_INDEX_PATH = "docs/equipment/shop-cards/README.md"
PUBLISHED_EQUIPMENT_INVENTORY_SCHEMA_VERSION = "agent-armory.equipment-stock.v1"
PUBLISHED_EQUIPMENT_SHOP_CARD_DIR = "docs/equipment/shop-cards"
PUBLISHED_EQUIPMENT_EMPTY_STOCK_SENTENCE = (
    "No stocked equipment is recorded in `inventory/equipment.toml` yet."
)
PUBLISHED_EQUIPMENT_PROMOTION_STATES = {
    "example",
    "specified",
    "planned",
    "implemented",
    "validated",
    "published",
}
PUBLISHED_EQUIPMENT_DELIVERY_COMPLIANCE_STATUSES = {
    "not_evaluated",
    "pending",
    "passed",
    "blocked",
}
PUBLISHED_EQUIPMENT_COMPONENT_STATUSES = {
    "required",
    "optional",
    "planned",
    "unavailable",
}
PUBLISHED_EQUIPMENT_REQUIRED_FIELDS = (
    "id",
    "name",
    "summary",
    "promotion_state",
    "delivery_compliance",
    "shop_card",
)
PUBLISHED_EQUIPMENT_COMPONENT_REQUIRED_FIELDS = ("name", "kind", "status", "paths")
EXISTING_EQUIPMENT_ONBOARDING_PRD_PATH = "docs/prd/existing-equipment-onboarding.md"
ISSUE_TRACKER_OPS_CONFIG_PROFILE_REQUIRED_SECTIONS = [
    "Purpose",
    "Progressive Enhancement Boundary",
    "Plain Handoff And Session Behavior",
    "Onboarding Flow",
    "Foreign Policy Surface Discovery And Migration Fates",
    "Compatibility Classification",
    "Machine-Visible Output",
    "CLI And MCP Parity",
    "Security And Safety",
    "Validation And Closeout",
    "Non-goals",
]
ISSUE_TRACKER_OPS_CONFIG_PROFILE_REQUIRED_TEXT = [
    "session-scoped",
    "plain handoff",
    "Agent Equipment Config",
    "Foreign Policy Surface",
    "migration fates",
    "keep and establish compatibility",
    "remove and ingest policy",
    "remove and discard policy",
    "`ignore` leaves a surface outside the migration scope",
    "`defer for review` records a blocking or judgment-heavy disposition",
    "`split` separates facets that need different fates",
    "compatibility classification",
    "Config Safety Status, safety status, assumptions, incomplete sections, confidence",
    "conflict reporting",
    "effective next-work",
    "CLI and MCP parity",
    "user-global",
    "explicit approval",
    "fail closed",
    "external disclosure",
]
CONFIG_BUNDLE_REQUIRED_PATHS = [
    f"{CONFIG_BUNDLE_PATH}/README.md",
    f"{CONFIG_BUNDLE_PATH}/capability-card.md",
    f"{CONFIG_BUNDLE_PATH}/interface-decision-record.md",
    f"{CONFIG_BUNDLE_PATH}/security-control-classification.md",
    f"{CONFIG_BUNDLE_PATH}/mcp-tools.md",
    f"{CONFIG_BUNDLE_PATH}/edit-boundaries.md",
    f"{CONFIG_BUNDLE_PATH}/authoring-plan-apply-model.md",
    f"{CONFIG_BUNDLE_PATH}/pressure-scenarios.md",
    f"{CONFIG_BUNDLE_PATH}/validation-plan.md",
    f"{CONFIG_BUNDLE_PATH}/closeout-evidence-plan.md",
]
CONFIG_BUNDLE_REQUIRED_TEXT = [
    "typed schemas",
    "schema fragments",
    "layered config",
    "effective-config",
    "config-diff",
    "Layer Precedence",
    "Policy Authority",
    "later overrides",
    "Config Safety Status",
    "semantic validators",
    "conflict diagnostics",
    "migrations",
    "session-scoped",
    "plain equipment-specific config handoff",
    "secret references",
    "consumer action decision",
    "MCP parity",
    "progressive fallback",
    "Issue Tracker Ops",
    "config propose",
    "config apply",
    "patch-layer",
    "create-layer",
    "reviewed plan artifacts",
    "precondition fingerprint",
    "virtual post-change effective Config",
    "all-or-nothing",
    "durability classification",
    "rollback stance",
    "python3.14 -m unittest tests.test_agent_equipment_config",
    "policy",
    "Codex",
    "OpenClaw",
    "Hermes Agent",
    "Claude Code",
    "Cursor",
    "OpenCode",
]
CONFIG_BUNDLE_FORBIDDEN_TEXT = [
    "lower-precedence layers",
    "lower precedence layers",
]
SPEC_REQUIRED_PATHS = [
    "specs/repo-ops.md",
    "specs/periodic-actions.md",
    "specs/harness-capability-refresh.md",
]
SPEC_REQUIRED_SECTIONS = [
    "Purpose",
    "User stories",
    "Acceptance criteria",
    "Non-goals",
]
SPEC_HARNESS_SECTION_ALTERNATIVES = [
    "Harness projections",
    "Harness-specific starting points",
]
SPEC_REQUIRED_TEXT = {
    "specs/repo-ops.md": [
        "TOML",
        "hook behavior",
        "sensibly typed values",
        "autonomy levels",
        "owner",
        "runbook",
        "safe defaults",
        "policy enforcement",
        "Fork Ops",
        "Codex",
        "OpenClaw",
        "Hermes Agent",
        "Claude Code",
        "Cursor",
        "OpenCode",
    ],
    "specs/periodic-actions.md": [
        "first-session install prompt",
        "list",
        "view",
        "install",
        "uninstall",
        "trigger-now",
        "edit-period",
        "mechanism selection order",
        ".repo-ops/",
        "Codex",
        "OpenClaw",
        "Hermes",
        "Claude Code",
        "Cursor",
        "OpenCode",
    ],
    "specs/harness-capability-refresh.md": [
        "Codex",
        "OpenClaw",
        "Hermes Agent",
        "Claude Code",
        "Cursor",
        "OpenCode",
        "current version",
        "checked-at timestamp",
        "source URLs",
        "supported Harness Component types",
        "key affordances",
        "known limitations",
        "scheduling mechanisms",
        "hook/event names",
        "skill discovery paths",
        "plugin interfaces",
        "MCP behavior",
        "high-priority issue",
        "previous version",
        "capability affected",
        "source evidence",
        "expected Forge impact",
        "suggested Smith task",
        "issues/pending/high/",
        "weekly starting cadence",
        "prioritization order",
    ],
}
EXAMPLE_TRACE_LINKS = {
    "capability-card.md": ["interface-decision-record.md"],
    "interface-decision-record.md": ["capability-card.md", "projected-components.md"],
    "projected-components.md": ["capability-card.md", "interface-decision-record.md"],
}
EXAMPLE_REQUIRED_SECTIONS = {
    "capability-card.md": ["Vision alignment"],
    "interface-decision-record.md": ["Vision alignment"],
}
FORBIDDEN_EXAMPLE_CLAIMS = [
    "production-ready",
    "ready for production",
    "validated Agent Equipment",
    "Promotion state: published",
    "Status: Published",
    "is installable",
    "are installable",
    "installable Agent Equipment",
    "can be installed",
    "ready to install",
    "is loadable",
    "are loadable",
    "loadable Agent Equipment",
    "can be loaded",
]
FORBIDDEN_SPEC_CLAIMS = FORBIDDEN_EXAMPLE_CLAIMS
ROOT_TEMPLATE_FILES = [
    "templates/capability-card.md",
    "templates/equipment-shop-card.md",
    "templates/interface-decision-record.md",
    "templates/security-review.md",
    "templates/context-budget-review.md",
]
ROOT_TEMPLATE_REQUIRED_SECTIONS = {
    "templates/capability-card.md": [
        "Purpose",
        "Vision alignment",
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
    "templates/equipment-shop-card.md": [
        "Fit",
        "What is stocked",
        "Gear-up paths",
        "Component manifest",
        "Delivery status",
        "Inspection and evidence",
        "Support and lifecycle",
    ],
    "templates/interface-decision-record.md": [
        "Requirement",
        "Vision alignment",
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
HOOK_SIDE_EFFECT_CLASSIFICATIONS = [
    "read-only",
    "external disclosure",
    "local write",
    "network write",
    "process execution",
    "privileged operation",
    "irreversible mutation",
]
HOOK_REQUIRED_CONTRACT_VALUES = {
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
EQUIPMENT_STOCK_RECORD_TEMPLATE_PATH = "templates/equipment-stock-record.toml"
CONFIG_REQUIRED_FIELDS = {
    "ownership": ("ownership",),
    "autonomy": ("autonomy",),
    "enabled": ("enabled",),
    "enabled_default": ("enabled", "default"),
    "review": ("review",),
    "approval": ("approval",),
}
EQUIPMENT_STOCK_RECORD_REQUIRED_FIELDS = {
    "schema_version": ("schema_version",),
    "equipment": ("equipment",),
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
PYTHON_RUNTIME_REFERENCE_EXCLUDED_DIRS = [
    Path("docs/adr"),
    Path("docs/metasmith"),
]
PYTHON_RUNTIME_REFERENCE_EXCLUDED_DIR_NAMES = {
    ".cache",
    ".git",
    ".mypy_cache",
    ".nox",
    ".pytest_cache",
    ".ruff_cache",
    ".scratch",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "scratch",
    "tmp",
    "venv",
}


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


def source_disposition_table_digest(rows: list[dict[str, str]], fields: list[str]) -> str:
    normalized_rows = [
        {field: row.get(field, "").strip() for field in fields}
        for row in rows
    ]
    data = json.dumps(normalized_rows, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def parse_bool_cell(value: str) -> bool | None:
    folded = value.strip().casefold()
    if folded == "true":
        return True
    if folded == "false":
        return False
    return None


def validate_source_disposition(root: Path, *, required_item_ids: set[str] | None = None) -> list[CheckResult]:
    ok, detail, path = repo_relative_path_status(root, SOURCE_DISPOSITION_PATH, "file")
    if not ok:
        if detail == "path contains symlink":
            detail = "source disposition path contains symlink"
        return [CheckResult("source_disposition:path", False, detail, SOURCE_DISPOSITION_PATH)]
    markdown = path.read_text(encoding="utf-8")
    headings = markdown_heading_texts(markdown)
    results: list[CheckResult] = []
    for required_section in ("Source Manifest", "Disposition Items", "Source-Bearing Stamp", "Final Source-Retired Stamp"):
        if normalize_reference_label(required_section) not in headings:
            results.append(
                CheckResult(
                    f"source_disposition:section:{required_section}",
                    False,
                    f"missing section: {required_section}",
                    SOURCE_DISPOSITION_PATH,
                )
            )

    manifest_rows = parse_markdown_table(markdown_section(markdown, "## Source Manifest") or "")
    item_rows = parse_markdown_table(markdown_section(markdown, "## Disposition Items") or "")
    if not manifest_rows:
        results.append(CheckResult("source_disposition:manifest", False, "no source rows", SOURCE_DISPOSITION_PATH))
    if not item_rows:
        results.append(CheckResult("source_disposition:items", False, "no item rows", SOURCE_DISPOSITION_PATH))

    source_ids: set[str] = set()
    for row in manifest_rows:
        source_id = row.get("source_id", "")
        source_ids.add(source_id)
        missing = [field for field in SOURCE_DISPOSITION_MANIFEST_FIELDS if field not in row]
        if missing:
            results.append(
                CheckResult(
                    f"source_disposition:source:{source_id or 'unknown'}",
                    False,
                    f"missing fields: {', '.join(missing)}",
                    SOURCE_DISPOSITION_PATH,
                )
            )
            continue
        if row["source_kind"] not in {"file", "synthetic"}:
            results.append(
                CheckResult(
                    f"source_disposition:source:{source_id}",
                    False,
                    "source_kind must be file or synthetic",
                    SOURCE_DISPOSITION_PATH,
                )
            )
        if row["source_kind"] == "file":
            if not HEX40_RE.match(row["git_blob_id"]):
                results.append(
                    CheckResult(
                        f"source_disposition:source:{source_id}",
                        False,
                        "file source git_blob_id must be a 40-character hex object id",
                        SOURCE_DISPOSITION_PATH,
                    )
                )
            for field in ("sha256", "normalized_payload_digest"):
                if not HEX64_RE.match(row[field]):
                    results.append(
                        CheckResult(
                            f"source_disposition:source:{source_id}",
                            False,
                            f"file source {field} must be a 64-character hex digest",
                            SOURCE_DISPOSITION_PATH,
                        )
                    )
        if row["source_kind"] == "synthetic" and not row["durable_payload"].strip():
            results.append(
                CheckResult(
                    f"source_disposition:source:{source_id}",
                    False,
                    "synthetic source missing durable payload",
                    SOURCE_DISPOSITION_PATH,
                )
            )
        if row["source_kind"] == "synthetic" and not row["normalized_payload_digest"].strip():
            results.append(
                CheckResult(
                    f"source_disposition:source:{source_id}",
                    False,
                    "synthetic source missing normalized payload digest",
                    SOURCE_DISPOSITION_PATH,
                )
            )

    item_ids = {row.get("item_id", "") for row in item_rows}
    if required_item_ids is not None:
        missing_required_ids = sorted(required_item_ids - item_ids)
        if missing_required_ids:
            results.append(
                CheckResult(
                    "source_disposition:required_items",
                    False,
                    f"missing required item ids: {', '.join(missing_required_ids)}",
                    SOURCE_DISPOSITION_PATH,
                )
            )

    source_manifest_digest = final_stamp_field(markdown, "source_manifest_digest")
    if source_manifest_digest is None:
        results.append(
            CheckResult(
                "source_disposition:source_manifest_digest",
                False,
                "missing source_manifest_digest",
                SOURCE_DISPOSITION_PATH,
            )
        )
    elif manifest_rows and source_manifest_digest != source_disposition_table_digest(
        manifest_rows,
        SOURCE_DISPOSITION_MANIFEST_FIELDS,
    ):
        results.append(
            CheckResult(
                "source_disposition:source_manifest_digest",
                False,
                "source_manifest_digest mismatch",
                SOURCE_DISPOSITION_PATH,
            )
        )

    source_disposition_digest = final_stamp_field(markdown, "source_disposition_digest")
    if source_disposition_digest is None:
        results.append(
            CheckResult(
                "source_disposition:source_disposition_digest",
                False,
                "missing source_disposition_digest",
                SOURCE_DISPOSITION_PATH,
            )
        )
    elif item_rows and source_disposition_digest != source_disposition_table_digest(
        item_rows,
        SOURCE_DISPOSITION_ITEM_FIELDS,
    ):
        results.append(
            CheckResult(
                "source_disposition:source_disposition_digest",
                False,
                "source_disposition_digest mismatch",
                SOURCE_DISPOSITION_PATH,
            )
        )

    for field in SOURCE_BEARING_STAMP_FIELDS:
        if final_stamp_field(markdown, field) is None:
            results.append(
                CheckResult(
                    f"source_disposition:stamp:{field}",
                    False,
                    f"missing {field}",
                    SOURCE_DISPOSITION_PATH,
                )
            )
    if final_stamp_field(markdown, "source_bearing_result") != "passed":
        results.append(
            CheckResult(
                "source_disposition:stamp:source_bearing_result",
                False,
                "source_bearing_result must be passed",
                SOURCE_DISPOSITION_PATH,
            )
        )

    for row in item_rows:
        item_id = row.get("item_id", "")
        missing = [field for field in SOURCE_DISPOSITION_ITEM_FIELDS if field not in row]
        if missing:
            results.append(
                CheckResult(
                    f"source_disposition:item:{item_id or 'unknown'}",
                    False,
                    f"missing fields: {', '.join(missing)}",
                    SOURCE_DISPOSITION_PATH,
                )
            )
            continue
        if not row["normalized_claim_summary"].strip():
            results.append(
                CheckResult(
                    f"source_disposition:item:{item_id}",
                    False,
                    "normalized_claim_summary required",
                    SOURCE_DISPOSITION_PATH,
                )
            )
        if row["source_id"] not in source_ids:
            results.append(
                CheckResult(
                    f"source_disposition:item:{item_id}",
                    False,
                    f"unknown source_id: {row['source_id']}",
                    SOURCE_DISPOSITION_PATH,
                )
            )
        coverage_status = row["coverage_status"]
        challenge_status = row["challenge_status"]
        disposition = row["disposition"]
        challenge_confirmation = parse_bool_cell(row["challenge_operator_confirmation_required"])
        arbitration_required = parse_bool_cell(row["arbitration_required"])
        operator_decision = row["operator_decision"].strip()
        if coverage_status not in SOURCE_DISPOSITION_COVERAGE_STATUSES:
            results.append(
                CheckResult(
                    f"source_disposition:item:{item_id}",
                    False,
                    "invalid coverage_status",
                    SOURCE_DISPOSITION_PATH,
                )
            )
        if challenge_status not in SOURCE_DISPOSITION_CHALLENGE_STATUSES:
            results.append(
                CheckResult(
                    f"source_disposition:item:{item_id}",
                    False,
                    "challenge_status must be unchallenged or resolved",
                    SOURCE_DISPOSITION_PATH,
                )
            )
        if challenge_confirmation is None or arbitration_required is None:
            results.append(
                CheckResult(
                    f"source_disposition:item:{item_id}",
                    False,
                    "confirmation and arbitration fields must be booleans",
                    SOURCE_DISPOSITION_PATH,
                )
            )
        expected_dispositions = SOURCE_DISPOSITION_MATRIX.get(coverage_status, set())
        if disposition not in expected_dispositions:
            results.append(
                CheckResult(
                    f"source_disposition:item:{item_id}",
                    False,
                    "disposition not allowed for coverage_status",
                    SOURCE_DISPOSITION_PATH,
                )
            )
        expected_arbitration = (
            coverage_status != "adequately_captured"
            or challenge_confirmation is True
            or disposition == "integrated"
        )
        if arbitration_required is not None and arbitration_required != expected_arbitration:
            results.append(
                CheckResult(
                    f"source_disposition:item:{item_id}",
                    False,
                    "arbitration_required does not match source disposition rule",
                    SOURCE_DISPOSITION_PATH,
                )
            )
        if disposition == "integrated" and (arbitration_required is not True or not operator_decision):
            results.append(
                CheckResult(
                    f"source_disposition:item:{item_id}",
                    False,
                    "integrated disposition requires arbitration and operator_decision",
                    SOURCE_DISPOSITION_PATH,
                )
            )
        if arbitration_required is True and not operator_decision:
            results.append(
                CheckResult(
                    f"source_disposition:item:{item_id}",
                    False,
                    "operator_decision required when arbitration_required is true",
                    SOURCE_DISPOSITION_PATH,
                )
            )
        evidence_target = row["evidence_target"].strip()
        if evidence_target and not invalid_repo_relative_target(evidence_target):
            ok, detail, _target = repo_relative_path_status(root, evidence_target, "any")
            if not ok:
                results.append(
                    CheckResult(
                        f"source_disposition:item:{item_id}:target:{evidence_target}",
                        False,
                        f"evidence target {detail}",
                        SOURCE_DISPOSITION_PATH,
                    )
                )
        elif evidence_target:
            results.append(
                CheckResult(
                    f"source_disposition:item:{item_id}:target:{evidence_target}",
                    False,
                    "evidence target invalid",
                    SOURCE_DISPOSITION_PATH,
                )
            )

    if not any(result.name.startswith("source_disposition:") and not result.ok for result in results):
        results.append(CheckResult("source_disposition:ledger", True, "present", SOURCE_DISPOSITION_PATH))
    return results


def required_downstream_route_present(searchable_markdown: str, route: str) -> bool:
    if re.fullmatch(r"#\d+", route):
        route_token_re = re.compile(rf"(?<![\w#]){re.escape(route)}(?![\w-])")
        return route_token_re.search(searchable_markdown) is not None
    return route.casefold() in searchable_markdown.casefold()


def validate_skill_eval_methodology_source_intake(root: Path) -> list[CheckResult]:
    ok, detail, path = repo_relative_path_status(root, SKILL_EVAL_METHODOLOGY_SOURCE_INTAKE_PATH, "file")
    if not ok:
        return [
            CheckResult(
                "skill_eval_methodology_source_intake:path",
                False,
                detail,
                SKILL_EVAL_METHODOLOGY_SOURCE_INTAKE_PATH,
            )
        ]
    markdown = path.read_text(encoding="utf-8")
    visible_markdown = markdown_visible_text(markdown)
    nonblank_lines = [line.strip() for line in visible_markdown.splitlines() if line.strip()]
    headings = markdown_heading_texts(markdown)
    results: list[CheckResult] = []
    if "Status: Source Disposition Ledger" not in nonblank_lines[:8]:
        results.append(
            CheckResult(
                "skill_eval_methodology_source_intake:status",
                False,
                "status must be Source Disposition Ledger",
                SKILL_EVAL_METHODOLOGY_SOURCE_INTAKE_PATH,
            )
        )
    for required_section in SKILL_EVAL_METHODOLOGY_SOURCE_INTAKE_REQUIRED_SECTIONS:
        if normalize_reference_label(required_section) not in headings:
            results.append(
                CheckResult(
                    f"skill_eval_methodology_source_intake:section:{required_section}",
                    False,
                    f"missing section: {required_section}",
                    SKILL_EVAL_METHODOLOGY_SOURCE_INTAKE_PATH,
                )
            )
    searchable_markdown = markdown_link_search_text(markdown)
    searchable_markdown_casefold = searchable_markdown.casefold()
    for required_term in SKILL_EVAL_METHODOLOGY_SOURCE_INTAKE_COVERAGE_TERMS:
        if required_term.casefold() not in searchable_markdown_casefold:
            results.append(
                CheckResult(
                    f"skill_eval_methodology_source_intake:coverage:{required_term}",
                    False,
                    f"missing coverage term: {required_term}",
                    SKILL_EVAL_METHODOLOGY_SOURCE_INTAKE_PATH,
                )
            )
    for route in SKILL_EVAL_METHODOLOGY_SOURCE_INTAKE_DOWNSTREAM_ROUTES:
        if not required_downstream_route_present(searchable_markdown, route):
            results.append(
                CheckResult(
                    f"skill_eval_methodology_source_intake:routing:{route}",
                    False,
                    f"missing downstream route: {route}",
                    SKILL_EVAL_METHODOLOGY_SOURCE_INTAKE_PATH,
                )
            )
    if HOST_LOCAL_PATH_RE.search(visible_markdown):
        results.append(
            CheckResult(
                "skill_eval_methodology_source_intake:portable_paths",
                False,
                "ledger must not preserve host-local paths",
                SKILL_EVAL_METHODOLOGY_SOURCE_INTAKE_PATH,
            )
        )
    if results:
        return results
    return [
        CheckResult(
            "skill_eval_methodology_source_intake:ledger",
            True,
            "present",
            SKILL_EVAL_METHODOLOGY_SOURCE_INTAKE_PATH,
        )
    ]


def validate_plugin_creator_source_intake(root: Path) -> list[CheckResult]:
    ok, detail, path = repo_relative_path_status(root, PLUGIN_CREATOR_SOURCE_INTAKE_PATH, "file")
    if not ok:
        return [
            CheckResult(
                "plugin_creator_source_intake:path",
                False,
                detail,
                PLUGIN_CREATOR_SOURCE_INTAKE_PATH,
            )
        ]
    markdown = path.read_text(encoding="utf-8")
    visible_markdown = markdown_visible_text(markdown)
    nonblank_lines = [line.strip() for line in visible_markdown.splitlines() if line.strip()]
    headings = markdown_heading_texts(markdown)
    results: list[CheckResult] = []
    if "Status: Source Disposition Ledger" not in nonblank_lines[:8]:
        results.append(
            CheckResult(
                "plugin_creator_source_intake:status",
                False,
                "status must be Source Disposition Ledger",
                PLUGIN_CREATOR_SOURCE_INTAKE_PATH,
            )
        )
    for required_section in PLUGIN_CREATOR_SOURCE_INTAKE_REQUIRED_SECTIONS:
        if normalize_reference_label(required_section) not in headings:
            results.append(
                CheckResult(
                    f"plugin_creator_source_intake:section:{required_section}",
                    False,
                    f"missing section: {required_section}",
                    PLUGIN_CREATOR_SOURCE_INTAKE_PATH,
                )
            )
    searchable_markdown = markdown_link_search_text(markdown)
    searchable_markdown_casefold = searchable_markdown.casefold()
    for required_term in PLUGIN_CREATOR_SOURCE_INTAKE_COVERAGE_TERMS:
        if required_term.casefold() not in searchable_markdown_casefold:
            results.append(
                CheckResult(
                    f"plugin_creator_source_intake:coverage:{required_term}",
                    False,
                    f"missing coverage term: {required_term}",
                    PLUGIN_CREATOR_SOURCE_INTAKE_PATH,
                )
            )
    for route in PLUGIN_CREATOR_SOURCE_INTAKE_DOWNSTREAM_ROUTES:
        if not required_downstream_route_present(searchable_markdown, route):
            results.append(
                CheckResult(
                    f"plugin_creator_source_intake:routing:{route}",
                    False,
                    f"missing downstream route: {route}",
                    PLUGIN_CREATOR_SOURCE_INTAKE_PATH,
                )
            )
    if HOST_LOCAL_PATH_RE.search(visible_markdown):
        results.append(
            CheckResult(
                "plugin_creator_source_intake:portable_paths",
                False,
                "ledger must not preserve host-local paths",
                PLUGIN_CREATOR_SOURCE_INTAKE_PATH,
            )
        )
    if results:
        return results
    return [
        CheckResult(
            "plugin_creator_source_intake:ledger",
            True,
            "present",
            PLUGIN_CREATOR_SOURCE_INTAKE_PATH,
        )
    ]


def validate_harbor_jig_source_map(root: Path) -> list[CheckResult]:
    ok, detail, path = repo_relative_path_status(root, HARBOR_JIG_SOURCE_MAP_PATH, "file")
    if not ok:
        return [
            CheckResult(
                "harbor_jig_source_map:path",
                False,
                detail,
                HARBOR_JIG_SOURCE_MAP_PATH,
            )
        ]
    markdown = path.read_text(encoding="utf-8")
    visible_markdown = markdown_visible_text(markdown)
    nonblank_lines = [line.strip() for line in visible_markdown.splitlines() if line.strip()]
    headings = markdown_heading_texts(markdown)
    results: list[CheckResult] = []
    if "Status: Source Disposition Ledger" not in nonblank_lines[:8]:
        results.append(
            CheckResult(
                "harbor_jig_source_map:status",
                False,
                "status must be Source Disposition Ledger",
                HARBOR_JIG_SOURCE_MAP_PATH,
            )
        )
    for required_section in HARBOR_JIG_SOURCE_MAP_REQUIRED_SECTIONS:
        if normalize_reference_label(required_section) not in headings:
            results.append(
                CheckResult(
                    f"harbor_jig_source_map:section:{required_section}",
                    False,
                    f"missing section: {required_section}",
                    HARBOR_JIG_SOURCE_MAP_PATH,
                )
            )
    searchable_markdown = markdown_link_search_text(markdown)
    searchable_markdown_casefold = searchable_markdown.casefold()
    for required_term in HARBOR_JIG_SOURCE_MAP_COVERAGE_TERMS:
        if required_term.casefold() not in searchable_markdown_casefold:
            results.append(
                CheckResult(
                    f"harbor_jig_source_map:coverage:{required_term}",
                    False,
                    f"missing coverage term: {required_term}",
                    HARBOR_JIG_SOURCE_MAP_PATH,
                )
            )
    for route in HARBOR_JIG_SOURCE_MAP_DOWNSTREAM_ROUTES:
        if not required_downstream_route_present(searchable_markdown, route):
            results.append(
                CheckResult(
                    f"harbor_jig_source_map:routing:{route}",
                    False,
                    f"missing downstream route: {route}",
                    HARBOR_JIG_SOURCE_MAP_PATH,
                )
            )
    if HOST_LOCAL_PATH_RE.search(visible_markdown):
        results.append(
            CheckResult(
                "harbor_jig_source_map:portable_paths",
                False,
                "ledger must not preserve host-local paths",
                HARBOR_JIG_SOURCE_MAP_PATH,
            )
        )
    if results:
        return results
    return [
        CheckResult(
            "harbor_jig_source_map:ledger",
            True,
            "present",
            HARBOR_JIG_SOURCE_MAP_PATH,
        )
    ]


def validate_harbor_neighbor_tool_catalog(root: Path) -> list[CheckResult]:
    ok, detail, path = repo_relative_path_status(root, HARBOR_NEIGHBOR_TOOL_CATALOG_PATH, "file")
    if not ok:
        return [
            CheckResult(
                "harbor_neighbor_tool_catalog:path",
                False,
                detail,
                HARBOR_NEIGHBOR_TOOL_CATALOG_PATH,
            )
        ]
    markdown = path.read_text(encoding="utf-8")
    visible_markdown = markdown_visible_text(markdown)
    nonblank_lines = [line.strip() for line in visible_markdown.splitlines() if line.strip()]
    headings = markdown_heading_texts(markdown)
    results: list[CheckResult] = []
    if "Status: Source Disposition Ledger" not in nonblank_lines[:8]:
        results.append(
            CheckResult(
                "harbor_neighbor_tool_catalog:status",
                False,
                "status must be Source Disposition Ledger",
                HARBOR_NEIGHBOR_TOOL_CATALOG_PATH,
            )
        )
    for required_section in HARBOR_NEIGHBOR_TOOL_CATALOG_REQUIRED_SECTIONS:
        if normalize_reference_label(required_section) not in headings:
            results.append(
                CheckResult(
                    f"harbor_neighbor_tool_catalog:section:{required_section}",
                    False,
                    f"missing section: {required_section}",
                    HARBOR_NEIGHBOR_TOOL_CATALOG_PATH,
                )
            )
    searchable_markdown = markdown_link_search_text(markdown)
    searchable_markdown_casefold = searchable_markdown.casefold()
    visible_markdown_casefold = visible_markdown.casefold()
    table_header_cells: set[str] = set()
    visible_lines = visible_markdown.splitlines()
    for index, line in enumerate(visible_lines[:-1]):
        stripped_line = line.strip()
        stripped_next_line = visible_lines[index + 1].strip()
        if not (
            stripped_line.startswith("|")
            and stripped_line.endswith("|")
            and stripped_next_line.startswith("|")
            and stripped_next_line.endswith("|")
        ):
            continue
        separator_cells = [cell.strip() for cell in stripped_next_line.strip("|").split("|")]
        if not all(re.fullmatch(r":?-{3,}:?", cell) for cell in separator_cells):
            continue
        table_header_cells.update(cell.strip().casefold() for cell in stripped_line.strip("|").split("|"))
    for required_field in HARBOR_NEIGHBOR_TOOL_CATALOG_FIELDS:
        if required_field.casefold() not in table_header_cells:
            results.append(
                CheckResult(
                    f"harbor_neighbor_tool_catalog:field:{required_field}",
                    False,
                    f"missing catalog field: {required_field}",
                    HARBOR_NEIGHBOR_TOOL_CATALOG_PATH,
                )
            )
    for required_term in HARBOR_NEIGHBOR_TOOL_CATALOG_COVERAGE_TERMS:
        if required_term.casefold() not in searchable_markdown_casefold:
            results.append(
                CheckResult(
                    f"harbor_neighbor_tool_catalog:coverage:{required_term}",
                    False,
                    f"missing coverage term: {required_term}",
                    HARBOR_NEIGHBOR_TOOL_CATALOG_PATH,
                )
            )
    for route in HARBOR_NEIGHBOR_TOOL_CATALOG_ROUTES:
        if not required_downstream_route_present(searchable_markdown, route):
            results.append(
                CheckResult(
                    f"harbor_neighbor_tool_catalog:routing:{route}",
                    False,
                    f"missing downstream route: {route}",
                    HARBOR_NEIGHBOR_TOOL_CATALOG_PATH,
                )
            )
    broad_survey_excluded = (
        "broad market survey work is out of scope" in visible_markdown_casefold
        or "broad eval-platform survey work is out of scope" in visible_markdown_casefold
    )
    broad_survey_mentioned = (
        "broad market survey" in visible_markdown_casefold
        or "broad eval-platform survey" in visible_markdown_casefold
    )
    if broad_survey_mentioned and not broad_survey_excluded:
        results.append(
            CheckResult(
                "harbor_neighbor_tool_catalog:scope:broad_survey",
                False,
                "catalog must exclude broad market survey work",
                HARBOR_NEIGHBOR_TOOL_CATALOG_PATH,
            )
        )
    if HOST_LOCAL_PATH_RE.search(visible_markdown):
        results.append(
            CheckResult(
                "harbor_neighbor_tool_catalog:portable_paths",
                False,
                "ledger must not preserve host-local paths",
                HARBOR_NEIGHBOR_TOOL_CATALOG_PATH,
            )
        )
    if results:
        return results
    return [
        CheckResult(
            "harbor_neighbor_tool_catalog:ledger",
            True,
            "present",
            HARBOR_NEIGHBOR_TOOL_CATALOG_PATH,
        )
    ]


def validate_external_tool_evaluation(root: Path) -> list[CheckResult]:
    ok, detail, path = repo_relative_path_status(root, EXTERNAL_TOOL_EVALUATION_PATH, "file")
    if not ok:
        return [
            CheckResult(
                "external_tool_evaluation:path",
                False,
                detail,
                EXTERNAL_TOOL_EVALUATION_PATH,
            )
        ]
    markdown = path.read_text(encoding="utf-8")
    visible_markdown = markdown_visible_text(markdown)
    nonblank_lines = [line.strip() for line in visible_markdown.splitlines() if line.strip()]
    headings = markdown_heading_texts(markdown)
    results: list[CheckResult] = []
    if "Status: Armory Operating Contract" not in nonblank_lines[:8]:
        results.append(
            CheckResult(
                "external_tool_evaluation:status",
                False,
                "status must be Armory Operating Contract",
                EXTERNAL_TOOL_EVALUATION_PATH,
            )
        )
    for required_section in EXTERNAL_TOOL_EVALUATION_REQUIRED_SECTIONS:
        if normalize_reference_label(required_section) not in headings:
            results.append(
                CheckResult(
                    f"external_tool_evaluation:section:{required_section}",
                    False,
                    f"missing section: {required_section}",
                    EXTERNAL_TOOL_EVALUATION_PATH,
                )
            )
    searchable_markdown = markdown_link_search_text(markdown)
    searchable_markdown_casefold = searchable_markdown.casefold()
    for required_term in EXTERNAL_TOOL_EVALUATION_COVERAGE_TERMS:
        if required_term.casefold() not in searchable_markdown_casefold:
            results.append(
                CheckResult(
                    f"external_tool_evaluation:coverage:{required_term}",
                    False,
                    f"missing coverage term: {required_term}",
                    EXTERNAL_TOOL_EVALUATION_PATH,
                )
            )
    for route in EXTERNAL_TOOL_EVALUATION_ROUTES:
        if not required_downstream_route_present(searchable_markdown, route):
            results.append(
                CheckResult(
                    f"external_tool_evaluation:routing:{route}",
                    False,
                    f"missing downstream route: {route}",
                    EXTERNAL_TOOL_EVALUATION_PATH,
                )
            )
    if HOST_LOCAL_PATH_RE.search(visible_markdown):
        results.append(
            CheckResult(
                "external_tool_evaluation:portable_paths",
                False,
                "contract must not preserve host-local paths",
                EXTERNAL_TOOL_EVALUATION_PATH,
            )
        )
    if results:
        return results
    return [
        CheckResult(
            "external_tool_evaluation:contract",
            True,
            "present",
            EXTERNAL_TOOL_EVALUATION_PATH,
        )
    ]


def validate_harbor_external_tool_evaluation_record(root: Path) -> list[CheckResult]:
    ok, detail, path = repo_relative_path_status(root, HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH, "file")
    if not ok:
        return [
            CheckResult(
                "harbor_external_tool_evaluation_record:path",
                False,
                detail,
                HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH,
            )
        ]
    markdown = path.read_text(encoding="utf-8")
    visible_markdown = markdown_visible_text(markdown)
    nonblank_lines = [line.strip() for line in visible_markdown.splitlines() if line.strip()]
    headings = markdown_heading_texts(markdown)
    results: list[CheckResult] = []
    if "Status: External Tool Evaluation Record" not in nonblank_lines[:8]:
        results.append(
            CheckResult(
                "harbor_external_tool_evaluation_record:status",
                False,
                "status must be External Tool Evaluation Record",
                HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH,
            )
        )
    state_prefix = "Evaluation state: "
    state = next((line.removeprefix(state_prefix).strip() for line in nonblank_lines[:10] if line.startswith(state_prefix)), "")
    state_folded = state.casefold()
    if state_folded not in HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_STATES:
        results.append(
            CheckResult(
                "harbor_external_tool_evaluation_record:evaluation_state",
                False,
                "evaluation state must be in progress or complete",
                HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH,
            )
        )
    disposition_prefix = "Final disposition: "
    disposition = next(
        (line.removeprefix(disposition_prefix).strip() for line in nonblank_lines[:12] if line.startswith(disposition_prefix)),
        "",
    )
    disposition_folded = disposition.casefold()
    if disposition_folded not in EXTERNAL_TOOL_EVALUATION_DISPOSITIONS:
        results.append(
            CheckResult(
                "harbor_external_tool_evaluation_record:final_disposition",
                False,
                "final disposition must be a fixed External Tool Evaluation Disposition",
                HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH,
            )
        )
    elif state_folded == "complete" and disposition_folded not in FINALIZED_EXTERNAL_TOOL_EVALUATION_DISPOSITIONS:
        results.append(
            CheckResult(
                "harbor_external_tool_evaluation_record:state_disposition_coherence",
                False,
                "complete evaluations must use a finalized final disposition",
                HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH,
            )
        )
    for required_section in HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_REQUIRED_SECTIONS:
        if normalize_reference_label(required_section) not in headings:
            results.append(
                CheckResult(
                    f"harbor_external_tool_evaluation_record:section:{required_section}",
                    False,
                    f"missing section: {required_section}",
                    HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH,
                )
            )
    searchable_markdown = markdown_link_search_text(markdown)
    searchable_markdown_casefold = searchable_markdown.casefold()
    for required_term in HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_COVERAGE_TERMS:
        if required_term.casefold() not in searchable_markdown_casefold:
            results.append(
                CheckResult(
                    f"harbor_external_tool_evaluation_record:coverage:{required_term}",
                    False,
                    f"missing coverage term: {required_term}",
                    HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH,
                )
            )
    for route in HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_ROUTES:
        if not required_downstream_route_present(searchable_markdown, route):
            results.append(
                CheckResult(
                    f"harbor_external_tool_evaluation_record:routing:{route}",
                    False,
                    f"missing downstream route: {route}",
                    HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH,
                )
            )
    if HOST_LOCAL_PATH_RE.search(visible_markdown):
        results.append(
            CheckResult(
                "harbor_external_tool_evaluation_record:portable_paths",
                False,
                "record must not preserve host-local paths",
                HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH,
            )
        )
    if results:
        return results
    return [
        CheckResult(
            "harbor_external_tool_evaluation_record:record",
            True,
            "present",
            HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH,
        )
    ]


def validate_source_retired_tree(root: Path, *, include_disposition: bool = True) -> list[CheckResult]:
    results: list[CheckResult] = []
    raw_source_path = root / "docs/metasmith"
    if raw_source_path.exists() or raw_source_path.is_symlink():
        results.append(
            CheckResult(
                "source_retired:raw_sources",
                False,
                "docs/metasmith must be removed after source disposition",
                "docs/metasmith",
            )
        )
    if include_disposition:
        results.extend(validate_source_disposition(root, required_item_ids=SOURCE_DISPOSITION_FINAL_REQUIRED_ITEM_IDS))
    if not any(not result.ok for result in results):
        results.append(CheckResult("source_retired:tree", True, "raw sources removed", "docs"))
    return results


def final_stamp_field(markdown: str, field: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(field)}:\s*(.*?)\s*$", markdown)
    return match.group(1) if match else None


def validate_final_source_retired_stamp(root: Path) -> list[CheckResult]:
    ok, detail, path = repo_relative_path_status(root, SOURCE_DISPOSITION_PATH, "file")
    if not ok:
        return [CheckResult("source_retired_stamp:path", False, detail, SOURCE_DISPOSITION_PATH)]
    markdown = path.read_text(encoding="utf-8")
    results: list[CheckResult] = []
    stamp_section = markdown_section(markdown, "## Final Source-Retired Stamp")
    if stamp_section is None:
        return [
            CheckResult(
                "source_retired_stamp:section",
                False,
                "missing Final Source-Retired Stamp section",
                SOURCE_DISPOSITION_PATH,
            )
        ]
    for volatile_field in ("stamp_target", "canonical_tree_digest", "timestamp"):
        if final_stamp_field(stamp_section, volatile_field) is not None:
            results.append(
                CheckResult(
                    f"source_retired_stamp:{volatile_field}",
                    False,
                    f"{volatile_field} is volatile and must be removed",
                    SOURCE_DISPOSITION_PATH,
                )
            )
    if final_stamp_field(stamp_section, "source_retired") != "true":
        results.append(
            CheckResult("source_retired_stamp:source_retired", False, "source_retired must be true", SOURCE_DISPOSITION_PATH)
        )
    if not any(result.name.startswith("source_retired_stamp:") and not result.ok for result in results):
        results.append(CheckResult("source_retired_stamp:source_retired", True, "true", SOURCE_DISPOSITION_PATH))
    return results


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


def story_closeout_gate_order_valid(markdown: str) -> bool:
    section = markdown_section(markdown_visible_text(markdown), "## Gate order")
    if section is None:
        return False
    numbered_items: list[str] = []
    for line in section.splitlines():
        match = re.match(r"^\s*\d+\.\s+(.+)$", line)
        if match:
            numbered_items.append(match.group(1).casefold())
    if not numbered_items:
        return False
    token_index = 0
    for item in numbered_items:
        if STORY_CLOSEOUT_GATE_ORDER_TOKENS[token_index] in item:
            token_index += 1
            if token_index == len(STORY_CLOSEOUT_GATE_ORDER_TOKENS):
                return True
    return False


CANONICAL_DOC_STATUSES = {
    "docs/vision.md": "Armory Canon",
    "docs/agent-equipment-forge.md": "Forge Canon",
    "docs/smith-runbook.md": "Forge Core",
    "docs/forgewright-runbook.md": "Forge Core",
    "docs/interface-decision-guide.md": "Forge Canon",
    "docs/harness-components.md": "Forge Canon",
    "docs/harness-capabilities.md": "Forge Canon",
    "docs/evidence-taxonomy.md": "Forge Canon",
    "docs/security-and-control.md": "Forge Canon",
    "docs/equipment-promotion.md": "Forge Canon",
    "docs/equipment-delivery.md": "Forge Canon",
    "docs/story-closeout.md": "Armory Operating Contract",
}


def has_live_canonical_status(markdown: str, required_status: str) -> bool:
    visible_markdown = markdown_visible_text(markdown)
    nonblank_lines = [line.strip() for line in visible_markdown.splitlines() if line.strip()]
    return f"Status: {required_status}" in nonblank_lines[:8]


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


def python_runtime_reference_path_excluded(relative_path: Path) -> bool:
    return any(part in PYTHON_RUNTIME_REFERENCE_EXCLUDED_DIR_NAMES for part in relative_path.parts) or any(
        relative_path == excluded or relative_path.is_relative_to(excluded)
        for excluded in PYTHON_RUNTIME_REFERENCE_EXCLUDED_DIRS
    )


def python_runtime_text_files(root: Path) -> list[Path]:
    files: list[Path] = []
    directories = [root]
    while directories:
        directory = directories.pop()
        try:
            entries = sorted(directory.iterdir())
        except OSError:
            continue
        for path in entries:
            relative = path.relative_to(root)
            if python_runtime_reference_path_excluded(relative):
                continue
            try:
                if path.is_symlink():
                    continue
                if path.is_dir():
                    directories.append(path)
                    continue
                if not path.is_file():
                    continue
                path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            files.append(path)
    return sorted(files)


def validate_python_runtime_declaration(root: Path) -> list[CheckResult]:
    ok, detail, path = repo_relative_path_status(root, PYTHON_VERSION_DECLARATION_PATH, "file")
    if not ok:
        return [
            CheckResult(
                "python_runtime:.python-version",
                False,
                detail,
                PYTHON_VERSION_DECLARATION_PATH,
            )
        ]
    declared_version = path.read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+", declared_version):
        return [
            CheckResult(
                "python_runtime:.python-version",
                False,
                "must contain MAJOR.MINOR",
                PYTHON_VERSION_DECLARATION_PATH,
            )
        ]

    results: list[CheckResult] = []
    for text_path in python_runtime_text_files(root):
        relative_path = text_path.relative_to(root).as_posix()
        text = text_path.read_text(encoding="utf-8")
        observed_versions = {
            match.group(1)
            for match in PYTHON_RUNTIME_REFERENCE_RE.finditer(text)
            if match.group(1) != declared_version
        }
        for observed_version in sorted(observed_versions):
            results.append(
                CheckResult(
                    f"python_runtime:reference:{relative_path}:{observed_version}",
                    False,
                    f"Python runtime reference {observed_version} does not match .python-version {declared_version}",
                    relative_path,
                )
            )
    if not results:
        results.append(
            CheckResult(
                "python_runtime:.python-version",
                True,
                f"declares Python {declared_version}",
                PYTHON_VERSION_DECLARATION_PATH,
            )
        )
    return results


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
        validation_status = row["validation_status"].strip()
        if validation_status not in SOURCE_PROJECTION_VALIDATION_STATUSES:
            results.append(
                CheckResult(
                    name=f"source_projection:{requirement_id}",
                    ok=False,
                    detail="validation_status must be planned or validated",
                    path=SOURCE_PROJECTION_PATH,
                )
            )
        elif validation_status == "validated" and requirement_id in SOURCE_PROJECTION_PLANNED_REQUIREMENTS:
            results.append(
                CheckResult(
                    name=f"source_projection:{requirement_id}",
                    ok=False,
                    detail="validation_status must remain planned until closeout evidence lands",
                    path=SOURCE_PROJECTION_PATH,
                )
            )
        elif (
            disposition == "projected"
            and validation_status == "planned"
            and requirement_id not in SOURCE_PROJECTION_PLANNED_REQUIREMENTS
        ):
            results.append(
                CheckResult(
                    name=f"source_projection:{requirement_id}",
                    ok=False,
                    detail="validation_status must be validated for completed projected requirement",
                    path=SOURCE_PROJECTION_PATH,
                )
            )
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


def validate_forge_routes(root: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    agents_path = root / "AGENTS.md"
    readme_path = root / "README.md"
    agents_markdown = agents_path.read_text(encoding="utf-8") if agents_path.exists() else ""
    readme_markdown = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

    agents_section = markdown_section(agents_markdown, "## Forge Conveyor")
    readme_section = markdown_section(readme_markdown, "## Agent Equipment Forge")

    if agents_section is None:
        results.append(CheckResult("forge_route:agent", False, "missing Forge Conveyor", "AGENTS.md"))
    if readme_section is None:
        results.append(CheckResult("forge_route:human", False, "missing Forge Tour", "README.md"))

    agents_targets: list[str] = []
    if agents_section is not None:
        agents_targets = unique_preserve_order([*find_markdown_links(agents_section), *find_backticked_paths(agents_section)])
        for required_route in REQUIRED_PRELOADED_ROUTES:
            if required_route not in agents_targets:
                results.append(
                    CheckResult(
                        f"forge_route:agent:{required_route}",
                        False,
                        "missing required preloaded route",
                        "AGENTS.md",
                    )
                )

    readme_targets: list[str] = []
    if readme_section is not None:
        readme_targets = find_markdown_links(readme_section)
        if "docs/forge-tour.md" not in readme_targets:
            results.append(
                CheckResult(
                    "forge_route:human:docs/forge-tour.md",
                    False,
                    "missing Forge Tour link",
                    "README.md",
                )
            )

    for target in unique_preserve_order([*agents_targets, *readme_targets]):
        ok, detail, _ = route_target_status(root, target)
        if not ok:
            source = "AGENTS.md" if target in agents_targets else "README.md"
            results.append(
                CheckResult(
                    f"forge_route:target:{target}",
                    False,
                    detail,
                    source,
                )
            )

    if not any(not result.ok for result in results):
        results.append(CheckResult("forge_route:agent", True, "present", "AGENTS.md"))
        results.append(CheckResult("forge_route:human", True, "present", "README.md"))
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
        if relative_path not in CANONICAL_DOC_STATUSES:
            results.append(
                CheckResult(
                    f"canonical_doc:status_mapping:{relative_path}",
                    False,
                    "missing canonical status mapping",
                    relative_path,
                )
            )
            continue
        required_status = CANONICAL_DOC_STATUSES[relative_path]
        if not has_live_canonical_status(markdown, required_status):
            results.append(
                CheckResult(
                    f"canonical_doc:status:{relative_path}",
                    False,
                    f"missing Status: {required_status}",
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
        if relative_path == STORY_CLOSEOUT_PATH and not story_closeout_gate_order_valid(markdown):
            results.append(
                CheckResult(
                    f"canonical_doc:story_closeout_gate_order:{relative_path}",
                    False,
                    "gate order must include required items in order",
                    relative_path,
                )
            )
        if not any(result.name.startswith(f"canonical_doc:") and result.path == relative_path and not result.ok for result in results):
            results.append(CheckResult(f"canonical_doc:{relative_path}", True, "present", relative_path))
    return results


def validate_context(root: Path) -> list[CheckResult]:
    ok, detail, path = repo_relative_path_status(root, "CONTEXT.md", "file")
    if not ok:
        if detail == "path contains symlink":
            detail = "context path contains symlink"
        return [CheckResult("context:path", False, detail, "CONTEXT.md")]
    markdown = path.read_text(encoding="utf-8")
    headings = markdown_heading_texts(markdown)
    results: list[CheckResult] = []
    for required_section in CONTEXT_REQUIRED_SECTIONS:
        if normalize_reference_label(required_section) not in headings:
            results.append(
                CheckResult(
                    f"context:section:{required_section}",
                    False,
                    f"missing section: {required_section}",
                    "CONTEXT.md",
                )
            )
    return results


def validate_threat_model(root: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    ok, detail, path = repo_relative_path_status(root, THREAT_MODEL_PATH, "file")
    if not ok:
        if detail == "path contains symlink":
            detail = "threat model path contains symlink"
        results.append(CheckResult(f"threat_model:path:{THREAT_MODEL_PATH}", False, detail, THREAT_MODEL_PATH))
    else:
        markdown = path.read_text(encoding="utf-8")
        headings = markdown_heading_texts(markdown)
        for required_section in THREAT_MODEL_REQUIRED_SECTIONS:
            if normalize_reference_label(required_section) not in headings:
                results.append(
                    CheckResult(
                        f"threat_model:section:{THREAT_MODEL_PATH}:{required_section}",
                        False,
                        f"missing section: {required_section}",
                        THREAT_MODEL_PATH,
                    )
                )
    referenced = False
    reference_missing = False
    for relative_path in THREAT_MODEL_REFERENCE_PATHS:
        ref_ok, ref_detail, ref_path = repo_relative_path_status(root, relative_path, "file")
        if not ref_ok:
            reference_missing = True
            continue
        markdown = ref_path.read_text(encoding="utf-8")
        visible = markdown_visible_text(markdown).casefold()
        links = find_markdown_links(markdown)
        if "repository threat model" in visible or THREAT_MODEL_PATH in links or "security/threat-model.md" in links:
            referenced = True
            break
    if not referenced:
        detail = "reference surface missing" if reference_missing else "missing threat model reference"
        results.append(
            CheckResult(
                f"threat_model:reference:{THREAT_MODEL_REFERENCE_PATHS[0]}",
                False,
                detail,
                THREAT_MODEL_REFERENCE_PATHS[0],
            )
        )
    if not any(result.name.startswith("threat_model:") and not result.ok for result in results):
        results.append(CheckResult("threat_model:repository", True, "present", THREAT_MODEL_PATH))
    return results


def validate_documentation_closeout(root: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    ok, detail, path = repo_relative_path_status(root, DOCUMENTATION_CLOSEOUT_PATH, "file")
    if not ok:
        if detail == "path contains symlink":
            detail = "documentation closeout path contains symlink"
        results.append(
            CheckResult(
                f"documentation_closeout:path:{DOCUMENTATION_CLOSEOUT_PATH}",
                False,
                detail,
                DOCUMENTATION_CLOSEOUT_PATH,
            )
        )
        return results
    markdown = path.read_text(encoding="utf-8")
    visible = markdown_visible_text(markdown)
    visible_folded = visible.casefold()
    visible_folded_normalized = " ".join(visible_folded.split())
    nonblank_lines = [line.strip() for line in visible.splitlines() if line.strip()]
    if "Status: Completed Closeout" not in nonblank_lines[:8]:
        results.append(
            CheckResult(
                f"documentation_closeout:status:{DOCUMENTATION_CLOSEOUT_PATH}",
                False,
                "missing completed closeout status",
                DOCUMENTATION_CLOSEOUT_PATH,
            )
        )
    headings = markdown_heading_texts(markdown)
    for required_section in DOCUMENTATION_CLOSEOUT_REQUIRED_SECTIONS:
        if normalize_reference_label(required_section) not in headings:
            results.append(
                CheckResult(
                    f"documentation_closeout:section:{DOCUMENTATION_CLOSEOUT_PATH}:{required_section}",
                    False,
                    f"missing section: {required_section}",
                    DOCUMENTATION_CLOSEOUT_PATH,
                )
            )
    for forbidden_text in DOCUMENTATION_CLOSEOUT_FORBIDDEN_INCOMPLETE_TEXT:
        if forbidden_text.casefold() in visible_folded:
            results.append(
                CheckResult(
                    f"documentation_closeout:review:{DOCUMENTATION_CLOSEOUT_PATH}",
                    False,
                    "contains unresolved review placeholder",
                    DOCUMENTATION_CLOSEOUT_PATH,
                )
            )
            break
    for required_text in DOCUMENTATION_CLOSEOUT_REQUIRED_EVIDENCE:
        if " ".join(required_text.casefold().split()) not in visible_folded_normalized:
            results.append(
                CheckResult(
                    f"documentation_closeout:evidence:{DOCUMENTATION_CLOSEOUT_PATH}:{required_text}",
                    False,
                    f"missing evidence: {required_text}",
                    DOCUMENTATION_CLOSEOUT_PATH,
                )
            )
    required_review_statuses = [
        "Documentation closeout",
        "Cross-Boundary Coherence",
        "Story Quality",
    ]
    for review_status in required_review_statuses:
        pattern = rf"(?im)^(?:-\s*)?{re.escape(review_status)}(?: review)?:\s*`?Ralph Review Cycle \d+`?\.?\s*$"
        if re.search(pattern, visible) is None:
            results.append(
                CheckResult(
                    f"documentation_closeout:review:{DOCUMENTATION_CLOSEOUT_PATH}:{review_status}",
                    False,
                    f"review status must name a Ralph Review Cycle: {review_status}",
                    DOCUMENTATION_CLOSEOUT_PATH,
                )
            )
    if not any(result.name.startswith("documentation_closeout:") and not result.ok for result in results):
        results.append(CheckResult("documentation_closeout:forge-seed", True, "present", DOCUMENTATION_CLOSEOUT_PATH))
    return results


def validate_security_closeout(root: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    ok, detail, path = repo_relative_path_status(root, SECURITY_CLOSEOUT_PATH, "file")
    if not ok:
        if detail == "path contains symlink":
            detail = "security closeout path contains symlink"
        results.append(
            CheckResult(
                f"security_closeout:path:{SECURITY_CLOSEOUT_PATH}",
                False,
                detail,
                SECURITY_CLOSEOUT_PATH,
            )
        )
        return results
    markdown = path.read_text(encoding="utf-8")
    visible = markdown_visible_text(markdown)
    visible_folded = visible.casefold()
    visible_normalized = " ".join(visible_folded.split())
    nonblank_lines = [line.strip() for line in visible.splitlines() if line.strip()]
    if "Status: Completed Security Closeout" not in nonblank_lines[:8]:
        results.append(
            CheckResult(
                f"security_closeout:status:{SECURITY_CLOSEOUT_PATH}",
                False,
                "missing completed security closeout status",
                SECURITY_CLOSEOUT_PATH,
            )
        )
    headings = markdown_heading_texts(markdown)
    for required_section in SECURITY_CLOSEOUT_REQUIRED_SECTIONS:
        if normalize_reference_label(required_section) not in headings:
            results.append(
                CheckResult(
                    f"security_closeout:section:{SECURITY_CLOSEOUT_PATH}:{required_section}",
                    False,
                    f"missing section: {required_section}",
                    SECURITY_CLOSEOUT_PATH,
                )
            )
    for required_text in SECURITY_CLOSEOUT_REQUIRED_EVIDENCE:
        required_text_normalized = " ".join(required_text.casefold().split())
        if required_text_normalized not in visible_normalized:
            results.append(
                CheckResult(
                    f"security_closeout:evidence:{SECURITY_CLOSEOUT_PATH}:{required_text}",
                    False,
                    f"missing evidence: {required_text}",
                    SECURITY_CLOSEOUT_PATH,
                )
            )
    skipped_phase_normalized = " ".join(SECURITY_CLOSEOUT_SKIPPED_PHASE_DISPOSITION.casefold().split())
    completed_phase_evidence_present = all(
        " ".join(required_text.casefold().split()) in visible_normalized
        for required_text in SECURITY_CLOSEOUT_COMPLETED_PHASE_EVIDENCE
    )
    if skipped_phase_normalized not in visible_normalized and not completed_phase_evidence_present:
        results.append(
            CheckResult(
                f"security_closeout:evidence:{SECURITY_CLOSEOUT_PATH}:validation and attack-path disposition",
                False,
                "missing validation and attack-path disposition",
                SECURITY_CLOSEOUT_PATH,
            )
        )
    if not any(result.name.startswith("security_closeout:") and not result.ok for result in results):
        results.append(CheckResult("security_closeout:forge-seed", True, "present", SECURITY_CLOSEOUT_PATH))
    return results


def plan_step_is_checked(root: Path, step_label: str) -> bool:
    ok, _detail, path = repo_relative_path_status(root, PLAN_PATH, "file")
    if not ok:
        return False
    pattern = re.compile(rf"(?m)^-\s*\[x\]\s+\*\*{re.escape(step_label)}\*\*")
    return bool(pattern.search(path.read_text(encoding="utf-8")))


def validate_projection_drafts(root: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    ok, detail, path = repo_relative_path_status(root, PROJECTION_DRAFTS_PATH, "file")
    if not ok:
        if detail == "path contains symlink":
            detail = "projection drafts path contains symlink"
        results.append(
            CheckResult(
                f"projection_drafts:path:{PROJECTION_DRAFTS_PATH}",
                False,
                detail,
                PROJECTION_DRAFTS_PATH,
            )
        )
        return results
    markdown = path.read_text(encoding="utf-8")
    visible = markdown_visible_text(markdown)
    raw_folded = markdown.casefold()
    raw_folded_normalized = " ".join(raw_folded.split())
    nonblank_lines = [line.strip() for line in visible.splitlines() if line.strip()]
    if "Status: Review Draft" not in nonblank_lines[:8]:
        results.append(
            CheckResult(
                f"projection_drafts:status:{PROJECTION_DRAFTS_PATH}",
                False,
                "missing review draft status",
                PROJECTION_DRAFTS_PATH,
            )
        )
    headings = markdown_heading_texts(markdown)
    for required_section in PROJECTION_DRAFTS_REQUIRED_SECTIONS:
        if normalize_reference_label(required_section) not in headings:
            results.append(
                CheckResult(
                    f"projection_drafts:section:{PROJECTION_DRAFTS_PATH}:{required_section}",
                    False,
                    f"missing section: {required_section}",
                    PROJECTION_DRAFTS_PATH,
                )
            )
    for required_text in PROJECTION_DRAFTS_REQUIRED_EVIDENCE:
        if " ".join(required_text.casefold().split()) not in raw_folded_normalized:
            results.append(
                CheckResult(
                    f"projection_drafts:evidence:{PROJECTION_DRAFTS_PATH}:{required_text}",
                    False,
                    f"missing evidence: {required_text}",
                    PROJECTION_DRAFTS_PATH,
                )
            )
    documentation_closeout_review_ok = re.search(
        r"(?im)^documentation closeout(?: review)?:\s*(?:`?Ralph Review Cycle \d+`?|Ralph Review Cycle \d+\.?)\s*$",
        markdown,
    )
    if any(forbidden.casefold() in raw_folded for forbidden in PROJECTION_DRAFTS_FORBIDDEN_UNRESOLVED_TEXT) or (
        documentation_closeout_review_ok is None
    ):
        results.append(
            CheckResult(
                f"projection_drafts:evidence:{PROJECTION_DRAFTS_PATH}:documentation closeout review",
                False,
                "documentation closeout review must name a Ralph Review Cycle",
                PROJECTION_DRAFTS_PATH,
            )
        )
    story_review_step_complete = plan_step_is_checked(root, STORY_REVIEW_STEP_LABEL)
    cross_boundary_review_ok = re.search(
        r"(?im)^(?:-\s*)?cross-boundary coherence(?: review)?:\s*(?:`?Ralph Review Cycle \d+`?|Ralph Review Cycle \d+\.?)\s*$",
        markdown,
    )
    story_quality_review_ok = re.search(
        r"(?im)^(?:-\s*)?story quality(?: review)?:\s*(?:`?Ralph Review Cycle \d+`?|Ralph Review Cycle \d+\.?)\s*$",
        markdown,
    )
    review_cycles_by_kind: dict[str, set[str]] = {
        "cross-boundary coherence": set(),
        "story quality": set(),
    }
    for match in STORY_REVIEW_LINE_RE.finditer(markdown):
        review_cycles_by_kind[match.group(1).casefold()].add(match.group(2))
    for kind, cycles in review_cycles_by_kind.items():
        if len(cycles) > 1:
            results.append(
                CheckResult(
                    f"projection_drafts:evidence:{PROJECTION_DRAFTS_PATH}:{kind} review consistency",
                    False,
                    f"projection drafts must not publish conflicting {kind} review cycles",
                    PROJECTION_DRAFTS_PATH,
                )
            )
    if (
        PROJECTION_DRAFTS_PENDING_STORY_REVIEW_PLACEHOLDER.casefold() in raw_folded
        and "tools/validate_armory_integrity.py --final-closeout`: passed" in raw_folded
    ):
        results.append(
            CheckResult(
                f"projection_drafts:evidence:{PROJECTION_DRAFTS_PATH}:final closeout status",
                False,
                "projection drafts must not claim final-closeout passed while story-review placeholders remain",
                PROJECTION_DRAFTS_PATH,
            )
        )
    if story_review_step_complete and (
        PROJECTION_DRAFTS_PENDING_STORY_REVIEW_PLACEHOLDER.casefold() in raw_folded
        or cross_boundary_review_ok is None
        or story_quality_review_ok is None
    ):
        results.append(
            CheckResult(
                f"projection_drafts:evidence:{PROJECTION_DRAFTS_PATH}:story closeout reviews",
                False,
                "completed story closeout must name Cross-Boundary Coherence and Story Quality Ralph Review cycles",
                PROJECTION_DRAFTS_PATH,
            )
        )
    if not any(result.name.startswith("projection_drafts:") and not result.ok for result in results):
        results.append(CheckResult("projection_drafts:forge-seed", True, "present", PROJECTION_DRAFTS_PATH))
    return results


def validate_final_closeout(root: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    ok, detail, path = repo_relative_path_status(root, PROJECTION_DRAFTS_PATH, "file")
    if not ok:
        return [CheckResult(f"final_closeout:path:{PROJECTION_DRAFTS_PATH}", False, detail, PROJECTION_DRAFTS_PATH)]
    markdown = path.read_text(encoding="utf-8")
    raw_folded = markdown.casefold()
    cross_boundary_review_ok = re.search(
        r"(?im)^(?:-\s*)?cross-boundary coherence(?: review)?:\s*(?:`?Ralph Review Cycle \d+`?|Ralph Review Cycle \d+\.?)\s*$",
        markdown,
    )
    story_quality_review_ok = re.search(
        r"(?im)^(?:-\s*)?story quality(?: review)?:\s*(?:`?Ralph Review Cycle \d+`?|Ralph Review Cycle \d+\.?)\s*$",
        markdown,
    )
    if not plan_step_is_checked(root, STORY_REVIEW_STEP_LABEL):
        results.append(
            CheckResult(
                f"final_closeout:evidence:{PLAN_PATH}:story closeout reviews",
                False,
                "final closeout requires completed story closeout review step in the plan",
                PLAN_PATH,
            )
        )
    if (
        PROJECTION_DRAFTS_PENDING_STORY_REVIEW_PLACEHOLDER.casefold() in raw_folded
        or cross_boundary_review_ok is None
        or story_quality_review_ok is None
    ):
        results.append(
            CheckResult(
                f"final_closeout:evidence:{PROJECTION_DRAFTS_PATH}:story closeout reviews",
                False,
                "final closeout must name Cross-Boundary Coherence and Story Quality Ralph Review cycles",
                PROJECTION_DRAFTS_PATH,
            )
        )
    review_cycles_by_kind: dict[str, set[str]] = {
        "cross-boundary coherence": set(),
        "story quality": set(),
    }
    for match in STORY_REVIEW_LINE_RE.finditer(markdown):
        review_cycles_by_kind[match.group(1).casefold()].add(match.group(2))
    for kind, cycles in review_cycles_by_kind.items():
        if len(cycles) > 1:
            results.append(
                CheckResult(
                    f"final_closeout:evidence:{PROJECTION_DRAFTS_PATH}:{kind} review consistency",
                    False,
                    f"final closeout must not publish conflicting {kind} review cycles",
                    PROJECTION_DRAFTS_PATH,
                )
            )
    if any(marker in raw_folded for marker in PROJECTION_DRAFTS_SCRATCH_ARTIFACT_MARKERS):
        results.append(
            CheckResult(
                f"final_closeout:evidence:{PROJECTION_DRAFTS_PATH}:portable evidence",
                False,
                "external projection drafts must not publish host-local or scratch artifact paths",
                PROJECTION_DRAFTS_PATH,
            )
        )
    for evidence_path in (PROJECTION_DRAFTS_PATH, SECURITY_CLOSEOUT_PATH):
        ok, _detail, current_path = repo_relative_path_status(root, evidence_path, "file")
        if ok and FINAL_CLOSEOUT_EXACT_VALIDATION_COUNT_RE.search(current_path.read_text(encoding="utf-8")):
            results.append(
                CheckResult(
                    f"final_closeout:evidence:{evidence_path}:validation evidence",
                    False,
                    "final closeout evidence should cite validation commands without hard-coded pass counts",
                    evidence_path,
                )
            )
    if not any(result.name.startswith("final_closeout:") and not result.ok for result in results):
        results.append(CheckResult("final_closeout:forge-seed", True, "ready", PROJECTION_DRAFTS_PATH))
    return results


def non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def non_empty_string_list(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(non_empty_string(item) for item in value)


def string_list(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def validate_harness_catalog(root: Path) -> list[CheckResult]:
    profile_dir = harness_capability_profiles.VANILLA_PROFILE_DIR.as_posix()
    try:
        manager_results = harness_capability_profiles.validate(root)
    except Exception as error:
        return [
            CheckResult(
                "harness_catalog:manager_core:exception",
                False,
                f"manager core validation crashed: {error.__class__.__name__}: {error}",
                profile_dir,
            )
        ]
    failures = [result for result in manager_results if not result.ok]
    if not failures:
        return [
            CheckResult(
                "harness_catalog:manager_core",
                True,
                f"{harness_capability_profiles.VALIDATION_NAME} passed",
                profile_dir,
            )
        ]
    return [
        CheckResult(
            f"harness_catalog:manager_core:{result.name}",
            False,
            result.detail,
            result.path,
        )
        for result in failures
    ]


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


def hook_declares_side_effect_classification_type(text: str) -> bool:
    type_match = re.search(
        r"export\s+type\s+SideEffectClassification\s*=\s*(?P<body>.*?);",
        text,
        flags=re.DOTALL,
    )
    if type_match is None:
        return False
    type_body = type_match.group("body")
    return all(f'"{classification}"' in type_body for classification in HOOK_SIDE_EFFECT_CLASSIFICATIONS)


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
    normalized = re.sub(r"\.trim\(\)", ".trim", stripped)
    normalized_structure = typescript_structure_source(normalized)
    if any(character in normalized_structure for character in "(){}[];,"):
        return False
    if re.search(r"\b(await|new|delete|yield|throw|import|function|class)\b", normalized_structure):
        return False
    if "=>" in normalized_structure or "++" in normalized_structure or "--" in normalized_structure:
        return False
    if re.search(r"(\+=|-=|\*=|/=|%=|&&=|\|\|=|\?\?=)", normalized_structure):
        return False
    if re.search(r"(?<![=!<>])=(?![=>])", normalized_structure):
        return False
    return re.fullmatch(r"[A-Za-z0-9_$.\s!&|=<>]*", normalized_structure) is not None


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
    guard_patterns = [
        r"!event\s*\|\|\s*!event\.kind",
        r'!event\s*\|\|\s*typeof\s+event\.kind\s*!==\s*"string"\s*\|\|\s*event\.kind\.trim\(\)\s*===\s*""',
    ]
    if not any(re.fullmatch(pattern, condition) for pattern in guard_patterns):
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
    if side_effect_classification not in HOOK_SIDE_EFFECT_CLASSIFICATIONS:
        results.append(
            CheckResult(
                f"template:hook:{HOOK_TEMPLATE_PATH}:side-effect classification vocabulary",
                False,
                "side-effect classification must be one canonical label",
                HOOK_TEMPLATE_PATH,
            )
        )
    if not hook_declares_side_effect_classification_type(text):
        results.append(
            CheckResult(
                f"template:hook:{HOOK_TEMPLATE_PATH}:side-effect classification type",
                False,
                "SideEffectClassification type must list canonical labels",
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
    return script_cli_entry_point_failure_detail(tree) is None


def script_cli_entry_point_failure_detail(tree: ast.AST) -> str | None:
    if not script_uses_only_allowed_calls(tree):
        return "CLI entry point uses disallowed imports, names, rebindings, or calls"
    main_definitions = [
        (index, node)
        for index, node in enumerate(tree.body)
        if isinstance(node, ast.FunctionDef) and node.name == "main"
    ]
    if len(main_definitions) != 1:
        return "CLI entry point requires exactly one main() definition"
    main_definition_index, main_definition = main_definitions[0]
    if not main_definition_is_plain(main_definition):
        return "main() must have the plain validator entry-point signature"
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
        return 'CLI entry point requires exactly one if __name__ == "__main__" guard'
    guard_index, guard = matching_guards[0]
    if guard_index <= main_definition_index:
        return "CLI entry point guard must appear after main()"
    if guard_index != main_definition_index + 1 or guard_index != len(tree.body) - 1:
        return "CLI entry point guard must immediately follow main() and be the final top-level statement"
    if not all(script_top_level_statement_is_allowed(statement, guard) for statement in tree.body):
        return "CLI entry point has unsupported top-level statements"
    if guard.orelse or len(guard.body) != 1 or not statement_invokes_main(guard.body[0]):
        return "CLI entry point guard must contain only raise SystemExit(main())"
    return None


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
    cli_failure_detail = "missing CLI entry point" if tree is None else script_cli_entry_point_failure_detail(tree)
    if cli_failure_detail is not None:
        results.append(
            CheckResult(
                f"template:script:{SCRIPT_TEMPLATE_PATH}:cli entry point",
                False,
                "missing CLI entry point",
                SCRIPT_TEMPLATE_PATH,
            )
        )
        if cli_failure_detail != "missing CLI entry point":
            results.append(
                CheckResult(
                    f"template:script:{SCRIPT_TEMPLATE_PATH}:cli entry point detail",
                    False,
                    cli_failure_detail,
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


def validate_published_equipment_delivery(root: Path) -> list[CheckResult]:
    ok, detail, path = repo_relative_path_status(root, PUBLISHED_EQUIPMENT_INVENTORY_PATH, "file")
    if not ok:
        if detail == "path contains symlink":
            detail = "stock inventory path contains symlink"
        return [CheckResult("published_equipment_delivery:inventory:path", False, detail, PUBLISHED_EQUIPMENT_INVENTORY_PATH)]
    try:
        data = load_toml(path)
    except tomllib.TOMLDecodeError as error:
        return [
            CheckResult(
                "published_equipment_delivery:inventory:toml",
                False,
                f"TOML invalid: {error.msg}",
                PUBLISHED_EQUIPMENT_INVENTORY_PATH,
            )
        ]
    schema_version = data.get("schema_version")
    if schema_version != PUBLISHED_EQUIPMENT_INVENTORY_SCHEMA_VERSION:
        return [
            CheckResult(
                "published_equipment_delivery:inventory:schema_version",
                False,
                f"schema_version must be {PUBLISHED_EQUIPMENT_INVENTORY_SCHEMA_VERSION}",
                PUBLISHED_EQUIPMENT_INVENTORY_PATH,
            )
        ]
    results: list[CheckResult] = []
    if "equipment" not in data:
        return [
            CheckResult(
                "published_equipment_delivery:equipment",
                False,
                "missing equipment",
                PUBLISHED_EQUIPMENT_INVENTORY_PATH,
            )
        ]
    equipment_records = data.get("equipment")
    if not isinstance(equipment_records, list):
        return [
            CheckResult(
                "published_equipment_delivery:equipment",
                False,
                "equipment must be a list",
                PUBLISHED_EQUIPMENT_INVENTORY_PATH,
            )
        ]
    for index, record in enumerate(equipment_records, start=1):
        if not isinstance(record, dict):
            results.append(
                CheckResult(
                    f"published_equipment_delivery:equipment:{index}",
                    False,
                    "equipment record must be a table",
                    PUBLISHED_EQUIPMENT_INVENTORY_PATH,
                )
            )
            continue
        equipment_id = record.get("id") if isinstance(record.get("id"), str) and record.get("id").strip() else str(index)
        for field in PUBLISHED_EQUIPMENT_REQUIRED_FIELDS:
            value = record.get(field)
            if not isinstance(value, str) or not value.strip():
                results.append(
                    CheckResult(
                        f"published_equipment_delivery:equipment:{equipment_id}:{field}",
                        False,
                        f"missing {field}",
                        PUBLISHED_EQUIPMENT_INVENTORY_PATH,
                    )
                )
        promotion_state = record.get("promotion_state")
        delivery_compliance = record.get("delivery_compliance")
        if (
            isinstance(promotion_state, str)
            and promotion_state.strip()
            and promotion_state not in PUBLISHED_EQUIPMENT_PROMOTION_STATES
        ):
            results.append(
                CheckResult(
                    f"published_equipment_delivery:equipment:{equipment_id}:promotion_state",
                    False,
                    "promotion_state must be a known equipment promotion state",
                    PUBLISHED_EQUIPMENT_INVENTORY_PATH,
                )
            )
        if (
            isinstance(delivery_compliance, str)
            and delivery_compliance.strip()
            and delivery_compliance not in PUBLISHED_EQUIPMENT_DELIVERY_COMPLIANCE_STATUSES
        ):
            results.append(
                CheckResult(
                    f"published_equipment_delivery:equipment:{equipment_id}:delivery_compliance",
                    False,
                    "delivery_compliance must be not_evaluated, pending, passed, or blocked",
                    PUBLISHED_EQUIPMENT_INVENTORY_PATH,
                )
            )
        elif delivery_compliance == "passed" and promotion_state != "published":
            results.append(
                CheckResult(
                    f"published_equipment_delivery:equipment:{equipment_id}:delivery_compliance",
                    False,
                    "delivery_compliance passed requires promotion_state published",
                    PUBLISHED_EQUIPMENT_INVENTORY_PATH,
                )
            )
        shop_card = record.get("shop_card")
        if isinstance(shop_card, str) and shop_card.strip():
            if not (
                shop_card.startswith(f"{PUBLISHED_EQUIPMENT_SHOP_CARD_DIR}/")
                and shop_card.endswith(".md")
            ):
                results.append(
                    CheckResult(
                        f"published_equipment_delivery:equipment:{equipment_id}:shop_card",
                        False,
                        "shop_card must be a Markdown file under docs/equipment/shop-cards/",
                        PUBLISHED_EQUIPMENT_INVENTORY_PATH,
                    )
                )
            else:
                card_ok, card_detail, _card_path = repo_relative_path_status(root, shop_card, "file")
                if not card_ok:
                    results.append(
                        CheckResult(
                            f"published_equipment_delivery:equipment:{equipment_id}:shop_card",
                            False,
                            card_detail,
                            shop_card,
                        )
                    )
        components = record.get("components", [])
        if not isinstance(components, list):
            results.append(
                CheckResult(
                    f"published_equipment_delivery:equipment:{equipment_id}:components",
                    False,
                    "components must be a list",
                    PUBLISHED_EQUIPMENT_INVENTORY_PATH,
                )
            )
            continue
        for component_index, component in enumerate(components, start=1):
            if not isinstance(component, dict):
                results.append(
                    CheckResult(
                        f"published_equipment_delivery:equipment:{equipment_id}:component:{component_index}",
                        False,
                        "component must be a table",
                        PUBLISHED_EQUIPMENT_INVENTORY_PATH,
                    )
                )
                continue
            component_name = (
                component.get("name")
                if isinstance(component.get("name"), str) and component.get("name").strip()
                else str(component_index)
            )
            for field in PUBLISHED_EQUIPMENT_COMPONENT_REQUIRED_FIELDS:
                value = component.get(field)
                valid = isinstance(value, list) if field == "paths" else isinstance(value, str) and value.strip()
                if not valid:
                    results.append(
                        CheckResult(
                            f"published_equipment_delivery:equipment:{equipment_id}:component:{component_name}:{field}",
                            False,
                            f"missing {field}",
                            PUBLISHED_EQUIPMENT_INVENTORY_PATH,
                        )
                    )
            status = component.get("status")
            if status not in PUBLISHED_EQUIPMENT_COMPONENT_STATUSES:
                results.append(
                    CheckResult(
                        f"published_equipment_delivery:equipment:{equipment_id}:component:{component_name}:status",
                        False,
                        "component status must be required, optional, planned, or unavailable",
                        PUBLISHED_EQUIPMENT_INVENTORY_PATH,
                    )
                )
            paths = component.get("paths", [])
            if not isinstance(paths, list) or not all(
                isinstance(item, str) and item.strip() for item in paths
            ):
                results.append(
                    CheckResult(
                        f"published_equipment_delivery:equipment:{equipment_id}:component:{component_name}:paths",
                        False,
                        "component paths must be a list of non-empty strings",
                        PUBLISHED_EQUIPMENT_INVENTORY_PATH,
                    )
                )
                continue
            if status == "required" and not paths:
                results.append(
                    CheckResult(
                        f"published_equipment_delivery:equipment:{equipment_id}:component:{component_name}:paths",
                        False,
                        "required components must list at least one inspectable repo path",
                        PUBLISHED_EQUIPMENT_INVENTORY_PATH,
                    )
                )
            notes = component.get("notes")
            if status in {"planned", "unavailable"} and not (isinstance(notes, str) and notes.strip()):
                results.append(
                    CheckResult(
                        f"published_equipment_delivery:equipment:{equipment_id}:component:{component_name}:notes",
                        False,
                        "planned and unavailable components must explain their status in notes",
                        PUBLISHED_EQUIPMENT_INVENTORY_PATH,
                    )
                )
            for component_path in paths:
                path_ok, path_detail, _path = repo_relative_path_status(root, component_path, "any")
                if not path_ok:
                    results.append(
                        CheckResult(
                            f"published_equipment_delivery:equipment:{equipment_id}:component:{component_name}:path:{component_path}",
                            False,
                            path_detail,
                            component_path,
                        )
                    )
    if results:
        return results
    return [
        CheckResult(
            "published_equipment_delivery:inventory",
            True,
            "valid stock inventory",
            PUBLISHED_EQUIPMENT_INVENTORY_PATH,
        )
    ]


def markdown_section_body(markdown: str, heading: str) -> str | None:
    visible = markdown_visible_text(markdown)
    pattern = re.compile(
        rf"(?ms)^## {re.escape(heading)}\s*$\n(?P<body>.*?)(?=^## |\Z)"
    )
    match = pattern.search(visible)
    if match is None:
        return None
    return match.group("body")


def markdown_bullet_items(markdown: str) -> list[str]:
    bullets: list[str] = []
    current: list[str] | None = None
    for line in markdown.splitlines():
        stripped = line.strip()
        bullet_match = re.match(r"^[-*+]\s+(?P<body>.+)$", stripped)
        if bullet_match:
            if current is not None:
                bullets.append(" ".join(current))
            current = [bullet_match.group("body")]
            continue
        if current is not None and not stripped:
            bullets.append(" ".join(current))
            current = None
            continue
        if current is not None:
            current.append(stripped)
    if current is not None:
        bullets.append(" ".join(current))
    return bullets


def markdown_record_token_present(bullet: str, value: str, *, path: bool = False) -> bool:
    if path:
        pattern = rf"(?<![\w./-])(?:\.\./)*{re.escape(value)}(?![\w./-])"
    else:
        pattern = rf"(?<![\w-]){re.escape(value)}(?![\w-])"
    return re.search(pattern, bullet) is not None


def validate_published_equipment_inventory_view(root: Path) -> list[CheckResult]:
    view_ok, view_detail, view_path = repo_relative_path_status(
        root, PUBLISHED_EQUIPMENT_INVENTORY_VIEW_PATH, "file"
    )
    if not view_ok:
        return [
            CheckResult(
                "published_equipment_inventory_view:path",
                False,
                view_detail,
                PUBLISHED_EQUIPMENT_INVENTORY_VIEW_PATH,
            )
        ]
    try:
        data = load_toml(root / PUBLISHED_EQUIPMENT_INVENTORY_PATH)
    except OSError:
        return [
            CheckResult(
                "published_equipment_inventory_view:inventory",
                False,
                "missing stock inventory",
                PUBLISHED_EQUIPMENT_INVENTORY_PATH,
            )
        ]
    except tomllib.TOMLDecodeError as error:
        return [
            CheckResult(
                "published_equipment_inventory_view:inventory",
                False,
                f"TOML invalid: {error.msg}",
                PUBLISHED_EQUIPMENT_INVENTORY_PATH,
            )
        ]

    markdown = view_path.read_text(encoding="utf-8")
    results: list[CheckResult] = []
    links = find_markdown_links(markdown)
    if "../../inventory/equipment.toml" not in links:
        results.append(
            CheckResult(
                "published_equipment_inventory_view:authority",
                False,
                "missing canonical inventory link",
                PUBLISHED_EQUIPMENT_INVENTORY_VIEW_PATH,
            )
        )
    if PUBLISHED_EQUIPMENT_INVENTORY_SCHEMA_VERSION not in markdown_visible_text(markdown):
        results.append(
            CheckResult(
                "published_equipment_inventory_view:schema_version",
                False,
                "missing stock inventory schema version",
                PUBLISHED_EQUIPMENT_INVENTORY_VIEW_PATH,
            )
        )
    if "shop-cards/README.md" not in links:
        results.append(
            CheckResult(
                "published_equipment_inventory_view:shop_cards",
                False,
                "missing shop-card index link",
                PUBLISHED_EQUIPMENT_INVENTORY_VIEW_PATH,
            )
        )

    stock_records = markdown_section_body(markdown, "Stock Records")
    if stock_records is None:
        results.append(
            CheckResult(
                "published_equipment_inventory_view:stock_records",
                False,
                "missing Stock Records section",
                PUBLISHED_EQUIPMENT_INVENTORY_VIEW_PATH,
            )
        )
        return results

    equipment_records = data.get("equipment")
    if not isinstance(equipment_records, list):
        results.append(
            CheckResult(
                "published_equipment_inventory_view:equipment",
                False,
                "equipment must be a list",
                PUBLISHED_EQUIPMENT_INVENTORY_PATH,
            )
        )
        return results

    bullets = markdown_bullet_items(stock_records)
    if not equipment_records:
        if bullets:
            results.append(
                CheckResult(
                    "published_equipment_inventory_view:empty_stock",
                    False,
                    "empty stock view must not list stock record bullets",
                    PUBLISHED_EQUIPMENT_INVENTORY_VIEW_PATH,
                )
            )
        elif stock_records.strip() != PUBLISHED_EQUIPMENT_EMPTY_STOCK_SENTENCE:
            results.append(
                CheckResult(
                    "published_equipment_inventory_view:empty_stock",
                    False,
                    "missing exact empty stock sentence",
                    PUBLISHED_EQUIPMENT_INVENTORY_VIEW_PATH,
                )
            )
    else:
        if len(bullets) != len(equipment_records):
            results.append(
                CheckResult(
                    "published_equipment_inventory_view:stock_records",
                    False,
                    "stock record bullet count must match inventory records",
                    PUBLISHED_EQUIPMENT_INVENTORY_VIEW_PATH,
                )
            )
        for index, record in enumerate(equipment_records, start=1):
            if not isinstance(record, dict):
                continue
            equipment_id = record.get("id")
            name = record.get("name")
            delivery_compliance = record.get("delivery_compliance")
            shop_card = record.get("shop_card")
            required_values = [equipment_id, name, delivery_compliance, shop_card]
            if not all(isinstance(value, str) and value.strip() for value in required_values):
                continue
            if not any(
                PUBLISHED_EQUIPMENT_EMPTY_STOCK_SENTENCE not in bullet
                and markdown_record_token_present(bullet, equipment_id)
                and markdown_record_token_present(bullet, name)
                and markdown_record_token_present(bullet, delivery_compliance)
                and markdown_record_token_present(bullet, shop_card, path=True)
                for bullet in bullets
            ):
                results.append(
                    CheckResult(
                        f"published_equipment_inventory_view:record:{equipment_id or index}",
                        False,
                        "stock record bullet must include id, name, delivery_compliance, and shop_card",
                        PUBLISHED_EQUIPMENT_INVENTORY_VIEW_PATH,
                    )
                )
    if results:
        return results
    return [
        CheckResult(
            "published_equipment_inventory_view:projection",
            True,
            "inventory view matches stock inventory",
            PUBLISHED_EQUIPMENT_INVENTORY_VIEW_PATH,
        )
    ]


def validate_published_equipment_inventory_routing(root: Path) -> list[CheckResult]:
    expected_routes = {
        "README.md": "docs/equipment/inventory.md",
        "docs/README.md": "equipment/inventory.md",
        "docs/forge-tour.md": "equipment/inventory.md",
    }
    results: list[CheckResult] = []
    for relative_path, target in expected_routes.items():
        path_ok, path_detail, path = repo_relative_path_status(root, relative_path, "file")
        if not path_ok:
            results.append(
                CheckResult(
                    f"published_equipment_inventory_view:routing:{relative_path}",
                    False,
                    path_detail,
                    relative_path,
                )
            )
            continue
        links = find_markdown_links(path.read_text(encoding="utf-8"))
        results.append(
            CheckResult(
                f"published_equipment_inventory_view:routing:{relative_path}",
                target in links,
                "inventory view route present" if target in links else "missing inventory view route",
                relative_path,
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
        *validate_toml_template_fields(
            root,
            EQUIPMENT_STOCK_RECORD_TEMPLATE_PATH,
            EQUIPMENT_STOCK_RECORD_REQUIRED_FIELDS,
        ),
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


def has_framework_example_status(markdown: str) -> bool:
    visible_markdown = markdown_visible_text(markdown)
    nonblank_lines = [line.strip() for line in visible_markdown.splitlines() if line.strip()]
    return "Status: Forge Example" in nonblank_lines[:8]


def has_example_promotion_state(markdown: str) -> bool:
    visible_markdown = markdown_visible_text(markdown)
    nonblank_lines = [line.strip() for line in visible_markdown.splitlines() if line.strip()]
    return "Promotion state: example" in nonblank_lines[:10]


def validate_examples(root: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    for example_directory in EXAMPLE_DIRECTORIES:
        for example_file in EXAMPLE_FILES:
            relative_path = f"{example_directory}/{example_file}"
            ok, detail, path = repo_relative_path_status(root, relative_path, "file")
            if not ok:
                if detail == "path contains symlink":
                    detail = "example path contains symlink"
                results.append(CheckResult(f"example:path:{relative_path}", False, detail, relative_path))
                continue
            markdown = path.read_text(encoding="utf-8")
            visible_markdown = markdown_visible_text(markdown)
            searchable_markdown = markdown_link_search_text(markdown)
            if not has_framework_example_status(markdown):
                results.append(
                    CheckResult(
                        f"example:status:{relative_path}",
                        False,
                        "missing Status: Forge Example",
                        relative_path,
                    )
                )
            if not has_example_promotion_state(markdown):
                results.append(
                    CheckResult(
                        f"example:promotion:{relative_path}",
                        False,
                        "missing Promotion state: example",
                        relative_path,
                    )
                )
            if "not Published Agent Equipment".casefold() not in visible_markdown.casefold():
                results.append(
                    CheckResult(
                        f"example:boundary:{relative_path}",
                        False,
                        "missing non-published boundary",
                        relative_path,
                    )
                )
            if "not installable".casefold() not in visible_markdown.casefold():
                results.append(
                    CheckResult(
                        f"example:boundary:{relative_path}:installable",
                        False,
                        "missing non-installable boundary",
                        relative_path,
                    )
                )
            observed_links = set(find_markdown_links(searchable_markdown))
            for required_link in EXAMPLE_TRACE_LINKS[example_file]:
                if required_link not in observed_links:
                    results.append(
                        CheckResult(
                            f"example:trace:{relative_path}:{required_link}",
                            False,
                            f"missing trace link: {required_link}",
                            relative_path,
                        )
                    )
            headings = markdown_heading_texts(markdown)
            for required_section in EXAMPLE_REQUIRED_SECTIONS.get(example_file, []):
                if normalize_reference_label(required_section) not in headings:
                    results.append(
                        CheckResult(
                            f"example:section:{relative_path}:{required_section}",
                            False,
                            f"missing section: {required_section}",
                            relative_path,
                        )
                    )
            for forbidden_claim in FORBIDDEN_EXAMPLE_CLAIMS:
                if forbidden_claim.casefold() in visible_markdown.casefold():
                    results.append(
                        CheckResult(
                            f"example:claim:{relative_path}:{forbidden_claim}",
                            False,
                            f"forbidden readiness claim: {forbidden_claim}",
                            relative_path,
                        )
                    )
    if not any(result.name.startswith("example:") and not result.ok for result in results):
        results.append(CheckResult("example:examples", True, "present", "examples"))
    return results


def effective_issue_tracker_ops_field(effective: dict, field_name: str) -> object:
    field = effective.get("effective", {}).get("issue_tracker_ops", {}).get(field_name, {})
    if isinstance(field, dict):
        return field.get("value")
    return None


def configured_issue_tracker_ops_doc_paths(effective: dict) -> list[str]:
    legacy_surfaces = effective_issue_tracker_ops_field(effective, "legacy_policy_surfaces")
    configured_paths: list[str] = []
    if isinstance(legacy_surfaces, list):
        for surface in legacy_surfaces:
            if isinstance(surface, dict) and isinstance(surface.get("path"), str):
                configured_paths.append(surface["path"])
    return unique_preserve_order([*ISSUE_TRACKER_OPS_COMPATIBILITY_DOCS, *configured_paths])


def configured_issue_tracker_ops_labels(effective: dict) -> list[str]:
    label_axes = effective_issue_tracker_ops_field(effective, "label_axes")
    labels: list[str] = []
    if not isinstance(label_axes, list):
        return labels
    for axis in label_axes:
        if not isinstance(axis, dict):
            continue
        axis_labels = axis.get("labels")
        if not isinstance(axis_labels, list):
            continue
        labels.extend(label for label in axis_labels if isinstance(label, str))
    return unique_preserve_order(labels)


def validate_issue_tracker_ops_policy_config(root: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    ok, detail, path = repo_relative_path_status(root, ISSUE_TRACKER_OPS_POLICY_CONFIG_PATH, "file")
    if not ok:
        results.append(
            CheckResult(
                f"issue_ops_policy_config:path:{ISSUE_TRACKER_OPS_POLICY_CONFIG_PATH}",
                False,
                detail,
                ISSUE_TRACKER_OPS_POLICY_CONFIG_PATH,
            )
        )
        return results

    fragment = agent_equipment_config.issue_tracker_ops_fragment()
    try:
        raw_config = load_toml(path)
        effective = agent_equipment_config.effective_config(
            [path],
            [fragment],
            requested_behavior="advisory",
        )
    except (agent_equipment_config.ConfigError, OSError, tomllib.TOMLDecodeError) as exc:
        results.append(
            CheckResult(
                f"issue_ops_policy_config:validate:{ISSUE_TRACKER_OPS_POLICY_CONFIG_PATH}",
                False,
                str(exc),
                ISSUE_TRACKER_OPS_POLICY_CONFIG_PATH,
            )
        )
        return results

    fragment_version = (
        raw_config.get("agent_equipment_config", {})
        .get("fragment_versions", {})
        .get("issue_tracker_ops")
    )
    if fragment_version != fragment.version:
        results.append(
            CheckResult(
                f"issue_ops_policy_config:version:{ISSUE_TRACKER_OPS_POLICY_CONFIG_PATH}",
                False,
                f"issue_tracker_ops fragment version must be {fragment.version}",
                ISSUE_TRACKER_OPS_POLICY_CONFIG_PATH,
            )
        )
    if effective.get("safety_status") != "usable":
        results.append(
            CheckResult(
                f"issue_ops_policy_config:safety:{ISSUE_TRACKER_OPS_POLICY_CONFIG_PATH}",
                False,
                f"safety_status={effective.get('safety_status')}",
                ISSUE_TRACKER_OPS_POLICY_CONFIG_PATH,
            )
        )
    if effective_issue_tracker_ops_field(effective, "policy_profile_status") != "authoritative":
        results.append(
            CheckResult(
                f"issue_ops_policy_config:authority:{ISSUE_TRACKER_OPS_POLICY_CONFIG_PATH}",
                False,
                "policy_profile_status must be authoritative",
                ISSUE_TRACKER_OPS_POLICY_CONFIG_PATH,
            )
        )
    if not configured_issue_tracker_ops_labels(effective):
        results.append(
            CheckResult(
                f"issue_ops_policy_config:labels:{ISSUE_TRACKER_OPS_POLICY_CONFIG_PATH}",
                False,
                "missing configured label axes",
                ISSUE_TRACKER_OPS_POLICY_CONFIG_PATH,
            )
        )

    doc_markdown: dict[str, str] = {}
    for relative_path in configured_issue_tracker_ops_doc_paths(effective):
        doc_ok, doc_detail, doc_path = repo_relative_path_status(root, relative_path, "file")
        if not doc_ok:
            results.append(CheckResult(f"issue_ops_policy_config:doc:{relative_path}:path", False, doc_detail, relative_path))
            continue
        markdown = doc_path.read_text(encoding="utf-8")
        visible_markdown = markdown_visible_text(markdown)
        normalized = " ".join(visible_markdown.casefold().split())
        doc_markdown[relative_path] = visible_markdown
        if ISSUE_TRACKER_OPS_POLICY_CONFIG_PATH not in visible_markdown or "compatibility layer" not in normalized:
            results.append(
                CheckResult(
                    f"issue_ops_policy_config:doc:{relative_path}:authority",
                    False,
                    "missing Config compatibility reference",
                    relative_path,
                )
            )

    triage_markdown = doc_markdown.get("docs/agents/triage-labels.md")
    if triage_markdown is not None:
        for label in configured_issue_tracker_ops_labels(effective):
            if label not in triage_markdown:
                results.append(
                    CheckResult(
                        f"issue_ops_policy_config:labels:docs/agents/triage-labels.md:{label}",
                        False,
                        f"missing configured label: {label}",
                        "docs/agents/triage-labels.md",
                    )
                )

    if not any(result.name.startswith("issue_ops_policy_config:") and not result.ok for result in results):
        results.append(
            CheckResult(
                "issue_ops_policy_config:config/agent-equipment.toml",
                True,
                "valid authoritative policy layer with compatible docs",
                ISSUE_TRACKER_OPS_POLICY_CONFIG_PATH,
            )
        )
    return results


def validate_issue_ops_workflow_executor(root: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    skill_ok, skill_detail, skill_path = repo_relative_path_status(
        root,
        ISSUE_OPS_WORKFLOW_EXECUTOR_SKILL_PATH,
        "file",
    )
    if not skill_ok:
        results.append(
            CheckResult(
                f"issue_ops_workflow_executor:path:{ISSUE_OPS_WORKFLOW_EXECUTOR_SKILL_PATH}",
                False,
                skill_detail,
                ISSUE_OPS_WORKFLOW_EXECUTOR_SKILL_PATH,
            )
        )
    else:
        skill_markdown = skill_path.read_text(encoding="utf-8")
        skill_frontmatter = markdown_frontmatter(skill_markdown)
        if skill_frontmatter.get("name") != "issue-ops-workflow-executor":
            results.append(
                CheckResult(
                    "issue_ops_workflow_executor:skill:frontmatter:name",
                    False,
                    "frontmatter name must be issue-ops-workflow-executor",
                    ISSUE_OPS_WORKFLOW_EXECUTOR_SKILL_PATH,
                )
            )
        skill_visible = markdown_visible_text(skill_markdown)
        for required_text in ISSUE_OPS_WORKFLOW_EXECUTOR_REQUIRED_SKILL_TEXT:
            if required_text not in skill_visible:
                results.append(
                    CheckResult(
                        f"issue_ops_workflow_executor:skill:text:{required_text}",
                        False,
                        f"missing text: {required_text}",
                        ISSUE_OPS_WORKFLOW_EXECUTOR_SKILL_PATH,
                    )
                )

    profile_ok, profile_detail, profile_path = repo_relative_path_status(
        root,
        ISSUE_OPS_WORKFLOW_EXECUTOR_PROFILE_PATH,
        "file",
    )
    if not profile_ok:
        results.append(
            CheckResult(
                f"issue_ops_workflow_executor:path:{ISSUE_OPS_WORKFLOW_EXECUTOR_PROFILE_PATH}",
                False,
                profile_detail,
                ISSUE_OPS_WORKFLOW_EXECUTOR_PROFILE_PATH,
            )
        )
    else:
        try:
            profile = load_toml(profile_path)
        except (OSError, tomllib.TOMLDecodeError) as exc:
            results.append(
                CheckResult(
                    f"issue_ops_workflow_executor:profile:toml:{ISSUE_OPS_WORKFLOW_EXECUTOR_PROFILE_PATH}",
                    False,
                    str(exc),
                    ISSUE_OPS_WORKFLOW_EXECUTOR_PROFILE_PATH,
                )
            )
            return results

        identity = profile.get("identity", {})
        tools = profile.get("tools", {})
        permissions = profile.get("permissions", {})
        config = profile.get("config", {})
        output = profile.get("output", {})
        if not isinstance(identity, dict):
            identity = {}
        if not isinstance(tools, dict):
            tools = {}
        if not isinstance(permissions, dict):
            permissions = {}
        if not isinstance(config, dict):
            config = {}
        if not isinstance(output, dict):
            output = {}

        if identity.get("name") != "issue-ops-workflow-executor":
            results.append(
                CheckResult(
                    "issue_ops_workflow_executor:profile:identity:name",
                    False,
                    "name must be issue-ops-workflow-executor",
                    ISSUE_OPS_WORKFLOW_EXECUTOR_PROFILE_PATH,
                )
            )
        if config.get("default_adapter") != "github-issues-baseline":
            results.append(
                CheckResult(
                    "issue_ops_workflow_executor:profile:default_adapter",
                    False,
                    "default_adapter must be github-issues-baseline",
                    ISSUE_OPS_WORKFLOW_EXECUTOR_PROFILE_PATH,
                )
            )
        if permissions.get("mode") != "read-only":
            results.append(
                CheckResult(
                    "issue_ops_workflow_executor:profile:permissions:mode",
                    False,
                    "mode must be read-only",
                    ISSUE_OPS_WORKFLOW_EXECUTOR_PROFILE_PATH,
                )
            )

        expected_workflow_ids = sorted(issue_tracker_core.workflow_definitions_by_id())
        if config.get("workflow_ids") != expected_workflow_ids:
            results.append(
                CheckResult(
                    "issue_ops_workflow_executor:profile:workflow_ids",
                    False,
                    "must match issue_tracker_core.workflow_definitions_by_id()",
                    ISSUE_OPS_WORKFLOW_EXECUTOR_PROFILE_PATH,
                )
            )

        allow = tools.get("allow")
        if not isinstance(allow, list):
            allow = []
        allow_strings = [item for item in allow if isinstance(item, str)]
        for required_allow in ISSUE_OPS_WORKFLOW_EXECUTOR_ALLOWED_TOOLS:
            if required_allow not in allow_strings:
                results.append(
                    CheckResult(
                        f"issue_ops_workflow_executor:profile:allow:{required_allow}",
                        False,
                        f"missing allow entry: {required_allow}",
                        ISSUE_OPS_WORKFLOW_EXECUTOR_PROFILE_PATH,
                    )
                )
        unexpected_allow = sorted(
            item for item in set(allow_strings) if item not in ISSUE_OPS_WORKFLOW_EXECUTOR_ALLOWED_TOOLS
        )
        if unexpected_allow:
            results.append(
                CheckResult(
                    "issue_ops_workflow_executor:profile:allow:unexpected",
                    False,
                    f"unexpected allow entries: {', '.join(unexpected_allow)}",
                    ISSUE_OPS_WORKFLOW_EXECUTOR_PROFILE_PATH,
                )
            )

        deny = tools.get("deny")
        if not isinstance(deny, list):
            deny = []
        deny_strings = [item for item in deny if isinstance(item, str)]
        for required_deny in ISSUE_OPS_WORKFLOW_EXECUTOR_REQUIRED_DENIES:
            if required_deny not in deny_strings:
                results.append(
                    CheckResult(
                        f"issue_ops_workflow_executor:profile:deny:{required_deny}",
                        False,
                        f"missing deny entry: {required_deny}",
                        ISSUE_OPS_WORKFLOW_EXECUTOR_PROFILE_PATH,
                    )
                )

        approvals = permissions.get("approval_required_for")
        if not isinstance(approvals, list):
            approvals = []
        approval_strings = [item for item in approvals if isinstance(item, str)]
        for required_approval in ISSUE_OPS_WORKFLOW_EXECUTOR_REQUIRED_APPROVALS:
            if required_approval not in approval_strings:
                results.append(
                    CheckResult(
                        f"issue_ops_workflow_executor:profile:approval:{required_approval}",
                        False,
                        f"missing approval entry: {required_approval}",
                        ISSUE_OPS_WORKFLOW_EXECUTOR_PROFILE_PATH,
                    )
                )

        output_contract = output.get("contract")
        if not isinstance(output_contract, str):
            output_contract = ""
        for required_output in ("candidate operation plans", "dry-run command shapes"):
            if required_output not in output_contract:
                results.append(
                    CheckResult(
                        f"issue_ops_workflow_executor:profile:output:{required_output}",
                        False,
                        f"missing output contract text: {required_output}",
                        ISSUE_OPS_WORKFLOW_EXECUTOR_PROFILE_PATH,
                    )
                )

    if not any(result.name.startswith("issue_ops_workflow_executor:") and not result.ok for result in results):
        results.append(
            CheckResult(
                "issue_ops_workflow_executor:components",
                True,
                "valid Issue Ops workflow executor skill and Agent Profile",
                "skills/issue-ops-workflow-executor",
            )
        )
    return results


def validate_specs(root: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    config_bundle_markdown_parts: list[str] = []
    ok, detail, path = repo_relative_path_status(root, ISSUE_TRACKER_OPS_CONFIG_PROFILE_PATH, "file")
    if not ok:
        if detail == "path contains symlink":
            detail = "spec path contains symlink"
        results.append(
            CheckResult(
                f"spec:path:{ISSUE_TRACKER_OPS_CONFIG_PROFILE_PATH}",
                False,
                detail,
                ISSUE_TRACKER_OPS_CONFIG_PROFILE_PATH,
            )
        )
    else:
        markdown = path.read_text(encoding="utf-8")
        visible_markdown = markdown_visible_text(markdown)
        visible_markdown_normalized = " ".join(visible_markdown.casefold().split())
        headings = markdown_heading_texts(markdown)
        if " ".join("Promotion state: planned".casefold().split()) not in visible_markdown_normalized:
            results.append(
                CheckResult(
                    f"spec:promotion:{ISSUE_TRACKER_OPS_CONFIG_PROFILE_PATH}",
                    False,
                    "missing Promotion state: planned",
                    ISSUE_TRACKER_OPS_CONFIG_PROFILE_PATH,
                )
            )
        if " ".join("does not implement Agent Equipment".casefold().split()) not in visible_markdown_normalized:
            results.append(
                CheckResult(
                    f"spec:boundary:{ISSUE_TRACKER_OPS_CONFIG_PROFILE_PATH}",
                    False,
                    "missing non-implementation boundary",
                    ISSUE_TRACKER_OPS_CONFIG_PROFILE_PATH,
                )
            )
        for required_section in ISSUE_TRACKER_OPS_CONFIG_PROFILE_REQUIRED_SECTIONS:
            if normalize_reference_label(required_section) not in headings:
                results.append(
                    CheckResult(
                        f"spec:section:{ISSUE_TRACKER_OPS_CONFIG_PROFILE_PATH}:{required_section}",
                        False,
                        f"missing section: {required_section}",
                        ISSUE_TRACKER_OPS_CONFIG_PROFILE_PATH,
                    )
                )
        for required_text in ISSUE_TRACKER_OPS_CONFIG_PROFILE_REQUIRED_TEXT:
            required_text_normalized = " ".join(required_text.casefold().split())
            if required_text_normalized not in visible_markdown_normalized:
                results.append(
                    CheckResult(
                        f"spec:text:{ISSUE_TRACKER_OPS_CONFIG_PROFILE_PATH}:{required_text}",
                        False,
                        f"missing {required_text}",
                        ISSUE_TRACKER_OPS_CONFIG_PROFILE_PATH,
                    )
                )
        for forbidden_claim in FORBIDDEN_SPEC_CLAIMS:
            if forbidden_claim.casefold() in visible_markdown.casefold():
                results.append(
                    CheckResult(
                        f"spec:claim:{ISSUE_TRACKER_OPS_CONFIG_PROFILE_PATH}:{forbidden_claim}",
                        False,
                        f"forbidden readiness claim: {forbidden_claim}",
                        ISSUE_TRACKER_OPS_CONFIG_PROFILE_PATH,
                    )
                )
    for relative_path in CONFIG_BUNDLE_REQUIRED_PATHS:
        ok, detail, path = repo_relative_path_status(root, relative_path, "file")
        if not ok:
            if detail == "path contains symlink":
                detail = "spec path contains symlink"
            results.append(CheckResult(f"spec:path:{relative_path}", False, detail, relative_path))
            continue
        markdown = path.read_text(encoding="utf-8")
        visible_markdown = markdown_visible_text(markdown)
        config_bundle_markdown_parts.append(visible_markdown)
        if "Promotion state: planned".casefold() not in visible_markdown.casefold():
            results.append(
                CheckResult(
                    f"spec:promotion:{relative_path}",
                    False,
                    "missing Promotion state: planned",
                    relative_path,
                )
            )
        if "does not implement Agent Equipment".casefold() not in visible_markdown.casefold():
            results.append(
                CheckResult(
                    f"spec:boundary:{relative_path}",
                    False,
                    "missing non-implementation boundary",
                    relative_path,
                )
            )
        for forbidden_claim in FORBIDDEN_SPEC_CLAIMS:
            if forbidden_claim.casefold() in visible_markdown.casefold():
                results.append(
                    CheckResult(
                        f"spec:claim:{relative_path}:{forbidden_claim}",
                        False,
                        f"forbidden readiness claim: {forbidden_claim}",
                        relative_path,
                    )
                )
    config_bundle_text = "\n".join(config_bundle_markdown_parts)
    if config_bundle_text:
        for required_text in CONFIG_BUNDLE_REQUIRED_TEXT:
            if required_text.casefold() not in config_bundle_text.casefold():
                results.append(
                    CheckResult(
                        f"spec:text:{CONFIG_BUNDLE_PATH}:{required_text}",
                        False,
                        f"missing {required_text}",
                        CONFIG_BUNDLE_PATH,
                    )
                )
        for forbidden_text in CONFIG_BUNDLE_FORBIDDEN_TEXT:
            if forbidden_text.casefold() in config_bundle_text.casefold():
                results.append(
                    CheckResult(
                        f"spec:text:{CONFIG_BUNDLE_PATH}:forbidden:{forbidden_text}",
                        False,
                        f"forbidden {forbidden_text}",
                        CONFIG_BUNDLE_PATH,
                    )
                )
    for relative_path in SPEC_REQUIRED_PATHS:
        ok, detail, path = repo_relative_path_status(root, relative_path, "file")
        if not ok:
            if detail == "path contains symlink":
                detail = "spec path contains symlink"
            results.append(CheckResult(f"spec:path:{relative_path}", False, detail, relative_path))
            continue
        markdown = path.read_text(encoding="utf-8")
        visible_markdown = markdown_visible_text(markdown)
        headings = markdown_heading_texts(markdown)
        if "Promotion state: specified".casefold() not in visible_markdown.casefold():
            results.append(
                CheckResult(
                    f"spec:promotion:{relative_path}",
                    False,
                    "missing Promotion state: specified",
                    relative_path,
                )
            )
        if "does not implement Agent Equipment".casefold() not in visible_markdown.casefold():
            results.append(
                CheckResult(
                    f"spec:boundary:{relative_path}",
                    False,
                    "missing non-implementation boundary",
                    relative_path,
                )
            )
        for required_section in SPEC_REQUIRED_SECTIONS:
            if normalize_reference_label(required_section) not in headings:
                results.append(
                    CheckResult(
                        f"spec:section:{relative_path}:{required_section}",
                        False,
                        f"missing section: {required_section}",
                        relative_path,
                    )
                )
        if not any(
            normalize_reference_label(section) in headings
            for section in SPEC_HARNESS_SECTION_ALTERNATIVES
        ):
            results.append(
                CheckResult(
                    f"spec:section:{relative_path}:Harness projections",
                    False,
                    "missing section: Harness projections or Harness-specific starting points",
                    relative_path,
                )
            )
        for required_text in SPEC_REQUIRED_TEXT[relative_path]:
            if required_text.casefold() not in visible_markdown.casefold():
                results.append(
                    CheckResult(
                        f"spec:text:{relative_path}:{required_text}",
                        False,
                        f"missing {required_text}",
                        relative_path,
                    )
                )
        for forbidden_claim in FORBIDDEN_SPEC_CLAIMS:
            if forbidden_claim.casefold() in visible_markdown.casefold():
                results.append(
                    CheckResult(
                        f"spec:claim:{relative_path}:{forbidden_claim}",
                        False,
                        f"forbidden readiness claim: {forbidden_claim}",
                        relative_path,
                    )
                )
    if not any(result.name.startswith("spec:") and not result.ok for result in results):
        results.append(CheckResult("spec:specs", True, "present", "specs"))
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
    payload = {
        "schema": VALIDATION_SCHEMA,
        "validation": VALIDATION_NAME,
        "forge_suite": FORGE_VALIDATION_NAME,
        "results": [asdict(result) for result in results],
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def run(root: Path, *, final_closeout: bool = False) -> list[CheckResult]:
    required_paths = [
        "README.md",
        PYTHON_VERSION_DECLARATION_PATH,
        "AGENTS.md",
        "CONTEXT.md",
        "docs/prd/forge-seed.md",
        CONFIG_PRD_PATH,
        ISSUE_TRACKER_OPS_PRD_PATH,
        EXISTING_EQUIPMENT_ONBOARDING_PRD_PATH,
        PUBLISHED_EQUIPMENT_DELIVERY_DOC_PATH,
        PUBLISHED_EQUIPMENT_INVENTORY_VIEW_PATH,
        PUBLISHED_EQUIPMENT_SHOP_CARD_INDEX_PATH,
        PUBLISHED_EQUIPMENT_INVENTORY_PATH,
        SOURCE_DISPOSITION_PATH,
        HARBOR_JIG_SOURCE_MAP_PATH,
        HARBOR_NEIGHBOR_TOOL_CATALOG_PATH,
        EXTERNAL_TOOL_EVALUATION_PATH,
        HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH,
        SKILL_EVAL_METHODOLOGY_SOURCE_INTAKE_PATH,
        PLUGIN_CREATOR_SOURCE_INTAKE_PATH,
        THREAT_MODEL_PATH,
        ISSUE_TRACKER_OPS_POLICY_CONFIG_PATH,
        DOCUMENTATION_CLOSEOUT_PATH,
        SECURITY_CLOSEOUT_PATH,
        PROJECTION_DRAFTS_PATH,
        "docs/forge-tour.md",
        *CANONICAL_DOC_REQUIRED_SECTIONS,
        *TEMPLATE_REQUIRED_PATHS,
        *EXAMPLE_REQUIRED_PATHS,
        *CONFIG_BUNDLE_REQUIRED_PATHS,
        ISSUE_TRACKER_OPS_CONFIG_PROFILE_PATH,
        *SPEC_REQUIRED_PATHS,
    ]
    results = [
        *validate_required_paths(root, required_paths),
        *validate_python_runtime_declaration(root),
        *validate_forge_routes(root),
        *validate_context(root),
        *validate_canonical_docs(root),
        *validate_threat_model(root),
        *validate_documentation_closeout(root),
        *validate_security_closeout(root),
        *validate_projection_drafts(root),
        *validate_harness_catalog(root),
        *validate_templates(root),
        *validate_published_equipment_delivery(root),
        *validate_published_equipment_inventory_view(root),
        *validate_published_equipment_inventory_routing(root),
        *validate_examples(root),
        *validate_specs(root),
        *validate_issue_ops_workflow_executor(root),
        *validate_issue_tracker_ops_policy_config(root),
        *validate_markdown_links(root),
    ]
    results.extend(validate_source_disposition(root))
    results.extend(validate_harbor_jig_source_map(root))
    results.extend(validate_harbor_neighbor_tool_catalog(root))
    results.extend(validate_external_tool_evaluation(root))
    results.extend(validate_harbor_external_tool_evaluation_record(root))
    results.extend(validate_skill_eval_methodology_source_intake(root))
    results.extend(validate_plugin_creator_source_intake(root))
    results.extend(validate_source_retired_tree(root, include_disposition=False))
    results.extend(validate_final_source_retired_stamp(root))
    if final_closeout:
        results.extend(validate_final_closeout(root))
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Agent Armory Integrity.",
        epilog="Armory Integrity Validation includes the Forge Integrity Validation suite and equipment-candidate shape checks. Equipment-specific behavior validation belongs to the named equipment validator.",
    )
    parser.add_argument("--root", default=".", help="Repository root to validate.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument(
        "--final-closeout",
        action="store_true",
        help="Require final closeout evidence before branch push or external projection.",
    )
    args = parser.parse_args(argv)

    results = run(Path(args.root).resolve(), final_closeout=args.final_closeout)
    output = render_json(results) if args.json else render_human(results)
    print(output)
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    sys.exit(main())
