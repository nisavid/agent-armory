import json
import importlib
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from unittest import mock
from pathlib import Path

from tools import issue_tracker_core
from tools.validate_armory_integrity import (
    ACCEPTED_SOURCE_REQUIREMENTS,
    CheckResult,
    CANONICAL_DOC_STATUSES,
    CONTEXT_REQUIRED_SECTIONS,
    REQUIRED_HARNESSES,
    SOURCE_DISPOSITION_ITEM_FIELDS,
    SOURCE_DISPOSITION_MANIFEST_FIELDS,
    SOURCE_DISPOSITION_PATH,
    HARBOR_JIG_SOURCE_MAP_PATH,
    HARBOR_NEIGHBOR_TOOL_CATALOG_PATH,
    HARBOR_REWARD_KIT_EVALUATION_PATH,
    HARBOR_AGENT_EQUIPMENT_AB_PROTOTYPE_RESULTS_PATH,
    HARBOR_ATIF_JOB_ARTIFACTS_EVALUATION_PATH,
    HARBOR_DRIVER_GATE_PATH,
    HARBOR_FINAL_DISPOSITION_PATH,
    EXTERNAL_TOOL_EVALUATION_PATH,
    HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH,
    SKILL_EVAL_METHODOLOGY_SOURCE_INTAKE_PATH,
    PLUGIN_CREATOR_SOURCE_INTAKE_PATH,
    find_markdown_links,
    harness_matrix_rows,
    load_toml,
    render_human,
    run,
    source_disposition_table_digest,
    validate_final_source_retired_stamp,
    validate_final_closeout,
    validate_canonical_docs,
    validate_context,
    validate_documentation_closeout,
    validate_examples,
    validate_forge_routes,
    validate_harness_catalog,
    validate_markdown_links,
    validate_issue_tracker_ops_policy_config,
    validate_projection_drafts,
    validate_python_runtime_declaration,
    validate_specs,
    validate_source_disposition,
    validate_source_retired_tree,
    validate_source_handoff_provenance,
    validate_source_projection,
    SOURCE_PROJECTION_PLANNED_REQUIREMENTS,
    validate_required_paths,
    validate_security_closeout,
    validate_harbor_jig_source_map,
    validate_harbor_neighbor_tool_catalog,
    validate_harbor_reward_kit_evaluation,
    validate_harbor_agent_equipment_ab_prototype_results,
    validate_harbor_atif_job_artifacts_evaluation,
    validate_harbor_driver_gate,
    validate_harbor_final_disposition,
    validate_external_tool_evaluation,
    validate_harbor_external_tool_evaluation_record,
    validate_skill_eval_methodology_source_intake,
    validate_plugin_creator_source_intake,
    validate_templates,
    validate_threat_model,
)


class ValidationBoundaryTests(unittest.TestCase):
    def load_live_validator(self):
        return importlib.import_module("tools.validate_armory_integrity")

    def test_live_validator_exposes_boundary_inventory(self):
        validator = self.load_live_validator()

        inventory_items = validator.validation_inventory()
        inventory_keys = [item["check"] for item in inventory_items]
        duplicate_keys = sorted({key for key in inventory_keys if inventory_keys.count(key) > 1})
        self.assertEqual(duplicate_keys, [])
        inventory = {item["check"]: item for item in inventory_items}

        self.assertEqual(inventory["required_paths"]["boundary"], "armory_integrity")
        self.assertEqual(inventory["python_runtime"]["boundary"], "armory_integrity")
        self.assertEqual(inventory["forge_routes"]["boundary"], "forge_integrity")
        self.assertEqual(inventory["canonical_docs"]["boundary"], "forge_integrity")
        self.assertEqual(inventory["threat_model"]["boundary"], "armory_integrity")
        self.assertEqual(inventory["documentation_closeout"]["boundary"], "armory_integrity")
        self.assertEqual(inventory["security_closeout"]["boundary"], "armory_integrity")
        self.assertEqual(inventory["projection_drafts"]["boundary"], "armory_integrity")
        self.assertEqual(inventory["harness_catalog"]["boundary"], "forge_integrity")
        self.assertEqual(inventory["templates"]["boundary"], "equipment_candidate_shape")
        self.assertEqual(inventory["published_equipment_delivery"]["boundary"], "armory_integrity")
        self.assertEqual(inventory["published_equipment_inventory_view"]["boundary"], "armory_integrity")
        self.assertEqual(inventory["examples"]["boundary"], "equipment_candidate_shape")
        self.assertEqual(inventory["specs"]["boundary"], "equipment_candidate_shape")
        self.assertIn("issue_ops_workflow_executor", inventory)
        self.assertEqual(inventory["issue_ops_workflow_executor"]["boundary"], "equipment_candidate_shape")
        self.assertEqual(inventory["markdown_links"]["boundary"], "armory_integrity")
        self.assertEqual(inventory["source_disposition"]["boundary"], "armory_integrity")
        self.assertEqual(inventory["harbor_jig_source_map"]["boundary"], "armory_integrity")
        self.assertEqual(inventory["harbor_neighbor_tool_catalog"]["boundary"], "armory_integrity")
        self.assertEqual(inventory["harbor_reward_kit_evaluation"]["boundary"], "armory_integrity")
        self.assertEqual(inventory["harbor_agent_equipment_ab_prototype_results"]["boundary"], "armory_integrity")
        self.assertIn("harbor_atif_job_artifacts_evaluation", inventory)
        self.assertEqual(inventory["harbor_atif_job_artifacts_evaluation"]["boundary"], "armory_integrity")
        self.assertIn("harbor_driver_gate", inventory)
        self.assertEqual(inventory["harbor_driver_gate"]["boundary"], "armory_integrity")
        self.assertIn("harbor_final_disposition", inventory)
        self.assertEqual(inventory["harbor_final_disposition"]["boundary"], "armory_integrity")
        self.assertEqual(inventory["external_tool_evaluation"]["boundary"], "armory_integrity")
        self.assertEqual(inventory["harbor_external_tool_evaluation_record"]["boundary"], "armory_integrity")
        self.assertEqual(inventory["skill_eval_methodology_source_intake"]["boundary"], "armory_integrity")
        self.assertEqual(inventory["plugin_creator_source_intake"]["boundary"], "armory_integrity")
        self.assertEqual(inventory["source_retired_tree"]["boundary"], "historical_seed_migration")
        self.assertEqual(inventory["final_source_retired_stamp"]["boundary"], "historical_seed_migration")
        self.assertEqual(
            inventory["harness_catalog"]["relationship"],
            "Forge-scoped live integrity; detailed Vanilla Harness Capability Profile behavior belongs to the Manager Core validator.",
        )

    def test_live_validator_json_uses_armory_integrity_envelope(self):
        validator = self.load_live_validator()

        output = json.loads(validator.render_json([CheckResult("demo", True, "ok", "README.md")]))

        self.assertEqual(output["schema"], "armory_integrity.validation_result.v1")
        self.assertEqual(output["validation"], "Armory Integrity Validation")
        self.assertEqual(output["results"][0]["name"], "demo")

    def test_live_validator_run_includes_plugin_creator_source_intake(self):
        repo_root = Path(__file__).resolve().parents[1]

        results = run(repo_root, final_closeout=True)
        result_map = {result.name: result for result in results}

        self.assertEqual(
            result_map[f"required_path:{PLUGIN_CREATOR_SOURCE_INTAKE_PATH}"],
            CheckResult(
                name=f"required_path:{PLUGIN_CREATOR_SOURCE_INTAKE_PATH}",
                ok=True,
                detail="exists",
                path=PLUGIN_CREATOR_SOURCE_INTAKE_PATH,
            ),
        )
        self.assertEqual(
            result_map["plugin_creator_source_intake:ledger"],
            CheckResult(
                name="plugin_creator_source_intake:ledger",
                ok=True,
                detail="present",
                path=PLUGIN_CREATOR_SOURCE_INTAKE_PATH,
            ),
        )

    def test_live_validator_run_includes_harbor_jig_source_map(self):
        repo_root = Path(__file__).resolve().parents[1]

        results = run(repo_root, final_closeout=True)
        result_map = {result.name: result for result in results}

        self.assertEqual(
            result_map[f"required_path:{HARBOR_JIG_SOURCE_MAP_PATH}"],
            CheckResult(
                name=f"required_path:{HARBOR_JIG_SOURCE_MAP_PATH}",
                ok=True,
                detail="exists",
                path=HARBOR_JIG_SOURCE_MAP_PATH,
            ),
        )
        self.assertEqual(
            result_map["harbor_jig_source_map:ledger"],
            CheckResult(
                name="harbor_jig_source_map:ledger",
                ok=True,
                detail="present",
                path=HARBOR_JIG_SOURCE_MAP_PATH,
            ),
        )

    def test_live_validator_run_includes_harbor_neighbor_tool_catalog(self):
        repo_root = Path(__file__).resolve().parents[1]

        results = run(repo_root, final_closeout=True)
        result_map = {result.name: result for result in results}

        self.assertEqual(
            result_map[f"required_path:{HARBOR_NEIGHBOR_TOOL_CATALOG_PATH}"],
            CheckResult(
                name=f"required_path:{HARBOR_NEIGHBOR_TOOL_CATALOG_PATH}",
                ok=True,
                detail="exists",
                path=HARBOR_NEIGHBOR_TOOL_CATALOG_PATH,
            ),
        )
        self.assertEqual(
            result_map["harbor_neighbor_tool_catalog:ledger"],
            CheckResult(
                name="harbor_neighbor_tool_catalog:ledger",
                ok=True,
                detail="present",
                path=HARBOR_NEIGHBOR_TOOL_CATALOG_PATH,
            ),
        )

    def test_live_validator_run_includes_harbor_reward_kit_evaluation(self):
        repo_root = Path(__file__).resolve().parents[1]

        results = run(repo_root, final_closeout=True)
        result_map = {result.name: result for result in results}

        self.assertEqual(
            result_map[f"required_path:{HARBOR_REWARD_KIT_EVALUATION_PATH}"],
            CheckResult(
                name=f"required_path:{HARBOR_REWARD_KIT_EVALUATION_PATH}",
                ok=True,
                detail="exists",
                path=HARBOR_REWARD_KIT_EVALUATION_PATH,
            ),
        )
        self.assertEqual(
            result_map["harbor_reward_kit_evaluation:ledger"],
            CheckResult(
                name="harbor_reward_kit_evaluation:ledger",
                ok=True,
                detail="present",
                path=HARBOR_REWARD_KIT_EVALUATION_PATH,
            ),
        )

    def test_live_validator_run_includes_harbor_agent_equipment_ab_prototype_results(self):
        repo_root = Path(__file__).resolve().parents[1]

        results = run(repo_root, final_closeout=True)
        result_map = {result.name: result for result in results}

        self.assertEqual(
            result_map[f"required_path:{HARBOR_AGENT_EQUIPMENT_AB_PROTOTYPE_RESULTS_PATH}"],
            CheckResult(
                name=f"required_path:{HARBOR_AGENT_EQUIPMENT_AB_PROTOTYPE_RESULTS_PATH}",
                ok=True,
                detail="exists",
                path=HARBOR_AGENT_EQUIPMENT_AB_PROTOTYPE_RESULTS_PATH,
            ),
        )
        self.assertEqual(
            result_map["harbor_agent_equipment_ab_prototype_results:ledger"],
            CheckResult(
                name="harbor_agent_equipment_ab_prototype_results:ledger",
                ok=True,
                detail="present",
                path=HARBOR_AGENT_EQUIPMENT_AB_PROTOTYPE_RESULTS_PATH,
            ),
        )

    def test_live_validator_run_includes_harbor_atif_job_artifacts_evaluation(self):
        repo_root = Path(__file__).resolve().parents[1]

        results = run(repo_root, final_closeout=True)
        result_map = {result.name: result for result in results}

        self.assertEqual(
            result_map[f"required_path:{HARBOR_ATIF_JOB_ARTIFACTS_EVALUATION_PATH}"],
            CheckResult(
                name=f"required_path:{HARBOR_ATIF_JOB_ARTIFACTS_EVALUATION_PATH}",
                ok=True,
                detail="exists",
                path=HARBOR_ATIF_JOB_ARTIFACTS_EVALUATION_PATH,
            ),
        )
        self.assertEqual(
            result_map["harbor_atif_job_artifacts_evaluation:ledger"],
            CheckResult(
                name="harbor_atif_job_artifacts_evaluation:ledger",
                ok=True,
                detail="present",
                path=HARBOR_ATIF_JOB_ARTIFACTS_EVALUATION_PATH,
            ),
        )

    def test_live_validator_run_includes_harbor_driver_gate(self):
        repo_root = Path(__file__).resolve().parents[1]

        results = run(repo_root, final_closeout=True)
        result_map = {result.name: result for result in results}

        self.assertEqual(
            result_map[f"required_path:{HARBOR_DRIVER_GATE_PATH}"],
            CheckResult(
                name=f"required_path:{HARBOR_DRIVER_GATE_PATH}",
                ok=True,
                detail="exists",
                path=HARBOR_DRIVER_GATE_PATH,
            ),
        )
        self.assertEqual(
            result_map["harbor_driver_gate:ledger"],
            CheckResult(
                name="harbor_driver_gate:ledger",
                ok=True,
                detail="present",
                path=HARBOR_DRIVER_GATE_PATH,
            ),
        )

    def test_live_validator_run_includes_harbor_final_disposition(self):
        repo_root = Path(__file__).resolve().parents[1]

        results = run(repo_root, final_closeout=True)
        result_map = {result.name: result for result in results}

        self.assertEqual(
            result_map[f"required_path:{HARBOR_FINAL_DISPOSITION_PATH}"],
            CheckResult(
                name=f"required_path:{HARBOR_FINAL_DISPOSITION_PATH}",
                ok=True,
                detail="exists",
                path=HARBOR_FINAL_DISPOSITION_PATH,
            ),
        )
        self.assertEqual(
            result_map["harbor_final_disposition:ledger"],
            CheckResult(
                name="harbor_final_disposition:ledger",
                ok=True,
                detail="present",
                path=HARBOR_FINAL_DISPOSITION_PATH,
            ),
        )

    def test_live_validator_run_includes_external_tool_evaluation_surfaces(self):
        repo_root = Path(__file__).resolve().parents[1]

        results = run(repo_root, final_closeout=True)
        result_map = {result.name: result for result in results}

        self.assertEqual(
            result_map[f"required_path:{EXTERNAL_TOOL_EVALUATION_PATH}"],
            CheckResult(
                name=f"required_path:{EXTERNAL_TOOL_EVALUATION_PATH}",
                ok=True,
                detail="exists",
                path=EXTERNAL_TOOL_EVALUATION_PATH,
            ),
        )
        self.assertEqual(
            result_map["external_tool_evaluation:contract"],
            CheckResult(
                name="external_tool_evaluation:contract",
                ok=True,
                detail="present",
                path=EXTERNAL_TOOL_EVALUATION_PATH,
            ),
        )
        self.assertEqual(
            result_map[f"required_path:{HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH}"],
            CheckResult(
                name=f"required_path:{HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH}",
                ok=True,
                detail="exists",
                path=HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH,
            ),
        )
        self.assertEqual(
            result_map["harbor_external_tool_evaluation_record:record"],
            CheckResult(
                name="harbor_external_tool_evaluation_record:record",
                ok=True,
                detail="present",
                path=HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH,
            ),
        )

    def test_live_validator_help_names_integrity_boundaries(self):
        completed = subprocess.run(
            [sys.executable, "tools/validate_armory_integrity.py", "--help"],
            cwd=Path(__file__).resolve().parents[1],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Validate Agent Armory Integrity.", completed.stdout)
        self.assertIn("Forge Integrity Validation", completed.stdout)
        self.assertNotIn("Forge Seed", completed.stdout)

    def test_live_validator_rejects_seed_compatibility_flags(self):
        completed = subprocess.run(
            [sys.executable, "tools/validate_armory_integrity.py", "--source-bearing"],
            cwd=Path(__file__).resolve().parents[1],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("unrecognized arguments: --source-bearing", completed.stderr)

    def test_live_surfaces_do_not_reference_retired_validator_command(self):
        root = Path(__file__).resolve().parents[1]
        live_surfaces = [
            "CONTEXT.md",
            "docs/story-closeout.md",
            "docs/security/threat-model.md",
            "specs/agent-equipment-config/interface-decision-record.md",
            "specs/agent-equipment-config/validation-plan.md",
            "specs/issue-tracker-ops/capability-card.md",
            "specs/issue-tracker-ops/validation-plan.md",
            "specs/vanilla-harness-capability-profiles/README.md",
            "specs/vanilla-harness-capability-profiles/validation-plan.md",
            "specs/vanilla-harness-capability-profiles/closeout-evidence-plan.md",
        ]
        operational_surfaces = [relative_path for relative_path in live_surfaces if relative_path != "CONTEXT.md"]

        offenders = [
            relative_path
            for relative_path in live_surfaces
            if "validate_forge_seed" in (root / relative_path).read_text(encoding="utf-8")
        ]
        offenders.extend(
            relative_path
            for relative_path in operational_surfaces
            if "Seed Validation" in (root / relative_path).read_text(encoding="utf-8")
        )

        self.assertEqual(offenders, [])


class ValidatorPrimitiveTests(unittest.TestCase):
    def test_validate_skill_eval_methodology_source_intake_reports_missing_doc(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = validate_skill_eval_methodology_source_intake(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="skill_eval_methodology_source_intake:path",
                    ok=False,
                    detail="missing",
                    path=SKILL_EVAL_METHODOLOGY_SOURCE_INTAKE_PATH,
                )
            ],
        )

    def test_validate_plugin_creator_source_intake_reports_missing_doc(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = validate_plugin_creator_source_intake(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="plugin_creator_source_intake:path",
                    ok=False,
                    detail="missing",
                    path=PLUGIN_CREATOR_SOURCE_INTAKE_PATH,
                )
            ],
        )

    def test_validate_plugin_creator_source_intake_requires_ledger_shape(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / PLUGIN_CREATOR_SOURCE_INTAKE_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                "# Plugin-Creator Source Intake\n\nStatus: Draft\n\n## Scope Boundary\n\nIncomplete.\n",
                encoding="utf-8",
            )

            results = validate_plugin_creator_source_intake(root)

        self.assertIn(
            CheckResult(
                name="plugin_creator_source_intake:status",
                ok=False,
                detail="status must be Source Disposition Ledger",
                path=PLUGIN_CREATOR_SOURCE_INTAKE_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                name="plugin_creator_source_intake:section:Portable Source Inventory",
                ok=False,
                detail="missing section: Portable Source Inventory",
                path=PLUGIN_CREATOR_SOURCE_INTAKE_PATH,
            ),
            results,
        )

    def test_validate_harbor_jig_source_map_reports_missing_doc(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = validate_harbor_jig_source_map(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="harbor_jig_source_map:path",
                    ok=False,
                    detail="missing",
                    path=HARBOR_JIG_SOURCE_MAP_PATH,
                )
            ],
        )

    def test_validate_harbor_reward_kit_evaluation_reports_missing_doc(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = validate_harbor_reward_kit_evaluation(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="harbor_reward_kit_evaluation:path",
                    ok=False,
                    detail="missing",
                    path=HARBOR_REWARD_KIT_EVALUATION_PATH,
                )
            ],
        )

    def test_validate_harbor_reward_kit_evaluation_requires_ledger_shape(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_REWARD_KIT_EVALUATION_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                "# Harbor Reward Kit Evaluation\n\nStatus: Draft\n\n## Scope Boundary\n\nIncomplete.\n",
                encoding="utf-8",
            )

            results = validate_harbor_reward_kit_evaluation(root)

        self.assertIn(
            CheckResult(
                name="harbor_reward_kit_evaluation:status",
                ok=False,
                detail="status must be Source Disposition Ledger",
                path=HARBOR_REWARD_KIT_EVALUATION_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                name="harbor_reward_kit_evaluation:section:Portable Source Inventory",
                ok=False,
                detail="missing section: Portable Source Inventory",
                path=HARBOR_REWARD_KIT_EVALUATION_PATH,
            ),
            results,
        )

    def test_validate_harbor_reward_kit_evaluation_requires_coverage_terms(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_REWARD_KIT_EVALUATION_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                textwrap.dedent(
                    """\
                    # Harbor Reward Kit Evaluation

                    Status: Source Disposition Ledger

                    ## Scope Boundary

                    Reward Kit evaluation for #188.

                    ## Portable Source Inventory

                    Reward Kit, judge TOML, LLM judges, agent judges, trajectory evaluation,
                    isolation, scoring, output files, provider routing, comparison behavior,
                    open Harbor PRs/issues, and security risks.

                    ## Reward Kit Fit Matrix

                    Assertion Provider, Learned Oracle, wrap, borrow concepts, defer, and reject.

                    ## Open Harbor PRs Issues And Security Risks

                    Harbor PRs and issues.

                    ## Downstream Routing

                    #188, #165, #166, and #191.

                    ## Deferments And Nonportable Claims

                    No Harbor execution.

                    ## Security Privacy And Durability

                    raw logs, local paths, credentials, trajectories, transcripts, model outputs,
                    provider account state, and external service usage.

                    ## Closeout Evidence

                    TDD, Prototype, Impeccable, Codex Security, and Ralph Review Cycle.
                    """
                ),
                encoding="utf-8",
            )

            results = validate_harbor_reward_kit_evaluation(root)

        self.assertIn(
            CheckResult(
                name="harbor_reward_kit_evaluation:coverage:deterministic criteria",
                ok=False,
                detail="missing coverage term: deterministic criteria",
                path=HARBOR_REWARD_KIT_EVALUATION_PATH,
            ),
            results,
        )

    def test_validate_harbor_reward_kit_evaluation_requires_routes_and_sources(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_REWARD_KIT_EVALUATION_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                textwrap.dedent(
                    """\
                    # Harbor Reward Kit Evaluation

                    Status: Source Disposition Ledger

                    ## Scope Boundary

                    Reward Kit evaluation for #188.

                    ## Portable Source Inventory

                    [Judge Criteria](https://www.harborframework.com/docs/rewardkit/judge-criteria)
                    and [Harbor source](https://github.com/harbor-framework/harbor) cover
                    deterministic criteria, judge TOML, LLM judges, agent judges,
                    trajectory evaluation, isolation, scoring, output files, provider
                    routing, comparison behavior, open Harbor PRs/issues, and security risks.

                    ## Reward Kit Fit Matrix

                    Assertion Provider, Learned Oracle, wrap, borrow concepts, defer, and reject.

                    ## Open Harbor PRs Issues And Security Risks

                    Harbor PRs and issues.

                    ## Downstream Routing

                    #188 and #191.

                    ## Deferments And Nonportable Claims

                    No Harbor execution.

                    ## Security Privacy And Durability

                    raw logs, local paths, credentials, trajectories, transcripts, model outputs,
                    provider account state, and external service usage.

                    ## Closeout Evidence

                    TDD, Prototype, Impeccable, Codex Security, and Ralph Review Cycle.
                    """
                ),
                encoding="utf-8",
            )

            results = validate_harbor_reward_kit_evaluation(root)

        self.assertIn(
            CheckResult(
                name="harbor_reward_kit_evaluation:routing:#165",
                ok=False,
                detail="missing downstream route: #165",
                path=HARBOR_REWARD_KIT_EVALUATION_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                name="harbor_reward_kit_evaluation:source:https://www.harborframework.com/docs/rewardkit",
                ok=False,
                detail="missing source URL: https://www.harborframework.com/docs/rewardkit",
                path=HARBOR_REWARD_KIT_EVALUATION_PATH,
            ),
            results,
        )

    def test_validate_harbor_reward_kit_evaluation_rejects_host_local_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_REWARD_KIT_EVALUATION_PATH
            path.parent.mkdir(parents=True)
            template = textwrap.dedent(
                """\
                # Harbor Reward Kit Evaluation

                Status: Source Disposition Ledger

                ## Scope Boundary

                Reward Kit evaluation for #188.

                ## Portable Source Inventory

                [Reward Kit](https://www.harborframework.com/docs/rewardkit),
                [Judge Criteria](https://www.harborframework.com/docs/rewardkit/judge-criteria),
                and [Harbor source](https://github.com/harbor-framework/harbor)
                cover deterministic criteria, judge TOML, LLM judges, agent judges,
                trajectory evaluation, isolation, scoring, output files, provider routing,
                comparison behavior, open Harbor PRs/issues, and security risks.

                ## Reward Kit Fit Matrix

                Assertion Provider, Learned Oracle, wrap, borrow concepts, defer, and reject.

                ## Open Harbor PRs Issues And Security Risks

                Harbor PRs and issues.

                ## Downstream Routing

                #188, #165, #166, and #191.

                ## Deferments And Nonportable Claims

                No Harbor execution.

                ## Security Privacy And Durability

                Scratch path: `{host_local_path}`. raw logs, local paths, credentials,
                trajectories, transcripts, model outputs, provider account state, and
                external service usage.

                ## Closeout Evidence

                TDD, Prototype, Impeccable, Codex Security, and Ralph Review Cycle.
                """
            )

            for host_local_path in (
                "/home/agent/harbor/rewardkit-output.json",
                r"C:\Users\agent\harbor\rewardkit-output.json",
            ):
                with self.subTest(host_local_path=host_local_path):
                    path.write_text(template.format(host_local_path=host_local_path), encoding="utf-8")
                    results = validate_harbor_reward_kit_evaluation(root)

                    self.assertIn(
                        CheckResult(
                            name="harbor_reward_kit_evaluation:portable_paths",
                            ok=False,
                            detail="ledger must not preserve host-local paths",
                            path=HARBOR_REWARD_KIT_EVALUATION_PATH,
                        ),
                        results,
                    )

    def test_validate_harbor_reward_kit_evaluation_accepts_complete_ledger(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_REWARD_KIT_EVALUATION_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                textwrap.dedent(
                    """\
                    # Harbor Reward Kit Evaluation

                    Status: Source Disposition Ledger

                    ## Scope Boundary

                    Reward Kit evaluation for #188.

                    ## Portable Source Inventory

                    [Reward Kit](https://www.harborframework.com/docs/rewardkit),
                    [Judge Criteria](https://www.harborframework.com/docs/rewardkit/judge-criteria),
                    and [Harbor source](https://github.com/harbor-framework/harbor)
                    cover deterministic criteria, judge TOML, LLM judges, agent judges,
                    trajectory evaluation, isolation, scoring, output files, provider routing,
                    comparison behavior, open Harbor PRs/issues, and security risks.

                    ## Reward Kit Fit Matrix

                    Assertion Provider, Learned Oracle, wrap, borrow concepts, defer, and reject.

                    ## Open Harbor PRs Issues And Security Risks

                    Harbor PRs and issues.

                    ## Downstream Routing

                    #188, #165, #166, and #191.

                    ## Deferments And Nonportable Claims

                    No Harbor execution.

                    ## Security Privacy And Durability

                    raw logs, local paths, credentials, trajectories, transcripts, model outputs,
                    provider account state, and external service usage.

                    ## Closeout Evidence

                    TDD, Prototype, Impeccable, Codex Security, and Ralph Review Cycle.
                    """
                ),
                encoding="utf-8",
            )

            results = validate_harbor_reward_kit_evaluation(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="harbor_reward_kit_evaluation:ledger",
                    ok=True,
                    detail="present",
                    path=HARBOR_REWARD_KIT_EVALUATION_PATH,
                )
            ],
        )

    def test_validate_harbor_atif_job_artifacts_evaluation_reports_missing_doc(self):
        validator = importlib.import_module("tools.validate_armory_integrity")
        self.assertTrue(
            hasattr(validator, "validate_harbor_atif_job_artifacts_evaluation")
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = validator.validate_harbor_atif_job_artifacts_evaluation(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="harbor_atif_job_artifacts_evaluation:path",
                    ok=False,
                    detail="missing",
                    path=validator.HARBOR_ATIF_JOB_ARTIFACTS_EVALUATION_PATH,
                )
            ],
        )

    def test_validate_harbor_atif_job_artifacts_evaluation_requires_ledger_shape(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_ATIF_JOB_ARTIFACTS_EVALUATION_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                "# Harbor ATIF And Job Artifact Evaluation\n\nStatus: Draft\n\n## Scope Boundary\n\nIncomplete.\n",
                encoding="utf-8",
            )

            results = validate_harbor_atif_job_artifacts_evaluation(root)

        self.assertIn(
            CheckResult(
                name="harbor_atif_job_artifacts_evaluation:status",
                ok=False,
                detail="status must be Source Disposition Ledger",
                path=HARBOR_ATIF_JOB_ARTIFACTS_EVALUATION_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                name="harbor_atif_job_artifacts_evaluation:section:Portable Source Inventory",
                ok=False,
                detail="missing section: Portable Source Inventory",
                path=HARBOR_ATIF_JOB_ARTIFACTS_EVALUATION_PATH,
            ),
            results,
        )

    def test_validate_harbor_atif_job_artifacts_evaluation_requires_coverage_routes_and_sources(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_ATIF_JOB_ARTIFACTS_EVALUATION_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                textwrap.dedent(
                    """\
                    # Harbor ATIF And Job Artifact Evaluation

                    Status: Source Disposition Ledger

                    ## Scope Boundary

                    Issue #189 evaluates Harbor result files.

                    ## Portable Source Inventory

                    [Harbor Evals](https://www.harborframework.com/docs/run-jobs/run-evals)
                    and [Harbor source](https://github.com/harbor-framework/harbor)
                    cover result.json and trajectory.json.

                    ## Harbor Output Fit Matrix

                    job result and trial result.

                    ## Compatibility Gaps

                    pass and fail only.

                    ## Evidence Durability

                    raw logs and model outputs are scratch.

                    ## Viewer And Review Surface Notes

                    Viewer screenshots are scratch.

                    ## Downstream Routing

                    #189 and #191.

                    ## Deferments And Nonportable Claims

                    No schema change.

                    ## Security Privacy And Durability

                    local paths are scratch.

                    ## Closeout Evidence

                    TDD, Prototype, Impeccable, Codex Security, and Ralph Review Cycle.
                    """
                ),
                encoding="utf-8",
            )

            results = validate_harbor_atif_job_artifacts_evaluation(root)

        self.assertIn(
            CheckResult(
                name="harbor_atif_job_artifacts_evaluation:coverage:artifact manifest.json",
                ok=False,
                detail="missing coverage term: artifact manifest.json",
                path=HARBOR_ATIF_JOB_ARTIFACTS_EVALUATION_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                name="harbor_atif_job_artifacts_evaluation:routing:#164",
                ok=False,
                detail="missing downstream route: #164",
                path=HARBOR_ATIF_JOB_ARTIFACTS_EVALUATION_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                name="harbor_atif_job_artifacts_evaluation:source:https://www.harborframework.com/docs/run-jobs/results-and-artifacts",
                ok=False,
                detail="missing source URL: https://www.harborframework.com/docs/run-jobs/results-and-artifacts",
                path=HARBOR_ATIF_JOB_ARTIFACTS_EVALUATION_PATH,
            ),
            results,
        )

    def test_validate_harbor_atif_job_artifacts_evaluation_rejects_host_local_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_ATIF_JOB_ARTIFACTS_EVALUATION_PATH
            path.parent.mkdir(parents=True)
            template = self.valid_harbor_atif_job_artifacts_evaluation().replace(
                "raw tool output remains scratch evidence.",
                "raw tool output remains scratch evidence. Scratch path: `{host_local_path}`.",
            )

            for host_local_path in (
                "/home/agent/harbor/jobs/job-a/result.json",
                r"C:\Users\agent\harbor\jobs\job-a\result.json",
            ):
                with self.subTest(host_local_path=host_local_path):
                    path.write_text(
                        template.format(host_local_path=host_local_path),
                        encoding="utf-8",
                    )
                    results = validate_harbor_atif_job_artifacts_evaluation(root)

                    self.assertIn(
                        CheckResult(
                            name="harbor_atif_job_artifacts_evaluation:portable_paths",
                            ok=False,
                            detail="ledger must not preserve host-local paths",
                            path=HARBOR_ATIF_JOB_ARTIFACTS_EVALUATION_PATH,
                        ),
                        results,
                    )
    def test_validate_harbor_atif_job_artifacts_evaluation_accepts_complete_ledger(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_ATIF_JOB_ARTIFACTS_EVALUATION_PATH
            path.parent.mkdir(parents=True)
            path.write_text(self.valid_harbor_atif_job_artifacts_evaluation(), encoding="utf-8")

            results = validate_harbor_atif_job_artifacts_evaluation(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="harbor_atif_job_artifacts_evaluation:ledger",
                    ok=True,
                    detail="present",
                    path=HARBOR_ATIF_JOB_ARTIFACTS_EVALUATION_PATH,
                )
            ],
        )

    @staticmethod
    def valid_harbor_atif_job_artifacts_evaluation() -> str:
        return textwrap.dedent(
            """\
            # Harbor ATIF And Job Artifact Evaluation

            Status: Source Disposition Ledger

            ## Scope Boundary

            Issue #189 evaluates Harbor ATIF and job artifacts for Jig Runner results.

            ## Portable Source Inventory

            [Harbor Evals](https://www.harborframework.com/docs/run-jobs/run-evals),
            [Artifact Collection](https://www.harborframework.com/docs/run-jobs/results-and-artifacts),
            [ATIF RFC](https://github.com/harbor-framework/harbor/blob/main/rfcs/0001-trajectory-format.md),
            and [Harbor source](https://github.com/harbor-framework/harbor) cover
            result.json, trajectory.json, artifact manifest.json, job result, trial result,
            ATIF-v1.7, best-effort collection, viewer affordances, raw logs, model outputs,
            viewer screenshots, and host-local paths.

            ## Harbor Output Fit Matrix

            pass, fail, inconclusive, disagreement, oracle_error, adjudicator_error,
            infra_error, fixture_error, sandbox_error, timeout, and flaky are mapped
            against Harbor job result, trial result, trajectory.json, and artifact manifest.json.

            ## Compatibility Gaps

            Harbor output is source material for #164, not a replacement result contract.

            ## Evidence Durability

            raw logs, local paths, trajectories, model outputs, viewer screenshots,
            and raw tool output remains scratch evidence.

            ## Viewer And Review Surface Notes

            Viewer affordances can inform #169 after result artifacts exist.

            ## Downstream Routing

            #189, #164, #169, and #191.

            ## Deferments And Nonportable Claims

            No PRD, ADR, schema, Harbor adoption, or UI implementation is accepted.

            ## Security Privacy And Durability

            credentials, raw logs, local paths, trajectories, transcripts, model outputs,
            viewer screenshots, provider account state, and external service usage stay scratch.

            ## Closeout Evidence

            TDD, Prototype, Impeccable, Codex Security, and Ralph Review Cycle.
            """
        )

    def test_validate_harbor_driver_gate_reports_missing_doc(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = validate_harbor_driver_gate(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="harbor_driver_gate:path",
                    ok=False,
                    detail="missing",
                    path=HARBOR_DRIVER_GATE_PATH,
                )
            ],
        )

    def test_validate_harbor_driver_gate_requires_ledger_shape(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_DRIVER_GATE_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                "# Harbor Driver Gate\n\nStatus: Draft\n\n## Scope Boundary\n\nIncomplete.\n",
                encoding="utf-8",
            )

            results = validate_harbor_driver_gate(root)

        self.assertIn(
            CheckResult(
                name="harbor_driver_gate:status",
                ok=False,
                detail="status must be Source Disposition Ledger",
                path=HARBOR_DRIVER_GATE_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                name="harbor_driver_gate:section:Portable Source Inventory",
                ok=False,
                detail="missing section: Portable Source Inventory",
                path=HARBOR_DRIVER_GATE_PATH,
            ),
            results,
        )

    def test_validate_harbor_driver_gate_requires_coverage_routes_sources_and_recommendation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_DRIVER_GATE_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                textwrap.dedent(
                    """\
                    # Harbor Driver Gate

                    Status: Source Disposition Ledger

                    ## Scope Boundary

                    Issue #190 evaluates Harbor as a driver.

                    ## Portable Source Inventory

                    [Cloud Sandboxes](https://www.harborframework.com/docs/run-jobs/cloud-sandboxes)
                    and [Tasks](https://www.harborframework.com/docs/tasks)
                    cover Docker, cloud sandbox, Daytona, Modal, E2B, Runloop,
                    Tensorlake, Islo, CoreWeave Sandboxes, W&B Sandboxes,
                    network policy, no-network, allowlist, sidecar, cleanup,
                    reproducibility, portability, Codex workflow compatibility,
                    maintenance cost, Docker credentials, and verifier/reward tampering.

                    ## Driver Gate Matrix

                    ADR 0022 and Jig Driver evidence.

                    ## Recommendation

                    Research reference.

                    ## Security Review

                    credentials and artifact integrity.

                    ## Downstream Routing

                    #190 and #191.

                    ## Deferments And Nonportable Claims

                    No Harbor adoption.

                    ## Security Privacy And Durability

                    raw logs and local paths are scratch.

                    ## Closeout Evidence

                    TDD, Prototype, Impeccable, Codex Security, and Ralph Review Cycle.
                    """
                ),
                encoding="utf-8",
            )

            results = validate_harbor_driver_gate(root)

        self.assertIn(
            CheckResult(
                name="harbor_driver_gate:coverage:artifact manifest.json",
                ok=False,
                detail="missing coverage term: artifact manifest.json",
                path=HARBOR_DRIVER_GATE_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                name="harbor_driver_gate:routing:#163",
                ok=False,
                detail="missing downstream route: #163",
                path=HARBOR_DRIVER_GATE_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                name="harbor_driver_gate:source:https://www.harborframework.com/docs/run-jobs/results-and-artifacts",
                ok=False,
                detail="missing source URL: https://www.harborframework.com/docs/run-jobs/results-and-artifacts",
                path=HARBOR_DRIVER_GATE_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                name="harbor_driver_gate:recommendation",
                ok=False,
                detail="recommendation must defer Harbor as the first Jig Driver",
                path=HARBOR_DRIVER_GATE_PATH,
            ),
            results,
        )

    def test_validate_harbor_driver_gate_rejects_host_local_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_DRIVER_GATE_PATH
            path.parent.mkdir(parents=True)
            template = self.valid_harbor_driver_gate().replace(
                "raw tool output remains scratch evidence.",
                "raw tool output remains scratch evidence. Scratch path: `{host_local_path}`.",
            )

            for host_local_path in (
                "/home/agent/harbor/jobs/job-a/result.json",
                r"C:\Users\agent\harbor\jobs\job-a\result.json",
            ):
                with self.subTest(host_local_path=host_local_path):
                    path.write_text(
                        template.format(host_local_path=host_local_path),
                        encoding="utf-8",
                    )
                    results = validate_harbor_driver_gate(root)

                    self.assertIn(
                        CheckResult(
                            name="harbor_driver_gate:portable_paths",
                            ok=False,
                            detail="ledger must not preserve host-local paths",
                            path=HARBOR_DRIVER_GATE_PATH,
                        ),
                        results,
                    )
            path.write_text(
                self.valid_harbor_driver_gate()
                + "\n```text\n/tmp/harbor/jobs/job-a/result.json\n```\n",
                encoding="utf-8",
            )
            results = validate_harbor_driver_gate(root)

            self.assertIn(
                CheckResult(
                    name="harbor_driver_gate:portable_paths",
                    ok=False,
                    detail="ledger must not preserve host-local paths",
                    path=HARBOR_DRIVER_GATE_PATH,
                ),
                results,
            )

    def test_validate_harbor_driver_gate_accepts_complete_ledger(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_DRIVER_GATE_PATH
            path.parent.mkdir(parents=True)
            path.write_text(self.valid_harbor_driver_gate(), encoding="utf-8")

            results = validate_harbor_driver_gate(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="harbor_driver_gate:ledger",
                    ok=True,
                    detail="present",
                    path=HARBOR_DRIVER_GATE_PATH,
                )
            ],
        )

    @staticmethod
    def valid_harbor_driver_gate() -> str:
        return textwrap.dedent(
            """\
            # Harbor Driver Gate

            Status: Source Disposition Ledger

            ## Scope Boundary

            Issue #190 applies ADR 0022 to Harbor as a Jig Driver candidate.

            ## Portable Source Inventory

            [Cloud Sandboxes](https://www.harborframework.com/docs/run-jobs/cloud-sandboxes),
            [Tasks](https://www.harborframework.com/docs/tasks),
            [Artifact Collection](https://www.harborframework.com/docs/run-jobs/results-and-artifacts),
            [Docker credentials issue](https://github.com/harbor-framework/harbor/issues/1687),
            [Sidecar state issue](https://github.com/harbor-framework/harbor/issues/1694),
            [Verifier tampering issue](https://github.com/harbor-framework/harbor/issues/1779),
            and [Modal network issue](https://github.com/harbor-framework/harbor/issues/1795)
            cover Docker, cloud sandbox, Daytona, Modal, E2B, Runloop, Tensorlake,
            Islo, CoreWeave Sandboxes, W&B Sandboxes, network policy, no-network,
            allowlist, sidecar, artifact manifest.json, best-effort collection,
            cleanup, reproducibility, portability, Codex workflow compatibility,
            maintenance cost, Docker credentials, verifier/reward tampering,
            artifact integrity, credential handling, unsupported isolation claims,
            and provider account state.

            ## Driver Gate Matrix

            The Jig Driver gate covers safety, isolation from host state,
            reproducibility, simplicity, local iteration speed, observability,
            effect controls, fixture and mock support, cleanup reliability,
            portability, Codex workflow compatibility, and maintenance cost.

            ## Recommendation

            The recommendation is to defer Harbor as the first Jig Driver and
            retain Harbor as a research reference plus supporting driver-component
            source material.

            ## Security Review

            The security review covers verifier/reward tampering, credential
            handling, network effects, cloud provider trust, local path disclosure,
            artifact integrity, and unsupported isolation claims.

            ## Downstream Routing

            #183 receives this driver-gate evidence. #190 owns this ledger. #163
            can use it before selecting a first Jig Driver. #191 owns final Harbor
            projection.

            ## Deferments And Nonportable Claims

            No Harbor adoption, ADR change, Agent Test Jig issue mutation, Harbor
            execution, cloud sandbox run, provider account claim, or UI
            implementation is accepted by this ledger.

            ## Security Privacy And Durability

            credentials, raw logs, local paths, trajectories, transcripts, model
            outputs, viewer screenshots, provider account state, external service
            usage, and raw tool output remains scratch evidence.

            ## Closeout Evidence

            TDD, Prototype, Impeccable, Codex Security, and Ralph Review Cycle.
            """
        )

    @staticmethod
    def valid_harbor_ab_prototype_results() -> str:
        return textwrap.dedent(
            """\
            # Harbor Agent Equipment A/B Prototype Results

            Status: Source Disposition Ledger

            ## Scope Boundary

            Issue #187 records a bounded Harbor Agent Equipment A/B prototype.
            This is not a Harbor adoption decision, Armory structured result
            contract, public API, PRD, ADR, or proof that the equipped skill is
            generally better.

            ## Prototype Setup

            Harbor CLI version 0.13.0 was installed with uv tool install harbor.
            [Harbor Getting Started](https://www.harborframework.com/docs/getting-started),
            [Harbor Tasks](https://www.harborframework.com/docs/tasks),
            [Harbor Agents](https://www.harborframework.com/docs/agents),
            [Harbor Evals](https://www.harborframework.com/docs/evals), and
            [Harbor source](https://github.com/harbor-framework/harbor) were the
            source inputs. The task used schema_version = "1.3", Docker
            environment, no-network runtime network mode, explicit timeouts,
            custom agent import paths, a deterministic shared agent, baseline
            without equipment, and equipped run with
            skills/issue-ops-workflow-executor/SKILL.md as the only variable.

            ## Command Summary

            harbor --help, harbor run --help, harbor --version, docker ps,
            docker compose version, podman ps, baseline harbor run, equipped
            harbor run, job result.json inspection, trial result.json inspection,
            verifier reward.json inspection, artifact manifest.json inspection,
            collected report artifact inspection, and trajectory search were run.

            ## Result Summary

            The baseline Harbor job completed one trial with reward 0.5714,
            score 0.5714, report_exists 1.0, artifact_written 1.0,
            required_sections_present 3, required_sections_missing 4, and no
            exception. The equipped Harbor job completed one trial with reward
            1.0, score 1.0, report_exists 1.0, artifact_written 1.0,
            required_sections_present 7, required_sections_missing 0, and no
            exception. Both artifact manifest.json files reported status ok for
            the /logs/artifacts collection source. No trajectory or ATIF file was
            emitted by this deterministic custom-agent prototype.

            ## Evidence Classification

            Durable project evidence is this sanitized closeout ledger and the
            Harbor evaluation record update. Scratch task files, raw jobs, raw
            logs, raw reward files, raw artifact reports, trial ids, local
            absolute paths, trajectories, transcripts, model outputs, provider
            credentials, and container runtime state are instance-scoped scratch
            evidence and are not committed.

            ## Runtime Controls And Boundaries

            The runtime used a local container-backed Harbor Docker environment
            through the local Podman-backed Docker/Compose shim. Task runtime
            network mode was no-network. Image availability and container
            runtime access were host prerequisites and are not Armory adoption
            evidence.

            ## Downstream Routing

            #187 accepts the bounded prototype evidence. #189 owns trajectory
            and artifact contract fit. #190 owns Harbor driver gate evidence.
            #191 owns final Harbor disposition. #183 remains the parent Harbor
            evaluation route.

            ## Deferments And Nonportable Claims

            Do not infer general skill quality, production jig driver fit,
            Harbor adoption, ATIF contract compatibility, provider behavior,
            cloud sandbox behavior, registry behavior, or verifier hardening
            from this prototype. Those claims remain deferred to #189, #190,
            and #191.

            ## Security Privacy And Durability

            The prototype used no provider credentials, no LLM calls, no cloud
            sandboxes, no Harbor registry writes, and no model access. The task
            runtime used no-network. Durable notes exclude host-local paths, raw
            logs, raw jobs, reward files, trajectories, transcripts, model
            outputs, credentials, provider account state, and sensitive external
            service usage details.

            ## Closeout Evidence

            Evidence includes Harbor CLI help and version probes, local
            container runtime checks, baseline and equipped Harbor run results,
            job result.json inspection, trial result.json inspection, verifier
            reward.json inspection, artifact manifest.json inspection, collected
            report artifact inspection, trajectory absence check, validator TDD,
            Armory integrity validation, security review, Change Set
            Documentation Closeout, Cross-Boundary Coherence Ralph Review, and
            Story Quality Ralph Review.
            """
        )

    def test_validate_harbor_agent_equipment_ab_prototype_results_reports_missing_doc(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = validate_harbor_agent_equipment_ab_prototype_results(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="harbor_agent_equipment_ab_prototype_results:path",
                    ok=False,
                    detail="missing",
                    path=HARBOR_AGENT_EQUIPMENT_AB_PROTOTYPE_RESULTS_PATH,
                )
            ],
        )

    def test_validate_harbor_agent_equipment_ab_prototype_results_requires_ledger_shape(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_AGENT_EQUIPMENT_AB_PROTOTYPE_RESULTS_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                "# Harbor Agent Equipment A/B Prototype Results\n\nStatus: Draft\n\n## Scope Boundary\n\nIncomplete.\n",
                encoding="utf-8",
            )

            results = validate_harbor_agent_equipment_ab_prototype_results(root)

        self.assertIn(
            CheckResult(
                name="harbor_agent_equipment_ab_prototype_results:status",
                ok=False,
                detail="status must be Source Disposition Ledger",
                path=HARBOR_AGENT_EQUIPMENT_AB_PROTOTYPE_RESULTS_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                name="harbor_agent_equipment_ab_prototype_results:section:Prototype Setup",
                ok=False,
                detail="missing section: Prototype Setup",
                path=HARBOR_AGENT_EQUIPMENT_AB_PROTOTYPE_RESULTS_PATH,
            ),
            results,
        )

    def test_validate_harbor_agent_equipment_ab_prototype_results_requires_coverage_terms(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_AGENT_EQUIPMENT_AB_PROTOTYPE_RESULTS_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                self.valid_harbor_ab_prototype_results().replace("no-network", "network boundary"),
                encoding="utf-8",
            )

            results = validate_harbor_agent_equipment_ab_prototype_results(root)

        self.assertIn(
            CheckResult(
                name="harbor_agent_equipment_ab_prototype_results:coverage:no-network",
                ok=False,
                detail="missing coverage term: no-network",
                path=HARBOR_AGENT_EQUIPMENT_AB_PROTOTYPE_RESULTS_PATH,
            ),
            results,
        )

    def test_validate_harbor_agent_equipment_ab_prototype_results_requires_routes_and_sources(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_AGENT_EQUIPMENT_AB_PROTOTYPE_RESULTS_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                self.valid_harbor_ab_prototype_results()
                .replace("#190", "#999")
                .replace("https://www.harborframework.com/docs/tasks", "https://example.invalid/tasks"),
                encoding="utf-8",
            )

            results = validate_harbor_agent_equipment_ab_prototype_results(root)

        self.assertIn(
            CheckResult(
                name="harbor_agent_equipment_ab_prototype_results:routing:#190",
                ok=False,
                detail="missing downstream route: #190",
                path=HARBOR_AGENT_EQUIPMENT_AB_PROTOTYPE_RESULTS_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                name="harbor_agent_equipment_ab_prototype_results:source:https://www.harborframework.com/docs/tasks",
                ok=False,
                detail="missing source URL: https://www.harborframework.com/docs/tasks",
                path=HARBOR_AGENT_EQUIPMENT_AB_PROTOTYPE_RESULTS_PATH,
            ),
            results,
        )

    def test_validate_harbor_agent_equipment_ab_prototype_results_rejects_host_local_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_AGENT_EQUIPMENT_AB_PROTOTYPE_RESULTS_PATH
            path.parent.mkdir(parents=True)

            for host_local_path in (
                "/home/agent/harbor/jobs/result.json",
                r"C:\Users\agent\harbor\jobs\result.json",
            ):
                with self.subTest(host_local_path=host_local_path):
                    path.write_text(
                        self.valid_harbor_ab_prototype_results()
                        + f"\nScratch path: `{host_local_path}`.\n",
                        encoding="utf-8",
                    )
                    results = validate_harbor_agent_equipment_ab_prototype_results(root)

                    self.assertIn(
                        CheckResult(
                            name="harbor_agent_equipment_ab_prototype_results:portable_paths",
                            ok=False,
                            detail="ledger must not preserve host-local paths",
                            path=HARBOR_AGENT_EQUIPMENT_AB_PROTOTYPE_RESULTS_PATH,
                        ),
                        results,
                    )

    def test_validate_harbor_agent_equipment_ab_prototype_results_accepts_complete_ledger(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_AGENT_EQUIPMENT_AB_PROTOTYPE_RESULTS_PATH
            path.parent.mkdir(parents=True)
            path.write_text(self.valid_harbor_ab_prototype_results(), encoding="utf-8")

            results = validate_harbor_agent_equipment_ab_prototype_results(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="harbor_agent_equipment_ab_prototype_results:ledger",
                    ok=True,
                    detail="present",
                    path=HARBOR_AGENT_EQUIPMENT_AB_PROTOTYPE_RESULTS_PATH,
                )
            ],
        )

    def test_validate_harbor_jig_source_map_requires_ledger_shape(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_JIG_SOURCE_MAP_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                "# Harbor Jig Source Map\n\nStatus: Draft\n\n## Scope Boundary\n\nIncomplete.\n",
                encoding="utf-8",
            )

            results = validate_harbor_jig_source_map(root)

        self.assertIn(
            CheckResult(
                name="harbor_jig_source_map:status",
                ok=False,
                detail="status must be Source Disposition Ledger",
                path=HARBOR_JIG_SOURCE_MAP_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                name="harbor_jig_source_map:section:Portable Source Inventory",
                ok=False,
                detail="missing section: Portable Source Inventory",
                path=HARBOR_JIG_SOURCE_MAP_PATH,
            ),
            results,
        )

    def test_validate_harbor_jig_source_map_requires_coverage_terms(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_JIG_SOURCE_MAP_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                textwrap.dedent(
                    """\
                    # Harbor Jig Source Map

                    Status: Source Disposition Ledger

                    ## Scope Boundary

                    Source map only.

                    ## Portable Source Inventory

                    Harbor docs.

                    ## Harbor-To-Armory Concept Map

                    task and dataset.

                    ## Risks And Open Issues

                    Network policy remains open.

                    ## Downstream Routing

                    #183.

                    ## Deferments And Nonportable Claims

                    No prototype.

                    ## Security Privacy And Durability

                    No raw logs.

                    ## Closeout Evidence

                    Reviewed.
                    """
                ),
                encoding="utf-8",
            )

            results = validate_harbor_jig_source_map(root)

        self.assertIn(
            CheckResult(
                name="harbor_jig_source_map:coverage:ATIF trajectory",
                ok=False,
                detail="missing coverage term: ATIF trajectory",
                path=HARBOR_JIG_SOURCE_MAP_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                name="harbor_jig_source_map:coverage:Agent Test Jig",
                ok=False,
                detail="missing coverage term: Agent Test Jig",
                path=HARBOR_JIG_SOURCE_MAP_PATH,
            ),
            results,
        )

    def test_validate_harbor_jig_source_map_requires_exact_issue_routes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_JIG_SOURCE_MAP_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                textwrap.dedent(
                    """\
                    # Harbor Jig Source Map

                    Status: Source Disposition Ledger

                    ## Scope Boundary

                    Source map only.

                    ## Portable Source Inventory

                    task, dataset, agent, trial, job, environment, verifier,
                    Reward Kit, ATIF trajectory, artifacts, scoring, cloud sandbox,
                    network policy, artifact handling, verifier/reward tampering,
                    auth/provider boundaries, Agent Test Jig, Jig Test Plan,
                    Jig Driver, Jig Runner, Assertion Provider, Learned Oracle,
                    Harness Test Suite, Capability Profiling Protocol, Study Report,
                    and Jig Adequacy Report.

                    ## Harbor-To-Armory Concept Map

                    Source-backed concept map.

                    ## Risks And Open Issues

                    Risks recorded.

                    ## Downstream Routing

                    #183, #185a, #186, #187, #188, #189, #190, and #191.

                    ## Deferments And Nonportable Claims

                    No prototype.

                    ## Security Privacy And Durability

                    No raw logs.

                    ## Closeout Evidence

                    Reviewed.
                    """
                ),
                encoding="utf-8",
            )

            results = validate_harbor_jig_source_map(root)

        self.assertIn(
            CheckResult(
                name="harbor_jig_source_map:routing:#185",
                ok=False,
                detail="missing downstream route: #185",
                path=HARBOR_JIG_SOURCE_MAP_PATH,
            ),
            results,
        )

    def test_validate_harbor_jig_source_map_rejects_host_local_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_JIG_SOURCE_MAP_PATH
            path.parent.mkdir(parents=True)
            template = textwrap.dedent(
                """\
                    # Harbor Jig Source Map

                    Status: Source Disposition Ledger

                    ## Scope Boundary

                    Source map only.

                    ## Portable Source Inventory

                    task, dataset, agent, trial, job, environment, verifier,
                    Reward Kit, ATIF trajectory, artifacts, scoring, cloud sandbox,
                    network policy, artifact handling, verifier/reward tampering,
                    auth/provider boundaries, Agent Test Jig, Jig Test Plan,
                    Jig Driver, Jig Runner, Assertion Provider, Learned Oracle,
                    Harness Test Suite, Capability Profiling Protocol, Study Report,
                    and Jig Adequacy Report.

                    Raw scratch lives at `{host_local_path}`.

                    ## Harbor-To-Armory Concept Map

                    Source-backed concept map.

                    ## Risks And Open Issues

                    Risks recorded.

                    ## Downstream Routing

                    #183, #185, #186, #187, #188, #189, #190, and #191.

                    ## Deferments And Nonportable Claims

                    No prototype.

                    ## Security Privacy And Durability

                    No raw logs.

                    ## Closeout Evidence

                    Reviewed.
                    """
            )

            for host_local_path in (
                "/home/agent/harbor/source-map-scratch.json",
                r"C:\Users\agent\harbor\source-map-scratch.json",
            ):
                with self.subTest(host_local_path=host_local_path):
                    path.write_text(template.format(host_local_path=host_local_path), encoding="utf-8")
                    results = validate_harbor_jig_source_map(root)

                    self.assertIn(
                        CheckResult(
                            name="harbor_jig_source_map:portable_paths",
                            ok=False,
                            detail="ledger must not preserve host-local paths",
                            path=HARBOR_JIG_SOURCE_MAP_PATH,
                        ),
                        results,
                    )

    def test_validate_harbor_jig_source_map_accepts_complete_ledger(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_JIG_SOURCE_MAP_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                textwrap.dedent(
                    """\
                    # Harbor Jig Source Map

                    Status: Source Disposition Ledger

                    ## Scope Boundary

                    Source map only.

                    ## Portable Source Inventory

                    Harbor docs cover task, dataset, agent, trial, job, environment,
                    verifier, Reward Kit, ATIF trajectory, artifacts, scoring,
                    cloud sandbox, network policy, artifact handling,
                    verifier/reward tampering, and auth/provider boundaries.

                    ## Harbor-To-Armory Concept Map

                    Agent Test Jig, Jig Test Plan, Jig Driver, Jig Runner,
                    Assertion Provider, Learned Oracle, Harness Test Suite,
                    Capability Profiling Protocol, Study Report, and
                    Jig Adequacy Report are mapped.

                    ## Risks And Open Issues

                    Risks recorded.

                    ## Downstream Routing

                    #183, #185, #186, #187, #188, #189, #190, and #191.

                    ## Deferments And Nonportable Claims

                    No prototype.

                    ## Security Privacy And Durability

                    No raw logs.

                    ## Closeout Evidence

                    Reviewed.
                    """
                ),
                encoding="utf-8",
            )

            results = validate_harbor_jig_source_map(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="harbor_jig_source_map:ledger",
                    ok=True,
                    detail="present",
                    path=HARBOR_JIG_SOURCE_MAP_PATH,
                )
            ],
        )

    def test_validate_harbor_neighbor_tool_catalog_reports_missing_doc(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = validate_harbor_neighbor_tool_catalog(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="harbor_neighbor_tool_catalog:path",
                    ok=False,
                    detail="missing",
                    path=HARBOR_NEIGHBOR_TOOL_CATALOG_PATH,
                )
            ],
        )

    def test_validate_harbor_neighbor_tool_catalog_requires_ledger_shape(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_NEIGHBOR_TOOL_CATALOG_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                "# Harbor Neighbor Catalog\n\nStatus: Draft\n\n## Scope Boundary\n\nIncomplete.\n",
                encoding="utf-8",
            )

            results = validate_harbor_neighbor_tool_catalog(root)

        self.assertIn(
            CheckResult(
                name="harbor_neighbor_tool_catalog:status",
                ok=False,
                detail="status must be Source Disposition Ledger",
                path=HARBOR_NEIGHBOR_TOOL_CATALOG_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                name="harbor_neighbor_tool_catalog:section:Harbor-Neighbor Tool Catalog",
                ok=False,
                detail="missing section: Harbor-Neighbor Tool Catalog",
                path=HARBOR_NEIGHBOR_TOOL_CATALOG_PATH,
            ),
            results,
        )

    def test_validate_harbor_neighbor_tool_catalog_requires_table_fields(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_NEIGHBOR_TOOL_CATALOG_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                textwrap.dedent(
                    """\
                    # Harbor-Neighbor Tool Catalog

                    Status: Source Disposition Ledger

                    ## Scope Boundary

                    Broad eval-platform survey work is out of scope.

                    ## Portable Source Inventory

                    Harbor docs and source URLs.

                    ## Harbor-Neighbor Tool Catalog

                    | entry_id | tool_or_surface | Harbor linkage |
                    | --- | --- | --- |
                    | HN001 | Daytona | Harbor sandbox provider. |

                    ## Role Classification Summary

                    Jig Driver substrate and sandbox provider.

                    ## Open Uncertainties And Follow-Up Conditions

                    No integration approval.

                    ## Downstream Routing

                    #183, #186, #187, #188, #189, #190, and #191.

                    ## Deferments And Nonportable Claims

                    No prototype.

                    ## Security Privacy And Durability

                    No raw logs.

                    ## Closeout Evidence

                    Reviewed.
                    """
                ),
                encoding="utf-8",
            )

            results = validate_harbor_neighbor_tool_catalog(root)

        self.assertIn(
            CheckResult(
                name="harbor_neighbor_tool_catalog:field:source URL",
                ok=False,
                detail="missing catalog field: source URL",
                path=HARBOR_NEIGHBOR_TOOL_CATALOG_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                name="harbor_neighbor_tool_catalog:field:open uncertainty",
                ok=False,
                detail="missing catalog field: open uncertainty",
                path=HARBOR_NEIGHBOR_TOOL_CATALOG_PATH,
            ),
            results,
        )

    def test_validate_harbor_neighbor_tool_catalog_ignores_field_names_outside_headers(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_NEIGHBOR_TOOL_CATALOG_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                textwrap.dedent(
                    """\
                    # Harbor-Neighbor Tool Catalog

                    Status: Source Disposition Ledger

                    ## Scope Boundary

                    Broad eval-platform survey work is out of scope.

                    ## Portable Source Inventory

                    Harbor docs and source URLs.

                    ## Harbor-Neighbor Tool Catalog

                    | entry_id | tool_or_surface | Harbor linkage |
                    | --- | --- | --- |
                    | HN001 | source URL, role classification, evidence quality, likely Armory consumer, open uncertainty | Harbor sandbox provider. |

                    ## Role Classification Summary

                    Jig Driver substrate and sandbox provider.

                    ## Open Uncertainties And Follow-Up Conditions

                    No integration approval.

                    ## Downstream Routing

                    #183, #186, #187, #188, #189, #190, and #191.

                    ## Deferments And Nonportable Claims

                    No prototype.

                    ## Security Privacy And Durability

                    No raw logs.

                    ## Closeout Evidence

                    Reviewed.
                    """
                ),
                encoding="utf-8",
            )

            results = validate_harbor_neighbor_tool_catalog(root)

        self.assertIn(
            CheckResult(
                name="harbor_neighbor_tool_catalog:field:source URL",
                ok=False,
                detail="missing catalog field: source URL",
                path=HARBOR_NEIGHBOR_TOOL_CATALOG_PATH,
            ),
            results,
        )

    def test_validate_harbor_neighbor_tool_catalog_requires_coverage_terms(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_NEIGHBOR_TOOL_CATALOG_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                textwrap.dedent(
                    """\
                    # Harbor-Neighbor Tool Catalog

                    Status: Source Disposition Ledger

                    ## Scope Boundary

                    Broad eval-platform survey work is out of scope.

                    ## Portable Source Inventory

                    Harbor docs and source URLs.

                    ## Harbor-Neighbor Tool Catalog

                    | entry_id | tool_or_surface | Harbor linkage | source URL | role classification | evidence quality | likely Armory consumer | open uncertainty |
                    | --- | --- | --- | --- | --- | --- | --- | --- |
                    | HN001 | Daytona | Harbor sandbox provider. | https://www.harborframework.com/docs/run-jobs/cloud-sandboxes | sandbox provider | harbor-doc-supported | #190 | Provider policy. |

                    ## Role Classification Summary

                    Jig Driver substrate and sandbox provider.

                    ## Open Uncertainties And Follow-Up Conditions

                    No integration approval.

                    ## Downstream Routing

                    #183, #186, #187, #188, #189, #190, and #191.

                    ## Deferments And Nonportable Claims

                    No prototype.

                    ## Security Privacy And Durability

                    No raw logs.

                    ## Closeout Evidence

                    Reviewed.
                    """
                ),
                encoding="utf-8",
            )

            results = validate_harbor_neighbor_tool_catalog(root)

        self.assertIn(
            CheckResult(
                name="harbor_neighbor_tool_catalog:coverage:Reward Kit",
                ok=False,
                detail="missing coverage term: Reward Kit",
                path=HARBOR_NEIGHBOR_TOOL_CATALOG_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                name="harbor_neighbor_tool_catalog:coverage:third-party-fallback",
                ok=False,
                detail="missing coverage term: third-party-fallback",
                path=HARBOR_NEIGHBOR_TOOL_CATALOG_PATH,
            ),
            results,
        )

    def test_validate_harbor_neighbor_tool_catalog_requires_exact_issue_routes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_NEIGHBOR_TOOL_CATALOG_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                textwrap.dedent(
                    """\
                    # Harbor-Neighbor Tool Catalog

                    Status: Source Disposition Ledger

                    ## Scope Boundary

                    Broad eval-platform survey work is out of scope.

                    ## Portable Source Inventory

                    Harbor docs and source URLs.

                    ## Harbor-Neighbor Tool Catalog

                    | entry_id | tool_or_surface | Harbor linkage | source URL | role classification | evidence quality | likely Armory consumer | open uncertainty |
                    | --- | --- | --- | --- | --- | --- | --- | --- |
                    | HN001 | Daytona, Modal, E2B, Runloop, Tensorlake, Islo, CoreWeave Sandboxes, W&B Sandboxes, Reward Kit, LiteLLM, ATIF, Opik, Harbor registry, dataset.toml, adapter templates, result viewer, Hugging Face parity experiments, SkyRL, and GEPA | Harbor-linked surfaces only. | https://www.harborframework.com/docs/run-jobs/cloud-sandboxes | Jig Driver substrate, sandbox provider, benchmark format, benchmark registry, Agent or harness configurator, tool provider, observability/evaluation instrumentation, verifier/assertion layer, trajectory/result format, training/export surface | harbor-doc-supported, harbor-source-supported, vendor-doc-supported, third-party-fallback | #187, #188, #189, #190, #191 | No integration approval. |

                    ## Role Classification Summary

                    Jig Driver substrate, sandbox provider, benchmark format,
                    benchmark registry, Agent or harness configurator, tool provider,
                    observability/evaluation instrumentation, verifier/assertion layer,
                    trajectory/result format, and training/export surface.

                    ## Open Uncertainties And Follow-Up Conditions

                    No integration approval.

                    ## Downstream Routing

                    #183, #186a, #187, #188, #189, #190, and #191.

                    ## Deferments And Nonportable Claims

                    No prototype.

                    ## Security Privacy And Durability

                    No raw logs.

                    ## Closeout Evidence

                    Reviewed.
                    """
                ),
                encoding="utf-8",
            )

            results = validate_harbor_neighbor_tool_catalog(root)

        self.assertIn(
            CheckResult(
                name="harbor_neighbor_tool_catalog:routing:#186",
                ok=False,
                detail="missing downstream route: #186",
                path=HARBOR_NEIGHBOR_TOOL_CATALOG_PATH,
            ),
            results,
        )

    def test_validate_harbor_neighbor_tool_catalog_rejects_host_local_paths_and_broad_survey(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_NEIGHBOR_TOOL_CATALOG_PATH
            path.parent.mkdir(parents=True)
            template = textwrap.dedent(
                """\
                    # Harbor-Neighbor Tool Catalog

                    Status: Source Disposition Ledger

                    ## Scope Boundary

                    {scope_statement}

                    ## Portable Source Inventory

                    Harbor docs and source URLs.

                    ## Harbor-Neighbor Tool Catalog

                    | entry_id | tool_or_surface | Harbor linkage | source URL | role classification | evidence quality | likely Armory consumer | open uncertainty |
                    | --- | --- | --- | --- | --- | --- | --- | --- |
                    | HN001 | Daytona, Modal, E2B, Runloop, Tensorlake, Islo, CoreWeave Sandboxes, W&B Sandboxes, Reward Kit, LiteLLM, ATIF, Opik, Harbor registry, dataset.toml, adapter templates, result viewer, Hugging Face parity experiments, SkyRL, and GEPA | Harbor-linked surfaces only. | https://www.harborframework.com/docs/run-jobs/cloud-sandboxes | Jig Driver substrate, sandbox provider, benchmark format, benchmark registry, Agent or harness configurator, tool provider, observability/evaluation instrumentation, verifier/assertion layer, trajectory/result format, training/export surface | harbor-doc-supported, harbor-source-supported, vendor-doc-supported, third-party-fallback | #187, #188, #189, #190, #191 | No integration approval. |

                    Scratch path: `{host_local_path}`.

                    ## Role Classification Summary

                    Jig Driver substrate, sandbox provider, benchmark format,
                    benchmark registry, Agent or harness configurator, tool provider,
                    observability/evaluation instrumentation, verifier/assertion layer,
                    trajectory/result format, and training/export surface.

                    ## Open Uncertainties And Follow-Up Conditions

                    No integration approval.

                    ## Downstream Routing

                    #183, #186, #187, #188, #189, #190, and #191.

                    ## Deferments And Nonportable Claims

                    No prototype.

                    ## Security Privacy And Durability

                    No raw logs.

                    ## Closeout Evidence

                    Reviewed.
                    """
            )

            for scope_statement in (
                "This is a broad market survey.",
                "This is a broad eval-platform survey.",
            ):
                for host_local_path in (
                    "/home/agent/harbor/neighbor-catalog.json",
                    r"C:\Users\agent\harbor\neighbor-catalog.json",
                ):
                    with self.subTest(scope_statement=scope_statement, host_local_path=host_local_path):
                        path.write_text(
                            template.format(
                                scope_statement=scope_statement,
                                host_local_path=host_local_path,
                            ),
                            encoding="utf-8",
                        )
                        results = validate_harbor_neighbor_tool_catalog(root)

                        self.assertIn(
                            CheckResult(
                                name="harbor_neighbor_tool_catalog:portable_paths",
                                ok=False,
                                detail="ledger must not preserve host-local paths",
                                path=HARBOR_NEIGHBOR_TOOL_CATALOG_PATH,
                            ),
                            results,
                        )
                        self.assertIn(
                            CheckResult(
                                name="harbor_neighbor_tool_catalog:scope:broad_survey",
                                ok=False,
                                detail="catalog must exclude broad market survey work",
                                path=HARBOR_NEIGHBOR_TOOL_CATALOG_PATH,
                            ),
                            results,
                        )

    def test_validate_harbor_neighbor_tool_catalog_accepts_complete_ledger(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_NEIGHBOR_TOOL_CATALOG_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                textwrap.dedent(
                    """\
                    # Harbor-Neighbor Tool Catalog

                    Status: Source Disposition Ledger

                    ## Scope Boundary

                    Catalog includes Harbor-linked surfaces only. Broad eval-platform
                    survey work is out of scope.

                    ## Portable Source Inventory

                    Harbor docs and source URLs cover Daytona, Modal, E2B, Runloop,
                    Tensorlake, Islo, CoreWeave Sandboxes, W&B Sandboxes, Reward Kit,
                    LiteLLM, ATIF, Opik, Harbor registry, dataset.toml, adapter
                    templates, result viewer, Hugging Face parity experiments, SkyRL,
                    and GEPA.

                    ## Harbor-Neighbor Tool Catalog

                    | entry_id | tool_or_surface | Harbor linkage | source URL | role classification | evidence quality | likely Armory consumer | open uncertainty |
                    | --- | --- | --- | --- | --- | --- | --- | --- |
                    | HN001 | Daytona, Modal, E2B, Runloop, Tensorlake, Islo, CoreWeave Sandboxes, W&B Sandboxes | Harbor cloud sandbox providers. | https://www.harborframework.com/docs/run-jobs/cloud-sandboxes | Jig Driver substrate; sandbox provider | harbor-doc-supported | #190 | No provider is approved as an Armory driver. |
                    | HN002 | Reward Kit and LiteLLM | Harbor verifier and judge routing. | https://www.harborframework.com/docs/rewardkit | verifier/assertion layer; trajectory/result format | harbor-doc-supported | #188 | Tamper and calibration boundaries remain open. |
                    | HN003 | ATIF and Opik | Harbor trajectory format and fallback integration context. | https://github.com/harbor-framework/harbor/blob/main/rfcs/0001-trajectory-format.md | observability/evaluation instrumentation; trajectory/result format | harbor-source-supported; third-party-fallback | #189 | Opik is fallback evidence only. |
                    | HN004 | Harbor registry, dataset.toml, adapter templates, result viewer, Hugging Face parity experiments, SkyRL, and GEPA | Harbor benchmark and training/export surfaces. | https://www.harborframework.com/docs/run-jobs/run-evals | benchmark format; benchmark registry; Agent or harness configurator; tool provider; training/export surface | harbor-doc-supported; vendor-doc-supported | #187, #191 | Later issues decide Armory adoption. |

                    ## Role Classification Summary

                    Jig Driver substrate, sandbox provider, benchmark format,
                    benchmark registry, Agent or harness configurator, tool provider,
                    observability/evaluation instrumentation, verifier/assertion layer,
                    trajectory/result format, and training/export surface.

                    ## Open Uncertainties And Follow-Up Conditions

                    No integration approval.

                    ## Downstream Routing

                    #183, #186, #187, #188, #189, #190, and #191.

                    ## Deferments And Nonportable Claims

                    No prototype.

                    ## Security Privacy And Durability

                    No raw logs.

                    ## Closeout Evidence

                    Reviewed.
                    """
                ),
                encoding="utf-8",
            )

            results = validate_harbor_neighbor_tool_catalog(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="harbor_neighbor_tool_catalog:ledger",
                    ok=True,
                    detail="present",
                    path=HARBOR_NEIGHBOR_TOOL_CATALOG_PATH,
                )
            ],
        )

    def test_validate_plugin_creator_source_intake_requires_coverage_terms(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / PLUGIN_CREATOR_SOURCE_INTAKE_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                textwrap.dedent(
                    """\
                    # Plugin-Creator Source Intake

                    Status: Source Disposition Ledger

                    ## Scope Boundary

                    Source intake only.

                    ## Portable Source Inventory

                    plugin-creator/SKILL.md.

                    ## Reusable Techniques

                    name normalization and marketplace projection.

                    ## UX And Marketplace Metadata

                    display metadata is covered.

                    ## Downstream Routing

                    #5 is covered.

                    ## Deferments And Nonportable Claims

                    No plugin implementation.

                    ## Security, Privacy, And Durability

                    No raw logs are retained.

                    ## Closeout Evidence

                    Reviewed.
                    """
                ),
                encoding="utf-8",
            )

            results = validate_plugin_creator_source_intake(root)

        self.assertIn(
            CheckResult(
                name="plugin_creator_source_intake:coverage:manifest scaffolding",
                ok=False,
                detail="missing coverage term: manifest scaffolding",
                path=PLUGIN_CREATOR_SOURCE_INTAKE_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                name="plugin_creator_source_intake:routing:#154",
                ok=False,
                detail="missing downstream route: #154",
                path=PLUGIN_CREATOR_SOURCE_INTAKE_PATH,
            ),
            results,
        )

    def test_validate_plugin_creator_source_intake_requires_exact_issue_routes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / PLUGIN_CREATOR_SOURCE_INTAKE_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                textwrap.dedent(
                    """\
                    # Plugin-Creator Source Intake

                    Status: Source Disposition Ledger

                    ## Scope Boundary

                    Source intake only.

                    ## Portable Source Inventory

                    plugin-creator/SKILL.md and plugin-creator/scripts/create_basic_plugin.py.

                    ## Reusable Techniques

                    manifest scaffolding, name normalization, marketplace projection,
                    cachebuster reinstall flow, schema validation, component surface selection,
                    placeholder debt, policy/auth semantics, and asset metadata.

                    ## UX And Marketplace Metadata

                    Marketplace display metadata is retained.

                    ## Downstream Routing

                    #51, #154a, and #157b.

                    ## Deferments And Nonportable Claims

                    No plugin implementation.

                    ## Security, Privacy, And Durability

                    No raw logs are retained.

                    ## Closeout Evidence

                    Reviewed.
                    """
                ),
                encoding="utf-8",
            )

            results = validate_plugin_creator_source_intake(root)

        self.assertIn(
            CheckResult(
                name="plugin_creator_source_intake:routing:#5",
                ok=False,
                detail="missing downstream route: #5",
                path=PLUGIN_CREATOR_SOURCE_INTAKE_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                name="plugin_creator_source_intake:routing:#154",
                ok=False,
                detail="missing downstream route: #154",
                path=PLUGIN_CREATOR_SOURCE_INTAKE_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                name="plugin_creator_source_intake:routing:#157",
                ok=False,
                detail="missing downstream route: #157",
                path=PLUGIN_CREATOR_SOURCE_INTAKE_PATH,
            ),
            results,
        )

    def test_validate_plugin_creator_source_intake_rejects_host_local_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / PLUGIN_CREATOR_SOURCE_INTAKE_PATH
            path.parent.mkdir(parents=True)
            template = textwrap.dedent(
                """\
                    # Plugin-Creator Source Intake

                    Status: Source Disposition Ledger

                    ## Scope Boundary

                    Source intake only.

                    ## Portable Source Inventory

                    The raw source lives at `{host_local_path}`.

                    ## Reusable Techniques

                    manifest scaffolding, name normalization, marketplace projection,
                    cachebuster reinstall flow, schema validation, component surface selection,
                    placeholder debt, policy/auth semantics, and asset metadata.

                    ## UX And Marketplace Metadata

                    Marketplace display metadata is retained.

                    ## Downstream Routing

                    #5, #154, and #157.

                    ## Deferments And Nonportable Claims

                    No plugin implementation.

                    ## Security, Privacy, And Durability

                    No raw logs are retained.

                    ## Closeout Evidence

                    Reviewed.
                    """
            )

            for host_local_path in (
                "/home/agent/.codex/skills/.system/plugin-creator/SKILL.md",
                r"C:\Users\agent\.codex\skills\.system\plugin-creator\SKILL.md",
            ):
                with self.subTest(host_local_path=host_local_path):
                    path.write_text(template.format(host_local_path=host_local_path), encoding="utf-8")
                    results = validate_plugin_creator_source_intake(root)

                    self.assertIn(
                        CheckResult(
                            name="plugin_creator_source_intake:portable_paths",
                            ok=False,
                            detail="ledger must not preserve host-local paths",
                            path=PLUGIN_CREATOR_SOURCE_INTAKE_PATH,
                        ),
                        results,
                    )

    def test_validate_plugin_creator_source_intake_accepts_complete_ledger(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / PLUGIN_CREATOR_SOURCE_INTAKE_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                textwrap.dedent(
                    """\
                    # Plugin-Creator Source Intake

                    Status: Source Disposition Ledger

                    ## Scope Boundary

                    Source intake only.

                    ## Portable Source Inventory

                    plugin-creator/SKILL.md and plugin-creator/scripts/create_basic_plugin.py.

                    ## Reusable Techniques

                    manifest scaffolding, name normalization, marketplace projection,
                    cachebuster reinstall flow, schema validation, component surface selection,
                    placeholder debt, policy/auth semantics, and asset metadata.

                    ## UX And Marketplace Metadata

                    Marketplace display metadata is retained.

                    ## Downstream Routing

                    #5, #154, and #157.

                    ## Deferments And Nonportable Claims

                    No plugin implementation.

                    ## Security, Privacy, And Durability

                    No raw logs are retained.

                    ## Closeout Evidence

                    Reviewed.
                    """
                ),
                encoding="utf-8",
            )

            results = validate_plugin_creator_source_intake(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="plugin_creator_source_intake:ledger",
                    ok=True,
                    detail="present",
                    path=PLUGIN_CREATOR_SOURCE_INTAKE_PATH,
                )
            ],
        )

    def test_validate_external_tool_evaluation_reports_missing_doc(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = validate_external_tool_evaluation(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="external_tool_evaluation:path",
                    ok=False,
                    detail="missing",
                    path=EXTERNAL_TOOL_EVALUATION_PATH,
                )
            ],
        )

    def test_validate_external_tool_evaluation_requires_contract_shape(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / EXTERNAL_TOOL_EVALUATION_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                "# External-Tool Evaluation\n\nStatus: Draft\n\n## Purpose\n\nIncomplete.\n",
                encoding="utf-8",
            )

            results = validate_external_tool_evaluation(root)

        self.assertIn(
            CheckResult(
                name="external_tool_evaluation:status",
                ok=False,
                detail="status must be Armory Operating Contract",
                path=EXTERNAL_TOOL_EVALUATION_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                name="external_tool_evaluation:section:Pipeline Stages",
                ok=False,
                detail="missing section: Pipeline Stages",
                path=EXTERNAL_TOOL_EVALUATION_PATH,
            ),
            results,
        )

    def test_validate_external_tool_evaluation_requires_coverage_terms(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / EXTERNAL_TOOL_EVALUATION_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                textwrap.dedent(
                    """\
                    # External-Tool Evaluation

                    Status: Armory Operating Contract

                    ## Purpose

                    Evaluate outside tools.

                    ## Pipeline Stages

                    Source review and closeout.

                    ## Evidence Classification

                    source-backed claims.

                    ## Projection Rules

                    Issues may be updated.

                    ## Security Disclosure And Durability

                    Credentials are sensitive.

                    ## Harbor-First Application

                    #184 and #185.

                    ## Closeout

                    Reviewed.
                    """
                ),
                encoding="utf-8",
            )

            results = validate_external_tool_evaluation(root)

        self.assertIn(
            CheckResult(
                name="external_tool_evaluation:coverage:prototype results",
                ok=False,
                detail="missing coverage term: prototype results",
                path=EXTERNAL_TOOL_EVALUATION_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                name="external_tool_evaluation:coverage:external service usage",
                ok=False,
                detail="missing coverage term: external service usage",
                path=EXTERNAL_TOOL_EVALUATION_PATH,
            ),
            results,
        )

    def test_validate_external_tool_evaluation_requires_exact_issue_routes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / EXTERNAL_TOOL_EVALUATION_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                textwrap.dedent(
                    """\
                    # External-Tool Evaluation

                    Status: Armory Operating Contract

                    ## Purpose

                    Reusable evaluation pipeline.

                    ## Pipeline Stages

                    intake scope, source review, live repository and issue review,
                    evidence classification, Armory role mapping, bounded prototype decision,
                    security and disclosure review, documentation closeout, issue projection,
                    and final disposition.

                    ## Evidence Classification

                    source-backed claims, local observations, prototype results,
                    implementation inference, unknowns, and rejected claims.

                    ## Projection Rules

                    update existing issues, create new issues, propose a PRD, and propose an ADR.

                    ## Security Disclosure And Durability

                    credentials, local paths, raw logs, trajectories, transcripts,
                    model outputs, and external service usage.

                    ## Harbor-First Application

                    #184a and #185b.

                    ## Closeout

                    Change Set Security Closeout and Change Set Documentation Closeout.
                    """
                ),
                encoding="utf-8",
            )

            results = validate_external_tool_evaluation(root)

        self.assertIn(
            CheckResult(
                name="external_tool_evaluation:routing:#184",
                ok=False,
                detail="missing downstream route: #184",
                path=EXTERNAL_TOOL_EVALUATION_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                name="external_tool_evaluation:routing:#185",
                ok=False,
                detail="missing downstream route: #185",
                path=EXTERNAL_TOOL_EVALUATION_PATH,
            ),
            results,
        )

    def test_validate_external_tool_evaluation_rejects_host_local_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / EXTERNAL_TOOL_EVALUATION_PATH
            path.parent.mkdir(parents=True)
            template = textwrap.dedent(
                """\
                    # External-Tool Evaluation

                    Status: Armory Operating Contract

                    ## Purpose

                    Reusable evaluation pipeline.

                    ## Pipeline Stages

                    intake scope, source review, live repository and issue review,
                    evidence classification, Armory role mapping, bounded prototype decision,
                    security and disclosure review, documentation closeout, issue projection,
                    and final disposition.

                    ## Evidence Classification

                    source-backed claims, local observations, prototype results,
                    implementation inference, unknowns, and rejected claims.

                    ## Projection Rules

                    update existing issues, create new issues, propose a PRD, and propose an ADR.

                    ## Security Disclosure And Durability

                    credentials, local paths, raw logs, trajectories, transcripts,
                    model outputs, and external service usage. Scratch path: `{host_local_path}`.

                    ## Harbor-First Application

                    #184 and #185.

                    ## Closeout

                    Change Set Security Closeout and Change Set Documentation Closeout.
                    """
            )

            for host_local_path in (
                "/home/agent/harbor/evaluation-log.json",
                r"C:\Users\agent\harbor\evaluation-log.json",
            ):
                with self.subTest(host_local_path=host_local_path):
                    path.write_text(template.format(host_local_path=host_local_path), encoding="utf-8")
                    results = validate_external_tool_evaluation(root)

                    self.assertIn(
                        CheckResult(
                            name="external_tool_evaluation:portable_paths",
                            ok=False,
                            detail="contract must not preserve host-local paths",
                            path=EXTERNAL_TOOL_EVALUATION_PATH,
                        ),
                        results,
                    )

    def test_validate_external_tool_evaluation_accepts_complete_contract(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / EXTERNAL_TOOL_EVALUATION_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                textwrap.dedent(
                    """\
                    # External-Tool Evaluation

                    Status: Armory Operating Contract

                    ## Purpose

                    Reusable evaluation pipeline.

                    ## Pipeline Stages

                    intake scope, source review, live repository and issue review,
                    evidence classification, Armory role mapping, bounded prototype decision,
                    security and disclosure review, documentation closeout, issue projection,
                    and final disposition.

                    ## Evidence Classification

                    source-backed claims, local observations, prototype results,
                    implementation inference, unknowns, and rejected claims.

                    ## Projection Rules

                    update existing issues, create new issues, propose a PRD, and propose an ADR.

                    ## Security Disclosure And Durability

                    credentials, local paths, raw logs, trajectories, transcripts,
                    model outputs, and external service usage.

                    ## Harbor-First Application

                    #184 and #185.

                    ## Closeout

                    Change Set Security Closeout and Change Set Documentation Closeout.
                    """
                ),
                encoding="utf-8",
            )

            results = validate_external_tool_evaluation(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="external_tool_evaluation:contract",
                    ok=True,
                    detail="present",
                    path=EXTERNAL_TOOL_EVALUATION_PATH,
                )
            ],
        )

    def test_validate_harbor_final_disposition_reports_missing_doc(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = validate_harbor_final_disposition(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="harbor_final_disposition:path",
                    ok=False,
                    detail="missing",
                    path=HARBOR_FINAL_DISPOSITION_PATH,
                )
            ],
        )

    def test_validate_harbor_final_disposition_requires_ledger_shape(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_FINAL_DISPOSITION_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                "# Harbor Final Disposition\n\nStatus: Draft\n\n## Scope Boundary\n\nIncomplete.\n",
                encoding="utf-8",
            )

            results = validate_harbor_final_disposition(root)

        self.assertIn(
            CheckResult(
                name="harbor_final_disposition:status",
                ok=False,
                detail="status must be Source Disposition Ledger",
                path=HARBOR_FINAL_DISPOSITION_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                name="harbor_final_disposition:section:Disposition Decision",
                ok=False,
                detail="missing section: Disposition Decision",
                path=HARBOR_FINAL_DISPOSITION_PATH,
            ),
            results,
        )

    def test_validate_harbor_final_disposition_requires_projection_routes_and_terms(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_FINAL_DISPOSITION_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                textwrap.dedent(
                    """\
                    # Harbor Final Disposition

                    Status: Source Disposition Ledger

                    ## Scope Boundary

                    Issue #191 finalizes Harbor.

                    ## Disposition Decision

                    Harbor is useful.

                    ## Evidence Basis

                    Source-map, prototype, Reward Kit, ATIF, and driver-gate evidence.

                    ## Projection Matrix

                    #191.

                    ## Non-Goals And Deferments

                    No broad eval-platform survey.

                    ## Security Privacy And Durability

                    credentials, raw logs, local paths, trajectories, transcripts,
                    model outputs, provider account state, and external service usage
                    remain scratch.

                    ## Closeout Evidence

                    TDD, Codex Security, and Ralph Review Cycle.
                    """
                ),
                encoding="utf-8",
            )

            results = validate_harbor_final_disposition(root)

        self.assertIn(
            CheckResult(
                name="harbor_final_disposition:coverage:research reference",
                ok=False,
                detail="missing coverage term: research reference",
                path=HARBOR_FINAL_DISPOSITION_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                name="harbor_final_disposition:routing:#163",
                ok=False,
                detail="missing downstream route: #163",
                path=HARBOR_FINAL_DISPOSITION_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                name="harbor_final_disposition:routing:#183",
                ok=False,
                detail="missing downstream route: #183",
                path=HARBOR_FINAL_DISPOSITION_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                name="harbor_final_disposition:source:docs/closeout/harbor-driver-gate.md",
                ok=False,
                detail="missing source reference: docs/closeout/harbor-driver-gate.md",
                path=HARBOR_FINAL_DISPOSITION_PATH,
            ),
            results,
        )

    def test_validate_harbor_final_disposition_rejects_host_local_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_FINAL_DISPOSITION_PATH
            path.parent.mkdir(parents=True)
            marker = "raw tool output remain scratch evidence."
            template = self.valid_harbor_final_disposition().replace(
                marker,
                (
                    "raw tool output remain scratch evidence. Scratch path: `{host_local_path}`."
                    "\n\n```text\n{host_local_path}\n```"
                ),
            )

            for host_local_path in (
                "/home/agent/harbor/final-projection.json",
                r"C:\Users\agent\harbor\final-projection.json",
            ):
                with self.subTest(host_local_path=host_local_path):
                    path.write_text(template.replace("{host_local_path}", host_local_path), encoding="utf-8")
                    results = validate_harbor_final_disposition(root)

                    self.assertIn(
                        CheckResult(
                            name="harbor_final_disposition:portable_paths",
                            ok=False,
                            detail="ledger must not preserve host-local paths",
                            path=HARBOR_FINAL_DISPOSITION_PATH,
                        ),
                        results,
                    )

    def test_validate_harbor_final_disposition_accepts_complete_ledger(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_FINAL_DISPOSITION_PATH
            path.parent.mkdir(parents=True)
            path.write_text(self.valid_harbor_final_disposition(), encoding="utf-8")

            results = validate_harbor_final_disposition(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="harbor_final_disposition:ledger",
                    ok=True,
                    detail="present",
                    path=HARBOR_FINAL_DISPOSITION_PATH,
                )
            ],
        )

    @staticmethod
    def valid_harbor_final_disposition() -> str:
        return textwrap.dedent(
            """\
            # Harbor Final Disposition

            Status: Source Disposition Ledger

            ## Scope Boundary

            Issue #191 completes Harbor final disposition for #183. It consumes
            docs/closeout/harbor-jig-source-map.md,
            docs/closeout/harbor-neighbor-tool-catalog.md,
            docs/closeout/harbor-reward-kit-evaluation.md,
            docs/closeout/harbor-agent-equipment-ab-prototype-results.md,
            docs/closeout/harbor-atif-job-artifacts-evaluation.md, and
            docs/closeout/harbor-driver-gate.md.

            ## Disposition Decision

            Final disposition: research reference. Harbor remains supporting source material,
            not an adopted candidate, supporting component,
            selected first Jig Driver, Assertion Provider, Learned Oracle,
            Harness Test Suite evidence source, or direct Armory result contract.

            ## Evidence Basis

            #187 remains bounded prototype evidence only. Reward Kit informs
            Assertion Provider and Learned Oracle work: borrow concepts and
            defer wrapping. ATIF, result.json, trajectory.json, verifier output,
            artifact manifest.json, and viewer affordances inform result/artifact
            and review-surface design. Harbor Driver Gate defers Harbor as the
            first Jig Driver.

            ## Projection Matrix

            #163 uses Harbor as comparison evidence for first Jig Driver selection.
            #164 borrows job result, trial result, trajectory, verifier output, and
            artifact manifest separation without replacing Armory statuses. #165
            borrows deterministic Reward Kit criteria concepts. #166 borrows judge
            TOML, trajectory evaluation, provider routing, and calibration pressure.
            #167 and #177 receive no direct update until structured Jig Runner or
            Harness Test Suite evidence exists. #169 may use Harbor viewer
            affordances as later UX evidence. #183 and #191 receive final closeout.

            ## Non-Goals And Deferments

            no broad eval-platform survey, no PRD, no ADR, Harbor adoption, Harbor run,
            cloud sandbox run, registry operation, provider credential use, UI
            implementation, or first Jig Driver selection is accepted here.

            ## Security Privacy And Durability

            Credentials, raw logs, local paths, host-local paths, raw trajectories,
            transcripts, model outputs, viewer screenshots, provider account state,
            external service usage, raw GitHub API output, raw Firecrawl output, and
            raw tool output remain scratch evidence.

            ## Closeout Evidence

            Triage, grill-with-docs, TDD, Codex Security, documentation closeout,
            Cross-Boundary Coherence Ralph Review, and Story Quality Ralph Review.
            """
        )

    def test_validate_harbor_external_tool_evaluation_record_reports_missing_doc(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = validate_harbor_external_tool_evaluation_record(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="harbor_external_tool_evaluation_record:path",
                    ok=False,
                    detail="missing",
                    path=HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH,
                )
            ],
        )

    def test_validate_harbor_external_tool_evaluation_record_requires_record_shape(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                "# Harbor Evaluation\n\nStatus: Draft\n\n## Scope\n\nIncomplete.\n",
                encoding="utf-8",
            )

            results = validate_harbor_external_tool_evaluation_record(root)

        self.assertIn(
            CheckResult(
                name="harbor_external_tool_evaluation_record:status",
                ok=False,
                detail="status must be External Tool Evaluation Record",
                path=HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                name="harbor_external_tool_evaluation_record:evaluation_state",
                ok=False,
                detail="evaluation state must be in progress or complete",
                path=HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                name="harbor_external_tool_evaluation_record:final_disposition",
                ok=False,
                detail="final disposition must be a fixed External Tool Evaluation Disposition",
                path=HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                name="harbor_external_tool_evaluation_record:section:Evidence Ledger",
                ok=False,
                detail="missing section: Evidence Ledger",
                path=HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH,
            ),
            results,
        )

    def test_validate_harbor_external_tool_evaluation_record_requires_coverage_terms(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                textwrap.dedent(
                    """\
                    # Harbor External Tool Evaluation

                    Status: External Tool Evaluation Record

                    Evaluation state: in progress

                    Final disposition: unknown pending evidence

                    ## Scope

                    Harbor evaluation for #183.

                    ## Source Inputs

                    #184.

                    ## Evidence Ledger

                    source-backed claims, local observations, implementation inference,
                    unknowns, and rejected claims.

                    ## Child Issue Outputs

                    #185, #186, #187, #188, #189, #190, and #191.

                    ## Security Disclosure And Durability

                    credentials, local paths, raw logs, trajectories, transcripts,
                    model outputs, and external service usage.

                    ## Projection State

                    update existing issues, create new issues, propose a PRD, and propose an ADR.

                    ## Final Disposition

                    unknown pending evidence.
                    """
                ),
                encoding="utf-8",
            )

            results = validate_harbor_external_tool_evaluation_record(root)

        self.assertIn(
            CheckResult(
                name="harbor_external_tool_evaluation_record:coverage:prototype results",
                ok=False,
                detail="missing coverage term: prototype results",
                path=HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                name="harbor_external_tool_evaluation_record:coverage:Harbor Agent Equipment A/B Prototype Results",
                ok=False,
                detail="missing coverage term: Harbor Agent Equipment A/B Prototype Results",
                path=HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH,
            ),
            results,
        )

    def test_validate_harbor_external_tool_evaluation_record_requires_child_issue_routes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                textwrap.dedent(
                    """\
                    # Harbor External Tool Evaluation

                    Status: External Tool Evaluation Record

                    Evaluation state: in progress

                    Final disposition: unknown pending evidence

                    ## Scope

                    Harbor evaluation for #183.

                    ## Source Inputs

                    #184a.

                    ## Evidence Ledger

                    source-backed claims, local observations, prototype results,
                    implementation inference, unknowns, and rejected claims.

                    ## Child Issue Outputs

                    #185.

                    ## Security Disclosure And Durability

                    credentials, local paths, raw logs, trajectories, transcripts,
                    model outputs, and external service usage.

                    ## Projection State

                    update existing issues, create new issues, propose a PRD, and propose an ADR.

                    ## Final Disposition

                    unknown pending evidence.
                    """
                ),
                encoding="utf-8",
            )

            results = validate_harbor_external_tool_evaluation_record(root)

        self.assertIn(
            CheckResult(
                name="harbor_external_tool_evaluation_record:routing:#184",
                ok=False,
                detail="missing downstream route: #184",
                path=HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                name="harbor_external_tool_evaluation_record:routing:#191",
                ok=False,
                detail="missing downstream route: #191",
                path=HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH,
            ),
            results,
        )

    def test_validate_harbor_external_tool_evaluation_record_rejects_host_local_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH
            path.parent.mkdir(parents=True)
            template = textwrap.dedent(
                """\
                    # Harbor External Tool Evaluation

                    Status: External Tool Evaluation Record

                    Evaluation state: in progress

                    Final disposition: unknown pending evidence

                    ## Scope

                    Harbor evaluation for #183.

                    ## Source Inputs

                    #184. Harbor Agent Equipment A/B Prototype Results,
                    bounded prototype evidence accepted, baseline reward, and
                    equipped reward.

                    ## Evidence Ledger

                    source-backed claims, local observations, prototype results,
                    implementation inference, unknowns, and rejected claims.

                    ## Child Issue Outputs

                    #185, #186, #187, #188, #189, #190, and #191.

                    ## Security Disclosure And Durability

                    credentials, local paths, raw logs, trajectories, transcripts,
                    model outputs, and external service usage. Scratch path: `{host_local_path}`.

                    ## Projection State

                    update existing issues, create new issues, propose a PRD, and propose an ADR.

                    ## Final Disposition

                    unknown pending evidence.
                    """
            )

            for host_local_path in (
                "/home/agent/harbor/evaluation-record.json",
                r"C:\Users\agent\harbor\evaluation-record.json",
            ):
                with self.subTest(host_local_path=host_local_path):
                    path.write_text(template.format(host_local_path=host_local_path), encoding="utf-8")
                    results = validate_harbor_external_tool_evaluation_record(root)

                    self.assertIn(
                        CheckResult(
                            name="harbor_external_tool_evaluation_record:portable_paths",
                            ok=False,
                            detail="record must not preserve host-local paths",
                            path=HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH,
                        ),
                        results,
                    )

    def test_validate_harbor_external_tool_evaluation_record_accepts_complete_record(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                textwrap.dedent(
                    """\
                    # Harbor External Tool Evaluation

                    Status: External Tool Evaluation Record

                    Evaluation state: in progress

                    Final disposition: unknown pending evidence

                    ## Scope

                    Harbor evaluation for #183.

                    ## Source Inputs

                    #184. Harbor Agent Equipment A/B Prototype Results,
                    bounded prototype evidence accepted, baseline reward, and
                    equipped reward.

                    ## Evidence Ledger

                    source-backed claims, local observations, prototype results,
                    implementation inference, unknowns, and rejected claims.

                    ## Child Issue Outputs

                    #185, #186, #187, #188, #189, #190, and #191.

                    ## Security Disclosure And Durability

                    credentials, local paths, raw logs, trajectories, transcripts,
                    model outputs, and external service usage.

                    ## Projection State

                    update existing issues, create new issues, propose a PRD, and propose an ADR.

                    ## Final Disposition

                    unknown pending evidence.
                    """
                ),
                encoding="utf-8",
            )

            results = validate_harbor_external_tool_evaluation_record(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="harbor_external_tool_evaluation_record:record",
                    ok=True,
                    detail="present",
                    path=HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH,
                )
            ],
        )

    def test_validate_harbor_external_tool_evaluation_record_rejects_complete_unknown_disposition(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                textwrap.dedent(
                    """\
                    # Harbor External Tool Evaluation

                    Status: External Tool Evaluation Record

                    Evaluation state: complete

                    Final disposition: unknown pending evidence

                    ## Scope

                    Harbor evaluation for #183.

                    ## Source Inputs

                    #184. Harbor Agent Equipment A/B Prototype Results, bounded
                    prototype evidence accepted, baseline reward, and equipped reward.

                    ## Evidence Ledger

                    source-backed claims, local observations, prototype results,
                    implementation inference, unknowns, and rejected claims.

                    ## Child Issue Outputs

                    #185, #186, #187, #188, #189, #190, and #191.

                    ## Security Disclosure And Durability

                    credentials, local paths, raw logs, trajectories, transcripts,
                    model outputs, and external service usage.

                    ## Projection State

                    update existing issues, create new issues, propose a PRD, and propose an ADR.

                    ## Final Disposition

                    unknown pending evidence.
                    """
                ),
                encoding="utf-8",
            )

            results = validate_harbor_external_tool_evaluation_record(root)

        self.assertIn(
            CheckResult(
                name="harbor_external_tool_evaluation_record:state_disposition_coherence",
                ok=False,
                detail="complete evaluations must use a finalized final disposition",
                path=HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH,
            ),
            results,
        )

    def test_validate_harbor_external_tool_evaluation_record_requires_final_projection_when_complete(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                textwrap.dedent(
                    """\
                    # Harbor External Tool Evaluation

                    Status: External Tool Evaluation Record

                    Evaluation state: complete

                    Final disposition: research reference

                    ## Scope

                    Harbor evaluation for #183.

                    ## Source Inputs

                    #184. Harbor Agent Equipment A/B Prototype Results,
                    bounded prototype evidence accepted, baseline reward, and
                    equipped reward.

                    ## Evidence Ledger

                    source-backed claims, local observations, prototype results,
                    implementation inference, unknowns, and rejected claims.

                    ## Child Issue Outputs

                    #185, #186, #187, #188, #189, #190, and #191.

                    ## Security Disclosure And Durability

                    credentials, local paths, raw logs, trajectories, transcripts,
                    model outputs, and external service usage.

                    ## Projection State

                    update existing issues, create new issues, propose a PRD, propose an ADR,
                    research reference, supporting source material, selected first Jig Driver,
                    docs/closeout/harbor-final-disposition.md.

                    ## Final Disposition

                    research reference.
                    """
                ),
                encoding="utf-8",
            )

            results = validate_harbor_external_tool_evaluation_record(root)

        self.assertIn(
            CheckResult(
                name="harbor_external_tool_evaluation_record:final_routing:#163",
                ok=False,
                detail="complete evaluation missing final projection route: #163",
                path=HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                name="harbor_external_tool_evaluation_record:final_routing:#177",
                ok=False,
                detail="complete evaluation missing final projection route: #177",
                path=HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH,
            ),
            results,
        )

    def test_validate_harbor_external_tool_evaluation_record_accepts_finalized_disposition(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                textwrap.dedent(
                    """\
                    # Harbor External Tool Evaluation

                    Status: External Tool Evaluation Record

                    Evaluation state: complete

                    Final disposition: research reference

                    ## Scope

                    Harbor evaluation for #183.

                    ## Source Inputs

                    #184. Harbor Agent Equipment A/B Prototype Results,
                    bounded prototype evidence accepted, baseline reward, and
                    equipped reward.

                    ## Evidence Ledger

                    source-backed claims, local observations, prototype results,
                    implementation inference, unknowns, and rejected claims.

                    ## Child Issue Outputs

                    #185, #186, #187, #188, #189, #190, and #191.

                    ## Security Disclosure And Durability

                    credentials, local paths, raw logs, trajectories, transcripts,
                    model outputs, and external service usage.

                    ## Projection State

                    update existing issues, create new issues, propose a PRD, propose an ADR,
                    research reference, supporting source material, selected first Jig Driver,
                    docs/closeout/harbor-final-disposition.md.
                    Final projection routes: #163, #164, #165, #166, #167, #169,
                    #177, #183, and #191.

                    ## Final Disposition

                    research reference.
                    """
                ),
                encoding="utf-8",
            )

            results = validate_harbor_external_tool_evaluation_record(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="harbor_external_tool_evaluation_record:record",
                    ok=True,
                    detail="present",
                    path=HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH,
                )
            ],
        )

    def test_validate_skill_eval_methodology_source_intake_requires_ledger_shape(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / SKILL_EVAL_METHODOLOGY_SOURCE_INTAKE_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                "# Skill-Eval Methodology Source Intake\n\nStatus: Draft\n\n## Scope Boundary\n\nIncomplete.\n",
                encoding="utf-8",
            )

            results = validate_skill_eval_methodology_source_intake(root)

        self.assertIn(
            CheckResult(
                name="skill_eval_methodology_source_intake:status",
                ok=False,
                detail="status must be Source Disposition Ledger",
                path=SKILL_EVAL_METHODOLOGY_SOURCE_INTAKE_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                name="skill_eval_methodology_source_intake:section:Portable Source Inventory",
                ok=False,
                detail="missing section: Portable Source Inventory",
                path=SKILL_EVAL_METHODOLOGY_SOURCE_INTAKE_PATH,
            ),
            results,
        )

    def test_validate_skill_eval_methodology_source_intake_requires_coverage_terms(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / SKILL_EVAL_METHODOLOGY_SOURCE_INTAKE_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                textwrap.dedent(
                    """\
                    # Skill-Eval Methodology Source Intake

                    Status: Source Disposition Ledger

                    ## Scope Boundary

                    Source intake only.

                    ## Portable Source Inventory

                    Portable skill source identities.

                    ## Reusable Techniques

                    Behavioral evals are covered.

                    ## Downstream Routing

                    #61 is covered.

                    ## Deferments And Nonportable Claims

                    No runnable eval design.

                    ## Security, Privacy, And Durability

                    No raw logs are retained.

                    ## Closeout Evidence

                    Reviewed.
                    """
                ),
                encoding="utf-8",
            )

            results = validate_skill_eval_methodology_source_intake(root)

        self.assertIn(
            CheckResult(
                name="skill_eval_methodology_source_intake:coverage:trigger-selection evals",
                ok=False,
                detail="missing coverage term: trigger-selection evals",
                path=SKILL_EVAL_METHODOLOGY_SOURCE_INTAKE_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                name="skill_eval_methodology_source_intake:routing:#62",
                ok=False,
                detail="missing downstream route: #62",
                path=SKILL_EVAL_METHODOLOGY_SOURCE_INTAKE_PATH,
            ),
            results,
        )

    def test_validate_skill_eval_methodology_source_intake_requires_exact_issue_routes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / SKILL_EVAL_METHODOLOGY_SOURCE_INTAKE_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                textwrap.dedent(
                    """\
                    # Skill-Eval Methodology Source Intake

                    Status: Source Disposition Ledger

                    ## Scope Boundary

                    Source intake only.

                    ## Portable Source Inventory

                    skill-creator/SKILL.md and adapting-skill-creator-to-harnesses/SKILL.md.

                    ## Reusable Techniques

                    behavioral evals, trigger-selection evals, harness adaptation,
                    description optimization, benchmarking, human review, grading,
                    packaging, and viewer/review workflow.

                    ## Downstream Routing

                    #61a, #62, #67, #51, #155, #157, and later Forge work.

                    ## Deferments And Nonportable Claims

                    No runnable eval design.

                    ## Security, Privacy, And Durability

                    No raw logs are retained.

                    ## Closeout Evidence

                    Reviewed.
                    """
                ),
                encoding="utf-8",
            )

            results = validate_skill_eval_methodology_source_intake(root)

        self.assertIn(
            CheckResult(
                name="skill_eval_methodology_source_intake:routing:#61",
                ok=False,
                detail="missing downstream route: #61",
                path=SKILL_EVAL_METHODOLOGY_SOURCE_INTAKE_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                name="skill_eval_methodology_source_intake:routing:#5",
                ok=False,
                detail="missing downstream route: #5",
                path=SKILL_EVAL_METHODOLOGY_SOURCE_INTAKE_PATH,
            ),
            results,
        )

    def test_validate_skill_eval_methodology_source_intake_rejects_host_local_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / SKILL_EVAL_METHODOLOGY_SOURCE_INTAKE_PATH
            path.parent.mkdir(parents=True)
            template = textwrap.dedent(
                """\
                    # Skill-Eval Methodology Source Intake

                    Status: Source Disposition Ledger

                    ## Scope Boundary

                    Source intake only.

                    ## Portable Source Inventory

                    The raw source lives at `{host_local_path}`.

                    ## Reusable Techniques

                    behavioral evals, trigger-selection evals, harness adaptation,
                    description optimization, benchmarking, human review, grading,
                    packaging, and viewer/review workflow.

                    ## Downstream Routing

                    #61, #62, #67, #5, #155, #157, and later Forge work.

                    ## Deferments And Nonportable Claims

                    No runnable eval design.

                    ## Security, Privacy, And Durability

                    No raw logs are retained.

                    ## Closeout Evidence

                    Reviewed.
                    """
            )

            for host_local_path in (
                "/home/agent/.agents/skills/skill-creator/SKILL.md",
                r"C:\Users\agent\.agents\skills\skill-creator\SKILL.md",
            ):
                with self.subTest(host_local_path=host_local_path):
                    path.write_text(
                        template.format(host_local_path=host_local_path),
                        encoding="utf-8",
                    )
                    results = validate_skill_eval_methodology_source_intake(root)

                    self.assertIn(
                        CheckResult(
                            name="skill_eval_methodology_source_intake:portable_paths",
                            ok=False,
                            detail="ledger must not preserve host-local paths",
                            path=SKILL_EVAL_METHODOLOGY_SOURCE_INTAKE_PATH,
                        ),
                        results,
                    )

    def test_validate_skill_eval_methodology_source_intake_accepts_complete_ledger(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / SKILL_EVAL_METHODOLOGY_SOURCE_INTAKE_PATH
            path.parent.mkdir(parents=True)
            path.write_text(
                textwrap.dedent(
                    """\
                    # Skill-Eval Methodology Source Intake

                    Status: Source Disposition Ledger

                    ## Scope Boundary

                    Source intake only.

                    ## Portable Source Inventory

                    skill-creator/SKILL.md and adapting-skill-creator-to-harnesses/SKILL.md.

                    ## Reusable Techniques

                    behavioral evals, trigger-selection evals, harness adaptation,
                    description optimization, benchmarking, human review, grading,
                    packaging, and viewer/review workflow.

                    ## Downstream Routing

                    #61, #62, #67, #5, #155, #157, and later Forge work.

                    ## Deferments And Nonportable Claims

                    No runnable eval design.

                    ## Security, Privacy, And Durability

                    No raw logs are retained.

                    ## Closeout Evidence

                    Reviewed.
                    """
                ),
                encoding="utf-8",
            )

            results = validate_skill_eval_methodology_source_intake(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="skill_eval_methodology_source_intake:ledger",
                    ok=True,
                    detail="present",
                    path=SKILL_EVAL_METHODOLOGY_SOURCE_INTAKE_PATH,
                )
            ],
        )

    def test_validate_required_paths_reports_missing_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "README.md").write_text("# Demo\n", encoding="utf-8")

            results = validate_required_paths(root, ["README.md", "docs/missing.md"])

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="required_path:README.md",
                    ok=True,
                    detail="exists",
                    path="README.md",
                ),
                CheckResult(
                    name="required_path:docs/missing.md",
                    ok=False,
                    detail="missing",
                    path="docs/missing.md",
                ),
            ],
        )

    def test_find_markdown_links_ignores_external_and_anchor_links(self):
        markdown = textwrap.dedent(
            """
            [local](docs/start.md)
            [anchor](#section)
            [external](https://example.com)
            [mail](mailto:agent@example.test)
            """
        )

        self.assertEqual(find_markdown_links(markdown), ["docs/start.md"])

    def test_find_markdown_links_includes_outer_link_wrapping_badge(self):
        markdown = "[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)\n"

        self.assertEqual(find_markdown_links(markdown), ["LICENSE"])

    def test_find_markdown_links_strips_inline_titles(self):
        markdown = textwrap.dedent(
            """
            [quoted](docs/quoted.md "Title")
            [single](docs/single.md 'Title')
            [paren](docs/paren.md (Title))
            [angled](<docs/angled.md> "Title")
            """
        )

        self.assertEqual(
            find_markdown_links(markdown),
            [
                "docs/quoted.md",
                "docs/single.md",
                "docs/paren.md",
                "docs/angled.md",
            ],
        )

    def test_validate_python_runtime_declaration_accepts_matching_references(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".python-version").write_text("3.14\n", encoding="utf-8")
            (root / "tools").mkdir()
            (root / "tools/validate.py").write_text("#!/usr/bin/env python3.14\n", encoding="utf-8")
            (root / "docs").mkdir()
            (root / "docs/runtime.md").write_text("Use Python 3.14.\n", encoding="utf-8")

            results = validate_python_runtime_declaration(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="python_runtime:.python-version",
                    ok=True,
                    detail="declares Python 3.14",
                    path=".python-version",
                )
            ],
        )

    def test_validate_python_runtime_declaration_rejects_drifted_reference(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".python-version").write_text("3.15\n", encoding="utf-8")
            (root / "tools").mkdir()
            (root / "tools/validate.py").write_text("#!/usr/bin/env python3.14\n", encoding="utf-8")

            results = validate_python_runtime_declaration(root)

        self.assertIn(
            CheckResult(
                name="python_runtime:reference:tools/validate.py:3.14",
                ok=False,
                detail="Python runtime reference 3.14 does not match .python-version 3.15",
                path="tools/validate.py",
            ),
            results,
        )

    def test_validate_python_runtime_declaration_rejects_invalid_version_shape(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".python-version").write_text("python3.14\n", encoding="utf-8")

            results = validate_python_runtime_declaration(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="python_runtime:.python-version",
                    ok=False,
                    detail="must contain MAJOR.MINOR",
                    path=".python-version",
                )
            ],
        )

    def test_validate_python_runtime_declaration_ignores_historical_and_source_bearing_docs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            drifted_reference = "Python " + "3.13"
            (root / ".python-version").write_text("3.14\n", encoding="utf-8")
            (root / "tools").mkdir()
            (root / "tools/validate.py").write_text("#!/usr/bin/env python3.14\n", encoding="utf-8")
            (root / "docs/adr").mkdir(parents=True)
            (root / "docs/adr/0001-runtime-history.md").write_text(
                f"This historical decision mentioned {drifted_reference}.\n",
                encoding="utf-8",
            )
            (root / "docs/metasmith/handoff/2026-05-02").mkdir(parents=True)
            (root / "docs/metasmith/handoff/2026-05-02/provenance.md").write_text(
                f"Source-bearing provenance mentioned {drifted_reference}.\n",
                encoding="utf-8",
            )

            results = validate_python_runtime_declaration(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="python_runtime:.python-version",
                    ok=True,
                    detail="declares Python 3.14",
                    path=".python-version",
                )
            ],
        )

    def test_validate_python_runtime_declaration_rejects_closeout_reference_drift(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            drifted_version = "3.13"
            drifted_reference = f"Python {drifted_version}"
            (root / ".python-version").write_text("3.14\n", encoding="utf-8")
            (root / "docs/closeout").mkdir(parents=True)
            (root / "docs/closeout/summary.md").write_text(
                f"Closeout evidence mentioned {drifted_reference}.\n",
                encoding="utf-8",
            )

            results = validate_python_runtime_declaration(root)

        self.assertIn(
            CheckResult(
                name="python_runtime:reference:docs/closeout/summary.md:3.13",
                ok=False,
                detail=f"Python runtime reference {drifted_version} does not match .python-version 3.14",
                path="docs/closeout/summary.md",
            ),
            results,
        )

    def test_validate_python_runtime_declaration_ignores_symlinked_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            root = workspace / "repo"
            root.mkdir()
            drifted_reference = "Python " + "3.13"
            (root / ".python-version").write_text("3.14\n", encoding="utf-8")
            external_note = workspace / "external-runtime.md"
            external_note.write_text(f"External note mentioned {drifted_reference}.\n", encoding="utf-8")
            (root / "docs").mkdir()
            (root / "docs/runtime.md").symlink_to(external_note)

            results = validate_python_runtime_declaration(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="python_runtime:.python-version",
                    ok=True,
                    detail="declares Python 3.14",
                    path=".python-version",
                )
            ],
        )

    def test_validate_python_runtime_declaration_ignores_directory_iteration_errors(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".python-version").write_text("3.14\n", encoding="utf-8")

            with mock.patch.object(Path, "iterdir", side_effect=OSError("unreadable")):
                results = validate_python_runtime_declaration(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="python_runtime:.python-version",
                    ok=True,
                    detail="declares Python 3.14",
                    path=".python-version",
                )
            ],
        )

    def test_validate_python_runtime_declaration_ignores_local_work_directories(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            drifted_reference = "Python " + "3.13"
            (root / ".python-version").write_text("3.14\n", encoding="utf-8")
            (root / "tools").mkdir()
            (root / "tools/validate.py").write_text("#!/usr/bin/env python3.14\n", encoding="utf-8")
            (root / ".venv/lib").mkdir(parents=True)
            (root / ".venv/lib/runtime.txt").write_text(
                f"Tool output mentioned {drifted_reference}.\n",
                encoding="utf-8",
            )
            (root / "scratch").mkdir()
            (root / "scratch/runtime.txt").write_text(
                f"Scratch notes mentioned {drifted_reference}.\n",
                encoding="utf-8",
            )
            (root / "node_modules/demo").mkdir(parents=True)
            (root / "node_modules/demo/runtime.txt").write_text(
                f"Dependency notes mentioned {drifted_reference}.\n",
                encoding="utf-8",
            )

            results = validate_python_runtime_declaration(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="python_runtime:.python-version",
                    ok=True,
                    detail="declares Python 3.14",
                    path=".python-version",
                )
            ],
        )

    def test_find_markdown_links_includes_local_image_targets(self):
        markdown = "![Diagram](docs/diagram.png)\n"

        self.assertEqual(find_markdown_links(markdown), ["docs/diagram.png"])

    def test_find_markdown_links_ignores_inline_code_spans(self):
        markdown = "Use `[example](docs/missing.md)` when describing Markdown syntax.\n"

        self.assertEqual(find_markdown_links(markdown), [])

    def test_find_markdown_links_ignores_indented_code_blocks(self):
        markdown = textwrap.dedent(
            """
            [real](docs/real.md)

                [example](docs/missing.md)
            """
        )

        self.assertEqual(find_markdown_links(markdown), ["docs/real.md"])

    def test_find_markdown_links_includes_reference_definitions(self):
        markdown = textwrap.dedent(
            """
            See [guide][framework].

            [framework]: docs/framework.md "Framework"
            [absolute]: https://example.com/reference
            [anchor]: #local
            """
        )

        self.assertEqual(find_markdown_links(markdown), ["docs/framework.md"])

    def test_find_markdown_links_ignores_footnote_definitions(self):
        markdown = textwrap.dedent(
            """
            See this note.[^1]

            [^1]: This note is prose, not a link target.
            """
        )

        self.assertEqual(find_markdown_links(markdown), [])

    def test_validate_markdown_links_ignores_escaped_reference_use(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            (root / "docs/start.md").write_text(r"\[guide][missing]" + "\n", encoding="utf-8")

            results = validate_markdown_links(root)

        self.assertTrue(all(result.ok for result in results), results)

    def test_find_markdown_links_ignores_fenced_code_blocks(self):
        fence = "`" * 3
        markdown = textwrap.dedent(
            f"""
            [real](docs/real.md)

            {fence}markdown
            [fixture](docs/missing-fixture.md)
            {fence}

               {fence}python
               [indented](docs/missing-indented.md)
               {fence}

            ~~~~
            [tilde](docs/missing-tilde.md)
            ~~~~
            """
        )

        self.assertEqual(find_markdown_links(markdown), ["docs/real.md"])

    def test_load_toml_returns_data(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "catalog.toml"
            path.write_text('[harness.codex]\nversion = "0.128.0"\n', encoding="utf-8")

            self.assertEqual(load_toml(path), {"harness": {"codex": {"version": "0.128.0"}}})

    def test_render_human_summarizes_pass_and_fail(self):
        output = render_human(
            [
                CheckResult("alpha", True, "ok", "README.md"),
                CheckResult("beta", False, "missing", "docs/beta.md"),
            ]
        )

        self.assertIn("PASS alpha README.md - ok", output)
        self.assertIn("FAIL beta docs/beta.md - missing", output)
        self.assertIn("1 failed, 1 passed", output)


class SourceProjectionTests(unittest.TestCase):
    def write_register(self, root: Path, rows: list[str]) -> None:
        register = root / "docs/metasmith/source-projection.md"
        register.parent.mkdir(parents=True, exist_ok=True)
        register.write_text(
            textwrap.dedent(
                f"""
                # Source Projection Register

                | requirement_id | source_file | source_anchor | summary | disposition | target_path | deferment_reason | validation_status |
                | --- | --- | --- | --- | --- | --- | --- | --- |
                {chr(10).join(rows)}
                """
            ),
            encoding="utf-8",
        )

    def write_source_handoff_fixture(self, root: Path, omit: set[str] | None = None) -> None:
        omitted = omit or set()
        handoff = root / "docs/metasmith/handoff/2026-05-02"
        handoff.mkdir(parents=True, exist_ok=True)
        anchors_by_file: dict[str, list[str]] = {}
        for metadata in ACCEPTED_SOURCE_REQUIREMENTS.values():
            anchors_by_file.setdefault(metadata["source_file"], []).append(metadata["source_anchor"])
        for source_file, anchors in anchors_by_file.items():
            if source_file in omitted:
                continue
            (handoff / source_file).parent.mkdir(parents=True, exist_ok=True)
            (handoff / source_file).write_text(
                "\n".join(f"# {anchor}" for anchor in anchors) + "\n",
                encoding="utf-8",
            )

    def test_validate_source_projection_accepts_complete_inventory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            self.write_source_handoff_fixture(root)
            (root / "CONTEXT.md").write_text("# Fixture\n", encoding="utf-8")
            rows = [
                f"| {requirement_id} | {metadata['source_file']} | {metadata['source_anchor']} | Summary | projected | CONTEXT.md |  | {'planned' if requirement_id in SOURCE_PROJECTION_PLANNED_REQUIREMENTS else 'validated'} |"
                for requirement_id, metadata in ACCEPTED_SOURCE_REQUIREMENTS.items()
            ]
            self.write_register(root, rows)

            results = validate_source_projection(root)

        self.assertTrue(all(result.ok for result in results), results)

    def test_validate_source_projection_rejects_symlinked_register(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            register = root / "docs/metasmith/source-projection.md"
            register.parent.mkdir(parents=True)
            outside = root / "outside-register.md"
            outside.write_text("# Source Projection Register\n", encoding="utf-8")
            register.symlink_to(outside)

            results = validate_source_projection(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    name="source_projection:register",
                    ok=False,
                    detail="register path contains symlink",
                    path="docs/metasmith/source-projection.md",
                )
            ],
        )

    def test_validate_source_projection_rejects_wrong_source_reference(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            self.write_source_handoff_fixture(root)
            (root / "CONTEXT.md").write_text("# Fixture\n", encoding="utf-8")
            rows = [
                f"| {requirement_id} | {metadata['source_file']} | {metadata['source_anchor']} | Summary | projected | CONTEXT.md |  | {'planned' if requirement_id in SOURCE_PROJECTION_PLANNED_REQUIREMENTS else 'validated'} |"
                for requirement_id, metadata in ACCEPTED_SOURCE_REQUIREMENTS.items()
            ]
            rows[0] = rows[0].replace("00-metasmith-handoff-prompt.md", "wrong-source.md")
            self.write_register(root, rows)

            results = validate_source_projection(root)

        self.assertIn(
            CheckResult(
                name="source_projection:H001",
                ok=False,
                detail="source_file must be 00-metasmith-handoff-prompt.md",
                path="docs/metasmith/source-projection.md",
            ),
            results,
        )

    def test_validate_source_projection_rejects_missing_source_anchor(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            self.write_source_handoff_fixture(root)
            (root / "docs/metasmith/handoff/2026-05-02/00-metasmith-handoff-prompt.md").write_text(
                "# Different anchor\n",
                encoding="utf-8",
            )
            (root / "CONTEXT.md").write_text("# Fixture\n", encoding="utf-8")
            rows = [
                f"| {requirement_id} | {metadata['source_file']} | {metadata['source_anchor']} | Summary | projected | CONTEXT.md |  | {'planned' if requirement_id in SOURCE_PROJECTION_PLANNED_REQUIREMENTS else 'validated'} |"
                for requirement_id, metadata in ACCEPTED_SOURCE_REQUIREMENTS.items()
            ]
            self.write_register(root, rows)

            results = validate_source_projection(root)

        self.assertIn(
            CheckResult(
                name="source_projection:H001",
                ok=False,
                detail="source_anchor not found in 00-metasmith-handoff-prompt.md",
                path="docs/metasmith/source-projection.md",
            ),
            results,
        )

    def test_validate_source_projection_rejects_missing_source_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            self.write_source_handoff_fixture(root, omit={"00-metasmith-handoff-prompt.md"})
            (root / "CONTEXT.md").write_text("# Fixture\n", encoding="utf-8")
            rows = [
                f"| {requirement_id} | {metadata['source_file']} | {metadata['source_anchor']} | Summary | projected | CONTEXT.md |  | {'planned' if requirement_id in SOURCE_PROJECTION_PLANNED_REQUIREMENTS else 'validated'} |"
                for requirement_id, metadata in ACCEPTED_SOURCE_REQUIREMENTS.items()
            ]
            self.write_register(root, rows)

            results = validate_source_projection(root)

        self.assertIn(
            CheckResult(
                name="source_projection:H001",
                ok=False,
                detail="source_file missing: 00-metasmith-handoff-prompt.md",
                path="docs/metasmith/source-projection.md",
            ),
            results,
        )

    def test_validate_source_projection_rejects_symlinked_source_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_source_handoff_fixture(root)
            source = root / "docs/metasmith/handoff/2026-05-02/00-metasmith-handoff-prompt.md"
            source.unlink()
            outside = root / "outside-handoff.md"
            outside.write_text("# Your objective\n", encoding="utf-8")
            source.symlink_to(outside)
            (root / "docs/target.md").write_text("# Target\n", encoding="utf-8")
            self.write_register(
                root,
                [
                    "| H001 | 00-metasmith-handoff-prompt.md | Your objective | Summary | projected | docs/target.md |  | validated |"
                ],
            )

            results = validate_source_projection(root)

        self.assertIn(
            CheckResult(
                name="source_projection:H001",
                ok=False,
                detail="source_file invalid: 00-metasmith-handoff-prompt.md (manifest-listed file is a symlink)",
                path="docs/metasmith/source-projection.md",
            ),
            results,
        )

    def test_validate_source_projection_rejects_symlinked_handoff_root(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            handoff_parent = root / "docs/metasmith/handoff"
            handoff_parent.mkdir(parents=True)
            outside = root / "outside-handoff"
            outside.mkdir()
            (outside / "00-metasmith-handoff-prompt.md").write_text("# Your objective\n", encoding="utf-8")
            (handoff_parent / "2026-05-02").symlink_to(outside, target_is_directory=True)
            (root / "docs/target.md").write_text("# Target\n", encoding="utf-8")
            self.write_register(
                root,
                [
                    "| H001 | 00-metasmith-handoff-prompt.md | Your objective | Summary | projected | docs/target.md |  | validated |"
                ],
            )

            results = validate_source_projection(root)

        self.assertIn(
            CheckResult(
                name="source_projection:H001",
                ok=False,
                detail="source_file invalid: 00-metasmith-handoff-prompt.md (handoff directory path contains symlink)",
                path="docs/metasmith/source-projection.md",
            ),
            results,
        )

    def test_validate_source_projection_rejects_symlinked_projected_target(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_source_handoff_fixture(root)
            target = root / "docs/target.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            outside = root / "outside-target.md"
            outside.write_text("# Target\n", encoding="utf-8")
            target.symlink_to(outside)
            rows = [
                f"| {requirement_id} | {metadata['source_file']} | {metadata['source_anchor']} | Summary | projected | docs/target.md |  | {'planned' if requirement_id in SOURCE_PROJECTION_PLANNED_REQUIREMENTS else 'validated'} |"
                for requirement_id, metadata in ACCEPTED_SOURCE_REQUIREMENTS.items()
            ]
            self.write_register(root, rows)

            results = validate_source_projection(root)

        self.assertIn(
            CheckResult(
                name="source_projection:H001:target:docs/target.md",
                ok=False,
                detail="projected target invalid",
                path="docs/metasmith/source-projection.md",
            ),
            results,
        )

    def test_validate_source_projection_rejects_missing_projected_target(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_source_handoff_fixture(root)
            rows = [
                f"| {requirement_id} | {metadata['source_file']} | {metadata['source_anchor']} | Summary | projected | docs/missing.md |  | {'planned' if requirement_id in SOURCE_PROJECTION_PLANNED_REQUIREMENTS else 'validated'} |"
                for requirement_id, metadata in ACCEPTED_SOURCE_REQUIREMENTS.items()
            ]
            self.write_register(root, rows)

            results = validate_source_projection(root)

        self.assertIn(
            CheckResult(
                name="source_projection:H001:target:docs/missing.md",
                ok=False,
                detail="projected target missing",
                path="docs/metasmith/source-projection.md",
            ),
            results,
        )

    def test_validate_source_projection_accepts_deferred_future_target_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            self.write_source_handoff_fixture(root)
            (root / "CONTEXT.md").write_text("# Fixture\n", encoding="utf-8")
            rows = [
                f"| {requirement_id} | {metadata['source_file']} | {metadata['source_anchor']} | Summary | projected | CONTEXT.md |  | {'planned' if requirement_id in SOURCE_PROJECTION_PLANNED_REQUIREMENTS else 'validated'} |"
                for requirement_id, metadata in ACCEPTED_SOURCE_REQUIREMENTS.items()
            ]
            rows[0] = "| H001 | 00-metasmith-handoff-prompt.md | Your objective | Defer seed objective | deferred | specs/future-work.md | Deferred until follow-up. | planned |"
            self.write_register(root, rows)

            results = validate_source_projection(root)

        self.assertTrue(all(result.ok for result in results), results)

    def test_validate_source_projection_rejects_unknown_validation_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            self.write_source_handoff_fixture(root)
            (root / "CONTEXT.md").write_text("# Fixture\n", encoding="utf-8")
            rows = [
                f"| {requirement_id} | {metadata['source_file']} | {metadata['source_anchor']} | Summary | projected | CONTEXT.md |  | {'planned' if requirement_id in SOURCE_PROJECTION_PLANNED_REQUIREMENTS else 'validated'} |"
                for requirement_id, metadata in ACCEPTED_SOURCE_REQUIREMENTS.items()
            ]
            rows[0] = rows[0].replace(" | validated |", " | done |")
            self.write_register(root, rows)

            results = validate_source_projection(root)

        self.assertIn(
            CheckResult(
                name="source_projection:H001",
                ok=False,
                detail="validation_status must be planned or validated",
                path="docs/metasmith/source-projection.md",
            ),
            results,
        )

    def test_validate_source_projection_rejects_premature_validated_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            self.write_source_handoff_fixture(root)
            (root / "CONTEXT.md").write_text("# Fixture\n", encoding="utf-8")
            rows = []
            for requirement_id, metadata in ACCEPTED_SOURCE_REQUIREMENTS.items():
                status = "validated" if requirement_id in SOURCE_PROJECTION_PLANNED_REQUIREMENTS else "planned"
                rows.append(
                    f"| {requirement_id} | {metadata['source_file']} | {metadata['source_anchor']} | Summary | projected | CONTEXT.md |  | {status} |"
                )
            self.write_register(root, rows)

            results = validate_source_projection(root)

        self.assertIn(
            CheckResult(
                name="source_projection:H012",
                ok=False,
                detail="validation_status must remain planned until closeout evidence lands",
                path="docs/metasmith/source-projection.md",
            ),
            results,
        )

    def test_validate_source_projection_rejects_stale_planned_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            self.write_source_handoff_fixture(root)
            (root / "CONTEXT.md").write_text("# Fixture\n", encoding="utf-8")
            rows = []
            for requirement_id, metadata in ACCEPTED_SOURCE_REQUIREMENTS.items():
                status = "planned" if requirement_id == "H001" else "validated"
                if requirement_id in SOURCE_PROJECTION_PLANNED_REQUIREMENTS:
                    status = "planned"
                rows.append(
                    f"| {requirement_id} | {metadata['source_file']} | {metadata['source_anchor']} | Summary | projected | CONTEXT.md |  | {status} |"
                )
            self.write_register(root, rows)

            results = validate_source_projection(root)

        self.assertIn(
            CheckResult(
                name="source_projection:H001",
                ok=False,
                detail="validation_status must be validated for completed projected requirement",
                path="docs/metasmith/source-projection.md",
            ),
            results,
        )

    def test_validate_source_projection_rejects_deferred_url_target(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_source_handoff_fixture(root)
            self.write_register(
                root,
                [
                    "| H001 | 00-metasmith-handoff-prompt.md | Your objective | Defer seed objective | deferred | file:///tmp/future.md | Deferred until follow-up. | planned |"
                ],
            )

            results = validate_source_projection(root)

        self.assertIn(
            CheckResult(
                name="source_projection:H001:target:file:///tmp/future.md",
                ok=False,
                detail="deferred target invalid",
                path="docs/metasmith/source-projection.md",
            ),
            results,
        )

    def test_validate_source_projection_rejects_deferred_parent_traversal_target(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_source_handoff_fixture(root)
            self.write_register(
                root,
                [
                    "| H001 | 00-metasmith-handoff-prompt.md | Your objective | Defer seed objective | deferred | ../future.md | Deferred until follow-up. | planned |"
                ],
            )

            results = validate_source_projection(root)

        self.assertIn(
            CheckResult(
                name="source_projection:H001:target:../future.md",
                ok=False,
                detail="deferred target invalid",
                path="docs/metasmith/source-projection.md",
            ),
            results,
        )

    def test_validate_source_projection_rejects_missing_accepted_requirement(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            self.write_source_handoff_fixture(root)
            (root / "CONTEXT.md").write_text("# Fixture\n", encoding="utf-8")
            self.write_register(
                root,
                [
                    "| H001 | 00-metasmith-handoff-prompt.md | Required content | Project vocabulary docs | projected | CONTEXT.md |  | planned |"
                ],
            )

            results = validate_source_projection(root)

        self.assertTrue(
            any(
                result.name == "source_projection:coverage"
                and not result.ok
                and result.detail.startswith("missing accepted requirements: H002")
                for result in results
            ),
            results,
        )

    def test_validate_source_projection_rejects_unknown_requirement(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_register(
                root,
                [
                    "| H999 | 08-initial-smith-task-specs.md | Agent Ops | Unknown task | deferred | specs/future-work.md | Deferred until follow-up. | planned |"
                ],
            )

            results = validate_source_projection(root)

        self.assertIn(
            CheckResult(
                name="source_projection:coverage",
                ok=False,
                detail="unknown requirement ids: H999",
                path="docs/metasmith/source-projection.md",
            ),
            results,
        )

    def test_validate_source_projection_rejects_duplicate_requirement(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            self.write_source_handoff_fixture(root)
            (root / "CONTEXT.md").write_text("# Fixture\n", encoding="utf-8")
            rows = [
                f"| {requirement_id} | {metadata['source_file']} | {metadata['source_anchor']} | Summary | projected | CONTEXT.md |  | {'planned' if requirement_id in SOURCE_PROJECTION_PLANNED_REQUIREMENTS else 'validated'} |"
                for requirement_id, metadata in ACCEPTED_SOURCE_REQUIREMENTS.items()
            ]
            rows.append(rows[0])
            self.write_register(root, rows)

            results = validate_source_projection(root)

        self.assertIn(
            CheckResult(
                name="source_projection:coverage",
                ok=False,
                detail="duplicate requirement ids: H001",
                path="docs/metasmith/source-projection.md",
            ),
            results,
        )

    def test_validate_source_projection_rejects_deferred_without_reason(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            register = root / "docs/metasmith/source-projection.md"
            register.parent.mkdir(parents=True)
            register.write_text(
                textwrap.dedent(
                    """
                    # Source Projection Register

                    | requirement_id | source_file | source_anchor | summary | disposition | target_path | deferment_reason | validation_status |
                    | --- | --- | --- | --- | --- | --- | --- | --- |
                    | H999 | 08-initial-smith-task-specs.md | Agent Ops | Implement Agent Ops | deferred |  |  | planned |
                    """
                ),
                encoding="utf-8",
            )

            results = validate_source_projection(root)

        self.assertIn(
            CheckResult(
                name="source_projection:H999",
                ok=False,
                detail="deferred requirement missing deferment_reason",
                path="docs/metasmith/source-projection.md",
            ),
            results,
        )

    def test_validate_source_projection_rejects_deferred_without_target(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_source_handoff_fixture(root)
            self.write_register(
                root,
                [
                    "| H001 | 00-metasmith-handoff-prompt.md | Your objective | Defer seed objective | deferred |  | Deferred until follow-up. | planned |"
                ],
            )

            results = validate_source_projection(root)

        self.assertIn(
            CheckResult(
                name="source_projection:H001",
                ok=False,
                detail="deferred requirement missing downstream target_path",
                path="docs/metasmith/source-projection.md",
            ),
            results,
        )

    def test_validate_source_handoff_provenance_checks_manifest_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            handoff = root / "docs/metasmith/handoff/2026-05-02"
            handoff.mkdir(parents=True)
            (handoff / "AGENTS.md").write_text(
                "# Handoff Provenance\n\nTreat the manifest-listed source files in this directory as provenance, not current operating instructions.\n",
                encoding="utf-8",
            )
            (handoff / "manifest.json").write_text(
                json.dumps({"files": ["README.md", "00-metasmith-handoff-prompt.md"]}),
                encoding="utf-8",
            )
            (handoff / "README.md").write_text("# Bundle\n", encoding="utf-8")

            results = validate_source_handoff_provenance(root)

        self.assertIn(
            CheckResult(
                name="source_handoff:file:00-metasmith-handoff-prompt.md",
                ok=False,
                detail="manifest-listed file missing",
                path="docs/metasmith/handoff/2026-05-02/00-metasmith-handoff-prompt.md",
            ),
            results,
        )

    def test_validate_source_handoff_provenance_rejects_invalid_manifest_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            handoff = root / "docs/metasmith/handoff/2026-05-02"
            handoff.mkdir(parents=True)
            (handoff / "AGENTS.md").write_text(
                "# Handoff Provenance\n\nTreat the manifest-listed source files in this directory as provenance, not current operating instructions.\n",
                encoding="utf-8",
            )
            (handoff / "manifest.json").write_text("not json", encoding="utf-8")

            results = validate_source_handoff_provenance(root)

        self.assertIn(
            CheckResult(
                name="source_handoff:manifest_json",
                ok=False,
                detail="manifest JSON invalid: Expecting value",
                path="docs/metasmith/handoff/2026-05-02/manifest.json",
            ),
            results,
        )

    def test_validate_source_handoff_provenance_rejects_non_object_manifest_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            handoff = root / "docs/metasmith/handoff/2026-05-02"
            handoff.mkdir(parents=True)
            (handoff / "AGENTS.md").write_text(
                "# Handoff Provenance\n\nTreat the manifest-listed source files in this directory as provenance, not current operating instructions.\n",
                encoding="utf-8",
            )
            (handoff / "manifest.json").write_text("[]", encoding="utf-8")

            results = validate_source_handoff_provenance(root)

        self.assertIn(
            CheckResult(
                name="source_handoff:manifest_json",
                ok=False,
                detail="manifest JSON must be an object",
                path="docs/metasmith/handoff/2026-05-02/manifest.json",
            ),
            results,
        )

    def test_validate_source_handoff_provenance_rejects_manifest_without_files_key(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            handoff = root / "docs/metasmith/handoff/2026-05-02"
            handoff.mkdir(parents=True)
            (handoff / "AGENTS.md").write_text(
                "# Handoff Provenance\n\nTreat the manifest-listed source files in this directory as provenance, not current operating instructions.\n",
                encoding="utf-8",
            )
            (handoff / "manifest.json").write_text(json.dumps({}), encoding="utf-8")

            results = validate_source_handoff_provenance(root)

        self.assertIn(
            CheckResult(
                name="source_handoff:manifest_files",
                ok=False,
                detail="manifest files must be a non-empty list",
                path="docs/metasmith/handoff/2026-05-02/manifest.json",
            ),
            results,
        )

    def test_validate_source_handoff_provenance_rejects_empty_manifest_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            handoff = root / "docs/metasmith/handoff/2026-05-02"
            handoff.mkdir(parents=True)
            (handoff / "AGENTS.md").write_text(
                "# Handoff Provenance\n\nTreat the manifest-listed source files in this directory as provenance, not current operating instructions.\n",
                encoding="utf-8",
            )
            (handoff / "manifest.json").write_text(json.dumps({"files": []}), encoding="utf-8")

            results = validate_source_handoff_provenance(root)

        self.assertIn(
            CheckResult(
                name="source_handoff:manifest_files",
                ok=False,
                detail="manifest files must be a non-empty list",
                path="docs/metasmith/handoff/2026-05-02/manifest.json",
            ),
            results,
        )

    def test_validate_source_handoff_provenance_rejects_null_manifest_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            handoff = root / "docs/metasmith/handoff/2026-05-02"
            handoff.mkdir(parents=True)
            (handoff / "AGENTS.md").write_text(
                "# Handoff Provenance\n\nTreat the manifest-listed source files in this directory as provenance, not current operating instructions.\n",
                encoding="utf-8",
            )
            (handoff / "manifest.json").write_text(json.dumps({"files": None}), encoding="utf-8")

            results = validate_source_handoff_provenance(root)

        self.assertIn(
            CheckResult(
                name="source_handoff:manifest_files",
                ok=False,
                detail="manifest files must be a non-empty list",
                path="docs/metasmith/handoff/2026-05-02/manifest.json",
            ),
            results,
        )

    def test_validate_source_handoff_provenance_rejects_string_manifest_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            handoff = root / "docs/metasmith/handoff/2026-05-02"
            handoff.mkdir(parents=True)
            (handoff / "AGENTS.md").write_text(
                "# Handoff Provenance\n\nTreat the manifest-listed source files in this directory as provenance, not current operating instructions.\n",
                encoding="utf-8",
            )
            (handoff / "manifest.json").write_text(json.dumps({"files": "README.md"}), encoding="utf-8")

            results = validate_source_handoff_provenance(root)

        self.assertIn(
            CheckResult(
                name="source_handoff:manifest_files",
                ok=False,
                detail="manifest files must be a non-empty list",
                path="docs/metasmith/handoff/2026-05-02/manifest.json",
            ),
            results,
        )

    def test_validate_source_handoff_provenance_rejects_manifest_missing_accepted_source(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_source_handoff_fixture(root)
            handoff = root / "docs/metasmith/handoff/2026-05-02"
            (handoff / "AGENTS.md").write_text(
                "# Handoff Provenance\n\nTreat the manifest-listed source files in this directory as provenance, not current operating instructions.\n",
                encoding="utf-8",
            )
            source_files = sorted({metadata["source_file"] for metadata in ACCEPTED_SOURCE_REQUIREMENTS.values()})
            source_files.remove("00-metasmith-handoff-prompt.md")
            (handoff / "manifest.json").write_text(json.dumps({"files": source_files}), encoding="utf-8")

            results = validate_source_handoff_provenance(root)

        self.assertIn(
            CheckResult(
                name="source_handoff:manifest_coverage",
                ok=False,
                detail="accepted source files missing from manifest: 00-metasmith-handoff-prompt.md",
                path="docs/metasmith/handoff/2026-05-02/manifest.json",
            ),
            results,
        )

    def test_validate_source_handoff_provenance_rejects_symlink_handoff_root(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            handoff_parent = root / "docs/metasmith/handoff"
            handoff_parent.mkdir(parents=True)
            outside = root / "outside-handoff"
            outside.mkdir()
            (outside / "AGENTS.md").write_text(
                "# Handoff Provenance\n\nTreat the manifest-listed source files in this directory as provenance, not current operating instructions.\n",
                encoding="utf-8",
            )
            (outside / "manifest.json").write_text(
                json.dumps({"files": ["00-metasmith-handoff-prompt.md"]}),
                encoding="utf-8",
            )
            (outside / "00-metasmith-handoff-prompt.md").write_text("# Your objective\n", encoding="utf-8")
            (handoff_parent / "2026-05-02").symlink_to(outside, target_is_directory=True)

            results = validate_source_handoff_provenance(root)

        self.assertIn(
            CheckResult(
                name="source_handoff:root",
                ok=False,
                detail="handoff directory path contains symlink",
                path="docs/metasmith/handoff/2026-05-02",
            ),
            results,
        )

    def test_validate_source_handoff_provenance_rejects_symlink_manifest(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            handoff = root / "docs/metasmith/handoff/2026-05-02"
            handoff.mkdir(parents=True)
            (handoff / "AGENTS.md").write_text(
                "# Handoff Provenance\n\nTreat the manifest-listed source files in this directory as provenance, not current operating instructions.\n",
                encoding="utf-8",
            )
            outside_manifest = root / "outside-manifest.json"
            outside_manifest.write_text(json.dumps({"files": []}), encoding="utf-8")
            (handoff / "manifest.json").symlink_to(outside_manifest)

            results = validate_source_handoff_provenance(root)

        self.assertIn(
            CheckResult(
                name="source_handoff:manifest_path",
                ok=False,
                detail="manifest path contains symlink",
                path="docs/metasmith/handoff/2026-05-02/manifest.json",
            ),
            results,
        )

    def test_validate_source_handoff_provenance_rejects_symlink_provenance_notice(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_source_handoff_fixture(root)
            handoff = root / "docs/metasmith/handoff/2026-05-02"
            source_files = sorted({metadata["source_file"] for metadata in ACCEPTED_SOURCE_REQUIREMENTS.values()})
            (handoff / "manifest.json").write_text(json.dumps({"files": source_files}), encoding="utf-8")
            outside_notice = root / "outside-AGENTS.md"
            outside_notice.write_text(
                "# Outside Instructions\n\nTreat this as current operating instructions.\n",
                encoding="utf-8",
            )
            (handoff / "AGENTS.md").symlink_to(outside_notice)

            results = validate_source_handoff_provenance(root)

        self.assertIn(
            CheckResult(
                name="source_handoff:provenance_notice_path",
                ok=False,
                detail="provenance notice path contains symlink",
                path="docs/metasmith/handoff/2026-05-02/AGENTS.md",
            ),
            results,
        )

    def test_validate_source_handoff_provenance_rejects_symlink_manifest_entry(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            handoff = root / "docs/metasmith/handoff/2026-05-02"
            handoff.mkdir(parents=True)
            (handoff / "AGENTS.md").write_text(
                "# Handoff Provenance\n\nTreat the manifest-listed source files in this directory as provenance, not current operating instructions.\n",
                encoding="utf-8",
            )
            outside = root / "outside-handoff.md"
            outside.write_text("# Outside bundle\n", encoding="utf-8")
            (handoff / "00-metasmith-handoff-prompt.md").symlink_to(outside)
            (handoff / "manifest.json").write_text(
                json.dumps({"files": ["00-metasmith-handoff-prompt.md"]}),
                encoding="utf-8",
            )

            results = validate_source_handoff_provenance(root)

        self.assertIn(
            CheckResult(
                name="source_handoff:file:00-metasmith-handoff-prompt.md",
                ok=False,
                detail="manifest-listed file is a symlink",
                path="docs/metasmith/handoff/2026-05-02/00-metasmith-handoff-prompt.md",
            ),
            results,
        )

    def test_validate_source_handoff_provenance_rejects_blank_manifest_entry(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            handoff = root / "docs/metasmith/handoff/2026-05-02"
            handoff.mkdir(parents=True)
            (handoff / "AGENTS.md").write_text(
                "# Handoff Provenance\n\nTreat the manifest-listed source files in this directory as provenance, not current operating instructions.\n",
                encoding="utf-8",
            )
            (handoff / "manifest.json").write_text(
                json.dumps({"files": [""]}),
                encoding="utf-8",
            )

            results = validate_source_handoff_provenance(root)

        self.assertIn(
            CheckResult(
                name="source_handoff:file:",
                ok=False,
                detail="manifest file path invalid",
                path="docs/metasmith/handoff/2026-05-02/manifest.json",
            ),
            results,
        )

    def test_validate_source_handoff_provenance_rejects_directory_manifest_entry(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            handoff = root / "docs/metasmith/handoff/2026-05-02"
            handoff.mkdir(parents=True)
            (handoff / "AGENTS.md").write_text(
                "# Handoff Provenance\n\nTreat the manifest-listed source files in this directory as provenance, not current operating instructions.\n",
                encoding="utf-8",
            )
            (handoff / "manifest.json").write_text(
                json.dumps({"files": ["."]}),
                encoding="utf-8",
            )

            results = validate_source_handoff_provenance(root)

        self.assertIn(
            CheckResult(
                name="source_handoff:file:.",
                ok=False,
                detail="manifest-listed file missing",
                path="docs/metasmith/handoff/2026-05-02/.",
            ),
            results,
        )

    def test_validate_source_handoff_provenance_rejects_manifest_traversal(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "README.md").write_text("# Outside bundle\n", encoding="utf-8")
            handoff = root / "docs/metasmith/handoff/2026-05-02"
            handoff.mkdir(parents=True)
            (handoff / "AGENTS.md").write_text(
                "# Handoff Provenance\n\nTreat the manifest-listed source files in this directory as provenance, not current operating instructions.\n",
                encoding="utf-8",
            )
            (handoff / "manifest.json").write_text(
                json.dumps({"files": ["../../../../README.md"]}),
                encoding="utf-8",
            )

            results = validate_source_handoff_provenance(root)

        self.assertIn(
            CheckResult(
                name="source_handoff:file:../../../../README.md",
                ok=False,
                detail="manifest file path invalid",
                path="docs/metasmith/handoff/2026-05-02/manifest.json",
            ),
            results,
        )

    def test_validate_source_handoff_provenance_rejects_manifest_url(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            handoff = root / "docs/metasmith/handoff/2026-05-02"
            handoff.mkdir(parents=True)
            (handoff / "AGENTS.md").write_text(
                "# Handoff Provenance\n\nTreat the manifest-listed source files in this directory as provenance, not current operating instructions.\n",
                encoding="utf-8",
            )
            (handoff / "manifest.json").write_text(
                json.dumps({"files": ["file:///tmp/handoff.md"]}),
                encoding="utf-8",
            )

            results = validate_source_handoff_provenance(root)

        self.assertIn(
            CheckResult(
                name="source_handoff:file:file:///tmp/handoff.md",
                ok=False,
                detail="manifest file path invalid",
                path="docs/metasmith/handoff/2026-05-02/manifest.json",
            ),
            results,
        )


class SourceDispositionTests(unittest.TestCase):
    def write_source_disposition(
        self,
        root: Path,
        *,
        synthetic_payload: str = "accepted requirement constants H001 H002",
    ) -> None:
        path = root / SOURCE_DISPOSITION_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        manifest_rows = [
            {
                "source_id": "SYN001",
                "source_kind": "synthetic",
                "original_path": "tools/validate_armory_integrity.py",
                "git_blob_id": "abc123",
                "sha256": "def456",
                "normalized_payload_digest": "789abc",
                "durable_payload": synthetic_payload,
            }
        ]
        item_rows = [
            {
                "item_id": "I001",
                "source_id": "SYN001",
                "coverage_status": "adequately_captured",
                "challenge_status": "unchallenged",
                "challenge_operator_confirmation_required": "false",
                "arbitration_required": "false",
                "disposition": "kept_current",
                "operator_decision": "",
                "evidence_target": "docs/agent-equipment-forge.md",
                "normalized_claim_summary": "Keep the synthetic accepted requirement in the Forge docs.",
            },
            {
                "item_id": "I002",
                "source_id": "SYN001",
                "coverage_status": "partially_captured",
                "challenge_status": "resolved",
                "challenge_operator_confirmation_required": "true",
                "arbitration_required": "true",
                "disposition": "integrated",
                "operator_decision": "Operator accepted integration.",
                "evidence_target": "docs/follow-ups/portable-agentic-engineering-workflow-equipment.md",
                "normalized_claim_summary": "Capture the portable workflow equipment follow-up.",
            },
        ]
        source_manifest_digest = source_disposition_table_digest(
            manifest_rows,
            SOURCE_DISPOSITION_MANIFEST_FIELDS,
        )
        source_disposition_digest = source_disposition_table_digest(
            item_rows,
            SOURCE_DISPOSITION_ITEM_FIELDS,
        )
        path.write_text(
            textwrap.dedent(
                f"""
                # Forge Seed Source Disposition

                Status: Source Bearing

                ## Source Manifest

                | source_id | source_kind | original_path | git_blob_id | sha256 | normalized_payload_digest | durable_payload |
                | --- | --- | --- | --- | --- | --- | --- |
                | SYN001 | synthetic | tools/validate_armory_integrity.py | abc123 | def456 | 789abc | {synthetic_payload} |

                ## Disposition Items

                | item_id | source_id | coverage_status | challenge_status | challenge_operator_confirmation_required | arbitration_required | disposition | operator_decision | evidence_target | normalized_claim_summary |
                | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
                | I001 | SYN001 | adequately_captured | unchallenged | false | false | kept_current |  | docs/agent-equipment-forge.md | Keep the synthetic accepted requirement in the Forge docs. |
                | I002 | SYN001 | partially_captured | resolved | true | true | integrated | Operator accepted integration. | docs/follow-ups/portable-agentic-engineering-workflow-equipment.md | Capture the portable workflow equipment follow-up. |

                ## Source-Bearing Stamp

                source_bearing_snapshot_tree_id: source-tree
                source_bearing_stamp_id: source-bearing-1
                source_manifest_digest: {source_manifest_digest}
                source_disposition_digest: {source_disposition_digest}
                source_bearing_result: passed

                ## Final Source-Retired Stamp

                source_retired: true
                """
            ).strip()
            + "\n",
            encoding="utf-8",
        )

    def test_validate_source_disposition_accepts_self_contained_synthetic_payload(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            (root / "docs/agent-equipment-forge.md").write_text("# Forge\n", encoding="utf-8")
            (root / "docs/follow-ups").mkdir()
            (root / "docs/follow-ups/portable-agentic-engineering-workflow-equipment.md").write_text(
                "# Follow-up\n",
                encoding="utf-8",
            )
            self.write_source_disposition(root)

            results = validate_source_disposition(root)

        self.assertTrue(all(result.ok for result in results), results)

    def test_validate_source_disposition_rejects_synthetic_source_without_durable_payload(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_source_disposition(root, synthetic_payload="")

            results = validate_source_disposition(root)

        self.assertIn(
            CheckResult(
                "source_disposition:source:SYN001",
                False,
                "synthetic source missing durable payload",
                SOURCE_DISPOSITION_PATH,
            ),
            results,
        )

    def test_validate_source_disposition_rejects_malformed_file_source_identity(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_source_disposition(root)
            path = root / SOURCE_DISPOSITION_PATH
            path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "| SYN001 | synthetic | tools/validate_armory_integrity.py | abc123 | def456 | 789abc | accepted requirement constants H001 H002 |",
                    "| SYN001 | file | docs/metasmith/source-projection.md |  | def456 | 789abc | retired source file |",
                ),
                encoding="utf-8",
            )

            results = validate_source_disposition(root)

        self.assertIn(
            CheckResult(
                "source_disposition:source:SYN001",
                False,
                "file source git_blob_id must be a 40-character hex object id",
                SOURCE_DISPOSITION_PATH,
            ),
            results,
        )

    def test_validate_source_disposition_rejects_integrated_item_without_arbitration(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_source_disposition(root)
            path = root / SOURCE_DISPOSITION_PATH
            path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "| I002 | SYN001 | partially_captured | resolved | true | true | integrated | Operator accepted integration. | docs/follow-ups/portable-agentic-engineering-workflow-equipment.md | Capture the portable workflow equipment follow-up. |",
                    "| I002 | SYN001 | partially_captured | resolved | false | false | integrated |  | docs/follow-ups/portable-agentic-engineering-workflow-equipment.md | Capture the portable workflow equipment follow-up. |",
                ),
                encoding="utf-8",
            )

            results = validate_source_disposition(root)

        self.assertIn(
            CheckResult(
                "source_disposition:item:I002",
                False,
                "integrated disposition requires arbitration and operator_decision",
                SOURCE_DISPOSITION_PATH,
            ),
            results,
        )

    def test_validate_source_disposition_rejects_missing_normalized_claim_summary(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_source_disposition(root)
            path = root / SOURCE_DISPOSITION_PATH
            path.write_text(
                path.read_text(encoding="utf-8").replace(" | normalized_claim_summary", ""),
                encoding="utf-8",
            )

            results = validate_source_disposition(root)

        self.assertIn(
            CheckResult(
                "source_disposition:item:I001",
                False,
                "missing fields: normalized_claim_summary",
                SOURCE_DISPOSITION_PATH,
            ),
            results,
        )

    def test_validate_source_disposition_rejects_empty_normalized_claim_summary(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_source_disposition(root)
            path = root / SOURCE_DISPOSITION_PATH
            path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "| I001 | SYN001 | adequately_captured | unchallenged | false | false | kept_current |  | docs/agent-equipment-forge.md | Keep the synthetic accepted requirement in the Forge docs. |",
                    "| I001 | SYN001 | adequately_captured | unchallenged | false | false | kept_current |  | docs/agent-equipment-forge.md |  |",
                ),
                encoding="utf-8",
            )

            results = validate_source_disposition(root)

        self.assertIn(
            CheckResult(
                "source_disposition:item:I001",
                False,
                "normalized_claim_summary required",
                SOURCE_DISPOSITION_PATH,
            ),
            results,
        )

    def test_validate_source_disposition_rejects_source_manifest_digest_mismatch(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_source_disposition(root)
            path = root / SOURCE_DISPOSITION_PATH
            path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "source_manifest_digest: ",
                    "source_manifest_digest: bad",
                    1,
                ),
                encoding="utf-8",
            )

            results = validate_source_disposition(root)

        self.assertIn(
            CheckResult(
                "source_disposition:source_manifest_digest",
                False,
                "source_manifest_digest mismatch",
                SOURCE_DISPOSITION_PATH,
            ),
            results,
        )

    def test_validate_source_disposition_rejects_missing_source_bearing_stamp_field(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_source_disposition(root)
            path = root / SOURCE_DISPOSITION_PATH
            path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "\nsource_bearing_result: passed",
                    "",
                ),
                encoding="utf-8",
            )

            results = validate_source_disposition(root)

        self.assertIn(
            CheckResult(
                "source_disposition:stamp:source_bearing_result",
                False,
                "missing source_bearing_result",
                SOURCE_DISPOSITION_PATH,
            ),
            results,
        )

    def test_validate_source_retired_tree_requires_final_source_item_coverage(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            (root / "docs/agent-equipment-forge.md").write_text("# Forge\n", encoding="utf-8")
            (root / "docs/follow-ups").mkdir()
            (root / "docs/follow-ups/portable-agentic-engineering-workflow-equipment.md").write_text(
                "# Follow-up\n",
                encoding="utf-8",
            )
            self.write_source_disposition(root)

            results = validate_source_retired_tree(root)

        self.assertTrue(
            any(
                result
                == CheckResult(
                    "source_disposition:required_items",
                    False,
                    result.detail,
                    SOURCE_DISPOSITION_PATH,
                )
                and "H001" in result.detail
                for result in results
            ),
            results,
        )

    def test_validate_source_disposition_rejects_symlink_evidence_target(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            outside = root / "outside.md"
            outside.write_text("# Outside\n", encoding="utf-8")
            (root / "docs").mkdir()
            (root / "docs/agent-equipment-forge.md").symlink_to(outside)
            (root / "docs/follow-ups").mkdir()
            (root / "docs/follow-ups/portable-agentic-engineering-workflow-equipment.md").write_text(
                "# Follow-up\n",
                encoding="utf-8",
            )
            self.write_source_disposition(root)

            results = validate_source_disposition(root)

        self.assertIn(
            CheckResult(
                "source_disposition:item:I001:target:docs/agent-equipment-forge.md",
                False,
                "evidence target path contains symlink",
                SOURCE_DISPOSITION_PATH,
            ),
            results,
        )

    def test_validate_source_retired_tree_rejects_raw_forgewright_sources(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs/metasmith/handoff").mkdir(parents=True)
            self.write_source_disposition(root)

            results = validate_source_retired_tree(root)

        self.assertIn(
            CheckResult(
                "source_retired:raw_sources",
                False,
                "docs/metasmith must be removed after source disposition",
                "docs/metasmith",
            ),
            results,
        )

    def test_validate_source_retired_tree_rejects_dangling_raw_source_symlink(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            (root / "docs/metasmith").symlink_to(root / "missing")
            self.write_source_disposition(root)

            results = validate_source_retired_tree(root)

        self.assertIn(
            CheckResult(
                "source_retired:raw_sources",
                False,
                "docs/metasmith must be removed after source disposition",
                "docs/metasmith",
            ),
            results,
        )

    def test_validate_final_source_retired_stamp_accepts_stable_retired_marker(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_source_disposition(root)

            results = validate_final_source_retired_stamp(root)

        self.assertTrue(all(result.ok for result in results), results)
        self.assertIn(
            CheckResult(
                "source_retired_stamp:source_retired",
                True,
                "true",
                SOURCE_DISPOSITION_PATH,
            ),
            results,
        )

    def test_validate_final_source_retired_stamp_scopes_fields_to_final_section(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_source_disposition(root)
            path = root / SOURCE_DISPOSITION_PATH
            markdown = path.read_text(encoding="utf-8")
            path.write_text(
                markdown.replace(
                    "## Final Source-Retired Stamp",
                    "\n".join(
                        [
                            "stamp_target: source-bearing tree",
                            "canonical_tree_digest: legacy-source-bearing-digest",
                            "timestamp: 2026-05-04T00:00:00Z",
                            "",
                            "## Final Source-Retired Stamp",
                        ]
                    ),
                ),
                encoding="utf-8",
            )

            results = validate_final_source_retired_stamp(root)

        self.assertTrue(all(result.ok for result in results), results)
        self.assertIn(
            CheckResult(
                "source_retired_stamp:source_retired",
                True,
                "true",
                SOURCE_DISPOSITION_PATH,
            ),
            results,
        )

    def test_validate_final_source_retired_stamp_rejects_volatile_digest_fields(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_source_disposition(root)
            path = root / SOURCE_DISPOSITION_PATH
            markdown = path.read_text(encoding="utf-8")
            path.write_text(
                markdown.replace(
                    "source_retired: true",
                    "\n".join(
                        [
                            "stamp_target: placeholder-normalized canonical tree",
                            "canonical_tree_digest: abc123",
                            "source_retired: true",
                            "timestamp: 2026-05-04T00:00:00Z",
                        ]
                    ),
                ),
                encoding="utf-8",
            )

            results = validate_final_source_retired_stamp(root)

        self.assertIn(
            CheckResult(
                "source_retired_stamp:canonical_tree_digest",
                False,
                "canonical_tree_digest is volatile and must be removed",
                SOURCE_DISPOSITION_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "source_retired_stamp:stamp_target",
                False,
                "stamp_target is volatile and must be removed",
                SOURCE_DISPOSITION_PATH,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "source_retired_stamp:timestamp",
                False,
                "timestamp is volatile and must be removed",
                SOURCE_DISPOSITION_PATH,
            ),
            results,
        )

    def test_run_validates_live_source_disposition_without_raw_source_inputs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            (root / "docs/agent-equipment-forge.md").write_text("# Forge\n", encoding="utf-8")
            (root / "docs/follow-ups").mkdir()
            (root / "docs/follow-ups/portable-agentic-engineering-workflow-equipment.md").write_text(
                "# Follow-up\n",
                encoding="utf-8",
            )
            self.write_source_disposition(root)

            results = run(root)

        self.assertNotIn(
            CheckResult(
                "required_path:docs/metasmith/source-projection.md",
                False,
                "missing",
                "docs/metasmith/source-projection.md",
            ),
            results,
        )
        self.assertFalse(
            any(result.name.startswith(("source_projection:", "source_handoff:")) for result in results),
            results,
        )
        self.assertIn(
            CheckResult(
                "source_disposition:ledger",
                True,
                "present",
                SOURCE_DISPOSITION_PATH,
            ),
            results,
        )
        self.assertEqual(sum(result.name == "source_disposition:ledger" for result in results), 1)

class ForgeRouteTests(unittest.TestCase):
    def test_validate_forge_routes_requires_agent_and_human_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "AGENTS.md").write_text("# AGENTS\n", encoding="utf-8")
            (root / "README.md").write_text("# README\n", encoding="utf-8")

            results = validate_forge_routes(root)

        self.assertIn(
            CheckResult("forge_route:agent", False, "missing Forge Conveyor", "AGENTS.md"),
            results,
        )
        self.assertIn(
            CheckResult("forge_route:human", False, "missing Forge Tour", "README.md"),
            results,
        )

    def test_validate_forge_routes_requires_all_preloaded_links(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "AGENTS.md").write_text(
                textwrap.dedent(
                    """
                    # AGENTS

                    ## Forge Conveyor

                    - `docs/vision.md`
                    - `docs/agent-equipment-forge.md`
                    - `docs/smith-runbook.md`
                    - `docs/harness-capabilities.md`
                    - `templates/`
                    - `specs/`
                    """
                ),
                encoding="utf-8",
            )
            (root / "README.md").write_text(
                "## Agent Equipment Forge\n\nStart with [Forge Tour](docs/forge-tour.md).\n",
                encoding="utf-8",
            )

            results = validate_forge_routes(root)

        self.assertIn(
            CheckResult(
                "forge_route:agent:docs/interface-decision-guide.md",
                False,
                "missing required preloaded route",
                "AGENTS.md",
            ),
            results,
        )

    def test_validate_forge_routes_rejects_unresolved_route_targets(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            (root / "templates").mkdir()
            (root / "specs").mkdir()
            for path in [
                "docs/vision.md",
                "docs/agent-equipment-forge.md",
                "docs/smith-runbook.md",
                "docs/interface-decision-guide.md",
            ]:
                (root / path).write_text("# Fixture\n", encoding="utf-8")
            (root / "AGENTS.md").write_text(
                textwrap.dedent(
                    """
                    # AGENTS

                    ## Forge Conveyor

                    - `docs/vision.md`
                    - `docs/agent-equipment-forge.md`
                    - `docs/smith-runbook.md`
                    - `docs/interface-decision-guide.md`
                    - `docs/harness-capabilities.md`
                    - `templates/`
                    - `specs/`
                    """
                ),
                encoding="utf-8",
            )
            (root / "README.md").write_text(
                "## Agent Equipment Forge\n\nStart with [Forge Tour](docs/forge-tour.md).\n",
                encoding="utf-8",
            )

            results = validate_forge_routes(root)

        self.assertIn(
            CheckResult(
                "forge_route:target:docs/harness-capabilities.md",
                False,
                "route target missing",
                "AGENTS.md",
            ),
            results,
        )

    def test_validate_forge_routes_rejects_wrong_route_target_kind(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            (root / "docs/vision.md").write_text("# Fixture\n", encoding="utf-8")
            (root / "docs/agent-equipment-forge.md").mkdir()
            (root / "docs/smith-runbook.md").write_text("# Fixture\n", encoding="utf-8")
            (root / "docs/interface-decision-guide.md").write_text("# Fixture\n", encoding="utf-8")
            (root / "docs/harness-capabilities.md").write_text("# Fixture\n", encoding="utf-8")
            (root / "templates").write_text("not a directory\n", encoding="utf-8")
            (root / "specs").mkdir()
            (root / "AGENTS.md").write_text(
                textwrap.dedent(
                    """
                    # AGENTS

                    ## Forge Conveyor

                    - `docs/vision.md`
                    - `docs/agent-equipment-forge.md`
                    - `docs/smith-runbook.md`
                    - `docs/interface-decision-guide.md`
                    - `docs/harness-capabilities.md`
                    - `templates/`
                    - `specs/`
                    """
                ),
                encoding="utf-8",
            )
            (root / "README.md").write_text(
                "## Agent Equipment Forge\n\nStart with [Forge Tour](docs/forge-tour.md).\n",
                encoding="utf-8",
            )

            results = validate_forge_routes(root)

        self.assertIn(
            CheckResult(
                "forge_route:target:docs/agent-equipment-forge.md",
                False,
                "route target not a file",
                "AGENTS.md",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "forge_route:target:templates/",
                False,
                "route target not a directory",
                "AGENTS.md",
            ),
            results,
        )


class CanonicalDocTests(unittest.TestCase):
    canonical_docs = {
        "docs/vision.md": [
            "Experience",
            "Equipment",
            "Deterministic boundaries",
            "Harness lifecycle",
            "Self-onboarding",
            "Metacognitive loop",
            "Reflection",
            "Lifecycle use",
        ],
        "docs/agent-equipment-forge.md": [
            "Purpose",
            "Vision alignment",
            "Least cognitive privilege",
            "Component model",
            "Context management",
            "Security",
            "Maintenance",
        ],
        "docs/smith-runbook.md": [
            "Capability card",
            "Interface decision record",
            "Docs/config/scripts/hooks/skills/agents/plugins",
            "Pressure Scenario Validation",
            "Equipment Promotion Path",
            "Tooling Request",
            "Closeout",
        ],
        "docs/forgewright-runbook.md": [
            "Source handoff preservation",
            "decision projection",
            "Review Until Clean",
            "Harness Fact Refresh",
            "Change set closeout",
            "Issue Projection",
            "Equipment Blueprints",
            "Tooling Gap intake",
        ],
        "docs/interface-decision-guide.md": ["Decision tree", "placement guide"],
        "docs/harness-components.md": [
            "Skills",
            "MCP/tools",
            "hooks",
            "Agent Profiles",
            "Harness Plugins",
            "scripts",
            "local docs",
            "config",
        ],
        "docs/harness-capabilities.md": [
            "Catalog policy",
            "Refresh summary",
            "Harness matrix",
            "Harness notes",
            "Periodic Actions projection order",
            "Refresh requirement",
        ],
        "docs/evidence-taxonomy.md": [
            "documentation-supported",
            "source-supported",
            "implementation inference",
            "practitioner wisdom",
            "hypothesis",
            "artifact durability",
            "source hygiene",
        ],
        "docs/security-and-control.md": [
            "least privilege",
            "mutation gates",
            "secrets",
            "hooks",
            "MCP/tool side effects",
            "examples caveat",
        ],
        "docs/equipment-promotion.md": [
            "example",
            "specified",
            "planned",
            "implemented",
            "validated",
            "published",
            "entry/exit criteria",
        ],
        "docs/story-closeout.md": [
            "Purpose",
            "Gate order",
            "Interdependency rules",
            "Review gates",
            "Recursion and bookkeeping",
            "Completion criteria",
        ],
    }
    canonical_doc_required_text = {
        "docs/vision.md": [
            "autonomous self-onboarding to purpose-built assemblies of harness components",
            "Use this vision as an input throughout the engineering lifecycle.",
        ],
        "docs/smith-runbook.md": [
            "When a Smith finds an unsatisfied Tooling Gap that blocks or materially weakens the current equipment task, treat the Tooling Work as a dependency and escalate to a Forgewright before continuing.",
            "Choose the least disruptive Forgewright path supported by the harness and operator policy: current session, subagent session, peer agent session, forked session, or new session.",
            "The handoff must include the blocked task, unsatisfied Tooling Gap, dependency impact, evidence checked, requested Forgewright deliverable, selected session path, and hand-back expectation.",
            "docs, config, scripts, hooks, skills, MCP/tools, Agent Profiles, plugins, and templates are discoverable from the Forge Conveyor",
            "Run a Cross-Boundary Coherence Ralph Review before story closeout.",
            "Run a Story Quality Ralph Review before story closeout.",
        ],
        "docs/forgewright-runbook.md": [
            "A Forgewright intake from a Smith starts by preserving the Smith handoff, refining the Tooling Gap, updating canonical surfaces and validation, and returning a hand-back note.",
            "The hand-back note names files changed, validation and review results, dependency updates, remaining risks, and the context the Smith needs to resume.",
        ],
        "docs/story-closeout.md": [
            "Story Closeout is the story-level gate; Change Set Security Closeout and Change Set Documentation Closeout are subordinate gates.",
            "Refresh the Intent Model before downstream closeout gates.",
            "Before committing or externally projecting closeout evidence, classify evidence artifacts by durability.",
            "Durable project evidence and portable review summaries may be committed or projected.",
            "Instance-scoped scratch artifacts, including raw tool reports, local scan bundles, copied diffs, host-local paths, screenshots, or work directories, should be summarized by scope, disposition, and durable conclusions instead of treated as project truth.",
            "Classify privacy and disclosure limits for actionable Reflection Findings",
            "Run Cross-Boundary Coherence before Story Quality because quality review depends on coherent process evidence.",
            "Intent Model Refresh is the first closeout gate.",
            "Update the agent's model of Underlying Intent by reviewing recent operator input, accepted ADR/PRD/spec/plan changes, review dispositions, handoff notes, and observed corrections relevant to the story before running downstream closeout gates.",
            "Story Quality also runs an Intent Alignment Check.",
            "Compare Effective Intent, meaning the Intent actually imposed by ADRs, PRDs, specs, plans, acceptance criteria, review dispositions, and other declarations, with the refreshed model of Underlying Intent after Cross-Boundary Coherence has made Effective Intent legible.",
            "Refresh the model again if closeout evidence introduced new intent signals.",
            "An agent does not directly know a stakeholder's or other intent-capable actor's Underlying Intent; it maintains an evidence-backed model that can be tested through questions, experiments, and observed corrections.",
            "Hypotheses about emotion, belief state, attention, engagement, discipline, or other internal disposition can explain why a mismatch might exist, but they are not evidence by themselves and must not justify unilateral realignment.",
            "When observable evidence shows misalignment beyond reasonable doubt, realign the affected declarations and reproject downstream implications.",
            "When the model remains uncertain, the case depends on internal-state inference, or the evidence otherwise creates a non-dismissible likelihood of misalignment without certainty, raise a concise question to the operator, using an interactive question tool when available.",
            "If a revision changes security, documentation, validation, PRD/spec/plan scope, or issue/PR projection, rerun the affected upstream gate before the next closeout review.",
            "Evidence-artifact durability changes rerun the closeout gate that owns the artifact and any projection surface that carries its claims.",
            "after privacy and disclosure limits are classified",
            "Recording the latest clean review result is bookkeeping and does not reopen the full review loop unless it changes substantive claims.",
            "Published issue, PR, release, or handoff corrections rerun a projection consistency check and a narrow Cross-Boundary Coherence review for the corrected surface.",
            "closeout evidence artifacts are classified by durability",
            "instance-scoped scratch artifacts are summarized rather than committed or externally projected as project truth",
        ],
    }

    def write_canonical_doc(self, root: Path, relative_path: str, sections: list[str] | None = None) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if relative_path == "docs/story-closeout.md" and sections is None:
            section_markdown = textwrap.dedent(
                """
                ## Purpose

                Content.

                ## Gate order

                1. Refresh the Intent Model before downstream closeout gates.
                2. Confirm the implementation, specs, plans, and deterministic validation reflect the same scope.
                3. Complete Change Set Security Closeout for the current change set.
                4. Complete Change Set Documentation Closeout for affected human-facing and agent-facing docs.
                5. Prepare projection drafts for issues, PR bodies, handoff notes, and release summaries from the current story evidence.
                6. Classify privacy and disclosure limits for actionable Reflection Findings discovered during the story, then route publishable findings into the issue tracker, Tooling Request, or the relevant Equipment Candidate, or record why the insight is not durable or not projectable.
                7. Run Cross-Boundary Coherence before Story Quality because quality review depends on coherent process evidence.
                8. Run Story Quality Ralph Review after coherence findings are fixed or soundly rejected.
                9. Run final validation and publication-readiness checks required by the active plan or repository policy.
                10. Push or otherwise publish the branch only when the active plan, operator direction, or issue-projection surface needs a pushed commit before PR creation.
                11. Publish or update issue, PR, release, and handoff surfaces from the clean final story evidence.
                12. Perform publication actions that remain in scope.

                ## Interdependency rules

                Content.

                ## Review gates

                Content.

                ## Recursion and bookkeeping

                Content.

                ## Completion criteria

                Content.
                """
            )
        else:
            section_markdown = "\n".join(f"## {section}\n\nContent.\n" for section in (sections or self.canonical_docs[relative_path]))
        required_text = "\n".join(self.canonical_doc_required_text.get(relative_path, []))
        status = CANONICAL_DOC_STATUSES[relative_path]
        path.write_text(f"# {path.stem}\n\nStatus: {status}\n\n{section_markdown}\n{required_text}\n", encoding="utf-8")

    def write_all_canonical_docs(self, root: Path) -> None:
        for relative_path in self.canonical_docs:
            self.write_canonical_doc(root, relative_path)

    def test_validate_canonical_docs_reports_missing_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = validate_canonical_docs(root)

        self.assertIn(
            CheckResult(
                "canonical_doc:docs/agent-equipment-forge.md",
                False,
                "missing",
                "docs/agent-equipment-forge.md",
            ),
            results,
        )

    def test_validate_canonical_docs_requires_story_closeout_doc(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            for relative_path in self.canonical_docs:
                if relative_path != "docs/story-closeout.md":
                    self.write_canonical_doc(root, relative_path)

            results = validate_canonical_docs(root)

        self.assertIn(
            CheckResult(
                "canonical_doc:docs/story-closeout.md",
                False,
                "missing",
                "docs/story-closeout.md",
            ),
            results,
        )

    def test_validate_canonical_docs_rejects_story_closeout_gate_order(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_canonical_docs(root)
            story_path = root / "docs/story-closeout.md"
            story_text = story_path.read_text(encoding="utf-8")
            story_text = story_text.replace(
                "5. Prepare projection drafts for issues, PR bodies, handoff notes, and release summaries from the current story evidence.",
                "5. Run Cross-Boundary Coherence before Story Quality because quality review depends on coherent process evidence.",
            ).replace(
                "7. Run Cross-Boundary Coherence before Story Quality because quality review depends on coherent process evidence.",
                "7. Prepare projection drafts for issues, PR bodies, handoff notes, and release summaries from the current story evidence.",
            )
            story_path.write_text(story_text, encoding="utf-8")

            results = validate_canonical_docs(root)

        self.assertIn(
            CheckResult(
                name="canonical_doc:story_closeout_gate_order:docs/story-closeout.md",
                ok=False,
                detail="gate order must include required items in order",
                path="docs/story-closeout.md",
            ),
            results,
        )

    def test_validate_canonical_docs_rejects_story_closeout_missing_reflection_route(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_canonical_docs(root)
            story_path = root / "docs/story-closeout.md"
            story_text = story_path.read_text(encoding="utf-8").replace(
                "6. Classify privacy and disclosure limits for actionable Reflection Findings discovered during the story, then route publishable findings into the issue tracker, Tooling Request, or the relevant Equipment Candidate, or record why the insight is not durable or not projectable.",
                "6. Record workflow observations before review.",
            )
            story_path.write_text(story_text, encoding="utf-8")

            results = validate_canonical_docs(root)

        self.assertIn(
            CheckResult(
                name="canonical_doc:story_closeout_gate_order:docs/story-closeout.md",
                ok=False,
                detail="gate order must include required items in order",
                path="docs/story-closeout.md",
            ),
            results,
        )

    def test_validate_canonical_docs_rejects_story_closeout_missing_branch_push_gate(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_canonical_docs(root)
            story_path = root / "docs/story-closeout.md"
            story_text = story_path.read_text(encoding="utf-8").replace(
                "10. Push or otherwise publish the branch only when the active plan, operator direction, or issue-projection surface needs a pushed commit before PR creation.",
                "10. Record local publication notes.",
            )
            story_path.write_text(story_text, encoding="utf-8")

            results = validate_canonical_docs(root)

        self.assertIn(
            CheckResult(
                name="canonical_doc:story_closeout_gate_order:docs/story-closeout.md",
                ok=False,
                detail="gate order must include required items in order",
                path="docs/story-closeout.md",
            ),
            results,
        )

    def test_validate_canonical_docs_requires_story_closeout_publication_correction_rule(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_canonical_docs(root)
            story_path = root / "docs/story-closeout.md"
            missing_text = "Published issue, PR, release, or handoff corrections rerun a projection consistency check and a narrow Cross-Boundary Coherence review for the corrected surface."
            story_path.write_text(story_path.read_text(encoding="utf-8").replace(missing_text, ""), encoding="utf-8")

            results = validate_canonical_docs(root)

        self.assertIn(
            CheckResult(
                f"canonical_doc:text:docs/story-closeout.md:{missing_text}",
                False,
                f"missing text: {missing_text}",
                "docs/story-closeout.md",
            ),
            results,
        )

    def test_validate_canonical_docs_requires_live_canonical_status(self):
        expected_status = CANONICAL_DOC_STATUSES["docs/agent-equipment-forge.md"]
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_canonical_docs(root)
            (root / "docs/agent-equipment-forge.md").write_text(
                "# Equipment Framework\n\n## Purpose\n\nContent.\n",
                encoding="utf-8",
            )

            results = validate_canonical_docs(root)

        self.assertIn(
            CheckResult(
                "canonical_doc:status:docs/agent-equipment-forge.md",
                False,
                f"missing Status: {expected_status}",
                "docs/agent-equipment-forge.md",
            ),
            results,
        )

    def test_validate_canonical_docs_reports_missing_status_mapping(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_canonical_docs(root)
            with mock.patch.dict(CANONICAL_DOC_STATUSES, {}, clear=True):
                results = validate_canonical_docs(root)

        self.assertIn(
            CheckResult(
                "canonical_doc:status_mapping:docs/agent-equipment-forge.md",
                False,
                "missing canonical status mapping",
                "docs/agent-equipment-forge.md",
            ),
            results,
        )

    def test_validate_canonical_docs_ignores_status_in_fenced_code(self):
        expected_status = CANONICAL_DOC_STATUSES["docs/agent-equipment-forge.md"]
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_canonical_docs(root)
            fence = "`" * 3
            (root / "docs/agent-equipment-forge.md").write_text(
                f"# Equipment Framework\n\n{fence}\nStatus: {expected_status}\n{fence}\n\n## Purpose\n\nContent.\n",
                encoding="utf-8",
            )

            results = validate_canonical_docs(root)

        self.assertIn(
            CheckResult(
                "canonical_doc:status:docs/agent-equipment-forge.md",
                False,
                f"missing Status: {expected_status}",
                "docs/agent-equipment-forge.md",
            ),
            results,
        )

    def test_validate_canonical_docs_requires_sections(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_canonical_docs(root)
            self.write_canonical_doc(root, "docs/agent-equipment-forge.md", sections=["Purpose"])

            results = validate_canonical_docs(root)

        self.assertIn(
            CheckResult(
                "canonical_doc:section:docs/agent-equipment-forge.md:Maintenance",
                False,
                "missing section: Maintenance",
                "docs/agent-equipment-forge.md",
            ),
            results,
        )

    def test_validate_canonical_docs_ignores_sections_in_indented_code(self):
        expected_status = CANONICAL_DOC_STATUSES["docs/agent-equipment-forge.md"]
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_canonical_docs(root)
            (root / "docs/agent-equipment-forge.md").write_text(
                textwrap.dedent(
                    f"""
                    # Equipment Framework

                    Status: {expected_status}

                    ## Purpose

                    Content.

                        ## Maintenance
                    """
                ),
                encoding="utf-8",
            )

            results = validate_canonical_docs(root)

        self.assertIn(
            CheckResult(
                "canonical_doc:section:docs/agent-equipment-forge.md:Maintenance",
                False,
                "missing section: Maintenance",
                "docs/agent-equipment-forge.md",
            ),
            results,
        )

    def test_validate_canonical_docs_requires_closeout_text(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_canonical_docs(root)
            self.write_canonical_doc(root, "docs/smith-runbook.md")
            missing_text = self.canonical_doc_required_text["docs/smith-runbook.md"][0]
            (root / "docs/smith-runbook.md").write_text(
                (root / "docs/smith-runbook.md").read_text(encoding="utf-8").replace(missing_text, ""),
                encoding="utf-8",
            )

            results = validate_canonical_docs(root)

        self.assertIn(
            CheckResult(
                f"canonical_doc:text:docs/smith-runbook.md:{missing_text}",
                False,
                f"missing text: {missing_text}",
                "docs/smith-runbook.md",
            ),
            results,
        )

    def test_validate_canonical_docs_requires_story_closeout_review_gates(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_canonical_docs(root)
            self.write_canonical_doc(root, "docs/smith-runbook.md")
            missing_text = "Run a Cross-Boundary Coherence Ralph Review before story closeout."
            (root / "docs/smith-runbook.md").write_text(
                (root / "docs/smith-runbook.md").read_text(encoding="utf-8").replace(missing_text, ""),
                encoding="utf-8",
            )

            results = validate_canonical_docs(root)

        self.assertIn(
            CheckResult(
                f"canonical_doc:text:docs/smith-runbook.md:{missing_text}",
                False,
                f"missing text: {missing_text}",
                "docs/smith-runbook.md",
            ),
            results,
        )

    def test_run_reports_missing_canonical_docs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = run(root)

        self.assertIn(
            CheckResult(
                "required_path:docs/agent-equipment-forge.md",
                False,
                "missing",
                "docs/agent-equipment-forge.md",
            ),
            results,
        )

    def test_run_reports_every_missing_canonical_doc(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = run(root)

        for relative_path in self.canonical_docs:
            self.assertIn(
                CheckResult(f"required_path:{relative_path}", False, "missing", relative_path),
                results,
            )
            self.assertIn(
                CheckResult(f"canonical_doc:{relative_path}", False, "missing", relative_path),
                results,
            )

    def test_run_reports_canonical_doc_status_and_section_failures(self):
        expected_status = CANONICAL_DOC_STATUSES["docs/agent-equipment-forge.md"]
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_canonical_docs(root)
            (root / "docs/agent-equipment-forge.md").write_text(
                "# Equipment Framework\n\n## Purpose\n\nContent.\n",
                encoding="utf-8",
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "canonical_doc:status:docs/agent-equipment-forge.md",
                False,
                f"missing Status: {expected_status}",
                "docs/agent-equipment-forge.md",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "canonical_doc:section:docs/agent-equipment-forge.md:Maintenance",
                False,
                "missing section: Maintenance",
                "docs/agent-equipment-forge.md",
            ),
            results,
        )


class ContextDocTests(unittest.TestCase):
    def valid_context(self) -> str:
        sections = "\n".join(f"## {section}\n\nContent.\n" for section in CONTEXT_REQUIRED_SECTIONS)
        return f"# Agent Armory\n\n{sections}"

    def test_validate_context_accepts_required_sections(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "CONTEXT.md").write_text(self.valid_context(), encoding="utf-8")

            results = validate_context(root)

        self.assertEqual(results, [])

    def test_validate_context_rejects_each_missing_required_section(self):
        for missing_section in CONTEXT_REQUIRED_SECTIONS:
            with self.subTest(missing_section=missing_section):
                with tempfile.TemporaryDirectory() as tmpdir:
                    root = Path(tmpdir)
                    sections = [
                        section for section in CONTEXT_REQUIRED_SECTIONS if section != missing_section
                    ]
                    markdown = "# Agent Armory\n\n" + "\n".join(
                        f"## {section}\n\nContent.\n" for section in sections
                    )
                    (root / "CONTEXT.md").write_text(markdown, encoding="utf-8")

                    results = validate_context(root)

                self.assertIn(
                    CheckResult(
                        f"context:section:{missing_section}",
                        False,
                        f"missing section: {missing_section}",
                        "CONTEXT.md",
                    ),
                    results,
                )


class ThreatModelValidationTests(unittest.TestCase):
    threat_model_path = "docs/security/threat-model.md"
    security_surface_path = "docs/security-and-control.md"
    required_sections = [
        "Assets",
        "Trust boundaries",
        "Attacker-controlled inputs",
        "Invariants",
        "Assumptions",
        "High-impact failure modes",
    ]

    def valid_threat_model(self) -> str:
        sections = "\n".join(f"## {section}\n\nContent.\n" for section in self.required_sections)
        return f"# Agent Armory Repository Threat Model\n\nStatus: Repository Threat Model\n\n{sections}"

    def write_valid_threat_model_surface(self, root: Path) -> None:
        threat_model = root / self.threat_model_path
        threat_model.parent.mkdir(parents=True, exist_ok=True)
        threat_model.write_text(self.valid_threat_model(), encoding="utf-8")
        security_surface = root / self.security_surface_path
        security_surface.parent.mkdir(parents=True, exist_ok=True)
        security_surface.write_text(
            "# Security and Control\n\nSee [Repository Threat Model](security/threat-model.md).\n",
            encoding="utf-8",
        )

    def test_validate_threat_model_reports_missing_surface(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = validate_threat_model(root)

        self.assertIn(
            CheckResult(
                f"threat_model:path:{self.threat_model_path}",
                False,
                "missing",
                self.threat_model_path,
            ),
            results,
        )

    def test_validate_threat_model_accepts_complete_surface(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_threat_model_surface(root)

            results = validate_threat_model(root)

        self.assertTrue(all(result.ok for result in results), results)

    def test_validate_threat_model_requires_sections(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_threat_model_surface(root)
            path = root / self.threat_model_path
            path.write_text(self.valid_threat_model().replace("## Invariants\n\nContent.\n", ""), encoding="utf-8")

            results = validate_threat_model(root)

        self.assertIn(
            CheckResult(
                f"threat_model:section:{self.threat_model_path}:Invariants",
                False,
                "missing section: Invariants",
                self.threat_model_path,
            ),
            results,
        )

    def test_validate_threat_model_requires_canonical_reference(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_threat_model_surface(root)
            (root / self.security_surface_path).write_text("# Security and Control\n", encoding="utf-8")

            results = validate_threat_model(root)

        self.assertIn(
            CheckResult(
                f"threat_model:reference:{self.security_surface_path}",
                False,
                "missing threat model reference",
                self.security_surface_path,
            ),
            results,
        )

    def test_run_requires_threat_model_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = run(root)

        self.assertIn(
            CheckResult(f"required_path:{self.threat_model_path}", False, "missing", self.threat_model_path),
            results,
        )


class DocumentationCloseoutValidationTests(unittest.TestCase):
    closeout_path = "docs/closeout/forge-seed-documentation.md"
    required_sections = [
        "Scope of inspected docs",
        "Docs changed",
        "Docs unchanged with rationale",
        "Stale-language cleanup result",
        "Established precedents added or updated",
        "Review status",
        "Residual documentation risk",
    ]

    def valid_closeout(self) -> str:
        sections = "\n\n".join(
            [
                "## Scope of inspected docs\n\nInspected `README.md`, `AGENTS.md`, `CONTEXT.md`, `docs/external-tool-evaluation.md`, `docs/evaluations/harbor.md`, `docs/agents/*.md`, Forge Canon under `docs/*.md`, `docs/prd/forge-seed.md`, `docs/adr/*.md`, `docs/plans/2026-05-03-forge-seed.md`, `docs/security/*.md`, `docs/closeout/*.md`, `docs/closeout/forge-seed-source-disposition.md`, `specs/*.md`, `templates/**/*.md`, and `examples/**/*.md`.",
                "## Docs changed\n\nUpdated `docs/security/threat-model.md` and `docs/metasmith/source-projection.md`.",
                "## Docs unchanged with rationale\n\nRecorded why `README.md` and `AGENTS.md` needed no change.",
                "## Stale-language cleanup result\n\nStale initial-state language was searched and resolved.",
                "## Established precedents added or updated\n\nRecorded Forge Seed precedents. Portable workflow capture says a branch-push pause does not close the capture. Full Seed completion requires a merged Seed. An explicit hold or cancellation continues capture through an unmerged-state hand-back and should record the unmerged state directly.",
                "## Review status\n\n- Documentation closeout: Ralph Review Cycle 99.\n- Cross-Boundary Coherence: Ralph Review Cycle 100.\n- Story Quality: Ralph Review Cycle 101.",
                "## Residual documentation risk\n\nResidual documentation risk is tracked for pending security closeout.",
            ]
        )
        return f"# Forge Seed Documentation Closeout\n\nStatus: Completed Closeout\n\n{sections}"

    def write_closeout(self, root: Path, content: str | None = None) -> None:
        path = root / self.closeout_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content or self.valid_closeout(), encoding="utf-8")

    def test_validate_documentation_closeout_reports_missing_surface(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = validate_documentation_closeout(root)

        self.assertIn(
            CheckResult(
                f"documentation_closeout:path:{self.closeout_path}",
                False,
                "missing",
                self.closeout_path,
            ),
            results,
        )

    def test_validate_documentation_closeout_accepts_complete_surface(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_closeout(root)

            results = validate_documentation_closeout(root)

        self.assertTrue(all(result.ok for result in results), results)

    def test_validate_documentation_closeout_requires_sections(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_closeout(
                root,
                self.valid_closeout().replace(
                    "## Stale-language cleanup result\n\nStale initial-state language was searched and resolved.\n\n",
                    "",
                ),
            )

            results = validate_documentation_closeout(root)

        self.assertIn(
            CheckResult(
                f"documentation_closeout:section:{self.closeout_path}:Stale-language cleanup result",
                False,
                "missing section: Stale-language cleanup result",
                self.closeout_path,
            ),
            results,
        )

    def test_validate_documentation_closeout_rejects_incomplete_review_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_closeout(root, self.valid_closeout().replace("Status: Completed Closeout", "Status: In Progress"))

            results = validate_documentation_closeout(root)

        self.assertIn(
            CheckResult(
                f"documentation_closeout:status:{self.closeout_path}",
                False,
                "missing completed closeout status",
                self.closeout_path,
            ),
            results,
        )

    def test_validate_documentation_closeout_rejects_unresolved_review_placeholder(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_closeout(
                root,
                self.valid_closeout()
                + "\n\nThis final documentation closeout summary still requires review. Record that review result here after it completes.\n",
            )

            results = validate_documentation_closeout(root)

        self.assertIn(
            CheckResult(
                f"documentation_closeout:review:{self.closeout_path}",
                False,
                "contains unresolved review placeholder",
                self.closeout_path,
            ),
            results,
        )

    def test_validate_documentation_closeout_rejects_pending_review_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_closeout(
                root,
                self.valid_closeout().replace(
                    "- Documentation closeout: Ralph Review Cycle 99.",
                    "- Documentation closeout: pending.",
                ),
            )

            results = validate_documentation_closeout(root)

        self.assertIn(
            CheckResult(
                f"documentation_closeout:review:{self.closeout_path}:Documentation closeout",
                False,
                "review status must name a Ralph Review Cycle: Documentation closeout",
                self.closeout_path,
            ),
            results,
        )

    def test_validate_documentation_closeout_requires_closeout_evidence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            sections = "\n".join(f"## {section}\n\nContent.\n" for section in self.required_sections)
            self.write_closeout(root, f"# Forge Seed Documentation Closeout\n\nStatus: Completed Closeout\n\n{sections}")

            results = validate_documentation_closeout(root)

        self.assertIn(
            CheckResult(
                f"documentation_closeout:evidence:{self.closeout_path}:Cross-Boundary Coherence",
                False,
                "missing evidence: Cross-Boundary Coherence",
                self.closeout_path,
            ),
            results,
        )

    def test_validate_documentation_closeout_requires_full_scope_evidence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_closeout(root, self.valid_closeout().replace("`specs/*.md`, ", ""))

            results = validate_documentation_closeout(root)

        self.assertIn(
            CheckResult(
                f"documentation_closeout:evidence:{self.closeout_path}:specs/*.md",
                False,
                "missing evidence: specs/*.md",
                self.closeout_path,
            ),
            results,
        )

    def test_validate_documentation_closeout_requires_external_tool_evidence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_closeout(root, self.valid_closeout().replace(f"`{EXTERNAL_TOOL_EVALUATION_PATH}`, ", ""))

            results = validate_documentation_closeout(root)

        self.assertIn(
            CheckResult(
                f"documentation_closeout:evidence:{self.closeout_path}:{EXTERNAL_TOOL_EVALUATION_PATH}",
                False,
                f"missing evidence: {EXTERNAL_TOOL_EVALUATION_PATH}",
                self.closeout_path,
            ),
            results,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_closeout(
                root,
                self.valid_closeout().replace(f"`{HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH}`, ", ""),
            )

            results = validate_documentation_closeout(root)

        self.assertIn(
            CheckResult(
                f"documentation_closeout:evidence:{self.closeout_path}:{HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH}",
                False,
                f"missing evidence: {HARBOR_EXTERNAL_TOOL_EVALUATION_RECORD_PATH}",
                self.closeout_path,
            ),
            results,
        )

    def test_validate_documentation_closeout_requires_completion_window_evidence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_closeout(
                root,
                self.valid_closeout().replace(
                    "Portable workflow capture says a branch-push pause does not close the capture. Full Seed completion requires a merged Seed. An explicit hold or cancellation continues capture through an unmerged-state hand-back and should record the unmerged state directly.",
                    "Portable workflow capture is recorded.",
                ),
            )

            results = validate_documentation_closeout(root)

        self.assertIn(
            CheckResult(
                f"documentation_closeout:evidence:{self.closeout_path}:branch-push pause does not close the capture",
                False,
                "missing evidence: branch-push pause does not close the capture",
                self.closeout_path,
            ),
            results,
        )

    def test_validate_documentation_closeout_requires_hold_cancel_condition(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_closeout(
                root,
                self.valid_closeout().replace(
                    "An explicit hold or cancellation continues capture through an unmerged-state hand-back and should record the unmerged state directly.",
                    "A stopped Seed keeps an unmerged-state hand-back.",
                ),
            )

            results = validate_documentation_closeout(root)

        self.assertIn(
            CheckResult(
                f"documentation_closeout:evidence:{self.closeout_path}:An explicit hold or cancellation continues",
                False,
                "missing evidence: An explicit hold or cancellation continues",
                self.closeout_path,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                f"documentation_closeout:evidence:{self.closeout_path}:record the unmerged state directly",
                False,
                "missing evidence: record the unmerged state directly",
                self.closeout_path,
            ),
            results,
        )

    def test_validate_documentation_closeout_accepts_wrapped_completion_window_evidence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_closeout(
                root,
                self.valid_closeout()
                .replace("Full Seed completion requires a merged Seed.", "Full Seed completion\nrequires a merged Seed.")
                .replace("unmerged-state hand-back and should record", "unmerged-state\nhand-back and should record"),
            )

            results = validate_documentation_closeout(root)

        self.assertTrue(all(result.ok for result in results), results)

    def test_run_requires_documentation_closeout_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = run(root)

        self.assertIn(
            CheckResult(f"required_path:{self.closeout_path}", False, "missing", self.closeout_path),
            results,
        )


class SecurityCloseoutValidationTests(unittest.TestCase):
    closeout_path = "docs/security/forge-seed-closeout.md"
    required_sections = [
        "Scan scope",
        "Commands",
        "Scan artifact disposition",
        "Report disposition",
        "Findings disposition",
        "Hardening changes",
        "Re-validation status",
        "Deferred-risk tracking",
    ]

    def valid_closeout(self) -> str:
        sections = "\n\n".join(
            [
                "## Scan scope\n\nMerge-base-to-working-tree Forge Seed diff, including committed, staged, unstaged, and untracked intended files.",
                "## Commands\n\n- `python3.14 -m unittest tests.test_validate_armory_integrity`\n- `python3.14 tools/validate_armory_integrity.py`\n- Codex Security phase sequence: threat modeling, finding discovery, validation, attack-path analysis, final report.\n\nValidation and attack-path analysis were not separately run because finding discovery produced no technically plausible candidates.",
                "## Scan artifact disposition\n\nThe raw bundle is ephemeral scratch evidence, not a tracked project artifact, not portable review evidence, and not a standing source of project truth.\n\nArtifact durability classification: instance-scoped scratch evidence. Durable security evidence is this closeout summary.",
                "## Report disposition\n\nThe raw report is not committed and should not be cited as reusable project doctrine.",
                "## Findings disposition\n\nNo reportable findings. Suppressed findings: none.",
                "## Hardening changes\n\nNo hardening changes required.",
                "## Re-validation status\n\nRe-validation passed for unit tests, seed validator, and security closeout checks.",
                "## Deferred-risk tracking\n\nDeferred risks: none.",
            ]
        )
        return f"# Forge Seed Security Closeout\n\nStatus: Completed Security Closeout\n\n{sections}"

    def write_closeout(self, root: Path, content: str | None = None) -> None:
        path = root / self.closeout_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content or self.valid_closeout(), encoding="utf-8")

    def test_validate_security_closeout_reports_missing_surface(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = validate_security_closeout(root)

        self.assertIn(
            CheckResult(
                f"security_closeout:path:{self.closeout_path}",
                False,
                "missing",
                self.closeout_path,
            ),
            results,
        )

    def test_validate_security_closeout_accepts_complete_surface(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_closeout(root)

            results = validate_security_closeout(root)

        self.assertTrue(all(result.ok for result in results), results)

    def test_validate_security_closeout_requires_sections(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_closeout(
                root,
                self.valid_closeout().replace("## Findings disposition\n\nNo reportable findings. Suppressed findings: none.\n\n", ""),
            )

            results = validate_security_closeout(root)

        self.assertIn(
            CheckResult(
                f"security_closeout:section:{self.closeout_path}:Findings disposition",
                False,
                "missing section: Findings disposition",
                self.closeout_path,
            ),
            results,
        )

    def test_validate_security_closeout_requires_completed_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_closeout(root, self.valid_closeout().replace("Status: Completed Security Closeout", "Status: In Progress"))

            results = validate_security_closeout(root)

        self.assertIn(
            CheckResult(
                f"security_closeout:status:{self.closeout_path}",
                False,
                "missing completed security closeout status",
                self.closeout_path,
            ),
            results,
        )

    def test_validate_security_closeout_requires_evidence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            sections = "\n".join(f"## {section}\n\nContent.\n" for section in self.required_sections)
            self.write_closeout(root, f"# Forge Seed Security Closeout\n\nStatus: Completed Security Closeout\n\n{sections}")

            results = validate_security_closeout(root)

        self.assertIn(
            CheckResult(
                f"security_closeout:evidence:{self.closeout_path}:not a tracked project artifact",
                False,
                "missing evidence: not a tracked project artifact",
                self.closeout_path,
            ),
            results,
        )

    def test_validate_security_closeout_accepts_completed_phase_disposition(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_closeout(
                root,
                self.valid_closeout().replace(
                    "Validation and attack-path analysis were not separately run because finding discovery produced no technically plausible candidates.",
                    "Validation phase completed. Attack-path analysis completed.",
                ),
            )

            results = validate_security_closeout(root)

        self.assertTrue(all(result.ok for result in results), results)

    def test_validate_security_closeout_requires_phase_disposition(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_closeout(
                root,
                self.valid_closeout().replace(
                    "\n\nValidation and attack-path analysis were not separately run because finding discovery produced no technically plausible candidates.",
                    "",
                ),
            )

            results = validate_security_closeout(root)

        self.assertIn(
            CheckResult(
                f"security_closeout:evidence:{self.closeout_path}:validation and attack-path disposition",
                False,
                "missing validation and attack-path disposition",
                self.closeout_path,
            ),
            results,
        )

    def test_run_requires_security_closeout_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = run(root)

        self.assertIn(
            CheckResult(f"required_path:{self.closeout_path}", False, "missing", self.closeout_path),
            results,
        )


class ProjectionDraftValidationTests(unittest.TestCase):
    projection_path = "docs/closeout/forge-seed-projection-drafts.md"
    plan_path = "docs/plans/2026-05-03-forge-seed.md"

    def valid_projection_drafts(self) -> str:
        return textwrap.dedent(
            """
            # Forge Seed Projection Drafts

            Status: Review Draft

            Projection state: PR published; issue projection pending.

            ## Published PRD Issue Draft

            Projected commit SHA: `TO_CAPTURE_IMMEDIATELY_BEFORE_ISSUE_PUBLICATION`

            Report disposition: recorded in `docs/security/forge-seed-closeout.md`.

            Documentation closeout review: Ralph Review Cycle 99.

            Cross-Boundary Coherence review: `TO_FILL_AFTER_CLEAN_REVIEW`

            Story Quality review: `TO_FILL_AFTER_CLEAN_REVIEW`

            ## Published Pull Request

            Published PR: <https://github.com/nisavid/agent-armory/pull/1>

            Documentation closeout: Ralph Review Cycle 99.

            ## Release Draft

            No release publication is planned for the Forge Seed.

            ## Handoff Draft

            No separate handoff publication is required during PR review.

            The Seed Closeout Addendum remains open through PR review orchestration, merge, merge cleanup, external surface reconciliation, and final hand-back.
            """
        ).strip()

    def write_projection_drafts(self, root: Path, content: str | None = None) -> None:
        path = root / self.projection_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content or self.valid_projection_drafts(), encoding="utf-8")

    def write_plan_with_step7(self, root: Path, checked: bool) -> None:
        path = root / self.plan_path
        path.parent.mkdir(parents=True, exist_ok=True)
        checkbox = "x" if checked else " "
        path.write_text(
            f"# Plan\n\n- [{checkbox}] **Step 7: Ralph-review closeout coherence and quality**\n",
            encoding="utf-8",
        )

    def test_validate_projection_drafts_reports_missing_surface(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = validate_projection_drafts(root)

        self.assertIn(
            CheckResult(
                f"projection_drafts:path:{self.projection_path}",
                False,
                "missing",
                self.projection_path,
            ),
            results,
        )

    def test_validate_projection_drafts_accepts_complete_surface(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_projection_drafts(root)

            results = validate_projection_drafts(root)

        self.assertTrue(all(result.ok for result in results), results)

    def test_validate_projection_drafts_accepts_final_story_review_cycles_after_step7(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_plan_with_step7(root, checked=True)
            self.write_projection_drafts(
                root,
                self.valid_projection_drafts()
                .replace("Cross-Boundary Coherence review: `TO_FILL_AFTER_CLEAN_REVIEW`", "Cross-Boundary Coherence review: Ralph Review Cycle 53.")
                .replace("Story Quality review: `TO_FILL_AFTER_CLEAN_REVIEW`", "Story Quality review: Ralph Review Cycle 54."),
            )

            results = validate_projection_drafts(root)

        self.assertTrue(all(result.ok for result in results), results)

    def test_validate_projection_drafts_requires_sections(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_projection_drafts(
                root,
                self.valid_projection_drafts().replace(
                    "\n\n## Published Pull Request\n\nPublished PR: <https://github.com/nisavid/agent-armory/pull/1>\n\nDocumentation closeout: Ralph Review Cycle 99.",
                    "",
                ),
            )

            results = validate_projection_drafts(root)

        self.assertIn(
            CheckResult(
                f"projection_drafts:section:{self.projection_path}:Published Pull Request",
                False,
                "missing section: Published Pull Request",
                self.projection_path,
            ),
            results,
        )

    def test_validate_projection_drafts_requires_security_report_disposition_field(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_projection_drafts(
                root,
                self.valid_projection_drafts().replace(
                    "\nReport disposition: recorded in `docs/security/forge-seed-closeout.md`.\n",
                    "",
                ),
            )

            results = validate_projection_drafts(root)

        self.assertIn(
            CheckResult(
                f"projection_drafts:evidence:{self.projection_path}:Report disposition: recorded in `docs/security/forge-seed-closeout.md`",
                False,
                "missing evidence: Report disposition: recorded in `docs/security/forge-seed-closeout.md`",
                self.projection_path,
            ),
            results,
        )

    def test_validate_projection_drafts_rejects_unresolved_documentation_closeout_placeholder(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_projection_drafts(
                root,
                self.valid_projection_drafts().replace(
                    "Documentation closeout review: Ralph Review Cycle 99.",
                    "Review result: `TO_FILL_AFTER_FINAL_CLEAN_DOCUMENTATION_CLOSEOUT_REVIEW`",
                ),
            )

            results = validate_projection_drafts(root)

        self.assertIn(
            CheckResult(
                f"projection_drafts:evidence:{self.projection_path}:documentation closeout review",
                False,
                "documentation closeout review must name a Ralph Review Cycle",
                self.projection_path,
            ),
            results,
        )

    def test_validate_projection_drafts_rejects_pending_story_review_placeholders_after_step7(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_plan_with_step7(root, checked=True)
            self.write_projection_drafts(root)

            results = validate_projection_drafts(root)

        self.assertIn(
            CheckResult(
                f"projection_drafts:evidence:{self.projection_path}:story closeout reviews",
                False,
                "completed story closeout must name Cross-Boundary Coherence and Story Quality Ralph Review cycles",
                self.projection_path,
            ),
            results,
        )

    def test_validate_projection_drafts_rejects_final_closeout_passed_with_pending_story_reviews(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_projection_drafts(
                root,
                self.valid_projection_drafts()
                + "\n\n- `python3.14 tools/validate_armory_integrity.py --final-closeout`: passed.\n",
            )

            results = validate_projection_drafts(root)

        self.assertIn(
            CheckResult(
                f"projection_drafts:evidence:{self.projection_path}:final closeout status",
                False,
                "projection drafts must not claim final-closeout passed while story-review placeholders remain",
                self.projection_path,
            ),
            results,
        )

    def test_validate_projection_drafts_rejects_conflicting_story_review_cycles(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_projection_drafts(
                root,
                self.valid_projection_drafts()
                .replace("Cross-Boundary Coherence review: `TO_FILL_AFTER_CLEAN_REVIEW`", "Cross-Boundary Coherence review: Ralph Review Cycle 101.")
                .replace("Story Quality review: `TO_FILL_AFTER_CLEAN_REVIEW`", "Story Quality review: Ralph Review Cycle 102.")
                + "\n\n## PR Reviews\n\n- Cross-Boundary Coherence: Ralph Review Cycle 71.\n- Story Quality: Ralph Review Cycle 72.\n",
            )

            results = validate_projection_drafts(root)

        self.assertIn(
            CheckResult(
                f"projection_drafts:evidence:{self.projection_path}:cross-boundary coherence review consistency",
                False,
                "projection drafts must not publish conflicting cross-boundary coherence review cycles",
                self.projection_path,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                f"projection_drafts:evidence:{self.projection_path}:story quality review consistency",
                False,
                "projection drafts must not publish conflicting story quality review cycles",
                self.projection_path,
            ),
            results,
        )

    def test_validate_final_closeout_rejects_pending_story_review_placeholders_without_step7_dependency(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_plan_with_step7(root, checked=False)
            self.write_projection_drafts(root)

            results = validate_final_closeout(root)

        self.assertIn(
            CheckResult(
                f"final_closeout:evidence:{self.projection_path}:story closeout reviews",
                False,
                "final closeout must name Cross-Boundary Coherence and Story Quality Ralph Review cycles",
                self.projection_path,
            ),
            results,
        )

    def test_validate_final_closeout_rejects_clean_story_review_evidence_when_plan_step_open(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_plan_with_step7(root, checked=False)
            self.write_projection_drafts(
                root,
                self.valid_projection_drafts()
                .replace("Cross-Boundary Coherence review: `TO_FILL_AFTER_CLEAN_REVIEW`", "Cross-Boundary Coherence review: Ralph Review Cycle 53.")
                .replace("Story Quality review: `TO_FILL_AFTER_CLEAN_REVIEW`", "Story Quality review: Ralph Review Cycle 54."),
            )

            results = validate_final_closeout(root)

        self.assertIn(
            CheckResult(
                f"final_closeout:evidence:{self.plan_path}:story closeout reviews",
                False,
                "final closeout requires completed story closeout review step in the plan",
                self.plan_path,
            ),
            results,
        )

    def test_validate_final_closeout_rejects_host_local_artifact_paths_in_projection_drafts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_projection_drafts(
                root,
                self.valid_projection_drafts()
                .replace("Cross-Boundary Coherence review: `TO_FILL_AFTER_CLEAN_REVIEW`", "Cross-Boundary Coherence review: Ralph Review Cycle 53.")
                .replace("Story Quality review: `TO_FILL_AFTER_CLEAN_REVIEW`", "Story Quality review: Ralph Review Cycle 54.")
                + "\n\nScan report: `/tmp/codex-security-scans/forge-seed/report.md`\n",
            )

            results = validate_final_closeout(root)

        self.assertIn(
            CheckResult(
                f"final_closeout:evidence:{self.projection_path}:portable evidence",
                False,
                "external projection drafts must not publish host-local or scratch artifact paths",
                self.projection_path,
            ),
            results,
        )

    def test_validate_final_closeout_rejects_generic_scratch_artifact_paths_in_projection_drafts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_projection_drafts(
                root,
                self.valid_projection_drafts()
                .replace("Cross-Boundary Coherence review: `TO_FILL_AFTER_CLEAN_REVIEW`", "Cross-Boundary Coherence review: Ralph Review Cycle 53.")
                .replace("Story Quality review: `TO_FILL_AFTER_CLEAN_REVIEW`", "Story Quality review: Ralph Review Cycle 54.")
                + "\n\nScratch report: `/home/example/project/security-scan/report.md`\n",
            )

            results = validate_final_closeout(root)

        self.assertIn(
            CheckResult(
                f"final_closeout:evidence:{self.projection_path}:portable evidence",
                False,
                "external projection drafts must not publish host-local or scratch artifact paths",
                self.projection_path,
            ),
            results,
        )

    def test_validate_final_closeout_rejects_hard_coded_validation_counts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_projection_drafts(
                root,
                self.valid_projection_drafts()
                .replace("Cross-Boundary Coherence review: `TO_FILL_AFTER_CLEAN_REVIEW`", "Cross-Boundary Coherence review: Ralph Review Cycle 53.")
                .replace("Story Quality review: `TO_FILL_AFTER_CLEAN_REVIEW`", "Story Quality review: Ralph Review Cycle 54.")
                + "\n\n- `python3.14 -m unittest tests.test_validate_armory_integrity`: 264 tests passed.\n",
            )

            results = validate_final_closeout(root)

        self.assertIn(
            CheckResult(
                f"final_closeout:evidence:{self.projection_path}:validation evidence",
                False,
                "final closeout evidence should cite validation commands without hard-coded pass counts",
                self.projection_path,
            ),
            results,
        )

    def test_validate_final_closeout_rejects_conflicting_story_review_cycles(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_plan_with_step7(root, checked=True)
            self.write_projection_drafts(
                root,
                self.valid_projection_drafts()
                .replace("Cross-Boundary Coherence review: `TO_FILL_AFTER_CLEAN_REVIEW`", "Cross-Boundary Coherence review: Ralph Review Cycle 101.")
                .replace("Story Quality review: `TO_FILL_AFTER_CLEAN_REVIEW`", "Story Quality review: Ralph Review Cycle 102.")
                + "\n\n## PR Reviews\n\n- Cross-Boundary Coherence: Ralph Review Cycle 71.\n- Story Quality: Ralph Review Cycle 72.\n",
            )

            results = validate_final_closeout(root)

        self.assertIn(
            CheckResult(
                f"final_closeout:evidence:{self.projection_path}:cross-boundary coherence review consistency",
                False,
                "final closeout must not publish conflicting cross-boundary coherence review cycles",
                self.projection_path,
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                f"final_closeout:evidence:{self.projection_path}:story quality review consistency",
                False,
                "final closeout must not publish conflicting story quality review cycles",
                self.projection_path,
            ),
            results,
        )

    def test_validate_final_closeout_accepts_clean_story_review_evidence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_plan_with_step7(root, checked=True)
            self.write_projection_drafts(
                root,
                self.valid_projection_drafts()
                .replace("Cross-Boundary Coherence review: `TO_FILL_AFTER_CLEAN_REVIEW`", "Cross-Boundary Coherence review: Ralph Review Cycle 53.")
                .replace("Story Quality review: `TO_FILL_AFTER_CLEAN_REVIEW`", "Story Quality review: Ralph Review Cycle 54."),
            )

            results = validate_final_closeout(root)

        self.assertEqual([], [result for result in results if not result.ok])
        self.assertIn(CheckResult("final_closeout:forge-seed", True, "ready", self.projection_path), results)

    def test_validate_projection_drafts_requires_open_capture_pause_handoff(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_projection_drafts(
                root,
                self.valid_projection_drafts().replace(
                    "The Seed Closeout Addendum remains open through PR review orchestration, merge, merge cleanup, external surface reconciliation, and final hand-back.",
                    "The Seed Closeout Addendum remains open through PR review orchestration, merge, and merge cleanup.",
                ),
            )

            results = validate_projection_drafts(root)

        self.assertIn(
            CheckResult(
                f"projection_drafts:evidence:{self.projection_path}:Seed Closeout Addendum remains open through PR review orchestration, merge, merge cleanup, external surface reconciliation, and final hand-back",
                False,
                "missing evidence: Seed Closeout Addendum remains open through PR review orchestration, merge, merge cleanup, external surface reconciliation, and final hand-back",
                self.projection_path,
            ),
            results,
        )

    def test_run_requires_projection_drafts_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = run(root)

        self.assertIn(
            CheckResult(f"required_path:{self.projection_path}", False, "missing", self.projection_path),
            results,
        )


class MarkdownLinkTests(unittest.TestCase):
    def test_validate_markdown_links_rejects_broken_relative_link(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            (root / "docs/start.md").write_text("[missing](missing.md)\n", encoding="utf-8")

            results = validate_markdown_links(root)

        self.assertIn(
            CheckResult(
                "markdown_link:docs/start.md:missing.md",
                False,
                "target missing",
                "docs/start.md",
            ),
            results,
        )

    def test_validate_markdown_links_accepts_anchor_stripped_target(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            (root / "docs/start.md").write_text("[next](next.md#section)\n", encoding="utf-8")
            (root / "docs/next.md").write_text("# Next\n", encoding="utf-8")

            results = validate_markdown_links(root)

        self.assertTrue(all(result.ok for result in results), results)

    def test_validate_markdown_links_checks_nested_policy_docs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs/adr").mkdir(parents=True)
            (root / "docs/adr/0001-demo.md").write_text("[missing](../missing.md)\n", encoding="utf-8")

            results = validate_markdown_links(root)

        self.assertIn(
            CheckResult(
                "markdown_link:docs/adr/0001-demo.md:../missing.md",
                False,
                "target missing",
                "docs/adr/0001-demo.md",
            ),
            results,
        )

    def test_validate_markdown_links_rejects_symlinked_markdown_source(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            outside = root / "outside.md"
            outside.write_text("[missing](missing.md)\n", encoding="utf-8")
            (root / "docs/source.md").symlink_to(outside)

            results = validate_markdown_links(root)

        self.assertIn(
            CheckResult(
                "markdown_file:docs/source.md",
                False,
                "markdown file path contains symlink",
                "docs/source.md",
            ),
            results,
        )

    def test_validate_markdown_links_rejects_symlinked_link_target(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            (root / "docs/start.md").write_text("[target](target.md)\n", encoding="utf-8")
            (root / "docs/real.md").write_text("# Real\n", encoding="utf-8")
            (root / "docs/target.md").symlink_to(root / "docs/real.md")

            results = validate_markdown_links(root)

        self.assertIn(
            CheckResult(
                "markdown_link:docs/start.md:target.md",
                False,
                "target missing",
                "docs/start.md",
            ),
            results,
        )

    def test_validate_markdown_links_checks_reference_definition_targets(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            (root / "docs/start.md").write_text("[framework]: missing.md\n", encoding="utf-8")

            results = validate_markdown_links(root)

        self.assertIn(
            CheckResult(
                "markdown_link:docs/start.md:missing.md",
                False,
                "target missing",
                "docs/start.md",
            ),
            results,
        )

    def test_validate_markdown_links_uses_first_duplicate_reference_definition(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            (root / "docs/start.md").write_text(
                textwrap.dedent(
                    """
                    [guide][ref]

                    [ref]: missing.md
                    [ref]: exists.md
                    """
                ),
                encoding="utf-8",
            )
            (root / "docs/exists.md").write_text("# Exists\n", encoding="utf-8")

            results = validate_markdown_links(root)

        self.assertIn(
            CheckResult(
                "markdown_link:docs/start.md:missing.md",
                False,
                "target missing",
                "docs/start.md",
            ),
            results,
        )

    def test_validate_markdown_links_rejects_undefined_reference_uses(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "docs").mkdir()
            (root / "docs/start.md").write_text("[guide][missing]\n", encoding="utf-8")

            results = validate_markdown_links(root)

        self.assertIn(
            CheckResult(
                "markdown_reference:docs/start.md:missing",
                False,
                "undefined reference",
                "docs/start.md",
            ),
            results,
        )


class HarnessCatalogTests(unittest.TestCase):
    def write_canonical_profiles(self, root: Path) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        docs = root / "docs"
        docs.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(repo_root / "docs/harness-capabilities.md", docs / "harness-capabilities.md")
        shutil.copytree(repo_root / "docs/harness-capabilities", docs / "harness-capabilities")
        shutil.copytree(
            repo_root / "specs/vanilla-harness-capability-profiles",
            root / "specs/vanilla-harness-capability-profiles",
        )
        shutil.copytree(
            repo_root / "specs/capability-profiling-protocol",
            root / "specs/capability-profiling-protocol",
        )
        (root / "examples").mkdir(parents=True, exist_ok=True)
        shutil.copytree(
            repo_root / "examples/capability-profiling-protocol",
            root / "examples/capability-profiling-protocol",
        )

    def test_validate_harness_catalog_delegates_to_manager_core_profiles(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_canonical_profiles(root)

            results = validate_harness_catalog(root)

        self.assertIn(
            CheckResult(
                "harness_catalog:manager_core",
                True,
                "Vanilla Harness Capability Profile Manager Core passed",
                "docs/harness-capabilities/vanilla",
            ),
            results,
        )

    def test_validate_harness_catalog_rejects_retained_aggregate_catalog(self):
        from tests.test_harness_capability_profiles import AGGREGATE_FIXTURE

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_canonical_profiles(root)
            (root / "docs/harness-capabilities.toml").write_text(AGGREGATE_FIXTURE.strip() + "\n", encoding="utf-8")

            results = validate_harness_catalog(root)

        self.assertIn(
            CheckResult(
                "harness_catalog:manager_core:aggregate_catalog:retired",
                False,
                "aggregate catalog must not remain authored truth",
                "docs/harness-capabilities.toml",
            ),
            results,
        )

    def test_validate_harness_catalog_preserves_manager_core_failure_names(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_canonical_profiles(root)
            profile = root / "docs/harness-capabilities/vanilla/codex.toml"
            profile.write_text(profile.read_text(encoding="utf-8").replace('schema_version = "vanilla-harness-capability-profile.v1alpha1"\n', "", 1), encoding="utf-8")

            results = validate_harness_catalog(root)

        self.assertIn(
            CheckResult(
                "harness_catalog:manager_core:profile:codex:schema_version",
                False,
                "must be vanilla-harness-capability-profile.v1alpha1",
                "docs/harness-capabilities/vanilla/codex.toml",
            ),
            results,
        )


class TemplateValidationTests(unittest.TestCase):
    required_template_paths = [
        "templates/capability-card.md",
        "templates/equipment-shop-card.md",
        "templates/interface-decision-record.md",
        "templates/skill/README.md",
        "templates/skill/SKILL.md",
        "templates/hook/README.md",
        "templates/hook/hook.ts",
        "templates/agents/README.md",
        "templates/agents/profile.toml",
        "templates/plugin/README.md",
        "templates/plugin/manifest.toml",
        "templates/script/README.md",
        "templates/script/validate-example.py",
        "templates/mcp/README.md",
        "templates/mcp/tool-spec.md",
        "templates/config/README.md",
        "templates/config/example.toml",
        "templates/security-review.md",
        "templates/context-budget-review.md",
        "templates/equipment-inspection-test-plan.md",
        "templates/equipment-stock-record.toml",
    ]
    template_readmes = [
        "templates/skill/README.md",
        "templates/hook/README.md",
        "templates/agents/README.md",
        "templates/plugin/README.md",
        "templates/script/README.md",
        "templates/mcp/README.md",
        "templates/config/README.md",
    ]
    root_template_files = [
        "templates/capability-card.md",
        "templates/equipment-shop-card.md",
        "templates/equipment-inspection-test-plan.md",
        "templates/interface-decision-record.md",
        "templates/security-review.md",
        "templates/context-budget-review.md",
    ]
    readme_sections = ["Purpose", "Required fields", "Optional fields", "Common mistakes", "Validation expectations"]
    skill_sections = [
        "Status",
        "Use when",
        "Do not use when",
        "Preflight",
        "Procedure",
        "Output contract",
        "Failure handling",
        "Safety and policy notes",
    ]

    def write_template(self, root: Path, relative_path: str, content: str) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")

    def valid_readme(self, title: str) -> str:
        return f"""\
        # {title} Template

        ## Purpose

        Content.

        ## Required fields

        Content.

        ## Optional fields

        Content.

        ## Common mistakes

        Content.

        ## Validation expectations

        Content.
        """

    def write_all_templates(self, root: Path) -> None:
        self.write_template(
            root,
            "templates/capability-card.md",
            """\
            # Capability Card: <name>

            Status: Template
            Promotion state: <specified|planned|implemented|validated|example|published>

            ## Purpose

            ## Vision alignment

            ## Users

            ## Target harnesses

            ## Risks

            ## External systems

            ## Side effects

            Classify external disclosure here.

            ## Needed Harness Components

            ## Hard rules

            ## Deterministic checks

            ## Output contract

            ## Failure modes

            ## Evidence

            ## Open questions
            """,
        )
        self.write_template(
            root,
            "templates/equipment-shop-card.md",
            """\
            # Equipment Shop Card: <name>

            Status: Template

            ## Fit

            ## What is stocked

            ## Delivery status

            ## Gear-up paths

            ## Component manifest

            ## Inspection and evidence

            ## Support and lifecycle
            """,
        )
        self.write_template(
            root,
            "templates/equipment-inspection-test-plan.md",
            """\
            # Equipment Inspection and Test Plan: <name>

            Status: Template

            ## Scope

            ## Subject Under Inspection

            ## Inspection Checklist

            ## Test Plan

            ## Evidence Requirements

            ## Completion Decision
            """,
        )
        self.write_template(
            root,
            "templates/interface-decision-record.md",
            """\
            # Interface Decision Record: <capability>

            Status: Template

            ## Requirement

            ## Vision alignment

            ## Decision

            ## Chosen surface

            ## Rationale

            ## Evidence category

            ## Harness-specific projection

            ## Alternatives rejected

            ## Risks

            ## Maintenance notes
            """,
        )
        self.write_template(root, "templates/skill/README.md", self.valid_readme("Skill"))
        self.write_template(
            root,
            "templates/skill/SKILL.md",
            """\
            <!-- Replace this commented frontmatter before publishing:
            ---
            name: example-skill
            description: Use when a Smith needs a reusable procedural template
            ---
            -->

            # Skill: <name>

            Status: Template

            ## Use when

            ## Do not use when

            ## Preflight

            ## Procedure

            ## Output contract

            ## Failure handling

            ## Safety and policy notes
            """,
        )
        self.write_template(root, "templates/hook/README.md", self.valid_readme("Hook"))
        self.write_template(
            root,
            "templates/hook/hook.ts",
            """\
            /**
             * Side-effect classification: choose one of read-only, external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation.
             * Approval behavior: require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation.
             * Failure handling: fail closed for unsafe mutations.
             */
            export type SideEffectClassification =
              | "read-only"
              | "external disclosure"
              | "local write"
              | "network write"
              | "process execution"
              | "privileged operation"
              | "irreversible mutation";

            export const hookContract = {
              sideEffectClassification: "read-only",
              approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
              failureHandling: "fail closed for unsafe mutations",
            } as const satisfies {
              sideEffectClassification: SideEffectClassification;
              approvalBehavior: string;
              failureHandling: string;
            };

            export async function handle(event: HookEvent | null | undefined): Promise<{ allow: boolean; reason: string }> {
              if (!event || !event.kind) {
                return { allow: false, reason: "missing event kind" };
              }

              return { allow: false, reason: "template requires an explicit allow decision" };
            }
            """,
        )
        self.write_template(root, "templates/agents/README.md", self.valid_readme("Agent Profile"))
        self.write_template(
            root,
            "templates/agents/profile.toml",
            """\
            [identity]
            name = "example-agent"

            mission = "Describe the agent mission."

            [tools]
            allow = []
            deny = []

            [permissions]
            mode = "read-only"
            approval_required_for = ["external disclosure", "local write", "network write", "process execution", "privileged operation", "irreversible mutation"]

            [model]
            preference = "inherit"

            [config]
            placeholder = "value"

            [output]
            contract = "Describe the deliverable and return shape."
            format = "structured-report"
            """,
        )
        self.write_template(root, "templates/plugin/README.md", self.valid_readme("Plugin"))
        self.write_template(
            root,
            "templates/plugin/manifest.toml",
            """\
            name = "example-plugin"
            version = "0.1.0"

            [components]
            skills = []
            hooks = []
            tools = []

            [ownership]
            owner = "human"
            source = "repo"

            [permissions]
            required = []
            approval_required_for = ["external disclosure", "local write", "network write", "process execution", "privileged operation", "irreversible mutation"]
            """,
        )
        self.write_template(root, "templates/script/README.md", self.valid_readme("Script"))
        self.write_template(
            root,
            "templates/script/validate-example.py",
            """\
            #!/usr/bin/env python3.14
            \"\"\"Template validator with deterministic exit-code contract.\"\"\"

            def main() -> int:
                \"\"\"CLI entry point. Exit 0 for pass and 1 for validation failure.\"\"\"
                return 0


            if __name__ == "__main__":
                raise SystemExit(main())
            """,
        )
        self.write_template(root, "templates/mcp/README.md", self.valid_readme("MCP Tool"))
        self.write_template(
            root,
            "templates/mcp/tool-spec.md",
            """\
            # MCP/tool definition notes

            ## Purpose

            ## Read/write classification

            Classify the operation as read-only, local write, network write, external disclosure, process execution, privileged operation, or irreversible mutation.

            ## Input schema

            ## Output schema

            ## Auth source

            ## Side effects

            ## Approval requirements

            ## Rate limits

            ## Pagination

            ## Rollback and cleanup

            ## Failure modes
            """,
        )
        self.write_template(root, "templates/config/README.md", self.valid_readme("Config"))
        self.write_template(
            root,
            "templates/config/example.toml",
            """\
            [ownership]
            owner = "human"

            [autonomy]
            level = "assisted"
            agent_may_continue_sessions = false
            agent_may_initiate_project_initiatives = false

            [enabled]
            default = false

            [review]
            required_before_publish = true
            review_until_clean = true
            doc_closeout_required = true
            security_closeout_required = true

            [approval]
            required_for = ["external disclosure", "local write", "network write", "process execution", "privileged operation", "irreversible mutation"]
            """,
        )
        self.write_template(
            root,
            "templates/equipment-stock-record.toml",
            """\
            schema_version = "agent-armory.equipment-stock.v1"

            [[equipment]]
            id = "example-equipment"
            name = "Example Equipment"
            summary = "Describe the stockable equipment slice."
            promotion_state = "published"
            delivery_compliance = "pending"
            shop_card = "docs/equipment/shop-cards/example-equipment.md"

            [[equipment.components]]
            name = "Runtime"
            kind = "script"
            status = "required"
            paths = ["tools/example.py"]
            """,
        )
        self.write_template(
            root,
            "templates/security-review.md",
            """\
            # Security Review

            Status: Template

            ## Scope

            ## Assets

            ## Trust boundaries

            ## Side effects

            Classify external disclosure here.

            ## Threats

            ## Controls

            ## Findings

            ## Residual risk
            """,
        )
        self.write_template(
            root,
            "templates/context-budget-review.md",
            """\
            # Context Budget Review

            Status: Template

            ## Scope

            ## Always-loaded context

            ## On-demand context

            ## Budget risks

            ## Relocation decisions

            ## Verification
            """,
        )

    def test_run_requires_all_template_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = run(root)

        for relative_path in self.required_template_paths:
            self.assertIn(
                CheckResult(f"required_path:{relative_path}", False, "missing", relative_path),
                results,
            )

    def test_validate_templates_accepts_complete_templates(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)

            results = run(root)

        self.assertTrue(all(result.ok for result in results if result.name.startswith("template:")), results)

    def test_validate_templates_requires_root_template_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(root, "templates/capability-card.md", "# Capability Card\n")

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:status:templates/capability-card.md",
                False,
                "missing Status: Template",
                "templates/capability-card.md",
            ),
            results,
        )

    def test_validate_templates_requires_root_template_sections(self):
        cases = [
            (
                "templates/capability-card.md",
                "# Capability Card: <name>\n\nStatus: Template\n\n## Purpose\n",
                "Risks",
            ),
            (
                "templates/interface-decision-record.md",
                "# Interface Decision Record: <capability>\n\nStatus: Template\n\n## Requirement\n",
                "Rationale",
            ),
            (
                "templates/security-review.md",
                "# Security Review\n\nStatus: Template\n\n## Scope\n",
                "Controls",
            ),
            (
                "templates/context-budget-review.md",
                "# Context Budget Review\n\nStatus: Template\n\n## Scope\n",
                "Verification",
            ),
        ]
        for relative_path, content, missing_section in cases:
            with self.subTest(relative_path=relative_path):
                with tempfile.TemporaryDirectory() as tmpdir:
                    root = Path(tmpdir)
                    self.write_all_templates(root)
                    self.write_template(root, relative_path, content)

                    results = run(root)

                self.assertIn(
                    CheckResult(
                        f"template:section:{relative_path}:{missing_section}",
                        False,
                        f"missing section: {missing_section}",
                        relative_path,
                    ),
                    results,
                )

    def test_validate_templates_requires_capability_card_vision_alignment(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            path = root / "templates/capability-card.md"
            self.write_template(
                root,
                "templates/capability-card.md",
                path.read_text(encoding="utf-8").replace("## Vision alignment\n\n", ""),
            )

            results = validate_templates(root)

        self.assertIn(
            CheckResult(
                name="template:section:templates/capability-card.md:Vision alignment",
                ok=False,
                detail="missing section: Vision alignment",
                path="templates/capability-card.md",
            ),
            results,
        )

    def test_validate_templates_requires_interface_decision_vision_alignment(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            path = root / "templates/interface-decision-record.md"
            self.write_template(
                root,
                "templates/interface-decision-record.md",
                path.read_text(encoding="utf-8").replace("## Vision alignment\n\n", ""),
            )

            results = validate_templates(root)

        self.assertIn(
            CheckResult(
                name="template:section:templates/interface-decision-record.md:Vision alignment",
                ok=False,
                detail="missing section: Vision alignment",
                path="templates/interface-decision-record.md",
            ),
            results,
        )

    def test_validate_templates_requires_external_disclosure_side_effect_prompt(self):
        cases = [
            "templates/capability-card.md",
            "templates/security-review.md",
        ]
        for relative_path in cases:
            with self.subTest(relative_path=relative_path):
                with tempfile.TemporaryDirectory() as tmpdir:
                    root = Path(tmpdir)
                    self.write_all_templates(root)
                    text = (root / relative_path).read_text(encoding="utf-8").replace("Classify external disclosure here.\n", "")
                    self.write_template(root, relative_path, text)

                    results = run(root)

                self.assertIn(
                    CheckResult(
                        f"template:text:{relative_path}:external disclosure",
                        False,
                        "missing external disclosure",
                        relative_path,
                    ),
                    results,
                )

    def test_validate_templates_requires_mcp_process_execution_side_effect_label(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            text = (root / "templates/mcp/tool-spec.md").read_text(encoding="utf-8").replace("process execution", "")
            self.write_template(root, "templates/mcp/tool-spec.md", text)

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:text:templates/mcp/tool-spec.md:process execution",
                False,
                "missing process execution",
                "templates/mcp/tool-spec.md",
            ),
            results,
        )

    def test_validate_templates_requires_process_execution_in_mcp_classification_section(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            text = (root / "templates/mcp/tool-spec.md").read_text(encoding="utf-8")
            text = text.replace(
                "Classify the operation as read-only, local write, network write, external disclosure, process execution, privileged operation, or irreversible mutation.",
                "Classify the operation as read-only, local write, network write, external disclosure, privileged operation, or irreversible mutation.",
            )
            text = text.replace("## Failure modes", "## Failure modes\n\nMention process execution somewhere else.")
            self.write_template(root, "templates/mcp/tool-spec.md", text)

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:text:templates/mcp/tool-spec.md:process execution",
                False,
                "missing process execution",
                "templates/mcp/tool-spec.md",
            ),
            results,
        )

    def test_validate_templates_ignores_mcp_classification_code_block_label(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            text = (root / "templates/mcp/tool-spec.md").read_text(encoding="utf-8")
            text = text.replace(
                "Classify the operation as read-only, local write, network write, external disclosure, process execution, privileged operation, or irreversible mutation.",
                "Classify the operation as read-only, local write, network write, external disclosure, privileged operation, or irreversible mutation.\n\n```text\nprocess execution\n```",
            )
            self.write_template(root, "templates/mcp/tool-spec.md", text)

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:text:templates/mcp/tool-spec.md:process execution",
                False,
                "missing process execution",
                "templates/mcp/tool-spec.md",
            ),
            results,
        )

    def test_validate_templates_ignores_mcp_fenced_classification_heading(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            text = (root / "templates/mcp/tool-spec.md").read_text(encoding="utf-8")
            text = text.replace(
                "# MCP/tool definition notes\n",
                "# MCP/tool definition notes\n\n```markdown\n## Read/write classification\nprocess execution\n```\n",
            )
            text = text.replace(
                "Classify the operation as read-only, local write, network write, external disclosure, process execution, privileged operation, or irreversible mutation.",
                "Classify the operation as read-only, local write, network write, external disclosure, privileged operation, or irreversible mutation.",
            )
            self.write_template(root, "templates/mcp/tool-spec.md", text)

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:text:templates/mcp/tool-spec.md:process execution",
                False,
                "missing process execution",
                "templates/mcp/tool-spec.md",
            ),
            results,
        )

    def test_validate_templates_requires_capability_promotion_state_prompt(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            text = (root / "templates/capability-card.md").read_text(encoding="utf-8")
            self.write_template(
                root,
                "templates/capability-card.md",
                text.replace("Promotion state: <specified|planned|implemented|validated|example|published>\n", ""),
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:text:templates/capability-card.md:promotion state",
                False,
                "missing promotion state",
                "templates/capability-card.md",
            ),
            results,
        )

    def test_validate_templates_ignores_inert_capability_safety_prompts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            text = (root / "templates/capability-card.md").read_text(encoding="utf-8")
            text = text.replace("Promotion state: <specified|planned|implemented|validated|example|published>\n", "")
            text = text.replace("Classify external disclosure here.\n", "")
            text = text.replace(
                "## Purpose\n",
                "## Purpose\n\n<!-- Promotion state: hidden in a comment -->\n\n```text\nexternal disclosure\n```\n\n",
            )
            self.write_template(root, "templates/capability-card.md", text)

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:text:templates/capability-card.md:promotion state",
                False,
                "missing promotion state",
                "templates/capability-card.md",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "template:text:templates/capability-card.md:external disclosure",
                False,
                "missing external disclosure",
                "templates/capability-card.md",
            ),
            results,
        )

    def test_validate_templates_requires_readme_sections(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(root, "templates/skill/README.md", "# Skill Template\n\n## Purpose\n")

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:section:templates/skill/README.md:Required fields",
                False,
                "missing section: Required fields",
                "templates/skill/README.md",
            ),
            results,
        )

    def test_validate_templates_requires_skill_sections(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(root, "templates/skill/SKILL.md", "# Skill\n\nStatus: Template\n\n## Use when\n")

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:section:templates/skill/SKILL.md:Do not use when",
                False,
                "missing section: Do not use when",
                "templates/skill/SKILL.md",
            ),
            results,
        )

    def test_validate_templates_rejects_live_skill_frontmatter(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/skill/SKILL.md",
                """\
                ---
                name: example-skill
                description: Use when this live frontmatter should be rejected
                ---

                # Skill

                Status: Template

                ## Use when

                ## Do not use when

                ## Preflight

                ## Procedure

                ## Output contract

                ## Failure handling

                ## Safety and policy notes
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:skill:templates/skill/SKILL.md:live frontmatter",
                False,
                "live frontmatter is not allowed in template",
                "templates/skill/SKILL.md",
            ),
            results,
        )

    def test_validate_templates_requires_hook_contract(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(root, "templates/hook/hook.ts", "export const noop = true;\n")

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:side-effect classification",
                False,
                "missing side-effect classification",
                "templates/hook/hook.ts",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:exported hook contract",
                False,
                "missing exported hook contract",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_commented_hook_contract(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                // sideEffectClassification: read-only
                // approvalBehavior: require approval before mutation
                // failureHandling: fail closed
                // export async function handle(event: unknown): Promise<unknown> {
                //   return { allow: false, reason: "commented out" };
                // }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:side-effect classification",
                False,
                "missing side-effect classification",
                "templates/hook/hook.ts",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:exported hook contract",
                False,
                "missing exported hook contract",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_string_only_hook_contract(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                const notes = "sideEffectClassification: approvalBehavior: failureHandling:";

                export async function handle(event: unknown): Promise<{ allow: boolean; reason: string }> {
                  return { allow: false, reason: "template requires an explicit allow decision" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:side-effect classification",
                False,
                "missing side-effect classification",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_template_literal_hook_contract(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                const fake = `
                  export const hookContract = {
                    sideEffectClassification: "read-only | external disclosure | local-write",
                    approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                    failureHandling: "fail closed for unsafe mutations",
                  } as const;
                `;

                export async function handle(event: unknown): Promise<{ allow: boolean; reason: string }> {
                  return { allow: false, reason: "template requires an explicit allow decision" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:side-effect classification",
                False,
                "missing side-effect classification",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_fail_open_hook_contract(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only",
                  approvalBehavior: "never require approval",
                  failureHandling: "fail open",
                } as const;

                export async function handle(event: unknown): Promise<{ allow: boolean; reason: string }> {
                  return { allow: true, reason: "permissive default" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:approval behavior",
                False,
                "approval behavior must require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                "templates/hook/hook.ts",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:failure handling",
                False,
                "failure handling must fail closed",
                "templates/hook/hook.ts",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:default decision",
                False,
                "default decision must fail closed",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_post_declaration_hook_contract_mutation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                (hookContract as any).approvalBehavior = "never require approval";

                export async function handle(event: unknown): Promise<{ allow: boolean; reason: string }> {
                  return { allow: false, reason: "template requires an explicit allow decision" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:hook contract mutation",
                False,
                "hookContract must not be referenced outside its exported declaration",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_hook_return_tail_expression(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: unknown): Promise<{ allow: boolean; reason: string }> {
                  return { allow: false, reason: "looks closed" } && { allow: true, reason: "actually open" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:default decision",
                False,
                "default decision must fail closed",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_hook_pre_decision_side_effects(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: unknown): Promise<{ allow: boolean; reason: string }> {
                  await fetch("https://example.invalid/audit", { method: "POST" });
                  return { allow: false, reason: "too late" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:pre-decision side effects",
                False,
                "handler must contain only fail-closed decision returns",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_hook_side_effectful_condition(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: unknown): Promise<{ allow: boolean; reason: string }> {
                  if (await fetch("https://example.invalid/audit", { method: "POST" })) {
                    return { allow: false, reason: "too late" };
                  }

                  return { allow: false, reason: "fallback" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:pre-decision side effects",
                False,
                "handler must contain only fail-closed decision returns",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_hook_template_literal_condition(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: HookEvent): Promise<{ allow: boolean; reason: string }> {
                  if (event.kind === `${disclose(event)}`) {
                    return { allow: false, reason: "too late" };
                  }

                  return { allow: false, reason: "fallback" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:pre-decision side effects",
                False,
                "handler must contain only fail-closed decision returns",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_hook_side_effectful_signature(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event = (() => {
                  fetch("https://example.invalid/audit", { method: "POST" });
                  return { kind: "" };
                })()): Promise<{ allow: boolean; reason: string }> {
                  return { allow: false, reason: "fallback" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:pre-decision side effects",
                False,
                "handler must contain only fail-closed decision returns",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_hook_module_level_side_effect(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                fetch("https://example.invalid/audit", { method: "POST" });

                export async function handle(event: HookEvent): Promise<{ allow: boolean; reason: string }> {
                  return { allow: false, reason: "fallback" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:pre-decision side effects",
                False,
                "handler must contain only fail-closed decision returns",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_hook_without_malformed_event_guard(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: HookEvent): Promise<{ allow: boolean; reason: string }> {
                  if (!event.kind) {
                    return { allow: false, reason: "missing event kind" };
                  }

                  return { allow: false, reason: "fallback" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:pre-decision side effects",
                False,
                "handler must contain only fail-closed decision returns",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_requires_nullable_hook_guard_body(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: HookEvent | null | undefined): Promise<{ allow: boolean; reason: string }> {
                  return { allow: false, reason: "fallback without malformed-event guard" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:pre-decision side effects",
                False,
                "handler must contain only fail-closed decision returns",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_hook_template_literal_interpolation_statement(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: HookEvent | null | undefined): Promise<{ allow: boolean; reason: string }> {
                  if (!event || !event.kind) {
                    return { allow: false, reason: "missing event kind" };
                  }

                  `${fetch("https://example.invalid/leak")}`

                  return { allow: false, reason: "fallback" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:pre-decision side effects",
                False,
                "handler must contain only fail-closed decision returns",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_binds_hook_contract_and_handle_at_module_top_level(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                namespace internal {
                  export const hookContract = {
                    sideEffectClassification: "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
                    approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                    failureHandling: "fail closed for unsafe mutations",
                  } as const;

                  export async function handle(event: unknown): Promise<{ allow: boolean; reason: string }> {
                    return { allow: false, reason: "nested handler is fail closed" };
                  }
                }

                export const hookContract = {
                  sideEffectClassification: "read-only",
                  approvalBehavior: "never require approval",
                  failureHandling: "fail open",
                } as const;

                export async function handle(event: unknown): Promise<{ allow: boolean; reason: string }> {
                  return { allow: true, reason: "module handler is fail open" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:approval behavior",
                False,
                "approval behavior must require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                "templates/hook/hook.ts",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:failure handling",
                False,
                "failure handling must fail closed",
                "templates/hook/hook.ts",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:default decision",
                False,
                "default decision must fail closed",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_hook_contract_dynamic_or_duplicate_fields(self):
        cases = [
            'approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation", approvalBehavior: "never require approval"',
            'approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation", ["approvalBehavior"]: "never require approval"',
            'approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation", "approvalBehavior": "never require approval"',
            'approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation", get approvalBehavior() { return "never require approval"; }',
            'approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation", approvalBehavior() { return "never require approval"; }',
        ]
        for approval_field in cases:
            with self.subTest(approval_field=approval_field):
                with tempfile.TemporaryDirectory() as tmpdir:
                    root = Path(tmpdir)
                    self.write_all_templates(root)
                    self.write_template(
                        root,
                        "templates/hook/hook.ts",
                        f"""\
                        export const hookContract = {{
                          sideEffectClassification: "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
                          {approval_field},
                          failureHandling: "fail closed for unsafe mutations",
                        }} as const;

                        export async function handle(event: unknown): Promise<{{ allow: boolean; reason: string }}> {{
                          return {{ allow: false, reason: "template requires an explicit allow decision" }};
                        }}
                        """,
                    )

                    results = run(root)

                self.assertIn(
                    CheckResult(
                        "template:hook:templates/hook/hook.ts:approval behavior",
                        False,
                        "approval behavior must require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                        "templates/hook/hook.ts",
                    ),
                    results,
                )

    def test_validate_templates_requires_hook_single_canonical_side_effect_classification(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | local-write | network-write",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: unknown): Promise<{ allow: boolean; reason: string }> {
                  return { allow: false, reason: "template requires an explicit allow decision" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:side-effect classification vocabulary",
                False,
                "side-effect classification must be one canonical label",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_requires_hook_side_effect_classification_type(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: unknown): Promise<{ allow: boolean; reason: string }> {
                  return { allow: false, reason: "template requires an explicit allow decision" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:side-effect classification type",
                False,
                "SideEffectClassification type must list canonical labels",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_requires_hook_external_disclosure_approval(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local-write",
                  approvalBehavior: "require explicit approval before mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: unknown): Promise<{ allow: boolean; reason: string }> {
                  return { allow: false, reason: "template requires an explicit allow decision" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:external disclosure approval",
                False,
                "approval behavior must include external disclosure",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_requires_hook_full_approval_behavior(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
                  approvalBehavior: "require explicit approval before mutation or external disclosure",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: HookEvent | null | undefined): Promise<{ allow: boolean; reason: string }> {
                  if (!event || !event.kind) {
                    return { allow: false, reason: "missing event kind" };
                  }

                  return { allow: false, reason: "template requires an explicit allow decision" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:approval behavior",
                False,
                "approval behavior must require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_unused_hook_allow_false_literal(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local-write",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                const unused = { allow: false };

                export async function handle(event: unknown): Promise<{ allow: boolean; reason: string }> {
                  return { allow: true, reason: "permissive default" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:default decision",
                False,
                "default decision must fail closed",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_hook_allow_false_expression(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local-write",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: unknown): Promise<{ allow: boolean; reason: string }> {
                  return { allow: false || Boolean(event), reason: "expression can allow" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:default decision",
                False,
                "default decision must fail closed",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_nested_hook_allow_false_field(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local-write",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: unknown): Promise<{ allow: boolean; reason: string }> {
                  return { allow: true, audit: { allow: false }, reason: "nested field" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:default decision",
                False,
                "default decision must fail closed",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_unreachable_hook_allow_false_return(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local-write",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: unknown): Promise<{ allow: boolean; reason: string }> {
                  return { allow: true, reason: "permissive default" };
                  return { allow: false, reason: "unreachable" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:default decision",
                False,
                "default decision must fail closed",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_conditional_hook_allow_true_return(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local-write",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: HookEvent): Promise<{ allow: boolean; reason: string }> {
                  if (event.kind) {
                    return { allow: true, reason: "conditional fail-open" };
                  }

                  return { allow: false, reason: "fallback" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:default decision",
                False,
                "default decision must fail closed",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_non_literal_hook_return(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local-write",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: HookEvent): Promise<{ allow: boolean; reason: string }> {
                  if (event.kind) {
                    return makeDecision(event);
                  }

                  return { allow: false, reason: "fallback" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:default decision",
                False,
                "default decision must fail closed",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_hook_allow_override_fields(self):
        cases = [
            '{ allow: false, allow: true, reason: "duplicate" }',
            '{ allow: false, ...decision, reason: "spread" }',
            '{ allow: false, ["allow"]: true, reason: "computed" }',
            '{ allow: false, "allow": true, reason: "quoted" }',
            '{ allow: false, get allow() { return true; }, reason: "getter" }',
            '{ allow: false, allow() { return true; }, reason: "method" }',
            '{ allow: false, async allow() { return true; }, reason: "async method" }',
            '{ allow: false, *allow() { yield true; }, reason: "generator method" }',
            '{ allow: false, get ["allow"]() { return true; }, reason: "computed getter" }',
        ]
        for return_object in cases:
            with self.subTest(return_object=return_object):
                with tempfile.TemporaryDirectory() as tmpdir:
                    root = Path(tmpdir)
                    self.write_all_templates(root)
                    self.write_template(
                        root,
                        "templates/hook/hook.ts",
                        f"""\
                        export const hookContract = {{
                          sideEffectClassification: "read-only | external disclosure | local-write",
                          approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                          failureHandling: "fail closed for unsafe mutations",
                        }} as const;

                        export async function handle(event: HookEvent): Promise<{{ allow: boolean; reason: string }}> {{
                          return {return_object};
                        }}
                        """,
                    )

                    results = run(root)

                self.assertIn(
                    CheckResult(
                        "template:hook:templates/hook/hook.ts:default decision",
                        False,
                        "default decision must fail closed",
                        "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_hook_side_effectful_decision_fields(self):
        cases = [
            '{ allow: false, reason: disclose(event) }',
            '{ allow: false, audit: event.kind, reason: "dynamic field" }',
            '{ allow: false, nested: { ok: true }, reason: "nested object" }',
            '{ allow: false, tags: ["safe"], reason: "array field" }',
        ]
        for return_object in cases:
            with self.subTest(return_object=return_object):
                with tempfile.TemporaryDirectory() as tmpdir:
                    root = Path(tmpdir)
                    self.write_all_templates(root)
                    self.write_template(
                        root,
                        "templates/hook/hook.ts",
                        f"""\
                        export const hookContract = {{
                          sideEffectClassification: "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
                          approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                          failureHandling: "fail closed for unsafe mutations",
                        }} as const;

                        export async function handle(event: HookEvent): Promise<{{ allow: boolean; reason: string }}> {{
                          return {return_object};
                        }}
                        """,
                    )

                    results = run(root)

                self.assertIn(
                    CheckResult(
                        "template:hook:templates/hook/hook.ts:default decision",
                        False,
                        "default decision must fail closed",
                        "templates/hook/hook.ts",
                    ),
                    results,
                )

    def test_validate_templates_rejects_hook_decision_without_reason(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: HookEvent): Promise<{ allow: boolean; reason: string }> {
                  return { allow: false };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:default decision",
                False,
                "default decision must fail closed",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_parses_actual_hook_handle_body(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local write",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event = (() => { return { allow: false, reason: "default" }; })()): Promise<{ allow: boolean; reason: string }> {
                  return { allow: true, reason: "actual handler" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:default decision",
                False,
                "default decision must fail closed",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_hook_return_newline_object(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local write",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: HookEvent): Promise<{ allow: boolean; reason: string }> {
                  return
                    { allow: false, reason: "ASI turns this into undefined" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:default decision",
                False,
                "default decision must fail closed",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_negated_hook_approval_behavior(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local write",
                  approvalBehavior: "do not require approval before external disclosure",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: HookEvent): Promise<{ allow: boolean; reason: string }> {
                  return { allow: false, reason: "fallback" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:approval behavior",
                False,
                "approval behavior must require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_treats_comment_markers_inside_hook_strings_as_strings(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local-write",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: HookEvent): Promise<{ allow: boolean; reason: string }> {
                  const marker = "/*";
                  return { allow: true, reason: "comment markers are string content" };
                  const tail = "*/";
                  return { allow: false, reason: "unreachable" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:default decision",
                False,
                "default decision must fail closed",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_treats_comment_markers_inside_hook_regex_literals_as_regex_content(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: HookEvent): Promise<{ allow: boolean; reason: string }> {
                  const opener = /[/*]/;
                  return { allow: true, reason: "regex markers are not comments" };
                  const closer = /[*/]/;
                  return { allow: false, reason: "unreachable" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:default decision",
                False,
                "default decision must fail closed",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_treats_comment_markers_inside_arrow_regex_literals_as_regex_content(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: HookEvent): Promise<{ allow: boolean; reason: string }> {
                  if (!event.kind) {
                    return { allow: false, reason: "conditional deny" };
                  }
                  const marker = () => /[/*]/;
                  return { allow: true, reason: "arrow regex markers are not comments" };
                  const closer = () => /[*/]/;
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:default decision",
                False,
                "default decision must fail closed",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_requires_hook_top_level_fallback_return(self):
        cases = [
            """\
            export async function handle(event: HookEvent): Promise<{ allow: boolean; reason: string }> {
              if (event.kind) {
                return { allow: false, reason: "conditional deny only" };
              }
            }
            """,
            """\
            export async function handle(event: HookEvent): Promise<{ allow: boolean; reason: string }> {
              class Nested {
                decide() {
                  return { allow: false, reason: "class method deny only" };
                }
              }
            }
            """,
        ]
        for handle_body in cases:
            with self.subTest(handle_body=handle_body):
                with tempfile.TemporaryDirectory() as tmpdir:
                    root = Path(tmpdir)
                    self.write_all_templates(root)
                    self.write_template(
                        root,
                        "templates/hook/hook.ts",
                        f"""\
                        export const hookContract = {{
                          sideEffectClassification: "read-only | external disclosure | local write | network write | process execution | privileged operation | irreversible mutation",
                          approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                          failureHandling: "fail closed for unsafe mutations",
                        }} as const;

                        {handle_body}
                        """,
                    )

                    results = run(root)

                self.assertIn(
                    CheckResult(
                        "template:hook:templates/hook/hook.ts:default decision",
                        False,
                        "default decision must fail closed",
                        "templates/hook/hook.ts",
                    ),
                    results,
                )

    def test_validate_templates_binds_hook_default_to_handle(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local-write",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function helper(event: unknown): Promise<{ allow: boolean; reason: string }> {
                  return { allow: false, reason: "helper is fail closed" };
                }

                export async function handle(event: unknown): Promise<{ allow: boolean; reason: string }> {
                  return { allow: true, reason: "handler is fail open" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:default decision",
                False,
                "default decision must fail closed",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_rejects_nested_hook_allow_false_return(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/hook/hook.ts",
                """\
                export const hookContract = {
                  sideEffectClassification: "read-only | external disclosure | local-write",
                  approvalBehavior: "require explicit approval before external disclosure, local write, network write, process execution, privileged operation, or irreversible mutation",
                  failureHandling: "fail closed for unsafe mutations",
                } as const;

                export async function handle(event: unknown): Promise<{ allow: boolean; reason: string }> {
                  function nested() {
                    return { allow: false, reason: "nested literal" };
                  }

                  return { allow: true, reason: "permissive default" };
                }
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:hook:templates/hook/hook.ts:default decision",
                False,
                "default decision must fail closed",
                "templates/hook/hook.ts",
            ),
            results,
        )

    def test_validate_templates_requires_agent_profile_fields(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(root, "templates/agents/profile.toml", 'mission = "only mission"\n')

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/agents/profile.toml:identity",
                False,
                "missing identity",
                "templates/agents/profile.toml",
            ),
            results,
        )

    def test_validate_templates_rejects_scalar_agent_profile_sections(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/agents/profile.toml",
                """\
                tools = "not a table"
                model = "not a table"
                config = "not a table"

                [identity]
                name = "example-agent"
                mission = "Describe the agent mission."

                [permissions]
                mode = "read-only"
                approval_required_for = ["external disclosure", "local write", "network write", "process execution", "privileged operation", "irreversible mutation"]

                [output]
                contract = "Describe the deliverable and return shape."
                format = "structured-report"
                """,
            )

            results = run(root)

        for field in ("tools", "model", "config"):
            with self.subTest(field=field):
                self.assertIn(
                    CheckResult(
                        f"template:toml:templates/agents/profile.toml:{field}",
                        False,
                        f"{field} must be a table",
                        "templates/agents/profile.toml",
                    ),
                    results,
                )

    def test_validate_templates_requires_plugin_manifest_fields(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(root, "templates/plugin/manifest.toml", 'name = "plugin-only"\n')

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/plugin/manifest.toml:components",
                False,
                "missing components",
                "templates/plugin/manifest.toml",
            ),
            results,
        )

    def test_validate_templates_rejects_scalar_plugin_components(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/plugin/manifest.toml",
                """\
                name = "example-plugin"
                version = "0.1.0"
                components = "not a table"

                [ownership]
                owner = "human"
                source = "repo"

                [permissions]
                required = ["read"]
                approval_required_for = ["external disclosure", "local write", "network write", "process execution", "privileged operation", "irreversible mutation"]
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/plugin/manifest.toml:components",
                False,
                "components must be a table",
                "templates/plugin/manifest.toml",
            ),
            results,
        )

    def test_validate_templates_requires_plugin_external_disclosure_approval(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/plugin/manifest.toml",
                """\
                name = "example-plugin"
                version = "0.1.0"

                [components]
                skills = []

                [permissions]
                required = ["read"]
                approval_required_for = ["write", "network-write", "privileged"]
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/plugin/manifest.toml:external disclosure approval",
                False,
                "approval_required_for must include external disclosure",
                "templates/plugin/manifest.toml",
            ),
            results,
        )

    def test_validate_templates_rejects_noncanonical_plugin_approval_terms(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/plugin/manifest.toml",
                """\
                name = "example-plugin"
                version = "0.1.0"

                [components]
                skills = []

                [ownership]
                source = "repo"

                [permissions]
                required = []
                approval_required_for = ["write", "external disclosure", "network-write", "privileged"]
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/plugin/manifest.toml:approval vocabulary",
                False,
                "approval_required_for must use canonical side-effect labels",
                "templates/plugin/manifest.toml",
            ),
            results,
        )

    def test_validate_templates_rejects_noncanonical_agent_profile_approval_terms(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/agents/profile.toml",
                """\
                [identity]
                name = "example-agent"
                mission = "Describe the agent mission."

                [tools]
                allow = []

                [permissions]
                mode = "read-only"
                approval_required_for = ["writes", "external disclosure", "privileged commands"]

                [model]
                preference = "inherit"

                [config]
                placeholder = "value"

                [output]
                contract = "Describe the deliverable and return shape."
                format = "structured-report"
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/agents/profile.toml:approval vocabulary",
                False,
                "approval_required_for must use canonical side-effect labels",
                "templates/agents/profile.toml",
            ),
            results,
        )

    def test_validate_templates_rejects_scalar_agent_profile_approval_terms(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/agents/profile.toml",
                """\
                [identity]
                name = "example-agent"
                mission = "Describe the agent mission."

                [tools]
                allow = []

                [permissions]
                mode = "read-only"
                approval_required_for = "external disclosure"

                [model]
                preference = "inherit"

                [config]
                placeholder = "value"

                [output]
                contract = "Describe the deliverable and return shape."
                format = "structured-report"
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/agents/profile.toml:approval vocabulary",
                False,
                "approval_required_for must use canonical side-effect labels",
                "templates/agents/profile.toml",
            ),
            results,
        )

    def test_validate_templates_requires_agent_profile_tool_allow_and_deny_lists(self):
        cases = [
            ("tools_allow", "deny = []"),
            ("tools_deny", "allow = []"),
        ]
        for field, tool_body in cases:
            with self.subTest(field=field):
                with tempfile.TemporaryDirectory() as tmpdir:
                    root = Path(tmpdir)
                    self.write_all_templates(root)
                    self.write_template(
                        root,
                        "templates/agents/profile.toml",
                        f"""\
                        [identity]
                        name = "example-agent"
                        mission = "Describe the agent mission."

                        [tools]
                        {tool_body}

                        [permissions]
                        mode = "read-only"
                        approval_required_for = ["external disclosure", "local write", "network write", "process execution", "privileged operation", "irreversible mutation"]

                        [model]
                        preference = "inherit"

                        [config]
                        placeholder = "value"

                        [output]
                        contract = "Describe the deliverable and return shape."
                        format = "structured-report"
                        """,
                    )

                    results = run(root)

                self.assertIn(
                    CheckResult(
                        f"template:toml:templates/agents/profile.toml:{field}",
                        False,
                        f"missing {field}",
                        "templates/agents/profile.toml",
                    ),
                    results,
                )

    def test_validate_templates_rejects_scalar_agent_profile_tool_lists(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/agents/profile.toml",
                """\
                [identity]
                name = "example-agent"
                mission = "Describe the agent mission."

                [tools]
                allow = "all"
                deny = "none"

                [permissions]
                mode = "read-only"
                approval_required_for = ["external disclosure", "local write", "network write", "process execution", "privileged operation", "irreversible mutation"]

                [model]
                preference = "inherit"

                [config]
                placeholder = "value"

                [output]
                contract = "Describe the deliverable and return shape."
                format = "structured-report"
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/agents/profile.toml:tools_allow",
                False,
                "tools_allow must be a list of strings",
                "templates/agents/profile.toml",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "template:toml:templates/agents/profile.toml:tools_deny",
                False,
                "tools_deny must be a list of strings",
                "templates/agents/profile.toml",
            ),
            results,
        )

    def test_validate_templates_requires_agent_profile_permission_mode(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/agents/profile.toml",
                """\
                [identity]
                name = "example-agent"
                mission = "Describe the agent mission."

                [tools]
                allow = []
                deny = []

                [permissions]
                approval_required_for = ["external disclosure", "local write", "network write", "process execution", "privileged operation", "irreversible mutation"]

                [model]
                preference = "inherit"

                [config]
                placeholder = "value"

                [output]
                contract = "Describe the deliverable and return shape."
                format = "structured-report"
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/agents/profile.toml:permission_mode",
                False,
                "missing permission_mode",
                "templates/agents/profile.toml",
            ),
            results,
        )

    def test_validate_templates_rejects_unsafe_agent_profile_permission_mode(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            text = (root / "templates/agents/profile.toml").read_text(encoding="utf-8")
            self.write_template(root, "templates/agents/profile.toml", text.replace('mode = "read-only"', 'mode = "full-access"'))

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/agents/profile.toml:permission_mode",
                False,
                "permissions.mode must be read-only",
                "templates/agents/profile.toml",
            ),
            results,
        )

    def test_validate_templates_rejects_incomplete_agent_profile_approval_coverage(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/agents/profile.toml",
                """\
                [identity]
                name = "example-agent"
                mission = "Describe the agent mission."

                [tools]
                allow = []

                [permissions]
                mode = "read-only"
                approval_required_for = ["external disclosure"]

                [model]
                preference = "inherit"

                [config]
                placeholder = "value"

                [output]
                contract = "Describe the deliverable and return shape."
                format = "structured-report"
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/agents/profile.toml:approval coverage",
                False,
                "approval_required_for must cover mutation side-effect labels",
                "templates/agents/profile.toml",
            ),
            results,
        )

    def test_validate_templates_rejects_duplicate_agent_profile_approval_labels(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/agents/profile.toml",
                """\
                [identity]
                name = "example-agent"
                mission = "Describe the agent mission."

                [tools]
                allow = []

                [permissions]
                mode = "read-only"
                approval_required_for = ["external disclosure", "external disclosure", "local write", "network write", "process execution", "privileged operation", "irreversible mutation"]

                [model]
                preference = "inherit"

                [config]
                placeholder = "value"

                [output]
                contract = "Describe the deliverable and return shape."
                format = "structured-report"
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/agents/profile.toml:approval coverage",
                False,
                "approval_required_for must cover mutation side-effect labels",
                "templates/agents/profile.toml",
            ),
            results,
        )

    def test_validate_templates_rejects_non_string_agent_profile_approval_items_without_crashing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/agents/profile.toml",
                """\
                [identity]
                name = "example-agent"
                mission = "Describe the agent mission."

                [tools]
                allow = []

                [permissions]
                mode = "read-only"
                approval_required_for = [{ label = "external disclosure" }]

                [model]
                preference = "inherit"

                [config]
                placeholder = "value"

                [output]
                contract = "Describe the deliverable and return shape."
                format = "structured-report"
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/agents/profile.toml:approval vocabulary",
                False,
                "approval_required_for must use canonical side-effect labels",
                "templates/agents/profile.toml",
            ),
            results,
        )

    def test_validate_templates_rejects_incomplete_plugin_approval_coverage(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/plugin/manifest.toml",
                """\
                name = "example-plugin"
                version = "0.1.0"

                [components]
                skills = []

                [ownership]
                source = "repo"

                [permissions]
                required = []
                approval_required_for = ["external disclosure"]
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/plugin/manifest.toml:approval coverage",
                False,
                "approval_required_for must cover mutation side-effect labels",
                "templates/plugin/manifest.toml",
            ),
            results,
        )

    def test_validate_templates_rejects_non_string_plugin_approval_items_without_crashing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/plugin/manifest.toml",
                """\
                name = "example-plugin"
                version = "0.1.0"

                [components]
                skills = []

                [ownership]
                source = "repo"

                [permissions]
                required = []
                approval_required_for = [{ label = "external disclosure" }]
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/plugin/manifest.toml:approval vocabulary",
                False,
                "approval_required_for must use canonical side-effect labels",
                "templates/plugin/manifest.toml",
            ),
            results,
        )

    def test_validate_templates_rejects_config_missing_mutation_approval_labels(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/config/example.toml",
                """\
                [ownership]
                owner = "human"

                [autonomy]
                level = "assisted"
                agent_may_continue_sessions = false

                [enabled]
                default = false

                [review]
                required = true

                [approval]
                required_for = ["external disclosure", "privileged operation", "irreversible mutation"]
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/config/example.toml:approval coverage",
                False,
                "approval.required_for must cover mutation side-effect labels",
                "templates/config/example.toml",
            ),
            results,
        )

    def test_validate_templates_rejects_non_string_config_approval_items_without_crashing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/config/example.toml",
                """\
                [ownership]
                owner = "human"

                [autonomy]
                level = "assisted"
                agent_may_continue_sessions = false
                agent_may_initiate_project_initiatives = false

                [enabled]
                default = false

                [review]
                required_before_publish = true
                review_until_clean = true
                doc_closeout_required = true
                security_closeout_required = true

                [approval]
                required_for = [{ label = "external disclosure" }]
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/config/example.toml:approval coverage",
                False,
                "approval.required_for must cover mutation side-effect labels",
                "templates/config/example.toml",
            ),
            results,
        )

    def test_validate_templates_requires_config_initiative_default_false(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/config/example.toml",
                """\
                [ownership]
                owner = "human"

                [autonomy]
                level = "assisted"
                agent_may_continue_sessions = false
                agent_may_initiate_project_initiatives = true

                [enabled]
                default = false

                [review]
                required_before_publish = true
                review_until_clean = true
                doc_closeout_required = true
                security_closeout_required = true

                [approval]
                required_for = ["external disclosure", "local write", "network write", "process execution", "privileged operation", "irreversible mutation"]
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/config/example.toml:agent_may_initiate_project_initiatives",
                False,
                "agent_may_initiate_project_initiatives must be false",
                "templates/config/example.toml",
            ),
            results,
        )

    def test_validate_templates_requires_config_review_safety_flags(self):
        cases = [
            "required_before_publish",
            "review_until_clean",
            "doc_closeout_required",
            "security_closeout_required",
        ]
        for flag in cases:
            with self.subTest(flag=flag):
                review_lines = {
                    "required_before_publish": "true",
                    "review_until_clean": "true",
                    "doc_closeout_required": "true",
                    "security_closeout_required": "true",
                }
                review_lines[flag] = "false"
                with tempfile.TemporaryDirectory() as tmpdir:
                    root = Path(tmpdir)
                    self.write_all_templates(root)
                    self.write_template(
                        root,
                        "templates/config/example.toml",
                        f"""\
                        [ownership]
                        owner = "human"

                        [autonomy]
                        level = "assisted"
                        agent_may_continue_sessions = false
                        agent_may_initiate_project_initiatives = false

                        [enabled]
                        default = false

                        [review]
                        required_before_publish = {review_lines["required_before_publish"]}
                        review_until_clean = {review_lines["review_until_clean"]}
                        doc_closeout_required = {review_lines["doc_closeout_required"]}
                        security_closeout_required = {review_lines["security_closeout_required"]}

                        [approval]
                        required_for = ["external disclosure", "local write", "network write", "process execution", "privileged operation", "irreversible mutation"]
                        """,
                    )

                    results = run(root)

                self.assertIn(
                    CheckResult(
                        f"template:toml:templates/config/example.toml:{flag}",
                        False,
                        f"review.{flag} must be true",
                        "templates/config/example.toml",
                    ),
                    results,
                )

    def test_validate_templates_requires_plugin_ownership_source(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/plugin/manifest.toml",
                """\
                name = "example-plugin"
                version = "0.1.0"

                [components]
                skills = []

                [permissions]
                required = ["read"]
                approval_required_for = ["external disclosure"]
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/plugin/manifest.toml:ownership",
                False,
                "missing ownership",
                "templates/plugin/manifest.toml",
            ),
            results,
        )

    def test_validate_templates_requires_non_empty_plugin_source(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/plugin/manifest.toml",
                """\
                name = "example-plugin"
                version = "0.1.0"

                [components]
                skills = []

                [ownership]
                owner = "human"
                source = ""

                [permissions]
                required = ["read"]
                approval_required_for = ["external disclosure"]
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/plugin/manifest.toml:source",
                False,
                "source must be a non-empty string",
                "templates/plugin/manifest.toml",
            ),
            results,
        )

    def test_validate_templates_requires_toml_fields_at_expected_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/config/example.toml",
                """\
                [ownership]
                owner = "human"
                autonomy = "misplaced"
                enabled = false
                review = true
                approval = "misplaced"
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/config/example.toml:autonomy",
                False,
                "missing autonomy",
                "templates/config/example.toml",
            ),
            results,
        )

    def test_validate_templates_requires_config_continuation_default_false(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/config/example.toml",
                """\
                [ownership]
                owner = "human"

                [autonomy]
                level = "assisted"
                agent_may_continue_sessions = true

                [enabled]
                default = false

                [review]
                required = true

                [approval]
                required_for = ["mutation"]
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/config/example.toml:agent_may_continue_sessions",
                False,
                "agent_may_continue_sessions must be false",
                "templates/config/example.toml",
            ),
            results,
        )

    def test_validate_templates_requires_config_disabled_by_default(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/config/example.toml",
                """\
                [ownership]
                owner = "human"

                [autonomy]
                level = "assisted"
                agent_may_continue_sessions = false

                [enabled]
                default = true

                [review]
                required = true

                [approval]
                required_for = ["mutation"]
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/config/example.toml:enabled.default",
                False,
                "enabled.default must be false",
                "templates/config/example.toml",
            ),
            results,
        )

    def test_validate_templates_requires_script_contract(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(root, "templates/script/validate-example.py", "print('missing contract')\n")

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:exit-code contract",
                False,
                "missing deterministic exit-code contract",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_requires_script_entry_point_equality(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                def main() -> int:
                    return 0


                if __name__ != "__main__":
                    raise SystemExit(main())
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point detail",
                False,
                'CLI entry point requires exactly one if __name__ == "__main__" guard',
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_bare_script_main_call(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                def main() -> int:
                    return 1


                if __name__ == "__main__":
                    main()
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_unreachable_script_main_call(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                def main() -> int:
                    return 0


                if __name__ == "__main__":
                    if False:
                        main()
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_lazy_script_main_call_argument(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                import sys


                def main() -> int:
                    return 0


                if __name__ == "__main__":
                    sys.exit(lambda: main())
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_sys_exit_script_entry_point(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                import sys


                def main() -> int:
                    return 1


                if __name__ == "__main__":
                    sys.exit(main())
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_requires_main_as_sole_exit_status_argument(self):
        cases = [
            "sys.exit(0, main())",
            "sys.exit(main(), status=0)",
            "raise SystemExit(0, main())",
            "raise SystemExit(main(), status=0)",
        ]
        for exit_statement in cases:
            with self.subTest(exit_statement=exit_statement):
                with tempfile.TemporaryDirectory() as tmpdir:
                    root = Path(tmpdir)
                    self.write_all_templates(root)
                    self.write_template(
                        root,
                        "templates/script/validate-example.py",
                        f"""\
                        \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                        import sys


                        def main() -> int:
                            return 1


                        if __name__ == "__main__":
                            {exit_statement}
                        """,
                    )

                    results = run(root)

                self.assertIn(
                    CheckResult(
                        "template:script:templates/script/validate-example.py:cli entry point",
                        False,
                        "missing CLI entry point",
                        "templates/script/validate-example.py",
                    ),
                    results,
                )

    def test_validate_templates_rejects_extra_script_entry_guard_statements(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                def main() -> int:
                    return 1


                if __name__ == "__main__":
                    main()
                    raise SystemExit(main())
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_multiple_script_entry_guards(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                def main() -> int:
                    return 1


                if __name__ == "__main__":
                    raise SystemExit(main())

                if __name__ == "__main__":
                    main()
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_script_entry_guard_else_body(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                def main() -> int:
                    return 1


                if __name__ == "__main__":
                    raise SystemExit(main())
                else:
                    main()
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_systemexit_raise_cause(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                def main() -> int:
                    return 1


                if __name__ == "__main__":
                    raise SystemExit(main()) from RuntimeError("side effect")
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_script_guard_before_main_definition(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                if __name__ == "__main__":
                    raise SystemExit(main())


                def main() -> int:
                    return 1
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_script_main_rebinding_before_guard(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                def main() -> int:
                    return 1


                main = lambda: 0


                if __name__ == "__main__":
                    raise SystemExit(main())
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_script_statements_after_entry_guard(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                def main() -> int:
                    return 1


                if __name__ == "__main__":
                    raise SystemExit(main())


                open("audit.log", "w").write("side effect")
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_script_module_level_side_effects(self):
        cases = [
            """\
            \"\"\"Template validator with deterministic exit-code contract.\"\"\"

            open("audit.log", "w").write("side effect")


            def main() -> int:
                return 1


            if __name__ == "__main__":
                raise SystemExit(main())
            """,
            """\
            \"\"\"Template validator with deterministic exit-code contract.\"\"\"

            def helper(value=open("audit.log", "w").write("default")) -> int:
                return 0


            def main() -> int:
                return 1


            if __name__ == "__main__":
                raise SystemExit(main())
            """,
        ]
        for script_text in cases:
            with self.subTest(script_text=script_text):
                with tempfile.TemporaryDirectory() as tmpdir:
                    root = Path(tmpdir)
                    self.write_all_templates(root)
                    self.write_template(root, "templates/script/validate-example.py", script_text)

                    results = run(root)

                self.assertIn(
                    CheckResult(
                        "template:script:templates/script/validate-example.py:cli entry point",
                        False,
                        "missing CLI entry point",
                        "templates/script/validate-example.py",
                    ),
                    results,
                )

    def test_validate_templates_rejects_script_class_body_side_effects(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                class Record:
                    value: int = open("audit.log", "w").write("side effect")


                def main() -> int:
                    return 1


                if __name__ == "__main__":
                    raise SystemExit(main())
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_script_main_body_side_effects(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                def main() -> int:
                    open("audit.log", "w").write("side effect")
                    return 1


                if __name__ == "__main__":
                    raise SystemExit(main())
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_script_path_write_side_effects(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                from pathlib import Path


                def main() -> int:
                    Path("audit.log").write_text("side effect", encoding="utf-8")
                    return 1


                if __name__ == "__main__":
                    raise SystemExit(main())
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_script_path_open_and_subprocess_side_effects(self):
        cases = [
            """\
            \"\"\"Template validator with deterministic exit-code contract.\"\"\"

            from pathlib import Path


            def main() -> int:
                Path("audit.log").open("w", encoding="utf-8")
                return 1


            if __name__ == "__main__":
                raise SystemExit(main())
            """,
            """\
            \"\"\"Template validator with deterministic exit-code contract.\"\"\"

            import subprocess


            def main() -> int:
                subprocess.Popen(["echo", "side effect"])
                return 1


            if __name__ == "__main__":
                raise SystemExit(main())
            """,
            """\
            \"\"\"Template validator with deterministic exit-code contract.\"\"\"

            import os


            def main() -> int:
                os.open("audit.log", os.O_CREAT)
                return 1


            if __name__ == "__main__":
                raise SystemExit(main())
            """,
        ]
        for script_text in cases:
            with self.subTest(script_text=script_text):
                with tempfile.TemporaryDirectory() as tmpdir:
                    root = Path(tmpdir)
                    self.write_all_templates(root)
                    self.write_template(root, "templates/script/validate-example.py", script_text)

                    results = run(root)

                self.assertIn(
                    CheckResult(
                        "template:script:templates/script/validate-example.py:cli entry point",
                        False,
                        "missing CLI entry point",
                        "templates/script/validate-example.py",
                    ),
                    results,
                )

    def test_validate_templates_rejects_script_network_side_effects(self):
        cases = [
            """\
            \"\"\"Template validator with deterministic exit-code contract.\"\"\"

            import urllib.request


            def main() -> int:
                urllib.request.urlopen("https://example.invalid")
                return 1


            if __name__ == "__main__":
                raise SystemExit(main())
            """,
            """\
            \"\"\"Template validator with deterministic exit-code contract.\"\"\"

            import socket


            def main() -> int:
                socket.create_connection(("example.invalid", 443))
                return 1


            if __name__ == "__main__":
                raise SystemExit(main())
            """,
            """\
            \"\"\"Template validator with deterministic exit-code contract.\"\"\"

            import http.client


            def main() -> int:
                http.client.HTTPConnection("example.invalid")
                return 1


            if __name__ == "__main__":
                raise SystemExit(main())
            """,
        ]
        for script_text in cases:
            with self.subTest(script_text=script_text):
                with tempfile.TemporaryDirectory() as tmpdir:
                    root = Path(tmpdir)
                    self.write_all_templates(root)
                    self.write_template(root, "templates/script/validate-example.py", script_text)

                    results = run(root)

                self.assertIn(
                    CheckResult(
                        "template:script:templates/script/validate-example.py:cli entry point",
                        False,
                        "missing CLI entry point",
                        "templates/script/validate-example.py",
                    ),
                    results,
                )

    def test_validate_templates_rejects_script_dynamic_network_side_effects(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                def main() -> int:
                    module = __builtins__["__import__"]("urllib.request", fromlist=["urlopen"])
                    getattr(module, "urlopen")("https://example.invalid/leak")
                    return 1


                if __name__ == "__main__":
                    raise SystemExit(main())
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_argparse_callable_side_effects(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                import argparse


                def main() -> int:
                    parser = argparse.ArgumentParser(description="Validate input.")
                    parser.add_argument("payload", type=eval)
                    parser.parse_args()
                    return 1


                if __name__ == "__main__":
                    raise SystemExit(main())
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_argparse_unpacking_callable_side_effects(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                import argparse


                def main() -> int:
                    parser = argparse.ArgumentParser(description="Validate input.")
                    parser.add_argument("payload", **{"type": eval})
                    parser.parse_args()
                    return 1


                if __name__ == "__main__":
                    raise SystemExit(main())
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_rebound_allowed_script_call_names(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                def main() -> int:
                    run = eval
                    run("__import__('os').system('echo unsafe')")
                    return 1


                if __name__ == "__main__":
                    raise SystemExit(main())
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_function_declaration_script_call_rebinding(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                def all(values) -> bool:
                    return True


                def main() -> int:
                    return 0 if all([False]) else 1


                if __name__ == "__main__":
                    raise SystemExit(main())
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_async_function_declaration_script_call_rebinding(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                def main() -> int:
                    async def all(values) -> bool:
                        return True

                    return 0 if all([False]) else 1


                if __name__ == "__main__":
                    raise SystemExit(main())
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_import_alias_script_call_rebinding(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                import json as run


                def main() -> int:
                    run("unsafe binding")
                    return 1


                if __name__ == "__main__":
                    raise SystemExit(main())
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_argparse_action_callable_side_effects(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                import argparse


                def transform(value: str) -> str:
                    return value


                def main() -> int:
                    parser = argparse.ArgumentParser(description="Validate input.")
                    parser.add_argument("payload", action=transform)
                    parser.parse_args()
                    return 1


                if __name__ == "__main__":
                    raise SystemExit(main())
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_script_side_effectful_main_declaration(self):
        cases = [
            """\
            \"\"\"Template validator with deterministic exit-code contract.\"\"\"

            def replace(function):
                open("audit.log", "w").write("decorated")
                return function


            @replace
            def main() -> int:
                return 1


            if __name__ == "__main__":
                raise SystemExit(main())
            """,
            """\
            \"\"\"Template validator with deterministic exit-code contract.\"\"\"

            def main(value=open("audit.log", "w").write("default")) -> int:
                return 1


            if __name__ == "__main__":
                raise SystemExit(main())
            """,
        ]
        for script_text in cases:
            with self.subTest(script_text=script_text):
                with tempfile.TemporaryDirectory() as tmpdir:
                    root = Path(tmpdir)
                    self.write_all_templates(root)
                    self.write_template(root, "templates/script/validate-example.py", script_text)

                    results = run(root)

                self.assertIn(
                    CheckResult(
                        "template:script:templates/script/validate-example.py:cli entry point",
                        False,
                        "missing CLI entry point",
                        "templates/script/validate-example.py",
                    ),
                    results,
                )

    def test_validate_templates_requires_module_level_script_main_definition(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                def wrapper() -> None:
                    def main() -> int:
                        return 0


                if __name__ == "__main__":
                    raise SystemExit(main())
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_nested_script_entry_point_guard(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                def main() -> int:
                    return 0


                def wrapper() -> None:
                    if __name__ == "__main__":
                        raise SystemExit(main())
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_rejects_commented_script_entry_point(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/script/validate-example.py",
                """\
                \"\"\"Template validator with deterministic exit-code contract.\"\"\"

                # def main() -> int:
                #     return 0

                # if __name__ == "__main__":
                #     raise SystemExit(main())
                """,
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:script:templates/script/validate-example.py:cli entry point",
                False,
                "missing CLI entry point",
                "templates/script/validate-example.py",
            ),
            results,
        )

    def test_validate_templates_requires_equipment_shop_card_sections(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(root, "templates/equipment-shop-card.md", "# Equipment Shop Card\n\nStatus: Template\n\n## Fit\n")

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:section:templates/equipment-shop-card.md:Component manifest",
                False,
                "missing section: Component manifest",
                "templates/equipment-shop-card.md",
            ),
            results,
        )

    def test_validate_templates_requires_equipment_inspection_test_plan_sections(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(
                root,
                "templates/equipment-inspection-test-plan.md",
                "# Equipment Inspection and Test Plan\n\nStatus: Template\n\n## Scope\n",
            )

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:section:templates/equipment-inspection-test-plan.md:Completion Decision",
                False,
                "missing section: Completion Decision",
                "templates/equipment-inspection-test-plan.md",
            ),
            results,
        )

    def test_validate_templates_requires_equipment_stock_record_schema_version(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(root, "templates/equipment-stock-record.toml", "[[equipment]]\nid = \"example\"\n")

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/equipment-stock-record.toml:schema_version",
                False,
                "missing schema_version",
                "templates/equipment-stock-record.toml",
            ),
            results,
        )

    def test_validate_templates_requires_mcp_tool_sections(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(root, "templates/mcp/tool-spec.md", "# Tool\n\n## Input schema\n")

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:section:templates/mcp/tool-spec.md:Read/write classification",
                False,
                "missing section: Read/write classification",
                "templates/mcp/tool-spec.md",
            ),
            results,
        )

    def test_validate_templates_requires_config_placeholders(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_templates(root)
            self.write_template(root, "templates/config/example.toml", "[ownership]\nowner = \"human\"\n")

            results = run(root)

        self.assertIn(
            CheckResult(
                "template:toml:templates/config/example.toml:autonomy",
                False,
                "missing autonomy",
                "templates/config/example.toml",
            ),
            results,
        )


class PublishedEquipmentDeliveryValidationTests(unittest.TestCase):
    def write_inventory(self, root: Path, content: str) -> None:
        path = root / "inventory/equipment.toml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")

    def write_inventory_view(self, root: Path, content: str) -> None:
        path = root / "docs/equipment/inventory.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")

    def write_inspection_test_plan(
        self,
        root: Path,
        relative_path: str = "docs/equipment/inspection-test-plans/example.md",
    ) -> None:
        plan = root / relative_path
        plan.parent.mkdir(parents=True, exist_ok=True)
        plan.write_text(
            "# Example Equipment Inspection and Test Plan\n\n"
            "Status: Equipment Inspection and Test Plan\n\n"
            "## Scope\n\n"
            "Example stock slice.\n\n"
            "## Subject Under Inspection\n\n"
            "Example Equipment.\n\n"
            "## Inspection Checklist\n\n"
            "- Inspect the stock record.\n\n"
            "## Test Plan\n\n"
            "- Run the validator.\n\n"
            "## Evidence Requirements\n\n"
            "- Record validation output.\n\n"
            "## Completion Decision\n\n"
            "Completion status: complete\n\n"
            "Delivery compliance: passed\n",
            encoding="utf-8",
        )

    def write_routing_docs(
        self,
        root: Path,
        *,
        readme_link: bool = True,
        docs_link: bool = True,
        tour_link: bool = True,
    ) -> None:
        readme = root / "README.md"
        readme.write_text(
            "[Inventory](docs/equipment/inventory.md)\n"
            if readme_link
            else "No inventory route.\n",
            encoding="utf-8",
        )
        docs = root / "docs/README.md"
        docs.parent.mkdir(parents=True, exist_ok=True)
        docs.write_text(
            "[Inventory](equipment/inventory.md)\n"
            if docs_link
            else "No inventory route.\n",
            encoding="utf-8",
        )
        tour = root / "docs/forge-tour.md"
        tour.write_text(
            "[Inventory](equipment/inventory.md)\n"
            if tour_link
            else "No inventory route.\n",
            encoding="utf-8",
        )

    def test_validate_published_equipment_delivery_accepts_empty_stock_inventory(self):
        validator = importlib.import_module("tools.validate_armory_integrity")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_inventory(
                root,
                """
                schema_version = "agent-armory.equipment-stock.v1"
                equipment = []
                """,
            )

            results = validator.validate_published_equipment_delivery(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    "published_equipment_delivery:inventory",
                    True,
                    "valid stock inventory",
                    "inventory/equipment.toml",
                )
            ],
        )

    def test_validate_published_equipment_delivery_rejects_missing_inspection_test_plan(self):
        validator = importlib.import_module("tools.validate_armory_integrity")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            runtime = root / "tools/runtime.py"
            runtime.parent.mkdir(parents=True, exist_ok=True)
            runtime.write_text("print('runtime')\n", encoding="utf-8")
            self.write_inventory(
                root,
                """
                schema_version = "agent-armory.equipment-stock.v1"

                [[equipment]]
                id = "example"
                name = "Example Equipment"
                summary = "Demonstrates a valid stock inventory record."
                promotion_state = "published"
                delivery_compliance = "passed"
                shop_card = "docs/equipment/shop-cards/example.md"

                [[equipment.components]]
                name = "Runtime"
                kind = "script"
                status = "required"
                paths = ["tools/runtime.py"]

                [[equipment.components]]
                name = "Future plugin"
                kind = "plugin"
                status = "planned"
                paths = []
                notes = "Future plugin is tracked but not part of the stocked slice."
                """,
            )
            shop_card = root / "docs/equipment/shop-cards/example.md"
            shop_card.parent.mkdir(parents=True, exist_ok=True)
            shop_card.write_text("# Example Equipment\n\nStatus: Equipment Shop Card\n", encoding="utf-8")

            results = validator.validate_published_equipment_delivery(root)

        self.assertIn(
            CheckResult(
                "published_equipment_delivery:equipment:example:inspection_test_plan",
                False,
                "missing inspection_test_plan",
                "inventory/equipment.toml",
            ),
            results,
        )

    def test_validate_published_equipment_delivery_rejects_inspection_test_plan_outside_itp_directory(self):
        validator = importlib.import_module("tools.validate_armory_integrity")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_inventory(
                root,
                """
                schema_version = "agent-armory.equipment-stock.v1"

                [[equipment]]
                id = "example"
                name = "Example Equipment"
                summary = "Demonstrates stock inventory validation."
                promotion_state = "published"
                delivery_compliance = "pending"
                shop_card = "docs/equipment/shop-cards/example.md"
                inspection_test_plan = "docs/equipment/example-itp.md"
                """,
            )
            shop_card = root / "docs/equipment/shop-cards/example.md"
            shop_card.parent.mkdir(parents=True, exist_ok=True)
            shop_card.write_text("# Example Equipment\n\nStatus: Equipment Shop Card\n", encoding="utf-8")
            self.write_inspection_test_plan(root, "docs/equipment/example-itp.md")

            results = validator.validate_published_equipment_delivery(root)

        self.assertIn(
            CheckResult(
                "published_equipment_delivery:equipment:example:inspection_test_plan",
                False,
                "inspection_test_plan must be a Markdown file under docs/equipment/inspection-test-plans/",
                "inventory/equipment.toml",
            ),
            results,
        )

    def test_validate_published_equipment_delivery_rejects_inspection_test_plan_missing_required_section(self):
        validator = importlib.import_module("tools.validate_armory_integrity")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_inventory(
                root,
                """
                schema_version = "agent-armory.equipment-stock.v1"

                [[equipment]]
                id = "example"
                name = "Example Equipment"
                summary = "Demonstrates stock inventory validation."
                promotion_state = "published"
                delivery_compliance = "pending"
                shop_card = "docs/equipment/shop-cards/example.md"
                inspection_test_plan = "docs/equipment/inspection-test-plans/example.md"
                """,
            )
            shop_card = root / "docs/equipment/shop-cards/example.md"
            shop_card.parent.mkdir(parents=True, exist_ok=True)
            shop_card.write_text("# Example Equipment\n\nStatus: Equipment Shop Card\n", encoding="utf-8")
            plan = root / "docs/equipment/inspection-test-plans/example.md"
            plan.parent.mkdir(parents=True, exist_ok=True)
            plan.write_text(
                "# Example Equipment Inspection and Test Plan\n\n"
                "Status: Equipment Inspection and Test Plan\n\n"
                "## Scope\n\nExample stock slice.\n\n"
                "## Subject Under Inspection\n\nExample Equipment.\n\n"
                "## Inspection Checklist\n\n- Inspect the stock record.\n\n"
                "## Evidence Requirements\n\n- Record validation output.\n\n"
                "## Completion Decision\n\nCompletion status: pending\n",
                encoding="utf-8",
            )

            results = validator.validate_published_equipment_delivery(root)

        self.assertIn(
            CheckResult(
                "published_equipment_delivery:equipment:example:inspection_test_plan:section:Test Plan",
                False,
                "missing section: Test Plan",
                "docs/equipment/inspection-test-plans/example.md",
            ),
            results,
        )

    def test_validate_published_equipment_delivery_rejects_missing_inspection_test_plan_file(self):
        validator = importlib.import_module("tools.validate_armory_integrity")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_inventory(
                root,
                """
                schema_version = "agent-armory.equipment-stock.v1"

                [[equipment]]
                id = "example"
                name = "Example Equipment"
                summary = "Demonstrates stock inventory validation."
                promotion_state = "published"
                delivery_compliance = "pending"
                shop_card = "docs/equipment/shop-cards/example.md"
                inspection_test_plan = "docs/equipment/inspection-test-plans/missing.md"
                """,
            )
            shop_card = root / "docs/equipment/shop-cards/example.md"
            shop_card.parent.mkdir(parents=True, exist_ok=True)
            shop_card.write_text("# Example Equipment\n\nStatus: Equipment Shop Card\n", encoding="utf-8")

            results = validator.validate_published_equipment_delivery(root)

        self.assertIn(
            CheckResult(
                "published_equipment_delivery:equipment:example:inspection_test_plan",
                False,
                "missing",
                "docs/equipment/inspection-test-plans/missing.md",
            ),
            results,
        )

    def test_validate_published_equipment_delivery_rejects_passed_delivery_without_completed_itp(self):
        validator = importlib.import_module("tools.validate_armory_integrity")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_inventory(
                root,
                """
                schema_version = "agent-armory.equipment-stock.v1"

                [[equipment]]
                id = "example"
                name = "Example Equipment"
                summary = "Demonstrates stock inventory validation."
                promotion_state = "published"
                delivery_compliance = "passed"
                shop_card = "docs/equipment/shop-cards/example.md"
                inspection_test_plan = "docs/equipment/inspection-test-plans/example.md"
                """,
            )
            shop_card = root / "docs/equipment/shop-cards/example.md"
            shop_card.parent.mkdir(parents=True, exist_ok=True)
            shop_card.write_text("# Example Equipment\n\nStatus: Equipment Shop Card\n", encoding="utf-8")
            plan = root / "docs/equipment/inspection-test-plans/example.md"
            plan.parent.mkdir(parents=True, exist_ok=True)
            plan.write_text(
                "# Example Equipment Inspection and Test Plan\n\n"
                "Status: Equipment Inspection and Test Plan\n\n"
                "## Scope\n\nExample stock slice.\n\n"
                "## Subject Under Inspection\n\nExample Equipment.\n\n"
                "## Inspection Checklist\n\n- Inspect the stock record.\n\n"
                "## Test Plan\n\n- Run the validator.\n\n"
                "## Evidence Requirements\n\n- Record validation output.\n\n"
                "## Completion Decision\n\nCompletion status: pending\n",
                encoding="utf-8",
            )

            results = validator.validate_published_equipment_delivery(root)

        self.assertIn(
            CheckResult(
                "published_equipment_delivery:equipment:example:inspection_test_plan:completion",
                False,
                "delivery_compliance passed requires completed ITP evidence",
                "docs/equipment/inspection-test-plans/example.md",
            ),
            results,
        )

    def test_validate_published_equipment_delivery_accepts_valid_stock_record_with_complete_itp(self):
        validator = importlib.import_module("tools.validate_armory_integrity")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            runtime = root / "tools/runtime.py"
            runtime.parent.mkdir(parents=True, exist_ok=True)
            runtime.write_text("print('runtime')\n", encoding="utf-8")
            self.write_inventory(
                root,
                """
                schema_version = "agent-armory.equipment-stock.v1"

                [[equipment]]
                id = "example"
                name = "Example Equipment"
                summary = "Demonstrates a valid stock inventory record."
                promotion_state = "published"
                delivery_compliance = "passed"
                shop_card = "docs/equipment/shop-cards/example.md"
                inspection_test_plan = "docs/equipment/inspection-test-plans/example.md"

                [[equipment.components]]
                name = "Runtime"
                kind = "script"
                status = "required"
                paths = ["tools/runtime.py"]

                [[equipment.components]]
                name = "Future plugin"
                kind = "plugin"
                status = "planned"
                paths = []
                notes = "Future plugin is tracked but not part of the stocked slice."
                """,
            )
            shop_card = root / "docs/equipment/shop-cards/example.md"
            shop_card.parent.mkdir(parents=True, exist_ok=True)
            shop_card.write_text("# Example Equipment\n\nStatus: Equipment Shop Card\n", encoding="utf-8")
            self.write_inspection_test_plan(root)

            results = validator.validate_published_equipment_delivery(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    "published_equipment_delivery:inventory",
                    True,
                    "valid stock inventory",
                    "inventory/equipment.toml",
                )
            ],
        )

    def test_validate_published_equipment_delivery_rejects_missing_equipment_key(self):
        validator = importlib.import_module("tools.validate_armory_integrity")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_inventory(root, 'schema_version = "agent-armory.equipment-stock.v1"\n')

            results = validator.validate_published_equipment_delivery(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    "published_equipment_delivery:equipment",
                    False,
                    "missing equipment",
                    "inventory/equipment.toml",
                )
            ],
        )

    def test_validate_published_equipment_delivery_accepts_completion_decision_at_deeper_heading(self):
        validator = importlib.import_module("tools.validate_armory_integrity")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_inventory(
                root,
                """
                schema_version = "agent-armory.equipment-stock.v1"

                [[equipment]]
                id = "example"
                name = "Example Equipment"
                summary = "Demonstrates stock inventory validation."
                promotion_state = "published"
                delivery_compliance = "passed"
                shop_card = "docs/equipment/shop-cards/example.md"
                inspection_test_plan = "docs/equipment/inspection-test-plans/example.md"
                """,
            )
            shop_card = root / "docs/equipment/shop-cards/example.md"
            shop_card.parent.mkdir(parents=True, exist_ok=True)
            shop_card.write_text("# Example Equipment\n\nStatus: Equipment Shop Card\n", encoding="utf-8")
            plan = root / "docs/equipment/inspection-test-plans/example.md"
            plan.parent.mkdir(parents=True, exist_ok=True)
            plan.write_text(
                "# Example Equipment Inspection and Test Plan\n\n"
                "Status: Equipment Inspection and Test Plan\n\n"
                "### Scope\n\nExample stock slice.\n\n"
                "### Subject Under Inspection\n\nExample Equipment.\n\n"
                "### Inspection Checklist\n\n- Inspect the stock record.\n\n"
                "### Test Plan\n\n- Run the validator.\n\n"
                "### Evidence Requirements\n\n- Record validation output.\n\n"
                "### Completion Decision\n\n"
                "Completion status: complete\n\n"
                "Delivery compliance: passed\n",
                encoding="utf-8",
            )

            results = validator.validate_published_equipment_delivery(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    "published_equipment_delivery:inventory",
                    True,
                    "valid stock inventory",
                    "inventory/equipment.toml",
                )
            ],
        )

    def test_validate_published_equipment_delivery_rejects_passed_delivery_for_unpublished_equipment(self):
        validator = importlib.import_module("tools.validate_armory_integrity")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_inventory(
                root,
                """
                schema_version = "agent-armory.equipment-stock.v1"

                [[equipment]]
                id = "example"
                name = "Example Equipment"
                summary = "Demonstrates stock inventory validation."
                promotion_state = "validated"
                delivery_compliance = "passed"
                shop_card = "docs/equipment/shop-cards/example.md"
                """,
            )
            shop_card = root / "docs/equipment/shop-cards/example.md"
            shop_card.parent.mkdir(parents=True, exist_ok=True)
            shop_card.write_text("# Example Equipment\n\nStatus: Equipment Shop Card\n", encoding="utf-8")

            results = validator.validate_published_equipment_delivery(root)

        self.assertIn(
            CheckResult(
                "published_equipment_delivery:equipment:example:delivery_compliance",
                False,
                "delivery_compliance passed requires promotion_state published",
                "inventory/equipment.toml",
            ),
            results,
        )

    def test_validate_published_equipment_delivery_rejects_required_component_without_paths(self):
        validator = importlib.import_module("tools.validate_armory_integrity")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_inventory(
                root,
                """
                schema_version = "agent-armory.equipment-stock.v1"

                [[equipment]]
                id = "example"
                name = "Example Equipment"
                summary = "Demonstrates stock inventory validation."
                promotion_state = "published"
                delivery_compliance = "passed"
                shop_card = "docs/equipment/shop-cards/example.md"

                [[equipment.components]]
                name = "Runtime"
                kind = "script"
                status = "required"
                paths = []
                """,
            )
            shop_card = root / "docs/equipment/shop-cards/example.md"
            shop_card.parent.mkdir(parents=True, exist_ok=True)
            shop_card.write_text("# Example Equipment\n\nStatus: Equipment Shop Card\n", encoding="utf-8")

            results = validator.validate_published_equipment_delivery(root)

        self.assertIn(
            CheckResult(
                "published_equipment_delivery:equipment:example:component:Runtime:paths",
                False,
                "required components must list at least one inspectable repo path",
                "inventory/equipment.toml",
            ),
            results,
        )

    def test_validate_published_equipment_delivery_rejects_missing_component_required_fields(self):
        validator = importlib.import_module("tools.validate_armory_integrity")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_inventory(
                root,
                """
                schema_version = "agent-armory.equipment-stock.v1"

                [[equipment]]
                id = "example"
                name = "Example Equipment"
                summary = "Demonstrates stock inventory validation."
                promotion_state = "published"
                delivery_compliance = "pending"
                shop_card = "docs/equipment/shop-cards/example.md"

                [[equipment.components]]
                status = "optional"
                paths = []

                [[equipment.components]]
                name = "Runtime"
                status = "required"
                paths = []

                [[equipment.components]]
                name = "Docs"
                kind = "documentation"
                status = "optional"
                """,
            )
            shop_card = root / "docs/equipment/shop-cards/example.md"
            shop_card.parent.mkdir(parents=True, exist_ok=True)
            shop_card.write_text("# Example Equipment\n\nStatus: Equipment Shop Card\n", encoding="utf-8")

            results = validator.validate_published_equipment_delivery(root)

        self.assertIn(
            CheckResult(
                "published_equipment_delivery:equipment:example:component:1:name",
                False,
                "missing name",
                "inventory/equipment.toml",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "published_equipment_delivery:equipment:example:component:1:kind",
                False,
                "missing kind",
                "inventory/equipment.toml",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "published_equipment_delivery:equipment:example:component:Runtime:kind",
                False,
                "missing kind",
                "inventory/equipment.toml",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "published_equipment_delivery:equipment:example:component:Docs:paths",
                False,
                "missing paths",
                "inventory/equipment.toml",
            ),
            results,
        )

    def test_validate_published_equipment_delivery_rejects_missing_component_path(self):
        validator = importlib.import_module("tools.validate_armory_integrity")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_inventory(
                root,
                """
                schema_version = "agent-armory.equipment-stock.v1"

                [[equipment]]
                id = "example"
                name = "Example Equipment"
                summary = "Demonstrates stock inventory validation."
                promotion_state = "published"
                delivery_compliance = "passed"
                shop_card = "docs/equipment/shop-cards/example.md"

                [[equipment.components]]
                name = "Runtime"
                kind = "script"
                status = "required"
                paths = ["tools/missing-runtime.py"]
                """,
            )
            shop_card = root / "docs/equipment/shop-cards/example.md"
            shop_card.parent.mkdir(parents=True, exist_ok=True)
            shop_card.write_text("# Example Equipment\n\nStatus: Equipment Shop Card\n", encoding="utf-8")

            results = validator.validate_published_equipment_delivery(root)

        self.assertIn(
            CheckResult(
                "published_equipment_delivery:equipment:example:component:Runtime:path:tools/missing-runtime.py",
                False,
                "missing",
                "tools/missing-runtime.py",
            ),
            results,
        )

    def test_validate_published_equipment_delivery_rejects_blank_component_path(self):
        validator = importlib.import_module("tools.validate_armory_integrity")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_inventory(
                root,
                """
                schema_version = "agent-armory.equipment-stock.v1"

                [[equipment]]
                id = "example"
                name = "Example Equipment"
                summary = "Demonstrates stock inventory validation."
                promotion_state = "published"
                delivery_compliance = "passed"
                shop_card = "docs/equipment/shop-cards/example.md"

                [[equipment.components]]
                name = "Runtime"
                kind = "script"
                status = "required"
                paths = [""]
                """,
            )
            shop_card = root / "docs/equipment/shop-cards/example.md"
            shop_card.parent.mkdir(parents=True, exist_ok=True)
            shop_card.write_text("# Example Equipment\n\nStatus: Equipment Shop Card\n", encoding="utf-8")

            results = validator.validate_published_equipment_delivery(root)

        self.assertIn(
            CheckResult(
                "published_equipment_delivery:equipment:example:component:Runtime:paths",
                False,
                "component paths must be a list of non-empty strings",
                "inventory/equipment.toml",
            ),
            results,
        )

    def test_validate_published_equipment_delivery_rejects_component_path_escape(self):
        validator = importlib.import_module("tools.validate_armory_integrity")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            runtime = root / "tools/runtime.py"
            runtime.parent.mkdir(parents=True, exist_ok=True)
            runtime.write_text("print('runtime')\n", encoding="utf-8")
            self.write_inventory(
                root,
                """
                schema_version = "agent-armory.equipment-stock.v1"

                [[equipment]]
                id = "example"
                name = "Example Equipment"
                summary = "Demonstrates stock inventory validation."
                promotion_state = "published"
                delivery_compliance = "passed"
                shop_card = "docs/equipment/shop-cards/example.md"

                [[equipment.components]]
                name = "Runtime"
                kind = "script"
                status = "required"
                paths = ["tools/runtime.py", "../outside.py"]
                """,
            )
            shop_card = root / "docs/equipment/shop-cards/example.md"
            shop_card.parent.mkdir(parents=True, exist_ok=True)
            shop_card.write_text("# Example Equipment\n\nStatus: Equipment Shop Card\n", encoding="utf-8")

            results = validator.validate_published_equipment_delivery(root)

        self.assertIn(
            CheckResult(
                "published_equipment_delivery:equipment:example:component:Runtime:path:../outside.py",
                False,
                "path invalid",
                "../outside.py",
            ),
            results,
        )

    def test_validate_published_equipment_delivery_rejects_symlinked_component_path(self):
        validator = importlib.import_module("tools.validate_armory_integrity")
        with tempfile.TemporaryDirectory() as tmpdir, tempfile.TemporaryDirectory() as outside_tmpdir:
            root = Path(tmpdir)
            outside = Path(outside_tmpdir) / "outside-runtime.py"
            outside.write_text("print('outside')\n", encoding="utf-8")
            runtime = root / "tools/runtime.py"
            runtime.parent.mkdir(parents=True, exist_ok=True)
            runtime.symlink_to(outside)
            self.write_inventory(
                root,
                """
                schema_version = "agent-armory.equipment-stock.v1"

                [[equipment]]
                id = "example"
                name = "Example Equipment"
                summary = "Demonstrates stock inventory validation."
                promotion_state = "published"
                delivery_compliance = "passed"
                shop_card = "docs/equipment/shop-cards/example.md"

                [[equipment.components]]
                name = "Runtime"
                kind = "script"
                status = "required"
                paths = ["tools/runtime.py"]
                """,
            )
            shop_card = root / "docs/equipment/shop-cards/example.md"
            shop_card.parent.mkdir(parents=True, exist_ok=True)
            shop_card.write_text("# Example Equipment\n\nStatus: Equipment Shop Card\n", encoding="utf-8")

            results = validator.validate_published_equipment_delivery(root)

        self.assertIn(
            CheckResult(
                "published_equipment_delivery:equipment:example:component:Runtime:path:tools/runtime.py",
                False,
                "path contains symlink",
                "tools/runtime.py",
            ),
            results,
        )

    def test_validate_published_equipment_delivery_rejects_planned_component_without_notes(self):
        validator = importlib.import_module("tools.validate_armory_integrity")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_inventory(
                root,
                """
                schema_version = "agent-armory.equipment-stock.v1"

                [[equipment]]
                id = "example"
                name = "Example Equipment"
                summary = "Demonstrates stock inventory validation."
                promotion_state = "published"
                delivery_compliance = "pending"
                shop_card = "docs/equipment/shop-cards/example.md"

                [[equipment.components]]
                name = "Codex Plugin"
                kind = "plugin"
                status = "planned"
                paths = []
                """,
            )
            shop_card = root / "docs/equipment/shop-cards/example.md"
            shop_card.parent.mkdir(parents=True, exist_ok=True)
            shop_card.write_text("# Example Equipment\n\nStatus: Equipment Shop Card\n", encoding="utf-8")

            results = validator.validate_published_equipment_delivery(root)

        self.assertIn(
            CheckResult(
                "published_equipment_delivery:equipment:example:component:Codex Plugin:notes",
                False,
                "planned and unavailable components must explain their status in notes",
                "inventory/equipment.toml",
            ),
            results,
        )

    def test_validate_published_equipment_delivery_rejects_shop_card_outside_shop_card_directory(self):
        validator = importlib.import_module("tools.validate_armory_integrity")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_inventory(
                root,
                """
                schema_version = "agent-armory.equipment-stock.v1"

                [[equipment]]
                id = "example"
                name = "Example Equipment"
                summary = "Demonstrates stock inventory validation."
                promotion_state = "published"
                delivery_compliance = "pending"
                shop_card = "docs/equipment/example.md"
                """,
            )
            shop_card = root / "docs/equipment/example.md"
            shop_card.parent.mkdir(parents=True, exist_ok=True)
            shop_card.write_text("# Example Equipment\n\nStatus: Equipment Shop Card\n", encoding="utf-8")

            results = validator.validate_published_equipment_delivery(root)

        self.assertIn(
            CheckResult(
                "published_equipment_delivery:equipment:example:shop_card",
                False,
                "shop_card must be a Markdown file under docs/equipment/shop-cards/",
                "inventory/equipment.toml",
            ),
            results,
        )

    def test_validate_published_equipment_delivery_rejects_missing_required_record_field(self):
        validator = importlib.import_module("tools.validate_armory_integrity")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_inventory(
                root,
                """
                schema_version = "agent-armory.equipment-stock.v1"

                [[equipment]]
                id = "example"
                name = "Example Equipment"
                promotion_state = "published"
                delivery_compliance = "pending"
                shop_card = "docs/equipment/shop-cards/example.md"
                """,
            )
            shop_card = root / "docs/equipment/shop-cards/example.md"
            shop_card.parent.mkdir(parents=True, exist_ok=True)
            shop_card.write_text("# Example Equipment\n\nStatus: Equipment Shop Card\n", encoding="utf-8")

            results = validator.validate_published_equipment_delivery(root)

        self.assertIn(
            CheckResult(
                "published_equipment_delivery:equipment:example:summary",
                False,
                "missing summary",
                "inventory/equipment.toml",
            ),
            results,
        )

    def test_validate_published_equipment_delivery_rejects_missing_fields_without_duplicate_detail_errors(self):
        validator = importlib.import_module("tools.validate_armory_integrity")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_inventory(
                root,
                """
                schema_version = "agent-armory.equipment-stock.v1"

                [[equipment]]
                id = "example"
                name = "Example Equipment"
                summary = "Demonstrates stock inventory validation."
                """,
            )

            results = validator.validate_published_equipment_delivery(root)

        for field in ["promotion_state", "delivery_compliance", "shop_card"]:
            self.assertIn(
                CheckResult(
                    f"published_equipment_delivery:equipment:example:{field}",
                    False,
                    f"missing {field}",
                    "inventory/equipment.toml",
                ),
                results,
            )
        duplicate_errors = [
            CheckResult(
                "published_equipment_delivery:equipment:example:promotion_state",
                False,
                "promotion_state must be a known equipment promotion state",
                "inventory/equipment.toml",
            ),
            CheckResult(
                "published_equipment_delivery:equipment:example:delivery_compliance",
                False,
                "delivery_compliance must be not_evaluated, pending, passed, or blocked",
                "inventory/equipment.toml",
            ),
            CheckResult(
                "published_equipment_delivery:equipment:example:shop_card",
                False,
                "shop_card must be a Markdown file under docs/equipment/shop-cards/",
                "inventory/equipment.toml",
            ),
        ]
        for duplicate_error in duplicate_errors:
            self.assertNotIn(duplicate_error, results)

    def test_validate_published_equipment_inventory_view_accepts_empty_stock_projection(self):
        validator = importlib.import_module("tools.validate_armory_integrity")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_inventory(
                root,
                """
                schema_version = "agent-armory.equipment-stock.v1"
                equipment = []
                """,
            )
            self.write_inventory_view(
                root,
                """
                # Stocked Equipment Inventory

                ## Stock Authority

                The canonical stock authority is
                [`inventory/equipment.toml`](../../inventory/equipment.toml).
                The stock inventory uses schema `agent-armory.equipment-stock.v1`.

                ## Stock Records

                No stocked equipment is recorded in `inventory/equipment.toml` yet.

                ## Shop Cards

                Shop cards live in the [shop-card index](shop-cards/README.md).

                ## Inspection and Test Plans

                ITPs live in the [ITP index](inspection-test-plans/README.md).
                """,
            )

            results = validator.validate_published_equipment_inventory_view(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    "published_equipment_inventory_view:projection",
                    True,
                    "inventory view matches stock inventory",
                    "docs/equipment/inventory.md",
                )
            ],
        )

    def test_validate_published_equipment_inventory_view_requires_empty_stock_sentence(self):
        validator = importlib.import_module("tools.validate_armory_integrity")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_inventory(
                root,
                """
                schema_version = "agent-armory.equipment-stock.v1"
                equipment = []
                """,
            )
            self.write_inventory_view(
                root,
                """
                # Stocked Equipment Inventory

                ## Stock Authority

                [`inventory/equipment.toml`](../../inventory/equipment.toml)
                uses schema `agent-armory.equipment-stock.v1`.

                ## Stock Records

                Nothing is stocked.

                ## Shop Cards

                [Shop-card index](shop-cards/README.md)
                """,
            )

            results = validator.validate_published_equipment_inventory_view(root)

        self.assertIn(
            CheckResult(
                "published_equipment_inventory_view:empty_stock",
                False,
                "missing exact empty stock sentence",
                "docs/equipment/inventory.md",
            ),
            results,
        )

    def test_validate_published_equipment_inventory_view_requires_itp_index_link(self):
        validator = importlib.import_module("tools.validate_armory_integrity")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_inventory(
                root,
                """
                schema_version = "agent-armory.equipment-stock.v1"
                equipment = []
                """,
            )
            self.write_inventory_view(
                root,
                """
                # Stocked Equipment Inventory

                ## Stock Authority

                [`inventory/equipment.toml`](../../inventory/equipment.toml)
                uses schema `agent-armory.equipment-stock.v1`.

                ## Stock Records

                No stocked equipment is recorded in `inventory/equipment.toml` yet.

                ## Shop Cards

                [Shop-card index](shop-cards/README.md)
                """,
            )

            results = validator.validate_published_equipment_inventory_view(root)

        self.assertIn(
            CheckResult(
                "published_equipment_inventory_view:inspection_test_plans",
                False,
                "missing inspection-test-plan index link",
                "docs/equipment/inventory.md",
            ),
            results,
        )

    def test_validate_published_equipment_inventory_view_rejects_extra_empty_stock_text(self):
        validator = importlib.import_module("tools.validate_armory_integrity")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_inventory(
                root,
                """
                schema_version = "agent-armory.equipment-stock.v1"
                equipment = []
                """,
            )
            self.write_inventory_view(
                root,
                """
                # Stocked Equipment Inventory

                ## Stock Authority

                [`inventory/equipment.toml`](../../inventory/equipment.toml)
                uses schema `agent-armory.equipment-stock.v1`.

                ## Stock Records

                No stocked equipment is recorded in `inventory/equipment.toml` yet.

                Another empty-stock note.

                ## Shop Cards

                [Shop-card index](shop-cards/README.md)
                """,
            )

            results = validator.validate_published_equipment_inventory_view(root)

        self.assertIn(
            CheckResult(
                "published_equipment_inventory_view:empty_stock",
                False,
                "missing exact empty stock sentence",
                "docs/equipment/inventory.md",
            ),
            results,
        )

    def test_validate_published_equipment_inventory_view_rejects_stale_stock_bullets_when_inventory_empty(self):
        validator = importlib.import_module("tools.validate_armory_integrity")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_inventory(
                root,
                """
                schema_version = "agent-armory.equipment-stock.v1"
                equipment = []
                """,
            )
            self.write_inventory_view(
                root,
                """
                # Stocked Equipment Inventory

                ## Stock Authority

                [`inventory/equipment.toml`](../../inventory/equipment.toml)
                uses schema `agent-armory.equipment-stock.v1`.

                ## Stock Records

                No stocked equipment is recorded in `inventory/equipment.toml` yet.

                - `agent-equipment-config` - stale stock claim

                ## Shop Cards

                [Shop-card index](shop-cards/README.md)
                """,
            )

            results = validator.validate_published_equipment_inventory_view(root)

        self.assertIn(
            CheckResult(
                "published_equipment_inventory_view:empty_stock",
                False,
                "empty stock view must not list stock record bullets",
                "docs/equipment/inventory.md",
            ),
            results,
        )
        self.assertNotIn(
            CheckResult(
                "published_equipment_inventory_view:empty_stock",
                False,
                "missing exact empty stock sentence",
                "docs/equipment/inventory.md",
            ),
            results,
        )

    def test_validate_published_equipment_inventory_view_requires_non_empty_stock_record_bullets(self):
        validator = importlib.import_module("tools.validate_armory_integrity")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_inventory(
                root,
                """
                schema_version = "agent-armory.equipment-stock.v1"

                [[equipment]]
                id = "example"
                name = "Example Equipment"
                summary = "Demonstrates stock inventory validation."
                promotion_state = "published"
                delivery_compliance = "pending"
                shop_card = "docs/equipment/shop-cards/example.md"
                inspection_test_plan = "docs/equipment/inspection-test-plans/example.md"
                """,
            )
            self.write_inventory_view(
                root,
                """
                # Stocked Equipment Inventory

                ## Stock Authority

                [`inventory/equipment.toml`](../../inventory/equipment.toml)
                uses schema `agent-armory.equipment-stock.v1`.

                ## Stock Records

                - `example` - Example Equipment - `pending` -
                  [shop card](../../docs/equipment/shop-cards/example.md) -
                  [ITP](../../docs/equipment/inspection-test-plans/example.md)

                ## Shop Cards

                [Shop-card index](shop-cards/README.md)

                ## Inspection and Test Plans

                [ITP index](inspection-test-plans/README.md)
                """,
            )

            results = validator.validate_published_equipment_inventory_view(root)

        self.assertEqual(
            results,
            [
                CheckResult(
                    "published_equipment_inventory_view:projection",
                    True,
                    "inventory view matches stock inventory",
                    "docs/equipment/inventory.md",
                )
            ],
        )

    def test_validate_published_equipment_inventory_view_rejects_non_empty_record_missing_field(self):
        validator = importlib.import_module("tools.validate_armory_integrity")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_inventory(
                root,
                """
                schema_version = "agent-armory.equipment-stock.v1"

                [[equipment]]
                id = "example"
                name = "Example Equipment"
                summary = "Demonstrates stock inventory validation."
                promotion_state = "published"
                delivery_compliance = "pending"
                shop_card = "docs/equipment/shop-cards/example.md"
                inspection_test_plan = "docs/equipment/inspection-test-plans/example.md"
                """,
            )
            self.write_inventory_view(
                root,
                """
                # Stocked Equipment Inventory

                ## Stock Authority

                [`inventory/equipment.toml`](../../inventory/equipment.toml)
                uses schema `agent-armory.equipment-stock.v1`.

                ## Stock Records

                - `example` - Example Equipment - `pending`

                ## Shop Cards

                [Shop-card index](shop-cards/README.md)
                """,
            )

            results = validator.validate_published_equipment_inventory_view(root)

        self.assertIn(
            CheckResult(
                "published_equipment_inventory_view:record:example",
                False,
                "stock record bullet must include id, name, delivery_compliance, shop_card, and inspection_test_plan",
                "docs/equipment/inventory.md",
            ),
            results,
        )

    def test_validate_published_equipment_inventory_view_rejects_stock_record_bullet_missing_itp(self):
        validator = importlib.import_module("tools.validate_armory_integrity")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_inventory(
                root,
                """
                schema_version = "agent-armory.equipment-stock.v1"

                [[equipment]]
                id = "example"
                name = "Example Equipment"
                summary = "Demonstrates stock inventory validation."
                promotion_state = "published"
                delivery_compliance = "pending"
                shop_card = "docs/equipment/shop-cards/example.md"
                inspection_test_plan = "docs/equipment/inspection-test-plans/example.md"
                """,
            )
            self.write_inventory_view(
                root,
                """
                # Stocked Equipment Inventory

                ## Stock Authority

                [`inventory/equipment.toml`](../../inventory/equipment.toml)
                uses schema `agent-armory.equipment-stock.v1`.

                ## Stock Records

                - `example` - Example Equipment - `pending` -
                  [shop card](../../docs/equipment/shop-cards/example.md)

                ## Shop Cards

                [Shop-card index](shop-cards/README.md)
                """,
            )

            results = validator.validate_published_equipment_inventory_view(root)

        self.assertIn(
            CheckResult(
                "published_equipment_inventory_view:record:example",
                False,
                "stock record bullet must include id, name, delivery_compliance, shop_card, and inspection_test_plan",
                "docs/equipment/inventory.md",
            ),
            results,
        )

    def test_validate_published_equipment_inventory_view_does_not_count_paragraph_after_bullet(self):
        validator = importlib.import_module("tools.validate_armory_integrity")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_inventory(
                root,
                """
                schema_version = "agent-armory.equipment-stock.v1"

                [[equipment]]
                id = "example"
                name = "Example Equipment"
                summary = "Demonstrates stock inventory validation."
                promotion_state = "published"
                delivery_compliance = "pending"
                shop_card = "docs/equipment/shop-cards/example.md"
                inspection_test_plan = "docs/equipment/inspection-test-plans/example.md"
                """,
            )
            self.write_inventory_view(
                root,
                """
                # Stocked Equipment Inventory

                ## Stock Authority

                [`inventory/equipment.toml`](../../inventory/equipment.toml)
                uses schema `agent-armory.equipment-stock.v1`.

                ## Stock Records

                - `example` - Example Equipment - `pending`

                The shop-card path is docs/equipment/shop-cards/example.md.

                ## Shop Cards

                [Shop-card index](shop-cards/README.md)
                """,
            )

            results = validator.validate_published_equipment_inventory_view(root)

        self.assertIn(
            CheckResult(
                "published_equipment_inventory_view:record:example",
                False,
                "stock record bullet must include id, name, delivery_compliance, shop_card, and inspection_test_plan",
                "docs/equipment/inventory.md",
            ),
            results,
        )

    def test_validate_published_equipment_inventory_view_rejects_substring_only_stock_record_bullet(self):
        validator = importlib.import_module("tools.validate_armory_integrity")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_inventory(
                root,
                """
                schema_version = "agent-armory.equipment-stock.v1"

                [[equipment]]
                id = "kit"
                name = "Kit"
                summary = "Demonstrates stock inventory validation."
                promotion_state = "published"
                delivery_compliance = "pending"
                shop_card = "docs/equipment/shop-cards/kit.md"
                inspection_test_plan = "docs/equipment/inspection-test-plans/kit.md"
                """,
            )
            self.write_inventory_view(
                root,
                """
                # Stocked Equipment Inventory

                ## Stock Authority

                [`inventory/equipment.toml`](../../inventory/equipment.toml)
                uses schema `agent-armory.equipment-stock.v1`.

                ## Stock Records

                - `toolkit` - Kitten - `pendingly` -
                  [shop card](docs/equipment/shop-cards/kit.md.bak)

                ## Shop Cards

                [Shop-card index](shop-cards/README.md)
                """,
            )

            results = validator.validate_published_equipment_inventory_view(root)

        self.assertIn(
            CheckResult(
                name="published_equipment_inventory_view:record:kit",
                ok=False,
                detail=(
                    "stock record bullet must include id, name, delivery_compliance, "
                    "shop_card, and inspection_test_plan"
                ),
                path="docs/equipment/inventory.md",
            ),
            results,
        )

    def test_validate_published_equipment_inventory_routing_requires_reader_routes(self):
        validator = importlib.import_module("tools.validate_armory_integrity")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_routing_docs(root, docs_link=False)

            results = validator.validate_published_equipment_inventory_routing(root)

        self.assertIn(
            CheckResult(
                "published_equipment_inventory_view:routing:docs/README.md",
                False,
                "missing inventory view route",
                "docs/README.md",
            ),
            results,
        )

    def test_run_requires_published_equipment_delivery_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = run(root)

        for relative_path in [
            "docs/equipment-delivery.md",
            "docs/equipment/inventory.md",
            "docs/equipment/inspection-test-plans/README.md",
            "docs/equipment/shop-cards/README.md",
            "inventory/equipment.toml",
            "templates/equipment-inspection-test-plan.md",
            "templates/equipment-shop-card.md",
            "templates/equipment-stock-record.toml",
        ]:
            self.assertIn(
                CheckResult(f"required_path:{relative_path}", False, "missing", relative_path),
                results,
            )


class ExampleValidationTests(unittest.TestCase):
    required_example_paths = [
        "examples/pr-review/capability-card.md",
        "examples/pr-review/interface-decision-record.md",
        "examples/pr-review/projected-components.md",
        "examples/docs-research/capability-card.md",
        "examples/docs-research/interface-decision-record.md",
        "examples/docs-research/projected-components.md",
        "examples/observability-investigation/capability-card.md",
        "examples/observability-investigation/interface-decision-record.md",
        "examples/observability-investigation/projected-components.md",
    ]

    def write_example(self, root: Path, example_id: str, overrides: dict[str, str] | None = None) -> None:
        files = {
            "capability-card.md": """\
                # Capability Card: Example capability

                Status: Forge Example
                Promotion state: example

                ## Vision alignment

                This example shows how a Forge capability supports `docs/vision.md`.

                This Forge Example is not Published Agent Equipment and is not installable.
                Trace: capability card -> [interface decision record](interface-decision-record.md) -> projected components.
                """,
            "interface-decision-record.md": """\
                # Interface Decision Record: Example capability

                Status: Forge Example
                Promotion state: example

                ## Vision alignment

                This example records why the interface keeps the Armory experience reliable.

                This Forge Example is not Published Agent Equipment and is not installable.
                Trace: [capability card](capability-card.md) -> interface decision record -> [projected components](projected-components.md).
                """,
            "projected-components.md": """\
                # Projected Components: Example capability

                Status: Forge Example
                Promotion state: example

                This Forge Example is not Published Agent Equipment and is not installable.
                Trace: [capability card](capability-card.md) -> [interface decision record](interface-decision-record.md) -> projected components.
                """,
        }
        files.update(overrides or {})
        for file_name, content in files.items():
            path = root / "examples" / example_id / file_name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")

    def write_all_examples(self, root: Path, overrides: dict[str, dict[str, str]] | None = None) -> None:
        for example_id in ["pr-review", "docs-research", "observability-investigation"]:
            self.write_example(root, example_id, (overrides or {}).get(example_id))

    def test_run_requires_all_example_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = run(root)

        for relative_path in self.required_example_paths:
            self.assertIn(
                CheckResult(f"required_path:{relative_path}", False, "missing", relative_path),
                results,
            )

    def test_validate_examples_accepts_complete_examples(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_examples(root)

            results = validate_examples(root)

        self.assertTrue(all(result.ok for result in results), results)

    def test_validate_examples_requires_framework_example_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_examples(
                root,
                {
                    "pr-review": {
                        "capability-card.md": """\
                            # Capability Card: PR review

                            Promotion state: example

                            This Forge Example is not Published Agent Equipment and is not installable.
                            Trace: capability card -> [interface decision record](interface-decision-record.md) -> projected components.
                            """
                    }
                },
            )

            results = validate_examples(root)

        self.assertIn(
            CheckResult(
                "example:status:examples/pr-review/capability-card.md",
                False,
                "missing Status: Forge Example",
                "examples/pr-review/capability-card.md",
            ),
            results,
        )

    def test_validate_examples_requires_promotion_state_example(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_examples(
                root,
                {
                    "docs-research": {
                        "interface-decision-record.md": """\
                            # Interface Decision Record: Docs research

                            Status: Forge Example

                            This Forge Example is not Published Agent Equipment and is not installable.
                            Trace: [capability card](capability-card.md) -> interface decision record -> [projected components](projected-components.md).
                            """
                    }
                },
            )

            results = validate_examples(root)

        self.assertIn(
            CheckResult(
                "example:promotion:examples/docs-research/interface-decision-record.md",
                False,
                "missing Promotion state: example",
                "examples/docs-research/interface-decision-record.md",
            ),
            results,
        )

    def test_validate_examples_requires_non_published_boundary(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_examples(
                root,
                {
                    "observability-investigation": {
                        "projected-components.md": """\
                            # Projected Components: Observability investigation

                            Status: Forge Example
                            Promotion state: example

                            Trace: [capability card](capability-card.md) -> [interface decision record](interface-decision-record.md) -> projected components.
                            """
                    }
                },
            )

            results = validate_examples(root)

        self.assertIn(
            CheckResult(
                "example:boundary:examples/observability-investigation/projected-components.md",
                False,
                "missing non-published boundary",
                "examples/observability-investigation/projected-components.md",
            ),
            results,
        )

    def test_validate_examples_requires_non_installable_boundary(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_examples(
                root,
                {
                    "docs-research": {
                        "projected-components.md": """\
                            # Projected Components: Documentation research

                            Status: Forge Example
                            Promotion state: example

                            This Forge Example is not Published Agent Equipment.
                            Trace: [capability card](capability-card.md) -> [interface decision record](interface-decision-record.md) -> projected components.
                            """
                    }
                },
            )

            results = validate_examples(root)

        self.assertIn(
            CheckResult(
                "example:boundary:examples/docs-research/projected-components.md:installable",
                False,
                "missing non-installable boundary",
                "examples/docs-research/projected-components.md",
            ),
            results,
        )

    def test_validate_examples_requires_trace_links(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_examples(
                root,
                {
                    "pr-review": {
                        "interface-decision-record.md": """\
                            # Interface Decision Record: PR review

                            Status: Forge Example
                            Promotion state: example

                            This Forge Example is not Published Agent Equipment and is not installable.
                            Trace: capability card -> interface decision record -> projected components.
                            """
                    }
                },
            )

            results = validate_examples(root)

        self.assertIn(
            CheckResult(
                "example:trace:examples/pr-review/interface-decision-record.md:capability-card.md",
                False,
                "missing trace link: capability-card.md",
                "examples/pr-review/interface-decision-record.md",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "example:trace:examples/pr-review/interface-decision-record.md:projected-components.md",
                False,
                "missing trace link: projected-components.md",
                "examples/pr-review/interface-decision-record.md",
            ),
            results,
        )

    def test_validate_examples_requires_capability_card_vision_alignment(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_examples(
                root,
                {
                    "pr-review": {
                        "capability-card.md": """\
                            # Capability Card: PR review

                            Status: Forge Example
                            Promotion state: example

                            This Forge Example is not Published Agent Equipment and is not installable.
                            Trace: capability card -> [interface decision record](interface-decision-record.md) -> projected components.
                            """
                    }
                },
            )

            results = validate_examples(root)

        self.assertIn(
            CheckResult(
                name="example:section:examples/pr-review/capability-card.md:Vision alignment",
                ok=False,
                detail="missing section: Vision alignment",
                path="examples/pr-review/capability-card.md",
            ),
            results,
        )

    def test_validate_examples_requires_interface_decision_vision_alignment(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_examples(
                root,
                {
                    "docs-research": {
                        "interface-decision-record.md": """\
                            # Interface Decision Record: Docs research

                            Status: Forge Example
                            Promotion state: example

                            This Forge Example is not Published Agent Equipment and is not installable.
                            Trace: [capability card](capability-card.md) -> interface decision record -> [projected components](projected-components.md).
                            """
                    }
                },
            )

            results = validate_examples(root)

        self.assertIn(
            CheckResult(
                name="example:section:examples/docs-research/interface-decision-record.md:Vision alignment",
                ok=False,
                detail="missing section: Vision alignment",
                path="examples/docs-research/interface-decision-record.md",
            ),
            results,
        )

    def test_validate_examples_rejects_published_or_production_claims(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_examples(
                root,
                {
                    "docs-research": {
                        "capability-card.md": """\
                            # Capability Card: Docs research

                            Status: Forge Example
                            Promotion state: example

                            This Forge Example is not Published Agent Equipment and is not installable.
                            This example is production-ready.
                            Trace: capability card -> [interface decision record](interface-decision-record.md) -> projected components.
                            """
                    }
                },
            )

            results = validate_examples(root)

        self.assertIn(
            CheckResult(
                "example:claim:examples/docs-research/capability-card.md:production-ready",
                False,
                "forbidden readiness claim: production-ready",
                "examples/docs-research/capability-card.md",
            ),
            results,
        )

    def test_validate_examples_rejects_installability_claims(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_examples(
                root,
                {
                    "observability-investigation": {
                        "interface-decision-record.md": """\
                            # Interface Decision Record: Observability investigation

                            Status: Forge Example
                            Promotion state: example

                            This Forge Example is not Published Agent Equipment and is not installable.
                            This example is installable.
                            Trace: [capability card](capability-card.md) -> interface decision record -> [projected components](projected-components.md).
                            """
                    }
                },
            )

            results = validate_examples(root)

        self.assertIn(
            CheckResult(
                "example:claim:examples/observability-investigation/interface-decision-record.md:is installable",
                False,
                "forbidden readiness claim: is installable",
                "examples/observability-investigation/interface-decision-record.md",
            ),
            results,
        )


class IssueTrackerOpsPolicyConfigValidationTests(unittest.TestCase):
    config_path = "config/agent-equipment.toml"
    issue_tracker_doc = "docs/agents/issue-tracker.md"
    triage_labels_doc = "docs/agents/triage-labels.md"

    def write_file(self, root: Path, relative_path: str, content: str) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")

    def valid_policy_config(self, *, extra_axis: str = "") -> str:
        return f"""
            [agent_equipment_config.layer]
            name = "repository policy"
            category = "committed durable config"

            [agent_equipment_config.authority]
            repo-maintainers = "usable"

            [agent_equipment_config.fragment_versions]
            issue_tracker_ops = 3

            [agent_equipment_config.policy.issue_tracker_ops.mode]
            required_for = "always"
            non_overridable = true
            authority = "repo-maintainers"

            [issue_tracker_ops]
            mode = "dry-run"
            external_disclosure = "blocked"
            policy_profile_status = "authoritative"

            [[issue_tracker_ops.label_axes]]
            name = "category"
            cardinality = "exactly_one"
            description = "coarse issue category role"
            labels = ["bug", "enhancement"]

            [[issue_tracker_ops.label_axes]]
            name = "state"
            cardinality = "exactly_one"
            description = "mutually exclusive triage state role"
            labels = ["needs-triage", "ready-for-agent"]

            {extra_axis}

            [[issue_tracker_ops.legacy_policy_surfaces]]
            path = "docs/agents/issue-tracker.md"
            fate = "compatibility layer"
            authority = "config/agent-equipment.toml"

            [[issue_tracker_ops.legacy_policy_surfaces]]
            path = "docs/agents/triage-labels.md"
            fate = "compatibility layer"
            authority = "config/agent-equipment.toml"
        """

    def valid_issue_tracker_doc(self) -> str:
        return """
            # Issue Tracker

            Preferred policy authority: `config/agent-equipment.toml`.

            This document is a compatibility layer for active dependents.
        """

    def valid_triage_labels_doc(self, extra_text: str = "") -> str:
        return f"""
            # Triage Labels

            Preferred policy authority: `config/agent-equipment.toml`.

            This document is a compatibility layer for active dependents.

            Labels: bug, enhancement, needs-triage, ready-for-agent.

            {extra_text}
        """

    def write_valid_policy_surface(self, root: Path, *, config: str | None = None, triage_doc: str | None = None) -> None:
        self.write_file(root, self.config_path, config or self.valid_policy_config())
        self.write_file(root, self.issue_tracker_doc, self.valid_issue_tracker_doc())
        self.write_file(root, self.triage_labels_doc, triage_doc or self.valid_triage_labels_doc())

    def test_validate_issue_tracker_ops_policy_config_requires_committed_layer(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = validate_issue_tracker_ops_policy_config(root)

        self.assertIn(
            CheckResult(
                "issue_ops_policy_config:path:config/agent-equipment.toml",
                False,
                "missing",
                "config/agent-equipment.toml",
            ),
            results,
        )

    def test_validate_issue_tracker_ops_policy_config_accepts_valid_layer_and_docs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_policy_surface(root)

            results = validate_issue_tracker_ops_policy_config(root)

        self.assertTrue(all(result.ok for result in results), results)

    def test_validate_issue_tracker_ops_policy_config_requires_compatibility_doc_references(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_policy_surface(
                root,
                triage_doc="""
                    # Triage Labels

                    Labels: bug, enhancement, needs-triage, ready-for-agent.
                """,
            )

            results = validate_issue_tracker_ops_policy_config(root)

        self.assertIn(
            CheckResult(
                "issue_ops_policy_config:doc:docs/agents/triage-labels.md:authority",
                False,
                "missing Config compatibility reference",
                "docs/agents/triage-labels.md",
            ),
            results,
        )

    def test_validate_issue_tracker_ops_policy_config_detects_label_drift(self):
        extra_axis = """
            [[issue_tracker_ops.label_axes]]
            name = "priority"
            cardinality = "exactly_one"
            description = "configured priority policy"
            labels = ["priority:high", "priority:low"]
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_policy_surface(
                root,
                config=self.valid_policy_config(extra_axis=extra_axis),
                triage_doc=self.valid_triage_labels_doc(extra_text="priority:high"),
            )

            results = validate_issue_tracker_ops_policy_config(root)

        self.assertIn(
            CheckResult(
                "issue_ops_policy_config:labels:docs/agents/triage-labels.md:priority:low",
                False,
                "missing configured label: priority:low",
                "docs/agents/triage-labels.md",
            ),
            results,
        )


class IssueOpsWorkflowExecutorValidationTests(unittest.TestCase):
    skill_path = "skills/issue-ops-workflow-executor/SKILL.md"
    profile_path = "agents/issue-ops-workflow-executor/profile.toml"

    def write_file(self, root: Path, relative_path: str, content: str) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")

    def workflow_ids(self) -> list[str]:
        return sorted(issue_tracker_core.workflow_definitions_by_id())

    def valid_skill(self) -> str:
        return """
            ---
            name: issue-ops-workflow-executor
            description: Use when executing Issue Ops advisory workflows for issue review, repair, enrichment, refactor, assignment, duplicate review, selection, session pickup, or issue-set orchestration.
            ---

            # Issue Ops Workflow Executor

            Status: Implemented candidate

            ## Use when

            Use this skill for Issue Ops advisory workflow execution.

            ## Procedure

            1. Run or consume `describe-workflows`.
            2. Run `plan-workflow --adapter github-issues-baseline --workflow <workflow-id>`.
            3. Gather the workflow's required context.
            4. Emit the workflow's configured output sections.
            5. List candidate writes only as deterministic Issue Ops operation plans or dry-run command shapes.

            ## Safety

            Do not use direct `gh` writes, direct GitHub MCP writes, or tracker mutation outside Issue Ops dry-run/write gates.
        """

    def valid_profile(self, workflow_ids: list[str] | None = None, deny: list[str] | None = None) -> str:
        workflow_id_items = ", ".join(f'"{workflow_id}"' for workflow_id in (workflow_ids or self.workflow_ids()))
        deny_items = ", ".join(
            f'"{item}"'
            for item in (
                deny
                or [
                    "direct tracker mutation",
                    "direct gh writes",
                    "direct GitHub MCP writes",
                    "user-global policy mutation",
                    "external disclosure without approval",
                ]
            )
        )
        return f"""
            [identity]
            name = "issue-ops-workflow-executor"
            description = "Prepare advisory Issue Ops workflow recommendations."
            mission = "Prepare Issue Ops workflow recommendations without direct tracker mutation."

            [tools]
            allow = ["describe-workflows", "plan-workflow", "read/context gathering"]
            deny = [{deny_items}]

            [permissions]
            mode = "read-only"
            approval_required_for = ["external disclosure", "network write", "tracker mutation", "user-global policy mutation"]

            [model]
            preference = "inherit"
            reasoning_effort = "inherit"

            [config]
            default_adapter = "github-issues-baseline"
            workflow_ids = [{workflow_id_items}]

            [output]
            contract = "Return workflow output sections, candidate operation plans, unresolved judgment, and dry-run command shapes."
            format = "structured-report"
        """

    def write_valid_executor(self, root: Path, *, profile: str | None = None) -> None:
        self.write_file(root, self.skill_path, self.valid_skill())
        self.write_file(root, self.profile_path, profile or self.valid_profile())

    def executor_results(self, results: list[CheckResult]) -> list[CheckResult]:
        return [result for result in results if result.name.startswith("issue_ops_workflow_executor:")]

    def test_validate_issue_ops_workflow_executor_requires_skill_and_profile(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = self.executor_results(run(root))

        self.assertIn(
            CheckResult(
                "issue_ops_workflow_executor:path:skills/issue-ops-workflow-executor/SKILL.md",
                False,
                "missing",
                "skills/issue-ops-workflow-executor/SKILL.md",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "issue_ops_workflow_executor:path:agents/issue-ops-workflow-executor/profile.toml",
                False,
                "missing",
                "agents/issue-ops-workflow-executor/profile.toml",
            ),
            results,
        )

    def test_validate_issue_ops_workflow_executor_accepts_valid_skill_and_profile(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_executor(root)

            results = self.executor_results(run(root))

        self.assertNotEqual(results, [])
        self.assertTrue(all(result.ok for result in results), results)

    def test_validate_issue_ops_workflow_executor_requires_workflow_id_parity(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_executor(root, profile=self.valid_profile(workflow_ids=["issue.review"]))

            results = self.executor_results(run(root))

        self.assertIn(
            CheckResult(
                "issue_ops_workflow_executor:profile:workflow_ids",
                False,
                "must match issue_tracker_core.workflow_definitions_by_id()",
                "agents/issue-ops-workflow-executor/profile.toml",
            ),
            results,
        )

    def test_validate_issue_ops_workflow_executor_requires_mutation_denies(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_valid_executor(root, profile=self.valid_profile(deny=["direct gh writes"]))

            results = self.executor_results(run(root))

        self.assertIn(
            CheckResult(
                "issue_ops_workflow_executor:profile:deny:direct tracker mutation",
                False,
                "missing deny entry: direct tracker mutation",
                "agents/issue-ops-workflow-executor/profile.toml",
            ),
            results,
        )

    def test_validate_issue_ops_workflow_executor_requires_valid_profile_toml(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_file(root, self.skill_path, self.valid_skill())
            self.write_file(root, self.profile_path, "[identity\nname = 'broken'\n")

            results = self.executor_results(run(root))

        self.assertTrue(
            any(
                result.name
                == "issue_ops_workflow_executor:profile:toml:agents/issue-ops-workflow-executor/profile.toml"
                and not result.ok
                for result in results
            ),
            results,
        )
        self.assertEqual(1, len(results), results)

    def test_validate_issue_ops_workflow_executor_requires_skill_workflow_contract_terms(self):
        skill_without_workflow_contract = self.valid_skill().replace(
            "`describe-workflows`",
            "`describe-core`",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_file(root, self.skill_path, skill_without_workflow_contract)
            self.write_file(root, self.profile_path, self.valid_profile())

            results = self.executor_results(run(root))

        self.assertIn(
            CheckResult(
                "issue_ops_workflow_executor:skill:text:describe-workflows",
                False,
                "missing text: describe-workflows",
                "skills/issue-ops-workflow-executor/SKILL.md",
            ),
            results,
        )

    def test_validate_issue_ops_workflow_executor_requires_profile_planning_contract_terms(self):
        profile_without_plan_or_dry_run = self.valid_profile().replace(
            '"plan-workflow", ',
            "",
        ).replace(
            " and dry-run command shapes",
            "",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_file(root, self.skill_path, self.valid_skill())
            self.write_file(root, self.profile_path, profile_without_plan_or_dry_run)

            results = self.executor_results(run(root))

        self.assertIn(
            CheckResult(
                "issue_ops_workflow_executor:profile:allow:plan-workflow",
                False,
                "missing allow entry: plan-workflow",
                "agents/issue-ops-workflow-executor/profile.toml",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "issue_ops_workflow_executor:profile:output:dry-run command shapes",
                False,
                "missing output contract text: dry-run command shapes",
                "agents/issue-ops-workflow-executor/profile.toml",
            ),
            results,
        )

    def test_validate_issue_ops_workflow_executor_rejects_unexpected_profile_allow_entries(self):
        profile_with_extra_allow = self.valid_profile().replace(
            '"read/context gathering"]',
            '"read/context gathering", "tracker write bypass"]',
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_file(root, self.skill_path, self.valid_skill())
            self.write_file(root, self.profile_path, profile_with_extra_allow)

            results = self.executor_results(run(root))

        self.assertIn(
            CheckResult(
                name="issue_ops_workflow_executor:profile:allow:unexpected",
                ok=False,
                detail="unexpected allow entries: tracker write bypass",
                path="agents/issue-ops-workflow-executor/profile.toml",
            ),
            results,
        )

    def test_validate_issue_ops_workflow_executor_requires_frontmatter_name(self):
        skill_without_frontmatter_name = self.valid_skill().replace(
            "name: issue-ops-workflow-executor",
            "summary: issue-ops-workflow-executor",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_file(root, self.skill_path, skill_without_frontmatter_name)
            self.write_file(root, self.profile_path, self.valid_profile())

            results = self.executor_results(run(root))

        self.assertIn(
            CheckResult(
                "issue_ops_workflow_executor:skill:frontmatter:name",
                False,
                "frontmatter name must be issue-ops-workflow-executor",
                "skills/issue-ops-workflow-executor/SKILL.md",
            ),
            results,
        )


class SpecValidationTests(unittest.TestCase):
    config_prd_path = "docs/prd/agent-equipment-config.md"
    existing_equipment_onboarding_prd_path = "docs/prd/existing-equipment-onboarding.md"
    issue_tracker_ops_config_profile_path = "specs/issue-tracker-ops/config-profile-and-onboarding.md"
    config_bundle_paths = (
        "specs/agent-equipment-config/README.md",
        "specs/agent-equipment-config/capability-card.md",
        "specs/agent-equipment-config/interface-decision-record.md",
        "specs/agent-equipment-config/security-control-classification.md",
        "specs/agent-equipment-config/mcp-tools.md",
        "specs/agent-equipment-config/edit-boundaries.md",
        "specs/agent-equipment-config/authoring-plan-apply-model.md",
        "specs/agent-equipment-config/pressure-scenarios.md",
        "specs/agent-equipment-config/validation-plan.md",
        "specs/agent-equipment-config/closeout-evidence-plan.md",
    )
    required_spec_paths = (
        *config_bundle_paths,
        issue_tracker_ops_config_profile_path,
        "specs/repo-ops.md",
        "specs/periodic-actions.md",
        "specs/harness-capability-refresh.md",
    )

    def write_spec(self, root: Path, relative_path: str, content: str) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")

    def valid_spec(self, title: str, extra: str) -> str:
        extra_text = textwrap.dedent(extra).strip()
        return "\n".join(
            [
                f"# {title}",
                "",
                "Status: Equipment Blueprint",
                "Promotion state: specified",
                "",
                "This spec describes desired behavior only. It does not implement Agent Equipment.",
                "",
                "## Purpose",
                "",
                "Content.",
                "",
                "## User stories",
                "",
                "Content.",
                "",
                "## Acceptance criteria",
                "",
                "Content.",
                "",
                "## Harness projections",
                "",
                "- Codex",
                "- OpenClaw",
                "- Hermes Agent",
                "- Claude Code",
                "- Cursor",
                "- OpenCode",
                "",
                "## Non-goals",
                "",
                "Content.",
                "",
                extra_text,
                "",
            ]
        )

    def valid_issue_tracker_ops_config_profile(self) -> str:
        return textwrap.dedent(
            """\
            # Config Profile And Onboarding: Issue Tracker Ops

            Status: Equipment Blueprint
            Promotion state: planned

            This spec describes desired behavior only. It does not implement Agent Equipment.

            ## Purpose

            Issue Tracker Ops defines its progressive config profile without
            owning Agent Equipment Config.

            ## Progressive Enhancement Boundary

            Issue Tracker Ops can run session-scoped behavior without shared
            Config, serialize a plain handoff, and later promote that handoff
            into Agent Equipment Config.

            ## Plain Handoff And Session Behavior

            The plain handoff records mode, external disclosure, taxonomy,
            priority scales, workflow status semantics, readiness signals,
            WIP policy, stakeholder overrides, issue-set selection, dependency
            semantics, mutation safety, and adapter capability assumptions.

            ## Onboarding Flow

            Onboarding covers first-run, interruption, resume, restart,
            re-onboarding, incomplete sections, confidence, assumptions, and
            unavailable config-equipment status.

            ## Foreign Policy Surface Discovery And Migration Fates

            Discovery covers repo-local and user-global Foreign Policy Surface
            inputs. Migration fates include keep and establish compatibility,
            remove and ingest policy, remove and discard policy, ignore,
            defer for review, and split.
            `ignore` leaves a surface outside the migration scope. `defer for
            review` records a blocking or judgment-heavy disposition. `split`
            separates facets that need different fates.

            ## Compatibility Classification

            Compatibility classification determines whether indirection,
            generation, adapter behavior, or a mixed strategy preserves a
            Foreign Policy Compatibility Surface.

            ## Machine-Visible Output

            Output includes Config Safety Status, safety status, assumptions,
            incomplete sections, confidence, policy authority evidence,
            conflict reporting, and effective next-work explanation.

            ## CLI And MCP Parity

            CLI and MCP parity expose the same typed contracts for dry-run
            plans, validation, onboarding, migration preview, migration apply,
            conflict reports, and adapter calls.

            ## Security And Safety

            User-global mutation requires explicit approval, unsafe writes
            fail closed, and external disclosure remains blocked unless policy
            allows it.

            ## Validation And Closeout

            Validation covers plain handoff ingestion, Config promotion,
            onboarding states, migration fates, compatibility classification,
            conflict reports, CLI and MCP parity, and tracker projection.

            ## Non-goals

            This design does not implement runtime onboarding, GitHub Projects,
            policy-doc migration, Config authoring mechanics, or final
            publication.
            """
        )

    def valid_config_bundle(self) -> dict[str, str]:
        common_header = textwrap.dedent(
            """\
            Status: Equipment Blueprint
            Promotion state: planned

            This Equipment Design Bundle describes desired behavior only. It does not implement Agent Equipment.
            """
        ).strip()

        def bundle_doc(title: str, body: str) -> str:
            return f"# {title}\n\n{common_header}\n\n{textwrap.dedent(body).strip()}\n"

        return {
            "specs/agent-equipment-config/README.md": bundle_doc(
                "Agent Equipment Config",
                """\
                ## Bundle map

                The bundle links the capability card, interface decision record,
                security/control classification, pressure scenarios, validation
                plan, and closeout evidence plan for issue #23.

                ## V0 scope

                Agent Equipment Config v0 defines the explainable effective-config
                contract for typed schemas, schema fragments, layered config,
                config-diff output, Layer Precedence, Policy Authority, Config Safety Status,
                semantic validators, conflict diagnostics, migrations, secret references,
                consumer action decision evidence, MCP parity, progressive fallback,
                session-scoped behavior, and plain equipment-specific config handoff
                promotion.

                ## Harness projections

                Required harnesses: Codex, OpenClaw, Hermes Agent, Claude Code,
                Cursor, OpenCode.
                """,
            ),
            "specs/agent-equipment-config/capability-card.md": bundle_doc(
                "Capability Card: Agent Equipment Config",
                """\
                ## Purpose

                Shared, layerable, composable, adaptable, and enforceable
                configuration across Agent Equipment.

                ## Vision alignment

                Config keeps deterministic policy, local choices, schema
                validation, and effective-config explanation out of hidden model
                preference.

                ## Hard rules

                Mutation-capable behavior fails closed unless the effective
                configuration is usable.
                """,
            ),
            "specs/agent-equipment-config/interface-decision-record.md": bundle_doc(
                "Interface Decision Record: Agent Equipment Config",
                """\
                ## Requirement

                Agent Equipment Config needs typed schema fragment registration,
                deterministic merge behavior, config-diff output, and
                effective-config output.

                ## Vision alignment

                The equipment projects deterministic configuration concerns into
                typed data, scripts, tools, hooks, approvals, and config rather
                than a single skill.

                ## Decision

                Use TOML for human-authored config and JSON-compatible objects
                for schemas, diagnostics, audit records, and tool output.
                """,
            ),
            "specs/agent-equipment-config/security-control-classification.md": bundle_doc(
                "Security and Control Classification: Agent Equipment Config",
                """\
                ## Scope

                This classification covers the v0 contract, not a runtime engine.

                ## Controls

                Secret references do not store secret values. Non-overridable
                policy, untrusted config, local-only state, and mutation gates
                are represented in structured diagnostics. Policy Authority
                constrains later overrides and lower-authority layers.
                """,
            ),
            "specs/agent-equipment-config/mcp-tools.md": bundle_doc(
                "MCP Tools: Agent Equipment Config",
                """\
                ## Tool definition contract

                MCP parity tools expose typed input schemas, output schemas,
                read/write classification, auth source, side effects, approval
                requirements, mutation gates, and failure modes. The current
                stdio MCP server is tools/agent_equipment_config_mcp_server.py.

                ## Operation map

                config.resolve, config.validate, config.diff, onboard.config,
                migrate.config_preview, and migrate.config_apply mirror the
                fluent CLI/runtime slice.
                """,
            ),
            "specs/agent-equipment-config/edit-boundaries.md": bundle_doc(
                "Edit Boundaries: Agent Equipment Config",
                """\
                ## Purpose

                Edit boundaries name propose, patch, migrate, revise, and apply
                intents for Config source changes.

                ## Source ownership

                Committed durable config and local-only operator config are the
                writable categories for current migration apply. Generated,
                checkout-local, secret reference, and session sources are
                read-only for Config source writes.

                ## Refusal states

                Refusals name source category, trusted provenance, Policy
                Authority, Config Safety Status, validation, and secret
                boundary failures.
                """,
            ),
            "specs/agent-equipment-config/authoring-plan-apply-model.md": bundle_doc(
                "Authoring Plan/Apply Model: Agent Equipment Config",
                """\
                ## Purpose

                The authoring model defines non-migration Config source changes
                through deterministic JSON plan artifacts before any general
                source patching surface writes source Config.

                ## Plan surfaces

                config propose is target-agnostic. config patch creates a
                patch-layer plan for an eligible selected source. create-layer
                creates a new authored source plan. config apply accepts only
                reviewed plan artifacts.

                ## Apply boundary

                Plans preserve the source target, source category,
                precondition fingerprint, diff or create payload, authority
                evidence, validation result, virtual post-change effective Config
                status, audit preview, refusal codes,
                durability classification, and rollback stance. Apply is
                all-or-nothing for committed durable config and local-only
                operator config. Secret-reference pointer edits are allowed,
                while secret values and secret-provider mutation are refused.
                """,
            ),
            "specs/agent-equipment-config/pressure-scenarios.md": bundle_doc(
                "Pressure Scenarios: Agent Equipment Config",
                """\
                ## Issue Tracker Ops effective config

                Issue Tracker Ops is the primary pressure scenario for tracker
                write policy, priority selection, dependency feasibility,
                dry-run versus execute behavior, external disclosure, partial
                onboarding, and stale config.
                """,
            ),
            "specs/agent-equipment-config/validation-plan.md": bundle_doc(
                "Validation Plan: Agent Equipment Config",
                """\
                ## Deterministic checks

                python3.14 -m unittest tests.test_agent_equipment_config
                python3.14 -m unittest tests.test_agent_equipment_config_mcp_server
                Validation covers absent config equipment, partial config,
                conflicting layers, semantic validators, schema migration,
                session overrides, local-only overrides, committed config,
                multi-equipment composition, enforcement projection, secret
                references, and handoff ingestion.
                """,
            ),
            "specs/agent-equipment-config/closeout-evidence-plan.md": bundle_doc(
                "Closeout Evidence Plan: Agent Equipment Config",
                """\
                ## Evidence

                Closeout records validator results, config-diff and
                effective-config contract coverage, Issue Tracker Ops pressure
                scenario coverage, child issue projection, and security review
                disposition.
                """,
            ),
        }

    def write_all_specs(self, root: Path, overrides: dict[str, str] | None = None) -> None:
        specs = {
            self.issue_tracker_ops_config_profile_path: self.valid_issue_tracker_ops_config_profile(),
            "specs/repo-ops.md": self.valid_spec(
                "Repo Ops Spec",
                """\
                TOML config stores durable owner and runbook config.
                The config drives Agent behavior, hook behavior, and other configurable aspects.
                Settings use sensibly typed values.
                Autonomy levels: off, advisory, assisted, supervised, autonomous, forbidden.
                Safe defaults require advance approval before automation.
                Policy enforcement blocks violations when the harness supports blocking and otherwise uses advisory fallback.
                Fork Ops extends Repo Ops for fork-specific behavior.
                """,
            ),
            "specs/periodic-actions.md": self.valid_spec(
                "Periodic Actions Spec",
                """\
                First-session install prompt persists the choice locally.
                List, view, install, uninstall, trigger-now, and edit-period behavior are required.
                Mechanism selection order: native scheduled agent actions, active loop or heartbeat, suitable hook, inference-driven pre/post task check.
                Suggested storage: .repo-ops/.
                """,
            ),
            "specs/harness-capability-refresh.md": self.valid_spec(
                "Harness Capability Refresh Spec",
                """\
                Required harnesses: Codex, OpenClaw, Hermes Agent, Claude Code, Cursor, OpenCode.
                Required tracked fields: current version, checked-at timestamp, source URLs, supported Harness Component types, key affordances, known limitations, scheduling mechanisms, hook/event names, skill discovery paths, plugin interfaces, MCP behavior.
                Change-response issue behavior creates a high-priority issue with current version, previous version, capability affected, source evidence, expected Forge impact, and suggested Smith task.
                Fallback issue candidate path: issues/pending/high/.
                Weekly starting cadence.
                Prioritization order: security-relevant behavior, hook blocking semantics, permissions and sandboxing, scheduling, skill discovery/context behavior, plugin packaging, MCP tool exposure and context bloat.
                """,
            ),
        }
        specs.update(self.valid_config_bundle())
        specs.update(overrides or {})
        for relative_path, content in specs.items():
            self.write_spec(root, relative_path, content)

    def test_run_requires_all_spec_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            results = run(root)

        self.assertIn(
            CheckResult(f"required_path:{self.config_prd_path}", False, "missing", self.config_prd_path),
            results,
        )
        self.assertIn(
            CheckResult(
                f"required_path:{self.existing_equipment_onboarding_prd_path}",
                False,
                "missing",
                self.existing_equipment_onboarding_prd_path,
            ),
            results,
        )
        for relative_path in self.required_spec_paths:
            self.assertIn(
                CheckResult(f"required_path:{relative_path}", False, "missing", relative_path),
                results,
            )

    def test_validate_specs_accepts_complete_specs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_specs(root)

            results = validate_specs(root)

        self.assertTrue(all(result.ok for result in results), results)

    def test_validate_specs_requires_issue_tracker_ops_config_profile_sections(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_specs(
                root,
                {
                    self.issue_tracker_ops_config_profile_path: self.valid_issue_tracker_ops_config_profile().replace(
                        "## Onboarding Flow\n",
                        "",
                    )
                },
            )

            results = validate_specs(root)

        self.assertIn(
            CheckResult(
                f"spec:section:{self.issue_tracker_ops_config_profile_path}:Onboarding Flow",
                False,
                "missing section: Onboarding Flow",
                self.issue_tracker_ops_config_profile_path,
            ),
            results,
        )

    def test_validate_specs_requires_issue_tracker_ops_config_profile_terms(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_specs(
                root,
                {
                    self.issue_tracker_ops_config_profile_path: self.valid_issue_tracker_ops_config_profile()
                    .replace("CLI And MCP Parity", "Tool Surface Equivalence")
                    .replace("CLI and MCP parity", "tool surface equivalence")
                },
            )

            results = validate_specs(root)

        self.assertIn(
            CheckResult(
                f"spec:text:{self.issue_tracker_ops_config_profile_path}:CLI and MCP parity",
                False,
                "missing CLI and MCP parity",
                self.issue_tracker_ops_config_profile_path,
            ),
            results,
        )

    def test_validate_specs_requires_issue_tracker_ops_config_profile_fate_context(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_specs(
                root,
                {
                    self.issue_tracker_ops_config_profile_path: self.valid_issue_tracker_ops_config_profile().replace(
                        "`ignore` leaves a surface outside the migration scope.",
                        "The word ignore appears.",
                    )
                },
            )

            results = validate_specs(root)

        self.assertIn(
            CheckResult(
                f"spec:text:{self.issue_tracker_ops_config_profile_path}:`ignore` leaves a surface outside the migration scope",
                False,
                "missing `ignore` leaves a surface outside the migration scope",
                self.issue_tracker_ops_config_profile_path,
            ),
            results,
        )

    def test_validate_specs_allows_wrapped_issue_tracker_ops_config_profile_fixed_phrases(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_specs(
                root,
                {
                    self.issue_tracker_ops_config_profile_path: self.valid_issue_tracker_ops_config_profile()
                    .replace("Promotion state: planned", "Promotion state:\nplanned")
                    .replace("does not implement Agent Equipment", "does not implement Agent\nEquipment")
                },
            )

            results = validate_specs(root)

        self.assertNotIn(
            CheckResult(
                f"spec:promotion:{self.issue_tracker_ops_config_profile_path}",
                False,
                "missing Promotion state: planned",
                self.issue_tracker_ops_config_profile_path,
            ),
            results,
        )
        self.assertNotIn(
            CheckResult(
                f"spec:boundary:{self.issue_tracker_ops_config_profile_path}",
                False,
                "missing non-implementation boundary",
                self.issue_tracker_ops_config_profile_path,
            ),
            results,
        )

    def test_validate_specs_requires_promotion_state_specified(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_specs(
                root,
                {
                    "specs/repo-ops.md": self.valid_spec(
                        "Repo Ops Spec",
                        "TOML owner runbook autonomy levels safe defaults policy enforcement Codex OpenClaw Hermes Agent Claude Code Cursor OpenCode.",
                    ).replace("Promotion state: specified\n", "")
                },
            )

            results = validate_specs(root)

        self.assertIn(
            CheckResult(
                "spec:promotion:specs/repo-ops.md",
                False,
                "missing Promotion state: specified",
                "specs/repo-ops.md",
            ),
            results,
        )

    def test_validate_specs_requires_sections(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_specs(
                root,
                {
                    "specs/periodic-actions.md": """\
                        # Periodic Actions Spec

                        Status: Equipment Blueprint
                        Promotion state: specified

                        ## Purpose

                        Content.
                        """
                },
            )

            results = validate_specs(root)

        self.assertIn(
            CheckResult(
                "spec:section:specs/periodic-actions.md:Acceptance criteria",
                False,
                "missing section: Acceptance criteria",
                "specs/periodic-actions.md",
            ),
            results,
        )

    def test_validate_specs_requires_repo_ops_content(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_specs(
                root,
                {
                    "specs/repo-ops.md": self.valid_spec(
                        "Repo Ops Spec",
                        "Autonomy levels and safe defaults are required.",
                    )
                },
            )

            results = validate_specs(root)

        self.assertIn(
            CheckResult(
                "spec:text:specs/repo-ops.md:TOML",
                False,
                "missing TOML",
                "specs/repo-ops.md",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "spec:text:specs/repo-ops.md:policy enforcement",
                False,
                "missing policy enforcement",
                "specs/repo-ops.md",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "spec:text:specs/repo-ops.md:hook behavior",
                False,
                "missing hook behavior",
                "specs/repo-ops.md",
            ),
            results,
        )

    def test_validate_specs_requires_each_agent_equipment_config_required_term(self):
        required_terms = [
            "typed schemas",
            "schema fragments",
            "layered config",
            "effective-config",
            "config-diff",
            "Layer Precedence",
            "Policy Authority",
            "later overrides",
            "Config Safety Status",
            "semantic validators",
            "conflict diagnostics",
            "migrations",
            "session-scoped",
            "plain equipment-specific config handoff",
            "secret references",
            "consumer action decision",
            "stdio MCP server",
            "agent_equipment_config_mcp_server.py",
            "python3.14 -m unittest tests.test_agent_equipment_config_mcp_server",
            "progressive fallback",
            "Issue Tracker Ops",
            "config propose",
            "config apply",
            "patch-layer",
            "create-layer",
            "reviewed plan artifacts",
            "precondition fingerprint",
            "virtual post-change effective Config",
            "all-or-nothing",
            "durability classification",
            "rollback stance",
            "python3.14 -m unittest tests.test_agent_equipment_config",
            "policy",
            "Codex",
            "OpenClaw",
            "Hermes Agent",
            "Claude Code",
            "Cursor",
            "OpenCode",
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_specs(root)
            bundle_paths = [root / path for path in self.config_bundle_paths]
            for required_term in required_terms:
                original_texts = {path: path.read_text(encoding="utf-8") for path in bundle_paths}
                for path, original_text in original_texts.items():
                    mutated_text = original_text
                    for variant in {required_term, required_term[:1].upper() + required_term[1:]}:
                        mutated_text = mutated_text.replace(variant, "")
                    if required_term == "secret references":
                        mutated_text = mutated_text.replace("secret reference", "")
                    path.write_text(mutated_text, encoding="utf-8")
                with self.subTest(required_term=required_term):
                    results = validate_specs(root)
                    self.assertIn(
                        CheckResult(
                            name=f"spec:text:specs/agent-equipment-config:{required_term}",
                            ok=False,
                            detail=f"missing {required_term}",
                            path="specs/agent-equipment-config",
                        ),
                        results,
                    )
                for path, original_text in original_texts.items():
                    path.write_text(original_text, encoding="utf-8")

    def test_validate_specs_rejects_config_policy_authority_direction_conflict(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_specs(root)
            security_path = root / "specs/agent-equipment-config/security-control-classification.md"
            security_path.write_text(
                security_path.read_text(encoding="utf-8")
                + "\nPolicy Authority to lower-precedence layers.\n",
                encoding="utf-8",
            )

            results = validate_specs(root)

        self.assertIn(
            CheckResult(
                name="spec:text:specs/agent-equipment-config:forbidden:lower-precedence layers",
                ok=False,
                detail="forbidden lower-precedence layers",
                path="specs/agent-equipment-config",
            ),
            results,
        )

    def test_validate_specs_requires_periodic_actions_content(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_specs(
                root,
                {
                    "specs/periodic-actions.md": self.valid_spec(
                        "Periodic Actions Spec",
                        "First-session install prompt and .repo-ops/ storage are required.",
                    )
                },
            )

            results = validate_specs(root)

        self.assertIn(
            CheckResult(
                "spec:text:specs/periodic-actions.md:trigger-now",
                False,
                "missing trigger-now",
                "specs/periodic-actions.md",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "spec:text:specs/periodic-actions.md:mechanism selection order",
                False,
                "missing mechanism selection order",
                "specs/periodic-actions.md",
            ),
            results,
        )

    def test_validate_specs_requires_harness_refresh_content(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_specs(
                root,
                {
                    "specs/harness-capability-refresh.md": self.valid_spec(
                        "Harness Capability Refresh Spec",
                        "Required harnesses and tracked fields are required.",
                    )
                },
            )

            results = validate_specs(root)

        self.assertIn(
            CheckResult(
                "spec:text:specs/harness-capability-refresh.md:issues/pending/high/",
                False,
                "missing issues/pending/high/",
                "specs/harness-capability-refresh.md",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "spec:text:specs/harness-capability-refresh.md:weekly starting cadence",
                False,
                "missing weekly starting cadence",
                "specs/harness-capability-refresh.md",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "spec:text:specs/harness-capability-refresh.md:key affordances",
                False,
                "missing key affordances",
                "specs/harness-capability-refresh.md",
            ),
            results,
        )
        self.assertIn(
            CheckResult(
                "spec:text:specs/harness-capability-refresh.md:previous version",
                False,
                "missing previous version",
                "specs/harness-capability-refresh.md",
            ),
            results,
        )

    def test_validate_specs_requires_each_harness_refresh_field(self):
        required_terms = [
            "current version",
            "checked-at timestamp",
            "source URLs",
            "supported Harness Component types",
            "key affordances",
            "known limitations",
            "scheduling mechanisms",
            "hook/event names",
            "skill discovery paths",
            "plugin interfaces",
            "MCP behavior",
            "previous version",
            "capability affected",
            "source evidence",
            "expected Forge impact",
            "suggested Smith task",
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_specs(root)
            path = root / "specs/harness-capability-refresh.md"
            spec_text = path.read_text(encoding="utf-8")
            for required_term in required_terms:
                path.write_text(spec_text.replace(required_term, ""), encoding="utf-8")
                with self.subTest(required_term=required_term):
                    results = validate_specs(root)
                    self.assertIn(
                        CheckResult(
                            f"spec:text:specs/harness-capability-refresh.md:{required_term}",
                            False,
                            f"missing {required_term}",
                            "specs/harness-capability-refresh.md",
                        ),
                        results,
                    )

    def test_validate_specs_requires_non_implementation_boundary(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_specs(
                root,
                {
                    "specs/repo-ops.md": self.valid_spec(
                        "Repo Ops Spec",
                        "TOML owner runbook hook behavior sensibly typed values autonomy levels safe defaults policy enforcement Fork Ops Codex OpenClaw Hermes Agent Claude Code Cursor OpenCode.",
                    ).replace(
                        "This spec describes desired behavior only. It does not implement Agent Equipment.\n",
                        "This spec describes desired behavior only.\n",
                    )
                },
            )

            results = validate_specs(root)

        self.assertIn(
            CheckResult(
                "spec:boundary:specs/repo-ops.md",
                False,
                "missing non-implementation boundary",
                "specs/repo-ops.md",
            ),
            results,
        )

    def test_validate_specs_rejects_readiness_and_installability_claims(self):
        for forbidden_claim in ["production-ready", "is installable"]:
            with tempfile.TemporaryDirectory() as tmpdir:
                root = Path(tmpdir)
                self.write_all_specs(
                    root,
                    {
                        "specs/periodic-actions.md": self.valid_spec(
                            "Periodic Actions Spec",
                            f"""\
                            First-session install prompt persists the choice locally.
                            List, view, install, uninstall, trigger-now, and edit-period behavior are required.
                            Mechanism selection order: native scheduled agent actions, active loop or heartbeat, suitable hook, inference-driven pre/post task check.
                            Suggested storage: .repo-ops/.
                            This spec {forbidden_claim}.
                            """,
                        )
                    },
                )

                results = validate_specs(root)

            with self.subTest(forbidden_claim=forbidden_claim):
                self.assertIn(
                    CheckResult(
                        f"spec:claim:specs/periodic-actions.md:{forbidden_claim}",
                        False,
                        f"forbidden readiness claim: {forbidden_claim}",
                        "specs/periodic-actions.md",
                    ),
                    results,
                )

    def test_validate_specs_accepts_harness_specific_starting_points(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.write_all_specs(
                root,
                {
                    "specs/periodic-actions.md": self.valid_spec(
                        "Periodic Actions Spec",
                        """\
                        First-session install prompt persists the choice locally.
                        List, view, install, uninstall, trigger-now, and edit-period behavior are required.
                        Mechanism selection order: native scheduled agent actions, active loop or heartbeat, suitable hook, inference-driven pre/post task check.
                        Suggested storage: .repo-ops/.
                        """,
                    ).replace("## Harness projections", "## Harness-specific starting points")
                },
            )

            results = validate_specs(root)

        self.assertTrue(all(result.ok for result in results), results)


if __name__ == "__main__":
    unittest.main()
