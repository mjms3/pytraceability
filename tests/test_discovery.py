from pathlib import Path
from unittest import mock

from pytraceability.discovery import (
    traceability,
    SearchResult,
    collect_traceability_from_directory,
    Traceability,
)


@traceability("A key")
def foo():
    pass


@traceability(key="A kwarg key")
def bar():
    pass


KEY_IN_VARIABLE = "KEY IN VARIABLE"


@traceability(key=KEY_IN_VARIABLE)
def baz():
    pass


def test_discover_traceability():
    root_dir = Path(__file__).parent.resolve()
    found_traceability = list(collect_traceability_from_directory(root_dir, root_dir))
    assert found_traceability == [
        SearchResult(
            function_name="foo",
            line_number=mock.ANY,
            end_line_number=mock.ANY,
            traceability_data=Traceability(key="A key"),
            is_complete=True,
        ),
        SearchResult(
            traceability_data=Traceability(key="A kwarg key"),
            is_complete=True,
            function_name="bar",
            line_number=mock.ANY,
            end_line_number=mock.ANY,
        ),
        SearchResult(
            traceability_data=Traceability(key="KEY IN VARIABLE"),
            is_complete=True,
            function_name="baz",
            line_number=mock.ANY,
            end_line_number=mock.ANY,
        ),
    ]
