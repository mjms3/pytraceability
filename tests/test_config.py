from pathlib import Path

from pytraceability.config import (
    find_pyproject_file,
    find_and_parse_config,
    PyTraceabilityConfig,
)


def test_find_pyproject_file():
    assert (
        find_pyproject_file(Path(__file__))
        == Path(__file__).parent.parent / "pyproject.toml"
    )


def test_find_and_parse_config():
    assert find_and_parse_config(Path(__file__)) == PyTraceabilityConfig(
        decorator_name="pytraceability"
    )
