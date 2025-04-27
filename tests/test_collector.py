from __future__ import annotations

import logging
from operator import attrgetter
from pathlib import Path

import pytest
from git import Repo

from pytraceability.config import (
    PyTraceabilityMode,
    PyTraceabilityConfig,
)
from pytraceability.data_definition import (
    TraceabilityReport,
    RawCode,
    MetaDataType,
    TraceabilityGitHistory,
)
from pytraceability.collector import PyTraceabilityCollector
from pytraceability.exceptions import InvalidTraceabilityError
from tests.conftest import write_traceability_file
from tests.examples import (
    function_with_traceability,
)
from tests.utils import M

EXAMPLES_DIR = Path(__file__).parent / "examples"


def _test_from_file(
    file_path: Path,
    tmp_path: Path,
    function_name: str = "foo",
    line_num_offset: int = 0,
    metadata: MetaDataType | None = None,
    contains_raw_source_code: bool = False,
    history: list[TraceabilityGitHistory] | None = None,
) -> None:
    new_file_path = tmp_path / file_path.name
    new_file_path.write_text(file_path.read_text())
    config = PyTraceabilityConfig(
        base_directory=tmp_path, mode=PyTraceabilityMode.MODULE_IMPORT
    )
    actual = list(PyTraceabilityCollector(config).collect())
    expected = [
        M(
            TraceabilityReport,
            file_path=new_file_path,
            function_name=function_name,
            line_number=5 + line_num_offset,
            end_line_number=6 + line_num_offset,
            key="A key",
            metadata=metadata or {},
            contains_raw_source_code=contains_raw_source_code,
            history=history,
        ),
    ]
    assert actual == expected


@pytest.mark.parametrize(
    "file_name,function_name,line_num_offset",
    [
        ("function_with_traceability.py", "foo", 0),
        ("class_with_traceability.py", "foo", 0),
        ("closure_with_traceability.py", "foo.bar", 1),
        ("method_on_a_class_with_traceability.py", "Foo.bar", 1),
    ],
)
def test_successful_extraction(
    file_name: str, function_name: str, line_num_offset: int, tmp_path: Path
) -> None:
    _test_from_file(
        EXAMPLES_DIR / file_name,
        tmp_path,
        function_name=function_name,
        line_num_offset=line_num_offset,
    )


@pytest.mark.parametrize(
    "file_name",
    [
        "function_with_traceability_key_in_a_variable.py",
        "method_on_a_class_with_key_in_a_variable.py",
    ],
)
def test_key_must_be_static(file_name: str, tmp_path: Path):
    with pytest.raises(InvalidTraceabilityError):
        _test_from_file(EXAMPLES_DIR / file_name, tmp_path)


def test_static_mode_errors_if_unable_to_get_traceability_data_statically(
    tmp_path,
) -> None:
    with pytest.raises(InvalidTraceabilityError):
        _test_from_file(
            EXAMPLES_DIR / "function_with_traceability_key_in_a_variable.py", tmp_path
        )


def test_closure_with_dynamic_key(tmp_path):
    with pytest.raises(InvalidTraceabilityError):
        _test_from_file(EXAMPLES_DIR / "closure_with_key_in_a_variable.py", tmp_path)


def test_with_metadata(tmp_path):
    _test_from_file(EXAMPLES_DIR / "with_metadata.py", tmp_path, metadata={"a": "b"})


def test_with_dynamic_metadata(tmp_path):
    _test_from_file(
        EXAMPLES_DIR / "with_dynamic_metadata.py",
        tmp_path,
        metadata={"a": "Variable value"},
        line_num_offset=2,
    )


def test_closure_with_dynamic_metadata(tmp_path):
    _test_from_file(
        EXAMPLES_DIR / "closure_with_metadata_in_a_variable.py",
        tmp_path,
        function_name="foo.bar",
        metadata={"a": RawCode(code="METADATA")},
        line_num_offset=6,
        contains_raw_source_code=True,
    )


def test_collect_from_directory(directory_with_two_files):
    config = PyTraceabilityConfig(base_directory=directory_with_two_files)

    actual = sorted(PyTraceabilityCollector(config).collect(), key=attrgetter("key"))
    expected = [
        M(
            TraceabilityReport,
            file_path=directory_with_two_files / "file1.py",
            function_name="foo",
            line_number=2,
            end_line_number=3,
            key="KEY-1",
            metadata={},
            contains_raw_source_code=False,
        ),
        M(
            TraceabilityReport,
            file_path=directory_with_two_files / "file2.py",
            function_name="foo",
            line_number=2,
            end_line_number=3,
            key="KEY-2",
            metadata={},
            contains_raw_source_code=False,
        ),
    ]
    assert actual == expected


@pytest.fixture
def directory_with_duplicate_keys(
    git_repo: Repo, tmp_path: Path, pyproject_file: Path
) -> Path:
    write_traceability_file(tmp_path / "file1.py", 1)
    write_traceability_file(tmp_path / "file2.py", 1)
    return tmp_path


def test_duplicate_keys_raises_error(directory_with_duplicate_keys):
    with pytest.raises(InvalidTraceabilityError):
        config = PyTraceabilityConfig(base_directory=directory_with_duplicate_keys)
        list(PyTraceabilityCollector(config).collect())


def test_filename_exclusion():
    file_path = Path(function_with_traceability.__file__).parent
    config = PyTraceabilityConfig(base_directory=file_path, exclude_patterns=["*test*"])
    assert list(PyTraceabilityCollector(config).collect()) == []


def test_invalid_python_file(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.WARNING)
    invalid_file = tmp_path / "invalid_file.py"
    invalid_file.write_text("def foo():\n    print('Hello World'")

    config = PyTraceabilityConfig(base_directory=tmp_path)

    assert list(PyTraceabilityCollector(config).collect()) == []
    assert "Ignoring file due to syntax error" in caplog.text
