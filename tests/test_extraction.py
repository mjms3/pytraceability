from pathlib import Path
from types import ModuleType

import pytest

from pytraceability.discovery import (
    SearchResult,
    Traceability,
    extract_traceability_from_file,
    InvalidTraceabilityError,
    MetaDataType,
    UNKNOWN,
)
from tests.examples import (
    function_with_traceability_key_as_arg,
    function_with_traceability_key_as_kwarg,
    function_with_traceability_key_in_a_variable,
    class_with_traceability_key,
    closure_with_static_key,
    closure_with_dynamic_key,
    with_metadata,
    closure_with_dynamic_metadata,
)


TEST_ROOT = Path(__file__).parent


def _test_from_module(
    module: ModuleType,
    line_num_offset: int = 0,
    metadata: MetaDataType | None = None,
    is_complete: bool = True,
) -> None:
    if module.__file__ is None:
        raise ValueError(f"module.__file__ is None. Module: {module}")
    assert list(extract_traceability_from_file(Path(module.__file__), TEST_ROOT)) == [
        SearchResult(
            function_name="foo",
            line_number=5 + line_num_offset,
            end_line_number=6 + line_num_offset,
            traceability_data=Traceability(key="A key", metadata=metadata or {}),
            is_complete=is_complete,
        ),
    ]


@pytest.mark.parametrize(
    "module,line_num_offset",
    [
        (function_with_traceability_key_as_arg, 0),
        (function_with_traceability_key_as_kwarg, 0),
        (function_with_traceability_key_in_a_variable, 2),
        (class_with_traceability_key, 0),
        (closure_with_static_key, 1),
    ],
)
def test_successful_extraction(module: ModuleType, line_num_offset: int) -> None:
    _test_from_module(module, line_num_offset=line_num_offset)


def test_closure_with_dynamic_key():
    with pytest.raises(InvalidTraceabilityError):
        _test_from_module(closure_with_dynamic_key)


def test_with_metadata():
    _test_from_module(with_metadata, metadata={"a": "b"})


def test_closure_with_dynamic_metadata():
    _test_from_module(
        closure_with_dynamic_metadata,
        metadata={"a": UNKNOWN},
        line_num_offset=6,
        is_complete=False,
    )
