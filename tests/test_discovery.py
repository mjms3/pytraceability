from pathlib import Path
from types import ModuleType

import pytest

from pytraceability.discovery import (
    extract_traceability_from_file,
)
from pytraceability.common import (
    UNKNOWN,
    InvalidTraceabilityError,
    Traceability,
)
from pytraceability.data_definition import (
    ExtractionResult,
    MetaDataType,
    DEFAULT_CONFIG,
)
from tests.examples import (
    function_with_traceability_key_as_arg,
    function_with_traceability_key_in_a_variable,
    class_with_traceability_key,
    closure_with_static_key,
    closure_with_dynamic_key,
    with_metadata,
    closure_with_dynamic_metadata,
    method_on_a_class_with_traceability_key,
    method_on_a_class_with_dynamic_traceability_key,
)


TEST_ROOT = Path(__file__).parent


def _test_from_module(
    module: ModuleType,
    function_name: str = "foo",
    line_num_offset: int = 0,
    metadata: MetaDataType | None = None,
    is_complete: bool = True,
) -> None:
    if module.__file__ is None:
        raise ValueError(f"module.__file__ is None. Module: {module}")
    actual = list(
        extract_traceability_from_file(Path(module.__file__), TEST_ROOT, DEFAULT_CONFIG)
    )
    expected = [
        ExtractionResult(
            function_name=function_name,
            line_number=5 + line_num_offset,
            end_line_number=6 + line_num_offset,
            traceability_data=Traceability(key="A key", metadata=metadata or {}),
            is_complete=is_complete,
        ),
    ]
    assert actual == expected


@pytest.mark.parametrize(
    "module,function_name,line_num_offset",
    [
        (function_with_traceability_key_as_arg, "foo", 0),
        (function_with_traceability_key_in_a_variable, "foo", 2),
        (class_with_traceability_key, "foo", 0),
        (closure_with_static_key, "foo.bar", 1),
        (method_on_a_class_with_traceability_key, "Foo.bar", 1),
        (method_on_a_class_with_dynamic_traceability_key, "Foo.bar", 3),
    ],
)
def test_successful_extraction(
    module: ModuleType, function_name: str, line_num_offset: int
) -> None:
    _test_from_module(
        module, function_name=function_name, line_num_offset=line_num_offset
    )


def test_closure_with_dynamic_key():
    with pytest.raises(InvalidTraceabilityError):
        _test_from_module(closure_with_dynamic_key)


def test_with_metadata():
    _test_from_module(with_metadata, metadata={"a": "b"})


def test_closure_with_dynamic_metadata():
    _test_from_module(
        closure_with_dynamic_metadata,
        function_name="foo.bar",
        metadata={"a": UNKNOWN},
        line_num_offset=6,
        is_complete=False,
    )
