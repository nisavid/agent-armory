#!/usr/bin/env python3

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
import venv
from dataclasses import dataclass
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parent
RECONSTRUCT_SCRIPT = SCRIPTS_DIR / "reconstruct-prompt-context.py"
RENDER_SCRIPT = SCRIPTS_DIR / "render-prompt-context-report.py"
DEFAULT_VENV_DIR = Path(tempfile.gettempdir()) / "prompt-context-report-tokenizer-venv"


@dataclass
class TokenizerPlan:
    python_executable: str
    use_proxy: bool
    bootstrap_error: str | None = None


def venv_python_path(venv_dir: Path) -> Path:
    if sys.platform == "win32":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def python_has_tiktoken(python_executable: str) -> bool:
    completed_process = subprocess.run(
        [
            python_executable,
            "-c",
            "import tiktoken; tiktoken.get_encoding('o200k_base')",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    return completed_process.returncode == 0


def create_or_repair_tokenizer_venv(venv_dir: Path) -> Path:
    venv_dir.parent.mkdir(parents=True, exist_ok=True)
    python_path = venv_python_path(venv_dir)

    if not python_path.exists():
        venv.EnvBuilder(with_pip=True, clear=False).create(venv_dir)

    try:
        subprocess.run(
            [
                str(python_path),
                "-m",
                "pip",
                "install",
                "--disable-pip-version-check",
                "--quiet",
                "tiktoken",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as error:
        stderr = error.stderr.strip() if error.stderr else "<no stderr>"
        raise RuntimeError(f"`pip install tiktoken` failed: {stderr}") from error
    return python_path


def choose_tokenizer_plan(venv_dir: Path) -> TokenizerPlan:
    current_python = sys.executable
    if python_has_tiktoken(current_python):
        return TokenizerPlan(python_executable=current_python, use_proxy=False)

    cached_venv_python = venv_python_path(venv_dir)
    if cached_venv_python.exists() and python_has_tiktoken(str(cached_venv_python)):
        return TokenizerPlan(python_executable=str(cached_venv_python), use_proxy=False)

    try:
        tokenizer_python = create_or_repair_tokenizer_venv(venv_dir)
        if python_has_tiktoken(str(tokenizer_python)):
            return TokenizerPlan(
                python_executable=str(tokenizer_python), use_proxy=False
            )
        raise RuntimeError(
            "Tokenizer venv did not provide a working `tiktoken` installation"
        )
    except Exception as error:
        return TokenizerPlan(
            python_executable=current_python,
            use_proxy=True,
            bootstrap_error=str(error),
        )


def build_helper_command(
    *,
    python_executable: str,
    helper_script: Path,
    helper_args: list[str],
    use_proxy: bool,
) -> list[str]:
    command = [python_executable, str(helper_script), *helper_args]
    if use_proxy:
        command.extend(["--allow-proxy", "--proxy-after-tiktoken-failure"])
    return command


def parse_args() -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(
        description="Run the prompt-context helper with automatic tokenizer bootstrapping."
    )
    parser.add_argument("--json-only", action="store_true")
    parser.add_argument("--venv-dir", default=str(DEFAULT_VENV_DIR))
    return parser.parse_known_args()


def helper_args_prompt_source_count(helper_args: list[str]) -> int:
    prompt_source_flags = {
        "--prompt-text-file",
        "--prompt-text-stdin",
        "--manifest-spec-file",
    }
    prompt_source_count = 0
    has_filesystem_fallback = False
    for helper_arg in helper_args:
        if helper_arg in prompt_source_flags or any(
            helper_arg.startswith(f"{flag}=") for flag in prompt_source_flags
        ):
            prompt_source_count += 1
        elif helper_arg == "--allow-filesystem-fallback":
            has_filesystem_fallback = True
    if prompt_source_count:
        return prompt_source_count
    if has_filesystem_fallback:
        return 1
    return prompt_source_count


def run_helper(
    plan: TokenizerPlan, helper_args: list[str]
) -> subprocess.CompletedProcess[str]:
    command = build_helper_command(
        python_executable=plan.python_executable,
        helper_script=RECONSTRUCT_SCRIPT,
        helper_args=helper_args,
        use_proxy=plan.use_proxy,
    )
    return subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )


def run_renderer(helper_output: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(RENDER_SCRIPT)],
        input=helper_output,
        check=False,
        capture_output=True,
        text=True,
    )


def main() -> int:
    wrapper_args, helper_args = parse_args()
    prompt_source_count = helper_args_prompt_source_count(helper_args)
    if prompt_source_count == 0 or prompt_source_count > 1:
        plan = TokenizerPlan(python_executable=sys.executable, use_proxy=False)
    else:
        plan = choose_tokenizer_plan(Path(wrapper_args.venv_dir))

    helper_process = run_helper(plan=plan, helper_args=helper_args)
    if helper_process.returncode != 0:
        sys.stderr.write(helper_process.stderr)
        return helper_process.returncode

    if wrapper_args.json_only:
        sys.stdout.write(helper_process.stdout)
        return 0

    renderer_process = run_renderer(helper_process.stdout)
    if renderer_process.returncode != 0:
        sys.stderr.write(renderer_process.stderr)
        return renderer_process.returncode

    sys.stdout.write(renderer_process.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
