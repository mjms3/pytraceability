from pathlib import Path
from types import ModuleType
from unittest import mock

import pytest

from pytraceability.discovery import (
    extract_traceability_from_file,
    collect_traceability_from_directory,
)
from pytraceability.common import (
    UNKNOWN,
    Traceability,
)
from pytraceability.exceptions import InvalidTraceabilityError
from pytraceability.data_definition import (
    ExtractionResult,
    MetaDataType,
)
from pytraceability.config import (
    PyTraceabilityMode,
    PyTraceabilityConfig,
    DEFAULT_CONFIG,
)
from tests.examples import (
    function_with_traceability,
    function_with_traceability_key_in_a_variable,
    class_with_traceability,
    closure_with_traceability,
    closure_with_key_in_a_variable,
    with_metadata,
    closure_with_metadata_in_a_variable,
    method_on_a_class_with_traceability,
    method_on_a_class_with_key_in_a_variable,
    function_with_multiple_traceability_one_key_in_a_variable,
)


TEST_ROOT = Path(__file__).parent
TEST_CONFIG = PyTraceabilityConfig(mode=PyTraceabilityMode.static_plus_dynamic)


def _test_from_module(
    module: ModuleType,
    function_name: str = "foo",
    line_num_offset: int = 0,
    metadata: MetaDataType | None = None,
    is_complete: bool = True,
    config: PyTraceabilityConfig = TEST_CONFIG,
) -> None:
    if module.__file__ is None:
        raise ValueError(f"module.__file__ is None. Module: {module}")
    file_path = Path(module.__file__)
    actual = list(extract_traceability_from_file(file_path, TEST_ROOT, config))
    expected = [
        ExtractionResult(
            file_path=file_path,
            function_name=function_name,
            line_number=5 + line_num_offset,
            end_line_number=6 + line_num_offset,
            source_code=mock.ANY,
            traceability_data=[
                Traceability(
                    key="A key", metadata=metadata or {}, is_complete=is_complete
                )
            ],
        ),
    ]
    assert actual == expected


@pytest.mark.parametrize(
    "module,function_name,line_num_offset",
    [
        (function_with_traceability, "foo", 0),
        (function_with_traceability_key_in_a_variable, "foo", 2),
        (class_with_traceability, "foo", 0),
        (closure_with_traceability, "foo.bar", 1),
        (method_on_a_class_with_traceability, "Foo.bar", 1),
        (method_on_a_class_with_key_in_a_variable, "Foo.bar", 3),
    ],
)
def test_successful_extraction(
    module: ModuleType, function_name: str, line_num_offset: int
) -> None:
    _test_from_module(
        module, function_name=function_name, line_num_offset=line_num_offset
    )


@pytest.mark.raises(exception=InvalidTraceabilityError)
def test_static_mode_errors_if_unable_to_get_traceability_data_statically() -> None:
    _test_from_module(
        function_with_traceability_key_in_a_variable, config=DEFAULT_CONFIG
    )


def test_multiple_traceability_one_key_in_a_variable() -> None:
    file_path = Path(function_with_multiple_traceability_one_key_in_a_variable.__file__)
    actual = list(extract_traceability_from_file(file_path, TEST_ROOT, TEST_CONFIG))
    expected = [
        ExtractionResult(
            file_path=file_path,
            function_name="foo",
            line_number=8,
            end_line_number=9,
            source_code=mock.ANY,
            traceability_data=[
                Traceability(key=k, metadata={}, is_complete=True)
                for k in ("A key", "Another key")
            ],
        )
    ]
    assert actual == expected


def test_closure_with_dynamic_key():
    with pytest.raises(InvalidTraceabilityError):
        _test_from_module(closure_with_key_in_a_variable)


def test_with_metadata():
    _test_from_module(with_metadata, metadata={"a": "b"})


def test_closure_with_dynamic_metadata():
    _test_from_module(
        closure_with_metadata_in_a_variable,
        function_name="foo.bar",
        metadata={"a": UNKNOWN},
        line_num_offset=6,
        is_complete=False,
    )


def test_collect_from_directory():
    file_path = Path(__file__).parent / "examples/separate_directory"

    actual = list(
        collect_traceability_from_directory(file_path, TEST_ROOT, DEFAULT_CONFIG)
    )
    expected = [
        ExtractionResult(
            file_path=file_path / "file1.py",
            function_name="foo",
            line_number=5,
            end_line_number=6,
            source_code=mock.ANY,
            traceability_data=[
                Traceability(key="KEY-1", metadata={}, is_complete=True)
            ],
        ),
        ExtractionResult(
            file_path=file_path / "file2.py",
            function_name="foo",
            line_number=5,
            end_line_number=6,
            source_code=mock.ANY,
            traceability_data=[
                Traceability(key="KEY-2", metadata={}, is_complete=True)
            ],
        ),
    ]
    assert actual == expected


def test_filename_exclusion():
    file_path = Path(function_with_traceability.__file__).parent
    config = PyTraceabilityConfig(exclude_patterns=["*test*"])
    actual = list(collect_traceability_from_directory(file_path, TEST_ROOT, config))
    assert actual == []
