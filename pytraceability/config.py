from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import git
import tomli

PROJECT_NAME = "pytraceability"


class PyTraceabilityMode(str, Enum):
    static_only = "static-only"
    static_plus_dynamic = "static-plus-dynamic"


@dataclass(frozen=True)
class PyTraceabilityConfig:
    decorator_name: str = "traceability"
    exclude_patterns: list[str] = field(default_factory=lambda: [])
    mode: PyTraceabilityMode = PyTraceabilityMode.static_only


DEFAULT_CONFIG = PyTraceabilityConfig()


def find_pyproject_file(path_in_repo: Path) -> Path:
    "Initially assume it's located in the root of the git repo"
    git_repo = git.Repo(path_in_repo, search_parent_directories=True)
    git_root = Path(git_repo.git.rev_parse("--show-toplevel"))
    return git_root / "pyproject.toml"


def find_and_parse_config(path_in_repo: Path) -> PyTraceabilityConfig:
    pyproject_file = find_pyproject_file(path_in_repo)
    contents = tomli.loads(pyproject_file.read_text())
    return PyTraceabilityConfig(**contents["tool"][PROJECT_NAME])
