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

    def test_multi_equipment_composition_keeps_neutral_fragments_separate(self):
        issue_ops = agent_equipment_config.SchemaFragment(
            namespace="issue_tracker_ops",
            version=1,
            fields={"mode": agent_equipment_config.FieldSpec(type="string", required=True)},
        )
        docs_research = agent_equipment_config.SchemaFragment(
            namespace="docs_research",
            version=1,
            fields={"citation_policy": agent_equipment_config.FieldSpec(type="string", default="required")},
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "repo.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [issue_tracker_ops]
                mode = "dry-run"

                [docs_research]
                citation_policy = "source-backed"
            """)

            result = agent_equipment_config.effective_config([layer], [issue_ops, docs_research], requested_behavior="advisory")

        self.assertEqual(result["effective"]["issue_tracker_ops"]["mode"]["value"], "dry-run")
        self.assertEqual(result["effective"]["docs_research"]["citation_policy"]["value"], "source-backed")
        self.assertEqual(result["safety_status"], "usable")
