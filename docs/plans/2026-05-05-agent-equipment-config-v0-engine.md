# Agent Equipment Config V0 Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first deterministic Agent Equipment Config v0 engine for schema-fragment validation, layered effective-config output, config-diff output, diagnostics, plain handoff fallback, projection classification, and Issue Tracker Ops pressure coverage.

**Architecture:** Add one standard-library Python CLI and module at `tools/agent_equipment_config.py`, with tests in `tests/test_agent_equipment_config.py`. The engine reads TOML layer files and plain handoff TOML, registers JSON-compatible schema fragments, computes effective-config and config-diff JSON, classifies enforcement projections, and emits diagnostics without mutating source config or resolving secret values.

**Tech Stack:** Python 3.14 standard library, `tomllib`, `argparse`, `json`, `dataclasses`, `unittest`.

---

## Scope

This plan implements the first runtime slice from `specs/agent-equipment-config/validation-plan.md`.

In scope:

- TOML layer loading.
- Canonical Layer Precedence.
- JSON-compatible schema fragments.
- Required-key, type, enum, default, deprecation, version, migration-preview metadata/output, and migration audit-preview shape.
- Diagnostic-only semantic validators.
- Effective-config JSON output with value provenance.
- Config-diff JSON output.
- Config Safety Status for `usable`, `incomplete`, `unsafe`, `stale`, `untrusted`, and `conflicted`.
- Secret reference recognition and status reporting without fetching values.
- Absent shared Config fallback through plain equipment-specific Issue Tracker Ops handoff ingestion and promotion.
- Missing-authority diagnostics for mutation-gated settings without usable approval authority.
- Deterministic enforcement projection classification as `blocking` or `advisory`, without harness enforcement.
- Issue Tracker Ops pressure fixture.

Out of scope:

- Source config rewrites.
- Migration apply execution.
- Provider-specific secret fetching.
- Hook, permission, approval, sandbox, or tool enforcement.
- Harness-specific blocking-control implementation.
- Harness-specific installation.
- Network access.
- GitHub issue mutation.

## File Structure

- Create `tools/agent_equipment_config.py`: CLI, data model, TOML loading, fragment registration, validation, merge, diff, and JSON output.
- Create `tests/test_agent_equipment_config.py`: behavior tests for each v0 contract case.
- Modify `specs/agent-equipment-config/validation-plan.md`: add the new test command and note the implemented runtime subset.
- Modify `specs/agent-equipment-config/README.md`: update promotion language only if the engine slice completes and remains consistent with the promotion path.

---

### Task 1: TOML Layer Loader And Source Categories

**Files:**
- Create: `tools/agent_equipment_config.py`
- Create: `tests/test_agent_equipment_config.py`

- [ ] **Step 1: Write the failing test for loading ordered TOML layers**

Add this initial test file:

```python
import json
import tempfile
import textwrap
import unittest
from pathlib import Path

from tools import agent_equipment_config


class AgentEquipmentConfigTests(unittest.TestCase):
    def write_layer(self, root: Path, name: str, text: str) -> Path:
        path = root / name
        path.write_text(textwrap.dedent(text).lstrip(), encoding="utf-8")
        return path

    def test_load_layers_preserves_declared_source_category_and_order(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            defaults = self.write_layer(
                root,
                "defaults.toml",
                """
                [agent_equipment_config.layer]
                name = "equipment defaults"
                category = "committed durable config"

                [issue_tracker_ops]
                mode = "dry-run"
                """,
            )
            session = self.write_layer(
                root,
                "session.toml",
                """
                [agent_equipment_config.layer]
                name = "session overrides"
                category = "session override"

                [issue_tracker_ops]
                mode = "execute"
                """,
            )

            layers = agent_equipment_config.load_layers([defaults, session])

        self.assertEqual([layer.name for layer in layers], ["equipment defaults", "session overrides"])
        self.assertEqual([layer.category for layer in layers], ["committed durable config", "session override"])
        self.assertEqual(layers[0].data["issue_tracker_ops"]["mode"], "dry-run")
        self.assertEqual(layers[1].data["issue_tracker_ops"]["mode"], "execute")
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
python3.14 -m unittest tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_load_layers_preserves_declared_source_category_and_order
```

Expected: failure or import error because `tools.agent_equipment_config` does not exist.

- [ ] **Step 3: Implement the minimal loader**

Create `tools/agent_equipment_config.py` with:

```python
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
```

- [ ] **Step 4: Run the test to verify it passes**

Run:

```bash
python3.14 -m unittest tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_load_layers_preserves_declared_source_category_and_order
```

Expected: `OK`.

- [ ] **Step 5: Commit**

```bash
git add tools/agent_equipment_config.py tests/test_agent_equipment_config.py
git commit -m "feat(config): load config layers" -m "Co-authored-by: Codex <noreply@openai.com>"
```

---

### Task 2: Schema Fragment Validation

**Files:**
- Modify: `tools/agent_equipment_config.py`
- Modify: `tests/test_agent_equipment_config.py`

- [ ] **Step 1: Write failing tests for schema fragments**

Append these tests inside `AgentEquipmentConfigTests`:

```python
    def test_schema_fragment_applies_defaults_and_reports_missing_required_keys(self):
        fragment = agent_equipment_config.SchemaFragment(
            namespace="issue_tracker_ops",
            version=1,
            fields={
                "mode": agent_equipment_config.FieldSpec(type="string", required=True, enum=["dry-run", "execute"]),
                "priority_policy": agent_equipment_config.FieldSpec(type="string", default="configured"),
            },
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(
                root,
                "repo.toml",
                """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [issue_tracker_ops]
                priority_policy = "configured"
                """,
            )

            result = agent_equipment_config.effective_config([layer], [fragment], requested_behavior="advisory")

        self.assertEqual(result["safety_status"], "incomplete")
        self.assertEqual(result["effective"]["issue_tracker_ops"]["priority_policy"]["value"], "configured")
        self.assertEqual(result["effective"]["issue_tracker_ops"]["mode"]["value"], None)
        self.assertEqual(result["diagnostics"][0]["kind"], "schema conflict")
        self.assertEqual(result["diagnostics"][0]["path"], "issue_tracker_ops.mode")

    def test_schema_fragment_rejects_wrong_type(self):
        fragment = agent_equipment_config.SchemaFragment(
            namespace="issue_tracker_ops",
            version=1,
            fields={"execute": agent_equipment_config.FieldSpec(type="boolean")},
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(
                root,
                "repo.toml",
                """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [issue_tracker_ops]
                execute = "yes"
                """,
            )

            result = agent_equipment_config.effective_config([layer], [fragment], requested_behavior="advisory")

        self.assertEqual(result["safety_status"], "conflicted")
        self.assertEqual(result["diagnostics"][0]["detail"], "expected boolean")

    def test_numeric_fields_reject_boolean_values(self):
        fragment = agent_equipment_config.SchemaFragment(
            namespace="issue_tracker_ops",
            version=1,
            fields={
                "retry_count": agent_equipment_config.FieldSpec(type="integer"),
                "risk_score": agent_equipment_config.FieldSpec(type="number"),
            },
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(
                root,
                "repo.toml",
                """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [issue_tracker_ops]
                retry_count = true
                risk_score = false
                """,
            )

            result = agent_equipment_config.effective_config([layer], [fragment], requested_behavior="advisory")

        self.assertEqual(result["safety_status"], "conflicted")
        self.assertEqual([item["detail"] for item in result["diagnostics"]], ["expected integer", "expected number"])

    def test_deprecated_field_reports_diagnostic_without_blocking_config(self):
        fragment = agent_equipment_config.SchemaFragment(
            namespace="issue_tracker_ops",
            version=1,
            fields={
                "old_mode": agent_equipment_config.FieldSpec(type="string", deprecated=True, replacement="mode"),
                "mode": agent_equipment_config.FieldSpec(type="string", default="dry-run"),
            },
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(
                root,
                "repo.toml",
                """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [issue_tracker_ops]
                old_mode = "dry-run"
                """,
            )

            result = agent_equipment_config.effective_config([layer], [fragment], requested_behavior="advisory")

        self.assertEqual(result["safety_status"], "usable")
        self.assertEqual(result["diagnostics"][0]["kind"], "deprecated field")
        self.assertEqual(result["diagnostics"][0]["detail"], "use issue_tracker_ops.mode instead")
```

- [ ] **Step 2: Run the tests to verify they fail**

Run:

```bash
python3.14 -m unittest tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_schema_fragment_applies_defaults_and_reports_missing_required_keys tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_schema_fragment_rejects_wrong_type tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_numeric_fields_reject_boolean_values tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_deprecated_field_reports_diagnostic_without_blocking_config
```

Expected: failure because `SchemaFragment`, `FieldSpec`, and `effective_config` are missing.

- [ ] **Step 3: Implement schema fragment support**

Add these dataclasses and helpers below `Layer`:

```python
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
```

Add this first version of `effective_config`:

```python
def effective_config(layer_paths: list[Path], fragments: list[SchemaFragment], *, requested_behavior: str) -> dict[str, Any]:
    layers = load_layers(layer_paths)
    effective: dict[str, dict[str, Any]] = {}
    diagnostics: list[Diagnostic] = []
    for fragment in fragments:
        namespace_values: dict[str, Any] = {}
        source_layers: dict[str, Layer] = {}
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
            if source_layer:
                source_layers[field_name] = source_layer
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
```

- [ ] **Step 4: Run schema tests**

Run:

```bash
python3.14 -m unittest tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_schema_fragment_applies_defaults_and_reports_missing_required_keys tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_schema_fragment_rejects_wrong_type tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_numeric_fields_reject_boolean_values tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_deprecated_field_reports_diagnostic_without_blocking_config
```

Expected: `OK`.

- [ ] **Step 5: Commit**

```bash
git add tools/agent_equipment_config.py tests/test_agent_equipment_config.py
git commit -m "feat(config): validate schema fragments" -m "Co-authored-by: Codex <noreply@openai.com>"
```

---

### Task 3: Layer Precedence, Policy Authority, And Conflict Diagnostics

**Files:**
- Modify: `tools/agent_equipment_config.py`
- Modify: `tests/test_agent_equipment_config.py`

- [ ] **Step 1: Write failing tests for precedence and blocked overrides**

Append:

```python
    def issue_ops_fragment(self):
        return agent_equipment_config.SchemaFragment(
            namespace="issue_tracker_ops",
            version=1,
            fields={
                "mode": agent_equipment_config.FieldSpec(type="string", required=True, enum=["dry-run", "execute"]),
                "external_disclosure": agent_equipment_config.FieldSpec(type="string", required=True, enum=["blocked", "allowed"]),
            },
        )

    def test_later_layer_wins_when_not_locked(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            defaults = self.write_layer(root, "defaults.toml", """
                [agent_equipment_config.layer]
                name = "equipment defaults"
                category = "committed durable config"

                [issue_tracker_ops]
                mode = "dry-run"
                external_disclosure = "blocked"
            """)
            session = self.write_layer(root, "session.toml", """
                [agent_equipment_config.layer]
                name = "session overrides"
                category = "session override"

                [issue_tracker_ops]
                mode = "execute"
            """)

            result = agent_equipment_config.effective_config([defaults, session], [self.issue_ops_fragment()], requested_behavior="advisory")

        self.assertEqual(result["effective"]["issue_tracker_ops"]["mode"]["value"], "execute")
        self.assertEqual(result["effective"]["issue_tracker_ops"]["mode"]["layer"], "session overrides")
        self.assertEqual(result["safety_status"], "usable")

    def test_policy_authority_blocks_lower_authority_override_for_mutation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            policy = self.write_layer(root, "org.toml", """
                [agent_equipment_config.layer]
                name = "organization or tracker policy"
                category = "committed durable config"

                [agent_equipment_config.policy.issue_tracker_ops.mode]
                non_overridable = true
                required_for = "mutation"
                authority = "live_tracker_write"

                [issue_tracker_ops]
                mode = "dry-run"
                external_disclosure = "blocked"
            """)
            session = self.write_layer(root, "session.toml", """
                [agent_equipment_config.layer]
                name = "session overrides"
                category = "session override"

                [issue_tracker_ops]
                mode = "execute"
            """)

            result = agent_equipment_config.effective_config([policy, session], [self.issue_ops_fragment()], requested_behavior="mutation")

        self.assertEqual(result["effective"]["issue_tracker_ops"]["mode"]["value"], "dry-run")
        self.assertEqual(result["safety_status"], "conflicted")
        self.assertEqual(result["diagnostics"][0]["kind"], "blocked override")
        self.assertEqual(result["diagnostics"][0]["path"], "issue_tracker_ops.mode")
        self.assertEqual(result["diagnostics"][0]["evidence"]["blocked_value"], "execute")
        self.assertEqual(result["diagnostics"][0]["evidence"]["blocked_by"]["layer"], "organization or tracker policy")
        self.assertEqual(result["diagnostics"][0]["evidence"]["blocked_by"]["source"], policy.as_posix())

    def test_same_precedence_collision_reports_conflict_without_silent_winner(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            repo_a = self.write_layer(root, "repo-a.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [issue_tracker_ops]
                mode = "dry-run"
                external_disclosure = "blocked"
            """)
            repo_b = self.write_layer(root, "repo-b.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [issue_tracker_ops]
                mode = "execute"
            """)

            result = agent_equipment_config.effective_config([repo_a, repo_b], [self.issue_ops_fragment()], requested_behavior="advisory")

        self.assertEqual(result["effective"]["issue_tracker_ops"]["mode"]["value"], None)
        self.assertEqual(result["safety_status"], "conflicted")
        self.assertEqual(result["diagnostics"][0]["kind"], "same-precedence collision")
        self.assertEqual(result["diagnostics"][0]["path"], "issue_tracker_ops.mode")

    def test_policy_value_survives_lower_authority_same_precedence_collision(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            policy = self.write_layer(root, "org.toml", """
                [agent_equipment_config.layer]
                name = "organization or tracker policy"
                category = "committed durable config"

                [agent_equipment_config.policy.issue_tracker_ops.mode]
                non_overridable = true
                required_for = "mutation"

                [issue_tracker_ops]
                mode = "dry-run"
                external_disclosure = "blocked"
            """)
            repo_a = self.write_layer(root, "repo-a.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [issue_tracker_ops]
                mode = "execute"
            """)
            repo_b = self.write_layer(root, "repo-b.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [issue_tracker_ops]
                mode = "dry-run"
            """)

            result = agent_equipment_config.effective_config([policy, repo_a, repo_b], [self.issue_ops_fragment()], requested_behavior="mutation")

        self.assertEqual(result["effective"]["issue_tracker_ops"]["mode"]["value"], "dry-run")
        self.assertEqual(result["effective"]["issue_tracker_ops"]["mode"]["source"], policy.as_posix())
        self.assertEqual(result["safety_status"], "conflicted")
        self.assertIn("blocked override", [item["kind"] for item in result["diagnostics"]])
        self.assertIn("same-precedence collision", [item["kind"] for item in result["diagnostics"]])
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
python3.14 -m unittest tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_later_layer_wins_when_not_locked tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_policy_authority_blocks_lower_authority_override_for_mutation tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_same_precedence_collision_reports_conflict_without_silent_winner tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_policy_value_survives_lower_authority_same_precedence_collision
```

Expected: failures because policy locks and same-precedence collision detection are not implemented.

- [ ] **Step 3: Implement Policy Authority lock handling**

Add:

```python
@dataclass(frozen=True)
class PolicyLock:
    namespace: str
    field: str
    layer: Layer
    required_for: str


def policy_locks(layer: Layer) -> dict[tuple[str, str], PolicyLock]:
    policy = layer.metadata.get("policy", {})
    locks: dict[tuple[str, str], PolicyLock] = {}
    for namespace, fields in policy.items():
        if not isinstance(fields, dict):
            continue
        for field_name, rule in fields.items():
            if isinstance(rule, dict) and rule.get("non_overridable"):
                locks[(namespace, field_name)] = PolicyLock(
                    namespace=namespace,
                    field=field_name,
                    layer=layer,
                    required_for=str(rule.get("required_for", "mutation")),
                )
    return locks
```

Task 1 stores the full `agent_equipment_config` table in `Layer.metadata`, while `Layer.data` contains only equipment namespaces. Keep that separation here so policy metadata cannot be confused with configurable equipment values.

Replace the whole `effective_config` function with:

```python
def effective_config(layer_paths: list[Path], fragments: list[SchemaFragment], *, requested_behavior: str) -> dict[str, Any]:
    layers = load_layers(layer_paths)
    effective: dict[str, dict[str, Any]] = {}
    diagnostics: list[Diagnostic] = []
    for fragment in fragments:
        namespace_values: dict[str, Any] = {}
        for field_name, field in fragment.fields.items():
            value = field.default
            source_layer: Layer | None = None
            active_lock: PolicyLock | None = None
            values_by_precedence: dict[int, tuple[JSONValue, Layer]] = {}
            field_conflicted = False
            path = f"{fragment.namespace}.{field_name}"
            for layer in layers:
                locks = policy_locks(layer)
                if (fragment.namespace, field_name) in locks:
                    active_lock = locks[(fragment.namespace, field_name)]
                section = layer.data.get(fragment.namespace, {})
                if field_name not in section:
                    continue
                candidate = section[field_name]
                prior_value = values_by_precedence.get(layer.precedence)
                if prior_value is not None and prior_value[0] != candidate:
                    diagnostics.append(
                        diagnostic(
                            "same-precedence collision",
                            path,
                            f"{layer.name} has multiple values at the same precedence",
                            layer,
                        )
                    )
                    if not (
                        active_lock is not None
                        and active_lock.required_for in {requested_behavior, "always"}
                        and active_lock.layer.precedence < layer.precedence
                    ):
                        value = None
                        source_layer = None
                    field_conflicted = True
                    continue
                values_by_precedence[layer.precedence] = (candidate, layer)
                lock_applies = active_lock is not None and active_lock.required_for in {requested_behavior, "always"}
                if lock_applies and layer.precedence > active_lock.layer.precedence:
                    diagnostics.append(
                        diagnostic(
                            "blocked override",
                            path,
                            f"{layer.name} cannot override non-overridable value from {active_lock.layer.name}",
                            layer,
                            evidence={
                                "blocked_value": candidate,
                                "blocked_by": {
                                    "layer": active_lock.layer.name,
                                    "source": active_lock.layer.path,
                                },
                            },
                        )
                    )
                    continue
                if not field_conflicted:
                    value = candidate
                    source_layer = layer
            if value is None and field.required and not field_conflicted:
                diagnostics.append(diagnostic("schema conflict", path, "missing required value", source_layer))
            if not field_conflicted:
                diagnostics.extend(validate_field(value, field, path, source_layer))
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
```

- [ ] **Step 4: Run precedence tests**

Run:

```bash
python3.14 -m unittest tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_later_layer_wins_when_not_locked tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_policy_authority_blocks_lower_authority_override_for_mutation tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_same_precedence_collision_reports_conflict_without_silent_winner tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_policy_value_survives_lower_authority_same_precedence_collision
```

Expected: `OK`.

- [ ] **Step 5: Commit**

```bash
git add tools/agent_equipment_config.py tests/test_agent_equipment_config.py
git commit -m "feat(config): enforce policy authority locks" -m "Co-authored-by: Codex <noreply@openai.com>"
```

---

### Task 4: Safety Status, Untrusted Layers, Stale Migrations, And Semantic Validators

**Files:**
- Modify: `tools/agent_equipment_config.py`
- Modify: `tests/test_agent_equipment_config.py`

- [ ] **Step 1: Write failing tests for all remaining safety statuses**

Append:

```python
    def test_untrusted_layer_sets_untrusted_for_mutation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "checkout.toml", """
                [agent_equipment_config.layer]
                name = "checkout-local state"
                category = "checkout-local state"
                trusted = false

                [issue_tracker_ops]
                mode = "execute"
                external_disclosure = "allowed"
            """)

            result = agent_equipment_config.effective_config([layer], [self.issue_ops_fragment()], requested_behavior="mutation")

        self.assertEqual(result["safety_status"], "untrusted")
        self.assertEqual(result["diagnostics"][0]["kind"], "untrusted source")

    def test_stale_fragment_version_reports_stale_without_rewriting_source(self):
        fragment = agent_equipment_config.SchemaFragment(
            namespace="issue_tracker_ops",
            version=2,
            fields={"mode": agent_equipment_config.FieldSpec(type="string", required=True, enum=["dry-run", "execute"])},
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "repo.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [agent_equipment_config.fragment_versions]
                issue_tracker_ops = 1

                [issue_tracker_ops]
                mode = "dry-run"
            """)

            result = agent_equipment_config.effective_config([layer], [fragment], requested_behavior="mutation")

        self.assertEqual(result["safety_status"], "stale")
        self.assertEqual(result["diagnostics"][0]["kind"], "stale schema")

    def test_migration_preview_reports_audit_shape_without_rewriting_source(self):
        fragment = agent_equipment_config.SchemaFragment(
            namespace="issue_tracker_ops",
            version=2,
            fields={"mode": agent_equipment_config.FieldSpec(type="string", enum=["dry-run", "execute"])},
            migrations=(
                agent_equipment_config.MigrationPreview(
                    from_version=1,
                    field_renames={"operation_mode": "mode"},
                    note="rename operation_mode to mode",
                ),
            ),
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "repo.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [agent_equipment_config.fragment_versions]
                issue_tracker_ops = 1

                [issue_tracker_ops]
                operation_mode = "dry-run"
            """)
            original_text = layer.read_text(encoding="utf-8")

            result = agent_equipment_config.effective_config([layer], [fragment], requested_behavior="mutation")
            rewritten_text = layer.read_text(encoding="utf-8")

        self.assertEqual(rewritten_text, original_text)
        self.assertEqual(result["safety_status"], "stale")
        self.assertEqual(
            result["migration_previews"][0]["changes"][0],
            {"from": "issue_tracker_ops.operation_mode", "to": "issue_tracker_ops.mode", "value": "dry-run"},
        )
        self.assertEqual(result["migration_previews"][0]["audit_preview"]["action"], "migration apply preview")
        self.assertFalse(result["migration_previews"][0]["audit_preview"]["would_rewrite_source"])

    def test_semantic_validator_can_mark_config_unsafe(self):
        def execute_requires_disclosure(values, requested_behavior):
            if requested_behavior == "mutation" and values.get("mode") == "execute" and values.get("external_disclosure") != "allowed":
                return [agent_equipment_config.Diagnostic("semantic conflict", "issue_tracker_ops.external_disclosure", "execute requires external disclosure policy")]
            return []

        fragment = agent_equipment_config.SchemaFragment(
            namespace="issue_tracker_ops",
            version=1,
            fields={
                "mode": agent_equipment_config.FieldSpec(type="string", required=True, enum=["dry-run", "execute"]),
                "external_disclosure": agent_equipment_config.FieldSpec(type="string", required=True, enum=["blocked", "allowed"]),
            },
            semantic_validators=(execute_requires_disclosure,),
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "session.toml", """
                [agent_equipment_config.layer]
                name = "session overrides"
                category = "session override"

                [issue_tracker_ops]
                mode = "execute"
                external_disclosure = "blocked"
            """)

            result = agent_equipment_config.effective_config([layer], [fragment], requested_behavior="mutation")

        self.assertEqual(result["safety_status"], "unsafe")
        self.assertEqual(result["diagnostics"][0]["kind"], "semantic conflict")

    def test_mutation_only_semantic_validator_does_not_block_advisory_behavior(self):
        def execute_requires_disclosure(values, requested_behavior):
            if requested_behavior == "mutation" and values.get("mode") == "execute" and values.get("external_disclosure") != "allowed":
                return [agent_equipment_config.Diagnostic("semantic conflict", "issue_tracker_ops.external_disclosure", "execute requires external disclosure policy")]
            return []

        fragment = agent_equipment_config.SchemaFragment(
            namespace="issue_tracker_ops",
            version=1,
            fields={
                "mode": agent_equipment_config.FieldSpec(type="string", required=True, enum=["dry-run", "execute"]),
                "external_disclosure": agent_equipment_config.FieldSpec(type="string", required=True, enum=["blocked", "allowed"]),
            },
            semantic_validators=(execute_requires_disclosure,),
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "session.toml", """
                [agent_equipment_config.layer]
                name = "session overrides"
                category = "session override"

                [issue_tracker_ops]
                mode = "execute"
                external_disclosure = "blocked"
            """)

            result = agent_equipment_config.effective_config([layer], [fragment], requested_behavior="advisory")

        self.assertEqual(result["safety_status"], "usable")
        self.assertEqual(result["diagnostics"], [])

    def test_safety_status_precedence_is_explicit_for_mixed_diagnostics(self):
        self.assertEqual(
            agent_equipment_config.safety_status_from_diagnostics(
                [
                    agent_equipment_config.Diagnostic("semantic conflict", "issue_tracker_ops.external_disclosure", "unsafe"),
                    agent_equipment_config.Diagnostic("blocked override", "issue_tracker_ops.mode", "blocked"),
                ],
                requested_behavior="mutation",
            ),
            "conflicted",
        )
        self.assertEqual(
            agent_equipment_config.safety_status_from_diagnostics(
                [
                    agent_equipment_config.Diagnostic("stale schema", "issue_tracker_ops", "stale"),
                    agent_equipment_config.Diagnostic("schema conflict", "issue_tracker_ops.mode", "missing required value"),
                ],
                requested_behavior="mutation",
            ),
            "incomplete",
        )
        self.assertEqual(
            agent_equipment_config.safety_status_from_diagnostics(
                [
                    agent_equipment_config.Diagnostic("semantic conflict", "issue_tracker_ops.external_disclosure", "unsafe"),
                    agent_equipment_config.Diagnostic("untrusted source", "issue_tracker_ops", "untrusted"),
                ],
                requested_behavior="mutation",
            ),
            "untrusted",
        )
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
python3.14 -m unittest tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_untrusted_layer_sets_untrusted_for_mutation tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_stale_fragment_version_reports_stale_without_rewriting_source tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_migration_preview_reports_audit_shape_without_rewriting_source tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_semantic_validator_can_mark_config_unsafe tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_mutation_only_semantic_validator_does_not_block_advisory_behavior tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_safety_status_precedence_is_explicit_for_mixed_diagnostics
```

Expected: failures because untrusted, stale, migration preview, and semantic validators are not complete.

- [ ] **Step 3: Implement remaining safety logic**

Add `MigrationPreview`, replace the existing `SchemaFragment` definition with the version below, and then add the helper functions:

```python
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


def fragment_versions(layer: Layer) -> dict[str, int]:
    versions = layer.metadata.get("fragment_versions", {})
    return {str(key): int(value) for key, value in versions.items()} if isinstance(versions, dict) else {}


def raw_values_for_namespace(effective_namespace: dict[str, Any]) -> dict[str, JSONValue]:
    return {
        field_name: wrapped.get("value")
        for field_name, wrapped in effective_namespace.items()
    }


def migration_previews_for_layer(layer: Layer, fragment: SchemaFragment) -> list[dict[str, Any]]:
    source_version = fragment_versions(layer).get(fragment.namespace)
    if source_version is None or source_version >= fragment.version:
        return []
    section = layer.data.get(fragment.namespace, {})
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
```

Replace the whole `effective_config` function with:

```python
def effective_config(layer_paths: list[Path], fragments: list[SchemaFragment], *, requested_behavior: str) -> dict[str, Any]:
    layers = load_layers(layer_paths)
    effective: dict[str, dict[str, Any]] = {}
    diagnostics: list[Diagnostic] = []
    migration_previews: list[dict[str, Any]] = []
    for fragment in fragments:
        namespace_values: dict[str, Any] = {}
        for field_name, field in fragment.fields.items():
            value = field.default
            source_layer: Layer | None = None
            active_lock: PolicyLock | None = None
            values_by_precedence: dict[int, tuple[JSONValue, Layer]] = {}
            field_conflicted = False
            path = f"{fragment.namespace}.{field_name}"
            for layer in layers:
                locks = policy_locks(layer)
                if (fragment.namespace, field_name) in locks:
                    active_lock = locks[(fragment.namespace, field_name)]
                section = layer.data.get(fragment.namespace, {})
                if field_name not in section:
                    continue
                candidate = section[field_name]
                prior_value = values_by_precedence.get(layer.precedence)
                if prior_value is not None and prior_value[0] != candidate:
                    diagnostics.append(
                        diagnostic(
                            "same-precedence collision",
                            path,
                            f"{layer.name} has multiple values at the same precedence",
                            layer,
                        )
                    )
                    if not (
                        active_lock is not None
                        and active_lock.required_for in {requested_behavior, "always"}
                        and active_lock.layer.precedence < layer.precedence
                    ):
                        value = None
                        source_layer = None
                    field_conflicted = True
                    continue
                values_by_precedence[layer.precedence] = (candidate, layer)
                lock_applies = active_lock is not None and active_lock.required_for in {requested_behavior, "always"}
                if lock_applies and layer.precedence > active_lock.layer.precedence:
                    diagnostics.append(
                        diagnostic(
                            "blocked override",
                            path,
                            f"{layer.name} cannot override non-overridable value from {active_lock.layer.name}",
                            layer,
                            evidence={
                                "blocked_value": candidate,
                                "blocked_by": {
                                    "layer": active_lock.layer.name,
                                    "source": active_lock.layer.path,
                                },
                            },
                        )
                    )
                    continue
                if not field_conflicted:
                    value = candidate
                    source_layer = layer
            if value is None and field.required and not field_conflicted:
                diagnostics.append(diagnostic("schema conflict", path, "missing required value", source_layer))
            if not field_conflicted:
                diagnostics.extend(validate_field(value, field, path, source_layer))
            namespace_values[field_name] = {
                "value": value,
                "source": source_layer.path if source_layer else "schema default",
                "layer": source_layer.name if source_layer else "schema default",
            }
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
    safety_status = safety_status_from_diagnostics(diagnostics, requested_behavior=requested_behavior)
    return {
        "safety_status": safety_status,
        "effective": effective,
        "diagnostics": [asdict(item) for item in diagnostics],
        "migration_previews": migration_previews,
    }
```

Replace `safety_status_from_diagnostics` with:

```python
def safety_status_from_diagnostics(diagnostics: list[Diagnostic], *, requested_behavior: str) -> str:
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
    if "semantic conflict" in kinds:
        return "unsafe"
    return "usable"
```

- [ ] **Step 4: Run safety tests**

Run:

```bash
python3.14 -m unittest tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_untrusted_layer_sets_untrusted_for_mutation tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_stale_fragment_version_reports_stale_without_rewriting_source tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_migration_preview_reports_audit_shape_without_rewriting_source tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_semantic_validator_can_mark_config_unsafe tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_mutation_only_semantic_validator_does_not_block_advisory_behavior tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_safety_status_precedence_is_explicit_for_mixed_diagnostics
```

Expected: `OK`.

- [ ] **Step 5: Commit**

```bash
git add tools/agent_equipment_config.py tests/test_agent_equipment_config.py
git commit -m "feat(config): classify config safety status" -m "Co-authored-by: Codex <noreply@openai.com>"
```

---

### Task 5: Secret References, Config-Diff, And CLI Output

**Files:**
- Modify: `tools/agent_equipment_config.py`
- Modify: `tests/test_agent_equipment_config.py`

- [ ] **Step 1: Write failing tests for secret references, diff, and CLI**

Append:

```python
    def test_secret_reference_is_reported_without_value_resolution(self):
        fragment = agent_equipment_config.SchemaFragment(
            namespace="issue_tracker_ops",
            version=1,
            fields={"github_token": agent_equipment_config.FieldSpec(type="object", required=True)},
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "local.toml", """
                [agent_equipment_config.layer]
                name = "user/operator local overrides"
                category = "local-only operator config"

                [issue_tracker_ops.github_token]
                kind = "env"
                name = "GITHUB_TOKEN"
                scope = "session"
                required_for = "tracker write"
            """)

            result = agent_equipment_config.effective_config([layer], [fragment], requested_behavior="mutation")

        token = result["effective"]["issue_tracker_ops"]["github_token"]
        self.assertEqual(token["secret_reference"]["kind"], "env")
        self.assertEqual(token["secret_reference"]["resolution_status"], "unresolved")
        self.assertNotIn("value", token["secret_reference"])

    def test_config_diff_reports_changed_values(self):
        before = {"issue_tracker_ops": {"mode": {"value": "dry-run"}}}
        after = {"issue_tracker_ops": {"mode": {"value": "execute"}}}

        diff = agent_equipment_config.config_diff(before, after)

        self.assertEqual(
            diff,
            {
                "changes": [
                    {
                        "path": "issue_tracker_ops.mode",
                        "before": "dry-run",
                        "after": "execute",
                    }
                ]
            },
        )

    def test_config_diff_reports_changed_secret_references(self):
        before = {
            "issue_tracker_ops": {
                "github_token": {
                    "secret_reference": {
                        "kind": "env",
                        "name": "OLD_GITHUB_TOKEN",
                        "resolution_status": "unresolved",
                    }
                }
            }
        }
        after = {
            "issue_tracker_ops": {
                "github_token": {
                    "secret_reference": {
                        "kind": "env",
                        "name": "NEW_GITHUB_TOKEN",
                        "resolution_status": "unresolved",
                    }
                }
            }
        }

        diff = agent_equipment_config.config_diff(before, after)

        self.assertEqual(diff["changes"][0]["path"], "issue_tracker_ops.github_token")
        self.assertEqual(diff["changes"][0]["before"]["secret_reference"]["name"], "OLD_GITHUB_TOKEN")
        self.assertEqual(diff["changes"][0]["after"]["secret_reference"]["name"], "NEW_GITHUB_TOKEN")

    def test_config_diff_reports_status_and_diagnostic_changes(self):
        before = {
            "safety_status": "usable",
            "effective": {"issue_tracker_ops": {"mode": {"value": "dry-run"}}},
            "diagnostics": [],
        }
        after = {
            "safety_status": "conflicted",
            "effective": {"issue_tracker_ops": {"mode": {"value": "dry-run"}}},
            "diagnostics": [
                {
                    "kind": "blocked override",
                    "path": "issue_tracker_ops.mode",
                    "detail": "session overrides cannot override non-overridable value from organization or tracker policy",
                    "evidence": {
                        "blocked_value": "execute",
                        "blocked_by": {"layer": "organization or tracker policy", "source": "org.toml"},
                    },
                },
                {
                    "kind": "same-precedence collision",
                    "path": "issue_tracker_ops.priority_policy",
                    "detail": "repository policy has multiple values at the same precedence",
                    "evidence": {},
                },
            ],
        }

        diff = agent_equipment_config.config_diff(before, after)

        self.assertEqual(diff["status_change"], {"before": "usable", "after": "conflicted"})
        self.assertEqual([item["kind"] for item in diff["diagnostic_changes"]["after"]], ["blocked override", "same-precedence collision"])
        self.assertEqual(diff["diagnostic_changes"]["after"][0]["evidence"]["blocked_value"], "execute")

    def test_cli_effective_config_outputs_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "repo.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [issue_tracker_ops]
                mode = "dry-run"
                external_disclosure = "blocked"
            """)
            stdout = agent_equipment_config.run(["effective-config", "--layer", str(layer), "--issue-tracker-ops"], stdout_text=True)

        payload = json.loads(stdout)
        self.assertEqual(payload["safety_status"], "usable")
        self.assertEqual(payload["effective"]["issue_tracker_ops"]["mode"]["value"], "dry-run")

    def test_cli_config_diff_outputs_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            before = root / "before.json"
            after = root / "after.json"
            before.write_text(json.dumps({"effective": {"issue_tracker_ops": {"mode": {"value": "dry-run"}}}}), encoding="utf-8")
            after.write_text(json.dumps({"effective": {"issue_tracker_ops": {"mode": {"value": "execute"}}}}), encoding="utf-8")

            stdout = agent_equipment_config.run(
                ["config-diff", "--before", str(before), "--after", str(after)],
                stdout_text=True,
            )

        payload = json.loads(stdout)
        self.assertEqual(payload["changes"][0]["path"], "issue_tracker_ops.mode")
        self.assertEqual(payload["changes"][0]["before"], "dry-run")
        self.assertEqual(payload["changes"][0]["after"], "execute")
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
python3.14 -m unittest tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_secret_reference_is_reported_without_value_resolution tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_config_diff_reports_changed_values tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_config_diff_reports_changed_secret_references tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_config_diff_reports_status_and_diagnostic_changes tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_cli_effective_config_outputs_json tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_cli_config_diff_outputs_json
```

Expected: failures because secret reference handling, diff, and CLI are missing.

- [ ] **Step 3: Implement secret reference and diff helpers**

Add:

```python
SECRET_REFERENCE_KINDS = {"env", "keychain", "vault", "harness-secret", "external"}


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


def diffable_wrapped_value(wrapped: dict[str, Any]) -> JSONValue | dict[str, Any]:
    if "secret_reference" in wrapped:
        return {"secret_reference": wrapped["secret_reference"]}
    return wrapped.get("value")


def effective_section(payload: dict[str, Any]) -> dict[str, Any]:
    return payload.get("effective", payload)


def config_diff(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    changes: list[dict[str, Any]] = []
    before_effective = effective_section(before)
    after_effective = effective_section(after)
    namespaces = sorted(set(before_effective) | set(after_effective))
    for namespace in namespaces:
        before_fields = before_effective.get(namespace, {})
        after_fields = after_effective.get(namespace, {})
        for field_name in sorted(set(before_fields) | set(after_fields)):
            before_value = diffable_wrapped_value(before_fields.get(field_name, {}))
            after_value = diffable_wrapped_value(after_fields.get(field_name, {}))
            if before_value != after_value:
                changes.append({"path": f"{namespace}.{field_name}", "before": before_value, "after": after_value})
    diff: dict[str, Any] = {"changes": changes}
    if before.get("safety_status") != after.get("safety_status"):
        diff["status_change"] = {"before": before.get("safety_status"), "after": after.get("safety_status")}
    if before.get("diagnostics", []) != after.get("diagnostics", []):
        diff["diagnostic_changes"] = {"before": before.get("diagnostics", []), "after": after.get("diagnostics", [])}
    return diff
```

When wrapping field values in `effective_config`, include:

```python
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
```

- [ ] **Step 4: Implement CLI**

Add:

```python
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
    effective.add_argument("--layer", action="append", required=True)
    effective.add_argument("--requested-behavior", choices=["advisory", "mutation"], default="advisory")
    effective.add_argument("--issue-tracker-ops", action="store_true")
    diff = subparsers.add_parser("config-diff")
    diff.add_argument("--before", required=True)
    diff.add_argument("--after", required=True)
    return parser


def run(argv: list[str] | None = None, *, stdout: TextIO | None = None, stdout_text: bool = False) -> int | str:
    parser = build_parser()
    args = parser.parse_args(argv)
    output = stdout or sys.stdout
    if args.command == "config-diff":
        before = json.loads(Path(args.before).read_text(encoding="utf-8"))
        after = json.loads(Path(args.after).read_text(encoding="utf-8"))
        payload = config_diff(before, after)
    else:
        fragments = [issue_tracker_ops_fragment()] if args.issue_tracker_ops else []
        payload = effective_config([Path(path) for path in args.layer], fragments, requested_behavior=args.requested_behavior)
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if stdout_text:
        return text
    output.write(text)
    return 0


def main(argv: list[str] | None = None) -> int:
    result = run(argv)
    return result if isinstance(result, int) else 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: Run CLI tests**

Run:

```bash
python3.14 -m unittest tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_secret_reference_is_reported_without_value_resolution tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_config_diff_reports_changed_values tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_config_diff_reports_changed_secret_references tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_config_diff_reports_status_and_diagnostic_changes tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_cli_effective_config_outputs_json tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_cli_config_diff_outputs_json
```

Expected: `OK`.

- [ ] **Step 6: Commit**

```bash
git add tools/agent_equipment_config.py tests/test_agent_equipment_config.py
git commit -m "feat(config): add effective config cli" -m "Co-authored-by: Codex <noreply@openai.com>"
```

---

### Task 6: Plain Handoff, Missing Authority, And Projection Classification

**Files:**
- Modify: `tools/agent_equipment_config.py`
- Modify: `tests/test_agent_equipment_config.py`

- [ ] **Step 1: Write failing tests for plain handoff fallback, missing authority, and projection classification**

Append:

```python
    def test_plain_issue_tracker_ops_handoff_promotes_without_shared_config_layer(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            handoff = self.write_layer(root, "issue-tracker-handoff.toml", """
                [issue_tracker_ops]
                mode = "dry-run"
                external_disclosure = "blocked"
            """)

            result = agent_equipment_config.effective_config(
                [],
                [agent_equipment_config.issue_tracker_ops_fragment()],
                requested_behavior="advisory",
                plain_handoff_paths=[handoff],
            )

        self.assertEqual(result["safety_status"], "usable")
        self.assertEqual(result["effective"]["issue_tracker_ops"]["mode"]["value"], "dry-run")
        self.assertEqual(result["plain_handoffs"][0]["source"], handoff.as_posix())
        self.assertEqual(result["plain_handoffs"][0]["promoted_to"], "session overrides")
        self.assertEqual(result["enforcement_projection"]["classification"], "advisory")

    def test_cli_accepts_plain_handoff_without_layer(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            handoff = self.write_layer(root, "issue-tracker-handoff.toml", """
                [issue_tracker_ops]
                mode = "dry-run"
                external_disclosure = "blocked"
            """)

            stdout = agent_equipment_config.run(
                ["effective-config", "--plain-handoff", str(handoff), "--issue-tracker-ops"],
                stdout_text=True,
            )

        payload = json.loads(stdout)
        self.assertEqual(payload["safety_status"], "usable")
        self.assertEqual(payload["plain_handoffs"][0]["source"], handoff.as_posix())

    def test_missing_authority_blocks_mutation_projection_without_harness_enforcement(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            policy = self.write_layer(root, "org.toml", """
                [agent_equipment_config.layer]
                name = "organization or tracker policy"
                category = "committed durable config"

                [agent_equipment_config.policy.issue_tracker_ops.mode]
                required_for = "mutation"
                authority = "live_tracker_write"

                [issue_tracker_ops]
                mode = "execute"
                external_disclosure = "allowed"
            """)

            result = agent_equipment_config.effective_config([policy], [self.issue_ops_fragment()], requested_behavior="mutation")

        self.assertEqual(result["safety_status"], "unsafe")
        self.assertEqual(result["diagnostics"][0]["kind"], "missing authority")
        self.assertEqual(result["diagnostics"][0]["evidence"]["authority"], "live_tracker_write")
        self.assertEqual(result["enforcement_projection"]["classification"], "blocking")
        self.assertEqual(result["enforcement_projection"]["enforced_by_harness"], False)

    def test_usable_authority_allows_mutation_projection_to_remain_advisory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            policy = self.write_layer(root, "org.toml", """
                [agent_equipment_config.layer]
                name = "organization or tracker policy"
                category = "committed durable config"

                [agent_equipment_config.policy.issue_tracker_ops.mode]
                required_for = "mutation"
                authority = "live_tracker_write"

                [agent_equipment_config.authority]
                live_tracker_write = "usable"

                [issue_tracker_ops]
                mode = "execute"
                external_disclosure = "allowed"
            """)

            result = agent_equipment_config.effective_config([policy], [self.issue_ops_fragment()], requested_behavior="mutation")

        self.assertEqual(result["safety_status"], "usable")
        self.assertEqual(result["diagnostics"], [])
        self.assertEqual(result["enforcement_projection"]["classification"], "advisory")

    def test_untrusted_metadata_only_authority_cannot_authorize_mutation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            policy = self.write_layer(root, "org.toml", """
                [agent_equipment_config.layer]
                name = "organization or tracker policy"
                category = "committed durable config"

                [agent_equipment_config.policy.issue_tracker_ops.mode]
                required_for = "mutation"
                authority = "live_tracker_write"

                [issue_tracker_ops]
                mode = "execute"
                external_disclosure = "allowed"
            """)
            untrusted_authority = self.write_layer(root, "local.toml", """
                [agent_equipment_config.layer]
                name = "user/operator local overrides"
                category = "local-only operator config"
                trusted = false

                [agent_equipment_config.authority]
                live_tracker_write = "usable"
            """)

            result = agent_equipment_config.effective_config([policy, untrusted_authority], [self.issue_ops_fragment()], requested_behavior="mutation")

        self.assertEqual(result["safety_status"], "unsafe")
        self.assertIn("missing authority", [item["kind"] for item in result["diagnostics"]])
        self.assertEqual(result["enforcement_projection"]["classification"], "blocking")
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
python3.14 -m unittest tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_plain_issue_tracker_ops_handoff_promotes_without_shared_config_layer tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_cli_accepts_plain_handoff_without_layer tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_missing_authority_blocks_mutation_projection_without_harness_enforcement tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_usable_authority_allows_mutation_projection_to_remain_advisory tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_untrusted_metadata_only_authority_cannot_authorize_mutation
```

Expected: failures because plain handoff loading, authority status, and enforcement projection classification are missing.

- [ ] **Step 3: Implement plain handoff loading, authority checks, and projection classification**

Replace `PolicyLock` and `policy_locks` with:

```python
@dataclass(frozen=True)
class PolicyLock:
    namespace: str
    field: str
    layer: Layer
    required_for: str
    non_overridable: bool = False
    authority: str | None = None


def policy_locks(layer: Layer) -> dict[tuple[str, str], PolicyLock]:
    policy = layer.metadata.get("policy", {})
    locks: dict[tuple[str, str], PolicyLock] = {}
    for namespace, fields in policy.items():
        if not isinstance(fields, dict):
            continue
        for field_name, rule in fields.items():
            if not isinstance(rule, dict):
                continue
            non_overridable = bool(rule.get("non_overridable", False))
            authority = rule.get("authority")
            if non_overridable or isinstance(authority, str):
                locks[(namespace, field_name)] = PolicyLock(
                    namespace=namespace,
                    field=field_name,
                    layer=layer,
                    required_for=str(rule.get("required_for", "mutation")),
                    non_overridable=non_overridable,
                    authority=authority if isinstance(authority, str) else None,
                )
    return locks
```

Add:

```python
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


def authority_is_usable(layers: list[Layer], authority: str) -> bool:
    for layer in layers:
        if not layer.trusted:
            continue
        authority_table = layer.metadata.get("authority", {})
        if isinstance(authority_table, dict) and authority_table.get(authority) == "usable":
            return True
    return False


def enforcement_projection(safety_status: str, requested_behavior: str) -> dict[str, Any]:
    classification = "blocking" if requested_behavior == "mutation" and safety_status != "usable" else "advisory"
    return {
        "requested_behavior": requested_behavior,
        "classification": classification,
        "enforced_by_harness": False,
    }
```

Replace the whole `effective_config` function with:

```python
def effective_config(
    layer_paths: list[Path],
    fragments: list[SchemaFragment],
    *,
    requested_behavior: str,
    plain_handoff_paths: list[Path] | None = None,
) -> dict[str, Any]:
    handoff_layers, plain_handoffs = load_plain_handoff_layers(plain_handoff_paths or [])
    layers = sorted([*load_layers(layer_paths), *handoff_layers], key=lambda layer: (layer.precedence, layer.source_order))
    effective: dict[str, dict[str, Any]] = {}
    diagnostics: list[Diagnostic] = []
    migration_previews: list[dict[str, Any]] = []
    for fragment in fragments:
        namespace_values: dict[str, Any] = {}
        for field_name, field in fragment.fields.items():
            value = field.default
            source_layer: Layer | None = None
            active_lock: PolicyLock | None = None
            values_by_precedence: dict[int, tuple[JSONValue, Layer]] = {}
            field_conflicted = False
            path = f"{fragment.namespace}.{field_name}"
            for layer in layers:
                locks = policy_locks(layer)
                if (fragment.namespace, field_name) in locks:
                    active_lock = locks[(fragment.namespace, field_name)]
                section = layer.data.get(fragment.namespace, {})
                if field_name not in section:
                    continue
                candidate = section[field_name]
                prior_value = values_by_precedence.get(layer.precedence)
                if prior_value is not None and prior_value[0] != candidate:
                    diagnostics.append(
                        diagnostic(
                            "same-precedence collision",
                            path,
                            f"{layer.name} has multiple values at the same precedence",
                            layer,
                        )
                    )
                    value = None
                    source_layer = None
                    field_conflicted = True
                    continue
                values_by_precedence[layer.precedence] = (candidate, layer)
                lock_applies = active_lock is not None and active_lock.required_for in {requested_behavior, "always"}
                if lock_applies and active_lock.non_overridable and layer.precedence > active_lock.layer.precedence:
                    diagnostics.append(
                        diagnostic(
                            "blocked override",
                            path,
                            f"{layer.name} cannot override non-overridable value from {active_lock.layer.name}",
                            layer,
                            evidence={
                                "blocked_value": candidate,
                                "blocked_by": {
                                    "layer": active_lock.layer.name,
                                    "source": active_lock.layer.path,
                                },
                            },
                        )
                    )
                    continue
                if not field_conflicted:
                    value = candidate
                    source_layer = layer
            if active_lock is not None and active_lock.required_for in {requested_behavior, "always"} and active_lock.authority:
                if not authority_is_usable(layers, active_lock.authority):
                    diagnostics.append(
                        diagnostic(
                            "missing authority",
                            path,
                            f"missing usable authority {active_lock.authority!r} for {active_lock.required_for}",
                            active_lock.layer,
                            evidence={"authority": active_lock.authority, "required_for": active_lock.required_for},
                        )
                    )
            if value is None and field.required and not field_conflicted:
                diagnostics.append(diagnostic("schema conflict", path, "missing required value", source_layer))
            if not field_conflicted:
                diagnostics.extend(validate_field(value, field, path, source_layer))
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
    safety_status = safety_status_from_diagnostics(diagnostics, requested_behavior=requested_behavior)
    return {
        "safety_status": safety_status,
        "effective": effective,
        "diagnostics": [asdict(item) for item in diagnostics],
        "migration_previews": migration_previews,
        "plain_handoffs": plain_handoffs,
        "enforcement_projection": enforcement_projection(safety_status, requested_behavior),
    }
```

Update `safety_status_from_diagnostics` so `missing authority` is unsafe:

```python
def safety_status_from_diagnostics(diagnostics: list[Diagnostic], *, requested_behavior: str) -> str:
    kinds = {item.kind for item in diagnostics}
    # Precedence is intentional: structural conflicts first, then incomplete schema,
    # then provenance/version hazards, then semantic or authority unsafety.
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
```

Update `build_parser` and `run` while preserving the `config-diff` subcommand:

```python
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


def run(argv: list[str] | None = None, *, stdout: TextIO | None = None, stdout_text: bool = False) -> int | str:
    parser = build_parser()
    args = parser.parse_args(argv)
    output = stdout or sys.stdout
    if args.command == "config-diff":
        before = json.loads(Path(args.before).read_text(encoding="utf-8"))
        after = json.loads(Path(args.after).read_text(encoding="utf-8"))
        payload = config_diff(before, after)
    else:
        fragments = [issue_tracker_ops_fragment()] if args.issue_tracker_ops else []
        payload = effective_config(
            [Path(path) for path in args.layer],
            fragments,
            requested_behavior=args.requested_behavior,
            plain_handoff_paths=[Path(path) for path in args.plain_handoff],
        )
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if stdout_text:
        return text
    output.write(text)
    return 0
```

- [ ] **Step 4: Run handoff and projection tests**

Run:

```bash
python3.14 -m unittest tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_plain_issue_tracker_ops_handoff_promotes_without_shared_config_layer tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_cli_accepts_plain_handoff_without_layer tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_missing_authority_blocks_mutation_projection_without_harness_enforcement tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_usable_authority_allows_mutation_projection_to_remain_advisory tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_untrusted_metadata_only_authority_cannot_authorize_mutation
```

Expected: `OK`.

- [ ] **Step 5: Commit**

```bash
git add tools/agent_equipment_config.py tests/test_agent_equipment_config.py
git commit -m "feat(config): support handoff and authority projection" -m "Co-authored-by: Codex <noreply@openai.com>"
```

---

### Task 7: Issue Tracker Ops Pressure Regression And Documentation

**Files:**
- Modify: `tests/test_agent_equipment_config.py`
- Modify: `specs/agent-equipment-config/validation-plan.md`
- Modify: `specs/agent-equipment-config/README.md`
- Modify: `specs/agent-equipment-config/pressure-scenarios.md`
- Modify: `specs/agent-equipment-config/interface-decision-record.md`
- Modify: `specs/agent-equipment-config/security-control-classification.md`
- Modify: `specs/agent-equipment-config/closeout-evidence-plan.md`

- [ ] **Step 1: Write pressure scenario regression test**

This is a post-implementation pressure regression: Task 6 provides the failing
tests for the underlying handoff, missing-authority, and projection behavior.
This test proves those pieces work together for the Issue Tracker Ops scenario
before updating the spec evidence.

Append:

```python
    def test_issue_tracker_ops_pressure_scenario_blocks_execute_without_authority(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            org = self.write_layer(root, "org.toml", """
                [agent_equipment_config.layer]
                name = "organization or tracker policy"
                category = "committed durable config"

                [agent_equipment_config.policy.issue_tracker_ops.mode]
                non_overridable = true
                required_for = "mutation"
                authority = "live_tracker_write"

                [issue_tracker_ops]
                mode = "dry-run"
                external_disclosure = "blocked"
            """)
            session = self.write_layer(root, "session.toml", """
                [agent_equipment_config.layer]
                name = "session overrides"
                category = "session override"

                [issue_tracker_ops]
                mode = "execute"
            """)

            result = agent_equipment_config.effective_config([org, session], [agent_equipment_config.issue_tracker_ops_fragment()], requested_behavior="mutation")

        self.assertEqual(result["effective"]["issue_tracker_ops"]["mode"]["value"], "dry-run")
        self.assertEqual(result["safety_status"], "conflicted")
        self.assertEqual(result["diagnostics"][0]["kind"], "blocked override")
        self.assertEqual(result["diagnostics"][0]["evidence"]["blocked_value"], "execute")
        self.assertEqual(result["diagnostics"][0]["evidence"]["blocked_by"]["layer"], "organization or tracker policy")
        self.assertEqual(result["diagnostics"][0]["evidence"]["blocked_by"]["source"], org.as_posix())
        self.assertIn("missing authority", [item["kind"] for item in result["diagnostics"]])
        self.assertEqual(result["enforcement_projection"]["classification"], "blocking")
        self.assertFalse(result["enforcement_projection"]["enforced_by_harness"])
```

- [ ] **Step 2: Run pressure scenario regression test**

Run:

```bash
python3.14 -m unittest tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_issue_tracker_ops_pressure_scenario_blocks_execute_without_authority
```

Expected: `OK` if Task 3, Task 5, and Task 6 are correct. If it fails, fix the implementation rather than weakening the test.

- [ ] **Step 3: Update runtime status claims across the bundle**

Replace the opening implementation-status sentence in these files:

- `specs/agent-equipment-config/README.md`
- `specs/agent-equipment-config/validation-plan.md`
- `specs/agent-equipment-config/pressure-scenarios.md`
- `specs/agent-equipment-config/interface-decision-record.md`
- `specs/agent-equipment-config/security-control-classification.md`
- `specs/agent-equipment-config/closeout-evidence-plan.md`

Use this current status:

```markdown
This Forge Entry Bundle describes desired behavior and includes the first
standard-library runtime engine slice for effective-config, config-diff,
diagnostics, plain handoff promotion, authority checks, and projection
classification. It does not publish Agent Equipment assets, resolve secrets,
mutate source config, mutate external systems, or implement harness controls.
```

Also make these targeted updates:

- In `specs/agent-equipment-config/interface-decision-record.md`, replace claims
  that the change set only defines source shape or does not build a runtime
  engine with language that names the implemented portable runtime slice and
  still defers consumer integration, onboarding, harness adapters, and
  enforcement.
- In `specs/agent-equipment-config/security-control-classification.md`, replace
  residual-risk claims that no parser or merge engine exists with language that
  limits the implemented parser and merge behavior to the tested portable CLI
  and keeps config mutation commands, provider-specific secret resolution, and
  harness controls out of scope.
- In `specs/agent-equipment-config/validation-plan.md`, replace the residual
  risk paragraph with language that says the runtime slice proves only the
  deterministic CLI behaviors covered by `tests.test_agent_equipment_config`;
  it does not prove external enforcement, provider secret resolution, source
  mutation, or harness-specific control projection.
- In `specs/agent-equipment-config/closeout-evidence-plan.md`, update the
  remaining-evidence list so deterministic effective-config engine evidence is
  marked complete by the runtime-slice command, while harness projection,
  external publication, and promotion beyond the runtime slice remain future.

- [ ] **Step 4: Update validation plan command list**

In `specs/agent-equipment-config/validation-plan.md`, add this item to "Current deterministic checks":

```markdown
- `python3.14 -m unittest tests.test_agent_equipment_config`
```

Rename "Future runtime cases" to "Runtime cases". Under that section, add this
subsection after the existing bullet list:

```markdown
Implemented by the v0 engine slice:

- TOML layer loading;
- schema fragment validation;
- effective-config output;
- config-diff output for values, secret-reference identity, status changes, and diagnostic changes;
- Config Safety Status classification;
- deprecation diagnostics and migration-preview output with audit-preview shape;
- plain Issue Tracker Ops handoff fallback and promotion;
- missing-authority diagnostics for mutation-gated settings;
- enforcement projection classification as `blocking` or `advisory`;
- Issue Tracker Ops pressure scenario for blocked live mutation.
```

- [ ] **Step 5: Update README bundle status**

In `specs/agent-equipment-config/README.md`, add this section after "V0 contract":

```markdown
## Runtime slice

The first runtime slice provides a standard-library Python effective-config
engine for deterministic validation and pressure coverage. It previews source
migrations and classifies enforcement projections, but does not rewrite source
config, resolve secrets, or implement harness controls.
```

- [ ] **Step 6: Add runtime-slice harness projection discussion**

In `specs/agent-equipment-config/README.md`, add this subsection under
"Runtime slice":

```markdown
### Runtime-slice harness projections

The runtime slice exposes one portable CLI. Each harness projection invokes the
CLI with the layer paths it can discover, receives effective-config or config-diff
JSON, and treats `blocking` classifications as decision evidence until a later
harness adapter implements blocking controls.

| Harness | Discovery and exposure for this slice | Blocking and advisory boundary |
| --- | --- | --- |
| Codex | A Codex agent, hook, automation, or external `codex exec` wrapper supplies repository-committed TOML, local-only TOML, checkout-local state, generated state, `--plain-handoff` session TOML, and schema fragments through the Python module. Effective-config and config-diff JSON are printed to stdout or captured by the invoking agent surface. Secret references stay unresolved metadata. | The engine classifies mutation-unsafe output as `blocking`, but Codex enforcement remains advisory unless a future hook, permission profile, or automation wrapper consumes the JSON and blocks the action. |
| OpenClaw | An OpenClaw command, hook, cron job, heartbeat turn, or plugin background service supplies the same layer categories and schema fragments to the portable CLI. Effective-config and config-diff JSON are exposed through the invoking command or plugin surface. Secret references stay unresolved metadata. | The engine classifies blocking conditions deterministically; actual OpenClaw hook, webhook, cron, or plugin blocking remains a future adapter concern. |
| Hermes Agent | A Hermes Agent gateway hook, plugin hook, cron job, curator job, terminal process, or profile-driven command invokes the CLI with committed, local-only, checkout-local, generated, session, and secret-reference inputs. Effective-config and config-diff JSON are returned to the invoking agent surface. | Blocking classifications are decision evidence only until a Hermes-specific gateway, plugin, toolset, or profile adapter enforces them. |
| Claude Code | A Claude Code hook, Routine, scheduled task, or command invokes the CLI with the available layer paths and schema fragments. Effective-config and config-diff JSON are visible in the command output or captured task context. Secret references remain typed pointers. | Blocking classifications guide the agent or hook consumer; no Claude Code hook or settings enforcement is implemented in this slice. |
| Cursor | Cursor rules, hooks, Cloud Agent Automations, SDK agents, or CLI configuration can invoke the CLI with the discovered layer paths and schema fragments. Effective-config and config-diff JSON are exposed through the caller. Secret references remain unresolved metadata. | Blocking classifications are advisory until a Cursor hook, automation, SDK agent, or policy surface consumes the JSON and prevents the action. |
| OpenCode | An OpenCode command template, plugin hook, GitHub Action, external scheduler, or `opencode run` wrapper invokes the CLI with committed, local-only, checkout-local, generated, session, and secret-reference inputs. Effective-config and config-diff JSON are returned to the invoking surface. | Blocking classifications are not enforced by OpenCode in this slice; a future plugin hook, permission, or wrapper may turn them into blocking controls. |
```

- [ ] **Step 7: Update pressure scenario status**

In `specs/agent-equipment-config/pressure-scenarios.md`, add this paragraph after the "Expected Config behavior" list in "Primary scenario: Issue Tracker Ops":

```markdown
Runtime coverage: `tests.test_agent_equipment_config` covers the blocked
session override path and missing-authority path for Issue Tracker Ops
mutation. The broader pressure scenario still needs harness-specific
enforcement implementation before promotion beyond `planned`.
```

- [ ] **Step 8: Commit**

```bash
git add tests/test_agent_equipment_config.py specs/agent-equipment-config/validation-plan.md specs/agent-equipment-config/README.md specs/agent-equipment-config/pressure-scenarios.md specs/agent-equipment-config/interface-decision-record.md specs/agent-equipment-config/security-control-classification.md specs/agent-equipment-config/closeout-evidence-plan.md
git commit -m "test(config): cover issue tracker pressure scenario" -m "Co-authored-by: Codex <noreply@openai.com>"
```

---

### Task 8: Validator, Security, And Closeout

**Files:**
- Modify: `tools/validate_forge_seed.py`
- Modify: `tests/test_validate_forge_seed.py`
- Modify: `specs/agent-equipment-config/closeout-evidence-plan.md`

- [ ] **Step 1: Write failing validator test for runtime command mention**

In `tests/test_validate_forge_seed.py`, extend `CONFIG_BUNDLE_REQUIRED_TEXT` fixture expectations in `SpecValidationTests.test_validate_specs_requires_each_agent_equipment_config_required_term` by adding:

```python
"python3.14 -m unittest tests.test_agent_equipment_config",
```

Run:

```bash
python3.14 -m unittest tests.test_validate_forge_seed.SpecValidationTests.test_validate_specs_requires_each_agent_equipment_config_required_term
```

Expected: failure until validator required text and docs are aligned.

- [ ] **Step 2: Update validator required terms**

In `tools/validate_forge_seed.py`, add to `CONFIG_BUNDLE_REQUIRED_TEXT`:

```python
"python3.14 -m unittest tests.test_agent_equipment_config",
```

- [ ] **Step 3: Update closeout evidence plan**

In `specs/agent-equipment-config/closeout-evidence-plan.md`, add this bullet to "Required evidence":

```markdown
- Agent Equipment Config runtime-slice command
  `python3.14 -m unittest tests.test_agent_equipment_config` and the focused
  security review conclusion for executable parsing, merge, diff, migration
  preview, plain handoff, authority, projection-classification, and
  secret-reference behavior.
- Change Set Security Closeout for the runtime slice, including scope,
  action performed, artifact durability classification, finding disposition,
  fixes, suppressions, deferments, or explicit non-applicability notes.
- Change Set Documentation Closeout for affected agent-facing and human-facing
  docs, including updated surfaces or a no-change rationale for each plausible
  affected surface.
- Full `docs/story-closeout.md` gate order before merge-readiness, including
  Intent Model Refresh, scope/validation coherence, security closeout,
  documentation closeout, projection draft or pending-projection rationale,
  Reflection Finding disclosure/routing, latest clean Cross-Boundary Coherence
  and Story Quality Ralph Review cycles, final validation, and publication
  readiness checks.
```

- [ ] **Step 4: Run focused validator tests**

Run:

```bash
python3.14 -m unittest tests.test_validate_forge_seed.SpecValidationTests
```

Expected: `OK`.

- [ ] **Step 5: Run full verification**

Run:

```bash
python3.14 -m unittest
python3.14 tools/validate_forge_seed.py
python3.14 tools/validate_forge_seed.py --final-closeout
git diff --check
```

Expected:

- unittest: all tests pass.
- normal Forge Seed validation: `0 failed`.
- final-closeout validation: `0 failed`.
- `git diff --check`: no output and exit 0.

- [ ] **Step 6: Perform security closeout**

Inspect this diff for:

- executable parsing of TOML;
- path handling;
- no network access;
- no subprocess calls;
- no source config rewrite;
- migration preview and audit-preview output remaining diagnostic-only;
- plain handoff promotion not writing source config;
- missing-authority and enforcement projection classification remaining
  diagnostic-only;
- no secret value logging or resolution;
- JSON and config-diff output not exposing secret values;
- mutation behavior remaining diagnostic-only.

Run the Codex Security workflow for the executable diff, or record why a
focused security review is the selected narrower security action. Record:

- security scope;
- command, workflow, or manual review method;
- artifact durability classification;
- findings, fixes, suppressions, approved deferments, or no-findings conclusion.

If a reportable issue is found, fix it before this task is complete.

- [ ] **Step 7: Perform documentation closeout**

Inspect affected agent-facing and human-facing docs before merge-readiness:

- `AGENTS.md`;
- `CONTEXT.md`;
- `docs/ubiquitous-language.md`;
- Forge Canon under `docs/`;
- `specs/agent-equipment-config/`;
- `templates/`;
- `examples/`;
- validator tests and closeout/security docs when changed.

Update stale or incomplete surfaces, or record a no-change rationale for each
plausible affected surface in the PR body, final change summary, issue tracker,
or a neutral committed closeout document.

- [ ] **Step 8: Run repo-required story closeout gates**

After deterministic validation, security closeout, and documentation closeout
are current, complete the repo-required gate order from `docs/story-closeout.md`:

- Refresh the Intent Model from current operator input, accepted spec/plan
  changes, review dispositions, handoff notes, and observed corrections.
- Confirm implementation, specs, plan, and deterministic validation reflect the
  same scope.
- Prepare projection drafts for issues, PR bodies, handoff notes, and release
  summaries from current story evidence, or record a pending-projection
  rationale.
- Classify privacy and disclosure limits for actionable Reflection Findings,
  then route publishable findings or record why the insight is not durable or
  projectable.

Run the repo-required review loops after the upstream gates are current:

- Cross-Boundary Coherence Ralph Review across PRD, specs, plan,
  implementation, deterministic validation, security, documentation, issue/PR
  projection, and handoff surfaces.
- Story Quality Ralph Review for DX, UX, code quality, architecture,
  robustness against unspecified interactions and attack paths, lessons from
  prior dev/ops cycles, and alignment with `docs/vision.md`.

Use the applicable doc-review guidance where those surfaces are affected:
`honing-agent-facing-docs`, `honing-human-facing-docs`, `writing-skills`,
`documentation-writer`, and `writing-clearly-and-concisely`. Each loop must have
a latest clean cycle before merge-readiness.

After both review loops have latest clean cycles, run final validation and
publication-readiness checks required by this plan and repository policy,
including `python3.14 tools/validate_forge_seed.py --final-closeout`.

- [ ] **Step 9: Commit**

```bash
git add tools/validate_forge_seed.py tests/test_validate_forge_seed.py specs/agent-equipment-config/closeout-evidence-plan.md
git commit -m "test(config): validate runtime slice coverage" -m "Co-authored-by: Codex <noreply@openai.com>"
```

---

## Self-Review Checklist

- Spec coverage: tasks cover schema fragments, layered config, Layer Precedence, Policy Authority, same-precedence collisions, higher-authority policy preservation over lower-authority collisions, effective-config, config-diff for values/status/diagnostics, behavior-aware semantic validators, Config Safety Status precedence, deprecation diagnostics, migration previews with audit-preview shape, secret references, session-scoped behavior, plain Issue Tracker Ops handoff fallback/promotion, missing authority, enforcement projection classification, Issue Tracker Ops pressure, bundle runtime-status updates, and validation commands.
- Deliberate deferrals: source rewrites, migration apply execution, provider-specific secret fetching, and harness blocking-control implementation remain out of scope and are named in the plan.
- Type consistency: `Layer`, `FieldSpec`, `SchemaFragment`, `MigrationPreview`, `Diagnostic`, `PolicyLock`, `effective_config`, `config_diff`, `enforcement_projection`, and `issue_tracker_ops_fragment` are introduced before use in later tasks.
- Security boundary: no network, subprocess, secret fetching, or source mutation is part of the runtime slice; untrusted layers cannot supply usable authority for mutation.
- Closeout boundary: merge-readiness requires the full `docs/story-closeout.md` gate order, not only deterministic checks and review summaries.

## Execution Handoff

Plan complete. Use `superpowers:subagent-driven-development` for task-by-task implementation with review between tasks, or `superpowers:executing-plans` for inline execution in this session.
