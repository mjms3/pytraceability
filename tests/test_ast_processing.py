import ast
from pathlib import Path
from textwrap import dedent

import pytest

from pytraceability.ast_processing import TraceabilityVisitor
from pytraceability.common import Traceability, InvalidTraceabilityError
from pytraceability.data_definition import (
    ExtractionResult,
    DEFAULT_CONFIG,
)

_FILE_PATH = Path(__file__)


def test_statically_extract_traceability_decorators():
    tree = ast.parse(
        dedent("""\
    @traceability("A key")
    def foo():
        pass
    """)
    )
    decorators = TraceabilityVisitor(DEFAULT_CONFIG, _FILE_PATH).visit(tree)
    assert decorators == [
        ExtractionResult(
            file_path=_FILE_PATH,
            traceability_data=[
                Traceability(key="A key", metadata={}, is_complete=True)
            ],
            function_name="foo",
            line_number=2,
            end_line_number=3,
        )
    ]


def test_can_statically_extract_stacked_traceability_decorators():
    tree = ast.parse(
        dedent("""\
    @traceability("KEY 1")
    @traceability("KEY 2")
    def foo():
        pass
    """)
    )
    decorators = TraceabilityVisitor(DEFAULT_CONFIG, _FILE_PATH).visit(tree)
    assert decorators == [
        ExtractionResult(
            file_path=_FILE_PATH,
            traceability_data=[
                Traceability(key=k, metadata={}, is_complete=True)
                for k in ("KEY 1", "KEY 2")
            ],
            function_name="foo",
            line_number=3,
            end_line_number=4,
        )
    ]


@pytest.mark.raises(exception=InvalidTraceabilityError)
def test_key_must_be_specified():
    tree = ast.parse(
        dedent("""\
    @traceability()
    def foo():
        pass
    """)
    )
    TraceabilityVisitor(DEFAULT_CONFIG, _FILE_PATH).visit(tree)


def test_other_decorators_are_ignored():
    tree = ast.parse(
        dedent("""\
    @another_decorator()
    def foo():
        pass
    """)
    )
    assert TraceabilityVisitor(DEFAULT_CONFIG, _FILE_PATH).visit(tree) == []


@pytest.mark.raises(exception=InvalidTraceabilityError)
def test_cannot_have_two_args():
    tree = ast.parse(
        dedent("""\
    @traceability('key1','key2')
    def foo():
        pass
    """)
    )
    TraceabilityVisitor(DEFAULT_CONFIG, _FILE_PATH).visit(tree)
