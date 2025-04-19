from __future__ import annotations

import ast
from datetime import date
from decimal import Decimal
from pathlib import Path
from textwrap import dedent

import pytest

from pytraceability.ast_processing import TraceabilityVisitor, RawCode
from pytraceability.common import STANDARD_DECORATOR_NAME
from pytraceability.data_definition import (
    ExtractionResult,
    Traceability,
)
from pytraceability.exceptions import InvalidTraceabilityError

_FILE_PATH = Path(__file__)

_fn_def = """\
def foo():
    pass"""


@pytest.mark.parametrize(
    "metadata,expected_metadata,is_complete",
    [
        ("", {}, True),
        ('info="some info"', {"info": "some info"}, True),
        (
            'info="some info", version="1.0"',
            {"info": "some info", "version": "1.0"},
            True,
        ),
        ("info=['info1', 'info2']", {"info": ["info1", "info2"]}, True),
        ("info={'key': 'value'}", {"info": {"key": "value"}}, True),
        (
            "info=f'{var} something'",
            {"info": RawCode(code="f'{var} something'")},
            False,
        ),
        (
            "info=[f'{var} something']",
            {"info": [RawCode(code="f'{var} something'")]},
            False,
        ),
        ("info={'item1', 'item2'}", {"info": {"item1", "item2"}}, True),
        (
            "info=('item1', 'item2')",
            {"info": ("item1", "item2")},
            True,
        ),
        (
            "info=[x**2 for x in range(2)]",
            {"info": [0, 1]},
            True,
        ),
        (
            "info=[x+y for x in range(2)]",
            {"info": RawCode(code="[x+y for x in range(2)]")},
            False,
        ),
        (
            "info=datetime.date(2020,1,1)",
            {"info": date(2020, 1, 1)},
            True,
        ),
        (
            "info=Decimal('1.0')",
            {"info": Decimal("1.0")},
            True,
        ),
    ],
)
def test_statically_extract_traceability_decorators(
    metadata, expected_metadata, is_complete
):
    source_code = dedent(f"""\
    @traceability("A key", {metadata})
    def foo():
        pass
    """)
    tree = ast.parse(source_code)
    decorators = TraceabilityVisitor(
        STANDARD_DECORATOR_NAME, _FILE_PATH, source_code
    ).visit(tree)
    assert decorators == [
        ExtractionResult(
            file_path=_FILE_PATH,
            function_name="foo",
            line_number=2,
            end_line_number=3,
            source_code=_fn_def,
            traceability_data=[Traceability(key="A key", metadata=expected_metadata)],
        )
    ]
    assert decorators[0].traceability_data[0].is_complete == is_complete


def test_can_statically_extract_stacked_traceability_decorators():
    source_code = dedent("""\
    @traceability("KEY 1")
    @traceability("KEY 2")
    def foo():
        pass
    """)
    tree = ast.parse(source_code)
    decorators = TraceabilityVisitor(
        STANDARD_DECORATOR_NAME, _FILE_PATH, source_code
    ).visit(tree)
    assert decorators == [
        ExtractionResult(
            file_path=_FILE_PATH,
            function_name="foo",
            line_number=3,
            end_line_number=4,
            source_code=_fn_def,
            traceability_data=[
                Traceability(key=k, metadata={}) for k in ("KEY 1", "KEY 2")
            ],
        )
    ]


def test_key_must_be_specified():
    source_code = dedent("""\
    @traceability()
    def foo():
        pass
    """)
    tree = ast.parse(source_code)
    with pytest.raises(InvalidTraceabilityError):
        TraceabilityVisitor(STANDARD_DECORATOR_NAME, _FILE_PATH, source_code).visit(
            tree
        )


@pytest.mark.parametrize(
    "decorator",
    [
        "@another_decorator()",
        "@dataclass",
        "@click.option()",
    ],
)
def test_other_decorators_are_ignored(decorator):
    source_code = dedent(f"""\
    {decorator}
    def foo():
        pass
    """)
    tree = ast.parse(source_code)
    assert (
        TraceabilityVisitor(STANDARD_DECORATOR_NAME, _FILE_PATH, source_code).visit(
            tree
        )
        == []
    )


def test_cannot_have_two_args():
    source_code = dedent("""\
    @traceability('key1','key2')
    def foo():
        pass
    """)
    tree = ast.parse(source_code)
    with pytest.raises(InvalidTraceabilityError):
        TraceabilityVisitor(STANDARD_DECORATOR_NAME, _FILE_PATH, source_code).visit(
            tree
        )
