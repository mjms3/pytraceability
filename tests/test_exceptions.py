import pytest

from pytraceability.exceptions import (
    additional_error_info,
    TraceabilityErrorMessages,
    InvalidTraceabilityError,
)


def test_all_InvalidTraceabilityErrors_are_documented():
    assert set(additional_error_info.keys()) == set(
        TraceabilityErrorMessages
    )  # Would be nice to do this by type checking


def test_cant_create_a_InvalidTraceabilityError_with_an_undocumeneted_message():
    with pytest.raises(ValueError):
        InvalidTraceabilityError("A random error message")
