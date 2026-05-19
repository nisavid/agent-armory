#!/usr/bin/env python3.14
from __future__ import annotations

import argparse
import json
import os
import stat
import sys
import tempfile
import tomllib
from json import JSONDecodeError
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, TextIO


JSONValue = dict[str, Any] | list[Any] | str | int | float | bool | None

LAYER_PRECEDENCE = [
    "equipment defaults",
    "harness or adapter defaults",
    "organization or tracker policy",
    "repository policy",
    "project or issue-set policy",
    "user/operator local overrides",
    "checkout-local state",
    "session overrides",
]

SOURCE_CATEGORIES = {
    "committed durable config",
    "local-only operator config",
    "checkout-local state",
    "session override",
    "generated cache or state",
    "secret reference source",
}

SOURCE_CATEGORY_LOAD_CONTRACT = {
    "committed durable config": {
        "core_discovery": "none",
        "caller_responsibility": "discover, select, order, and pass source paths",
        "input_surfaces": ["--layer", "layer_paths"],
        "provenance_requirement": "agent_equipment_config.layer metadata",
        "secret_resolution": "unresolved metadata only when present",
    },
    "local-only operator config": {
        "core_discovery": "none",
        "caller_responsibility": "discover, select, order, and pass source paths",
        "input_surfaces": ["--layer", "layer_paths"],
        "provenance_requirement": "agent_equipment_config.layer metadata",
        "secret_resolution": "unresolved metadata only when present",
    },
    "checkout-local state": {
        "core_discovery": "none",
        "caller_responsibility": "discover, select, order, and pass source paths",
        "input_surfaces": ["--layer", "layer_paths"],
        "provenance_requirement": "agent_equipment_config.layer metadata",
        "secret_resolution": "unresolved metadata only when present",
    },
    "generated cache or state": {
        "core_discovery": "none",
        "caller_responsibility": "discover, select, order, and pass source paths",
        "input_surfaces": ["--layer", "layer_paths"],
        "provenance_requirement": "agent_equipment_config.layer metadata",
        "secret_resolution": "unresolved metadata only when present",
    },
    "secret reference source": {
        "core_discovery": "none",
        "caller_responsibility": "discover, select, order, and pass source paths",
        "input_surfaces": ["--layer", "layer_paths"],
        "provenance_requirement": "agent_equipment_config.layer metadata",
        "secret_resolution": "unresolved metadata only when present",
    },
    "session override": {
        "core_discovery": "none",
        "caller_responsibility": "discover, select, order, and pass source paths",
        "input_surfaces": ["--layer", "--plain-handoff", "layer_paths", "plain_handoff_paths"],
        "provenance_requirement": "agent_equipment_config.layer metadata or plain handoff promotion record",
        "secret_resolution": "unresolved metadata only when present",
    },
}

MIGRATION_APPLY_SOURCE_CATEGORIES = {
    "committed durable config",
    "local-only operator config",
}

SECRET_REFERENCE_KINDS = {"env", "keychain", "vault", "harness-secret", "external"}
SENSITIVE_KEYWORDS = ("secret", "token", "credential", "password", "api_key", "private_key")
REDACTED = "<redacted>"
REQUIRED_FOR_VALUES = {"advisory", "mutation", "always"}
ONBOARDING_STATES = {"first-run", "interrupted", "resume", "restart"}
BLOCKED_CONFIG_SAFETY_STATUSES = {"conflicted", "untrusted", "stale", "unsafe"}
FIRST_RUN_ONBOARDING_STATUSES = {
    "usable": "complete",
    "incomplete": "missing_config_data",
    "conflicted": "blocked_config",
    "untrusted": "blocked_config",
    "stale": "blocked_config",
    "unsafe": "blocked_config",
}
ABSENT = {"presence": "absent"}
MISSING = object()


class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class Layer:
    name: str
    category: str
    path: str
    precedence: int
    source_order: int
    data: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)
    trusted: bool = True


@dataclass(frozen=True)
class FieldSpec:
    type: str
    required: bool = False
    default: JSONValue = None
    enum: list[JSONValue] | None = None
    deprecated: bool = False
    replacement: str | None = None


@dataclass(frozen=True)
class MigrationPreview:
    from_version: int
    field_renames: dict[str, str]
    note: str


@dataclass(frozen=True)
class SchemaFragment:
    namespace: str
    version: int
    fields: dict[str, FieldSpec]
    semantic_validators: tuple[Callable[[dict[str, Any], str], list["Diagnostic"]], ...] = ()
    migrations: tuple[MigrationPreview, ...] = ()


@dataclass(frozen=True)
class Diagnostic:
    kind: str
    path: str
    detail: str
    layer: str | None = None
    source: str | None = None
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PolicyLock:
    namespace: str
    field: str
    layer: Layer
    required_for: str
    non_overridable: bool = False
    authority: str | None = None


TYPE_CHECKS: dict[str, type | tuple[type, ...]] = {
    "string": str,
    "boolean": bool,
    "object": dict,
    "array": list,
}


def diagnostic(kind: str, path: str, detail: str, layer: Layer | None = None, *, evidence: dict[str, Any] | None = None) -> Diagnostic:
    return Diagnostic(
        kind=kind,
        path=path,
        detail=detail,
        layer=layer.name if layer else None,
        source=layer.path if layer else None,
        evidence=evidence or {},
    )


def type_matches(value: JSONValue, field_type: str) -> bool:
    if value is None:
        return True
    if field_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if field_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if field_type not in TYPE_CHECKS:
        raise ConfigError(f"unsupported field type {field_type!r}")
    return isinstance(value, TYPE_CHECKS[field_type])


def validate_field(value: JSONValue, field: FieldSpec, path: str, layer: Layer | None) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    if not type_matches(value, field.type):
        diagnostics.append(diagnostic("schema conflict", path, f"expected {field.type}", layer))
    if field.enum is not None and value is not None and value not in field.enum:
        diagnostics.append(diagnostic("schema conflict", path, f"expected one of {field.enum!r}", layer))
    if field.deprecated and layer is not None:
        replacement = f"use {path.rsplit('.', 1)[0]}.{field.replacement} instead" if field.replacement else "field is deprecated"
        diagnostics.append(diagnostic("deprecated field", path, replacement, layer))
    return diagnostics


def policy_locks(layer: Layer) -> dict[tuple[str, str], PolicyLock]:
    policy = layer.metadata.get("policy", {})
    if not isinstance(policy, dict):
        raise ConfigError(f"{layer.path}: agent_equipment_config.policy must be a table")
    locks: dict[tuple[str, str], PolicyLock] = {}
    for namespace, fields in policy.items():
        if not isinstance(fields, dict):
            raise ConfigError(f"{layer.path}: agent_equipment_config.policy.{namespace} must be a table")
        for field_name, rule in fields.items():
            if not isinstance(rule, dict):
                raise ConfigError(f"{layer.path}: agent_equipment_config.policy.{namespace}.{field_name} must be a table")
            non_overridable = rule.get("non_overridable", False)
            if not isinstance(non_overridable, bool):
                raise ConfigError(
                    f"{layer.path}: agent_equipment_config.policy.{namespace}.{field_name}.non_overridable must be a boolean"
                )
            authority = rule.get("authority")
            if authority is not None and not isinstance(authority, str):
                raise ConfigError(f"{layer.path}: agent_equipment_config.policy.{namespace}.{field_name}.authority must be a string")
            required_for = rule.get("required_for", "mutation")
            if not isinstance(required_for, str):
                raise ConfigError(f"{layer.path}: agent_equipment_config.policy.{namespace}.{field_name}.required_for must be a string")
            if required_for not in REQUIRED_FOR_VALUES:
                raise ConfigError(
                    f"{layer.path}: agent_equipment_config.policy.{namespace}.{field_name}.required_for must be one of {sorted(REQUIRED_FOR_VALUES)!r}"
                )
            if non_overridable or isinstance(authority, str):
                locks[(namespace, field_name)] = PolicyLock(
                    namespace=namespace,
                    field=field_name,
                    layer=layer,
                    required_for=required_for,
                    non_overridable=non_overridable,
                    authority=authority,
                )
    return locks


def fragment_versions(layer: Layer) -> dict[str, int]:
    versions = layer.metadata.get("fragment_versions", {})
    if not isinstance(versions, dict):
        raise ConfigError(f"{layer.path}: agent_equipment_config.fragment_versions must be a table")
    parsed: dict[str, int] = {}
    for key, value in versions.items():
        if not isinstance(value, int) or isinstance(value, bool):
            raise ConfigError(f"{layer.path}: agent_equipment_config.fragment_versions.{key} must be an integer")
        parsed[str(key)] = value
    return parsed


def raw_values_for_namespace(effective_namespace: dict[str, Any]) -> dict[str, JSONValue]:
    return {
        field_name: wrapped.get("value")
        for field_name, wrapped in effective_namespace.items()
    }


def migration_previews_for_layer(layer: Layer, fragment: SchemaFragment) -> list[dict[str, Any]]:
    source_version = fragment_versions(layer).get(fragment.namespace)
    if source_version is None or source_version >= fragment.version:
        return []
    section = namespace_section(layer, fragment.namespace)
    previews: list[dict[str, Any]] = []
    for migration in fragment.migrations:
        if migration.from_version != source_version:
            continue
        changes = [
            {
                "from": f"{fragment.namespace}.{old_name}",
                "to": f"{fragment.namespace}.{new_name}",
                "value": section[old_name],
            }
            for old_name, new_name in migration.field_renames.items()
            if old_name in section
        ]
        previews.append(
            {
                "namespace": fragment.namespace,
                "source": layer.path,
                "from_version": source_version,
                "to_version": fragment.version,
                "note": migration.note,
                "changes": changes,
                "audit_preview": {
                    "action": "migration apply preview",
                    "source": layer.path,
                    "namespace": fragment.namespace,
                    "from_version": source_version,
                    "to_version": fragment.version,
                    "would_rewrite_source": False,
                },
            }
        )
    if previews:
        return previews
    return [
        {
            "namespace": fragment.namespace,
            "source": layer.path,
            "from_version": source_version,
            "to_version": fragment.version,
            "note": "no registered migration preview",
            "changes": [],
            "audit_preview": {
                "action": "migration apply preview",
                "source": layer.path,
                "namespace": fragment.namespace,
                "from_version": source_version,
                "to_version": fragment.version,
                "would_rewrite_source": False,
            },
        }
    ]


def migration_for_version(fragment: SchemaFragment, source_version: int) -> MigrationPreview | None:
    for migration in fragment.migrations:
        if migration.from_version == source_version:
            return migration
    return None


def migration_source_durability(layer: Layer) -> tuple[str, bool]:
    if layer.category == "committed durable config":
        return ("durable project evidence", True)
    return ("instance-scoped local evidence", False)


def migration_apply_authority(layers: list[Layer], apply_authority: str | None, target_layer: Layer) -> tuple[bool, str]:
    if apply_authority == "operator":
        return True, "operator"
    for layer in layers:
        if not layer.trusted:
            continue
        if layer.precedence > target_layer.precedence:
            continue
        if layer.precedence == target_layer.precedence and layer.source_order > target_layer.source_order:
            continue
        authority_table = layer.metadata.get("authority", {})
        if isinstance(authority_table, dict) and authority_table.get("config_migration_apply") == "usable":
            return True, f"configured:{layer.name}:{layer.path}"
    return False, "not supplied"


def migration_apply_audit_record(
    layer: Layer,
    fragment: SchemaFragment,
    *,
    from_version: int,
    decision: str,
    authority: str | None,
    action: str = "migration apply decision",
    reason: str | None = None,
    result: str | None = None,
) -> dict[str, Any]:
    durability, project_truth = migration_source_durability(layer)
    record: dict[str, Any] = {
        "action": action,
        "decision": decision,
        "source": layer.path,
        "source_layer": layer.name,
        "source_category": layer.category,
        "namespace": fragment.namespace,
        "from_version": from_version,
        "to_version": fragment.version,
        "write_target": layer.path if layer.category in MIGRATION_APPLY_SOURCE_CATEGORIES else None,
        "authority": authority or "not supplied",
        "artifact_durability": durability,
        "project_truth": project_truth,
        "rollback": "restore the source file from version control or the recorded diff",
    }
    if reason is not None:
        record["reason"] = reason
    if result is not None:
        record["result"] = result
    return record


def migration_change_set(layer: Layer, fragment: SchemaFragment, migration: MigrationPreview, source_version: int) -> tuple[list[dict[str, Any]], str | None]:
    section = namespace_section(layer, fragment.namespace)
    changes: list[dict[str, Any]] = []
    for old_name, new_name in migration.field_renames.items():
        if old_name not in section:
            continue
        if new_name in section:
            return ([], f"migration target field already exists: {fragment.namespace}.{new_name}")
        changes.append(
            {
                "operation": "rename field",
                "from": f"{fragment.namespace}.{old_name}",
                "to": f"{fragment.namespace}.{new_name}",
                "value": section[old_name],
            }
        )
    changes.append(
        {
            "operation": "update fragment version",
            "path": f"agent_equipment_config.fragment_versions.{fragment.namespace}",
            "from": source_version,
            "to": fragment.version,
        }
    )
    return (changes, None)


def projected_migrated_layer(layer: Layer, fragment: SchemaFragment, migration: MigrationPreview) -> Layer:
    data = dict(layer.data)
    section = dict(namespace_section(layer, fragment.namespace))
    for old_name, new_name in migration.field_renames.items():
        if old_name in section and new_name not in section:
            section[new_name] = section.pop(old_name)
    data[fragment.namespace] = section
    metadata = dict(layer.metadata)
    versions = dict(fragment_versions(layer))
    versions[fragment.namespace] = fragment.version
    metadata["fragment_versions"] = versions
    return Layer(
        name=layer.name,
        category=layer.category,
        path=layer.path,
        precedence=layer.precedence,
        source_order=layer.source_order,
        data=data,
        metadata=metadata,
        trusted=layer.trusted,
    )


def migration_apply_candidate_keys(
    layers: list[Layer],
    fragments: list[SchemaFragment],
    *,
    apply: bool,
    apply_authority: str | None,
) -> set[tuple[int, str]]:
    candidates: set[tuple[int, str]] = set()
    for layer_index, layer in enumerate(layers):
        authorized, _authority = migration_apply_authority(layers, apply_authority, layer)
        versions = fragment_versions(layer)
        for fragment in fragments:
            source_version = versions.get(fragment.namespace)
            if source_version is None or source_version >= fragment.version:
                continue
            migration = migration_for_version(fragment, source_version)
            if (
                not layer.trusted
                or layer.category not in MIGRATION_APPLY_SOURCE_CATEGORIES
                or migration is None
                or (apply and not authorized)
            ):
                continue
            _changes, reason = migration_change_set(layer, fragment, migration, source_version)
            if reason is None:
                candidates.add((layer_index, fragment.namespace))
    return candidates


def projected_migration_layers(
    layers: list[Layer],
    fragments: list[SchemaFragment],
    *,
    accepted_migrations: set[tuple[int, str]] | None = None,
) -> list[Layer]:
    projected: list[Layer] = []
    for layer_index, layer in enumerate(layers):
        next_layer = layer
        for fragment in fragments:
            if accepted_migrations is not None and (layer_index, fragment.namespace) not in accepted_migrations:
                continue
            versions = fragment_versions(next_layer)
            source_version = versions.get(fragment.namespace)
            if source_version is None or source_version >= fragment.version:
                continue
            migration = migration_for_version(fragment, source_version)
            if migration is None:
                continue
            next_layer = projected_migrated_layer(next_layer, fragment, migration)
        projected.append(next_layer)
    return projected


def toml_header_text(line: str) -> str:
    return line.split("#", 1)[0].strip()


def toml_table_bounds(lines: list[str], table_name: str) -> tuple[int, int]:
    header = f"[{table_name}]"
    start = None
    for index, line in enumerate(lines):
        if toml_header_text(line) == header:
            start = index
            break
    if start is None:
        raise ConfigError(f"could not find TOML table {header}")
    end = len(lines)
    for index in range(start + 1, len(lines)):
        stripped = toml_header_text(lines[index])
        if stripped.startswith("[") and stripped.endswith("]"):
            end = index
            break
    return start, end


def toml_key_line_index(lines: list[str], start: int, end: int, key: str) -> int:
    for index in range(start + 1, end):
        stripped = lines[index].lstrip()
        if not stripped.startswith(key):
            continue
        remainder = stripped[len(key):]
        if remainder and (remainder[0].isspace() or remainder.lstrip().startswith("=")):
            return index
    raise ConfigError(f"could not find TOML key {key!r}")


def rename_toml_key(lines: list[str], table_name: str, old_name: str, new_name: str) -> None:
    start, end = toml_table_bounds(lines, table_name)
    index = toml_key_line_index(lines, start, end, old_name)
    line = lines[index]
    stripped = line.lstrip()
    indent = line[: len(line) - len(stripped)]
    lines[index] = f"{indent}{new_name}{stripped[len(old_name):]}"


def update_toml_integer_key(lines: list[str], table_name: str, key: str, value: int) -> None:
    start, end = toml_table_bounds(lines, table_name)
    index = toml_key_line_index(lines, start, end, key)
    line = lines[index]
    stripped = line.lstrip()
    indent = line[: len(line) - len(stripped)]
    newline = "\n" if line.endswith("\n") else ""
    body = line[:-1] if newline else line
    comment_index = body.find("#")
    comment = f"  {body[comment_index:].strip()}" if comment_index >= 0 else ""
    lines[index] = f"{indent}{key} = {value}{comment}{newline}"


def render_migration_source_from_text(text: str, layer: Layer, fragment: SchemaFragment, migration: MigrationPreview) -> str:
    lines = text.splitlines(keepends=True)
    for old_name, new_name in migration.field_renames.items():
        if old_name in namespace_section(layer, fragment.namespace):
            rename_toml_key(lines, fragment.namespace, old_name, new_name)
    update_toml_integer_key(lines, "agent_equipment_config.fragment_versions", fragment.namespace, fragment.version)
    return "".join(lines)


def atomic_write_text(path: Path, text: str) -> None:
    original_mode = stat.S_IMODE(path.stat().st_mode)
    temporary_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as temporary:
            temporary_path = temporary.name
            temporary.write(text)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.chmod(temporary_path, original_mode)
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None:
            try:
                os.unlink(temporary_path)
            except FileNotFoundError:
                pass


def migration_refusal(
    layer: Layer,
    fragment: SchemaFragment,
    *,
    from_version: int,
    reason: str,
    authority: str | None,
) -> dict[str, Any]:
    record = migration_apply_audit_record(
        layer,
        fragment,
        from_version=from_version,
        decision="refused",
        authority=authority,
        reason=reason,
    )
    return {
        "source": layer.path,
        "source_category": layer.category,
        "namespace": fragment.namespace,
        "from_version": from_version,
        "to_version": fragment.version,
        "reason": reason,
        "audit_record": record,
    }


def migration_apply_safety_refusal_reason(effective: dict[str, Any]) -> str | None:
    diagnostic_kinds = {item.get("kind") for item in effective.get("diagnostics", [])}
    if diagnostic_kinds & {"semantic conflict", "missing authority"}:
        return "effective Config Safety Status is unsafe"
    safety_status = effective["safety_status"]
    if safety_status not in {"stale", "usable"}:
        return f"effective Config Safety Status is {safety_status}"
    return None


def migration_apply(
    layer_paths: list[Path],
    fragments: list[SchemaFragment],
    *,
    apply: bool = False,
    apply_authority: str | None = None,
) -> dict[str, Any]:
    source_snapshots: dict[Path, str] = {}
    layers = load_layers(layer_paths, source_snapshots=source_snapshots)
    effective = effective_config_from_layers(layers, fragments, requested_behavior="mutation")
    accepted_migrations = migration_apply_candidate_keys(
        layers,
        fragments,
        apply=apply,
        apply_authority=apply_authority,
    )
    projected_effective = effective_config_from_layers(
        projected_migration_layers(layers, fragments, accepted_migrations=accepted_migrations),
        fragments,
        requested_behavior="mutation",
    )
    applications: list[dict[str, Any]] = []
    refusals: list[dict[str, Any]] = []
    audit_records: list[dict[str, Any]] = []
    pending_writes: dict[Path, dict[str, Any]] = {}
    for layer in layers:
        authorized, authority = migration_apply_authority(layers, apply_authority, layer)
        versions = fragment_versions(layer)
        for fragment in fragments:
            source_version = versions.get(fragment.namespace)
            if source_version is None or source_version >= fragment.version:
                continue
            migration = migration_for_version(fragment, source_version)
            reason: str | None = None
            if not layer.trusted:
                reason = "source is not trusted for migration apply"
            elif layer.category not in MIGRATION_APPLY_SOURCE_CATEGORIES:
                reason = "source category is not eligible for migration apply"
            elif migration is None:
                reason = "no registered migration for stale schema"
            elif (safety_reason := migration_apply_safety_refusal_reason(projected_effective)) is not None:
                reason = safety_reason
            elif apply and not authorized:
                reason = "missing migration apply authority"
            changes: list[dict[str, Any]] = []
            if reason is None and migration is not None:
                changes, reason = migration_change_set(layer, fragment, migration, source_version)
            if reason is not None:
                refusal = migration_refusal(
                    layer,
                    fragment,
                    from_version=source_version,
                    reason=reason,
                    authority=authority,
                )
                refusals.append(refusal)
                audit_records.append(refusal["audit_record"])
                continue
            decision = "authorized" if apply else "dry-run"
            record = migration_apply_audit_record(
                layer,
                fragment,
                from_version=source_version,
                decision=decision,
                authority=authority,
            )
            application = {
                "source": layer.path,
                "source_layer": layer.name,
                "source_category": layer.category,
                "namespace": fragment.namespace,
                "from_version": source_version,
                "to_version": fragment.version,
                "decision": decision,
                "write_authorized": authorized,
                "dry_run_would_write": not apply,
                "write_performed": False,
                "changes": changes,
                "audit_record": record,
            }
            if apply:
                path = Path(layer.path)
                staged = pending_writes.get(path)
                snapshot_key = path.resolve()
                original_text = source_snapshots[snapshot_key]
                base_text = staged["text"] if staged is not None else original_text
                next_text = render_migration_source_from_text(base_text, layer, fragment, migration)
                if staged is None:
                    staged = {"text": next_text, "original_text": original_text, "items": []}
                    pending_writes[path] = staged
                else:
                    staged["text"] = next_text
                staged["items"].append((application, layer, fragment, source_version, authority))
                audit_records.append(record)
            else:
                audit_records.append(record)
            applications.append(application)
    partial_application = False
    write_failures: list[dict[str, Any]] = []
    if apply and refusals:
        for staged in pending_writes.values():
            for application, _layer, _fragment, _source_version, _authority in staged["items"]:
                application["decision"] = "blocked"
                application["audit_record"]["decision"] = "blocked"
                application["audit_record"]["result"] = "blocked by refusal"
    elif apply:
        for path, staged in pending_writes.items():
            try:
                if path.read_text(encoding="utf-8") != staged["original_text"]:
                    raise ConfigError("source changed since migration planning")
                atomic_write_text(path, staged["text"])
            except (ConfigError, OSError) as exc:
                partial_application = any(item["write_performed"] for item in applications)
                failure = {
                    "source": path.as_posix(),
                    "reason": exc.strerror if isinstance(exc, OSError) and exc.strerror else str(exc),
                }
                write_failures.append(failure)
                for application, _layer, _fragment, _source_version, _authority in staged["items"]:
                    application["decision"] = "write-failed"
                    application["write_failure"] = failure
                break
            for application, layer, fragment, source_version, authority in staged["items"]:
                application["decision"] = "applied"
                application["write_performed"] = True
                mutation_record = migration_apply_audit_record(
                    layer,
                    fragment,
                    from_version=source_version,
                    decision="applied",
                    authority=authority,
                    action="migration apply mutation",
                    result="applied",
                )
                application["mutation_audit_record"] = mutation_record
                audit_records.append(mutation_record)
    return {
        "mode": "apply" if apply else "dry-run",
        "applied": any(application["write_performed"] for application in applications),
        "partial_application": partial_application,
        "applications": applications,
        "refusals": refusals,
        "write_failures": write_failures,
        "audit_records": audit_records,
        "effective_config": effective,
        "projected_effective_config": projected_effective,
    }


def secret_reference(value: JSONValue) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    kind = value.get("kind")
    name = value.get("name")
    if kind in SECRET_REFERENCE_KINDS and isinstance(name, str):
        return {
            "kind": kind,
            "name": name,
            "scope": value.get("scope"),
            "required_for": value.get("required_for"),
            "resolution_status": "unresolved",
        }
    return None


def sensitive_key(key: str) -> bool:
    normalized = key.lower().replace("-", "_")
    return any(keyword in normalized for keyword in SENSITIVE_KEYWORDS)


def sensitive_path(path: Any) -> bool:
    if not isinstance(path, str):
        return False
    parts = path.replace("[", ".").replace("]", "").split(".")
    return any(sensitive_key(part) for part in parts)


def redact_for_cli(value: Any, path: tuple[str, ...] = (), *, sensitive_context: bool = False) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        entry_path_sensitive = any(sensitive_path(value.get(key)) for key in ("path", "from", "to"))
        child_sensitive_context = sensitive_context or entry_path_sensitive
        for key, item in value.items():
            key_text = str(key)
            child_path = (*path, key_text)
            if key_text == "name" and path and path[-1] == "secret_reference":
                redacted[key] = REDACTED
            elif key_text in {"before", "after", "value", "blocked_value"} and child_sensitive_context and not isinstance(item, (dict, list)):
                redacted[key] = REDACTED
            elif key_text == "value" and any(sensitive_key(part) for part in path) and not isinstance(item, (dict, list)):
                redacted[key] = REDACTED
            elif sensitive_key(key_text) and not isinstance(item, (dict, list)):
                redacted[key] = REDACTED
            else:
                redacted[key] = redact_for_cli(item, child_path, sensitive_context=child_sensitive_context)
        return redacted
    if isinstance(value, list):
        list_sensitive = sensitive_context or any(sensitive_key(part) for part in path)
        return [
            REDACTED if list_sensitive and not isinstance(item, (dict, list)) else redact_for_cli(item, (*path, "[]"), sensitive_context=list_sensitive)
            for item in value
        ]
    return value


def diffable_wrapped_value(wrapped: dict[str, Any]) -> JSONValue | dict[str, Any] | object:
    if "secret_reference" in wrapped:
        return {"secret_reference": wrapped["secret_reference"]}
    return wrapped.get("value")


def effective_section(payload: Any, label: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ConfigError(f"{label}: config-diff input must be a JSON object")
    section = payload.get("effective", payload)
    if not isinstance(section, dict):
        raise ConfigError(f"{label}: effective must be a JSON object")
    return section


def namespace_section(layer: Layer, namespace: str) -> dict[str, Any]:
    section = layer.data.get(namespace, {})
    if not isinstance(section, dict):
        raise ConfigError(f"{layer.path}: {namespace} must be a table")
    return section


def diff_namespace_fields(effective: dict[str, Any], namespace: str, label: str) -> dict[str, Any]:
    fields = effective.get(namespace, {})
    if not isinstance(fields, dict):
        raise ConfigError(f"{label}: effective.{namespace} must be a JSON object")
    return fields


def diff_field_value(fields: dict[str, Any], field_name: str, label: str, namespace: str) -> JSONValue | dict[str, Any] | object:
    if field_name not in fields:
        return MISSING
    wrapped = fields[field_name]
    if not isinstance(wrapped, dict):
        raise ConfigError(f"{label}: effective.{namespace}.{field_name} must be a JSON object")
    return diffable_wrapped_value(wrapped)


def public_diff_value(value: JSONValue | dict[str, Any] | object) -> JSONValue | dict[str, Any]:
    if value is MISSING:
        return dict(ABSENT)
    return value


def config_diff(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    changes: list[dict[str, Any]] = []
    before_effective = effective_section(before, "before")
    after_effective = effective_section(after, "after")
    namespaces = sorted(set(before_effective) | set(after_effective))
    for namespace in namespaces:
        before_fields = diff_namespace_fields(before_effective, namespace, "before")
        after_fields = diff_namespace_fields(after_effective, namespace, "after")
        for field_name in sorted(set(before_fields) | set(after_fields)):
            before_value = diff_field_value(before_fields, field_name, "before", namespace)
            after_value = diff_field_value(after_fields, field_name, "after", namespace)
            if before_value != after_value:
                changes.append(
                    {
                        "path": f"{namespace}.{field_name}",
                        "before": public_diff_value(before_value),
                        "after": public_diff_value(after_value),
                    }
                )
    diff: dict[str, Any] = {"changes": changes}
    if before.get("safety_status") != after.get("safety_status"):
        diff["status_change"] = {"before": before.get("safety_status"), "after": after.get("safety_status")}
    if before.get("diagnostics", []) != after.get("diagnostics", []):
        diff["diagnostic_changes"] = {"before": before.get("diagnostics", []), "after": after.get("diagnostics", [])}
    return diff


def load_plain_handoff_layers(paths: Iterable[Path]) -> tuple[list[Layer], list[dict[str, Any]]]:
    layers: list[Layer] = []
    summaries: list[dict[str, Any]] = []
    for index, path in enumerate(paths):
        document = load_toml(path)
        layer = Layer(
            name="session overrides",
            category="session override",
            path=path.as_posix(),
            precedence=LAYER_PRECEDENCE.index("session overrides"),
            source_order=10_000 + index,
            data=document,
            metadata={"plain_handoff": True},
            trusted=True,
        )
        layers.append(layer)
        summaries.append({"source": path.as_posix(), "promoted_to": "session overrides", "category": "session override"})
    return layers, summaries


def lock_precedes_layer(lock: PolicyLock, layer: Layer) -> bool:
    return (
        layer.precedence > lock.layer.precedence
        or (layer.precedence == lock.layer.precedence and layer.source_order > lock.layer.source_order)
    )


def lock_blocks_layer(lock: PolicyLock, layer: Layer, requested_behavior: str) -> bool:
    return (
        lock.required_for in {requested_behavior, "always"}
        and (lock.non_overridable or lock.authority is not None)
        and lock_precedes_layer(lock, layer)
    )


def blocked_override_diagnostic(path: str, layer: Layer, lock: PolicyLock, candidate: JSONValue) -> Diagnostic:
    lock_reason = "non-overridable" if lock.non_overridable else f"authority-gated {lock.authority!r}"
    return diagnostic(
        "blocked override",
        path,
        f"{layer.name} cannot override {lock_reason} value from {lock.layer.name}",
        layer,
        evidence={
            "blocked_value": candidate,
            "blocked_by": {
                "layer": lock.layer.name,
                "source": lock.layer.path,
            },
        },
    )


def authority_is_usable(layers: list[Layer], authority: str, required_by: PolicyLock) -> bool:
    for layer in layers:
        if not layer.trusted:
            continue
        if layer.precedence > required_by.layer.precedence:
            continue
        if layer.precedence == required_by.layer.precedence and layer.source_order > required_by.layer.source_order:
            continue
        authority_table = layer.metadata.get("authority", {})
        if isinstance(authority_table, dict) and authority_table.get(authority) == "usable":
            return True
    return False


def untrusted_authority_diagnostics(layers: list[Layer], authority: str) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for layer in layers:
        if layer.trusted:
            continue
        authority_table = layer.metadata.get("authority", {})
        if isinstance(authority_table, dict) and authority_table.get(authority) == "usable":
            diagnostics.append(
                diagnostic(
                    "untrusted source",
                    f"agent_equipment_config.authority.{authority}",
                    f"{layer.name} is not trusted to authorize mutation",
                    layer,
                    evidence={"authority": authority},
                )
            )
    return diagnostics


def dedupe_diagnostics(diagnostics: list[Diagnostic]) -> list[Diagnostic]:
    deduped: list[Diagnostic] = []
    seen: set[tuple[str, str, str, str | None, str | None, str]] = set()
    for item in diagnostics:
        evidence_key = json.dumps(item.evidence, sort_keys=True)
        key = (item.kind, item.path, item.detail, item.layer, item.source, evidence_key)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def enforcement_projection(safety_status: str, requested_behavior: str) -> dict[str, Any]:
    classification = "blocking" if requested_behavior == "mutation" and safety_status != "usable" else "advisory"
    return {
        "requested_behavior": requested_behavior,
        "classification": classification,
        "enforced_by_harness": False,
    }


def sorted_unique(values: Iterable[Any]) -> list[str]:
    unique: dict[str, None] = {}
    for value in values:
        unique[str(value)] = None
    return sorted(unique)


def list_or_empty(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def fallback_for_behavior(requested_behavior: str) -> str:
    return "advisory dry-run" if requested_behavior == "mutation" else "none"


def consumer_action_decision(
    effective: dict[str, Any],
    *,
    equipment: str,
    requested_behavior: str,
    required_capabilities: Iterable[str] = (),
    supported_capabilities: Iterable[str] = (),
    warning_diagnostic_kinds: Iterable[str] = ("deprecated field",),
) -> dict[str, Any]:
    diagnostics = list_or_empty(effective.get("diagnostics", []))
    migration_previews = list_or_empty(effective.get("migration_previews", []))
    projection_value = effective.get("enforcement_projection", {})
    projection = projection_value if isinstance(projection_value, dict) else {}
    required = sorted_unique(required_capabilities)
    supported = sorted_unique(supported_capabilities)
    supported_set = set(supported)
    unsupported = [capability for capability in required if capability not in supported_set]
    evidence = {
        "safety_status": effective.get("safety_status"),
        "enforcement_projection": projection,
        "diagnostics": diagnostics,
        "migration_previews": migration_previews,
        "required_capabilities": required,
        "supported_capabilities": supported,
        "unsupported_capabilities": unsupported,
    }
    projection_blocking = projection.get("classification") == "blocking"
    safety_blocking = requested_behavior == "mutation" and effective.get("safety_status") != "usable"
    if projection_blocking or safety_blocking:
        diagnostic_kinds = sorted_unique(
            item.get("kind")
            for item in diagnostics
            if isinstance(item, dict) and item.get("kind") is not None
        )
        source = "effective_config.enforcement_projection" if projection_blocking else "effective_config.safety_status"
        reason = (
            "enforcement projection classified requested behavior as blocking"
            if projection_blocking
            else "effective Config Safety Status is not usable for mutation"
        )
        if diagnostic_kinds:
            reason = f"{reason}: {', '.join(diagnostic_kinds)}"
        return {
            "equipment": equipment,
            "requested_behavior": requested_behavior,
            "state": "blocking",
            "source": source,
            "reason": reason,
            "fallback": fallback_for_behavior(requested_behavior),
            "evidence": evidence,
        }
    if unsupported:
        return {
            "equipment": equipment,
            "requested_behavior": requested_behavior,
            "state": "unsupported",
            "source": "consumer.required_capabilities",
            "reason": f"required capability unavailable: {', '.join(unsupported)}",
            "fallback": fallback_for_behavior(requested_behavior),
            "evidence": evidence,
        }
    warning_kind_set = set(warning_diagnostic_kinds)
    warnings = sorted_unique(
        item.get("kind")
        for item in diagnostics
        if isinstance(item, dict) and item.get("kind") in warning_kind_set
    )
    if migration_previews:
        warnings = sorted_unique([*warnings, "migration preview"])
    if warnings:
        return {
            "equipment": equipment,
            "requested_behavior": requested_behavior,
            "state": "warning",
            "source": "effective_config.diagnostics",
            "reason": ", ".join(warnings),
            "fallback": "none",
            "evidence": evidence,
        }
    if requested_behavior == "mutation":
        return {
            "equipment": equipment,
            "requested_behavior": requested_behavior,
            "state": "allowed",
            "source": "effective_config.safety_status",
            "reason": "effective Config Safety Status is usable",
            "fallback": "none",
            "evidence": evidence,
        }
    return {
        "equipment": equipment,
        "requested_behavior": requested_behavior,
        "state": "advisory",
        "source": "requested_behavior",
        "reason": "read-only or dry-run behavior",
        "fallback": "none",
        "evidence": evidence,
    }


def evaluate_consumer_config(
    layer_paths: list[Path],
    fragments: list[SchemaFragment],
    *,
    equipment: str,
    requested_behavior: str,
    plain_handoff_paths: list[Path] | None = None,
    required_capabilities: Iterable[str] = (),
    supported_capabilities: Iterable[str] = (),
    warning_diagnostic_kinds: Iterable[str] = ("deprecated field",),
) -> dict[str, Any]:
    effective = effective_config(
        layer_paths,
        fragments,
        requested_behavior=requested_behavior,
        plain_handoff_paths=plain_handoff_paths,
    )
    return {
        "equipment": equipment,
        "requested_behavior": requested_behavior,
        "effective_config": effective,
        "consumer_action_decision": consumer_action_decision(
            effective,
            equipment=equipment,
            requested_behavior=requested_behavior,
            required_capabilities=required_capabilities,
            supported_capabilities=supported_capabilities,
            warning_diagnostic_kinds=warning_diagnostic_kinds,
        ),
    }


def onboarding_status(shared_config_present: bool, onboarding_state: str, safety_status: str) -> str:
    if onboarding_state not in ONBOARDING_STATES:
        raise ConfigError(f"unknown onboarding state {onboarding_state!r}")
    if safety_status not in FIRST_RUN_ONBOARDING_STATUSES:
        raise ConfigError(f"unknown Config Safety Status {safety_status!r}")
    if not shared_config_present:
        return "missing_shared_config"
    if onboarding_state == "restart":
        return "restart_ready"
    if onboarding_state == "interrupted":
        if safety_status == "usable":
            return "interrupted_complete"
        if safety_status in BLOCKED_CONFIG_SAFETY_STATUSES:
            return "blocked_config"
        return "interrupted_partial"
    if onboarding_state == "resume":
        if safety_status == "usable":
            return "resumed_complete"
        if safety_status in BLOCKED_CONFIG_SAFETY_STATUSES:
            return "blocked_config"
        return "resume_needs_input"
    return FIRST_RUN_ONBOARDING_STATUSES[safety_status]


def partial_config_from_effective(effective: dict[str, Any], fragments: list[SchemaFragment], diagnostics: list[dict[str, Any]]) -> dict[str, Any]:
    sections: dict[str, Any] = {}
    invalid_schema_diagnostics = [
        item
        for item in diagnostics
        if item.get("kind") == "schema conflict" and "missing required" not in str(item.get("detail", ""))
    ]
    for fragment in fragments:
        effective_section = effective.get(fragment.namespace, {})
        def is_missing_required(wrapped: Any, field_spec: FieldSpec) -> bool:
            return (
                field_spec.required
                and (
                    not isinstance(wrapped, dict)
                    or (wrapped.get("value") is None and "secret_reference" not in wrapped)
                )
            )

        missing_required = sorted(
            field_name
            for field_name, field_spec in fragment.fields.items()
            if is_missing_required(effective_section.get(field_name), field_spec)
        )
        fields: dict[str, Any] = {}
        for field_name, field_spec in fragment.fields.items():
            wrapped = effective_section.get(field_name, {})
            if isinstance(wrapped, dict):
                layer = wrapped.get("layer", "schema default")
                presence_value = wrapped.get("secret_reference", wrapped.get("value"))
            else:
                layer = "missing"
                presence_value = None
            field = {
                "presence": "missing" if field_spec.required and presence_value is None else "present",
                "layer": layer,
            }
            if isinstance(wrapped, dict) and "secret_reference" in wrapped:
                field["secret_reference"] = wrapped["secret_reference"]
            else:
                field["value"] = presence_value
            fields[field_name] = field
        sections[fragment.namespace] = {
            "status": "partial" if missing_required else "complete",
            "missing_required": missing_required,
            "fields": fields,
        }
    return {
        "schema_valid": not invalid_schema_diagnostics,
        "unsafe_write_modes": "blocked" if any(section["missing_required"] for section in sections.values()) else "available",
        "sections": sections,
    }


def empty_partial_config(fragments: list[SchemaFragment]) -> dict[str, Any]:
    sections = {
        fragment.namespace: {
            "status": "partial",
            "missing_required": sorted(field_name for field_name, field_spec in fragment.fields.items() if field_spec.required),
            "fields": {
                field_name: {
                    "presence": "missing" if field_spec.required else "present",
                    "value": field_spec.default,
                    "layer": "schema default",
                }
                for field_name, field_spec in fragment.fields.items()
            },
        }
        for fragment in fragments
    }
    return {
        "schema_valid": True,
        "unsafe_write_modes": "blocked",
        "sections": sections,
    }


def discovery_proposals(layers: list[Layer]) -> list[dict[str, Any]]:
    categories = [
        "committed durable config",
        "local-only operator config",
        "checkout-local state",
        "generated cache or state",
        "secret reference source",
        "session override",
    ]
    found_by_category: dict[str, list[Layer]] = {category: [] for category in categories}
    for layer in layers:
        if layer.category in found_by_category:
            found_by_category[layer.category].append(layer)
    proposals: list[dict[str, Any]] = []
    for category in categories:
        found_layers = found_by_category[category]
        proposals.append(
            {
                "source_category": category,
                "status": "found" if found_layers else "proposed",
                "layers": [
                    {"name": layer.name, "source": layer.path}
                    for layer in found_layers
                ],
                "path_owner": "harness or equipment projection",
                **SOURCE_CATEGORY_LOAD_CONTRACT[category],
            }
        )
    return proposals


def revision_plan(fragments: list[SchemaFragment], revise_sections: list[str] | None) -> dict[str, Any]:
    requested = sorted(set(revise_sections or []))
    namespaces = sorted(fragment.namespace for fragment in fragments)
    unknown = [namespace for namespace in requested if namespace not in namespaces]
    if unknown:
        raise ConfigError(f"unknown revise section(s): {', '.join(unknown)}")
    selected = [namespace for namespace in requested if namespace in namespaces]
    return {
        "selected_sections": selected,
        "unselected_sections": [namespace for namespace in namespaces if namespace not in selected],
        "preserve_unselected_sections": bool(requested),
    }


def effective_config_from_layers(
    layers: list[Layer],
    fragments: list[SchemaFragment],
    *,
    requested_behavior: str,
    plain_handoffs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    layers = sorted(layers, key=lambda layer: (layer.precedence, layer.source_order))
    plain_handoffs = plain_handoffs or []
    locks_by_layer = [policy_locks(layer) for layer in layers]
    effective: dict[str, dict[str, Any]] = {}
    diagnostics: list[Diagnostic] = []
    migration_previews: list[dict[str, Any]] = []
    for fragment in fragments:
        namespace_values: dict[str, Any] = {}
        for field_name, field_spec in fragment.fields.items():
            value = field_spec.default
            source_layer: Layer | None = None
            active_lock: PolicyLock | None = None
            values_by_precedence: dict[int, tuple[JSONValue, Layer]] = {}
            conflicted_precedences: set[int] = set()
            path = f"{fragment.namespace}.{field_name}"
            for layer, locks in zip(layers, locks_by_layer, strict=True):
                candidate_lock = locks.get((fragment.namespace, field_name))
                if candidate_lock is not None and (
                    active_lock is None
                    or candidate_lock.layer.precedence < active_lock.layer.precedence
                ):
                    active_lock = candidate_lock
                section = namespace_section(layer, fragment.namespace)
                if field_name not in section:
                    continue
                candidate = section[field_name]
                prior_value = values_by_precedence.get(layer.precedence)
                if prior_value is not None and prior_value[0] != candidate:
                    lock_blocks_candidate = active_lock is not None and lock_blocks_layer(active_lock, layer, requested_behavior)
                    diagnostics.append(
                        diagnostic(
                            "same-precedence collision",
                            path,
                            f"{layer.name} has multiple values at the same precedence",
                            layer,
                        )
                    )
                    if lock_blocks_candidate:
                        diagnostics.append(blocked_override_diagnostic(path, layer, active_lock, candidate))
                    elif not (
                        active_lock is not None
                        and active_lock.required_for in {requested_behavior, "always"}
                        and active_lock.layer.precedence < layer.precedence
                    ):
                        value = None
                        source_layer = None
                    conflicted_precedences.add(layer.precedence)
                    continue
                values_by_precedence[layer.precedence] = (candidate, layer)
                if layer.precedence in conflicted_precedences:
                    continue
                if active_lock is not None and lock_blocks_layer(active_lock, layer, requested_behavior):
                    diagnostics.append(blocked_override_diagnostic(path, layer, active_lock, candidate))
                    continue
                value = candidate
                source_layer = layer
            if active_lock is not None and active_lock.required_for in {requested_behavior, "always"} and active_lock.authority:
                diagnostics.extend(untrusted_authority_diagnostics(layers, active_lock.authority))
                if not authority_is_usable(layers, active_lock.authority, active_lock):
                    diagnostics.append(
                        diagnostic(
                            "missing authority",
                            path,
                            f"missing usable authority {active_lock.authority!r} for {active_lock.required_for}",
                            active_lock.layer,
                            evidence={"authority": active_lock.authority, "required_for": active_lock.required_for},
                        )
                    )
            unresolved_conflict = value is None and bool(conflicted_precedences)
            if value is None and field_spec.required and not unresolved_conflict:
                diagnostics.append(diagnostic("schema conflict", path, "missing required value", source_layer))
            if not unresolved_conflict:
                diagnostics.extend(validate_field(value, field_spec, path, source_layer))
            wrapped_value = {
                "value": value,
                "source": source_layer.path if source_layer else "schema default",
                "layer": source_layer.name if source_layer else "schema default",
            }
            reference = secret_reference(value)
            if reference is not None:
                wrapped_value.pop("value", None)
                wrapped_value["secret_reference"] = reference
            namespace_values[field_name] = wrapped_value
        for layer in layers:
            if not layer.trusted and fragment.namespace in layer.data and requested_behavior == "mutation":
                diagnostics.append(diagnostic("untrusted source", fragment.namespace, f"{layer.name} is not trusted for mutation", layer))
            versions = fragment_versions(layer)
            if fragment.namespace in versions and versions[fragment.namespace] < fragment.version:
                diagnostics.append(diagnostic("stale schema", fragment.namespace, f"source version {versions[fragment.namespace]} is older than schema version {fragment.version}", layer))
                migration_previews.extend(migration_previews_for_layer(layer, fragment))
        plain_values = raw_values_for_namespace(namespace_values)
        for validator in fragment.semantic_validators:
            diagnostics.extend(validator(plain_values, requested_behavior))
        effective[fragment.namespace] = namespace_values
    diagnostics = dedupe_diagnostics(diagnostics)
    safety_status = safety_status_from_diagnostics(diagnostics, requested_behavior=requested_behavior)
    return {
        "safety_status": safety_status,
        "effective": effective,
        "diagnostics": [asdict(item) for item in diagnostics],
        "migration_previews": migration_previews,
        "plain_handoffs": plain_handoffs,
        "enforcement_projection": enforcement_projection(safety_status, requested_behavior),
    }


def config_onboarding_plan(
    layer_paths: list[Path],
    fragments: list[SchemaFragment],
    *,
    requested_behavior: str,
    plain_handoff_paths: list[Path] | None = None,
    shared_config_present: bool = True,
    onboarding_state: str = "first-run",
    revise_sections: list[str] | None = None,
) -> dict[str, Any]:
    if onboarding_state not in ONBOARDING_STATES:
        raise ConfigError(f"unknown onboarding state {onboarding_state!r}")
    if not shared_config_present:
        if layer_paths or plain_handoff_paths:
            raise ConfigError("shared Config is absent; omit layer and plain handoff paths")
        return {
            "onboarding_status": "missing_shared_config",
            "effective_config": None,
            "partial_config": empty_partial_config(fragments),
            "handoff_behavior": {
                "plain_handoff": "required",
                "mutation_capable_behavior": "blocked",
                "reason": "shared Config equipment is absent",
            },
            "discovery_proposals": discovery_proposals([]),
            "revision_plan": revision_plan(fragments, revise_sections),
            "authoring_roles": authoring_roles(),
        }
    layers = load_layers(layer_paths)
    handoff_layers, plain_handoffs = load_plain_handoff_layers(plain_handoff_paths or [])
    all_layers = sorted([*layers, *handoff_layers], key=lambda layer: (layer.precedence, layer.source_order))
    effective = effective_config_from_layers(
        all_layers,
        fragments,
        requested_behavior=requested_behavior,
        plain_handoffs=plain_handoffs,
    )
    partial = partial_config_from_effective(effective["effective"], fragments, effective["diagnostics"])
    mutation_allowed = effective["safety_status"] == "usable"
    return {
        "onboarding_status": onboarding_status(shared_config_present, onboarding_state, effective["safety_status"]),
        "effective_config": effective,
        "partial_config": {
            **partial,
            "unsafe_write_modes": "available" if mutation_allowed else "blocked",
        },
        "handoff_behavior": {
            "plain_handoff": "optional" if mutation_allowed else "available",
            "mutation_capable_behavior": "allowed" if mutation_allowed else "blocked",
            "reason": "effective Config Safety Status is usable" if mutation_allowed else "effective Config Safety Status is not usable",
        },
        "discovery_proposals": discovery_proposals(all_layers),
        "revision_plan": revision_plan(fragments, revise_sections),
        "authoring_roles": authoring_roles(),
    }


def authoring_roles() -> list[dict[str, str]]:
    return [
        {
            "role": "Smith",
            "responsibility": "define schema fragments, defaults, semantic validators, and policy gates for the equipment namespace",
        },
        {
            "role": "Wielder",
            "responsibility": "supply local, checkout, or session values without weakening committed policy authority",
        },
    ]


def read_config_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError(f"could not read {path}: {exc.strerror or exc}") from exc


def parse_toml_text(path: Path, text: str) -> dict[str, Any]:
    try:
        return tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"could not parse {path}: {exc}") from exc


def load_toml(path: Path) -> dict[str, Any]:
    return parse_toml_text(path, read_config_text(path))


def load_layers(paths: Iterable[Path], *, source_snapshots: dict[Path, str] | None = None) -> list[Layer]:
    ordered_paths = list(paths)
    layers: list[Layer] = []
    for index, path in enumerate(ordered_paths):
        if source_snapshots is None:
            document = load_toml(path)
        else:
            text = read_config_text(path)
            source_snapshots[path.resolve()] = text
            document = parse_toml_text(path, text)
        root_metadata = document.get("agent_equipment_config", {})
        if not isinstance(root_metadata, dict):
            raise ConfigError(f"{path}: agent_equipment_config must be a table")
        layer_metadata = root_metadata.get("layer", {})
        if not isinstance(layer_metadata, dict):
            raise ConfigError(f"{path}: agent_equipment_config.layer must be a table")
        name = layer_metadata.get("name")
        category = layer_metadata.get("category")
        if name not in LAYER_PRECEDENCE:
            raise ConfigError(f"{path}: unknown layer name {name!r}")
        if category not in SOURCE_CATEGORIES:
            raise ConfigError(f"{path}: unknown source category {category!r}")
        trusted = layer_metadata.get("trusted", True)
        if not isinstance(trusted, bool):
            raise ConfigError(f"{path}: agent_equipment_config.layer.trusted must be a boolean")
        data = {
            key: value
            for key, value in document.items()
            if key != "agent_equipment_config"
        }
        layers.append(
            Layer(
                name=name,
                category=category,
                path=path.as_posix(),
                precedence=LAYER_PRECEDENCE.index(name),
                source_order=index,
                data=data,
                metadata=root_metadata,
                trusted=trusted,
            )
        )
    return sorted(layers, key=lambda layer: (layer.precedence, layer.source_order))


def effective_config(
    layer_paths: list[Path],
    fragments: list[SchemaFragment],
    *,
    requested_behavior: str,
    plain_handoff_paths: list[Path] | None = None,
) -> dict[str, Any]:
    handoff_layers, plain_handoffs = load_plain_handoff_layers(plain_handoff_paths or [])
    layers = [*load_layers(layer_paths), *handoff_layers]
    return effective_config_from_layers(
        layers,
        fragments,
        requested_behavior=requested_behavior,
        plain_handoffs=plain_handoffs,
    )


def safety_status_from_diagnostics(diagnostics: list[Diagnostic], *, requested_behavior: str) -> str:
    # Reserved for API symmetry with enforcement projection decisions.
    _ = requested_behavior
    kinds = {item.kind for item in diagnostics}
    # Precedence is intentional: structural conflicts first, then incomplete schema,
    # then provenance/version hazards, then semantic unsafety.
    if "blocked override" in kinds or "same-precedence collision" in kinds:
        return "conflicted"
    if "schema conflict" in kinds and any("missing required" in item.detail for item in diagnostics):
        return "incomplete"
    if "schema conflict" in kinds:
        return "conflicted"
    if "untrusted source" in kinds:
        return "untrusted"
    if "stale schema" in kinds:
        return "stale"
    if "semantic conflict" in kinds or "missing authority" in kinds:
        return "unsafe"
    return "usable"


def issue_tracker_ops_fragment() -> SchemaFragment:
    def execute_requires_disclosure(values: dict[str, Any], requested_behavior: str) -> list[Diagnostic]:
        if requested_behavior == "mutation" and values.get("mode") == "execute" and values.get("external_disclosure") != "allowed":
            return [Diagnostic("semantic conflict", "issue_tracker_ops.external_disclosure", "execute requires external disclosure policy")]
        return []

    return SchemaFragment(
        namespace="issue_tracker_ops",
        version=2,
        fields={
            "mode": FieldSpec(type="string", required=True, enum=["dry-run", "execute"]),
            "external_disclosure": FieldSpec(type="string", required=True, enum=["blocked", "allowed"]),
            "github_token": FieldSpec(type="object", required=False),
        },
        semantic_validators=(execute_requires_disclosure,),
        migrations=(
            MigrationPreview(
                from_version=1,
                field_renames={"operation_mode": "mode"},
                note="rename operation_mode to mode",
            ),
        ),
    )


def diagnostic_matches_namespace(diagnostic_item: dict[str, Any], namespace: str) -> bool:
    path = diagnostic_item.get("path")
    return path == namespace or (isinstance(path, str) and path.startswith(f"{namespace}."))


def diagnostic_evidence_value(diagnostic_item: dict[str, Any], key: str) -> Any:
    evidence = diagnostic_item.get("evidence", {})
    if not isinstance(evidence, dict):
        return None
    return evidence.get(key)


def sorted_present(values: Iterable[Any]) -> list[str]:
    return sorted_unique(value for value in values if isinstance(value, str) and value)


def authority_readiness_from_effective(effective: dict[str, Any]) -> dict[str, Any]:
    diagnostics = list_or_empty(effective.get("diagnostics", []))
    missing_authorities = sorted_present(
        diagnostic_evidence_value(item, "authority")
        for item in diagnostics
        if isinstance(item, dict) and item.get("kind") == "missing authority"
    )
    untrusted_authorities = sorted_present(
        diagnostic_evidence_value(item, "authority")
        for item in diagnostics
        if (
            isinstance(item, dict)
            and item.get("kind") == "untrusted source"
            and isinstance(item.get("path"), str)
            and item["path"].startswith("agent_equipment_config.authority.")
        )
    )
    return {
        "status": "ready" if not missing_authorities and not untrusted_authorities else "not_ready",
        "missing_authorities": missing_authorities,
        "untrusted_authorities": untrusted_authorities,
    }


def fragment_readiness_from_effective(effective: dict[str, Any], fragments: list[SchemaFragment]) -> dict[str, Any]:
    diagnostics = list_or_empty(effective.get("diagnostics", []))
    effective_values = effective.get("effective", {})
    if not isinstance(effective_values, dict):
        effective_values = {}
    partial = partial_config_from_effective(effective_values, fragments, diagnostics)
    readiness_items: list[dict[str, Any]] = []
    blocking_fragment_kinds = {
        "schema conflict",
        "same-precedence collision",
        "stale schema",
        "semantic conflict",
        "untrusted source",
        "blocked override",
        "missing authority",
    }
    for fragment in fragments:
        namespace_diagnostics = [
            item
            for item in diagnostics
            if isinstance(item, dict) and diagnostic_matches_namespace(item, fragment.namespace)
        ]
        diagnostic_kinds = sorted_present(item.get("kind") for item in namespace_diagnostics)
        blocking_diagnostics = [
            item
            for item in namespace_diagnostics
            if item.get("kind") in blocking_fragment_kinds
        ]
        section = partial["sections"][fragment.namespace]
        readiness_items.append(
            {
                "namespace": fragment.namespace,
                "version": fragment.version,
                "status": "ready" if section["status"] == "complete" and not blocking_diagnostics else "not_ready",
                "missing_required": section["missing_required"],
                "diagnostic_kinds": diagnostic_kinds,
                "stale_sources": sorted_present(
                    item.get("source")
                    for item in namespace_diagnostics
                    if item.get("kind") == "stale schema"
                ),
            }
        )
    return {
        "status": "ready" if all(item["status"] == "ready" for item in readiness_items) else "not_ready",
        "fragments": readiness_items,
    }


def config_validation_report(
    layer_paths: list[Path],
    fragments: list[SchemaFragment],
    *,
    requested_behavior: str,
    plain_handoff_paths: list[Path] | None = None,
    include_effective_config: bool = False,
) -> dict[str, Any]:
    effective = effective_config(
        layer_paths,
        fragments,
        requested_behavior=requested_behavior,
        plain_handoff_paths=plain_handoff_paths,
    )
    report = {
        "operation": "config validate",
        "passed": effective["safety_status"] == "usable",
        "safety_status": effective["safety_status"],
        "authority_readiness": authority_readiness_from_effective(effective),
        "fragment_readiness": fragment_readiness_from_effective(effective, fragments),
        "diagnostics": effective["diagnostics"],
        "enforcement_projection": effective["enforcement_projection"],
    }
    if include_effective_config:
        report["effective_config"] = effective
    return report


MCP_FRAGMENT_BUILDERS: dict[str, Callable[[], SchemaFragment]] = {
    "issue_tracker_ops": issue_tracker_ops_fragment,
}
MCP_FRAGMENT_NAMES = sorted(MCP_FRAGMENT_BUILDERS)


def mcp_array_schema(description: str) -> dict[str, Any]:
    return {
        "type": "array",
        "description": description,
        "items": {"type": "string"},
    }


def mcp_fragment_schema() -> dict[str, Any]:
    return {
        "type": "array",
        "description": "Schema fragment names to register before evaluating Config.",
        "items": {"type": "string", "enum": MCP_FRAGMENT_NAMES},
        "minItems": 1,
        "uniqueItems": True,
    }


def mcp_requested_behavior_schema(default: str) -> dict[str, Any]:
    return {
        "type": "string",
        "enum": ["advisory", "mutation"],
        "default": default,
        "description": "Behavior to evaluate for Config safety and readiness.",
    }


def mcp_load_input_properties(*, default_requested_behavior: str) -> dict[str, Any]:
    return {
        "layer_paths": mcp_array_schema("Explicit authored TOML layer paths supplied by the caller."),
        "plain_handoff_paths": mcp_array_schema("Explicit plain handoff TOML paths to promote as session overrides."),
        "fragments": mcp_fragment_schema(),
        "requested_behavior": mcp_requested_behavior_schema(default_requested_behavior),
    }


def mcp_object_schema(description: str) -> dict[str, Any]:
    return {
        "type": "object",
        "description": description,
        "additionalProperties": True,
    }


def mcp_output_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "tool": {"type": "string"},
            "operation": {"type": "string"},
            "cli_operation": {"type": "string"},
            "read_write_classification": {"type": "string"},
            "result": {"type": "object"},
        },
        "required": ["tool", "operation", "cli_operation", "read_write_classification", "result"],
        "additionalProperties": True,
    }


def mcp_tool_spec(
    name: str,
    *,
    title: str,
    description: str,
    cli_operation: str,
    input_schema: dict[str, Any],
    read_write_classification: str,
    side_effects: list[str],
    approval_requirements: list[str],
    failure_modes: list[str],
    auth_source: str = "none",
    mutation_gate: str = "not mutation-capable",
    read_only: bool = True,
    destructive: bool = False,
    idempotent: bool = True,
) -> dict[str, Any]:
    annotations: dict[str, Any] = {
        "readOnlyHint": read_only,
        "openWorldHint": False,
    }
    if not read_only:
        annotations["destructiveHint"] = destructive
        annotations["idempotentHint"] = idempotent
    return {
        "name": name,
        "title": title,
        "description": description,
        "inputSchema": input_schema,
        "outputSchema": mcp_output_schema(),
        "annotations": annotations,
        "x-agent-armory": {
            "cli_operation": cli_operation,
            "read_write_classification": read_write_classification,
            "auth_source": auth_source,
            "approval_requirements": approval_requirements,
            "side_effects": side_effects,
            "mutation_gate": mutation_gate,
            "failure_modes": failure_modes,
        },
    }


def mcp_tool_definitions() -> list[dict[str, Any]]:
    load_properties = mcp_load_input_properties(default_requested_behavior="advisory")
    validate_properties = mcp_load_input_properties(default_requested_behavior="mutation")
    return [
        mcp_tool_spec(
            "config.resolve",
            title="Config Resolve",
            description="Resolve effective Agent Equipment Config with provenance, diagnostics, safety status, and enforcement evidence.",
            cli_operation="config resolve",
            input_schema={
                "type": "object",
                "properties": load_properties,
                "required": ["fragments"],
                "additionalProperties": False,
            },
            read_write_classification="read-only",
            side_effects=[],
            approval_requirements=[],
            failure_modes=["input validation failure", "config parse failure", "schema conflict", "policy diagnostic"],
        ),
        mcp_tool_spec(
            "config.validate",
            title="Config Validate",
            description="Validate Agent Equipment Config readiness without returning full effective Config by default.",
            cli_operation="config validate",
            input_schema={
                "type": "object",
                "properties": {
                    **validate_properties,
                    "include_effective_config": {
                        "type": "boolean",
                        "default": False,
                        "description": "Include full effective Config output in addition to the low-noise report.",
                    },
                },
                "required": ["fragments"],
                "additionalProperties": False,
            },
            read_write_classification="read-only",
            side_effects=[],
            approval_requirements=[],
            failure_modes=["input validation failure", "config parse failure", "blocking validation", "policy diagnostic"],
        ),
        mcp_tool_spec(
            "config.diff",
            title="Config Diff",
            description="Compare two effective Config JSON objects and report value, diagnostic, and safety-status changes.",
            cli_operation="config diff",
            input_schema={
                "type": "object",
                "properties": {
                    "before": mcp_object_schema("Effective Config output or an effective section before the change."),
                    "after": mcp_object_schema("Effective Config output or an effective section after the change."),
                },
                "required": ["before", "after"],
                "additionalProperties": False,
            },
            read_write_classification="read-only",
            side_effects=[],
            approval_requirements=[],
            failure_modes=["input validation failure", "malformed effective Config input"],
        ),
        mcp_tool_spec(
            "onboard.config",
            title="Onboard Config",
            description="Return first-run, resume, restart, or revise planning output for Agent Equipment Config.",
            cli_operation="onboard config",
            input_schema={
                "type": "object",
                "properties": {
                    **load_properties,
                    "shared_config_present": {
                        "type": "boolean",
                        "default": True,
                        "description": "Whether shared Config is present for the onboarding run.",
                    },
                    "onboarding_state": {
                        "type": "string",
                        "enum": sorted(ONBOARDING_STATES),
                        "default": "first-run",
                    },
                    "revise_sections": mcp_array_schema("Config namespaces selected for revise-planning output."),
                },
                "required": ["fragments"],
                "additionalProperties": False,
            },
            read_write_classification="read-only",
            side_effects=[],
            approval_requirements=[],
            failure_modes=["input validation failure", "config parse failure", "unknown revise section", "policy diagnostic"],
        ),
        mcp_tool_spec(
            "migrate.config_preview",
            title="Migrate Config Preview",
            description="Preview registered Config migrations, refusals, and audit evidence without rewriting source files.",
            cli_operation="migrate config preview",
            input_schema={
                "type": "object",
                "properties": {
                    "layer_paths": mcp_array_schema("Explicit authored TOML layer paths supplied by the caller."),
                    "fragments": mcp_fragment_schema(),
                },
                "required": ["layer_paths", "fragments"],
                "additionalProperties": False,
            },
            read_write_classification="read-only",
            side_effects=[],
            approval_requirements=[],
            failure_modes=["input validation failure", "config parse failure", "migration refusal", "policy diagnostic"],
        ),
        mcp_tool_spec(
            "migrate.config_apply",
            title="Migrate Config Apply",
            description="Apply registered Config migrations to eligible local TOML sources with per-call authority and audit records.",
            cli_operation="migrate config apply",
            input_schema={
                "type": "object",
                "properties": {
                    "layer_paths": mcp_array_schema("Explicit authored TOML layer paths supplied by the caller."),
                    "fragments": mcp_fragment_schema(),
                    "apply_authority": {
                        "type": "string",
                        "enum": ["operator"],
                        "description": "Per-call authority to write eligible migration targets.",
                    },
                },
                "required": ["layer_paths", "fragments", "apply_authority"],
                "additionalProperties": False,
            },
            read_write_classification="local write",
            auth_source="per-call apply_authority",
            side_effects=["eligible local TOML source rewrite"],
            approval_requirements=["per-call apply_authority"],
            failure_modes=[
                "input validation failure",
                "config parse failure",
                "missing migration apply authority",
                "ineligible source refusal",
                "source precondition failure",
                "partial local write failure",
            ],
            mutation_gate="eligible source category, trusted provenance, usable projected Config, per-call apply_authority, and source precondition check",
            read_only=False,
            destructive=True,
            idempotent=False,
        ),
    ]


def mcp_tool_definition_by_name() -> dict[str, dict[str, Any]]:
    return {tool["name"]: tool for tool in mcp_tool_definitions()}


def mcp_validate_schema_value(schema: dict[str, Any], value: Any, path: str, *, tool_name: str) -> None:
    expected_type = schema.get("type")
    if expected_type == "object":
        if not isinstance(value, dict):
            raise ConfigError(f"{path} must be an object")
        properties = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in value or value[key] is None:
                if path == "arguments":
                    raise ConfigError(f"{key} is required for {tool_name}")
                raise ConfigError(f"{path}.{key} is required")
        if schema.get("additionalProperties") is False:
            unknown_keys = sorted(set(value) - set(properties))
            if unknown_keys:
                if path == "arguments":
                    raise ConfigError(f"unknown argument(s) for {tool_name}: {', '.join(unknown_keys)}")
                raise ConfigError(f"{path} contains unknown field(s): {', '.join(unknown_keys)}")
        for key, item in value.items():
            property_schema = properties.get(key)
            if property_schema is not None:
                mcp_validate_schema_value(property_schema, item, f"{path}.{key}", tool_name=tool_name)
        return
    if expected_type == "array":
        if not isinstance(value, list):
            raise ConfigError(f"{path} must be an array")
        minimum_items = schema.get("minItems")
        if isinstance(minimum_items, int) and len(value) < minimum_items:
            raise ConfigError(f"{path} must contain at least {minimum_items} item(s)")
        if schema.get("uniqueItems") is True:
            seen: set[str] = set()
            duplicate_items: list[Any] = []
            for item in value:
                try:
                    marker = json.dumps(item, sort_keys=True, separators=(",", ":"))
                except TypeError:
                    marker = repr(item)
                if marker in seen and item not in duplicate_items:
                    duplicate_items.append(item)
                seen.add(marker)
            if duplicate_items:
                duplicates = ", ".join(str(item) for item in duplicate_items)
                raise ConfigError(f"{path} must not contain duplicate item(s): {duplicates}")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                mcp_validate_schema_value(item_schema, item, f"{path}[{index}]", tool_name=tool_name)
    elif expected_type == "string":
        if not isinstance(value, str):
            raise ConfigError(f"{path} must be a string")
    elif expected_type == "boolean":
        if not isinstance(value, bool):
            raise ConfigError(f"{path} must be a boolean")
    enum_values = schema.get("enum")
    if isinstance(enum_values, list) and value not in enum_values:
        raise ConfigError(f"{path} must be one of {enum_values!r}")


def mcp_validate_arguments(tool: dict[str, Any], arguments: dict[str, Any]) -> None:
    mcp_validate_schema_value(tool["inputSchema"], arguments, "arguments", tool_name=tool["name"])


def mcp_path_list(arguments: dict[str, Any], key: str) -> list[Path]:
    values = arguments.get(key, [])
    if values is None:
        values = []
    if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
        raise ConfigError(f"{key} must be a list of paths")
    return [Path(value) for value in values]


def mcp_string_list(arguments: dict[str, Any], key: str) -> list[str]:
    values = arguments.get(key, [])
    if values is None:
        values = []
    if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
        raise ConfigError(f"{key} must be a list of strings")
    return values


def mcp_bool(arguments: dict[str, Any], key: str, default: bool) -> bool:
    value = arguments.get(key, default)
    if not isinstance(value, bool):
        raise ConfigError(f"{key} must be a boolean")
    return value


def mcp_requested_behavior(arguments: dict[str, Any], default: str) -> str:
    value = arguments.get("requested_behavior", default)
    if value not in {"advisory", "mutation"}:
        raise ConfigError("requested_behavior must be 'advisory' or 'mutation'")
    return str(value)


def mcp_fragments(arguments: dict[str, Any]) -> list[SchemaFragment]:
    names = mcp_string_list(arguments, "fragments")
    if not names:
        raise ConfigError("MCP Config tools require at least one schema fragment")
    seen_names: set[str] = set()
    duplicate_names: list[str] = []
    for name in names:
        if name in seen_names and name not in duplicate_names:
            duplicate_names.append(name)
        seen_names.add(name)
    if duplicate_names:
        raise ConfigError(f"fragments contains duplicate fragment name(s): {', '.join(duplicate_names)}")
    fragments: list[SchemaFragment] = []
    for name in names:
        builder = MCP_FRAGMENT_BUILDERS.get(name)
        if builder is None:
            raise ConfigError(f"unknown schema fragment {name!r}")
        fragments.append(builder())
    return fragments


def mcp_apply_authority(arguments: dict[str, Any]) -> str | None:
    value = arguments.get("apply_authority")
    if value is None:
        return None
    if value != "operator":
        raise ConfigError("apply_authority must be 'operator'")
    return str(value)


def mcp_call_summary(tool_name: str, payload: dict[str, Any]) -> str:
    if "passed" in payload:
        return f"{tool_name}: passed={payload['passed']} safety_status={payload.get('safety_status')}"
    if "safety_status" in payload:
        return f"{tool_name}: safety_status={payload['safety_status']}"
    if "applied" in payload:
        return f"{tool_name}: mode={payload.get('mode')} applied={payload['applied']} refusals={len(payload.get('refusals', []))}"
    if "onboarding_status" in payload:
        return f"{tool_name}: onboarding_status={payload['onboarding_status']}"
    if "changes" in payload:
        return f"{tool_name}: changes={len(payload['changes'])}"
    return f"{tool_name}: completed"


def mcp_call_result(tool: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    metadata = tool["x-agent-armory"]
    structured = {
        "tool": tool["name"],
        "operation": tool["name"],
        "cli_operation": metadata["cli_operation"],
        "read_write_classification": metadata["read_write_classification"],
        "result": redact_for_cli(payload),
    }
    return {
        "content": [{"type": "text", "text": mcp_call_summary(tool["name"], payload)}],
        "structuredContent": structured,
    }


def mcp_error_result(tool_or_name: dict[str, Any] | str, message: str) -> dict[str, Any]:
    if isinstance(tool_or_name, dict):
        tool_name = tool_or_name["name"]
        metadata = tool_or_name["x-agent-armory"]
        cli_operation = metadata["cli_operation"]
        read_write_classification = metadata["read_write_classification"]
    else:
        tool_name = tool_or_name
        cli_operation = "unknown"
        read_write_classification = "unknown"
    error = {
        "kind": "tool_error",
        "message": message,
    }
    return {
        "content": [{"type": "text", "text": f"{tool_name}: error: {message}"}],
        "structuredContent": {
            "tool": tool_name,
            "operation": tool_name,
            "cli_operation": cli_operation,
            "read_write_classification": read_write_classification,
            "result": {"error": error},
            "error": error,
        },
        "isError": True,
    }


def call_mcp_tool(name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    tool = mcp_tool_definition_by_name().get(name)
    if tool is None:
        return mcp_error_result(name, f"unknown MCP Config tool {name!r}")
    if arguments is None:
        arguments = {}
    if not isinstance(arguments, dict):
        return mcp_error_result(tool, "arguments must be an object")
    try:
        mcp_validate_arguments(tool, arguments)
        if name == "config.resolve":
            payload = effective_config(
                mcp_path_list(arguments, "layer_paths"),
                mcp_fragments(arguments),
                requested_behavior=mcp_requested_behavior(arguments, "advisory"),
                plain_handoff_paths=mcp_path_list(arguments, "plain_handoff_paths"),
            )
        elif name == "config.validate":
            payload = config_validation_report(
                mcp_path_list(arguments, "layer_paths"),
                mcp_fragments(arguments),
                requested_behavior=mcp_requested_behavior(arguments, "mutation"),
                plain_handoff_paths=mcp_path_list(arguments, "plain_handoff_paths"),
                include_effective_config=mcp_bool(arguments, "include_effective_config", False),
            )
        elif name == "config.diff":
            before = arguments.get("before")
            after = arguments.get("after")
            if not isinstance(before, dict) or not isinstance(after, dict):
                raise ConfigError("before and after must be effective Config objects")
            payload = config_diff(before, after)
        elif name == "onboard.config":
            onboarding_state = arguments.get("onboarding_state", "first-run")
            if onboarding_state not in ONBOARDING_STATES:
                raise ConfigError(f"unknown onboarding state {onboarding_state!r}")
            payload = config_onboarding_plan(
                mcp_path_list(arguments, "layer_paths"),
                mcp_fragments(arguments),
                requested_behavior=mcp_requested_behavior(arguments, "advisory"),
                plain_handoff_paths=mcp_path_list(arguments, "plain_handoff_paths"),
                shared_config_present=mcp_bool(arguments, "shared_config_present", True),
                onboarding_state=str(onboarding_state),
                revise_sections=mcp_string_list(arguments, "revise_sections"),
            )
        elif name == "migrate.config_preview":
            payload = migration_apply(
                mcp_path_list(arguments, "layer_paths"),
                mcp_fragments(arguments),
                apply=False,
            )
        elif name == "migrate.config_apply":
            payload = migration_apply(
                mcp_path_list(arguments, "layer_paths"),
                mcp_fragments(arguments),
                apply=True,
                apply_authority=mcp_apply_authority(arguments),
            )
        else:
            raise ConfigError(f"no dispatcher registered for MCP Config tool {name!r}")
    except (ConfigError, OSError, JSONDecodeError, UnicodeDecodeError) as exc:
        return mcp_error_result(tool, str(exc))
    return mcp_call_result(tool, payload)


def add_effective_config_arguments(parser: argparse.ArgumentParser, *, default_requested_behavior: str = "advisory") -> None:
    parser.add_argument("--layer", action="append", default=[])
    parser.add_argument("--plain-handoff", action="append", default=[])
    parser.add_argument(
        "--requested-behavior",
        choices=["advisory", "mutation"],
        default=default_requested_behavior,
        help="Behavior to evaluate for safety and readiness.",
    )
    parser.add_argument("--issue-tracker-ops", action="store_true")


def add_onboarding_arguments(parser: argparse.ArgumentParser) -> None:
    add_effective_config_arguments(parser)
    parser.add_argument("--shared-config-missing", dest="shared_config_present", action="store_false", default=True)
    parser.add_argument("--onboarding-state", choices=sorted(ONBOARDING_STATES), default="first-run")
    parser.add_argument("--revise-section", action="append", default=[])


def add_migration_arguments(parser: argparse.ArgumentParser, *, include_apply_flag: bool) -> None:
    parser.add_argument("--layer", action="append", default=[])
    parser.add_argument("--issue-tracker-ops", action="store_true")
    if include_apply_flag:
        parser.add_argument("--apply", action="store_true")
    parser.add_argument("--apply-authority", choices=["operator"])


def add_diff_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--before", required=True)
    parser.add_argument("--after", required=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compute Agent Equipment Config v0 outputs.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    effective = subparsers.add_parser("effective-config")
    add_effective_config_arguments(effective)
    effective.set_defaults(operation="config_resolve", display_operation="effective-config")

    onboarding = subparsers.add_parser("onboarding-plan")
    add_onboarding_arguments(onboarding)
    onboarding.set_defaults(operation="onboard_config", display_operation="onboarding-plan")

    migration = subparsers.add_parser("migration-apply")
    add_migration_arguments(migration, include_apply_flag=True)
    migration.set_defaults(operation="migrate_config", display_operation="migration-apply")

    diff = subparsers.add_parser("config-diff")
    add_diff_arguments(diff)
    diff.set_defaults(operation="config_diff", display_operation="config-diff")

    config = subparsers.add_parser("config")
    config_subparsers = config.add_subparsers(dest="config_operation", required=True)
    config_resolve = config_subparsers.add_parser("resolve")
    add_effective_config_arguments(config_resolve)
    config_resolve.set_defaults(operation="config_resolve", display_operation="config resolve")
    config_validate = config_subparsers.add_parser("validate", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    add_effective_config_arguments(config_validate, default_requested_behavior="mutation")
    config_validate.add_argument("--include-effective-config", action="store_true")
    config_validate.set_defaults(operation="config_validate", display_operation="config validate")
    config_diff = config_subparsers.add_parser("diff")
    add_diff_arguments(config_diff)
    config_diff.set_defaults(operation="config_diff", display_operation="config diff")

    onboard = subparsers.add_parser("onboard")
    onboard_subparsers = onboard.add_subparsers(dest="onboard_operation", required=True)
    onboard_config = onboard_subparsers.add_parser("config")
    add_onboarding_arguments(onboard_config)
    onboard_config.set_defaults(operation="onboard_config", display_operation="onboard config")

    migrate = subparsers.add_parser("migrate")
    migrate_subparsers = migrate.add_subparsers(dest="migrate_operation", required=True)
    migrate_config = migrate_subparsers.add_parser("config")
    migrate_config_subparsers = migrate_config.add_subparsers(dest="migrate_config_operation", required=True)
    migrate_preview = migrate_config_subparsers.add_parser("preview")
    add_migration_arguments(migrate_preview, include_apply_flag=False)
    migrate_preview.set_defaults(operation="migrate_config", display_operation="migrate config preview", apply=False)
    migrate_apply = migrate_config_subparsers.add_parser("apply")
    add_migration_arguments(migrate_apply, include_apply_flag=False)
    migrate_apply.set_defaults(operation="migrate_config", display_operation="migrate config apply", apply=True)

    return parser


def run(
    argv: list[str] | None = None,
    *,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
    stdout_text: bool = False,
) -> int | str:
    parser = build_parser()
    args = parser.parse_args(argv)
    output = stdout or sys.stdout
    error_output = stderr or sys.stderr
    try:
        operation = args.operation
        display_operation = args.display_operation
        if operation == "config_diff":
            before = json.loads(Path(args.before).read_text(encoding="utf-8"))
            after = json.loads(Path(args.after).read_text(encoding="utf-8"))
            payload = config_diff(before, after)
        else:
            fragments = [issue_tracker_ops_fragment()] if args.issue_tracker_ops else []
            if not fragments:
                raise ConfigError(f"{display_operation} requires at least one schema fragment flag")
            if operation == "onboard_config":
                payload = config_onboarding_plan(
                    [Path(path) for path in args.layer],
                    fragments,
                    requested_behavior=args.requested_behavior,
                    plain_handoff_paths=[Path(path) for path in args.plain_handoff],
                    shared_config_present=args.shared_config_present,
                    onboarding_state=args.onboarding_state,
                    revise_sections=args.revise_section,
                )
            elif operation == "migrate_config":
                payload = migration_apply(
                    [Path(path) for path in args.layer],
                    fragments,
                    apply=args.apply,
                    apply_authority=args.apply_authority,
                )
            elif operation == "config_validate":
                payload = config_validation_report(
                    [Path(path) for path in args.layer],
                    fragments,
                    requested_behavior=args.requested_behavior,
                    plain_handoff_paths=[Path(path) for path in args.plain_handoff],
                    include_effective_config=args.include_effective_config,
                )
            else:
                payload = effective_config(
                    [Path(path) for path in args.layer],
                    fragments,
                    requested_behavior=args.requested_behavior,
                    plain_handoff_paths=[Path(path) for path in args.plain_handoff],
                )
    except (ConfigError, OSError, JSONDecodeError, UnicodeDecodeError) as exc:
        if stdout_text:
            raise
        error_output.write(f"error: {exc}\n")
        return 2
    text = json.dumps(redact_for_cli(payload), indent=2, sort_keys=True) + "\n"
    if stdout_text:
        return text
    # CLI output is redacted by redact_for_cli before this write boundary.
    output.writelines([text])
    if operation == "config_validate" and not payload["passed"]:
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    result = run(argv)
    return result if isinstance(result, int) else 0


if __name__ == "__main__":
    raise SystemExit(main())
