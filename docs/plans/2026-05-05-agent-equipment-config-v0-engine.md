# Agent Equipment Config V0 Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first deterministic Agent Equipment Config v0 engine for schema-fragment validation, layered effective-config output, config-diff output, diagnostics, and Issue Tracker Ops pressure coverage.

**Architecture:** Add one standard-library Python CLI and module at `tools/agent_equipment_config.py`, with tests in `tests/test_agent_equipment_config.py`. The engine reads TOML layer files, registers JSON-compatible schema fragments, computes effective-config and config-diff JSON, and emits diagnostics without mutating source config or resolving secret values.

**Tech Stack:** Python 3.14 standard library, `tomllib`, `argparse`, `json`, `dataclasses`, `unittest`.

---

## Scope

This plan implements the first runtime slice from `specs/agent-equipment-config/validation-plan.md`.

In scope:

- TOML layer loading.
- Canonical Layer Precedence.
- JSON-compatible schema fragments.
- Required-key, type, enum, default, deprecation, version, and migration-preview metadata.
- Diagnostic-only semantic validators.
- Effective-config JSON output with value provenance.
- Config-diff JSON output.
- Config Safety Status for `usable`, `incomplete`, `unsafe`, `stale`, `untrusted`, and `conflicted`.
- Secret reference recognition and status reporting without fetching values.
- Issue Tracker Ops pressure fixture.

Out of scope:

- Source config rewrites.
- Provider-specific secret fetching.
- Hook, permission, approval, sandbox, or tool enforcement.
- Harness-specific installation.
- Network access.
- GitHub issue mutation.

## File Structure

- Create `tools/agent_equipment_config.py`: CLI, data model, TOML loading, fragment registration, validation, merge, diff, and JSON output.
- Create `tests/test_agent_equipment_config.py`: behavior tests for each v0 contract case.
- Modify `specs/agent-equipment-config/validation-plan.md`: add the new test command and note the implemented runtime subset.
- Modify `specs/agent-equipment-config/README.md`: update promotion language only if the engine slice completes and remains consistent with the promotion path.
- Modify `docs/README.md` or `README.md` only if the public roadmap needs a new status phrase after implementation.

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
```

- [ ] **Step 2: Run the tests to verify they fail**

Run:

```bash
python3.14 -m unittest tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_schema_fragment_applies_defaults_and_reports_missing_required_keys tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_schema_fragment_rejects_wrong_type
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


@dataclass(frozen=True)
class SchemaFragment:
    namespace: str
    version: int
    fields: dict[str, FieldSpec]
    semantic_validators: tuple[Callable[[dict[str, Any]], list["Diagnostic"]], ...] = ()


@dataclass(frozen=True)
class Diagnostic:
    kind: str
    path: str
    detail: str
    layer: str | None = None
    source: str | None = None


TYPE_CHECKS: dict[str, type | tuple[type, ...]] = {
    "string": str,
    "boolean": bool,
    "integer": int,
    "number": (int, float),
    "object": dict,
    "array": list,
}


def diagnostic(kind: str, path: str, detail: str, layer: Layer | None = None) -> Diagnostic:
    return Diagnostic(
        kind=kind,
        path=path,
        detail=detail,
        layer=layer.name if layer else None,
        source=layer.path if layer else None,
    )


def validate_field(value: JSONValue, field: FieldSpec, path: str, layer: Layer | None) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    expected = TYPE_CHECKS[field.type]
    if value is not None and not isinstance(value, expected):
        diagnostics.append(diagnostic("schema conflict", path, f"expected {field.type}", layer))
    if field.enum is not None and value is not None and value not in field.enum:
        diagnostics.append(diagnostic("schema conflict", path, f"expected one of {field.enum!r}", layer))
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
    if any(item.kind == "schema conflict" and "missing required" in item.detail for item in diagnostics):
        return "incomplete"
    if diagnostics:
        return "conflicted"
    return "usable"
```

- [ ] **Step 4: Run schema tests**

Run:

```bash
python3.14 -m unittest tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_schema_fragment_applies_defaults_and_reports_missing_required_keys tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_schema_fragment_rejects_wrong_type
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
python3.14 -m unittest tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_later_layer_wins_when_not_locked tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_policy_authority_blocks_lower_authority_override_for_mutation
```

Expected: second test fails because policy locks are not implemented.

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

Replace field merge logic inside `effective_config` with:

```python
            active_lock: PolicyLock | None = None
            for layer in layers:
                locks = policy_locks(layer)
                if (fragment.namespace, field_name) in locks:
                    active_lock = locks[(fragment.namespace, field_name)]
                section = layer.data.get(fragment.namespace, {})
                if field_name not in section:
                    continue
                candidate = section[field_name]
                lock_applies = active_lock is not None and active_lock.required_for in {requested_behavior, "always"}
                if lock_applies and layer.precedence > active_lock.layer.precedence:
                    diagnostics.append(
                        diagnostic(
                            "blocked override",
                            f"{fragment.namespace}.{field_name}",
                            f"{layer.name} cannot override non-overridable value from {active_lock.layer.name}",
                            layer,
                        )
                    )
                    continue
                value = candidate
                source_layer = layer
```

- [ ] **Step 4: Run precedence tests**

Run:

```bash
python3.14 -m unittest tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_later_layer_wins_when_not_locked tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_policy_authority_blocks_lower_authority_override_for_mutation
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

    def test_semantic_validator_can_mark_config_unsafe(self):
        def execute_requires_disclosure(values):
            if values.get("mode") == "execute" and values.get("external_disclosure") != "allowed":
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
python3.14 -m unittest tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_untrusted_layer_sets_untrusted_for_mutation tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_stale_fragment_version_reports_stale_without_rewriting_source tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_semantic_validator_can_mark_config_unsafe
```

Expected: failures because untrusted, stale, and semantic validators are not complete.

- [ ] **Step 3: Implement remaining safety logic**

Add helpers:

```python
def fragment_versions(layer: Layer) -> dict[str, int]:
    versions = layer.metadata.get("fragment_versions", {})
    return {str(key): int(value) for key, value in versions.items()} if isinstance(versions, dict) else {}


def raw_values_for_namespace(effective_namespace: dict[str, Any]) -> dict[str, JSONValue]:
    return {
        field_name: wrapped.get("value")
        for field_name, wrapped in effective_namespace.items()
    }
```

Before returning from each namespace loop in `effective_config`, add:

```python
        for layer in layers:
            if not layer.trusted and fragment.namespace in layer.data and requested_behavior == "mutation":
                diagnostics.append(diagnostic("untrusted source", fragment.namespace, f"{layer.name} is not trusted for mutation", layer))
            versions = fragment_versions(layer)
            if fragment.namespace in versions and versions[fragment.namespace] < fragment.version:
                diagnostics.append(diagnostic("stale schema", fragment.namespace, f"source version {versions[fragment.namespace]} is older than schema version {fragment.version}", layer))
        plain_values = raw_values_for_namespace(namespace_values)
        for validator in fragment.semantic_validators:
            diagnostics.extend(validator(plain_values))
```

Replace `safety_status_from_diagnostics` with:

```python
def safety_status_from_diagnostics(diagnostics: list[Diagnostic], *, requested_behavior: str) -> str:
    kinds = {item.kind for item in diagnostics}
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
python3.14 -m unittest tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_untrusted_layer_sets_untrusted_for_mutation tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_stale_fragment_version_reports_stale_without_rewriting_source tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_semantic_validator_can_mark_config_unsafe
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
python3.14 -m unittest tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_secret_reference_is_reported_without_value_resolution tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_config_diff_reports_changed_values tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_cli_effective_config_outputs_json
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


def config_diff(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    changes: list[dict[str, Any]] = []
    namespaces = sorted(set(before) | set(after))
    for namespace in namespaces:
        before_fields = before.get(namespace, {})
        after_fields = after.get(namespace, {})
        for field_name in sorted(set(before_fields) | set(after_fields)):
            before_value = before_fields.get(field_name, {}).get("value")
            after_value = after_fields.get(field_name, {}).get("value")
            if before_value != after_value:
                changes.append({"path": f"{namespace}.{field_name}", "before": before_value, "after": after_value})
    return {"changes": changes}
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
    def execute_requires_disclosure(values: dict[str, Any]) -> list[Diagnostic]:
        if values.get("mode") == "execute" and values.get("external_disclosure") != "allowed":
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
    return parser


def run(argv: list[str] | None = None, *, stdout: TextIO | None = None, stdout_text: bool = False) -> int | str:
    parser = build_parser()
    args = parser.parse_args(argv)
    output = stdout or sys.stdout
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
python3.14 -m unittest tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_secret_reference_is_reported_without_value_resolution tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_config_diff_reports_changed_values tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_cli_effective_config_outputs_json
```

Expected: `OK`.

- [ ] **Step 6: Commit**

```bash
git add tools/agent_equipment_config.py tests/test_agent_equipment_config.py
git commit -m "feat(config): add effective config cli" -m "Co-authored-by: Codex <noreply@openai.com>"
```

---

### Task 6: Issue Tracker Ops Pressure Coverage And Documentation

**Files:**
- Modify: `tests/test_agent_equipment_config.py`
- Modify: `specs/agent-equipment-config/validation-plan.md`
- Modify: `specs/agent-equipment-config/README.md`
- Modify: `specs/agent-equipment-config/pressure-scenarios.md`

- [ ] **Step 1: Write pressure scenario regression test**

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
```

- [ ] **Step 2: Run pressure scenario regression test**

Run:

```bash
python3.14 -m unittest tests.test_agent_equipment_config.AgentEquipmentConfigTests.test_issue_tracker_ops_pressure_scenario_blocks_execute_without_authority
```

Expected: `OK` if Task 3 and Task 5 are correct. If it fails, fix the implementation rather than weakening the test.

- [ ] **Step 3: Update validation plan command list**

In `specs/agent-equipment-config/validation-plan.md`, add this item to "Current deterministic checks":

```markdown
- `python3.14 -m unittest tests.test_agent_equipment_config`
```

Under "Future runtime cases", add this subsection after the existing bullet list:

```markdown
Implemented by the v0 engine slice:

- TOML layer loading;
- schema fragment validation;
- effective-config output;
- config-diff output;
- Config Safety Status classification;
- Issue Tracker Ops pressure scenario for blocked live mutation.
```

- [ ] **Step 4: Update README bundle status**

In `specs/agent-equipment-config/README.md`, add this section after "V0 contract":

```markdown
## Runtime slice

The first runtime slice provides a standard-library Python effective-config
engine for deterministic validation and pressure coverage. It does not apply
source migrations, resolve secrets, or enforce harness controls.
```

- [ ] **Step 5: Update pressure scenario status**

In `specs/agent-equipment-config/pressure-scenarios.md`, add this paragraph after the "Expected Config behavior" list in "Primary scenario: Issue Tracker Ops":

```markdown
Runtime coverage: `tests.test_agent_equipment_config` covers the blocked
session override path for Issue Tracker Ops mutation. The broader pressure
scenario still needs harness-specific projection coverage before promotion
beyond `planned`.
```

- [ ] **Step 6: Commit**

```bash
git add tests/test_agent_equipment_config.py specs/agent-equipment-config/validation-plan.md specs/agent-equipment-config/README.md specs/agent-equipment-config/pressure-scenarios.md
git commit -m "test(config): cover issue tracker pressure scenario" -m "Co-authored-by: Codex <noreply@openai.com>"
```

---

### Task 7: Validator, Security, And Closeout

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

- [ ] **Step 3: Run focused validator tests**

Run:

```bash
python3.14 -m unittest tests.test_validate_forge_seed.SpecValidationTests
```

Expected: `OK`.

- [ ] **Step 4: Run full verification**

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

- [ ] **Step 5: Perform focused security review**

Inspect this diff for:

- executable parsing of TOML;
- path handling;
- no network access;
- no subprocess calls;
- no source config rewrite;
- no secret value logging or resolution;
- JSON output not exposing secret values;
- mutation behavior remaining diagnostic-only.

Record the conclusion in the final change summary or PR body. If a reportable issue is found, fix it before this task is complete.

- [ ] **Step 6: Commit**

```bash
git add tools/validate_forge_seed.py tests/test_validate_forge_seed.py specs/agent-equipment-config/closeout-evidence-plan.md
git commit -m "test(config): validate runtime slice coverage" -m "Co-authored-by: Codex <noreply@openai.com>"
```

---

## Self-Review Checklist

- Spec coverage: tasks cover schema fragments, layered config, Layer Precedence, Policy Authority, effective-config, config-diff, semantic validators, Config Safety Status, migrations as stale previews, secret references, session-scoped behavior, plain Issue Tracker Ops handoff pressure, and validation commands.
- Deliberate deferrals: source rewrites, provider-specific secret fetching, and harness blocking enforcement remain out of scope and are named in the plan.
- Type consistency: `Layer`, `FieldSpec`, `SchemaFragment`, `Diagnostic`, `effective_config`, `config_diff`, and `issue_tracker_ops_fragment` are introduced before use in later tasks.
- Security boundary: no network, subprocess, secret fetching, or source mutation is part of the runtime slice.

## Execution Handoff

Plan complete. Use `superpowers:subagent-driven-development` for task-by-task implementation with review between tasks, or `superpowers:executing-plans` for inline execution in this session.
