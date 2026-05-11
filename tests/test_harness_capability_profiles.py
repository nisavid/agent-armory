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


def write_protocol_artifacts_fixture(root: Path) -> None:
    protocol_dir = root / "specs/capability-profiling-protocol"
    examples_dir = root / "examples/capability-profiling-protocol"
    protocol_dir.parent.mkdir(parents=True, exist_ok=True)
    examples_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(REPO_ROOT / "specs/capability-profiling-protocol", protocol_dir)
    shutil.copytree(REPO_ROOT / "examples/capability-profiling-protocol", examples_dir)


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


def insert_claim_block_detail(profile_text: str, claim_id: str, detail: str) -> str:
    claim_marker = f'id = "{claim_id}"'
    start = profile_text.index(claim_marker)
    next_claim = profile_text.find("\n[[claim]]", start + len(claim_marker))
    if next_claim == -1:
        next_claim = len(profile_text)
    return profile_text[:next_claim].rstrip() + "\n" + detail.strip() + "\n" + profile_text[next_claim:]


def replace_in_claim_block(profile_text: str, claim_id: str, old: str, new: str) -> str:
    claim_marker = f'id = "{claim_id}"'
    start = profile_text.index(claim_marker)
    next_claim = profile_text.find("\n[[claim]]", start + len(claim_marker))
    if next_claim == -1:
        next_claim = len(profile_text)
    block = profile_text[start:next_claim]
    if old not in block:
        raise AssertionError(f"{old!r} not found in {claim_id}")
    return profile_text[:start] + block.replace(old, new, 1) + profile_text[next_claim:]


def claim_index(profile_path: Path, claim_id: str) -> int:
    with profile_path.open("rb") as handle:
        claims = tomllib.load(handle)["claim"]
    for index, claim in enumerate(claims):
        if claim["id"] == claim_id:
            return index
    raise AssertionError(f"{claim_id!r} not found in {profile_path}")


def refresh_claim_with_triage(profile_text: str, claim_id: str, triage: str = "changed") -> str:
    profile_text = replace_in_claim_block(
        profile_text,
        claim_id,
        'migration_status = "migrated_from_aggregate"',
        'migration_status = "refreshed_from_migrated_claim"',
    )
    return replace_in_claim_block(
        profile_text,
        claim_id,
        'evidence_basis = "aggregate_catalog_migration"',
        'evidence_basis = "current_first_party_source"\n'
        f'claim_triage = "{triage}"\n'
        'triage_rationale = "Regression fixture refreshed this claim."\n'
        'install_activation = "Regression fixture activation."\n'
        'configuration_surface = "Regression fixture configuration."\n'
        'reload_update_behavior = "Regression fixture reload behavior."',
    )


def append_enriched_codex_records(profile_text: str, extension_evidence_id: str = "ev-codex-plugin-support-18bcdf25dd") -> str:
    return (
        profile_text.rstrip()
        + f"""

[[version_observation]]
id = "vo-codex-rust-v0-130-0"
observed_version = "rust-v0.130.0"
checked_at = "2026-05-10T17:40:00-04:00"
source_url = "https://github.com/openai/codex/releases/tag/rust-v0.130.0"
source_kind = "first_party"
canonical_profile_change = true
evidence_class = "source_backed"

[[harness_extension]]
id = "ext-codex-plugin-share-metadata"
name = "Plugin share metadata"
scope = "codex plugin sharing"
description = "Codex plugin share settings expose link metadata and discoverability controls."
evidence_ids = ["{extension_evidence_id}"]
evidence_class = "source_backed"
schema_pressure_ids = ["SP-003"]
"""
    )


class HarnessCapabilityProfileManagerTests(unittest.TestCase):
    def assert_indexed_failure(self, failures: set[str], prefix: str, suffix: str) -> None:
        self.assertTrue(any(name.startswith(prefix) and name.endswith(suffix) for name in failures), failures)

    def test_canonical_profiles_are_issue45_enriched_and_triaged(self):
        profile_paths = sorted((REPO_ROOT / "docs/harness-capabilities/vanilla").glob("*.toml"))
        self.assertEqual(len(profile_paths), 6)
        for profile_path in profile_paths:
            with profile_path.open("rb") as handle:
                profile = tomllib.load(handle)
            self.assertTrue(profile.get("version_observation"), profile_path)
            self.assertTrue(profile.get("harness_extension"), profile_path)
            for claim in profile["claim"]:
                with self.subTest(profile=profile_path.name, claim=claim["id"]):
                    self.assertNotEqual(claim["migration_status"], "migrated_from_aggregate")
                    self.assertNotEqual(claim["evidence_basis"], "aggregate_catalog_migration")
                    self.assertIn(claim.get("claim_triage"), {"retained", "changed", "new", "unsupported", "unknown", "not-applicable", "retired"})
                    for field in ["triage_rationale", "install_activation", "configuration_surface", "reload_update_behavior"]:
                        self.assertIsInstance(claim.get(field), str)
                        self.assertTrue(claim[field].strip())
                    if claim["family"] == "memory_context_retrieval":
                        self.assertTrue(claim.get("memory_like_surface"))
                    if claim["family"] == "scheduling_automation":
                        self.assertTrue(claim.get("automation_surface"))
                    if claim["family"] == "cross_harness_import_compatibility":
                        self.assertTrue(claim.get("compatibility_bridge"))

    def write_migration_root(self, root: Path) -> None:
        docs = root / "docs"
        docs.mkdir()
        (docs / "harness-capabilities.toml").write_text(AGGREGATE_FIXTURE.strip() + "\n", encoding="utf-8")
        shutil.copyfile(REPO_ROOT / "docs/harness-capabilities.md", docs / "harness-capabilities.md")

    def write_research_outputs(self, root: Path) -> None:
        write_research_outputs_fixture(root)

    def write_canonical_validation_root(self, root: Path) -> None:
        docs = root / "docs"
        docs.mkdir()
        shutil.copyfile(REPO_ROOT / "docs/harness-capabilities.md", docs / "harness-capabilities.md")
        shutil.copytree(REPO_ROOT / "docs/harness-capabilities", docs / "harness-capabilities")
        shutil.copytree(
            REPO_ROOT / "specs/vanilla-harness-capability-profiles",
            root / "specs/vanilla-harness-capability-profiles",
        )
        write_protocol_artifacts_fixture(root)

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

    def write_refresh_scout_input(self, root: Path, *, effect: str = "passive_scanning") -> Path:
        scratch = root / "scratch"
        scratch.mkdir(exist_ok=True)
        input_path = scratch / "codex-refresh-scout-input.json"
        input_path.write_text(
            json.dumps(
                {
                    "schema": "harness_capability_profiles.refresh_scout_input.v1",
                    "harness_id": "codex",
                    "checked_at": "2026-05-11T10:00:00-04:00",
                    "effects": [
                        {
                            "effect": effect,
                            "classification_ref": "" if effect != "passive_scanning" else "passive-source-review",
                            "approval_ref": "" if effect != "passive_scanning" else "not-required",
                        }
                    ],
                    "sources": [
                        {
                            "id": "source-codex-release",
                            "kind": "first_party_source",
                            "url": "https://github.com/openai/codex/releases/tag/rust-v0.131.0",
                            "observed_version": "0.131.0",
                            "summary": "Fixture Codex release evidence.",
                            "claim_refs": ["claim-codex-lifecycle_reload_update"],
                        },
                        {
                            "id": "source-codex-fallback",
                            "kind": "fallback_source",
                            "url": "https://example.com/codex/fallback",
                            "summary": "Fixture fallback metadata.",
                            "claim_refs": ["claim-codex-runtime_modes"],
                        },
                    ],
                    "local_observations": [
                        {
                            "id": "local-codex-version",
                            "summary": "Fixture local CLI observation.",
                            "claim_refs": ["claim-codex-runtime_modes"],
                        }
                    ],
                    "study_reports": [
                        {
                            "id": "study-codex-skills",
                            "path": "examples/capability-profiling-protocol/vanilla-codex-skill-study-report.toml",
                            "summary": "Selected fixture study report.",
                            "selected": True,
                            "rigor_deviation": "passive source review only",
                        }
                    ],
                    "evidence_notes": [
                        {
                            "id": "note-codex-release",
                            "summary": "Curated durable release note.",
                            "durability": "curated_durable_evidence",
                        }
                    ],
                    "hypotheses": [
                        {
                            "id": "hypothesis-codex-hook-reload",
                            "summary": "Hook reload behavior may have changed.",
                            "claim_refs": ["claim-codex-hooks_events"],
                        }
                    ],
                    "unknowns": [
                        {
                            "id": "unknown-codex-memory-write-authority",
                            "summary": "Memory write authority remains unclear.",
                            "claim_refs": ["claim-codex-memory_context_retrieval"],
                            "follow_up": True,
                        }
                    ],
                    "scratch_disposition": "raw fetched pages are instance-scoped scratch and are not promoted",
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        return input_path

    def write_codex_profile_replacement(self, root: Path) -> Path:
        scratch = root / "scratch"
        scratch.mkdir(exist_ok=True)
        source = root / "docs/harness-capabilities/vanilla/codex.toml"
        replacement = scratch / "codex-planned.toml"
        text = source.read_text(encoding="utf-8")
        current_refresh_notes = 'refresh_notes = "Refresh from GitHub releases first, then first-party OpenAI Codex docs. Keep app, CLI, plugin, hook, and automation surfaces distinct."'
        planned_refresh_notes = 'refresh_notes = "Manual refresh fixture preserves source-backed Codex evidence and records a reviewable refresh-note mutation."'
        self.assertIn(current_refresh_notes, text)
        text = text.replace(current_refresh_notes, planned_refresh_notes, 1)
        replacement.write_text(text, encoding="utf-8")
        return replacement

    def prepare_refresh_artifacts(self, root: Path) -> tuple[Path, Path, Path, Path, Path]:
        scout_input = self.write_refresh_scout_input(root)
        scout_report = root / "scratch/scout-report.json"
        analysis_report = root / "scratch/analysis-report.json"
        plan_path = root / "scratch/update-plan.json"
        replacement = self.write_codex_profile_replacement(root)

        scout = self.run_manager(root, "scout", "--input", str(scout_input), "--write-output", str(scout_report), "--json")
        self.assertEqual(scout.returncode, 0, scout.stderr)
        analyze = self.run_manager(root, "analyze", "--scout-report", str(scout_report), "--write-output", str(analysis_report), "--json")
        self.assertEqual(analyze.returncode, 0, analyze.stderr)
        plan = self.run_manager(
            root,
            "plan",
            "--analysis-report",
            str(analysis_report),
            "--profile-replacement",
            f"codex:{replacement}",
            "--write-output",
            str(plan_path),
            "--json",
        )
        self.assertEqual(plan.returncode, 0, plan.stderr)
        return scout_input, scout_report, analysis_report, plan_path, replacement

    def test_manual_refresh_scout_analyze_plan_diff_and_audit_json_contract(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_canonical_validation_root(root)
            before = (root / "docs/harness-capabilities/vanilla/codex.toml").read_text(encoding="utf-8")

            scout_input, scout_report, analysis_report, plan_path, _replacement = self.prepare_refresh_artifacts(root)

            after = (root / "docs/harness-capabilities/vanilla/codex.toml").read_text(encoding="utf-8")
            self.assertEqual(after, before)

            scout_payload = json.loads(scout_report.read_text(encoding="utf-8"))
            self.assertEqual(scout_payload["schema"], "harness_capability_profiles.refresh_scout_report.v1")
            self.assertEqual(scout_payload["harness_id"], "codex")
            self.assertTrue(scout_payload["dry_run"])
            self.assertEqual(scout_payload["evidence_counts"]["first_party_source"], 1)
            self.assertEqual(scout_payload["evidence_counts"]["fallback_source"], 1)
            self.assertTrue(scout_payload["durable_evidence_candidates"])

            analysis_payload = json.loads(analysis_report.read_text(encoding="utf-8"))
            self.assertEqual(analysis_payload["schema"], "harness_capability_profiles.refresh_analysis_report.v1")
            self.assertEqual(analysis_payload["version_delta"]["disposition"], "changed")
            self.assertTrue(any(item["triage"] == "deeper_review" for item in analysis_payload["claim_triage"]))
            self.assertTrue(analysis_payload["follow_up_issue_candidates"])
            self.assertTrue(analysis_payload["schema_pressure"])

            plan_payload = json.loads(plan_path.read_text(encoding="utf-8"))
            self.assertEqual(plan_payload["schema"], "harness_capability_profiles.refresh_update_plan.v1")
            self.assertEqual(plan_payload["result"], "planned")
            self.assertEqual(plan_payload["mutations"][0]["path"], "docs/harness-capabilities/vanilla/codex.toml")
            self.assertIn("python3.14 tools/harness_capability_profiles.py validate --json", plan_payload["validation_commands"])

            diff = self.run_manager(root, "diff", "--plan", str(plan_path), "--json")
            self.assertEqual(diff.returncode, 0, diff.stderr)
            diff_payload = json.loads(diff.stdout)
            self.assertEqual(diff_payload["schema"], "harness_capability_profiles.refresh_diff.v1")
            self.assertIn("Manual refresh fixture", diff_payload["diffs"][0]["unified_diff"])

            apply = self.run_manager(
                root,
                "apply",
                "--plan",
                str(plan_path),
                "--allow-effect",
                "profile_mutation",
                "--security-ref",
                "specs/vanilla-harness-capability-profiles/security-control-classification.md#profile-mutation",
                "--approval-ref",
                "issue-48-fixture-approval",
                "--json",
            )
            self.assertEqual(apply.returncode, 0, apply.stderr)
            apply_result = root / "scratch/apply-result.json"
            apply_result.write_text(apply.stdout, encoding="utf-8")
            validate = self.run_manager(root, "validate", "--json")
            self.assertEqual(validate.returncode, 0, validate.stderr)
            validation_result = root / "scratch/manager-validation.json"
            validation_result.write_text(validate.stdout, encoding="utf-8")
            audit = self.run_manager(
                root,
                "audit",
                "--scout-report",
                str(scout_report),
                "--analysis-report",
                str(analysis_report),
                "--plan",
                str(plan_path),
                "--apply-result",
                str(apply_result),
                "--validation-result",
                str(validation_result),
                "--json",
            )
            self.assertEqual(audit.returncode, 0, audit.stderr)
            audit_payload = json.loads(audit.stdout)
            self.assertEqual(audit_payload["schema"], "harness_capability_profiles.refresh_audit.v1")
            self.assertIn("source-codex-release", audit_payload["sources_checked"])
            self.assertEqual(audit_payload["profile_files_planned"], ["docs/harness-capabilities/vanilla/codex.toml"])
            self.assertEqual(audit_payload["profile_files_changed"], ["docs/harness-capabilities/vanilla/codex.toml"])
            self.assertIn("not_applicable", audit_payload["claim_change_summary"])
            self.assertEqual(audit_payload["validation_results"][0]["result"], "passed")
            self.assertEqual(audit_payload["scratch_evidence_disposition"], scout_payload["scratch_disposition"])
            self.assertTrue(audit_payload["selected_rigor_deviations"])

            self.assertIn("Manual refresh fixture", (root / "docs/harness-capabilities/vanilla/codex.toml").read_text(encoding="utf-8"))
            self.assertTrue(scout_input.is_file())

    def test_manual_refresh_diff_rejects_mutation_paths_outside_refresh_scope(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_canonical_validation_root(root)
            _scout_input, _scout_report, _analysis_report, plan_path, _replacement = self.prepare_refresh_artifacts(root)
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            plan["mutations"][0]["path"] = "CONTEXT.md"
            plan_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            diff = self.run_manager(root, "diff", "--plan", str(plan_path), "--json")

            self.assertNotEqual(diff.returncode, 0)
            self.assertIn("mutation path not allowed", json.loads(diff.stdout)["error"])

    def test_manual_refresh_effect_gates_block_unapproved_scout_and_apply(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_canonical_validation_root(root)
            scout_input = self.write_refresh_scout_input(root, effect="external_network_access")
            blocked_scout = self.run_manager(root, "scout", "--input", str(scout_input), "--json")
            self.assertNotEqual(blocked_scout.returncode, 0)
            self.assertIn("approval required for effects", json.loads(blocked_scout.stdout)["error"])

            scout_report = root / "scratch/scout-report.json"
            allowed_scout = self.run_manager(
                root,
                "scout",
                "--input",
                str(scout_input),
                "--allow-effect",
                "external_network_access",
                "--security-ref",
                "specs/vanilla-harness-capability-profiles/security-control-classification.md#network-scouting",
                "--approval-ref",
                "issue-48-fixture-approval",
                "--write-output",
                str(scout_report),
                "--json",
            )
            self.assertEqual(allowed_scout.returncode, 0, allowed_scout.stderr)

            _scout_input, _scout_report, _analysis_report, plan_path, _replacement = self.prepare_refresh_artifacts(root)
            blocked_apply = self.run_manager(root, "apply", "--plan", str(plan_path), "--json")
            self.assertNotEqual(blocked_apply.returncode, 0)
            self.assertIn("profile_mutation", json.loads(blocked_apply.stdout)["error"])

    def test_manual_refresh_effect_refs_treat_null_as_unapproved(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_canonical_validation_root(root)
            scout_input = self.write_refresh_scout_input(root, effect="external_network_access")
            payload = json.loads(scout_input.read_text(encoding="utf-8"))
            payload["effects"][0]["classification_ref"] = None
            payload["effects"][0]["approval_ref"] = None
            scout_input.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            blocked = self.run_manager(root, "scout", "--input", str(scout_input), "--json")

            self.assertNotEqual(blocked.returncode, 0)
            self.assertIn("approval required for effects", json.loads(blocked.stdout)["error"])

    def test_manual_refresh_requires_explicit_effects_for_effectful_scout_evidence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_canonical_validation_root(root)
            scout_input = self.write_refresh_scout_input(root)
            payload = json.loads(scout_input.read_text(encoding="utf-8"))
            payload.pop("effects")
            scout_input.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            blocked = self.run_manager(root, "scout", "--input", str(scout_input), "--json")

            self.assertNotEqual(blocked.returncode, 0)
            self.assertIn("effects must be explicit", json.loads(blocked.stdout)["error"])

    def test_manual_refresh_analyze_compares_version_tokens_without_prefix_substrings(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_canonical_validation_root(root)
            scout_input = self.write_refresh_scout_input(root)
            payload = json.loads(scout_input.read_text(encoding="utf-8"))
            profile_path = root / "docs/harness-capabilities/vanilla/codex.toml"
            profile_path.write_text(
                profile_path.read_text(encoding="utf-8").replace(
                    'checked_version = "0.128.0 stable"',
                    'checked_version = "0.130.0 (rust-v0.130.0)"',
                    1,
                ),
                encoding="utf-8",
            )
            scout_report = root / "scratch/scout-report.json"
            analysis_report = root / "scratch/analysis-report.json"

            payload["sources"][0]["observed_version"] = "rust-v0.130.0"
            scout_input.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            scout = self.run_manager(root, "scout", "--input", str(scout_input), "--write-output", str(scout_report), "--json")
            self.assertEqual(scout.returncode, 0, scout.stderr)
            analyze = self.run_manager(root, "analyze", "--scout-report", str(scout_report), "--write-output", str(analysis_report), "--json")
            self.assertEqual(analyze.returncode, 0, analyze.stderr)
            self.assertEqual(json.loads(analysis_report.read_text(encoding="utf-8"))["version_delta"]["disposition"], "unchanged")

            payload["sources"][0]["observed_version"] = "0.13.0"
            scout_input.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            scout = self.run_manager(root, "scout", "--input", str(scout_input), "--write-output", str(scout_report), "--json")
            self.assertEqual(scout.returncode, 0, scout.stderr)
            analyze = self.run_manager(root, "analyze", "--scout-report", str(scout_report), "--write-output", str(analysis_report), "--json")
            self.assertEqual(analyze.returncode, 0, analyze.stderr)
            self.assertEqual(json.loads(analysis_report.read_text(encoding="utf-8"))["version_delta"]["disposition"], "changed")

    def test_manual_refresh_absolute_paths_preserve_symlink_detection(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_canonical_validation_root(root)
            scout_input = self.write_refresh_scout_input(root)
            link = root / "scratch-link"
            link.symlink_to(root / "scratch", target_is_directory=True)

            blocked = self.run_manager(root, "scout", "--input", str(link / scout_input.name), "--json")

            self.assertNotEqual(blocked.returncode, 0)
            self.assertIn("path contains symlink", json.loads(blocked.stdout)["error"])

    def test_manual_refresh_write_outputs_cannot_overwrite_canonical_profiles(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_canonical_validation_root(root)
            scout_input = self.write_refresh_scout_input(root)
            target = root / "docs/harness-capabilities/vanilla/codex.toml"
            before = target.read_text(encoding="utf-8")

            blocked = self.run_manager(
                root,
                "scout",
                "--input",
                str(scout_input),
                "--write-output",
                str(target),
                "--json",
            )

            self.assertNotEqual(blocked.returncode, 0)
            self.assertIn("refresh output may not overwrite canonical profile or schema paths", json.loads(blocked.stdout)["error"])
            self.assertEqual(target.read_text(encoding="utf-8"), before)

    def test_manual_refresh_write_output_guard_does_not_create_blocked_parent_directories(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_canonical_validation_root(root)
            scout_input = self.write_refresh_scout_input(root)
            blocked_parent = root / "docs/harness-capabilities/vanilla/newsubdir"
            target = blocked_parent / "report.json"

            blocked = self.run_manager(
                root,
                "scout",
                "--input",
                str(scout_input),
                "--write-output",
                str(target),
                "--json",
            )

            self.assertNotEqual(blocked.returncode, 0)
            self.assertIn("refresh output may not overwrite canonical profile or schema paths", json.loads(blocked.stdout)["error"])
            self.assertFalse(blocked_parent.exists())

    def test_manual_refresh_write_outputs_must_be_json_artifacts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_canonical_validation_root(root)
            scout_input = self.write_refresh_scout_input(root)
            target = root / "scratch/scout-report.md"

            blocked = self.run_manager(
                root,
                "scout",
                "--input",
                str(scout_input),
                "--write-output",
                str(target),
                "--json",
            )

            self.assertNotEqual(blocked.returncode, 0)
            self.assertIn("refresh output path must end in .json", json.loads(blocked.stdout)["error"])

    def test_manual_refresh_plan_rejects_replacement_for_different_harness(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_canonical_validation_root(root)
            scout_input = self.write_refresh_scout_input(root)
            scout_report = root / "scratch/scout-report.json"
            analysis_report = root / "scratch/analysis-report.json"
            scout = self.run_manager(root, "scout", "--input", str(scout_input), "--write-output", str(scout_report), "--json")
            self.assertEqual(scout.returncode, 0, scout.stderr)
            analyze = self.run_manager(root, "analyze", "--scout-report", str(scout_report), "--write-output", str(analysis_report), "--json")
            self.assertEqual(analyze.returncode, 0, analyze.stderr)

            mismatch = self.run_manager(
                root,
                "plan",
                "--analysis-report",
                str(analysis_report),
                "--profile-replacement",
                "claude_code:docs/harness-capabilities/vanilla/claude_code.toml",
                "--json",
            )

            self.assertNotEqual(mismatch.returncode, 0)
            self.assertIn("must match analysis report harness_id", json.loads(mismatch.stdout)["error"])

    def test_manual_refresh_audit_rejects_cross_report_harness_mismatch(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_canonical_validation_root(root)
            _scout_input, scout_report, analysis_report, plan_path, _replacement = self.prepare_refresh_artifacts(root)
            analysis = json.loads(analysis_report.read_text(encoding="utf-8"))
            analysis["harness_id"] = "cursor"
            analysis_report.write_text(json.dumps(analysis, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            audit = self.run_manager(
                root,
                "audit",
                "--scout-report",
                str(scout_report),
                "--analysis-report",
                str(analysis_report),
                "--plan",
                str(plan_path),
                "--json",
            )

            self.assertNotEqual(audit.returncode, 0)
            self.assertIn("refresh audit artifacts must share harness_id", json.loads(audit.stdout)["error"])

    def test_manual_refresh_audit_requires_apply_and_passing_validation_for_mutations(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_canonical_validation_root(root)
            _scout_input, scout_report, analysis_report, plan_path, _replacement = self.prepare_refresh_artifacts(root)

            without_apply = self.run_manager(
                root,
                "audit",
                "--scout-report",
                str(scout_report),
                "--analysis-report",
                str(analysis_report),
                "--plan",
                str(plan_path),
                "--json",
            )
            self.assertNotEqual(without_apply.returncode, 0)
            self.assertIn("requires apply result", json.loads(without_apply.stdout)["error"])

            apply = self.run_manager(
                root,
                "apply",
                "--plan",
                str(plan_path),
                "--allow-effect",
                "profile_mutation",
                "--security-ref",
                "specs/vanilla-harness-capability-profiles/security-control-classification.md#profile-mutation",
                "--approval-ref",
                "issue-48-fixture-approval",
                "--json",
            )
            self.assertEqual(apply.returncode, 0, apply.stderr)
            apply_result = root / "scratch/apply-result.json"
            apply_result.write_text(apply.stdout, encoding="utf-8")

            without_validation = self.run_manager(
                root,
                "audit",
                "--scout-report",
                str(scout_report),
                "--analysis-report",
                str(analysis_report),
                "--plan",
                str(plan_path),
                "--apply-result",
                str(apply_result),
                "--json",
            )
            self.assertNotEqual(without_validation.returncode, 0)
            self.assertIn("requires validation results", json.loads(without_validation.stdout)["error"])

            failed_validation = root / "scratch/failed-validation.json"
            failed_validation.write_text(
                json.dumps(
                    {
                        "schema": "harness_capability_profiles.validation_result.v1",
                        "result": "failed",
                        "results": [{"name": "fixture", "ok": False, "detail": "failed", "path": "."}],
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
            failed_audit = self.run_manager(
                root,
                "audit",
                "--scout-report",
                str(scout_report),
                "--analysis-report",
                str(analysis_report),
                "--plan",
                str(plan_path),
                "--apply-result",
                str(apply_result),
                "--validation-result",
                str(failed_validation),
                "--json",
            )
            self.assertNotEqual(failed_audit.returncode, 0)
            self.assertIn("validation result did not pass", json.loads(failed_audit.stdout)["error"])

    def test_manual_refresh_apply_refuses_stale_plan_and_explicit_apply_writes_planned_profile_only(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_canonical_validation_root(root)
            _scout_input, _scout_report, _analysis_report, plan_path, _replacement = self.prepare_refresh_artifacts(root)
            target = root / "docs/harness-capabilities/vanilla/codex.toml"
            original = target.read_text(encoding="utf-8")

            target.write_text(original.replace("Codex", "Codex stale fixture", 1), encoding="utf-8")
            stale_apply = self.run_manager(
                root,
                "apply",
                "--plan",
                str(plan_path),
                "--allow-effect",
                "profile_mutation",
                "--security-ref",
                "specs/vanilla-harness-capability-profiles/security-control-classification.md#profile-mutation",
                "--approval-ref",
                "issue-48-fixture-approval",
                "--json",
            )
            self.assertNotEqual(stale_apply.returncode, 0)
            self.assertIn("stale plan precondition", json.loads(stale_apply.stdout)["error"])

            target.write_text(original, encoding="utf-8")
            apply = self.run_manager(
                root,
                "apply",
                "--plan",
                str(plan_path),
                "--allow-effect",
                "profile_mutation",
                "--security-ref",
                "specs/vanilla-harness-capability-profiles/security-control-classification.md#profile-mutation",
                "--approval-ref",
                "issue-48-fixture-approval",
                "--json",
            )
            self.assertEqual(apply.returncode, 0, apply.stderr)
            payload = json.loads(apply.stdout)
            self.assertEqual(payload["schema"], "harness_capability_profiles.refresh_apply.v1")
            self.assertEqual(payload["writes"], ["docs/harness-capabilities/vanilla/codex.toml"])
            self.assertIn("Manual refresh fixture", target.read_text(encoding="utf-8"))

            validate = self.run_manager(root, "validate", "--json")
            self.assertEqual(validate.returncode, 0, validate.stderr)

    def test_manual_refresh_apply_rejects_tampered_plan_content(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_canonical_validation_root(root)
            _scout_input, _scout_report, _analysis_report, plan_path, _replacement = self.prepare_refresh_artifacts(root)
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            plan["mutations"][0]["content"] = plan["mutations"][0]["content"].replace("Codex", "Tampered Codex", 1)
            plan_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            tampered = self.run_manager(
                root,
                "apply",
                "--plan",
                str(plan_path),
                "--allow-effect",
                "profile_mutation",
                "--security-ref",
                "specs/vanilla-harness-capability-profiles/security-control-classification.md#profile-mutation",
                "--approval-ref",
                "issue-48-fixture-approval",
                "--json",
            )

            self.assertNotEqual(tampered.returncode, 0)
            self.assertIn("planned content hash mismatch", json.loads(tampered.stdout)["error"])

    def test_manual_refresh_apply_rejects_mutation_path_outside_plan_harness_scope(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_canonical_validation_root(root)
            _scout_input, _scout_report, _analysis_report, plan_path, _replacement = self.prepare_refresh_artifacts(root)
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            plan["mutations"][0]["path"] = "docs/harness-capabilities/vanilla/claude_code.toml"
            plan["mutations"][0]["harness_id"] = "claude_code"
            plan_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            tampered = self.run_manager(
                root,
                "apply",
                "--plan",
                str(plan_path),
                "--allow-effect",
                "profile_mutation",
                "--security-ref",
                "specs/vanilla-harness-capability-profiles/security-control-classification.md#profile-mutation",
                "--approval-ref",
                "issue-48-fixture-approval",
                "--json",
            )

            self.assertNotEqual(tampered.returncode, 0)
            self.assertIn("mutation harness_id must match plan harness_id", json.loads(tampered.stdout)["error"])

    def test_manual_refresh_apply_requires_profile_mutation_for_tampered_effect_requirements(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_canonical_validation_root(root)
            _scout_input, _scout_report, _analysis_report, plan_path, _replacement = self.prepare_refresh_artifacts(root)
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            plan["effect_requirements"] = []
            plan_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            tampered = self.run_manager(root, "apply", "--plan", str(plan_path), "--json")

            self.assertNotEqual(tampered.returncode, 0)
            self.assertIn("profile_mutation", json.loads(tampered.stdout)["error"])

    def test_manual_refresh_apply_requires_cli_approval_not_embedded_plan_approval(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_canonical_validation_root(root)
            _scout_input, _scout_report, _analysis_report, plan_path, _replacement = self.prepare_refresh_artifacts(root)
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            plan["effect_requirements"] = [
                {
                    "effect": "profile_mutation",
                    "classification_ref": "fake-embedded-classification",
                    "approval_ref": "fake-embedded-approval",
                }
            ]
            plan_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            tampered = self.run_manager(root, "apply", "--plan", str(plan_path), "--json")

            self.assertNotEqual(tampered.returncode, 0)
            self.assertIn("profile_mutation", json.loads(tampered.stdout)["error"])

    def test_repository_capability_profiling_protocol_examples_are_present_and_validated(self):
        required_paths = [
            "specs/capability-profiling-protocol/README.md",
            "specs/capability-profiling-protocol/schema-v1alpha1.md",
            "examples/capability-profiling-protocol/vanilla-codex-skill-study-plan.toml",
            "examples/capability-profiling-protocol/effective-loadout-memory-study-plan.toml",
            "examples/capability-profiling-protocol/vanilla-codex-skill-study-report.toml",
            "examples/capability-profiling-protocol/standard-clean-room-jig-adequacy-report.toml",
        ]
        for relative_path in required_paths:
            with self.subTest(path=relative_path):
                self.assertTrue((REPO_ROOT / relative_path).is_file())

        completed = self.run_manager(REPO_ROOT, "validate", "--json")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        protocol_results = [result for result in payload["results"] if result["name"].startswith("capability_profiling_protocol:")]
        self.assertTrue(protocol_results)
        self.assertTrue(all(result["ok"] for result in protocol_results), protocol_results)

    def test_validate_json_requires_capability_profiling_protocol_artifacts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_canonical_validation_root(root)
            shutil.rmtree(root / "specs/capability-profiling-protocol")
            shutil.rmtree(root / "examples/capability-profiling-protocol")

            completed = self.run_manager(root, "validate", "--json")

            self.assertNotEqual(completed.returncode, 0)
            failures = {result["name"] for result in json.loads(completed.stdout)["results"] if not result["ok"]}
            self.assertIn("capability_profiling_protocol:spec", failures)
            self.assertIn("capability_profiling_protocol:schema", failures)
            self.assertIn("capability_profiling_protocol:example:vanilla_plan:path", failures)
            self.assertIn("capability_profiling_protocol:example:effective_plan:path", failures)
            self.assertIn("capability_profiling_protocol:example:study_report:path", failures)
            self.assertIn("capability_profiling_protocol:example:jig_adequacy:path", failures)

    def test_validate_json_rejects_effectful_protocol_study_without_approval_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_canonical_validation_root(root)
            plan = root / "examples/capability-profiling-protocol/effective-loadout-memory-study-plan.toml"
            text = plan.read_text(encoding="utf-8")
            text = text.replace(
                'security_classification_ref = "specs/vanilla-harness-capability-profiles/security-control-classification.md#local-probing"',
                'security_classification_ref = ""',
                1,
            )
            text = text.replace('operator_approval_ref = "issue-46-example-approval"', 'operator_approval_ref = ""', 1)
            plan.write_text(text, encoding="utf-8")

            completed = self.run_manager(root, "validate", "--json")

            self.assertNotEqual(completed.returncode, 0)
            failures = {result["name"] for result in json.loads(completed.stdout)["results"] if not result["ok"]}
            self.assertIn("capability_profiling_protocol:example:effective_plan:approval:security_classification_ref", failures)
            self.assertIn("capability_profiling_protocol:example:effective_plan:approval:operator_approval_ref", failures)

    def test_validate_json_rejects_invalid_protocol_state_graph_and_analysis_links(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_canonical_validation_root(root)
            plan = root / "examples/capability-profiling-protocol/vanilla-codex-skill-study-plan.toml"
            text = plan.read_text(encoding="utf-8")
            text = text.replace('to = "state-default-onboarded"', 'to = "state-missing"', 1)
            text = text.replace('state_id = "state-default-onboarded"', 'state_id = "state-missing"', 1)
            text = text.replace('claim_refs = ["claim-codex-skills"]', 'claim_refs = ["claim-codex-missing"]', 1)
            text = text.replace('observation_point_refs = ["observe-default-skill-source"]', 'observation_point_refs = ["observe-missing"]', 1)
            plan.write_text(text, encoding="utf-8")

            completed = self.run_manager(root, "validate", "--json")

            self.assertNotEqual(completed.returncode, 0)
            failures = {result["name"] for result in json.loads(completed.stdout)["results"] if not result["ok"]}
            self.assertIn("capability_profiling_protocol:example:vanilla_plan:transition:transition-default-onboarding:to", failures)
            self.assertIn("capability_profiling_protocol:example:vanilla_plan:observation_point:observe-default-skill-source:state_id", failures)
            self.assertIn("capability_profiling_protocol:example:vanilla_plan:observation_point:observe-default-skill-source:claim_refs", failures)
            self.assertIn("capability_profiling_protocol:example:vanilla_plan:analysis_angle:source-doc-angle:observation_point_refs", failures)

    def test_validate_json_rejects_cyclic_protocol_state_graph(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_canonical_validation_root(root)
            plan = root / "examples/capability-profiling-protocol/vanilla-codex-skill-study-plan.toml"
            text = plan.read_text(encoding="utf-8")
            text = text.replace('from = "state-before-install"', 'from = "state-default-onboarded"', 1)
            plan.write_text(text, encoding="utf-8")

            completed = self.run_manager(root, "validate", "--json")

            self.assertNotEqual(completed.returncode, 0)
            failures = {result["name"] for result in json.loads(completed.stdout)["results"] if not result["ok"]}
            self.assertIn("capability_profiling_protocol:example:vanilla_plan:state_graph:cycle", failures)

    def test_validate_json_rejects_multiple_selected_protocol_analysis_angles(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_canonical_validation_root(root)
            plan = root / "examples/capability-profiling-protocol/vanilla-codex-skill-study-plan.toml"
            text = plan.read_text(encoding="utf-8")
            text = text.replace("selected = false", "selected = true", 1)
            plan.write_text(text, encoding="utf-8")

            completed = self.run_manager(root, "validate", "--json")

            self.assertNotEqual(completed.returncode, 0)
            failures = {result["name"] for result in json.loads(completed.stdout)["results"] if not result["ok"]}
            self.assertIn("capability_profiling_protocol:example:vanilla_plan:analysis_angle:selected", failures)

    def test_validate_json_rejects_invalid_and_overlapping_protocol_effects(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_canonical_validation_root(root)
            plan = root / "examples/capability-profiling-protocol/vanilla-codex-skill-study-plan.toml"
            text = plan.read_text(encoding="utf-8")
            text = text.replace(
                'blocked = ["local_mutation", "profile_mutation", "external_disclosure", "process_execution", "harness_runtime_state_change"]',
                'blocked = ["passive_scanning", "unknown_effect"]',
                1,
            )
            plan.write_text(text, encoding="utf-8")

            completed = self.run_manager(root, "validate", "--json")

            self.assertNotEqual(completed.returncode, 0)
            failures = {result["name"] for result in json.loads(completed.stdout)["results"] if not result["ok"]}
            self.assertIn("capability_profiling_protocol:example:vanilla_plan:effects:blocked", failures)
            self.assertIn("capability_profiling_protocol:example:vanilla_plan:effects:overlap", failures)

    def test_validate_json_rejects_missing_protocol_blocked_effects(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_canonical_validation_root(root)
            plan = root / "examples/capability-profiling-protocol/vanilla-codex-skill-study-plan.toml"
            text = plan.read_text(encoding="utf-8")
            text = text.replace(
                'blocked = ["local_mutation", "profile_mutation", "external_disclosure", "process_execution", "harness_runtime_state_change"]\n',
                "",
                1,
            )
            plan.write_text(text, encoding="utf-8")

            completed = self.run_manager(root, "validate", "--json")

            self.assertNotEqual(completed.returncode, 0)
            failures = {result["name"] for result in json.loads(completed.stdout)["results"] if not result["ok"]}
            self.assertIn("capability_profiling_protocol:example:vanilla_plan:effects:blocked", failures)

    def test_validate_json_rejects_protocol_selected_rigor_mismatch(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_canonical_validation_root(root)
            plan = root / "examples/capability-profiling-protocol/vanilla-codex-skill-study-plan.toml"
            text = plan.read_text(encoding="utf-8")
            text = text.replace('selected_rigor = "passive_source_review"', 'selected_rigor = "controlled_fixture"', 1)
            plan.write_text(text, encoding="utf-8")

            completed = self.run_manager(root, "validate", "--json")

            self.assertNotEqual(completed.returncode, 0)
            failures = {result["name"] for result in json.loads(completed.stdout)["results"] if not result["ok"]}
            self.assertIn("capability_profiling_protocol:example:vanilla_plan:selected_rigor", failures)

    def test_validate_json_rejects_protocol_study_report_orphaned_plan_refs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_canonical_validation_root(root)
            report = root / "examples/capability-profiling-protocol/vanilla-codex-skill-study-report.toml"
            text = report.read_text(encoding="utf-8")
            text = text.replace('plan_id = "study-plan-vanilla-codex-skills"', 'plan_id = "study-plan-missing"', 1)
            text = text.replace('claim_ref = "claim-codex-skills"', 'claim_ref = "claim-codex-missing"', 1)
            text = text.replace('observation_point_ref = "observe-default-skill-source"', 'observation_point_ref = "observe-missing"', 1)
            text = text.replace('claim_ref = "claim-codex-skills"', 'claim_ref = "claim-assessment-missing"', 1)
            report.write_text(text, encoding="utf-8")

            completed = self.run_manager(root, "validate", "--json")

            self.assertNotEqual(completed.returncode, 0)
            failures = {result["name"] for result in json.loads(completed.stdout)["results"] if not result["ok"]}
            self.assertIn("capability_profiling_protocol:example:study_report:plan_id", failures)
            self.assertIn("capability_profiling_protocol:example:study_report:observed_result:result-codex-skills-source:claim_ref", failures)
            self.assertIn(
                "capability_profiling_protocol:example:study_report:observed_result:result-codex-skills-source:observation_point_ref",
                failures,
            )
            self.assertIn("capability_profiling_protocol:example:study_report:claim_assessment:claim-assessment-missing:claim_ref", failures)

    def test_validate_json_rejects_protocol_study_report_missing_plan_ref(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_canonical_validation_root(root)
            report = root / "examples/capability-profiling-protocol/vanilla-codex-skill-study-report.toml"
            text = report.read_text(encoding="utf-8")
            text = text.replace(
                'plan_ref = "examples/capability-profiling-protocol/vanilla-codex-skill-study-plan.toml"',
                'plan_ref = "examples/capability-profiling-protocol/missing-study-plan.toml"',
                1,
            )
            report.write_text(text, encoding="utf-8")

            completed = self.run_manager(root, "validate", "--json")

            self.assertNotEqual(completed.returncode, 0)
            failures = {result["name"] for result in json.loads(completed.stdout)["results"] if not result["ok"]}
            self.assertIn("capability_profiling_protocol:example:study_report:plan_ref", failures)

    def test_validate_json_rejects_non_jig_target_in_jig_adequacy_report(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_canonical_validation_root(root)
            report = root / "examples/capability-profiling-protocol/standard-clean-room-jig-adequacy-report.toml"
            text = report.read_text(encoding="utf-8")
            text = text.replace('type = "clean_room_jig_surface"', 'type = "vanilla_harness_surface"', 1)
            report.write_text(text, encoding="utf-8")

            completed = self.run_manager(root, "validate", "--json")

            self.assertNotEqual(completed.returncode, 0)
            failures = {result["name"] for result in json.loads(completed.stdout)["results"] if not result["ok"]}
            self.assertIn("capability_profiling_protocol:example:jig_adequacy:target:type", failures)

    def test_validate_json_rejects_jig_adequacy_without_control_dispositions(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_canonical_validation_root(root)
            report = root / "examples/capability-profiling-protocol/standard-clean-room-jig-adequacy-report.toml"
            text = report.read_text(encoding="utf-8")
            text = text.replace('disposition = "verified"', 'disposition = "claimed"', 1)
            text = text.replace('disposition = "unsupported"', 'disposition = "claimed"', 1)
            text = text.replace('disposition = "unknown"', 'disposition = "claimed"', 1)
            report.write_text(text, encoding="utf-8")

            completed = self.run_manager(root, "validate", "--json")

            self.assertNotEqual(completed.returncode, 0)
            failures = {result["name"] for result in json.loads(completed.stdout)["results"] if not result["ok"]}
            self.assertIn("capability_profiling_protocol:example:jig_adequacy:control_dispositions", failures)

    def test_validate_accepts_enriched_claim_extensions_without_claim_id_churn(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_canonical_validation_root(root)
            codex_profile = root / "docs/harness-capabilities/vanilla/codex.toml"
            with codex_profile.open("rb") as handle:
                codex_claims = tomllib.load(handle)["claim"]

            completed = self.run_manager(root, "validate", "--json")

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["result"], "passed")
            for claim in codex_claims:
                with self.subTest(claim=claim["id"]):
                    self.assertEqual(claim["id"], f"claim-codex-{claim['family']}")

    def test_validate_accepts_local_observation_version_observation_without_source_url(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_canonical_validation_root(root)
            codex_profile = root / "docs/harness-capabilities/vanilla/codex.toml"
            text = codex_profile.read_text(encoding="utf-8").rstrip() + """

[[version_observation]]
id = "vo-codex-local"
observed_version = "local smoke"
checked_at = "2026-05-10T17:40:00-04:00"
canonical_profile_change = false
evidence_class = "local_observation"
"""
            codex_profile.write_text(text, encoding="utf-8")

            completed = self.run_manager(root, "validate", "--json")

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["result"], "passed")

    def test_validate_rejects_local_observation_version_observation_with_source_metadata(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_migration_root(root)
            self.migrate_and_summarize(root)
            codex_profile = root / "docs/harness-capabilities/vanilla/codex.toml"
            text = codex_profile.read_text(encoding="utf-8").rstrip() + """

[[version_observation]]
id = "vo-codex-local"
observed_version = "local smoke"
checked_at = "2026-05-10T17:40:00-04:00"
source_url = "https://example.invalid/local"
source_kind = "first_party"
canonical_profile_change = false
evidence_class = "local_observation"
"""
            codex_profile.write_text(text, encoding="utf-8")

            completed = self.run_manager(root, "validate", "--json")

            self.assertNotEqual(completed.returncode, 0)
            failures = {result["name"] for result in json.loads(completed.stdout)["results"] if not result["ok"]}
            self.assert_indexed_failure(failures, "profile:codex:version_observation:", ":source_kind")
            self.assert_indexed_failure(failures, "profile:codex:version_observation:", ":source_url")

    def test_validate_rejects_missing_canonical_enrichment_records(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_migration_root(root)
            self.migrate_and_summarize(root)

            completed = self.run_manager(root, "validate", "--json")

            self.assertNotEqual(completed.returncode, 0)
            failures = {result["name"] for result in json.loads(completed.stdout)["results"] if not result["ok"]}
            self.assertIn("profile:codex:version_observation", failures)
            self.assertIn("profile:codex:harness_extension", failures)

    def test_validate_rejects_migrated_only_canonical_claims(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_migration_root(root)
            self.migrate_and_summarize(root)
            codex_profile = root / "docs/harness-capabilities/vanilla/codex.toml"

            completed = self.run_manager(root, "validate", "--json")

            self.assertNotEqual(completed.returncode, 0)
            failures = {result["name"] for result in json.loads(completed.stdout)["results"] if not result["ok"]}
            first_claim_index = claim_index(codex_profile, "claim-codex-instructions_context")
            self.assertIn(f"profile:codex:claim:{first_claim_index}:migration_status", failures)

    def test_validate_rejects_refreshed_claim_missing_triage_and_integration_detail(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_migration_root(root)
            self.migrate_and_summarize(root)
            codex_profile = root / "docs/harness-capabilities/vanilla/codex.toml"
            text = codex_profile.read_text(encoding="utf-8")
            text = text.replace('migration_status = "migrated_from_aggregate"', 'migration_status = "refreshed_from_migrated_claim"', 1)
            text = text.replace('evidence_basis = "aggregate_catalog_migration"', 'evidence_basis = "current_first_party_source"', 1)
            codex_profile.write_text(text, encoding="utf-8")

            completed = self.run_manager(root, "validate", "--json")

            self.assertNotEqual(completed.returncode, 0)
            failures = {result["name"] for result in json.loads(completed.stdout)["results"] if not result["ok"]}
            first_claim_index = claim_index(codex_profile, "claim-codex-instructions_context")
            self.assertIn(f"profile:codex:claim:{first_claim_index}:claim_triage", failures)
            self.assertIn(f"profile:codex:claim:{first_claim_index}:triage_rationale", failures)
            self.assertIn(f"profile:codex:claim:{first_claim_index}:install_activation", failures)
            self.assertIn(f"profile:codex:claim:{first_claim_index}:configuration_surface", failures)
            self.assertIn(f"profile:codex:claim:{first_claim_index}:reload_update_behavior", failures)

    def test_validate_rejects_unpaired_migrated_status_and_evidence_basis(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_migration_root(root)
            self.migrate_and_summarize(root)
            codex_profile = root / "docs/harness-capabilities/vanilla/codex.toml"
            text = codex_profile.read_text(encoding="utf-8")
            text = replace_in_claim_block(
                text,
                "claim-codex-skills",
                'migration_status = "migrated_from_aggregate"',
                'migration_status = "refreshed_from_migrated_claim"',
            )
            codex_profile.write_text(text, encoding="utf-8")

            completed = self.run_manager(root, "validate", "--json")

            self.assertNotEqual(completed.returncode, 0)
            failures = {result["name"] for result in json.loads(completed.stdout)["results"] if not result["ok"]}
            skills_index = claim_index(codex_profile, "claim-codex-skills")
            self.assertIn(f"profile:codex:claim:{skills_index}:migration_evidence_pair", failures)

    def test_validate_rejects_refreshed_claim_without_detail(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_migration_root(root)
            self.migrate_and_summarize(root)
            codex_profile = root / "docs/harness-capabilities/vanilla/codex.toml"
            text = codex_profile.read_text(encoding="utf-8")
            text = refresh_claim_with_triage(text, "claim-codex-skills")
            codex_profile.write_text(text, encoding="utf-8")

            completed = self.run_manager(root, "validate", "--json")

            self.assertNotEqual(completed.returncode, 0)
            failures = {result["name"] for result in json.loads(completed.stdout)["results"] if not result["ok"]}
            skills_index = claim_index(codex_profile, "claim-codex-skills")
            self.assertIn(f"profile:codex:claim:{skills_index}:detail", failures)

    def test_validate_rejects_required_refreshed_family_claims_without_nested_surface(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_migration_root(root)
            self.migrate_and_summarize(root)
            codex_profile = root / "docs/harness-capabilities/vanilla/codex.toml"
            text = codex_profile.read_text(encoding="utf-8")
            required_claims = [
                ("claim-codex-memory_context_retrieval", "memory_like_surface"),
                ("claim-codex-scheduling_automation", "automation_surface"),
                ("claim-codex-cross_harness_import_compatibility", "compatibility_bridge"),
            ]
            for claim_id_value, _ in required_claims:
                text = refresh_claim_with_triage(text, claim_id_value)
            codex_profile.write_text(text, encoding="utf-8")

            completed = self.run_manager(root, "validate", "--json")

            self.assertNotEqual(completed.returncode, 0)
            failures = {result["name"] for result in json.loads(completed.stdout)["results"] if not result["ok"]}
            for claim_id_value, nested_table in required_claims:
                index = claim_index(codex_profile, claim_id_value)
                self.assertIn(f"profile:codex:claim:{index}:{nested_table}", failures)

    def test_validate_rejects_source_backed_claim_without_evidence_refs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_migration_root(root)
            self.migrate_and_summarize(root)
            codex_profile = root / "docs/harness-capabilities/vanilla/codex.toml"
            text = codex_profile.read_text(encoding="utf-8")
            with codex_profile.open("rb") as handle:
                skill_evidence_id = tomllib.load(handle)["evidence"][0]["id"]
            text = refresh_claim_with_triage(text, "claim-codex-skills", triage="unknown")
            text = replace_in_claim_block(text, "claim-codex-skills", 'status = "supported"', 'status = "unknown"')
            text = replace_in_claim_block(text, "claim-codex-skills", f'evidence_ids = ["{skill_evidence_id}"]', "evidence_ids = []")
            text = insert_claim_block_detail(
                text,
                "claim-codex-skills",
                """
[[claim.detail]]
component = "skills"
load_attachment_point = "configured skill roots"
activation = "explicit or implicit"
mutability = "filesystem-backed and plugin-provided"
scope = ["project", "user", "plugin"]
evidence_ids = []
evidence_class = "local_observation"
""",
            )
            codex_profile.write_text(text, encoding="utf-8")

            completed = self.run_manager(root, "validate", "--json")

            self.assertNotEqual(completed.returncode, 0)
            failures = {result["name"] for result in json.loads(completed.stdout)["results"] if not result["ok"]}
            skills_index = claim_index(codex_profile, "claim-codex-skills")
            self.assertIn(f"profile:codex:claim:{skills_index}:evidence_refs", failures)

    def test_validate_rejects_unknown_schema_pressure_ids(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_migration_root(root)
            self.migrate_and_summarize(root)
            codex_profile = root / "docs/harness-capabilities/vanilla/codex.toml"
            text = codex_profile.read_text(encoding="utf-8")
            with codex_profile.open("rb") as handle:
                skill_evidence_id = tomllib.load(handle)["evidence"][0]["id"]
            text = append_enriched_codex_records(text, skill_evidence_id)
            text = text.replace('schema_pressure_ids = ["SP-003"]', 'schema_pressure_ids = ["SP-999"]', 1)
            codex_profile.write_text(text, encoding="utf-8")

            completed = self.run_manager(root, "validate", "--json")

            self.assertNotEqual(completed.returncode, 0)
            failures = {result["name"] for result in json.loads(completed.stdout)["results"] if not result["ok"]}
            self.assertIn("profile:codex:harness_extension:0:schema_pressure_ids:SP-999", failures)

    def test_validate_rejects_malformed_enrichment_extension_records(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_migration_root(root)
            self.migrate_and_summarize(root)
            codex_profile = root / "docs/harness-capabilities/vanilla/codex.toml"
            text = codex_profile.read_text(encoding="utf-8")
            text = insert_claim_block_detail(
                text,
                "claim-codex-scheduling_automation",
                """
[[claim.automation_surface]]
trigger_class = "recurring schedule"
runner_locus = ""
recurrence_shape = "cron-like schedule"
permission_sandbox_context = "inherits Codex sandbox and approval policy"
missed_run_behavior = "unknown"
output_delivery = "thread continuation"
evidence_ids = ["ev-codex-missing"]
evidence_class = "source_backed"
""",
            )
            text = text.rstrip() + """

[[version_observation]]
observed_version = "rust-v0.130.0"
checked_at = "2026-05-10T17:40:00-04:00"
source_url = "file:///tmp/release"
source_kind = "local"
canonical_profile_change = "yes"
evidence_class = "rumor"

[[harness_extension]]
id = "ext-codex-invalid"
name = ""
scope = "codex"
description = "Missing evidence references."
evidence_ids = ["ev-codex-missing"]
evidence_class = "source_backed"
schema_pressure_ids = ["SP-003"]
"""
            codex_profile.write_text(text, encoding="utf-8")

            completed = self.run_manager(root, "validate", "--json")

            self.assertNotEqual(completed.returncode, 0)
            failures = {result["name"] for result in json.loads(completed.stdout)["results"] if not result["ok"]}
            self.assert_indexed_failure(failures, "profile:codex:version_observation:", ":id")
            self.assert_indexed_failure(failures, "profile:codex:version_observation:", ":source_kind")
            self.assert_indexed_failure(failures, "profile:codex:version_observation:", ":source_url")
            self.assert_indexed_failure(failures, "profile:codex:version_observation:", ":canonical_profile_change")
            self.assert_indexed_failure(failures, "profile:codex:version_observation:", ":evidence_class")
            automation_index = claim_index(codex_profile, "claim-codex-scheduling_automation")
            self.assertIn(f"profile:codex:claim:{automation_index}:automation_surface:0:runner_locus", failures)
            self.assertIn(f"profile:codex:claim:{automation_index}:automation_surface:0:evidence_refs", failures)
            self.assertIn("profile:codex:harness_extension:0:name", failures)
            self.assertIn("profile:codex:harness_extension:0:evidence_refs", failures)

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

    def test_validate_json_accepts_canonical_issue45_profiles(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_canonical_validation_root(root)

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

    def test_validate_json_omits_schema_pressure_id_cascade_when_report_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_canonical_validation_root(root)
            (root / "specs/vanilla-harness-capability-profiles/schema-pressure-report.md").unlink()

            completed = self.run_manager(root, "validate", "--json")

            self.assertNotEqual(completed.returncode, 0)
            payload = json.loads(completed.stdout)
            failures = {result["name"] for result in payload["results"] if not result["ok"]}
            self.assertIn("schema_pressure:path", failures)
            self.assertFalse(any(":schema_pressure_ids:" in failure for failure in failures))

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
            self.write_canonical_validation_root(root)
            report = root / "specs/vanilla-harness-capability-profiles/schema-pressure-report.md"
            report.write_text(report.read_text(encoding="utf-8").replace("needs more evidence", "needs-more-evidence", 1), encoding="utf-8")

            completed = self.run_manager(root, "validate", "--json")

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["result"], "passed")

    def test_validate_json_accepts_extra_whitespace_in_research_note_headings(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_canonical_validation_root(root)
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

    def test_validate_json_ignores_code_block_headings_in_research_notes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_migration_root(root)
            self.migrate_and_summarize(root)
            codex_note = root / "specs/vanilla-harness-capability-profiles/research-notes/codex.md"
            original = codex_note.read_text(encoding="utf-8")
            surface_body = original.split("## Surface Findings\n\n", 1)[1].split("\n## Evidence Classification", 1)[0]
            indented_surface_body = "".join(f"    {line}\n" for line in surface_body.splitlines())
            codex_note.write_text(
                original.replace("## Source Set", "Source Set", 1)
                .replace("- [Fixture source](https://example.com/codex)", "No source URL here.", 1)
                .replace("## Surface Findings", "Surface Findings", 1)
                .replace(surface_body, "No surface family matrix here.\n", 1)
                + "\n```markdown\n## Source Set\n- [Fixture source](https://example.com/codex)\n```\n"
                + f"\n    ## Surface Findings\n{indented_surface_body}",
                encoding="utf-8",
            )

            completed = self.run_manager(root, "validate", "--json")

            self.assertNotEqual(completed.returncode, 0)
            payload = json.loads(completed.stdout)
            failures = {result["name"]: result for result in payload["results"] if not result["ok"]}
            self.assertIn("research_note:codex:section:source_set", failures)
            self.assertIn("research_note:codex:section:surface_findings", failures)
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
