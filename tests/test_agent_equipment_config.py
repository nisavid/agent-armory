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
