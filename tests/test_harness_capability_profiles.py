import json
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MANAGER = REPO_ROOT / "tools/harness_capability_profiles.py"
AGGREGATE_FIXTURE = """
checked_at = "2026-05-03T09:25:05-04:00"

[harness.codex]
display_name = "Codex"
checked_version = "0.128.0 stable"
version_basis = "GitHub releases for openai/codex, plus first-party OpenAI Codex docs."
evidence = "source-supported"
sources = [{ url = "https://developers.openai.com/codex/skills", kind = "first_party", claim_scope = "skill support" }]
uncertainty = "Fixture uncertainty."
components = ["skills", "app-server APIs"]
summary_scheduling = "App automations and external schedulers around codex exec."
scheduling = "Codex app automations support recurring schedules."
limitations = "Fixture limitation."
refresh_notes = "Fixture refresh note."
local_observations = ["No local Codex binary was inspected."]

[harness.claude_code]
display_name = "Claude Code"
checked_version = "2.1.126"
version_basis = "Official Claude Code changelog and docs."
evidence = "documentation-supported"
sources = [{ url = "https://code.claude.com/docs/en/skills", kind = "first_party", claim_scope = "skill support" }]
uncertainty = "Fixture uncertainty."
components = ["skills"]
summary_scheduling = "Routines."
scheduling = "Claude Code supports Routines."
limitations = "Fixture limitation."
refresh_notes = "Fixture refresh note."
local_observations = []

[harness.cursor]
display_name = "Cursor"
checked_version = "3.2"
version_basis = "Official Cursor changelog and first-party docs."
evidence = "documentation-supported"
sources = [{ url = "https://cursor.com/docs/skills", kind = "first_party", claim_scope = "skill support" }]
uncertainty = "Fixture uncertainty."
components = ["skills"]
summary_scheduling = "Cloud Agent Automations."
scheduling = "Cursor supports Automations."
limitations = "Fixture limitation."
refresh_notes = "Fixture refresh note."
local_observations = []

[harness.hermes_agent]
display_name = "Hermes Agent"
checked_version = "0.12.0"
version_basis = "GitHub release and tag-pinned docs."
evidence = "source-supported"
sources = [{ url = "https://github.com/NousResearch/hermes-agent/releases/tag/v2026.4.30", kind = "first_party", claim_scope = "release version" }]
uncertainty = "Fixture uncertainty."
components = ["skills"]
summary_scheduling = "Cron jobs."
scheduling = "Hermes supports cron jobs."
limitations = "Fixture limitation."
refresh_notes = "Fixture refresh note."
local_observations = []

[harness.opencode]
display_name = "OpenCode"
checked_version = "1.14.33"
version_basis = "GitHub release and first-party docs."
evidence = "source-supported"
sources = [{ url = "https://opencode.ai/docs/skills/", kind = "first_party", claim_scope = "skill support" }]
uncertainty = "Fixture uncertainty."
components = ["skills"]
summary_scheduling = "External schedulers."
scheduling = "OpenCode can run under external schedulers."
limitations = "Fixture limitation."
refresh_notes = "Fixture refresh note."
local_observations = []

[harness.openclaw]
display_name = "OpenClaw"
checked_version = "2026.5.2"
version_basis = "GitHub release and tag-pinned source/docs."
evidence = "source-supported"
sources = [{ url = "https://github.com/openclaw/openclaw/releases/tag/v2026.5.2", kind = "first_party", claim_scope = "release version" }]
uncertainty = "Fixture uncertainty."
components = ["skills"]
summary_scheduling = "Cron jobs and heartbeat turns."
scheduling = "OpenClaw supports cron jobs."
limitations = "Fixture limitation."
refresh_notes = "Fixture refresh note."
local_observations = []
"""


def write_research_outputs_fixture(root: Path) -> None:
    research_dir = root / "specs/vanilla-harness-capability-profiles/research-notes"
    research_dir.mkdir(parents=True, exist_ok=True)
    surface_lines = "\n".join(
        f"- `{family}`: source-backed fact, local observation, implementation inference, hypothesis, unsupported claim, unknown, or not-applicable."
        for family in [
            "instructions_context",
            "skills",
            "mcp_tools",
            "hooks_events",
            "plugins_bundles",
            "agent_profiles_subagents",
            "memory_context_retrieval",
            "config_settings",
            "permissions_approvals_sandboxing",
            "scheduling_automation",
            "commands_shortcuts",
            "providers_connectors",
            "runtime_modes",
            "cross_harness_import_compatibility",
            "lifecycle_reload_update",
        ]
    )
    for harness_id in ["claude_code", "codex", "cursor", "hermes_agent", "openclaw", "opencode"]:
        (research_dir / f"{harness_id}.md").write_text(
            f"""# Research Note: {harness_id}

Status: draft

## Version Basis

Checked at: 2026-05-08T12:00:00-04:00.
Version basis: fixture.

## Source Set

- [Fixture source](https://example.com/{harness_id})

## Surface Findings

{surface_lines}

## Evidence Classification

This note distinguishes source-backed facts, local observations, implementation inferences, hypotheses, unsupported claims, unknowns, and not-applicable surfaces.

## Cross-Harness Import And Compatibility

Compatibility is reviewed separately from native support.

## Memory-Like Surfaces

Memory-like behavior is reviewed without assuming a stable shared memory API.

## Schema Pressure

Fixture schema pressure.

## Analysis Angle Notes

Capability Analysis Angles and Capability State Graph alternatives were considered.

## Local Observations

No local observation.

## Major Uncertainty

Fixture uncertainty.

## Scratch Artifact Disposition

Scratch artifacts are summarized, not committed as raw project truth.
""",
            encoding="utf-8",
        )
    (root / "specs/vanilla-harness-capability-profiles/schema-pressure-report.md").write_text(
        """# Schema Pressure Report: Harness Surfaces

Status: draft

## Research Scope

Fixture scope.

## Current Schema Comparison

Fixture comparison.

## Schema Pressure Findings

| ID | Disposition | Affected harnesses | Motivating evidence | Example claim shape | Proposed validation rule | Migration impact |
| --- | --- | --- | --- | --- | --- | --- |
| SP-001 | accepted | codex | [Fixture source](https://example.com/codex) | field = value | Require fixture field. | Migration must preserve fixture. |
| SP-002 | deferred | claude_code | [Fixture source](https://example.com/claude_code) | extension = value | Defer until profile enrichment. | No current migration. |
| SP-003 | rejected | cursor | [Fixture source](https://example.com/cursor) | consumer_logic = value | Reject downstream consumer logic. | No schema migration. |
| SP-004 | needs more evidence | opencode | [Fixture source](https://example.com/opencode) | unknown = value | Keep unknown explicit. | No current migration. |

## Cross-Harness Import And Compatibility

Fixture cross-harness review.

## Memory-Like Surfaces

Fixture memory-like review.

## Analysis Angles And State Graphs

Fixture analysis angle review.

## Migration Implications

Fixture migration implications.

## Ralph Review Disposition

Latest cycle: clean.

## Scratch Artifact Disposition

Scratch artifacts are summarized, not committed as raw project truth.
""",
        encoding="utf-8",
    )


class HarnessCapabilityProfileManagerTests(unittest.TestCase):
    def write_migration_root(self, root: Path) -> None:
        docs = root / "docs"
        docs.mkdir()
        (docs / "harness-capabilities.toml").write_text(AGGREGATE_FIXTURE.strip() + "\n", encoding="utf-8")
        shutil.copyfile(REPO_ROOT / "docs/harness-capabilities.md", docs / "harness-capabilities.md")

    def write_research_outputs(self, root: Path) -> None:
        write_research_outputs_fixture(root)

    def migrate_and_summarize(self, root: Path) -> None:
        migrate = self.run_manager(root, "migrate", "--apply", "--json")
        self.assertEqual(migrate.returncode, 0, migrate.stderr)
        summarize = self.run_manager(root, "summarize", "--write", "--json")
        self.assertEqual(summarize.returncode, 0, summarize.stderr)
        self.write_research_outputs(root)

    def run_manager(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(MANAGER), "--root", str(root), *args],
            cwd=REPO_ROOT,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30,
        )

    def test_migrate_dry_run_reports_six_profile_writes_without_mutating_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_migration_root(root)

            completed = self.run_manager(root, "migrate", "--json")

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["schema"], "harness_capability_profiles.migrate_result.v1")
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["result"], "would_write")
            self.assertEqual(
                [write["path"] for write in payload["writes"]],
                [
                    "docs/harness-capabilities/vanilla/claude_code.toml",
                    "docs/harness-capabilities/vanilla/codex.toml",
                    "docs/harness-capabilities/vanilla/cursor.toml",
                    "docs/harness-capabilities/vanilla/hermes_agent.toml",
                    "docs/harness-capabilities/vanilla/openclaw.toml",
                    "docs/harness-capabilities/vanilla/opencode.toml",
                ],
            )
            self.assertFalse((root / "docs/harness-capabilities/vanilla").exists())

    def test_migrate_json_reports_missing_required_harness_without_traceback(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_migration_root(root)
            fixture_without_openclaw = AGGREGATE_FIXTURE.split("\n[harness.openclaw]\n", 1)[0]
            (root / "docs/harness-capabilities.toml").write_text(fixture_without_openclaw.strip() + "\n", encoding="utf-8")

            completed = self.run_manager(root, "migrate", "--json")

            self.assertNotEqual(completed.returncode, 0)
            self.assertEqual(completed.stderr, "")
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["result"], "failed")
            self.assertIn("aggregate catalog missing required harness: openclaw", payload["error"])

    def test_migrate_json_rejects_missing_checked_at_before_writing_profiles(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_migration_root(root)
            aggregate = root / "docs/harness-capabilities.toml"
            aggregate.write_text(aggregate.read_text(encoding="utf-8").replace('checked_at = "2026-05-03T09:25:05-04:00"\n', "", 1), encoding="utf-8")

            completed = self.run_manager(root, "migrate", "--apply", "--json")

            self.assertNotEqual(completed.returncode, 0)
            self.assertEqual(completed.stderr, "")
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["result"], "failed")
            self.assertIn("aggregate catalog missing checked_at", payload["error"])
            self.assertFalse((root / "docs/harness-capabilities/vanilla").exists())

    def test_migrate_json_validates_generated_profiles_before_writing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_migration_root(root)
            aggregate = root / "docs/harness-capabilities.toml"
            aggregate.write_text(aggregate.read_text(encoding="utf-8").replace('checked_version = "0.128.0 stable"\n', "", 1), encoding="utf-8")

            completed = self.run_manager(root, "migrate", "--apply", "--json")

            self.assertNotEqual(completed.returncode, 0)
            self.assertEqual(completed.stderr, "")
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["result"], "failed")
            self.assertIn("generated profile invalid for codex", payload["error"])
            self.assertIn("profile:codex:checked_version", payload["error"])
            self.assertFalse((root / "docs/harness-capabilities/vanilla").exists())

    def test_migrate_apply_writes_stable_profiles_and_retires_aggregate_catalog(self):
        with tempfile.TemporaryDirectory() as first_tmpdir, tempfile.TemporaryDirectory() as second_tmpdir:
            first_root = Path(first_tmpdir)
            second_root = Path(second_tmpdir)
            self.write_migration_root(first_root)
            self.write_migration_root(second_root)

            first = self.run_manager(first_root, "migrate", "--apply", "--json")
            second = self.run_manager(second_root, "migrate", "--apply", "--json")

            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(json.loads(first.stdout), json.loads(second.stdout))
            self.assertFalse((first_root / "docs/harness-capabilities.toml").exists())
            codex_profile = first_root / "docs/harness-capabilities/vanilla/codex.toml"
            with codex_profile.open("rb") as handle:
                profile = tomllib.load(handle)
            self.assertEqual(profile["schema_version"], "vanilla-harness-capability-profile.v1alpha1")
            self.assertEqual(profile["profile_kind"], "vanilla_harness_capability_profile")
            self.assertEqual(profile["harness_id"], "codex")
            self.assertEqual(profile["checked_at"], "2026-05-03T09:25:05-04:00")
            self.assertEqual(profile["display_name"], "Codex")
            self.assertIn("app-server APIs", profile["components"])
            self.assertRegex(profile["evidence"][0]["id"], r"^ev-codex-skill-support-[0-9a-f]{10}$")
            self.assertIn(
                {
                    "id": "claim-codex-skills",
                    "family": "skills",
                    "status": "supported",
                    "statement": "Source-backed evidence records skills support.",
                    "evidence_ids": [profile["evidence"][0]["id"]],
                    "applicability_scope": "vanilla harness after default installation and onboarding",
                    "capability_origin": "migrated aggregate harness catalog",
                    "migration_status": "migrated_from_aggregate",
                    "evidence_basis": "aggregate_catalog_migration",
                    "limitations": profile["limitations"],
                    "uncertainty": profile["uncertainty"],
                },
                profile["claim"],
            )

    def test_migrate_evidence_ids_do_not_depend_on_source_order(self):
        with tempfile.TemporaryDirectory() as first_tmpdir, tempfile.TemporaryDirectory() as second_tmpdir:
            first_root = Path(first_tmpdir)
            second_root = Path(second_tmpdir)
            self.write_migration_root(first_root)
            self.write_migration_root(second_root)
            original_sources = (
                'sources = [{ url = "https://developers.openai.com/codex/skills", '
                'kind = "first_party", claim_scope = "skill support" }]'
            )
            skill_source = '{ url = "https://developers.openai.com/codex/skills", kind = "first_party", claim_scope = "skill support" }'
            plugin_source = '{ url = "https://developers.openai.com/codex/plugins", kind = "first_party", claim_scope = "plugin support" }'
            first_sources = f"sources = [{skill_source}, {plugin_source}]"
            second_sources = f"sources = [{plugin_source}, {skill_source}]"
            for root, replacement in [(first_root, first_sources), (second_root, second_sources)]:
                aggregate = root / "docs/harness-capabilities.toml"
                aggregate.write_text(aggregate.read_text(encoding="utf-8").replace(original_sources, replacement, 1), encoding="utf-8")

            first = self.run_manager(first_root, "migrate", "--apply", "--json")
            second = self.run_manager(second_root, "migrate", "--apply", "--json")

            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            with (first_root / "docs/harness-capabilities/vanilla/codex.toml").open("rb") as handle:
                first_profile = tomllib.load(handle)
            with (second_root / "docs/harness-capabilities/vanilla/codex.toml").open("rb") as handle:
                second_profile = tomllib.load(handle)
            first_ids = {evidence["claim_scope"]: evidence["id"] for evidence in first_profile["evidence"]}
            second_ids = {evidence["claim_scope"]: evidence["id"] for evidence in second_profile["evidence"]}
            self.assertEqual(first_ids["skill support"], second_ids["skill support"])
            self.assertEqual(first_ids["plugin support"], second_ids["plugin support"])

    def test_validate_json_accepts_migrated_profiles_after_aggregate_retirement(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_migration_root(root)
            self.migrate_and_summarize(root)

            completed = self.run_manager(root, "validate", "--json")

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["schema"], "harness_capability_profiles.validation_result.v1")
            self.assertEqual(payload["validation"], "Vanilla Harness Capability Profile Manager Core")
            self.assertEqual(payload["result"], "passed")
            self.assertTrue(all(result["ok"] for result in payload["results"]))

    def test_validate_json_requires_research_notes_and_schema_pressure_report(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_migration_root(root)
            migrate = self.run_manager(root, "migrate", "--apply", "--json")
            self.assertEqual(migrate.returncode, 0, migrate.stderr)
            summarize = self.run_manager(root, "summarize", "--write", "--json")
            self.assertEqual(summarize.returncode, 0, summarize.stderr)

            completed = self.run_manager(root, "validate", "--json")

            self.assertNotEqual(completed.returncode, 0)
            payload = json.loads(completed.stdout)
            failures = {result["name"]: result for result in payload["results"] if not result["ok"]}
            self.assertIn("research_note:codex:path", failures)
            self.assertIn("schema_pressure:path", failures)

    def test_validate_json_rejects_incomplete_research_and_schema_pressure_rows(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_migration_root(root)
            self.migrate_and_summarize(root)
            codex_note = root / "specs/vanilla-harness-capability-profiles/research-notes/codex.md"
            codex_note.write_text(
                codex_note.read_text(encoding="utf-8").replace("## Source Set", "Source Set", 1).replace("`skills`", "`skillz`", 1),
                encoding="utf-8",
            )
            report = root / "specs/vanilla-harness-capability-profiles/schema-pressure-report.md"
            report.write_text(report.read_text(encoding="utf-8").replace("accepted", "maybe", 1), encoding="utf-8")

            completed = self.run_manager(root, "validate", "--json")

            self.assertNotEqual(completed.returncode, 0)
            payload = json.loads(completed.stdout)
            failures = {result["name"]: result for result in payload["results"] if not result["ok"]}
            self.assertIn("research_note:codex:section:source_set", failures)
            self.assertIn("research_note:codex:surface_family_coverage", failures)
            self.assertIn("schema_pressure:row:SP-001:disposition", failures)

    def test_validate_json_accepts_hyphenated_needs_more_evidence_disposition(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_migration_root(root)
            self.migrate_and_summarize(root)
            report = root / "specs/vanilla-harness-capability-profiles/schema-pressure-report.md"
            report.write_text(report.read_text(encoding="utf-8").replace("needs more evidence", "needs-more-evidence", 1), encoding="utf-8")

            completed = self.run_manager(root, "validate", "--json")

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["result"], "passed")

    def test_validate_json_accepts_extra_whitespace_in_research_note_headings(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_migration_root(root)
            self.migrate_and_summarize(root)
            codex_note = root / "specs/vanilla-harness-capability-profiles/research-notes/codex.md"
            codex_note.write_text(
                codex_note.read_text(encoding="utf-8")
                .replace("## Version Basis", "##   Version   Basis  ", 1)
                .replace("## Source Set", "##  Source   Set  ", 1)
                .replace("## Surface Findings", "## Surface   Findings  ", 1),
                encoding="utf-8",
            )

            completed = self.run_manager(root, "validate", "--json")

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["result"], "passed")

    def test_validate_json_rejects_misplaced_research_note_markers(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_migration_root(root)
            self.migrate_and_summarize(root)
            codex_note = root / "specs/vanilla-harness-capability-profiles/research-notes/codex.md"
            original = codex_note.read_text(encoding="utf-8")
            version_markers = "Checked at: 2026-05-08T12:00:00-04:00.\nVersion basis: fixture."
            source_marker = "- [Fixture source](https://example.com/codex)"
            surface_body = original.split("## Surface Findings\n\n", 1)[1].split("\n## Evidence Classification", 1)[0]
            codex_note.write_text(
                original.replace(version_markers, "No version marker here.", 1)
                .replace(source_marker, "No source URL here.", 1)
                .replace(surface_body, "No surface family matrix here.\n", 1)
                .replace(
                    "No local observation.",
                    f"No local observation.\n\n{version_markers}\n\n{source_marker}\n\n{surface_body}",
                    1,
                ),
                encoding="utf-8",
            )

            completed = self.run_manager(root, "validate", "--json")

            self.assertNotEqual(completed.returncode, 0)
            payload = json.loads(completed.stdout)
            failures = {result["name"]: result for result in payload["results"] if not result["ok"]}
            self.assertIn("research_note:codex:checked_at", failures)
            self.assertIn("research_note:codex:version_basis", failures)
            self.assertIn("research_note:codex:source_set", failures)
            self.assertIn("research_note:codex:surface_family_coverage", failures)

    def test_validate_json_rejects_malformed_schema_pressure_table_rows(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_migration_root(root)
            self.migrate_and_summarize(root)
            report = root / "specs/vanilla-harness-capability-profiles/schema-pressure-report.md"
            report.write_text(report.read_text(encoding="utf-8").replace("field = value", 'field = "left|right"', 1), encoding="utf-8")

            completed = self.run_manager(root, "validate", "--json")

            self.assertNotEqual(completed.returncode, 0)
            payload = json.loads(completed.stdout)
            failures = {result["name"]: result for result in payload["results"] if not result["ok"]}
            self.assertIn("schema_pressure:row:SP-001:table_shape", failures)

    def test_summarize_write_updates_human_catalog_to_per_harness_profiles(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_migration_root(root)
            migrate = self.run_manager(root, "migrate", "--apply", "--json")
            self.assertEqual(migrate.returncode, 0, migrate.stderr)

            completed = self.run_manager(root, "summarize", "--write", "--json")

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["result"], "wrote")
            summary = (root / "docs/harness-capabilities.md").read_text(encoding="utf-8")
            self.assertIn("The structured source of truth is `docs/harness-capabilities/vanilla/`.", summary)
            self.assertIn("| Codex |", summary)
            self.assertIn("[Codex profile](harness-capabilities/vanilla/codex.toml)", summary)
            self.assertNotIn("harness-capabilities.toml", summary)

    def test_validate_json_reports_profile_failures_with_nonzero_exit(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_migration_root(root)
            self.migrate_and_summarize(root)
            codex_profile = root / "docs/harness-capabilities/vanilla/codex.toml"
            text = codex_profile.read_text(encoding="utf-8")
            text = text.replace('schema_version = "vanilla-harness-capability-profile.v1alpha1"\n', "", 1)
            text = text.replace('checked_version = "0.128.0 stable"\n', "", 1)
            text = text.replace('evidence_category = "source-supported"', 'evidence_category = "rumor"', 1)
            text = text.replace('id = "claim-codex-mcp_tools"', 'id = "claim-codex-skills"', 1)
            text = text.replace('status = "supported"', 'status = "maybe"', 1)
            with codex_profile.open("rb") as handle:
                evidence_id = tomllib.load(handle)["evidence"][0]["id"]
            text = text.replace(f'id = "{evidence_id}"', 'id = "ev-codex-unstable"', 1)
            text = text.replace(f'evidence_ids = ["{evidence_id}"]', 'evidence_ids = ["ev-codex-missing"]', 1)
            text = text.replace('source_kind = "first_party"', 'source_kind = "local_observation"', 1)
            text = text.replace('url = "https://developers.openai.com/codex/skills"', 'url = "file:///tmp/source"', 1)
            text = text.replace('applicability_scope = "vanilla harness after default installation and onboarding"\n', "", 1)
            text = text.replace('capability_origin = "migrated aggregate harness catalog"\n', "", 1)
            text = text.replace('migration_status = "migrated_from_aggregate"\n', "", 1)
            text = text.replace('evidence_basis = "aggregate_catalog_migration"\n', "", 1)
            text = text.replace('family = "lifecycle_reload_update"', 'family = "invalid_family"', 1)
            codex_profile.write_text(text, encoding="utf-8")

            completed = self.run_manager(root, "validate", "--json")

            self.assertNotEqual(completed.returncode, 0)
            payload = json.loads(completed.stdout)
            failures = {result["name"]: result for result in payload["results"] if not result["ok"]}
            self.assertEqual(payload["result"], "failed")
            self.assertIn("profile:codex:schema_version", failures)
            self.assertIn("profile:codex:checked_version", failures)
            self.assertIn("profile:codex:evidence_category", failures)
            self.assertIn("profile:codex:evidence:0:source_kind", failures)
            self.assertIn("profile:codex:evidence:0:url", failures)
            self.assertIn("profile:codex:evidence:0:id", failures)
            self.assertIn("profile:codex:claim:claim-codex-skills", failures)
            self.assertIn("profile:codex:claim:1:status", failures)
            self.assertIn("profile:codex:claim:1:evidence_refs", failures)
            self.assertIn("profile:codex:claim:0:applicability_scope", failures)
            self.assertIn("profile:codex:claim:0:capability_origin", failures)
            self.assertIn("profile:codex:claim:0:migration_status", failures)
            self.assertIn("profile:codex:claim:0:evidence_basis", failures)
            self.assertIn("profile:codex:claim:14:family", failures)
            self.assertIn("profile:codex:surface_family_coverage", failures)

    def test_validate_rejects_missing_scope_applicability(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_migration_root(root)
            self.migrate_and_summarize(root)
            codex_profile = root / "docs/harness-capabilities/vanilla/codex.toml"
            text = codex_profile.read_text(encoding="utf-8")
            text = text.replace('applicability = "Default settings and default equipment immediately after installation and onboarding."\n', "", 1)
            codex_profile.write_text(text, encoding="utf-8")

            completed = self.run_manager(root, "validate", "--json")

            self.assertNotEqual(completed.returncode, 0)
            payload = json.loads(completed.stdout)
            failures = {result["name"] for result in payload["results"] if not result["ok"]}
            self.assertIn("profile:codex:scope:applicability", failures)

    def test_validate_rejects_summary_drift_and_retained_aggregate_truth(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_migration_root(root)
            self.migrate_and_summarize(root)
            (root / "docs/harness-capabilities.toml").write_text(AGGREGATE_FIXTURE.strip() + "\n", encoding="utf-8")
            summary = root / "docs/harness-capabilities.md"
            summary.write_text(summary.read_text(encoding="utf-8").replace("0.128.0 stable", "stale version", 1), encoding="utf-8")

            completed = self.run_manager(root, "validate", "--json")

            self.assertNotEqual(completed.returncode, 0)
            failures = {result["name"] for result in json.loads(completed.stdout)["results"] if not result["ok"]}
            self.assertIn("aggregate_catalog:retired", failures)
            self.assertIn("summary:codex:checked_version", failures)

    def test_validate_json_reports_unexpected_read_errors_without_traceback(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_migration_root(root)
            self.migrate_and_summarize(root)
            (root / "docs/harness-capabilities.md").write_bytes(b"\xff")

            completed = self.run_manager(root, "validate", "--json")

            self.assertNotEqual(completed.returncode, 0)
            self.assertEqual(completed.stderr, "")
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["result"], "failed")
            failures = {result["name"]: result for result in payload["results"] if not result["ok"]}
            self.assertIn("validate:exception", failures)
            self.assertIn("UnicodeDecodeError", failures["validate:exception"]["detail"])

    def test_summarize_json_reports_invalid_profile_toml_without_traceback(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_migration_root(root)
            self.migrate_and_summarize(root)
            (root / "docs/harness-capabilities/vanilla/codex.toml").write_text("not toml =", encoding="utf-8")

            completed = self.run_manager(root, "summarize", "--json")

            self.assertNotEqual(completed.returncode, 0)
            self.assertEqual(completed.stderr, "")
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["result"], "failed")
            self.assertIn("Expected", payload["error"])

    def test_migrate_apply_rejects_symlinked_profile_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_migration_root(root)
            outside = root / "outside"
            outside.mkdir()
            (root / "docs/harness-capabilities").symlink_to(outside, target_is_directory=True)

            completed = self.run_manager(root, "migrate", "--apply", "--json")

            self.assertNotEqual(completed.returncode, 0)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["result"], "failed")
            self.assertIn("path contains symlink", payload["error"])
            self.assertFalse((outside / "vanilla/codex.toml").exists())

    def test_validate_rejects_symlinked_profile_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_migration_root(root)
            self.migrate_and_summarize(root)
            profile = root / "docs/harness-capabilities/vanilla/codex.toml"
            outside = root / "outside-profile.toml"
            outside.write_text(profile.read_text(encoding="utf-8"), encoding="utf-8")
            profile.unlink()
            profile.symlink_to(outside)

            completed = self.run_manager(root, "validate", "--json")

            self.assertNotEqual(completed.returncode, 0)
            failures = {result["name"]: result for result in json.loads(completed.stdout)["results"] if not result["ok"]}
            self.assertEqual(failures["profile:codex:path"]["detail"], "path contains symlink")

    def test_validate_rejects_symlinked_summary_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_migration_root(root)
            self.migrate_and_summarize(root)
            summary = root / "docs/harness-capabilities.md"
            outside = root / "outside-summary.md"
            outside.write_text(summary.read_text(encoding="utf-8"), encoding="utf-8")
            summary.unlink()
            summary.symlink_to(outside)

            completed = self.run_manager(root, "validate", "--json")

            self.assertNotEqual(completed.returncode, 0)
            failures = {result["name"]: result for result in json.loads(completed.stdout)["results"] if not result["ok"]}
            self.assertEqual(failures["summary:path"]["detail"], "path contains symlink")

    def test_summarize_write_rejects_symlinked_summary_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_migration_root(root)
            self.migrate_and_summarize(root)
            summary = root / "docs/harness-capabilities.md"
            outside = root / "outside-summary.md"
            outside.write_text("outside\n", encoding="utf-8")
            summary.unlink()
            summary.symlink_to(outside)

            completed = self.run_manager(root, "summarize", "--write", "--json")

            self.assertNotEqual(completed.returncode, 0)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["result"], "failed")
            self.assertIn("path contains symlink", payload["error"])
            self.assertEqual(outside.read_text(encoding="utf-8"), "outside\n")
