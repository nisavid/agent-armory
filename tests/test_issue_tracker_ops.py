import argparse
import io
import json
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from tools import issue_tracker_ops


class FakeGh:
    def __init__(self, responses=None):
        self.calls = []
        self.responses = list(responses or [])

    def __call__(self, args, *, input_text=None):
        self.calls.append((args, input_text))
        if self.responses:
            return self.responses.pop(0)
        return subprocess.CompletedProcess(args, 0, stdout="{}", stderr="")


class IssueTrackerOpsTests(unittest.TestCase):
    def run_cli(self, argv, gh=None):
        stdout = io.StringIO()
        stderr = io.StringIO()
        exit_code = issue_tracker_ops.run(argv, gh=gh or FakeGh(), stdout=stdout, stderr=stderr)
        return exit_code, stdout.getvalue(), stderr.getvalue()

    def write_config_layer(self, root: Path, name: str, text: str) -> Path:
        path = root / name
        path.write_text(textwrap.dedent(text).lstrip(), encoding="utf-8")
        return path

    def assert_config_projection(
        self,
        config: dict,
        *,
        action: str,
        decision_state: str,
        safety_status: str,
        diagnostic_kind: str | None = None,
        operation: str = "comment",
    ) -> None:
        projection = config["consumer_enforcement_projection"]
        self.assertEqual(projection["surface"], "issue_tracker_ops.github_api_mutation_preflight")
        self.assertEqual(projection["operation"], operation)
        self.assertEqual(projection["requested_behavior"], "mutation")
        self.assertEqual(projection["adapter_action"], action)
        self.assertEqual(projection["decision_state"], decision_state)
        self.assertEqual(projection["approval_behavior"], "not_supported")
        self.assertEqual(projection["owner"], "issue_tracker_ops_adapter")
        self.assertEqual(projection["effective_config"]["safety_status"], safety_status)
        self.assertEqual(config["effective_config"]["safety_status"], safety_status)
        if diagnostic_kind is not None:
            self.assertIn(diagnostic_kind, projection["effective_config"]["diagnostic_kinds"])

    def test_describe_core_reports_tracker_neutral_contract_without_calling_gh(self):
        gh = FakeGh()

        exit_code, stdout, stderr = self.run_cli(["describe-core"], gh=gh)

        self.assertEqual(exit_code, 0, stderr)
        self.assertEqual(gh.calls, [])
        payload = json.loads(stdout)
        self.assertEqual(payload["schema"], "issue_tracker_ops.core_contract.v1alpha1")
        self.assertEqual(payload["mode"], "describe")
        self.assertEqual(payload["operation"], "describe-core")
        self.assertIn("issue.create", payload["operation_ids"])
        self.assertIn("dependency.list_blocked_by", payload["operation_ids"])
        self.assertEqual(payload["operation_classes"], ["advisory", "read", "write"])
        self.assertIn("request_shape", payload["audit_requirements"])
        self.assertIn("result_summary", payload["audit_requirements"])
        self.assertEqual(payload["capability_dispositions"], ["emulated", "fallback", "native", "unsupported"])
        self.assertIn("external_network_write", payload["side_effect_classes"])
        issue_create = payload["operations"]["issue.create"]
        self.assertEqual(issue_create["operation_class"], "write")
        self.assertIn("dry_run_required", issue_create["audit_requirements"])

    def test_describe_adapter_reports_github_baseline_capabilities_without_calling_gh(self):
        gh = FakeGh()

        exit_code, stdout, stderr = self.run_cli(
            ["describe-adapter", "--adapter", "github-issues-baseline"],
            gh=gh,
        )

        self.assertEqual(exit_code, 0, stderr)
        self.assertEqual(gh.calls, [])
        payload = json.loads(stdout)
        self.assertEqual(payload["schema"], "issue_tracker_ops.adapter_contract.v1alpha1")
        self.assertEqual(payload["mode"], "describe")
        self.assertEqual(payload["operation"], "describe-adapter")
        self.assertEqual(payload["adapter"], "github-issues-baseline")
        self.assertEqual(payload["capabilities"]["issue.create"]["disposition"], "native")
        self.assertEqual(payload["capabilities"]["issue.read"]["disposition"], "fallback")
        self.assertNotIn("runtime_command", payload["capabilities"]["issue.read"])
        self.assertEqual(payload["capabilities"]["issue.read"]["fallback"], "Use gh issue view until #15 expands the runtime adapter.")
        self.assertEqual(payload["capabilities"]["dependency.add_blocked_by"]["runtime_command"], ["add-blocked-by"])
        self.assertEqual(payload["capabilities"]["status.set"]["disposition"], "fallback")
        self.assertEqual(payload["capabilities"]["attachment.add"]["disposition"], "unsupported")
        self.assertIn("GitHub Projects fields are follow-up adapter work.", payload["notes"])

    def test_plan_operation_reports_native_write_plan_without_calling_gh(self):
        gh = FakeGh()

        exit_code, stdout, stderr = self.run_cli(
            [
                "plan-operation",
                "--adapter",
                "github-issues-baseline",
                "--operation",
                "issue.create",
            ],
            gh=gh,
        )

        self.assertEqual(exit_code, 0, stderr)
        self.assertEqual(gh.calls, [])
        payload = json.loads(stdout)
        self.assertEqual(payload["schema"], "issue_tracker_ops.operation_plan.v1alpha1")
        self.assertEqual(payload["mode"], "plan")
        self.assertEqual(payload["operation"], "plan-operation")
        self.assertEqual(payload["adapter"], "github-issues-baseline")
        self.assertEqual(payload["operation_id"], "issue.create")
        self.assertEqual(payload["operation_class"], "write")
        self.assertEqual(payload["capability"]["disposition"], "native")
        self.assertEqual(payload["capability"]["runtime_command"], ["create-issue"])
        self.assertEqual(payload["safety"]["dry_run_default"], True)
        self.assertEqual(payload["safety"]["execute_required"], True)
        self.assertEqual(payload["safety"]["config_preflight_required"], False)
        self.assertEqual(payload["safety"]["mutation_authority_required"], True)
        self.assertEqual(payload["safety"]["config_authorization_supported"], True)
        self.assertEqual(payload["safety"]["mutation_policy_ref_supported"], True)
        self.assertIn("external_network_write", payload["side_effects"])

    def test_plan_operation_reports_native_read_safety_without_calling_gh(self):
        gh = FakeGh()

        exit_code, stdout, stderr = self.run_cli(
            [
                "plan-operation",
                "--adapter",
                "github-issues-baseline",
                "--operation",
                "dependency.list_blocked_by",
            ],
            gh=gh,
        )

        self.assertEqual(exit_code, 0, stderr)
        self.assertEqual(gh.calls, [])
        payload = json.loads(stdout)
        self.assertEqual(payload["operation_id"], "dependency.list_blocked_by")
        self.assertEqual(payload["operation_class"], "read")
        self.assertEqual(payload["capability"]["disposition"], "native")
        self.assertEqual(payload["capability"]["runtime_command"], ["list-blocked-by"])
        self.assertEqual(payload["safety"]["available"], True)
        self.assertEqual(payload["safety"]["dry_run_default"], False)
        self.assertEqual(payload["safety"]["execute_required"], True)
        self.assertEqual(payload["safety"]["config_preflight_required"], False)
        self.assertIn("external_network_read", payload["side_effects"])

    def test_plan_operation_reports_fallback_and_unsupported_boundaries(self):
        cases = [
            ("status.set", "fallback", True, True, "Represent workflow status with configured labels or tracker comments until Projects support lands."),
            ("attachment.add", "unsupported", False, False, None),
        ]
        for operation_id, disposition, available, execute_required, fallback in cases:
            with self.subTest(operation_id=operation_id):
                gh = FakeGh()

                exit_code, stdout, stderr = self.run_cli(
                    [
                        "plan-operation",
                        "--adapter",
                        "github-issues-baseline",
                        "--operation",
                        operation_id,
                    ],
                    gh=gh,
                )

                self.assertEqual(exit_code, 0, stderr)
                self.assertEqual(gh.calls, [])
                payload = json.loads(stdout)
                self.assertEqual(payload["operation_id"], operation_id)
                self.assertEqual(payload["capability"]["disposition"], disposition)
                self.assertEqual(payload["safety"]["available"], available)
                self.assertEqual(payload["safety"]["execute_required"], execute_required)
                self.assertEqual(payload["safety"]["dry_run_default"], available)
                if fallback is None:
                    self.assertNotIn("fallback", payload["capability"])
                else:
                    self.assertEqual(payload["capability"]["fallback"], fallback)

    def test_create_issue_defaults_to_dry_run_without_calling_gh(self):
        gh = FakeGh()

        exit_code, stdout, stderr = self.run_cli(
            [
                "create-issue",
                "--repo",
                "OWNER/REPO",
                "--title",
                "Build child issue",
                "--body",
                "Issue body",
                "--label",
                "ready-for-agent",
            ],
            gh=gh,
        )

        self.assertEqual(exit_code, 0, stderr)
        self.assertEqual(gh.calls, [])
        payload = json.loads(stdout)
        self.assertEqual(payload["mode"], "dry-run")
        self.assertEqual(payload["operation"], "create-issue")
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["endpoint"], "repos/OWNER/REPO/issues")
        self.assertEqual(
            payload["request"]["body"],
            {
                "title": "Build child issue",
                "body": "Issue body",
                "labels": ["ready-for-agent"],
            },
        )

    def test_comment_execute_posts_issue_comment_with_audit_output(self):
        gh = FakeGh(
            [
                subprocess.CompletedProcess(["gh"], 0, stdout="[]", stderr=""),
                subprocess.CompletedProcess(["gh"], 0, stdout='{"id": 44}', stderr=""),
            ]
        )

        exit_code, stdout, stderr = self.run_cli(
            [
                "comment",
                "--repo",
                "OWNER/REPO",
                "--issue-number",
                "11",
                "--body",
                "Validation note",
                "--mutation-policy-ref",
                "issue-17-approved-plan",
                "--execute",
            ],
            gh=gh,
        )

        self.assertEqual(exit_code, 0, stderr)
        self.assertEqual(len(gh.calls), 2)
        preflight_args, preflight_input = gh.calls[0]
        self.assertEqual(preflight_args[:5], ["gh", "api", "-X", "GET", "repos/OWNER/REPO/issues/11/comments?per_page=100"])
        self.assertIsNone(preflight_input)
        args, input_text = gh.calls[1]
        self.assertEqual(args[:5], ["gh", "api", "-X", "POST", "repos/OWNER/REPO/issues/11/comments"])
        self.assertEqual(json.loads(input_text), {"body": "Validation note"})
        payload = json.loads(stdout)
        self.assertEqual(payload["mode"], "execute")
        self.assertEqual(payload["operation"], "comment")
        self.assertEqual(payload["result"], {"id": 44})
        self.assertEqual(payload["mutation_policy"]["ref"], "issue-17-approved-plan")

    def test_comment_dry_run_with_config_layer_reports_advisory_config_decision(self):
        gh = FakeGh()
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_config_layer(root, "repo.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [issue_tracker_ops]
                mode = "dry-run"
                external_disclosure = "blocked"
            """)

            exit_code, stdout, stderr = self.run_cli(
                [
                    "comment",
                    "--repo",
                    "OWNER/REPO",
                    "--issue-number",
                    "11",
                    "--body",
                    "Validation note",
                    "--config-layer",
                    str(layer),
                ],
                gh=gh,
            )

        self.assertEqual(exit_code, 0, stderr)
        self.assertEqual(gh.calls, [])
        payload = json.loads(stdout)
        self.assertEqual(payload["mode"], "dry-run")
        self.assertEqual(payload["config"]["consumer_action_decision"]["state"], "advisory")
        self.assertEqual(payload["config"]["consumer_enforcement_projection"]["adapter_action"], "advise")
        self.assertEqual(payload["config"]["consumer_enforcement_projection"]["requested_behavior"], "advisory")
        self.assertEqual(
            payload["config"]["effective_config"]["effective"]["issue_tracker_ops"]["mode"]["value"],
            "dry-run",
        )

    def test_comment_dry_run_with_plain_config_handoff_reports_promotion(self):
        gh = FakeGh()
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            handoff = self.write_config_layer(root, "handoff.toml", """
                [issue_tracker_ops]
                mode = "dry-run"
                external_disclosure = "blocked"
            """)

            exit_code, stdout, stderr = self.run_cli(
                [
                    "comment",
                    "--repo",
                    "OWNER/REPO",
                    "--issue-number",
                    "11",
                    "--body",
                    "Validation note",
                    "--config-plain-handoff",
                    str(handoff),
                ],
                gh=gh,
            )

        self.assertEqual(exit_code, 0, stderr)
        self.assertEqual(gh.calls, [])
        payload = json.loads(stdout)
        self.assertEqual(payload["config"]["consumer_action_decision"]["state"], "advisory")
        self.assertEqual(payload["config"]["effective_config"]["plain_handoffs"][0]["source"], handoff.as_posix())
        self.assertEqual(
            payload["config"]["effective_config"]["effective"]["issue_tracker_ops"]["mode"]["layer"],
            "session overrides",
        )

    def test_comment_execute_with_configured_execute_mode_reports_config_decision(self):
        gh = FakeGh(
            [
                subprocess.CompletedProcess(["gh"], 0, stdout="[]", stderr=""),
                subprocess.CompletedProcess(["gh"], 0, stdout='{"id": 44}', stderr=""),
            ]
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_config_layer(root, "repo.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [issue_tracker_ops]
                mode = "execute"
                external_disclosure = "allowed"
            """)

            exit_code, stdout, stderr = self.run_cli(
                [
                    "comment",
                    "--repo",
                    "OWNER/REPO",
                    "--issue-number",
                    "11",
                    "--body",
                    "Validation note",
                    "--config-layer",
                    str(layer),
                    "--execute",
                ],
                gh=gh,
            )

        self.assertEqual(exit_code, 0, stderr)
        self.assertEqual(len(gh.calls), 2)
        payload = json.loads(stdout)
        self.assertEqual(payload["mode"], "execute")
        self.assertEqual(payload["config"]["consumer_action_decision"]["state"], "allowed")
        self.assertEqual(payload["config"]["consumer_semantics"]["configured_mode"], "execute")
        self.assert_config_projection(
            payload["config"],
            action="allow",
            decision_state="allowed",
            safety_status="usable",
        )

    def test_comment_execute_config_projection_blocks_required_safety_statuses(self):
        cases = [
            (
                "incomplete",
                [(
                    "repo.toml",
                    """
                    [agent_equipment_config.layer]
                    name = "repository policy"
                    category = "committed durable config"

                    [issue_tracker_ops]
                    mode = "execute"
                    """,
                )],
                "schema conflict",
            ),
            (
                "unsafe",
                [(
                    "repo.toml",
                    """
                    [agent_equipment_config.layer]
                    name = "repository policy"
                    category = "committed durable config"

                    [issue_tracker_ops]
                    mode = "execute"
                    external_disclosure = "blocked"
                    """,
                )],
                "semantic conflict",
            ),
            (
                "conflicted",
                [
                    (
                        "repo-a.toml",
                        """
                        [agent_equipment_config.layer]
                        name = "repository policy"
                        category = "committed durable config"

                        [issue_tracker_ops]
                        mode = "execute"
                        external_disclosure = "allowed"
                        """,
                    ),
                    (
                        "repo-b.toml",
                        """
                        [agent_equipment_config.layer]
                        name = "repository policy"
                        category = "committed durable config"

                        [issue_tracker_ops]
                        mode = "dry-run"
                        external_disclosure = "allowed"
                        """,
                    ),
                ],
                "same-precedence collision",
            ),
            (
                "stale",
                [(
                    "repo.toml",
                    """
                    [agent_equipment_config.layer]
                    name = "repository policy"
                    category = "committed durable config"

                    [agent_equipment_config.fragment_versions]
                    issue_tracker_ops = 1

                    [issue_tracker_ops]
                    mode = "execute"
                    external_disclosure = "allowed"
                    """,
                )],
                "stale schema",
            ),
            (
                "untrusted",
                [(
                    "repo.toml",
                    """
                    [agent_equipment_config.layer]
                    name = "repository policy"
                    category = "committed durable config"
                    trusted = false

                    [issue_tracker_ops]
                    mode = "execute"
                    external_disclosure = "allowed"
                    """,
                )],
                "untrusted source",
            ),
            (
                "unsafe",
                [(
                    "repo.toml",
                    """
                    [agent_equipment_config.layer]
                    name = "organization or tracker policy"
                    category = "committed durable config"

                    [agent_equipment_config.policy.issue_tracker_ops.mode]
                    required_for = "mutation"
                    authority = "live_tracker_write"

                    [issue_tracker_ops]
                    mode = "execute"
                    external_disclosure = "allowed"
                    """,
                )],
                "missing authority",
            ),
        ]
        for expected_status, layers, diagnostic_kind in cases:
            with self.subTest(expected_status=expected_status, diagnostic_kind=diagnostic_kind):
                gh = FakeGh()
                with tempfile.TemporaryDirectory() as tmpdir:
                    root = Path(tmpdir)
                    layer_paths = [
                        self.write_config_layer(root, layer_name, layer_text)
                        for layer_name, layer_text in layers
                    ]
                    argv = [
                        "comment",
                        "--repo",
                        "OWNER/REPO",
                        "--issue-number",
                        "11",
                        "--body",
                        "Validation note",
                        "--execute",
                    ]
                    for layer_path in layer_paths:
                        argv.extend(["--config-layer", str(layer_path)])

                    exit_code, stdout, stderr = self.run_cli(argv, gh=gh)

                self.assertEqual(exit_code, 1)
                self.assertEqual(stderr, "")
                self.assertEqual(gh.calls, [])
                payload = json.loads(stdout)
                self.assertEqual(payload["error"]["code"], "config_refused")
                self.assert_config_projection(
                    payload["config"],
                    action="block",
                    decision_state="blocking",
                    safety_status=expected_status,
                    diagnostic_kind=diagnostic_kind,
                )

    def test_comment_execute_with_configured_dry_run_refuses_without_calling_gh(self):
        gh = FakeGh()
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            layer = self.write_config_layer(root, "repo.toml", """
                [agent_equipment_config.layer]
                name = "repository policy"
                category = "committed durable config"

                [issue_tracker_ops]
                mode = "dry-run"
                external_disclosure = "blocked"
            """)

            exit_code, stdout, stderr = self.run_cli(
                [
                    "comment",
                    "--repo",
                    "OWNER/REPO",
                    "--issue-number",
                    "11",
                    "--body",
                    "Validation note",
                    "--config-layer",
                    str(layer),
                    "--execute",
                ],
                gh=gh,
            )

        self.assertEqual(exit_code, 1)
        self.assertEqual(stderr, "")
        self.assertEqual(gh.calls, [])
        payload = json.loads(stdout)
        self.assertEqual(payload["mode"], "execute")
        self.assertEqual(payload["operation"], "comment")
        self.assertEqual(payload["error"]["code"], "config_refused")
        self.assertEqual(payload["config"]["consumer_action_decision"]["state"], "unsupported")
        self.assertEqual(payload["config"]["consumer_action_decision"]["fallback"], "advisory dry-run")
        self.assertEqual(payload["config"]["consumer_enforcement_projection"]["adapter_action"], "block")
        self.assertEqual(payload["config"]["consumer_enforcement_projection"]["decision_state"], "unsupported")
        self.assertIn(
            "configured_execute_mode",
            payload["config"]["consumer_action_decision"]["evidence"]["unsupported_capabilities"],
        )

    def test_mutation_execute_without_config_or_policy_ref_fails_closed_before_gh(self):
        gh = FakeGh()

        exit_code, stdout, stderr = self.run_cli(
            [
                "comment",
                "--repo",
                "OWNER/REPO",
                "--issue-number",
                "11",
                "--body",
                "Validation note",
                "--execute",
            ],
            gh=gh,
        )

        self.assertEqual(exit_code, 1)
        self.assertEqual(stderr, "")
        self.assertEqual(gh.calls, [])
        payload = json.loads(stdout)
        self.assertEqual(payload["mode"], "execute")
        self.assertEqual(payload["operation"], "comment")
        self.assertEqual(payload["error"]["code"], "mutation_policy_required")
        self.assertEqual(
            payload["error"]["message"],
            "Issue Tracker Ops mutation execute requires Config authorization or --mutation-policy-ref.",
        )

    def test_comment_execute_with_policy_ref_blocks_duplicate_body_before_posting(self):
        gh = FakeGh(
            [
                subprocess.CompletedProcess(
                    ["gh"],
                    0,
                    stdout=json.dumps(
                        [
                            {
                                "id": 100,
                                "html_url": "https://github.com/OWNER/REPO/issues/11#issuecomment-100",
                                "body": "Validation note",
                            }
                        ]
                    ),
                    stderr="",
                )
            ]
        )

        exit_code, stdout, stderr = self.run_cli(
            [
                "comment",
                "--repo",
                "OWNER/REPO",
                "--issue-number",
                "11",
                "--body",
                "Validation note",
                "--mutation-policy-ref",
                "issue-17-approved-plan",
                "--idempotency-key",
                "comment-validation-note",
                "--execute",
            ],
            gh=gh,
        )

        self.assertEqual(exit_code, 1)
        self.assertEqual(stderr, "")
        self.assertEqual(len(gh.calls), 1)
        args, input_text = gh.calls[0]
        self.assertEqual(args[:5], ["gh", "api", "-X", "GET", "repos/OWNER/REPO/issues/11/comments?per_page=100"])
        self.assertIsNone(input_text)
        payload = json.loads(stdout)
        self.assertEqual(payload["error"]["code"], "duplicate_detected")
        self.assertEqual(payload["duplicate_decision"]["action"], "block")
        self.assertEqual(payload["duplicate_decision"]["existing"]["id"], 100)
        self.assertEqual(payload["mutation_policy"]["ref"], "issue-17-approved-plan")
        self.assertEqual(payload["idempotency_key"], "comment-validation-note")

    def test_comment_execute_blocks_duplicate_body_from_paginated_preflight(self):
        gh = FakeGh(
            [
                subprocess.CompletedProcess(
                    ["gh"],
                    0,
                    stdout=json.dumps(
                        [
                            [],
                            [
                                {
                                    "id": 100,
                                    "html_url": "https://github.com/OWNER/REPO/issues/11#issuecomment-100",
                                    "body": "Validation note",
                                }
                            ],
                        ]
                    ),
                    stderr="",
                )
            ]
        )

        exit_code, stdout, stderr = self.run_cli(
            [
                "comment",
                "--repo",
                "OWNER/REPO",
                "--issue-number",
                "11",
                "--body",
                "Validation note",
                "--mutation-policy-ref",
                "issue-17-approved-plan",
                "--execute",
            ],
            gh=gh,
        )

        self.assertEqual(exit_code, 1)
        self.assertEqual(stderr, "")
        self.assertEqual(len(gh.calls), 1)
        args, input_text = gh.calls[0]
        self.assertEqual(args[:5], ["gh", "api", "-X", "GET", "repos/OWNER/REPO/issues/11/comments?per_page=100"])
        self.assertIn("--paginate", args)
        self.assertIn("--slurp", args)
        self.assertIsNone(input_text)
        payload = json.loads(stdout)
        self.assertEqual(payload["error"]["code"], "duplicate_detected")
        self.assertEqual(payload["duplicate_decision"]["existing"]["id"], 100)

    def test_comment_execute_fails_closed_on_unexpected_preflight_response(self):
        gh = FakeGh([subprocess.CompletedProcess(["gh"], 0, stdout='{"message": "unexpected"}', stderr="")])

        exit_code, stdout, stderr = self.run_cli(
            [
                "comment",
                "--repo",
                "OWNER/REPO",
                "--issue-number",
                "11",
                "--body",
                "Validation note",
                "--mutation-policy-ref",
                "issue-17-approved-plan",
                "--execute",
            ],
            gh=gh,
        )

        self.assertEqual(exit_code, 1)
        self.assertEqual(stderr, "")
        self.assertEqual(len(gh.calls), 1)
        payload = json.loads(stdout)
        self.assertEqual(payload["error"]["code"], "preflight_response_invalid")
        self.assertEqual(payload["preflight"]["request"]["endpoint"], "repos/OWNER/REPO/issues/11/comments?per_page=100")

    def test_create_issue_execute_blocks_duplicate_title_before_posting(self):
        gh = FakeGh(
            [
                subprocess.CompletedProcess(
                    ["gh"],
                    0,
                    stdout=json.dumps(
                        [
                            {
                                "id": 200,
                                "number": 17,
                                "html_url": "https://github.com/OWNER/REPO/issues/17",
                                "title": "Implement issue ops safety",
                                "state": "open",
                            }
                        ]
                    ),
                    stderr="",
                )
            ]
        )

        exit_code, stdout, stderr = self.run_cli(
            [
                "create-issue",
                "--repo",
                "OWNER/REPO",
                "--title",
                "  implement   ISSUE OPS safety  ",
                "--body",
                "Issue body",
                "--mutation-policy-ref",
                "issue-17-approved-plan",
                "--execute",
            ],
            gh=gh,
        )

        self.assertEqual(exit_code, 1)
        self.assertEqual(stderr, "")
        self.assertEqual(len(gh.calls), 1)
        args, input_text = gh.calls[0]
        self.assertEqual(args[:5], ["gh", "api", "-X", "GET", "repos/OWNER/REPO/issues?state=open&per_page=100"])
        self.assertIsNone(input_text)
        payload = json.loads(stdout)
        self.assertEqual(payload["error"]["code"], "duplicate_detected")
        self.assertEqual(payload["duplicate_decision"]["existing"]["number"], 17)
        self.assertEqual(payload["duplicate_decision"]["action"], "block")

    def test_comment_execute_with_duplicate_override_records_audit_decision(self):
        gh = FakeGh(
            [
                subprocess.CompletedProcess(
                    ["gh"],
                    0,
                    stdout=json.dumps(
                        [
                            {
                                "id": 100,
                                "html_url": "https://github.com/OWNER/REPO/issues/11#issuecomment-100",
                                "body": "Validation note",
                            }
                        ]
                    ),
                    stderr="",
                ),
                subprocess.CompletedProcess(["gh"], 0, stdout='{"id": 101}', stderr=""),
            ]
        )

        exit_code, stdout, stderr = self.run_cli(
            [
                "comment",
                "--repo",
                "OWNER/REPO",
                "--issue-number",
                "11",
                "--body",
                "Validation note",
                "--mutation-policy-ref",
                "issue-17-approved-plan",
                "--if-duplicate",
                "allow-with-reason",
                "--duplicate-override-reason",
                "Second note is intentionally sent after reopening the issue.",
                "--execute",
            ],
            gh=gh,
        )

        self.assertEqual(exit_code, 0, stderr)
        self.assertEqual(len(gh.calls), 2)
        payload = json.loads(stdout)
        self.assertEqual(payload["result"], {"id": 101})
        self.assertEqual(payload["duplicate_decision"]["action"], "allow-with-reason")
        self.assertEqual(payload["duplicate_decision"]["existing"]["id"], 100)
        self.assertEqual(
            payload["duplicate_decision"]["override_reason"],
            "Second note is intentionally sent after reopening the issue.",
        )

    def test_execute_failure_with_fallback_file_writes_reconciliation_record(self):
        gh = FakeGh(
            [
                subprocess.CompletedProcess(["gh"], 0, stdout="[]", stderr=""),
                subprocess.CompletedProcess(["gh"], 1, stdout="", stderr="secondary rate limit exceeded"),
            ]
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            fallback_path = Path(tmpdir) / "issue-17-fallback.json"

            exit_code, stdout, stderr = self.run_cli(
                [
                    "comment",
                    "--repo",
                    "OWNER/REPO",
                    "--issue-number",
                    "11",
                    "--body",
                    "Validation note",
                    "--mutation-policy-ref",
                    "issue-17-approved-plan",
                    "--idempotency-key",
                    "comment-validation-note",
                    "--fallback-record-file",
                    str(fallback_path),
                    "--execute",
                ],
                gh=gh,
            )

            self.assertEqual(exit_code, 1)
            self.assertEqual(stderr, "")
            self.assertEqual(len(gh.calls), 2)
            payload = json.loads(stdout)
            record = json.loads(fallback_path.read_text(encoding="utf-8"))

        self.assertEqual(payload["failure"]["class"], "secondary-rate-limit")
        self.assertEqual(payload["retry_condition"], "retry after the API condition clears and rerun reconciliation first")
        self.assertEqual(payload["fallback_record_file"], str(fallback_path))
        self.assertEqual(record["schema"], "issue_tracker_ops.fallback_record.v1alpha1")
        self.assertEqual(record["status"], "pending_reconciliation")
        self.assertEqual(record["operation"], "comment")
        self.assertEqual(record["idempotency_key"], "comment-validation-note")
        self.assertEqual(record["request"]["endpoint"], "repos/OWNER/REPO/issues/11/comments")
        self.assertTrue(record["reconciliation"]["required"])

    def test_execute_failure_reports_unwritable_fallback_record_file(self):
        gh = FakeGh(
            [
                subprocess.CompletedProcess(["gh"], 0, stdout="[]", stderr=""),
                subprocess.CompletedProcess(["gh"], 1, stdout="", stderr="secondary rate limit exceeded"),
            ]
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            exit_code, stdout, stderr = self.run_cli(
                [
                    "comment",
                    "--repo",
                    "OWNER/REPO",
                    "--issue-number",
                    "11",
                    "--body",
                    "Validation note",
                    "--mutation-policy-ref",
                    "issue-17-approved-plan",
                    "--fallback-record-file",
                    tmpdir,
                    "--execute",
                ],
                gh=gh,
            )

        self.assertEqual(exit_code, 1)
        self.assertEqual(stderr, "")
        payload = json.loads(stdout)
        self.assertEqual(payload["failure"]["class"], "secondary-rate-limit")
        self.assertEqual(payload["fallback_record_file"], tmpdir)
        self.assertEqual(payload["fallback_record_error"]["code"], "fallback_record_write_failed")

    def test_execute_failure_classifies_secondary_rate_limit_before_permission_403(self):
        gh = FakeGh(
            [
                subprocess.CompletedProcess(["gh"], 0, stdout="[]", stderr=""),
                subprocess.CompletedProcess(
                    ["gh"],
                    1,
                    stdout="",
                    stderr="HTTP 403: You have exceeded a secondary rate limit.",
                ),
            ]
        )

        exit_code, stdout, stderr = self.run_cli(
            [
                "comment",
                "--repo",
                "OWNER/REPO",
                "--issue-number",
                "11",
                "--body",
                "Validation note",
                "--mutation-policy-ref",
                "issue-17-approved-plan",
                "--execute",
            ],
            gh=gh,
        )

        self.assertEqual(exit_code, 1)
        self.assertEqual(stderr, "")
        payload = json.loads(stdout)
        self.assertEqual(payload["failure"]["class"], "secondary-rate-limit")
        self.assertTrue(payload["failure"]["retryable"])

    def test_reconcile_fallback_retire_record_after_projected_comment_is_verified(self):
        gh = FakeGh(
            [
                subprocess.CompletedProcess(
                    ["gh"],
                    0,
                    stdout=json.dumps(
                        [
                            {
                                "id": 100,
                                "html_url": "https://github.com/OWNER/REPO/issues/11#issuecomment-100",
                                "body": "Validation note",
                            }
                        ]
                    ),
                    stderr="",
                )
            ]
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            fallback_path = Path(tmpdir) / "fallback.json"
            fallback_path.write_text(
                json.dumps(
                    {
                        "schema": "issue_tracker_ops.fallback_record.v1alpha1",
                        "status": "pending_reconciliation",
                        "owner": "issue_tracker_ops_adapter",
                        "operation": "comment",
                        "repo": "OWNER/REPO",
                        "request": {
                            "method": "POST",
                            "endpoint": "repos/OWNER/REPO/issues/11/comments",
                            "body": {"body": "Validation note"},
                        },
                    }
                ),
                encoding="utf-8",
            )

            exit_code, stdout, stderr = self.run_cli(
                [
                    "reconcile-fallback",
                    "--repo",
                    "OWNER/REPO",
                    "--fallback-record-file",
                    str(fallback_path),
                    "--retire-record",
                    "--retirement-note",
                    "Verified projected comment.",
                    "--execute",
                ],
                gh=gh,
            )
            retired_record = json.loads(fallback_path.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0, stderr)
        self.assertEqual(len(gh.calls), 1)
        args, input_text = gh.calls[0]
        self.assertEqual(args[:5], ["gh", "api", "-X", "GET", "repos/OWNER/REPO/issues/11/comments?per_page=100"])
        self.assertIsNone(input_text)
        payload = json.loads(stdout)
        self.assertEqual(payload["operation"], "reconcile-fallback")
        self.assertEqual(payload["result"]["projection_status"], "projected")
        self.assertEqual(payload["result"]["recommended_action"], "retire_record")
        self.assertEqual(retired_record["status"], "retired")
        self.assertEqual(retired_record["retirement_note"], "Verified projected comment.")

    def test_reconcile_fallback_retire_record_after_projected_update_is_verified(self):
        gh = FakeGh(
            [
                subprocess.CompletedProcess(
                    ["gh"],
                    0,
                    stdout=json.dumps(
                        {
                            "id": 44,
                            "number": 11,
                            "html_url": "https://github.com/OWNER/REPO/issues/11",
                            "title": "Updated title",
                            "body": "Updated body",
                            "state": "open",
                        }
                    ),
                    stderr="",
                )
            ]
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            fallback_path = Path(tmpdir) / "fallback.json"
            fallback_path.write_text(
                json.dumps(
                    {
                        "schema": "issue_tracker_ops.fallback_record.v1alpha1",
                        "status": "pending_reconciliation",
                        "owner": "issue_tracker_ops_adapter",
                        "operation": "update-issue",
                        "repo": "OWNER/REPO",
                        "request": {
                            "method": "PATCH",
                            "endpoint": "repos/OWNER/REPO/issues/11",
                            "body": {"title": "Updated title", "body": "Updated body"},
                        },
                    }
                ),
                encoding="utf-8",
            )

            exit_code, stdout, stderr = self.run_cli(
                [
                    "reconcile-fallback",
                    "--repo",
                    "OWNER/REPO",
                    "--fallback-record-file",
                    str(fallback_path),
                    "--retire-record",
                    "--retirement-note",
                    "Verified projected issue update.",
                    "--execute",
                ],
                gh=gh,
            )
            retired_record = json.loads(fallback_path.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0, stderr)
        self.assertEqual(len(gh.calls), 1)
        args, input_text = gh.calls[0]
        self.assertEqual(args[:5], ["gh", "api", "-X", "GET", "repos/OWNER/REPO/issues/11"])
        self.assertIsNone(input_text)
        payload = json.loads(stdout)
        self.assertEqual(payload["result"]["projection_status"], "projected")
        self.assertEqual(payload["result"]["projected"]["number"], 11)
        self.assertEqual(retired_record["status"], "retired")

    def test_reconcile_fallback_retire_record_after_projected_dependency_is_verified(self):
        gh = FakeGh(
            [
                subprocess.CompletedProcess(
                    ["gh"],
                    0,
                    stdout='[{"id": 98765, "number": 11, "html_url": "https://github.com/OWNER/REPO/issues/11"}]',
                    stderr="",
                )
            ]
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            fallback_path = Path(tmpdir) / "fallback.json"
            fallback_path.write_text(
                json.dumps(
                    {
                        "schema": "issue_tracker_ops.fallback_record.v1alpha1",
                        "status": "pending_reconciliation",
                        "owner": "issue_tracker_ops_adapter",
                        "operation": "add-blocked-by",
                        "repo": "OWNER/REPO",
                        "request": {
                            "method": "POST",
                            "endpoint": "repos/OWNER/REPO/issues/10/dependencies/blocked_by",
                            "body": {"issue_id": 98765},
                        },
                    }
                ),
                encoding="utf-8",
            )

            exit_code, stdout, stderr = self.run_cli(
                [
                    "reconcile-fallback",
                    "--repo",
                    "OWNER/REPO",
                    "--fallback-record-file",
                    str(fallback_path),
                    "--retire-record",
                    "--retirement-note",
                    "Verified projected dependency relation.",
                    "--execute",
                ],
                gh=gh,
            )
            retired_record = json.loads(fallback_path.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0, stderr)
        self.assertEqual(len(gh.calls), 1)
        args, input_text = gh.calls[0]
        self.assertEqual(args[:5], ["gh", "api", "-X", "GET", "repos/OWNER/REPO/issues/10/dependencies/blocked_by"])
        self.assertIsNone(input_text)
        payload = json.loads(stdout)
        self.assertEqual(payload["result"]["projection_status"], "projected")
        self.assertEqual(payload["result"]["projected"]["number"], 11)
        self.assertEqual(retired_record["status"], "retired")

    def test_reconcile_fallback_refuses_to_retire_removed_dependency_on_unexpected_response(self):
        gh = FakeGh([subprocess.CompletedProcess(["gh"], 0, stdout='{"message": "unexpected"}', stderr="")])
        with tempfile.TemporaryDirectory() as tmpdir:
            fallback_path = Path(tmpdir) / "fallback.json"
            fallback_path.write_text(
                json.dumps(
                    {
                        "schema": "issue_tracker_ops.fallback_record.v1alpha1",
                        "status": "pending_reconciliation",
                        "owner": "issue_tracker_ops_adapter",
                        "operation": "remove-blocked-by",
                        "repo": "OWNER/REPO",
                        "request": {
                            "method": "DELETE",
                            "endpoint": "repos/OWNER/REPO/issues/10/dependencies/blocked_by/98765",
                        },
                    }
                ),
                encoding="utf-8",
            )

            exit_code, stdout, stderr = self.run_cli(
                [
                    "reconcile-fallback",
                    "--repo",
                    "OWNER/REPO",
                    "--fallback-record-file",
                    str(fallback_path),
                    "--retire-record",
                    "--retirement-note",
                    "Verified relation removal.",
                    "--execute",
                ],
                gh=gh,
            )
            record = json.loads(fallback_path.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 1)
        self.assertEqual(stderr, "")
        payload = json.loads(stdout)
        self.assertEqual(payload["result"]["projection_status"], "unknown")
        self.assertEqual(payload["result"]["recommended_action"], "manual_review")
        self.assertEqual(payload["error"]["code"], "retirement_not_allowed")
        self.assertEqual(record["status"], "pending_reconciliation")

    def test_reconcile_fallback_retire_record_requires_note_before_gh(self):
        gh = FakeGh()
        with tempfile.TemporaryDirectory() as tmpdir:
            fallback_path = Path(tmpdir) / "fallback.json"
            fallback_path.write_text(
                json.dumps(
                    {
                        "schema": "issue_tracker_ops.fallback_record.v1alpha1",
                        "status": "pending_reconciliation",
                        "owner": "issue_tracker_ops_adapter",
                        "operation": "comment",
                        "repo": "OWNER/REPO",
                        "request": {
                            "method": "POST",
                            "endpoint": "repos/OWNER/REPO/issues/11/comments",
                            "body": {"body": "Validation note"},
                        },
                    }
                ),
                encoding="utf-8",
            )

            exit_code, stdout, stderr = self.run_cli(
                [
                    "reconcile-fallback",
                    "--repo",
                    "OWNER/REPO",
                    "--fallback-record-file",
                    str(fallback_path),
                    "--retire-record",
                    "--execute",
                ],
                gh=gh,
            )

        self.assertEqual(exit_code, 2)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "--retirement-note is required with --retire-record\n")
        self.assertEqual(gh.calls, [])

    def test_execute_config_without_consumer_decision_fails_closed(self):
        args = argparse.Namespace(operation="comment", execute=True)

        self.assertTrue(issue_tracker_ops.config_refuses_execute({"consumer_semantics": {}}, args))

        payload = issue_tracker_ops.config_refusal_payload(
            "comment",
            issue_tracker_ops.RequestSpec("POST", "repos/OWNER/REPO/issues/11/comments", {"body": "x"}),
            {"consumer_enforcement_projection": {"adapter_action": "allow"}},
        )

        self.assertEqual(
            payload["error"]["message"],
            "Issue Tracker Ops Config did not authorize execute: "
            "missing or malformed consumer action decision",
        )

    def test_execute_config_without_enforcement_projection_fails_closed(self):
        args = argparse.Namespace(operation="comment", execute=True)

        self.assertTrue(
            issue_tracker_ops.config_refuses_execute(
                {"consumer_action_decision": {"state": "allowed"}},
                args,
            )
        )

        payload = issue_tracker_ops.config_refusal_payload(
            "comment",
            issue_tracker_ops.RequestSpec("POST", "repos/OWNER/REPO/issues/11/comments", {"body": "x"}),
            {"consumer_action_decision": {"state": "allowed"}},
        )

        self.assertEqual(
            payload["error"]["message"],
            "Issue Tracker Ops Config did not authorize execute: "
            "missing or malformed consumer_enforcement_projection",
        )

    def test_execute_config_with_malformed_decision_state_fails_closed(self):
        args = argparse.Namespace(operation="comment", execute=True)
        config = {
            "consumer_action_decision": {"state": ["allowed"]},
            "consumer_enforcement_projection": {"adapter_action": "allow"},
        }

        self.assertTrue(issue_tracker_ops.config_refuses_execute(config, args))
        payload = issue_tracker_ops.config_refusal_payload(
            "comment",
            issue_tracker_ops.RequestSpec("POST", "repos/OWNER/REPO/issues/11/comments", {"body": "x"}),
            config,
        )

        self.assertEqual(payload["error"]["state"], "unknown")
        self.assertEqual(
            payload["error"]["message"],
            "Issue Tracker Ops Config did not authorize execute: "
            "consumer action decision did not authorize execute",
        )

    def test_execute_config_with_allowed_decision_but_missing_usable_safety_evidence_fails_closed(self):
        args = argparse.Namespace(operation="comment", execute=True)
        config = {
            "effective_config": {"safety_status": "unsafe"},
            "consumer_action_decision": {"state": "allowed"},
            "consumer_enforcement_projection": {
                "surface": "issue_tracker_ops.github_api_mutation_preflight",
                "mutation_requested": True,
                "adapter_action": "allow",
                "effective_config": {"safety_status": "usable"},
            },
        }

        self.assertTrue(issue_tracker_ops.config_refuses_execute(config, args))

        payload = issue_tracker_ops.config_refusal_payload(
            "comment",
            issue_tracker_ops.RequestSpec("POST", "repos/OWNER/REPO/issues/11/comments", {"body": "x"}),
            config,
        )

        self.assertEqual(payload["error"]["state"], "allowed")
        self.assertEqual(
            payload["error"]["message"],
            "Issue Tracker Ops Config did not authorize execute: "
            "effective Config safety status did not authorize execute",
        )

    def test_execute_config_with_allowed_decision_but_projection_safety_not_usable_fails_closed(self):
        args = argparse.Namespace(operation="comment", execute=True)
        for projection_effective_config in ({"safety_status": "unsafe"}, {}):
            with self.subTest(projection_effective_config=projection_effective_config):
                config = {
                    "effective_config": {"safety_status": "usable"},
                    "consumer_action_decision": {"state": "allowed"},
                    "consumer_enforcement_projection": {
                        "surface": "issue_tracker_ops.github_api_mutation_preflight",
                        "mutation_requested": True,
                        "adapter_action": "allow",
                        "effective_config": projection_effective_config,
                    },
                }

                self.assertTrue(issue_tracker_ops.config_refuses_execute(config, args))

                payload = issue_tracker_ops.config_refusal_payload(
                    "comment",
                    issue_tracker_ops.RequestSpec("POST", "repos/OWNER/REPO/issues/11/comments", {"body": "x"}),
                    config,
                )

                self.assertEqual(payload["error"]["state"], "allowed")
                self.assertEqual(
                    payload["error"]["message"],
                    "Issue Tracker Ops Config did not authorize execute: "
                    "effective Config safety status did not authorize execute",
                )

    def test_execute_config_with_allowed_decision_but_malformed_projection_surface_fails_closed(self):
        args = argparse.Namespace(operation="comment", execute=True)
        config = {
            "effective_config": {"safety_status": "usable"},
            "consumer_action_decision": {"state": "allowed"},
            "consumer_enforcement_projection": {
                "surface": "other.surface",
                "mutation_requested": True,
                "adapter_action": "allow",
                "effective_config": {"safety_status": "usable"},
            },
        }

        self.assertTrue(issue_tracker_ops.config_refuses_execute(config, args))

        payload = issue_tracker_ops.config_refusal_payload(
            "comment",
            issue_tracker_ops.RequestSpec("POST", "repos/OWNER/REPO/issues/11/comments", {"body": "x"}),
            config,
        )

        self.assertEqual(payload["error"]["state"], "allowed")
        self.assertEqual(
            payload["error"]["message"],
            "Issue Tracker Ops Config did not authorize execute: "
            "consumer_enforcement_projection did not identify live mutation preflight",
        )

    def test_enforcement_projection_with_malformed_decision_state_blocks(self):
        args = argparse.Namespace(operation="comment", execute=True)

        projection = issue_tracker_ops.issue_tracker_ops_enforcement_projection(
            args,
            {
                "effective_config": {"safety_status": "usable"},
                "consumer_action_decision": {"state": ["allowed"]},
            },
        )

        self.assertEqual(projection["adapter_action"], "block")
        self.assertEqual(projection["decision_state"], "unknown")

    def test_execute_error_omits_resolved_when_no_resolution_occurred(self):
        gh = FakeGh(
            [
                subprocess.CompletedProcess(["gh"], 0, stdout="[]", stderr=""),
                subprocess.CompletedProcess(["gh"], 1, stdout="", stderr="boom"),
            ]
        )

        exit_code, stdout, stderr = self.run_cli(
            [
                "comment",
                "--repo",
                "OWNER/REPO",
                "--issue-number",
                "11",
                "--body",
                "Validation note",
                "--mutation-policy-ref",
                "issue-17-approved-plan",
                "--execute",
            ],
            gh=gh,
        )

        self.assertEqual(exit_code, 1)
        self.assertEqual(stderr, "")
        payload = json.loads(stdout)
        self.assertEqual(payload["mode"], "execute")
        self.assertEqual(payload["operation"], "comment")
        self.assertEqual(payload["error"], {"returncode": 1, "stderr": "boom", "class": "unknown"})
        self.assertEqual(payload["failure"]["class"], "unknown")
        self.assertNotIn("resolved", payload)

    def test_execute_success_includes_empty_resolved_when_provided(self):
        gh = FakeGh([subprocess.CompletedProcess(["gh"], 0, stdout="{}", stderr="")])
        stdout = io.StringIO()
        stderr = io.StringIO()

        exit_code = issue_tracker_ops.execute_request(
            "dependency-op",
            issue_tracker_ops.RequestSpec("GET", "repos/OWNER/REPO/issues/11"),
            args=argparse.Namespace(api_version="2026-03-10"),
            gh=gh,
            stdout=stdout,
            stderr=stderr,
            resolved={},
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(stderr.getvalue(), "")
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["resolved"], {})

    def test_add_blocked_by_issue_number_resolves_issue_id_before_posting(self):
        gh = FakeGh(
            [
                subprocess.CompletedProcess(["gh"], 0, stdout='{"id": 98765}', stderr=""),
                subprocess.CompletedProcess(["gh"], 0, stdout="[]", stderr=""),
                subprocess.CompletedProcess(["gh"], 0, stdout='{"number": 11}', stderr=""),
            ]
        )

        exit_code, stdout, stderr = self.run_cli(
            [
                "add-blocked-by",
                "--repo",
                "OWNER/REPO",
                "--issue-number",
                "10",
                "--blocking-issue-number",
                "11",
                "--mutation-policy-ref",
                "issue-17-approved-plan",
                "--execute",
            ],
            gh=gh,
        )

        self.assertEqual(exit_code, 0, stderr)
        self.assertEqual(len(gh.calls), 3)
        get_args, get_input = gh.calls[0]
        preflight_args, preflight_input = gh.calls[1]
        post_args, post_input = gh.calls[2]
        self.assertEqual(get_args[:5], ["gh", "api", "-X", "GET", "repos/OWNER/REPO/issues/11"])
        self.assertIsNone(get_input)
        self.assertEqual(preflight_args[:5], ["gh", "api", "-X", "GET", "repos/OWNER/REPO/issues/10/dependencies/blocked_by"])
        self.assertIsNone(preflight_input)
        self.assertEqual(
            post_args[:5],
            ["gh", "api", "-X", "POST", "repos/OWNER/REPO/issues/10/dependencies/blocked_by"],
        )
        self.assertEqual(json.loads(post_input), {"issue_id": 98765})
        payload = json.loads(stdout)
        self.assertEqual(payload["operation"], "add-blocked-by")
        self.assertEqual(payload["resolved"]["blocking_issue_id"], 98765)

    def test_dependency_dry_run_with_issue_number_shows_resolution_step(self):
        gh = FakeGh()

        exit_code, stdout, stderr = self.run_cli(
            [
                "add-blocked-by",
                "--repo",
                "OWNER/REPO",
                "--issue-number",
                "10",
                "--blocking-issue-number",
                "11",
            ],
            gh=gh,
        )

        self.assertEqual(exit_code, 0, stderr)
        self.assertEqual(gh.calls, [])
        payload = json.loads(stdout)
        self.assertEqual(payload["mode"], "dry-run")
        self.assertTrue(payload["policy"]["network_requires_execute"])
        self.assertNotIn("mutation_requires_execute", payload["policy"])
        self.assertEqual(
            payload["steps"],
            [
                {
                    "method": "GET",
                    "endpoint": "repos/OWNER/REPO/issues/11",
                    "jq": ".id",
                },
                {
                    "method": "POST",
                    "endpoint": "repos/OWNER/REPO/issues/10/dependencies/blocked_by",
                    "body": {"issue_id": "<resolved from issue #11>"},
                },
            ],
        )

    def test_remove_blocked_by_issue_id_dry_run_previews_delete(self):
        gh = FakeGh()

        exit_code, stdout, stderr = self.run_cli(
            [
                "remove-blocked-by",
                "--repo",
                "OWNER/REPO",
                "--issue-number",
                "10",
                "--blocking-issue-id",
                "98765",
            ],
            gh=gh,
        )

        self.assertEqual(exit_code, 0, stderr)
        self.assertEqual(gh.calls, [])
        payload = json.loads(stdout)
        self.assertEqual(payload["mode"], "dry-run")
        self.assertTrue(payload["policy"]["network_requires_execute"])
        self.assertEqual(payload["request"]["method"], "DELETE")
        self.assertEqual(
            payload["request"]["endpoint"],
            "repos/OWNER/REPO/issues/10/dependencies/blocked_by/98765",
        )

    def test_remove_blocked_by_issue_number_resolves_issue_id_before_deleting(self):
        gh = FakeGh(
            [
                subprocess.CompletedProcess(["gh"], 0, stdout='{"id": 98765}', stderr=""),
                subprocess.CompletedProcess(["gh"], 0, stdout='[{"id": 98765, "number": 11}]', stderr=""),
                subprocess.CompletedProcess(["gh"], 0, stdout="{}", stderr=""),
            ]
        )

        exit_code, stdout, stderr = self.run_cli(
            [
                "remove-blocked-by",
                "--repo",
                "OWNER/REPO",
                "--issue-number",
                "10",
                "--blocking-issue-number",
                "11",
                "--mutation-policy-ref",
                "issue-17-approved-plan",
                "--execute",
            ],
            gh=gh,
        )

        self.assertEqual(exit_code, 0, stderr)
        self.assertEqual(len(gh.calls), 3)
        get_args, get_input = gh.calls[0]
        preflight_args, preflight_input = gh.calls[1]
        delete_args, delete_input = gh.calls[2]
        self.assertEqual(get_args[:5], ["gh", "api", "-X", "GET", "repos/OWNER/REPO/issues/11"])
        self.assertIsNone(get_input)
        self.assertEqual(preflight_args[:5], ["gh", "api", "-X", "GET", "repos/OWNER/REPO/issues/10/dependencies/blocked_by"])
        self.assertIsNone(preflight_input)
        self.assertEqual(
            delete_args[:5],
            ["gh", "api", "-X", "DELETE", "repos/OWNER/REPO/issues/10/dependencies/blocked_by/98765"],
        )
        self.assertIsNone(delete_input)
        payload = json.loads(stdout)
        self.assertEqual(payload["operation"], "remove-blocked-by")
        self.assertEqual(payload["resolved"]["blocking_issue_id"], 98765)

    def test_remove_blocked_by_fails_closed_on_unexpected_dependency_preflight_response(self):
        gh = FakeGh(
            [
                subprocess.CompletedProcess(["gh"], 0, stdout='{"id": 98765}', stderr=""),
                subprocess.CompletedProcess(["gh"], 0, stdout='{"message": "unexpected"}', stderr=""),
            ]
        )

        exit_code, stdout, stderr = self.run_cli(
            [
                "remove-blocked-by",
                "--repo",
                "OWNER/REPO",
                "--issue-number",
                "10",
                "--blocking-issue-number",
                "11",
                "--mutation-policy-ref",
                "issue-17-approved-plan",
                "--execute",
            ],
            gh=gh,
        )

        self.assertEqual(exit_code, 1)
        self.assertEqual(stderr, "")
        self.assertEqual(len(gh.calls), 2)
        payload = json.loads(stdout)
        self.assertEqual(payload["error"]["code"], "preflight_response_invalid")
        self.assertEqual(payload["resolved"]["blocking_issue_id"], 98765)
        preflight_args, _ = gh.calls[1]
        self.assertIn("--paginate", preflight_args)
        self.assertIn("--slurp", preflight_args)

    def test_update_issue_execute_skips_when_existing_issue_matches_patch(self):
        gh = FakeGh(
            [
                subprocess.CompletedProcess(
                    ["gh"],
                    0,
                    stdout=json.dumps(
                        {
                            "id": 44,
                            "number": 11,
                            "html_url": "https://github.com/OWNER/REPO/issues/11",
                            "title": "Same title",
                            "body": "Same body",
                            "state": "open",
                            "labels": [{"name": "ready-for-agent"}],
                            "assignees": [{"login": "nisavid"}],
                        }
                    ),
                    stderr="",
                )
            ]
        )

        exit_code, stdout, stderr = self.run_cli(
            [
                "update-issue",
                "--repo",
                "OWNER/REPO",
                "--issue-number",
                "11",
                "--title",
                "Same title",
                "--body",
                "Same body",
                "--label",
                "ready-for-agent",
                "--assignee",
                "nisavid",
                "--mutation-policy-ref",
                "issue-17-approved-plan",
                "--idempotency-key",
                "update-same-fields",
                "--execute",
            ],
            gh=gh,
        )

        self.assertEqual(exit_code, 0, stderr)
        self.assertEqual(len(gh.calls), 1)
        payload = json.loads(stdout)
        self.assertEqual(payload["result"]["status"], "idempotent_skip")
        self.assertEqual(payload["result"]["reason"], "issue already matches requested fields")
        self.assertEqual(payload["result"]["existing"]["number"], 11)
        self.assertEqual(payload["idempotency_key"], "update-same-fields")

    def test_add_blocked_by_execute_skips_when_relation_already_exists(self):
        gh = FakeGh(
            [
                subprocess.CompletedProcess(["gh"], 0, stdout='{"id": 98765}', stderr=""),
                subprocess.CompletedProcess(["gh"], 0, stdout='[{"id": 98765, "number": 11}]', stderr=""),
            ]
        )

        exit_code, stdout, stderr = self.run_cli(
            [
                "add-blocked-by",
                "--repo",
                "OWNER/REPO",
                "--issue-number",
                "10",
                "--blocking-issue-number",
                "11",
                "--mutation-policy-ref",
                "issue-17-approved-plan",
                "--execute",
            ],
            gh=gh,
        )

        self.assertEqual(exit_code, 0, stderr)
        self.assertEqual(len(gh.calls), 2)
        payload = json.loads(stdout)
        self.assertEqual(payload["result"]["status"], "idempotent_skip")
        self.assertEqual(payload["result"]["reason"], "blocked-by relation already exists")

    def test_list_blocking_dry_run_uses_outgoing_dependency_relation(self):
        gh = FakeGh()

        exit_code, stdout, stderr = self.run_cli(
            [
                "list-blocking",
                "--repo",
                "OWNER/REPO",
                "--issue-number",
                "10",
            ],
            gh=gh,
        )

        self.assertEqual(exit_code, 0, stderr)
        self.assertEqual(gh.calls, [])
        payload = json.loads(stdout)
        self.assertEqual(payload["mode"], "dry-run")
        self.assertTrue(payload["policy"]["network_requires_execute"])
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["endpoint"], "repos/OWNER/REPO/issues/10/dependencies/blocking")

    def test_update_issue_rejects_empty_patch_without_calling_gh(self):
        gh = FakeGh()

        exit_code, stdout, stderr = self.run_cli(
            [
                "update-issue",
                "--repo",
                "OWNER/REPO",
                "--issue-number",
                "11",
            ],
            gh=gh,
        )

        self.assertEqual(exit_code, 2)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "update-issue requires at least one field to update\n")
        self.assertNotIn("Traceback", stderr)
        self.assertEqual(gh.calls, [])

    def test_update_issue_rejects_state_reason_without_state(self):
        gh = FakeGh()

        exit_code, stdout, stderr = self.run_cli(
            [
                "update-issue",
                "--repo",
                "OWNER/REPO",
                "--issue-number",
                "11",
                "--state-reason",
                "completed",
            ],
            gh=gh,
        )

        self.assertEqual(exit_code, 2)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "`--state-reason` requires `--state`\n")
        self.assertNotIn("Traceback", stderr)
        self.assertEqual(gh.calls, [])

    def test_numeric_issue_flags_reject_non_positive_values_without_calling_gh(self):
        cases = [
            [
                "update-issue",
                "--repo",
                "OWNER/REPO",
                "--issue-number",
                "0",
                "--title",
                "Title",
            ],
            [
                "comment",
                "--repo",
                "OWNER/REPO",
                "--issue-number",
                "-1",
                "--body",
                "Body",
            ],
            [
                "add-blocked-by",
                "--repo",
                "OWNER/REPO",
                "--issue-number",
                "10",
                "--blocking-issue-id",
                "0",
            ],
            [
                "add-blocked-by",
                "--repo",
                "OWNER/REPO",
                "--issue-number",
                "10",
                "--blocking-issue-number",
                "-1",
            ],
            [
                "remove-blocked-by",
                "--repo",
                "OWNER/REPO",
                "--issue-number",
                "0",
                "--blocking-issue-id",
                "1",
            ],
            [
                "remove-blocked-by",
                "--repo",
                "OWNER/REPO",
                "--issue-number",
                "10",
                "--blocking-issue-number",
                "0",
            ],
            [
                "list-blocked-by",
                "--repo",
                "OWNER/REPO",
                "--issue-number",
                "0",
            ],
            [
                "list-blocking",
                "--repo",
                "OWNER/REPO",
                "--issue-number",
                "-1",
            ],
        ]
        for argv in cases:
            with self.subTest(argv=argv):
                gh = FakeGh()

                exit_code, stdout, stderr = self.run_cli(argv, gh=gh)

                self.assertEqual(exit_code, 2)
                self.assertEqual(stdout, "")
                self.assertIn("is not a positive integer", stderr)
                self.assertNotIn("Traceback", stderr)
                self.assertEqual(gh.calls, [])

    def test_parse_errors_use_injected_stderr_without_calling_gh(self):
        gh = FakeGh()

        exit_code, stdout, stderr = self.run_cli(
            [
                "comment",
                "--repo",
                "OWNER/REPO",
                "--issue-number",
                "not-a-number",
                "--body",
                "Body",
            ],
            gh=gh,
        )

        self.assertEqual(exit_code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("argument --issue-number", stderr)
        self.assertIn("is not a positive integer", stderr)
        self.assertNotIn("Traceback", stderr)
        self.assertEqual(gh.calls, [])

    def test_help_uses_injected_stdout_and_returns_zero(self):
        gh = FakeGh()

        exit_code, stdout, stderr = self.run_cli(["--help"], gh=gh)

        self.assertEqual(exit_code, 0)
        self.assertIn("GitHub Issues adapter MVP", stdout)
        self.assertEqual(stderr, "")
        self.assertEqual(gh.calls, [])

    def test_body_file_missing_exits_usage_error_without_calling_gh(self):
        gh = FakeGh()
        with tempfile.TemporaryDirectory() as tmp:
            body_file = f"{tmp}/missing.md"

            exit_code, stdout, stderr = self.run_cli(
                [
                    "comment",
                    "--repo",
                    "OWNER/REPO",
                    "--issue-number",
                    "11",
                    "--body-file",
                    body_file,
                ],
                gh=gh,
            )

        self.assertEqual(exit_code, 2)
        self.assertEqual(stdout, "")
        self.assertTrue(stderr.startswith("could not read --body-file "), stderr)
        self.assertIn(repr(body_file), stderr)
        self.assertTrue(stderr.endswith("\n"), stderr)
        self.assertNotIn("Traceback", stderr)
        self.assertEqual(gh.calls, [])

    def test_body_file_directory_exits_usage_error_without_calling_gh(self):
        gh = FakeGh()
        with tempfile.TemporaryDirectory() as body_file:
            exit_code, stdout, stderr = self.run_cli(
                [
                    "comment",
                    "--repo",
                    "OWNER/REPO",
                    "--issue-number",
                    "11",
                    "--body-file",
                    body_file,
                ],
                gh=gh,
            )

        self.assertEqual(exit_code, 2)
        self.assertEqual(stdout, "")
        self.assertTrue(stderr.startswith("could not read --body-file "), stderr)
        self.assertIn(repr(body_file), stderr)
        self.assertTrue(stderr.endswith("\n"), stderr)
        self.assertNotIn("Traceback", stderr)
        self.assertEqual(gh.calls, [])

    def test_default_gh_missing_executable_exits_usage_error(self):
        stdout = io.StringIO()
        stderr = io.StringIO()

        with mock.patch(
            "tools.issue_tracker_ops.subprocess.run",
            side_effect=FileNotFoundError(2, "No such file or directory", "gh"),
        ):
            exit_code = issue_tracker_ops.run(
                [
                    "comment",
                    "--repo",
                    "OWNER/REPO",
                    "--issue-number",
                    "11",
                    "--body",
                    "Validation note",
                    "--mutation-policy-ref",
                    "issue-17-approved-plan",
                    "--execute",
                ],
                stdout=stdout,
                stderr=stderr,
            )

        self.assertEqual(exit_code, 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("could not run gh: No such file or directory", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())

    def test_compact_request_preserves_zero_values(self):
        request = issue_tracker_ops.RequestSpec("GET", "repos/OWNER/REPO/issues/0", jq=0)

        self.assertEqual(
            issue_tracker_ops.compact_request(request),
            {
                "method": "GET",
                "endpoint": "repos/OWNER/REPO/issues/0",
                "jq": 0,
            },
        )

    def test_gh_api_args_preserves_falsy_jq_values(self):
        request = issue_tracker_ops.RequestSpec("GET", "repos/OWNER/REPO/issues/1", jq="")

        args = issue_tracker_ops.gh_api_args(request, api_version="2026-03-10")

        self.assertIn("--jq", args)
        self.assertEqual(args[args.index("--jq") + 1], "")

    def test_execute_output_summarizes_issue_response(self):
        gh = FakeGh(
            [
                subprocess.CompletedProcess(
                    ["gh"],
                    0,
                    stdout="[]",
                    stderr="",
                ),
                subprocess.CompletedProcess(
                    ["gh"],
                    0,
                    stdout=json.dumps(
                        {
                            "id": 44,
                            "number": 11,
                            "html_url": "https://github.com/OWNER/REPO/issues/11",
                            "title": "Issue title",
                            "state": "open",
                            "repository": {"permissions": {"admin": True}},
                        }
                    ),
                    stderr="",
                )
            ]
        )

        exit_code, stdout, stderr = self.run_cli(
            [
                "comment",
                "--repo",
                "OWNER/REPO",
                "--issue-number",
                "11",
                "--body",
                "Validation note",
                "--mutation-policy-ref",
                "issue-17-approved-plan",
                "--execute",
            ],
            gh=gh,
        )

        self.assertEqual(exit_code, 0, stderr)
        payload = json.loads(stdout)
        self.assertEqual(
            payload["result"],
            {
                "id": 44,
                "number": 11,
                "html_url": "https://github.com/OWNER/REPO/issues/11",
                "title": "Issue title",
                "state": "open",
            },
        )

    def test_execute_output_summarizes_issue_lists(self):
        first_page = {
            "id": 44,
            "number": 11,
            "html_url": "https://github.com/OWNER/REPO/issues/11",
            "title": "Blocking issue",
            "state": "open",
            "repository": {"permissions": {"admin": True}},
        }
        second_page = {
            "id": 45,
            "number": 12,
            "html_url": "https://github.com/OWNER/REPO/issues/12",
            "title": "Another blocker",
            "state": "closed",
            "repository": {"permissions": {"admin": False}},
        }
        gh = FakeGh(
            [
                subprocess.CompletedProcess(
                    ["gh"],
                    0,
                    stdout=json.dumps([[first_page], [second_page]]),
                    stderr="",
                )
            ]
        )

        exit_code, stdout, stderr = self.run_cli(
            [
                "list-blocked-by",
                "--repo",
                "OWNER/REPO",
                "--issue-number",
                "10",
                "--paginate",
                "--execute",
            ],
            gh=gh,
        )

        self.assertEqual(exit_code, 0, stderr)
        args, input_text = gh.calls[0]
        self.assertIn("--paginate", args)
        self.assertIn("--slurp", args)
        self.assertIsNone(input_text)
        payload = json.loads(stdout)
        self.assertEqual(
            payload["result"],
            [
                {
                    "id": 44,
                    "number": 11,
                    "html_url": "https://github.com/OWNER/REPO/issues/11",
                    "title": "Blocking issue",
                    "state": "open",
                },
                {
                    "id": 45,
                    "number": 12,
                    "html_url": "https://github.com/OWNER/REPO/issues/12",
                    "title": "Another blocker",
                    "state": "closed",
                },
            ],
        )

    def test_audit_labels_dry_run_exposes_axis_policy_without_calling_gh(self):
        gh = FakeGh()

        exit_code, stdout, stderr = self.run_cli(
            [
                "audit-labels",
                "--repo",
                "OWNER/REPO",
            ],
            gh=gh,
        )

        self.assertEqual(exit_code, 0, stderr)
        self.assertEqual(gh.calls, [])
        payload = json.loads(stdout)
        self.assertEqual(payload["mode"], "dry-run")
        self.assertEqual(payload["operation"], "audit-labels")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["endpoint"], "repos/OWNER/REPO/issues?state=open&per_page=100")
        self.assertTrue(payload["request"]["paginate"])
        self.assertEqual(payload["label_axes"]["category"]["cardinality"], "exactly_one")
        self.assertEqual(payload["label_axes"]["state"]["labels"], ["needs-triage", "needs-info", "ready-for-agent", "ready-for-human", "wontfix"])

    def test_audit_labels_execute_reports_axis_findings_and_skips_prs(self):
        issues = [
            {
                "number": 1,
                "html_url": "https://github.com/OWNER/REPO/issues/1",
                "title": "Unlabeled issue",
                "labels": [],
            },
            {
                "number": 2,
                "html_url": "https://github.com/OWNER/REPO/issues/2",
                "title": "Clean issue",
                "labels": [{"name": "bug"}, {"name": "ready-for-agent"}, {"name": "depth:L1"}],
            },
            {
                "number": 3,
                "html_url": "https://github.com/OWNER/REPO/issues/3",
                "title": "Conflicting issue",
                "labels": [
                    {"name": "bug"},
                    {"name": "enhancement"},
                    {"name": "needs-triage"},
                    {"name": "ready-for-agent"},
                    {"name": "depth:L1"},
                    {"name": "depth:L2"},
                    {"name": "kind:design"},
                    {"name": "kind:implementation"},
                ],
            },
            {
                "number": 4,
                "html_url": "https://github.com/OWNER/REPO/pull/4",
                "title": "Pull request",
                "labels": [],
                "pull_request": {},
            },
        ]
        gh = FakeGh([subprocess.CompletedProcess(["gh"], 0, stdout=json.dumps([issues]), stderr="")])

        exit_code, stdout, stderr = self.run_cli(
            [
                "audit-labels",
                "--repo",
                "OWNER/REPO",
                "--execute",
            ],
            gh=gh,
        )

        self.assertEqual(exit_code, 0, stderr)
        args, input_text = gh.calls[0]
        self.assertIn("--paginate", args)
        self.assertIsNone(input_text)
        payload = json.loads(stdout)
        self.assertEqual(payload["operation"], "audit-labels")
        self.assertEqual(
            payload["result"]["summary"],
            {
                "checked_issues": 3,
                "issues_with_findings": 2,
                "errors": 5,
                "warnings": 1,
            },
        )
        self.assertEqual([issue["number"] for issue in payload["result"]["issues"]], [1, 3])
        self.assertEqual(
            payload["result"]["issues"][0]["findings"],
            [
                {
                    "axis": "category",
                    "code": "missing",
                    "message": "Expected exactly one category label.",
                    "severity": "error",
                },
                {
                    "axis": "state",
                    "code": "missing",
                    "message": "Expected exactly one state label.",
                    "severity": "error",
                },
            ],
        )
        conflicting_codes = [(finding["axis"], finding["code"], finding["severity"]) for finding in payload["result"]["issues"][1]["findings"]]
        self.assertEqual(
            conflicting_codes,
            [
                ("category", "conflict", "error"),
                ("state", "conflict", "error"),
                ("depth", "conflict", "error"),
                ("work_kind", "multi_primary", "warning"),
            ],
        )

    def test_audit_labels_execute_fails_closed_on_unexpected_response_shape(self):
        cases = [
            (
                '{"message": "not a list"}',
                "",
                {"returncode": 1, "stderr": "unexpected GitHub issue list response"},
                "",
            ),
            (
                '["not an issue object"]',
                "",
                {"returncode": 1, "stderr": "unexpected GitHub issue list response"},
                "",
            ),
            (
                '{"message": "not a list"}',
                "gh warning\n",
                {
                    "returncode": 1,
                    "stderr": "unexpected GitHub issue list response",
                    "gh_stderr": "gh warning",
                },
                "gh warning\n",
            ),
        ]

        for gh_stdout, gh_stderr, expected_error, expected_stderr in cases:
            with self.subTest(gh_stdout=gh_stdout, gh_stderr=gh_stderr):
                gh = FakeGh(
                    [subprocess.CompletedProcess(["gh"], 0, stdout=gh_stdout, stderr=gh_stderr)]
                )

                exit_code, stdout, stderr = self.run_cli(
                    [
                        "audit-labels",
                        "--repo",
                        "OWNER/REPO",
                        "--execute",
                    ],
                    gh=gh,
                )

                self.assertEqual(exit_code, 1)
                self.assertEqual(stderr, expected_stderr)
                payload = json.loads(stdout)
                self.assertEqual(payload["mode"], "execute")
                self.assertEqual(payload["operation"], "audit-labels")
                self.assertEqual(payload["error"], expected_error)


if __name__ == "__main__":
    unittest.main()
