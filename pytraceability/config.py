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
    DEFAULT = "default"
    MODULE_IMPORT = "module-import"


class GitHistoryMode(str, Enum):
    NONE = "none"
    FUNCTION_HISTORY = "function-history"


class OutputFormats(str, Enum):
    KEY_ONLY = "key-only"
    JSON = "json"


def _load_config_from_pyproject_file(pyproject_file: Path) -> dict[str, Any]:
    return tomli.loads(pyproject_file.read_text())["tool"][PROJECT_NAME]


def get_config_from_pyproject_file(
    pyproject_file: Path | None,
    base_directory: Path,
    python_root: Path | None,
) -> dict[str, Any]:
    supplied_pyproject_file = pyproject_file
    if supplied_pyproject_file is not None:
        return _load_config_from_pyproject_file(supplied_pyproject_file)

    pyproject_file_sources: list[Path | None] = [
        base_directory,
        python_root,
        get_repo_root(base_directory),
        Path.cwd(),
    ]

    for pyproject_file_path in pyproject_file_sources:
        if pyproject_file_path:
            _log.info(f"Looking for pyproject file in {pyproject_file_path}")
            if not pyproject_file_path.is_dir():
                raise ValueError(f"Path {pyproject_file_path} is not a directory")
            pyproject_file_path = pyproject_file_path / "pyproject.toml"
            if pyproject_file_path.exists():
                _log.info(f"Loading config from pyproject file {pyproject_file_path}")
                return _load_config_from_pyproject_file(pyproject_file_path)

    return {}


class PyTraceabilityConfig(BaseModel):
    base_directory: Path
    python_root: Path | None = (
        None  # Optional, will be set to base_directory if not provided
    )
    decorator_name: str = STANDARD_DECORATOR_NAME
    exclude_patterns: list[str] = Field(default_factory=list)
    mode: PyTraceabilityMode = PyTraceabilityMode.DEFAULT
    git_history_mode: GitHistoryMode = GitHistoryMode.NONE
    output_format: OutputFormats = OutputFormats.KEY_ONLY
    since: datetime | None = None

    @model_validator(mode="before")
    def validate_config(cls, values):
        if values.get("python_root") is None:
            values["python_root"] = values.get("base_directory")
        return values

    @classmethod
    def from_command_line_arguments(
        cls, cli_params: dict[str, Any]
    ) -> PyTraceabilityConfig:
        _log.info(f"cli_params: {cli_params}")
        config_from_file = get_config_from_pyproject_file(
            Path(cli_params["pyproject_file"])
            if cli_params.get("pyproject_file")
            else None,
            cli_params["base_directory"],
            cli_params.get("python_root"),
        )
        config = ChainMap(
            {k: v for k, v in cli_params.items() if v},
            config_from_file,
        )
        _log.info(f"config: {config}")
        return cls(**config)


def get_repo_root(path_in_repo: Path) -> Path:
    _log.debug("Finding git root for %s", path_in_repo)
    git_repo = git.Repo(path_in_repo, search_parent_directories=True)
    git_root = Path(git_repo.git.rev_parse("--show-toplevel"))
    return git_root
