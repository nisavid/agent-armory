#!/usr/bin/env python3.14
from __future__ import annotations

import argparse
import json
import sys
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

SECRET_REFERENCE_KINDS = {"env", "keychain", "vault", "harness-secret", "external"}
SENSITIVE_KEYWORDS = ("secret", "token", "credential", "password", "api_key", "private_key")
REDACTED = "<redacted>"
REQUIRED_FOR_VALUES = {"advisory", "mutation", "always"}
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


def load_toml(path: Path) -> dict[str, Any]:
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ConfigError(f"could not read {path}: {exc.strerror or exc}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"could not parse {path}: {exc}") from exc


def load_layers(paths: Iterable[Path]) -> list[Layer]:
    ordered_paths = list(paths)
    layers: list[Layer] = []
    for index, path in enumerate(ordered_paths):
        document = load_toml(path)
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
    layers = sorted([*load_layers(layer_paths), *handoff_layers], key=lambda layer: (layer.precedence, layer.source_order))
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
        version=1,
        fields={
            "mode": FieldSpec(type="string", required=True, enum=["dry-run", "execute"]),
            "external_disclosure": FieldSpec(type="string", required=True, enum=["blocked", "allowed"]),
            "github_token": FieldSpec(type="object", required=False),
        },
        semantic_validators=(execute_requires_disclosure,),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compute Agent Equipment Config v0 outputs.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    effective = subparsers.add_parser("effective-config")
    effective.add_argument("--layer", action="append", default=[])
    effective.add_argument("--plain-handoff", action="append", default=[])
    effective.add_argument("--requested-behavior", choices=["advisory", "mutation"], default="advisory")
    effective.add_argument("--issue-tracker-ops", action="store_true")
    diff = subparsers.add_parser("config-diff")
    diff.add_argument("--before", required=True)
    diff.add_argument("--after", required=True)
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
        if args.command == "config-diff":
            before = json.loads(Path(args.before).read_text(encoding="utf-8"))
            after = json.loads(Path(args.after).read_text(encoding="utf-8"))
            payload = config_diff(before, after)
        else:
            fragments = [issue_tracker_ops_fragment()] if args.issue_tracker_ops else []
            if not fragments:
                raise ConfigError("effective-config requires at least one schema fragment flag")
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
    return 0


def main(argv: list[str] | None = None) -> int:
    result = run(argv)
    return result if isinstance(result, int) else 0


if __name__ == "__main__":
    raise SystemExit(main())
