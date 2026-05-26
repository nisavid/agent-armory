import contextlib
import io
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

    def issue_tracker_ops_consumer_decision(
        self,
        result: dict,
        *,
        requested_behavior: str,
        supported_capabilities: frozenset[str] = frozenset({"tracker_read", "tracker_write"}),
    ) -> dict[str, object]:
        return agent_equipment_config.consumer_action_decision(
            result,
            equipment="issue_tracker_ops",
            requested_behavior=requested_behavior,
            required_capabilities=["tracker_write"] if requested_behavior == "mutation" else [],
            supported_capabilities=supported_capabilities,
        )

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

    def test_published_config_example_loads_as_repository_policy(self):
        root = Path(__file__).parents[1]
        example = root / "templates/config/agent-equipment-config-example.toml"

        advisory_result = agent_equipment_config.effective_config(
            [example],
            [self.issue_ops_fragment()],
            requested_behavior="advisory",
        )
        mutation_result = agent_equipment_config.effective_config(
            [example],
            [self.issue_ops_fragment()],
            requested_behavior="mutation",
        )

        self.assertEqual(advisory_result["safety_status"], "usable")
        self.assertEqual(advisory_result["effective"]["issue_tracker_ops"]["mode"]["value"], "dry-run")
        self.assertEqual(advisory_result["effective"]["issue_tracker_ops"]["mode"]["layer"], "repository policy")
        self.assertEqual(advisory_result["effective"]["issue_tracker_ops"]["external_disclosure"]["value"], "blocked")
        self.assertEqual(mutation_result["safety_status"], "usable")
        self.assertEqual(mutation_result["effective"]["issue_tracker_ops"]["mode"]["value"], "dry-run")
        self.assertEqual(mutation_result["effective"]["issue_tracker_ops"]["external_disclosure"]["value"], "blocked")

    def test_committed_agent_armory_issue_ops_policy_layer_validates(self):
        root = Path(__file__).parents[1]
        policy = root / "config/agent-equipment.toml"

        result = agent_equipment_config.effective_config(
            [policy],
            [agent_equipment_config.issue_tracker_ops_fragment()],
            requested_behavior="advisory",
        )

        self.assertEqual(result["safety_status"], "usable")
        self.assertEqual(result["effective"]["issue_tracker_ops"]["mode"]["value"], "dry-run")
        self.assertEqual(result["effective"]["issue_tracker_ops"]["external_disclosure"]["value"], "blocked")
        self.assertEqual(result["effective"]["issue_tracker_ops"]["policy_profile_status"]["value"], "authoritative")
        self.assertEqual(result["effective"]["issue_tracker_ops"]["tracker"]["value"]["repo"], "nisavid/agent-armory")
        label_axes = result["effective"]["issue_tracker_ops"]["label_axes"]["value"]
        self.assertIn(
            {"name": "category", "cardinality": "exactly_one", "description": "coarse issue category role", "labels": ["bug", "enhancement"]},
            label_axes,
        )

    def test_onboarding_reports_missing_shared_config_handoff_behavior(self):
        result = agent_equipment_config.config_onboarding_plan(
            [],
            [agent_equipment_config.issue_tracker_ops_fragment()],
            requested_behavior="mutation",
            shared_config_present=False,
        )

        self.assertEqual(result["onboarding_status"], "missing_shared_config")
        self.assertEqual(result["handoff_behavior"]["plain_handoff"], "required")
        self.assertEqual(result["handoff_behavior"]["mutation_capable_behavior"], "blocked")
        self.assertTrue(result["partial_config"]["schema_valid"])
        self.assertIn("secret reference source", [item["source_category"] for item in result["discovery_proposals"]])

    def test_onboarding_missing_shared_config_rejects_ignored_inputs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "repo.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"
            """)

            with self.assertRaisesRegex(agent_equipment_config.ConfigError, "shared Config is absent"):
                agent_equipment_config.config_onboarding_plan(
                    [layer],
                    [self.issue_ops_fragment()],
                    requested_behavior="mutation",
                    shared_config_present=False,
                )

    def test_onboarding_reports_missing_config_data_as_partial_output(self):
        result = agent_equipment_config.config_onboarding_plan(
            [],
            [self.issue_ops_fragment()],
            requested_behavior="mutation",
        )

        self.assertEqual(result["onboarding_status"], "missing_config_data")
        self.assertEqual(result["effective_config"]["safety_status"], "incomplete")
        self.assertEqual(
            result["partial_config"]["sections"]["issue_tracker_ops"]["missing_required"],
            ["external_disclosure", "mode"],
        )
        self.assertEqual(result["handoff_behavior"]["mutation_capable_behavior"], "blocked")
        self.assertIn("committed durable config", [item["source_category"] for item in result["discovery_proposals"]])

    def test_onboarding_discovery_proposals_describe_load_contract_responsibilities(self):
        result = agent_equipment_config.config_onboarding_plan(
            [],
            [self.issue_ops_fragment()],
            requested_behavior="mutation",
        )

        proposals = {
            item["source_category"]: item
            for item in result["discovery_proposals"]
        }

        self.assertEqual(proposals["committed durable config"]["core_discovery"], "none")
        self.assertEqual(
            proposals["committed durable config"]["caller_responsibility"],
            "discover, select, order, and pass source paths",
        )
        self.assertEqual(proposals["committed durable config"]["input_surfaces"], ["--layer", "layer_paths"])
        self.assertEqual(
            proposals["session override"]["input_surfaces"],
            ["--layer", "--plain-handoff", "layer_paths", "plain_handoff_paths"],
        )
        self.assertEqual(
            proposals["session override"]["provenance_requirement"],
            "agent_equipment_config.layer metadata or plain handoff promotion record",
        )
        self.assertEqual(
            proposals["secret reference source"]["secret_resolution"],
            "unresolved metadata only when present",
        )

    def test_interrupted_onboarding_keeps_partial_output_and_blocks_mutation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            partial = self.write_layer(root, "partial.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [issue_tracker_ops]
                mode = "dry-run"
            """)

            result = agent_equipment_config.config_onboarding_plan(
                [partial],
                [self.issue_ops_fragment()],
                requested_behavior="mutation",
                onboarding_state="interrupted",
            )

        self.assertEqual(result["onboarding_status"], "interrupted_partial")
        self.assertTrue(result["partial_config"]["schema_valid"])
        self.assertEqual(result["partial_config"]["unsafe_write_modes"], "blocked")
        self.assertEqual(result["partial_config"]["sections"]["issue_tracker_ops"]["missing_required"], ["external_disclosure"])

    def test_resumed_onboarding_can_complete_from_plain_handoff(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            partial = self.write_layer(root, "partial.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [issue_tracker_ops]
                mode = "dry-run"
            """)
            handoff = self.write_layer(root, "handoff.toml", """
                [issue_tracker_ops]
                external_disclosure = "blocked"
            """)

            result = agent_equipment_config.config_onboarding_plan(
                [partial],
                [self.issue_ops_fragment()],
                requested_behavior="mutation",
                onboarding_state="resume",
                plain_handoff_paths=[handoff],
            )

        self.assertEqual(result["onboarding_status"], "resumed_complete")
        self.assertEqual(result["effective_config"]["safety_status"], "usable")
        self.assertEqual(result["effective_config"]["plain_handoffs"][0]["source"], handoff.as_posix())

    def test_restarted_onboarding_preserves_unselected_sections(self):
        docs_research = agent_equipment_config.SchemaFragment(
            namespace="docs_research",
            version=1,
            fields={"citation_policy": agent_equipment_config.FieldSpec(type="string", required=True)},
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "repo.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [issue_tracker_ops]
                mode = "dry-run"
                external_disclosure = "blocked"

                [docs_research]
                citation_policy = "source-backed"
            """)

            result = agent_equipment_config.config_onboarding_plan(
                [layer],
                [self.issue_ops_fragment(), docs_research],
                requested_behavior="advisory",
                onboarding_state="restart",
                revise_sections=["issue_tracker_ops"],
            )

        self.assertEqual(result["onboarding_status"], "restart_ready")
        self.assertTrue(result["revision_plan"]["preserve_unselected_sections"])
        self.assertEqual(result["revision_plan"]["selected_sections"], ["issue_tracker_ops"])
        self.assertEqual(result["revision_plan"]["unselected_sections"], ["docs_research"])

    def test_restarted_onboarding_rejects_unknown_revision_sections(self):
        with self.assertRaisesRegex(agent_equipment_config.ConfigError, "unknown revise section"):
            agent_equipment_config.config_onboarding_plan(
                [],
                [self.issue_ops_fragment()],
                requested_behavior="advisory",
                onboarding_state="restart",
                revise_sections=["missing_equipment"],
            )

    def test_onboarding_missing_shared_config_labels_defaults_as_schema_defaults(self):
        result = agent_equipment_config.config_onboarding_plan(
            [],
            [agent_equipment_config.issue_tracker_ops_fragment()],
            requested_behavior="mutation",
            shared_config_present=False,
        )

        token_field = result["partial_config"]["sections"]["issue_tracker_ops"]["fields"]["github_token"]
        self.assertEqual(token_field["layer"], "schema default")

    def test_onboarding_schema_valid_ignores_semantic_conflict(self):
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

            result = agent_equipment_config.config_onboarding_plan(
                [layer],
                [agent_equipment_config.issue_tracker_ops_fragment()],
                requested_behavior="mutation",
            )

        self.assertEqual(result["effective_config"]["safety_status"], "unsafe")
        self.assertEqual(result["onboarding_status"], "blocked_config")
        self.assertTrue(result["partial_config"]["schema_valid"])
        self.assertEqual(result["partial_config"]["unsafe_write_modes"], "blocked")

    def test_onboarding_status_maps_non_usable_first_run_safety_statuses(self):
        for safety_status in ["conflicted", "untrusted", "stale", "unsafe"]:
            with self.subTest(safety_status=safety_status):
                self.assertEqual(
                    agent_equipment_config.onboarding_status(True, "first-run", safety_status),
                    "blocked_config",
                )

    def test_onboarding_status_maps_resumed_and_interrupted_blocked_config(self):
        for onboarding_state in ["interrupted", "resume"]:
            for safety_status in ["conflicted", "untrusted", "stale", "unsafe"]:
                with self.subTest(onboarding_state=onboarding_state, safety_status=safety_status):
                    self.assertEqual(
                        agent_equipment_config.onboarding_status(True, onboarding_state, safety_status),
                        "blocked_config",
                    )

    def test_onboarding_status_rejects_unknown_safety_status(self):
        with self.assertRaisesRegex(agent_equipment_config.ConfigError, "unknown Config Safety Status"):
            agent_equipment_config.onboarding_status(True, "first-run", "new-status")

    def test_onboarding_status_rejects_unknown_onboarding_state(self):
        with self.assertRaisesRegex(agent_equipment_config.ConfigError, "unknown onboarding state"):
            agent_equipment_config.onboarding_status(True, "unknown-state", "usable")

    def test_partial_config_treats_omitted_required_fields_as_missing(self):
        result = agent_equipment_config.partial_config_from_effective(
            {},
            [self.issue_ops_fragment()],
            [],
        )

        section = result["sections"]["issue_tracker_ops"]
        self.assertEqual(section["status"], "partial")
        self.assertIn("mode", section["missing_required"])
        self.assertEqual(section["fields"]["mode"]["presence"], "missing")

    def test_onboarding_plan_reuses_loaded_layers(self):
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

            calls = []
            original_load_toml = agent_equipment_config.load_toml

            def counting_load_toml(path):
                calls.append(path)
                return original_load_toml(path)

            try:
                agent_equipment_config.load_toml = counting_load_toml
                result = agent_equipment_config.config_onboarding_plan(
                    [layer],
                    [self.issue_ops_fragment()],
                    requested_behavior="mutation",
                )
            finally:
                agent_equipment_config.load_toml = original_load_toml

        self.assertEqual(result["effective_config"]["safety_status"], "usable")
        self.assertEqual(calls.count(layer), 1)

    def test_onboarding_partial_config_treats_required_secret_reference_as_present(self):
        fragment = agent_equipment_config.SchemaFragment(
            namespace="issue_tracker_ops",
            version=1,
            fields={"github_token": agent_equipment_config.FieldSpec(type="object", required=True)},
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "repo.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [issue_tracker_ops.github_token]
                kind = "env"
                name = "GITHUB_TOKEN"
            """)

            result = agent_equipment_config.config_onboarding_plan(
                [layer],
                [fragment],
                requested_behavior="mutation",
            )

        field = result["partial_config"]["sections"]["issue_tracker_ops"]["fields"]["github_token"]
        self.assertEqual(result["partial_config"]["sections"]["issue_tracker_ops"]["missing_required"], [])
        self.assertEqual(field["presence"], "present")
        self.assertEqual(field["secret_reference"]["kind"], "env")

    def test_cli_emits_redacted_onboarding_plan_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "repo.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [issue_tracker_ops]
                mode = "dry-run"
                external_disclosure = "blocked"

                [issue_tracker_ops.github_token]
                kind = "env"
                name = "GITHUB_TOKEN"
            """)

            payload = json.loads(agent_equipment_config.run(
                [
                    "onboarding-plan",
                    "--layer",
                    str(layer),
                    "--issue-tracker-ops",
                    "--requested-behavior",
                    "mutation",
                ],
                stdout_text=True,
            ))

        self.assertEqual(payload["onboarding_status"], "complete")
        self.assertEqual(payload["effective_config"]["safety_status"], "usable")
        token_field = payload["partial_config"]["sections"]["issue_tracker_ops"]["fields"]["github_token"]
        self.assertEqual(token_field["secret_reference"]["name"], "<redacted>")

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

    def test_unknown_schema_field_type_fails_cleanly(self):
        fragment = agent_equipment_config.SchemaFragment(
            namespace="issue_tracker_ops",
            version=1,
            fields={"mode": agent_equipment_config.FieldSpec(type="mystery")},
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
                mode = "dry-run"
                """,
            )

            with self.assertRaisesRegex(agent_equipment_config.ConfigError, "unsupported field type 'mystery'"):
                agent_equipment_config.effective_config([layer], [fragment], requested_behavior="advisory")

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

    def test_namespace_section_must_be_table(self):
        fragment = agent_equipment_config.SchemaFragment(
            namespace="issue_tracker_ops",
            version=1,
            fields={"mode": agent_equipment_config.FieldSpec(type="string", required=True)},
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "repo.toml", """
                issue_tracker_ops = "oops"

                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"
            """)

            with self.assertRaisesRegex(agent_equipment_config.ConfigError, "issue_tracker_ops must be a table"):
                agent_equipment_config.effective_config([layer], [fragment], requested_behavior="advisory")

    def issue_ops_fragment(self):
        return agent_equipment_config.SchemaFragment(
            namespace="issue_tracker_ops",
            version=1,
            fields={
                "mode": agent_equipment_config.FieldSpec(type="string", required=True, enum=["dry-run", "execute"]),
                "external_disclosure": agent_equipment_config.FieldSpec(type="string", required=True, enum=["blocked", "allowed"]),
            },
        )

    def renamed_mode_fragment(self, *, required: bool = False):
        return agent_equipment_config.SchemaFragment(
            namespace="issue_tracker_ops",
            version=2,
            fields={"mode": agent_equipment_config.FieldSpec(type="string", required=required, enum=["dry-run", "execute"])},
            migrations=(
                agent_equipment_config.MigrationPreview(
                    from_version=1,
                    field_renames={"operation_mode": "mode"},
                    note="rename operation_mode to mode",
                ),
            ),
        )

    def renamed_repo_ops_state_fragment(self):
        return agent_equipment_config.SchemaFragment(
            namespace="repo_ops",
            version=2,
            fields={"state": agent_equipment_config.FieldSpec(type="string", enum=["active", "paused"])},
            migrations=(
                agent_equipment_config.MigrationPreview(
                    from_version=1,
                    field_renames={"run_state": "state"},
                    note="rename run_state to state",
                ),
            ),
        )

    def test_issue_tracker_ops_fragment_v3_accepts_policy_profile_fields(self):
        fragment = agent_equipment_config.issue_tracker_ops_fragment()
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "repo.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [agent_equipment_config.fragment_versions]
                issue_tracker_ops = 3

                [issue_tracker_ops]
                mode = "dry-run"
                external_disclosure = "blocked"
                policy_profile_status = "authoritative"

                [issue_tracker_ops.tracker]
                platform = "github-issues"
                repo = "nisavid/agent-armory"

                [[issue_tracker_ops.label_axes]]
                name = "category"
                cardinality = "exactly_one"
                description = "coarse issue category role"
                labels = ["bug", "enhancement"]
            """)

            result = agent_equipment_config.effective_config([layer], [fragment], requested_behavior="advisory")

        self.assertEqual(fragment.version, 3)
        self.assertEqual(result["safety_status"], "usable")
        self.assertEqual(result["effective"]["issue_tracker_ops"]["policy_profile_status"]["value"], "authoritative")
        self.assertEqual(result["effective"]["issue_tracker_ops"]["tracker"]["value"]["platform"], "github-issues")
        self.assertEqual(result["effective"]["issue_tracker_ops"]["label_axes"]["value"][0]["labels"], ["bug", "enhancement"])

    def test_issue_tracker_ops_fragment_v3_reports_malformed_label_axes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "repo.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [agent_equipment_config.fragment_versions]
                issue_tracker_ops = 3

                [issue_tracker_ops]
                mode = "dry-run"
                external_disclosure = "blocked"

                [[issue_tracker_ops.label_axes]]
                name = "category"
                cardinality = "exactly_one"
                labels = []
            """)

            result = agent_equipment_config.effective_config(
                [layer],
                [agent_equipment_config.issue_tracker_ops_fragment()],
                requested_behavior="advisory",
            )

        self.assertEqual(result["safety_status"], "unsafe")
        self.assertEqual(result["diagnostics"][0]["kind"], "semantic conflict")
        self.assertEqual(result["diagnostics"][0]["path"], "issue_tracker_ops.label_axes")
        self.assertIn("labels must be a non-empty list", result["diagnostics"][0]["detail"])

    def test_issue_tracker_ops_fragment_v3_reports_labels_reused_across_axes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "repo.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [agent_equipment_config.fragment_versions]
                issue_tracker_ops = 3

                [issue_tracker_ops]
                mode = "dry-run"
                external_disclosure = "blocked"

                [[issue_tracker_ops.label_axes]]
                name = "category"
                cardinality = "exactly_one"
                labels = ["bug"]

                [[issue_tracker_ops.label_axes]]
                name = "priority"
                cardinality = "at_most_one"
                labels = ["bug"]
            """)

            result = agent_equipment_config.effective_config(
                [layer],
                [agent_equipment_config.issue_tracker_ops_fragment()],
                requested_behavior="advisory",
            )

        self.assertEqual(result["safety_status"], "unsafe")
        self.assertIn(
            {
                "kind": "semantic conflict",
                "path": "issue_tracker_ops.label_axes",
                "detail": "label 'bug' appears in both category and priority axes",
                "layer": None,
                "source": None,
                "evidence": {},
            },
            result["diagnostics"],
        )

    def test_issue_tracker_ops_fragment_v3_previews_v2_migration(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "repo.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [agent_equipment_config.fragment_versions]
                issue_tracker_ops = 2

                [issue_tracker_ops]
                mode = "dry-run"
                external_disclosure = "blocked"
            """)

            result = agent_equipment_config.effective_config(
                [layer],
                [agent_equipment_config.issue_tracker_ops_fragment()],
                requested_behavior="advisory",
            )

        self.assertEqual(result["safety_status"], "stale")
        self.assertEqual(result["migration_previews"][0]["from_version"], 2)
        self.assertEqual(result["migration_previews"][0]["to_version"], 3)
        self.assertEqual(
            result["migration_previews"][0]["changes"],
            [{"operation": "update fragment version", "path": "agent_equipment_config.fragment_versions.issue_tracker_ops", "from": 2, "to": 3}],
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

    def test_later_layer_cannot_shadow_policy_lock_or_mint_authority(self):
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

                [agent_equipment_config.policy.issue_tracker_ops.mode]
                required_for = "mutation"
                authority = "session_write"

                [agent_equipment_config.authority]
                session_write = "usable"

                [issue_tracker_ops]
                mode = "execute"
            """)

            result = agent_equipment_config.effective_config([policy, session], [self.issue_ops_fragment()], requested_behavior="mutation")

        self.assertEqual(result["effective"]["issue_tracker_ops"]["mode"]["value"], "dry-run")
        self.assertEqual(result["effective"]["issue_tracker_ops"]["mode"]["source"], policy.as_posix())
        self.assertEqual(result["safety_status"], "conflicted")
        self.assertIn("blocked override", [item["kind"] for item in result["diagnostics"]])
        self.assertIn("missing authority", [item["kind"] for item in result["diagnostics"]])
        self.assertEqual(
            [item["evidence"].get("authority") for item in result["diagnostics"] if item["kind"] == "missing authority"],
            ["live_tracker_write"],
        )

    def test_later_same_precedence_layer_cannot_mint_policy_authority(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            policy = self.write_layer(root, "org-a.toml", """
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
            later_policy = self.write_layer(root, "org-b.toml", """
                [agent_equipment_config.layer]
                name = "organization or tracker policy"
                category = "committed durable config"

                [agent_equipment_config.authority]
                live_tracker_write = "usable"
            """)

            result = agent_equipment_config.effective_config([policy, later_policy], [self.issue_ops_fragment()], requested_behavior="mutation")

        self.assertEqual(result["safety_status"], "unsafe")
        self.assertEqual(result["diagnostics"][0]["kind"], "missing authority")
        self.assertEqual(result["diagnostics"][0]["evidence"]["authority"], "live_tracker_write")
        self.assertEqual(result["enforcement_projection"]["classification"], "blocking")

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

    def test_higher_precedence_layer_resolves_lower_same_precedence_collision(self):
        fragment = agent_equipment_config.SchemaFragment(
            namespace="issue_tracker_ops",
            version=1,
            fields={"mode": agent_equipment_config.FieldSpec(type="string", required=True, enum=["dry-run", "execute"])},
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            repo_a = self.write_layer(root, "repo-a.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [issue_tracker_ops]
                mode = "dry-run"
            """)
            repo_b = self.write_layer(root, "repo-b.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [issue_tracker_ops]
                mode = "execute"
            """)
            session = self.write_layer(root, "session.toml", """
                [agent_equipment_config.layer]
                name = "session overrides"
                category = "session override"

                [issue_tracker_ops]
                mode = "execute"
            """)

            result = agent_equipment_config.effective_config([repo_a, repo_b, session], [fragment], requested_behavior="advisory")

        self.assertEqual(result["effective"]["issue_tracker_ops"]["mode"]["value"], "execute")
        self.assertEqual(result["effective"]["issue_tracker_ops"]["mode"]["source"], session.as_posix())
        self.assertEqual(result["safety_status"], "conflicted")
        self.assertIn("same-precedence collision", [item["kind"] for item in result["diagnostics"]])

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

    def test_non_overridable_lock_blocks_later_same_precedence_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            repo_a = self.write_layer(root, "repo-a.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [agent_equipment_config.policy.issue_tracker_ops.mode]
                non_overridable = true
                required_for = "mutation"

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

            result = agent_equipment_config.effective_config([repo_a, repo_b], [self.issue_ops_fragment()], requested_behavior="mutation")

        self.assertEqual(result["effective"]["issue_tracker_ops"]["mode"]["value"], "dry-run")
        self.assertEqual(result["effective"]["issue_tracker_ops"]["mode"]["source"], repo_a.as_posix())
        self.assertIn("blocked override", [item["kind"] for item in result["diagnostics"]])

    def test_policy_authority_lock_blocks_later_override_for_mutation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            org = self.write_layer(root, "org.toml", """
                [agent_equipment_config.layer]
                name = "organization or tracker policy"
                category = "committed durable config"

                [agent_equipment_config.policy.issue_tracker_ops.mode]
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

            result = agent_equipment_config.effective_config([org, session], [self.issue_ops_fragment()], requested_behavior="mutation")

        self.assertEqual(result["effective"]["issue_tracker_ops"]["mode"]["value"], "dry-run")
        self.assertEqual(result["effective"]["issue_tracker_ops"]["mode"]["source"], org.as_posix())
        self.assertIn("blocked override", [item["kind"] for item in result["diagnostics"]])
        self.assertIn("missing authority", [item["kind"] for item in result["diagnostics"]])

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

    def test_trusted_metadata_must_be_boolean(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "checkout.toml", """
                [agent_equipment_config.layer]
                name = "checkout-local state"
                category = "checkout-local state"
                trusted = "false"

                [issue_tracker_ops]
                mode = "execute"
            """)

            with self.assertRaisesRegex(agent_equipment_config.ConfigError, "agent_equipment_config.layer.trusted must be a boolean"):
                agent_equipment_config.load_layers([layer])

    def test_policy_rule_metadata_must_use_declared_types(self):
        fragment = agent_equipment_config.SchemaFragment(
            namespace="issue_tracker_ops",
            version=1,
            fields={"mode": agent_equipment_config.FieldSpec(type="string", required=True, enum=["dry-run", "execute"])},
        )
        cases = (
            ("non_overridable", '"yes"', "must be a boolean"),
            ("authority", "true", "must be a string"),
            ("required_for", "true", "must be a string"),
            ("required_for", '"sometimes"', "must be one of"),
        )
        for key, value, message in cases:
            with self.subTest(key=key):
                with tempfile.TemporaryDirectory() as tmpdir:
                    root = Path(tmpdir)
                    layer = self.write_layer(root, "org.toml", f"""
                        [agent_equipment_config.layer]
                        name = "organization or tracker policy"
                        category = "committed durable config"

                        [agent_equipment_config.policy.issue_tracker_ops.mode]
                        {key} = {value}

                        [issue_tracker_ops]
                        mode = "dry-run"
                    """)

                    with self.assertRaisesRegex(agent_equipment_config.ConfigError, f"policy.issue_tracker_ops.mode.{key} {message}"):
                        agent_equipment_config.effective_config([layer], [fragment], requested_behavior="mutation")

    def test_policy_metadata_tables_must_be_well_formed(self):
        fragment = agent_equipment_config.SchemaFragment(
            namespace="issue_tracker_ops",
            version=1,
            fields={"mode": agent_equipment_config.FieldSpec(type="string", required=True, enum=["dry-run", "execute"])},
        )
        cases = (
            (
                """
                policy = "oops"
                """,
                "agent_equipment_config.policy must be a table",
            ),
            (
                """
                [agent_equipment_config.policy]
                issue_tracker_ops = "oops"
                """,
                "agent_equipment_config.policy.issue_tracker_ops must be a table",
            ),
            (
                """
                [agent_equipment_config.policy.issue_tracker_ops]
                mode = "oops"
                """,
                "agent_equipment_config.policy.issue_tracker_ops.mode must be a table",
            ),
        )
        for policy_metadata, message in cases:
            with self.subTest(message=message):
                with tempfile.TemporaryDirectory() as tmpdir:
                    root = Path(tmpdir)
                    layer = self.write_layer(root, "repo.toml", f"""
                        [agent_equipment_config.layer]
                        name = "repository policy"
                        category = "committed durable config"

                        [agent_equipment_config]
                        {policy_metadata}

                        [issue_tracker_ops]
                        mode = "dry-run"
                    """)

                    with self.assertRaisesRegex(agent_equipment_config.ConfigError, message):
                        agent_equipment_config.effective_config([layer], [fragment], requested_behavior="mutation")

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

    def test_fragment_versions_must_be_integer_metadata(self):
        fragment = agent_equipment_config.SchemaFragment(
            namespace="issue_tracker_ops",
            version=2,
            fields={"mode": agent_equipment_config.FieldSpec(type="string", required=True, enum=["dry-run", "execute"])},
        )
        cases = ('"v1"', "true")
        for value in cases:
            with self.subTest(value=value):
                with tempfile.TemporaryDirectory() as tmpdir:
                    root = Path(tmpdir)
                    layer = self.write_layer(root, "repo.toml", f"""
                        [agent_equipment_config.layer]
                        name = "repository policy"
                        category = "committed durable config"

                        [agent_equipment_config.fragment_versions]
                        issue_tracker_ops = {value}

                        [issue_tracker_ops]
                        mode = "dry-run"
                    """)

                    with self.assertRaisesRegex(agent_equipment_config.ConfigError, "fragment_versions.issue_tracker_ops must be an integer"):
                        agent_equipment_config.effective_config([layer], [fragment], requested_behavior="mutation")

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
            result["migration_previews"][0]["changes"],
            [
                {"from": "issue_tracker_ops.operation_mode", "to": "issue_tracker_ops.mode", "value": "dry-run"},
                {
                    "operation": "update fragment version",
                    "path": "agent_equipment_config.fragment_versions.issue_tracker_ops",
                    "from": 1,
                    "to": 2,
                },
            ],
        )
        self.assertEqual(result["migration_previews"][0]["audit_preview"]["action"], "migration apply preview")
        self.assertFalse(result["migration_previews"][0]["audit_preview"]["would_rewrite_source"])

    def test_migration_apply_dry_run_reports_exact_changes_and_audit_records(self):
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

            result = agent_equipment_config.migration_apply(
                [layer],
                [self.renamed_mode_fragment()],
                apply=False,
            )
            rewritten_text = layer.read_text(encoding="utf-8")

        self.assertEqual(rewritten_text, original_text)
        self.assertFalse(result["applied"])
        self.assertEqual(result["applications"][0]["decision"], "dry-run")
        self.assertFalse(result["applications"][0]["write_authorized"])
        self.assertTrue(result["applications"][0]["dry_run_would_write"])
        self.assertFalse(result["applications"][0]["write_performed"])
        self.assertEqual(
            result["applications"][0]["changes"],
            [
                {
                    "operation": "rename field",
                    "from": "issue_tracker_ops.operation_mode",
                    "to": "issue_tracker_ops.mode",
                    "value": "dry-run",
                },
                {
                    "operation": "update fragment version",
                    "path": "agent_equipment_config.fragment_versions.issue_tracker_ops",
                    "from": 1,
                    "to": 2,
                },
            ],
        )
        self.assertEqual(result["audit_records"][0]["action"], "migration apply decision")
        self.assertEqual(result["audit_records"][0]["decision"], "dry-run")
        self.assertEqual(result["audit_records"][0]["artifact_durability"], "durable project evidence")
        self.assertEqual(result["audit_records"][0]["rollback"], "restore the source file from version control or the recorded diff")

    def test_migration_apply_writes_eligible_source_with_operator_authority(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "repo.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [agent_equipment_config.fragment_versions] # schema versions
                issue_tracker_ops = 1  # v1

                [issue_tracker_ops] # settings
                operation_mode = "dry-run"
            """)

            result = agent_equipment_config.migration_apply(
                [layer],
                [self.renamed_mode_fragment(required=True)],
                apply=True,
                apply_authority="operator",
            )
            rewritten_text = layer.read_text(encoding="utf-8")

        self.assertTrue(result["applied"])
        self.assertEqual(result["applications"][0]["decision"], "applied")
        self.assertFalse(result["applications"][0]["dry_run_would_write"])
        self.assertTrue(result["applications"][0]["write_performed"])
        self.assertIn("issue_tracker_ops = 2  # v1", rewritten_text)
        self.assertIn('mode = "dry-run"', rewritten_text)
        self.assertNotIn("operation_mode", rewritten_text)
        self.assertEqual(result["audit_records"][-1]["action"], "migration apply mutation")
        self.assertEqual(result["audit_records"][-1]["result"], "applied")

    def test_migration_apply_rewrites_exact_toml_key_only(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "repo.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [agent_equipment_config.fragment_versions]
                issue_tracker_ops_extra = 99
                issue_tracker_ops = 1

                [issue_tracker_ops]
                operation_mode_extra = "keep"
                operation_mode = "dry-run"
            """)

            result = agent_equipment_config.migration_apply(
                [layer],
                [self.renamed_mode_fragment()],
                apply=True,
                apply_authority="operator",
            )
            rewritten_text = layer.read_text(encoding="utf-8")

        self.assertTrue(result["applied"])
        self.assertIn("issue_tracker_ops_extra = 99", rewritten_text)
        self.assertIn("issue_tracker_ops = 2", rewritten_text)
        self.assertIn('operation_mode_extra = "keep"', rewritten_text)
        self.assertIn('mode = "dry-run"', rewritten_text)
        self.assertNotIn('operation_mode = "dry-run"', rewritten_text)

    def test_migration_apply_preserves_all_changes_when_multiple_fragments_target_same_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "repo.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [agent_equipment_config.fragment_versions]
                issue_tracker_ops = 1
                repo_ops = 1

                [issue_tracker_ops]
                operation_mode = "dry-run"

                [repo_ops]
                run_state = "active"
            """)

            result = agent_equipment_config.migration_apply(
                [layer],
                [self.renamed_mode_fragment(), self.renamed_repo_ops_state_fragment()],
                apply=True,
                apply_authority="operator",
            )
            rewritten_text = layer.read_text(encoding="utf-8")

        self.assertTrue(result["applied"])
        self.assertEqual([application["namespace"] for application in result["applications"]], ["issue_tracker_ops", "repo_ops"])
        self.assertTrue(all(application["write_performed"] for application in result["applications"]))
        self.assertIn("issue_tracker_ops = 2", rewritten_text)
        self.assertIn("repo_ops = 2", rewritten_text)
        self.assertIn('mode = "dry-run"', rewritten_text)
        self.assertIn('state = "active"', rewritten_text)
        self.assertNotIn("operation_mode", rewritten_text)
        self.assertNotIn("run_state", rewritten_text)

    def test_migration_apply_accepts_trusted_configured_authority(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "repo.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [agent_equipment_config.authority]
                config_migration_apply = "usable"

                [agent_equipment_config.fragment_versions]
                issue_tracker_ops = 1

                [issue_tracker_ops]
                operation_mode = "dry-run"
            """)

            result = agent_equipment_config.migration_apply(
                [layer],
                [self.renamed_mode_fragment()],
                apply=True,
            )

        self.assertTrue(result["applied"])
        self.assertEqual(result["applications"][0]["decision"], "applied")
        self.assertRegex(result["applications"][0]["audit_record"]["authority"], r"^configured:repository policy:")

    def test_migration_apply_rejects_authority_from_later_layer(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            repo = self.write_layer(root, "repo.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [agent_equipment_config.fragment_versions]
                issue_tracker_ops = 1

                [issue_tracker_ops]
                operation_mode = "dry-run"
            """)
            local = self.write_layer(root, "local.toml", """
                [agent_equipment_config.layer]
                name = "user/operator local overrides"
                category = "local-only operator config"

                [agent_equipment_config.authority]
                config_migration_apply = "usable"
            """)

            result = agent_equipment_config.migration_apply(
                [repo, local],
                [self.renamed_mode_fragment()],
                apply=True,
            )

        self.assertFalse(result["applied"])
        self.assertEqual(result["refusals"][0]["reason"], "missing migration apply authority")

    def test_migration_apply_requires_authority_before_writing(self):
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

            result = agent_equipment_config.migration_apply(
                [layer],
                [self.renamed_mode_fragment()],
                apply=True,
            )
            rewritten_text = layer.read_text(encoding="utf-8")

        self.assertFalse(result["applied"])
        self.assertEqual(rewritten_text, original_text)
        self.assertEqual(result["refusals"][0]["reason"], "missing migration apply authority")
        self.assertEqual(result["audit_records"][0]["decision"], "refused")

    def test_migration_apply_records_local_only_source_as_instance_scoped(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "local.toml", """
                [agent_equipment_config.layer]
                name = "user/operator local overrides"
                category = "local-only operator config"

                [agent_equipment_config.fragment_versions]
                issue_tracker_ops = 1

                [issue_tracker_ops]
                operation_mode = "dry-run"
            """)

            result = agent_equipment_config.migration_apply(
                [layer],
                [self.renamed_mode_fragment()],
                apply=False,
            )

        self.assertEqual(result["applications"][0]["source_category"], "local-only operator config")
        self.assertEqual(result["audit_records"][0]["artifact_durability"], "instance-scoped local evidence")
        self.assertFalse(result["audit_records"][0]["project_truth"])

    def test_migration_apply_refuses_generated_or_untrusted_sources(self):
        cases = (
            ("repository policy", "generated cache or state", True, "source category is not eligible for migration apply"),
            ("checkout-local state", "checkout-local state", True, "source category is not eligible for migration apply"),
            ("session overrides", "session override", True, "source category is not eligible for migration apply"),
            ("user/operator local overrides", "secret reference source", True, "source category is not eligible for migration apply"),
            ("repository policy", "committed durable config", False, "source is not trusted for migration apply"),
        )
        for layer_name, category, trusted, reason in cases:
            with self.subTest(category=category, trusted=trusted):
                with tempfile.TemporaryDirectory() as tmpdir:
                    root = Path(tmpdir)
                    trust_line = f"trusted = {str(trusted).lower()}"
                    layer = self.write_layer(root, "repo.toml", f"""
                        [agent_equipment_config.layer]
                        name = "{layer_name}"
                        category = "{category}"
                        {trust_line}

                        [agent_equipment_config.fragment_versions]
                        issue_tracker_ops = 1

                        [issue_tracker_ops]
                        operation_mode = "dry-run"
                    """)

                    result = agent_equipment_config.migration_apply(
                        [layer],
                        [self.renamed_mode_fragment()],
                        apply=True,
                        apply_authority="operator",
                    )

                self.assertFalse(result["applied"])
                self.assertEqual(result["refusals"][0]["reason"], reason)

    def test_migration_apply_projection_uses_only_realizable_migrations(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            repo = self.write_layer(root, "repo.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [agent_equipment_config.fragment_versions]
                issue_tracker_ops = 1

                [issue_tracker_ops]
                operation_mode = "dry-run"
            """)
            generated = self.write_layer(root, "generated.toml", """
                [agent_equipment_config.layer]
                name = "checkout-local state"
                category = "generated cache or state"

                [agent_equipment_config.fragment_versions]
                issue_tracker_ops = 1

                [issue_tracker_ops]
                operation_mode = "execute"
            """)

            result = agent_equipment_config.migration_apply(
                [repo, generated],
                [self.renamed_mode_fragment()],
                apply=False,
            )

        self.assertEqual(result["projected_effective_config"]["effective"]["issue_tracker_ops"]["mode"]["value"], "dry-run")
        self.assertEqual(result["refusals"][0]["source_category"], "generated cache or state")

    def test_migration_apply_fails_if_source_changes_before_write(self):
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
            original_render = agent_equipment_config.render_migration_source_from_text

            def render_after_concurrent_change(text, layer_record, fragment, migration):
                rendered = original_render(text, layer_record, fragment, migration)
                Path(layer_record.path).write_text(f"{text}\n# concurrent edit\n", encoding="utf-8")
                return rendered

            agent_equipment_config.render_migration_source_from_text = render_after_concurrent_change
            try:
                result = agent_equipment_config.migration_apply(
                    [layer],
                    [self.renamed_mode_fragment()],
                    apply=True,
                    apply_authority="operator",
                )
            finally:
                agent_equipment_config.render_migration_source_from_text = original_render

            rewritten_text = layer.read_text(encoding="utf-8")

        self.assertFalse(result["applied"])
        self.assertEqual(result["write_failures"][0]["reason"], "source changed since migration planning")
        self.assertIn("# concurrent edit", rewritten_text)
        self.assertIn("operation_mode", rewritten_text)

    def test_migration_apply_refuses_stale_schema_without_registered_migration(self):
        fragment = agent_equipment_config.SchemaFragment(
            namespace="issue_tracker_ops",
            version=2,
            fields={"mode": agent_equipment_config.FieldSpec(type="string", enum=["dry-run", "execute"])},
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

            result = agent_equipment_config.migration_apply(
                [layer],
                [fragment],
                apply=False,
            )

        self.assertFalse(result["applied"])
        self.assertEqual(result["refusals"][0]["reason"], "no registered migration for stale schema")

    def test_migration_apply_refuses_unsafe_inputs(self):
        def always_unsafe(values, requested_behavior):
            if requested_behavior == "mutation":
                return [agent_equipment_config.Diagnostic("semantic conflict", "issue_tracker_ops.mode", "unsafe")]
            return []

        fragment = agent_equipment_config.SchemaFragment(
            namespace="issue_tracker_ops",
            version=2,
            fields={"mode": agent_equipment_config.FieldSpec(type="string", enum=["dry-run", "execute"])},
            semantic_validators=(always_unsafe,),
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

            result = agent_equipment_config.migration_apply(
                [layer],
                [fragment],
                apply=False,
            )

        self.assertFalse(result["applied"])
        self.assertEqual(result["refusals"][0]["reason"], "effective Config Safety Status is unsafe")

    def test_migration_apply_refuses_incomplete_inputs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "repo.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [agent_equipment_config.fragment_versions]
                issue_tracker_ops = 1

                [issue_tracker_ops]
                unrelated = "dry-run"
            """)

            result = agent_equipment_config.migration_apply(
                [layer],
                [self.renamed_mode_fragment(required=True)],
                apply=False,
            )

        self.assertFalse(result["applied"])
        self.assertEqual(result["refusals"][0]["reason"], "effective Config Safety Status is incomplete")

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
                required_for = "mutation"
            """)

            result = agent_equipment_config.effective_config([layer], [fragment], requested_behavior="mutation")

        token = result["effective"]["issue_tracker_ops"]["github_token"]
        self.assertEqual(token["secret_reference"]["kind"], "env")
        self.assertEqual(token["secret_reference"]["resolution_status"], "unresolved")
        self.assertNotIn("value", token["secret_reference"])

    def test_secret_reference_with_direct_value_payload_is_blocked(self):
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
                value = "raw-token"
            """)

            result = agent_equipment_config.effective_config([layer], [fragment], requested_behavior="mutation")

        token = result["effective"]["issue_tracker_ops"]["github_token"]
        rendered = json.dumps(result, sort_keys=True)
        self.assertEqual(result["safety_status"], "unsafe")
        self.assertEqual(token["secret_reference"]["kind"], "env")
        self.assertNotIn("value", token)
        self.assertNotIn("raw-token", rendered)
        self.assertIn("secret boundary violation", [item["kind"] for item in result["diagnostics"]])

    def test_secret_reference_candidate_with_invalid_name_and_payload_is_blocked(self):
        fragment = agent_equipment_config.SchemaFragment(
            namespace="service_config",
            version=1,
            fields={"auth": agent_equipment_config.FieldSpec(type="object", required=True)},
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "local.toml", """
                [agent_equipment_config.layer]
                name = "user/operator local overrides"
                category = "local-only operator config"

                [service_config.auth]
                kind = "env"
                name = 123
                secret-value = "raw-token"
            """)

            result = agent_equipment_config.effective_config([layer], [fragment], requested_behavior="mutation")

        auth = result["effective"]["service_config"]["auth"]
        rendered = json.dumps(result, sort_keys=True)
        self.assertEqual(result["safety_status"], "unsafe")
        self.assertEqual(auth["value"], agent_equipment_config.REDACTED)
        self.assertEqual(auth["redaction_status"], "blocked_direct_secret_value")
        self.assertNotIn("raw-token", rendered)
        self.assertIn("secret boundary violation", [item["kind"] for item in result["diagnostics"]])

    def test_secret_reference_candidate_with_invalid_kind_shape_is_blocked(self):
        fragment = agent_equipment_config.SchemaFragment(
            namespace="service_config",
            version=1,
            fields={"auth": agent_equipment_config.FieldSpec(type="object", required=True)},
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "local.toml", """
                [agent_equipment_config.layer]
                name = "user/operator local overrides"
                category = "local-only operator config"

                [service_config.auth]
                kind = ["env"]
                token = "raw-token"
            """)

            result = agent_equipment_config.effective_config([layer], [fragment], requested_behavior="mutation")

        auth = result["effective"]["service_config"]["auth"]
        rendered = json.dumps(result, sort_keys=True)
        self.assertEqual(result["safety_status"], "unsafe")
        self.assertEqual(auth["value"], agent_equipment_config.REDACTED)
        self.assertNotIn("raw-token", rendered)
        self.assertIn("secret boundary violation", [item["kind"] for item in result["diagnostics"]])

    def test_valid_secret_reference_with_nested_payload_is_blocked(self):
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

                [issue_tracker_ops.github_token.metadata]
                token = "raw-token"
            """)

            result = agent_equipment_config.effective_config([layer], [fragment], requested_behavior="mutation")

        token = result["effective"]["issue_tracker_ops"]["github_token"]
        rendered = json.dumps(result, sort_keys=True)
        self.assertEqual(result["safety_status"], "unsafe")
        self.assertEqual(token["secret_reference"]["kind"], "env")
        self.assertNotIn("value", token)
        self.assertNotIn("metadata", token["secret_reference"])
        self.assertNotIn("raw-token", rendered)
        self.assertIn("secret boundary violation", [item["kind"] for item in result["diagnostics"]])

    def test_secret_reference_metadata_payload_is_blocked(self):
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
                required_for = "tracker write"

                [issue_tracker_ops.github_token.scope]
                value = "raw-token"
            """)

            result = agent_equipment_config.effective_config([layer], [fragment], requested_behavior="mutation")

        token = result["effective"]["issue_tracker_ops"]["github_token"]
        rendered = json.dumps(result, sort_keys=True)
        self.assertEqual(result["safety_status"], "unsafe")
        self.assertEqual(token["secret_reference"]["kind"], "env")
        self.assertNotIn("scope", token["secret_reference"])
        self.assertNotIn("raw-token", rendered)
        self.assertIn("secret boundary violation", [item["kind"] for item in result["diagnostics"]])

    def test_secret_reference_metadata_array_payload_is_blocked(self):
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
                scope = ["raw-token"]
            """)

            result = agent_equipment_config.effective_config([layer], [fragment], requested_behavior="mutation")

        token = result["effective"]["issue_tracker_ops"]["github_token"]
        rendered = json.dumps(result, sort_keys=True)
        self.assertEqual(result["safety_status"], "unsafe")
        self.assertEqual(token["secret_reference"]["kind"], "env")
        self.assertNotIn("scope", token["secret_reference"])
        self.assertNotIn("raw-token", rendered)
        self.assertIn("secret boundary violation", [item["kind"] for item in result["diagnostics"]])

    def test_blocked_override_diagnostic_redacts_direct_secret_candidate(self):
        fragment = agent_equipment_config.SchemaFragment(
            namespace="issue_tracker_ops",
            version=1,
            fields={"github_token": agent_equipment_config.FieldSpec(type="object", required=True)},
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            policy = self.write_layer(root, "org.toml", """
                [agent_equipment_config.layer]
                name = "organization or tracker policy"
                category = "committed durable config"

                [agent_equipment_config.policy.issue_tracker_ops.github_token]
                non_overridable = true

                [issue_tracker_ops.github_token]
                kind = "env"
                name = "GITHUB_TOKEN"
            """)
            session = self.write_layer(root, "session.toml", """
                [agent_equipment_config.layer]
                name = "session overrides"
                category = "session override"

                [issue_tracker_ops.github_token]
                token = "raw-token"
            """)

            result = agent_equipment_config.effective_config([policy, session], [fragment], requested_behavior="mutation")

        blocked = next(item for item in result["diagnostics"] if item["kind"] == "blocked override")
        rendered = json.dumps(result, sort_keys=True)
        self.assertEqual(blocked["evidence"]["blocked_value"], agent_equipment_config.REDACTED)
        self.assertNotIn("raw-token", rendered)

    def test_blocked_override_diagnostic_redacts_malformed_secret_reference_candidate(self):
        fragment = agent_equipment_config.SchemaFragment(
            namespace="issue_tracker_ops",
            version=1,
            fields={"github_token": agent_equipment_config.FieldSpec(type="object", required=True)},
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            policy = self.write_layer(root, "org.toml", """
                [agent_equipment_config.layer]
                name = "organization or tracker policy"
                category = "committed durable config"

                [agent_equipment_config.policy.issue_tracker_ops.github_token]
                non_overridable = true

                [issue_tracker_ops.github_token]
                kind = "env"
                name = "POLICY_TOKEN"
            """)
            session = self.write_layer(root, "session.toml", """
                [agent_equipment_config.layer]
                name = "session overrides"
                category = "session override"

                [issue_tracker_ops.github_token]
                kind = "env"
                name = "GH_TOKEN"

                [issue_tracker_ops.github_token.scope]
                name = "GH_TOKEN"
            """)

            result = agent_equipment_config.effective_config([policy, session], [fragment], requested_behavior="mutation")

        blocked = next(item for item in result["diagnostics"] if item["kind"] == "blocked override")
        rendered = json.dumps(result, sort_keys=True)
        self.assertEqual(blocked["evidence"]["blocked_value"], agent_equipment_config.REDACTED)
        self.assertIn("secret boundary violation", [item["kind"] for item in result["diagnostics"]])
        self.assertNotIn("GH_TOKEN", rendered)

    def test_direct_sensitive_value_is_blocked_from_effective_config(self):
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
                token = "raw-token"
            """)

            result = agent_equipment_config.effective_config([layer], [fragment], requested_behavior="mutation")

        token = result["effective"]["issue_tracker_ops"]["github_token"]
        rendered = json.dumps(result, sort_keys=True)
        self.assertEqual(result["safety_status"], "unsafe")
        self.assertEqual(token["value"], agent_equipment_config.REDACTED)
        self.assertEqual(token["redaction_status"], "blocked_direct_secret_value")
        self.assertNotIn("raw-token", rendered)
        self.assertIn("secret boundary violation", [item["kind"] for item in result["diagnostics"]])

    def test_nested_direct_secret_key_is_blocked_from_effective_config(self):
        fragment = agent_equipment_config.SchemaFragment(
            namespace="service_config",
            version=1,
            fields={"auth": agent_equipment_config.FieldSpec(type="object", required=True)},
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "local.toml", """
                [agent_equipment_config.layer]
                name = "user/operator local overrides"
                category = "local-only operator config"

                [service_config.auth]
                token = "raw-token"
            """)

            result = agent_equipment_config.effective_config([layer], [fragment], requested_behavior="mutation")

        auth = result["effective"]["service_config"]["auth"]
        rendered = json.dumps(result, sort_keys=True)
        self.assertEqual(result["safety_status"], "unsafe")
        self.assertEqual(auth["value"], agent_equipment_config.REDACTED)
        self.assertEqual(auth["redaction_status"], "blocked_direct_secret_value")
        self.assertNotIn("raw-token", rendered)
        self.assertIn("secret boundary violation", [item["kind"] for item in result["diagnostics"]])

    def test_auth_scalar_secret_is_blocked_from_effective_config(self):
        fragment = agent_equipment_config.SchemaFragment(
            namespace="service_config",
            version=1,
            fields={"auth": agent_equipment_config.FieldSpec(type="string", required=True)},
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "local.toml", """
                [agent_equipment_config.layer]
                name = "user/operator local overrides"
                category = "local-only operator config"

                [service_config]
                auth = "raw-token"
            """)

            result = agent_equipment_config.effective_config([layer], [fragment], requested_behavior="mutation")

        auth = result["effective"]["service_config"]["auth"]
        rendered = json.dumps(result, sort_keys=True)
        self.assertEqual(result["safety_status"], "unsafe")
        self.assertEqual(auth["value"], agent_equipment_config.REDACTED)
        self.assertEqual(auth["redaction_status"], "blocked_direct_secret_value")
        self.assertNotIn("raw-token", rendered)
        self.assertIn("secret boundary violation", [item["kind"] for item in result["diagnostics"]])

    def test_auth_array_secret_is_blocked_from_effective_config(self):
        fragment = agent_equipment_config.SchemaFragment(
            namespace="service_config",
            version=1,
            fields={"auth": agent_equipment_config.FieldSpec(type="array", required=True)},
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "local.toml", """
                [agent_equipment_config.layer]
                name = "user/operator local overrides"
                category = "local-only operator config"

                [service_config]
                auth = ["raw-token"]
            """)

            result = agent_equipment_config.effective_config([layer], [fragment], requested_behavior="mutation")

        auth = result["effective"]["service_config"]["auth"]
        rendered = json.dumps(result, sort_keys=True)
        self.assertEqual(result["safety_status"], "unsafe")
        self.assertEqual(auth["value"], agent_equipment_config.REDACTED)
        self.assertEqual(auth["redaction_status"], "blocked_direct_secret_value")
        self.assertNotIn("raw-token", rendered)
        self.assertIn("secret boundary violation", [item["kind"] for item in result["diagnostics"]])

    def test_direct_secret_redaction_preserves_semantic_validator_input(self):
        seen_tokens = []

        def validator(values, requested_behavior):
            _ = requested_behavior
            seen_tokens.append(values["auth"].get("token"))
            return []

        fragment = agent_equipment_config.SchemaFragment(
            namespace="service_config",
            version=1,
            fields={"auth": agent_equipment_config.FieldSpec(type="object", required=True)},
            semantic_validators=(validator,),
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "local.toml", """
                [agent_equipment_config.layer]
                name = "user/operator local overrides"
                category = "local-only operator config"

                [service_config.auth]
                token = "raw-token"
            """)

            result = agent_equipment_config.effective_config([layer], [fragment], requested_behavior="mutation")

        auth = result["effective"]["service_config"]["auth"]
        rendered = json.dumps(result, sort_keys=True)
        self.assertEqual(seen_tokens, ["raw-token"])
        self.assertEqual(auth["value"], agent_equipment_config.REDACTED)
        self.assertNotIn("raw-token", rendered)

    def test_structural_token_named_object_is_not_blocked_as_direct_secret(self):
        fragment = agent_equipment_config.SchemaFragment(
            namespace="service_config",
            version=1,
            fields={"auth": agent_equipment_config.FieldSpec(type="object", required=True)},
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "local.toml", """
                [agent_equipment_config.layer]
                name = "user/operator local overrides"
                category = "local-only operator config"

                [service_config.auth.refresh_token]
                expires_at = "2026-05-20T00:00:00Z"
            """)

            result = agent_equipment_config.effective_config([layer], [fragment], requested_behavior="advisory")

        auth = result["effective"]["service_config"]["auth"]
        self.assertEqual(result["safety_status"], "usable")
        self.assertEqual(auth["value"]["refresh_token"]["expires_at"], "2026-05-20T00:00:00Z")
        self.assertNotIn("secret boundary violation", [item["kind"] for item in result["diagnostics"]])

    def test_non_secret_token_named_field_is_not_blocked_as_direct_secret(self):
        fragment = agent_equipment_config.SchemaFragment(
            namespace="model_runtime",
            version=1,
            fields={"token_budget": agent_equipment_config.FieldSpec(type="integer", required=True)},
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "local.toml", """
                [agent_equipment_config.layer]
                name = "user/operator local overrides"
                category = "local-only operator config"

                [model_runtime]
                token_budget = 4096
            """)

            result = agent_equipment_config.effective_config([layer], [fragment], requested_behavior="advisory")

        token_budget = result["effective"]["model_runtime"]["token_budget"]
        self.assertEqual(result["safety_status"], "usable")
        self.assertEqual(token_budget["value"], 4096)
        self.assertNotIn("secret boundary violation", [item["kind"] for item in result["diagnostics"]])

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

    def test_config_diff_distinguishes_absent_field_from_explicit_null(self):
        before = {"effective": {"issue_tracker_ops": {}}}
        after = {"effective": {"issue_tracker_ops": {"mode": {"value": None}}}}

        diff = agent_equipment_config.config_diff(before, after)

        self.assertEqual(diff["changes"][0]["path"], "issue_tracker_ops.mode")
        self.assertEqual(diff["changes"][0]["before"], agent_equipment_config.ABSENT)
        self.assertIsNone(diff["changes"][0]["after"])

    def test_config_diff_rejects_wrong_shaped_inputs(self):
        cases = (
            ([], {}, "before: config-diff input must be a JSON object"),
            ({"effective": []}, {}, "before: effective must be a JSON object"),
            ({"effective": {"issue_tracker_ops": []}}, {}, "before: effective.issue_tracker_ops must be a JSON object"),
            ({"effective": {"issue_tracker_ops": {"mode": "dry-run"}}}, {}, "before: effective.issue_tracker_ops.mode must be a JSON object"),
        )
        for before, after, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(agent_equipment_config.ConfigError, message):
                    agent_equipment_config.config_diff(before, after)

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

    def test_cli_effective_config_requires_schema_fragment_flag(self):
        stdout = io.StringIO()
        stderr = io.StringIO()

        exit_code = agent_equipment_config.run(["effective-config"], stdout=stdout, stderr=stderr)

        self.assertEqual(exit_code, 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("error: effective-config requires at least one schema fragment flag", stderr.getvalue())

    def test_cli_config_resolve_outputs_effective_config_json(self):
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

            stdout = agent_equipment_config.run(
                ["config", "resolve", "--layer", str(layer), "--issue-tracker-ops"],
                stdout_text=True,
            )

        payload = json.loads(stdout)
        self.assertEqual(payload["safety_status"], "usable")
        self.assertEqual(payload["effective"]["issue_tracker_ops"]["mode"]["value"], "dry-run")
        self.assertEqual(payload["enforcement_projection"]["classification"], "advisory")

    def test_cli_config_validate_outputs_lower_noise_report_and_exit_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "repo.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [issue_tracker_ops]
                mode = "dry-run"
            """)
            stdout = io.StringIO()
            stderr = io.StringIO()

            exit_code = agent_equipment_config.run(
                [
                    "config",
                    "validate",
                    "--layer",
                    str(layer),
                    "--issue-tracker-ops",
                    "--requested-behavior",
                    "mutation",
                ],
                stdout=stdout,
                stderr=stderr,
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertEqual(stderr.getvalue(), "")
        self.assertFalse(payload["passed"])
        self.assertEqual(payload["safety_status"], "incomplete")
        self.assertEqual(payload["authority_readiness"]["status"], "ready")
        self.assertEqual(payload["fragment_readiness"]["status"], "not_ready")
        self.assertEqual(
            payload["fragment_readiness"]["fragments"][0]["missing_required"],
            ["external_disclosure"],
        )
        self.assertEqual(payload["diagnostics"][0]["kind"], "schema conflict")
        self.assertNotIn("effective_config", payload)

    def test_cli_config_validate_can_include_effective_config_on_request(self):
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

            stdout = agent_equipment_config.run(
                [
                    "config",
                    "validate",
                    "--layer",
                    str(layer),
                    "--issue-tracker-ops",
                    "--include-effective-config",
                ],
                stdout_text=True,
            )

        payload = json.loads(stdout)
        self.assertTrue(payload["passed"])
        self.assertEqual(payload["safety_status"], "usable")
        self.assertEqual(payload["effective_config"]["effective"]["issue_tracker_ops"]["mode"]["value"], "dry-run")

    def test_cli_config_validate_reports_missing_authority_readiness(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "org.toml", """
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
            stdout = io.StringIO()

            exit_code = agent_equipment_config.run(
                [
                    "config",
                    "validate",
                    "--layer",
                    str(layer),
                    "--issue-tracker-ops",
                ],
                stdout=stdout,
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertEqual(payload["safety_status"], "unsafe")
        self.assertEqual(payload["authority_readiness"]["status"], "not_ready")
        self.assertEqual(payload["authority_readiness"]["missing_authorities"], ["live_tracker_write"])
        self.assertEqual(payload["fragment_readiness"]["status"], "not_ready")
        self.assertEqual(payload["fragment_readiness"]["fragments"][0]["diagnostic_kinds"], ["missing authority"])

    def test_cli_config_validate_help_reports_requested_behavior_default(self):
        parser = agent_equipment_config.build_parser()
        stdout = io.StringIO()

        with self.assertRaises(SystemExit) as raised:
            with contextlib.redirect_stdout(stdout):
                parser.parse_args(["config", "validate", "--help"])

        self.assertEqual(raised.exception.code, 0)
        self.assertIn("(default: mutation)", stdout.getvalue())

    def test_fragment_readiness_ignores_diagnostics_without_kind(self):
        readiness = agent_equipment_config.fragment_readiness_from_effective(
            {
                "diagnostics": [
                    {"path": "issue_tracker_ops.mode"},
                    {"path": "issue_tracker_ops.external_disclosure", "kind": 7},
                ],
                "effective": {
                    "issue_tracker_ops": {
                        "mode": {"value": "dry-run", "layer": "repository policy"},
                        "external_disclosure": {"value": "blocked", "layer": "repository policy"},
                    }
                },
            },
            [self.issue_ops_fragment()],
        )

        self.assertEqual(readiness["status"], "ready")
        self.assertEqual(readiness["fragments"][0]["diagnostic_kinds"], [])

    def test_cli_config_validate_marks_blocked_override_fragment_not_ready(self):
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
            stdout = io.StringIO()

            exit_code = agent_equipment_config.run(
                [
                    "config",
                    "validate",
                    "--layer",
                    str(policy),
                    "--layer",
                    str(session),
                    "--issue-tracker-ops",
                    "--requested-behavior",
                    "mutation",
                ],
                stdout=stdout,
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertEqual(payload["safety_status"], "conflicted")
        self.assertEqual(payload["fragment_readiness"]["status"], "not_ready")
        self.assertEqual(payload["fragment_readiness"]["fragments"][0]["diagnostic_kinds"], ["blocked override"])

    def test_cli_config_validate_marks_semantic_conflict_fragment_not_ready(self):
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
            stdout = io.StringIO()

            exit_code = agent_equipment_config.run(
                [
                    "config",
                    "validate",
                    "--layer",
                    str(layer),
                    "--issue-tracker-ops",
                    "--requested-behavior",
                    "mutation",
                ],
                stdout=stdout,
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertEqual(payload["safety_status"], "unsafe")
        self.assertEqual(payload["authority_readiness"]["status"], "ready")
        self.assertEqual(payload["fragment_readiness"]["status"], "not_ready")
        self.assertEqual(payload["fragment_readiness"]["fragments"][0]["diagnostic_kinds"], ["semantic conflict"])

    def test_cli_config_propose_emits_target_agnostic_candidate_changes(self):
        stdout = agent_equipment_config.run(
            [
                "config",
                "propose",
                "--issue-tracker-ops",
                "--set",
                "issue_tracker_ops.mode=execute",
                "--set",
                "issue_tracker_ops.external_disclosure=allowed",
                "--rationale",
                "enable reviewed live tracker mutation",
            ],
            stdout_text=True,
        )

        payload = json.loads(stdout)
        self.assertEqual(payload["operation"], "config propose")
        self.assertEqual(payload["plan_surface"], "proposal")
        self.assertIsNone(payload["source_target"])
        self.assertEqual(payload["affected_namespaces"], ["issue_tracker_ops"])
        self.assertEqual(payload["affected_fields"], ["issue_tracker_ops.external_disclosure", "issue_tracker_ops.mode"])
        self.assertEqual(
            payload["possible_target_categories"],
            ["committed durable config", "local-only operator config"],
        )
        self.assertEqual(payload["candidates"][0]["rationale"], "enable reviewed live tracker mutation")
        self.assertEqual(
            payload["candidates"][0]["changes"],
            [
                {"path": "issue_tracker_ops.external_disclosure", "value": "allowed"},
                {"path": "issue_tracker_ops.mode", "value": "execute"},
            ],
        )

    def test_cli_config_propose_reports_nondeterministic_duplicate_changes(self):
        stdout = io.StringIO()

        exit_code = agent_equipment_config.run(
            [
                "config",
                "propose",
                "--issue-tracker-ops",
                "--set",
                "issue_tracker_ops.mode=dry-run",
                "--set",
                "issue_tracker_ops.mode=execute",
            ],
            stdout=stdout,
        )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertEqual(payload["refusal_codes"], ["non_deterministic_plan"])

    def test_cli_config_propose_refuses_unknown_schema_paths(self):
        stdout = io.StringIO()

        exit_code = agent_equipment_config.run(
            [
                "config",
                "propose",
                "--issue-tracker-ops",
                "--set",
                "issue_tracker_ops.unknown=value",
            ],
            stdout=stdout,
        )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertEqual(payload["refusal_codes"], ["validation_failed"])
        self.assertEqual(payload["path_errors"][0]["detail"], "unknown schema field")
        self.assertEqual(payload["candidates"][0]["path_errors"], payload["path_errors"])

    def test_cli_config_propose_refuses_schema_invalid_values(self):
        stdout = io.StringIO()

        exit_code = agent_equipment_config.run(
            [
                "config",
                "propose",
                "--issue-tracker-ops",
                "--set",
                "issue_tracker_ops.mode=bogus",
            ],
            stdout=stdout,
        )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertEqual(payload["refusal_codes"], ["validation_failed"])
        self.assertEqual(payload["value_errors"][0]["detail"], "expected one of ['dry-run', 'execute']")
        self.assertEqual(payload["candidates"][0]["value_errors"], payload["value_errors"])

    def test_cli_config_propose_reports_known_value_errors_with_unknown_paths(self):
        stdout = io.StringIO()

        exit_code = agent_equipment_config.run(
            [
                "config",
                "propose",
                "--issue-tracker-ops",
                "--set",
                "issue_tracker_ops.unknown=value",
                "--set",
                "issue_tracker_ops.mode=bogus",
            ],
            stdout=stdout,
        )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertEqual(payload["refusal_codes"], ["validation_failed"])
        self.assertEqual(payload["path_errors"][0]["detail"], "unknown schema field")
        self.assertEqual(payload["value_errors"][0]["detail"], "expected one of ['dry-run', 'execute']")
        self.assertEqual(payload["candidates"][0]["path_errors"], payload["path_errors"])
        self.assertEqual(payload["candidates"][0]["value_errors"], payload["value_errors"])

    def test_cli_config_patch_emits_read_only_patch_layer_plan(self):
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
            original_text = layer.read_text(encoding="utf-8")

            stdout = agent_equipment_config.run(
                [
                    "config",
                    "patch",
                    "--layer",
                    str(layer),
                    "--source-target",
                    str(layer),
                    "--issue-tracker-ops",
                    "--set",
                    "issue_tracker_ops.mode=execute",
                    "--set",
                    "issue_tracker_ops.external_disclosure=allowed",
                    "--plan-authority",
                    "operator",
                    "--rationale",
                    "enable reviewed live tracker mutation",
                ],
                stdout_text=True,
            )
            rewritten_text = layer.read_text(encoding="utf-8")

        payload = json.loads(stdout)
        self.assertEqual(rewritten_text, original_text)
        self.assertEqual(payload["schema"], "agent-armory.config.authoring-plan.v1")
        self.assertEqual(payload["operation"], "config patch")
        self.assertEqual(payload["plan_kind"], "patch-layer")
        self.assertEqual(payload["source_target"], str(layer))
        self.assertEqual(payload["source_category"], "committed durable config")
        self.assertTrue(payload["source_identity"]["trusted"])
        self.assertRegex(payload["precondition_fingerprint"], r"^sha256:[0-9a-f]{64}$")
        self.assertEqual(payload["authority_evidence"]["status"], "accepted")
        self.assertEqual(payload["authority_evidence"]["source"], "operator")
        self.assertTrue(payload["validation_result"]["passed"])
        self.assertEqual(payload["virtual_post_change_effective_config"]["safety_status"], "usable")
        self.assertEqual(payload["audit_preview"]["result"], "planned")
        self.assertFalse(payload["audit_preview"]["would_write"])
        self.assertEqual(payload["refusal_codes"], [])
        self.assertEqual(
            payload["change_payload"]["changes"],
            [
                {"path": "issue_tracker_ops.external_disclosure", "before": "blocked", "after": "allowed"},
                {"path": "issue_tracker_ops.mode", "before": "dry-run", "after": "execute"},
            ],
        )

    def test_cli_config_patch_refuses_ineligible_source_missing_authority_and_unsafe_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            generated = self.write_layer(root, "generated.toml", """
                [agent_equipment_config.layer]
                name = "checkout-local state"
                category = "generated cache or state"

                [issue_tracker_ops]
                mode = "dry-run"
                external_disclosure = "blocked"
            """)
            repo = self.write_layer(root, "repo.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [issue_tracker_ops]
                mode = "dry-run"
                external_disclosure = "blocked"
            """)

            ineligible = agent_equipment_config.run(
                [
                    "config",
                    "patch",
                    "--layer",
                    str(generated),
                    "--source-target",
                    str(generated),
                    "--issue-tracker-ops",
                    "--set",
                    "issue_tracker_ops.mode=execute",
                    "--set",
                    "issue_tracker_ops.external_disclosure=allowed",
                    "--plan-authority",
                    "operator",
                ],
                stdout_text=True,
            )
            missing_authority_stdout = io.StringIO()
            missing_authority_exit = agent_equipment_config.run(
                [
                    "config",
                    "patch",
                    "--layer",
                    str(repo),
                    "--source-target",
                    str(repo),
                    "--issue-tracker-ops",
                    "--set",
                    "issue_tracker_ops.mode=execute",
                    "--set",
                    "issue_tracker_ops.external_disclosure=allowed",
                ],
                stdout=missing_authority_stdout,
            )
            unsafe = agent_equipment_config.run(
                [
                    "config",
                    "patch",
                    "--layer",
                    str(repo),
                    "--source-target",
                    str(repo),
                    "--issue-tracker-ops",
                    "--set",
                    "issue_tracker_ops.mode=execute",
                    "--plan-authority",
                    "operator",
                ],
                stdout_text=True,
            )

        self.assertEqual(json.loads(ineligible)["refusal_codes"], ["source_category_ineligible"])
        missing_authority = json.loads(missing_authority_stdout.getvalue())
        self.assertEqual(missing_authority_exit, 1)
        self.assertEqual(missing_authority["refusal_codes"], ["missing_authority"])
        unsafe_codes = json.loads(unsafe)["refusal_codes"]
        self.assertIn("safety_status_blocking", unsafe_codes)

    def test_cli_config_patch_missing_target_reports_all_input_refusals(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            stdout = io.StringIO()

            exit_code = agent_equipment_config.run(
                [
                    "config",
                    "patch",
                    "--source-target",
                    str(root / "missing.toml"),
                    "--issue-tracker-ops",
                    "--set",
                    "issue_tracker_ops.unknown=value",
                ],
                stdout=stdout,
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertEqual(payload["refusal_codes"], ["missing_authority", "validation_failed", "source_changed"])
        self.assertEqual(payload["authority_evidence"]["status"], "missing")
        self.assertEqual(payload["validation_result"]["path_errors"][0]["detail"], "unknown schema field")

    def test_cli_config_patch_missing_target_reports_schema_invalid_values(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            stdout = io.StringIO()

            exit_code = agent_equipment_config.run(
                [
                    "config",
                    "patch",
                    "--source-target",
                    str(root / "missing.toml"),
                    "--issue-tracker-ops",
                    "--set",
                    "issue_tracker_ops.mode=bogus",
                    "--plan-authority",
                    "operator",
                ],
                stdout=stdout,
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertEqual(payload["refusal_codes"], ["validation_failed", "source_changed"])
        self.assertEqual(payload["authority_evidence"]["status"], "accepted")
        self.assertEqual(payload["validation_result"]["value_errors"][0]["detail"], "expected one of ['dry-run', 'execute']")

    def test_cli_config_patch_maps_existing_secret_diagnostics_to_secret_refusal_code(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "repo.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [issue_tracker_ops]
                mode = "dry-run"
                external_disclosure = "blocked"

                [issue_tracker_ops.github_token]
                token = "raw-token"
            """)

            stdout = agent_equipment_config.run(
                [
                    "config",
                    "patch",
                    "--layer",
                    str(layer),
                    "--source-target",
                    str(layer),
                    "--issue-tracker-ops",
                    "--set",
                    "issue_tracker_ops.mode=execute",
                    "--set",
                    "issue_tracker_ops.external_disclosure=allowed",
                    "--plan-authority",
                    "operator",
                ],
                stdout_text=True,
            )

        payload = json.loads(stdout)
        self.assertEqual(payload["refusal_codes"], ["safety_status_blocking", "secret_boundary_violation"])
        self.assertNotIn("raw-token", stdout)

    def test_cli_config_patch_allows_whole_secret_reference_pointer_plan(self):
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

            stdout = agent_equipment_config.run(
                [
                    "config",
                    "patch",
                    "--layer",
                    str(layer),
                    "--source-target",
                    str(layer),
                    "--issue-tracker-ops",
                    "--set",
                    'issue_tracker_ops.github_token={"kind":"env","name":"GH_TOKEN"}',
                    "--plan-authority",
                    "operator",
                ],
                stdout_text=True,
            )

        payload = json.loads(stdout)
        self.assertEqual(payload["refusal_codes"], [])
        token = payload["virtual_post_change_effective_config"]["effective"]["issue_tracker_ops"]["github_token"]
        self.assertEqual(token["secret_reference"]["kind"], "env")
        self.assertEqual(token["secret_reference"]["name"], agent_equipment_config.REDACTED)

    def test_cli_config_patch_refuses_and_redacts_secret_values(self):
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
            stdout = agent_equipment_config.run(
                [
                    "config",
                    "patch",
                    "--layer",
                    str(layer),
                    "--source-target",
                    str(layer),
                    "--issue-tracker-ops",
                    "--set",
                    'issue_tracker_ops.github_token={"kind":"env","name":"GH_TOKEN","value":"raw-token"}',
                    "--plan-authority",
                    "operator",
                ],
                stdout_text=True,
            )
            provider_mutation_stdout = agent_equipment_config.run(
                [
                    "config",
                    "patch",
                    "--layer",
                    str(layer),
                    "--source-target",
                    str(layer),
                    "--issue-tracker-ops",
                    "--set",
                    "issue_tracker_ops.github_token.name=GH_TOKEN",
                    "--plan-authority",
                    "operator",
                ],
                stdout_text=True,
            )

        payload = json.loads(stdout)
        self.assertEqual(payload["refusal_codes"], ["secret_boundary_violation"])
        self.assertNotIn("raw-token", stdout)
        self.assertNotIn("GH_TOKEN", stdout)
        provider_mutation = json.loads(provider_mutation_stdout)
        self.assertEqual(provider_mutation["refusal_codes"], ["secret_boundary_violation"])
        self.assertEqual(provider_mutation["validation_result"]["value_errors"], [])
        self.assertNotIn("GH_TOKEN", provider_mutation_stdout)

    def test_cli_authoring_surfaces_refuse_and_redact_malformed_secret_reference_payloads(self):
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
            malformed_changes = [
                'issue_tracker_ops.github_token={"name":"GH_TOKEN"}',
                'issue_tracker_ops.github_token={"kind":"env","name":"GH_TOKEN","scope":{"name":"GH_TOKEN"}}',
            ]

            results: list[tuple[int, str]] = []
            for index, malformed_change in enumerate(malformed_changes):
                propose_stdout = io.StringIO()
                patch_stdout = io.StringIO()
                create_stdout = io.StringIO()
                propose_exit = agent_equipment_config.run(
                    [
                        "config",
                        "propose",
                        "--issue-tracker-ops",
                        "--set",
                        malformed_change,
                    ],
                    stdout=propose_stdout,
                )
                patch_exit = agent_equipment_config.run(
                    [
                        "config",
                        "patch",
                        "--layer",
                        str(layer),
                        "--source-target",
                        str(layer),
                        "--issue-tracker-ops",
                        "--set",
                        malformed_change,
                        "--plan-authority",
                        "operator",
                    ],
                    stdout=patch_stdout,
                )
                create_exit = agent_equipment_config.run(
                    [
                        "create-layer",
                        "--destination",
                        str(root / f"agent-equipment-{index}.toml"),
                        "--layer-name",
                        "repository policy",
                        "--source-category",
                        "committed durable config",
                        "--issue-tracker-ops",
                        "--set",
                        malformed_change,
                        "--plan-authority",
                        "operator",
                    ],
                    stdout=create_stdout,
                )
                results.extend(
                    [
                        (propose_exit, propose_stdout.getvalue()),
                        (patch_exit, patch_stdout.getvalue()),
                        (create_exit, create_stdout.getvalue()),
                    ]
                )

        for exit_code, stdout in results:
            payload = json.loads(stdout)
            self.assertEqual(exit_code, 1)
            self.assertIn("secret_boundary_violation", payload["refusal_codes"])
            self.assertNotIn("GH_TOKEN", stdout)

    def test_authoring_refusal_artifacts_do_not_expose_secret_values_to_runtime_callers(self):
        changes = agent_equipment_config.parse_authoring_changes(
            ['issue_tracker_ops.github_token={"kind":"env","name":"GH_TOKEN","value":"raw-token"}']
        )
        proposal = agent_equipment_config.config_proposal(changes, [agent_equipment_config.issue_tracker_ops_fragment()])

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            missing_target_plan = agent_equipment_config.config_patch_plan(
                [],
                [agent_equipment_config.issue_tracker_ops_fragment()],
                source_target=root / "missing.toml",
                changes=changes,
                plan_authority="operator",
            )
            create_plan = agent_equipment_config.create_layer_plan(
                [],
                [agent_equipment_config.issue_tracker_ops_fragment()],
                destination=root / "new.toml",
                layer_name="repository policy",
                source_category="committed durable config",
                changes=changes,
                plan_authority="operator",
            )

        for artifact in (proposal, missing_target_plan, create_plan):
            serialized = json.dumps(artifact)
            self.assertNotIn("raw-token", serialized)
            self.assertNotIn("GH_TOKEN", serialized)

    def test_cli_config_patch_refuses_and_redacts_malformed_existing_secret_reference(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "repo.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [issue_tracker_ops]
                mode = "dry-run"
                external_disclosure = "blocked"

                [issue_tracker_ops.github_token]
                name = "GH_TOKEN"
            """)

            stdout = agent_equipment_config.run(
                [
                    "config",
                    "patch",
                    "--layer",
                    str(layer),
                    "--source-target",
                    str(layer),
                    "--issue-tracker-ops",
                    "--set",
                    "issue_tracker_ops.mode=dry-run",
                    "--plan-authority",
                    "operator",
                ],
                stdout_text=True,
            )

        payload = json.loads(stdout)
        self.assertEqual(payload["refusal_codes"], ["safety_status_blocking", "secret_boundary_violation"])
        self.assertFalse(payload["validation_result"]["passed"])
        self.assertIn("secret boundary violation", payload["validation_result"]["planned_source_diagnostic_kinds"])
        self.assertNotIn("GH_TOKEN", stdout)

    def test_cli_config_patch_validates_projected_source_when_effective_value_is_masked(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            repo = self.write_layer(root, "repo.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [issue_tracker_ops]
                mode = "dry-run"
                external_disclosure = "blocked"
            """)
            user = self.write_layer(root, "user.toml", """
                [agent_equipment_config.layer]
                name = "user/operator local overrides"
                category = "local-only operator config"

                [issue_tracker_ops]
                mode = "dry-run"
                external_disclosure = "blocked"
            """)

            stdout = agent_equipment_config.run(
                [
                    "config",
                    "patch",
                    "--layer",
                    str(repo),
                    "--layer",
                    str(user),
                    "--source-target",
                    str(repo),
                    "--issue-tracker-ops",
                    "--set",
                    "issue_tracker_ops.mode=bogus",
                    "--plan-authority",
                    "operator",
                ],
                stdout_text=True,
            )

        payload = json.loads(stdout)
        self.assertEqual(payload["refusal_codes"], ["validation_failed"])
        self.assertFalse(payload["validation_result"]["passed"])
        self.assertEqual(payload["validation_result"]["value_errors"][0]["detail"], "expected one of ['dry-run', 'execute']")
        self.assertEqual(payload["validation_result"]["planned_source_diagnostic_kinds"], ["schema conflict"])
        self.assertEqual(payload["virtual_post_change_effective_config"]["safety_status"], "usable")

    def test_cli_config_patch_validates_missing_required_source_field_when_effective_value_is_masked(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            repo = self.write_layer(root, "repo.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [issue_tracker_ops]
                mode = "dry-run"
            """)
            user = self.write_layer(root, "user.toml", """
                [agent_equipment_config.layer]
                name = "user/operator local overrides"
                category = "local-only operator config"

                [issue_tracker_ops]
                mode = "dry-run"
                external_disclosure = "blocked"
            """)

            stdout = agent_equipment_config.run(
                [
                    "config",
                    "patch",
                    "--layer",
                    str(repo),
                    "--layer",
                    str(user),
                    "--source-target",
                    str(repo),
                    "--issue-tracker-ops",
                    "--set",
                    "issue_tracker_ops.mode=dry-run",
                    "--plan-authority",
                    "operator",
                ],
                stdout_text=True,
            )

        payload = json.loads(stdout)
        self.assertEqual(payload["refusal_codes"], ["validation_failed"])
        self.assertFalse(payload["validation_result"]["passed"])
        self.assertEqual(payload["validation_result"]["planned_source_diagnostic_kinds"], ["schema conflict"])
        self.assertEqual(payload["virtual_post_change_effective_config"]["safety_status"], "usable")

    def test_cli_config_patch_validates_null_required_source_field_when_effective_value_is_masked(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            repo = self.write_layer(root, "repo.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [issue_tracker_ops]
                mode = "dry-run"
                external_disclosure = "blocked"
            """)
            user = self.write_layer(root, "user.toml", """
                [agent_equipment_config.layer]
                name = "user/operator local overrides"
                category = "local-only operator config"

                [issue_tracker_ops]
                mode = "dry-run"
                external_disclosure = "blocked"
            """)

            stdout = agent_equipment_config.run(
                [
                    "config",
                    "patch",
                    "--layer",
                    str(repo),
                    "--layer",
                    str(user),
                    "--source-target",
                    str(repo),
                    "--issue-tracker-ops",
                    "--set",
                    "issue_tracker_ops.mode=null",
                    "--plan-authority",
                    "operator",
                ],
                stdout_text=True,
            )

        payload = json.loads(stdout)
        self.assertEqual(payload["refusal_codes"], ["validation_failed"])
        self.assertFalse(payload["validation_result"]["passed"])
        self.assertEqual(payload["validation_result"]["value_errors"][0]["detail"], "missing required value")
        self.assertEqual(payload["validation_result"]["planned_source_diagnostic_kinds"], ["schema conflict"])
        self.assertEqual(payload["virtual_post_change_effective_config"]["safety_status"], "usable")

    def test_cli_create_layer_emits_read_only_create_layer_plan(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            destination = root / "agent-equipment.toml"

            stdout = agent_equipment_config.run(
                [
                    "create-layer",
                    "--destination",
                    str(destination),
                    "--layer-name",
                    "repository policy",
                    "--source-category",
                    "committed durable config",
                    "--issue-tracker-ops",
                    "--set",
                    "issue_tracker_ops.mode=dry-run",
                    "--set",
                    "issue_tracker_ops.external_disclosure=blocked",
                    "--plan-authority",
                    "operator",
                ],
                stdout_text=True,
            )

            self.assertFalse(destination.exists())

        payload = json.loads(stdout)
        self.assertEqual(payload["operation"], "create-layer")
        self.assertEqual(payload["plan_kind"], "create-layer")
        self.assertEqual(payload["source_target"], str(destination))
        self.assertEqual(payload["source_category"], "committed durable config")
        self.assertEqual(payload["precondition_fingerprint"], "absent")
        self.assertTrue(payload["validation_result"]["passed"])
        self.assertEqual(payload["virtual_post_change_effective_config"]["safety_status"], "usable")
        self.assertEqual(payload["refusal_codes"], [])
        self.assertEqual(
            payload["change_payload"]["create_payload"]["agent_equipment_config"]["fragment_versions"],
            {"issue_tracker_ops": 3},
        )

    def test_cli_create_layer_refuses_existing_destination(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            destination = self.write_layer(root, "agent-equipment.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"
            """)
            stdout = io.StringIO()

            exit_code = agent_equipment_config.run(
                [
                    "create-layer",
                    "--destination",
                    str(destination),
                    "--layer-name",
                    "repository policy",
                    "--source-category",
                    "committed durable config",
                    "--issue-tracker-ops",
                    "--set",
                    "issue_tracker_ops.mode=dry-run",
                    "--plan-authority",
                    "operator",
                ],
                stdout=stdout,
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertEqual(payload["refusal_codes"], ["validation_failed", "source_changed"])

    def test_cli_create_layer_validates_new_source_when_effective_value_is_masked(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            user = self.write_layer(root, "user.toml", """
                [agent_equipment_config.layer]
                name = "user/operator local overrides"
                category = "local-only operator config"

                [issue_tracker_ops]
                mode = "dry-run"
                external_disclosure = "blocked"
            """)
            destination = root / "agent-equipment.toml"

            stdout = agent_equipment_config.run(
                [
                    "create-layer",
                    "--layer",
                    str(user),
                    "--destination",
                    str(destination),
                    "--layer-name",
                    "repository policy",
                    "--source-category",
                    "committed durable config",
                    "--issue-tracker-ops",
                    "--set",
                    "issue_tracker_ops.mode=bogus",
                    "--set",
                    "issue_tracker_ops.external_disclosure=blocked",
                    "--plan-authority",
                    "operator",
                ],
                stdout_text=True,
            )

        payload = json.loads(stdout)
        self.assertEqual(payload["refusal_codes"], ["validation_failed"])
        self.assertFalse(payload["validation_result"]["passed"])
        self.assertEqual(payload["validation_result"]["value_errors"][0]["detail"], "expected one of ['dry-run', 'execute']")
        self.assertEqual(payload["validation_result"]["planned_source_diagnostic_kinds"], ["schema conflict"])
        self.assertEqual(payload["virtual_post_change_effective_config"]["safety_status"], "usable")

    def test_cli_create_layer_validates_missing_required_source_field_when_effective_value_is_masked(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            user = self.write_layer(root, "user.toml", """
                [agent_equipment_config.layer]
                name = "user/operator local overrides"
                category = "local-only operator config"

                [issue_tracker_ops]
                mode = "dry-run"
                external_disclosure = "blocked"
            """)
            destination = root / "agent-equipment.toml"

            stdout = agent_equipment_config.run(
                [
                    "create-layer",
                    "--layer",
                    str(user),
                    "--destination",
                    str(destination),
                    "--layer-name",
                    "repository policy",
                    "--source-category",
                    "committed durable config",
                    "--issue-tracker-ops",
                    "--set",
                    "issue_tracker_ops.mode=dry-run",
                    "--plan-authority",
                    "operator",
                ],
                stdout_text=True,
            )

        payload = json.loads(stdout)
        self.assertEqual(payload["refusal_codes"], ["validation_failed"])
        self.assertFalse(payload["validation_result"]["passed"])
        self.assertEqual(payload["validation_result"]["planned_source_diagnostic_kinds"], ["schema conflict"])
        self.assertEqual(payload["virtual_post_change_effective_config"]["safety_status"], "usable")

    def test_cli_create_layer_validates_null_required_source_field_when_effective_value_is_masked(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            user = self.write_layer(root, "user.toml", """
                [agent_equipment_config.layer]
                name = "user/operator local overrides"
                category = "local-only operator config"

                [issue_tracker_ops]
                mode = "dry-run"
                external_disclosure = "blocked"
            """)
            destination = root / "agent-equipment.toml"

            stdout = agent_equipment_config.run(
                [
                    "create-layer",
                    "--layer",
                    str(user),
                    "--destination",
                    str(destination),
                    "--layer-name",
                    "repository policy",
                    "--source-category",
                    "committed durable config",
                    "--issue-tracker-ops",
                    "--set",
                    "issue_tracker_ops.mode=null",
                    "--set",
                    "issue_tracker_ops.external_disclosure=blocked",
                    "--plan-authority",
                    "operator",
                ],
                stdout_text=True,
            )

        payload = json.loads(stdout)
        self.assertEqual(payload["refusal_codes"], ["validation_failed"])
        self.assertFalse(payload["validation_result"]["passed"])
        self.assertEqual(payload["validation_result"]["planned_source_diagnostic_kinds"], ["schema conflict"])
        self.assertEqual(payload["virtual_post_change_effective_config"]["safety_status"], "usable")

    def test_cli_config_apply_writes_reviewed_patch_layer_plan_from_file(self):
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
            plan = {
                "schema": agent_equipment_config.AUTHORING_PLAN_SCHEMA,
                "operation": "config patch",
                "plan_surface": "reviewed-plan",
                "plan_kind": "patch-layer",
                "source_target": str(layer),
                "source_category": "committed durable config",
                "source_identity": {
                    "name": "repository policy",
                    "category": "committed durable config",
                    "path": str(layer),
                    "trusted": True,
                    "precedence": agent_equipment_config.LAYER_PRECEDENCE.index("repository policy"),
                    "source_order": 0,
                },
                "precondition_fingerprint": agent_equipment_config.source_fingerprint(layer.read_text(encoding="utf-8")),
                "change_payload": {
                    "type": "diff",
                    "changes": [
                        {"path": "issue_tracker_ops.mode", "before": "dry-run", "after": "execute"},
                        {"path": "issue_tracker_ops.external_disclosure", "before": "blocked", "after": "allowed"},
                    ],
                },
                "authority_evidence": {"status": "accepted", "source": "operator", "authority": "operator"},
                "validation_result": {"passed": True},
                "refusal_codes": [],
            }
            plan_path = root / "patch-plan.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            apply_stdout = agent_equipment_config.run(
                [
                    "config",
                    "apply",
                    "--plan",
                    str(plan_path),
                    "--apply-authority",
                    "operator",
                ],
                stdout_text=True,
            )
            applied_text = layer.read_text(encoding="utf-8")

        payload = json.loads(apply_stdout)
        self.assertEqual(payload["operation"], "config apply")
        self.assertEqual(payload["plan_kind"], "patch-layer")
        self.assertTrue(payload["applied"])
        self.assertEqual(payload["result"], "applied")
        self.assertEqual(payload["refusal_codes"], [])
        self.assertIn('mode = "execute"', applied_text)
        self.assertIn('external_disclosure = "allowed"', applied_text)
        self.assertEqual(payload["audit_records"][-1]["action"], "config authoring apply mutation")
        self.assertEqual(payload["audit_records"][-1]["result"], "applied")
        self.assertTrue(payload["audit_records"][-1]["project_truth_after_apply"])

    def test_cli_config_apply_preserves_array_of_tables_source_shape(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "repo.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [issue_tracker_ops]
                mode = "dry-run"
                external_disclosure = "blocked"

                [[tool.samples]]
                name = "first"
                enabled = true
            """)
            plan = {
                "schema": agent_equipment_config.AUTHORING_PLAN_SCHEMA,
                "operation": "config patch",
                "plan_surface": "reviewed-plan",
                "plan_kind": "patch-layer",
                "source_target": str(layer),
                "source_category": "committed durable config",
                "source_identity": {
                    "name": "repository policy",
                    "category": "committed durable config",
                    "path": str(layer),
                    "trusted": True,
                    "precedence": agent_equipment_config.LAYER_PRECEDENCE.index("repository policy"),
                    "source_order": 0,
                },
                "precondition_fingerprint": agent_equipment_config.source_fingerprint(layer.read_text(encoding="utf-8")),
                "change_payload": {
                    "type": "diff",
                    "changes": [
                        {"path": "issue_tracker_ops.mode", "before": "dry-run", "after": "execute"},
                        {"path": "issue_tracker_ops.external_disclosure", "before": "blocked", "after": "allowed"},
                    ],
                },
                "authority_evidence": {"status": "accepted", "source": "operator", "authority": "operator"},
                "validation_result": {"passed": True},
                "refusal_codes": [],
            }

            apply_stdout = agent_equipment_config.run(
                [
                    "config",
                    "apply",
                    "--plan",
                    "-",
                    "--apply-authority",
                    "operator",
                ],
                stdin=io.StringIO(json.dumps(plan)),
                stdout_text=True,
            )
            applied_text = layer.read_text(encoding="utf-8")

        payload = json.loads(apply_stdout)
        reparsed = agent_equipment_config.tomllib.loads(applied_text)
        self.assertTrue(payload["applied"])
        self.assertIn("[[tool.samples]]", applied_text)
        self.assertEqual(reparsed["tool"]["samples"][0]["name"], "first")
        self.assertTrue(reparsed["tool"]["samples"][0]["enabled"])
        self.assertEqual(reparsed["issue_tracker_ops"]["mode"], "execute")

    def test_render_toml_document_quotes_non_ascii_keys(self):
        rendered = agent_equipment_config.render_toml_document({"caf\u00e9": True})

        reparsed = agent_equipment_config.tomllib.loads(rendered)
        self.assertIn('"caf\\u00e9" = true', rendered)
        self.assertTrue(reparsed["caf\u00e9"])

    def test_cli_config_apply_creates_reviewed_layer_plan_from_stdin(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            destination = root / "agent-equipment.toml"
            plan_stdout = agent_equipment_config.run(
                [
                    "create-layer",
                    "--destination",
                    str(destination),
                    "--layer-name",
                    "repository policy",
                    "--source-category",
                    "committed durable config",
                    "--issue-tracker-ops",
                    "--set",
                    "issue_tracker_ops.mode=dry-run",
                    "--set",
                    "issue_tracker_ops.external_disclosure=blocked",
                    "--plan-authority",
                    "operator",
                ],
                stdout_text=True,
            )

            apply_stdout = agent_equipment_config.run(
                [
                    "config",
                    "apply",
                    "--plan",
                    "-",
                    "--apply-authority",
                    "operator",
                ],
                stdin=io.StringIO(plan_stdout),
                stdout_text=True,
            )
            applied_text = destination.read_text(encoding="utf-8")

        payload = json.loads(apply_stdout)
        self.assertTrue(payload["applied"])
        self.assertEqual(payload["plan_kind"], "create-layer")
        self.assertIn("[agent_equipment_config.layer]", applied_text)
        self.assertIn('name = "repository policy"', applied_text)
        self.assertIn("[issue_tracker_ops]", applied_text)
        self.assertEqual(payload["audit_records"][-1]["source_artifact_durability"], "durable project evidence")

    def test_cli_config_apply_refuses_stale_patch_layer_precondition(self):
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
            plan_stdout = agent_equipment_config.run(
                [
                    "config",
                    "patch",
                    "--layer",
                    str(layer),
                    "--source-target",
                    str(layer),
                    "--issue-tracker-ops",
                    "--set",
                    "issue_tracker_ops.mode=execute",
                    "--set",
                    "issue_tracker_ops.external_disclosure=allowed",
                    "--plan-authority",
                    "operator",
                ],
                stdout_text=True,
            )
            layer.write_text(layer.read_text(encoding="utf-8").replace('mode = "dry-run"', 'mode = "execute"'), encoding="utf-8")
            stdout = io.StringIO()

            exit_code = agent_equipment_config.run(
                [
                    "config",
                    "apply",
                    "--plan",
                    "-",
                    "--apply-authority",
                    "operator",
                ],
                stdin=io.StringIO(plan_stdout),
                stdout=stdout,
            )
            current_text = layer.read_text(encoding="utf-8")

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertFalse(payload["applied"])
        self.assertIn("source_changed", payload["refusal_codes"])
        self.assertIn('external_disclosure = "blocked"', current_text)
        self.assertFalse(payload["audit_records"][-1]["write_performed"])

    def test_cli_config_apply_rechecks_operator_authority(self):
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
            plan_stdout = agent_equipment_config.run(
                [
                    "config",
                    "patch",
                    "--layer",
                    str(layer),
                    "--source-target",
                    str(layer),
                    "--issue-tracker-ops",
                    "--set",
                    "issue_tracker_ops.mode=execute",
                    "--set",
                    "issue_tracker_ops.external_disclosure=allowed",
                    "--plan-authority",
                    "operator",
                ],
                stdout_text=True,
            )
            stdout = io.StringIO()

            exit_code = agent_equipment_config.run(
                ["config", "apply", "--plan", "-"],
                stdin=io.StringIO(plan_stdout),
                stdout=stdout,
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertIn("missing_authority", payload["refusal_codes"])
        self.assertEqual(payload["authority_evidence"]["status"], "missing")
        self.assertFalse(payload["applied"])

    def test_cli_config_apply_refuses_validation_and_blocks_partial_write(self):
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
            plan = json.loads(agent_equipment_config.run(
                [
                    "config",
                    "patch",
                    "--layer",
                    str(layer),
                    "--source-target",
                    str(layer),
                    "--issue-tracker-ops",
                    "--set",
                    "issue_tracker_ops.mode=execute",
                    "--set",
                    "issue_tracker_ops.external_disclosure=allowed",
                    "--plan-authority",
                    "operator",
                ],
                stdout_text=True,
            ))
            for change in plan["change_payload"]["changes"]:
                if change["path"] == "issue_tracker_ops.mode":
                    change["after"] = "bogus"
            stdout = io.StringIO()

            exit_code = agent_equipment_config.run(
                [
                    "config",
                    "apply",
                    "--plan",
                    "-",
                    "--apply-authority",
                    "operator",
                ],
                stdin=io.StringIO(json.dumps(plan)),
                stdout=stdout,
            )
            current_text = layer.read_text(encoding="utf-8")

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertIn("validation_failed", payload["refusal_codes"])
        self.assertIn("partial_write_blocked", payload["refusal_codes"])
        self.assertIn('mode = "dry-run"', current_text)
        self.assertIn('external_disclosure = "blocked"', current_text)

    def test_cli_config_apply_refuses_null_authoring_value_before_render(self):
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
            plan = json.loads(agent_equipment_config.run(
                [
                    "config",
                    "patch",
                    "--layer",
                    str(layer),
                    "--source-target",
                    str(layer),
                    "--issue-tracker-ops",
                    "--set",
                    "issue_tracker_ops.mode=execute",
                    "--set",
                    "issue_tracker_ops.external_disclosure=allowed",
                    "--plan-authority",
                    "operator",
                ],
                stdout_text=True,
            ))
            for change in plan["change_payload"]["changes"]:
                if change["path"] == "issue_tracker_ops.external_disclosure":
                    change["after"] = None
            stdout = io.StringIO()

            exit_code = agent_equipment_config.run(
                [
                    "config",
                    "apply",
                    "--plan",
                    "-",
                    "--apply-authority",
                    "operator",
                ],
                stdin=io.StringIO(json.dumps(plan)),
                stdout=stdout,
            )
            current_text = layer.read_text(encoding="utf-8")

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertIn("validation_failed", payload["refusal_codes"])
        self.assertIn("partial_write_blocked", payload["refusal_codes"])
        self.assertFalse(payload["applied"])
        self.assertIn('mode = "dry-run"', current_text)
        self.assertIn('external_disclosure = "blocked"', current_text)

    def test_cli_config_apply_refuses_semantic_safety_regression(self):
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
            plan = json.loads(agent_equipment_config.run(
                [
                    "config",
                    "patch",
                    "--layer",
                    str(layer),
                    "--source-target",
                    str(layer),
                    "--issue-tracker-ops",
                    "--set",
                    "issue_tracker_ops.mode=execute",
                    "--set",
                    "issue_tracker_ops.external_disclosure=allowed",
                    "--plan-authority",
                    "operator",
                ],
                stdout_text=True,
            ))
            for change in plan["change_payload"]["changes"]:
                if change["path"] == "issue_tracker_ops.external_disclosure":
                    change["after"] = "blocked"
            stdout = io.StringIO()

            exit_code = agent_equipment_config.run(
                [
                    "config",
                    "apply",
                    "--plan",
                    "-",
                    "--apply-authority",
                    "operator",
                ],
                stdin=io.StringIO(json.dumps(plan)),
                stdout=stdout,
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertIn("safety_status_blocking", payload["refusal_codes"])
        self.assertIn("validation_failed", payload["refusal_codes"])
        self.assertEqual(payload["virtual_post_change_effective_config"]["safety_status"], "unsafe")

    def test_cli_config_apply_refuses_secret_boundary_violation(self):
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
            plan = json.loads(agent_equipment_config.run(
                [
                    "config",
                    "patch",
                    "--layer",
                    str(layer),
                    "--source-target",
                    str(layer),
                    "--issue-tracker-ops",
                    "--set",
                    "issue_tracker_ops.mode=dry-run",
                    "--plan-authority",
                    "operator",
                ],
                stdout_text=True,
            ))
            plan["change_payload"]["changes"] = [
                {
                    "path": "issue_tracker_ops.github_token",
                    "before": {"presence": "absent"},
                    "after": {"kind": "env", "name": "GH_TOKEN", "value": "raw-token"},
                }
            ]
            stdout = io.StringIO()

            exit_code = agent_equipment_config.run(
                [
                    "config",
                    "apply",
                    "--plan",
                    "-",
                    "--apply-authority",
                    "operator",
                ],
                stdin=io.StringIO(json.dumps(plan)),
                stdout=stdout,
            )

        output = stdout.getvalue()
        payload = json.loads(output)
        self.assertEqual(exit_code, 1)
        self.assertIn("secret_boundary_violation", payload["refusal_codes"])
        self.assertNotIn("raw-token", output)
        self.assertNotIn("GH_TOKEN", output)

    def test_cli_config_apply_refuses_redacted_secret_reference_plan(self):
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
            plan_stdout = agent_equipment_config.run(
                [
                    "config",
                    "patch",
                    "--layer",
                    str(layer),
                    "--source-target",
                    str(layer),
                    "--issue-tracker-ops",
                    "--set",
                    'issue_tracker_ops.github_token={"kind":"env","name":"GH_TOKEN"}',
                    "--plan-authority",
                    "operator",
                ],
                stdout_text=True,
            )
            self.assertIn(agent_equipment_config.REDACTED, plan_stdout)
            stdout = io.StringIO()

            exit_code = agent_equipment_config.run(
                [
                    "config",
                    "apply",
                    "--plan",
                    "-",
                    "--apply-authority",
                    "operator",
                ],
                stdin=io.StringIO(plan_stdout),
                stdout=stdout,
            )
            current_text = layer.read_text(encoding="utf-8")

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertIn("secret_boundary_violation", payload["refusal_codes"])
        self.assertNotIn(agent_equipment_config.REDACTED, current_text)

    def test_cli_config_apply_refuses_tampered_source_category(self):
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
            plan = json.loads(agent_equipment_config.run(
                [
                    "config",
                    "patch",
                    "--layer",
                    str(layer),
                    "--source-target",
                    str(layer),
                    "--issue-tracker-ops",
                    "--set",
                    "issue_tracker_ops.mode=execute",
                    "--set",
                    "issue_tracker_ops.external_disclosure=allowed",
                    "--plan-authority",
                    "operator",
                ],
                stdout_text=True,
            ))
            plan["source_category"] = "local-only operator config"
            stdout = io.StringIO()

            exit_code = agent_equipment_config.run(
                [
                    "config",
                    "apply",
                    "--plan",
                    "-",
                    "--apply-authority",
                    "operator",
                ],
                stdin=io.StringIO(json.dumps(plan)),
                stdout=stdout,
            )
            current_text = layer.read_text(encoding="utf-8")

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertIn("ownership_boundary_violation", payload["refusal_codes"])
        self.assertFalse(payload["applied"])
        self.assertIn('mode = "dry-run"', current_text)

    def test_cli_config_apply_refuses_tampered_source_identity_path(self):
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
            other = self.write_layer(root, "other.toml", layer.read_text(encoding="utf-8"))
            plan = json.loads(agent_equipment_config.run(
                [
                    "config",
                    "patch",
                    "--layer",
                    str(layer),
                    "--source-target",
                    str(layer),
                    "--issue-tracker-ops",
                    "--set",
                    "issue_tracker_ops.mode=execute",
                    "--set",
                    "issue_tracker_ops.external_disclosure=allowed",
                    "--plan-authority",
                    "operator",
                ],
                stdout_text=True,
            ))
            plan["source_target"] = str(other)
            stdout = io.StringIO()

            exit_code = agent_equipment_config.run(
                [
                    "config",
                    "apply",
                    "--plan",
                    "-",
                    "--apply-authority",
                    "operator",
                ],
                stdin=io.StringIO(json.dumps(plan)),
                stdout=stdout,
            )
            other_text = other.read_text(encoding="utf-8")

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertIn("ownership_boundary_violation", payload["refusal_codes"])
        self.assertFalse(payload["applied"])
        self.assertIn('mode = "dry-run"', other_text)

    def test_cli_config_apply_refuses_plan_kind_payload_type_mismatch(self):
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
            plan = json.loads(agent_equipment_config.run(
                [
                    "config",
                    "patch",
                    "--layer",
                    str(layer),
                    "--source-target",
                    str(layer),
                    "--issue-tracker-ops",
                    "--set",
                    "issue_tracker_ops.mode=execute",
                    "--set",
                    "issue_tracker_ops.external_disclosure=allowed",
                    "--plan-authority",
                    "operator",
                ],
                stdout_text=True,
            ))
            plan["change_payload"]["type"] = "create"
            stdout = io.StringIO()

            exit_code = agent_equipment_config.run(
                [
                    "config",
                    "apply",
                    "--plan",
                    "-",
                    "--apply-authority",
                    "operator",
                ],
                stdin=io.StringIO(json.dumps(plan)),
                stdout=stdout,
            )
            current_text = layer.read_text(encoding="utf-8")

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertIn("validation_failed", payload["refusal_codes"])
        self.assertFalse(payload["applied"])
        self.assertIn('mode = "dry-run"', current_text)

    def test_cli_config_apply_refuses_invalid_context_layer_for_create(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            invalid_layer = root / "invalid.toml"
            invalid_layer.write_text("not toml", encoding="utf-8")
            destination = root / "agent-equipment.toml"
            plan_stdout = agent_equipment_config.run(
                [
                    "create-layer",
                    "--destination",
                    str(destination),
                    "--layer-name",
                    "repository policy",
                    "--source-category",
                    "committed durable config",
                    "--issue-tracker-ops",
                    "--set",
                    "issue_tracker_ops.mode=dry-run",
                    "--set",
                    "issue_tracker_ops.external_disclosure=blocked",
                    "--plan-authority",
                    "operator",
                ],
                stdout_text=True,
            )
            stdout = io.StringIO()

            exit_code = agent_equipment_config.run(
                [
                    "config",
                    "apply",
                    "--plan",
                    "-",
                    "--layer",
                    str(invalid_layer),
                    "--apply-authority",
                    "operator",
                ],
                stdin=io.StringIO(plan_stdout),
                stdout=stdout,
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertIn("validation_failed", payload["refusal_codes"])
        self.assertFalse(payload["applied"])
        self.assertFalse(destination.exists())

    def test_cli_config_apply_refuses_ineligible_source_plan(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            generated = self.write_layer(root, "generated.toml", """
                [agent_equipment_config.layer]
                name = "checkout-local state"
                category = "generated cache or state"

                [issue_tracker_ops]
                mode = "dry-run"
                external_disclosure = "blocked"
            """)
            plan_stdout = agent_equipment_config.run(
                [
                    "config",
                    "patch",
                    "--layer",
                    str(generated),
                    "--source-target",
                    str(generated),
                    "--issue-tracker-ops",
                    "--set",
                    "issue_tracker_ops.mode=execute",
                    "--set",
                    "issue_tracker_ops.external_disclosure=allowed",
                    "--plan-authority",
                    "operator",
                ],
                stdout_text=True,
            )
            stdout = io.StringIO()

            exit_code = agent_equipment_config.run(
                [
                    "config",
                    "apply",
                    "--plan",
                    "-",
                    "--apply-authority",
                    "operator",
                ],
                stdin=io.StringIO(plan_stdout),
                stdout=stdout,
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertIn("source_category_ineligible", payload["refusal_codes"])
        self.assertFalse(payload["applied"])

    def test_cli_config_apply_refuses_unsupported_plan_kind(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            plan_path = root / "bad-plan.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "schema": "agent-armory.config.authoring-plan.v1",
                        "plan_surface": "reviewed-plan",
                        "plan_kind": "revise-layer",
                        "source_target": str(root / "repo.toml"),
                        "source_category": "committed durable config",
                        "precondition_fingerprint": "absent",
                        "change_payload": {"type": "revise", "changes": []},
                        "authority_evidence": {"status": "accepted", "source": "operator"},
                        "validation_result": {"passed": True},
                        "refusal_codes": [],
                    }
                ),
                encoding="utf-8",
            )
            stdout = io.StringIO()

            exit_code = agent_equipment_config.run(
                [
                    "config",
                    "apply",
                    "--plan",
                    str(plan_path),
                    "--apply-authority",
                    "operator",
                ],
                stdout=stdout,
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertEqual(payload["refusal_codes"], ["unsupported_plan_kind"])
        self.assertFalse(payload["applied"])

    def test_cli_config_diff_fluent_operation_outputs_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            before = root / "before.json"
            after = root / "after.json"
            before.write_text(json.dumps({"effective": {"issue_tracker_ops": {"mode": {"value": "dry-run"}}}}), encoding="utf-8")
            after.write_text(json.dumps({"effective": {"issue_tracker_ops": {"mode": {"value": "execute"}}}}), encoding="utf-8")

            stdout = agent_equipment_config.run(
                ["config", "diff", "--before", str(before), "--after", str(after)],
                stdout_text=True,
            )

        payload = json.loads(stdout)
        self.assertEqual(payload["changes"][0]["path"], "issue_tracker_ops.mode")
        self.assertEqual(payload["changes"][0]["after"], "execute")

    def test_cli_onboard_config_fluent_operation_outputs_json(self):
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

            stdout = agent_equipment_config.run(
                ["onboard", "config", "--layer", str(layer), "--issue-tracker-ops"],
                stdout_text=True,
            )

        payload = json.loads(stdout)
        self.assertEqual(payload["onboarding_status"], "complete")
        self.assertEqual(payload["effective_config"]["safety_status"], "usable")

    def test_cli_migrate_config_preview_and_apply_map_to_migration_runtime(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            preview_layer = self.write_layer(root, "preview.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [agent_equipment_config.fragment_versions]
                issue_tracker_ops = 1

                [issue_tracker_ops]
                operation_mode = "dry-run"
                external_disclosure = "blocked"
            """)
            apply_layer = self.write_layer(root, "apply.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [agent_equipment_config.fragment_versions]
                issue_tracker_ops = 1

                [issue_tracker_ops]
                operation_mode = "dry-run"
                external_disclosure = "blocked"
            """)

            preview_stdout = agent_equipment_config.run(
                ["migrate", "config", "preview", "--layer", str(preview_layer), "--issue-tracker-ops"],
                stdout_text=True,
            )
            apply_stdout = agent_equipment_config.run(
                [
                    "migrate",
                    "config",
                    "apply",
                    "--layer",
                    str(apply_layer),
                    "--issue-tracker-ops",
                    "--apply-authority",
                    "operator",
                ],
                stdout_text=True,
            )
            applied_text = apply_layer.read_text(encoding="utf-8")

        preview_payload = json.loads(preview_stdout)
        apply_payload = json.loads(apply_stdout)
        self.assertEqual(preview_payload["mode"], "dry-run")
        self.assertFalse(preview_payload["applications"][0]["write_performed"])
        self.assertEqual(apply_payload["mode"], "apply")
        self.assertTrue(apply_payload["applied"])
        self.assertIn('mode = "dry-run"', applied_text)
        self.assertNotIn("operation_mode", applied_text)

    def test_mcp_tool_definitions_cover_config_operation_map_and_effects(self):
        tools = {
            tool["name"]: tool
            for tool in agent_equipment_config.mcp_tool_definitions()
        }

        self.assertEqual(
            sorted(tools),
            [
                "config.apply",
                "config.create_layer",
                "config.diff",
                "config.patch",
                "config.propose",
                "config.resolve",
                "config.validate",
                "migrate.config_apply",
                "migrate.config_preview",
                "onboard.config",
            ],
        )
        for tool in tools.values():
            self.assertEqual(tool["inputSchema"]["type"], "object")
            self.assertEqual(tool["outputSchema"]["type"], "object")
            self.assertIn("description", tool)
            self.assertIn("annotations", tool)
            self.assertIn("x-agent-armory", tool)
            self.assertIn("read_write_classification", tool["x-agent-armory"])
            self.assertIn("failure_modes", tool["x-agent-armory"])

        self.assertTrue(tools["config.resolve"]["annotations"]["readOnlyHint"])
        self.assertEqual(tools["config.resolve"]["x-agent-armory"]["cli_operation"], "config resolve")
        self.assertEqual(tools["config.validate"]["x-agent-armory"]["cli_operation"], "config validate")
        self.assertEqual(tools["migrate.config_preview"]["x-agent-armory"]["side_effects"], [])
        self.assertFalse(tools["migrate.config_apply"]["annotations"]["readOnlyHint"])
        self.assertTrue(tools["migrate.config_apply"]["annotations"]["destructiveHint"])
        self.assertEqual(
            tools["migrate.config_apply"]["x-agent-armory"]["approval_requirements"],
            ["per-call apply_authority"],
        )
        self.assertEqual(
            tools["migrate.config_apply"]["x-agent-armory"]["auth_source"],
            "per-call apply_authority",
        )
        self.assertIn("apply_authority", tools["migrate.config_apply"]["inputSchema"]["required"])
        self.assertTrue(tools["config.propose"]["annotations"]["readOnlyHint"])
        self.assertEqual(tools["config.propose"]["x-agent-armory"]["cli_operation"], "config propose")
        self.assertEqual(tools["config.patch"]["x-agent-armory"]["read_write_classification"], "read-only policy decision")
        self.assertTrue(tools["config.patch"]["annotations"]["readOnlyHint"])
        self.assertEqual(tools["config.create_layer"]["x-agent-armory"]["cli_operation"], "create-layer")
        self.assertTrue(tools["config.create_layer"]["annotations"]["readOnlyHint"])
        self.assertFalse(tools["config.apply"]["annotations"]["readOnlyHint"])
        self.assertTrue(tools["config.apply"]["annotations"]["destructiveHint"])
        self.assertEqual(tools["config.apply"]["x-agent-armory"]["auth_source"], "per-call apply_authority")
        self.assertEqual(
            tools["config.apply"]["x-agent-armory"]["approval_requirements"],
            ["explicit operator or host approval before mutation-capable call"],
        )
        self.assertEqual(tools["config.apply"]["x-agent-armory"]["side_effects"], ["eligible local TOML source rewrite"])
        self.assertEqual(tools["config.apply"]["inputSchema"]["required"], ["plan", "apply_authority"])
        self.assertNotIn("layer_paths", tools["config.apply"]["inputSchema"]["properties"])
        self.assertIn("plan_schema", tools["config.apply"]["outputSchema"]["properties"]["result"]["properties"])

    def test_mcp_config_resolve_returns_structured_read_only_success(self):
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

            result = agent_equipment_config.call_mcp_tool(
                "config.resolve",
                {
                    "layer_paths": [str(layer)],
                    "fragments": ["issue_tracker_ops"],
                    "requested_behavior": "advisory",
                },
            )

        self.assertFalse(result.get("isError", False))
        self.assertEqual(result["content"][0]["type"], "text")
        self.assertEqual(result["structuredContent"]["tool"], "config.resolve")
        self.assertEqual(result["structuredContent"]["operation"], "config.resolve")
        self.assertEqual(result["structuredContent"]["cli_operation"], "config resolve")
        self.assertEqual(result["structuredContent"]["read_write_classification"], "read-only")
        payload = result["structuredContent"]["result"]
        self.assertEqual(payload["safety_status"], "usable")
        self.assertEqual(payload["effective"]["issue_tracker_ops"]["mode"]["value"], "dry-run")

    def test_mcp_config_resolve_redacts_secret_references_in_structured_result(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "repo.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [issue_tracker_ops]
                mode = "dry-run"
                external_disclosure = "blocked"

                [issue_tracker_ops.github_token]
                kind = "env"
                name = "GITHUB_TOKEN_RAW"
            """)

            result = agent_equipment_config.call_mcp_tool(
                "config.resolve",
                {
                    "layer_paths": [str(layer)],
                    "fragments": ["issue_tracker_ops"],
                    "requested_behavior": "advisory",
                },
            )

        self.assertFalse(result.get("isError", False))
        payload = result["structuredContent"]["result"]
        token = payload["effective"]["issue_tracker_ops"]["github_token"]
        self.assertEqual(token["secret_reference"]["name"], agent_equipment_config.REDACTED)
        rendered = json.dumps(payload, sort_keys=True)
        self.assertIn(agent_equipment_config.REDACTED, rendered)
        self.assertNotIn("GITHUB_TOKEN_RAW", rendered)

    def test_mcp_rejects_arguments_outside_published_input_schema(self):
        result = agent_equipment_config.call_mcp_tool(
            "config.resolve",
            {
                "fragments": ["issue_tracker_ops"],
                "implicit_default_path": ".agent-equipment.toml",
            },
        )

        self.assertTrue(result["isError"])
        self.assertIn("unknown argument(s) for config.resolve", result["content"][0]["text"])

    def test_mcp_rejects_values_outside_published_input_schema(self):
        result = agent_equipment_config.call_mcp_tool(
            "config.resolve",
            {
                "fragments": ["issue_tracker_ops"],
                "requested_behavior": "execute",
            },
        )

        self.assertTrue(result["isError"])
        self.assertIn("arguments.requested_behavior must be one of", result["content"][0]["text"])

    def test_mcp_rejects_duplicate_fragments(self):
        result = agent_equipment_config.call_mcp_tool(
            "config.resolve",
            {"fragments": ["issue_tracker_ops", "issue_tracker_ops"]},
        )

        self.assertTrue(result["isError"])
        self.assertIn("arguments.fragments must not contain duplicate item(s)", result["content"][0]["text"])
        self.assertIn("issue_tracker_ops", result["content"][0]["text"])

    def test_mcp_rejects_nested_authoring_inputs_outside_published_schema(self):
        unknown_change_field = agent_equipment_config.call_mcp_tool(
            "config.propose",
            {
                "fragments": ["issue_tracker_ops"],
                "changes": [
                    {
                        "path": "issue_tracker_ops.mode",
                        "value": "execute",
                        "source_target": "repo.toml",
                    }
                ],
            },
        )
        malformed_plan = agent_equipment_config.call_mcp_tool(
            "config.apply",
            {
                "plan": {"schema": "agent-armory.config.authoring-plan.v1"},
                "apply_authority": "operator",
            },
        )
        apply_with_authoring_inputs = agent_equipment_config.call_mcp_tool(
            "config.apply",
            {
                "plan": {
                    "schema": "agent-armory.config.authoring-plan.v1",
                    "operation": "config patch",
                    "plan_surface": "reviewed-plan",
                    "plan_kind": "patch-layer",
                    "source_target": "repo.toml",
                    "source_category": "committed durable config",
                    "source_identity": None,
                    "precondition_fingerprint": "abc123",
                    "change_payload": {},
                    "authority_evidence": {},
                    "validation_result": {},
                    "virtual_post_change_effective_config": {},
                    "audit_preview": {},
                    "refusal_codes": [],
                    "durability_classification": "durable project evidence",
                },
                "apply_authority": "operator",
                "layer_paths": ["repo.toml"],
                "fragments": ["issue_tracker_ops"],
                "changes": [{"path": "issue_tracker_ops.mode", "value": "execute"}],
            },
        )

        self.assertTrue(unknown_change_field["isError"])
        self.assertIn("arguments.changes[0] contains unknown field(s): source_target", unknown_change_field["content"][0]["text"])
        self.assertTrue(malformed_plan["isError"])
        self.assertIn("arguments.plan.operation is required", malformed_plan["content"][0]["text"])
        self.assertTrue(apply_with_authoring_inputs["isError"])
        self.assertIn("unknown argument(s) for config.apply", apply_with_authoring_inputs["content"][0]["text"])
        self.assertIn("changes", apply_with_authoring_inputs["content"][0]["text"])
        self.assertIn("fragments", apply_with_authoring_inputs["content"][0]["text"])
        self.assertIn("layer_paths", apply_with_authoring_inputs["content"][0]["text"])

    def test_mcp_validation_error_preserves_structured_output_contract(self):
        result = agent_equipment_config.call_mcp_tool(
            "config.resolve",
            {
                "fragments": ["issue_tracker_ops"],
                "requested_behavior": "execute",
            },
        )

        self.assertTrue(result["isError"])
        structured = result["structuredContent"]
        self.assertEqual(structured["tool"], "config.resolve")
        self.assertEqual(structured["operation"], "config.resolve")
        self.assertEqual(structured["cli_operation"], "config resolve")
        self.assertEqual(structured["read_write_classification"], "read-only")
        self.assertIn("error", structured["result"])

    def test_mcp_config_validate_returns_low_noise_blocking_report(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "repo.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [issue_tracker_ops]
                mode = "dry-run"
            """)

            result = agent_equipment_config.call_mcp_tool(
                "config.validate",
                {
                    "layer_paths": [str(layer)],
                    "fragments": ["issue_tracker_ops"],
                    "requested_behavior": "mutation",
                },
            )

        self.assertFalse(result.get("isError", False))
        self.assertEqual(result["content"][0]["text"], "config.validate: passed=False safety_status=incomplete")
        payload = result["structuredContent"]["result"]
        self.assertFalse(payload["passed"])
        self.assertEqual(payload["safety_status"], "incomplete")
        self.assertEqual(payload["fragment_readiness"]["status"], "not_ready")
        self.assertEqual(payload["diagnostics"][0]["kind"], "schema conflict")
        self.assertNotIn("effective_config", payload)

    def test_mcp_config_diff_returns_structured_read_only_changes(self):
        before = {
            "effective": {
                "issue_tracker_ops": {
                    "mode": {"value": "dry-run"},
                    "external_disclosure": {"value": "blocked"},
                },
            },
            "safety_status": "usable",
            "diagnostics": [],
        }
        after = {
            "effective": {
                "issue_tracker_ops": {
                    "mode": {"value": "execute"},
                    "external_disclosure": {"value": "allowed"},
                },
            },
            "safety_status": "usable",
            "diagnostics": [],
        }

        result = agent_equipment_config.call_mcp_tool(
            "config.diff",
            {"before": before, "after": after},
        )

        self.assertFalse(result.get("isError", False))
        self.assertEqual(result["structuredContent"]["tool"], "config.diff")
        self.assertEqual(result["structuredContent"]["read_write_classification"], "read-only")
        payload = result["structuredContent"]["result"]
        self.assertEqual(
            [change["path"] for change in payload["changes"]],
            ["issue_tracker_ops.external_disclosure", "issue_tracker_ops.mode"],
        )
        changes_by_path = {change["path"]: change for change in payload["changes"]}
        self.assertEqual(changes_by_path["issue_tracker_ops.external_disclosure"]["before"], "blocked")
        self.assertEqual(changes_by_path["issue_tracker_ops.external_disclosure"]["after"], "allowed")
        self.assertEqual(changes_by_path["issue_tracker_ops.mode"]["before"], "dry-run")
        self.assertEqual(changes_by_path["issue_tracker_ops.mode"]["after"], "execute")

    def test_mcp_config_propose_returns_read_only_authoring_proposal(self):
        result = agent_equipment_config.call_mcp_tool(
            "config.propose",
            {
                "fragments": ["issue_tracker_ops"],
                "changes": [
                    {"path": "issue_tracker_ops.mode", "value": "execute"},
                    {"path": "issue_tracker_ops.external_disclosure", "value": "allowed"},
                ],
                "rationale": "enable reviewed live tracker mutation",
            },
        )

        self.assertFalse(result.get("isError", False))
        self.assertEqual(result["structuredContent"]["tool"], "config.propose")
        self.assertEqual(result["structuredContent"]["cli_operation"], "config propose")
        self.assertEqual(result["structuredContent"]["read_write_classification"], "read-only")
        payload = result["structuredContent"]["result"]
        self.assertEqual(payload["operation"], "config propose")
        self.assertEqual(payload["plan_surface"], "proposal")
        self.assertIsNone(payload["source_target"])
        self.assertEqual(payload["possible_target_categories"], ["committed durable config", "local-only operator config"])
        self.assertEqual(
            sorted(payload["affected_fields"]),
            ["issue_tracker_ops.external_disclosure", "issue_tracker_ops.mode"],
        )
        self.assertEqual(payload["refusal_codes"], [])
        self.assertEqual(result["content"][0]["text"], "config.propose: candidates=1 refusals=0")

    def test_mcp_config_patch_returns_read_only_patch_layer_plan(self):
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
            original_text = layer.read_text(encoding="utf-8")

            result = agent_equipment_config.call_mcp_tool(
                "config.patch",
                {
                    "layer_paths": [str(layer)],
                    "source_target": str(layer),
                    "fragments": ["issue_tracker_ops"],
                    "changes": [
                        {"path": "issue_tracker_ops.mode", "value": "execute"},
                        {"path": "issue_tracker_ops.external_disclosure", "value": "allowed"},
                    ],
                    "plan_authority": "operator",
                    "requested_behavior": "mutation",
                    "rationale": "enable reviewed live tracker mutation",
                },
            )
            rewritten_text = layer.read_text(encoding="utf-8")

        self.assertEqual(rewritten_text, original_text)
        self.assertFalse(result.get("isError", False))
        self.assertEqual(result["structuredContent"]["tool"], "config.patch")
        self.assertEqual(result["structuredContent"]["cli_operation"], "config patch")
        self.assertEqual(result["structuredContent"]["read_write_classification"], "read-only policy decision")
        payload = result["structuredContent"]["result"]
        self.assertEqual(payload["schema"], "agent-armory.config.authoring-plan.v1")
        self.assertEqual(payload["operation"], "config patch")
        self.assertEqual(payload["plan_kind"], "patch-layer")
        self.assertEqual(payload["source_target"], str(layer))
        self.assertTrue(payload["validation_result"]["passed"])
        self.assertEqual(payload["refusal_codes"], [])
        self.assertFalse(payload["audit_preview"]["would_write"])

    def test_mcp_config_create_layer_returns_read_only_create_layer_plan(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            destination = root / "agent-equipment.toml"

            result = agent_equipment_config.call_mcp_tool(
                "config.create_layer",
                {
                    "destination": str(destination),
                    "layer_name": "repository policy",
                    "source_category": "committed durable config",
                    "fragments": ["issue_tracker_ops"],
                    "changes": [
                        {"path": "issue_tracker_ops.mode", "value": "dry-run"},
                        {"path": "issue_tracker_ops.external_disclosure", "value": "blocked"},
                    ],
                    "plan_authority": "operator",
                    "requested_behavior": "mutation",
                    "rationale": "create reviewed tracker policy config",
                },
            )

        self.assertFalse(destination.exists())
        self.assertFalse(result.get("isError", False))
        self.assertEqual(result["structuredContent"]["tool"], "config.create_layer")
        self.assertEqual(result["structuredContent"]["cli_operation"], "create-layer")
        self.assertEqual(result["structuredContent"]["read_write_classification"], "read-only policy decision")
        payload = result["structuredContent"]["result"]
        self.assertEqual(payload["schema"], "agent-armory.config.authoring-plan.v1")
        self.assertEqual(payload["operation"], "create-layer")
        self.assertEqual(payload["plan_kind"], "create-layer")
        self.assertEqual(payload["source_target"], str(destination))
        self.assertEqual(payload["precondition_fingerprint"], "absent")
        self.assertTrue(payload["validation_result"]["passed"])
        self.assertEqual(payload["refusal_codes"], [])
        self.assertFalse(payload["audit_preview"]["would_write"])

    def test_mcp_authoring_plan_generation_reports_refusals_without_writing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            generated = self.write_layer(root, "generated.toml", """
                [agent_equipment_config.layer]
                name = "checkout-local state"
                category = "generated cache or state"

                [issue_tracker_ops]
                mode = "dry-run"
                external_disclosure = "blocked"
            """)
            repo = self.write_layer(root, "repo.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [issue_tracker_ops]
                mode = "dry-run"
                external_disclosure = "blocked"
            """)
            generated_text = generated.read_text(encoding="utf-8")
            repo_text = repo.read_text(encoding="utf-8")

            ineligible = agent_equipment_config.call_mcp_tool(
                "config.patch",
                {
                    "layer_paths": [str(generated)],
                    "source_target": str(generated),
                    "fragments": ["issue_tracker_ops"],
                    "changes": [
                        {"path": "issue_tracker_ops.mode", "value": "execute"},
                        {"path": "issue_tracker_ops.external_disclosure", "value": "allowed"},
                    ],
                    "plan_authority": "operator",
                },
            )
            missing_authority = agent_equipment_config.call_mcp_tool(
                "config.patch",
                {
                    "layer_paths": [str(repo)],
                    "source_target": str(repo),
                    "fragments": ["issue_tracker_ops"],
                    "changes": [
                        {"path": "issue_tracker_ops.mode", "value": "execute"},
                        {"path": "issue_tracker_ops.external_disclosure", "value": "allowed"},
                    ],
                },
            )
            unsafe = agent_equipment_config.call_mcp_tool(
                "config.patch",
                {
                    "layer_paths": [str(repo)],
                    "source_target": str(repo),
                    "fragments": ["issue_tracker_ops"],
                    "changes": [{"path": "issue_tracker_ops.mode", "value": "execute"}],
                    "plan_authority": "operator",
                },
            )
            secret = agent_equipment_config.call_mcp_tool(
                "config.propose",
                {
                    "fragments": ["issue_tracker_ops"],
                    "changes": [
                        {
                            "path": "issue_tracker_ops.github_token",
                            "value": {"kind": "env", "name": "GH_TOKEN", "value": "raw-token"},
                        }
                    ],
                },
            )
            generated_after = generated.read_text(encoding="utf-8")
            repo_after = repo.read_text(encoding="utf-8")

        self.assertEqual(generated_after, generated_text)
        self.assertEqual(repo_after, repo_text)
        self.assertEqual(ineligible["structuredContent"]["result"]["refusal_codes"], ["source_category_ineligible"])
        self.assertEqual(missing_authority["structuredContent"]["result"]["refusal_codes"], ["missing_authority"])
        self.assertIn("safety_status_blocking", unsafe["structuredContent"]["result"]["refusal_codes"])
        secret_payload = secret["structuredContent"]["result"]
        self.assertEqual(secret_payload["refusal_codes"], ["secret_boundary_violation"])
        self.assertNotIn("GH_TOKEN", json.dumps(secret_payload))
        self.assertNotIn("raw-token", json.dumps(secret_payload))

    def test_mcp_config_apply_writes_reviewed_patch_plan_with_explicit_authority(self):
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

            plan_result = agent_equipment_config.call_mcp_tool(
                "config.patch",
                {
                    "layer_paths": [str(layer)],
                    "source_target": str(layer),
                    "fragments": ["issue_tracker_ops"],
                    "changes": [
                        {"path": "issue_tracker_ops.mode", "value": "execute"},
                        {"path": "issue_tracker_ops.external_disclosure", "value": "allowed"},
                    ],
                    "plan_authority": "operator",
                },
            )
            apply_result = agent_equipment_config.call_mcp_tool(
                "config.apply",
                {
                    "plan": plan_result["structuredContent"]["result"],
                    "apply_authority": "operator",
                },
            )
            rewritten_text = layer.read_text(encoding="utf-8")

        self.assertFalse(apply_result.get("isError", False))
        self.assertEqual(apply_result["structuredContent"]["tool"], "config.apply")
        self.assertEqual(apply_result["structuredContent"]["cli_operation"], "config apply")
        self.assertEqual(apply_result["structuredContent"]["read_write_classification"], "local write")
        payload = apply_result["structuredContent"]["result"]
        self.assertEqual(payload["operation"], "config apply")
        self.assertEqual(payload["plan_schema"], "agent-armory.config.authoring-plan.v1")
        self.assertEqual(payload["plan_kind"], "patch-layer")
        self.assertTrue(payload["applied"])
        self.assertEqual(payload["result"], "applied")
        self.assertEqual(payload["refusal_codes"], [])
        self.assertEqual(payload["audit_records"][-1]["action"], "config authoring apply mutation")
        self.assertIn('mode = "execute"', rewritten_text)
        self.assertIn('external_disclosure = "allowed"', rewritten_text)
        self.assertEqual(apply_result["content"][0]["text"], "config.apply: result=applied applied=True refusals=0")

    def test_mcp_config_apply_refuses_invalid_authority_and_stale_precondition(self):
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
            plan_result = agent_equipment_config.call_mcp_tool(
                "config.patch",
                {
                    "layer_paths": [str(layer)],
                    "source_target": str(layer),
                    "fragments": ["issue_tracker_ops"],
                    "changes": [
                        {"path": "issue_tracker_ops.mode", "value": "execute"},
                        {"path": "issue_tracker_ops.external_disclosure", "value": "allowed"},
                    ],
                    "plan_authority": "operator",
                },
            )
            invalid_authority = agent_equipment_config.call_mcp_tool(
                "config.apply",
                {
                    "plan": plan_result["structuredContent"]["result"],
                    "apply_authority": "configured",
                },
            )
            layer.write_text(
                textwrap.dedent(
                    """
                    [agent_equipment_config.layer]
                    name = "repository policy"
                    category = "committed durable config"

                    [issue_tracker_ops]
                    mode = "dry-run"
                    external_disclosure = "allowed"
                    """
                ).lstrip(),
                encoding="utf-8",
            )
            stale = agent_equipment_config.call_mcp_tool(
                "config.apply",
                {
                    "plan": plan_result["structuredContent"]["result"],
                    "apply_authority": "operator",
                },
            )
            rewritten_text = layer.read_text(encoding="utf-8")

        self.assertTrue(invalid_authority["isError"])
        self.assertIn("arguments.apply_authority must be one of", invalid_authority["content"][0]["text"])
        stale_payload = stale["structuredContent"]["result"]
        self.assertFalse(stale_payload["applied"])
        self.assertIn("source_changed", stale_payload["refusal_codes"])
        self.assertNotIn('mode = "execute"', rewritten_text)

    def test_mcp_config_apply_writes_reviewed_create_layer_plan_with_explicit_authority(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            destination = root / "agent-equipment.toml"

            plan_result = agent_equipment_config.call_mcp_tool(
                "config.create_layer",
                {
                    "destination": str(destination),
                    "layer_name": "repository policy",
                    "source_category": "committed durable config",
                    "fragments": ["issue_tracker_ops"],
                    "changes": [
                        {"path": "issue_tracker_ops.mode", "value": "dry-run"},
                        {"path": "issue_tracker_ops.external_disclosure", "value": "blocked"},
                    ],
                    "plan_authority": "operator",
                },
            )
            apply_result = agent_equipment_config.call_mcp_tool(
                "config.apply",
                {
                    "plan": plan_result["structuredContent"]["result"],
                    "apply_authority": "operator",
                },
            )
            created_text = destination.read_text(encoding="utf-8")

        self.assertFalse(apply_result.get("isError", False))
        payload = apply_result["structuredContent"]["result"]
        self.assertEqual(payload["plan_schema"], "agent-armory.config.authoring-plan.v1")
        self.assertEqual(payload["plan_kind"], "create-layer")
        self.assertTrue(payload["applied"])
        self.assertEqual(payload["result"], "applied")
        self.assertEqual(payload["refusal_codes"], [])
        self.assertIn('name = "repository policy"', created_text)
        self.assertIn('category = "committed durable config"', created_text)
        self.assertIn('mode = "dry-run"', created_text)
        self.assertIn('external_disclosure = "blocked"', created_text)

    def test_mcp_onboard_config_returns_missing_shared_config_plan(self):
        result = agent_equipment_config.call_mcp_tool(
            "onboard.config",
            {
                "fragments": ["issue_tracker_ops"],
                "shared_config_present": False,
            },
        )

        self.assertFalse(result.get("isError", False))
        self.assertEqual(result["structuredContent"]["tool"], "onboard.config")
        payload = result["structuredContent"]["result"]
        self.assertEqual(payload["onboarding_status"], "missing_shared_config")
        self.assertEqual(payload["handoff_behavior"]["plain_handoff"], "required")

    def test_mcp_migrate_config_preview_does_not_write_source(self):
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
                external_disclosure = "blocked"
            """)
            original_text = layer.read_text(encoding="utf-8")

            result = agent_equipment_config.call_mcp_tool(
                "migrate.config_preview",
                {
                    "layer_paths": [str(layer)],
                    "fragments": ["issue_tracker_ops"],
                },
            )
            rewritten_text = layer.read_text(encoding="utf-8")

        self.assertEqual(rewritten_text, original_text)
        payload = result["structuredContent"]["result"]
        self.assertEqual(payload["mode"], "dry-run")
        self.assertFalse(payload["applied"])
        self.assertEqual(payload["applications"][0]["decision"], "dry-run")

    def test_mcp_migrate_config_apply_requires_per_call_authority(self):
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
                external_disclosure = "blocked"
            """)
            original_text = layer.read_text(encoding="utf-8")

            result = agent_equipment_config.call_mcp_tool(
                "migrate.config_apply",
                {
                    "layer_paths": [str(layer)],
                    "fragments": ["issue_tracker_ops"],
                },
            )
            rewritten_text = layer.read_text(encoding="utf-8")

        self.assertEqual(rewritten_text, original_text)
        self.assertTrue(result["isError"])
        self.assertIn("apply_authority is required for migrate.config_apply", result["content"][0]["text"])

    def test_mcp_migrate_config_apply_requires_per_call_authority_even_with_configured_authority(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "repo.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [agent_equipment_config.authority]
                config_migration_apply = "usable"

                [agent_equipment_config.fragment_versions]
                issue_tracker_ops = 1

                [issue_tracker_ops]
                operation_mode = "dry-run"
                external_disclosure = "blocked"
            """)
            original_text = layer.read_text(encoding="utf-8")

            result = agent_equipment_config.call_mcp_tool(
                "migrate.config_apply",
                {
                    "layer_paths": [str(layer)],
                    "fragments": ["issue_tracker_ops"],
                },
            )
            rewritten_text = layer.read_text(encoding="utf-8")

        self.assertEqual(rewritten_text, original_text)
        self.assertTrue(result["isError"])
        self.assertIn("apply_authority is required for migrate.config_apply", result["content"][0]["text"])

    def test_mcp_migrate_config_apply_preserves_runtime_refusal_with_explicit_authority(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "cache.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "generated cache or state"

                [agent_equipment_config.fragment_versions]
                issue_tracker_ops = 1

                [issue_tracker_ops]
                operation_mode = "dry-run"
                external_disclosure = "blocked"
            """)
            original_text = layer.read_text(encoding="utf-8")

            result = agent_equipment_config.call_mcp_tool(
                "migrate.config_apply",
                {
                    "layer_paths": [str(layer)],
                    "fragments": ["issue_tracker_ops"],
                    "apply_authority": "operator",
                },
            )
            rewritten_text = layer.read_text(encoding="utf-8")

        self.assertEqual(rewritten_text, original_text)
        payload = result["structuredContent"]["result"]
        self.assertFalse(payload["applied"])
        self.assertEqual(payload["refusals"][0]["reason"], "source category is not eligible for migration apply")
        self.assertEqual(payload["audit_records"][0]["decision"], "refused")

    def test_mcp_migrate_config_apply_writes_with_explicit_authority(self):
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
                external_disclosure = "blocked"
            """)

            result = agent_equipment_config.call_mcp_tool(
                "migrate.config_apply",
                {
                    "layer_paths": [str(layer)],
                    "fragments": ["issue_tracker_ops"],
                    "apply_authority": "operator",
                },
            )
            rewritten_text = layer.read_text(encoding="utf-8")

        payload = result["structuredContent"]["result"]
        self.assertTrue(payload["applied"])
        self.assertEqual(payload["applications"][0]["decision"], "applied")
        self.assertEqual(payload["audit_records"][-1]["action"], "migration apply mutation")
        self.assertIn('mode = "dry-run"', rewritten_text)
        self.assertNotIn("operation_mode", rewritten_text)

    def test_cli_migration_apply_outputs_dry_run_json(self):
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
            stdout = agent_equipment_config.run(
                ["migration-apply", "--layer", str(layer), "--issue-tracker-ops"],
                stdout_text=True,
            )

        payload = json.loads(stdout)
        self.assertEqual(payload["mode"], "dry-run")
        self.assertFalse(payload["applied"])
        self.assertEqual(payload["applications"], [])
        self.assertEqual(payload["refusals"], [])

    def test_cli_migration_apply_rejects_unknown_apply_authority(self):
        stderr = io.StringIO()

        with self.assertRaises(SystemExit) as raised:
            with contextlib.redirect_stderr(stderr):
                agent_equipment_config.run(
                    ["migration-apply", "--issue-tracker-ops", "--apply-authority", "typo"],
                )

        self.assertEqual(raised.exception.code, 2)
        self.assertIn("invalid choice: 'typo'", stderr.getvalue())

    def test_cli_effective_config_redacts_secret_reference_names(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_layer(root, "local.toml", """
                [agent_equipment_config.layer]
                name = "user/operator local overrides"
                category = "local-only operator config"

                [issue_tracker_ops]
                mode = "dry-run"
                external_disclosure = "blocked"

                [issue_tracker_ops.github_token]
                kind = "env"
                name = "GITHUB_TOKEN"
                scope = "session"
                required_for = "mutation"
            """)
            stdout = agent_equipment_config.run(["effective-config", "--layer", str(layer), "--issue-tracker-ops"], stdout_text=True)

        payload = json.loads(stdout)
        token = payload["effective"]["issue_tracker_ops"]["github_token"]
        self.assertEqual(token["secret_reference"]["kind"], "env")
        self.assertEqual(token["secret_reference"]["name"], agent_equipment_config.REDACTED)
        self.assertNotIn("GITHUB_TOKEN", stdout)

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

    def test_cli_config_diff_reports_input_errors_without_traceback(self):
        cases = ("{", "[]", '{"effective": []}')
        for before_text in cases:
            with self.subTest(before_text=before_text):
                with tempfile.TemporaryDirectory() as tmpdir:
                    root = Path(tmpdir)
                    before = root / "before.json"
                    after = root / "after.json"
                    before.write_text(before_text, encoding="utf-8")
                    after.write_text("{}", encoding="utf-8")
                    stdout = io.StringIO()
                    stderr = io.StringIO()

                    exit_code = agent_equipment_config.run(
                        ["config-diff", "--before", str(before), "--after", str(after)],
                        stdout=stdout,
                        stderr=stderr,
                    )

                self.assertEqual(exit_code, 2)
                self.assertEqual(stdout.getvalue(), "")
                self.assertIn("error:", stderr.getvalue())
                self.assertNotIn("Traceback", stderr.getvalue())

    def test_cli_config_diff_redacts_secret_reference_names(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            before = root / "before.json"
            after = root / "after.json"
            before.write_text(
                json.dumps(
                    {
                        "effective": {
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
                    }
                ),
                encoding="utf-8",
            )
            after.write_text(
                json.dumps(
                    {
                        "effective": {
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
                    }
                ),
                encoding="utf-8",
            )

            stdout = agent_equipment_config.run(
                ["config-diff", "--before", str(before), "--after", str(after)],
                stdout_text=True,
            )

        payload = json.loads(stdout)
        self.assertEqual(payload["changes"][0]["path"], "issue_tracker_ops.github_token")
        self.assertEqual(payload["changes"][0]["before"]["secret_reference"]["name"], agent_equipment_config.REDACTED)
        self.assertEqual(payload["changes"][0]["after"]["secret_reference"]["name"], agent_equipment_config.REDACTED)
        self.assertNotIn("OLD_GITHUB_TOKEN", stdout)
        self.assertNotIn("NEW_GITHUB_TOKEN", stdout)

    def test_cli_config_diff_redacts_sensitive_scalar_values(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            before = root / "before.json"
            after = root / "after.json"
            before.write_text(
                json.dumps({"effective": {"issue_tracker_ops": {"api_key": {"value": "old-secret"}}}}),
                encoding="utf-8",
            )
            after.write_text(
                json.dumps({"effective": {"issue_tracker_ops": {"api_key": {"value": "new-secret"}}}}),
                encoding="utf-8",
            )

            stdout = agent_equipment_config.run(
                ["config-diff", "--before", str(before), "--after", str(after)],
                stdout_text=True,
            )

        payload = json.loads(stdout)
        self.assertEqual(payload["changes"][0]["path"], "issue_tracker_ops.api_key")
        self.assertEqual(payload["changes"][0]["before"], agent_equipment_config.REDACTED)
        self.assertEqual(payload["changes"][0]["after"], agent_equipment_config.REDACTED)
        self.assertNotIn("old-secret", stdout)
        self.assertNotIn("new-secret", stdout)

    def test_cli_redacts_sensitive_diagnostic_and_migration_values(self):
        payload = {
            "diagnostics": [
                {
                    "kind": "blocked override",
                    "path": "issue_tracker_ops.api_key",
                    "evidence": {"blocked_value": "raw-api-key"},
                }
            ],
            "migration_previews": [
                {
                    "changes": [
                        {
                            "from": "issue_tracker_ops.api_key",
                            "to": "issue_tracker_ops.api_key",
                            "value": "migrated-api-key",
                        }
                    ]
                }
            ],
            "effective": {
                "issue_tracker_ops": {
                    "api_keys": {
                        "value": ["list-api-key"],
                    }
                }
            },
        }

        redacted = agent_equipment_config.redact_for_cli(payload)
        rendered = json.dumps(redacted)

        self.assertEqual(redacted["diagnostics"][0]["evidence"]["blocked_value"], agent_equipment_config.REDACTED)
        self.assertEqual(redacted["migration_previews"][0]["changes"][0]["value"], agent_equipment_config.REDACTED)
        self.assertEqual(redacted["effective"]["issue_tracker_ops"]["api_keys"]["value"][0], agent_equipment_config.REDACTED)
        self.assertNotIn("raw-api-key", rendered)
        self.assertNotIn("migrated-api-key", rendered)
        self.assertNotIn("list-api-key", rendered)

    def test_cli_redacts_blocked_secret_reference_names(self):
        payload = {
            "diagnostics": [
                {
                    "kind": "blocked override",
                    "path": "issue_tracker_ops.github_token",
                    "evidence": {
                        "blocked_value": {
                            "kind": "env",
                            "name": "GITHUB_TOKEN",
                            "resolution_status": "unresolved",
                        }
                    },
                }
            ]
        }

        redacted = agent_equipment_config.redact_for_cli(payload)
        rendered = json.dumps(redacted)

        self.assertEqual(redacted["diagnostics"][0]["evidence"]["blocked_value"]["name"], agent_equipment_config.REDACTED)
        self.assertNotIn("GITHUB_TOKEN", rendered)

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

    def test_consumer_integration_surface_loads_config_and_returns_decision_evidence(self):
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

            result = agent_equipment_config.evaluate_consumer_config(
                [policy],
                [self.issue_ops_fragment()],
                equipment="issue_tracker_ops",
                requested_behavior="mutation",
                required_capabilities=["tracker_write"],
                supported_capabilities=["tracker_read", "tracker_write"],
            )

        decision = result["consumer_action_decision"]
        self.assertEqual(result["effective_config"]["safety_status"], "usable")
        self.assertEqual(decision["state"], "allowed")
        self.assertEqual(decision["equipment"], "issue_tracker_ops")
        self.assertEqual(decision["requested_behavior"], "mutation")
        self.assertEqual(decision["evidence"]["required_capabilities"], ["tracker_write"])
        self.assertEqual(decision["evidence"]["unsupported_capabilities"], [])

    def test_consumer_action_decision_allows_usable_mutation_behavior(self):
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

        decision = self.issue_tracker_ops_consumer_decision(
            result,
            requested_behavior="mutation",
        )

        self.assertEqual(decision["state"], "allowed")
        self.assertEqual(decision["fallback"], "none")

    def test_consumer_action_decision_warns_for_non_blocking_diagnostics(self):
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
            layer = self.write_layer(root, "repo.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [issue_tracker_ops]
                old_mode = "dry-run"
            """)

            result = agent_equipment_config.effective_config([layer], [fragment], requested_behavior="advisory")

        decision = self.issue_tracker_ops_consumer_decision(
            result,
            requested_behavior="advisory",
        )

        self.assertEqual(result["safety_status"], "usable")
        self.assertEqual(decision["state"], "warning")
        self.assertEqual(decision["reason"], "deprecated field")

    def test_consumer_action_decision_returns_advisory_for_clean_read_only_behavior(self):
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

            result = agent_equipment_config.effective_config([layer], [self.issue_ops_fragment()], requested_behavior="advisory")

        decision = self.issue_tracker_ops_consumer_decision(
            result,
            requested_behavior="advisory",
        )

        self.assertEqual(result["safety_status"], "usable")
        self.assertEqual(decision["state"], "advisory")
        self.assertEqual(decision["fallback"], "none")

    def test_consumer_action_decision_blocks_mutation_behavior(self):
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

        decision = self.issue_tracker_ops_consumer_decision(
            result,
            requested_behavior="mutation",
        )

        self.assertEqual(decision["state"], "blocking")
        self.assertIn("missing authority", decision["reason"])
        self.assertEqual(decision["fallback"], "advisory dry-run")

    def test_consumer_action_decision_blocks_mutation_when_projection_is_missing(self):
        decision = agent_equipment_config.consumer_action_decision(
            {
                "safety_status": "unsafe",
                "diagnostics": [{"kind": "semantic conflict"}],
                "migration_previews": [],
            },
            equipment="issue_tracker_ops",
            requested_behavior="mutation",
            required_capabilities=["tracker_write"],
            supported_capabilities=["tracker_write"],
        )

        self.assertEqual(decision["state"], "blocking")
        self.assertEqual(decision["source"], "effective_config.safety_status")
        self.assertIn("semantic conflict", decision["reason"])
        self.assertEqual(decision["fallback"], "advisory dry-run")

    def test_consumer_action_decision_blocks_mutation_when_projection_is_malformed(self):
        for malformed_projection in (None, "blocking", ["classification", "blocking"]):
            with self.subTest(malformed_projection=malformed_projection):
                decision = agent_equipment_config.consumer_action_decision(
                    {
                        "safety_status": "unsafe",
                        "enforcement_projection": malformed_projection,
                        "diagnostics": [{"kind": "semantic conflict"}],
                        "migration_previews": [],
                    },
                    equipment="issue_tracker_ops",
                    requested_behavior="mutation",
                    required_capabilities=["tracker_write"],
                    supported_capabilities=["tracker_write"],
                )

                self.assertEqual(decision["state"], "blocking")
                self.assertEqual(decision["source"], "effective_config.safety_status")
                self.assertEqual(decision["evidence"]["enforcement_projection"], {})
                self.assertEqual(decision["fallback"], "advisory dry-run")

    def test_consumer_action_decision_blocks_mutation_when_diagnostics_are_malformed(self):
        for malformed_diagnostics in (None, "semantic conflict", {"kind": "semantic conflict"}):
            with self.subTest(malformed_diagnostics=malformed_diagnostics):
                decision = agent_equipment_config.consumer_action_decision(
                    {
                        "safety_status": "unsafe",
                        "enforcement_projection": {"classification": "blocking"},
                        "diagnostics": malformed_diagnostics,
                        "migration_previews": [],
                    },
                    equipment="issue_tracker_ops",
                    requested_behavior="mutation",
                    required_capabilities=["tracker_write"],
                    supported_capabilities=["tracker_write"],
                )

                self.assertEqual(decision["state"], "blocking")
                self.assertEqual(decision["source"], "effective_config.enforcement_projection")
                self.assertEqual(decision["evidence"]["diagnostics"], [])
                self.assertEqual(decision["fallback"], "advisory dry-run")

    def test_consumer_action_decision_ignores_malformed_migration_previews(self):
        for malformed_migration_previews in (None, "migration preview", {"kind": "rename"}):
            with self.subTest(malformed_migration_previews=malformed_migration_previews):
                decision = agent_equipment_config.consumer_action_decision(
                    {
                        "safety_status": "usable",
                        "enforcement_projection": {"classification": "advisory"},
                        "diagnostics": [],
                        "migration_previews": malformed_migration_previews,
                    },
                    equipment="issue_tracker_ops",
                    requested_behavior="advisory",
                )

                self.assertEqual(decision["state"], "advisory")
                self.assertEqual(decision["evidence"]["migration_previews"], [])
                self.assertNotIn("migration preview", decision["reason"])

    def test_consumer_action_decision_prefers_blocking_over_unsupported(self):
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

        decision = self.issue_tracker_ops_consumer_decision(
            result,
            requested_behavior="mutation",
            supported_capabilities=frozenset({"tracker_read"}),
        )

        self.assertEqual(result["safety_status"], "unsafe")
        self.assertEqual(result["enforcement_projection"]["classification"], "blocking")
        self.assertEqual(decision["state"], "blocking")
        self.assertIn("missing authority", decision["reason"])
        self.assertEqual(decision["fallback"], "advisory dry-run")

    def test_consumer_action_decision_reports_unsupported_capability(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            policy = self.write_layer(root, "org.toml", """
                [agent_equipment_config.layer]
                name = "organization or tracker policy"
                category = "committed durable config"

                [agent_equipment_config.authority]
                live_tracker_write = "usable"

                [issue_tracker_ops]
                mode = "execute"
                external_disclosure = "allowed"
            """)

            result = agent_equipment_config.effective_config([policy], [self.issue_ops_fragment()], requested_behavior="mutation")

        decision = self.issue_tracker_ops_consumer_decision(
            result,
            requested_behavior="mutation",
            supported_capabilities=frozenset({"tracker_read"}),
        )

        self.assertEqual(result["safety_status"], "usable")
        self.assertEqual(decision["state"], "unsupported")
        self.assertEqual(decision["fallback"], "advisory dry-run")

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

        self.assertEqual(result["safety_status"], "untrusted")
        self.assertIn("untrusted source", [item["kind"] for item in result["diagnostics"]])
        self.assertIn("missing authority", [item["kind"] for item in result["diagnostics"]])
        self.assertEqual(result["enforcement_projection"]["classification"], "blocking")

    def test_untrusted_authority_diagnostic_is_not_repeated_per_field(self):
        fragment = agent_equipment_config.SchemaFragment(
            namespace="issue_tracker_ops",
            version=1,
            fields={
                "mode": agent_equipment_config.FieldSpec(type="string", required=True),
                "external_disclosure": agent_equipment_config.FieldSpec(type="string", required=True),
            },
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            policy = self.write_layer(root, "org.toml", """
                [agent_equipment_config.layer]
                name = "organization or tracker policy"
                category = "committed durable config"

                [agent_equipment_config.policy.issue_tracker_ops.mode]
                required_for = "mutation"
                authority = "live_tracker_write"

                [agent_equipment_config.policy.issue_tracker_ops.external_disclosure]
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

            result = agent_equipment_config.effective_config([policy, untrusted_authority], [fragment], requested_behavior="mutation")

        untrusted_authority_diagnostics = [
            item for item in result["diagnostics"]
            if item["kind"] == "untrusted source" and item["path"] == "agent_equipment_config.authority.live_tracker_write"
        ]
        self.assertEqual(len(untrusted_authority_diagnostics), 1)

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

    def test_issue_tracker_ops_authoring_pressure_scenario_applies_reviewed_live_mutation_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            org = self.write_layer(root, "org.toml", """
                [agent_equipment_config.layer]
                name = "organization or tracker policy"
                category = "committed durable config"

                [agent_equipment_config.authority]
                live_tracker_write = "usable"

                [agent_equipment_config.policy.issue_tracker_ops.mode]
                required_for = "mutation"
                authority = "live_tracker_write"

                [agent_equipment_config.policy.issue_tracker_ops.external_disclosure]
                required_for = "mutation"
                authority = "live_tracker_write"

                [issue_tracker_ops]
                mode = "dry-run"
                external_disclosure = "blocked"
            """)
            original_text = org.read_text(encoding="utf-8")

            proposal = json.loads(agent_equipment_config.run(
                [
                    "config",
                    "propose",
                    "--issue-tracker-ops",
                    "--set",
                    "issue_tracker_ops.mode=execute",
                    "--set",
                    "issue_tracker_ops.external_disclosure=allowed",
                ],
                stdout_text=True,
            ))
            plan_stdout = agent_equipment_config.run(
                [
                    "config",
                    "patch",
                    "--layer",
                    str(org),
                    "--source-target",
                    str(org),
                    "--issue-tracker-ops",
                    "--set",
                    "issue_tracker_ops.mode=execute",
                    "--set",
                    "issue_tracker_ops.external_disclosure=allowed",
                    "--plan-authority",
                    "operator",
                ],
                stdout_text=True,
            )
            planned_text = org.read_text(encoding="utf-8")
            apply_stdout = io.StringIO()
            apply_exit = agent_equipment_config.run(
                [
                    "config",
                    "apply",
                    "--plan",
                    "-",
                    "--apply-authority",
                    "operator",
                ],
                stdin=io.StringIO(plan_stdout),
                stdout=apply_stdout,
            )
            applied_text = org.read_text(encoding="utf-8")
            effective = agent_equipment_config.effective_config(
                [org],
                [agent_equipment_config.issue_tracker_ops_fragment()],
                requested_behavior="mutation",
            )
            decision = self.issue_tracker_ops_consumer_decision(effective, requested_behavior="mutation")

        plan = json.loads(plan_stdout)
        apply_payload = json.loads(apply_stdout.getvalue())
        self.assertIsNone(proposal["source_target"])
        self.assertEqual(proposal["possible_target_categories"], ["committed durable config", "local-only operator config"])
        self.assertEqual(proposal["candidates"][0]["source_target"], None)
        self.assertEqual(planned_text, original_text)
        self.assertEqual(plan["plan_kind"], "patch-layer")
        self.assertTrue(plan["validation_result"]["passed"])
        self.assertEqual(plan["virtual_post_change_effective_config"]["safety_status"], "usable")
        self.assertEqual(plan["audit_preview"]["source_artifact_durability"], "durable project evidence")
        self.assertTrue(plan["audit_preview"]["project_truth_after_apply"])
        self.assertEqual(apply_exit, 0)
        self.assertTrue(apply_payload["applied"])
        self.assertEqual(apply_payload["audit_records"][-1]["action"], "config authoring apply mutation")
        self.assertTrue(apply_payload["audit_records"][-1]["write_performed"])
        self.assertIn('mode = "execute"', applied_text)
        self.assertIn('external_disclosure = "allowed"', applied_text)
        self.assertEqual(effective["safety_status"], "usable")
        self.assertEqual(effective["enforcement_projection"]["classification"], "advisory")
        self.assertEqual(decision["state"], "allowed")
