import argparse
import io
import json
import subprocess
import tempfile
import unittest
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
        gh = FakeGh([subprocess.CompletedProcess(["gh"], 0, stdout='{"id": 44}', stderr="")])

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

        self.assertEqual(exit_code, 0, stderr)
        self.assertEqual(len(gh.calls), 1)
        args, input_text = gh.calls[0]
        self.assertEqual(args[:5], ["gh", "api", "-X", "POST", "repos/OWNER/REPO/issues/11/comments"])
        self.assertEqual(json.loads(input_text), {"body": "Validation note"})
        payload = json.loads(stdout)
        self.assertEqual(payload["mode"], "execute")
        self.assertEqual(payload["operation"], "comment")
        self.assertEqual(payload["result"], {"id": 44})

    def test_execute_error_omits_resolved_when_no_resolution_occurred(self):
        gh = FakeGh([subprocess.CompletedProcess(["gh"], 1, stdout="", stderr="boom")])

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
        payload = json.loads(stdout)
        self.assertEqual(payload["mode"], "execute")
        self.assertEqual(payload["operation"], "comment")
        self.assertEqual(payload["error"], {"returncode": 1, "stderr": "boom"})
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
                "--execute",
            ],
            gh=gh,
        )

        self.assertEqual(exit_code, 0, stderr)
        self.assertEqual(len(gh.calls), 2)
        get_args, get_input = gh.calls[0]
        post_args, post_input = gh.calls[1]
        self.assertEqual(get_args[:5], ["gh", "api", "-X", "GET", "repos/OWNER/REPO/issues/11"])
        self.assertIsNone(get_input)
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
                "--execute",
            ],
            gh=gh,
        )

        self.assertEqual(exit_code, 0, stderr)
        self.assertEqual(len(gh.calls), 2)
        get_args, get_input = gh.calls[0]
        delete_args, delete_input = gh.calls[1]
        self.assertEqual(get_args[:5], ["gh", "api", "-X", "GET", "repos/OWNER/REPO/issues/11"])
        self.assertIsNone(get_input)
        self.assertEqual(
            delete_args[:5],
            ["gh", "api", "-X", "DELETE", "repos/OWNER/REPO/issues/10/dependencies/blocked_by/98765"],
        )
        self.assertIsNone(delete_input)
        payload = json.loads(stdout)
        self.assertEqual(payload["operation"], "remove-blocked-by")
        self.assertEqual(payload["resolved"]["blocking_issue_id"], 98765)

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
            '{"message": "not a list"}',
            '["not an issue object"]',
        ]

        for gh_stdout in cases:
            with self.subTest(gh_stdout=gh_stdout):
                gh = FakeGh([subprocess.CompletedProcess(["gh"], 0, stdout=gh_stdout, stderr="")])

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
                self.assertEqual(stderr, "")
                payload = json.loads(stdout)
                self.assertEqual(payload["mode"], "execute")
                self.assertEqual(payload["operation"], "audit-labels")
                self.assertEqual(
                    payload["error"],
                    {
                        "returncode": 1,
                        "stderr": "unexpected GitHub issue list response",
                    },
                )


if __name__ == "__main__":
    unittest.main()
