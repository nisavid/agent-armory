#!/usr/bin/env python3.14
from __future__ import annotations

import argparse
import difflib
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
RESEARCH_NOTE_DIR = Path("specs/vanilla-harness-capability-profiles/research-notes")
SCHEMA_PRESSURE_REPORT_PATH = Path("specs/vanilla-harness-capability-profiles/schema-pressure-report.md")
CAPABILITY_PROTOCOL_SPEC_PATH = Path("specs/capability-profiling-protocol/README.md")
CAPABILITY_PROTOCOL_SCHEMA_PATH = Path("specs/capability-profiling-protocol/schema-v1alpha1.md")
CAPABILITY_PROTOCOL_EXAMPLE_DIR = Path("examples/capability-profiling-protocol")
PROFILE_SCHEMA_VERSION = "vanilla-harness-capability-profile.v1alpha1"
CAPABILITY_PROTOCOL_SCHEMA_VERSION = "capability-profiling-protocol.v1alpha1"
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
REFRESH_SCOUT_INPUT_SCHEMA = "harness_capability_profiles.refresh_scout_input.v1"
REFRESH_SCOUT_REPORT_SCHEMA = "harness_capability_profiles.refresh_scout_report.v1"
REFRESH_ANALYSIS_REPORT_SCHEMA = "harness_capability_profiles.refresh_analysis_report.v1"
REFRESH_UPDATE_PLAN_SCHEMA = "harness_capability_profiles.refresh_update_plan.v1"
REFRESH_DIFF_SCHEMA = "harness_capability_profiles.refresh_diff.v1"
REFRESH_APPLY_SCHEMA = "harness_capability_profiles.refresh_apply.v1"
REFRESH_AUDIT_SCHEMA = "harness_capability_profiles.refresh_audit.v1"
SUPPORTED_REFRESH_VALIDATION_SCHEMAS = {VALIDATION_RESULT_SCHEMA, "armory_integrity.validation_result.v1"}
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
CLAIM_MIGRATION_STATUSES = {
    CLAIM_MIGRATION_STATUS,
    "refreshed_from_migrated_claim",
    "new_from_profile_enrichment",
    "split_from_migrated_claim",
    "retired_by_profile_enrichment",
}
CLAIM_EVIDENCE_BASES = {
    CLAIM_EVIDENCE_BASIS,
    "current_first_party_source",
    "fallback_source",
    "local_observation",
    "explicit_unknown",
    "explicit_unsupported",
    "not-applicable",
}
SOURCE_BACKED_CLAIM_EVIDENCE_BASES = {"current_first_party_source", "fallback_source"}
CLAIM_TRIAGE_VALUES = {"retained", "changed", "new", "unsupported", "unknown", "not-applicable", "retired"}
ENRICHMENT_EVIDENCE_CLASSES = {
    "source_backed",
    "fallback_source",
    "local_observation",
    "implementation_inference",
    "hypothesis",
    "unsupported",
    "unknown",
    "not-applicable",
}
RESEARCH_NOTE_SECTIONS = [
    "## Version Basis",
    "## Source Set",
    "## Surface Findings",
    "## Evidence Classification",
    "## Cross-Harness Import And Compatibility",
    "## Memory-Like Surfaces",
    "## Schema Pressure",
    "## Analysis Angle Notes",
    "## Local Observations",
    "## Major Uncertainty",
    "## Scratch Artifact Disposition",
]
RESEARCH_EVIDENCE_TERMS = [
    "source-backed facts",
    "local observations",
    "implementation inferences",
    "hypotheses",
    "unsupported claims",
    "unknowns",
    "not-applicable surfaces",
]
SCHEMA_PRESSURE_SECTIONS = [
    "## Research Scope",
    "## Current Schema Comparison",
    "## Schema Pressure Findings",
    "## Cross-Harness Import And Compatibility",
    "## Memory-Like Surfaces",
    "## Analysis Angles And State Graphs",
    "## Migration Implications",
    "## Ralph Review Disposition",
    "## Scratch Artifact Disposition",
]
SCHEMA_PRESSURE_COLUMNS = [
    "ID",
    "Disposition",
    "Affected harnesses",
    "Motivating evidence",
    "Example claim shape",
    "Proposed validation rule",
    "Migration impact",
]
SCHEMA_PRESSURE_DISPOSITIONS = {"accepted", "deferred", "rejected", "needs more evidence", "needs-more-evidence"}
TABLE_PARSE_ERROR = "__parse_error__"
TABLE_PARSE_ERROR_DETAIL = "__parse_error_detail__"
CAPABILITY_PROTOCOL_EXAMPLES = {
    "vanilla_plan": (
        CAPABILITY_PROTOCOL_EXAMPLE_DIR / "vanilla-codex-skill-study-plan.toml",
        "study_plan",
    ),
    "effective_plan": (
        CAPABILITY_PROTOCOL_EXAMPLE_DIR / "effective-loadout-memory-study-plan.toml",
        "study_plan",
    ),
    "study_report": (
        CAPABILITY_PROTOCOL_EXAMPLE_DIR / "vanilla-codex-skill-study-report.toml",
        "study_report",
    ),
    "jig_adequacy": (
        CAPABILITY_PROTOCOL_EXAMPLE_DIR / "standard-clean-room-jig-adequacy-report.toml",
        "jig_adequacy_report",
    ),
}
CAPABILITY_PROTOCOL_TARGET_TYPES = {
    "vanilla_harness_surface",
    "effective_harness_surface",
    "equipment_surface",
    "clean_room_jig_surface",
    "hypothetical_surface",
}
CAPABILITY_PROTOCOL_JIG_TARGET_TYPES = {"clean_room_jig_surface"}
CAPABILITY_PROTOCOL_RIGOR_FIELDS = [
    "advised_rigor",
    "selected_rigor",
    "selected_rigor_rationale",
    "isolation",
    "reproducibility",
    "harness_state_control",
    "equipment_state_control",
    "config_control",
    "version_pinning",
    "provider_randomness_control",
    "subject_operator_separation",
    "network_access",
    "mutation_allowance",
    "observation_quality",
]
CAPABILITY_PROTOCOL_EFFECTS = {
    "passive_scanning",
    "active_non_mutating_use",
    "local_mutation",
    "profile_mutation",
    "external_network_access",
    "external_disclosure",
    "process_execution",
    "harness_runtime_state_change",
}
CAPABILITY_PROTOCOL_APPROVAL_EFFECTS = CAPABILITY_PROTOCOL_EFFECTS - {"passive_scanning"}
REFRESH_SOURCE_KINDS = {"first_party_source", "fallback_source"}
REFRESH_MUTATION_PATH_PREFIXES = (
    "docs/harness-capabilities/vanilla/",
    "docs/harness-capabilities/schema/",
)
JIG_CONTROL_DISPOSITIONS = {"claimed", "verified", "unsupported", "unknown"}


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


def user_path(root: Path, raw_path: str, *, expected_kind: str | None = None, for_write: bool = False) -> tuple[Path, Path]:
    candidate = Path(raw_path)
    if candidate.is_absolute():
        try:
            root_resolved = root.resolve(strict=True)
        except OSError as error:
            raise ManagerError("repository root missing") from error
        try:
            relative = candidate.relative_to(root_resolved)
        except ValueError as error:
            raise ManagerError(f"{raw_path}: path escapes repository root") from error
    else:
        relative = candidate
    if for_write:
        path = checked_write_file(root, relative)
        return path, relative
    ok, detail, path = path_status(root, relative, expected_kind=expected_kind)
    if not ok:
        raise ManagerError(f"{relative.as_posix()}: {detail}")
    return path, relative


def load_json_file(root: Path, raw_path: str, *, expected_schema: str | None = None) -> tuple[dict[str, Any], Path, Path]:
    path, relative = user_path(root, raw_path, expected_kind="file")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ManagerError(f"{relative.as_posix()}: JSON invalid: {error.msg}") from error
    if not isinstance(payload, dict):
        raise ManagerError(f"{relative.as_posix()}: JSON root must be an object")
    if expected_schema is not None and payload.get("schema") != expected_schema:
        raise ManagerError(f"{relative.as_posix()}: expected schema {expected_schema}")
    return payload, path, relative


def write_json_file(root: Path, raw_path: str | None, payload: dict[str, Any]) -> dict[str, Any] | None:
    if raw_path is None:
        return None
    path, relative = user_path(root, raw_path, for_write=True)
    if any(relative.as_posix().startswith(prefix) for prefix in REFRESH_MUTATION_PATH_PREFIXES):
        raise ManagerError("refresh output may not overwrite canonical profile or schema paths")
    if relative.suffix != ".json":
        raise ManagerError("refresh output path must end in .json")
    content = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return {"path": relative.as_posix(), "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest()}


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def valid_http_url(value: Any) -> bool:
    if not non_empty_string(value):
        return False
    parsed_url = urlparse(value)
    return parsed_url.scheme in {"http", "https"} and bool(parsed_url.netloc)


def validate_string_fields(
    record: dict[str, Any],
    fields: list[str],
    prefix: str,
    path: str,
) -> list[CheckResult]:
    return [CheckResult(f"{prefix}:{field}", False, f"missing {field}", path) for field in fields if not non_empty_string(record.get(field))]


def validate_evidence_class(record: dict[str, Any], prefix: str, path: str) -> list[CheckResult]:
    evidence_class = record.get("evidence_class")
    if evidence_class not in ENRICHMENT_EVIDENCE_CLASSES:
        return [CheckResult(f"{prefix}:evidence_class", False, "invalid evidence class", path)]
    return []


def validate_record_evidence_refs(
    record: dict[str, Any],
    evidence_ids: set[str],
    prefix: str,
    path: str,
    *,
    require_refs_for_source: bool = True,
) -> list[CheckResult]:
    results: list[CheckResult] = []
    refs = record.get("evidence_ids")
    if not isinstance(refs, list) or not all(isinstance(ref, str) for ref in refs):
        results.append(CheckResult(f"{prefix}:evidence_ids", False, "evidence_ids must be a list of strings", path))
        refs = []
    missing_refs = [ref for ref in refs if ref not in evidence_ids]
    if missing_refs:
        results.append(CheckResult(f"{prefix}:evidence_refs", False, f"unknown evidence ids: {', '.join(missing_refs)}", path))
    evidence_class = record.get("evidence_class")
    if require_refs_for_source and evidence_class in {"source_backed", "fallback_source"} and not refs:
        results.append(CheckResult(f"{prefix}:evidence_refs", False, "evidence-backed enrichment needs evidence", path))
    return results


def validate_version_observations(
    profile: dict[str, Any],
    harness_id: str,
    relative_path: Path,
    *,
    require_enrichment: bool,
) -> list[CheckResult]:
    records = profile.get("version_observation", [])
    path = relative_path.as_posix()
    if records is None or records == []:
        if require_enrichment:
            return [
                CheckResult(
                    f"profile:{harness_id}:version_observation",
                    False,
                    "version_observation must be a non-empty array of tables",
                    path,
                )
            ]
        return []
    if not isinstance(records, list):
        return [
            CheckResult(
                f"profile:{harness_id}:version_observation",
                False,
                "version_observation must be an array of tables",
                path,
            )
        ]
    results: list[CheckResult] = []
    for index, record in enumerate(records):
        prefix = f"profile:{harness_id}:version_observation:{index}"
        if not isinstance(record, dict):
            results.append(CheckResult(prefix, False, "version_observation entry must be a table", path))
            continue
        results.extend(validate_string_fields(record, ["id", "observed_version", "checked_at"], prefix, path))
        evidence_class = record.get("evidence_class")
        source_kind = record.get("source_kind")
        if evidence_class == "local_observation":
            if "source_kind" in record:
                results.append(CheckResult(f"{prefix}:source_kind", False, "local observations omit source_kind", path))
            if "source_url" in record:
                results.append(CheckResult(f"{prefix}:source_url", False, "local observations omit source_url", path))
        else:
            if source_kind not in SOURCE_KINDS:
                results.append(CheckResult(f"{prefix}:source_kind", False, "invalid source kind", path))
            if not valid_http_url(record.get("source_url")):
                results.append(CheckResult(f"{prefix}:source_url", False, "source url must be http or https with a host", path))
        if not isinstance(record.get("canonical_profile_change"), bool):
            results.append(CheckResult(f"{prefix}:canonical_profile_change", False, "canonical_profile_change must be boolean", path))
        results.extend(validate_evidence_class(record, prefix, path))
    return results


def validate_harness_extensions(
    profile: dict[str, Any],
    harness_id: str,
    evidence_ids: set[str],
    schema_pressure_ids: set[str] | None,
    relative_path: Path,
    *,
    require_enrichment: bool,
) -> list[CheckResult]:
    records = profile.get("harness_extension", [])
    path = relative_path.as_posix()
    if records is None or records == []:
        if require_enrichment:
            return [
                CheckResult(
                    f"profile:{harness_id}:harness_extension",
                    False,
                    "harness_extension must be a non-empty array of tables",
                    path,
                )
            ]
        return []
    if not isinstance(records, list):
        return [
            CheckResult(
                f"profile:{harness_id}:harness_extension",
                False,
                "harness_extension must be an array of tables",
                path,
            )
        ]
    results: list[CheckResult] = []
    for index, record in enumerate(records):
        prefix = f"profile:{harness_id}:harness_extension:{index}"
        if not isinstance(record, dict):
            results.append(CheckResult(prefix, False, "harness_extension entry must be a table", path))
            continue
        results.extend(validate_string_fields(record, ["id", "name", "scope", "description"], prefix, path))
        extension_schema_pressure_ids = record.get("schema_pressure_ids")
        if not string_list(extension_schema_pressure_ids):
            results.append(CheckResult(f"{prefix}:schema_pressure_ids", False, "schema_pressure_ids must be a list of strings", path))
        elif schema_pressure_ids is not None:
            for schema_pressure_id in extension_schema_pressure_ids:
                if schema_pressure_id not in schema_pressure_ids:
                    results.append(
                        CheckResult(
                            f"{prefix}:schema_pressure_ids:{schema_pressure_id}",
                            False,
                            "schema_pressure_id not found in report rows",
                            path,
                        )
                    )
        results.extend(validate_evidence_class(record, prefix, path))
        results.extend(validate_record_evidence_refs(record, evidence_ids, prefix, path))
    return results


def validate_claim_detail_records(
    claim: dict[str, Any],
    harness_id: str,
    claim_index: int,
    evidence_ids: set[str],
    relative_path: Path,
    *,
    refreshed_claim: bool,
) -> list[CheckResult]:
    path = relative_path.as_posix()
    nested_specs = {
        "detail": ["component", "load_attachment_point", "activation", "mutability"],
        "compatibility_bridge": [
            "imported_from",
            "imported_convention",
            "activation",
            "disable_behavior",
            "precedence",
            "fidelity_limits",
        ],
        "memory_like_surface": [
            "persistence_scope",
            "retrieval_trigger",
            "mutability",
            "freshness",
            "privacy_boundary",
            "write_authority",
            "api_stability",
        ],
        "automation_surface": [
            "trigger_class",
            "runner_locus",
            "recurrence_shape",
            "permission_sandbox_context",
            "missed_run_behavior",
            "output_delivery",
        ],
    }
    results: list[CheckResult] = []
    family_required_tables = {
        "memory_context_retrieval": "memory_like_surface",
        "scheduling_automation": "automation_surface",
        "cross_harness_import_compatibility": "compatibility_bridge",
    }
    required_table = family_required_tables.get(str(claim.get("family")))
    if refreshed_claim and not claim.get("detail"):
        results.append(
            CheckResult(
                f"profile:{harness_id}:claim:{claim_index}:detail",
                False,
                f"refreshed {claim.get('family')} claim needs detail",
                path,
            )
        )
    if refreshed_claim and required_table and not claim.get(required_table):
        results.append(
            CheckResult(
                f"profile:{harness_id}:claim:{claim_index}:{required_table}",
                False,
                f"refreshed {claim.get('family')} claim needs {required_table}",
                path,
            )
        )
    for table_name, string_fields in nested_specs.items():
        records = claim.get(table_name, [])
        if records is None:
            continue
        prefix_base = f"profile:{harness_id}:claim:{claim_index}:{table_name}"
        if not isinstance(records, list):
            results.append(CheckResult(prefix_base, False, f"{table_name} must be an array of tables", path))
            continue
        for record_index, record in enumerate(records):
            prefix = f"{prefix_base}:{record_index}"
            if not isinstance(record, dict):
                results.append(CheckResult(prefix, False, f"{table_name} entry must be a table", path))
                continue
            results.extend(validate_string_fields(record, string_fields, prefix, path))
            if table_name == "detail" and not string_list(record.get("scope")):
                results.append(CheckResult(f"{prefix}:scope", False, "scope must be a list of strings", path))
            if table_name == "compatibility_bridge" and not string_list(record.get("surviving_components")):
                results.append(
                    CheckResult(f"{prefix}:surviving_components", False, "surviving_components must be a list of strings", path)
                )
            results.extend(validate_evidence_class(record, prefix, path))
            results.extend(validate_record_evidence_refs(record, evidence_ids, prefix, path))
    return results


def validate_profile_data(
    profile: dict[str, Any],
    harness_id: str,
    relative_path: Path,
    *,
    schema_pressure_ids: set[str] | None = None,
    require_enrichment: bool = False,
) -> list[CheckResult]:
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

    results.extend(validate_version_observations(profile, harness_id, relative_path, require_enrichment=require_enrichment))
    results.extend(
        validate_harness_extensions(
            profile,
            harness_id,
            evidence_ids,
            schema_pressure_ids,
            relative_path,
            require_enrichment=require_enrichment,
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
            expected_claim_values = {
                "applicability_scope": CLAIM_APPLICABILITY_SCOPE,
                "capability_origin": CLAIM_CAPABILITY_ORIGIN,
            }
            for field, expected in expected_claim_values.items():
                if claim.get(field) != expected:
                    results.append(CheckResult(f"profile:{harness_id}:claim:{index}:{field}", False, f"must be {expected}", relative_path.as_posix()))
            migration_status = claim.get("migration_status")
            evidence_basis = claim.get("evidence_basis")
            valid_migration_status = migration_status in CLAIM_MIGRATION_STATUSES
            valid_evidence_basis = evidence_basis in CLAIM_EVIDENCE_BASES
            if not valid_migration_status:
                results.append(CheckResult(f"profile:{harness_id}:claim:{index}:migration_status", False, "invalid migration status", relative_path.as_posix()))
            if not valid_evidence_basis:
                results.append(CheckResult(f"profile:{harness_id}:claim:{index}:evidence_basis", False, "invalid evidence basis", relative_path.as_posix()))
            if valid_evidence_basis and evidence_basis in SOURCE_BACKED_CLAIM_EVIDENCE_BASES and not refs:
                results.append(CheckResult(f"profile:{harness_id}:claim:{index}:evidence_refs", False, "source-backed claim needs evidence", relative_path.as_posix()))
            elif status == "supported" and not refs:
                results.append(CheckResult(f"profile:{harness_id}:claim:{index}:evidence_refs", False, "supported claim needs evidence", relative_path.as_posix()))
            if valid_migration_status and valid_evidence_basis:
                migrated_status = migration_status == CLAIM_MIGRATION_STATUS
                aggregate_basis = evidence_basis == CLAIM_EVIDENCE_BASIS
                if migrated_status != aggregate_basis:
                    results.append(
                        CheckResult(
                            f"profile:{harness_id}:claim:{index}:migration_evidence_pair",
                            False,
                            "migrated aggregate status and aggregate evidence basis must be paired",
                            relative_path.as_posix(),
                        )
                    )
                refreshed_claim = not (migrated_status and aggregate_basis)
            else:
                refreshed_claim = True
            if require_enrichment and not refreshed_claim:
                results.append(
                    CheckResult(
                        f"profile:{harness_id}:claim:{index}:migration_status",
                        False,
                        "canonical profile claim must be refreshed from migrated aggregate status",
                        relative_path.as_posix(),
                    )
                )
            if refreshed_claim:
                claim_triage = claim.get("claim_triage")
                if claim_triage not in CLAIM_TRIAGE_VALUES:
                    results.append(CheckResult(f"profile:{harness_id}:claim:{index}:claim_triage", False, "invalid or missing claim triage", relative_path.as_posix()))
                for field in ["triage_rationale", "install_activation", "configuration_surface", "reload_update_behavior"]:
                    if not non_empty_string(claim.get(field)):
                        results.append(CheckResult(f"profile:{harness_id}:claim:{index}:{field}", False, f"missing {field}", relative_path.as_posix()))
            results.extend(
                validate_claim_detail_records(
                    claim,
                    harness_id,
                    index,
                    evidence_ids,
                    relative_path,
                    refreshed_claim=refreshed_claim,
                )
            )
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


def load_schema_pressure_report_ids(root: Path) -> set[str] | None:
    path = repo_path(root, SCHEMA_PRESSURE_REPORT_PATH)
    if not path.is_file():
        return None
    row_ids: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\|\s*(SP-\d+)\s*\|", line)
        if match:
            row_ids.add(match.group(1))
    return row_ids


def validate_profile(root: Path, harness_id: str, schema_pressure_ids: set[str] | None = None) -> list[CheckResult]:
    relative_path = profile_path(harness_id)
    ok, detail, path = path_status(root, relative_path, expected_kind="file")
    if not ok:
        return [CheckResult(f"profile:{harness_id}:path", False, detail if detail != "not a file" else "missing profile", relative_path.as_posix())]
    try:
        profile = load_toml(path)
    except tomllib.TOMLDecodeError as error:
        return [CheckResult(f"profile:{harness_id}:toml", False, f"TOML invalid: {error.msg}", relative_path.as_posix())]
    return validate_profile_data(
        profile,
        harness_id,
        relative_path,
        schema_pressure_ids=schema_pressure_ids,
        require_enrichment=True,
    )


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
            continue
        row_id = cells[0] if cells and cells[0] else f"row_{len(rows) + 1}"
        rows.append(
            {
                "ID": row_id,
                TABLE_PARSE_ERROR: "invalid column count",
                TABLE_PARSE_ERROR_DETAIL: f"expected {len(headers)} cells, got {len(cells)}",
            }
        )
    return rows


def normalized_heading_title(title: str) -> str:
    return re.sub(r"\s+", " ", title.strip()).casefold()


def strip_markdown_code_blocks(markdown: str) -> str:
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
            opening_fence = re.match(r"(`{3,}|~{3,})", stripped)
            if opening_fence:
                marker = opening_fence.group(1)
                fence_char = marker[0]
                fence_length = len(marker)
                continue
        if fence_char is not None:
            continue
        if line.startswith(("    ", "\t")):
            visible_lines.append("\n" if line.endswith("\n") else "")
            continue
        visible_lines.append(line)
    return "".join(visible_lines)


def markdown_h2_sections(markdown: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current_section: str | None = None
    for line in strip_markdown_code_blocks(markdown).splitlines():
        match = re.match(r"^\s*##\s+(?P<title>.+?)\s*$", line)
        if match:
            current_section = normalized_heading_title(match.group("title"))
            sections[current_section] = []
            continue
        if current_section is not None:
            sections[current_section].append(line)
    return {title: "\n".join(lines) for title, lines in sections.items()}


def validate_required_markdown_sections(markdown: str, required_sections: list[str], prefix: str, path: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    sections = markdown_h2_sections(markdown)
    for section in required_sections:
        required_title = normalized_heading_title(section.removeprefix("## "))
        if required_title not in sections:
            results.append(CheckResult(f"{prefix}:section:{section.removeprefix('## ').casefold().replace(' ', '_')}", False, f"missing section: {section}", path.as_posix()))
    return results


def validate_research_note(root: Path, harness_id: str) -> list[CheckResult]:
    relative_path = RESEARCH_NOTE_DIR / f"{harness_id}.md"
    ok, detail, path = path_status(root, relative_path, expected_kind="file")
    if not ok:
        missing_detail = "missing research note" if detail in {"missing", "not a file"} else detail
        return [CheckResult(f"research_note:{harness_id}:path", False, missing_detail, relative_path.as_posix())]
    markdown = path.read_text(encoding="utf-8")
    results = validate_required_markdown_sections(markdown, RESEARCH_NOTE_SECTIONS, f"research_note:{harness_id}", relative_path)
    sections = markdown_h2_sections(markdown)
    version_basis = sections.get("version basis", "")
    source_set = sections.get("source set", "")
    surface_findings = sections.get("surface findings", "")
    if "Checked at:" not in version_basis:
        results.append(CheckResult(f"research_note:{harness_id}:checked_at", False, "missing checked-at timestamp", relative_path.as_posix()))
    if "Version basis:" not in version_basis:
        results.append(CheckResult(f"research_note:{harness_id}:version_basis", False, "missing version basis", relative_path.as_posix()))
    if not re.search(r"https?://", source_set):
        results.append(CheckResult(f"research_note:{harness_id}:source_set", False, "missing source URL", relative_path.as_posix()))
    missing_families = [
        family
        for family in SURFACE_FAMILIES
        if not re.search(rf"(?<![A-Za-z0-9_]){re.escape(family)}(?![A-Za-z0-9_])", surface_findings)
    ]
    if missing_families:
        results.append(
            CheckResult(
                f"research_note:{harness_id}:surface_family_coverage",
                False,
                f"missing families: {', '.join(missing_families)}",
                relative_path.as_posix(),
            )
        )
    folded = markdown.casefold()
    missing_terms = [term for term in RESEARCH_EVIDENCE_TERMS if term not in folded]
    if missing_terms:
        results.append(
            CheckResult(
                f"research_note:{harness_id}:evidence_classification",
                False,
                f"missing evidence terms: {', '.join(missing_terms)}",
                relative_path.as_posix(),
            )
        )
    if "Capability Analysis Angle" not in markdown or "Capability State Graph" not in markdown:
        results.append(
            CheckResult(
                f"research_note:{harness_id}:analysis_angles",
                False,
                "must mention Capability Analysis Angles and Capability State Graphs",
                relative_path.as_posix(),
            )
        )
    if not any(not result.ok for result in results):
        results.append(CheckResult(f"research_note:{harness_id}", True, "complete", relative_path.as_posix()))
    return results


def validate_schema_pressure_report(root: Path) -> list[CheckResult]:
    relative_path = SCHEMA_PRESSURE_REPORT_PATH
    ok, detail, path = path_status(root, relative_path, expected_kind="file")
    if not ok:
        missing_detail = "missing schema pressure report" if detail in {"missing", "not a file"} else detail
        return [CheckResult("schema_pressure:path", False, missing_detail, relative_path.as_posix())]
    markdown = path.read_text(encoding="utf-8")
    results = validate_required_markdown_sections(markdown, SCHEMA_PRESSURE_SECTIONS, "schema_pressure", relative_path)
    rows = markdown_table_rows(markdown, "## Schema Pressure Findings")
    if not rows:
        results.append(CheckResult("schema_pressure:findings_table", False, "missing schema pressure findings rows", relative_path.as_posix()))
    for index, row in enumerate(rows):
        row_id = row.get("ID") or f"row_{index + 1}"
        if row.get(TABLE_PARSE_ERROR):
            detail = row.get(TABLE_PARSE_ERROR_DETAIL, "invalid table row column count")
            results.append(CheckResult(f"schema_pressure:row:{row_id}:table_shape", False, detail, relative_path.as_posix()))
            continue
        for column in SCHEMA_PRESSURE_COLUMNS:
            if not row.get(column, "").strip():
                result_field = slug(column).replace("-", "_")
                results.append(CheckResult(f"schema_pressure:row:{row_id}:{result_field}", False, f"missing {column}", relative_path.as_posix()))
        disposition = row.get("Disposition", "").casefold()
        if disposition and disposition not in SCHEMA_PRESSURE_DISPOSITIONS:
            results.append(CheckResult(f"schema_pressure:row:{row_id}:disposition", False, "invalid disposition", relative_path.as_posix()))
        evidence = row.get("Motivating evidence", "")
        if evidence and not re.search(r"https?://|\[[^\]]+\]\([^)]+\)", evidence):
            results.append(CheckResult(f"schema_pressure:row:{row_id}:motivating_evidence", False, "missing evidence reference", relative_path.as_posix()))
    if not any(not result.ok for result in results):
        results.append(CheckResult("schema_pressure:report", True, "complete", relative_path.as_posix()))
    return results


def validate_research_outputs(root: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    for harness_id in sorted(REQUIRED_HARNESSES):
        results.extend(validate_research_note(root, harness_id))
    results.extend(validate_schema_pressure_report(root))
    return results


def non_empty_string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(non_empty_string(item) for item in value)


def validate_protocol_document(root: Path, relative_path: Path, name: str, required_terms: list[str]) -> list[CheckResult]:
    ok, detail, path = path_status(root, relative_path, expected_kind="file")
    if not ok:
        missing_detail = "missing protocol artifact" if detail in {"missing", "not a file"} else detail
        return [CheckResult(f"capability_profiling_protocol:{name}", False, missing_detail, relative_path.as_posix())]
    markdown = path.read_text(encoding="utf-8")
    normalized_markdown = " ".join(markdown.split())
    missing_terms = [term for term in required_terms if " ".join(term.split()) not in normalized_markdown]
    if missing_terms:
        return [
            CheckResult(
                f"capability_profiling_protocol:{name}",
                False,
                f"missing terms: {', '.join(missing_terms)}",
                relative_path.as_posix(),
            )
        ]
    return [CheckResult(f"capability_profiling_protocol:{name}", True, "present", relative_path.as_posix())]


def validate_protocol_record_list(
    artifact: dict[str, Any],
    key: str,
    prefix: str,
    path: str,
    *,
    require_non_empty: bool = True,
) -> tuple[list[dict[str, Any]], list[CheckResult]]:
    value = artifact.get(key)
    if value is None:
        if require_non_empty:
            return [], [CheckResult(f"{prefix}:{key}", False, f"{key} must be a non-empty array of tables", path)]
        return [], []
    if not isinstance(value, list):
        return [], [CheckResult(f"{prefix}:{key}", False, f"{key} must be an array of tables", path)]
    records: list[dict[str, Any]] = []
    results: list[CheckResult] = []
    if require_non_empty and not value:
        results.append(CheckResult(f"{prefix}:{key}", False, f"{key} must be a non-empty array of tables", path))
    for index, record in enumerate(value):
        if not isinstance(record, dict):
            results.append(CheckResult(f"{prefix}:{key}:{index}", False, f"{key} entry must be a table", path))
            continue
        records.append(record)
    return records, results


def validate_protocol_target(
    artifact: dict[str, Any],
    prefix: str,
    path: str,
    state_ids: set[str],
    claim_ids: set[str],
) -> list[CheckResult]:
    target = artifact.get("target")
    if not isinstance(target, dict):
        return [CheckResult(f"{prefix}:target", False, "target must be a table", path)]
    results = validate_string_fields(
        target,
        ["type", "surface", "scope", "state_ref", "selected_rigor"],
        f"{prefix}:target",
        path,
    )
    target_type = target.get("type")
    if non_empty_string(target_type) and target_type not in CAPABILITY_PROTOCOL_TARGET_TYPES:
        results.append(CheckResult(f"{prefix}:target:type", False, "invalid target type", path))
    state_ref = target.get("state_ref")
    if non_empty_string(state_ref) and state_ids and state_ref not in state_ids:
        results.append(CheckResult(f"{prefix}:target:state_ref", False, "target state_ref must reference a state", path))
    claims_under_study = target.get("claims_under_study")
    if not non_empty_string_list(claims_under_study):
        results.append(CheckResult(f"{prefix}:target:claims_under_study", False, "claims_under_study must be a non-empty list of strings", path))
    elif claim_ids:
        missing_claims = [claim_ref for claim_ref in claims_under_study if claim_ref not in claim_ids]
        if missing_claims:
            results.append(CheckResult(f"{prefix}:target:claims_under_study", False, f"unknown claims: {', '.join(missing_claims)}", path))
    for field in ["required_evidence", "operator_preferences"]:
        if not non_empty_string_list(target.get(field)):
            results.append(CheckResult(f"{prefix}:target:{field}", False, f"{field} must be a non-empty list of strings", path))
    return results


def validate_protocol_rigor_effects_controls(artifact: dict[str, Any], prefix: str, path: str) -> list[CheckResult]:
    results: list[CheckResult] = []
    rigor = artifact.get("rigor")
    if not isinstance(rigor, dict):
        results.append(CheckResult(f"{prefix}:rigor", False, "rigor must be a table", path))
    else:
        results.extend(validate_string_fields(rigor, CAPABILITY_PROTOCOL_RIGOR_FIELDS, f"{prefix}:rigor", path))
    effects = artifact.get("effects")
    if not isinstance(effects, dict):
        results.append(CheckResult(f"{prefix}:effects", False, "effects must be a table", path))
        allowed_effects: list[str] = []
    else:
        allowed = effects.get("allowed")
        if not non_empty_string_list(allowed):
            results.append(CheckResult(f"{prefix}:effects:allowed", False, "allowed effects must be a non-empty list of strings", path))
            allowed_effects = []
        else:
            allowed_effects = list(allowed)
            invalid_effects = [effect for effect in allowed_effects if effect not in CAPABILITY_PROTOCOL_EFFECTS]
            if invalid_effects:
                results.append(CheckResult(f"{prefix}:effects:allowed", False, f"invalid effects: {', '.join(invalid_effects)}", path))
        blocked = effects.get("blocked")
        if blocked is None:
            results.append(CheckResult(f"{prefix}:effects:blocked", False, "blocked effects must be present as a list of strings", path))
            blocked_effects: list[str] = []
        elif not isinstance(blocked, list) or not all(isinstance(effect, str) for effect in blocked):
            results.append(CheckResult(f"{prefix}:effects:blocked", False, "blocked effects must be a list of strings", path))
            blocked_effects: list[str] = []
        else:
            blocked_effects = list(blocked)
            invalid_blocked_effects = [effect for effect in blocked_effects if effect not in CAPABILITY_PROTOCOL_EFFECTS]
            if invalid_blocked_effects:
                results.append(CheckResult(f"{prefix}:effects:blocked", False, f"invalid effects: {', '.join(invalid_blocked_effects)}", path))
            overlapping_effects = sorted(set(allowed_effects) & set(blocked_effects))
            if overlapping_effects:
                results.append(CheckResult(f"{prefix}:effects:overlap", False, f"effects cannot be both allowed and blocked: {', '.join(overlapping_effects)}", path))
    controls = artifact.get("controls")
    if not isinstance(controls, dict):
        results.append(CheckResult(f"{prefix}:controls", False, "controls must be a table", path))
    else:
        for field in ["available", "missing", "operator_preferences"]:
            if not isinstance(controls.get(field), list) or not all(isinstance(item, str) for item in controls.get(field, [])):
                results.append(CheckResult(f"{prefix}:controls:{field}", False, f"{field} must be a list of strings", path))
    approval_required = sorted(effect for effect in allowed_effects if effect in CAPABILITY_PROTOCOL_APPROVAL_EFFECTS)
    approval = artifact.get("approval")
    if approval_required:
        if not isinstance(approval, dict):
            results.append(CheckResult(f"{prefix}:approval", False, "effectful studies require approval table", path))
        else:
            for field in ["security_classification_ref", "operator_approval_ref"]:
                if not non_empty_string(approval.get(field)):
                    results.append(
                        CheckResult(
                            f"{prefix}:approval:{field}",
                            False,
                            f"allowed effects require {field}: {', '.join(approval_required)}",
                            path,
                        )
                    )
    return results


def validate_protocol_state_graph(artifact: dict[str, Any], prefix: str, path: str) -> tuple[set[str], list[CheckResult]]:
    states, results = validate_protocol_record_list(artifact, "state", prefix, path)
    state_ids: set[str] = set()
    adjacency: dict[str, list[str]] = {}
    for index, state in enumerate(states):
        state_prefix = f"{prefix}:state:{index}"
        results.extend(validate_string_fields(state, ["id", "kind", "description"], state_prefix, path))
        state_id = state.get("id")
        if non_empty_string(state_id):
            if state_id in state_ids:
                results.append(CheckResult(f"{state_prefix}:id", False, "duplicate state id", path))
            state_ids.add(str(state_id))
        if not non_empty_string_list(state.get("expected_controls")):
            results.append(CheckResult(f"{state_prefix}:expected_controls", False, "expected_controls must be a non-empty list of strings", path))
    transitions, transition_results = validate_protocol_record_list(artifact, "transition", prefix, path, require_non_empty=False)
    results.extend(transition_results)
    for transition in transitions:
        transition_id = str(transition.get("id", "unknown"))
        transition_prefix = f"{prefix}:transition:{transition_id}"
        results.extend(validate_string_fields(transition, ["id", "from", "to", "description"], transition_prefix, path))
        from_state = transition.get("from")
        to_state = transition.get("to")
        if non_empty_string(from_state):
            if from_state not in state_ids:
                results.append(CheckResult(f"{transition_prefix}:from", False, "transition source must reference a state", path))
            else:
                adjacency.setdefault(str(from_state), [])
        if non_empty_string(to_state):
            if to_state not in state_ids:
                results.append(CheckResult(f"{transition_prefix}:to", False, "transition target must reference a state", path))
            elif non_empty_string(from_state) and from_state in state_ids:
                adjacency.setdefault(str(from_state), []).append(str(to_state))

    visited: set[str] = set()
    visiting: set[str] = set()

    def has_cycle(state_id: str) -> bool:
        if state_id in visiting:
            return True
        if state_id in visited:
            return False
        visiting.add(state_id)
        for next_state in adjacency.get(state_id, []):
            if has_cycle(next_state):
                return True
        visiting.remove(state_id)
        visited.add(state_id)
        return False

    if any(has_cycle(state_id) for state_id in sorted(state_ids)):
        results.append(CheckResult(f"{prefix}:state_graph:cycle", False, "Capability State Graph must be acyclic", path))
    return state_ids, results


def validate_protocol_claims(artifact: dict[str, Any], prefix: str, path: str) -> tuple[set[str], list[CheckResult]]:
    claims, results = validate_protocol_record_list(artifact, "claim", prefix, path)
    claim_ids: set[str] = set()
    for index, claim in enumerate(claims):
        claim_prefix = f"{prefix}:claim:{index}"
        results.extend(validate_string_fields(claim, ["id", "statement", "profile_claim_ref"], claim_prefix, path))
        claim_id_value = claim.get("id")
        if non_empty_string(claim_id_value):
            if claim_id_value in claim_ids:
                results.append(CheckResult(f"{claim_prefix}:id", False, "duplicate claim id", path))
            claim_ids.add(str(claim_id_value))
        if not non_empty_string_list(claim.get("required_evidence")):
            results.append(CheckResult(f"{claim_prefix}:required_evidence", False, "required_evidence must be a non-empty list of strings", path))
    return claim_ids, results


def validate_protocol_observations_and_angles(
    artifact: dict[str, Any],
    prefix: str,
    path: str,
    state_ids: set[str],
    claim_ids: set[str],
) -> list[CheckResult]:
    results: list[CheckResult] = []
    observations, observation_results = validate_protocol_record_list(artifact, "observation_point", prefix, path)
    results.extend(observation_results)
    observation_ids: set[str] = set()
    for observation in observations:
        observation_id = str(observation.get("id", "unknown"))
        observation_prefix = f"{prefix}:observation_point:{observation_id}"
        results.extend(validate_string_fields(observation, ["id", "state_id", "evidence_class"], observation_prefix, path))
        if non_empty_string(observation.get("id")):
            if observation["id"] in observation_ids:
                results.append(CheckResult(f"{observation_prefix}:id", False, "duplicate observation point id", path))
            observation_ids.add(str(observation["id"]))
        state_id = observation.get("state_id")
        if non_empty_string(state_id) and state_id not in state_ids:
            results.append(CheckResult(f"{observation_prefix}:state_id", False, "observation point must reference a state", path))
        claim_refs = observation.get("claim_refs")
        if not non_empty_string_list(claim_refs):
            results.append(CheckResult(f"{observation_prefix}:claim_refs", False, "claim_refs must be a non-empty list of strings", path))
        else:
            missing_claims = [claim_ref for claim_ref in claim_refs if claim_ref not in claim_ids]
            if missing_claims:
                results.append(CheckResult(f"{observation_prefix}:claim_refs", False, f"unknown claims: {', '.join(missing_claims)}", path))
        if not non_empty_string_list(observation.get("expected_evidence")):
            results.append(CheckResult(f"{observation_prefix}:expected_evidence", False, "expected_evidence must be a non-empty list of strings", path))
    angles, angle_results = validate_protocol_record_list(artifact, "analysis_angle", prefix, path)
    results.extend(angle_results)
    selected_count = 0
    for angle in angles:
        angle_id = str(angle.get("id", "unknown"))
        angle_prefix = f"{prefix}:analysis_angle:{angle_id}"
        results.extend(
            validate_string_fields(
                angle,
                ["id", "cost", "control", "observation_strength", "contamination_risk", "expected_confidence", "rationale"],
                angle_prefix,
                path,
            )
        )
        if angle.get("selected") is True:
            selected_count += 1
        elif not isinstance(angle.get("selected"), bool):
            results.append(CheckResult(f"{angle_prefix}:selected", False, "selected must be boolean", path))
        claim_refs = angle.get("claim_refs")
        if not non_empty_string_list(claim_refs):
            results.append(CheckResult(f"{angle_prefix}:claim_refs", False, "claim_refs must be a non-empty list of strings", path))
        else:
            missing_claims = [claim_ref for claim_ref in claim_refs if claim_ref not in claim_ids]
            if missing_claims:
                results.append(CheckResult(f"{angle_prefix}:claim_refs", False, f"unknown claims: {', '.join(missing_claims)}", path))
        observation_refs = angle.get("observation_point_refs")
        if not non_empty_string_list(observation_refs):
            results.append(CheckResult(f"{angle_prefix}:observation_point_refs", False, "observation_point_refs must be a non-empty list of strings", path))
        else:
            missing_observations = [observation_ref for observation_ref in observation_refs if observation_ref not in observation_ids]
            if missing_observations:
                results.append(
                    CheckResult(
                        f"{angle_prefix}:observation_point_refs",
                        False,
                        f"unknown observation points: {', '.join(missing_observations)}",
                        path,
                    )
                )
    if angles and selected_count == 0:
        results.append(CheckResult(f"{prefix}:analysis_angle:selected", False, "one analysis angle must be selected", path))
    elif selected_count > 1:
        results.append(CheckResult(f"{prefix}:analysis_angle:selected", False, "exactly one analysis angle must be selected", path))
    return results


def validate_protocol_study_plan(artifact: dict[str, Any], prefix: str, path: str) -> list[CheckResult]:
    results: list[CheckResult] = []
    state_ids, state_results = validate_protocol_state_graph(artifact, prefix, path)
    results.extend(state_results)
    claim_ids, claim_results = validate_protocol_claims(artifact, prefix, path)
    results.extend(claim_results)
    results.extend(validate_protocol_target(artifact, prefix, path, state_ids, claim_ids))
    results.extend(validate_protocol_rigor_effects_controls(artifact, prefix, path))
    target = artifact.get("target")
    rigor = artifact.get("rigor")
    if isinstance(target, dict) and isinstance(rigor, dict):
        target_selected_rigor = target.get("selected_rigor")
        rigor_selected_rigor = rigor.get("selected_rigor")
        if (
            non_empty_string(target_selected_rigor)
            and non_empty_string(rigor_selected_rigor)
            and target_selected_rigor != rigor_selected_rigor
        ):
            results.append(
                CheckResult(
                    f"{prefix}:selected_rigor",
                    False,
                    "target.selected_rigor must match rigor.selected_rigor",
                    path,
                )
            )
    results.extend(validate_protocol_observations_and_angles(artifact, prefix, path, state_ids, claim_ids))
    return results


def protocol_record_ids(artifact: dict[str, Any], key: str) -> set[str]:
    records = artifact.get(key)
    if not isinstance(records, list):
        return set()
    return {
        str(record["id"])
        for record in records
        if isinstance(record, dict) and non_empty_string(record.get("id"))
    }


def load_protocol_plan_ref(
    root: Path,
    plan_ref: Any,
    prefix: str,
    path: str,
) -> tuple[dict[str, Any] | None, list[CheckResult]]:
    if not non_empty_string(plan_ref):
        return None, []
    relative_path = Path(str(plan_ref))
    ok, detail, plan_path = path_status(root, relative_path, expected_kind="file")
    if not ok:
        return None, [CheckResult(f"{prefix}:plan_ref", False, f"plan_ref {detail}", path)]
    try:
        plan = load_toml(plan_path)
    except tomllib.TOMLDecodeError as error:
        return None, [CheckResult(f"{prefix}:plan_ref", False, f"referenced plan TOML invalid: {error.msg}", path)]
    if plan.get("artifact_kind") != "study_plan":
        return plan, [CheckResult(f"{prefix}:plan_ref", False, "plan_ref must reference a study_plan artifact", path)]
    return plan, []


def validate_protocol_study_report(root: Path, artifact: dict[str, Any], prefix: str, path: str) -> list[CheckResult]:
    results = validate_string_fields(artifact, ["plan_id", "plan_ref"], prefix, path)
    referenced_plan, plan_results = load_protocol_plan_ref(root, artifact.get("plan_ref"), prefix, path)
    results.extend(plan_results)
    plan_claim_ids: set[str] = set()
    plan_observation_ids: set[str] = set()
    if referenced_plan is not None:
        plan_id = referenced_plan.get("id")
        if non_empty_string(artifact.get("plan_id")) and non_empty_string(plan_id) and artifact["plan_id"] != plan_id:
            results.append(CheckResult(f"{prefix}:plan_id", False, "plan_id must match referenced plan id", path))
        plan_claim_ids = protocol_record_ids(referenced_plan, "claim")
        plan_observation_ids = protocol_record_ids(referenced_plan, "observation_point")
    execution = artifact.get("execution")
    if not isinstance(execution, dict):
        results.append(CheckResult(f"{prefix}:execution", False, "execution must be a table", path))
    else:
        results.extend(validate_string_fields(execution, ["executed_at"], f"{prefix}:execution", path))
        for field in ["deviations", "failed_controls", "limitations"]:
            if not isinstance(execution.get(field), list) or not all(isinstance(item, str) for item in execution.get(field, [])):
                results.append(CheckResult(f"{prefix}:execution:{field}", False, f"{field} must be a list of strings", path))
    evidence_records, evidence_results = validate_protocol_record_list(artifact, "evidence", prefix, path)
    results.extend(evidence_results)
    evidence_ids: set[str] = set()
    for evidence in evidence_records:
        evidence_id_value = str(evidence.get("id", "unknown"))
        evidence_prefix = f"{prefix}:evidence:{evidence_id_value}"
        results.extend(validate_string_fields(evidence, ["id", "kind", "ref", "disposition", "summary"], evidence_prefix, path))
        if non_empty_string(evidence.get("id")):
            if evidence["id"] in evidence_ids:
                results.append(CheckResult(f"{evidence_prefix}:id", False, "duplicate evidence id", path))
            evidence_ids.add(str(evidence["id"]))
    observed_results, observed_validation = validate_protocol_record_list(artifact, "observed_result", prefix, path)
    results.extend(observed_validation)
    for observed in observed_results:
        observed_id = str(observed.get("id", "unknown"))
        observed_prefix = f"{prefix}:observed_result:{observed_id}"
        results.extend(validate_string_fields(observed, ["id", "claim_ref", "observation_point_ref", "outcome", "summary"], observed_prefix, path))
        claim_ref = observed.get("claim_ref")
        if referenced_plan is not None and non_empty_string(claim_ref) and claim_ref not in plan_claim_ids:
            results.append(CheckResult(f"{observed_prefix}:claim_ref", False, "claim_ref must reference the report plan", path))
        observation_point_ref = observed.get("observation_point_ref")
        if referenced_plan is not None and non_empty_string(observation_point_ref) and observation_point_ref not in plan_observation_ids:
            results.append(CheckResult(f"{observed_prefix}:observation_point_ref", False, "observation_point_ref must reference the report plan", path))
        refs = observed.get("evidence_refs")
        if not non_empty_string_list(refs):
            results.append(CheckResult(f"{observed_prefix}:evidence_refs", False, "evidence_refs must be a non-empty list of strings", path))
        else:
            missing_refs = [ref for ref in refs if ref not in evidence_ids]
            if missing_refs:
                results.append(CheckResult(f"{observed_prefix}:evidence_refs", False, f"unknown evidence ids: {', '.join(missing_refs)}", path))
    assessments, assessment_validation = validate_protocol_record_list(artifact, "claim_assessment", prefix, path)
    results.extend(assessment_validation)
    for assessment in assessments:
        assessment_prefix = f"{prefix}:claim_assessment:{assessment.get('claim_ref', 'unknown')}"
        results.extend(
            validate_string_fields(
                assessment,
                ["claim_ref", "claim_confidence", "test_sufficiency", "profile_impact"],
                assessment_prefix,
                path,
            )
        )
        claim_ref = assessment.get("claim_ref")
        if referenced_plan is not None and non_empty_string(claim_ref) and claim_ref not in plan_claim_ids:
            results.append(CheckResult(f"{assessment_prefix}:claim_ref", False, "claim_ref must reference the report plan", path))
        for field in ["limitations", "failed_controls"]:
            if not isinstance(assessment.get(field), list) or not all(isinstance(item, str) for item in assessment.get(field, [])):
                results.append(CheckResult(f"{assessment_prefix}:{field}", False, f"{field} must be a list of strings", path))
    artifacts, artifact_validation = validate_protocol_record_list(artifact, "artifact", prefix, path)
    results.extend(artifact_validation)
    for report_artifact in artifacts:
        artifact_prefix = f"{prefix}:artifact:{report_artifact.get('id', 'unknown')}"
        results.extend(validate_string_fields(report_artifact, ["id", "disposition", "path_or_ref", "summary"], artifact_prefix, path))
    return results


def validate_protocol_jig_adequacy_report(artifact: dict[str, Any], prefix: str, path: str) -> list[CheckResult]:
    results: list[CheckResult] = []
    state_ids, state_results = validate_protocol_state_graph(artifact, prefix, path)
    results.extend(state_results)
    claim_ids, claim_results = validate_protocol_claims(artifact, prefix, path)
    results.extend(claim_results)
    results.extend(validate_protocol_target(artifact, prefix, path, state_ids, claim_ids))
    target = artifact.get("target")
    if isinstance(target, dict) and target.get("type") not in CAPABILITY_PROTOCOL_JIG_TARGET_TYPES:
        results.append(CheckResult(f"{prefix}:target:type", False, "jig_adequacy_report target.type must be clean_room_jig_surface", path))
    controls, control_results = validate_protocol_record_list(artifact, "control", prefix, path)
    results.extend(control_results)
    dispositions: set[str] = set()
    for control in controls:
        control_prefix = f"{prefix}:control:{control.get('id', 'unknown')}"
        results.extend(validate_string_fields(control, ["id", "name", "category", "disposition", "selected_rigor_impact"], control_prefix, path))
        disposition = control.get("disposition")
        if non_empty_string(disposition):
            if disposition not in JIG_CONTROL_DISPOSITIONS:
                results.append(CheckResult(f"{control_prefix}:disposition", False, "invalid control disposition", path))
            else:
                dispositions.add(str(disposition))
        if not non_empty_string_list(control.get("evidence_refs")):
            results.append(CheckResult(f"{control_prefix}:evidence_refs", False, "evidence_refs must be a non-empty list of strings", path))
    missing_dispositions = sorted(JIG_CONTROL_DISPOSITIONS - dispositions)
    if missing_dispositions:
        results.append(
            CheckResult(
                f"{prefix}:control_dispositions",
                False,
                f"missing control dispositions: {', '.join(missing_dispositions)}",
                path,
            )
        )
    return results


def validate_protocol_artifact(root: Path, label: str, relative_path: Path, expected_kind: str) -> list[CheckResult]:
    prefix = f"capability_profiling_protocol:example:{label}"
    ok, detail, path = path_status(root, relative_path, expected_kind="file")
    if not ok:
        missing_detail = "missing protocol example" if detail in {"missing", "not a file"} else detail
        return [CheckResult(f"{prefix}:path", False, missing_detail, relative_path.as_posix())]
    try:
        artifact = load_toml(path)
    except tomllib.TOMLDecodeError as error:
        return [CheckResult(f"{prefix}:toml", False, f"TOML invalid: {error.msg}", relative_path.as_posix())]
    results: list[CheckResult] = []
    results.extend(validate_string_fields(artifact, ["schema_version", "artifact_kind", "id", "title", "status", "protocol_version"], prefix, relative_path.as_posix()))
    if artifact.get("schema_version") != CAPABILITY_PROTOCOL_SCHEMA_VERSION:
        results.append(CheckResult(f"{prefix}:schema_version", False, f"must be {CAPABILITY_PROTOCOL_SCHEMA_VERSION}", relative_path.as_posix()))
    if artifact.get("artifact_kind") != expected_kind:
        results.append(CheckResult(f"{prefix}:artifact_kind", False, f"must be {expected_kind}", relative_path.as_posix()))
    if expected_kind == "study_plan":
        results.extend(validate_protocol_study_plan(artifact, prefix, relative_path.as_posix()))
    elif expected_kind == "study_report":
        results.extend(validate_protocol_study_report(root, artifact, prefix, relative_path.as_posix()))
    elif expected_kind == "jig_adequacy_report":
        results.extend(validate_protocol_jig_adequacy_report(artifact, prefix, relative_path.as_posix()))
    if not any(not result.ok for result in results):
        results.append(CheckResult(prefix, True, "valid", relative_path.as_posix()))
    return results


def validate_capability_profiling_protocol(root: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    results.extend(
        validate_protocol_document(
            root,
            CAPABILITY_PROTOCOL_SPEC_PATH,
            "spec",
            [
                "Capability Profiling Protocol",
                "Capability State Graph",
                "Capability Analysis Angle",
                "permitted effects",
                "does not execute studies or certify inference-heavy conclusions",
            ],
        )
    )
    results.extend(
        validate_protocol_document(
            root,
            CAPABILITY_PROTOCOL_SCHEMA_PATH,
            "schema",
            [
                CAPABILITY_PROTOCOL_SCHEMA_VERSION,
                "study_plan",
                "study_report",
                "jig_adequacy_report",
                "claimed, verified, unsupported, or unknown",
            ],
        )
    )
    for label, (relative_path, expected_kind) in CAPABILITY_PROTOCOL_EXAMPLES.items():
        results.extend(validate_protocol_artifact(root, label, relative_path, expected_kind))
    return results


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
    schema_pressure_ids = load_schema_pressure_report_ids(root)
    for harness_id in sorted(REQUIRED_HARNESSES):
        results.extend(validate_profile(root, harness_id, schema_pressure_ids))
    results.extend(validate_summary(root))
    results.extend(validate_research_outputs(root))
    results.extend(validate_capability_profiling_protocol(root))
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
        "The profiles preserve source-backed version, component, scheduling, limitation, uncertainty, refresh-note, local-observation, claim-triage, and enrichment fields. No local harness binaries, workspace configs, gateways, plugin installs, cloud agents, or automation state were inspected during the issue #45 profile refresh.",
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


def refresh_effect_records(payload: dict[str, Any], default_effect: str = "passive_scanning") -> list[dict[str, str]]:
    effects = payload.get("effects")
    effectful_evidence = bool(payload.get("local_observations") or payload.get("study_reports"))
    if effects is None or effects == []:
        if effectful_evidence:
            raise ManagerError("effects must be explicit when scout input includes local observations or study reports")
        return [{"effect": default_effect, "classification_ref": "default-passive", "approval_ref": "not-required"}]
    if not isinstance(effects, list):
        raise ManagerError("effects must be a list")
    records: list[dict[str, str]] = []
    for index, effect_record in enumerate(effects):
        if not isinstance(effect_record, dict):
            raise ManagerError(f"effects[{index}] must be an object")
        effect = effect_record.get("effect")
        if effect not in CAPABILITY_PROTOCOL_EFFECTS:
            raise ManagerError(f"effects[{index}]: invalid effect")
        classification_ref = effect_record.get("classification_ref", "")
        approval_ref = effect_record.get("approval_ref", "")
        if classification_ref is None:
            classification_ref = ""
        if approval_ref is None:
            approval_ref = ""
        if not isinstance(classification_ref, str):
            raise ManagerError(f"effects[{index}].classification_ref must be a string")
        if not isinstance(approval_ref, str):
            raise ManagerError(f"effects[{index}].approval_ref must be a string")
        records.append(
            {
                "effect": str(effect),
                "classification_ref": classification_ref,
                "approval_ref": approval_ref,
            }
        )
    return records


def require_effect_approval(
    effects: list[dict[str, str]],
    *,
    allowed_effects: set[str],
    security_ref: str,
    approval_ref: str,
    allow_embedded_approval: bool = True,
) -> list[dict[str, str]]:
    blocked: list[str] = []
    approved_records: list[dict[str, str]] = []
    for record in effects:
        effect = record["effect"]
        if effect == "passive_scanning":
            approved_records.append(record)
            continue
        record_security = record.get("classification_ref", "")
        record_approval = record.get("approval_ref", "")
        cli_approved = effect in allowed_effects and bool(security_ref.strip()) and bool(approval_ref.strip())
        record_approved = allow_embedded_approval and bool(record_security.strip()) and bool(record_approval.strip())
        if cli_approved:
            approved_records.append({"effect": effect, "classification_ref": security_ref, "approval_ref": approval_ref})
        elif record_approved:
            approved_records.append(record)
        else:
            blocked.append(effect)
    if blocked:
        raise ManagerError(f"approval required for effects: {', '.join(sorted(set(blocked)))}")
    return approved_records


def normalized_refresh_records(payload: dict[str, Any], key: str) -> list[dict[str, Any]]:
    records = payload.get(key, [])
    if records is None:
        return []
    if not isinstance(records, list):
        raise ManagerError(f"{key} must be a list")
    normalized: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ManagerError(f"{key}[{index}] must be an object")
        record_id = record.get("id")
        if not non_empty_string(record_id):
            raise ManagerError(f"{key}[{index}].id must be a non-empty string")
        summary = record.get("summary")
        if not non_empty_string(summary):
            raise ManagerError(f"{key}[{index}].summary must be a non-empty string")
        if "claim_refs" in record:
            claim_refs = record.get("claim_refs")
            if not isinstance(claim_refs, list):
                raise ManagerError(f"{key}[{index}].claim_refs must be a list")
            for claim_index, claim_ref in enumerate(claim_refs):
                if not non_empty_string(claim_ref):
                    raise ManagerError(f"{key}[{index}].claim_refs[{claim_index}] must be a non-empty string")
        normalized.append(record)
    return normalized


def refresh_scout(
    root: Path,
    *,
    input_path: str,
    output_path: str | None,
    allowed_effects: set[str],
    security_ref: str,
    approval_ref: str,
) -> dict[str, Any]:
    payload, _path, input_relative = load_json_file(root, input_path, expected_schema=REFRESH_SCOUT_INPUT_SCHEMA)
    harness_id = payload.get("harness_id")
    if harness_id not in REQUIRED_HARNESSES:
        raise ManagerError("harness_id must name a supported harness")
    effects = require_effect_approval(
        refresh_effect_records(payload),
        allowed_effects=allowed_effects,
        security_ref=security_ref,
        approval_ref=approval_ref,
    )
    sources = normalized_refresh_records(payload, "sources")
    for index, source in enumerate(sources):
        if source.get("kind") not in REFRESH_SOURCE_KINDS:
            raise ManagerError(f"sources[{index}].kind must be one of {', '.join(sorted(REFRESH_SOURCE_KINDS))}")
        if not valid_http_url(source.get("url")):
            raise ManagerError(f"sources[{index}].url must be an http(s) URL")
    local_observations = normalized_refresh_records(payload, "local_observations")
    study_reports = normalized_refresh_records(payload, "study_reports")
    for report in study_reports:
        report_path = report.get("path")
        if non_empty_string(report_path):
            user_path(root, str(report_path), expected_kind="file")
    evidence_notes = normalized_refresh_records(payload, "evidence_notes")
    hypotheses = normalized_refresh_records(payload, "hypotheses")
    unknowns = normalized_refresh_records(payload, "unknowns")
    evidence_counts = {
        "first_party_source": sum(1 for source in sources if source.get("kind") == "first_party_source"),
        "fallback_source": sum(1 for source in sources if source.get("kind") == "fallback_source"),
        "local_observation": len(local_observations),
        "selected_study_report": sum(1 for report in study_reports if report.get("selected") is True),
        "curated_evidence_note": len(evidence_notes),
        "hypothesis": len(hypotheses),
        "unknown": len(unknowns),
    }
    durable_candidates = [
        note["id"]
        for note in evidence_notes
        if note.get("durability") in {"curated_durable_evidence", "durable_project_evidence"}
    ]
    result: dict[str, Any] = {
        "schema": REFRESH_SCOUT_REPORT_SCHEMA,
        "result": "scouted",
        "dry_run": True,
        "canonical_profile_mutation": False,
        "input_path": input_relative.as_posix(),
        "harness_id": harness_id,
        "checked_at": payload.get("checked_at", ""),
        "effects": effects,
        "evidence_counts": evidence_counts,
        "sources": sources,
        "local_observations": local_observations,
        "selected_study_reports": [report for report in study_reports if report.get("selected") is True],
        "evidence_notes": evidence_notes,
        "hypotheses": hypotheses,
        "unknowns": unknowns,
        "durable_evidence_candidates": durable_candidates,
        "scratch_disposition": payload.get(
            "scratch_disposition",
            "raw scout artifacts are instance-scoped scratch unless explicitly promoted",
        ),
    }
    write = write_json_file(root, output_path, result)
    if write is not None:
        result["writes"] = [write]
    return result


def claim_refs_from(records: Any, record_key: str) -> set[str]:
    if not isinstance(records, list):
        raise ManagerError(f"{record_key} must be a list")
    refs: set[str] = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ManagerError(f"{record_key}[{index}] must be an object")
        claim_refs = record.get("claim_refs", [])
        if not isinstance(claim_refs, list):
            raise ManagerError(f"{record_key}[{index}].claim_refs must be a list")
        for ref_index, ref in enumerate(claim_refs):
            if not non_empty_string(ref):
                raise ManagerError(f"{record_key}[{index}].claim_refs[{ref_index}] must be a non-empty string")
            refs.add(str(ref))
    return refs


VERSION_TOKEN_PATTERN = re.compile(r"(?<!\d)(?:[A-Za-z]+-v|v)?(?P<version>\d+(?:\.\d+)+(?:[-+][0-9A-Za-z.-]+)?)")


def version_tokens(value: str) -> set[str]:
    return {match.group("version") for match in VERSION_TOKEN_PATTERN.finditer(value)}


def observed_version_changed(observed_version: str, checked_version: str) -> bool:
    observed_tokens = version_tokens(observed_version)
    checked_tokens = version_tokens(checked_version)
    if observed_tokens and checked_tokens:
        return observed_tokens.isdisjoint(checked_tokens)
    return observed_version.strip() != checked_version.strip()


def refresh_analyze(root: Path, *, scout_report_path: str, output_path: str | None) -> dict[str, Any]:
    scout, _path, scout_relative = load_json_file(root, scout_report_path, expected_schema=REFRESH_SCOUT_REPORT_SCHEMA)
    harness_id = scout.get("harness_id")
    if harness_id not in REQUIRED_HARNESSES:
        raise ManagerError("scout report harness_id must name a supported harness")
    profile = load_profile(root, str(harness_id))
    checked_version = str(profile.get("checked_version", ""))
    observed_versions = [
        str(source["observed_version"])
        for source in scout.get("sources", [])
        if isinstance(source, dict) and non_empty_string(source.get("observed_version"))
    ]
    changed_versions = [version for version in observed_versions if observed_version_changed(version, checked_version)]
    version_delta = {
        "current_profile_version": checked_version,
        "observed_versions": observed_versions,
        "disposition": "changed" if changed_versions else "unchanged",
    }
    source_claim_refs = claim_refs_from(scout.get("sources", []), "sources")
    hypothesis_claim_refs = claim_refs_from(scout.get("hypotheses", []), "hypotheses")
    unknown_claim_refs = claim_refs_from(scout.get("unknowns", []), "unknowns")
    similar_by_family: dict[str, list[str]] = {}
    for other in load_profiles(root):
        if other.get("harness_id") == harness_id:
            continue
        for claim in other.get("claim", []):
            if claim.get("status") == "supported":
                similar_by_family.setdefault(str(claim.get("family", "")), []).append(
                    f"{other.get('harness_id')}:{claim.get('id')}"
                )
    claim_triage: list[dict[str, Any]] = []
    for claim in profile.get("claim", []):
        claim_ref = str(claim.get("id", ""))
        family = str(claim.get("family", ""))
        if claim_ref in unknown_claim_refs or claim.get("status") == "unknown":
            triage = "keep_visible"
            rationale = "Claim remains uncertain or has explicit unknown refresh evidence."
        elif changed_versions and (claim_ref in source_claim_refs or claim_ref in hypothesis_claim_refs):
            triage = "deeper_review"
            rationale = "Refresh evidence indicates a version or source delta for this claim."
        elif changed_versions and family in {"lifecycle_reload_update", "runtime_modes", "permissions_approvals_sandboxing"}:
            triage = "deeper_review"
            rationale = "Version delta affects a material integration surface."
        elif claim.get("status") in {"unsupported", "not-applicable"}:
            triage = str(claim.get("status"))
            rationale = "Existing explicit non-support disposition can be retained unless new evidence changes it."
        else:
            triage = "accept_reuse"
            rationale = "Existing claim is well-grounded and no direct delta was reported."
        claim_triage.append(
            {
                "claim_id": claim_ref,
                "family": family,
                "current_status": claim.get("status", ""),
                "prior_evidence_basis": claim.get("evidence_basis", ""),
                "triage": triage,
                "rationale": rationale,
                "similar_claims": similar_by_family.get(family, [])[:3],
            }
        )
    schema_pressure_ids = sorted(load_schema_pressure_report_ids(root) or [])
    follow_ups = [
        {
            "title": f"[high] Refresh {profile.get('display_name')} {unknown.get('id')} unknown",
            "source_id": unknown.get("id", ""),
            "rationale": unknown.get("summary", ""),
        }
        for unknown in scout.get("unknowns", [])
        if isinstance(unknown, dict) and unknown.get("follow_up") is True
    ]
    result: dict[str, Any] = {
        "schema": REFRESH_ANALYSIS_REPORT_SCHEMA,
        "result": "analyzed",
        "dry_run": True,
        "canonical_profile_mutation": False,
        "scout_report_path": scout_relative.as_posix(),
        "harness_id": harness_id,
        "profile_path": profile_path(str(harness_id)).as_posix(),
        "version_delta": version_delta,
        "claim_triage": claim_triage,
        "schema_pressure": [{"id": item, "disposition": "known"} for item in schema_pressure_ids],
        "follow_up_issue_candidates": follow_ups,
        "scratch_disposition": scout.get("scratch_disposition", ""),
    }
    write = write_json_file(root, output_path, result)
    if write is not None:
        result["writes"] = [write]
    return result


def allowed_mutation_path(relative_path: str) -> bool:
    return any(relative_path.startswith(prefix) for prefix in REFRESH_MUTATION_PATH_PREFIXES)


def refresh_plan_harness_id(plan: dict[str, Any]) -> str:
    harness_id = plan.get("harness_id")
    if harness_id not in REQUIRED_HARNESSES:
        raise ManagerError("plan harness_id must name a supported harness")
    return str(harness_id)


def refresh_plan_mutations(plan: dict[str, Any]) -> list[dict[str, Any]]:
    raw_mutations = plan.get("mutations", [])
    if not isinstance(raw_mutations, list):
        raise ManagerError("plan mutations must be a list")
    mutations: list[dict[str, Any]] = []
    seen_paths: set[str] = set()
    for mutation in raw_mutations:
        if not isinstance(mutation, dict) or mutation.get("type") != "replace_file":
            raise ManagerError("plan contains unsupported mutation")
        raw_path = mutation.get("path")
        if not non_empty_string(raw_path):
            raise ManagerError("mutation missing path")
        path = Path(str(raw_path)).as_posix()
        if path in seen_paths:
            raise ManagerError(f"duplicate mutation for path: {path}")
        seen_paths.add(path)
        mutations.append(mutation)
    return mutations


def validate_refresh_mutation_scope(plan_harness_id: str, mutation: dict[str, Any]) -> Path:
    relative = Path(str(mutation.get("path", "")))
    if invalid_relative_path(relative) or not allowed_mutation_path(relative.as_posix()):
        raise ManagerError(f"{relative.as_posix()}: mutation path not allowed")
    if "harness_id" in mutation:
        mutation_harness_id = mutation.get("harness_id")
        if not non_empty_string(mutation_harness_id):
            raise ManagerError(f"{relative.as_posix()}: mutation harness_id must be a non-empty string")
        if mutation_harness_id != plan_harness_id:
            raise ManagerError(f"{relative.as_posix()}: mutation harness_id must match plan harness_id")
    if relative.as_posix().startswith(VANILLA_PROFILE_DIR.as_posix() + "/") and relative.stem != plan_harness_id:
        raise ManagerError(f"{relative.as_posix()}: mutation path must match plan harness_id")
    return relative


def report_harness_id(payload: dict[str, Any], artifact_name: str) -> str:
    harness_id = payload.get("harness_id")
    if harness_id not in REQUIRED_HARNESSES:
        raise ManagerError(f"{artifact_name} harness_id must name a supported harness")
    return str(harness_id)


def validation_result_passed(payload: dict[str, Any]) -> bool:
    if payload.get("schema") not in SUPPORTED_REFRESH_VALIDATION_SCHEMAS:
        return False
    if payload.get("result") != "passed":
        return False
    results = payload.get("results")
    if isinstance(results, list):
        return bool(results) and all(isinstance(result, dict) and result.get("ok") is True for result in results)
    return False


def validation_result_summary(payload: dict[str, Any], relative: Path) -> dict[str, Any]:
    results = payload.get("results", [])
    check_count = len(results) if isinstance(results, list) else 0
    failed_count = (
        sum(1 for result in results if not (isinstance(result, dict) and result.get("ok") is True))
        if isinstance(results, list)
        else 0
    )
    passed = validation_result_passed(payload)
    return {
        "path": relative.as_posix(),
        "schema": str(payload.get("schema", "")),
        "result": "passed" if passed else "failed",
        "checks": check_count,
        "failed": failed_count,
    }


def empty_claim_change_summary() -> dict[str, int]:
    return {
        "added": 0,
        "changed": 0,
        "retired": 0,
        "unsupported": 0,
        "not_applicable": 0,
        "unknown": 0,
        "accepted_reuse": 0,
    }


def profile_claims_by_id(profile: dict[str, Any]) -> dict[str, dict[str, Any]]:
    claims = profile.get("claim", [])
    if not isinstance(claims, list):
        return {}
    return {
        str(claim["id"]): claim
        for claim in claims
        if isinstance(claim, dict) and non_empty_string(claim.get("id"))
    }


def profile_claim_change_summary(before_content: str, after_content: str) -> dict[str, int]:
    before_claims = profile_claims_by_id(tomllib.loads(before_content))
    after_claims = profile_claims_by_id(tomllib.loads(after_content))
    summary = empty_claim_change_summary()
    before_ids = set(before_claims)
    after_ids = set(after_claims)
    added_ids = after_ids - before_ids
    retired_ids = before_ids - after_ids
    changed_ids = {claim_id for claim_id in before_ids & after_ids if before_claims[claim_id] != after_claims[claim_id]}
    summary["added"] = len(added_ids)
    summary["retired"] = len(retired_ids)
    summary["changed"] = len(changed_ids)
    affected_after_ids = added_ids | changed_ids
    for claim_id in affected_after_ids:
        status = str(after_claims[claim_id].get("status", "unknown"))
        if status == "unsupported":
            summary["unsupported"] += 1
        elif status == "not-applicable":
            summary["not_applicable"] += 1
        elif status == "unknown":
            summary["unknown"] += 1
    return summary


def sum_claim_change_summaries(summaries: list[dict[str, Any]]) -> dict[str, int]:
    total = empty_claim_change_summary()
    for summary in summaries:
        if not isinstance(summary, dict):
            continue
        for key in total:
            value = summary.get(key, 0)
            if isinstance(value, int):
                total[key] += value
    return total


def parse_replacement_arg(value: str) -> tuple[str, Path]:
    if ":" not in value:
        raise ManagerError("--profile-replacement must use harness_id:path")
    harness_id, raw_path = value.split(":", 1)
    if harness_id not in REQUIRED_HARNESSES:
        raise ManagerError("--profile-replacement harness_id must name a supported harness")
    return harness_id, Path(raw_path)


def refresh_plan(
    root: Path,
    *,
    analysis_report_path: str,
    profile_replacements: list[str],
    output_path: str | None,
) -> dict[str, Any]:
    analysis, _analysis_path, analysis_relative = load_json_file(
        root, analysis_report_path, expected_schema=REFRESH_ANALYSIS_REPORT_SCHEMA
    )
    analysis_harness_id = analysis.get("harness_id")
    if analysis_harness_id not in REQUIRED_HARNESSES:
        raise ManagerError("analysis report harness_id must name a supported harness")
    mutations: list[dict[str, Any]] = []
    schema_pressure_ids = load_schema_pressure_report_ids(root)
    seen_targets: set[str] = set()
    for replacement_arg in profile_replacements:
        harness_id, replacement_path_raw = parse_replacement_arg(replacement_arg)
        if harness_id != analysis_harness_id:
            raise ManagerError("--profile-replacement harness_id must match analysis report harness_id")
        replacement_path, replacement_relative = user_path(root, str(replacement_path_raw), expected_kind="file")
        try:
            replacement_profile = load_toml(replacement_path)
        except tomllib.TOMLDecodeError as error:
            raise ManagerError(f"{replacement_relative.as_posix()}: TOML invalid: {error.msg}") from error
        results = validate_profile_data(
            replacement_profile,
            harness_id,
            replacement_relative,
            require_enrichment=True,
            schema_pressure_ids=schema_pressure_ids,
        )
        failures = [result for result in results if not result.ok]
        if failures:
            raise ManagerError(f"{replacement_relative.as_posix()}: replacement profile failed validation: {failures[0].name}")
        target_relative = profile_path(harness_id)
        if not allowed_mutation_path(target_relative.as_posix()):
            raise ManagerError(f"{target_relative.as_posix()}: mutation path not allowed")
        target_key = target_relative.as_posix()
        if target_key in seen_targets:
            raise ManagerError(f"duplicate mutation for path: {target_key}")
        seen_targets.add(target_key)
        current_path = checked_read_file(root, target_relative)
        current_content = current_path.read_text(encoding="utf-8")
        planned_content = replacement_path.read_text(encoding="utf-8")
        mutations.append(
            {
                "type": "replace_file",
                "harness_id": harness_id,
                "path": target_relative.as_posix(),
                "source_path": replacement_relative.as_posix(),
                "precondition_sha256": hashlib.sha256(current_content.encode("utf-8")).hexdigest(),
                "planned_sha256": hashlib.sha256(planned_content.encode("utf-8")).hexdigest(),
                "claim_change_summary": profile_claim_change_summary(current_content, planned_content),
                "content": planned_content,
            }
        )
    result: dict[str, Any] = {
        "schema": REFRESH_UPDATE_PLAN_SCHEMA,
        "result": "planned",
        "dry_run": True,
        "analysis_report_path": analysis_relative.as_posix(),
        "harness_id": analysis_harness_id,
        "mutations": mutations,
        "effect_requirements": [
            {
                "effect": "profile_mutation",
                "classification_ref": "",
                "approval_ref": "",
            }
        ]
        if mutations
        else [],
        "claim_triage": analysis.get("claim_triage", []),
        "schema_migrations": [],
        "evidence_promotions": [],
        "follow_up_issue_candidates": analysis.get("follow_up_issue_candidates", []),
        "validation_commands": [
            "python3.14 tools/harness_capability_profiles.py validate --json",
            "python3.14 tools/validate_armory_integrity.py --json",
            "git diff --check",
        ],
    }
    write = write_json_file(root, output_path, result)
    if write is not None:
        result["writes"] = [write]
    return result


def refresh_diff(root: Path, *, plan_path: str) -> dict[str, Any]:
    plan, _path, plan_relative = load_json_file(root, plan_path, expected_schema=REFRESH_UPDATE_PLAN_SCHEMA)
    plan_harness_id = refresh_plan_harness_id(plan)
    diffs: list[dict[str, Any]] = []
    for mutation in refresh_plan_mutations(plan):
        relative = validate_refresh_mutation_scope(plan_harness_id, mutation)
        current_path = checked_read_file(root, relative)
        current_text = current_path.read_text(encoding="utf-8")
        planned_text = str(mutation.get("content", ""))
        unified = "".join(
            difflib.unified_diff(
                current_text.splitlines(keepends=True),
                planned_text.splitlines(keepends=True),
                fromfile=f"current/{relative.as_posix()}",
                tofile=f"planned/{relative.as_posix()}",
            )
        )
        diffs.append(
            {
                "path": relative.as_posix(),
                "precondition_matches": file_sha256(current_path) == mutation.get("precondition_sha256"),
                "unified_diff": unified,
            }
        )
    return {
        "schema": REFRESH_DIFF_SCHEMA,
        "result": "diffed",
        "dry_run": True,
        "plan_path": plan_relative.as_posix(),
        "diffs": diffs,
    }


def refresh_apply(
    root: Path,
    *,
    plan_path: str,
    allowed_effects: set[str],
    security_ref: str,
    approval_ref: str,
) -> dict[str, Any]:
    plan, _path, plan_relative = load_json_file(root, plan_path, expected_schema=REFRESH_UPDATE_PLAN_SCHEMA)
    plan_harness_id = refresh_plan_harness_id(plan)
    mutations = refresh_plan_mutations(plan)
    effect_requirements = plan.get("effect_requirements", [])
    if (
        mutations
        and isinstance(effect_requirements, list)
        and not any(isinstance(record, dict) and record.get("effect") == "profile_mutation" for record in effect_requirements)
    ):
        effect_requirements = list(effect_requirements) + [
            {"effect": "profile_mutation", "classification_ref": "", "approval_ref": ""}
        ]
    effects = require_effect_approval(
        refresh_effect_records({"effects": effect_requirements}, default_effect="profile_mutation"),
        allowed_effects=allowed_effects,
        security_ref=security_ref,
        approval_ref=approval_ref,
        allow_embedded_approval=False,
    )
    validated_targets: list[tuple[Path, str]] = []
    for mutation in mutations:
        relative = validate_refresh_mutation_scope(plan_harness_id, mutation)
        planned_content = str(mutation.get("content", ""))
        planned_hash = hashlib.sha256(planned_content.encode("utf-8")).hexdigest()
        if planned_hash != mutation.get("planned_sha256"):
            raise ManagerError(f"{relative.as_posix()}: planned content hash mismatch")
        if relative.as_posix().startswith(VANILLA_PROFILE_DIR.as_posix() + "/"):
            try:
                planned_profile = tomllib.loads(planned_content)
            except tomllib.TOMLDecodeError as error:
                raise ManagerError(f"{relative.as_posix()}: planned profile TOML invalid: {error.msg}") from error
            harness_id = str(mutation.get("harness_id", relative.stem))
            results = validate_profile_data(
                planned_profile,
                harness_id,
                relative,
                require_enrichment=True,
                schema_pressure_ids=load_schema_pressure_report_ids(root),
            )
            failures = [result for result in results if not result.ok]
            if failures:
                raise ManagerError(f"{relative.as_posix()}: planned profile failed validation: {failures[0].name}")
        current_path = checked_read_file(root, relative)
        current_hash = file_sha256(current_path)
        if current_hash != mutation.get("precondition_sha256"):
            raise ManagerError(f"{relative.as_posix()}: stale plan precondition")
        validated_targets.append((relative, planned_content))
    writes: list[str] = []
    for relative, planned_content in validated_targets:
        target = checked_write_file(root, relative)
        target.write_text(planned_content, encoding="utf-8")
        writes.append(relative.as_posix())
    return {
        "schema": REFRESH_APPLY_SCHEMA,
        "result": "applied",
        "dry_run": False,
        "plan_path": plan_relative.as_posix(),
        "effects": effects,
        "writes": writes,
    }


def refresh_audit(
    root: Path,
    *,
    scout_report_path: str,
    analysis_report_path: str,
    plan_path: str,
    apply_result_path: str | None,
    validation_result_paths: list[str],
    output_path: str | None,
) -> dict[str, Any]:
    scout, _scout_path, scout_relative = load_json_file(root, scout_report_path, expected_schema=REFRESH_SCOUT_REPORT_SCHEMA)
    analysis, _analysis_path, analysis_relative = load_json_file(
        root, analysis_report_path, expected_schema=REFRESH_ANALYSIS_REPORT_SCHEMA
    )
    plan, _plan_path, plan_relative = load_json_file(root, plan_path, expected_schema=REFRESH_UPDATE_PLAN_SCHEMA)
    artifact_harness_ids = {
        report_harness_id(scout, "scout report"),
        report_harness_id(analysis, "analysis report"),
        refresh_plan_harness_id(plan),
    }
    if len(artifact_harness_ids) != 1:
        raise ManagerError("refresh audit artifacts must share harness_id")
    mutations = refresh_plan_mutations(plan)
    planned_paths = [validate_refresh_mutation_scope(next(iter(artifact_harness_ids)), mutation).as_posix() for mutation in mutations]
    applied_writes: list[str] = []
    apply_relative: Path | None = None
    if apply_result_path is not None:
        apply_result, _apply_path, apply_relative = load_json_file(
            root, apply_result_path, expected_schema=REFRESH_APPLY_SCHEMA
        )
        if apply_result.get("plan_path") != plan_relative.as_posix():
            raise ManagerError("refresh audit apply result must reference the audited plan")
        raw_writes = apply_result.get("writes", [])
        if not isinstance(raw_writes, list) or not all(isinstance(write, str) for write in raw_writes):
            raise ManagerError("refresh audit apply result writes must be a string list")
        applied_writes = raw_writes
    elif planned_paths:
        raise ManagerError("refresh audit requires apply result for mutation plans")
    if apply_result_path is not None and sorted(applied_writes) != sorted(planned_paths):
        raise ManagerError("refresh audit apply result writes must match plan mutations")
    validation_summaries: list[dict[str, Any]] = []
    for raw_validation_path in validation_result_paths:
        validation_result, _validation_path, validation_relative = load_json_file(root, raw_validation_path)
        summary = validation_result_summary(validation_result, validation_relative)
        if summary["result"] != "passed":
            raise ManagerError(f"{validation_relative.as_posix()}: validation result did not pass")
        validation_summaries.append(summary)
    if planned_paths and not validation_summaries:
        raise ManagerError("refresh audit requires validation results for mutation plans")
    if planned_paths and not any(summary.get("schema") == VALIDATION_RESULT_SCHEMA for summary in validation_summaries):
        raise ManagerError("refresh audit requires Manager Core validation result for mutation plans")
    applied_write_set = set(applied_writes)
    claim_change_summary = sum_claim_change_summaries(
        [
            mutation.get("claim_change_summary", {})
            for mutation in mutations
            if isinstance(mutation.get("path"), str) and mutation["path"] in applied_write_set
        ]
    )
    result: dict[str, Any] = {
        "schema": REFRESH_AUDIT_SCHEMA,
        "result": "audited",
        "dry_run": True,
        "scout_report_path": scout_relative.as_posix(),
        "analysis_report_path": analysis_relative.as_posix(),
        "plan_path": plan_relative.as_posix(),
        "apply_result_path": apply_relative.as_posix() if apply_relative is not None else "",
        "sources_checked": [source.get("id", "") for source in scout.get("sources", []) if isinstance(source, dict)],
        "profile_files_planned": planned_paths,
        "profile_files_changed": applied_writes,
        "claim_change_summary": claim_change_summary,
        "claim_triage_summary": analysis.get("claim_triage", []),
        "schema_pressure": analysis.get("schema_pressure", []),
        "selected_rigor_deviations": [
            report.get("rigor_deviation", "")
            for report in scout.get("selected_study_reports", [])
            if isinstance(report, dict) and non_empty_string(report.get("rigor_deviation"))
        ],
        "scratch_evidence_disposition": scout.get("scratch_disposition", ""),
        "validation_results": validation_summaries,
        "validation_commands": plan.get("validation_commands", []),
        "follow_up_disposition": analysis.get("follow_up_issue_candidates", []),
    }
    write = write_json_file(root, output_path, result)
    if write is not None:
        result["writes"] = [write]
    return result


def command_error(schema: str, error: Exception) -> dict[str, Any]:
    return {"schema": schema, "result": "failed", "error": str(error)}


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

    scout_parser = subparsers.add_parser("scout", help="Normalize manual refresh scouting evidence without mutating profiles.")
    scout_parser.add_argument("--input", required=True, help="JSON scout input artifact.")
    scout_parser.add_argument("--write-output", help="Write the normalized scout report JSON to this path.")
    scout_parser.add_argument("--allow-effect", action="append", default=[], help="Approved effect token for this run.")
    scout_parser.add_argument("--security-ref", default="", help="Security/control classification reference for approved effects.")
    scout_parser.add_argument("--approval-ref", default="", help="Operator approval reference for approved effects.")
    scout_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")

    analyze_parser = subparsers.add_parser("analyze", help="Analyze a scout report against current profiles.")
    analyze_parser.add_argument("--scout-report", required=True, help="Scout report JSON artifact.")
    analyze_parser.add_argument("--write-output", help="Write the analysis report JSON to this path.")
    analyze_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")

    plan_parser = subparsers.add_parser("plan", help="Build a reviewable manual refresh update plan.")
    plan_parser.add_argument("--analysis-report", required=True, help="Analysis report JSON artifact.")
    plan_parser.add_argument(
        "--profile-replacement",
        action="append",
        default=[],
        help="Explicit profile replacement in the form harness_id:path.",
    )
    plan_parser.add_argument("--write-output", help="Write the update plan JSON to this path.")
    plan_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")

    diff_parser = subparsers.add_parser("diff", help="Show reviewable diffs for a manual refresh update plan.")
    diff_parser.add_argument("--plan", required=True, help="Update plan JSON artifact.")
    diff_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")

    apply_parser = subparsers.add_parser("apply", help="Apply an explicit manual refresh update plan.")
    apply_parser.add_argument("--plan", required=True, help="Update plan JSON artifact.")
    apply_parser.add_argument("--allow-effect", action="append", default=[], help="Approved effect token for this run.")
    apply_parser.add_argument("--security-ref", default="", help="Security/control classification reference for approved effects.")
    apply_parser.add_argument("--approval-ref", default="", help="Operator approval reference for approved effects.")
    apply_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")

    audit_parser = subparsers.add_parser("audit", help="Summarize a manual refresh run for review and closeout.")
    audit_parser.add_argument("--scout-report", required=True, help="Scout report JSON artifact.")
    audit_parser.add_argument("--analysis-report", required=True, help="Analysis report JSON artifact.")
    audit_parser.add_argument("--plan", required=True, help="Update plan JSON artifact.")
    audit_parser.add_argument("--apply-result", help="Apply result JSON artifact for mutation plans.")
    audit_parser.add_argument(
        "--validation-result",
        action="append",
        default=[],
        help="Passing validation result JSON artifact produced after apply; repeat for multiple validation gates.",
    )
    audit_parser.add_argument("--write-output", help="Write the audit summary JSON to this path.")
    audit_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")

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
    if args.command == "scout":
        try:
            payload = refresh_scout(
                root,
                input_path=args.input,
                output_path=args.write_output,
                allowed_effects=set(args.allow_effect),
                security_ref=args.security_ref,
                approval_ref=args.approval_ref,
            )
        except Exception as error:
            payload = command_error(REFRESH_SCOUT_REPORT_SCHEMA, error)
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print(f"FAIL {error}", file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"Scouted {payload['harness_id']} evidence: {sum(payload['evidence_counts'].values())} records")
        return 0
    if args.command == "analyze":
        try:
            payload = refresh_analyze(root, scout_report_path=args.scout_report, output_path=args.write_output)
        except Exception as error:
            payload = command_error(REFRESH_ANALYSIS_REPORT_SCHEMA, error)
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print(f"FAIL {error}", file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"Analyzed {payload['harness_id']} refresh: {payload['version_delta']['disposition']} version delta")
        return 0
    if args.command == "plan":
        try:
            payload = refresh_plan(
                root,
                analysis_report_path=args.analysis_report,
                profile_replacements=args.profile_replacement,
                output_path=args.write_output,
            )
        except Exception as error:
            payload = command_error(REFRESH_UPDATE_PLAN_SCHEMA, error)
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print(f"FAIL {error}", file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"Planned {len(payload['mutations'])} explicit mutations")
        return 0
    if args.command == "diff":
        try:
            payload = refresh_diff(root, plan_path=args.plan)
        except Exception as error:
            payload = command_error(REFRESH_DIFF_SCHEMA, error)
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print(f"FAIL {error}", file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            for diff_result in payload["diffs"]:
                print(diff_result["unified_diff"], end="")
        return 0
    if args.command == "apply":
        try:
            payload = refresh_apply(
                root,
                plan_path=args.plan,
                allowed_effects=set(args.allow_effect),
                security_ref=args.security_ref,
                approval_ref=args.approval_ref,
            )
        except Exception as error:
            payload = command_error(REFRESH_APPLY_SCHEMA, error)
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print(f"FAIL {error}", file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            for path in payload["writes"]:
                print(f"Wrote {path}")
        return 0
    if args.command == "audit":
        try:
            payload = refresh_audit(
                root,
                scout_report_path=args.scout_report,
                analysis_report_path=args.analysis_report,
                plan_path=args.plan,
                apply_result_path=args.apply_result,
                validation_result_paths=args.validation_result,
                output_path=args.write_output,
            )
        except Exception as error:
            payload = command_error(REFRESH_AUDIT_SCHEMA, error)
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print(f"FAIL {error}", file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"Audited refresh for {payload.get('profile_files_changed', [])}")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
