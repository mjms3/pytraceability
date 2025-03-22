import ast
from pathlib import Path
from textwrap import dedent

import pytest

from pytraceability.ast_processing import TraceabilityVisitor
from pytraceability.common import InvalidTraceabilityError
from pytraceability.data_definition import (
    ExtractionResult,
    DEFAULT_CONFIG,
    Traceability,
)

_FILE_PATH = Path(__file__)

_fn_def = """\
def foo():
    pass"""


def test_statically_extract_traceability_decorators():
    source_code = dedent("""\
    @traceability("A key")
    def foo():
        pass
    """)
    tree = ast.parse(source_code)
    decorators = TraceabilityVisitor(DEFAULT_CONFIG, _FILE_PATH, source_code).visit(
        tree
    )
    assert decorators == [
        ExtractionResult(
            file_path=_FILE_PATH,
            function_name="foo",
            line_number=2,
            end_line_number=3,
            source_code=_fn_def,
            traceability_data=[
                Traceability(key="A key", metadata={}, is_complete=True)
            ],
        )
    ]


def test_can_statically_extract_stacked_traceability_decorators():
    source_code = dedent("""\
    @traceability("KEY 1")
    @traceability("KEY 2")
    def foo():
        pass
    """)
    tree = ast.parse(source_code)
    decorators = TraceabilityVisitor(DEFAULT_CONFIG, _FILE_PATH, source_code).visit(
        tree
    )
    assert decorators == [
        ExtractionResult(
            file_path=_FILE_PATH,
            function_name="foo",
            line_number=3,
            end_line_number=4,
            source_code=_fn_def,
            traceability_data=[
                Traceability(key=k, metadata={}, is_complete=True)
                for k in ("KEY 1", "KEY 2")
            ],
        )
    ]


@pytest.mark.raises(exception=InvalidTraceabilityError)
def test_key_must_be_specified():
    source_code = dedent("""\
    @traceability()
    def foo():
        pass
    """)
    tree = ast.parse(source_code)
    TraceabilityVisitor(DEFAULT_CONFIG, _FILE_PATH, source_code).visit(tree)


def test_other_decorators_are_ignored():
    source_code = dedent("""\
    @another_decorator()
    def foo():
        pass
    """)
    tree = ast.parse(source_code)
    assert (
        TraceabilityVisitor(DEFAULT_CONFIG, _FILE_PATH, source_code).visit(tree) == []
    )


@pytest.mark.raises(exception=InvalidTraceabilityError)
def test_cannot_have_two_args():
    source_code = dedent("""\
    @traceability('key1','key2')
    def foo():
        pass
    """)
    tree = ast.parse(source_code)
    TraceabilityVisitor(DEFAULT_CONFIG, _FILE_PATH, source_code).visit(tree)
