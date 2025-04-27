from __future__ import annotations

import logging
from collections import ChainMap
from typing import Any

from pydantic import BaseModel, Field, computed_field
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


class OutputFormats(str, Enum):
    KEY_ONLY = "key-only"
    JSON = "json"
    HTML = "html"


def load_config_from_pyproject_file(pyproject_file: Path) -> dict[str, Any]:
    return tomli.loads(pyproject_file.read_text())["tool"][PROJECT_NAME]


def find_pyproject_file(
    base_directory: Path,
    python_root: Path | None,
) -> Path | None:
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
                return pyproject_file_path

    return None


class HistoryModeConfig(BaseModel):
    git_branch: str = "main"
    commit_url_template: str | None = None


class PyTraceabilityConfig(BaseModel):
    base_directory: Path
    _python_root: Path | None = None
    decorator_name: str = STANDARD_DECORATOR_NAME
    exclude_patterns: list[str] = Field(default_factory=list)
    mode: PyTraceabilityMode = PyTraceabilityMode.DEFAULT
    output_format: OutputFormats = OutputFormats.KEY_ONLY
    history_config: HistoryModeConfig | None = None

    def __init__(self, /, **data: Any) -> None:
        python_root = data.pop("python_root", None)
        super().__init__(**data)
        self._python_root = Path(python_root) if python_root else None

    @computed_field
    @property
    def python_root(self) -> Path:
        if self._python_root:
            return self._python_root
        return self.base_directory

    @classmethod
    def from_command_line_arguments(
        cls, cli_params: dict[str, Any]
    ) -> PyTraceabilityConfig:
        _log.info(f"cli_params: {cli_params}")
        if cli_params.get("history"):
            cli_params["history"] = {
                k: v
                for k, v in cli_params.items()
                if k in HistoryModeConfig.model_fields and v is not None
            }
        if pyproject_file := cli_params.get("pyproject_file"):
            config_from_file = load_config_from_pyproject_file(Path(pyproject_file))
        elif pyproject_file := find_pyproject_file(
            cli_params["base_directory"],
            cli_params.get("python_root"),
        ):
            config_from_file = load_config_from_pyproject_file(Path(pyproject_file))
        else:
            config_from_file = {}

        config = ChainMap(
            {k: v for k, v in cli_params.items() if v},
            config_from_file,
        )
        _log.info(f"config: {config}")
        if config.get("history") and cli_params.get("history") is not False:
            history_config = HistoryModeConfig(
                **config["history"],
            )
            config["history_config"] = history_config
        return cls(**config)


def get_repo_root(path_in_repo: Path) -> Path:
    _log.debug("Finding git root for %s", path_in_repo)
    git_repo = git.Repo(path_in_repo, search_parent_directories=True)
    git_root = Path(git_repo.git.rev_parse("--show-toplevel"))
    return git_root
