from pathlib import Path

from pytraceability.config import (
    find_pyproject_file,
    find_and_parse_config,
    PyTraceabilityConfig,
)
from tests.factories import THIS_REPO_ROOT


def test_find_pyproject_file():
    assert (
        find_pyproject_file(Path(__file__))
        == Path(__file__).parent.parent / "pyproject.toml"
    )


def test_find_and_parse_config():
    assert find_and_parse_config(Path(__file__)) == PyTraceabilityConfig(
        repo_root=THIS_REPO_ROOT, decorator_name="pytraceability"
    )
