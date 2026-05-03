import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "run-prompt-context-report.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "run_prompt_context_report", SCRIPT_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load run-prompt-context-report module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class RunPromptContextReportTests(unittest.TestCase):
    def test_prefers_current_python_when_tiktoken_is_available(self) -> None:
        module = load_module()

        with tempfile.TemporaryDirectory() as temporary_directory:
            venv_dir = Path(temporary_directory) / "venv"
            with mock.patch.object(
                module,
                "python_has_tiktoken",
                side_effect=lambda python: python == sys.executable,
            ):
                with mock.patch.object(
                    module, "create_or_repair_tokenizer_venv"
                ) as create_venv:
                    plan = module.choose_tokenizer_plan(venv_dir)

        self.assertEqual(plan.python_executable, sys.executable)
        self.assertFalse(plan.use_proxy)
        self.assertIsNone(plan.bootstrap_error)
        create_venv.assert_not_called()

    def test_uses_cached_venv_when_it_already_has_tiktoken(self) -> None:
        module = load_module()

        with tempfile.TemporaryDirectory() as temporary_directory:
            venv_dir = Path(temporary_directory) / "venv"
            venv_python = module.venv_python_path(venv_dir)
            venv_python.parent.mkdir(parents=True)
            venv_python.write_text("")

            def has_tiktoken(python: str) -> bool:
                return python == str(venv_python)

            with mock.patch.object(
                module, "python_has_tiktoken", side_effect=has_tiktoken
            ):
                with mock.patch.object(
                    module, "create_or_repair_tokenizer_venv"
                ) as create_venv:
                    plan = module.choose_tokenizer_plan(venv_dir)

        self.assertEqual(plan.python_executable, str(venv_python))
        self.assertFalse(plan.use_proxy)
        self.assertIsNone(plan.bootstrap_error)
        create_venv.assert_not_called()

    def test_creates_or_repairs_venv_when_no_working_tokenizer_exists(self) -> None:
        module = load_module()

        with tempfile.TemporaryDirectory() as temporary_directory:
            venv_dir = Path(temporary_directory) / "venv"
            venv_python = module.venv_python_path(venv_dir)

            def has_tiktoken(python: str) -> bool:
                return python == str(venv_python)

            with mock.patch.object(
                module, "python_has_tiktoken", side_effect=has_tiktoken
            ):
                with mock.patch.object(
                    module, "create_or_repair_tokenizer_venv", return_value=venv_python
                ) as create_venv:
                    plan = module.choose_tokenizer_plan(venv_dir)

        self.assertEqual(plan.python_executable, str(venv_python))
        self.assertFalse(plan.use_proxy)
        self.assertIsNone(plan.bootstrap_error)
        create_venv.assert_called_once_with(venv_dir)

    def test_create_or_repair_venv_preserves_pip_stderr(self) -> None:
        module = load_module()

        with tempfile.TemporaryDirectory() as temporary_directory:
            venv_dir = Path(temporary_directory) / "venv"
            venv_python = module.venv_python_path(venv_dir)
            venv_python.parent.mkdir(parents=True)
            venv_python.write_text("")

            pip_error = module.subprocess.CalledProcessError(
                returncode=1,
                cmd=[str(venv_python), "-m", "pip", "install", "tiktoken"],
                stderr="pip exploded",
            )
            with mock.patch.object(module.subprocess, "run", side_effect=pip_error):
                with self.assertRaisesRegex(RuntimeError, "pip exploded"):
                    module.create_or_repair_tokenizer_venv(venv_dir)

    def test_proxy_flags_are_only_added_after_bootstrap_failure(self) -> None:
        module = load_module()

        helper_script = Path("/tmp/reconstruct.py")
        base_args = ["--prompt-text-file", "/tmp/prompt.txt"]
        direct_command = module.build_helper_command(
            python_executable="/tmp/token-python",
            helper_script=helper_script,
            helper_args=base_args,
            use_proxy=False,
        )
        proxy_command = module.build_helper_command(
            python_executable="/tmp/plain-python",
            helper_script=helper_script,
            helper_args=base_args,
            use_proxy=True,
        )

        self.assertNotIn("--allow-proxy", direct_command)
        self.assertNotIn("--proxy-after-tiktoken-failure", direct_command)
        self.assertEqual(
            proxy_command[-2:],
            ["--allow-proxy", "--proxy-after-tiktoken-failure"],
        )

    def test_no_input_invocation_does_not_bootstrap_tokenizer_venv(self) -> None:
        module = load_module()
        wrapper_args = module.argparse.Namespace(
            json_only=False,
            venv_dir="/tmp/unused-tokenizer-venv",
        )
        helper_process = module.subprocess.CompletedProcess(
            args=[],
            returncode=1,
            stdout="",
            stderr='{"error":"prompt_snapshot_required"}\n',
        )

        with mock.patch.object(module, "parse_args", return_value=(wrapper_args, [])):
            with mock.patch.object(module, "choose_tokenizer_plan") as choose_plan:
                with mock.patch.object(
                    module, "run_helper", return_value=helper_process
                ) as run_helper:
                    with mock.patch.object(module.sys.stderr, "write"):
                        exit_code = module.main()

        self.assertEqual(exit_code, 1)
        choose_plan.assert_not_called()
        run_helper.assert_called_once()
        plan = run_helper.call_args.kwargs["plan"]
        self.assertEqual(plan.python_executable, sys.executable)
        self.assertFalse(plan.use_proxy)


if __name__ == "__main__":
    unittest.main()
