from __future__ import annotations

import logging
from collections import ChainMap
from typing import Any

from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from enum import Enum
from pathlib import Path

import git
import tomli
from pytraceability.common import STANDARD_DECORATOR_NAME

PROJECT_NAME = "pytraceability"

_log = logging.getLogger(__name__)


class PyTraceabilityMode(str, Enum):
    static_only = "static-only"
    static_plus_dynamic = "static-plus-dynamic"


class GitHistoryMode(str, Enum):
    NONE = "none"
    FUNCTION_HISTORY = "function-history"


class OutputFormats(str, Enum):
    KEY_ONLY = "key-only"
    JSON = "json"


class PyTraceabilityConfig(BaseModel):
    base_directory: Path
    python_root: Path | None = (
        None  # Optional, will be set to base_directory if not provided
    )
    decorator_name: str = STANDARD_DECORATOR_NAME
    exclude_patterns: list[str] = Field(default_factory=list)
    mode: PyTraceabilityMode = PyTraceabilityMode.static_only
    git_history_mode: GitHistoryMode = GitHistoryMode.NONE
    output_format: OutputFormats = OutputFormats.KEY_ONLY
    since: datetime | None = None

    @model_validator(mode="before")
    def validate_date(cls, values):
        if values.get("python_root") is None:
            values["python_root"] = values.get("base_directory")
        return values

    @staticmethod
    def get_pyproject_file_path(params: dict[str, Any]) -> Path | None:
        if params.get("pyproject_file") is None:
            return params.pop("pyproject_file")
        elif pyproject_file := find_pyproject_file(params["base_directory"]):
            return pyproject_file
        elif params.get("python_root"):
            return params["python_root"] / "pyproject.toml"
        return None

    @classmethod
    def from_command_line_arguments(
        cls, cli_params: dict[str, Any]
    ) -> PyTraceabilityConfig:
        pyproject_file_path = cls.get_pyproject_file_path(cli_params)
        if pyproject_file_path is not None:
            pyproject_contents = tomli.loads(pyproject_file_path.read_text())["tool"][
                PROJECT_NAME
            ]
        else:
            pyproject_contents = {}
        config = ChainMap(cli_params, pyproject_contents)
        return cls(**config)


def find_pyproject_file(path_in_repo: Path) -> Path:
    "Initially assume it's located in the root of the git repo"
    git_root = get_repo_root(path_in_repo)
    pyproject_toml_file = git_root / "pyproject.toml"
    _log.info("Using pyproject.toml file: %s", pyproject_toml_file)
    return pyproject_toml_file


def get_repo_root(path_in_repo):
    _log.debug("Finding git root for %s", path_in_repo)
    git_repo = git.Repo(path_in_repo, search_parent_directories=True)
    git_root = Path(git_repo.git.rev_parse("--show-toplevel"))
    return git_root


def find_and_parse_config(path_in_repo: Path) -> PyTraceabilityConfig:
    pyproject_file_path = find_pyproject_file(path_in_repo)
    pyproject_contents = tomli.loads(pyproject_file_path.read_text())["tool"][
        PROJECT_NAME
    ]
    return PyTraceabilityConfig(
        base_directory=pyproject_file_path.parent, **pyproject_contents
    )
