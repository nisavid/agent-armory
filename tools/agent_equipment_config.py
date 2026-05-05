#!/usr/bin/env python3.14
from __future__ import annotations

import argparse
import json
import sys
import tomllib
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
class SchemaFragment:
    namespace: str
    version: int
    fields: dict[str, FieldSpec]
    semantic_validators: tuple[Callable[[dict[str, Any], str], list["Diagnostic"]], ...] = ()


@dataclass(frozen=True)
class Diagnostic:
    kind: str
    path: str
    detail: str
    layer: str | None = None
    source: str | None = None
    evidence: dict[str, Any] = field(default_factory=dict)


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
        trusted = bool(layer_metadata.get("trusted", True))
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


def effective_config(layer_paths: list[Path], fragments: list[SchemaFragment], *, requested_behavior: str) -> dict[str, Any]:
    layers = load_layers(layer_paths)
    effective: dict[str, dict[str, Any]] = {}
    diagnostics: list[Diagnostic] = []
    for fragment in fragments:
        namespace_values: dict[str, Any] = {}
        for field_name, field in fragment.fields.items():
            value = field.default
            source_layer: Layer | None = None
            for layer in layers:
                section = layer.data.get(fragment.namespace, {})
                if field_name in section:
                    value = section[field_name]
                    source_layer = layer
            if value is None and field.required:
                diagnostics.append(diagnostic("schema conflict", f"{fragment.namespace}.{field_name}", "missing required value", source_layer))
            diagnostics.extend(validate_field(value, field, f"{fragment.namespace}.{field_name}", source_layer))
            namespace_values[field_name] = {
                "value": value,
                "source": source_layer.path if source_layer else "schema default",
                "layer": source_layer.name if source_layer else "schema default",
            }
        effective[fragment.namespace] = namespace_values
    safety_status = safety_status_from_diagnostics(diagnostics, requested_behavior=requested_behavior)
    return {
        "safety_status": safety_status,
        "effective": effective,
        "diagnostics": [asdict(item) for item in diagnostics],
    }


def safety_status_from_diagnostics(diagnostics: list[Diagnostic], *, requested_behavior: str) -> str:
    blocking_diagnostics = [item for item in diagnostics if item.kind != "deprecated field"]
    if any(item.kind == "schema conflict" and "missing required" in item.detail for item in blocking_diagnostics):
        return "incomplete"
    if blocking_diagnostics:
        return "conflicted"
    return "usable"
