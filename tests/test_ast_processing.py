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
    TraceabilityReport,
)
from pytraceability.exceptions import InvalidTraceabilityError

_FILE_PATH = Path(__file__)

_fn_def = """\
def foo():
    pass"""


@pytest.mark.parametrize(
    "metadata,expected_metadata,contains_raw_source_code",
    [
        ("", {}, False),
        ('info="some info"', {"info": "some info"}, False),
        (
            'info="some info", version="1.0"',
            {"info": "some info", "version": "1.0"},
            False,
        ),
        ("info=['info1', 'info2']", {"info": ["info1", "info2"]}, False),
        ("info={'key': 'value'}", {"info": {"key": "value"}}, False),
        (
            "info=f'{var} something'",
            {"info": RawCode(code="f'{var} something'")},
            True,
        ),
        (
            "info=[f'{var} something']",
            {"info": [RawCode(code="f'{var} something'")]},
            True,
        ),
        ("info={'item1', 'item2'}", {"info": {"item1", "item2"}}, False),
        (
            "info=('item1', 'item2')",
            {"info": ("item1", "item2")},
            False,
        ),
        (
            "info=[x**2 for x in range(2)]",
            {"info": [0, 1]},
            False,
        ),
        (
            "info=[x+y for x in range(2)]",
            {"info": RawCode(code="[x+y for x in range(2)]")},
            True,
        ),
        (
            "info=datetime.date(2020,1,1)",
            {"info": date(2020, 1, 1)},
            False,
        ),
        (
            "info=Decimal('1.0')",
            {"info": Decimal("1.0")},
            False,
        ),
    ],
)
def test_statically_extract_traceability_decorators(
    metadata, expected_metadata, contains_raw_source_code
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
        TraceabilityReport(
            file_path=_FILE_PATH,
            function_name="foo",
            line_number=2,
            end_line_number=3,
            source_code=_fn_def,
            key="A key",
            metadata=expected_metadata,
        )
    ]
    assert decorators[0].contains_raw_source_code == contains_raw_source_code


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
        TraceabilityReport(
            file_path=_FILE_PATH,
            function_name="foo",
            line_number=3,
            end_line_number=4,
            source_code=_fn_def,
            key=k,
            metadata={},
        )
        for k in ("KEY 1", "KEY 2")
    ]


def test_key_can_be_a_kwarg():
    source_code = dedent("""\
    @traceability(key="KEY")
    def foo():
        pass
    """)
    tree = ast.parse(source_code)
    decorators = TraceabilityVisitor(
        STANDARD_DECORATOR_NAME, _FILE_PATH, source_code
    ).visit(tree)
    assert decorators == [
        TraceabilityReport(
            file_path=_FILE_PATH,
            function_name="foo",
            line_number=2,
            end_line_number=3,
            source_code=_fn_def,
            key="KEY",
            metadata={},
        )
    ]


@pytest.mark.parametrize(
    "decorator_definition",
    [
        "@traceability()",
        "@traceability('key1','key2')",
        "@traceability('key1',key='key1')",
    ],
)
def test_invalid_decorators(decorator_definition):
    source_code = dedent(f"""\
    {decorator_definition}
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
