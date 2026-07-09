from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
IGNORED_CONFIG_PARTS = {
    ".git",
    ".opencode",
    ".loopspace",
    ".pytest_cache",
    "__pycache__",
}
FORBIDDEN_IMPORTS = {"socket", "urllib", "requests", "httpx"}
FORBIDDEN_HELP_OPTIONS = {
    "--tail",
    "--follow",
    "--gz",
    "--since",
    "--until",
    "--time-filter",
    "--group-by",
}


def project_python_files() -> list[Path]:
    ignored_parts = {".git", ".opencode", ".loopspace", "tests", "__pycache__"}
    return [
        path
        for path in REPO_ROOT.rglob("*.py")
        if not any(part in ignored_parts for part in path.relative_to(REPO_ROOT).parts)
    ]


def test_v1_repo_root_excludes_packaging_plugin_and_ui_entries() -> None:
    forbidden_root_entries = ["pyproject.toml", "setup.py", "plugins", "ui"]

    present = [entry for entry in forbidden_root_entries if (REPO_ROOT / entry).exists()]

    assert present == []


def test_v1_repo_has_no_config_dot_files_outside_ignored_directories() -> None:
    matches = []
    for path in REPO_ROOT.rglob("config.*"):
        relative = path.relative_to(REPO_ROOT)
        if any(part in IGNORED_CONFIG_PARTS for part in relative.parts):
            continue
        matches.append(str(relative))

    assert matches == []


def test_project_python_files_do_not_import_network_modules() -> None:
    violations = []
    for path in project_python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root_name = alias.name.split(".", 1)[0]
                    if root_name in FORBIDDEN_IMPORTS:
                        violations.append(f"{path.relative_to(REPO_ROOT)}:{node.lineno} import {alias.name}")
            elif isinstance(node, ast.ImportFrom) and node.module:
                root_name = node.module.split(".", 1)[0]
                if root_name in FORBIDDEN_IMPORTS:
                    violations.append(f"{path.relative_to(REPO_ROOT)}:{node.lineno} from {node.module}")

    assert violations == []


def test_project_python_files_do_not_read_from_stdin() -> None:
    violations = []
    for path in project_python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Attribute)
                and node.attr == "stdin"
                and isinstance(node.value, ast.Name)
                and node.value.id == "sys"
            ):
                violations.append(f"{path.relative_to(REPO_ROOT)}:{node.lineno} sys.stdin")

    assert violations == []


def test_help_does_not_expose_post_v1_options() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "loglens", "--help"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert [option for option in FORBIDDEN_HELP_OPTIONS if option in result.stdout] == []


def test_v1_rejects_more_than_one_positional_input_file() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "loglens", "sample.ndjson", "sample.ndjson"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
