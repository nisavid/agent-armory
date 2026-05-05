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

        self.assertEqual(result["safety_status"], "untrusted")
        self.assertIn("untrusted source", [item["kind"] for item in result["diagnostics"]])
        self.assertIn("missing authority", [item["kind"] for item in result["diagnostics"]])
        self.assertEqual(result["enforcement_projection"]["classification"], "blocking")

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
