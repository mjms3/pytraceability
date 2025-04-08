import logging

from pydantic import BaseModel, Field
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


class PyTraceabilityConfig(BaseModel):
    repo_root: Path
    decorator_name: str = STANDARD_DECORATOR_NAME
    exclude_patterns: list[str] = Field(default_factory=list)
    mode: PyTraceabilityMode = PyTraceabilityMode.static_only
    git_history_mode: GitHistoryMode = GitHistoryMode.NONE
    since: datetime | None = None

    @classmethod
    def from_pyproject_toml(cls, pyproject_file: Path) -> "PyTraceabilityConfig":
        """Create a PyTraceabilityConfig from a pyproject.toml file."""
        if not pyproject_file.exists():
            raise FileNotFoundError(f"pyproject.toml file not found: {pyproject_file}")
        contents = tomli.loads(pyproject_file.read_text())
        return cls(
            repo_root=get_repo_root(pyproject_file.parent),
            **contents["tool"][PROJECT_NAME],
        )


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
    pyproject_file = find_pyproject_file(path_in_repo)
    return PyTraceabilityConfig.from_pyproject_toml(pyproject_file)
