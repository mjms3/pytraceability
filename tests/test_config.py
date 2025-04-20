from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest
from git import Repo

from pytraceability.config import (
    PROJECT_NAME,
    PyTraceabilityConfig,
    OutputFormats,
    GitHistoryMode,
    PyTraceabilityMode,
)
from tests.utils import M


def test_explicit_pyproject_file(tmp_path: Path):
    pyproject_file = tmp_path / "pyproject.toml"
    pyproject_file.write_text(
        dedent(
            f"""
            [tool.{PROJECT_NAME}]
            base_directory = "{tmp_path}"
            python_root = "{tmp_path / "src"}"
            decorator_name = "custom_decorator"
            exclude_patterns = ["*test*"]
            mode = "module-import"
            git_history_mode = "none"
            output_format = "json"
            """
        )
    )

    config = PyTraceabilityConfig.from_command_line_arguments(
        {
            "pyproject_file": pyproject_file,
            "base_directory": tmp_path,
        }
    )

    assert config == M(
        PyTraceabilityConfig,
        base_directory=tmp_path,
        python_root=tmp_path / "src",
        decorator_name="custom_decorator",
        exclude_patterns=["*test*"],
        mode=PyTraceabilityMode.MODULE_IMPORT,
        git_history_mode=GitHistoryMode.NONE,
        output_format=OutputFormats.JSON,
    )


@pytest.fixture
def folder_setup(tmp_path: Path, git_repo: Repo):
    (tmp_path / "python_root" / "base_directory").mkdir(parents=True, exist_ok=True)
    return tmp_path


def _test_pyproject_file(
    folder_setup: Path, pyproject_path: Path, decorator_name: str, **kwargs
):
    pyproject_path.write_text(
        dedent(
            f"""
            [tool.{PROJECT_NAME}]
            decorator_name = "{decorator_name}"
            """
        )
    )

    config = PyTraceabilityConfig.from_command_line_arguments(
        {"base_directory": folder_setup, **kwargs}
    )

    assert config.decorator_name == decorator_name


def test_pyproject_file_at_python_root(folder_setup: Path):
    _test_pyproject_file(
        folder_setup=folder_setup,
        pyproject_path=folder_setup / "python_root" / "pyproject.toml",
        decorator_name="python_root",
        python_root=folder_setup / "python_root",
    )


def test_pyproject_file_at_base_directory(folder_setup: Path):
    _test_pyproject_file(
        folder_setup=folder_setup,
        pyproject_path=folder_setup / "pyproject.toml",
        decorator_name="base_directory",
    )


def test_pyproject_file_at_repo_root(folder_setup: Path):
    _test_pyproject_file(
        folder_setup=folder_setup,
        pyproject_path=folder_setup / "pyproject.toml",
        decorator_name="repo_root",
    )
