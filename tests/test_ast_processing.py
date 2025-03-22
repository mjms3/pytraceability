import ast
from pathlib import Path
from textwrap import dedent

from pytraceability.ast_processing import TraceabilityVisitor
from pytraceability.data_definition import (
    ExtractionResult,
    DEFAULT_CONFIG,
    ExtractedTraceability,
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
                ExtractedTraceability(key="A key", metadata={}, is_complete=True)
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
                ExtractedTraceability(key=k, metadata={}, is_complete=True)
                for k in ("KEY 1", "KEY 2")
            ],
            function_name="foo",
            line_number=3,
            end_line_number=4,
        )
    ]
