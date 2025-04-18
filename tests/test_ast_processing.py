from __future__ import annotations

import ast
from pathlib import Path
from textwrap import dedent

import pytest

from pytraceability.ast_processing import TraceabilityVisitor
from pytraceability.exceptions import InvalidTraceabilityError
from pytraceability.data_definition import (
    ExtractionResult,
    Traceability,
    RawSourceCode,
)
from tests.factories import TEST_CONFIG

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
            {"info": RawSourceCode("f'{var} something'")},
            False,
        ),
        (
            "info=[f'{var} something']",
            {"info": [RawSourceCode("f'{var} something'")]},
            False,
        ),
        ("info={'item1', 'item2'}", {"info": {"item1", "item2"}}, True),  # Test for set
        (
            "info=('item1', 'item2')",
            {"info": ("item1", "item2")},
            True,
        ),  # Test for tuple
        (
            "info={f'{var} something'}",
            {"info": {RawSourceCode("f'{var} something'")}},
            False,
        ),  # Set with RawSourceCode
        (
            "info=(f'{var} something',)",
            {"info": (RawSourceCode("f'{var} something'"),)},
            False,
        ),  # Tuple with RawSourceCode
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
    decorators = TraceabilityVisitor(TEST_CONFIG, _FILE_PATH, source_code).visit(tree)
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
    decorators = TraceabilityVisitor(TEST_CONFIG, _FILE_PATH, source_code).visit(tree)
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


@pytest.mark.raises(exception=InvalidTraceabilityError)
def test_key_must_be_specified():
    source_code = dedent("""\
    @traceability()
    def foo():
        pass
    """)
    tree = ast.parse(source_code)
    TraceabilityVisitor(TEST_CONFIG, _FILE_PATH, source_code).visit(tree)


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
    assert TraceabilityVisitor(TEST_CONFIG, _FILE_PATH, source_code).visit(tree) == []


@pytest.mark.raises(exception=InvalidTraceabilityError)
def test_cannot_have_two_args():
    source_code = dedent("""\
    @traceability('key1','key2')
    def foo():
        pass
    """)
    tree = ast.parse(source_code)
    TraceabilityVisitor(TEST_CONFIG, _FILE_PATH, source_code).visit(tree)
