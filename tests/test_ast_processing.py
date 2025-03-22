import ast
from textwrap import dedent

from pytraceability.ast_processing import Visitor
from pytraceability.data_definition import (
    ExtractionResult,
    DEFAULT_CONFIG,
)
from pytraceability.common import Traceability


def test_statically_extract_traceability_decorators():
    tree = ast.parse(
        dedent("""\
    @traceability("A key")
    def foo():
        pass
    """)
    )
    decorators = Visitor(DEFAULT_CONFIG).visit(tree)
    assert decorators == [
        ExtractionResult(
            traceability_data=Traceability(key="A key", metadata={}),
            is_complete=True,
            function_name="foo",
            line_number=2,
            end_line_number=3,
        )
    ]
