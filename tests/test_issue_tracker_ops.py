import io
import json
import subprocess
import unittest

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
        gh = FakeGh(
            [
                subprocess.CompletedProcess(
                    ["gh"],
                    0,
                    stdout=json.dumps(
                        [
                            {
                                "id": 44,
                                "number": 11,
                                "html_url": "https://github.com/OWNER/REPO/issues/11",
                                "title": "Blocking issue",
                                "state": "open",
                                "repository": {"permissions": {"admin": True}},
                            }
                        ]
                    ),
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
                "--execute",
            ],
            gh=gh,
        )

        self.assertEqual(exit_code, 0, stderr)
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
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
