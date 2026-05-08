#!/usr/bin/env python3.14
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


AGGREGATE_CATALOG_PATH = Path("docs/harness-capabilities.toml")
HARNESS_CAPABILITIES_SUMMARY_PATH = Path("docs/harness-capabilities.md")
VANILLA_PROFILE_DIR = Path("docs/harness-capabilities/vanilla")
PROFILE_SCHEMA_VERSION = "vanilla-harness-capability-profile.v1alpha1"
PROFILE_KIND = "vanilla_harness_capability_profile"
PROFILE_SCOPE_SURFACE = "vanilla_harness_capability_surface"
PROFILE_SCOPE_APPLICABILITY = "Default settings and default equipment immediately after installation and onboarding."
CLAIM_APPLICABILITY_SCOPE = "vanilla harness after default installation and onboarding"
CLAIM_CAPABILITY_ORIGIN = "migrated aggregate harness catalog"
CLAIM_MIGRATION_STATUS = "migrated_from_aggregate"
CLAIM_EVIDENCE_BASIS = "aggregate_catalog_migration"

REQUIRED_HARNESSES = [
    "codex",
    "claude_code",
    "cursor",
    "hermes_agent",
    "opencode",
    "openclaw",
]

SURFACE_FAMILIES = [
    "instructions_context",
    "skills",
    "mcp_tools",
    "hooks_events",
    "plugins_bundles",
    "agent_profiles_subagents",
    "memory_context_retrieval",
    "config_settings",
    "permissions_approvals_sandboxing",
    "scheduling_automation",
    "commands_shortcuts",
    "providers_connectors",
    "runtime_modes",
    "cross_harness_import_compatibility",
    "lifecycle_reload_update",
]

FAMILY_KEYWORDS = {
    "instructions_context": ["instruction", "rules", "agents.md"],
    "skills": ["skill"],
    "mcp_tools": ["mcp", "tool"],
    "hooks_events": ["hook", "webhook", "trigger", "event"],
    "plugins_bundles": ["plugin", "bundle"],
    "agent_profiles_subagents": ["profile", "subagent", "agent", "delegation"],
    "memory_context_retrieval": ["memory", "context provider", "retrieval", "persisted goals"],
    "config_settings": ["config", "settings", "permission"],
    "permissions_approvals_sandboxing": ["permission", "approval", "sandbox"],
    "scheduling_automation": ["schedule", "scheduling", "automation", "cron", "routine", "task", "heartbeat"],
    "commands_shortcuts": ["command", "slash"],
    "providers_connectors": ["provider", "connector", "gateway", "channel"],
    "runtime_modes": ["desktop", "web mode", "server mode", "run", "exec", "tui", "terminal", "noninteractive"],
    "cross_harness_import_compatibility": ["compatible", "import", "codex", "claude", "cursor", "ecosystem"],
    "lifecycle_reload_update": ["reload", "restart", "refresh", "update", "install"],
}

MIGRATION_RESULT_SCHEMA = "harness_capability_profiles.migrate_result.v1"
SUMMARY_RESULT_SCHEMA = "harness_capability_profiles.summary_result.v1"
VALIDATION_RESULT_SCHEMA = "harness_capability_profiles.validation_result.v1"
VALIDATION_NAME = "Vanilla Harness Capability Profile Manager Core"
SUMMARY_SOURCE_LIMIT = 6
CLAIM_STATUSES = {"supported", "unsupported", "unknown", "not-applicable"}
SOURCE_KINDS = {"first_party", "third_party_fallback"}
EVIDENCE_CATEGORIES = {
    "documentation-supported",
    "source-supported",
    "implementation inference",
    "practitioner wisdom",
    "hypothesis",
}


class ManagerError(Exception):
    pass


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    detail: str
    path: str


def repo_path(root: Path, relative: Path) -> Path:
    return root / relative


def invalid_relative_path(relative: Path) -> bool:
    return relative.is_absolute() or ".." in relative.parts


def path_status(root: Path, relative: Path, *, expected_kind: str | None = None) -> tuple[bool, str, Path]:
    if invalid_relative_path(relative):
        return False, "path invalid", root / relative
    candidate = root / relative
    current = root
    parts_to_check = relative.parts if expected_kind in {"file", "dir"} else relative.parent.parts
    for part in parts_to_check:
        current = current / part
        if current.is_symlink():
            return False, "path contains symlink", candidate
    try:
        root_resolved = root.resolve(strict=True)
    except OSError:
        return False, "repository root missing", candidate
    try:
        if candidate.exists():
            candidate_resolved = candidate.resolve(strict=True)
        else:
            candidate_resolved = candidate.parent.resolve(strict=True) / candidate.name
    except OSError:
        return False, "missing", candidate
    try:
        candidate_resolved.relative_to(root_resolved)
    except ValueError:
        return False, "path escapes repository root", candidate
    if expected_kind == "file" and not candidate.is_file():
        return False, "not a file", candidate
    if expected_kind == "dir" and not candidate.is_dir():
        return False, "not a directory", candidate
    return True, "ok", candidate


def checked_read_file(root: Path, relative: Path) -> Path:
    ok, detail, path = path_status(root, relative, expected_kind="file")
    if not ok:
        raise ManagerError(f"{relative.as_posix()}: {detail}")
    return path


def checked_write_file(root: Path, relative: Path) -> Path:
    if invalid_relative_path(relative):
        raise ManagerError(f"{relative.as_posix()}: path invalid")
    path = root / relative
    try:
        root_resolved = root.resolve(strict=True)
    except OSError as error:
        raise ManagerError(f"{relative.as_posix()}: repository root missing") from error
    current = root
    for part in relative.parent.parts:
        current = current / part
        if current.exists():
            if current.is_symlink():
                raise ManagerError(f"{relative.as_posix()}: path contains symlink")
            try:
                current.resolve(strict=True).relative_to(root_resolved)
            except (OSError, ValueError) as error:
                raise ManagerError(f"{relative.as_posix()}: path escapes repository root") from error
        else:
            break
    if path.exists() and path.is_symlink():
        raise ManagerError(f"{relative.as_posix()}: path contains symlink")
    return path


def load_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def slug(value: str, *, limit: int = 36) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return (normalized or "entry")[:limit].strip("-") or "entry"


def stable_suffix(*parts: str) -> str:
    digest = hashlib.sha256("\0".join(parts).encode("utf-8")).hexdigest()
    return digest[:10]


def evidence_id(harness_id: str, source: dict[str, Any]) -> str:
    scope = str(source.get("claim_scope", "source"))
    url = str(source.get("url", ""))
    return f"ev-{harness_id}-{slug(scope, limit=32)}-{stable_suffix(url, scope)}"


def claim_id(harness_id: str, family: str) -> str:
    return f"claim-{harness_id}-{family}"


def family_evidence_ids(
    family: str,
    sources: list[dict[str, Any]],
    evidence_ids: list[str],
) -> list[str]:
    keywords = FAMILY_KEYWORDS[family]
    matched_indexes = [
        index
        for index, source in enumerate(sources)
        if any(keyword in str(source.get("claim_scope", "")).casefold() for keyword in keywords)
    ]
    if matched_indexes:
        return [evidence_ids[index] for index in matched_indexes]
    return []


def family_status(matched_evidence_ids: list[str]) -> str:
    if matched_evidence_ids:
        return "supported"
    return "unknown"


def profile_from_aggregate(harness_id: str, checked_at: str, entry: dict[str, Any]) -> dict[str, Any]:
    sources = entry.get("sources", [])
    source_ids = [evidence_id(harness_id, source) for source in sources]
    components = list(entry.get("components", []))
    scheduling = str(entry.get("scheduling", ""))
    uncertainty = str(entry.get("uncertainty", ""))
    limitations = str(entry.get("limitations", ""))
    evidence_records = [
        {
            "id": source_ids[index],
            "category": entry.get("evidence", ""),
            "source_kind": source.get("kind", ""),
            "url": source.get("url", ""),
            "claim_scope": source.get("claim_scope", ""),
        }
        for index, source in enumerate(sources)
    ]
    claims: list[dict[str, Any]] = []
    for family in SURFACE_FAMILIES:
        matched_evidence = family_evidence_ids(family, sources, source_ids)
        status = family_status(matched_evidence)
        if status == "supported":
            statement = f"Source-backed evidence records {family.replace('_', ' ')} support."
        else:
            statement = f"Source-backed evidence does not prove {family.replace('_', ' ')} support."
        claims.append(
            {
                "id": claim_id(harness_id, family),
                "family": family,
                "status": status,
                "statement": statement,
                "evidence_ids": matched_evidence,
                "applicability_scope": CLAIM_APPLICABILITY_SCOPE,
                "capability_origin": CLAIM_CAPABILITY_ORIGIN,
                "migration_status": CLAIM_MIGRATION_STATUS,
                "evidence_basis": CLAIM_EVIDENCE_BASIS,
                "limitations": limitations if status == "supported" else "No migrated aggregate row proves this surface family.",
                "uncertainty": uncertainty,
            }
        )
    return {
        "schema_version": PROFILE_SCHEMA_VERSION,
        "profile_kind": PROFILE_KIND,
        "harness_id": harness_id,
        "display_name": entry.get("display_name", ""),
        "checked_at": checked_at,
        "checked_version": entry.get("checked_version", ""),
        "version_basis": entry.get("version_basis", ""),
        "evidence_category": entry.get("evidence", ""),
        "summary_scheduling": entry.get("summary_scheduling", ""),
        "scheduling": scheduling,
        "limitations": limitations,
        "uncertainty": uncertainty,
        "refresh_notes": entry.get("refresh_notes", ""),
        "components": components,
        "local_observations": list(entry.get("local_observations", [])),
        "scope": {
            "surface": PROFILE_SCOPE_SURFACE,
            "applicability": PROFILE_SCOPE_APPLICABILITY,
        },
        "evidence": evidence_records,
        "claim": claims,
    }


def toml_quote(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def toml_value(value: Any) -> str:
    if isinstance(value, str):
        return toml_quote(value)
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        return "[" + ", ".join(toml_value(item) for item in value) + "]"
    raise TypeError(f"unsupported TOML value: {value!r}")


def render_table(lines: list[str], values: dict[str, Any], keys: list[str]) -> None:
    for key in keys:
        lines.append(f"{key} = {toml_value(values.get(key, ''))}")


def render_profile(profile: dict[str, Any]) -> str:
    lines: list[str] = []
    render_table(
        lines,
        profile,
        [
            "schema_version",
            "profile_kind",
            "harness_id",
            "display_name",
            "checked_at",
            "checked_version",
            "version_basis",
            "evidence_category",
            "summary_scheduling",
            "scheduling",
            "limitations",
            "uncertainty",
            "refresh_notes",
            "components",
            "local_observations",
        ],
    )
    lines.append("")
    lines.append("[scope]")
    render_table(lines, profile["scope"], ["surface", "applicability"])
    for evidence in profile["evidence"]:
        lines.append("")
        lines.append("[[evidence]]")
        render_table(lines, evidence, ["id", "category", "source_kind", "url", "claim_scope"])
    for claim in profile["claim"]:
        lines.append("")
        lines.append("[[claim]]")
        render_table(
            lines,
            claim,
            [
                "id",
                "family",
                "status",
                "statement",
                "evidence_ids",
                "applicability_scope",
                "capability_origin",
                "migration_status",
                "evidence_basis",
                "limitations",
                "uncertainty",
            ],
        )
    return "\n".join(lines) + "\n"


def migration_writes(root: Path) -> list[dict[str, str]]:
    try:
        catalog = load_toml(checked_read_file(root, AGGREGATE_CATALOG_PATH))
    except tomllib.TOMLDecodeError as error:
        raise ManagerError(f"{AGGREGATE_CATALOG_PATH.as_posix()}: TOML invalid: {error.msg}") from error
    checked_at = str(catalog.get("checked_at", ""))
    if not checked_at:
        raise ManagerError("aggregate catalog missing checked_at")
    harnesses = catalog.get("harness", {})
    if not isinstance(harnesses, dict):
        raise ManagerError("aggregate catalog missing harness table")
    writes = []
    for harness_id in sorted(REQUIRED_HARNESSES):
        entry = harnesses.get(harness_id)
        if not isinstance(entry, dict):
            raise ManagerError(f"aggregate catalog missing required harness: {harness_id}")
        profile = profile_from_aggregate(harness_id, checked_at, entry)
        path = VANILLA_PROFILE_DIR / f"{harness_id}.toml"
        failures = [result for result in validate_profile_data(profile, harness_id, path) if not result.ok]
        if failures:
            failure = failures[0]
            raise ManagerError(f"generated profile invalid for {harness_id}: {failure.name}: {failure.detail}")
        writes.append({"path": path.as_posix(), "content": render_profile(profile)})
    return writes


def migrate(root: Path, *, apply: bool) -> dict[str, Any]:
    writes = migration_writes(root)
    if apply:
        checked_paths = [checked_write_file(root, Path(write["path"])) for write in writes]
        for index, write in enumerate(writes):
            path = checked_paths[index]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(write["content"], encoding="utf-8")
        aggregate = repo_path(root, AGGREGATE_CATALOG_PATH)
        if aggregate.exists():
            aggregate.unlink()
    return {
        "schema": MIGRATION_RESULT_SCHEMA,
        "result": "wrote" if apply else "would_write",
        "dry_run": not apply,
        "writes": [{"path": write["path"], "sha256": hashlib.sha256(write["content"].encode("utf-8")).hexdigest()} for write in writes],
    }


def profile_path(harness_id: str) -> Path:
    return VANILLA_PROFILE_DIR / f"{harness_id}.toml"


def load_profile(root: Path, harness_id: str) -> dict[str, Any]:
    return load_toml(checked_read_file(root, profile_path(harness_id)))


def load_profiles(root: Path) -> list[dict[str, Any]]:
    return [load_profile(root, harness_id) for harness_id in REQUIRED_HARNESSES]


def non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def string_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def validate_profile_data(profile: dict[str, Any], harness_id: str, relative_path: Path) -> list[CheckResult]:
    results: list[CheckResult] = []

    required_scalars = {
        "schema_version": PROFILE_SCHEMA_VERSION,
        "profile_kind": PROFILE_KIND,
        "harness_id": harness_id,
    }
    for field, expected in required_scalars.items():
        value = profile.get(field)
        if value != expected:
            results.append(CheckResult(f"profile:{harness_id}:{field}", False, f"must be {expected}", relative_path.as_posix()))
    for field in [
        "display_name",
        "checked_at",
        "checked_version",
        "version_basis",
        "evidence_category",
        "summary_scheduling",
        "scheduling",
        "limitations",
        "uncertainty",
        "refresh_notes",
    ]:
        if not non_empty_string(profile.get(field)):
            results.append(CheckResult(f"profile:{harness_id}:{field}", False, f"missing {field}", relative_path.as_posix()))
    if non_empty_string(profile.get("evidence_category")) and profile.get("evidence_category") not in EVIDENCE_CATEGORIES:
        results.append(CheckResult(f"profile:{harness_id}:evidence_category", False, "invalid evidence category", relative_path.as_posix()))
    if not string_list(profile.get("components")):
        results.append(CheckResult(f"profile:{harness_id}:components", False, "components must be a list of strings", relative_path.as_posix()))
    if not string_list(profile.get("local_observations")):
        results.append(
            CheckResult(f"profile:{harness_id}:local_observations", False, "local_observations must be a list of strings", relative_path.as_posix())
        )

    scope = profile.get("scope")
    if not isinstance(scope, dict) or scope.get("surface") != PROFILE_SCOPE_SURFACE:
        results.append(CheckResult(f"profile:{harness_id}:scope", False, "scope must describe vanilla harness surface", relative_path.as_posix()))
    elif scope.get("applicability") != PROFILE_SCOPE_APPLICABILITY:
        results.append(CheckResult(f"profile:{harness_id}:scope:applicability", False, "scope applicability must match vanilla profile default", relative_path.as_posix()))

    evidence = profile.get("evidence")
    evidence_ids: set[str] = set()
    if not isinstance(evidence, list) or not evidence:
        results.append(CheckResult(f"profile:{harness_id}:evidence", False, "evidence must be non-empty", relative_path.as_posix()))
    else:
        for index, record in enumerate(evidence):
            if not isinstance(record, dict):
                results.append(CheckResult(f"profile:{harness_id}:evidence:{index}", False, "evidence must be a table", relative_path.as_posix()))
                continue
            evidence_id_value = record.get("id")
            if not non_empty_string(evidence_id_value):
                results.append(CheckResult(f"profile:{harness_id}:evidence:{index}:id", False, "missing evidence id", relative_path.as_posix()))
            elif evidence_id_value in evidence_ids:
                results.append(CheckResult(f"profile:{harness_id}:evidence:{evidence_id_value}", False, "duplicate evidence id", relative_path.as_posix()))
            elif evidence_id_value != evidence_id(harness_id, record):
                results.append(CheckResult(f"profile:{harness_id}:evidence:{index}:id", False, "unstable evidence id", relative_path.as_posix()))
            else:
                evidence_ids.add(evidence_id_value)
            for field in ["category", "source_kind", "url", "claim_scope"]:
                if not non_empty_string(record.get(field)):
                    results.append(CheckResult(f"profile:{harness_id}:evidence:{index}:{field}", False, f"missing {field}", relative_path.as_posix()))
            category = record.get("category")
            if non_empty_string(category) and category not in EVIDENCE_CATEGORIES:
                results.append(CheckResult(f"profile:{harness_id}:evidence:{index}:category", False, "invalid evidence category", relative_path.as_posix()))
            source_kind = record.get("source_kind")
            if non_empty_string(source_kind) and source_kind not in SOURCE_KINDS:
                results.append(CheckResult(f"profile:{harness_id}:evidence:{index}:source_kind", False, "invalid source kind", relative_path.as_posix()))
            url = record.get("url")
            if non_empty_string(url):
                parsed_url = urlparse(url)
                if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
                    results.append(
                        CheckResult(
                            f"profile:{harness_id}:evidence:{index}:url",
                            False,
                            "source url must be http or https with a host",
                            relative_path.as_posix(),
                        )
                    )

    claims = profile.get("claim")
    claim_ids: set[str] = set()
    families: set[str] = set()
    if not isinstance(claims, list) or not claims:
        results.append(CheckResult(f"profile:{harness_id}:claim", False, "claims must be non-empty", relative_path.as_posix()))
    else:
        for index, claim in enumerate(claims):
            if not isinstance(claim, dict):
                results.append(CheckResult(f"profile:{harness_id}:claim:{index}", False, "claim must be a table", relative_path.as_posix()))
                continue
            claim_id_value = claim.get("id")
            family = claim.get("family")
            if not non_empty_string(claim_id_value):
                results.append(CheckResult(f"profile:{harness_id}:claim:{index}:id", False, "missing claim id", relative_path.as_posix()))
            elif claim_id_value in claim_ids:
                results.append(CheckResult(f"profile:{harness_id}:claim:{claim_id_value}", False, "duplicate claim id", relative_path.as_posix()))
            else:
                claim_ids.add(claim_id_value)
            if family not in SURFACE_FAMILIES:
                results.append(CheckResult(f"profile:{harness_id}:claim:{index}:family", False, "invalid family", relative_path.as_posix()))
            else:
                families.add(family)
                if non_empty_string(claim_id_value) and claim_id_value != claim_id(harness_id, family):
                    results.append(CheckResult(f"profile:{harness_id}:claim:{family}:id", False, "unstable claim id", relative_path.as_posix()))
            status = claim.get("status")
            if status not in CLAIM_STATUSES:
                results.append(CheckResult(f"profile:{harness_id}:claim:{index}:status", False, "invalid claim status", relative_path.as_posix()))
            refs = claim.get("evidence_ids")
            if not isinstance(refs, list) or not all(isinstance(ref, str) for ref in refs):
                results.append(CheckResult(f"profile:{harness_id}:claim:{index}:evidence_ids", False, "evidence_ids must be a list of strings", relative_path.as_posix()))
                refs = []
            missing_refs = [ref for ref in refs if ref not in evidence_ids]
            if missing_refs:
                results.append(
                    CheckResult(
                        f"profile:{harness_id}:claim:{index}:evidence_refs",
                        False,
                        f"unknown evidence ids: {', '.join(missing_refs)}",
                        relative_path.as_posix(),
                    )
                )
            if status == "supported" and not refs:
                results.append(CheckResult(f"profile:{harness_id}:claim:{index}:evidence_refs", False, "supported claim needs evidence", relative_path.as_posix()))
            expected_claim_values = {
                "applicability_scope": CLAIM_APPLICABILITY_SCOPE,
                "capability_origin": CLAIM_CAPABILITY_ORIGIN,
                "migration_status": CLAIM_MIGRATION_STATUS,
                "evidence_basis": CLAIM_EVIDENCE_BASIS,
            }
            for field, expected in expected_claim_values.items():
                if claim.get(field) != expected:
                    results.append(CheckResult(f"profile:{harness_id}:claim:{index}:{field}", False, f"must be {expected}", relative_path.as_posix()))
            if not non_empty_string(claim.get("limitations")) and not non_empty_string(claim.get("uncertainty")):
                results.append(
                    CheckResult(
                        f"profile:{harness_id}:claim:{index}:limits",
                        False,
                        "claim needs limitations or uncertainty",
                        relative_path.as_posix(),
                    )
                )
    missing_families = [family for family in SURFACE_FAMILIES if family not in families]
    if missing_families:
        results.append(
            CheckResult(f"profile:{harness_id}:surface_family_coverage", False, f"missing families: {', '.join(missing_families)}", relative_path.as_posix())
        )
    if not any(not result.ok for result in results):
        results.append(CheckResult(f"profile:{harness_id}", True, "valid", relative_path.as_posix()))
    return results


def validate_profile(root: Path, harness_id: str) -> list[CheckResult]:
    relative_path = profile_path(harness_id)
    ok, detail, path = path_status(root, relative_path, expected_kind="file")
    if not ok:
        return [CheckResult(f"profile:{harness_id}:path", False, detail if detail != "not a file" else "missing profile", relative_path.as_posix())]
    try:
        profile = load_toml(path)
    except tomllib.TOMLDecodeError as error:
        return [CheckResult(f"profile:{harness_id}:toml", False, f"TOML invalid: {error.msg}", relative_path.as_posix())]
    return validate_profile_data(profile, harness_id, relative_path)


def markdown_table_rows(markdown: str, heading: str) -> list[dict[str, str]]:
    lines = markdown.splitlines()
    start_index = None
    for index, line in enumerate(lines):
        if line.strip() == heading:
            start_index = index + 1
            break
    if start_index is None:
        return []
    table_lines: list[str] = []
    for line in lines[start_index:]:
        if table_lines and not line.startswith("|"):
            break
        if line.startswith("|"):
            table_lines.append(line)
    if len(table_lines) < 2:
        return []
    headers = [cell.strip() for cell in table_lines[0].strip("|").split("|")]
    rows = []
    for line in table_lines[2:]:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) == len(headers):
            rows.append(dict(zip(headers, cells, strict=True)))
    return rows


def validate_summary(root: Path) -> list[CheckResult]:
    relative_path = HARNESS_CAPABILITIES_SUMMARY_PATH
    ok, detail, path = path_status(root, relative_path, expected_kind="file")
    if not ok:
        return [
            CheckResult(
                "summary:path",
                False,
                detail if detail != "not a file" else "missing harness capability summary",
                relative_path.as_posix(),
            )
        ]
    markdown = path.read_text(encoding="utf-8")
    results: list[CheckResult] = []
    try:
        rendered_summary = render_summary(load_profiles(root))
    except (ManagerError, tomllib.TOMLDecodeError, KeyError, TypeError) as error:
        return [
            CheckResult(
                "summary:profiles",
                False,
                f"cannot render summary from profiles: {error.__class__.__name__}: {error}",
                relative_path.as_posix(),
            )
        ]
    if markdown != rendered_summary:
        results.append(CheckResult("summary:rendered", False, "summary differs from manager-rendered output", relative_path.as_posix()))
    rows = {row.get("Harness", ""): row for row in markdown_table_rows(markdown, "## Harness matrix")}
    for harness_id in REQUIRED_HARNESSES:
        profile_ok, _, _ = path_status(root, profile_path(harness_id), expected_kind="file")
        if not profile_ok:
            continue
        profile = load_profile(root, harness_id)
        display_name = profile.get("display_name", "")
        row = rows.get(display_name)
        if row is None:
            results.append(CheckResult(f"summary:{harness_id}:display_name", False, f"missing matrix row: {display_name}", relative_path.as_posix()))
            continue
        expected = {
            "checked_version": ("Checked version", profile.get("checked_version", "")),
            "evidence_category": ("Evidence", profile.get("evidence_category", "")),
            "summary_scheduling": ("Scheduling posture", profile.get("summary_scheduling", "")),
        }
        for field, (column, expected_value) in expected.items():
            if non_empty_string(expected_value) and row.get(column) != expected_value:
                results.append(
                    CheckResult(
                        f"summary:{harness_id}:{field}",
                        False,
                        f"markdown matrix {column} mismatch: expected {expected_value}",
                        relative_path.as_posix(),
                    )
                )
    if "docs/harness-capabilities.toml" in markdown or "harness-capabilities.toml" in markdown:
        results.append(CheckResult("summary:aggregate_reference", False, "summary must point to per-harness profiles", relative_path.as_posix()))
    if not any(not result.ok for result in results):
        results.append(CheckResult("summary:harness-capabilities", True, "aligned", relative_path.as_posix()))
    return results


def validate(root: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    if repo_path(root, AGGREGATE_CATALOG_PATH).exists():
        results.append(CheckResult("aggregate_catalog:retired", False, "aggregate catalog must not remain authored truth", AGGREGATE_CATALOG_PATH.as_posix()))
    for harness_id in sorted(REQUIRED_HARNESSES):
        results.extend(validate_profile(root, harness_id))
    results.extend(validate_summary(root))
    return results


def validation_payload(results: list[CheckResult]) -> dict[str, Any]:
    return {
        "schema": VALIDATION_RESULT_SCHEMA,
        "validation": VALIDATION_NAME,
        "result": "passed" if all(result.ok for result in results) else "failed",
        "results": [asdict(result) for result in results],
    }


def source_lines(profile: dict[str, Any], max_sources: int = SUMMARY_SOURCE_LIMIT) -> list[str]:
    lines = []
    # Keep the human catalog concise while leaving full evidence in the TOML profiles.
    for evidence in profile.get("evidence", [])[:max_sources]:
        scope = evidence.get("claim_scope", "source")
        url = evidence.get("url", "")
        lines.append(f"- [{scope}]({url})")
    return lines


def render_summary(profiles: list[dict[str, Any]]) -> str:
    by_id = {profile["harness_id"]: profile for profile in profiles}
    ordered_profiles = [by_id[harness_id] for harness_id in REQUIRED_HARNESSES]
    checked_at_values = sorted({profile["checked_at"] for profile in ordered_profiles})
    checked_at_summary = checked_at_values[0] if len(checked_at_values) == 1 else f"{checked_at_values[0]} to {checked_at_values[-1]}"
    lines = [
        "# Harness Capability Catalog",
        "",
        "Status: Forge Canon",
        "",
        "This catalog is the human-facing front door for source-backed Vanilla Harness Capability Profiles that Smiths may use when designing Agent Equipment. Harness capabilities move quickly, so each profile states when its facts were checked, what source supports them, and what remains uncertain.",
        "",
        "The structured source of truth is `docs/harness-capabilities/vanilla/`. Each supported harness has one per-harness Vanilla Harness Capability Profile. This Markdown document summarizes the validated profiles for humans and Agents.",
        "",
        "The first-slice schema reference is [Vanilla Harness Capability Profile v1alpha1](harness-capabilities/schema/vanilla-profile-v1alpha1.md).",
        "",
        "## Catalog policy",
        "",
        "Use this catalog before making harness-specific claims in Forge Canon, Equipment Blueprints, templates, examples, or equipment implementation plans.",
        "",
        "Treat every profile as versioned state. A Smith must refresh the relevant harness profile before relying on recently changed scheduling, hook, plugin, MCP, permission, or Agent Profile behavior. Record local CLI observations separately from public source facts.",
        "",
        "Use first-party sources where available. Use third-party fallback metadata only when first-party evidence is unavailable or clearly insufficient, and label it as fallback evidence in the profile's source, uncertainty, or refresh notes.",
        "",
        "## Refresh summary",
        "",
        f"Checked at: {checked_at_summary}.",
        "",
        "The profiles preserve source-backed version, component, scheduling, limitation, uncertainty, refresh-note, and local-observation fields. No local harness binaries, workspace configs, gateways, plugin installs, cloud agents, or automation state were inspected during the migrated seed refresh.",
        "",
        "Documentation indexes can lag behind current release evidence. For version anchors, prefer GitHub releases or official changelogs over generated indexes or secondary metadata.",
        "",
        "## Harness matrix",
        "",
        "| Harness | Profile | Version basis | Checked version | Evidence | Scheduling posture |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for profile in ordered_profiles:
        profile_link = f"[{profile['display_name']} profile](harness-capabilities/vanilla/{profile['harness_id']}.toml)"
        lines.append(
            f"| {profile['display_name']} | {profile_link} | {profile['version_basis']} | {profile['checked_version']} | {profile['evidence_category']} | {profile['summary_scheduling']} |"
        )
    lines.extend(["", "## Harness notes", ""])
    for profile in ordered_profiles:
        lines.extend(
            [
                f"### {profile['display_name']}",
                "",
                f"The [{profile['display_name']} profile](harness-capabilities/vanilla/{profile['harness_id']}.toml) preserves source-backed component, scheduling, limitation, uncertainty, refresh-note, source, and local-observation records.",
                "",
                f"Scheduling support: {profile['summary_scheduling']}",
                "",
                f"Limitations: {profile['limitations']}",
                "",
                "Key sources:",
                "",
                *source_lines(profile, max_sources=SUMMARY_SOURCE_LIMIT),
                "",
            ]
        )
    lines.extend(
        [
            "## Periodic Actions projection order",
            "",
            "For each harness, choose the first available mechanism that satisfies the desired autonomy, visibility, control, and durability:",
            "",
            "1. Native durable scheduler or automation.",
            "2. Native local scheduled task.",
            "3. Active loop or heartbeat.",
            "4. Suitable hook.",
            "5. Inference-driven pre/post task check.",
            "",
            "Recommended starting choices:",
            "",
            "| Harness | Projection order |",
            "| --- | --- |",
            "| OpenClaw | cron, heartbeat, hooks, then rules or equivalent instructions. |",
            "| Hermes Agent | cron, plugin or gateway hooks, then rules or equivalent instructions. |",
            "| Claude Code | Routines or Desktop scheduled tasks, session scheduled tasks, hooks, then rules or equivalent instructions. |",
            "| Cursor | Automations or background agents, then rules or hooks after verification. |",
            "| Codex | app automations or external schedulers around `codex exec`, then hooks, then rules or equivalent instructions. |",
            "| OpenCode | GitHub Actions cron or external scheduler around `opencode run`, then plugin hooks, then rules or equivalent instructions. |",
            "",
            "## Refresh requirement",
            "",
            "The catalog is versioned state, not timeless documentation. Refresh the affected harness profile when:",
            "",
            "- a Smith spec or implementation depends on a harness capability listed here;",
            "- the source's release or changelog has moved since the checked-at timestamp;",
            "- a capability is marked experimental, preview-like, prerelease, plan-dependent, or locally unobserved;",
            "- local installation state can materially differ from public documentation;",
            "- a downstream change needs a hard security, scheduling, hook, MCP, or plugin claim.",
            "",
            "At minimum, a refreshed profile records version, version basis, checked-at timestamp, first-party sources, evidence category, component support, scheduling support, limitations, uncertainty, and local observations when local state was inspected.",
            "",
        ]
    )
    return "\n".join(lines)


def summarize(root: Path, *, write: bool) -> dict[str, Any]:
    content = render_summary(load_profiles(root))
    if write:
        path = checked_write_file(root, HARNESS_CAPABILITIES_SUMMARY_PATH)
        path.write_text(content, encoding="utf-8")
    return {
        "schema": SUMMARY_RESULT_SCHEMA,
        "result": "wrote" if write else "would_write",
        "dry_run": not write,
        "writes": [{"path": HARNESS_CAPABILITIES_SUMMARY_PATH.as_posix(), "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest()}],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Manage Vanilla Harness Capability Profiles.")
    parser.add_argument("--root", default=".", help="Repository root.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    migrate_parser = subparsers.add_parser("migrate", help="Migrate the aggregate harness catalog into per-harness profiles.")
    migrate_parser.add_argument("--apply", action="store_true", help="Write migrated profile files.")
    migrate_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")

    validate_parser = subparsers.add_parser("validate", help="Validate per-harness Vanilla Harness Capability Profiles.")
    validate_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")

    summarize_parser = subparsers.add_parser("summarize", help="Render the human-facing harness capability summary from profiles.")
    summarize_parser.add_argument("--write", action="store_true", help="Write docs/harness-capabilities.md.")
    summarize_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")

    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    if args.command == "migrate":
        try:
            payload = migrate(root, apply=args.apply)
        except Exception as error:
            payload = {"schema": MIGRATION_RESULT_SCHEMA, "result": "failed", "dry_run": not args.apply, "error": str(error)}
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print(f"FAIL {error}", file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            action = "Wrote" if args.apply else "Would write"
            for write in payload["writes"]:
                print(f"{action} {write['path']}")
        return 0
    if args.command == "validate":
        try:
            results = validate(root)
        except Exception as error:
            results = [
                CheckResult(
                    "validate:exception",
                    False,
                    f"validation crashed: {error.__class__.__name__}: {error}",
                    ".",
                )
            ]
        payload = validation_payload(results)
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            for result in results:
                status = "PASS" if result.ok else "FAIL"
                print(f"{status} {result.name} {result.path} - {result.detail}")
            failed = sum(1 for result in results if not result.ok)
            passed = len(results) - failed
            print(f"{failed} failed, {passed} passed")
        return 0 if all(result.ok for result in results) else 1
    if args.command == "summarize":
        try:
            payload = summarize(root, write=args.write)
        except Exception as error:
            payload = {"schema": SUMMARY_RESULT_SCHEMA, "result": "failed", "dry_run": not args.write, "error": str(error)}
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print(f"FAIL {error}", file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            action = "Wrote" if args.write else "Would write"
            for write in payload["writes"]:
                print(f"{action} {write['path']}")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
