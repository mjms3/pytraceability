import logging
from operator import attrgetter
from pathlib import Path
from types import ModuleType

import pytest

from pytraceability.config import (
    PyTraceabilityMode,
)
from pytraceability.data_definition import (
    TraceabilityReport,
    RawCode,
)
from pytraceability.discovery import (
    collect_output_data,
)
from pytraceability.exceptions import InvalidTraceabilityError
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
)
from tests.factories import TEST_ROOT, TEST_CONFIG, _test_from_module
from tests.utils import M


@pytest.mark.parametrize(
    "module,function_name,line_num_offset",
    [
        (function_with_traceability, "foo", 0),
        (class_with_traceability, "foo", 0),
        (closure_with_traceability, "foo.bar", 1),
        (method_on_a_class_with_traceability, "Foo.bar", 1),
    ],
)
def test_successful_extraction(
    module: ModuleType, function_name: str, line_num_offset: int
) -> None:
    _test_from_module(
        module, function_name=function_name, line_num_offset=line_num_offset
    )


@pytest.mark.parametrize(
    "module",
    [
        function_with_traceability_key_in_a_variable,
        method_on_a_class_with_key_in_a_variable,
    ],
)
def test_key_must_be_static(module):
    with pytest.raises(InvalidTraceabilityError):
        _test_from_module(module)


@pytest.mark.raises(exception=InvalidTraceabilityError)
def test_static_mode_errors_if_unable_to_get_traceability_data_statically() -> None:
    static_only_config = TEST_CONFIG.model_copy(
        update={"mode": PyTraceabilityMode.static_only}
    )
    _test_from_module(
        function_with_traceability_key_in_a_variable, config=static_only_config
    )


def test_closure_with_dynamic_key():
    with pytest.raises(InvalidTraceabilityError):
        _test_from_module(closure_with_key_in_a_variable)


def test_with_metadata():
    _test_from_module(with_metadata, metadata={"a": "b"})


def test_closure_with_dynamic_metadata():
    _test_from_module(
        closure_with_metadata_in_a_variable,
        function_name="foo.bar",
        metadata={"a": RawCode("METADATA")},
        line_num_offset=6,
        is_complete=False,
    )


def test_collect_from_directory():
    file_path = Path(__file__).parent / "examples/separate_directory"

    actual = sorted(
        collect_output_data(file_path, TEST_ROOT, TEST_CONFIG), key=attrgetter("key")
    )
    expected = [
        M(
            TraceabilityReport,
            file_path=file_path / "file1.py",
            function_name="foo",
            line_number=5,
            end_line_number=6,
            key="KEY-1",
            metadata={},
            is_complete=True,
        ),
        M(
            TraceabilityReport,
            file_path=file_path / "file2.py",
            function_name="foo",
            line_number=5,
            end_line_number=6,
            key="KEY-2",
            metadata={},
            is_complete=True,
        ),
    ]
    assert actual == expected


def test_filename_exclusion():
    file_path = Path(function_with_traceability.__file__).parent
    config = TEST_CONFIG.model_copy(update={"exclude_patterns": ["*test*"]})
    assert list(collect_output_data(file_path, TEST_ROOT, config)) == []


def test_invalid_python_file(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.WARNING)
    invalid_file = tmp_path / "invalid_file.py"
    invalid_file.write_text("def foo():\n    print('Hello World'")

    config = TEST_CONFIG.model_copy(update={"repo_root": tmp_path})

    assert list(collect_output_data(tmp_path, tmp_path, config)) == []
    assert "Ignoring file due to syntax error" in caplog.text
